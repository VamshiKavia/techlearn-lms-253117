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
   - Backend requires: `SUPABASE_URL`, `SUPABASE_KEY`
   - Frontend requires:
     - Vite: `VITE_SUPABASE_URL`, `VITE_SUPABASE_KEY`, `VITE_SITE_URL`
     - CRA: `REACT_APP_SUPABASE_URL`, `REACT_APP_SUPABASE_KEY`, `REACT_APP_SITE_URL`
2. In Supabase project settings:
   - Authentication -> URL Configuration
     - Set "Site URL" to your frontend origin (e.g., `http://localhost:3000`).
     - Add any additional redirect URLs if using separate callback routes.
   - Authentication -> Providers (Email/OAuth)
     - Ensure redirect URLs include your frontend origin.
3. Start backend:
   - `uvicorn src.api.main:app --reload --port 3001`
   - CORS: Backend defaults allow `http://localhost:3000` and `http://127.0.0.1:3000`. Override via `CORS_ALLOWED_ORIGINS`.
4. Start frontend and sign up / log in with Supabase. The backend will verify JWTs via JWKS and authorize requests.
5. Optional: Use the temporary auth debug endpoint to verify end-to-end:
   - `GET /api/v1/auth/debug` with header `Authorization: Bearer <access_token>`

```text
Health: GET /health -> { status: "OK", db_available: <bool>, auth: "supabase" }
Me:     GET /api/v1/auth/me (with Bearer token)
Debug:  GET /api/v1/auth/debug (with Bearer token) -> { authenticated: true, user, claims }
```

### Notes

- Frontend uses a single Supabase client (`src/lib/supabaseClient.ts`) and attaches `Authorization: Bearer <access_token>` from `supabase.auth.getSession()` in `src/lib/apiClient.ts`.
- `emailRedirectTo` during sign-up uses `VITE_SITE_URL` or `REACT_APP_SITE_URL` (falls back to `window.location.origin`).
- Backend verifies:
  - `iss` starts with `SUPABASE_URL`
  - `aud` contains `authenticated` or `supabase`
  - JWKS keys fetched and cached (10-min TTL)
- If DB is not configured, only DB-dependent endpoints will return 503; auth endpoints continue to work.
