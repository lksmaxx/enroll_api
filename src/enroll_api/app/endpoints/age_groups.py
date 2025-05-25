from fastapi import APIRouter, HTTPException, Depends
from app.services.age_groups import create_age_group, get_age_group, get_all_age_groups, update_age_group, delete_age_group
from app.models.age_group import AgeGroup, AgeGroupCreate, AgeGroupUpdate
from app.auth.basic_auth import get_current_user, get_admin_user
from typing import Dict

router = APIRouter()

@router.post("/", response_model=AgeGroup)
async def create_age_group_endpoint(
    age_group: AgeGroupCreate,
    current_user: Dict[str, str] = Depends(get_admin_user)
):
    """Cria um novo age group (requer privilégios administrativos)"""
    return await create_age_group(age_group)

@router.get("/{age_group_id}", response_model=AgeGroup)
async def get_age_group_endpoint(
    age_group_id: str,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """Busca um age group por ID (requer autenticação)"""
    age_group = await get_age_group(age_group_id)
    if not age_group:
        raise HTTPException(status_code=404, detail="Age group not found")
    return age_group

@router.get("/", response_model=list[AgeGroup])
async def get_all_age_groups_endpoint(
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """Lista todos os age groups (requer autenticação)"""
    return await get_all_age_groups()

@router.put("/{age_group_id}", response_model=AgeGroup)
async def update_age_group_endpoint(
    age_group_id: str, 
    age_group: AgeGroupUpdate,
    current_user: Dict[str, str] = Depends(get_admin_user)
):
    """Atualiza um age group (requer privilégios administrativos)"""
    updated = await update_age_group(age_group_id, age_group)
    if not updated:
        raise HTTPException(status_code=404, detail="Age group not found")
    return updated

@router.delete("/{age_group_id}")
async def delete_age_group_endpoint(
    age_group_id: str,
    current_user: Dict[str, str] = Depends(get_admin_user)
):
    """Deleta um age group (requer privilégios administrativos)"""
    result = await delete_age_group(age_group_id)
    if result == 0:
        raise HTTPException(status_code=404, detail="Age group not found")
    return {"message": "Age group deleted successfully"}

