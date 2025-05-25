import pytest
import time
from typing import Dict, Any
from tests.conftest import TestClient, wait_for_enrollment_processing


class TestEnrollments:
    """Testes para os endpoints de Enrollments"""

    def test_create_enrollment_success(self, api_client: TestClient, sample_age_groups, valid_enrollment_data):
        """Testa criação bem-sucedida de enrollment"""
        response = api_client.post("/enrollments/", json=valid_enrollment_data)
        
        assert response.status_code == 200
        enrollment = response.json()
        assert "id" in enrollment
        assert enrollment["status"] == "pending"

    def test_create_enrollment_invalid_data(self, api_client: TestClient, sample_age_groups, invalid_enrollment_data):
        """Testa criação de enrollment com dados inválidos"""
        for invalid_data in invalid_enrollment_data:
            response = api_client.post("/enrollments/", json=invalid_data)
            assert response.status_code in [400, 422]  # Bad request ou validation error

    def test_create_enrollment_no_age_group(self, api_client: TestClient, clean_database):
        """Testa criação de enrollment sem age groups disponíveis"""
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": "123.456.789-01"
        }
        
        response = api_client.post("/enrollments/", json=enrollment_data)
        
        assert response.status_code == 400
        error = response.json()
        assert "idade" in error["detail"].lower()

    def test_create_enrollment_age_outside_groups(self, api_client: TestClient, sample_age_groups):
        """Testa criação de enrollment com idade fora dos age groups"""
        enrollment_data = {
            "name": "Maria Silva",
            "age": 100,  # Idade fora dos age groups criados (18-50)
            "cpf": "123.456.789-01"
        }
        
        response = api_client.post("/enrollments/", json=enrollment_data)
        
        assert response.status_code == 400
        error = response.json()
        assert "idade" in error["detail"].lower()

    def test_get_enrollment_status_pending(self, api_client: TestClient, sample_age_groups, valid_enrollment_data):
        """Testa busca de status de enrollment pendente"""
        # Cria enrollment
        response = api_client.post("/enrollments/", json=valid_enrollment_data)
        enrollment_id = response.json()["id"]
        
        # Busca status imediatamente (deve estar pending)
        status_response = api_client.get(f"/enrollments/{enrollment_id}")
        
        assert status_response.status_code == 200
        status = status_response.json()
        assert status["id"] == enrollment_id
        assert status["status"] == "pending"
        assert "age_group_id" in status

    def test_get_enrollment_status_processed(self, api_client: TestClient, sample_age_groups, valid_enrollment_data):
        """Testa busca de status de enrollment processado"""
        # Cria enrollment
        response = api_client.post("/enrollments/", json=valid_enrollment_data)
        enrollment_id = response.json()["id"]
        
        # Aguarda processamento
        try:
            processed_status = wait_for_enrollment_processing(api_client, enrollment_id, timeout=15)
            
            assert processed_status["id"] == enrollment_id
            assert processed_status["status"] == "processed"
            assert processed_status["message"] is not None
            assert "age_group_id" in processed_status
        except TimeoutError:
            pytest.fail("Enrollment não foi processado no tempo esperado")

    def test_get_enrollment_not_found(self, api_client: TestClient, clean_database):
        """Testa busca de enrollment inexistente"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = api_client.get(f"/enrollments/{fake_id}")
        
        assert response.status_code == 404

    def test_get_enrollment_invalid_id_format(self, api_client: TestClient, clean_database):
        """Testa busca de enrollment com ID em formato inválido"""
        invalid_id = "invalid-uuid-format"
        
        response = api_client.get(f"/enrollments/{invalid_id}")
        
        assert response.status_code in [400, 422, 404]

    def test_multiple_enrollments_same_cpf(self, api_client: TestClient, sample_age_groups):
        """Testa criação de múltiplos enrollments com mesmo CPF"""
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": "123.456.789-01"
        }
        
        # Primeiro enrollment
        response1 = api_client.post("/enrollments/", json=enrollment_data)
        assert response1.status_code == 200
        
        # Segundo enrollment com mesmo CPF
        enrollment_data["name"] = "João Santos"  # Nome diferente, mesmo CPF
        response2 = api_client.post("/enrollments/", json=enrollment_data)
        
        # Atualmente permite, mas seria bom validar duplicação de CPF
        assert response2.status_code == 200

    def test_enrollment_cpf_formats(self, api_client: TestClient, sample_age_groups):
        """Testa diferentes formatos de CPF"""
        cpf_formats = [
            "123.456.789-01",  # Formato com pontos e hífen
            "12345678901",     # Formato sem pontos e hífen
            "123 456 789 01",  # Formato com espaços
        ]
        
        for i, cpf in enumerate(cpf_formats):
            enrollment_data = {
                "name": f"Pessoa {i+1}",
                "age": 25,
                "cpf": cpf
            }
            
            response = api_client.post("/enrollments/", json=enrollment_data)
            # Deve aceitar ou rejeitar consistentemente
            assert response.status_code in [200, 400, 422]

    def test_enrollment_invalid_cpf_formats(self, api_client: TestClient, sample_age_groups):
        """Testa CPFs com formatos claramente inválidos"""
        invalid_cpfs = [
            "111.111.111-11",  # CPF com todos os dígitos iguais
            "000.000.000-00",  # CPF zerado
            "123.456.789-00",  # CPF com dígito verificador inválido
            "abc.def.ghi-jk",  # CPF com letras
            "123.456.789",     # CPF incompleto
            "123.456.789-012", # CPF com dígito extra
        ]
        
        for cpf in invalid_cpfs:
            enrollment_data = {
                "name": "Pessoa Teste",
                "age": 25,
                "cpf": cpf
            }
            
            response = api_client.post("/enrollments/", json=enrollment_data)
            assert response.status_code in [400, 422]

    def test_enrollment_age_boundaries(self, api_client: TestClient, sample_age_groups):
        """Testa enrollments com idades nos limites dos age groups"""
        # Age groups criados: 18-25, 26-35, 36-50
        boundary_ages = [18, 25, 26, 35, 36, 50]
        
        for age in boundary_ages:
            enrollment_data = {
                "name": f"Pessoa {age} anos",
                "age": age,
                "cpf": f"123.456.789-{age:02d}"
            }
            
            response = api_client.post("/enrollments/", json=enrollment_data)
            assert response.status_code == 200

    def test_enrollment_processing_time(self, api_client: TestClient, sample_age_groups, valid_enrollment_data):
        """Testa se o processamento ocorre dentro do tempo esperado"""
        # Cria enrollment
        response = api_client.post("/enrollments/", json=valid_enrollment_data)
        enrollment_id = response.json()["id"]
        
        start_time = time.time()
        
        # Aguarda processamento
        try:
            wait_for_enrollment_processing(api_client, enrollment_id, timeout=10)
            processing_time = time.time() - start_time
            
            # Verifica se processou em tempo razoável (worker simula 2s + overhead)
            assert processing_time < 8  # Margem para overhead de rede/sistema
            
        except TimeoutError:
            pytest.fail("Enrollment não foi processado no tempo esperado")

    def test_enrollment_worker_integration(self, api_client: TestClient, sample_age_groups):
        """Testa integração completa com o worker"""
        enrollments_data = [
            {"name": "João Silva", "age": 20, "cpf": "123.456.789-01"},
            {"name": "Maria Santos", "age": 30, "cpf": "987.654.321-01"},
            {"name": "Pedro Oliveira", "age": 40, "cpf": "456.789.123-01"},
        ]
        
        enrollment_ids = []
        
        # Cria múltiplos enrollments
        for enrollment_data in enrollments_data:
            response = api_client.post("/enrollments/", json=enrollment_data)
            assert response.status_code == 200
            enrollment_ids.append(response.json()["id"])
        
        # Aguarda processamento de todos
        for enrollment_id in enrollment_ids:
            try:
                processed_status = wait_for_enrollment_processing(api_client, enrollment_id, timeout=15)
                assert processed_status["status"] == "processed"
            except TimeoutError:
                pytest.fail(f"Enrollment {enrollment_id} não foi processado no tempo esperado")

    def test_enrollment_name_validation(self, api_client: TestClient, sample_age_groups):
        """Testa validação de nomes"""
        name_test_cases = [
            ("", False),  # Nome vazio
            ("A", True),  # Nome muito curto (pode ser válido)
            ("João da Silva Santos Oliveira Pereira", True),  # Nome longo
            ("José123", True),  # Nome com números (pode ser válido)
            ("Maria-José", True),  # Nome com hífen
            ("Ana Paula", True),  # Nome com espaço
        ]
        
        for name, should_succeed in name_test_cases:
            enrollment_data = {
                "name": name,
                "age": 25,
                "cpf": "123.456.789-01"
            }
            
            response = api_client.post("/enrollments/", json=enrollment_data)
            
            if should_succeed:
                assert response.status_code == 200
            else:
                assert response.status_code in [400, 422] 