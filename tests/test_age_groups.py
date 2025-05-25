import pytest
import json
from tests.conftest import APITestClient, create_basic_auth_header


@pytest.mark.functional
class TestAgeGroups:
    """Testes funcionais para endpoints de Age Groups - Foco em Autenticação"""

    def test_age_groups_require_authentication(self, api_client: APITestClient):
        """Testa que todos os endpoints requerem autenticação"""
        endpoints_and_methods = [
            ("GET", "/age-groups/"),
            ("POST", "/age-groups/"),
            ("GET", "/age-groups/507f1f77bcf86cd799439011"),
            ("PUT", "/age-groups/507f1f77bcf86cd799439011"),
            ("DELETE", "/age-groups/507f1f77bcf86cd799439011"),
        ]
        
        for method, endpoint in endpoints_and_methods:
            if method == "GET":
                response = api_client.client.get(endpoint)
            elif method == "POST":
                response = api_client.client.post(endpoint, json={"min_age": 18, "max_age": 25})
            elif method == "PUT":
                response = api_client.client.put(endpoint, json={"min_age": 18, "max_age": 25})
            elif method == "DELETE":
                response = api_client.client.delete(endpoint)
            
            assert response.status_code == 401, f"{method} {endpoint} deveria retornar 401"

    def test_create_age_group_requires_admin_auth(self, api_client: APITestClient):
        """Testa que criação de age group requer privilégios admin"""
        auth_header = create_basic_auth_header("config", "config123")
        age_group_data = {"min_age": 18, "max_age": 25}
        
        response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": auth_header})
        
        assert response.status_code == 403

    def test_update_age_group_requires_admin_auth(self, api_client: APITestClient):
        """Testa que atualização requer privilégios admin"""
        user_auth = create_basic_auth_header("config", "config123")
        fake_id = "507f1f77bcf86cd799439011"
        update_data = {"min_age": 20, "max_age": 30}
        
        response = api_client.client.put(f"/age-groups/{fake_id}", json=update_data, headers={"Authorization": user_auth})
        
        assert response.status_code == 403

    def test_delete_age_group_requires_admin_auth(self, api_client: APITestClient):
        """Testa que exclusão requer privilégios admin"""
        user_auth = create_basic_auth_header("config", "config123")
        fake_id = "507f1f77bcf86cd799439011"
        
        response = api_client.client.delete(f"/age-groups/{fake_id}", headers={"Authorization": user_auth})
        
        assert response.status_code == 403

    def test_create_age_group_invalid_data_validation(self, api_client: APITestClient):
        """Testa validação de dados inválidos (sem conectar ao banco)"""
        auth_header = create_basic_auth_header("admin", "secret123")
        
        # Testa dados claramente inválidos que devem falhar na validação
        invalid_data_sets = [
            {"min_age": "abc", "max_age": 25},  # tipo inválido
            {"max_age": 25},  # campo obrigatório faltando
            {},  # dados vazios
        ]
        
        for invalid_data in invalid_data_sets:
            response = api_client.client.post("/age-groups/", json=invalid_data, headers={"Authorization": auth_header})
            # Deve falhar na validação antes de tentar conectar ao banco
            assert response.status_code == 422, f"Dados inválidos deveriam retornar 422: {invalid_data}"

    def test_operator_has_no_admin_privileges(self, api_client: APITestClient):
        """Testa que operator não tem privilégios administrativos"""
        operator_auth = create_basic_auth_header("operator", "operator456")
        
        # Testa operações administrativas
        admin_operations = [
            ("POST", "/age-groups/", {"min_age": 18, "max_age": 25}),
            ("PUT", "/age-groups/507f1f77bcf86cd799439011", {"min_age": 20, "max_age": 30}),
            ("DELETE", "/age-groups/507f1f77bcf86cd799439011", None),
        ]
        
        for method, endpoint, data in admin_operations:
            if method == "POST":
                response = api_client.client.post(endpoint, json=data, headers={"Authorization": operator_auth})
            elif method == "PUT":
                response = api_client.client.put(endpoint, json=data, headers={"Authorization": operator_auth})
            elif method == "DELETE":
                response = api_client.client.delete(endpoint, headers={"Authorization": operator_auth})
            
            assert response.status_code == 403, f"Operator não deveria ter acesso a {method} {endpoint}"

    def test_config_user_has_no_admin_privileges(self, api_client: APITestClient):
        """Testa que usuário config não tem privilégios administrativos"""
        config_auth = create_basic_auth_header("config", "config123")
        
        # Testa operações administrativas que devem ser negadas
        admin_operations = [
            ("POST", "/age-groups/", {"min_age": 18, "max_age": 25}),
            ("PUT", "/age-groups/507f1f77bcf86cd799439011", {"min_age": 20, "max_age": 30}),
            ("DELETE", "/age-groups/507f1f77bcf86cd799439011", None),
        ]
        
        for method, endpoint, data in admin_operations:
            if method == "POST":
                response = api_client.client.post(endpoint, json=data, headers={"Authorization": config_auth})
            elif method == "PUT":
                response = api_client.client.put(endpoint, json=data, headers={"Authorization": config_auth})
            elif method == "DELETE":
                response = api_client.client.delete(endpoint, headers={"Authorization": config_auth})
            
            assert response.status_code == 403, f"Config user não deveria ter acesso a {method} {endpoint}"

    def test_invalid_auth_headers(self, api_client: APITestClient):
        """Testa headers de autenticação inválidos"""
        invalid_headers = [
            {"Authorization": "Basic invalid"},
            {"Authorization": "Bearer token123"},
            {"Authorization": "Basic " + "invalid:credentials".encode().hex()},  # Encoding errado
        ]
        
        for headers in invalid_headers:
            response = api_client.client.get("/age-groups/", headers=headers)
            assert response.status_code == 401, f"Header inválido deveria retornar 401: {headers}"

    def test_multiple_users_auth_consistency(self, api_client: APITestClient):
        """Testa consistência de autenticação entre diferentes usuários"""
        users_and_expected = [
            ("admin", "secret123", "admin"),
            ("manager", "manager789", "admin"), 
            ("config", "config123", "user"),
            ("operator", "operator456", "user"),
        ]
        
        for username, password, expected_role in users_and_expected:
            auth_header = create_basic_auth_header(username, password)
            
            # Testa endpoint /me para verificar autenticação
            response = api_client.client.get("/me", headers={"Authorization": auth_header})
            assert response.status_code == 200, f"Usuário {username} deveria conseguir autenticar"
            
            user_data = response.json()
            # Verifica se tem os campos esperados (pode variar dependendo da implementação)
            assert "user" in user_data or "username" in user_data, f"Resposta deveria ter dados do usuário: {user_data}"
            
            # Se tem campo user, verifica dentro dele
            if "user" in user_data:
                assert user_data["user"]["username"] == username
                assert user_data["user"]["role"] == expected_role
            else:
                assert user_data["username"] == username
                assert user_data["role"] == expected_role

    def test_auth_consistency_across_endpoints(self, api_client: APITestClient):
        """Testa que a autenticação funciona consistentemente em diferentes endpoints"""
        # Testa usuários válidos
        valid_users = [
            ("admin", "secret123"),
            ("config", "config123"),
        ]
        
        for username, password in valid_users:
            auth_header = create_basic_auth_header(username, password)
            
            # Testa endpoints que não requerem MongoDB
            endpoints = ["/", "/me"]
            
            for endpoint in endpoints:
                response = api_client.client.get(endpoint, headers={"Authorization": auth_header})
                assert response.status_code == 200, f"Usuário {username} deveria acessar {endpoint}" 