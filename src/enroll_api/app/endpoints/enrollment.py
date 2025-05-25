from fastapi import APIRouter, HTTPException
from app.models.enrollment import EnrollmentCreate, EnrollmentStatus
from app.services.enrollment import publish_enrollment, get_enrollment_status

router = APIRouter()

@router.post("/", response_model=dict)
def create_enrollment(enrollment: EnrollmentCreate):
    enrollment_id = publish_enrollment(enrollment)
    return {"id": enrollment_id, "status": "pending"}

@router.get("/{enrollment_id}", response_model=EnrollmentStatus)
def get_status(enrollment_id: str):
    status = get_enrollment_status(enrollment_id)
    if not status:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return status 