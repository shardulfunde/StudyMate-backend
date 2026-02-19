from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.role_assignment import RoleAssignment


def get_user_capabilities(db: Session, user: User):

    if user.role == "platform_superadmin":
        return {
            "isPlatformSuperadmin": True,
            "managedColleges": "ALL",
            "managedPrograms": "ALL",
            "managedYears": "ALL",
            "managedSubjects": "ALL"
        }

    scoped_roles = (
        db.query(RoleAssignment)
        .filter(RoleAssignment.user_id == user.id)
        .all()
    )

    managed_colleges = []
    managed_programs = []
    managed_years = []
    managed_subjects = []

    for r in scoped_roles:
        if r.role_type == "college_superadmin":
            managed_colleges.append(str(r.scope_id))
        elif r.role_type == "program_admin":
            managed_programs.append(str(r.scope_id))
        elif r.role_type == "year_admin":
            managed_years.append(str(r.scope_id))
        elif r.role_type == "subject_admin":
            managed_subjects.append(str(r.scope_id))

    return {
        "isPlatformSuperadmin": False,
        "managedColleges": managed_colleges,
        "managedPrograms": managed_programs,
        "managedYears": managed_years,
        "managedSubjects": managed_subjects
    }

