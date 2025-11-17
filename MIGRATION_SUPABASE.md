# Migration to Supabase Auth

This repository has migrated from local JWT auth to Supabase Auth.

## Backend (FastAPI)

- Supabase JWT verification via JWKS (no local JWT secret).
- Required env vars:
  - SUPABASE_URL
  - SUPABASE_KEY
  - Optional: SUPABASE_JWKS_URL (defaults to `${SUPABASE_URL}/auth/v1/jwks`)
- MongoDB is optional. If `MONGODB_URI` is not set, the app still starts and DB-dependent endpoints will return 503 "Database not configured".
- Auth dependency verifies Supabase JWTs and exposes:
  - GET /api/v1/auth/me
  - GET /api/v1/auth/debug (temporary diagnostics)

CORS:
- Allows `http://localhost:3000` by default (override via `CORS_ALLOWED_ORIGINS`).
- Authorization header allowed; credentials are not used.

## Frontend

- Uses `@supabase/supabase-js` for sign up/sign in.
- Env variables (Vite preferred):
  - VITE_SUPABASE_URL
  - VITE_SUPABASE_KEY
  - VITE_SITE_URL (e.g., http://localhost:3000)
  - VITE_API_BASE_URL (e.g., http://localhost:3001)
- API requests include `Authorization: Bearer <access_token>` from `supabase.auth.getSession()`.

Sign Up:
- Uses `emailRedirectTo` set from `VITE_SITE_URL` (falls back to window.location.origin).
- If email confirmation is required, frontend shows a clear "confirm your email" message.

## Supabase Dashboard Checklist

- Authentication -> Providers: enable Email/Password.
- Authentication -> URL Configuration:
  - Site URL: http://localhost:3000
  - Redirect URLs: http://localhost:3000
- (Dev only) Consider disabling "Confirm email" or ensure email delivery works.

## Verify End-to-End

1) Start backend:
   uvicorn src.api.main:app --reload --port 3001

2) Start frontend (http://localhost:3000), sign up and log in.

3) Call debug with your access token:
   GET http://localhost:3001/api/v1/auth/debug
   Header: Authorization: Bearer <access_token>

Expected:
- /health -> { status: "OK", db_available: <bool>, auth: "supabase" }
- /api/v1/auth/me -> user info (requires Bearer token)
- /api/v1/auth/debug -> { authenticated: true, user, claims } (requires Bearer token)

Notes:
- Backend verifies `iss` starts with SUPABASE_URL and `aud` includes "authenticated" or "supabase".
- JWKS keys cached for 10 minutes.
- If DB is not configured, DB endpoints return 503; auth endpoints continue to function.
