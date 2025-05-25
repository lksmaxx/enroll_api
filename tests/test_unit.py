import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adiciona o path do src para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/enroll_api'))

from app.models.enrollment import EnrollmentCreate, EnrollmentStatus
from app.models.age_group import AgeGroup, AgeGroupCreate, AgeGroupUpdate


class TestEnrollmentModels:
    """Testes unitários para os modelos de Enrollment"""

    def test_enrollment_create_valid_data(self):
        """Testa criação de EnrollmentCreate com dados válidos"""
        with patch('app.utils.validators.validate_cpf_format', return_value=True):
            with patch('app.utils.validators.format_cpf', return_value="123.456.789-01"):
                enrollment = EnrollmentCreate(
                    name="João Silva",
                    age=25,
                    cpf="12345678901"
                )
                
                assert enrollment.name == "João Silva"
                assert enrollment.age == 25
                assert enrollment.cpf == "123.456.789-01"

    def test_enrollment_create_invalid_age(self):
        """Testa criação de EnrollmentCreate com idade inválida"""
        with pytest.raises(ValueError):
            EnrollmentCreate(
                name="João Silva",
                age=0,  # Idade inválida
                cpf="123.456.789-01"
            )
        
        with pytest.raises(ValueError):
            EnrollmentCreate(
                name="João Silva",
                age=150,  # Idade muito alta
                cpf="123.456.789-01"
            )

    def test_enrollment_create_invalid_cpf(self):
        """Testa criação de EnrollmentCreate com CPF inválido"""
        with patch('app.utils.validators.validate_cpf_format', return_value=False):
            with patch('app.utils.validators.format_cpf', return_value="111.111.111-11"):
                with pytest.raises(ValueError, match="CPF com formato inválido"):
                    EnrollmentCreate(
                        name="João Silva",
                        age=25,
                        cpf="111.111.111-11"
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
        
        with patch('app.utils.validators.validate_cpf_format', return_value=True):
            with patch('app.utils.validators.format_cpf', return_value="123.456.789-01"):
                enrollment_data = EnrollmentCreate(
                    name="João Silva",
                    age=25,
                    cpf="12345678901"
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
        
        with patch('app.utils.validators.validate_cpf_format', return_value=True):
            with patch('app.utils.validators.format_cpf', return_value="123.456.789-01"):
                enrollment_data = EnrollmentCreate(
                    name="João Silva",
                    age=100,  # Idade fora de qualquer age group
                    cpf="12345678901"
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


class TestAgeGroupService:
    """Testes unitários para o serviço de Age Group"""

    @patch('app.services.age_groups.mongo_db')
    async def test_create_age_group_success(self, mock_db):
        """Testa criação bem-sucedida de age group"""
        # Mock da inserção e busca
        mock_db.age_groups.insert_one.return_value = Mock(inserted_id="507f1f77bcf86cd799439011")
        mock_db.age_groups.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "min_age": 18,
            "max_age": 25
        }
        
        from app.services.age_groups import create_age_group
        
        age_group_data = AgeGroupCreate(min_age=18, max_age=25)
        result = await create_age_group(age_group_data)
        
        assert result["id"] == "507f1f77bcf86cd799439011"
        assert result["min_age"] == 18
        assert result["max_age"] == 25

    @patch('app.services.age_groups.mongo_db')
    async def test_get_age_group_found(self, mock_db):
        """Testa busca de age group existente"""
        # Mock do documento encontrado
        mock_db.age_groups.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "min_age": 18,
            "max_age": 25
        }
        
        from app.services.age_groups import get_age_group
        
        result = await get_age_group("507f1f77bcf86cd799439011")
        
        assert result is not None
        assert result["id"] == "507f1f77bcf86cd799439011"
        assert result["min_age"] == 18
        assert result["max_age"] == 25

    @patch('app.services.age_groups.mongo_db')
    async def test_get_age_group_not_found(self, mock_db):
        """Testa busca de age group inexistente"""
        # Mock de nenhum documento encontrado
        mock_db.age_groups.find_one.return_value = None
        
        from app.services.age_groups import get_age_group
        
        result = await get_age_group("507f1f77bcf86cd799439011")
        
        assert result is None

    @patch('app.services.age_groups.mongo_db')
    async def test_get_all_age_groups(self, mock_db):
        """Testa listagem de todos os age groups"""
        # Mock da busca
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter([
            {"_id": "507f1f77bcf86cd799439011", "min_age": 18, "max_age": 25},
            {"_id": "507f1f77bcf86cd799439012", "min_age": 26, "max_age": 35}
        ]))
        mock_db.age_groups.find.return_value = mock_cursor
        
        from app.services.age_groups import get_all_age_groups
        
        result = await get_all_age_groups()
        
        assert len(result) == 2
        assert result[0]["id"] == "507f1f77bcf86cd799439011"
        assert result[1]["id"] == "507f1f77bcf86cd799439012"

    @patch('app.services.age_groups.mongo_db')
    async def test_update_age_group_success(self, mock_db):
        """Testa atualização bem-sucedida de age group"""
        # Mock da atualização e busca
        mock_db.age_groups.update_one.return_value = Mock(modified_count=1)
        mock_db.age_groups.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "min_age": 20,
            "max_age": 30
        }
        
        from app.services.age_groups import update_age_group
        
        update_data = AgeGroupUpdate(min_age=20, max_age=30)
        result = await update_age_group("507f1f77bcf86cd799439011", update_data)
        
        assert result is not None
        assert result["id"] == "507f1f77bcf86cd799439011"
        assert result["min_age"] == 20
        assert result["max_age"] == 30

    @patch('app.services.age_groups.mongo_db')
    async def test_update_age_group_not_found(self, mock_db):
        """Testa atualização de age group inexistente"""
        # Mock de nenhuma modificação
        mock_db.age_groups.update_one.return_value = Mock(modified_count=0)
        
        from app.services.age_groups import update_age_group
        
        update_data = AgeGroupUpdate(min_age=20, max_age=30)
        result = await update_age_group("507f1f77bcf86cd799439011", update_data)
        
        assert result is None

    @patch('app.services.age_groups.mongo_db')
    async def test_delete_age_group_success(self, mock_db):
        """Testa exclusão bem-sucedida de age group"""
        # Mock da exclusão
        mock_db.age_groups.delete_one.return_value = Mock(deleted_count=1)
        
        from app.services.age_groups import delete_age_group
        
        result = await delete_age_group("507f1f77bcf86cd799439011")
        
        assert result == 1

    @patch('app.services.age_groups.mongo_db')
    async def test_delete_age_group_not_found(self, mock_db):
        """Testa exclusão de age group inexistente"""
        # Mock de nenhuma exclusão
        mock_db.age_groups.delete_one.return_value = Mock(deleted_count=0)
        
        from app.services.age_groups import delete_age_group
        
        result = await delete_age_group("507f1f77bcf86cd799439011")
        
        assert result == 0 