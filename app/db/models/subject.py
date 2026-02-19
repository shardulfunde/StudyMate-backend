from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(UUID(as_uuid=True), primary_key=True)
    year_id = Column(UUID(as_uuid=True), ForeignKey("years.id"))
    college_id = Column(UUID(as_uuid=True), ForeignKey("colleges.id"))
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    year = relationship("Year")
    college = relationship("College")
