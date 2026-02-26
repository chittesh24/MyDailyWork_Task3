"""
Database models.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import datetime


class User(Base):
    """User table."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    api_keys = relationship('APIKey', back_populates='user', cascade='all, delete-orphan')
    captions = relationship('Caption', back_populates='user', cascade='all, delete-orphan')
    usage = relationship('Usage', back_populates='user', uselist=False, cascade='all, delete-orphan')


class APIKey(Base):
    """API Key table."""
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    hashed_key = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), default='Default Key')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = revoked
    
    # Relationships
    user = relationship('User', back_populates='api_keys')


class Caption(Base):
    """Caption history table."""
    __tablename__ = 'captions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    image_path = Column(String(500), nullable=True)  # S3 path or local path
    generated_caption = Column(Text, nullable=False)
    model_version = Column(String(50), default='v1.0')
    confidence_score = Column(Float, nullable=True)
    inference_time_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship('User', back_populates='captions')


class Usage(Base):
    """Usage tracking table."""
    __tablename__ = 'usage'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    daily_request_count = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    last_reset = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship('User', back_populates='usage')
