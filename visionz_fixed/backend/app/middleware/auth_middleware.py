"""
VISIONZ — Auth Middleware
Token/Session validation for protected routes with expiration checking.
"""

import logging
from fastapi import Header, HTTPException, status

from app.services.session_manager import get_session_manager
from app.errors import UnauthorizedError, ForbiddenError

logger = logging.getLogger(__name__)


def get_current_user(authorization: str = Header(...)):
    """
    Extract and validate Bearer token with session expiration check.
    Returns the user info or raises 401.
    """
    try:
        if not authorization.startswith("Bearer "):
            raise UnauthorizedError("Invalid authorization header. Use: Bearer <token>")
        
        token = authorization[len("Bearer "):]
        
        # Validate session and check expiration
        session_manager = get_session_manager()
        session = session_manager.validate_session(token)
        
        if not session:
            logger.warning("[Auth] Invalid or expired token attempt")
            raise UnauthorizedError("Invalid or expired token. Please login again.")
        
        # Return user info from session
        user_info = {
            "id": session.get("user_id"),
            "name": session.get("name"),
            "email": session.get("email"),
            "role": session.get("role"),
            "avatar": session.get("avatar"),
            "department": session.get("department"),
            "session_id": session.get("id"),
            "last_activity": session.get("last_activity")
        }
        
        return user_info
    
    except UnauthorizedError:
        raise
    except Exception as e:
        logger.error(f"[Auth] get_current_user error: {e}")
        raise UnauthorizedError("Authentication error.")


def require_admin(authorization: str = Header(...)):
    """Only admin users can access this endpoint."""
    user = get_current_user(authorization)
    if user["role"] != "admin":
        logger.warning(f"[Auth] Non-admin user {user['email']} attempted admin access")
        raise ForbiddenError("Admin access required.")
    return user


def require_manager_or_above(authorization: str = Header(...)):
    """Manager or admin users only."""
    user = get_current_user(authorization)
    if user["role"] not in ("admin", "manager"):
        logger.warning(f"[Auth] User {user['email']} attempted manager-only access")
        raise ForbiddenError("Manager or Admin access required.")
    return user
