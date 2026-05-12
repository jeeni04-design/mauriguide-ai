# 🌴 MauriGuide AI

A smart tourism web application for Mauritius — combining Django, FastAPI, and Groq AI to help tourists and locals discover the best of the island.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203.3-purple)

## Features
- 🌴 **Discover** — Browse 74+ real Mauritius places (beaches, food, hikes, sites)
- 🗺️ **Explore Map** — Interactive Leaflet map with coloured markers
- ✈️ **My Trips** — AI-generated itineraries with route mapping
- 🤖 **AI Chat** — Smart assistant with memory, location awareness, place cards
- 🔐 **Auth** — JWT login, Tourist and Local user types

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/mauriguide-ai.git
cd mauriguide-ai

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment files
cp .env.example backend/django_app/.env
cp .env.example backend/fastapi_app/.env
# Edit both files and add your keys

# 5. Django setup
cd backend/django_app
python manage.py migrate
python manage.py createsuperuser

# 6. Run both servers (two terminals)
# Terminal 1:
python manage.py runserver 8000

# Terminal 2:
cd backend/fastapi_app
python -m uvicorn main:app --reload --port 8001
```

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| `SECRET_KEY` | django `.env` | Django secret key — generate at djecrety.ir |
| `DEBUG` | django `.env` | `True` for dev, `False` for production |
| `GROQ_API_KEY` | fastapi `.env` | Free at console.groq.com |
| `DJANGO_URL` | fastapi `.env` | URL of Django server |

## Tech Stack
- **Django 4.2** — Web server, database, auth
- **FastAPI 0.104** — AI microservice
- **Groq Llama 3.3 70B** — Language model (free tier)
- **SQLite** — Database
- **Leaflet.js** — Interactive maps

## Deployment
See [SETUP.md](SETUP.md) for full deployment guide on Render.com.