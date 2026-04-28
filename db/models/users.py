from __future__ import annotations
from datetime import datetime, date, time
from uuid import UUID
import enum
import passlib.context

from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Users(Base):
    """Generated model for table: users"""
    __tablename__ = 'users'
    id = Column(Uuid(255), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    role = Column(String(255))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    __table_args__ = (Index('idx_users_email', "email", unique=True),)
    __table_args__ = (Index('idx_users_created_at', "created_at"),)
    __table_args__ = ()  # comment: User accounts and authentication
