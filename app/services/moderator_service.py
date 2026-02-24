import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import ModeratorApplication, User
from app.schemas.moderator_application import ModeratorApplyRequest


def _ensure_platform_superadmin(current_user: User):
    if current_user.role != "platform_superadmin":
        raise HTTPException(status_code=403, detail="Only platform superadmin can review applications")


def submit_moderator_application(
    db: Session,
    current_user: User,
    request: ModeratorApplyRequest,
):
    try:
        existing_pending = (
            db.query(ModeratorApplication)
            .filter(
                ModeratorApplication.user_id == current_user.id,
                ModeratorApplication.status == "pending",
            )
            .first()
        )

        if existing_pending:
            raise HTTPException(
                status_code=409,
                detail="Pending application already exists",
            )

        application = ModeratorApplication(
            id=uuid.uuid4(),
            user_id=current_user.id,
            full_name=request.full_name,
            phone_number=request.phone_number,
            branch=request.branch,
            year=request.year,
            motivation=request.motivation,
            status="pending",
        )

        db.add(application)
        db.commit()
        db.refresh(application)

        return {
            "application_id": application.id,
            "status": application.status,
            "message": "Application submitted successfully.",
        }
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Pending application already exists",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to submit application",
        )


def list_moderator_applications(
    db: Session,
    current_user: User,
    status: str = "pending",
):
    _ensure_platform_superadmin(current_user)

    q = db.query(ModeratorApplication)
    if status in {"pending", "approved", "rejected"}:
        q = q.filter(ModeratorApplication.status == status)

    applications = q.order_by(ModeratorApplication.created_at.desc()).all()
    user_ids = list({item.user_id for item in applications if item.user_id})
    user_email_map = {}
    if user_ids:
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        user_email_map = {u.id: u.email for u in users}

    return [
        {
            "application_id": item.id,
            "user_id": item.user_id,
            "applicant_name": item.full_name,
            "applicant_email": user_email_map.get(item.user_id) if item.user_id else None,
            "phone_number": item.phone_number,
            "branch": item.branch,
            "year": item.year,
            "motivation": item.motivation,
            "status": item.status,
            "created_at": item.created_at,
            "reviewed_at": item.reviewed_at,
            "reviewed_by": item.reviewed_by,
        }
        for item in applications
    ]


def review_moderator_application(
    db: Session,
    current_user: User,
    application_id,
    action: str,
):
    _ensure_platform_superadmin(current_user)

    application = (
        db.query(ModeratorApplication)
        .filter(ModeratorApplication.id == application_id)
        .first()
    )

    if not application:
        raise HTTPException(status_code=404, detail="Moderator application not found")

    if application.status != "pending":
        raise HTTPException(status_code=409, detail="Application already reviewed")

    application.status = "approved" if action == "approve" else "rejected"
    application.reviewed_at = datetime.now(timezone.utc)
    application.reviewed_by = current_user.id

    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "application_id": application.id,
        "status": application.status,
        "message": f"Application {application.status}.",
    }
