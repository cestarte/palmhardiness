import unicodedata
from typing import Optional, Any

def clean(s:Any) -> Optional[str]:
    """Remove leading/trailing whitespace and normalize unicode characters."""
    if s is None or not isinstance(s, (str, int, float)):
        return None

    # the 2023 excel...
    #   * has some \xa0 (non-breaking space) characters where nulls are expected
    #   * has some ._x000D_ (carriage return) text where newlines are expected
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

def normalize_country(s:Optional[str]) -> Optional[str]:
    if s is None:
        return None

    s = remove_non_alpha(clean(s), keep_spaces=True)
    s = s.strip().lower()
    if s == 'usa' or s == 'us' or s == 'united states of america': 
        return 'United States'
    
    if len(s) <= 3:
        return s.upper()
    
    if s == 'unknown' or s == 'various':
        return None

    if (len(s) == 0):
        return None

    return s.title()

def normalize_state(s:Optional[str]) -> Optional[str]:
    if s is None:
        return None

    s = remove_non_alpha(clean(s), keep_spaces=True, keep_slashes=True)
    s = s.strip().lower()
    
    if len(s) <= 3 or  s.count('/') > 0:
        return s.upper()
    
    if s == 'unknown' or s == 'various':
        return None

    if (len(s) == 0):
        return None

    return s.title()


def normalize_city(s:Optional[str]) -> Optional[str]:
    if s is None:
        return None

    s = remove_non_alpha(clean(s), keep_spaces=True, keep_hyphens=True)
    s = s.strip().lower()

    if s == 'unknown' or s == 'unkown' or s == 'various' or s == 'multiple':
        return None

    if (len(s) == 0):
        return None

    return s.title()

def remove_non_alpha(s:str, keep_spaces:bool=False, keep_hyphens:bool=False, keep_slashes=True) -> str:
    if s is None:
        return ''
    return ''.join(i for i in s 
                if i.isalpha() or (
                    keep_spaces and i.isspace()
                    or (keep_hyphens and i == '-') 
                    or (keep_slashes and i == '/')
                    or (keep_slashes and i == '\\')
                )
            )

def remove_non_numeric(s:str) -> str:
    if s is None:
        return ''
    return ''.join(i for i in s if i.isnumeric())

def remove_symbols(s:str) -> str:
    if s is None:
        return ''
    return ''.join(i for i in s if i.isalnum())
