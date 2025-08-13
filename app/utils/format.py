from babel.numbers import format_currency

def money(amount: float, currency: str, locale: str):
    try:
        return format_currency(amount, currency, locale=locale)
    except Exception:
        return f"{currency} {amount:,.2f}"
