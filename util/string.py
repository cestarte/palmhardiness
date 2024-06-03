import unicodedata

def clean(s:str) -> str | None:
    """Remove leading/trailing whitespace and normalize unicode characters."""
    # the 2023 excel...
    #   * has some \xa0 (non-breaking space) characters where nulls are expected
    #   * has some ._x000D_ (carriage return) text where newlines are expected
    if s is None:
        return None
    
    normalized =  unicodedata.normalize('NFKD', s).strip()
    normalized = normalized.replace("""_x000D_
_________.""", '\n')
    normalized = normalized.replace('_x000D_', '\n')

    if normalized == "":
        return None
    else:
        return normalized
