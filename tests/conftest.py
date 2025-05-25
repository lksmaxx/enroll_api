import pytest
import requests
import time
import os
import json
import base64
import sys
from typing import Generator, Dict, Any
from pymongo import MongoClient
import pika
from fastapi.testclient import TestClient as FastAPITestClient
from pymongo.errors import ServerSelectionTimeoutError

# Adiciona o path do src para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/enroll_api'))

# Configurações
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "enroll_api_test")

# Configurações de autenticação (usuários do arquivo)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "secret123"
USER_USERNAME = "config"
USER_PASSWORD = "config123"
MANAGER_USERNAME = "manager"
MANAGER_PASSWORD = "manager789"
OPERATOR_USERNAME = "operator"
OPERATOR_PASSWORD = "operator456"

# Configuração de ambiente para testes (localhost para testes locais)
os.environ["MONGO_HOST"] = "localhost"
os.environ["MONGO_PORT"] = "27017"
# Remover autenticação para testes locais
if "MONGO_INITDB_ROOT_USERNAME" in os.environ:
    del os.environ["MONGO_INITDB_ROOT_USERNAME"]
if "MONGO_INITDB_ROOT_PASSWORD" in os.environ:
    del os.environ["MONGO_INITDB_ROOT_PASSWORD"]
os.environ["RABBITMQ_HOST"] = "localhost"
os.environ["RABBITMQ_PORT"] = "5672"
os.environ["BASIC_AUTH_USERS"] = "admin:secret123,config:config123,test:test123"

# Import da aplicação após configurar variáveis de ambiente
from app.main import app

def clean_db():
    """Função utilitária para limpar completamente o banco e fila"""
    import pika
    from pymongo import MongoClient
    
    # Limpa MongoDB
    try:
        mongo_client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        db = mongo_client.enrollment_db
        
        # Limpa as coleções
        deleted_enrollments = db.enrollments.delete_many({}).deleted_count
        deleted_age_groups = db.age_groups.delete_many({}).deleted_count
        
        print(f"[CLEAN_DB] MongoDB limpo: {deleted_enrollments} enrollments, {deleted_age_groups} age_groups removidos")
        mongo_client.close()
    except Exception as e:
        print(f"[CLEAN_DB] Erro ao limpar MongoDB: {e}")
    
    # Limpa fila RabbitMQ
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
        channel = connection.channel()
        
        # Purga a fila (remove todas as mensagens)
        method = channel.queue_purge(queue='enrollment_queue')
        purged_count = method.method.message_count if method and hasattr(method, 'method') else 0
        
        print(f"[CLEAN_DB] RabbitMQ limpo: {purged_count} mensagens removidas da fila")
        
        connection.close()
    except Exception as e:
        print(f"[CLEAN_DB] Erro ao limpar RabbitMQ: {e}")

class APITestClient:
    """Cliente de teste personalizado com verificação de conectividade"""
    
    def __init__(self):
        self.client = FastAPITestClient(app)
        self._verify_connectivity()
    
    def _verify_connectivity(self):
        """Verifica se a API está respondendo"""
        try:
            response = self.client.get("/")
            if response.status_code != 200:
                raise Exception(f"API não está respondendo corretamente: {response.status_code}")
        except Exception as e:
            raise Exception(f"Erro ao conectar à API: {e}")
    
    def __getattr__(self, name):
        """Delega chamadas para o cliente FastAPI"""
        return getattr(self.client, name)

@pytest.fixture(scope="session")
def api_client():
    """Fixture que fornece um cliente de teste para toda a sessão"""
    return APITestClient()

@pytest.fixture(scope="session")
def unauthenticated_client() -> Generator[APITestClient, None, None]:
    """Fixture que fornece um cliente sem autenticação"""
    client = APITestClient()
    yield client

@pytest.fixture(scope="session")
def admin_client() -> Generator[APITestClient, None, None]:
    """Fixture que fornece um cliente com privilégios administrativos"""
    client = APITestClient()
    yield client

@pytest.fixture(scope="session")
def manager_client() -> Generator[APITestClient, None, None]:
    """Fixture que fornece um cliente manager (também admin)"""
    client = APITestClient()
    yield client

@pytest.fixture(scope="session")
def user_client() -> Generator[APITestClient, None, None]:
    """Fixture que fornece um cliente com privilégios de usuário"""
    client = APITestClient()
    yield client

@pytest.fixture(scope="session")
def operator_client() -> Generator[APITestClient, None, None]:
    """Fixture que fornece um cliente operador (usuário comum)"""
    client = APITestClient()
    yield client

