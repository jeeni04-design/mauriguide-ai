"""
MauriGuide AI Service v5 — Production Smart Tourism Assistant
- Full intent routing with sub-intents
- Conversational memory (location, preferences, last places)
- Location-aware proximity sorting
- Emergency bypass (zero tokens)
- Google Maps URL generation
- Dataset injection only when relevant
- Groq token optimisation
- Hallucination prevention
"""

import uuid, json, re
from groq import Groq
from typing import List, Dict, Optional
from models.schemas import (
    ChatMessage, MessageRole,
    ItineraryRequest, ItineraryResponse, DayPlan, Activity, InterestCategory
)
from config import settings

try:
    import httpx
    HTTPX_OK = True
except ImportError:
    HTTPX_OK = False
    print("WARNING: pip install httpx")

DJANGO = "http://127.0.0.1:8000"

# ── Emergency ─────────────────────────────────────────────────
EMERGENCY_WORDS = {
    "help","danger","sos","crime","accident","emergency","fire",
    "police","ambulance","injured","injury","drowning","stolen",
    "theft","robbery","hospital","doctor","medical","sick","crash",
    "attack","assault","missing","trapped","rescue","bleeding"
}

EMERGENCY_RESPONSE = (
    "🚨 **MAURITIUS EMERGENCY CONTACTS**\n\n"
    "🚑 **Ambulance / SAMU:** 114\n"
    "🚒 **Fire Brigade:** 115\n"
    "👮 **Police:** 999\n"
    "🏥 **DR Jeetoo Hospital:** +230 212 3201\n"
    "🏥 **Victoria Hospital:** +230 425 3031\n"
    "🌊 **Coast Guard:** +230 206 9100\n"
    "🛡️ **Tourist Police:** +230 213 2818\n\n"
    "⚠️ **Call 999 now if in immediate danger.**"
)

# ── Google Maps URL builders ───────────────────────────────────
def gmaps_search(place_name: str, location: str = "") -> str:
    query = f"{place_name} {location} Mauritius".strip().replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={query}"

def gmaps_directions(place_name: str, location: str = "", origin: str = "") -> str:
    dest = f"{place_name} {location} Mauritius".strip().replace(" ", "+")
    if origin:
        orig = f"{origin} Mauritius".replace(" ", "+")
        return f"https://www.google.com/maps/dir/?api=1&origin={orig}&destination={dest}"
    return f"https://www.google.com/maps/dir/?api=1&destination={dest}"

def gmaps_coords(lat: float, lng: float, place_name: str = "") -> str:
    query = place_name.replace(" ", "+") if place_name else ""
    if query:
        return f"https://www.google.com/maps/search/?api=1&query={query}&center={lat},{lng}"
    return f"https://www.google.com/maps?q={lat},{lng}"

# ── Mauritius regions ─────────────────────────────────────────
REGIONS: Dict[str, List[str]] = {
    "north":      ["grand baie","cap malheureux","goodlands","triolet","pamplemousses",
                   "terre rouge","riviere du rempart","mapou","piton","anse la raie"],
    "east":       ["trou d'eau douce","centre de flacq","flacq","quatre cocos",
                   "camp de masque","lalmatie","belle mare","roches noires"],
    "south":      ["mahebourg","rose belle","souillac","baie du cap","bel ombre",
                   "chemin grenier","grand sable","vieux grand port"],
    "west":       ["flic en flac","tamarin","black river","le morne","chamarel",
                   "albion","la gaulette","case noyale"],
    "central":    ["curepipe","vacoas","quatre bornes","rose hill","beau bassin",
                   "phoenix","floreal","moka","saint pierre","quartier militaire"],
    "port_louis": ["port louis","pailles","le hochet","baie du tombeau"],
}

ADJACENT: Dict[str, set] = {
    "north":      {"north","port_louis","central"},
    "east":       {"east","central"},
    "south":      {"south","central","west"},
    "west":       {"west","south","port_louis"},
    "central":    {"central","north","east","south","west","port_louis"},
    "port_louis": {"port_louis","north","west","central"},
}

def get_region(location: str) -> Optional[str]:
    if not location:
        return None
    loc = location.lower()
    for region, towns in REGIONS.items():
        if any(t in loc for t in towns):
            return region
    return None

def is_nearby(place_loc: str, user_loc: str) -> bool:
    r1 = get_region(place_loc)
    r2 = get_region(user_loc)
    if not r1 or not r2:
        return False
    return r2 in ADJACENT.get(r1, {r1})

