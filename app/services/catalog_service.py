import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Program, Year, Subject, Resource, User, RoleAssignment
from app.services import authority_service


# ============================================================
# READ OPERATIONS
# ============================================================

def get_programs(db: Session, current_user: User):
    programs = (
        db.query(Program)
        .filter(Program.college_id == current_user.college_id)
        .order_by(Program.name)
        .all()
    )
    return [{"id": str(p.id), "name": p.name} for p in programs]


def get_years(db: Session, current_user: User, program_id: str = None):
    q = db.query(Year).filter(Year.college_id == current_user.college_id)

    if program_id:
        q = q.filter(Year.program_id == program_id)

    years = q.order_by(Year.year_number).all()

    return [
        {
            "id": str(y.id),
            "year_number": y.year_number,
            "program_id": str(y.program_id),
            "program_name": y.program.name if y.program else None,
        }
        for y in years
    ]


# ============================================================
# CREATE OPERATIONS (unchanged)
# ============================================================

def create_program(db: Session, current_user: User, program_name: str):

    if not authority_service.can_manage(
        db, current_user, "college", current_user.college_id
    ):
        raise HTTPException(status_code=403, detail="Not allowed")

    existing = db.query(Program).filter(
        Program.name == program_name,
        Program.college_id == current_user.college_id,
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Program already exists")

    new_program = Program(
        id=uuid.uuid4(),
        name=program_name,
        college_id=current_user.college_id,
    )

    db.add(new_program)
    db.commit()
    db.refresh(new_program)

    return {
        "message": "Program created successfully",
        "program_id": str(new_program.id),
    }


def create_year(db: Session, current_user: User, program_id: str, year_number: int):

    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    if not authority_service.can_manage(db, current_user, "program", program_id):
        raise HTTPException(status_code=403, detail="Not allowed")

    new_year = Year(
        id=uuid.uuid4(),
        program_id=program_id,
        year_number=year_number,
        college_id=program.college_id,
    )

    db.add(new_year)
    db.commit()
    db.refresh(new_year)

    return {
        "message": "Year created successfully",
        "year_id": str(new_year.id),
    }


def create_subject(db: Session, current_user: User, year_id: str, subject_name: str):

    year = db.query(Year).filter(Year.id == year_id).first()
    if not year:
        raise HTTPException(status_code=404, detail="Year not found")

    if not authority_service.can_manage(db, current_user, "year", year_id):
        raise HTTPException(status_code=403, detail="Not allowed")

    existing = db.query(Subject).filter(
        Subject.year_id == year_id,
        Subject.name == subject_name,
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Subject already exists")

    new_subject = Subject(
        id=uuid.uuid4(),
        name=subject_name,
        year_id=year_id,
        college_id=year.college_id,
    )

    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)

    return {
        "message": "Subject created successfully",
        "subject_id": str(new_subject.id),
    }


# ============================================================
# DELETE PROGRAM
# ============================================================

def delete_program(db: Session, current_user: User, program_id: str):
    try:
        program = (
            db.query(Program)
            .filter(Program.id == program_id)
            .with_for_update()
            .first()
        )

        if not program:
            raise HTTPException(status_code=404, detail="Program not found")

        if not authority_service.can_manage(db, current_user, "program", program_id):
            raise HTTPException(status_code=403, detail="Not allowed")

        year_count = db.query(Year).filter(
            Year.program_id == program_id
        ).count()

        if year_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete program. It contains {year_count} year(s).",
            )

        db.query(RoleAssignment).filter(
            RoleAssignment.scope_type == "program",
            RoleAssignment.scope_id == program_id,
        ).delete(synchronize_session=False)

        db.delete(program)
        db.commit()

        return {"message": "Program deleted successfully"}

    except:
        db.rollback()
        raise


# ============================================================
# DELETE YEAR
# ============================================================

def delete_year(db: Session, current_user: User, year_id: str):
    try:
        year = (
            db.query(Year)
            .filter(Year.id == year_id)
            .with_for_update()
            .first()
        )

        if not year:
            raise HTTPException(status_code=404, detail="Year not found")

        if not authority_service.can_manage(db, current_user, "year", year_id):
            raise HTTPException(status_code=403, detail="Not allowed")

        subject_count = db.query(Subject).filter(
            Subject.year_id == year_id
        ).count()

        if subject_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete year. It contains {subject_count} subject(s).",
            )

        db.query(RoleAssignment).filter(
            RoleAssignment.scope_type == "year",
            RoleAssignment.scope_id == year_id,
        ).delete(synchronize_session=False)

        db.delete(year)
        db.commit()

        return {"message": "Year deleted successfully"}

    except:
        db.rollback()
        raise


# ============================================================
# DELETE SUBJECT
# ============================================================

def delete_subject(db: Session, current_user: User, subject_id: str):
    try:
        subject = (
            db.query(Subject)
            .filter(Subject.id == subject_id)
            .with_for_update()
            .first()
        )

        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")

        if not authority_service.can_manage(db, current_user, "subject", subject_id):
            raise HTTPException(status_code=403, detail="Not allowed")

        active_resources = db.query(Resource).filter(
            Resource.subject_id == subject_id,
            Resource.is_active == True,
        ).count()

        if active_resources > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete subject. It contains {active_resources} active resource(s).",
            )

        db.query(RoleAssignment).filter(
            RoleAssignment.scope_type == "subject",
            RoleAssignment.scope_id == subject_id,
        ).delete(synchronize_session=False)

        db.delete(subject)
        db.commit()

        return {"message": "Subject deleted successfully"}

    except:
        db.rollback()
        raise
