from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.survey_response import StudentDealsSurveyResponse
from app.schemas.student_deals_survey import StudentDealsSurveyRequest


def has_student_deals_survey_submission(
    db: Session,
    responder_email: Optional[str] = None,
) -> bool:
    email = (responder_email or "").strip().lower()
    if not email:
        return False

    existing = (
        db.query(StudentDealsSurveyResponse.id)
        .filter(StudentDealsSurveyResponse.responder_email == email)
        .first()
    )
    return existing is not None


def submit_student_deals_survey(
    db: Session,
    request: StudentDealsSurveyRequest,
    responder_email: Optional[str] = None,
) -> dict:
    email = (responder_email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=401, detail="Unable to identify user email.")

    if has_student_deals_survey_submission(db=db, responder_email=email):
        raise HTTPException(
            status_code=409,
            detail="You have already submitted this survey.",
        )

    row = StudentDealsSurveyResponse(
        responder_email=email,
        interest=request.interest,
        spending=request.spending,
        frequency=request.frequency,
        category_preference=request.category_preference,
        decision_driver=request.decision_driver,
        offer_preference=request.offer_preference,
        ordering_preference=request.ordering_preference,
        delivery_flexibility=request.delivery_flexibility,
        usage_intent=request.usage_intent,
        open_feedback=request.open_feedback,
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "id": row.id,
        "message": "Thank you! Your response has been recorded.",
    }
