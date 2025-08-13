from babel.core import Locale
from babel.numbers import get_currency_name
from .currency_codes import CURRENCY_CODES

def localized_currency_list(locale: str):
    loc = (locale or 'en').split('-')[0]
    items = []
    for code in CURRENCY_CODES:
        try:
            name = get_currency_name(code, locale=loc)
        except Exception:
            name = code
        items.append((code, name))
    items.sort(key=lambda x: x[1].lower())
    return items
