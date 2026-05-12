from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ============= ENUMS =============
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class InterestCategory(str, Enum):
    BEACHES = "beaches"
    ADVENTURE = "adventure"
    CULTURE = "culture"
    FOOD = "food"
    NATURE = "nature"
    SHOPPING = "shopping"
    RELAXATION = "relaxation"
    WATER_SPORTS = "water_sports"

class BudgetLevel(str, Enum):
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"

# ============= CHAT MODELS =============
class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What are the best beaches in Mauritius?",
                "user_id": 1,
                "session_id": "abc123",
                "context": {"location": "North", "interests": ["beaches", "water_sports"]}
            }
        }

class ChatResponse(BaseModel):
    message: str
    session_id: str
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime

# ============= ITINERARY MODELS =============
class ItineraryRequest(BaseModel):
    days: int = Field(..., ge=1, le=14, description="Number of days (1-14)")
    interests: List[InterestCategory] = Field(..., min_items=1, description="User interests")
    budget: BudgetLevel = Field(default=BudgetLevel.MODERATE)
    travelers: int = Field(1, ge=1, le=20, description="Number of travelers")
    start_date: Optional[str] = None
    special_requirements: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "days": 5,
                "interests": ["beaches", "food", "culture"],
                "budget": "moderate",
                "travelers": 2,
                "start_date": "2024-06-01",
                "special_requirements": ["vegetarian", "family-friendly"]
            }
        }

class Activity(BaseModel):
    time: str
    title: str
    description: str
    location: str
    duration: str
    cost_estimate: Optional[str] = None
    category: Optional[InterestCategory] = None
    coordinates: Optional[Dict[str, float]] = None

class DayPlan(BaseModel):
    day: int
    date: Optional[str] = None
    title: str
    activities: List[Activity]
    meals: Optional[List[Dict[str, str]]] = None
    notes: Optional[str] = None

class ItineraryResponse(BaseModel):
    itinerary_id: str
    title: str
    days: List[DayPlan]
    total_days: int
    estimated_cost: Optional[str] = None
    tips: Optional[List[str]] = None
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)

# ============= IMAGE RECOGNITION MODELS =============
class ImageRecognitionRequest(BaseModel):
    image_data: Optional[str] = None  # Base64 encoded
    image_url: Optional[str] = None
    context: Optional[str] = None
    
    @validator('image_data', 'image_url')
    def check_image_provided(cls, v, values):
        if not v and not values.get('image_url') and not values.get('image_data'):
            raise ValueError('Either image_data or image_url must be provided')
        return v

class RecognizedPlace(BaseModel):
    name: str
    confidence: float
    category: str
    description: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    similar_places: Optional[List[str]] = None

class ImageRecognitionResponse(BaseModel):
    recognized_places: List[RecognizedPlace]
    labels: List[str]
    description: str
    recommendations: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

# ============= RECOMMENDATION MODELS =============
class RecommendationRequest(BaseModel):
    category: InterestCategory
    location: Optional[str] = None
    budget: Optional[BudgetLevel] = None
    user_preferences: Optional[Dict[str, Any]] = None
    limit: int = Field(10, ge=1, le=50)

class Place(BaseModel):
    id: str
    name: str
    category: InterestCategory
    description: str
    rating: Optional[float] = Field(None, ge=0, le=5)
    location: Dict[str, Any]
    images: Optional[List[str]] = None
    price_level: Optional[BudgetLevel] = None
    opening_hours: Optional[str] = None
    contact: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None

class RecommendationResponse(BaseModel):
    recommendations: List[Place]
    total: int
    category: InterestCategory
    filters_applied: Dict[str, Any]

# ============= GENERAL MODELS =============
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str
    services: Dict[str, bool]

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)