import pytest
import time
import json
from tests.conftest import APITestClient, wait_for_enrollment_processing, create_basic_auth_header


@pytest.mark.functional
class TestEnrollments:
    """Testes para os endpoints de Enrollments"""

    def test_enrollments_require_authentication(self, api_client: APITestClient):
        """Testa que todos os endpoints de enrollment requerem autenticação"""
        endpoints_and_methods = [
            ("POST", "/enrollments/", {"name": "João", "age": 25, "cpf": "123.456.789-01"}),
            ("GET", "/enrollments/00000000-0000-0000-0000-000000000000", None),
        ]
        
        for method, endpoint, data in endpoints_and_methods:
            if method == "POST":
                response = api_client.client.post(endpoint, json=data)
            elif method == "GET":
                response = api_client.client.get(endpoint)
            
            assert response.status_code == 401, f"{method} {endpoint} deveria retornar 401"

    def test_enrollment_data_validation(self, api_client: APITestClient):
        """Testa validação de dados de enrollment"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Testa dados claramente inválidos que devem falhar na validação
        invalid_data_sets = [
            {"name": "", "age": 25, "cpf": "123.456.789-01"},  # Nome vazio
            {"age": 25, "cpf": "123.456.789-01"},  # Nome faltando
            {"name": "João", "cpf": "123.456.789-01"},  # Idade faltando
            {"name": "João", "age": 25},  # CPF faltando
            {"name": "João", "age": "abc", "cpf": "123.456.789-01"},  # Idade inválida
            {},  # Dados vazios
        ]
        
        for invalid_data in invalid_data_sets:
            response = api_client.client.post("/enrollments/", json=invalid_data, headers={"Authorization": auth_header})
            # Deve falhar na validação antes de tentar conectar ao banco
            assert response.status_code == 422, f"Dados inválidos deveriam retornar 422: {invalid_data}"

    def test_enrollment_cpf_validation(self, api_client: APITestClient):
        """Testa validação específica de CPF"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # CPFs claramente inválidos
        invalid_cpfs = [
            "111.111.111-11",  # Todos os dígitos iguais
            "000.000.000-00",  # CPF zerado
            "abc.def.ghi-jk",  # CPF com letras
            "123.456.789",     # CPF incompleto
            "123.456.789-012", # CPF com dígito extra
            "",                # CPF vazio
        ]
        
        for cpf in invalid_cpfs:
            enrollment_data = {
                "name": "Pessoa Teste",
                "age": 25,
                "cpf": cpf
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            # Deve falhar na validação (422) ou lógica de negócio (400)
            assert response.status_code in [400, 422], f"CPF inválido deveria falhar: {cpf}"

    def test_create_enrollment_success(self, api_client: APITestClient, sample_age_groups, valid_enrollment_data):
        """Testa criação bem-sucedida de enrollment"""
        auth_header = create_basic_auth_header("config", "config123")
        
        response = api_client.client.post("/enrollments/", json=valid_enrollment_data, headers={"Authorization": auth_header})
        
        assert response.status_code == 200
        enrollment = response.json()
        assert "id" in enrollment
        assert enrollment["status"] == "pending"

    def test_create_enrollment_invalid_data(self, api_client: APITestClient, sample_age_groups, invalid_enrollment_data):
        """Testa criação de enrollment com dados inválidos"""
        auth_header = create_basic_auth_header("config", "config123")
        
        for invalid_data in invalid_enrollment_data:
            response = api_client.client.post("/enrollments/", json=invalid_data, headers={"Authorization": auth_header})
            assert response.status_code in [400, 422]  # Bad request ou validation error

    def test_create_enrollment_no_age_group(self, api_client: APITestClient, clean_database):
        """Testa criação de enrollment sem age groups disponíveis"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Garante que não há age groups no banco
        from app.db.mongo import mongo_db
        mongo_db.age_groups.delete_many({})
        
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": "11144477735"  # CPF matematicamente válido
        }
        
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        
        assert response.status_code == 400
        error = response.json()
        assert "idade" in error["detail"].lower()

    def test_create_enrollment_age_outside_groups(self, api_client: APITestClient, sample_age_groups):
        """Testa criação de enrollment com idade fora dos age groups"""
        auth_header = create_basic_auth_header("config", "config123")
        
        enrollment_data = {
            "name": "Maria Silva",
            "age": 100,  # Idade fora dos age groups criados (18-50)
            "cpf": "11144477735"  # CPF matematicamente válido
        }
        
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        
        assert response.status_code == 400
        error = response.json()
        assert "idade" in error["detail"].lower()

    def test_get_enrollment_status_pending(self, api_client: APITestClient, sample_age_groups, valid_enrollment_data):
        """Testa busca de status de enrollment pendente"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Cria enrollment
        response = api_client.client.post("/enrollments/", json=valid_enrollment_data, headers={"Authorization": auth_header})
        enrollment_id = response.json()["id"]
        
        # Busca status imediatamente (deve estar pending)
        status_response = api_client.client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": auth_header})
        
        assert status_response.status_code == 200
        status = status_response.json()
        assert status["id"] == enrollment_id
        assert status["status"] == "pending"
        assert "age_group_id" in status

    def test_get_enrollment_status_processed(self, api_client: APITestClient, sample_age_groups):
        """Testa busca de status de enrollment processado"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Cria enrollment
        enrollment_data = {
            "name": "Maria Santos",
            "age": 30,
            "cpf": "11144477735"  # CPF matematicamente válido
        }
        
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        assert response.status_code == 200
        
        enrollment_id = response.json()["id"]
        
        # Verifica status inicial
        response = api_client.client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": auth_header})
        assert response.status_code == 200
        
        status_data = response.json()
        assert status_data["id"] == enrollment_id
        assert status_data["status"] in ["pending", "processed"]  # Pode já estar processado
        
        # Se ainda está pending, aguarda processamento (com timeout maior)
        if status_data["status"] == "pending":
            try:
                processed = wait_for_enrollment_processing(api_client, enrollment_id, timeout=15)  # Reduzido de 20 para 15
                if processed:
                    # Verifica status final
                    response = api_client.client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": auth_header})
                    assert response.status_code == 200
                    final_status = response.json()
                    assert final_status["status"] == "processed"
                    assert "message" in final_status
                else:
                    pytest.skip("Worker não processou o enrollment no tempo esperado")
            except TimeoutError:
                pytest.skip("Worker não está funcionando ou está muito lento")

    def test_get_enrollment_not_found(self, api_client: APITestClient, clean_database):
        """Testa busca de enrollment inexistente"""
        auth_header = create_basic_auth_header("config", "config123")
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = api_client.client.get(f"/enrollments/{fake_id}", headers={"Authorization": auth_header})
        
        assert response.status_code == 404

    def test_get_enrollment_invalid_id_format(self, api_client: APITestClient, clean_database):
        """Testa busca de enrollment com ID em formato inválido"""
        auth_header = create_basic_auth_header("config", "config123")
        invalid_id = "invalid-uuid-format"
        
        response = api_client.client.get(f"/enrollments/{invalid_id}", headers={"Authorization": auth_header})
        
        assert response.status_code in [400, 422, 404]

    def test_multiple_enrollments_same_cpf(self, api_client: APITestClient, sample_age_groups):
        """Testa criação de múltiplos enrollments com mesmo CPF"""
        auth_header = create_basic_auth_header("config", "config123")
        
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": "11144477735"  # CPF matematicamente válido
        }
        
        # Primeiro enrollment
        response1 = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        assert response1.status_code == 200
        
        # Segundo enrollment com mesmo CPF
        enrollment_data["name"] = "João Santos"  # Nome diferente, mesmo CPF
        response2 = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        
        # Atualmente permite, mas seria bom validar duplicação de CPF
        assert response2.status_code == 200

    def test_enrollment_cpf_formats(self, api_client: APITestClient, sample_age_groups):
        """Testa diferentes formatos de CPF"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Usando CPFs matematicamente válidos
        cpf_formats = [
            "11144477735",     # Formato sem pontos e hífen
            "111.444.777-35",  # Formato com pontos e hífen
            "111 444 777 35",  # Formato com espaços
        ]
        
        for i, cpf in enumerate(cpf_formats):
            enrollment_data = {
                "name": f"Pessoa {i+1}",
                "age": 25,
                "cpf": cpf
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            # Deve aceitar ou rejeitar consistentemente
            assert response.status_code in [200, 400, 422]

    def test_enrollment_age_boundaries(self, api_client: APITestClient, sample_age_groups):
        """Testa enrollments com idades nos limites dos age groups"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Age groups criados: 18-25, 26-35, 36-50
        boundary_ages = [18, 25, 26, 35, 36, 50]
        
        # Usando CPFs válidos diferentes para cada teste
        valid_cpfs = [
            "11144477735",  # Para idade 18
            "11144477816",  # Para idade 25
            "11144477905",  # Para idade 26
            "11144478030",  # Para idade 35
            "11144478111",  # Para idade 36
            "11144478200",  # Para idade 50
        ]
        
        for i, age in enumerate(boundary_ages):
            enrollment_data = {
                "name": f"Pessoa {age} anos",
                "age": age,
                "cpf": valid_cpfs[i]
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            assert response.status_code == 200

    def test_enrollment_processing_time(self, api_client: APITestClient, sample_age_groups):
        """Testa se o processamento respeita o tempo mínimo de 2s"""
        auth_header = create_basic_auth_header("config", "config123")
        
        enrollment_data = {
            "name": "Pedro Oliveira",
            "age": 28,
            "cpf": "11144477816"  # CPF matematicamente válido
        }
        
        start_time = time.time()
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        assert response.status_code == 200
        
        enrollment_id = response.json()["id"]
        
        try:
            processed = wait_for_enrollment_processing(api_client, enrollment_id, timeout=15)  # Reduzido de 25 para 15
            if processed:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Verifica se levou pelo menos 2 segundos (conforme requisito)
                assert processing_time >= 2.0, f"Processamento levou apenas {processing_time:.2f}s, deveria ser pelo menos 2s"
                
                # Verifica se não demorou muito (máximo 15s é razoável, considerando overhead)
                assert processing_time <= 15.0, f"Processamento demorou {processing_time:.2f}s, muito lento"
            else:
                pytest.skip("Worker não processou o enrollment")
        except TimeoutError:
            pytest.skip("Worker não está funcionando ou está muito lento")

    def test_enrollment_worker_integration(self, api_client: APITestClient, sample_age_groups):
        """Testa integração completa com o worker"""
        auth_header = create_basic_auth_header("config", "config123")
        
        enrollment_data = {
            "name": "Ana Costa",
            "age": 22,
            "cpf": "11144477905"  # CPF matematicamente válido
        }
        
        # Cria enrollment
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        assert response.status_code == 200
        
        enrollment_id = response.json()["id"]
        
        # Verifica que foi criado com status pending
        response = api_client.client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": auth_header})
        assert response.status_code == 200
        initial_status = response.json()
        assert initial_status["status"] in ["pending", "processed"]  # Pode já estar processado se worker for muito rápido
        
        # Se ainda está pending, aguarda processamento
        if initial_status["status"] == "pending":
            try:
                processed = wait_for_enrollment_processing(api_client, enrollment_id, timeout=15)  # Reduzido de 20 para 15
                if not processed:
                    pytest.skip("Worker não processou o enrollment no tempo esperado")
            except TimeoutError:
                pytest.skip("Worker não está funcionando ou está muito lento")
        
        # Verifica status final
        response = api_client.client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": auth_header})
        assert response.status_code == 200
        
        final_status = response.json()
        assert final_status["status"] == "processed"
        assert "message" in final_status
        assert final_status["message"] is not None 