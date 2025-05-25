from pydantic import BaseModel

class AgeGroup(BaseModel):
    id: str
    min_age: int
    max_age: int

class AgeGroupCreate(BaseModel):
    min_age: int
    max_age: int

class AgeGroupUpdate(BaseModel):
    min_age: int
    max_age: int
