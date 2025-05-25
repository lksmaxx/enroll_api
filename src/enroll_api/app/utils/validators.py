import re

def validate_cpf_format(cpf_number: str) -> bool:
    """
    Valida o formato e a matemática do CPF
    Inclui validação dos dígitos verificadores
    """
    # Remove caracteres especiais
    cpf_clean = format_cpf(cpf_number)
    
    # Verifica se tem exatamente 11 dígitos
    if len(cpf_clean) != 11:
        return False
    
    # Verifica se todos são dígitos
    if not cpf_clean.isdigit():
        return False
    
    # Verifica se não são todos os dígitos iguais (ex: 11111111111)
    if len(set(cpf_clean)) == 1:
        return False
    
    # Lista de CPFs inválidos conhecidos
    invalid_cpfs = [
        '00000000000', '11111111111', '22222222222', '33333333333',
        '44444444444', '55555555555', '66666666666', '77777777777',
        '88888888888', '99999999999', '12345678901', '01234567890'
    ]
    
    if cpf_clean in invalid_cpfs:
        return False
    
    # Validação matemática dos dígitos verificadores
    return _validate_cpf_digits(cpf_clean)

def _validate_cpf_digits(cpf: str) -> bool:
    """
    Valida os dígitos verificadores do CPF usando o algoritmo oficial
    """
    # Calcula o primeiro dígito verificador
    sum1 = 0
    for i in range(9):
        sum1 += int(cpf[i]) * (10 - i)
    
    remainder1 = sum1 % 11
    digit1 = 0 if remainder1 < 2 else 11 - remainder1
    
    if int(cpf[9]) != digit1:
        return False
    
    # Calcula o segundo dígito verificador
    sum2 = 0
    for i in range(10):
        sum2 += int(cpf[i]) * (11 - i)
    
    remainder2 = sum2 % 11
    digit2 = 0 if remainder2 < 2 else 11 - remainder2
    
    return int(cpf[10]) == digit2

def format_cpf(cpf_number: str) -> str:
    """
    Remove caracteres especiais do CPF, mantendo apenas números
    """
    if not cpf_number:
        return ""
    return re.sub(r'[^0-9]', '', cpf_number)

def validate_name(name: str) -> bool:
    """
    Valida se o nome é válido
    """
    if not name or not name.strip():
        return False
    
    # Nome deve ter pelo menos 2 caracteres
    if len(name.strip()) < 2:
        return False
    
    # Nome não pode conter apenas números
    if name.strip().isdigit():
        return False
    
    # Nome deve conter pelo menos uma letra
    if not re.search(r'[a-zA-ZÀ-ÿ]', name):
        return False
    
    return True

def validate_age(age: int) -> bool:
    """
    Valida se a idade é válida
    """
    return isinstance(age, int) and 0 < age <= 120

def validate_enrollment_data(name: str, age: int, cpf: str) -> list[str]:
    """
    Valida todos os dados de enrollment e retorna lista de erros
    """
    errors = []
    
    # Valida nome
    if not validate_name(name):
        errors.append("Nome deve ter pelo menos 2 caracteres e conter letras")
    
    # Valida idade
    if not validate_age(age):
        errors.append("Idade deve ser um número entre 1 e 120")
    
    # Valida CPF
    if not validate_cpf_format(cpf):
        errors.append("CPF inválido - verifique o formato e os dígitos verificadores")
    
    return errors 