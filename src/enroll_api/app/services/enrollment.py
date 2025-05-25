import uuid
import json
from app.db.mongo import mongo_db
from app.db.rabbitMQ import publish_message
from app.models.enrollment import EnrollmentCreate, EnrollmentStatus

# Função para publicar inscrição na fila
def publish_enrollment(enrollment: EnrollmentCreate) -> str:
    enrollment_id = str(uuid.uuid4())
    data = enrollment.model_dump()
    data["id"] = enrollment_id
    data["status"] = "pending"
    mongo_db.enrollments.insert_one({"_id": enrollment_id, **data})
    publish_message(json.dumps(data))
    return enrollment_id

def get_enrollment_status(enrollment_id: str) -> EnrollmentStatus:
    doc = mongo_db.enrollments.find_one({"_id": enrollment_id})
    if not doc:
        return None
    return EnrollmentStatus(id=doc["_id"], status=doc.get("status", "unknown"), message=doc.get("message")) 


