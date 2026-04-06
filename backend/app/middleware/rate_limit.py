"""
VISIONZ — Rate Limiting Utilities
Per-endpoint and per-user rate limiting
"""

import logging
from typing import Callable, Optional
from functools import wraps
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from app.database import get_db
from app.config import settings
from app.errors import RateLimitError

logger = logging.getLogger(__name__)


class RateLimiter:
    """Advanced rate limiting with per-user and per-endpoint tracking"""
    
    def __init__(self, requests: int = settings.RATE_LIMIT_REQUESTS, 
                 window_seconds: int = settings.RATE_LIMIT_WINDOW_SECONDS):
        self.requests = requests
        self.window_seconds = window_seconds
        self.request_log = {}  # In-memory store: {user_id: [timestamps]}
    
    def is_allowed(self, user_id: int, endpoint: str) -> bool:
        """
        Check if request is allowed for user on endpoint
        
        Args:
            user_id: User ID
            endpoint: API endpoint
        
        Returns:
            True if allowed, False if rate limited
        """
        key = f"{user_id}:{endpoint}"
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Initialize if needed
        if key not in self.request_log:
            self.request_log[key] = []
        
        # Remove old requests outside window
        self.request_log[key] = [
            ts for ts in self.request_log[key] 
            if ts > cutoff
        ]
        
        # Check limit
        if len(self.request_log[key]) >= self.requests:
            logger.warning(f"[RateLimit] User {user_id} exceeded limit on {endpoint}")
            return False
        
        # Add current request
        self.request_log[key].append(now)
        return True
    
    def get_remaining_requests(self, user_id: int, endpoint: str) -> int:
        """Get remaining requests for user on endpoint"""
        key = f"{user_id}:{endpoint}"
        if key not in self.request_log:
            return self.requests
        
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)
        active_requests = len([
            ts for ts in self.request_log[key]
            if ts > cutoff
        ])
        
        return max(0, self.requests - active_requests)
    
    def cleanup_old_entries(self):
        """Remove old entries to prevent memory bloat"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds * 10)
        
        keys_to_delete = []
        for key, timestamps in self.request_log.items():
            self.request_log[key] = [
                ts for ts in timestamps 
                if ts > cutoff
            ]
            if not self.request_log[key]:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.request_log[key]


# Global rate limiter instance
_rate_limiter = RateLimiter() if settings.RATE_LIMIT_ENABLED else None


def rate_limit(requests: int = settings.RATE_LIMIT_REQUESTS,
               window_seconds: int = settings.RATE_LIMIT_WINDOW_SECONDS,
               per_user: bool = True):
    """
    Decorator for rate limiting an endpoint
    
    Args:
        requests: Max requests allowed
        window_seconds: Time window in seconds
        per_user: If True, limits per user; if False, global limit
    
    Usage:
        @router.get("/expensive-endpoint")
        @rate_limit(requests=10, window_seconds=60)
        def expensive_endpoint():
            return {"data": "value"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, request: Request, **kwargs):
            if not settings.RATE_LIMIT_ENABLED or not _rate_limiter:
                return await func(*args, request=request, **kwargs)
            
            # Extract user_id from headers or use IP
            user_id = request.headers.get("X-User-ID", request.client.host)
            endpoint = request.url.path
            
            if not _rate_limiter.is_allowed(user_id, endpoint):
                remaining = _rate_limiter.get_remaining_requests(user_id, endpoint)
                raise RateLimitError(retry_after=_rate_limiter.window_seconds)
            
            return await func(*args, request=request, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, request: Request, **kwargs):
            if not settings.RATE_LIMIT_ENABLED or not _rate_limiter:
                return func(*args, request=request, **kwargs)
            
            user_id = request.headers.get("X-User-ID", request.client.host)
            endpoint = request.url.path
            
            if not _rate_limiter.is_allowed(user_id, endpoint):
                raise RateLimitError(retry_after=_rate_limiter.window_seconds)
            
            return func(*args, request=request, **kwargs)
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def get_rate_limiter() -> Optional[RateLimiter]:
    """Get global rate limiter instance"""
    return _rate_limiter


import asyncio
