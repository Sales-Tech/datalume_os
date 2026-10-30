import re
from django.core.exceptions import ValidationError

def validate_cnpj(value):
    """
    Valida se o CNPJ inserido é matematicamente válido.
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', str(value))

    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        raise ValidationError("O CNPJ deve conter exatamente 14 dígitos.")

    # Elimina CNPJs inválidos conhecidos (ex: 11111111111111)
    if cnpj == cnpj[0] * len(cnpj):
        raise ValidationError("CNPJ inválido.")

    # --- CÁLCULO DOS DÍGITOS VERIFICADORES ---

    # Validação do primeiro dígito
    weight = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(cnpj[i]) * weight[i] for i in range(12))
    remainder = total % 11
    digit_1 = 0 if remainder < 2 else 11 - remainder

    if int(cnpj[12]) != digit_1:
        raise ValidationError("CNPJ inválido (Dígito verificador incorreto).")

    # Validação do segundo dígito
    weight = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(cnpj[i]) * weight[i] for i in range(13))
    remainder = total % 11
    digit_2 = 0 if remainder < 2 else 11 - remainder

    if int(cnpj[13]) != digit_2:
        raise ValidationError("CNPJ inválido (Dígito verificador incorreto).")

    return cnpj