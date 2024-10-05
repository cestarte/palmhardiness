import unicodedata
from typing import Optional

def clean(s:str) -> Optional[str]:
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

def remove_underscore(s:str) -> str:
    return s.replace('_', ' ')

def normalize_country(value:str) -> Optional[str]:
    value = remove_non_alpha(clean(value), keep_spaces=True)
    value = value.strip().lower()
    if value == 'usa' or value == 'us' or value == 'united states of america': 
        return 'United States'
    
    if len(value) <= 3:
        return value.upper()
    
    if value == 'unknown' or value == 'various':
        return None

    return value.title()

def normalize_state(value:str) -> Optional[str]:
    value = remove_non_alpha(clean(value), keep_spaces=True)
    value = value.strip().lower()
    
    if len(value) <= 3:
        return value.upper()
    
    if value == 'unknown' or value == 'various':
        return None

    return value.title()


def normalize_city(value:str) -> Optional[str]:
    value = remove_non_alpha(clean(value), keep_spaces=True, keep_hyphens=True)
    value = value.strip().lower()

    if value == 'unknown' or value == 'various' or value == 'multiple':
        return None

    return value.title()

def remove_non_alpha(s:str, keep_spaces:bool=False, keep_hyphens:bool=False) -> str:
    if s is None:
        return ''
    return ''.join(i for i in s if i.isalpha() or (keep_spaces and i.isspace() or (keep_hyphens and i == '-')))

def remove_non_numeric(s:str) -> str:
    if s is None:
        return ''
    return ''.join(i for i in s if i.isnumeric())

def remove_symbols(s:str) -> str:
    if s is None:
        return ''
    return ''.join(i for i in s if i.isalnum())
