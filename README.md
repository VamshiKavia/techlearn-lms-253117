# TechLearn LMS - Monorepo

This repository contains multiple containers:
- lms_backend (FastAPI)
- lms_frontend (React)
- lms_database (MongoDB)

For this step, the backend service has been scaffolded.

Quick start (backend):
1) cd lms_backend
2) cp .env.example .env  # then edit secrets
3) pip install -r requirements.txt
4) uvicorn src.api.main:app --reload --port 3001