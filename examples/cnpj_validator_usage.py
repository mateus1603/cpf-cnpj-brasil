"""Exemplos de uso da classe CNPJValidator."""
from cpf_cnpj_brasil.cnpj_validator import CNPJValidator


def main() -> None:
    """Mostra operações comuns de validação, formatação e consulta de CNPJ."""
    validator = CNPJValidator()

    raw_cnpj = "04252011000110"
    formatted_cnpj = CNPJValidator.format_cnpj(raw_cnpj)
    print(f"CNPJ formatado: {formatted_cnpj}")

    is_valid = validator.validate_cnpj(raw_cnpj)
    print(f"CNPJ {formatted_cnpj} é válido? {is_valid}")

    headquarters = validator.find_headquarters("04.252.011/0002-00")
    print(f"Matriz encontrada: {headquarters}")

    try:
        investigation = validator.investigate(raw_cnpj, timeout=5)
        if investigation:
            print("Resumo da consulta:")
            print(f"Razão social: {investigation.get('razao_social')}")
            print(
                f"Situação: {investigation.get('descricao_situacao_cadastral')}")
        else:
            print("Nenhum dado retornado pela API para o CNPJ informado.")
    except ValueError as exc:
        print(f"Entrada inválida: {exc}")


if __name__ == "__main__":
    main()
