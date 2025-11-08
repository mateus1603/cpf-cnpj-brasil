"""Testes unitários para o módulo CPF."""

import pytest
from cpf_cnpj_brasil.cpf_validator_gemini import CPF
from cpf_cnpj_brasil.exceptions import CPFValidationError


class TestCPFValidateInputFormat:
    """Testes para o método _validate_input_format."""

    def test_cpf_string_valido_com_formatacao(self):
        """Testa CPF string válido com formatação."""
        result = CPF._validate_input_format("123.456.789-09")
        assert result == "12345678909"

    def test_cpf_string_valido_sem_formatacao(self):
        """Testa CPF string válido sem formatação."""
        result = CPF._validate_input_format("12345678909")
        assert result == "12345678909"

    def test_cpf_inteiro_valido(self):
        """Testa CPF como inteiro válido."""
        result = CPF._validate_input_format(12345678909)
        assert result == "12345678909"

    def test_cpf_inteiro_com_zeros_a_esquerda(self):
        """Testa CPF inteiro que precisa de zeros à esquerda."""
        result = CPF._validate_input_format(1234567890)
        assert result == "01234567890"

    def test_cpf_string_com_menos_de_11_digitos(self):
        """Testa CPF string com menos de 11 dígitos."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._validate_input_format("123456789")
        assert "formato inválido" in str(excinfo.value).lower()

    def test_cpf_string_com_mais_de_11_digitos(self):
        """Testa CPF string com mais de 11 dígitos."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._validate_input_format("123456789012")
        assert "formato inválido" in str(excinfo.value).lower()

    def test_cpf_inteiro_com_mais_de_11_digitos(self):
        """Testa CPF inteiro com mais de 11 dígitos."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._validate_input_format(123456789012)
        assert "formato inválido" in str(excinfo.value).lower()

    def test_cpf_com_letras(self):
        """Testa CPF com caracteres não numéricos."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._validate_input_format("12345678ABC")
        assert "formato inválido" in str(excinfo.value).lower()

    def test_cpf_tipo_invalido(self):
        """Testa CPF com tipo inválido (não string nem inteiro)."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._validate_input_format(12.345)
        assert "string ou inteiro" in str(excinfo.value).lower()

    def test_cpf_none(self):
        """Testa CPF None."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._validate_input_format(None)
        assert "string ou inteiro" in str(excinfo.value).lower()

    def test_cpf_lista(self):
        """Testa CPF como lista."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._validate_input_format([1, 2, 3])
        assert "string ou inteiro" in str(excinfo.value).lower()


class TestCPFCalculateDigit:
    """Testes para o método _calculate_digit."""

    def test_calculo_primeiro_digito(self):
        """Testa cálculo do primeiro dígito verificador."""
        result = CPF._calculate_digit("123456789")
        assert isinstance(result, int)
        assert 0 <= result <= 9

    def test_calculo_segundo_digito(self):
        """Testa cálculo do segundo dígito verificador."""
        result = CPF._calculate_digit("1234567890")
        assert isinstance(result, int)
        assert 0 <= result <= 9

    def test_cpf_parcial_com_8_digitos(self):
        """Testa CPF parcial com 8 dígitos (inválido)."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._calculate_digit("12345678")
        assert "9 ou 10 dígitos" in str(excinfo.value).lower()

    def test_cpf_parcial_com_11_digitos(self):
        """Testa CPF parcial com 11 dígitos (inválido)."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._calculate_digit("12345678901")
        assert "9 ou 10 dígitos" in str(excinfo.value).lower()

    def test_cpf_parcial_vazio(self):
        """Testa CPF parcial vazio."""
        with pytest.raises(CPFValidationError) as excinfo:
            CPF._calculate_digit("")
        assert "9 ou 10 dígitos" in str(excinfo.value).lower()

    def test_digito_quando_resto_menor_que_2(self):
        """Testa caso onde o resto é menor que 2 (dígito = 0)."""
        # CPF que gera resto < 2: precisamos encontrar um exemplo
        result = CPF._calculate_digit("000000006")
        assert result == 0


class TestCPFFormat:
    """Testes para o método format."""

    def test_formatar_cpf_string_sem_formatacao(self):
        """Testa formatação de CPF string sem formatação."""
        result = CPF.format("12345678909")
        assert result == "123.456.789-09"

    def test_formatar_cpf_inteiro(self):
        """Testa formatação de CPF inteiro."""
        result = CPF.format(12345678909)
        assert result == "123.456.789-09"

    def test_formatar_cpf_com_zeros_a_esquerda(self):
        """Testa formatação de CPF com zeros à esquerda."""
        result = CPF.format(1234567890)
        assert result == "012.345.678-90"

    def test_formatar_cpf_ja_formatado(self):
        """Testa formatação de CPF já formatado."""
        result = CPF.format("123.456.789-09")
        assert result == "123.456.789-09"

    def test_formatar_cpf_invalido(self):
        """Testa formatação de CPF inválido."""
        with pytest.raises(CPFValidationError):
            CPF.format("123")


class TestCPFValidate:
    """Testes para o método validate."""

    # CPFs válidos conhecidos
    def test_validar_cpf_valido_11144477735(self):
        """Testa CPF válido conhecido."""
        result = CPF.validate("111.444.777-35")
        assert result == "11144477735"

    def test_validar_cpf_valido_52998224725(self):
        """Testa outro CPF válido conhecido."""
        result = CPF.validate(52998224725)
        assert result == "52998224725"

    def test_validar_cpf_valido_inteiro(self):
        """Testa CPF válido como inteiro."""
        result = CPF.validate(11144477735)
        assert result == "11144477735"

    def test_validar_cpf_valido_string_formatada(self):
        """Testa CPF válido como string formatada."""
        result = CPF.validate("111.444.777-35")
        assert result == "11144477735"

    def test_validar_cpf_valido_string_sem_formatacao(self):
        """Testa CPF válido como string sem formatação."""
        result = CPF.validate("11144477735")
        assert result == "11144477735"

    # CPFs com todos os dígitos iguais (inválidos)
    def test_validar_cpf_todos_digitos_iguais_00000000000(self):
        """Testa CPF com todos os dígitos iguais (00000000000)."""
        result = CPF.validate("00000000000")
        assert result is False

    def test_validar_cpf_todos_digitos_iguais_11111111111(self):
        """Testa CPF com todos os dígitos iguais (11111111111)."""
        result = CPF.validate("11111111111")
        assert result is False

    def test_validar_cpf_todos_digitos_iguais_99999999999(self):
        """Testa CPF com todos os dígitos iguais (99999999999)."""
        result = CPF.validate("99999999999")
        assert result is False

    # CPFs com dígitos verificadores incorretos
    def test_validar_cpf_digitos_verificadores_incorretos(self):
        """Testa CPF com dígitos verificadores incorretos."""
        result = CPF.validate("11144477736")  # Último dígito errado
        assert result is False

    def test_validar_cpf_primeiro_digito_incorreto(self):
        """Testa CPF com primeiro dígito verificador incorreto."""
        result = CPF.validate("11144477745")  # Penúltimo dígito errado
        assert result is False

    # CPFs com formato inválido
    def test_validar_cpf_formato_invalido_curto(self):
        """Testa CPF muito curto."""
        result = CPF.validate("123456789")
        assert result is False

    def test_validar_cpf_formato_invalido_longo(self):
        """Testa CPF muito longo."""
        result = CPF.validate("123456789012")
        assert result is False

    def test_validar_cpf_com_letras(self):
        """Testa CPF com letras."""
        result = CPF.validate("1234567890A")
        assert result is False

    def test_validar_cpf_vazio(self):
        """Testa CPF vazio."""
        result = CPF.validate("")
        assert result is False

    def test_validar_cpf_tipo_invalido_float(self):
        """Testa CPF com tipo float."""
        result = CPF.validate(111.444)
        assert result is False

    def test_validar_cpf_tipo_invalido_none(self):
        """Testa CPF None."""
        result = CPF.validate(None)
        assert result is False

    def test_validar_cpf_inteiro_negativo(self):
        """Testa CPF inteiro negativo."""
        result = CPF.validate(-11144477735)
        assert result is False

    # Casos limites
    def test_validar_cpf_com_zeros_a_esquerda(self):
        """Testa CPF válido com zeros à esquerda."""
        # CPF 000.000.001-91 é válido
        result = CPF.validate("00000000191")
        assert result == "00000000191"

    def test_validar_cpf_apenas_espacos(self):
        """Testa CPF com apenas espaços."""
        result = CPF.validate("           ")
        assert result is False

    def test_validar_cpf_com_caracteres_especiais(self):
        """Testa CPF com caracteres especiais além da formatação padrão."""
        result = CPF.validate("111@444#777-35")
        assert result is False


class TestCPFIntegration:
    """Testes de integração entre os métodos."""

    def test_fluxo_completo_validacao_e_formatacao(self):
        """Testa fluxo completo: validar e depois formatar."""
        cpf_input = 11144477735
        validated = CPF.validate(cpf_input)
        assert validated
        formatted = CPF.format(validated)
        assert formatted == "111.444.777-35"

    def test_validar_cpf_formatado_e_reformatar(self):
        """Testa validar CPF já formatado e reformatar."""
        cpf_input = "111.444.777-35"
        validated = CPF.validate(cpf_input)
        assert validated
        formatted = CPF.format(validated)
        assert formatted == cpf_input

    def test_multiplas_formatacoes_idempotente(self):
        """Testa que múltiplas formatações retornam o mesmo resultado."""
        cpf = "11144477735"
        format1 = CPF.format(cpf)
        format2 = CPF.format(format1)
        assert format1 == format2
