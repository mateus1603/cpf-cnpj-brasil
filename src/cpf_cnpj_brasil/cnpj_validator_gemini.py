"""
Classe para validação de CNPJ (Cadastro Nacional da Pessoa Jurídica).

Suporta formato numérico (tradicional) e alfanumérico (a partir de junho/2026).
Implementação baseada na especificação oficial do SERPRO.
"""
import re
import time
import functools
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Callable

import requests


def rate_limited(min_interval: float) -> Callable:
    """
    Decorator para garantir um intervalo mínimo entre chamadas de função.
    """
    def decorator(func: Callable) -> Callable:
        last_request_time = 0.0

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            nonlocal last_request_time

            # Definir a diferença de tempo desde a última requisição
            current_time = time.time()
            time_since_last = current_time - last_request_time

            # Verificar se é necessário aguardar
            if time_since_last < min_interval:
                # Aguarda o tempo necessário para respeitar o rate limit
                wait_time = min_interval - time_since_last
                time.sleep(wait_time)

            # Atualizar o tempo da última requisição
            last_request_time = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class CNPJValidator:
    """
    Classe para validação de CNPJ.

    Suporta:
    - CNPJ numérico tradicional (14 dígitos)
    - CNPJ alfanumérico (14 caracteres A-Z e 0-9)

    Os dígitos verificadores são sempre numéricos (0-9).
    """

    # Sequências de pesos para cálculo dos dígitos verificadores
    _SEQUENCE1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    _SEQUENCE2 = [6] + _SEQUENCE1

    # Rate limit da API CNPJws: máximo 3 requisições/minuto
    _MIN_INTERVAL = 60 / 3  # 20 segundos

    # URL base da API CNPJws
    _BASE_URL = "https://publica.cnpj.ws/cnpj/"

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
        Validar o formato do CNPJ de entrada.

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

    @staticmethod
    def _calculate_digit(partial_cnpj):
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
            sequence = CNPJValidator._SEQUENCE1
        elif len(partial_cnpj) == 13:
            sequence = CNPJValidator._SEQUENCE2
        else:
            raise ValueError("CNPJ parcial deve ter 12 ou 13 dígitos.")

        # Calcular o dígito verificador
        sum_value = sum(
            CNPJValidator._character_to_value(digit) * weight
            for digit, weight in zip(partial_cnpj, sequence)
        )
        remainder = sum_value % 11
        return 0 if remainder < 2 else 11 - remainder

    @staticmethod
    def format_cnpj(cnpj):
        """
        Formatar o CNPJ no padrão AA.AAA.AAA/AAAA-DV.

        Suporta CNPJ numérico e alfanumérico.

        Parâmetros:
            cnpj (str ou int): CNPJ sem formatação (14 caracteres).

        Retorna:
            str: CNPJ formatado.
        """

        # Validar formato do CNPJ e retornar formatado
        cnpj = CNPJValidator._validate_input_format(cnpj)
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

    @staticmethod
    def validate_cnpj(cnpj):
        """
        Validar o CNPJ (numérico ou alfanumérico).

        Parâmetros:
            cnpj (str ou int): CNPJ a ser validado.

        Retorna:
            bool: True se válido, False caso contrário.
        """

        # Validar formato do CNPJ
        cnpj = CNPJValidator._validate_input_format(cnpj)

        # Calcular primeiro dígito verificador
        digit1 = CNPJValidator._calculate_digit(cnpj[:12])

        # Calcular segundo dígito verificador
        digit2 = CNPJValidator._calculate_digit(cnpj[:12] + str(digit1))

        # Verificar se os dígitos calculados correspondem aos dígitos do CNPJ
        return cnpj[-2:] == f"{digit1}{digit2}"

    @staticmethod
    def find_headquarters(branch_cnpj):
        """
        Encontrar o CNPJ da matriz a partir do CNPJ da filial.

        Suporta CNPJ numérico e alfanumérico.

        Parâmetros:
            branch_cnpj (str ou int): CNPJ da filial.

        Retorna:
            str: CNPJ da matriz formatado.

        Raises:
            ValueError: Se o CNPJ da filial for inválido.
        """

        # Validar formato do CNPJ da filial
        branch_cnpj = CNPJValidator._validate_input_format(branch_cnpj)

        # Verificar se o CNPJ é válido
        if not CNPJValidator.validate_cnpj(branch_cnpj):
            raise ValueError("CNPJ inserido é inválido.")

        # Extrair a parte do CNPJ que identifica a empresa (8 primeiros dígitos)
        partial_headquarters_cnpj = branch_cnpj[:8] + '0001'

        # Calcular os dígitos verificadores para o CNPJ da matriz
        digit1 = CNPJValidator._calculate_digit(partial_headquarters_cnpj)
        digit2 = CNPJValidator._calculate_digit(partial_headquarters_cnpj + str(digit1))

        # Montar o CNPJ completo da matriz
        headquarters_cnpj = partial_headquarters_cnpj + f"{digit1}{digit2}"
        return CNPJValidator.format_cnpj(headquarters_cnpj)

    @staticmethod
    def _extract_and_wait_for_release(error_message: str) -> float:
        """
        Extrair a data de liberação da mensagem de erro e aguardar.

        Parâmetros:
            error_message (str): Mensagem de erro da API.
        Retorna:
            bool: True se aguardou com sucesso, False se não encontrou data.
        Levanta:
            ValueError: Se não for possível extrair a data.
        """

        # Padrão regex para capturar a data no formato da mensagem
        # pattern = r'([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{2}\s+\d{4}\s+\d{2}:\d{2}:\d{2})\s+GMT([+-]\d{4})'
        pattern = (
            r'([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{2}\s+\d{4}\s+'
            r'\d{2}:\d{2}:\d{2})\s+GMT([+-]\d{4})'
        )
        match = re.search(pattern, error_message)

        if not match:
            raise ValueError("Não foi possível extrair a data de liberação.")

        # Extrair data e timezone da mensagem
        date_str = match.group(1)
        timezone_str = match.group(2)  # Ex: "-0300"

        # Criar objeto de fuso horário a partir da string de offset
        # Ex: -0300 -> offset de -3 horas
        tz_offset = timedelta(hours=int(timezone_str[:3]),
                              minutes=int(timezone_str[0] + timezone_str[3:]))
        tz = timezone(tz_offset)
        # Parsear a data e aplicar o fuso horário
        # Formato: "Mon Oct 27 2025 14:30:00"
        release_date_aware = datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S")
        release_date_aware = release_date_aware.replace(tzinfo=tz)

        # Obter a data/hora local ATUAL, ciente do fuso horário
        now_local = datetime.now().astimezone()

        # Calcular o tempo de espera em segundos
        # Isso funciona corretamente mesmo que o servidor e o cliente
        # estejam em fusos horários diferentes.
        wait_seconds = (release_date_aware - now_local).total_seconds()

        if wait_seconds <= 0:
            # print("A liberação já ocorreu!")
            return 0

        # Definir minutos e segundos de espera
        minutes = int(wait_seconds // 60)
        seconds = int(wait_seconds % 60)
        print(f"Aguardando liberação: {minutes}m {seconds}s")
        return wait_seconds

    @rate_limited(min_interval=_MIN_INTERVAL)
    @staticmethod
    def investigate(cnpj: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Consultar informações de um CNPJ via API CNPJws.
        
        Suporta CNPJ numérico e alfanumérico (dependendo do suporte da API).

        Parâmetros:
            cnpj (str ou int): CNPJ a ser consultado (com ou sem formatação).
            timeout (int): Tempo máximo de espera pela resposta da API em segundos (padrão: 10).
        Retorna:
            dict: Dicionário com os dados do CNPJ se encontrado.
            None: Se o CNPJ não for encontrado (404).
        Levanta:
            ValueError: Se o CNPJ tiver formato inválido.
            requests.exceptions.SSLError: Se houver erro de certificado SSL.
            requests.exceptions.Timeout: Se a requisição exceder o tempo limite.
            requests.exceptions.ConnectionError: Se houver falha na conexão.
            requests.exceptions.RequestException: Para outros erros de requisição.
        Nota:
            Este método respeita o rate limit de 3 requisições/minuto da API CNPJws.
            Pode ser usado em loops sem preocupação com o limite de requisições.
        """

        # Validar formato do CNPJ
        cnpj = CNPJValidator._validate_input_format(cnpj)

        try:
            # Fazer a requisição GET
            response = requests.get(CNPJValidator._BASE_URL + cnpj, timeout=timeout)
            # Tentar parsear JSON mesmo em caso de erro, pois a API retorna detalhes
            response_info = response.json()

            # Verificar o código de status
            if response.status_code == 200:
                # CNPJ encontrado - retornar dados em JSON
                return response_info

            if response.status_code == 404:
                # CNPJ não encontrado
                print(
                    f"{response_info['titulo']}. {response_info['detalhes']}.")
                return None  # Retorna None especificamente para 404

            if response.status_code == 429:
                # Limite de requisições excedido
                print(
                    f"{response_info['titulo']}. {response_info['detalhes']}.")
                # Extrair e aguardar liberação
                wait_for_release = CNPJValidator._extract_and_wait_for_release(
                    response_info['detalhes'])
                # Aguardar tempo necessário para liberação
                time.sleep(wait_for_release)
                # Retornar None para indicar que a operação falhou desta vez
                return None

            if response.status_code not in (200, 404, 429):
                # Outro código de status
                print(
                    f"Erro ao consultar CNPJ. Status code: {response.status_code}")
                # Levanta um erro genérico do requests para outros status
                response.raise_for_status()

            return None

        # Levantar exceções específicas para tratamento externo
        except requests.exceptions.SSLError as e:
            print(
                f"Erro de certificado SSL ao consultar o CNPJ {CNPJValidator.format_cnpj(cnpj)}. "
                "Verifique a configuração de certificados do sistema.")
            raise e  # Re-levanta a exceção

        except requests.exceptions.Timeout as e:
            print(
                f"Tempo limite excedido ao consultar o CNPJ {CNPJValidator.format_cnpj(cnpj)}.")
            raise e  # Re-levanta a exceção

        except requests.exceptions.ConnectionError as e:
            print("Erro de conexão ao consultar a API OpenCNPJ.")
            raise e  # Re-levanta a exceção

        except requests.exceptions.RequestException as e:
            # Captura outros erros do requests (como o raise_for_status)
            print(f"Erro ao fazer requisição: {e}")
            raise e  # Re-levanta a exceção

        except ValueError as e:
            # Re-lançar ValueError de validação de formato
            raise e
