from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.models import User, RoleAssignment
from app.services import authority_service


def assign_role(
    db: Session,
    current_user: User,
    role_type: str,
    scope_type: str,
    scope_id,
    target_user_id: str = None,
    target_email: str = None,
):

    
    if role_type == "platform_superadmin":
        raise HTTPException(
            status_code=403,
            detail="Platform superadmin role cannot be assigned here",
        )

    
    target_user = None

    if target_user_id:
        target_user = db.query(User).filter(User.id == target_user_id).first()

    if not target_user and target_email:
        target_user = db.query(User).filter(User.email == target_email).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    
    if current_user.role != "platform_superadmin":
        if target_user.college_id != current_user.college_id:
            raise HTTPException(
                status_code=403,
                detail="Cross-college role assignment not allowed",
            )
            
    
    allowed = authority_service.can_assign_role(
        db=db,
        assigner=current_user,
        target_role_type=role_type,
        target_scope_type=scope_type,
        target_scope_id=scope_id,
    )

    if not allowed:
        raise HTTPException(status_code=403, detail="Not allowed")

    
    existing = (
        db.query(RoleAssignment)
        .filter(
            RoleAssignment.user_id == target_user.id,
            RoleAssignment.role_type == role_type,
            RoleAssignment.scope_type == scope_type,
            RoleAssignment.scope_id == scope_id,
        )
        .first()
    )

    if existing:
        return {
            "message": "Role already assigned",
            "user": target_user.id,
            "role_type": role_type,
            "scope_type": scope_type,
            "scope_id": str(scope_id),
        }

    try:
        assignment = RoleAssignment(
            user_id=target_user.id,
            role_type=role_type,
            scope_type=scope_type,
            scope_id=scope_id,
        )
        db.add(assignment)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role assignment conflict",
        )

    return {
        "message": "Role assigned successfully",
        "user": target_user.id,
        "role_type": role_type,
        "scope_type": scope_type,
        "scope_id": str(scope_id),
    }
