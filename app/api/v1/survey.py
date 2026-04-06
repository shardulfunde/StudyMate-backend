from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.limiter import limiter
from app.db.models.user import User
from app.schemas.student_deals_survey import (
    StudentDealsSurveyRequest,
    StudentDealsSurveyResponseSchema,
    StudentDealsSurveyStatusResponseSchema,
)
from app.services import survey_service

router = APIRouter()


async def parse_survey_request(request: Request) -> StudentDealsSurveyRequest:
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid request body")

    try:
        return StudentDealsSurveyRequest(**payload)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.errors())
    except TypeError:
        raise HTTPException(status_code=400, detail="Invalid request body")


@router.post(
    "/survey/student-deals",
    response_model=StudentDealsSurveyResponseSchema,
    status_code=201,
)
@limiter.limit("5/minute")
def submit_student_deals_survey(
    request: Request,
    survey_request: StudentDealsSurveyRequest = Depends(parse_survey_request),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return survey_service.submit_student_deals_survey(
        db=db,
        request=survey_request,
        responder_email=current_user.email,
    )


@router.get(
    "/survey/student-deals/status",
    response_model=StudentDealsSurveyStatusResponseSchema,
)
def get_student_deals_survey_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submitted = survey_service.has_student_deals_survey_submission(
        db=db,
        responder_email=current_user.email,
    )
    return {"submitted": submitted}
