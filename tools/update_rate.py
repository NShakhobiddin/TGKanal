# -*- coding: utf-8 -*-
"""Markaziy bank (cbu.uz) kursini oladi va state/rate.json ga yozadi.

    python tools/update_rate.py            # USD
    CBU_API_BASE=http://127.0.0.1:8905 python tools/update_rate.py   # lokal sinov

GitHub Actions (rate.yml) 6 soatda bir ishga tushiradi — «Pochtam» ilovasidagi kabi
cbu.uz ochiq ma'lumotlaridan. Faqat standart kutubxona.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "state" / "rate.json"
BASE = os.environ.get("CBU_API_BASE", "https://cbu.uz")
URL = f"{BASE}/uz/arkhiv-kursov-valyut/json/USD/"
TASHKENT = timezone(timedelta(hours=5))


def fetch() -> dict:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (TGKanal kurs)"})
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
            row = data[0] if isinstance(data, list) else data
            if row.get("Ccy") != "USD":
                raise ValueError(f"kutilmagan valyuta: {row.get('Ccy')}")
            rate = float(row["Rate"]) / float(row.get("Nominal") or 1)
            if not 5000 < rate < 50000:
                raise ValueError(f"kurs g'alati: {rate}")
            return {"usd": round(rate, 2), "date": row["Date"], "source": "cbu.uz"}
        except Exception as e:  # tarmoq yoki format xatosi — qayta urinish
            last = e
    raise SystemExit(f"Kursni olib bo'lmadi: {last}")


def main() -> int:
    new = fetch()
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    if old.get("usd") == new["usd"] and old.get("date") == new["date"]:
        print(f"Kurs o'zgarmagan: 1 $ = {new['usd']} so'm ({new['date']})")
        return 0
    new["updated_at"] = datetime.now(TASHKENT).isoformat(timespec="seconds")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Kurs yangilandi: 1 $ = {new['usd']} so'm ({new['date']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
