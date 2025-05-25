import pytest
import time
import json
from typing import Dict, Any
from tests.conftest import APITestClient, create_basic_auth_header


@pytest.mark.integration
class TestIntegrationWorkflow:
    """Testes de integração focados em autenticação e validação"""

    def test_authentication_integration_workflow(self, api_client: APITestClient):
        """Testa o fluxo de autenticação em diferentes endpoints"""
        
        # 1. Verificar que endpoints requerem autenticação
        response = api_client.client.get("/age-groups/")
        assert response.status_code == 401
        
        response = api_client.client.post("/enrollments/", json={"name": "João", "age": 25, "cpf": "123.456.789-01"})
        assert response.status_code == 401
        
        # 2. Verificar autenticação válida
        auth_header = create_basic_auth_header("config", "config123")
        response = api_client.client.get("/me", headers={"Authorization": auth_header})
        assert response.status_code == 200
        
        # 3. Verificar que usuário comum não tem acesso admin
        response = api_client.client.post("/age-groups/", json={"min_age": 18, "max_age": 25}, headers={"Authorization": auth_header})
        assert response.status_code == 403
        
        # 4. Verificar que admin tem acesso
        admin_auth = create_basic_auth_header("admin", "secret123")
        response = api_client.client.get("/admin/users", headers={"Authorization": admin_auth})
        assert response.status_code == 200

    def test_multiple_users_integration(self, api_client: APITestClient):
        """Testa integração com múltiplos usuários"""
        
        users_and_roles = [
            ("admin", "secret123", "admin"),
            ("manager", "manager789", "admin"),
            ("config", "config123", "user"),
            ("operator", "operator456", "user"),
        ]
        
        for username, password, expected_role in users_and_roles:
            auth_header = create_basic_auth_header(username, password)
            
            # Verificar autenticação
            response = api_client.client.get("/me", headers={"Authorization": auth_header})
            assert response.status_code == 200
            
            user_data = response.json()
            if "user" in user_data:
                assert user_data["user"]["username"] == username
                assert user_data["user"]["role"] == expected_role
            else:
                assert user_data["username"] == username
                assert user_data["role"] == expected_role

    def test_enrollment_validation_integration(self, api_client: APITestClient):
        """Testa integração de validação de enrollments"""
        
        auth_header = create_basic_auth_header("config", "config123")
        
        # Testa dados válidos (estruturalmente)
        valid_enrollment = {
            "name": "João da Silva",
            "age": 25,
            "cpf": "11144477735"  # CPF matematicamente válido
        }
        
        response = api_client.client.post("/enrollments/", json=valid_enrollment, headers={"Authorization": auth_header})
        # Não deve falhar por validação (pode falhar por falta de age groups)
        assert response.status_code not in [401, 403, 422]
        
        # Testa dados inválidos
        invalid_enrollments = [
            {"age": 25, "cpf": "11144477735"},  # Nome faltando
            {"name": "João", "cpf": "11144477735"},  # Idade faltando
            {"name": "João", "age": 25},  # CPF faltando
            {"name": "", "age": 25, "cpf": "11144477735"},  # Nome vazio
        ]
        
        for invalid_data in invalid_enrollments:
            response = api_client.client.post("/enrollments/", json=invalid_data, headers={"Authorization": auth_header})
            assert response.status_code == 422

    def test_age_group_validation_integration(self, api_client: APITestClient):
        """Testa integração de validação de age groups"""
        
        admin_auth = create_basic_auth_header("admin", "secret123")
        
        # Testa dados válidos (estruturalmente)
        valid_age_group = {"min_age": 18, "max_age": 25}
        
        response = api_client.client.post("/age-groups/", json=valid_age_group, headers={"Authorization": admin_auth})
        # Não deve falhar por validação ou autenticação
        assert response.status_code not in [401, 403, 422]
        
        # Testa dados inválidos
        invalid_age_groups = [
            {"max_age": 25},  # min_age faltando
            {"min_age": 18},  # max_age faltando
            {},  # Dados vazios
            {"min_age": "abc", "max_age": 25},  # Tipo inválido
        ]
        
        for invalid_data in invalid_age_groups:
            response = api_client.client.post("/age-groups/", json=invalid_data, headers={"Authorization": admin_auth})
            assert response.status_code == 422

    def test_system_health_integration(self, api_client: APITestClient):
        """Testa saúde geral do sistema"""
        
        # Verificar health check público
        response = api_client.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verificar que sistema responde consistentemente
        for _ in range(3):
            response = api_client.client.get("/")
            assert response.status_code == 200

    def test_error_handling_integration(self, api_client: APITestClient):
        """Testa tratamento de erros em cenários de integração"""
        
        auth_header = create_basic_auth_header("config", "config123")
        
        # Tentar buscar recursos inexistentes
        response = api_client.client.get("/age-groups/507f1f77bcf86cd799439011", headers={"Authorization": auth_header})
        # Não deve ser problema de autenticação
        assert response.status_code != 401
        assert response.status_code != 403
        
        response = api_client.client.get("/enrollments/00000000-0000-0000-0000-000000000000", headers={"Authorization": auth_header})
        # Não deve ser problema de autenticação
        assert response.status_code != 401
        assert response.status_code != 403
        
        # Verificar que sistema continua funcionando após erros
        response = api_client.client.get("/")
        assert response.status_code == 200

    def test_concurrent_authentication_integration(self, api_client: APITestClient):
        """Testa autenticação simultânea de múltiplos usuários"""
        import concurrent.futures
        
        users = [
            ("admin", "secret123"),
            ("config", "config123"),
            ("operator", "operator456"),
        ]
        
        def authenticate_user(username: str, password: str):
            auth_header = create_basic_auth_header(username, password)
            response = api_client.client.get("/me", headers={"Authorization": auth_header})
            return {
                "username": username,
                "success": response.status_code == 200,
                "status_code": response.status_code
            }
        
        # Autentica múltiplos usuários simultaneamente
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(authenticate_user, username, password) for username, password in users]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Todos devem autenticar com sucesso
        successful_auths = [r for r in results if r["success"]]
        assert len(successful_auths) == len(users)

    def test_admin_endpoints_integration(self, api_client: APITestClient):
        """Testa integração dos endpoints administrativos"""
        
        admin_auth = create_basic_auth_header("admin", "secret123")
        user_auth = create_basic_auth_header("config", "config123")
        
        # Verificar que admin tem acesso
        response = api_client.client.get("/admin/users", headers={"Authorization": admin_auth})
        assert response.status_code == 200
        
        response = api_client.client.get("/admin/users/info", headers={"Authorization": admin_auth})
        assert response.status_code == 200
        
        # Verificar que usuário comum não tem acesso
        response = api_client.client.get("/admin/users", headers={"Authorization": user_auth})
        assert response.status_code == 403
        
        response = api_client.client.get("/admin/users/info", headers={"Authorization": user_auth})
        assert response.status_code == 403

    def test_data_validation_consistency_integration(self, api_client: APITestClient):
        """Testa consistência de validação de dados"""
        
        auth_header = create_basic_auth_header("config", "config123")
        
        # Testa CPFs inválidos consistentemente
        invalid_cpfs = [
            "111.111.111-11",
            "000.000.000-00",
            "abc.def.ghi-jk",
            "",
        ]
        
        for cpf in invalid_cpfs:
            enrollment_data = {
                "name": "Teste CPF",
                "age": 25,
                "cpf": cpf
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            # Deve falhar consistentemente
            assert response.status_code in [400, 422], f"CPF inválido deveria falhar: {cpf}"

    def test_role_based_access_integration(self, api_client: APITestClient):
        """Testa integração do controle de acesso baseado em roles"""
        
        # Operações que requerem role admin
        admin_operations = [
            ("POST", "/age-groups/", {"min_age": 18, "max_age": 25}),
            ("GET", "/admin/users", None),
        ]
        
        # Testa com usuário comum (deve falhar)
        user_auth = create_basic_auth_header("config", "config123")
        for method, endpoint, data in admin_operations:
            if method == "POST":
                response = api_client.client.post(endpoint, json=data, headers={"Authorization": user_auth})
            else:
                response = api_client.client.get(endpoint, headers={"Authorization": user_auth})
            
            assert response.status_code == 403, f"Usuário comum não deveria acessar {method} {endpoint}"
        
        # Testa com admin (deve funcionar)
        admin_auth = create_basic_auth_header("admin", "secret123")
        for method, endpoint, data in admin_operations:
            if method == "POST":
                response = api_client.client.post(endpoint, json=data, headers={"Authorization": admin_auth})
            else:
                response = api_client.client.get(endpoint, headers={"Authorization": admin_auth})
            
            # Não deve ser problema de autenticação/autorização
            assert response.status_code not in [401, 403], f"Admin deveria acessar {method} {endpoint}" 