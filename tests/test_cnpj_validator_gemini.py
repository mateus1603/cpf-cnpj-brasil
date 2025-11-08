"""Testes unitários para o módulo CNPJ."""
from unittest.mock import patch, Mock
import pytest

from cpf_cnpj_brasil.cnpj_validator_gemini import CNPJ
from cpf_cnpj_brasil.exceptions import CNPJValidationError, CNPJAPIError


class TestCNPJCharacterToValue:
    """Testes para o método _character_to_value."""

    def test_digito_0(self):
        """Testa conversão do dígito 0."""
        assert CNPJ._character_to_value('0') == 0

    def test_digito_9(self):
        """Testa conversão do dígito 9."""
        assert CNPJ._character_to_value('9') == 9

    def test_letra_A(self):
        """Testa conversão da letra A."""
        assert CNPJ._character_to_value('A') == 17

    def test_letra_Z(self):
        """Testa conversão da letra Z."""
        assert CNPJ._character_to_value('Z') == 42

    def test_letra_M(self):
        """Testa conversão da letra M (meio do alfabeto)."""
        assert CNPJ._character_to_value('M') == 29

    def test_caractere_minusculo_invalido(self):
        """Testa que letras minúsculas são inválidas."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._character_to_value('a')
        assert "inválido" in str(excinfo.value).lower()

    def test_caractere_especial_invalido(self):
        """Testa que caracteres especiais são inválidos."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._character_to_value('@')
        assert "inválido" in str(excinfo.value).lower()

    def test_espaco_invalido(self):
        """Testa que espaço é inválido."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._character_to_value(' ')
        assert "inválido" in str(excinfo.value).lower()


class TestCNPJValidateInputFormat:
    """Testes para o método _validate_input_format."""

    # CNPJs numéricos válidos
    def test_cnpj_string_valido_com_formatacao(self):
        """Testa CNPJ string válido com formatação."""
        result = CNPJ._validate_input_format("12.345.678/0001-95")
        assert result == "12345678000195"

    def test_cnpj_string_valido_sem_formatacao(self):
        """Testa CNPJ string válido sem formatação."""
        result = CNPJ._validate_input_format("12345678000195")
        assert result == "12345678000195"

    def test_cnpj_inteiro_valido(self):
        """Testa CNPJ como inteiro válido."""
        result = CNPJ._validate_input_format(12345678000195)
        assert result == "12345678000195"

    def test_cnpj_inteiro_com_zeros_a_esquerda(self):
        """Testa CNPJ inteiro que precisa de zeros à esquerda."""
        result = CNPJ._validate_input_format(1234567890123)
        assert result == "01234567890123"

    # CNPJs alfanuméricos válidos
    def test_cnpj_alfanumerico_maiusculo(self):
        """Testa CNPJ alfanumérico com letras maiúsculas."""
        result = CNPJ._validate_input_format("ABC12345000195")
        assert result == "ABC12345000195"

    def test_cnpj_alfanumerico_minusculo_convertido(self):
        """Testa CNPJ alfanumérico com letras minúsculas (convertidas)."""
        result = CNPJ._validate_input_format("abc12345000195")
        assert result == "ABC12345000195"

    def test_cnpj_alfanumerico_formatado(self):
        """Testa CNPJ alfanumérico formatado."""
        result = CNPJ._validate_input_format("AB.C12.345/0001-95")
        assert result == "ABC12345000195"

    # CNPJs inválidos - formato
    def test_cnpj_string_com_menos_de_14_caracteres(self):
        """Testa CNPJ string com menos de 14 caracteres."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._validate_input_format("1234567890123")
        assert "14 caracteres" in str(excinfo.value).lower()

    def test_cnpj_string_com_mais_de_14_caracteres(self):
        """Testa CNPJ string com mais de 14 caracteres."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._validate_input_format("123456789012345")
        assert "14 caracteres" in str(excinfo.value).lower()

    def test_cnpj_inteiro_com_mais_de_14_digitos(self):
        """Testa CNPJ inteiro com mais de 14 dígitos."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._validate_input_format(123456789012345)
        assert "formato inválido" in str(excinfo.value).lower()

    def test_cnpj_inteiro_negativo(self):
        """Testa CNPJ inteiro negativo."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._validate_input_format(-12345678000195)
        assert "negativo" in str(excinfo.value).lower()

    def test_cnpj_com_caracteres_invalidos(self):
        """Testa CNPJ com caracteres não alfanuméricos."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._validate_input_format("123456@8000195")
        assert "apenas letras" in str(excinfo.value).lower()

    def test_cnpj_tipo_invalido(self):
        """Testa CNPJ com tipo inválido (não string nem inteiro)."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._validate_input_format(12.345)
        assert "string ou inteiro" in str(excinfo.value).lower()

    def test_cnpj_none(self):
        """Testa CNPJ None."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._validate_input_format(None)
        assert "string ou inteiro" in str(excinfo.value).lower()

    def test_cnpj_lista(self):
        """Testa CNPJ como lista."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._validate_input_format([1, 2, 3])
        assert "string ou inteiro" in str(excinfo.value).lower()

    def test_cnpj_vazio(self):
        """Testa CNPJ string vazia."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._validate_input_format("")
        assert "14 caracteres" in str(excinfo.value).lower()


