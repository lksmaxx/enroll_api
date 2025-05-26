"""
Testes específicos para melhorar cobertura dos modelos Pydantic
"""

import pytest
from pydantic import ValidationError
from app.models.age_group import AgeGroup, AgeGroupCreate, AgeGroupUpdate
from app.models.enrollment import EnrollmentCreate, EnrollmentStatus


class TestAgeGroupModelsCoverage:
    """Testes para melhorar cobertura dos modelos AgeGroup"""

    def test_age_group_create_validation_error_min_greater_than_max(self):
        """Testa erro quando min_age > max_age"""
        with pytest.raises(ValidationError) as exc_info:
            AgeGroupCreate(min_age=30, max_age=20)
        
        errors = exc_info.value.errors()
        assert any("Idade mínima não pode ser maior que a idade máxima" in str(error) for error in errors)

    def test_age_group_create_validation_error_negative_ages(self):
        """Testa erro com idades negativas"""
        with pytest.raises(ValidationError) as exc_info:
            AgeGroupCreate(min_age=-5, max_age=10)
        
        errors = exc_info.value.errors()
        assert any("greater_than_equal" in str(error) for error in errors)

    def test_age_group_create_validation_error_max_age_too_high(self):
        """Testa erro com max_age muito alto"""
        with pytest.raises(ValidationError) as exc_info:
            AgeGroupCreate(min_age=18, max_age=200)
        
        errors = exc_info.value.errors()
        assert any("less_than_equal" in str(error) for error in errors)

    def test_age_group_create_validation_error_equal_ages(self):
        """Testa erro quando min_age == max_age"""
        with pytest.raises(ValidationError) as exc_info:
            AgeGroupCreate(min_age=25, max_age=25)
        
        errors = exc_info.value.errors()
        assert any("Idade mínima e máxima não podem ser iguais" in str(error) for error in errors)

    def test_age_group_update_validation_error(self):
        """Testa erro de validação no AgeGroupUpdate"""
        with pytest.raises(ValidationError) as exc_info:
            AgeGroupUpdate(min_age=40, max_age=30)
        
        errors = exc_info.value.errors()
        assert any("Idade mínima não pode ser maior que a idade máxima" in str(error) for error in errors)

    def test_age_group_model_with_id(self):
        """Testa modelo AgeGroup com ID"""
        age_group = AgeGroup(
            id="507f1f77bcf86cd799439011",
            min_age=18,
            max_age=25
        )
        assert age_group.id == "507f1f77bcf86cd799439011"
        assert age_group.min_age == 18
        assert age_group.max_age == 25

    def test_age_group_create_boundary_values(self):
        """Testa valores de fronteira para AgeGroupCreate"""
        # Valores válidos na fronteira
        age_group = AgeGroupCreate(min_age=0, max_age=120)
        assert age_group.min_age == 0
        assert age_group.max_age == 120

        # Valores válidos diferentes
        age_group = AgeGroupCreate(min_age=18, max_age=25)
        assert age_group.min_age == 18
        assert age_group.max_age == 25

    def test_age_group_update_valid_data(self):
        """Testa AgeGroupUpdate com dados válidos"""
        update = AgeGroupUpdate(min_age=20, max_age=30)
        assert update.min_age == 20
        assert update.max_age == 30


