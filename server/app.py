from flask import Flask, jsonify, request
from flask_cors import CORS
import os, time, requests
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("CURRENCYFREAKS_API_KEY")
TTL = int(os.getenv("CACHE_TTL_SECONDS", "7200"))

_cache = {"ts": 0, "base": "USD", "rates": {}}

class ConvertQuery(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

def fetch_rates(base="USD"):
    global _cache
    now = time.time()
    if (now - _cache["ts"]) < TTL and _cache["base"] == base and _cache["rates"]:
        return _cache["rates"]
    url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={API_KEY}&base={base}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    _cache = {"ts": now, "base": base, "rates": data.get("rates", {})}
    return _cache["rates"]

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/rates")
def rates():
    base = request.args.get("base", "USD").upper()
    try:
        rates = fetch_rates(base)
        return jsonify({"base": base, "rates": rates})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/convert")
def convert():
    try:
        body = request.get_json(force=True) or {}
        q = ConvertQuery(**body)
        rates = fetch_rates(base=q.from_currency.upper())
        fx = float(rates[q.to_currency.upper()])
        return jsonify({"amount": q.amount * fx, "rate": fx})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", "8080")), host="0.0.0.0")
