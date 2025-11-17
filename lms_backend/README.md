# TechLearn LMS - Backend (FastAPI)

Backend service providing REST APIs for the LMS.

## Features (foundation)
- FastAPI app with OpenAPI docs and health/version endpoints
- Environment-driven configuration (.env supported)
- Async MongoDB (Motor) with startup/shutdown events (optional; app starts without DB)
- Supabase Auth (JWT verification via JWKS)
- Role-based access control dependencies (admin, instructor, student)
- Courses endpoints (create/list/get/update/delete)
- Structured JSON logging with requestId correlation
- Centralized error handling
- Basic tests (pytest)

## Quick start

1. Create `.env` from `.env.example` and fill required secrets (SUPABASE_URL, SUPABASE_KEY). Mongo is optional.
2. Install dependencies:
   pip install -r requirements.txt
3. Run server:
   uvicorn src.api.main:app --reload --port $PORT

Open http://localhost:3001/docs for API docs.

Notes:
- When `MONGODB_URI` is not set, DB-dependent endpoints respond with 503 "Database not configured".
- On startup the app performs a quick non-blocking `ping` to MongoDB; on success logs `MongoDB connected` and enables DB features; on failure it logs an error and continues to serve with `db_available=false`.
- Auth endpoints issuing local JWTs are deprecated; use Supabase for sign-in/up. Backend provides `/api/v1/auth/me` to fetch the current user from the Supabase JWT.

## Scripts
- Generate OpenAPI: `python -m src.api.generate_openapi`
- Seed placeholder: `python scripts/seed.py` (requires MongoDB configured)
