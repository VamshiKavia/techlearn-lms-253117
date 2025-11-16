# TechLearn LMS - Backend (FastAPI)

Backend service providing REST APIs for the LMS.

## Features (foundation)
- FastAPI app with OpenAPI docs and health/version endpoints
- Environment-driven configuration (.env supported)
- Async MongoDB (Motor) with startup/shutdown events
- JWT auth (access + refresh) and password hashing (bcrypt)
- Role-based access control dependencies (admin, instructor, student)
- Courses endpoints (create/list/get/update/delete)
- Structured JSON logging with requestId correlation
- Centralized error handling
- Basic tests (pytest)

## Quick start

1. Create `.env` from `.env.example` and fill required secrets.
2. Install dependencies:
   pip install -r requirements.txt
3. Run server:
   uvicorn src.api.main:app --reload --port $PORT

Open http://localhost:3001/docs for API docs.

## Scripts
- Generate OpenAPI: `python -m src.api.generate_openapi`
- Seed placeholder: `python scripts/seed.py`