# ── Intent detection ──────────────────────────────────────────
INTENT_PATTERNS: Dict[str, List[str]] = {
    "food":      [r"\bfood\b",r"\beat\b",r"\bhungry\b",r"\brestaurant\b",r"\bcafe\b",
                  r"\blunch\b",r"\bdinner\b",r"\bbreakfast\b",r"\bcuisine\b",r"\bdining\b",
                  r"\bsnack\b",r"\bdrink\b",r"\bmeal\b",r"\bwhere to eat\b"],
    "beach":     [r"\bbeach\b",r"\bbeaches\b",r"\blagoon\b",r"\bswim\b",
                  r"\bsnorkel\b",r"\bcoast\b"],
    "hike":      [r"\bhike\b",r"\bhiking\b",r"\btrail\b",r"\btrek\b",r"\bmountain\b",
                  r"\bwalk\b",r"\bgorge\b",r"\bpeak\b",r"\bnature walk\b"],
    "water":     [r"\bdiving\b",r"\bsurf\b",r"\bkayak\b",r"\bcatamaran\b",
                  r"\bkitesurf\b",r"\bwater sport\b",r"\bsnorkeling\b"],
    "land":      [r"\bquad\b",r"\bzip.?line\b",r"\bbuggy\b",r"\batv\b",
                  r"\badventure\b",r"\bcasela\b"],
    "site":      [r"\bmuseum\b",r"\btemple\b",r"\bgarden\b",r"\bheritage\b",
                  r"\bhistory\b",r"\bmonument\b",r"\bchurch\b",r"\bmosque\b"],
    "contact":   [r"\bnumber\b",r"\bphone\b",r"\bcall\b",r"\bcontact\b",
                  r"\baddress\b",r"\bwebsite\b"],
    "direction": [r"\bdirection\b",r"\bhow to get\b",r"\bwhere is\b",
                  r"\bget there\b",r"\bnavigate\b",r"\broute\b"],
    "weather":   [r"\bweather\b",r"\btemperature\b",r"\bclimate\b",
                  r"\brain\b",r"\bcyclone\b"],
    "price":     [r"\bprice\b",r"\bcost\b",r"\bhow much\b",
                  r"\bexpensive\b",r"\bcheap\b",r"\bbudget\b"],
    "transport": [r"\btaxi\b",r"\bbus\b",r"\brent.*car\b",
                  r"\btransport\b",r"\bgetting around\b"],
    "hotel":     [r"\bhotel\b",r"\bresort\b",r"\baccommodation\b",r"\bstay\b"],
    "itinerary": [r"\bitinerary\b",r"\b\d+[\s-]day\b",r"\bplan.*trip\b",r"\bschedule\b"],
    "location":  [r"\bi('m| am) (?:in|at|near)\b",r"\bstaying in\b",r"\bliving in\b"],
    "small_talk":[r"^(hi|hello|hey|good\s+\w+|thanks|thank you|bye|ok|okay|sure|cool|wow)[\s!.?]*$"],
}

PLACE_CATS = {"food", "beach", "hike", "water", "land", "site"}
WEB_CATS   = {"weather", "price", "transport", "hotel"}

TOKEN_BUDGET: Dict[str, int] = {
    "small_talk": 100, "location": 80,  "contact": 120,
    "direction":  200, "weather":  200, "price":   200,
    "transport":  250, "itinerary":600,
}

def detect_intent(message: str) -> str:
    m = message.strip().lower()
    words = set(re.findall(r'\b\w+\b', m))
    if words & EMERGENCY_WORDS:
        return "emergency"
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, m, re.I):
                return intent
    return "general"

def extract_location(message: str) -> Optional[str]:
    msg_low = message.lower()
    all_towns = sorted(
        [t for towns in REGIONS.values() for t in towns],
        key=len, reverse=True
    )
    for town in all_towns:
        if re.search(r'\b' + re.escape(town) + r'\b', msg_low):
            return town.title()
    return None

def trim_history(history: List[ChatMessage], max_turns: int = 3) -> List[Dict]:
    recent = history[-(max_turns * 2):]
    msgs: List[Dict] = []
    for msg in recent:
        role = "user" if msg.role == MessageRole.USER else "assistant"
        if msgs and msgs[-1]["role"] == role:
            msgs[-1]["content"] += f"\n{msg.content}"
        else:
            msgs.append({"role": role, "content": msg.content})
    return msgs


