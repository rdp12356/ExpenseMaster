import os, requests, time
from dotenv import load_dotenv
load_dotenv()
API_BASE = os.getenv("RATES_API_BASE")

_cache = {"ts":0, "base":"USD", "rates":{}}

def rates(base="USD"):
    base = base.upper()
    now = time.time()
    if _cache["rates"] and _cache["base"] == base and (now - _cache["ts"]) < 3600:
        return _cache["rates"]
    r = requests.get(f"{API_BASE}/rates", params={"base": base}, timeout=15)
    r.raise_for_status()
    data = r.json()
    _cache.update({"ts": now, "base": base, "rates": data.get('rates',{})})
    return _cache["rates"]

def convert(amount, from_currency, to_currency):
    payload = {"amount": float(amount), "from_currency": from_currency.upper(), "to_currency": to_currency.upper()}
    r = requests.post(f"{API_BASE}/convert", json=payload, timeout=15)
    r.raise_for_status()
    return r.json()
