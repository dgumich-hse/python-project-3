import uuid

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UUID
from datetime import datetime, timezone

from src.auth.db import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    short_code = Column(String(10), unique=True, index=True)
    original_url = Column(Text, nullable=False)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    clicks_count = Column(Integer, default=0)
    custom_alias = Column(String(50), unique=True, nullable=True)