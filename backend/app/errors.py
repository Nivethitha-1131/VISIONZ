"""
VISIONZ Error Handling
Custom exceptions and error responses
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """Standard error codes"""
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    DATABASE_ERROR = "DATABASE_ERROR"
    FILE_ERROR = "FILE_ERROR"
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"


class VisionzException(Exception):
    """Base exception for VISIONZ application"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        return {
            "success": False,
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp
            }
        }


class ValidationError(VisionzException):
    """Validation error"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details
        )


class UnauthorizedError(VisionzException):
    """Unauthorized error"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401
        )


class ForbiddenError(VisionzException):
    """Forbidden error"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=403
        )


class NotFoundError(VisionzException):
    """Not found error"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            f"{resource} not found",
            error_code=ErrorCode.NOT_FOUND,
            status_code=404
        )


class ConflictError(VisionzException):
    """Conflict error"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message,
            error_code=ErrorCode.CONFLICT,
            status_code=409,
            details=details
        )


class DatabaseError(VisionzException):
    """Database error"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message,
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            details=details
        )
        logger.error(f"Database error: {message}", extra=details)


class FileError(VisionzException):
    """File handling error"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message,
            error_code=ErrorCode.FILE_ERROR,
            status_code=400,
            details=details
        )


class AIServiceError(VisionzException):
    """AI service error"""
    def __init__(self, service: str, message: str):
        super().__init__(
            f"{service} error: {message}",
            error_code=ErrorCode.AI_SERVICE_ERROR,
            status_code=503,
            details={"service": service}
        )


class RateLimitError(VisionzException):
    """Rate limit exceeded"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            "Rate limit exceeded",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details={"retry_after": retry_after}
        )


def register_error_handlers(app: FastAPI):
    """Register error handlers with FastAPI app"""
    
    @app.exception_handler(VisionzException)
    async def visionz_exception_handler(request: Request, exc: VisionzException):
        logger.warning(f"Application error: {exc.message}", extra=exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.error(f"Value error: {str(exc)}")
        response = {
            "success": False,
            "error": {
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        return JSONResponse(status_code=400, content=response)
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        response = {
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        return JSONResponse(status_code=500, content=response)
