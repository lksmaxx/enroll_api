from fastapi import APIRouter, HTTPException, Depends
from app.auth.basic_auth import get_admin_user, auth_manager
from typing import Dict, List

router = APIRouter()

@router.get("/users", response_model=List[Dict[str, str]])
def list_users(current_user: Dict[str, str] = Depends(get_admin_user)):
    """Lista todos os usuários (apenas admins)"""
    return auth_manager.list_users()

@router.get("/users/info")
def get_users_info(current_user: Dict[str, str] = Depends(get_admin_user)):
    """Retorna informações detalhadas sobre os usuários e configuração"""
    return {
        "users": auth_manager.list_users(),
        "total_users": len(auth_manager.users),
        "metadata": auth_manager.users_metadata,
        "source": "file" if auth_manager.users_metadata else "environment_variables"
    }

@router.post("/users/reload")
def reload_users(current_user: Dict[str, str] = Depends(get_admin_user)):
    """Recarrega usuários do arquivo (apenas admins)"""
    success = auth_manager.reload_users()
    
    if success:
        return {
            "message": "Usuários recarregados com sucesso",
            "users": auth_manager.list_users(),
            "total_users": len(auth_manager.users)
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Falha ao recarregar usuários do arquivo"
        )

@router.get("/system/auth-status")
def get_auth_status(current_user: Dict[str, str] = Depends(get_admin_user)):
    """Retorna status do sistema de autenticação"""
    return {
        "auth_system": "Basic Auth",
        "users_source": "file" if auth_manager.users_metadata else "environment_variables",
        "total_users": len(auth_manager.users),
        "admin_users": len([u for u in auth_manager.users.values() if u["role"] == "admin"]),
        "regular_users": len([u for u in auth_manager.users.values() if u["role"] == "user"]),
        "file_metadata": auth_manager.users_metadata,
        "current_user": current_user
    } 