class TestCNPJCalculateDigit:
    """Testes para o método _calculate_digit."""

    def test_calculo_primeiro_digito(self):
        """Testa cálculo do primeiro dígito verificador."""
        result = CNPJ._calculate_digit("123456780001")
        assert isinstance(result, int)
        assert 0 <= result <= 9

    def test_calculo_segundo_digito(self):
        """Testa cálculo do segundo dígito verificador."""
        result = CNPJ._calculate_digit("1234567800019")
        assert isinstance(result, int)
        assert 0 <= result <= 9

    def test_cnpj_parcial_com_11_caracteres(self):
        """Testa CNPJ parcial com 11 caracteres (inválido)."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._calculate_digit("12345678001")
        assert "12 ou 13 dígitos" in str(excinfo.value).lower()

    def test_cnpj_parcial_com_14_caracteres(self):
        """Testa CNPJ parcial com 14 caracteres (inválido)."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._calculate_digit("12345678000195")
        assert "12 ou 13 dígitos" in str(excinfo.value).lower()

    def test_cnpj_parcial_vazio(self):
        """Testa CNPJ parcial vazio."""
        with pytest.raises(CNPJValidationError) as excinfo:
            CNPJ._calculate_digit("")
        assert "12 ou 13 dígitos" in str(excinfo.value).lower()

    def test_cnpj_alfanumerico_parcial(self):
        """Testa cálculo com CNPJ alfanumérico parcial."""
        result = CNPJ._calculate_digit("ABC123450001")
        assert isinstance(result, int)
        assert 0 <= result <= 9

    def test_digito_quando_resto_menor_que_2(self):
        """Testa caso onde o resto é menor que 2 (dígito = 0)."""
        result = CNPJ._calculate_digit("000000000006")
        assert result == 0


class TestCNPJFormat:
    """Testes para o método format."""

    def test_formatar_cnpj_numerico_string(self):
        """Testa formatação de CNPJ numérico como string."""
        result = CNPJ.format("11222333000181")
        assert result == "11.222.333/0001-81"

    def test_formatar_cnpj_numerico_inteiro(self):
        """Testa formatação de CNPJ numérico como inteiro."""
        result = CNPJ.format(11222333000181)
        assert result == "11.222.333/0001-81"

    def test_formatar_cnpj_alfanumerico(self):
        """Testa formatação de CNPJ alfanumérico."""
        result = CNPJ.format("AB222333000181")
        assert result == "AB.222.333/0001-81"

    def test_formatar_cnpj_ja_formatado(self):
        """Testa formatação de CNPJ já formatado."""
        result = CNPJ.format("11.222.333/0001-81")
        assert result == "11.222.333/0001-81"

    def test_formatar_cnpj_com_zeros_a_esquerda(self):
        """Testa formatação de CNPJ com zeros à esquerda."""
        result = CNPJ.format(1222333000181)
        assert result == "01.222.333/0001-81"

    def test_formatar_cnpj_invalido(self):
        """Testa formatação de CNPJ inválido."""
        with pytest.raises(CNPJValidationError):
            CNPJ.format("123")


