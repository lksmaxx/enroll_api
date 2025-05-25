from pydantic import BaseModel, Field, field_validator, model_validator
from app.utils.validators import validate_cpf_format, format_cpf, validate_name, validate_age, validate_enrollment_data

class EnrollmentBase(BaseModel):
    name: str = Field(..., description="The name of the student", min_length=1)
    age: int = Field(..., description="The age of the student", gt=0, le=120)
    cpf: str = Field(..., description="The CPF of the student", min_length=1)

    @field_validator('name')
    @classmethod
    def validate_name_field(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        
        if not validate_name(v):
            raise ValueError('Nome deve ter pelo menos 2 caracteres e conter letras')
        
        return v.strip()

    @field_validator('age')
    @classmethod
    def validate_age_field(cls, v):
        if not validate_age(v):
            raise ValueError('Idade deve ser um número entre 1 e 120')
        return v

    @field_validator('cpf')
    @classmethod
    def validate_cpf_field(cls, v):
        if not v or not v.strip():
            raise ValueError('CPF é obrigatório')
        
        formatted_cpf = format_cpf(v)
        if not validate_cpf_format(formatted_cpf):
            raise ValueError('CPF inválido - verifique o formato e os dígitos verificadores')
        return formatted_cpf

    @model_validator(mode='after')
    def validate_enrollment(self):
        """Validação adicional de todo o modelo"""
        errors = validate_enrollment_data(self.name, self.age, self.cpf)
        if errors:
            raise ValueError(f"Dados inválidos: {'; '.join(errors)}")
        return self

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentStatus(BaseModel):
    id: str
    status: str
    message: str | None = None
    age_group_id: str | None = None 