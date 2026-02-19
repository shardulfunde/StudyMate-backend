from pydantic import BaseModel


class SubjectCreate(BaseModel):
    year_id: str
    subject_name: str


class SubjectDelete(BaseModel):
    subject_id: str
