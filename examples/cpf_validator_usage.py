"""Exemplos básicos de uso da classe CPFValidator."""
from cpf_cnpj_brasil.cpf_validator import CPFValidator


def main() -> None:
    """Executa exemplos simples de validação e formatação de CPF."""
    validator = CPFValidator()

    raw_cpf = "39053344705"
    formatted_cpf = CPFValidator.format_cpf(raw_cpf)
    print(f"CPF formatado: {formatted_cpf}")

    is_valid = validator.validate_cpf(raw_cpf)
    print(f"CPF {formatted_cpf} é válido? {is_valid}")

    invalid_cpf = "111.111.111-11"
    print(f"CPF {invalid_cpf} é válido? {validator.validate_cpf(invalid_cpf)}")


if __name__ == "__main__":
    main()
