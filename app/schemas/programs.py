from pydantic import BaseModel


class ProgramCreate(BaseModel):
    program_name: str


class ProgramDelete(BaseModel):
    program_id: str
