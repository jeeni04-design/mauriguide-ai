from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    Place,
    InterestCategory,
    BudgetLevel
)
from datetime import datetime
import uuid

router = APIRouter()



# Mock database (replace with actual database)
PLACES_DB = [
    {
        "id": "beach_trou_aux_biches",
        "name": "Trou aux Biches Beach",
        "category": InterestCategory.BEACHES,
        "description": "Beautiful beach with crystal clear waters, perfect for families and snorkeling",
        "rating": 4.8,
        "location": {
            "region": "North",
            "coordinates": {"lat": -20.0347, "lon": 57.5472},
            "address": "Trou aux Biches, Mauritius"
        },
        "images": [
            "trou_aux_biches_1.jpg",
            "trou_aux_biches_2.jpg"
        ],
        "price_level": BudgetLevel.BUDGET,
        "opening_hours": "Open 24/7",
        "contact": {
            "phone": "+230 xxx xxxx",
            "website": "www.example.com"
        },
        "tags": ["family-friendly", "snorkeling", "swimming", "beach"]
    },
    {
        "id": "restaurant_chez_tino",
        "name": "Chez Tino",
        "category": InterestCategory.FOOD,
        "description": "Authentic Mauritian cuisine in a traditional setting",
        "rating": 4.6,
        "location": {
            "region": "North",
            "coordinates": {"lat": -20.1039, "lon": 57.5789},
            "address": "Grand Baie, Mauritius"
        },
        "price_level": BudgetLevel.MODERATE,
        "opening_hours": "11:00 - 22:00",
        "tags": ["local cuisine", "seafood", "family-friendly"]
    },
    {
        "id": "activity_casela",
        "name": "Casela World of Adventures",
        "category": InterestCategory.ADVENTURE,
        "description": "Wildlife park with safari, zip-lining, and adventure activities",
        "rating": 4.7,
        "location": {
            "region": "West",
            "coordinates": {"lat": -20.3219, "lon": 57.4089},
            "address": "Cascavelle, Mauritius"
        },
        "price_level": BudgetLevel.MODERATE,
        "opening_hours": "09:00 - 17:00",
        "tags": ["safari", "adventure", "wildlife", "family-friendly"]
    },
    {
        "id": "culture_aapravasi_ghat",
        "name": "Aapravasi Ghat",
        "category": InterestCategory.CULTURE,
        "description": "UNESCO World Heritage Site, historic immigration depot",
        "rating": 4.3,
        "location": {
            "region": "Port Louis",
            "coordinates": {"lat": -20.1615, "lon": 57.5001},
            "address": "Port Louis, Mauritius"
        },
        "price_level": BudgetLevel.BUDGET,
        "opening_hours": "09:00 - 16:00",
        "tags": ["history", "unesco", "cultural", "educational"]
    },
    {
        "id": "nature_black_river",
        "name": "Black River Gorges National Park",
        "category": InterestCategory.NATURE,
        "description": "Largest national park with hiking trails and endemic species",
        "rating": 4.9,
        "location": {
            "region": "Southwest",
            "coordinates": {"lat": -20.4142, "lon": 57.4692},
            "address": "Black River, Mauritius"
        },
        "price_level": BudgetLevel.BUDGET,
        "opening_hours": "06:00 - 18:00",
        "tags": ["hiking", "nature", "wildlife", "scenic views"]
    }
]

