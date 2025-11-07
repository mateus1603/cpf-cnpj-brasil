"""Utilitários para validação de CPF (Cadastro de Pessoas Físicas)."""

import re
import logging
from typing import Union, Literal

from .exceptions import CPFValidationError

# Configurar logging
logger = logging.getLogger(__name__)

# Type hints
CpfInput = Union[str, int]
ValidationResult = Union[str, Literal[False]]


class CPF:
    """
    Classe utilitária para validar e formatar números de CPF.

    Esta classe não precisa ser instanciada, pois todos os métodos
    são estáticos.
    """

    # Sequências de pesos para cálculo dos dígitos verificadores (PEP 8: Constantes)
    _SEQUENCE1 = list(range(10, 1, -1)) # de 10 a 2
    _SEQUENCE2 = list(range(11, 1, -1)) # de 11 a 2

    @staticmethod
    def _validate_input_format(cpf: CpfInput) -> str:
        """
        Valida o formato do CPF e retorna apenas os dígitos.

        Parâmetros:
            cpf (str | int): CPF a ser validado, com ou sem formatação.

        Retorna:
            str: Os 11 dígitos numéricos do CPF.

        Raises:
            CPFValidationError: Se o CPF tiver formato inválido.
        """
        # Converter para string se for inteiro
        if isinstance(cpf, int):
            cpf_str = str(cpf).zfill(11)
        elif isinstance(cpf, str):
            cpf_str = cpf
        else:
            raise CPFValidationError("Entrada do CPF deve ser string ou inteiro.")

        numeric_digits = re.sub(r'\D', '', cpf_str)

        if len(numeric_digits) != 11 or not numeric_digits.isdigit():
            raise CPFValidationError(
                "CPF com formato inválido. Deve conter exatamente 11 "
                "dígitos numéricos."
            )
        return numeric_digits

    @staticmethod
    def _calculate_digit(partial_cpf: str) -> int:
        """
        Calcula um dígito verificador com base nos dígitos parciais.

        Parâmetros:
            partial_cpf (str): Parte do CPF (9 ou 10 dígitos).

        Retorna:
            int: Dígito verificador calculado.
        
        Raises:
            CPFValidationError: Se o CPF parcial for inválido.
        """
        if len(partial_cpf) == 9:
            sequence = CPF._SEQUENCE1
        elif len(partial_cpf) == 10:
            sequence = CPF._SEQUENCE2
        else:
            raise CPFValidationError("CPF parcial deve ter 9 ou 10 dígitos.")

        # Calcular o dígito verificador
        total = sum(
            int(digit) * weight
            for digit, weight in zip(partial_cpf, sequence)
        )
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    @staticmethod
    def format(cpf: CpfInput) -> str:
        """
        Formata o CPF no padrão XXX.XXX.XXX-XX.

        Parâmetros:
            cpf (str | int): CPF sem formatação (11 dígitos) ou formatado.

        Retorna:
            str: CPF formatado.
        """
        # Validar formato do CPF e retornar formatado
        cpf_digits = CPF._validate_input_format(cpf)
        return f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"

    @staticmethod
    def validate(cpf: CpfInput) -> ValidationResult:
        """
        Valida se um número de CPF é autêntico.

        Parâmetros:
            cpf (str | int): CPF a ser validado.

        Retorna:
            str: O CPF limpo (11 caracteres) se válido.
            False: Caso contrário.
        """

        # Validar formato do CPF
        try:
            cpf_digits = CPF._validate_input_format(cpf)
        except CPFValidationError:
            logger.debug("CPF rejeitado: formato inválido.")
            return False

        # Verificar se todos os dígitos são iguais (ex: 111.111.111-11)
        if cpf_digits == cpf_digits[0] * len(cpf_digits):
            logger.debug(
                "CPF rejeitado: todos os dígitos iguais (%s)",
                cpf_digits[0]
            )
            return False

        # Calcular primeiro dígito verificador
        digit1 = CPF._calculate_digit(cpf_digits[:9])
        # Calcular segundo dígito verificador
        digit2 = CPF._calculate_digit(cpf_digits[:9] + str(digit1))
        
        # Verificar se os dígitos calculados correspondem aos dígitos do CPF
        is_valid = cpf_digits[-2:] == f"{digit1}{digit2}"

        if is_valid:
            logger.debug("CPF validado com sucesso: %s", cpf_digits)
            return cpf_digits

        logger.debug(
            "CPF %s inválido: esperado %s%s, encontrado %s",
            cpf_digits, digit1, digit2, cpf_digits[-2:]
        )
        return False