from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CSV = ROOT / "data" / "monthly_payments.csv"
API = "https://data-api.dbie.rbihub.in/api/tables/financial_sector/r612_payment_system_indicators/rows?limit=500&offset=0"


def number(value):
    if value is None:
        return None
    cleaned = str(value).strip().replace(",", "")
    if not cleaned or cleaned in {"-", "—", "–"}:
        return None
    return float(cleaned)


def main():
    with urlopen(API, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    RAW.mkdir(parents=True, exist_ok=True)
    captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (RAW / "rbi_payment_system_indicators.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = payload.get("rows", [])
    headers = next((r for r in rows if str(r[1]).strip() == "New Format" and r[3] == 6), None)
    if headers is None:
        raise RuntimeError("Could not locate the RBI DBIE New Format header row.")

    def find_header(needle):
        return next((i for i, value in enumerate(headers) if needle.casefold() in str(value).casefold()), None)

    upi = find_header("2.7 UPI")
    credit = find_header("4.1 Credit Cards")
    debit = find_header("4.2 Debit Cards")
    if None in (upi, credit, debit):
        raise RuntimeError("Expected UPI, credit-card, and debit-card columns were not found in the DBIE table.")
    normalized = []
    for row in rows:
        if str(row[1]).strip() != "New Format" or row[3] < 8:
            continue
        month = str(row[4]).strip()
        if not month or "-" not in month:
            continue
        try:
            date = pd.to_datetime(month, format="%b-%Y")
        except ValueError:
            continue
        normalized.append({
            "month": date.strftime("%Y-%m-01"),
            "upi_volume_lakh": number(row[upi]), "upi_value_crore": number(row[upi + 1]),
            "credit_card_volume_lakh": number(row[credit]), "credit_card_value_crore": number(row[credit + 1]),
            "debit_card_volume_lakh": number(row[debit]), "debit_card_value_crore": number(row[debit + 1]),
            "source_table": payload.get("table", "financial_sector.r612_payment_system_indicators"),
            "retrieved_at_utc": captured,
        })
    if not normalized:
        raise RuntimeError("No monthly observations were extracted from the DBIE response.")
    result = pd.DataFrame(normalized).drop_duplicates("month", keep="last").sort_values("month")
    result.to_csv(CSV, index=False)
    print(f"Saved {len(result):,} monthly rows ({result.month.min()} to {result.month.max()}) to {CSV}.")


if __name__ == "__main__":
    main()
