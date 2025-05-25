import pytest
import time
import concurrent.futures
from typing import List, Dict, Any
from tests.conftest import TestClient, wait_for_enrollment_processing


class TestPerformance:
    """Testes de performance e carga do sistema"""

    def test_concurrent_enrollments(self, api_client: TestClient, sample_age_groups):
        """Testa criação simultânea de múltiplos enrollments"""
        def create_enrollment(index: int) -> Dict[str, Any]:
            enrollment_data = {
                "name": f"Pessoa {index}",
                "age": 25,
                "cpf": f"123.456.{index:03d}-01"
            }
            response = api_client.post("/enrollments/", json=enrollment_data)
            return {
                "index": index,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None
            }

        # Testa com 10 enrollments simultâneos
        num_enrollments = 10
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_enrollment, i) for i in range(num_enrollments)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        # Verifica se todos foram criados com sucesso
        successful_enrollments = [r for r in results if r["status_code"] == 200]
        assert len(successful_enrollments) == num_enrollments
        
        # Verifica tempo total (deve ser razoável)
        total_time = end_time - start_time
        assert total_time < 30  # Máximo 30 segundos para 10 enrollments

    def test_age_groups_crud_performance(self, api_client: TestClient, clean_database):
        """Testa performance das operações CRUD de age groups"""
        num_groups = 20
        
        # Teste de criação em massa
        start_time = time.time()
        created_groups = []
        
        for i in range(num_groups):
            age_group_data = {
                "min_age": i * 5,
                "max_age": (i * 5) + 4
            }
            response = api_client.post("/age-groups/", json=age_group_data)
            assert response.status_code == 200
            created_groups.append(response.json())
        
        creation_time = time.time() - start_time
        
        # Teste de listagem
        start_time = time.time()
        response = api_client.get("/age-groups/")
        listing_time = time.time() - start_time
        
        assert response.status_code == 200
        assert len(response.json()) == num_groups
        
        # Teste de busca individual
        start_time = time.time()
        for group in created_groups[:5]:  # Testa apenas 5 para não demorar muito
            response = api_client.get(f"/age-groups/{group['id']}")
            assert response.status_code == 200
        individual_search_time = time.time() - start_time
        
        # Verifica tempos (valores razoáveis)
        assert creation_time < 10  # Máximo 10 segundos para criar 20 groups
        assert listing_time < 2    # Máximo 2 segundos para listar
        assert individual_search_time < 5  # Máximo 5 segundos para 5 buscas

    def test_enrollment_processing_queue_performance(self, api_client: TestClient, sample_age_groups):
        """Testa performance da fila de processamento"""
        num_enrollments = 5  # Número menor para não sobrecarregar o teste
        enrollment_ids = []
        
        # Cria múltiplos enrollments rapidamente
        start_time = time.time()
        for i in range(num_enrollments):
            enrollment_data = {
                "name": f"Pessoa Queue {i}",
                "age": 25,
                "cpf": f"987.654.{i:03d}-01"
            }
            response = api_client.post("/enrollments/", json=enrollment_data)
            assert response.status_code == 200
            enrollment_ids.append(response.json()["id"])
        
        creation_time = time.time() - start_time
        
        # Aguarda processamento de todos
        start_processing_time = time.time()
        processed_count = 0
        
        for enrollment_id in enrollment_ids:
            try:
                wait_for_enrollment_processing(api_client, enrollment_id, timeout=20)
                processed_count += 1
            except TimeoutError:
                pass  # Conta quantos foram processados
        
        total_processing_time = time.time() - start_processing_time
        
        # Verifica se pelo menos 80% foram processados
        assert processed_count >= (num_enrollments * 0.8)
        
        # Verifica tempos
        assert creation_time < 5  # Criação deve ser rápida
        assert total_processing_time < 30  # Processamento deve ser razoável

    def test_api_response_times(self, api_client: TestClient, sample_age_groups):
        """Testa tempos de resposta dos endpoints principais"""
        
        # Testa tempo de resposta do health check
        start_time = time.time()
        response = api_client.get("/")
        health_time = time.time() - start_time
        assert response.status_code == 200
        assert health_time < 1  # Deve responder em menos de 1 segundo
        
        # Testa tempo de resposta da listagem de age groups
        start_time = time.time()
        response = api_client.get("/age-groups/")
        list_time = time.time() - start_time
        assert response.status_code == 200
        assert list_time < 2  # Deve responder em menos de 2 segundos
        
        # Testa tempo de resposta da criação de enrollment
        enrollment_data = {
            "name": "Teste Performance",
            "age": 25,
            "cpf": "111.222.333-44"
        }
        start_time = time.time()
        response = api_client.post("/enrollments/", json=enrollment_data)
        enrollment_time = time.time() - start_time
        assert response.status_code == 200
        assert enrollment_time < 3  # Deve responder em menos de 3 segundos

    def test_database_consistency_under_load(self, api_client: TestClient, sample_age_groups):
        """Testa consistência do banco sob carga"""
        
        def create_and_check_enrollment(index: int) -> bool:
            enrollment_data = {
                "name": f"Consistência {index}",
                "age": 25,
                "cpf": f"555.666.{index:03d}-77"
            }
            
            # Cria enrollment
            response = api_client.post("/enrollments/", json=enrollment_data)
            if response.status_code != 200:
                return False
            
            enrollment_id = response.json()["id"]
            
            # Verifica se pode buscar imediatamente
            status_response = api_client.get(f"/enrollments/{enrollment_id}")
            return status_response.status_code == 200
        
        # Executa múltiplas operações simultâneas
        num_operations = 8
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(create_and_check_enrollment, i) for i in range(num_operations)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verifica se todas as operações foram consistentes
        successful_operations = sum(results)
        assert successful_operations >= (num_operations * 0.9)  # Pelo menos 90% de sucesso

    @pytest.mark.slow
    def test_long_running_stability(self, api_client: TestClient, sample_age_groups):
        """Testa estabilidade do sistema em execução prolongada"""
        # Marca como teste lento - só executa se especificamente solicitado
        
        num_cycles = 10
        enrollments_per_cycle = 3
        
        for cycle in range(num_cycles):
            # Cria enrollments
            enrollment_ids = []
            for i in range(enrollments_per_cycle):
                enrollment_data = {
                    "name": f"Ciclo {cycle} Pessoa {i}",
                    "age": 25 + (i % 10),
                    "cpf": f"888.{cycle:03d}.{i:03d}-99"
                }
                response = api_client.post("/enrollments/", json=enrollment_data)
                assert response.status_code == 200
                enrollment_ids.append(response.json()["id"])
            
            # Aguarda um pouco entre ciclos
            time.sleep(1)
            
            # Verifica se ainda consegue acessar os enrollments
            for enrollment_id in enrollment_ids:
                response = api_client.get(f"/enrollments/{enrollment_id}")
                assert response.status_code == 200
        
        # Verifica se a API ainda responde normalmente
        response = api_client.get("/")
        assert response.status_code == 200

    def test_memory_usage_pattern(self, api_client: TestClient, sample_age_groups):
        """Testa padrão de uso de memória através de operações repetitivas"""
        
        # Executa múltiplos ciclos de criação e busca
        for cycle in range(5):
            # Cria vários age groups
            created_groups = []
            for i in range(10):
                age_group_data = {
                    "min_age": (cycle * 100) + (i * 2),
                    "max_age": (cycle * 100) + (i * 2) + 1
                }
                response = api_client.post("/age-groups/", json=age_group_data)
                if response.status_code == 200:
                    created_groups.append(response.json())
            
            # Lista todos os age groups
            response = api_client.get("/age-groups/")
            assert response.status_code == 200
            
            # Remove os age groups criados neste ciclo
            for group in created_groups:
                api_client.delete(f"/age-groups/{group['id']}")
            
            # Pequena pausa entre ciclos
            time.sleep(0.5)
        
        # Verifica se o sistema ainda está responsivo
        response = api_client.get("/age-groups/")
        assert response.status_code == 200 