@pytest.fixture(scope="session")
def mongo_client():
    """Fixture que fornece um cliente MongoDB para verificações diretas"""
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        # Testa a conexão
        client.admin.command('ping')
        yield client
    except Exception as e:
        pytest.skip(f"MongoDB não disponível: {e}")
    finally:
        if 'client' in locals():
            client.close()

@pytest.fixture(scope="function")
def clean_database(mongo_client):
    """Fixture que limpa o banco de dados e fila antes de cada teste"""
    import pika
    
    # Usa o banco correto (enrollment_db é o padrão da aplicação)
    db = mongo_client.enrollment_db
    
    # Limpa as coleções antes do teste
    db.age_groups.delete_many({})
    db.enrollments.delete_many({})
    
    # Limpa a fila RabbitMQ também
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
        channel = connection.channel()
        channel.queue_purge(queue='enrollment_queue')
        connection.close()
    except Exception as e:
        print(f"[CLEAN_DATABASE] Aviso: Não foi possível limpar RabbitMQ: {e}")
    
    yield
    
    # Limpa as coleções após o teste
    db.age_groups.delete_many({})
    db.enrollments.delete_many({})
    
    # Limpa a fila RabbitMQ novamente após o teste
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
        channel = connection.channel()
        channel.queue_purge(queue='enrollment_queue')
        connection.close()
    except Exception as e:
        print(f"[CLEAN_DATABASE] Aviso: Não foi possível limpar RabbitMQ após teste: {e}")

@pytest.fixture
def sample_age_groups(api_client: APITestClient, clean_database):
    """Fixture que cria age groups de exemplo para testes"""
    auth_header = create_basic_auth_header("admin", "secret123")
    
    age_groups_data = [
        {"min_age": 18, "max_age": 25},
        {"min_age": 26, "max_age": 35},
        {"min_age": 36, "max_age": 50}
    ]
    
    created_groups = []
    for age_group_data in age_groups_data:
        response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": auth_header})
        if response.status_code == 200:
            created_groups.append(response.json())
    
    return created_groups

@pytest.fixture
def valid_enrollment_data():
    """Fixture que fornece dados válidos para enrollment"""
    return {
        "name": "João da Silva",
        "age": 22,
        "cpf": "11144477735"  # CPF matematicamente válido
    }

@pytest.fixture
def invalid_enrollment_data():
    """Fixture que fornece dados inválidos para enrollment"""
    return [
        {"name": "", "age": 25, "cpf": "11144477735"},  # Nome vazio
        {"age": 25, "cpf": "11144477735"},  # Nome faltando
        {"name": "João", "cpf": "11144477735"},  # Idade faltando
        {"name": "João", "age": 25},  # CPF faltando
        {"name": "João", "age": "abc", "cpf": "11144477735"},  # Idade inválida
        {"name": "João", "age": -1, "cpf": "11144477735"},  # Idade negativa
    ]

def create_basic_auth_header(username: str, password: str) -> str:
    """Cria header de autenticação Basic Auth"""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

def wait_for_enrollment_processing(api_client: APITestClient, enrollment_id: str, timeout: int = 15) -> bool:
    """Aguarda o processamento de um enrollment pelo worker"""
    auth_header = create_basic_auth_header("config", "config123")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = api_client.client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": auth_header})
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                
                if status == "processed":
                    return True
                elif status in ["failed", "error"]:
                    print(f"Enrollment {enrollment_id} falhou: {data.get('message', 'Sem mensagem')}")
                    return False
                # Se status é "pending", continua aguardando
            else:
                print(f"Erro ao buscar status do enrollment {enrollment_id}: {response.status_code}")
                
        except Exception as e:
            print(f"Erro ao verificar status do enrollment {enrollment_id}: {e}")
        
        time.sleep(0.5)  # Aguarda meio segundo antes de tentar novamente
    
    # Timeout atingido
    try:
        response = api_client.client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": auth_header})
        if response.status_code == 200:
            final_status = response.json().get("status", "unknown")
            print(f"Timeout: Enrollment {enrollment_id} ainda está com status '{final_status}' após {timeout}s")
        else:
            print(f"Timeout: Não foi possível verificar status final do enrollment {enrollment_id}")
    except Exception as e:
        print(f"Timeout: Erro ao verificar status final: {e}")
    
    raise TimeoutError(f"Enrollment {enrollment_id} não foi processado no tempo esperado ({timeout}s)") 