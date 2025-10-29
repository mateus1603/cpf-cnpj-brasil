"""Utilitários para validação de CPF (Cadastro de Pessoas Físicas)."""

import re
from typing import Union

# Type hint para CPF (pode ser str ou int)
CpfInput = Union[str, int]


class CPFValidator:
    """
    Classe utilitária para validar e formatar números de CPF.

    Esta classe não precisa ser instanciada, pois todos os métodos
    são estáticos.
    """

    # Sequências de pesos para cálculo dos dígitos verificadores (PEP 8: Constantes)
    _SEQUENCE1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    _SEQUENCE2 = [11] + _SEQUENCE1

    @staticmethod
    def _validate_input_format(cpf: CpfInput) -> str:
        """
        Valida o formato do CPF e retorna apenas os dígitos.

        Parâmetros:
            cpf (str | int): CPF a ser validado, com ou sem formatação.

        Retorna:
            str: Os 11 dígitos numéricos do CPF.

        Raises:
            ValueError: Se o CPF tiver formato inválido.
        """
        # Converter para string se for inteiro
        if isinstance(cpf, int):
            cpf_str = str(cpf).zfill(11)
        elif isinstance(cpf, str):
            cpf_str = cpf
        else:
            raise ValueError("Entrada do CPF deve ser string ou inteiro.")

        numeric_digits = re.sub(r'\D', '', cpf_str)

        if len(numeric_digits) != 11 or not numeric_digits.isdigit():
            raise ValueError(
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
        """
        if len(partial_cpf) == 9:
            sequence = CPFValidator._SEQUENCE1
        elif len(partial_cpf) == 10:
            sequence = CPFValidator._SEQUENCE2
        else:
            raise ValueError("CPF parcial deve ter 9 ou 10 dígitos.")

        # Calcular o dígito verificador
        total = sum(
            int(digit) * weight
            for digit, weight in zip(partial_cpf, sequence)
        )
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    @staticmethod
    def format_cpf(cpf: CpfInput) -> str:
        """
        Formata o CPF no padrão XXX.XXX.XXX-XX.

        Parâmetros:
            cpf (str | int): CPF sem formatação (11 dígitos) ou formatado.

        Retorna:
            str: CPF formatado.
        """
        # Validar formato do CPF e retornar formatado
        cpf_digits = CPFValidator._validate_input_format(cpf)
        return f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"

    @staticmethod
    def validate_cpf(cpf: CpfInput) -> bool:
        """
        Valida se um número de CPF é autêntico.

        Parâmetros:
            cpf (str | int): CPF a ser validado.

        Retorna:
            bool: True se válido, False caso contrário.
        """
        try:
            # Validar formato do CPF
            cpf_digits = CPFValidator._validate_input_format(cpf)
        except ValueError:
            return False

        # Verificar se todos os dígitos são iguais (ex: 111.111.111-11)
        if cpf_digits == cpf_digits[0] * len(cpf_digits):
            return False

        # Calcular primeiro dígito verificador
        digit1 = CPFValidator._calculate_digit(cpf_digits[:9])
        # Calcular segundo dígito verificador
        digit2 = CPFValidator._calculate_digit(cpf_digits[:9] + str(digit1))
        # Verificar se os dígitos calculados correspondem aos dígitos do CPF
        return cpf_digits[-2:] == f"{digit1}{digit2}"