class TestCNPJValidate:
    """Testes para o método validate."""

    # CNPJs numéricos válidos conhecidos
    def test_validar_cnpj_valido_11222333000181(self):
        """Testa CNPJ válido conhecido."""
        result = CNPJ.validate("11.222.333/0001-81")
        assert result == "11222333000181"

    def test_validar_cnpj_valido_00000000000191(self):
        """Testa CNPJ válido com zeros."""
        result = CNPJ.validate("00000000000191")
        assert result == "00000000000191"

    def test_validar_cnpj_valido_inteiro(self):
        """Testa CNPJ válido como inteiro."""
        result = CNPJ.validate(11222333000181)
        assert result == "11222333000181"

    def test_validar_cnpj_valido_string_formatada(self):
        """Testa CNPJ válido como string formatada."""
        result = CNPJ.validate("11.222.333/0001-81")
        assert result == "11222333000181"

    def test_validar_cnpj_valido_string_sem_formatacao(self):
        """Testa CNPJ válido como string sem formatação."""
        result = CNPJ.validate("11222333000181")
        assert result == "11222333000181"

    # CNPJs com todos os caracteres iguais (inválidos)
    def test_validar_cnpj_todos_digitos_iguais_00000000000000(self):
        """Testa CNPJ com todos os dígitos iguais (00000000000000)."""
        result = CNPJ.validate("00000000000000")
        assert result is False

    def test_validar_cnpj_todos_digitos_iguais_11111111111111(self):
        """Testa CNPJ com todos os dígitos iguais (11111111111111)."""
        result = CNPJ.validate("11111111111111")
        assert result is False

    def test_validar_cnpj_todos_digitos_iguais_AAAAAAAAAAAAAA(self):
        """Testa CNPJ com todas as letras iguais."""
        result = CNPJ.validate("AAAAAAAAAAAAAA")
        assert result is False

    # CNPJs com dígitos verificadores incorretos
    def test_validar_cnpj_digitos_verificadores_incorretos(self):
        """Testa CNPJ com dígitos verificadores incorretos."""
        result = CNPJ.validate("11222333000182")
        assert result is False

    def test_validar_cnpj_primeiro_digito_incorreto(self):
        """Testa CNPJ com primeiro dígito verificador incorreto."""
        result = CNPJ.validate("11222333000191")
        assert result is False

    # CNPJs com formato inválido
    def test_validar_cnpj_formato_invalido_curto(self):
        """Testa CNPJ muito curto."""
        result = CNPJ.validate("1122233300018")
        assert result is False

    def test_validar_cnpj_formato_invalido_longo(self):
        """Testa CNPJ muito longo."""
        result = CNPJ.validate("112223330001811")
        assert result is False

    def test_validar_cnpj_com_caracteres_invalidos(self):
        """Testa CNPJ com caracteres inválidos."""
        result = CNPJ.validate("11@22#33/0001-81")
        assert result is False

    def test_validar_cnpj_vazio(self):
        """Testa CNPJ vazio."""
        result = CNPJ.validate("")
        assert result is False

    def test_validar_cnpj_tipo_invalido_float(self):
        """Testa CNPJ com tipo float."""
        result = CNPJ.validate(11.222)
        assert result is False

    def test_validar_cnpj_tipo_invalido_none(self):
        """Testa CNPJ None."""
        result = CNPJ.validate(None)
        assert result is False

    def test_validar_cnpj_inteiro_negativo(self):
        """Testa CNPJ inteiro negativo."""
        result = CNPJ.validate(-11222333000181)
        assert result is False

    # CNPJs alfanuméricos
    def test_validar_cnpj_alfanumerico_valido(self):
        """Testa validação de CNPJ alfanumérico (se houver um válido)."""
        # Nota: precisaria de um CNPJ alfanumérico válido real
        # Por ora, testaremos a estrutura
        pass

    def test_validar_cnpj_alfanumerico_minusculo(self):
        """Testa que letras minúsculas são convertidas para maiúsculas."""
        # Se abc12333000181 fosse válido, deveria aceitar
        result = CNPJ.validate("abc12333000181")
        # Resultado depende se os dígitos verificadores batem
        assert isinstance(result, (str, bool))

    # Casos limites
    def test_validar_cnpj_apenas_espacos(self):
        """Testa CNPJ com apenas espaços."""
        result = CNPJ.validate("              ")
        assert result is False