class TestEnrollmentModelsCoverage:
    """Testes para melhorar cobertura dos modelos Enrollment"""

    def test_enrollment_create_cpf_validation_invalid_format(self):
        """Testa validação de CPF com formato inválido"""
        with pytest.raises(ValidationError) as exc_info:
            EnrollmentCreate(
                name="João Silva",
                age=25,
                cpf="123.456.789"  # Formato incompleto
            )
        
        errors = exc_info.value.errors()
        assert any("CPF inválido" in str(error) for error in errors)

    def test_enrollment_create_cpf_validation_invalid_characters(self):
        """Testa validação de CPF com caracteres inválidos"""
        with pytest.raises(ValidationError) as exc_info:
            EnrollmentCreate(
                name="João Silva",
                age=25,
                cpf="123.456.789-AB"  # Letras no final
            )
        
        errors = exc_info.value.errors()
        assert any("CPF inválido" in str(error) for error in errors)

    def test_enrollment_create_cpf_validation_mathematical_invalid(self):
        """Testa validação matemática de CPF inválido"""
        with pytest.raises(ValidationError) as exc_info:
            EnrollmentCreate(
                name="João Silva",
                age=25,
                cpf="111.111.111-11"  # CPF matematicamente inválido
            )
        
        errors = exc_info.value.errors()
        assert any("CPF inválido" in str(error) for error in errors)

    def test_enrollment_create_name_validation_empty(self):
        """Testa validação de nome vazio"""
        with pytest.raises(ValidationError) as exc_info:
            EnrollmentCreate(
                name="",
                age=25,
                cpf="11144477735"
            )
        
        errors = exc_info.value.errors()
        # Pode ser qualquer uma dessas mensagens dependendo da validação
        assert any(msg in str(error) for error in errors for msg in ["Nome é obrigatório", "ensure this value has at least 1 characters"])

    def test_enrollment_create_name_validation_too_short(self):
        """Testa validação de nome muito curto"""
        with pytest.raises(ValidationError) as exc_info:
            EnrollmentCreate(
                name="A",  # Apenas 1 caractere
                age=25,
                cpf="11144477735"
            )
        
        errors = exc_info.value.errors()
        assert any("Nome deve ter pelo menos 2 caracteres" in str(error) for error in errors)

    def test_enrollment_create_age_validation_zero(self):
        """Testa validação de idade zero"""
        with pytest.raises(ValidationError) as exc_info:
            EnrollmentCreate(
                name="João Silva",
                age=0,
                cpf="11144477735"
            )
        
        errors = exc_info.value.errors()
        assert any("greater_than" in str(error) for error in errors)

    def test_enrollment_create_age_validation_too_high(self):
        """Testa validação de idade muito alta"""
        with pytest.raises(ValidationError) as exc_info:
            EnrollmentCreate(
                name="João Silva",
                age=200,
                cpf="11144477735"
            )
        
        errors = exc_info.value.errors()
        assert any("less_than_equal" in str(error) for error in errors)

    def test_enrollment_status_model_complete(self):
        """Testa modelo EnrollmentStatus completo"""
        status = EnrollmentStatus(
            id="test-id",
            status="processed",
            message="Processamento concluído com sucesso",
            age_group_id="age-group-123"
        )
        assert status.id == "test-id"
        assert status.status == "processed"
        assert status.message == "Processamento concluído com sucesso"
        assert status.age_group_id == "age-group-123"

    def test_enrollment_status_model_minimal(self):
        """Testa modelo EnrollmentStatus com campos opcionais"""
        status = EnrollmentStatus(
            id="test-id",
            status="pending"
        )
        assert status.id == "test-id"
        assert status.status == "pending"
        assert status.message is None
        assert status.age_group_id is None

    def test_enrollment_create_cpf_formats_accepted(self):
        """Testa diferentes formatos de CPF aceitos"""
        # CPF com pontos e hífen (será formatado)
        enrollment1 = EnrollmentCreate(
            name="João Silva",
            age=25,
            cpf="111.444.777-35"
        )
        assert enrollment1.cpf == "11144477735"  # Formatado sem pontos/hífen

        # CPF apenas números
        enrollment2 = EnrollmentCreate(
            name="Maria Santos",
            age=30,
            cpf="11144477735"
        )
        assert enrollment2.cpf == "11144477735"

    def test_enrollment_create_name_whitespace_handling(self):
        """Testa tratamento de espaços no nome"""
        # Nome com espaços extras (será feito strip)
        enrollment = EnrollmentCreate(
            name="  João Silva  ",
            age=25,
            cpf="11144477735"
        )
        assert enrollment.name == "João Silva"

    def test_enrollment_create_boundary_ages(self):
        """Testa idades nos limites"""
        # Idade mínima válida
        enrollment1 = EnrollmentCreate(
            name="Criança",
            age=1,
            cpf="11144477735"
        )
        assert enrollment1.age == 1

        # Idade máxima
        enrollment2 = EnrollmentCreate(
            name="Idoso",
            age=120,
            cpf="11144477735"
        )
        assert enrollment2.age == 120

    def test_enrollment_status_different_statuses(self):
        """Testa diferentes valores de status"""
        statuses = ["pending", "processing", "processed", "failed", "cancelled"]
        
        for status_value in statuses:
            status = EnrollmentStatus(
                id=f"test-{status_value}",
                status=status_value
            )
            assert status.status == status_value

    def test_enrollment_create_valid_cpf_examples(self):
        """Testa com CPFs válidos conhecidos"""
        valid_cpfs = [
            "11144477735",
            "12345678909",
            "98765432100"
        ]
        
        for cpf in valid_cpfs:
            enrollment = EnrollmentCreate(
                name="Teste CPF",
                age=25,
                cpf=cpf
            )
            assert enrollment.cpf == cpf

    def test_enrollment_create_name_validation_only_numbers(self):
        """Testa validação de nome apenas com números"""
        with pytest.raises(ValidationError) as exc_info:
            EnrollmentCreate(
                name="123456",
                age=25,
                cpf="11144477735"
            )
        
        errors = exc_info.value.errors()
        assert any("Nome deve ter pelo menos 2 caracteres e conter letras" in str(error) for error in errors) 