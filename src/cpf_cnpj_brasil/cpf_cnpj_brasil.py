"""
Módulo para validação de CPF (Cadastro de Pessoas Físicas) e 
CNPJ (Cadastro Nacional da Pessoa Jurídica).
"""
import re
import time
import requests
from typing import Dict, Optional, Any


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


class CNPJValidator:
    """
    Classe para validação de CNPJ.
    """

    def __init__(self):
        # Sequências de pesos para cálculo dos dígitos verificadores
        self.sequencia1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        self.sequencia2 = [6] + self.sequencia1
        
        # URL base da API OpenCNPJ
        self._url_base = "https://api.opencnpj.org/"

        # Controle de rate limit: máximo 50 requisições/segundo
        self._last_request_time = 0
        self._min_interval = 1 / 50  # ~0.02 segundos entre requisições

    @staticmethod
    def _validar_formato_entrada(cnpj):
        """
        Valida o formato do CNPJ de entrada.

        Parâmetros:
            cnpj (str ou int): CNPJ a ser validado.

        Retorna:
            bool: True se válido, False caso contrário.
        
        Raises:
            ValueError: Se o CNPJ tiver formato inválido.
        """

        # Converter para string se for inteiro
        if isinstance(cnpj, int):
            cnpj = str(cnpj).zfill(14)

        # Extrair dígitos numéricos
        dig_numericos = re.sub(r'\D', '', cnpj)

        # Verificar se tem 14 dígitos, todos numéricos e é string
        if not isinstance(dig_numericos, str) or len(dig_numericos) != 14 or not dig_numericos.isdigit():
            raise ValueError(
                "CNPJ com formato inválido. Deve ser uma string de 14 dígitos numéricos ou um inteiro.")
        return dig_numericos

    def _calcular_digito(self, cnpj_parcial):
        """
        Calcular o dígito verificador do CNPJ.

        Parâmetros:
            cnpj_parcial (str): Parte do CNPJ (12 ou 13 dígitos).

        Retorna:
            int: Dígito verificador calculado.
        
        Raises:
            ValueError: Se as entradas forem incompatíveis.
        """

        # Definir sequência de pesos com base no comprimento do cnpj_parcial
        if len(cnpj_parcial) == 12:
            sequencia = self.sequencia1
        elif len(cnpj_parcial) == 13:
            sequencia = self.sequencia2
        else:
            raise ValueError("CNPJ parcial deve ter 12 ou 13 dígitos.")

        # Calcular o dígito verificador
        soma = sum(int(digito) * peso for digito,
                   peso in zip(cnpj_parcial, sequencia))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    @staticmethod
    def formatar_cnpj(cnpj):
        """
        Formata o CNPJ no padrão XX.XXX.XXX/XXX-XX

        Parâmetros:
            cnpj (str): CNPJ sem formatação (14 dígitos).

        Retorna:
            str: CNPJ formatado.
        """

        # Validar formato do CNPJ e retornar formatado
        cnpj = CNPJValidator._validar_formato_entrada(cnpj)
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

    def validar_cnpj(self, cnpj):
        """
        Valida o CNPJ.

        Parâmetros:
            cnpj (str ou int): CNPJ a ser validado.

        Retorna:
            bool: True se válido, False caso contrário.
        """

        # Validar formato do CNPJ
        cnpj = self._validar_formato_entrada(cnpj)

        # Calcular primeiro dígito verificador
        digito1 = self._calcular_digito(cnpj[:12])

        # Calcular segundo dígito verificador
        digito2 = self._calcular_digito(cnpj[:12] + str(digito1))

        # Verificar se os dígitos calculados correspondem aos dígitos do CNPJ
        return cnpj[-2:] == f"{digito1}{digito2}"

    def encontrar_matriz(self, cnpj_filial):
        """
        Encontra o CNPJ da matriz a partir do CNPJ da filial.

        Parâmetros:
            cnpj_filial (str ou int): CNPJ da filial.

        Retorna:
            str: CNPJ da matriz formatado.
        
        Raises:
            ValueError: Se o CNPJ da filial for inválido.
        """

        # Validar formato do CNPJ da filial
        cnpj_filial = self._validar_formato_entrada(cnpj_filial)

        # Verificar se o CNPJ é válido
        if not self.validar_cnpj(cnpj_filial):
            raise ValueError("CNPJ inserido é inválido.")

        # Extrair a parte do CNPJ que identifica a empresa (8 primeiros dígitos)
        cnpj_matriz_parcial = cnpj_filial[:8] + '0001'

        # Calcular os dígitos verificadores para o CNPJ da matriz
        digito1 = self._calcular_digito(cnpj_matriz_parcial)
        digito2 = self._calcular_digito(cnpj_matriz_parcial + str(digito1))

        # Montar o CNPJ completo da matriz
        cnpj_matriz = cnpj_matriz_parcial + f"{digito1}{digito2}"
        return self.formatar_cnpj(cnpj_matriz)

    def _aguardar_rate_limit(self):
        """
        Aguarda o tempo necessário para respeitar o rate limit da API.
        Garante que não sejam feitas mais de 50 requisições por segundo.
        """

        # Definir a diferença de tempo desde a última requisição
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time

        # Verificar se é necessário aguardar
        if time_since_last_request < self._min_interval:
            # Aguarda o tempo necessário para respeitar o rate limit
            time.sleep(self._min_interval - time_since_last_request)

        # Atualizar o tempo da última requisição
        self._last_request_time = time.time()

    def investigar(self, cnpj: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Consulta informações de um CNPJ via API OpenCNPJ.
        Parâmetros:
            cnpj (str ou int): CNPJ a ser consultado (com ou sem formatação).
            timeout (int): Tempo máximo de espera pela resposta da API em segundos (padrão: 10).
        Retorna:
            dict: Dicionário com os dados do CNPJ se encontrado.
            None: Se o CNPJ não for encontrado ou ocorrer erro.
        Levanta:
            ValueError: Se o CNPJ tiver formato inválido.
            requests.exceptions.RequestException: Se houver erro de conexão.
        Nota:
            Este método respeita o rate limit de 50 requisições/segundo da API OpenCNPJ.
            Pode ser usado em loops sem preocupação com o limite de requisições.
        """

        # Validar formato do CNPJ
        cnpj = self._validar_formato_entrada(cnpj)

        # Aguardar para respeitar o rate limit
        self._aguardar_rate_limit()

        try:
            # Fazer a requisição GET
            response = requests.get(self._url_base + cnpj, timeout=timeout)

            # Verificar o código de status
            if response.status_code == 200:
                # CNPJ encontrado - retornar dados em JSON
                return response.json()

            elif response.status_code == 404:
                # CNPJ não encontrado
                print(
                    f"CNPJ {self.formatar_cnpj(cnpj)} não encontrado na base de dados.")
                return None

            elif response.status_code == 429:
                # Limite de requisições excedido
                print(
                    "Limite de requisições excedido. Aguarde alguns instantes e tente novamente.")
                # Aguardar 1 segundo adicional antes de retornar
                time.sleep(1)
                return None

            else:
                # Outro código de status
                print(
                    f"Erro ao consultar CNPJ. Status code: {response.status_code}")
                return None

        # Levantar exceções específicas para tratamento externo
        except requests.exceptions.SSLError:
            print(
                f"Erro de certificado SSL ao consultar o CNPJ {self.formatar_cnpj(cnpj)}. "
                "Verifique a configuração de certificados do sistema.")
            return None

        except requests.exceptions.Timeout:
            print(
                f"Tempo limite excedido ao consultar o CNPJ {self.formatar_cnpj(cnpj)}.")
            return None

        except requests.exceptions.ConnectionError:
            print("Erro de conexão ao consultar a API OpenCNPJ.")
            return None

        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer requisição: {e}")
            return None

        except ValueError as e:
            # Re-lançar ValueError de validação de formato
            raise e
