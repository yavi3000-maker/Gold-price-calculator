#!/usr/bin/env python3
"""Runs on GitHub Actions. Fetches the PAXG price (1 PAXG = 1 troy oz gold) and writes price.json.
If every source fails, it exits with an error and leaves the existing price.json untouched.
Standard library only.
"""
import json
import sys
import time
import urllib.request

SOURCES = [
    ("CoinGecko", "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd",
     lambda d: d["pax-gold"]["usd"]),
    ("Binance", "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT",
     lambda d: float(d["price"])),
    ("Kraken", "https://api.kraken.com/0/public/Ticker?pair=PAXGUSD",
     lambda d: float(next(iter(d["result"].values()))["c"][0])),
    ("Crypto.com", "https://api.crypto.com/exchange/v1/public/get-tickers?instrument_name=PAXG_USD",
     lambda d: float(d["result"]["data"][0]["a"])),
]


def main():
    errors = []
    for name, url, parse in SOURCES:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "gold-calc/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                price = float(parse(json.loads(resp.read().decode("utf-8"))))
            if not price or price <= 0:
                raise ValueError("no usable price")
            out = {
                "price": round(price, 2),
                "source": name,
                "updated_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            }
            with open("price.json", "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2)
                f.write("\n")
            print(f"Wrote price.json: {out}")
            return 0
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    print("All sources failed:", *errors, sep="\n  ")
    return 1


if __name__ == "__main__":
    sys.exit(main())
