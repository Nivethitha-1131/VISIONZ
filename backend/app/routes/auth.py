"""
VISIONZ — Auth Routes
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
GET  /api/auth/sessions
"""

import secrets
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Header, Request
from typing import Optional

from app.database import get_db, hash_password
from app.security import verify_password
from app.services.session_manager import get_session_manager
from app.models.schemas import LoginRequest, LoginResponse, LogoutRequest
from app.middleware.auth_middleware import get_current_user
from app.errors import UnauthorizedError, ValidationError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, request: Request):
    """
    Authenticate user with email + password + role.
    Returns a session token with expiration.
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        # Find user by email
        cur.execute(
            "SELECT * FROM users WHERE email = ?",
            (body.email.strip().lower(),)
        )
        user = cur.fetchone()

        if not user:
            conn.close()
            logger.warning(f"[Auth] Failed login: user not found - {body.email}")
            raise UnauthorizedError("Email not found. Check your credentials.")

        # Verify password using bcrypt
        if not verify_password(body.password, user["password"]):
            conn.close()
            logger.warning(f"[Auth] Failed login: wrong password - {body.email}")
            raise UnauthorizedError("Incorrect password.")

        # Verify role matches (admin can login as any role)
        if user["role"] != body.role and user["role"] != "admin":
            conn.close()
            logger.warning(f"[Auth] Failed login: role mismatch - {body.email}")
            raise UnauthorizedError(f"Your account role is '{user['role']}', not '{body.role}'.")

        # Generate secure token
        token = secrets.token_hex(32)
        client_ip = request.client.host if request.client else None
        
        # Create session via manager
        session_manager = get_session_manager()
        session_info = session_manager.create_session(user["id"], token, client_ip)
        
        if not session_info:
            conn.close()
            raise UnauthorizedError("Failed to create session.")
        
        # Update last_login timestamp
        cur.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), user["id"])
        )
        conn.commit()
        conn.close()

        logger.info(f"[Auth] Successful login: {body.email}")

        return LoginResponse(
            token=token,
            user_id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user["role"],
            avatar=user["avatar"],
            department=user["department"],
            login_time=session_info["created_at"],
        )
    
    except Exception as e:
        logger.error(f"[Auth] Login error: {e}")
        if isinstance(e, HTTPException):
            raise
        raise UnauthorizedError(str(e))


@router.post("/logout")
def logout(body: LogoutRequest):
    """Invalidate the session token."""
    try:
        session_manager = get_session_manager()
        success = session_manager.invalidate_session(body.token)
        
        if success:
            logger.info("[Auth] User logged out successfully")
            return {"success": True, "message": "Logged out successfully."}
        else:
            raise UnauthorizedError("Failed to logout.")
    
    except Exception as e:
        logger.error(f"[Auth] Logout error: {e}")
        if isinstance(e, HTTPException):
            raise
        raise UnauthorizedError(str(e))


@router.get("/me")
def get_me(authorization: str = Header(...)):
    """Return current logged-in user info."""
    try:
        user = get_current_user(authorization)
        logger.info(f"[Auth] Getting user info: {user.get('email')}")
        return user
    
    except Exception as e:
        logger.error(f"[Auth] Get me error: {e}")
        if isinstance(e, HTTPException):
            raise
        raise UnauthorizedError("Failed to get user info.")


@router.get("/sessions")
def list_active_sessions(authorization: str = Header(...)):
    """List all active sessions for current user."""
    try:
        user = get_current_user(authorization)
        session_manager = get_session_manager()
        
        sessions = session_manager.get_active_sessions(user["id"])
        logger.info(f"[Auth] Listed {len(sessions)} active sessions for user {user['id']}")
        
        return {
            "success": True,
            "user_id": user["id"],
            "active_sessions": sessions,
            "session_count": len(sessions)
        }
    
    except Exception as e:
        logger.error(f"[Auth] List sessions error: {e}")
        if isinstance(e, HTTPException):
            raise
        raise UnauthorizedError(str(e))


@router.post("/sessions/{session_id}/revoke")
def revoke_session(session_id: int, authorization: str = Header(...)):
    """Revoke a specific session"""
    try:
        user = get_current_user(authorization)
        conn = get_db()
        cur = conn.cursor()
        
        # Verify session belongs to user
        cur.execute(
            "SELECT * FROM sessions WHERE id = ? AND user_id = ?",
            (session_id, user["id"])
        )
        
        session = cur.fetchone()
        if not session:
            conn.close()
            raise ValidationError("Session not found")
        
        # Revoke session
        cur.execute(
            "UPDATE sessions SET is_active = 0, logout_time = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), session_id)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"[Auth] Revoked session {session_id} for user {user['id']}")
        
        return {
            "success": True,
            "message": "Session revoked successfully."
        }
    
    except Exception as e:
        logger.error(f"[Auth] Revoke session error: {e}")
        if isinstance(e, HTTPException):
            raise
        raise UnauthorizedError(str(e))
