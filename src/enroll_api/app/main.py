from fastapi import FastAPI
from app.endpoints import age_groups
from app.db.init_db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

app.include_router(age_groups.router, prefix="/age-groups", tags=["age-groups"])
