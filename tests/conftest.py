import pytest
import requests
import time
import os
import json
import base64
from typing import Generator, Dict, Any
from pymongo import MongoClient
import pika

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

class TestClient:
    """Cliente de teste para a API com suporte a Basic Auth"""
    
    def __init__(self, base_url: str, username: str = None, password: str = None):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configura autenticação se fornecida
        if username and password:
            self.session.auth = (username, password)
    
    def get(self, endpoint: str, **kwargs):
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)
    
    def post(self, endpoint: str, **kwargs):
        return self.session.post(f"{self.base_url}{endpoint}", **kwargs)
    
    def put(self, endpoint: str, **kwargs):
        return self.session.put(f"{self.base_url}{endpoint}", **kwargs)
    
    def delete(self, endpoint: str, **kwargs):
        return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)
    
    def set_auth(self, username: str, password: str):
        """Define autenticação para o cliente"""
        self.session.auth = (username, password)
    
    def clear_auth(self):
        """Remove autenticação do cliente"""
        self.session.auth = None

@pytest.fixture(scope="session")
def api_client() -> Generator[TestClient, None, None]:
    """Fixture que fornece um cliente de teste autenticado para a API"""
    client = TestClient(API_BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD)
    
    # Verifica se a API está rodando
    try:
        response = client.get("/")
        if response.status_code != 200:
            pytest.skip("API não está respondendo corretamente")
    except requests.exceptions.ConnectionError:
        pytest.skip("API não está rodando. Execute 'docker compose up' primeiro.")
    
    yield client

@pytest.fixture(scope="session")
def unauthenticated_client() -> Generator[TestClient, None, None]:
    """Fixture que fornece um cliente sem autenticação"""
    client = TestClient(API_BASE_URL)
    yield client

@pytest.fixture(scope="session")
def admin_client() -> Generator[TestClient, None, None]:
    """Fixture que fornece um cliente com privilégios administrativos"""
    client = TestClient(API_BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD)
    yield client

@pytest.fixture(scope="session")
def manager_client() -> Generator[TestClient, None, None]:
    """Fixture que fornece um cliente manager (também admin)"""
    client = TestClient(API_BASE_URL, MANAGER_USERNAME, MANAGER_PASSWORD)
    yield client

@pytest.fixture(scope="session")
def user_client() -> Generator[TestClient, None, None]:
    """Fixture que fornece um cliente com privilégios de usuário"""
    client = TestClient(API_BASE_URL, USER_USERNAME, USER_PASSWORD)
    yield client

@pytest.fixture(scope="session")
def operator_client() -> Generator[TestClient, None, None]:
    """Fixture que fornece um cliente operador (usuário comum)"""
    client = TestClient(API_BASE_URL, OPERATOR_USERNAME, OPERATOR_PASSWORD)
    yield client

@pytest.fixture(scope="session")
def mongo_client() -> Generator[MongoClient, None, None]:
    """Fixture que fornece um cliente MongoDB para testes"""
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')
        yield client
    except Exception:
        pytest.skip("MongoDB não está disponível")
    finally:
        if 'client' in locals():
            client.close()

@pytest.fixture(scope="function")
def clean_database(mongo_client: MongoClient):
    """Fixture que limpa o banco de dados antes de cada teste"""
    db = mongo_client[MONGO_DB]
    
    # Limpa as coleções antes do teste
    db.age_groups.delete_many({})
    db.enrollments.delete_many({})
    
    yield
    
    # Limpa as coleções após o teste
    db.age_groups.delete_many({})
    db.enrollments.delete_many({})

@pytest.fixture
def sample_age_groups(admin_client: TestClient, clean_database) -> list[Dict[str, Any]]:
    """Fixture que cria age groups de exemplo para testes"""
    age_groups_data = [
        {"min_age": 18, "max_age": 25},
        {"min_age": 26, "max_age": 35},
        {"min_age": 36, "max_age": 50},
    ]
    
    created_groups = []
    for age_group_data in age_groups_data:
        response = admin_client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 200
        created_groups.append(response.json())
    
    return created_groups

@pytest.fixture
def valid_enrollment_data() -> Dict[str, Any]:
    """Fixture que fornece dados válidos para enrollment"""
    return {
        "name": "João da Silva",
        "age": 25,
        "cpf": "123.456.789-01"
    }

@pytest.fixture
def invalid_enrollment_data() -> list[Dict[str, Any]]:
    """Fixture que fornece dados inválidos para enrollment"""
    return [
        {
            "name": "",  # Nome vazio
            "age": 25,
            "cpf": "123.456.789-01"
        },
        {
            "name": "Maria Silva",
            "age": 0,  # Idade inválida
            "cpf": "123.456.789-01"
        },
        {
            "name": "Pedro Silva",
            "age": 25,
            "cpf": "111.111.111-11"  # CPF inválido
        },
        {
            "name": "Ana Silva",
            "age": 150,  # Idade fora do range
            "cpf": "123.456.789-01"
        }
    ]

def wait_for_enrollment_processing(api_client: TestClient, enrollment_id: str, timeout: int = 10) -> Dict[str, Any]:
    """Função auxiliar para aguardar o processamento de um enrollment"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = api_client.get(f"/enrollments/{enrollment_id}")
        if response.status_code == 200:
            status = response.json()
            if status["status"] == "processed":
                return status
        time.sleep(0.5)
    
    raise TimeoutError(f"Enrollment {enrollment_id} não foi processado em {timeout} segundos")

def create_basic_auth_header(username: str, password: str) -> str:
    """Cria header Authorization para Basic Auth"""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded_credentials}" 