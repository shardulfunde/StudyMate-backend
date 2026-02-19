from pydantic import BaseModel


class ScopeAssignment(BaseModel):
    target_email: str
    subject_id: str
