"""
VISIONZ Backend — FastAPI Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging
from datetime import datetime

from app.config import settings
from app.database import init_db
from app.routes import auth, users, detections, analytics, reports, video, ai
from app.services.llama_service import initialize_llama
from app.services.yolo_service import initialize_yolo
from app.errors import register_error_handlers
from app.middleware import register_security_middleware

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("  VISIONZ Backend — Startup Sequence")
    print("=" * 60)
    
    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    print("[Startup] Uploads directory ready")
    
    # Initialize database
    init_db()
    print("[Startup] Database initialized")
    
    # Initialize AI services
    print("[Startup] Initializing AI services...")
    try:
        initialize_llama()
    except Exception as e:
        print(f"[Startup] Llama initialization warning: {e}")
    
    try:
        initialize_yolo()
    except Exception as e:
        print(f"[Startup] YOLOv6 initialization warning: {e}")
    
    print("=" * 60)
    print("  VISIONZ Backend — Ready")
    print("=" * 60)
    
    yield
    
    print("[Shutdown] VISIONZ Backend shutting down...")


app = FastAPI(
    title="VISIONZ QC API",
    description="AI-Powered FMCG Quality Control System with Llama & YOLOv6",
    version="3.0.0",
    lifespan=lifespan,
)

# Register error handlers
register_error_handlers(app)

# Register security middleware (CSP, headers, logging, etc.)
register_security_middleware(app)

# CORS configuration from settings
cors_origins = settings.cors_origins_list
cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
cors_headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=cors_methods,
    allow_headers=cors_headers,
)

# Rate limiting middleware if enabled
if settings.RATE_LIMIT_ENABLED:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from fastapi.responses import JSONResponse
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    logger.info(f"Rate limiting enabled: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW_SECONDS} seconds")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router,       prefix="/api/auth",       tags=["Auth"])
app.include_router(users.router,      prefix="/api/users",      tags=["Users"])
app.include_router(detections.router, prefix="/api/detections", tags=["Detections"])
app.include_router(analytics.router,  prefix="/api/analytics",  tags=["Analytics"])
app.include_router(reports.router,    prefix="/api/reports",    tags=["Reports"])
app.include_router(video.router,      prefix="/api/video",      tags=["Video"])
app.include_router(ai.router,         prefix="/api/ai",         tags=["AI"])


@app.get("/", tags=["Health"])
def root():
    return {"app": "VISIONZ QC System", "version": "3.0.0", "status": "running", "docs": "/docs"}

@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok"}
