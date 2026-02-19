from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.services.capability_service import get_user_capabilities
from app.db.models.user import User

router = APIRouter()


@router.get("/me/capabilities")
def get_capabilities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_capabilities(db, current_user)
