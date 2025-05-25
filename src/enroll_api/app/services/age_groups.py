from app.db.mongo import mongo_db
from app.models.age_group import AgeGroup, AgeGroupCreate, AgeGroupUpdate
from bson import ObjectId

async def create_age_group(age_group: AgeGroupCreate):
    age_group_dict = age_group.model_dump()
    result = mongo_db.age_groups.insert_one(age_group_dict)
    created_age_group = mongo_db.age_groups.find_one({"_id": result.inserted_id})
    created_age_group["id"] = str(created_age_group.pop("_id"))
    return created_age_group

async def get_age_group(age_group_id: str):
    result = mongo_db.age_groups.find_one({"_id": ObjectId(age_group_id)})
    if result:
        result["id"] = str(result.pop("_id"))
    return result

async def get_all_age_groups():
    result = mongo_db.age_groups.find()
    age_groups = []
    for doc in result:
        doc["id"] = str(doc.pop("_id"))
        age_groups.append(doc)
    return age_groups

async def update_age_group(age_group_id: str, age_group: AgeGroupUpdate):
    result = mongo_db.age_groups.update_one(
        {"_id": ObjectId(age_group_id)}, 
        {"$set": age_group.model_dump()}
    )
    if result.modified_count > 0:
        updated = mongo_db.age_groups.find_one({"_id": ObjectId(age_group_id)})
        updated["id"] = str(updated.pop("_id"))
        return updated
    return None

async def delete_age_group(age_group_id: str):
    result = mongo_db.age_groups.delete_one({"_id": ObjectId(age_group_id)})
    return result.deleted_count


