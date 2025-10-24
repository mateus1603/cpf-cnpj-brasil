"""
Classe para validação de CNPJ (Cadastro Nacional da Pessoa Jurídica).
"""
from os import times
import re
from datetime import datetime
from typing import Dict, Optional, Any
import time
import requests


class CNPJValidator:
    """
    Classe para validação de CNPJ.
    """

    def __init__(self):
        # Sequências de pesos para cálculo dos dígitos verificadores
        self.sequencia1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        self.sequencia2 = [6] + self.sequencia1

        # URL base da API OpenCNPJ
        self._url_base = "https://publica.cnpj.ws/cnpj/"

        # Controle de rate limit: máximo 3 requisições/minuto
        self._last_request_time = 0
        self._min_interval = 60 / 3  # 20 segundos entre requisições

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
                "CNPJ com formato inválido. Deve ser uma string de 14 dígitos.")
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

    def _extrair_e_aguardar_liberacao(self, mensagem_erro: str) -> int:
        """
        Extrai a data de liberação da mensagem de erro e aguarda até essa data.

        Parâmetros:
            mensagem_erro (str): Mensagem de erro da API.
        Retorna:
            bool: True se aguardou com sucesso, False se não encontrou data.
        """

        # Padrão regex para capturar a data no formato da mensagem
        padrao = r'([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{2}\s+\d{4}\s+\d{2}:\d{2}:\d{2})\s+GMT([+-]\d{4})'

        match = re.search(padrao, mensagem_erro)

        if not match:
            raise ValueError("Não foi possível extrair a data de liberação.")

        # Extrair data e timezone da mensagem
        data_str = match.group(1)
        timezone_str = match.group(2)  # Ex: "-0300"

        # Parsear a data (sem timezone ainda)
        data_liberacao = datetime.strptime(data_str, "%a %b %d %Y %H:%M:%S")

        # Calcular o offset do timezone da mensagem em segundos
        tz_hours = int(timezone_str[:3])
        tz_minutes = int(timezone_str[0] + timezone_str[3:])
        tz_offset_segundos = tz_hours * 3600 + tz_minutes * 60

        # Converter a data de liberação para timestamp UTC
        timestamp_liberacao_utc = data_liberacao.timestamp() - tz_offset_segundos

        # Obter o offset do sistema local
        utc_offset = datetime.now().astimezone().utcoffset()
        offset_local = utc_offset.total_seconds() if utc_offset is not None else 0

        # Ajustar timestamp para o timezone local
        timestamp_liberacao_local = timestamp_liberacao_utc + offset_local

        # Tempo atual
        timestamp_atual = time.time()

        # Calcular quanto tempo falta
        segundos_espera = timestamp_liberacao_local - timestamp_atual

        if segundos_espera <= 0:
            print("A liberação já ocorreu!")
            return 0
        
        minutos_espera = int(segundos_espera // 60)
        segundos_espera = int(segundos_espera % 60)

        print(f"Aguardando liberação... {minutos_espera}m {segundos_espera}s")
        print(f"Liberação em: {data_str} GMT{timezone_str}")

        time.sleep(segundos_espera)
        print("Liberado! Continuando...")

        return 0


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
            SSLError: Se houver erro de certificado SSL.
            TimeoutError: Se a requisição exceder o tempo limite.
            ConnectionError: Se houver falha na conexão.
            RequestException: Para outros erros de requisição.
            ValueError: Como boa prática, se o CNPJ tiver formato inválido.
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
            response_info = response.json()  # Forçar o parsing do JSON para capturar erros

            # Verificar o código de status
            if response.status_code == 200:
                # CNPJ encontrado - retornar dados em JSON
                return response_info

            if response.status_code == 404:
                # CNPJ não encontrado
                print(
                    f"{response_info['titulo']}. {response_info['detalhes']}.")

            if response.status_code == 429:
                # Limite de requisições excedido
                print(
                    f"{response_info['titulo']}. {response_info['detalhes']}.")
                # Extrair e aguardar liberação
                aguardar_liberacao = self._extrair_e_aguardar_liberacao(response_info['detalhes'])
                # Aguardar 1 segundo adicional antes de retornar
                time.sleep(aguardar_liberacao)

            if response.status_code not in (200, 404, 429):
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
