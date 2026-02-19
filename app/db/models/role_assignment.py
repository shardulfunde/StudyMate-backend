from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class RoleAssignment(Base):
    __tablename__ = "role_assignments"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_type = Column(Text, primary_key=True)
    scope_type = Column(Text, primary_key=True)
    scope_id = Column(UUID(as_uuid=True), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
