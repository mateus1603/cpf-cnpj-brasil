"""
Classe para validação de CPF (Cadastro de Pessoas Físicas).
"""
import re


class CPFValidator:
    """
    Classe para validação de CPF.
    """

    def __init__(self):
        self.sequence1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        self.sequence2 = [11] + self.sequence1

    @staticmethod
    def _validate_input_format(cpf):
        """
        Valida o formato do CPF de entrada.

        Parâmetros:
            cpf (str ou int): CPF a ser validado.

        Retorna:
            bool: True se válido, False caso contrário.

        Raises:
            ValueError: Se o CPF tiver formato inválido.
        """

        # Converter para string se for inteiro
        if isinstance(cpf, int):
            cpf = str(cpf).zfill(11)

        # Extrair dígitos numéricos
        numeric_digits = re.sub(r'\D', '', cpf)

        # Verificar se tem 11 dígitos, todos numéricos e é string
        if not isinstance(numeric_digits, str) or len(numeric_digits) != 11 or not numeric_digits.isdigit():
            raise ValueError(
                "CPF com formato inválido. Deve ser uma string de 11 dígitos numéricos ou um inteiro.")
        return numeric_digits

    def _calculate_digit(self, partial_cpf):
        """
        Calcular o dígito verificador do CPF.

        Parâmetros:
            partial_cpf (str): Parte do CPF (9 ou 10 dígitos).

        Retorna:
            int: Dígito verificador calculado.

        Raises:
            ValueError: Se as entradas forem incompatíveis.
        """

        # Definir sequência de pesos com base no comprimento do partial_cpf
        if len(partial_cpf) == 9:
            sequence = self.sequence1
        elif len(partial_cpf) == 10:
            sequence = self.sequence2
        else:
            raise ValueError("CPF parcial deve ter 9 ou 10 dígitos.")

        # Calcular o dígito verificador
        total = sum(int(digit) * weight for digit,
                   weight in zip(partial_cpf, sequence))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    @staticmethod
    def format_cpf(cpf):
        """
        Formata o CPF no padrão XXX.XXX.XXX-XX

        Parâmetros:
            cpf (str): CPF sem formatação (11 dígitos).

        Retorna:
            str: CPF formatado.
        """

        # Validar formato do CPF e retornar formatado
        cpf = CPFValidator._validate_input_format(cpf)
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    def validate_cpf(self, cpf):
        """
        Valida o CPF.

        Parâmetros:
            cpf (str ou int): CPF a ser validado.

        Retorna:
            bool: True se válido, False caso contrário.
        """

        # Validar formato do CPF
        cpf = self._validate_input_format(cpf)

        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * len(cpf):
            return False  # CPF com todos os dígitos iguais é inválido

        # Calcular primeiro dígito verificador
        digit1 = self._calculate_digit(cpf[:9])

        # Calcular segundo dígito verificador
        digit2 = self._calculate_digit(cpf[:9] + str(digit1))

        # Verificar se os dígitos calculados correspondem aos dígitos do CPF
        return cpf[-2:] == f"{digit1}{digit2}"
