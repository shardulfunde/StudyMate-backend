from sqlalchemy.orm import Session
from app.db.models import User


def ensure_user(db: Session, uid: str, email: str, college_id: str):
    user = db.query(User).filter(User.id == uid).first()

    if not user:
        user = User(
            id=uid,
            email=email,
            role="viewer",
            college_id=college_id,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
    return user
