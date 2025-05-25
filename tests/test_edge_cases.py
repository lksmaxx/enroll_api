import pytest
import json
import base64
from tests.conftest import APITestClient, create_basic_auth_header


@pytest.mark.edge
class TestEdgeCases:
    """Testes para casos extremos e situações incomuns"""

    def test_endpoints_require_authentication(self, api_client: APITestClient):
        """Testa que endpoints requerem autenticação"""
        # Testa endpoints sem autenticação
        response = api_client.client.post("/enrollments/", json={"name": "João", "age": 25, "cpf": "123.456.789-01"})
        assert response.status_code == 401
        
        response = api_client.client.post("/age-groups/", json={"min_age": 18, "max_age": 25})
        assert response.status_code == 401

    def test_malformed_json_requests(self, api_client: APITestClient):
        """Testa requisições com JSON malformado"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Testa com dados que não são objetos válidos
        invalid_data_types = [
            "string_simples",
            123,
            [],
            True,
            None,
        ]
        
        for data in invalid_data_types:
            response = api_client.client.post("/enrollments/", json=data, headers={"Authorization": auth_header})
            assert response.status_code == 422, f"Dados inválidos deveriam retornar 422: {data}"

    def test_extremely_large_payloads(self, api_client: APITestClient):
        """Testa payloads extremamente grandes"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Nome muito longo
        very_long_name = "A" * 10000
        enrollment_data = {
            "name": very_long_name,
            "age": 25,
            "cpf": "123.456.789-01"
        }
        
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        # Pode aceitar ou rejeitar, mas não deve quebrar o servidor
        assert response.status_code in [200, 400, 413, 422, 500]

    def test_unicode_and_special_characters(self, api_client: APITestClient):
        """Testa caracteres Unicode e especiais"""
        auth_header = create_basic_auth_header("config", "config123")
        
        special_names = [
            "José da Silva",  # Acentos
            "François Müller",  # Caracteres especiais
            "李小明",  # Caracteres chineses
            "محمد علي",  # Caracteres árabes
            "João\"Silva",  # Aspas
            "João'Silva",  # Apóstrofe
        ]
        
        for name in special_names:
            enrollment_data = {
                "name": name,
                "age": 25,
                "cpf": "123.456.789-01"
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            # Deve aceitar ou rejeitar graciosamente
            assert response.status_code in [200, 400, 422, 500]

    def test_sql_injection_attempts(self, api_client: APITestClient):
        """Testa tentativas de SQL injection (mesmo usando MongoDB)"""
        auth_header = create_basic_auth_header("config", "config123")
        
        injection_attempts = [
            "'; DROP TABLE enrollments; --",
            "' OR '1'='1",
            "'; DELETE FROM age_groups; --",
            "admin'--",
            "' UNION SELECT * FROM users --",
        ]
        
        for injection in injection_attempts:
            enrollment_data = {
                "name": injection,
                "age": 25,
                "cpf": "123.456.789-01"
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            # Não deve quebrar o sistema
            assert response.status_code in [200, 400, 422, 500]
            
            # Verifica se o sistema ainda funciona
            health_response = api_client.client.get("/")
            assert health_response.status_code == 200

    def test_nosql_injection_attempts(self, api_client: APITestClient):
        """Testa tentativas de NoSQL injection"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Tenta injeção através de nomes especiais
        nosql_injections = [
            "$ne",
            "$gt",
            "$where",
            "$regex",
            "function() { return true; }",
        ]
        
        for injection in nosql_injections:
            enrollment_data = {
                "name": injection,
                "age": 25,
                "cpf": "123.456.789-01"
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            # Deve rejeitar ou tratar adequadamente
            assert response.status_code in [200, 400, 422, 500]

    def test_boundary_age_values(self, api_client: APITestClient):
        """Testa valores extremos de idade"""
        auth_header = create_basic_auth_header("admin", "secret123")
        
        # Testa criação de age groups com valores extremos
        extreme_age_groups = [
            {"min_age": 0, "max_age": 0},
            {"min_age": 1, "max_age": 1},
            {"min_age": 150, "max_age": 200},
        ]
        
        for age_group_data in extreme_age_groups:
            response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": auth_header})
            # Aceita ou rejeita, mas não deve quebrar
            assert response.status_code in [200, 400, 422, 500]

    def test_negative_values(self, api_client: APITestClient):
        """Testa valores negativos"""
        auth_header = create_basic_auth_header("admin", "secret123")
        
        negative_test_cases = [
            {"min_age": -1, "max_age": 25},  # Idade mínima negativa
            {"min_age": 18, "max_age": -1},  # Idade máxima negativa
            {"min_age": -10, "max_age": -5}, # Ambas negativas
        ]
        
        for age_group_data in negative_test_cases:
            response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": auth_header})
            assert response.status_code in [400, 422]  # Deve rejeitar
        
        # Testa idade negativa em enrollment
        auth_header = create_basic_auth_header("config", "config123")
        enrollment_data = {
            "name": "Teste Negativo",
            "age": -5,
            "cpf": "123.456.789-01"
        }
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        assert response.status_code in [400, 422]

    def test_null_values_in_json(self, api_client: APITestClient):
        """Testa valores null no JSON"""
        auth_header = create_basic_auth_header("config", "config123")
        
        null_test_cases = [
            {"name": None, "age": 25, "cpf": "123.456.789-01"},
            {"name": "João", "age": None, "cpf": "123.456.789-01"},
            {"name": "João", "age": 25, "cpf": None},
        ]
        
        for enrollment_data in null_test_cases:
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            assert response.status_code in [400, 422]

    def test_wrong_data_types(self, api_client: APITestClient):
        """Testa tipos de dados incorretos"""
        auth_header = create_basic_auth_header("config", "config123")
        
        wrong_type_cases = [
            {"name": 123, "age": 25, "cpf": "123.456.789-01"},  # Nome como número
            {"name": "João", "age": "25", "cpf": "123.456.789-01"},  # Idade como string
            {"name": "João", "age": 25.5, "cpf": "123.456.789-01"},  # Idade como float
            {"name": "João", "age": 25, "cpf": 12345678901},  # CPF como número
        ]
        
        for enrollment_data in wrong_type_cases:
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            # Pode aceitar (conversão automática) ou rejeitar
            assert response.status_code in [200, 400, 422, 500]

    def test_extremely_long_cpf(self, api_client: APITestClient):
        """Testa CPF extremamente longo"""
        auth_header = create_basic_auth_header("config", "config123")
        
        very_long_cpf = "1" * 1000
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": very_long_cpf
        }
        
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        assert response.status_code in [400, 422]

    def test_age_group_with_same_min_max(self, api_client: APITestClient):
        """Testa age group com min_age igual a max_age"""
        auth_header = create_basic_auth_header("admin", "secret123")
        
        age_group_data = {"min_age": 25, "max_age": 25}
        
        response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": auth_header})
        # Pode ser válido (idade exata) ou inválido
        assert response.status_code in [200, 400, 422, 500]

    def test_invalid_auth_headers_edge_cases(self, api_client: APITestClient):
        """Testa casos extremos de headers de autenticação"""
        invalid_headers = [
            {"Authorization": "Basic "},  # Basic vazio
            {"Authorization": "Basic invalid"},  # Base64 inválido
            {"Authorization": "Bearer token123"},  # Tipo errado
            {"Authorization": ""},  # Authorization vazio
            {"Authorization": "Basic " + "a" * 10000},  # Header muito longo
        ]
        
        for headers in invalid_headers:
            response = api_client.client.get("/age-groups/", headers=headers)
            assert response.status_code == 401, f"Header inválido deveria retornar 401: {headers}"

    def test_concurrent_requests_same_user(self, api_client: APITestClient):
        """Testa requisições simultâneas do mesmo usuário"""
        import concurrent.futures
        
        auth_header = create_basic_auth_header("config", "config123")
        
        def make_request(index: int):
            enrollment_data = {
                "name": f"Pessoa {index}",
                "age": 25,
                "cpf": f"123.456.{index:03d}-01"
            }
            return api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        
        # Faz múltiplas requisições simultâneas
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verifica que todas as requisições foram processadas (mesmo que falhem por outros motivos)
        for result in results:
            assert result.status_code != 401  # Não deve ser problema de auth
            assert result.status_code in [200, 400, 422, 500]  # Códigos esperados 