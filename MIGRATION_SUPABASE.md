# Migration to Supabase Auth

This repository has migrated from local JWT auth to Supabase Auth.

## Backend (FastAPI)

- Removed requirement for `JWT_SECRET`. Backend now verifies Supabase-issued JWTs using JWKS.
- Required env vars:
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - Optional: `SUPABASE_JWKS_URL` (defaults to `${SUPABASE_URL}/auth/v1/jwks`)
- MongoDB is optional. If `MONGODB_URI` is not set, the app still starts and DB-dependent endpoints will return 503 "Database not configured".
- New auth dependency verifies Supabase JWTs and exposes `/api/v1/auth/me`.
- Legacy local auth endpoints for issuing JWTs are removed/deprecated.

## Frontend

- Use `@supabase/supabase-js` to sign up/sign in.
- Read env from `REACT_APP_SUPABASE_URL` & `REACT_APP_SUPABASE_KEY` (CRA) or `VITE_SUPABASE_URL` & `VITE_SUPABASE_KEY` (Vite).
- Include the Supabase access token in API requests under `Authorization: Bearer <token>`.

## Steps to Configure

1. Create `.env` files for backend and frontend from provided examples.
2. In Supabase project settings, copy the project URL and `anon` public key to the frontend; use service role only on server-side if needed (not required here).
3. Start backend:
   - `uvicorn src.api.main:app --reload --port 3001`
4. Start frontend and log in via Supabase; the backend will verify JWTs and authorize requests.

```text
Health: GET /health -> { status: "OK", db_available: <bool>, auth: "supabase" }
Me:     GET /api/v1/auth/me (with Bearer token)
```
