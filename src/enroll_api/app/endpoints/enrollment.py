from fastapi import APIRouter, HTTPException, Depends
from app.models.enrollment import EnrollmentCreate, EnrollmentStatus
from app.services.enrollment import publish_enrollment, get_enrollment_status
from app.auth.basic_auth import get_current_user
from typing import Dict

router = APIRouter()

@router.post("/", response_model=dict)
def create_enrollment(
    enrollment: EnrollmentCreate,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """Cria um novo enrollment (requer autenticação)"""
    enrollment_id = publish_enrollment(enrollment)
    return {"id": enrollment_id, "status": "pending"}

@router.get("/{enrollment_id}", response_model=EnrollmentStatus)
def get_status(
    enrollment_id: str,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """Busca o status de um enrollment (requer autenticação)"""
    status = get_enrollment_status(enrollment_id)
    if not status:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return status 