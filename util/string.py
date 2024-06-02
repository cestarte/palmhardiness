import unicodedata

def clean(s:str) -> str | None:
    """Remove leading/trailing whitespace and normalize unicode characters."""
    # the 2023 excel has some \xa0 (non-breaking space) characters where nulls are expected
    if s is None:
        return None
    
    normalized =  unicodedata.normalize('NFKD', s).strip()
    if normalized == "":
        return None
    else:
        return normalized
