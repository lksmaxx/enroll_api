import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adiciona o path do src para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/enroll_api'))

from app.models.enrollment import EnrollmentCreate, EnrollmentStatus
from app.models.age_group import AgeGroup, AgeGroupCreate, AgeGroupUpdate


@pytest.mark.unit
class TestEnrollmentModels:
    """Testes unitários para os modelos de Enrollment"""

    def test_enrollment_create_valid_data(self):
        """Testa criação de EnrollmentCreate com dados válidos"""
        enrollment = EnrollmentCreate(
            name="João Silva",
            age=25,
            cpf="11144477735"  # CPF matematicamente válido
        )
        
        assert enrollment.name == "João Silva"
        assert enrollment.age == 25
        assert enrollment.cpf == "11144477735"  # CPF formatado (sem pontos/traços)

    def test_enrollment_create_invalid_age(self):
        """Testa criação de EnrollmentCreate com idade inválida"""
        with pytest.raises(ValueError):
            EnrollmentCreate(
                name="João Silva",
                age=0,  # Idade inválida
                cpf="11144477735"
            )
        
        with pytest.raises(ValueError):
            EnrollmentCreate(
                name="João Silva",
                age=150,  # Idade muito alta
                cpf="11144477735"
            )

    def test_enrollment_create_invalid_cpf(self):
        """Testa criação de EnrollmentCreate com CPF inválido"""
        with pytest.raises(ValueError, match="CPF inválido"):
            EnrollmentCreate(
                name="João Silva",
                age=25,
                cpf="111.111.111-11"  # CPF inválido (todos dígitos iguais)
            )

    def test_enrollment_status_model(self):
        """Testa modelo EnrollmentStatus"""
        status = EnrollmentStatus(
            id="123e4567-e89b-12d3-a456-426614174000",
            status="processed",
            message="Processado com sucesso",
            age_group_id="507f1f77bcf86cd799439011"
        )
        
        assert status.id == "123e4567-e89b-12d3-a456-426614174000"
        assert status.status == "processed"
        assert status.message == "Processado com sucesso"
        assert status.age_group_id == "507f1f77bcf86cd799439011"


@pytest.mark.unit
class TestAgeGroupModels:
    """Testes unitários para os modelos de Age Group"""

    def test_age_group_create_valid_data(self):
        """Testa criação de AgeGroupCreate com dados válidos"""
        age_group = AgeGroupCreate(min_age=18, max_age=25)
        
        assert age_group.min_age == 18
        assert age_group.max_age == 25

    def test_age_group_update_valid_data(self):
        """Testa criação de AgeGroupUpdate com dados válidos"""
        age_group = AgeGroupUpdate(min_age=20, max_age=30)
        
        assert age_group.min_age == 20
        assert age_group.max_age == 30

    def test_age_group_model(self):
        """Testa modelo AgeGroup completo"""
        age_group = AgeGroup(
            id="507f1f77bcf86cd799439011",
            min_age=18,
            max_age=25
        )
        
        assert age_group.id == "507f1f77bcf86cd799439011"
        assert age_group.min_age == 18
        assert age_group.max_age == 25


@pytest.mark.unit
class TestEnrollmentService:
    """Testes unitários para o serviço de Enrollment"""

    @patch('app.services.enrollment.mongo_db')
    @patch('app.services.enrollment.publish_message')
    def test_publish_enrollment_success(self, mock_publish, mock_db):
        """Testa publicação bem-sucedida de enrollment"""
        # Mock do age group encontrado
        mock_db.age_groups.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "min_age": 18,
            "max_age": 25
        }
        
        # Mock da inserção no banco
        mock_db.enrollments.insert_one.return_value = None
        
        # Importa e testa a função
        from app.services.enrollment import publish_enrollment
        
        enrollment_data = EnrollmentCreate(
            name="João Silva",
            age=25,
            cpf="11144477735"  # CPF matematicamente válido
        )
        
        enrollment_id = publish_enrollment(enrollment_data)
        
        # Verifica se foi chamado corretamente
        mock_db.age_groups.find_one.assert_called_once()
        mock_db.enrollments.insert_one.assert_called_once()
        mock_publish.assert_called_once()
        
        assert enrollment_id is not None

    @patch('app.services.enrollment.mongo_db')
    def test_publish_enrollment_no_age_group(self, mock_db):
        """Testa publicação de enrollment sem age group válido"""
        # Mock de nenhum age group encontrado
        mock_db.age_groups.find_one.return_value = None
        
        from app.services.enrollment import publish_enrollment
        from fastapi import HTTPException
        
        enrollment_data = EnrollmentCreate(
            name="João Silva",
            age=100,  # Idade fora de qualquer age group
            cpf="11144477735"  # CPF matematicamente válido
        )
        
        with pytest.raises(HTTPException) as exc_info:
            publish_enrollment(enrollment_data)
        
        assert exc_info.value.status_code == 400
        assert "idade" in exc_info.value.detail.lower()

    @patch('app.services.enrollment.mongo_db')
    def test_get_enrollment_status_found(self, mock_db):
        """Testa busca de status de enrollment existente"""
        # Mock do documento encontrado
        mock_db.enrollments.find_one.return_value = {
            "_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "processed",
            "message": "Processado com sucesso",
            "age_group_id": "507f1f77bcf86cd799439011"
        }
        
        from app.services.enrollment import get_enrollment_status
        
        result = get_enrollment_status("123e4567-e89b-12d3-a456-426614174000")
        
        assert result is not None
        assert result.id == "123e4567-e89b-12d3-a456-426614174000"
        assert result.status == "processed"
        assert result.message == "Processado com sucesso"
        assert result.age_group_id == "507f1f77bcf86cd799439011"

    @patch('app.services.enrollment.mongo_db')
    def test_get_enrollment_status_not_found(self, mock_db):
        """Testa busca de status de enrollment inexistente"""
        # Mock de nenhum documento encontrado
        mock_db.enrollments.find_one.return_value = None
        
        from app.services.enrollment import get_enrollment_status
        
        result = get_enrollment_status("00000000-0000-0000-0000-000000000000")
        
        assert result is None


@pytest.mark.unit
class TestValidators:
    """Testes unitários para os validadores"""
    
    def test_validate_cpf_format_valid(self):
        """Testa validação de CPF com formato válido"""
        from app.utils.validators import validate_cpf_format
        
        # Usando CPFs matematicamente válidos
        assert validate_cpf_format("11144477735") == True
        assert validate_cpf_format("111.444.777-35") == True
        assert validate_cpf_format("52998224725") == True

    def test_validate_cpf_format_invalid(self):
        """Testa validação de CPF com formato inválido"""
        from app.utils.validators import validate_cpf_format
        
        assert validate_cpf_format("111.111.111-11") == False  # Todos iguais
        assert validate_cpf_format("123.456.789") == False     # Muito curto
        assert validate_cpf_format("123.456.789-012") == False # Muito longo
        assert validate_cpf_format("abc.def.ghi-jk") == False  # Não numérico

    def test_format_cpf(self):
        """Testa formatação de CPF"""
        from app.utils.validators import format_cpf
        
        assert format_cpf("111.444.777-35") == "11144477735"
        assert format_cpf("111 444 777 35") == "11144477735"
        assert format_cpf("11144477735") == "11144477735" 