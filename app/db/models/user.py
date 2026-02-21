from sqlalchemy import Column, String, Text, TIMESTAMP, Boolean, ForeignKey,Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base



class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    college_id = Column(UUID(as_uuid=True), ForeignKey("colleges.id"))
    role = Column(Text, default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    tests_generated_count = Column(Integer, default=0, nullable=False)
    resources_viewed_count = Column(Integer, default=0, nullable=False)

    college = relationship("College")