import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .database import Base


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    constraints = Column(JSONB, default={})
    preferences = Column(JSONB, default={})
    status = Column(String(20), nullable=False, default="analyzing")
    analysis = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_ideas_user_id", "user_id"),
        Index("idx_ideas_status", "status"),
    )