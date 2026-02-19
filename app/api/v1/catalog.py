from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas import ProgramCreate, YearCreate, SubjectCreate, ProgramDelete, SubjectDelete,YearDelete
from app.services import catalog_service
from app.db.models import User

router = APIRouter()


@router.get("/programs")
def get_programs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return catalog_service.get_programs(db, current_user)


@router.get("/years")
def get_years(
    program_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return catalog_service.get_years(db, current_user, program_id)


@router.post("/create-program")
def create_program(
    request: ProgramCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return catalog_service.create_program(db, current_user, request.program_name)


@router.post("/create-year")
def create_year(
    request: YearCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return catalog_service.create_year(db, current_user, request.program_id, request.year_number)


@router.post("/create-subject")
def create_subject(
    request: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return catalog_service.create_subject(db, current_user, request.year_id, request.subject_name)


@router.delete("/delete-program")
def delete_program(
    request: ProgramDelete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return catalog_service.delete_program(db, current_user, request.program_id)

@router.delete("/delete-year")
def delete_year(
    request: YearDelete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return catalog_service.delete_year(db, current_user, request.year_id)



@router.delete("/delete-subject")
def delete_subject(
    request: SubjectDelete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return catalog_service.delete_subject(db, current_user, request.subject_id)
