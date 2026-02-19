from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.db.models import College, User, Subject
from app.db.models import RoleAssignment

router = APIRouter()


@router.get("/")
def root(current_user: User = Depends(get_current_user)):
    return {"message": "StudyMate backend is running!"}


@router.get("/colleges")
def get_colleges(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(College).filter(
        College.id == current_user.college_id
    ).all()




@router.get("/users")
def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

 
    if current_user.role == "platform_superadmin":
        users = db.query(User).all()

    else:
        has_admin_role = db.query(RoleAssignment).filter(
            RoleAssignment.user_id == current_user.id
        ).first()

        if not has_admin_role:
            raise HTTPException(status_code=403, detail="Not Allowed")


        users = db.query(User).filter(
            User.college_id == current_user.college_id
        ).all()

    return [
        {
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]


@router.get("/subjects")
def get_subjects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subjects = db.query(Subject).filter(
        Subject.college_id == current_user.college_id
    ).all()

    return [
        {
            "id": str(s.id),
            "subject": s.name,
            "year_id": str(s.year_id) if s.year_id else None,
            "program_id": str(s.year.program_id) if s.year and s.year.program_id else None,
            "Year": s.year.year_number if s.year else None,
            "Program": s.year.program.name if s.year and s.year.program else None
        }
        for s in subjects
    ]
