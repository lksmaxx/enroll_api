import pytest
import json
from typing import Dict, Any
from tests.conftest import TestClient


class TestEdgeCases:
    """Testes para casos extremos e situações incomuns"""

    def test_malformed_json_requests(self, api_client: TestClient, clean_database):
        """Testa requisições com JSON malformado"""
        malformed_payloads = [
            '{"name": "João", "age": 25, "cpf": "123.456.789-01"',  # JSON incompleto
            '{"name": "João", "age": 25, "cpf": "123.456.789-01",}',  # Vírgula extra
            '{"name": "João", "age": 25, "cpf": "123.456.789-01"} extra',  # Texto extra
            '{name: "João", age: 25, cpf: "123.456.789-01"}',  # Sem aspas nas chaves
        ]
        
        for payload in malformed_payloads:
            response = api_client.session.post(
                f"{api_client.base_url}/enrollments/",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code in [400, 422]

    def test_extremely_large_payloads(self, api_client: TestClient, sample_age_groups):
        """Testa payloads extremamente grandes"""
        # Nome muito longo
        very_long_name = "A" * 10000
        enrollment_data = {
            "name": very_long_name,
            "age": 25,
            "cpf": "123.456.789-01"
        }
        
        response = api_client.post("/enrollments/", json=enrollment_data)
        # Pode aceitar ou rejeitar, mas não deve quebrar o servidor
        assert response.status_code in [200, 400, 413, 422]

    def test_unicode_and_special_characters(self, api_client: TestClient, sample_age_groups):
        """Testa caracteres Unicode e especiais"""
        special_names = [
            "José da Silva",  # Acentos
            "François Müller",  # Caracteres especiais
            "李小明",  # Caracteres chineses
            "محمد علي",  # Caracteres árabes
            "🙂 João Silva",  # Emoji
            "João\nSilva",  # Quebra de linha
            "João\tSilva",  # Tab
            "João\"Silva",  # Aspas
            "João'Silva",  # Apóstrofe
            "João\\Silva",  # Barra invertida
        ]
        
        for name in special_names:
            enrollment_data = {
                "name": name,
                "age": 25,
                "cpf": "123.456.789-01"
            }
            
            response = api_client.post("/enrollments/", json=enrollment_data)
            # Deve aceitar ou rejeitar graciosamente
            assert response.status_code in [200, 400, 422]

    def test_sql_injection_attempts(self, api_client: TestClient, sample_age_groups):
        """Testa tentativas de SQL injection (mesmo usando MongoDB)"""
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
            
            response = api_client.post("/enrollments/", json=enrollment_data)
            # Não deve quebrar o sistema
            assert response.status_code in [200, 400, 422]
            
            # Verifica se o sistema ainda funciona
            health_response = api_client.get("/")
            assert health_response.status_code == 200

    def test_nosql_injection_attempts(self, api_client: TestClient, sample_age_groups):
        """Testa tentativas de NoSQL injection"""
        nosql_injections = [
            {"$ne": None},
            {"$gt": ""},
            {"$where": "function() { return true; }"},
            {"$regex": ".*"},
        ]
        
        for injection in nosql_injections:
            # Tenta injeção no campo name
            enrollment_data = {
                "name": injection,
                "age": 25,
                "cpf": "123.456.789-01"
            }
            
            response = api_client.post("/enrollments/", json=enrollment_data)
            # Deve rejeitar ou tratar adequadamente
            assert response.status_code in [200, 400, 422]

    def test_concurrent_age_group_modifications(self, api_client: TestClient, clean_database):
        """Testa modificações simultâneas de age groups"""
        # Cria um age group
        age_group_data = {"min_age": 18, "max_age": 25}
        response = api_client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 200
        age_group_id = response.json()["id"]
        
        # Tenta múltiplas operações simultâneas no mesmo age group
        import concurrent.futures
        
        def update_age_group(new_max_age: int):
            update_data = {"min_age": 18, "max_age": new_max_age}
            return api_client.put(f"/age-groups/{age_group_id}", json=update_data)
        
        def delete_age_group():
            return api_client.delete(f"/age-groups/{age_group_id}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submete operações simultâneas
            futures = [
                executor.submit(update_age_group, 30),
                executor.submit(update_age_group, 35),
                executor.submit(delete_age_group),
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Pelo menos uma operação deve ter sucesso
        successful_operations = [r for r in results if r.status_code in [200, 404]]
        assert len(successful_operations) >= 1

    def test_boundary_age_values(self, api_client: TestClient, clean_database):
        """Testa valores extremos de idade"""
        # Cria age groups para testar
        extreme_age_groups = [
            {"min_age": 0, "max_age": 0},
            {"min_age": 1, "max_age": 1},
            {"min_age": 150, "max_age": 200},
        ]
        
        for age_group_data in extreme_age_groups:
            response = api_client.post("/age-groups/", json=age_group_data)
            # Aceita ou rejeita, mas não deve quebrar
            assert response.status_code in [200, 400, 422]

    def test_negative_values(self, api_client: TestClient, clean_database):
        """Testa valores negativos"""
        negative_test_cases = [
            {"min_age": -1, "max_age": 25},  # Idade mínima negativa
            {"min_age": 18, "max_age": -1},  # Idade máxima negativa
            {"min_age": -10, "max_age": -5}, # Ambas negativas
        ]
        
        for age_group_data in negative_test_cases:
            response = api_client.post("/age-groups/", json=age_group_data)
            assert response.status_code in [400, 422]  # Deve rejeitar
        
        # Testa idade negativa em enrollment
        enrollment_data = {
            "name": "Teste Negativo",
            "age": -5,
            "cpf": "123.456.789-01"
        }
        response = api_client.post("/enrollments/", json=enrollment_data)
        assert response.status_code in [400, 422]

    def test_missing_content_type_header(self, api_client: TestClient, sample_age_groups):
        """Testa requisições sem Content-Type"""
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": "123.456.789-01"
        }
        
        response = api_client.session.post(
            f"{api_client.base_url}/enrollments/",
            data=json.dumps(enrollment_data)
            # Sem header Content-Type
        )
        
        # Deve rejeitar ou tratar adequadamente
        assert response.status_code in [200, 400, 415, 422]

    def test_wrong_content_type_header(self, api_client: TestClient, sample_age_groups):
        """Testa requisições com Content-Type incorreto"""
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": "123.456.789-01"
        }
        
        response = api_client.session.post(
            f"{api_client.base_url}/enrollments/",
            data=json.dumps(enrollment_data),
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code in [400, 415, 422]

    def test_empty_request_body(self, api_client: TestClient, clean_database):
        """Testa requisições com corpo vazio"""
        response = api_client.session.post(
            f"{api_client.base_url}/enrollments/",
            data="",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]

    def test_null_values_in_json(self, api_client: TestClient, sample_age_groups):
        """Testa valores null no JSON"""
        null_test_cases = [
            {"name": None, "age": 25, "cpf": "123.456.789-01"},
            {"name": "João", "age": None, "cpf": "123.456.789-01"},
            {"name": "João", "age": 25, "cpf": None},
        ]
        
        for enrollment_data in null_test_cases:
            response = api_client.post("/enrollments/", json=enrollment_data)
            assert response.status_code in [400, 422]

    def test_wrong_data_types(self, api_client: TestClient, sample_age_groups):
        """Testa tipos de dados incorretos"""
        wrong_type_cases = [
            {"name": 123, "age": 25, "cpf": "123.456.789-01"},  # Nome como número
            {"name": "João", "age": "25", "cpf": "123.456.789-01"},  # Idade como string
            {"name": "João", "age": 25.5, "cpf": "123.456.789-01"},  # Idade como float
            {"name": "João", "age": 25, "cpf": 12345678901},  # CPF como número
        ]
        
        for enrollment_data in wrong_type_cases:
            response = api_client.post("/enrollments/", json=enrollment_data)
            # Pode aceitar (conversão automática) ou rejeitar
            assert response.status_code in [200, 400, 422]

    def test_extremely_long_cpf(self, api_client: TestClient, sample_age_groups):
        """Testa CPF extremamente longo"""
        very_long_cpf = "1" * 1000
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": very_long_cpf
        }
        
        response = api_client.post("/enrollments/", json=enrollment_data)
        assert response.status_code in [400, 422]

    def test_age_group_with_same_min_max(self, api_client: TestClient, clean_database):
        """Testa age group com min_age igual a max_age"""
        age_group_data = {"min_age": 25, "max_age": 25}
        
        response = api_client.post("/age-groups/", json=age_group_data)
        # Pode ser válido (idade exata) ou inválido
        assert response.status_code in [200, 400, 422]

    def test_overlapping_age_groups_edge_case(self, api_client: TestClient, clean_database):
        """Testa age groups com sobreposição nos limites"""
        # Cria primeiro age group
        response1 = api_client.post("/age-groups/", json={"min_age": 18, "max_age": 25})
        assert response1.status_code == 200
        
        # Testa sobreposição exata nos limites
        edge_cases = [
            {"min_age": 25, "max_age": 30},  # Começa onde o outro termina
            {"min_age": 15, "max_age": 18},  # Termina onde o outro começa
            {"min_age": 20, "max_age": 23},  # Completamente dentro
            {"min_age": 15, "max_age": 30},  # Engloba completamente
        ]
        
        for age_group_data in edge_cases:
            response = api_client.post("/age-groups/", json=age_group_data)
            # Sistema pode permitir ou não sobreposições
            assert response.status_code in [200, 400, 422] 