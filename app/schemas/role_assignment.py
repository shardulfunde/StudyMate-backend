from pydantic import BaseModel
from uuid import UUID
from typing import Literal


class AssignRoleRequest(BaseModel):
    target_user_id: str
    role_type: Literal[
        "college_superadmin",
        "program_admin",
        "year_admin",
        "subject_admin",
    ]
    scope_type: Literal[
        "college",
        "program",
        "year",
        "subject",
    ]
    scope_id: UUID
