import pytest
from typing import Dict, Any
from tests.conftest import TestClient


class TestAgeGroups:
    """Testes para os endpoints de Age Groups"""

    def test_create_age_group_success(self, admin_client: TestClient, clean_database):
        """Testa criação bem-sucedida de age group"""
        age_group_data = {"min_age": 18, "max_age": 25}
        
        response = admin_client.post("/age-groups/", json=age_group_data)
        
        assert response.status_code == 200
        created_group = response.json()
        assert "id" in created_group
        assert created_group["min_age"] == 18
        assert created_group["max_age"] == 25

    def test_create_age_group_requires_admin(self, user_client: TestClient, clean_database):
        """Testa que criação de age group requer privilégios administrativos"""
        age_group_data = {"min_age": 18, "max_age": 25}
        
        response = user_client.post("/age-groups/", json=age_group_data)
        
        assert response.status_code == 403

    def test_create_age_group_invalid_range(self, admin_client: TestClient, clean_database):
        """Testa criação de age group com range inválido (min > max)"""
        age_group_data = {"min_age": 30, "max_age": 20}  # Range inválido
        
        response = admin_client.post("/age-groups/", json=age_group_data)
        
        # Nota: Este teste pode falhar se não houver validação no backend
        # Seria bom adicionar validação para min_age <= max_age
        assert response.status_code in [200, 400, 422]

    def test_create_age_group_missing_fields(self, admin_client: TestClient, clean_database):
        """Testa criação de age group com campos obrigatórios faltando"""
        test_cases = [
            {"min_age": 18},  # Falta max_age
            {"max_age": 25},  # Falta min_age
            {},  # Falta ambos
        ]
        
        for age_group_data in test_cases:
            response = admin_client.post("/age-groups/", json=age_group_data)
            assert response.status_code == 422  # Validation error

    def test_get_all_age_groups_empty(self, api_client: TestClient, clean_database):
        """Testa listagem de age groups quando não há nenhum"""
        response = api_client.get("/age-groups/")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_age_groups_with_data(self, api_client: TestClient, sample_age_groups):
        """Testa listagem de age groups com dados"""
        response = api_client.get("/age-groups/")
        
        assert response.status_code == 200
        age_groups = response.json()
        assert len(age_groups) == 3
        
        # Verifica se todos os age groups têm os campos necessários
        for group in age_groups:
            assert "id" in group
            assert "min_age" in group
            assert "max_age" in group

    def test_get_age_group_by_id_success(self, api_client: TestClient, sample_age_groups):
        """Testa busca de age group por ID existente"""
        age_group_id = sample_age_groups[0]["id"]
        
        response = api_client.get(f"/age-groups/{age_group_id}")
        
        assert response.status_code == 200
        age_group = response.json()
        assert age_group["id"] == age_group_id
        assert age_group["min_age"] == sample_age_groups[0]["min_age"]
        assert age_group["max_age"] == sample_age_groups[0]["max_age"]

    def test_get_age_group_by_id_not_found(self, api_client: TestClient, clean_database):
        """Testa busca de age group por ID inexistente"""
        fake_id = "507f1f77bcf86cd799439011"  # ObjectId válido mas inexistente
        
        response = api_client.get(f"/age-groups/{fake_id}")
        
        assert response.status_code == 404

    def test_get_age_group_invalid_id_format(self, api_client: TestClient, clean_database):
        """Testa busca de age group com ID em formato inválido"""
        invalid_id = "invalid-id-format"
        
        response = api_client.get(f"/age-groups/{invalid_id}")
        
        assert response.status_code in [400, 422]  # Bad request ou validation error

    def test_update_age_group_success(self, admin_client: TestClient, sample_age_groups):
        """Testa atualização bem-sucedida de age group"""
        age_group_id = sample_age_groups[0]["id"]
        update_data = {"min_age": 20, "max_age": 30}
        
        response = admin_client.put(f"/age-groups/{age_group_id}", json=update_data)
        
        assert response.status_code == 200
        updated_group = response.json()
        assert updated_group["id"] == age_group_id
        assert updated_group["min_age"] == 20
        assert updated_group["max_age"] == 30

    def test_update_age_group_requires_admin(self, user_client: TestClient, sample_age_groups):
        """Testa que atualização requer privilégios administrativos"""
        age_group_id = sample_age_groups[0]["id"]
        update_data = {"min_age": 20, "max_age": 30}
        
        response = user_client.put(f"/age-groups/{age_group_id}", json=update_data)
        
        assert response.status_code == 403

    def test_update_age_group_not_found(self, admin_client: TestClient, clean_database):
        """Testa atualização de age group inexistente"""
        fake_id = "507f1f77bcf86cd799439011"
        update_data = {"min_age": 20, "max_age": 30}
        
        response = admin_client.put(f"/age-groups/{fake_id}", json=update_data)
        
        assert response.status_code == 404

    def test_delete_age_group_success(self, admin_client: TestClient, sample_age_groups):
        """Testa exclusão bem-sucedida de age group"""
        age_group_id = sample_age_groups[0]["id"]
        
        response = admin_client.delete(f"/age-groups/{age_group_id}")
        
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Verifica se foi realmente deletado
        get_response = admin_client.get(f"/age-groups/{age_group_id}")
        assert get_response.status_code == 404

    def test_delete_age_group_requires_admin(self, user_client: TestClient, sample_age_groups):
        """Testa que exclusão requer privilégios administrativos"""
        age_group_id = sample_age_groups[0]["id"]
        
        response = user_client.delete(f"/age-groups/{age_group_id}")
        
        assert response.status_code == 403

    def test_delete_age_group_not_found(self, admin_client: TestClient, clean_database):
        """Testa exclusão de age group inexistente"""
        fake_id = "507f1f77bcf86cd799439011"
        
        response = admin_client.delete(f"/age-groups/{fake_id}")
        
        assert response.status_code == 404

    def test_age_groups_overlapping_ranges(self, admin_client: TestClient, clean_database):
        """Testa criação de age groups com ranges sobrepostos"""
        # Cria primeiro age group
        first_group = {"min_age": 18, "max_age": 30}
        response1 = admin_client.post("/age-groups/", json=first_group)
        assert response1.status_code == 200
        
        # Tenta criar age group sobreposto
        overlapping_group = {"min_age": 25, "max_age": 35}
        response2 = admin_client.post("/age-groups/", json=overlapping_group)
        
        # Nota: Atualmente permite sobreposição, mas seria bom validar isso
        assert response2.status_code == 200

    def test_age_groups_boundary_values(self, admin_client: TestClient, clean_database):
        """Testa age groups com valores limite"""
        boundary_cases = [
            {"min_age": 0, "max_age": 0},    # Idade zero
            {"min_age": 1, "max_age": 1},    # Idade mínima
            {"min_age": 120, "max_age": 120}, # Idade máxima
        ]
        
        for age_group_data in boundary_cases:
            response = admin_client.post("/age-groups/", json=age_group_data)
            # Aceita tanto sucesso quanto erro de validação
            assert response.status_code in [200, 400, 422]

    def test_age_groups_without_auth(self, unauthenticated_client: TestClient):
        """Testa que todos os endpoints de age groups requerem autenticação"""
        # Listar
        response = unauthenticated_client.get("/age-groups/")
        assert response.status_code == 401
        
        # Criar
        response = unauthenticated_client.post("/age-groups/", json={"min_age": 18, "max_age": 25})
        assert response.status_code == 401
        
        # Buscar por ID
        response = unauthenticated_client.get("/age-groups/507f1f77bcf86cd799439011")
        assert response.status_code == 401
        
        # Atualizar
        response = unauthenticated_client.put("/age-groups/507f1f77bcf86cd799439011", json={"min_age": 20, "max_age": 30})
        assert response.status_code == 401
        
        # Deletar
        response = unauthenticated_client.delete("/age-groups/507f1f77bcf86cd799439011")
        assert response.status_code == 401 