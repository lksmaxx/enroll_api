from fastapi import FastAPI
from app.endpoints import age_groups
from app.endpoints import enrollment

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

app.include_router(age_groups.router, prefix="/age-groups", tags=["age-groups"])
app.include_router(enrollment.router, prefix="/enrollments", tags=["enrollments"])
