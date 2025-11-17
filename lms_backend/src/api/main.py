from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.config import settings, validate_settings_or_exit
from src.utils.logging import configure_logging, logger
from src.errors.handlers import register_exception_handlers
from src.db.mongodb import connect_to_mongo, close_mongo_connection
from src.api.v1.router import api_router, tags_metadata
from src.utils.rate_limit import RateLimitMiddleware
from src.utils.request_id import get_request_id

# Initialize settings and logging
validate_settings_or_exit()
configure_logging(service_name=settings.APP_NAME)

app = FastAPI(
    title=settings.APP_NAME,
    description="TechLearn LMS Backend API",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting placeholder middleware
if settings.RATE_LIMIT_ENABLE:
    app.add_middleware(RateLimitMiddleware, rate="100/minute")

# Request context middleware for correlation id
class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = get_request_id(request)
        response = await call_next(request)
        if request_id:
            response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(CorrelationIdMiddleware)

# Register exception handlers
register_exception_handlers(app)

# Health and version endpoints
# PUBLIC_INTERFACE
@app.get("/health", summary="Health Check", tags=["health"])
async def health_check() -> dict:
    """Return a simple health response without blocking on external dependencies."""
    return {"status": "OK", "db_available": settings.DB_AVAILABLE, "auth": "supabase"}

# PUBLIC_INTERFACE
@app.get("/", summary="Service Version", tags=["health"])
async def version() -> dict:
    """Service version and environment information."""
    return {"service": settings.APP_NAME, "version": "1.0.0", "env": settings.APP_ENV}

# Include API v1
app.include_router(api_router, prefix="/api/v1")

# Startup and shutdown events
@app.on_event("startup")
async def on_startup():
    await connect_to_mongo()
    if settings.DB_AVAILABLE:
        logger.info({"msg": "Application startup complete", "db": "available", "auth": "supabase"})
    else:
        logger.warning({"msg": "Application startup complete - DB unavailable (MONGODB_URI not set). Running with limited functionality.", "auth": "supabase"})

@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo_connection()
    logger.info({"msg": "Application shutdown complete"})
