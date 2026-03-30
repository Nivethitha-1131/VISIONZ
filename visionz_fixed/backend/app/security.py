"""
VISIONZ Security Utilities
Password hashing and token management
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from app.config import settings


class PasswordManager:
    """Secure password handling with bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt with salt
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt(rounds=10)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify password against bcrypt hash
        
        Args:
            password: Plain text password to verify
            hashed_password: Previously hashed password
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            print(f"[Security] Password verification error: {e}")
            return False


class TokenManager:
    """JWT token management"""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            data: Data to encode in token
            expires_delta: Custom expiration time
        
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token
        
        Args:
            data: Data to encode in token
        
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
        
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            print("[Security] Token expired")
            return None
        except jwt.InvalidTokenError:
            print("[Security] Invalid token")
            return None


class SecurityUtils:
    """General security utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Basic email validation
        
        Args:
            email: Email string to validate
        
        Returns:
            True if valid email format
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"


# Utility functions for easy access
def hash_password(password: str) -> str:
    return PasswordManager.hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    return PasswordManager.verify_password(password, hashed)


def create_access_token(data: Dict[str, Any]) -> str:
    return TokenManager.create_access_token(data)


def create_refresh_token(data: Dict[str, Any]) -> str:
    return TokenManager.create_refresh_token(data)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    return TokenManager.verify_token(token)