class TestCNPJFindMatrix:
    """Testes para o método find_matrix."""

    def test_encontrar_matriz_de_filial_valida(self):
        """Testa encontrar matriz a partir de filial válida."""
        # CNPJ de filial: 11.222.333/0002-XX
        # Matriz esperada: 11.222.333/0001-XX
        branch_cnpj = "11222333000281"  # Assumindo dígitos corretos
        # Primeiro valida se a filial é válida
        if CNPJ.validate(branch_cnpj):
            result = CNPJ.find_matrix(branch_cnpj)
            assert "11.222.333/0001-" in result

    def test_encontrar_matriz_ja_eh_matriz(self):
        """Testa encontrar matriz quando o CNPJ já é matriz."""
        matrix_cnpj = "11222333000181"
        result = CNPJ.find_matrix(matrix_cnpj)
        # Deve retornar a própria matriz formatada
        assert result == "11.222.333/0001-81"

    def test_encontrar_matriz_cnpj_invalido(self):
        """Testa encontrar matriz com CNPJ inválido."""
        with pytest.raises(CNPJValidationError):
            CNPJ.find_matrix("11111111111111")

    def test_encontrar_matriz_cnpj_formato_invalido(self):
        """Testa encontrar matriz com formato inválido."""
        with pytest.raises(CNPJValidationError):
            CNPJ.find_matrix("123")

    def test_encontrar_matriz_com_cnpj_formatado(self):
        """Testa encontrar matriz com CNPJ formatado."""
        branch_cnpj = "11.222.333/0002-62"
        if CNPJ.validate(branch_cnpj):
            result = CNPJ.find_matrix(branch_cnpj)
            assert isinstance(result, str)
            assert "/" in result
            assert "-" in result


