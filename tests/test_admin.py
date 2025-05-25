import pytest
from tests.conftest import APITestClient, create_basic_auth_header


@pytest.mark.admin
class TestAdminEndpoints:
    """Testes para endpoints administrativos"""

    def test_list_users_as_admin(self, api_client: APITestClient):
        """Testa listagem de usuários como admin"""
        auth_header = create_basic_auth_header("admin", "secret123")
        response = api_client.client.get("/admin/users", headers={"Authorization": auth_header})
        
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 4  # admin, config, operator, manager
        
        # Verifica se todos os usuários têm os campos necessários
        for user in users:
            assert "username" in user
            assert "role" in user
            assert "description" in user
            # Verifica que a senha não está exposta
            assert "password" not in user

    def test_list_users_as_manager(self, api_client: APITestClient):
        """Testa listagem de usuários como manager (também admin)"""
        auth_header = create_basic_auth_header("manager", "manager789")
        response = api_client.client.get("/admin/users", headers={"Authorization": auth_header})
        
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 4

    def test_list_users_as_regular_user_forbidden(self, api_client: APITestClient):
        """Testa que usuário comum não pode listar usuários"""
        auth_header = create_basic_auth_header("config", "config123")
        response = api_client.client.get("/admin/users", headers={"Authorization": auth_header})
        
        assert response.status_code == 403

    def test_list_users_as_operator_forbidden(self, api_client: APITestClient):
        """Testa que operador não pode listar usuários"""
        auth_header = create_basic_auth_header("operator", "operator456")
        response = api_client.client.get("/admin/users", headers={"Authorization": auth_header})
        
        assert response.status_code == 403

    def test_list_users_unauthenticated(self, api_client: APITestClient):
        """Testa que endpoint requer autenticação"""
        response = api_client.client.get("/admin/users")
        
        assert response.status_code == 401

    def test_get_users_info_as_admin(self, api_client: APITestClient):
        """Testa informações detalhadas dos usuários como admin"""
        auth_header = create_basic_auth_header("admin", "secret123")
        response = api_client.client.get("/admin/users/info", headers={"Authorization": auth_header})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "users" in data
        assert "total_users" in data
        assert "metadata" in data
        assert "source" in data
        
        assert data["total_users"] >= 4
        assert data["source"] in ["file", "environment_variables"]

    def test_get_users_info_forbidden_for_regular_user(self, api_client: APITestClient):
        """Testa que usuário comum não pode ver informações detalhadas"""
        auth_header = create_basic_auth_header("config", "config123")
        response = api_client.client.get("/admin/users/info", headers={"Authorization": auth_header})
        
        assert response.status_code == 403

    def test_reload_users_as_admin(self, api_client: APITestClient):
        """Testa recarga de usuários como admin"""
        auth_header = create_basic_auth_header("admin", "secret123")
        response = api_client.client.post("/admin/users/reload", headers={"Authorization": auth_header})
        
        # Pode ser sucesso (200) ou erro (500) dependendo se o arquivo existe
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "users" in data
            assert "total_users" in data

    def test_reload_users_forbidden_for_regular_user(self, api_client: APITestClient):
        """Testa que usuário comum não pode recarregar usuários"""
        auth_header = create_basic_auth_header("config", "config123")
        response = api_client.client.post("/admin/users/reload", headers={"Authorization": auth_header})
        
        assert response.status_code == 403

    def test_get_auth_status_as_admin(self, api_client: APITestClient):
        """Testa status do sistema de autenticação como admin"""
        auth_header = create_basic_auth_header("admin", "secret123")
        response = api_client.client.get("/admin/system/auth-status", headers={"Authorization": auth_header})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "auth_system" in data
        assert "users_source" in data
        assert "total_users" in data
        assert "admin_users" in data
        assert "regular_users" in data
        assert "current_user" in data
        
        assert data["auth_system"] == "Basic Auth"
        assert data["total_users"] >= 4
        assert data["admin_users"] >= 2  # admin e manager
        assert data["regular_users"] >= 2  # config e operator
        assert data["current_user"]["username"] == "admin"
        assert data["current_user"]["role"] == "admin"

    def test_get_auth_status_as_manager(self, api_client: APITestClient):
        """Testa status do sistema como manager"""
        auth_header = create_basic_auth_header("manager", "manager789")
        response = api_client.client.get("/admin/system/auth-status", headers={"Authorization": auth_header})
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_user"]["username"] == "manager"
        assert data["current_user"]["role"] == "admin"

    def test_get_auth_status_forbidden_for_regular_user(self, api_client: APITestClient):
        """Testa que usuário comum não pode ver status do sistema"""
        auth_header = create_basic_auth_header("config", "config123")
        response = api_client.client.get("/admin/system/auth-status", headers={"Authorization": auth_header})
        
        assert response.status_code == 403

    def test_admin_endpoints_require_admin_role(self, api_client: APITestClient):
        """Testa que todos os endpoints admin requerem role admin"""
        auth_header = create_basic_auth_header("operator", "operator456")
        admin_endpoints = [
            "/admin/users",
            "/admin/users/info",
            "/admin/system/auth-status"
        ]
        
        for endpoint in admin_endpoints:
            response = api_client.client.get(endpoint, headers={"Authorization": auth_header})
            assert response.status_code == 403, f"Endpoint {endpoint} deveria retornar 403"
        
        # Testa POST também
        response = api_client.client.post("/admin/users/reload", headers={"Authorization": auth_header})
        assert response.status_code == 403

    def test_verify_user_roles_in_listing(self, api_client: APITestClient):
        """Testa que os usuários têm os roles corretos"""
        auth_header = create_basic_auth_header("admin", "secret123")
        response = api_client.client.get("/admin/users", headers={"Authorization": auth_header})
        assert response.status_code == 200
        
        users = response.json()
        users_by_name = {user["username"]: user for user in users}
        
        # Verifica roles específicos
        assert users_by_name["admin"]["role"] == "admin"
        assert users_by_name["manager"]["role"] == "admin"
        assert users_by_name["config"]["role"] == "user"
        assert users_by_name["operator"]["role"] == "user"

    def test_verify_user_descriptions(self, api_client: APITestClient):
        """Testa que os usuários têm descrições"""
        auth_header = create_basic_auth_header("admin", "secret123")
        response = api_client.client.get("/admin/users", headers={"Authorization": auth_header})
        assert response.status_code == 200
        
        users = response.json()
        
        for user in users:
            assert "description" in user
            assert len(user["description"]) > 0  # Descrição não vazia 