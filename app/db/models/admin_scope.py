from sqlalchemy import Column, TIMESTAMP, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class AdminScope(Base):
    __tablename__ = "admin_scopes"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User")
    subject = relationship("Subject")
