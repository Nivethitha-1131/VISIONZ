"""
VISIONZ — Security Headers Middleware
Adds HTTP security headers to all responses
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Content Security Policy - prevent XSS
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' http://localhost:*; "
            "form-action 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection in older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        # HSTS (HTTPS only in production)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Disable caching for sensitive endpoints
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests for audit trail"""
    
    async def dispatch(self, request: Request, call_next):
        # Extract useful info
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_id = request.headers.get("X-User-ID", "anonymous")
        
        # Log request
        logger.info(f"[Request] {method} {path} from {client_ip} (User: {user_id})")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(f"[Response] {method} {path} - {response.status_code}")
        
        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Whitelist IPs for sensitive endpoints (optional)"""
    
    SENSITIVE_PATHS = [
        "/api/auth/admin",
        "/api/users/delete",
        "/api/system"
    ]
    
    WHITELISTED_IPS = {
        "127.0.0.1",
        "localhost",
        "::1"  # IPv6 localhost
    }
    
    async def dispatch(self, request: Request, call_next):
        # Check sensitive paths
        if any(request.url.path.startswith(path) for path in self.SENSITIVE_PATHS):
            client_ip = request.client.host if request.client else None
            
            if client_ip not in self.WHITELISTED_IPS:
                logger.warning(f"[Security] Blocked access from {client_ip} to {request.url.path}")
                return Response(
                    content="Access denied",
                    status_code=403
                )
        
        return await call_next(request)


def register_security_middleware(app: FastAPI):
    """Register all security middleware"""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    logger.info("[Middleware] Security headers and logging middleware registered")
