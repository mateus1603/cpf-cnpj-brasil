"""
Módulo para exceções personalizadas da biblioteca cpf-cnpj-brasil.
"""

class CpfCnpjException(Exception):
    """Exceção base para todos os erros da biblioteca."""
    pass

class CNPJValidationError(CpfCnpjException):
    """Levantado para todos os erros de validação de CNPJ."""
    pass

class CNPJAPIError(CpfCnpjException):
    """Levantado para erros relacionados à API de consulta de CNPJ."""
    pass

class CPFValidationError(CpfCnpjException):
    """Levantado para todos os erros de validação de CPF."""
    pass
