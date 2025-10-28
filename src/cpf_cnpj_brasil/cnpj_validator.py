"""
Classe para validação de CNPJ (Cadastro Nacional da Pessoa Jurídica).
Suporta formato numérico (tradicional) e alfanumérico (a partir de junho/2026).
Implementação baseada na especificação oficial do SERPRO.
"""
import re
from datetime import datetime
from typing import Dict, Optional, Any
import time
import requests


class CNPJValidator:
    """
    Classe para validação de CNPJ.
    
    Suporta:
    - CNPJ numérico tradicional (14 dígitos)
    - CNPJ alfanumérico (14 caracteres A-Z e 0-9)
    
    Os dígitos verificadores são sempre numéricos (0-9).
    """

    def __init__(self):
        # Sequências de pesos para cálculo dos dígitos verificadores
        self.sequence1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        self.sequence2 = [6] + self.sequence1

        # URL base da API CNPJws
        self._base_url = "https://publica.cnpj.ws/cnpj/"

        # Controle de rate limit: máximo 3 requisições/minuto
        self._last_request_time = 0
        self._min_interval = 60 / 3  # 20 segundos entre requisições

    @staticmethod
    def _character_to_value(character) -> int:
        """
        Converte um caractere para seu valor numérico usando tabela ASCII.
        Implementação conforme especificação SERPRO.
        
        Parâmetros:
            character (str): Caractere a ser convertido (0-9 ou A-Z).
        
        Retorna:
            int: Valor numérico do caractere.
    
        Levanta:
            ValueError: Se o caractere não for válido (0-9 ou A-Z).
        
        Exemplos:
            '0'-'9' → 0-9
            'A'-'Z' → 17-42
        """
        value = ord(character) - 48

        # Valida se o caractere está no intervalo esperado
        # '0'-'9': 0-9 ou 'A'-'Z': 17-42
        if not (0 <= value <= 9 or 17 <= value <= 42):
            raise ValueError(f"Caractere inválido: '{character}'")

        return value

    @staticmethod
    def _validate_input_format(cnpj):
        """
        Valida o formato do CNPJ de entrada.
        Suporta formato numérico (tradicional) e alfanumérico (novo).

        Parâmetros:
            cnpj (str ou int): CNPJ a ser validado.

        Retorna:
            str: CNPJ limpo (14 caracteres, uppercase, sem pontuação).

        Raises:
            ValueError: Se o CNPJ tiver formato inválido.
        """

        # Converter para string se for inteiro (apenas numéricos)
        if isinstance(cnpj, int):
            cnpj = str(cnpj).zfill(14)

            # Se veio como int, deve ser numérico
            if len(cnpj) != 14 or not cnpj.isdigit():
                raise ValueError(
                    "CNPJ com formato inválido. Inteiro deve ter no máximo 14 dígitos.")
            return cnpj

        # Se for string, pode ser alfanumérico
        if isinstance(cnpj, str):
            # Converter para maiúsculas
            cnpj = cnpj.upper()

            # Remover pontuação mas manter alfanuméricos
            clean_cnpj = re.sub(r'[.\-/\s]', '', cnpj)

            # Verificar se tem 14 caracteres
            if len(clean_cnpj) != 14:
                raise ValueError(
                    "CNPJ deve ter 14 caracteres (letras A-Z ou números 0-9).")

            # Verificar se todos são alfanuméricos (A-Z ou 0-9)
            if not re.match(r'^[A-Z0-9]{14}$', clean_cnpj):
                raise ValueError(
                    "CNPJ deve conter apenas letras (A-Z) e números (0-9).")

            return clean_cnpj

        raise ValueError("CNPJ deve ser string ou inteiro.")

    def _calculate_digit(self, partial_cnpj):
        """
        Calcular o dígito verificador do CNPJ.

        Parâmetros:
            partial_cnpj (str): Parte do CNPJ (12 ou 13 dígitos).

        Retorna:
            int: Dígito verificador calculado.

        Raises:
            ValueError: Se as entradas forem incompatíveis.
        """

        # Definir sequência de pesos com base no comprimento do partial_cnpj
        if len(partial_cnpj) == 12:
            sequence = self.sequence1
        elif len(partial_cnpj) == 13:
            sequence = self.sequence2
        else:
            raise ValueError("CNPJ parcial deve ter 12 ou 13 dígitos.")

        # Calcular o dígito verificador
        sum_value = sum(self._character_to_value(digit) * weight for digit,
                   weight in zip(partial_cnpj, sequence))
        remainder = sum_value % 11
        return 0 if remainder < 2 else 11 - remainder

    @staticmethod
    def format_cnpj(cnpj):
        """
        Formata o CNPJ no padrão XX.XXX.XXX/XXXX-XX
        Suporta CNPJ numérico e alfanumérico.

        Parâmetros:
            cnpj (str ou int): CNPJ sem formatação (14 caracteres).

        Retorna:
            str: CNPJ formatado.
        """

        # Validar formato do CNPJ e retornar formatado
        cnpj = CNPJValidator._validate_input_format(cnpj)
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

    def validate_cnpj(self, cnpj):
        """
        Valida o CNPJ (numérico ou alfanumérico).

        Parâmetros:
            cnpj (str ou int): CNPJ a ser validado.

        Retorna:
            bool: True se válido, False caso contrário.
        """

        # Validar formato do CNPJ
        cnpj = self._validate_input_format(cnpj)

        # Calcular primeiro dígito verificador
        digit1 = self._calculate_digit(cnpj[:12])

        # Calcular segundo dígito verificador
        digit2 = self._calculate_digit(cnpj[:12] + str(digit1))

        # Verificar se os dígitos calculados correspondem aos dígitos do CNPJ
        return cnpj[-2:] == f"{digit1}{digit2}"

    def find_headquarters(self, branch_cnpj):
        """
        Encontra o CNPJ da matriz a partir do CNPJ da filial.
        Suporta CNPJ numérico e alfanumérico.

        Parâmetros:
            branch_cnpj (str ou int): CNPJ da filial.

        Retorna:
            str: CNPJ da matriz formatado.

        Raises:
            ValueError: Se o CNPJ da filial for inválido.
        """

        # Validar formato do CNPJ da filial
        branch_cnpj = self._validate_input_format(branch_cnpj)

        # Verificar se o CNPJ é válido
        if not self.validate_cnpj(branch_cnpj):
            raise ValueError("CNPJ inserido é inválido.")

        # Extrair a parte do CNPJ que identifica a empresa (8 primeiros dígitos)
        partial_headquarters_cnpj = branch_cnpj[:8] + '0001'

        # Calcular os dígitos verificadores para o CNPJ da matriz
        digit1 = self._calculate_digit(partial_headquarters_cnpj)
        digit2 = self._calculate_digit(partial_headquarters_cnpj + str(digit1))

        # Montar o CNPJ completo da matriz
        headquarters_cnpj = partial_headquarters_cnpj + f"{digit1}{digit2}"
        return self.format_cnpj(headquarters_cnpj)

    def _wait_rate_limit(self):
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

    def _extract_and_wait_for_release(self, error_message: str) -> float:
        """
        Extrai a data de liberação da mensagem de erro e aguarda até essa data.

        Parâmetros:
            error_message (str): Mensagem de erro da API.
        Retorna:
            bool: True se aguardou com sucesso, False se não encontrou data.
        Levanta:
            ValueError: Se não for possível extrair a data.
        """

        # Padrão regex para capturar a data no formato da mensagem
        pattern = r'([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{2}\s+\d{4}\s+\d{2}:\d{2}:\d{2})\s+GMT([+-]\d{4})'

        match = re.search(pattern, error_message)

        if not match:
            raise ValueError("Não foi possível extrair a data de liberação.")

        # Extrair data e timezone da mensagem
        date_str = match.group(1)
        timezone_str = match.group(2)  # Ex: "-0300"

        # Parsear a data (sem timezone ainda)
        release_date = datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S")

        # Calcular o offset do timezone da mensagem em segundos
        tz_hours = int(timezone_str[:3])
        tz_minutes = int(timezone_str[0] + timezone_str[3:])
        tz_offset_seconds = tz_hours * 3600 + tz_minutes * 60

        # Converter a data de liberação para timestamp UTC
        release_timestamp_utc = release_date.timestamp() - tz_offset_seconds

        # Obter o offset do sistema local
        utc_offset = datetime.now().astimezone().utcoffset()
        local_offset = utc_offset.total_seconds() if utc_offset is not None else 0

        # Ajustar timestamp para o timezone local
        release_timestamp_local = release_timestamp_utc + local_offset

        # Tempo atual
        current_timestamp = time.time()

        # Calcular quanto tempo falta
        wait_seconds = release_timestamp_local - current_timestamp

        # Definir minutos e segundos de espera
        minutes = int(wait_seconds // 60)
        seconds = int(wait_seconds % 60)

        if wait_seconds <= 0:
            # print("A liberação já ocorreu!")
            return 0

        print(f"Aguardando liberação: {minutes}m {seconds}s")
        return wait_seconds

    def investigate(self, cnpj: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Consulta informações de um CNPJ via API OpenCNPJ.
        Suporta CNPJ numérico e alfanumérico (dependendo do suporte da API).
        
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
        cnpj = self._validate_input_format(cnpj)

        # Aguardar para respeitar o rate limit
        self._wait_rate_limit()

        try:
            # Fazer a requisição GET
            response = requests.get(self._base_url + cnpj, timeout=timeout)
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
                wait_for_release = self._extract_and_wait_for_release(response_info['detalhes'])
                # Aguardar tempo necessário para liberação
                time.sleep(wait_for_release)

            if response.status_code not in (200, 404, 429):
                # Outro código de status
                print(
                    f"Erro ao consultar CNPJ. Status code: {response.status_code}")

            return None

        # Levantar exceções específicas para tratamento externo
        except requests.exceptions.SSLError:
            print(
                f"Erro de certificado SSL ao consultar o CNPJ {self.format_cnpj(cnpj)}. "
                "Verifique a configuração de certificados do sistema.")
            return None

        except requests.exceptions.Timeout:
            print(
                f"Tempo limite excedido ao consultar o CNPJ {self.format_cnpj(cnpj)}.")
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
