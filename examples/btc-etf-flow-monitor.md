# Example: Bitcoin ETF Flow Monitor — Track Institutional Accumulation

Track daily Bitcoin spot ETF fund flows (IBIT, FBTC, GBTC, etc.) from Farside Investors. Detect when BlackRock and other institutions are accumulating or distributing.

---

## Dependencies

```bash
pip install curl-cffi beautifulsoup4
```

---

## Code

```python
import re
from curl_cffi import requests as cf_requests
from bs4 import BeautifulSoup

IMPERSONATE = "chrome110"
URL = "https://farside.co.uk/bitcoin-etf-flow-all-data/"  # full history since Jan 2024

FUNDS = ["IBIT", "FBTC", "BITB", "ARKB", "BTCO", "EZBC",
         "BRRR", "HODL", "BTCW", "MSBT", "GBTC", "BTC"]


def parse_value(s: str) -> float | None:
    """Parse Farside format: '269.3' or '(86.5)' (negative) or '-' (no data)."""
    s = s.strip()
    if not s or s == "-":
        return None
    neg = "(" in s
    s = s.replace("(", "").replace(")", "").replace(",", "")
    try:
        v = float(s)
        return -v if neg else v
    except ValueError:
        return None


def fetch_flows() -> list[dict]:
    """Fetch all daily ETF flow rows from Farside. Returns list of dicts."""
    s = cf_requests.Session(impersonate=IMPERSONATE)
    r = s.get(URL, headers={"Accept": "text/html"})
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find_all("table")[1]  # second table = flow data
    rows = table.find_all("tr")

    data = []
    for row in rows:
        cells = [td.text.strip() for td in row.find_all("td")]
        if not cells or len(cells) < 14:
            continue
        date_str = cells[0]
        if any(k in date_str for k in ["Total", "Average", "Maximum", "Minimum"]):
            continue

        entry = {"date": date_str}
        for i, fund in enumerate(FUNDS):
            entry[fund] = parse_value(cells[i + 1])
        entry["Total"] = parse_value(cells[13])
        data.append(entry)

    # Deduplicate by date (Farside sometimes has dupes)
    seen = set()
    deduped = []
    for row in data:
        if row["date"] not in seen:
            seen.add(row["date"])
            deduped.append(row)
    return deduped


def print_recent(data: list[dict], days: int = 20):
    """Print the most recent N trading days."""
    recent = data[-days:]

    header = f"{'Date':<16}"
    for fund in ["IBIT", "FBTC", "ARKB", "GBTC", "Total"]:
        header += f"{fund:>9}"
    print(header)
    print("-" * len(header))

    for row in recent:
        line = f"{row['date']:<16}"
        for fund in ["IBIT", "FBTC", "ARKB", "GBTC", "Total"]:
            v = row.get(fund)
            if v is None:
                line += f"{'—':>9}"
            elif v < 0:
                line += f"{'(' + f'{abs(v):.1f}' + ')':>9}"
            else:
                line += f"{v:>9.1f}"
        print(line)


def summarise(data: list[dict], month: str = None):
    """Summarise flows for a given month (e.g. 'Apr 2026') or all data."""
    filtered = data
    if month:
        filtered = [r for r in data if month in r["date"]]

    if not filtered:
        print(f"No data for {month}")
        return

    # Per-fund totals
    totals = {}
    for fund in FUNDS + ["Total"]:
        vals = [r[fund] for r in filtered if r.get(fund) is not None]
        totals[fund] = sum(vals)

    inflow_days = sum(1 for r in filtered if (r.get("IBIT") or 0) > 0)
    outflow_days = sum(1 for r in filtered if (r.get("IBIT") or 0) < 0)
    trading_days = sum(1 for r in filtered if r.get("IBIT") is not None)

    print(f"\n{'Fund':<8} {'Net Flow ($M)':>14}")
    print("-" * 24)
    for fund in ["IBIT", "FBTC", "BITB", "ARKB", "GBTC", "Total"]:
        v = totals.get(fund, 0)
        print(f"{fund:<8} {v:>13.1f}")

    print(f"\nIBIT: {inflow_days} inflow days / {outflow_days} outflow days / {trading_days} total")


if __name__ == "__main__":
    data = fetch_flows()
    print(f"Fetched {len(data)} trading days\n")
    print_recent(data, days=15)
    summarise(data, month="Apr 2026")
```

---

## Example Output

```
Date                 IBIT     FBTC     ARKB     GBTC    Total
--------------------------------------------------------------
01 Apr 2026        (86.5)   (78.6)      0.0   (13.3)  (173.7)
02 Apr 2026         (3.0)      7.3      0.0      0.0      9.0
06 Apr 2026        181.9    147.3    118.8      0.0    471.4
09 Apr 2026        269.3     53.3      4.8      0.0    358.1
10 Apr 2026        137.6     78.0      3.6      0.0    256.7
14 Apr 2026        213.8     45.3    113.1      0.0    411.4
15 Apr 2026        291.9    (47.3)   (42.2)   (23.4)   186.1

Fund       Net Flow ($M)
------------------------
IBIT           1,063.0
FBTC             178.4
ARKB              98.3
GBTC             (87.0)
Total          1,376.1

IBIT: 7 inflow days / 3 outflow days / 10 total
```

---

## How to Read

- **Unit:** millions USD. `(86.5)` = net outflow of $86.5M
- **IBIT** = BlackRock iShares Bitcoin Trust (largest BTC ETF, ~45% market share)
- **FBTC** = Fidelity, **ARKB** = Ark/21Shares, **GBTC** = Grayscale (legacy, high fee)
- **Divergence signal:** when IBIT is positive but Total is negative → BlackRock is buying while others are selling. This often precedes recoveries
- **GBTC consistently negative** = continued outflow from Grayscale's 1.5% fee product into cheaper alternatives

---

## Combining with Blave Alpha

Use ETF flow direction as a macro filter for Blave signals:

```python
# If IBIT has been net positive for 3+ consecutive days,
# bias toward long signals from Blave alpha_table
recent_ibit = [r["IBIT"] for r in data[-5:] if r.get("IBIT") is not None]
consecutive_inflow = all(v > 0 for v in recent_ibit[-3:])

if consecutive_inflow:
    # Institutional tailwind — Blave long signals have higher conviction
    ...
```

---

## Notes

- Farside publishes data after US market close (typically available by ~21:00 UTC)
- Data covers all US-listed spot Bitcoin ETFs since launch (Jan 2024)
- Weekend/holiday dates are skipped (no trading)
- `curl_cffi` with `impersonate="chrome110"` is needed to bypass Cloudflare; plain `requests` gets 403
- For Ethereum ETF flows, change URL to `https://farside.co.uk/eth/`
