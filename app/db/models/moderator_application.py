import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class ModeratorApplication(Base):
    __tablename__ = "moderator_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(10), nullable=False)
    branch = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    motivation = Column(Text, nullable=True)
    status = Column(Text, nullable=False, default="pending")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    reviewed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    reviewed_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
