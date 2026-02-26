"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    """User registration schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str


class CaptionRequest(BaseModel):
    """Caption generation request."""
    method: str = Field(default="beam_search", pattern="^(greedy|beam_search)$")
    beam_width: int = Field(default=5, ge=1, le=10)
    max_length: int = Field(default=50, ge=10, le=100)


class CaptionResponse(BaseModel):
    """Caption generation response."""
    caption: str
    inference_time_ms: float
    model_version: str
    method: str
    
    class Config:
        protected_namespaces = ()


class APIKeyResponse(BaseModel):
    """API key generation response."""
    api_key: str
    name: str
    created_at: datetime
    message: str


class CaptionHistoryItem(BaseModel):
    """Single caption history item."""
    caption: str
    timestamp: datetime
    inference_time_ms: Optional[float]


class UserStats(BaseModel):
    """User statistics."""
    email: str
    daily_requests: int
    total_requests: int
    recent_captions: List[CaptionHistoryItem]
