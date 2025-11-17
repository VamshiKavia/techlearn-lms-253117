# TechLearn LMS - Monorepo

This repository contains multiple containers:
- lms_backend (FastAPI)
- lms_frontend (React)
- lms_database (MongoDB)

For this step, the backend service has been scaffolded and migrated to Supabase Auth.

Quick start (backend):
1) cd lms_backend
2) cp .env.example .env  # then set SUPABASE_URL and SUPABASE_KEY; MONGODB_URI is optional
3) pip install -r requirements.txt
4) uvicorn src.api.main:app --reload --port 3001

See MIGRATION_SUPABASE.md for details.