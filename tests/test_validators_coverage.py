"""
Testes específicos para melhorar cobertura dos validadores
"""

import pytest
from app.utils.validators import (
    validate_cpf_format,
    format_cpf,
    validate_name,
    validate_age,
    validate_enrollment_data
)


class TestValidatorsCoverage:
    """Testes para melhorar cobertura dos validadores"""

    def test_validate_cpf_format_valid_cases(self):
        """Testa validação de CPF com casos válidos"""
        valid_cpfs = [
            "11144477735",
            "12345678909",
            "98765432100",
            "00000000191"
        ]
        
        for cpf in valid_cpfs:
            assert validate_cpf_format(cpf) is True, f"CPF {cpf} deveria ser válido"

    def test_validate_cpf_format_invalid_cases(self):
        """Testa validação de CPF com casos inválidos"""
        invalid_cpfs = [
            "111.111.111-11",  # Todos iguais
            "000.000.000-00",  # Todos zeros
            "123.456.789-00",  # Dígitos verificadores incorretos
            "111.444.777-36",  # Último dígito incorreto
            "111.444.777-34",  # Penúltimo dígito incorreto
            "12345678901",     # 11 dígitos mas inválido
            "1234567890",      # 10 dígitos
            "123456789012",    # 12 dígitos
            "",                # Vazio
            "abc.def.ghi-jk",  # Letras
            "111.111.111-1a",  # Letra no final
        ]
        
        for cpf in invalid_cpfs:
            assert validate_cpf_format(cpf) is False, f"CPF {cpf} deveria ser inválido"

    def test_validate_cpf_format_edge_cases(self):
        """Testa casos extremos de validação de CPF"""
        # CPF None
        assert validate_cpf_format(None) is False
        
        # CPF com espaços
        assert validate_cpf_format("  11144477735  ") is True
        
        # CPF com caracteres especiais misturados - format_cpf remove caracteres especiais
        assert validate_cpf_format("111@444#777$35") is True  # Vira "11144477735" que é válido

    def test_format_cpf_various_formats(self):
        """Testa formatação de CPF com vários formatos de entrada"""
        test_cases = [
            ("111.444.777-35", "11144477735"),
            ("111 444 777 35", "11144477735"),
            ("111-444-777-35", "11144477735"),
            ("  111.444.777-35  ", "11144477735"),
            ("11144477735", "11144477735"),
            ("", ""),
            ("abc", ""),  # Não numérico, remove tudo
        ]
        
        for input_cpf, expected in test_cases:
            result = format_cpf(input_cpf)
            assert result == expected, f"format_cpf('{input_cpf}') deveria retornar '{expected}', mas retornou '{result}'"

    def test_format_cpf_edge_cases(self):
        """Testa casos extremos de formatação de CPF"""
        # CPF None
        assert format_cpf(None) == ""
        
        # CPF com muitos caracteres especiais
        assert format_cpf("1!1@1#4$4%4^7&7*7(3)5") == "11144477735"

    def test_validate_name_valid_cases(self):
        """Testa validação de nome com casos válidos"""
        valid_names = [
            "João Silva",
            "Maria",
            "José da Silva Santos",
            "Ana-Paula",
            "João D'Angelo",
            "Maria José",
            "Carlos Eduardo",
            "A B",  # Mínimo 2 caracteres
        ]
        
        for name in valid_names:
            assert validate_name(name) is True, f"Nome '{name}' deveria ser válido"

    def test_validate_name_invalid_cases(self):
        """Testa validação de nome com casos inválidos"""
        invalid_names = [
            "",           # Vazio
            " ",          # Apenas espaço
            "A",          # Muito curto
            "123456",     # Apenas números
            "@#$%",       # Apenas símbolos
            "   ",        # Apenas espaços
        ]
        
        for name in invalid_names:
            assert validate_name(name) is False, f"Nome '{name}' deveria ser inválido"

    def test_validate_name_edge_cases(self):
        """Testa casos extremos de validação de nome"""
        # Nome None
        assert validate_name(None) is False
        
        # Nome com espaços extras
        assert validate_name("  João Silva  ") is True
        
        # Nome muito longo mas válido
        long_name = "A" * 100 + " B"
        assert validate_name(long_name) is True

    def test_validate_age_valid_cases(self):
        """Testa validação de idade com casos válidos"""
        valid_ages = [1, 18, 25, 65, 100, 120]
        
        for age in valid_ages:
            assert validate_age(age) is True, f"Idade {age} deveria ser válida"

    def test_validate_age_invalid_cases(self):
        """Testa validação de idade com casos inválidos"""
        invalid_ages = [0, -1, -10, 121, 150, 200]
        
        for age in invalid_ages:
            assert validate_age(age) is False, f"Idade {age} deveria ser inválida"

    def test_validate_age_edge_cases(self):
        """Testa casos extremos de validação de idade"""
        # Idade None
        assert validate_age(None) is False
        
        # Idade como string
        assert validate_age("25") is False
        
        # Idade como float
        assert validate_age(25.5) is False

    def test_validate_enrollment_data_valid_cases(self):
        """Testa validação de dados de enrollment com casos válidos"""
        valid_data = [
            ("João Silva", 25, "11144477735"),
            ("Maria Santos", 30, "12345678909"),
            ("José da Silva", 18, "98765432100"),
        ]
        
        for name, age, cpf in valid_data:
            errors = validate_enrollment_data(name, age, cpf)
            assert errors == [], f"Dados válidos não deveriam ter erros: {errors}"

    def test_validate_enrollment_data_invalid_cases(self):
        """Testa validação de dados de enrollment com casos inválidos"""
        invalid_data = [
            ("", 25, "11144477735"),           # Nome vazio
            ("João", 0, "11144477735"),        # Idade inválida
            ("João", 25, "111.111.111-11"),   # CPF inválido
            ("", 0, ""),                       # Tudo inválido
            ("A", -1, "invalid_cpf"),         # Múltiplos erros
        ]
        
        for name, age, cpf in invalid_data:
            errors = validate_enrollment_data(name, age, cpf)
            assert len(errors) > 0, f"Dados inválidos deveriam ter erros: nome='{name}', age={age}, cpf='{cpf}'"

    def test_validate_enrollment_data_specific_errors(self):
        """Testa mensagens específicas de erro na validação de enrollment"""
        # Teste nome inválido
        errors = validate_enrollment_data("", 25, "11144477735")
        assert any("nome" in error.lower() for error in errors)
        
        # Teste idade inválida
        errors = validate_enrollment_data("João", 0, "11144477735")
        assert any("idade" in error.lower() for error in errors)
        
        # Teste CPF inválido
        errors = validate_enrollment_data("João", 25, "invalid")
        assert any("cpf" in error.lower() for error in errors)

    def test_validate_enrollment_data_edge_cases(self):
        """Testa casos extremos de validação de enrollment"""
        # Dados None
        errors = validate_enrollment_data(None, None, None)
        assert len(errors) >= 3  # Deve ter pelo menos 3 erros
        
        # Dados com espaços
        errors = validate_enrollment_data("  João Silva  ", 25, "  11144477735  ")
        assert errors == []  # Deve ser válido após trim

    def test_cpf_validation_mathematical_algorithm(self):
        """Testa especificamente o algoritmo matemático de validação de CPF"""
        # CPFs com primeiro dígito verificador correto, segundo incorreto
        cpf_first_digit_ok = "11144477734"  # Último dígito deveria ser 5
        assert validate_cpf_format(cpf_first_digit_ok) is False
        
        # CPFs com primeiro dígito verificador incorreto
        cpf_first_digit_wrong = "11144477745"  # Penúltimo dígito deveria ser 3
        assert validate_cpf_format(cpf_first_digit_wrong) is False
        
        # CPF com ambos dígitos verificadores corretos
        cpf_both_correct = "11144477735"
        assert validate_cpf_format(cpf_both_correct) is True

    def test_cpf_special_invalid_sequences(self):
        """Testa sequências especiais de CPF que são inválidas"""
        invalid_sequences = [
            "11111111111",
            "22222222222",
            "33333333333",
            "44444444444",
            "55555555555",
            "66666666666",
            "77777777777",
            "88888888888",
            "99999999999",
            "00000000000"
        ]
        
        for cpf in invalid_sequences:
            assert validate_cpf_format(cpf) is False, f"CPF com sequência {cpf} deveria ser inválido"

    def test_name_validation_character_types(self):
        """Testa validação de nome com diferentes tipos de caracteres"""
        # Nomes com acentos (válidos)
        accented_names = ["José", "María", "João", "Ângela", "Ção"]
        for name in accented_names:
            assert validate_name(name) is True, f"Nome com acentos '{name}' deveria ser válido"
        
        # Nomes com símbolos especiais (alguns válidos, outros não)
        assert validate_name("Ana-Paula") is True  # Hífen válido
        assert validate_name("João D'Angelo") is True  # Apóstrofe válido
        assert validate_name("Maria@Silva") is True  # @ válido se tem letras
        assert validate_name("João#Silva") is True  # # válido se tem letras
        
        # Nomes que são apenas números (inválidos)
        assert validate_name("123456") is False  # Apenas números
        
        # Nomes que não têm letras (inválidos)
        assert validate_name("@#$%") is False  # Apenas símbolos

    def test_integration_all_validators(self):
        """Testa integração de todos os validadores juntos"""
        # Caso completamente válido
        name = "João Silva"
        age = 25
        cpf = "111.444.777-35"
        
        # Testa cada validador individualmente
        assert validate_name(name) is True
        assert validate_age(age) is True
        formatted_cpf = format_cpf(cpf)
        assert validate_cpf_format(formatted_cpf) is True
        
        # Testa validação completa
        errors = validate_enrollment_data(name, age, cpf)
        assert errors == [] 