from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.schemas import RoleAssignment, ScopeAssignment
from app.services import admin_service
from app.db.models import User

router = APIRouter()


@router.post("/assign-role")
def assign_role(
    request: RoleAssignment,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return admin_service.assign_role(
        db=db,
        current_user=current_user,
        target_user_id=request.target_user_id,
        target_email=request.target_email,
        role_type=request.role_type,
        scope_type=request.scope_type,
        scope_id=request.scope_id,
    )


@router.post("/assign-scope")
def assign_scope(
    request: ScopeAssignment,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return admin_service.assign_scope_deprecated()
