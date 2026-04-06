import uuid

from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func

from app.db.base import Base


class StudentDealsSurveyResponse(Base):
    __tablename__ = "student_deals_survey_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    responder_email = Column(Text, nullable=False, unique=True)
    interest = Column(String(20), nullable=False)
    spending = Column(String(20), nullable=False)
    frequency = Column(String(30), nullable=False)
    category_preference = Column(ARRAY(String), nullable=False)
    decision_driver = Column(String(40), nullable=False)
    offer_preference = Column(String(40), nullable=False)
    ordering_preference = Column(String(20), nullable=False)
    delivery_flexibility = Column(String(10), nullable=False)
    usage_intent = Column(String(30), nullable=False)
    open_feedback = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
