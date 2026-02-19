from pydantic import BaseModel, root_validator
from typing import Literal, Optional
from uuid import UUID


class RoleAssignment(BaseModel):
    target_user_id: Optional[str] = None
    target_email: Optional[str] = None
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

    @root_validator(skip_on_failure=True)
    def ensure_target_identifier(cls, values):
        uid, email = values.get("target_user_id"), values.get("target_email")
        if not uid and not email:
            raise ValueError("target_user_id or target_email is required")
        return values
