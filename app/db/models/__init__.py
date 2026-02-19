from app.db.models.college import College
from app.db.models.user import User
from app.db.models.program import Program
from app.db.models.year import Year
from app.db.models.subject import Subject
from app.db.models.admin_scope import AdminScope
from app.db.models.resource import Resource
from app.db.models.role_assignment import RoleAssignment

__all__ = [
    "College",
    "User",
    "Program",
    "Year",
    "Subject",
    "AdminScope",
    "Resource",
    "RoleAssignment",
]
