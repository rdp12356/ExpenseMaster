import os
import time

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import BaseModel

load_dotenv()

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
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    _cache = {"ts": now, "base": base, "rates": data.get("rates", {})}
    return _cache["rates"]


def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/rates")
    def rates():
        base = request.args.get("base", "USD").upper()
        try:
            rates = fetch_rates(base)
            return jsonify({"base": base, "rates": rates})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.post("/convert")
    def convert():
        try:
            body = request.get_json(force=True) or {}
            q = ConvertQuery(**body)
            rates = fetch_rates(base=q.from_currency.upper())
            fx = float(rates[q.to_currency.upper()])
            return jsonify({"amount": q.amount * fx, "rate": fx})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    return app


app = create_app()
