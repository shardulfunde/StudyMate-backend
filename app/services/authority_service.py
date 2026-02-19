from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.role_assignment import RoleAssignment
from app.db.models.program import Program
from app.db.models.year import Year
from app.db.models.subject import Subject


ROLE_RANK = {
    "platform_superadmin": 1,
    "college_superadmin": 2,
    "program_admin": 3,
    "year_admin": 4,
    "subject_admin": 5,
}

ROLE_SCOPE_MAP = {
    "college_superadmin": "college",
    "program_admin": "program",
    "year_admin": "year",
    "subject_admin": "subject",
}


def has_scoped_role(
    db: Session,
    user: User,
    role_type: str,
    scope_type: str,
    scope_id,
) -> bool:
    return (
        db.query(RoleAssignment)
        .filter(
            RoleAssignment.user_id == user.id,
            RoleAssignment.role_type == role_type,
            RoleAssignment.scope_type == scope_type,
            RoleAssignment.scope_id == scope_id,
        )
        .first()
        is not None
    )

def can_manage(
    db: Session,
    user: User,
    scope_type: str,
    scope_id,
) -> bool:
    if user.role == "platform_superadmin":
        return True

    if not scope_id:
        return False

 
    if scope_type == "college":
        return has_scoped_role(db, user, "college_superadmin", "college", scope_id)


    if scope_type == "program":
        program = db.query(Program).filter(Program.id == scope_id).first()
        if not program:
            return False

        return (
            has_scoped_role(db, user, "program_admin", "program", program.id)
            or has_scoped_role(db, user, "college_superadmin", "college", program.college_id)
        )


    if scope_type == "year":
        year = db.query(Year).filter(Year.id == scope_id).first()
        if not year:
            return False

        return (
            has_scoped_role(db, user, "year_admin", "year", year.id)
            or has_scoped_role(db, user, "program_admin", "program", year.program_id)
            or has_scoped_role(db, user, "college_superadmin", "college", year.college_id)
        )


    if scope_type == "subject":
        subject = db.query(Subject).filter(Subject.id == scope_id).first()
        if not subject:
            return False

        year = db.query(Year).filter(Year.id == subject.year_id).first()
        if not year:
            return False

        return (
            has_scoped_role(db, user, "subject_admin", "subject", subject.id)
            or has_scoped_role(db, user, "year_admin", "year", year.id)
            or has_scoped_role(db, user, "program_admin", "program", year.program_id)
            or has_scoped_role(db, user, "college_superadmin", "college", subject.college_id)
        )

    return False



def can_assign_role(
    db: Session,
    assigner: User,
    target_role_type: str,
    target_scope_type: str,
    target_scope_id,
) -> bool:

    expected_scope = ROLE_SCOPE_MAP.get(target_role_type)
    if expected_scope != target_scope_type:
        return False


    if assigner.role == "platform_superadmin":
        return True

    target_rank = ROLE_RANK.get(target_role_type)
    if not target_rank:
        return False

    assigner_roles = (
        db.query(RoleAssignment)
        .filter(RoleAssignment.user_id == assigner.id)
        .all()
    )

    if not assigner_roles:
        return False

    for role in assigner_roles:

        assigner_rank = ROLE_RANK.get(role.role_type)
        if not assigner_rank:
            continue

       
        if assigner_rank >= target_rank:
            continue

        if can_manage(db, assigner, target_scope_type, target_scope_id):
            return True

    return False


def can_manage_subject_resources(
    db: Session,
    user: User,
    subject_id: str
) -> bool:

    # 1. Platform superadmin
    if user.role == "platform_superadmin":
        return True

    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        return False

    # Cross-college guard
    if subject.college_id != user.college_id:
        return False

    year = db.query(Year).filter(Year.id == subject.year_id).first()
    if not year:
        return False

    # Direct subject admin
    if has_scoped_role(db, user, "subject_admin", "subject", subject.id):
        return True

    # Year admin
    if has_scoped_role(db, user, "year_admin", "year", year.id):
        return True

    # Program admin
    if has_scoped_role(db, user, "program_admin", "program", year.program_id):
        return True

    # College superadmin
    if has_scoped_role(db, user, "college_superadmin", "college", subject.college_id):
        return True

    return False
