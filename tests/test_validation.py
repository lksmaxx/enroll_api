import pytest
from tests.conftest import APITestClient, create_basic_auth_header


@pytest.mark.functional
class TestValidationRobusta:
    """Testes para validações robustas de dados"""

    def test_cpf_validation_mathematical(self, api_client: APITestClient, sample_age_groups):
        """Testa validação matemática de CPF"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # CPFs matematicamente inválidos
        invalid_cpfs = [
            "111.111.111-11",  # Todos os dígitos iguais
            "000.000.000-00",  # CPF zerado
            "123.456.789-00",  # Dígitos verificadores errados
            "123.456.789-99",  # Dígitos verificadores errados
            "12345678901",     # Sem formatação, mas inválido
            "abc.def.ghi-jk",  # Letras
            "123.456.789",     # Incompleto
            "",                # Vazio
        ]
        
        for cpf in invalid_cpfs:
            enrollment_data = {
                "name": "Pessoa Teste",
                "age": 25,
                "cpf": cpf
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            assert response.status_code == 422, f"CPF inválido deveria falhar: {cpf}"
            
            error_detail = response.json()["detail"]
            assert any("cpf" in str(error).lower() for error in error_detail), f"Erro deveria mencionar CPF: {cpf}"

    def test_cpf_validation_valid(self, api_client: APITestClient, sample_age_groups):
        """Testa CPFs matematicamente válidos"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # CPFs matematicamente válidos (gerados com algoritmo correto)
        valid_cpfs = [
            "11144477735",     # CPF válido
            "111.444.777-35",  # CPF válido com formatação
        ]
        
        for i, cpf in enumerate(valid_cpfs):
            enrollment_data = {
                "name": f"Pessoa Válida {i+1}",
                "age": 25,
                "cpf": cpf
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            assert response.status_code == 200, f"CPF válido deveria passar: {cpf}"

    def test_name_validation_robust(self, api_client: APITestClient, sample_age_groups):
        """Testa validação robusta de nomes"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Nomes inválidos
        invalid_names = [
            "",           # Vazio
            "   ",        # Apenas espaços
            "A",          # Muito curto
            "123",        # Apenas números
            "123456",     # Apenas números
            "!@#$%",      # Apenas símbolos
        ]
        
        for name in invalid_names:
            enrollment_data = {
                "name": name,
                "age": 25,
                "cpf": "11144477735"
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            assert response.status_code == 422, f"Nome inválido deveria falhar: '{name}'"

    def test_name_validation_valid(self, api_client: APITestClient, sample_age_groups):
        """Testa nomes válidos"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Nomes válidos
        valid_names = [
            "João Silva",
            "Maria José",
            "José da Silva",
            "Ana",
            "Pedro123",      # Nome com números é válido
            "José-Carlos",   # Nome com hífen é válido
            "Maria D'Angelo", # Nome com apóstrofe é válido
        ]
        
        for i, name in enumerate(valid_names):
            enrollment_data = {
                "name": name,
                "age": 25,
                "cpf": "11144477735"
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            assert response.status_code == 200, f"Nome válido deveria passar: '{name}'"

    def test_age_validation_boundaries(self, api_client: APITestClient, sample_age_groups):
        """Testa validação de idade nos limites"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Idades inválidas
        invalid_ages = [
            0,      # Zero
            -1,     # Negativa
            -10,    # Muito negativa
            121,    # Acima do limite
            1000,   # Muito alta
        ]
        
        for age in invalid_ages:
            enrollment_data = {
                "name": "Pessoa Teste",
                "age": age,
                "cpf": "11144477735"
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            assert response.status_code == 422, f"Idade inválida deveria falhar: {age}"

    def test_age_validation_valid(self, api_client: APITestClient, sample_age_groups):
        """Testa idades válidas"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Idades válidas
        valid_ages = [1, 18, 25, 50, 100, 120]
        
        for age in valid_ages:
            enrollment_data = {
                "name": f"Pessoa {age} anos",
                "age": age,
                "cpf": "11144477735"
            }
            
            response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
            # Pode falhar por não ter age group, mas não por validação
            assert response.status_code != 422, f"Idade válida não deveria falhar na validação: {age}"

    def test_age_group_validation_robust(self, api_client: APITestClient):
        """Testa validação robusta de age groups"""
        admin_auth = create_basic_auth_header("admin", "secret123")
        
        # Age groups inválidos
        invalid_age_groups = [
            {"min_age": 25, "max_age": 18},  # min > max
            {"min_age": 25, "max_age": 25},  # min == max
            {"min_age": -1, "max_age": 25},  # min negativo
            {"min_age": 18, "max_age": 121}, # max acima do limite
            {"min_age": 18, "max_age": -1},  # max negativo
        ]
        
        for age_group_data in invalid_age_groups:
            response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": admin_auth})
            assert response.status_code == 422, f"Age group inválido deveria falhar: {age_group_data}"

    def test_age_group_validation_valid(self, api_client: APITestClient, clean_database):
        """Testa age groups válidos"""
        admin_auth = create_basic_auth_header("admin", "secret123")
        
        # Age groups válidos
        valid_age_groups = [
            {"min_age": 18, "max_age": 25},
            {"min_age": 0, "max_age": 17},
            {"min_age": 26, "max_age": 120},
            {"min_age": 50, "max_age": 60},
        ]
        
        for age_group_data in valid_age_groups:
            response = api_client.client.post("/age-groups/", json=age_group_data, headers={"Authorization": admin_auth})
            assert response.status_code == 200, f"Age group válido deveria passar: {age_group_data}"

    def test_json_malformed_handling(self, api_client: APITestClient):
        """Testa tratamento de JSON malformado"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # JSON malformado
        malformed_json = '{"name": "João", "age": 25, "cpf": "11144477735"'  # Falta fechar chave
        
        response = api_client.client.post(
            "/enrollments/", 
            content=malformed_json,
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 422

    def test_missing_required_fields(self, api_client: APITestClient):
        """Testa campos obrigatórios faltando"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Dados com campos faltando
        incomplete_data_sets = [
            {"age": 25, "cpf": "11144477735"},  # name faltando
            {"name": "João", "cpf": "11144477735"},  # age faltando
            {"name": "João", "age": 25},  # cpf faltando
            {},  # Todos os campos faltando
        ]
        
        for incomplete_data in incomplete_data_sets:
            response = api_client.client.post("/enrollments/", json=incomplete_data, headers={"Authorization": auth_header})
            assert response.status_code == 422, f"Dados incompletos deveriam falhar: {incomplete_data}"

    def test_type_validation(self, api_client: APITestClient):
        """Testa validação de tipos de dados"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Dados com tipos incorretos que realmente falham
        wrong_type_data_sets = [
            {"name": 123, "age": 25, "cpf": "11144477735"},  # name como número
            {"name": "João", "age": "abc", "cpf": "11144477735"},  # age como string não numérica
            {"name": "João", "age": [], "cpf": "11144477735"},  # age como lista
            {"name": None, "age": 25, "cpf": "11144477735"},  # name como None
            {"name": "João", "age": 25, "cpf": 123},  # cpf como número
        ]
        
        for wrong_data in wrong_type_data_sets:
            response = api_client.client.post("/enrollments/", json=wrong_data, headers={"Authorization": auth_header})
            assert response.status_code == 422, f"Tipos incorretos deveriam falhar: {wrong_data}"

    def test_whitespace_handling(self, api_client: APITestClient, sample_age_groups):
        """Testa tratamento de espaços em branco"""
        auth_header = create_basic_auth_header("config", "config123")
        
        # Nome com espaços extras (deve ser aceito e limpo)
        enrollment_data = {
            "name": "  João Silva  ",  # Espaços extras
            "age": 25,
            "cpf": "11144477735"
        }
        
        response = api_client.client.post("/enrollments/", json=enrollment_data, headers={"Authorization": auth_header})
        assert response.status_code == 200
        
        # Verifica se o nome foi limpo (sem espaços extras)
        # Isso seria verificado se tivéssemos um endpoint para buscar o enrollment criado 