@router.post("/get", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized recommendations based on preferences
    
    - **category**: Type of recommendations (beaches, food, culture, etc.)
    - **location**: Optional location filter
    - **budget**: Budget level (budget, moderate, luxury)
    - **user_preferences**: Additional preferences
    - **limit**: Maximum number of results (1-50)
    """
    try:
        # Filter places by category
        filtered_places = [
            place for place in PLACES_DB
            if place["category"] == request.category
        ]
        
        # Apply location filter
        if request.location:
            filtered_places = [
                place for place in filtered_places
                if request.location.lower() in place["location"]["region"].lower()
            ]
        
        # Apply budget filter
        if request.budget:
            filtered_places = [
                place for place in filtered_places
                if place["price_level"] == request.budget
            ]
        
        # Apply user preferences (tags matching)
        if request.user_preferences and request.user_preferences.get("tags"):
            user_tags = request.user_preferences["tags"]
            filtered_places = [
                place for place in filtered_places
                if any(tag in place.get("tags", []) for tag in user_tags)
            ]
        
        # Sort by rating
        filtered_places.sort(key=lambda x: x.get("rating", 0), reverse=True)
        
        # Limit results
        filtered_places = filtered_places[:request.limit]
        
        # Convert to Place models
        recommendations = [
            Place(
                id=place["id"],
                name=place["name"],
                category=place["category"],
                description=place["description"],
                rating=place.get("rating"),
                location=place["location"],
                images=place.get("images"),
                price_level=place.get("price_level"),
                opening_hours=place.get("opening_hours"),
                contact=place.get("contact"),
                tags=place.get("tags")
            )
            for place in filtered_places
        ]
        
        return RecommendationResponse(
            recommendations=recommendations,
            total=len(recommendations),
            category=request.category,
            filters_applied={
                "location": request.location,
                "budget": request.budget.value if request.budget else None,
                "user_preferences": request.user_preferences
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.get("/categories")
async def list_categories():
    """
    List all available recommendation categories
    """
    return {
        "categories": [
            {
                "value": cat.value,
                "label": cat.value.replace("_", " ").title(),
                "count": len([p for p in PLACES_DB if p["category"] == cat])
            }
            for cat in InterestCategory
        ]
    }

@router.get("/places/{place_id}")
async def get_place_details(place_id: str):
    """
    Get detailed information about a specific place
    """
    try:
        place = next((p for p in PLACES_DB if p["id"] == place_id), None)
        
        if not place:
            raise HTTPException(
                status_code=404,
                detail=f"Place '{place_id}' not found"
            )
        
        return Place(**place)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving place: {str(e)}"
        )

@router.get("/search")
async def search_places(
    query: str = Query(..., min_length=2),
    category: Optional[InterestCategory] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search for places by name or description
    
    - **query**: Search query (minimum 2 characters)
    - **category**: Optional category filter
    - **limit**: Maximum results (1-50)
    """
    try:
        query_lower = query.lower()
        
        # Search in name, description, and tags
        results = []
        for place in PLACES_DB:
            if category and place["category"] != category:
                continue
            
            if (query_lower in place["name"].lower() or
                query_lower in place["description"].lower() or
                any(query_lower in tag.lower() for tag in place.get("tags", []))):
                results.append(Place(**place))
        
        # Limit results
        results = results[:limit]
        
        return {
            "results": results,
            "total": len(results),
            "query": query,
            "category": category.value if category else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching places: {str(e)}"
        )

@router.get("/nearby")
async def get_nearby_places(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(10, ge=1, le=100),  # km
    category: Optional[InterestCategory] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get places near a location
    
    - **lat**: Latitude
    - **lon**: Longitude
    - **radius**: Search radius in kilometers (1-100)
    - **category**: Optional category filter
    - **limit**: Maximum results (1-50)
    """
    try:
        # Simplified distance calculation (for demo)
        # In production, use proper geospatial queries
        
        nearby_places = []
        for place in PLACES_DB:
            if category and place["category"] != category:
                continue
            
            # Mock distance calculation
            place_coords = place["location"]["coordinates"]
            # In production, calculate actual distance
            distance = 5.0  # Mock distance
            
            nearby_places.append({
                "place": Place(**place),
                "distance_km": distance
            })
        
        # Sort by distance and limit
        nearby_places.sort(key=lambda x: x["distance_km"])
        nearby_places = nearby_places[:limit]
        
        return {
            "places": nearby_places,
            "total": len(nearby_places),
            "center": {"lat": lat, "lon": lon},
            "radius_km": radius
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding nearby places: {str(e)}"
        )