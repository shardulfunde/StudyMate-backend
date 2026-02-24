from pydantic import BaseModel, validator


class ResourceRejectRequest(BaseModel):
    rejection_reason: str

    @validator("rejection_reason")
    def validate_rejection_reason(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("rejection_reason is required")
        return cleaned
