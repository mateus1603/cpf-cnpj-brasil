"""
Módulo para exceções personalizadas da biblioteca cpf-cnpj-brasil.
"""
from typing import Any, Optional


class CpfCnpjException(Exception):
    """Exceção base para todos os erros da biblioteca."""

    def __init__(self, message: str, value: Optional[Any] = None):
        """
        Inicializa a exceção com uma mensagem e um valor opcional.

        Parâmetros:
            message (str): A mensagem de erro descritiva.
            value (Any, opcional): O valor (ex: CPF/CNPJ) que causou o erro.
        """
        self.value = value
        full_message = f"{message} | Valor recebido: '{value}'" if value else message
        super().__init__(full_message)


class CNPJValidationError(CpfCnpjException):
    """Levantado para todos os erros de validação de CNPJ."""


class CNPJAPIError(CpfCnpjException):
    """Levantado para erros relacionados à API de consulta de CNPJ."""


class CPFValidationError(CpfCnpjException):
    """Levantado para todos os erros de validação de CPF."""
