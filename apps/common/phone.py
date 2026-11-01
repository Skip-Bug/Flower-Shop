import phonenumbers


def normalize_phone(raw, region="RU"):
    """Приводит номер к E164. Возвращает None, если номер невалиден."""
    try:
        parsed = phonenumbers.parse(raw or "", region)
    except phonenumbers.NumberParseException:
        return None
    if not phonenumbers.is_valid_number(parsed):
        return None
    if phonenumbers.region_code_for_number(parsed) != region:
        return None
    return phonenumbers.format_number(
        parsed,
        phonenumbers.PhoneNumberFormat.E164,
    )


def format_phone_national(raw, region="RU"):
    """Показывает номер в национальном формате, например 8 (911) 174-44-60."""
    normalized = normalize_phone(raw, region)
    if normalized is None:
        return raw or ""
    parsed = phonenumbers.parse(normalized, region)
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
