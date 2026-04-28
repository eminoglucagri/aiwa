from __future__ import annotations
from datetime import datetime, date, time
from uuid import UUID
import enum

from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Sessions(Base):
    """Generated model for table: sessions"""
    __tablename__ = 'sessions'
    id = Column(Uuid(255), primary_key=True)
    user_id = Column(Uuid(255), nullable=False, ForeignKey('users(id)'))
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    __table_args__ = (Index('idx_sessions_user_id', "user_id"),)
    __table_args__ = (Index('idx_sessions_token_hash', "token_hash", unique=True),)
    __table_args__ = ()  # comment: User session management
    users = relationship('users', back_populates='sessions')
