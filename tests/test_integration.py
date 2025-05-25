import pytest
import time
import json
from typing import Dict, Any
from tests.conftest import TestClient, wait_for_enrollment_processing


@pytest.mark.integration
class TestIntegrationWorkflow:
    """Testes de integração que verificam o fluxo completo do sistema"""

    def test_complete_enrollment_workflow(self, api_client: TestClient, clean_database):
        """Testa o fluxo completo: criar age group -> criar enrollment -> processar -> verificar"""
        
        # 1. Criar age group
        age_group_data = {"min_age": 18, "max_age": 25}
        response = api_client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 200
        age_group = response.json()
        age_group_id = age_group["id"]
        
        # 2. Verificar que age group foi criado
        response = api_client.get(f"/age-groups/{age_group_id}")
        assert response.status_code == 200
        assert response.json()["min_age"] == 18
        assert response.json()["max_age"] == 25
        
        # 3. Criar enrollment válido
        enrollment_data = {
            "name": "João da Silva",
            "age": 22,
            "cpf": "123.456.789-01"
        }
        response = api_client.post("/enrollments/", json=enrollment_data)
        assert response.status_code == 200
        enrollment = response.json()
        enrollment_id = enrollment["id"]
        assert enrollment["status"] == "pending"
        
        # 4. Verificar status inicial
        response = api_client.get(f"/enrollments/{enrollment_id}")
        assert response.status_code == 200
        status = response.json()
        assert status["status"] == "pending"
        assert status["age_group_id"] == age_group_id
        
        # 5. Aguardar processamento pelo worker
        try:
            processed_status = wait_for_enrollment_processing(api_client, enrollment_id, timeout=15)
            assert processed_status["status"] == "processed"
            assert processed_status["message"] is not None
            assert processed_status["age_group_id"] == age_group_id
        except TimeoutError:
            pytest.fail("Worker não processou o enrollment no tempo esperado")

    def test_multiple_age_groups_workflow(self, api_client: TestClient, clean_database):
        """Testa criação de múltiplos age groups e enrollments correspondentes"""
        
        # Criar múltiplos age groups
        age_groups_data = [
            {"min_age": 18, "max_age": 25},
            {"min_age": 26, "max_age": 35},
            {"min_age": 36, "max_age": 50}
        ]
        
        created_groups = []
        for age_group_data in age_groups_data:
            response = api_client.post("/age-groups/", json=age_group_data)
            assert response.status_code == 200
            created_groups.append(response.json())
        
        # Verificar listagem de age groups
        response = api_client.get("/age-groups/")
        assert response.status_code == 200
        assert len(response.json()) == 3
        
        # Criar enrollments para cada age group
        enrollments_data = [
            {"name": "João Silva", "age": 20, "cpf": "123.456.789-01"},  # Grupo 1
            {"name": "Maria Santos", "age": 30, "cpf": "987.654.321-01"},  # Grupo 2
            {"name": "Pedro Oliveira", "age": 40, "cpf": "456.789.123-01"}  # Grupo 3
        ]
        
        enrollment_ids = []
        for enrollment_data in enrollments_data:
            response = api_client.post("/enrollments/", json=enrollment_data)
            assert response.status_code == 200
            enrollment_ids.append(response.json()["id"])
        
        # Aguardar processamento de todos
        for i, enrollment_id in enumerate(enrollment_ids):
            try:
                processed_status = wait_for_enrollment_processing(api_client, enrollment_id, timeout=15)
                assert processed_status["status"] == "processed"
                # Verificar se foi associado ao age group correto
                expected_group_id = created_groups[i]["id"]
                assert processed_status["age_group_id"] == expected_group_id
            except TimeoutError:
                pytest.fail(f"Enrollment {enrollment_id} não foi processado no tempo esperado")

    def test_enrollment_without_age_group(self, api_client: TestClient, clean_database):
        """Testa tentativa de criar enrollment sem age groups disponíveis"""
        
        # Tentar criar enrollment sem age groups
        enrollment_data = {
            "name": "João Silva",
            "age": 25,
            "cpf": "123.456.789-01"
        }
        
        response = api_client.post("/enrollments/", json=enrollment_data)
        assert response.status_code == 400
        error = response.json()
        assert "idade" in error["detail"].lower()

    def test_enrollment_age_outside_groups(self, api_client: TestClient, clean_database):
        """Testa enrollment com idade fora dos age groups disponíveis"""
        
        # Criar age group limitado
        age_group_data = {"min_age": 18, "max_age": 25}
        response = api_client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 200
        
        # Tentar criar enrollment com idade fora do range
        enrollment_data = {
            "name": "Maria Silva",
            "age": 30,  # Fora do range 18-25
            "cpf": "123.456.789-01"
        }
        
        response = api_client.post("/enrollments/", json=enrollment_data)
        assert response.status_code == 400
        error = response.json()
        assert "idade" in error["detail"].lower()

    def test_age_group_crud_integration(self, api_client: TestClient, clean_database):
        """Testa operações CRUD completas de age groups"""
        
        # 1. Criar
        age_group_data = {"min_age": 18, "max_age": 25}
        response = api_client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 200
        age_group_id = response.json()["id"]
        
        # 2. Ler
        response = api_client.get(f"/age-groups/{age_group_id}")
        assert response.status_code == 200
        assert response.json()["min_age"] == 18
        assert response.json()["max_age"] == 25
        
        # 3. Atualizar
        update_data = {"min_age": 20, "max_age": 30}
        response = api_client.put(f"/age-groups/{age_group_id}", json=update_data)
        assert response.status_code == 200
        updated_group = response.json()
        assert updated_group["min_age"] == 20
        assert updated_group["max_age"] == 30
        
        # 4. Verificar atualização
        response = api_client.get(f"/age-groups/{age_group_id}")
        assert response.status_code == 200
        assert response.json()["min_age"] == 20
        assert response.json()["max_age"] == 30
        
        # 5. Deletar
        response = api_client.delete(f"/age-groups/{age_group_id}")
        assert response.status_code == 200
        
        # 6. Verificar deleção
        response = api_client.get(f"/age-groups/{age_group_id}")
        assert response.status_code == 404

    def test_system_health_and_connectivity(self, api_client: TestClient):
        """Testa conectividade e saúde do sistema"""
        
        # Verificar health check
        response = api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verificar endpoints principais estão respondendo
        response = api_client.get("/age-groups/")
        assert response.status_code == 200
        
        # Verificar que sistema aceita requisições válidas
        age_group_data = {"min_age": 18, "max_age": 25}
        response = api_client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 200

    def test_concurrent_operations_integration(self, api_client: TestClient, clean_database):
        """Testa operações simultâneas no sistema"""
        import concurrent.futures
        
        # Criar age group base
        age_group_data = {"min_age": 18, "max_age": 50}
        response = api_client.post("/age-groups/", json=age_group_data)
        assert response.status_code == 200
        
        def create_enrollment(index: int) -> Dict[str, Any]:
            enrollment_data = {
                "name": f"Pessoa {index}",
                "age": 25,
                "cpf": f"123.456.{index:03d}-01"
            }
            response = api_client.post("/enrollments/", json=enrollment_data)
            return {
                "index": index,
                "success": response.status_code == 200,
                "enrollment_id": response.json().get("id") if response.status_code == 200 else None
            }
        
        # Criar múltiplos enrollments simultaneamente
        num_enrollments = 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_enrollment, i) for i in range(num_enrollments)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verificar que todos foram criados com sucesso
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) == num_enrollments
        
        # Verificar que pelo menos alguns foram processados
        time.sleep(5)  # Aguarda processamento
        processed_count = 0
        for result in successful_results:
            if result["enrollment_id"]:
                response = api_client.get(f"/enrollments/{result['enrollment_id']}")
                if response.status_code == 200 and response.json()["status"] == "processed":
                    processed_count += 1
        
        # Pelo menos 50% devem ter sido processados
        assert processed_count >= (num_enrollments * 0.5)

    def test_data_persistence_integration(self, api_client: TestClient, clean_database):
        """Testa persistência de dados através de operações"""
        
        # Criar dados
        age_group_data = {"min_age": 18, "max_age": 25}
        response = api_client.post("/age-groups/", json=age_group_data)
        age_group_id = response.json()["id"]
        
        enrollment_data = {
            "name": "João Silva",
            "age": 22,
            "cpf": "123.456.789-01"
        }
        response = api_client.post("/enrollments/", json=enrollment_data)
        enrollment_id = response.json()["id"]
        
        # Aguardar processamento
        try:
            wait_for_enrollment_processing(api_client, enrollment_id, timeout=10)
        except TimeoutError:
            pass  # Continua mesmo se não processar
        
        # Verificar que dados persistem após operações
        response = api_client.get(f"/age-groups/{age_group_id}")
        assert response.status_code == 200
        
        response = api_client.get(f"/enrollments/{enrollment_id}")
        assert response.status_code == 200
        
        # Verificar listagens
        response = api_client.get("/age-groups/")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_error_handling_integration(self, api_client: TestClient, clean_database):
        """Testa tratamento de erros em cenários de integração"""
        
        # Tentar buscar recursos inexistentes
        response = api_client.get("/age-groups/507f1f77bcf86cd799439011")
        assert response.status_code == 404
        
        response = api_client.get("/enrollments/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        
        # Tentar atualizar recursos inexistentes
        update_data = {"min_age": 20, "max_age": 30}
        response = api_client.put("/age-groups/507f1f77bcf86cd799439011", json=update_data)
        assert response.status_code == 404
        
        # Tentar deletar recursos inexistentes
        response = api_client.delete("/age-groups/507f1f77bcf86cd799439011")
        assert response.status_code == 404
        
        # Verificar que sistema continua funcionando após erros
        response = api_client.get("/")
        assert response.status_code == 200 