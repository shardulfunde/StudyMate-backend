from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.db.session import SessionLocal
from app.db.models import User
from app.utils.constants import WCE_COLLEGE_ID
from app.services.auth_service import ensure_user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(decoded_token=Depends(verify_token), db: Session = Depends(get_db)):
    uid = decoded_token["uid"]
    email = decoded_token.get("email")
    user = ensure_user(db, uid, email, WCE_COLLEGE_ID)
    return user
