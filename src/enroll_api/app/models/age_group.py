from pydantic import BaseModel, Field, field_validator, model_validator

class AgeGroup(BaseModel):
    id: str
    min_age: int
    max_age: int

class AgeGroupCreate(BaseModel):
    min_age: int = Field(..., description="Idade mínima do grupo", ge=0, le=120)
    max_age: int = Field(..., description="Idade máxima do grupo", ge=0, le=120)

    @field_validator('min_age')
    @classmethod
    def validate_min_age(cls, v):
        if not isinstance(v, int) or v < 0 or v > 120:
            raise ValueError('Idade mínima deve ser um número entre 0 e 120')
        return v

    @field_validator('max_age')
    @classmethod
    def validate_max_age(cls, v):
        if not isinstance(v, int) or v < 0 or v > 120:
            raise ValueError('Idade máxima deve ser um número entre 0 e 120')
        return v

    @model_validator(mode='after')
    def validate_age_range(self):
        """Valida se min_age <= max_age"""
        if self.min_age > self.max_age:
            raise ValueError('Idade mínima não pode ser maior que a idade máxima')
        
        if self.min_age == self.max_age:
            raise ValueError('Idade mínima e máxima não podem ser iguais')
        
        return self

class AgeGroupUpdate(BaseModel):
    min_age: int = Field(..., description="Idade mínima do grupo", ge=0, le=120)
    max_age: int = Field(..., description="Idade máxima do grupo", ge=0, le=120)

    @field_validator('min_age')
    @classmethod
    def validate_min_age(cls, v):
        if not isinstance(v, int) or v < 0 or v > 120:
            raise ValueError('Idade mínima deve ser um número entre 0 e 120')
        return v

    @field_validator('max_age')
    @classmethod
    def validate_max_age(cls, v):
        if not isinstance(v, int) or v < 0 or v > 120:
            raise ValueError('Idade máxima deve ser um número entre 0 e 120')
        return v

    @model_validator(mode='after')
    def validate_age_range(self):
        """Valida se min_age <= max_age"""
        if self.min_age > self.max_age:
            raise ValueError('Idade mínima não pode ser maior que a idade máxima')
        
        if self.min_age == self.max_age:
            raise ValueError('Idade mínima e máxima não podem ser iguais')
        
        return self
