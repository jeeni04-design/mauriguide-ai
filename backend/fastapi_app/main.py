from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, recognition, recommendations
from models.schemas import ItineraryRequest, ItineraryResponse
from services.ai_service import AIService
from config import settings
import uvicorn
from datetime import datetime

app = FastAPI(
    title="MauriGuide AI API",
    description="""
    🌴 **MauriGuide AI - Your Intelligent Travel Assistant for Mauritius**

    Features:
    * 💬 AI-powered chatbot (Groq — Llama 3.1 70B)
    * 🗓️ Personalised itinerary generation
    * 🖼️ Image recognition for landmarks
    * 🎯 Smart recommendations for places and activities
    """,
    version="1.0.0",
    contact={"name": "MauriGuide Team", "email": "support@mauriguide.com"},
    license_info={"name": "MIT License"}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router,            prefix="/api/chat",            tags=["💬 Chat"])
app.include_router(recognition.router,     prefix="/api/recognition",     tags=["🖼️ Image Recognition"])
app.include_router(recommendations.router, prefix="/api/recommendations",  tags=["🎯 Recommendations"])


@app.get("/", tags=["🏠 General"])
async def root():
    return {
        "message": "Welcome to MauriGuide AI API! 🌴",
        "version": "1.0.0",
        "status": "running",
        "ai_model": "Groq — Llama 3.1 70B",
        "endpoints": {
            "docs":            "/docs",
            "chat":            "/api/chat/send",
            "itinerary":       "/api/itinerary/generate",
            "recognition":     "/api/recognition/identify",
            "recommendations": "/api/recommendations/get"
        }
    }


@app.get("/health", tags=["🏠 General"])
async def health_check():
    return {
        "status": "healthy",
        "service": "MauriGuide AI Chatbot",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "ai_model": "Groq — Llama 3.1 70B",
        "environment": "development" if settings.DEBUG else "production"
    }


@app.post("/api/itinerary/generate", response_model=ItineraryResponse, tags=["🗓️ Itinerary"])
async def generate_itinerary(request: ItineraryRequest):
    """Generate a personalised travel itinerary using Groq AI."""
    ai_service = AIService()
    return await ai_service.generate_itinerary(request)


@app.on_event("startup")
async def startup_event():
    print("🚀 MauriGuide AI API is starting...")
    print(f"📝 Debug mode: {settings.DEBUG}")
    print(f"🔗 Django API URL: {settings.DJANGO_API_URL}")
    print(f"🤖 AI Model: Groq — Llama 3.1 70B")
    if settings.GROQ_API_KEY:
        print("✅ Groq API Key configured — AI chat is ready!")
    else:
        print("⚠️  WARNING: GROQ_API_KEY not found in .env")
        print("   Chat will use fallback responses only")
    print("✅ API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    print("👋 MauriGuide AI API is shutting down...")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True, log_level="info")