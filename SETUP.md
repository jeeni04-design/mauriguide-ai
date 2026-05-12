# MauriGuide AI — Setup Guide

## Requirements
- Python 3.11+
- Node.js (not required — pure Python/HTML)

## 1. Clone / unzip the project
```
cd Desktop
# unzip mauriguide-ai.zip or clone from git
cd mauriguide-ai
```

## 2. Create virtual environment
```bash
python -m venv venv # create

Remove-Item -Recurse -Force venv  #delete old version venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

## 3. Install all dependencies
```bash
pip install -r requirements.txt
```

## 4. Set up environment variables

Create `backend/django_app/.env`:
```
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Create `backend/fastapi_app/.env`:
```
GROQ_API_KEY=your-groq-api-key-here
```

> Get a free Groq API key at: https://console.groq.com

## 5. Run Django migrations
```bash
cd backend/django_app
python manage.py migrate
python manage.py createsuperuser
```

## 6. Load dataset (if included)
```bash
python manage.py loaddata fixtures/places.json
# or run the import script if provided
```

## 7. Start both servers

**Terminal 1 — Django (port 8000):**
```bash
cd backend/django_app
python manage.py runserver 8000
```

**Terminal 2 — FastAPI AI service (port 8001):**
```bash
cd backend/fastapi_app
python -m uvicorn main:app --reload --port 8001
```

## 8. Open the app
- Home: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Dashboard: http://127.0.0.1:8000/dashboard/
- FastAPI docs: http://127.0.0.1:8001/docs

## Project Structure
```
mauriguide-ai/
├── requirements.txt          ← Install this
├── SETUP.md                  ← This file
└── backend/
    ├── django_app/           ← Main web app (port 8000)
    │   ├── manage.py
    │   ├── .env              ← Create this
    │   ├── mauriguide/       ← Django settings
    │   ├── frontend/         ← HTML templates + static
    │   ├── accounts/         ← User auth
    │   ├── datasets/         ← Places API
    │   └── itinerary/        ← Trips API
    └── fastapi_app/          ← AI service (port 8001)
        ├── main.py
        ├── .env              ← Create this (GROQ_API_KEY)
        ├── routers/
        │   └── chat.py
        └── services/
            └── ai_service.py
```

## Notes
- The AI chat uses **Groq** (free tier, fast) — no paid API needed to start
- Static images go in: `backend/django_app/frontend/static/frontend/images/`
- All 9 background photos (home1.jpg–home9.jpg + local_bg.jpg + register_bg.jpg) must be copied there
