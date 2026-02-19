from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class Program(Base):
    __tablename__ = "programs"

    id = Column(UUID(as_uuid=True), primary_key=True)
    college_id = Column(UUID(as_uuid=True), ForeignKey("colleges.id"))
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    college = relationship("College")
