import re

def validate_cpf_format(cpf_number: str) -> bool:
    """
    Valida apenas o formato do CPF (11 dígitos numéricos)
    Não verifica se o CPF existe realmente
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
    
    return True

def format_cpf(cpf_number: str) -> str:
    """
    Remove caracteres especiais do CPF, mantendo apenas números
    """
    return re.sub(r'[^0-9]', '', cpf_number) 