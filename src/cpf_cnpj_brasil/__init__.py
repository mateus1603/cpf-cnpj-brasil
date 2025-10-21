"""
Inicialização dos pacotes de validação de CPF e CNPJ.
"""
from .cpf_validator import CPFValidator
from .cnpj_validator import CNPJValidator

__version__ = "0.1.0"
__all__ = ["CPFValidator", "CNPJValidator"]
