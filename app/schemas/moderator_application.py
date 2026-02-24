from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, validator


class ModeratorApplyRequest(BaseModel):
    full_name: str
    phone_number: str
    branch: str
    year: int
    motivation: Optional[str] = None

    @validator("full_name")
    def validate_full_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("full_name is required")
        if len(cleaned) > 100:
            raise ValueError("full_name must be at most 100 characters")
        return cleaned

    @validator("phone_number")
    def validate_phone_number(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 10:
            raise ValueError("phone_number must be exactly 10 digits")
        return value

    @validator("branch")
    def validate_branch(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("branch is required")
        return cleaned

    @validator("year")
    def validate_year(cls, value: int) -> int:
        if value < 1 or value > 4:
            raise ValueError("year must be between 1 and 4")
        return value


class ModeratorApplyResponse(BaseModel):
    application_id: UUID
    status: Literal["pending"]
    message: str


class ModeratorApplicationItem(BaseModel):
    application_id: UUID
    user_id: Optional[str] = None
    applicant_name: str
    applicant_email: Optional[str] = None
    phone_number: str
    branch: str
    year: int
    motivation: Optional[str] = None
    status: Literal["pending", "approved", "rejected"]
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None


class ModeratorDecisionRequest(BaseModel):
    action: Literal["approve", "reject"]


class ModeratorDecisionResponse(BaseModel):
    application_id: UUID
    status: Literal["approved", "rejected"]
    message: str
