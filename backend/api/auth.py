"""
Authentication utilities.
"""

from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import hashlib
from sqlalchemy.orm import Session

from database.models import APIKey

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        token: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Optional[str]:
    """
    Decode JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        user_id: User ID from token or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        return None


def create_api_key() -> tuple[str, str]:
    """
    Generate API key and its hash.
    
    Returns:
        api_key: Original API key (show only once)
        hashed_key: Hashed key for storage
    """
    # Generate random API key
    api_key = "ic_" + secrets.token_urlsafe(32)
    
    # Hash the key
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    
    return api_key, hashed_key


def verify_api_key(api_key: str, db: Session) -> Optional[int]:
    """
    Verify API key and return user ID.
    
    Args:
        api_key: API key to verify
        db: Database session
        
    Returns:
        user_id: User ID if valid, None otherwise
    """
    # Hash the provided key
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Look up in database
    db_key = db.query(APIKey).filter(
        APIKey.hashed_key == hashed_key,
        APIKey.is_active == 1
    ).first()
    
    if db_key:
        # Update last used
        db_key.last_used = datetime.utcnow()
        db.commit()
        
        return db_key.user_id
    
    return None
