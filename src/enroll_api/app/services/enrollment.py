import uuid
import json
from app.db.mongo import mongo_db
from app.db.rabbitMQ import publish_message
from app.models.enrollment import EnrollmentCreate, EnrollmentStatus
from fastapi import HTTPException

# Função para verificar se a idade está em um age group válido
def find_valid_age_group(age: int):
    age_group = mongo_db.age_groups.find_one({
        "min_age": {"$lte": age},
        "max_age": {"$gte": age}
    })
    return age_group

# Função para publicar inscrição na fila
def publish_enrollment(enrollment: EnrollmentCreate) -> str:
    # Validar se a idade está em um age group válido
    age_group = find_valid_age_group(enrollment.age)
    if not age_group:
        raise HTTPException(
            status_code=400, 
            detail=f"Idade {enrollment.age} não está dentro de nenhum grupo de idade válido"
        )
    
    enrollment_id = str(uuid.uuid4())
    data = enrollment.model_dump()
    data["id"] = enrollment_id
    data["status"] = "pending"
    data["age_group_id"] = str(age_group["_id"])  # Adiciona referência do age group
    
    mongo_db.enrollments.insert_one({"_id": enrollment_id, **data})
    publish_message(json.dumps(data))
    return enrollment_id

def get_enrollment_status(enrollment_id: str) -> EnrollmentStatus:
    doc = mongo_db.enrollments.find_one({"_id": enrollment_id})
    if not doc:
        return None
    return EnrollmentStatus(
        id=doc["_id"], 
        status=doc.get("status", "unknown"), 
        message=doc.get("message"),
        age_group_id=doc.get("age_group_id")
    ) 


