from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.db.models import User
from app.schemas.moderator_application import (
    ModeratorApplyRequest,
    ModeratorApplyResponse,
    ModeratorDecisionRequest,
)
from app.services import moderator_service

router = APIRouter()


async def parse_moderator_apply_request(request: Request) -> ModeratorApplyRequest:
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid request body")

    try:
        return ModeratorApplyRequest(**payload)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.errors())
    except TypeError:
        raise HTTPException(status_code=400, detail="Invalid request body")


@router.post("/moderator/apply", response_model=ModeratorApplyResponse, status_code=200)
def apply_for_moderator(
    apply_request: ModeratorApplyRequest = Depends(parse_moderator_apply_request),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return moderator_service.submit_moderator_application(
        db=db,
        current_user=current_user,
        request=apply_request,
    )


@router.get("/moderator/applications")
def list_applications(
    status: str = "pending",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return moderator_service.list_moderator_applications(
        db=db,
        current_user=current_user,
        status=status,
    )


@router.post("/moderator/applications/{application_id}/decision")
def review_application(
    application_id: str,
    request: ModeratorDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return moderator_service.review_moderator_application(
        db=db,
        current_user=current_user,
        application_id=application_id,
        action=request.action,
    )
