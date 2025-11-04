"""
Inicialização dos pacotes de validação de CPF e CNPJ.
"""
from .cpf_validator_gemini import CPF
from .cnpj_validator_gemini import CNPJ

__version__ = "0.1.0"
__all__ = ["CPF", "CNPJ"]
