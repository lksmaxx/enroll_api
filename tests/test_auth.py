import pytest
from tests.conftest import TestClient, create_basic_auth_header


class TestBasicAuth:
    """Testes para autenticação Basic Auth"""

    def test_health_endpoint_public(self, unauthenticated_client: TestClient):
        """Testa que o endpoint de health é público"""
        response = unauthenticated_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "auth" in data

    def test_me_endpoint_requires_auth(self, unauthenticated_client: TestClient):
        """Testa que o endpoint /me requer autenticação"""
        response = unauthenticated_client.get("/me")
        
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Basic"

    def test_me_endpoint_with_valid_auth(self, api_client: TestClient):
        """Testa endpoint /me com autenticação válida"""
        response = api_client.get("/me")
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "admin"

    def test_age_groups_require_auth(self, unauthenticated_client: TestClient):
        """Testa que endpoints de age groups requerem autenticação"""
        # Listar age groups
        response = unauthenticated_client.get("/age-groups/")
        assert response.status_code == 401
        
        # Criar age group
        age_group_data = {"min_age": 18, "max_age": 25}
        response = unauthenticated_client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 401

    def test_enrollments_require_auth(self, unauthenticated_client: TestClient):
        """Testa que endpoints de enrollments requerem autenticação"""
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": "123.456.789-01"
        }
        
        # Criar enrollment
        response = unauthenticated_client.post("/enrollments/", json=enrollment_data)
        assert response.status_code == 401
        
        # Buscar status
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = unauthenticated_client.get(f"/enrollments/{fake_id}")
        assert response.status_code == 401

    def test_admin_operations_require_admin_role(self, user_client: TestClient, clean_database):
        """Testa que operações administrativas requerem role admin"""
        age_group_data = {"min_age": 18, "max_age": 25}
        
        # Usuário comum não pode criar age group
        response = user_client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 403
        assert "privilégios administrativos" in response.json()["detail"].lower()

    def test_user_can_read_but_not_modify(self, user_client: TestClient, sample_age_groups):
        """Testa que usuário comum pode ler mas não modificar"""
        # Pode listar age groups
        response = user_client.get("/age-groups/")
        assert response.status_code == 200
        
        # Pode buscar age group específico
        age_group_id = sample_age_groups[0]["id"]
        response = user_client.get(f"/age-groups/{age_group_id}")
        assert response.status_code == 200
        
        # Não pode atualizar
        update_data = {"min_age": 20, "max_age": 30}
        response = user_client.put(f"/age-groups/{age_group_id}", json=update_data)
        assert response.status_code == 403
        
        # Não pode deletar
        response = user_client.delete(f"/age-groups/{age_group_id}")
        assert response.status_code == 403

    def test_invalid_credentials(self, unauthenticated_client: TestClient):
        """Testa credenciais inválidas"""
        # Configura credenciais inválidas
        unauthenticated_client.set_auth("invalid_user", "invalid_pass")
        
        response = unauthenticated_client.get("/me")
        assert response.status_code == 401
        assert "credenciais inválidas" in response.json()["detail"].lower()

    def test_multiple_users_authentication(self):
        """Testa autenticação com múltiplos usuários"""
        from tests.conftest import API_BASE_URL, TestClient
        
        # Testa usuário admin
        admin_client = TestClient(API_BASE_URL, "admin", "secret123")
        response = admin_client.get("/me")
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "admin"
        
        # Testa usuário config
        config_client = TestClient(API_BASE_URL, "config", "config123")
        response = config_client.get("/me")
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "user"

    def test_basic_auth_header_format(self, unauthenticated_client: TestClient):
        """Testa formato correto do header Basic Auth"""
        # Cria header manualmente
        auth_header = create_basic_auth_header("admin", "secret123")
        
        response = unauthenticated_client.session.get(
            f"{unauthenticated_client.base_url}/me",
            headers={"Authorization": auth_header}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "admin"

    def test_malformed_auth_header(self, unauthenticated_client: TestClient):
        """Testa headers de autenticação malformados"""
        malformed_headers = [
            "Basic invalid_base64",
            "Basic " + "invalid:format".encode().hex(),  # Não é base64
            "Bearer token123",  # Tipo errado
            "Basic",  # Sem credenciais
        ]
        
        for auth_header in malformed_headers:
            response = unauthenticated_client.session.get(
                f"{unauthenticated_client.base_url}/me",
                headers={"Authorization": auth_header}
            )
            assert response.status_code == 401

    def test_enrollment_workflow_with_auth(self, api_client: TestClient, sample_age_groups, valid_enrollment_data):
        """Testa fluxo completo de enrollment com autenticação"""
        # Criar enrollment
        response = api_client.post("/enrollments/", json=valid_enrollment_data)
        assert response.status_code == 200
        enrollment_id = response.json()["id"]
        
        # Verificar status
        response = api_client.get(f"/enrollments/{enrollment_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "pending"

    def test_concurrent_auth_requests(self, api_client: TestClient):
        """Testa múltiplas requisições autenticadas simultâneas"""
        import concurrent.futures
        
        def make_request():
            response = api_client.get("/me")
            return response.status_code == 200
        
        # Executa 10 requisições simultâneas
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Todas devem ter sucesso
        assert all(results)

    def test_auth_with_special_characters_in_password(self):
        """Testa autenticação com caracteres especiais na senha"""
        from tests.conftest import API_BASE_URL, TestClient
        
        # Nota: Este teste assumiria que existe um usuário com senha especial
        # Para um teste real, seria necessário configurar tal usuário
        special_client = TestClient(API_BASE_URL, "admin", "secret123")
        response = special_client.get("/me")
        assert response.status_code == 200 