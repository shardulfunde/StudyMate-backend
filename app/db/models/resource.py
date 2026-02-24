from sqlalchemy import Column, Text, TIMESTAMP, Boolean, String,Integer
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True)
    college_id = Column(UUID(as_uuid=True))
    subject_id = Column(UUID(as_uuid=True))
    title = Column(Text)
    file_key = Column(Text)
    resource_type = Column(Text, nullable=False)
    approval_status = Column(Text, nullable=False, default="pending", server_default="pending")
    approved_by = Column(String, nullable=True)
    approved_at = Column(TIMESTAMP, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    embedding_status = Column(String, nullable=False, default="pending", server_default="pending")
    uploaded_by = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    view_count = Column(Integer, default=0, nullable=False)
    tests_generated_count = Column(Integer, default=0, nullable=False)
