from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class Year(Base):
    __tablename__ = "years"

    id = Column(UUID(as_uuid=True), primary_key=True)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"))
    college_id = Column(UUID(as_uuid=True), ForeignKey("colleges.id"))
    year_number = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    program = relationship("Program")
    college = relationship("College")