class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model  = "llama-3.3-70b-versatile"
        self._places_cache: Optional[List[Dict]] = None

    # ── Places ────────────────────────────────────────────────
    async def _get_places(self) -> List[Dict]:
        if self._places_cache is not None:
            return self._places_cache
        if not HTTPX_OK:
            return []
        try:
            async with httpx.AsyncClient(timeout=5.0) as c:
                r = await c.get(f"{DJANGO}/api/places/")
                if r.status_code == 200:
                    self._places_cache = r.json().get("places", [])
                    print(f"[v5] Places cached: {len(self._places_cache)}")
                    return self._places_cache
        except Exception as e:
            print(f"[v5] Places error: {e}")
        return []

    def _filter_by_category(
        self,
        places: List[Dict],
        category: str,
        user_location: str = "",
        limit: int = 6
    ) -> List[Dict]:
        filtered = [p for p in places if p.get("category") == category]
        if user_location:
            near  = [p for p in filtered if is_nearby(p.get("location", ""), user_location)]
            far   = [p for p in filtered if not is_nearby(p.get("location", ""), user_location)]
            filtered = near + far
        return filtered[:limit]

    def _build_db_context(self, places: List[Dict], user_location: str = "") -> str:
        if not places:
            return ""
        header = f"[DB - places near {user_location}]" if user_location else "[DB]"
        lines = []
        for p in places:
            line = f"- {p['name']} ({p['location']})"
            if p.get("phone"):
                line += f" | Tel: {p['phone']}"
            if p.get("opening_hours"):
                line += f" | Hours: {p['opening_hours']}"
            lat, lng = p.get("latitude"), p.get("longitude")
            if lat and lng:
                gm = gmaps_coords(lat, lng, p["name"])
            else:
                gm = gmaps_search(p["name"], p.get("location", ""))
            line += f" | Maps: {gm}"
            lines.append(line)
        return header + "\n" + "\n".join(lines)

    # ── Web search ────────────────────────────────────────────
    async def _web_search(self, query: str) -> str:
        if not HTTPX_OK:
            return ""
        try:
            async with httpx.AsyncClient(timeout=5.0) as c:
                r = await c.get(
                    "https://api.duckduckgo.com/",
                    params={"q": f"Mauritius {query}", "format": "json",
                            "no_html": "1", "skip_disambig": "1"},
                    headers={"User-Agent": "MauriGuide/1.0"}
                )
                d = r.json()
            answer   = (d.get("Answer") or "")[:150]
            abstract = (d.get("AbstractText") or "")[:200]
            source   = d.get("AbstractSource", "")
            if answer:
                return f"[WEB: {answer} (Source: DuckDuckGo)]"
            if abstract and source:
                return f"[WEB: {abstract} (Source: {source})]"
        except Exception as e:
            print(f"[v5] Web search error: {e}")
        return ""

    # ── System prompt ─────────────────────────────────────────
    def _system(self, memory: Dict) -> str:
        ctx_lines = []
        if memory.get("location"):
            region = get_region(memory["location"]) or "unknown"
            ctx_lines.append(f"User is in: {memory['location']} (region: {region})")
        if memory.get("last_places"):
            ctx_lines.append(f"Last discussed: {', '.join(memory['last_places'][:3])}")
        ctx_block = "\n".join(ctx_lines) if ctx_lines else "No user context yet."

        return (
            "You are MauriGuide AI, a smart Mauritius travel assistant.\n\n"
            f"USER CONTEXT:\n{ctx_block}\n\n"
            "STRICT RULES:\n"
            "1. NEVER invent place names, phone numbers, addresses or directions.\n"
            "2. ONLY recommend places from [DB]. If no [DB], say you don't have that info.\n"
            "3. For food questions: recommend ONLY food places from [DB].\n"
            "4. For beach/hike/activity: recommend ONLY that category from [DB].\n"
            "5. For phone/contact: ONLY give numbers that appear in [DB].\n"
            "6. For directions: say 'tap the Maps button below to open Google Maps directions' - never invent routes.\n"
            "7. Prioritise places near the user's location shown in USER CONTEXT.\n"
            "8. Reply in user's language. Max 2 short sentences + place names from [DB].\n"
            "9. Use 1 emoji max. No unnecessary follow-up questions.\n"
            "10. If [WEB] provided, cite as (Source: name).\n"
            "11. NEVER reference any internal map system. All navigation uses Google Maps externally."
        )

    # ── Main chat ─────────────────────────────────────────────
    async def process_chat(
        self,
        message: str,
        history: List[ChatMessage],
        context: Optional[Dict] = None,
        memory: Optional[Dict] = None
    ) -> Dict:

        if memory is None:
            memory = {}

        # Emergency — always responds, zero tokens
        if set(re.findall(r'\b\w+\b', message.lower())) & EMERGENCY_WORDS:
            return {"reply": EMERGENCY_RESPONSE, "places": [], "memory_updates": {}}

        intent = detect_intent(message)
        print(f"[v5] intent={intent} | msg={message[:60]}")

        # Extract and store location
        memory_updates: Dict = {}
        new_loc = extract_location(message)
        if new_loc:
            memory_updates["location"] = new_loc
            memory["location"] = new_loc
            print(f"[v5] location={new_loc}")

        user_location = memory.get("location", "")

        # Build context and get structured places
        structured_places: List[Dict] = []
        ctx = ""

        try:
            all_places = await self._get_places()

            if intent in PLACE_CATS:
                structured_places = self._filter_by_category(
                    all_places, intent, user_location
                )
                ctx = self._build_db_context(structured_places, user_location)

            elif intent == "contact":
                last = memory.get("last_places", [])
                structured_places = [p for p in all_places if p.get("name") in last][:3]
                # Also check if message names a place directly
                for p in all_places:
                    if (p["name"].lower() in message.lower()
                            and p not in structured_places):
                        structured_places.append(p)
                        break
                ctx = self._build_db_context(structured_places, user_location)

            elif intent == "direction":
                # Find the place mentioned in the message
                for p in all_places:
                    if p["name"].lower() in message.lower():
                        structured_places = [p]
                        break
                # Fall back to last discussed place
                if not structured_places and memory.get("last_places"):
                    structured_places = [
                        p for p in all_places
                        if p.get("name") in memory["last_places"]
                    ][:1]
                if structured_places:
                    p = structured_places[0]
                    gm_dir = gmaps_directions(
                        p["name"], p.get("location", ""), user_location
                    )
                    ctx = (
                        f"[DIRECTION]\n"
                        f"Place: {p['name']} in {p.get('location', '')}\n"
                        f"Google Maps link: {gm_dir}\n"
                        f"Tell user to tap the Maps button below to open Google Maps."
                    )

            elif intent in WEB_CATS:
                web = await self._web_search(message)
                if web:
                    ctx = web

            elif intent == "general":
                seek = {"where","what","recommend","suggest","show",
                        "find","visit","near","best","good","any"}
                if seek & set(re.findall(r'\b\w+\b', message.lower())):
                    structured_places = (
                        self._filter_by_category(all_places, "food",  user_location, 3)
                        + self._filter_by_category(all_places, "beach", user_location, 2)
                    )
                    ctx = self._build_db_context(structured_places[:5], user_location)

        except Exception as e:
            print(f"[v5] context error: {e}")

        # Update memory with last recommended places
        if structured_places:
            memory_updates["last_places"] = [p["name"] for p in structured_places[:4]]
            memory["last_places"] = memory_updates["last_places"]

        # Build messages for Groq
        no_ctx_intents = {"small_talk", "location", "emergency"}
        user_msg = (
            f"{ctx}\n\n{message}".strip()
            if ctx and intent not in no_ctx_intents
            else message
        )
        max_turns   = 1 if intent in ("small_talk", "location") else 3
        history_msgs = trim_history(history, max_turns)
        messages    = [*history_msgs, {"role": "user", "content": user_msg}]
        max_tokens  = TOKEN_BUDGET.get(intent, 280)

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._system(memory)},
                    *messages
                ],
                temperature=0.6,
                max_tokens=max_tokens
            )
            reply = resp.choices[0].message.content
            return {
                "reply":          reply,
                "places":         structured_places,
                "memory_updates": memory_updates
            }

        except Exception as e:
            err = str(e)
            print(f"[v5] Groq error: {err}")
            if "429" in err or "rate_limit" in err:
                wait = re.search(r"try again in ([\w.]+)", err)
                wt = wait.group(1) if wait else "a few minutes"
                return {
                    "reply":          f"AI limit reached. Try again in {wt}. Browse the Discover section meanwhile!",
                    "places":         structured_places,
                    "memory_updates": memory_updates
                }
            return {
                "reply":          self._fallback(intent),
                "places":         structured_places,
                "memory_updates": memory_updates
            }

    def _fallback(self, intent: str) -> str:
        return {
            "food":      "Check out local restaurants from the Discover section. Any area preference? 🍽️",
            "beach":     "Top beaches: Trou aux Biches, Belle Mare, Flic en Flac, Le Morne. 🏖️",
            "hike":      "Top hikes: Black River Gorges, Le Pouce, Piton de la Petite Riviere Noire. ⛰️",
            "water":     "Water sports: Blue Bay diving, Le Morne kitesurfing, catamaran tours. 🤿",
            "land":      "Adventures: Casela quad biking, Chamarel zip-lining, buggy tours. 🏍️",
            "site":      "Must-see: Pamplemousses Garden, Aapravasi Ghat, Mahebourg Museum. 🏛️",
            "weather":   "Best weather: May-Nov. Cyclone season: Dec-Apr. 🌤️",
            "emergency": EMERGENCY_RESPONSE,
        }.get(intent, "Hello! Ask me about food, beaches, hikes or activities in Mauritius! 🌴")

    # ── Itinerary ─────────────────────────────────────────────
    async def generate_itinerary(self, request: ItineraryRequest) -> ItineraryResponse:
        all_places = await self._get_places()
        interests  = [i.value for i in request.interests]
        cat_map    = {"beaches": "beach", "water_sports": "water"}
        cats       = {cat_map.get(i, i) for i in interests}
        rel_places = [p for p in all_places if p.get("category") in cats][:12]
        db_ctx     = self._build_db_context(rel_places) if rel_places else ""
        prompt = (
            f"Create a {request.days}-day Mauritius itinerary. "
            f"Interests: {', '.join(interests)}. Budget: {request.budget.value}.\n"
            f"{db_ctx}\n\n"
            "Respond ONLY with valid JSON (no markdown):\n"
            '{"title":"","estimated_cost":"","tips":[],'
            '"days":[{"day":1,"title":"","notes":"",'
            '"activities":[{"time":"","title":"","description":"",'
            '"location":"","duration":"","cost_estimate":"","category":"beaches"}],'
            '"meals":[{"meal":"breakfast","suggestion":""}]}]}'
        )
        try:
            r = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Mauritius travel expert. JSON only, no markdown."},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.7, max_tokens=2000
            )
            raw = r.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return self._parse_itinerary(json.loads(raw.strip()), request)
        except Exception as e:
            print(f"[v5] Itinerary error: {e}")
            return self._fallback_itinerary(request)

    def _parse_itinerary(self, data: Dict, request: ItineraryRequest) -> ItineraryResponse:
        days = []
        for d in data.get("days", []):
            acts = []
            for a in d.get("activities", []):
                try:
                    cat = InterestCategory(a.get("category", ""))
                except Exception:
                    cat = request.interests[0] if request.interests else InterestCategory.BEACHES
                acts.append(Activity(
                    time=a.get("time", ""),
                    title=a.get("title", ""),
                    description=a.get("description", ""),
                    location=a.get("location", "Mauritius"),
                    duration=a.get("duration", ""),
                    cost_estimate=a.get("cost_estimate"),
                    category=cat,
                    coordinates=a.get("coordinates")
                ))
            days.append(DayPlan(
                day=d.get("day", len(days) + 1),
                title=d.get("title", ""),
                activities=acts,
                meals=d.get("meals"),
                notes=d.get("notes"),
                date=request.start_date
            ))
        return ItineraryResponse(
            itinerary_id=str(uuid.uuid4()),
            title=data.get("title", "Your Mauritius Journey"),
            days=days,
            total_days=request.days,
            estimated_cost=data.get("estimated_cost", "Varies"),
            tips=data.get("tips", []),
            session_id=str(uuid.uuid4())
        )

    def _fallback_itinerary(self, request: ItineraryRequest) -> ItineraryResponse:
        return ItineraryResponse(
            itinerary_id=str(uuid.uuid4()),
            title=f"Your {request.days}-Day Mauritius Trip",
            days=[
                DayPlan(
                    day=i + 1,
                    title=f"Day {i + 1}",
                    activities=[Activity(
                        time="9:00 AM",
                        title="Explore Mauritius",
                        description="Please try again when AI is available.",
                        location="Mauritius",
                        duration="Full day",
                        cost_estimate=None,
                        category=request.interests[0] if request.interests else InterestCategory.BEACHES
                    )],
                    meals=None,
                    notes=None
                )
                for i in range(request.days)
            ],
            total_days=request.days,
            estimated_cost="Varies",
            tips=["Book in advance", "Rent a car for flexibility"],
            session_id=str(uuid.uuid4())
        )