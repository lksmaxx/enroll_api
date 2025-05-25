from fastapi import FastAPI, Depends
from app.endpoints import age_groups
from app.endpoints import enrollment
from app.endpoints import admin
from app.auth.basic_auth import get_current_user
from typing import Dict

app = FastAPI(
    title="Enrollment API",
    description="API para gerenciamento de inscrições com autenticação Basic Auth",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """Endpoint público de health check"""
    return {
        "message": "Enrollment API está funcionando!",
        "version": "1.0.0",
        "auth": "Basic Auth required for protected endpoints"
    }

@app.get("/me")
def get_current_user_info(current_user: Dict[str, str] = Depends(get_current_user)):
    """Retorna informações do usuário autenticado"""
    return {
        "user": current_user,
        "message": "Usuário autenticado com sucesso"
    }

app.include_router(age_groups.router, prefix="/age-groups", tags=["age-groups"])
app.include_router(enrollment.router, prefix="/enrollments", tags=["enrollments"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
