import secrets
import base64
import json
import os
from typing import Optional, Dict, Tuple, List
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.config.config import config


# Instância do HTTPBasic para FastAPI
security = HTTPBasic()


class BasicAuthManager:
    """Gerenciador de autenticação Basic Auth"""
    
    def __init__(self):
        self.users = self._load_users()
        self.users_metadata = {}
    
    def _load_users_from_file(self) -> Tuple[Dict[str, Dict], Dict]:
        """Carrega usuários do arquivo JSON"""
        try:
            # Tenta diferentes caminhos para o arquivo
            possible_paths = [
                config.USERS_FILE_PATH,
                os.path.join(os.getcwd(), config.USERS_FILE_PATH),
                os.path.join(os.path.dirname(__file__), "..", "config", "users.json"),
                "users.json"
            ]
            
            users_data = None
            used_path = None
            
            for path in possible_paths:
                try:
                    if os.path.exists(path):
                        with open(path, 'r', encoding='utf-8') as file:
                            users_data = json.load(file)
                            used_path = path
                            break
                except Exception as e:
                    print(f"Erro ao tentar ler arquivo {path}: {e}")
                    continue
            
            if not users_data:
                print(f"⚠️ Arquivo de usuários não encontrado. Tentativas: {possible_paths}")
                return {}, {}
            
            print(f"✅ Usuários carregados do arquivo: {used_path}")
            
            # Processa os usuários do arquivo
            users = {}
            for user_data in users_data.get("users", []):
                username = user_data.get("username")
                if username:
                    users[username] = {
                        "password": user_data.get("password"),
                        "role": user_data.get("role", "user"),
                        "description": user_data.get("description", "")
                    }
            
            metadata = users_data.get("metadata", {})
            print(f"📊 Carregados {len(users)} usuários do arquivo (versão: {metadata.get('version', 'N/A')})")
            
            return users, metadata
            
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo de usuários: {e}")
            return {}, {}
    
    def _load_users_from_env(self) -> Dict[str, Dict]:
        """Carrega usuários das variáveis de ambiente (fallback)"""
        print("⚠️ Usando fallback: carregando usuários das variáveis de ambiente")
        users = {}
        
        # Adiciona usuário padrão
        users[config.BASIC_AUTH_USERNAME] = {
            "password": config.BASIC_AUTH_PASSWORD,
            "role": "admin",
            "description": "Usuário padrão das variáveis de ambiente"
        }
        
        # Adiciona usuários múltiplos se configurados
        if config.BASIC_AUTH_USERS:
            try:
                for user_pass in config.BASIC_AUTH_USERS.split(','):
                    if ':' in user_pass:
                        username, password = user_pass.strip().split(':', 1)
                        users[username] = {
                            "password": password,
                            "role": "admin" if username == "admin" else "user",
                            "description": "Usuário das variáveis de ambiente"
                        }
            except Exception as e:
                print(f"Erro ao carregar usuários das variáveis de ambiente: {e}")
        
        return users
    
    def _load_users(self) -> Dict[str, Dict]:
        """Carrega usuários do arquivo ou fallback para variáveis de ambiente"""
        # Tenta carregar do arquivo primeiro
        users, metadata = self._load_users_from_file()
        self.users_metadata = metadata
        
        # Se não conseguiu carregar do arquivo, usa variáveis de ambiente
        if not users:
            users = self._load_users_from_env()
        
        # Log dos usuários carregados (sem senhas)
        print("👥 Usuários disponíveis:")
        for username, user_data in users.items():
            print(f"  - {username} ({user_data['role']}): {user_data['description']}")
        
        return users
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """Verifica se as credenciais são válidas"""
        if username not in self.users:
            return False
        
        stored_password = self.users[username]["password"]
        # Usa secrets.compare_digest para evitar timing attacks
        return secrets.compare_digest(stored_password, password)
    
    def get_user_info(self, username: str) -> Optional[Dict[str, str]]:
        """Retorna informações do usuário autenticado"""
        if username in self.users:
            user_data = self.users[username]
            return {
                "username": username,
                "role": user_data["role"],
                "description": user_data["description"]
            }
        return None
    
    def list_users(self) -> List[Dict[str, str]]:
        """Lista todos os usuários (sem senhas) - para debugging"""
        return [
            {
                "username": username,
                "role": user_data["role"],
                "description": user_data["description"]
            }
            for username, user_data in self.users.items()
        ]
    
    def reload_users(self) -> bool:
        """Recarrega usuários do arquivo"""
        try:
            new_users, new_metadata = self._load_users_from_file()
            if new_users:
                self.users = new_users
                self.users_metadata = new_metadata
                print("🔄 Usuários recarregados com sucesso")
                return True
            else:
                print("❌ Falha ao recarregar usuários")
                return False
        except Exception as e:
            print(f"❌ Erro ao recarregar usuários: {e}")
            return False


# Instância global do gerenciador
auth_manager = BasicAuthManager()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> Dict[str, str]:
    """
    Dependency para verificar autenticação Basic Auth
    Retorna informações do usuário autenticado
    """
    if not auth_manager.verify_credentials(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    user_info = auth_manager.get_user_info(credentials.username)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user_info


def get_admin_user(current_user: Dict[str, str] = Depends(get_current_user)) -> Dict[str, str]:
    """
    Dependency para verificar se o usuário é admin
    Usado para endpoints que requerem privilégios administrativos
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Privilégios administrativos necessários."
        )
    
    return current_user


def decode_basic_auth(authorization: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Decodifica header Authorization Basic Auth
    Útil para testes e debugging
    """
    try:
        if not authorization.startswith("Basic "):
            return None, None
        
        encoded_credentials = authorization.split(" ", 1)[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        
        if ":" not in decoded_credentials:
            return None, None
        
        username, password = decoded_credentials.split(":", 1)
        return username, password
    
    except Exception:
        return None, None


def create_basic_auth_header(username: str, password: str) -> str:
    """
    Cria header Authorization para Basic Auth
    Útil para testes
    """
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded_credentials}" 