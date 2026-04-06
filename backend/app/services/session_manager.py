"""
VISIONZ — Session Management Service
Manages user sessions with timeout and expiration
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage user sessions with automatic expiration"""
    
    SESSION_TIMEOUT_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    CLEANUP_INTERVAL_MINUTES = 60
    
    @staticmethod
    def create_session(user_id: int, token: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Create new user session
        
        Args:
            user_id: User ID
            token: Session token
            ip_address: Client IP address
        
        Returns:
            Session info
        """
        try:
            conn = get_db()
            cur = conn.cursor()
            
            login_time = datetime.utcnow().isoformat()
            
            # Deactivate old sessions for this user
            cur.execute(
                "UPDATE sessions SET is_active = 0 WHERE user_id = ? AND is_active = 1",
                (user_id,)
            )
            
            # Create new session
            cur.execute("""
                INSERT INTO sessions 
                (user_id, token, login_time, is_active, ip_address, last_activity)
                VALUES (?, ?, ?, 1, ?, ?)
            """, (user_id, token, login_time, ip_address, login_time))
            
            session_id = cur.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"[Session] Created session {session_id} for user {user_id}")
            
            return {
                "session_id": session_id,
                "user_id": user_id,
                "token": token,
                "created_at": login_time,
                "expires_at": (datetime.utcnow() + timedelta(minutes=SessionManager.SESSION_TIMEOUT_MINUTES)).isoformat()
            }
        
        except Exception as e:
            logger.error(f"[Session] Create error: {e}")
            return None
    
    @staticmethod
    def validate_session(token: str) -> Optional[Dict[str, Any]]:
        """
        Validate session and check expiration
        
        Args:
            token: Session token
        
        Returns:
            Session data if valid, None otherwise
        """
        try:
            conn = get_db()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT s.*, u.id as user_id, u.email, u.role, u.name
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.token = ? AND s.is_active = 1
            """, (token,))
            
            session = cur.fetchone()
            
            if not session:
                conn.close()
                return None
            
            # Check session expiration
            login_time = datetime.fromisoformat(session["login_time"])
            timeout_delta = timedelta(minutes=SessionManager.SESSION_TIMEOUT_MINUTES)
            
            if datetime.utcnow() - login_time > timeout_delta:
                logger.warning(f"[Session] Session expired: {session['id']}")
                # Invalidate expired session
                cur.execute("UPDATE sessions SET is_active = 0 WHERE id = ?", (session["id"],))
                conn.commit()
                conn.close()
                return None
            
            # Update last activity
            cur.execute(
                "UPDATE sessions SET last_activity = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), session["id"])
            )
            conn.commit()
            conn.close()
            
            return dict(session)
        
        except Exception as e:
            logger.error(f"[Session] Validation error: {e}")
            return None
    
    @staticmethod
    def invalidate_session(token: str) -> bool:
        """
        Invalidate/logout session
        
        Args:
            token: Session token
        
        Returns:
            True if successful
        """
        try:
            conn = get_db()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE sessions 
                SET is_active = 0, logout_time = ? 
                WHERE token = ?
            """, (datetime.utcnow().isoformat(), token))
            
            conn.commit()
            conn.close()
            
            logger.info(f"[Session] Invalidated session")
            return True
        
        except Exception as e:
            logger.error(f"[Session] Invalidation error: {e}")
            return False
    
    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        Clean up expired sessions from database
        
        Returns:
            Number of sessions cleaned
        """
        try:
            conn = get_db()
            cur = conn.cursor()
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=SessionManager.SESSION_TIMEOUT_MINUTES)
            
            cur.execute("""
                DELETE FROM sessions 
                WHERE is_active = 0 AND logout_time IS NULL 
                AND login_time < ?
            """, (cutoff_time.isoformat(),))
            
            deleted = cur.rowcount
            conn.commit()
            conn.close()
            
            if deleted > 0:
                logger.info(f"[Session] Cleaned up {deleted} expired sessions")
            
            return deleted
        
        except Exception as e:
            logger.error(f"[Session] Cleanup error: {e}")
            return 0
    
    @staticmethod
    def get_active_sessions(user_id: int) -> list:
        """Get all active sessions for a user"""
        try:
            conn = get_db()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, login_time, last_activity, ip_address
                FROM sessions
                WHERE user_id = ? AND is_active = 1
                ORDER BY login_time DESC
            """, (user_id,))
            
            sessions = [dict(row) for row in cur.fetchall()]
            conn.close()
            
            return sessions
        
        except Exception as e:
            logger.error(f"[Session] Get sessions error: {e}")
            return []


def get_session_manager() -> SessionManager:
    """Get session manager instance"""
    return SessionManager()
