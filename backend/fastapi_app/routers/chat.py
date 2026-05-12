from fastapi import APIRouter, Depends, Header
from typing import Optional
from models.schemas import ChatRequest, ChatResponse, ChatMessage, MessageRole
from services.ai_service import AIService
import uuid
from datetime import datetime

router = APIRouter()
chat_sessions: dict = {}

def get_ai_service():
    return AIService()

GREETINGS = {"good morning","good evening","good afternoon","good night",
             "hello","hi","hey","Hola","bonjour","salut"}

@router.post("/send")
async def send_message(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        # Auth
        user_id = None
        if authorization:
            try:
                from services.auth_service import verify_django_token
                user_data = await verify_django_token(authorization)
                if user_data:
                    user_id = user_data.get("user_id")
            except Exception:
                pass
        if not user_id and request.user_id:
            user_id = request.user_id

        session_id = request.session_id or str(uuid.uuid4())

        # Init session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                "messages": [],
                "memory": {
                    "location": None,
                    "last_places": [],
                    "preferred_food": None,
                    "preferred_region": None,
                },
                "user_id": user_id,
                "created_at": datetime.now()
            }

        session = chat_sessions[session_id]
        history = session["messages"]
        memory  = session["memory"]

        # Reset on greeting after long conversation
        msg_lower = request.message.strip().lower()
        if any(g in msg_lower for g in GREETINGS) and len(history) > 10:
            session["messages"] = []
            session["memory"] = {
                "location": None, "last_places": [],
                "preferred_food": None, "preferred_region": None,
            }
            history = session["messages"]
            memory  = session["memory"]
            print(f"[router] session {session_id[:8]} reset on greeting")

        # Process
        result = await ai_service.process_chat(
            message=request.message,
            history=history,
            context=request.context,
            memory=memory
        )

        reply          = result["reply"]
        places         = result.get("places", [])
        memory_updates = result.get("memory_updates", {})

        # Apply memory updates
        session["memory"].update({k: v for k, v in memory_updates.items() if v is not None})

        # Append to history
        session["messages"].extend([
            ChatMessage(role=MessageRole.USER,      content=request.message, timestamp=datetime.now()),
            ChatMessage(role=MessageRole.ASSISTANT, content=reply,           timestamp=datetime.now()),
        ])
        # Cap history
        if len(session["messages"]) > 40:
            session["messages"] = session["messages"][-40:]

        # Build place cards
        place_cards = []
        for p in places:
            lat = p.get("latitude")
            lng = p.get("longitude")
            pname = p.get("name", "")
            ploc  = p.get("location", "")
            query = f"{pname} {ploc} Mauritius".strip().replace(" ", "+")
            if lat and lng:
                # Search link with coordinates as center for precision
                maps_url = f"https://www.google.com/maps/search/?api=1&query={query}&center={lat},{lng}"
                # Directions link (user_location as origin if known)
                user_loc = session["memory"].get("location","") if "session" in dir() else ""
                if user_loc:
                    origin = user_loc.replace(" ", "+") + "+Mauritius"
                    dir_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={query}"
                else:
                    dir_url = f"https://www.google.com/maps/dir/?api=1&destination={query}"
            else:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={query}"
                dir_url  = f"https://www.google.com/maps/dir/?api=1&destination={query}"

            place_cards.append({
                "name":          p.get("name", ""),
                "category":      p.get("category", ""),
                "location":      p.get("location", ""),
                "description":   p.get("description", ""),
                "image_url":     p.get("image_url", ""),
                "latitude":      lat,
                "longitude":     lng,
                "phone":         p.get("phone", ""),
                "address":       p.get("address") or p.get("location", ""),
                "website":       p.get("website", ""),
                "opening_hours": p.get("opening_hours", ""),
                "rating":        p.get("rating", 0),
                "cuisine":       p.get("cuisine", ""),
                "maps_url":      maps_url,
                "call_url":      f"tel:{p['phone']}" if p.get("phone") else "",
                "dir_url":       dir_url,
            })

        return {
            "message":    reply,
            "session_id": session_id,
            "places":     place_cards,
            "memory": {
                "location":    session["memory"].get("location"),
                "last_places": session["memory"].get("last_places", []),
            },
            "metadata": {
                "user_location": session["memory"].get("location", ""),
                "message_count": len(session["messages"]),
                "ai_model":      "Groq — Llama 3.3 70B",
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "message":    "Sorry, something went wrong. Please try again.",
            "session_id": request.session_id or str(uuid.uuid4()),
            "places":     [],
            "memory":     {},
            "metadata":   {},
            "timestamp":  datetime.now().isoformat()
        }