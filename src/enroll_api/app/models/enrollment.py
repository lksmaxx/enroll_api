from pydantic import BaseModel, Field

class EnrollmentBase(BaseModel):
    name: str = Field(..., description="The name of the student")
    age: int = Field(..., description="The age of the student")
    cpf: str = Field(..., description="The CPF of the student")

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentStatus(BaseModel):
    id: str
    status: str
    message: str | None = None
    age_group_id: str | None = None 