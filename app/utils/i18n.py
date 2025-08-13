import json, os
from functools import lru_cache

LOCALES_DIR = os.path.join(os.path.dirname(__file__), "..", "i18n")

@lru_cache
def load_locale(locale: str):
    path = os.path.join(LOCALES_DIR, f"{locale}.json")
    if not os.path.exists(path):
        path = os.path.join(LOCALES_DIR, "en.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def t(locale: str, key: str, **kwargs):
    data = load_locale(locale)
    text = data.get(key, key)
    return text.format(**kwargs)