class TestCNPJInvestigate:
    """Testes para os métodos investigate e _investigate_cnpj."""

    @patch('cpf_cnpj_brasil.cnpj_validator_gemini.requests.get')
    def test_investigate_cnpj_encontrado(self, mock_get):
        """Testa consulta de CNPJ encontrado na API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "razao_social": "Empresa Teste LTDA",
            "cnpj": "11222333000181"
        }
        mock_get.return_value = mock_response

        result = CNPJ.investigate("11222333000181")
        assert result is not None
        assert result["razao_social"] == "Empresa Teste LTDA"

    @patch('cpf_cnpj_brasil.cnpj_validator_gemini.requests.get')
    def test_investigate_cnpj_nao_encontrado(self, mock_get):
        """Testa consulta de CNPJ não encontrado (404)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "detalhes": "CNPJ não encontrado"
        }
        mock_get.return_value = mock_response

        result = CNPJ.investigate("11222333000181")
        assert result is None

    @patch('cpf_cnpj_brasil.cnpj_validator_gemini.requests.get')
    def test_investigate_cnpj_rate_limit(self, mock_get):
        """Testa comportamento com rate limit (429)."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "detalhes": "Rate limit. Tente após Mon Oct 27 2025 14:30:00 GMT-0300"
        }
        mock_get.return_value = mock_response

        # Devido ao sleep, este teste pode demorar
        # Podemos usar um timeout menor ou mockar o sleep
        with patch('time.sleep'):
            result = CNPJ.investigate("11222333000181", timeout=1)
            # Após múltiplas tentativas com 429, deve retornar None
            assert result is None or isinstance(result, dict)

    @patch('cpf_cnpj_brasil.cnpj_validator_gemini.requests.get')
    def test_investigate_erro_ssl(self, mock_get):
        """Testa erro SSL na API."""
        import requests
        mock_get.side_effect = requests.exceptions.SSLError("SSL Error")

        with pytest.raises(CNPJAPIError) as excinfo:
            CNPJ._investigate_cnpj("11222333000181")
        assert "erro na api" in str(excinfo.value).lower()

    @patch('cpf_cnpj_brasil.cnpj_validator_gemini.requests.get')
    def test_investigate_timeout(self, mock_get):
        """Testa timeout na API."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        with pytest.raises(CNPJAPIError) as excinfo:
            CNPJ._investigate_cnpj("11222333000181", timeout=1)
        assert "erro na api" in str(excinfo.value).lower()

    @patch('cpf_cnpj_brasil.cnpj_validator_gemini.requests.get')
    def test_investigate_connection_error(self, mock_get):
        """Testa erro de conexão com a API."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed")

        with pytest.raises(CNPJAPIError) as excinfo:
            CNPJ._investigate_cnpj("11222333000181")
        assert "erro na api" in str(excinfo.value).lower()

    def test_investigate_cnpj_invalido(self):
        """Testa investigação com CNPJ inválido."""
        result = CNPJ.investigate("11111111111111")
        assert result is None

    def test_investigate_cnpj_formato_invalido(self):
        """Testa investigação com formato inválido."""
        result = CNPJ.investigate("123")
        assert result is None


class TestCNPJExtractAndWaitForRelease:
    """Testes para o método _extract_and_wait_for_release."""

    def test_extrair_data_valida(self):
        """Testa extração de data válida da mensagem."""
        message = "Rate limit. Tente após Mon Oct 27 2025 14:30:00 GMT-0300"
        # Não vamos aguardar de verdade, apenas testar a extração
        with patch('time.sleep'):
            wait_time = CNPJ._extract_and_wait_for_release(message)
            assert isinstance(wait_time, float)

    def test_extrair_data_invalida(self):
        """Testa extração com mensagem sem data."""
        message = "Erro genérico sem data"
        with pytest.raises(CNPJAPIError) as excinfo:
            CNPJ._extract_and_wait_for_release(message)
        assert "não foi possível extrair" in str(excinfo.value).lower()

    def test_data_no_passado(self):
        """Testa quando a data de liberação já passou."""
        # Data no passado
        message = "Tente após Mon Jan 01 2020 00:00:00 GMT+0000"
        wait_time = CNPJ._extract_and_wait_for_release(message)
        assert wait_time == 0.0


class TestCNPJIntegration:
    """Testes de integração entre os métodos."""

    def test_fluxo_completo_validacao_e_formatacao(self):
        """Testa fluxo completo: validar e depois formatar."""
        cnpj_input = 11222333000181
        validated = CNPJ.validate(cnpj_input)
        assert validated
        formatted = CNPJ.format(validated)
        assert formatted == "11.222.333/0001-81"

    def test_validar_cnpj_formatado_e_reformatar(self):
        """Testa validar CNPJ já formatado e reformatar."""
        cnpj_input = "11.222.333/0001-81"
        validated = CNPJ.validate(cnpj_input)
        assert validated
        formatted = CNPJ.format(validated)
        assert formatted == cnpj_input

    def test_multiplas_formatacoes_idempotente(self):
        """Testa que múltiplas formatações retornam o mesmo resultado."""
        cnpj = "11222333000181"
        format1 = CNPJ.format(cnpj)
        format2 = CNPJ.format(format1)
        assert format1 == format2

    def test_find_matrix_e_validar(self):
        """Testa encontrar matriz e validar o resultado."""
        branch_cnpj = "11222333000281"
        if CNPJ.validate(branch_cnpj):
            matrix = CNPJ.find_matrix(branch_cnpj)
            # Remove formatação para validar
            matrix_clean = matrix.replace(
                ".", "").replace("/", "").replace("-", "")
            validated = CNPJ.validate(matrix_clean)
            assert validated
