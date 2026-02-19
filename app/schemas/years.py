from pydantic import BaseModel


class YearCreate(BaseModel):
    program_id: str
    year_number: int


class YearDelete(BaseModel):
    year_id: str
