from pydantic import BaseModel, Field, field_validator
from app.utils.validators import validate_cpf_format, format_cpf

class EnrollmentBase(BaseModel):
    name: str = Field(..., description="The name of the student")
    age: int = Field(..., description="The age of the student", gt=0, le=120)
    cpf: str = Field(..., description="The CPF of the student")

    @field_validator('cpf')
    @classmethod
    def validate_cpf_field(cls, v):
        formatted_cpf = format_cpf(v)
        if not validate_cpf_format(formatted_cpf):
            raise ValueError('CPF com formato inválido')
        return formatted_cpf

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentStatus(BaseModel):
    id: str
    status: str
    message: str | None = None
    age_group_id: str | None = None 