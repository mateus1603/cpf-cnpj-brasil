"""
Classe para validação de CPF (Cadastro de Pessoas Físicas).
"""
import re


class CPFValidator:
    """
    Classe para validação de CPF.
    """

    def __init__(self):
        self.sequencia1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        self.sequencia2 = [11] + self.sequencia1

    @staticmethod
    def _validar_formato_entrada(cpf):
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
        dig_numericos = re.sub(r'\D', '', cpf)

        # Verificar se tem 11 dígitos, todos numéricos e é string
        if not isinstance(dig_numericos, str) or len(dig_numericos) != 11 or not dig_numericos.isdigit():
            raise ValueError(
                "CPF com formato inválido. Deve ser uma string de 11 dígitos numéricos ou um inteiro.")
        return dig_numericos

    def _calcular_digito(self, cpf_parcial):
        """
        Calcular o dígito verificador do CPF.

        Parâmetros:
            cpf_parcial (str): Parte do CPF (9 ou 10 dígitos).

        Retorna:
            int: Dígito verificador calculado.

        Raises:
            ValueError: Se as entradas forem incompatíveis.
        """

        # Definir sequência de pesos com base no comprimento do cpf_parcial
        if len(cpf_parcial) == 9:
            sequencia = self.sequencia1
        elif len(cpf_parcial) == 10:
            sequencia = self.sequencia2
        else:
            raise ValueError("CPF parcial deve ter 9 ou 10 dígitos.")

        # Calcular o dígito verificador
        soma = sum(int(digito) * peso for digito,
                   peso in zip(cpf_parcial, sequencia))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    @staticmethod
    def formatar_cpf(cpf):
        """
        Formata o CPF no padrão XXX.XXX.XXX-XX

        Parâmetros:
            cpf (str): CPF sem formatação (11 dígitos).

        Retorna:
            str: CPF formatado.
        """

        # Validar formato do CPF e retornar formatado
        cpf = CPFValidator._validar_formato_entrada(cpf)
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    def validar_cpf(self, cpf):
        """
        Valida o CPF.

        Parâmetros:
            cpf (str ou int): CPF a ser validado.

        Retorna:
            bool: True se válido, False caso contrário.
        """

        # Validar formato do CPF
        cpf = self._validar_formato_entrada(cpf)

        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * len(cpf):
            return False  # CPF com todos os dígitos iguais é inválido

        # Calcular primeiro dígito verificador
        digito1 = self._calcular_digito(cpf[:9])

        # Calcular segundo dígito verificador
        digito2 = self._calcular_digito(cpf[:9] + str(digito1))

        # Verificar se os dígitos calculados correspondem aos dígitos do CPF
        return cpf[-2:] == f"{digito1}{digito2}"
