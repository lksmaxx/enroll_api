import pytest
import base64
from tests.conftest import APITestClient, create_basic_auth_header


@pytest.mark.auth
class TestBasicAuth:
    """Testes para autenticação Basic Auth"""

    def test_health_endpoint_public(self, api_client: APITestClient):
        """Testa que o endpoint de health é público"""
        response = api_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_me_endpoint_requires_auth(self, api_client: APITestClient):
        """Testa que o endpoint /me requer autenticação"""
        # Faz requisição sem autenticação
        response = api_client.client.get("/me")
        
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Basic"

    def test_me_endpoint_with_valid_auth(self, api_client: APITestClient):
        """Testa endpoint /me com autenticação válida"""
        # Faz requisição com autenticação
        auth_header = create_basic_auth_header("admin", "secret123")
        response = api_client.client.get("/me", headers={"Authorization": auth_header})
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "admin"

    def test_age_groups_require_auth(self, api_client: APITestClient):
        """Testa que endpoints de age groups requerem autenticação"""
        # Listar age groups sem auth
        response = api_client.client.get("/age-groups/")
        assert response.status_code == 401
        
        # Criar age group sem auth
        age_group_data = {"min_age": 18, "max_age": 25}
        response = api_client.client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 401

    def test_enrollments_require_auth(self, api_client: APITestClient):
        """Testa que endpoints de enrollments requerem autenticação"""
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": "11144477735"  # CPF matematicamente válido
        }
        
        # Criar enrollment sem auth
        response = api_client.client.post("/enrollments/", json=enrollment_data)
        assert response.status_code == 401
        
        # Buscar status sem auth
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = api_client.client.get(f"/enrollments/{fake_id}")
        assert response.status_code == 401

    def test_admin_operations_require_admin_role(self, api_client: APITestClient, clean_database):
        """Testa que operações administrativas requerem role admin"""
        age_group_data = {"min_age": 18, "max_age": 25}
        
        # Usuário comum não pode criar age group
        user_auth = create_basic_auth_header("config", "config123")
        response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": user_auth})
        assert response.status_code == 403
        assert "privilégios administrativos" in response.json()["detail"].lower()

    def test_user_can_read_age_groups(self, api_client: APITestClient, clean_database):
        """Testa que usuário comum pode ler age groups"""
        # Primeiro cria um age group como admin
        admin_auth = create_basic_auth_header("admin", "secret123")
        age_group_data = {"min_age": 18, "max_age": 25}
        response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": admin_auth})
        assert response.status_code == 200
        age_group_id = response.json()["id"]
        
        # Usuário comum pode listar age groups
        user_auth = create_basic_auth_header("config", "config123")
        response = api_client.client.get("/age-groups/", headers={"Authorization": user_auth})
        assert response.status_code == 200
        
        # Pode buscar age group específico
        response = api_client.client.get(f"/age-groups/{age_group_id}", headers={"Authorization": user_auth})
        assert response.status_code == 200
        
        # Não pode atualizar
        update_data = {"min_age": 20, "max_age": 30}
        response = api_client.client.put(f"/age-groups/{age_group_id}", json=update_data, headers={"Authorization": user_auth})
        assert response.status_code == 403
        
        # Não pode deletar
        response = api_client.client.delete(f"/age-groups/{age_group_id}", headers={"Authorization": user_auth})
        assert response.status_code == 403

    def test_invalid_credentials(self, api_client: APITestClient):
        """Testa credenciais inválidas"""
        auth_header = create_basic_auth_header("invalid_user", "invalid_pass")
        
        response = api_client.client.get("/me", headers={"Authorization": auth_header})
        assert response.status_code == 401
        assert "credenciais inválidas" in response.json()["detail"].lower()

    def test_multiple_users_authentication(self, api_client: APITestClient):
        """Testa autenticação com múltiplos usuários"""
        # Testa usuário admin
        admin_auth = create_basic_auth_header("admin", "secret123")
        response = api_client.client.get("/me", headers={"Authorization": admin_auth})
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "admin"
        
        # Testa usuário config
        config_auth = create_basic_auth_header("config", "config123")
        response = api_client.client.get("/me", headers={"Authorization": config_auth})
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "user"

    def test_basic_auth_header_format(self, api_client: APITestClient):
        """Testa formato correto do header Basic Auth"""
        # Cria header manualmente
        auth_header = create_basic_auth_header("admin", "secret123")
        
        response = api_client.client.get("/me", headers={"Authorization": auth_header})
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "admin"

    def test_malformed_auth_header(self, api_client: APITestClient):
        """Testa headers de autenticação malformados"""
        malformed_headers = [
            "Basic invalid_base64",
            "Basic " + "invalid:format".encode().hex(),  # Não é base64
            "Bearer token123",  # Tipo errado
            "Basic",  # Sem credenciais
        ]
        
        for auth_header in malformed_headers:
            response = api_client.client.get("/me", headers={"Authorization": auth_header})
            assert response.status_code == 401

    def test_enrollment_workflow_with_auth(self, api_client: APITestClient, clean_database):
        """Testa fluxo completo de enrollment com autenticação"""
        # Primeiro cria um age group
        admin_auth = create_basic_auth_header("admin", "secret123")
        age_group_data = {"min_age": 18, "max_age": 25}
        response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": admin_auth})
        assert response.status_code == 200
        
        # Criar enrollment como usuário comum
        user_auth = create_basic_auth_header("config", "config123")
        enrollment_data = {
            "name": "João Silva",
            "age": 22,
            "cpf": "11144477735"  # CPF matematicamente válido
        }
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": user_auth})
        assert response.status_code == 200
        enrollment_id = response.json()["id"]
        
        # Verificar status
        response = api_client.client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": user_auth})
        assert response.status_code == 200
        assert response.json()["status"] == "pending"

    def test_concurrent_auth_requests(self, api_client: APITestClient):
        """Testa múltiplas requisições autenticadas simultâneas"""
        import concurrent.futures
        
        def make_request():
            auth_header = create_basic_auth_header("admin", "secret123")
            response = api_client.client.get("/me", headers={"Authorization": auth_header})
            return response.status_code == 200
        
        # Executa 5 requisições simultâneas
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Todas devem ter sucesso
        assert all(results) 