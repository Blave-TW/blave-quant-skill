# Example: Bitfinex Auto-Lending

Automatically lend idle funds on Bitfinex. Adapts to market conditions:
- **Period:** FRR high → allocate more to long periods (lock in). FRR low → stay short (flexibility)
- **Rate:** median to P75 ladder per period, floored by order book best bid
- **Large amounts:** split across multiple periods and rate levels for better fill

---

## Dependencies

```bash
pip install requests
```

---

## Code

```python
#!/usr/bin/env python3
"""
Bitfinex 自動放貸：
  - FRR 決定天期分配（高利率→長期為主，低利率→短期為主）
  - 大單拆成梯形掛單：多天期 × 多利率（median → P75）
  - 不低於 order book best bid

cron 每 15 分鐘執行一次
"""

import hmac, hashlib, json, time
from datetime import datetime, timezone
import requests

# ── Config ────────────────────────────────────────────────────────────────
BITFINEX_API_KEY    = "YOUR_API_KEY"
BITFINEX_API_SECRET = "YOUR_API_SECRET"
CURRENCY            = "UST"              # UST = USDT on Bitfinex
MIN_OFFER           = 150.0              # Bitfinex minimum: $150 equivalent
DEMAND_THRESHOLD    = 50_000             # book: require 50K+ cumulative bid depth
TRANCHES_PER_PERIOD = 3                  # rate levels per period (median → P75)

BASE_URL = "https://api.bitfinex.com"
PUB_URL  = "https://api-pub.bitfinex.com"

# FRR → period allocation weights
# High FRR: weight long (lock in). Low FRR: weight short (stay flexible).
PERIOD_WEIGHTS = {
    10.0: {2: 0.1, 30: 0.2, 120: 0.7},           # FRR ≥ 10%
    6.0:  {2: 0.2, 7: 0.2, 30: 0.3, 120: 0.3},   # FRR ≥ 6%
    3.0:  {2: 0.4, 7: 0.3, 30: 0.2, 120: 0.1},   # FRR ≥ 3%
    0.0:  {2: 0.7, 7: 0.2, 30: 0.1},              # FRR < 3%
}


# ── Auth ──────────────────────────────────────────────────────────────────
def bfx_request(path, body=None):
    body = body or {}
    nonce = str(int(time.time() * 1_000_000))
    body_json = json.dumps(body)
    sig = hmac.new(
        BITFINEX_API_SECRET.encode(),
        f"/api/{path}{nonce}{body_json}".encode(),
        hashlib.sha384,
    ).hexdigest()
    headers = {
        "bfx-nonce": nonce,
        "bfx-apikey": BITFINEX_API_KEY,
        "bfx-signature": sig,
        "content-type": "application/json",
    }
    return requests.post(f"{BASE_URL}/{path}", headers=headers,
                         data=body_json, timeout=15)


# ── Market Analysis ───────────────────────────────────────────────────────
def fetch_trades_3d(symbol="fUST"):
    """Fetch 3 days of funding trades with pagination."""
    end = int(time.time() * 1000)
    start = end - 3 * 24 * 60 * 60 * 1000
    all_trades = []
    cursor = end

    while cursor > start:
        r = requests.get(
            f"{PUB_URL}/v2/trades/{symbol}/hist",
            params={"limit": 10000, "start": start, "end": cursor, "sort": -1},
            timeout=15,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        all_trades.extend(batch)
        cursor = batch[-1][1] - 1
        time.sleep(0.5)

    seen = set()
    return [t for t in all_trades if t[0] not in seen and not seen.add(t[0])]


def analyze_rates(trades, period):
    """Compute rate statistics for a specific period."""
    rates = sorted([t[3] for t in trades if t[4] == period])
    if not rates:
        return None
    n = len(rates)
    return {
        "count":  n,
        "min":    rates[0],
        "max":    rates[-1],
        "median": rates[n // 2],
        "p75":    rates[3 * n // 4],
    }


def get_frr(symbol="fUST"):
    r = requests.get(f"{PUB_URL}/v2/ticker/{symbol}", timeout=10)
    r.raise_for_status()
    return r.json()[0]


def get_book_best_bid(symbol="fUST", demand_threshold=50_000):
    """Rate where cumulative borrower demand ≥ threshold."""
    r = requests.get(f"{PUB_URL}/v2/book/{symbol}/P0",
                     params={"len": 250}, timeout=10)
    r.raise_for_status()
    bids = sorted([e for e in r.json() if e[3] > 0], key=lambda x: -x[0])
    if not bids:
        return None, 0
    cumulative = 0
    for b in bids:
        cumulative += b[3]
        if cumulative >= demand_threshold:
            return b[0], cumulative
    return bids[-1][0], cumulative


def choose_weights(frr):
    """Pick period allocation weights based on FRR."""
    frr_ann = frr * 365 * 100
    for threshold in sorted(PERIOD_WEIGHTS.keys(), reverse=True):
        if frr_ann >= threshold:
            return PERIOD_WEIGHTS[threshold], threshold
    return PERIOD_WEIGHTS[0.0], 0.0


# ── Account ───────────────────────────────────────────────────────────────
def get_available_balance(currency="UST"):
    r = bfx_request("v2/auth/r/wallets")
    r.raise_for_status()
    for w in r.json():
        if w[0] == "funding" and w[1] == currency:
            return float(w[4] or w[2] or 0)
    return 0.0


def get_active_offers(symbol=None):
    path = f"v2/auth/r/funding/offers/{symbol}" if symbol else "v2/auth/r/funding/offers"
    r = bfx_request(path)
    r.raise_for_status()
    return r.json()


def get_active_credits(symbol=None):
    path = f"v2/auth/r/funding/credits/{symbol}" if symbol else "v2/auth/r/funding/credits"
    r = bfx_request(path)
    r.raise_for_status()
    return r.json()


# ── Execute ───────────────────────────────────────────────────────────────
def submit_offer(currency, amount, rate, period):
    body = {
        "type": "LIMIT",
        "symbol": f"f{currency}",
        "amount": str(round(amount, 8)),
        "rate": str(rate),
        "period": period,
    }
    r = bfx_request("v2/auth/w/funding/offer/submit", body)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and data[0] == "error":
        return False, data[2]
    status = data[6] if len(data) > 6 else ""
    return status == "SUCCESS", data


def cancel_offer(offer_id):
    r = bfx_request("v2/auth/w/funding/offer/cancel", {"id": offer_id})
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and data[0] == "error":
        return False, data[2]
    return True, data


# ── Build Ladder ──────────────────────────────────────────────────────────
def build_ladder(total_amount, weights, all_trades, book_rate, frr):
    """
    Build a list of (period, rate, amount) offers.
    Splits across periods by weight, then within each period
    spreads rates from median to P75 in TRANCHES_PER_PERIOD steps.
    All rates floored by book_rate.
    """
    ann = lambda r: f"{r * 365 * 100:.2f}%"
    offers = []

    for period, weight in weights.items():
        period_amount = total_amount * weight
        if period_amount < MIN_OFFER:
            continue

        stats = analyze_rates(all_trades, period)

        if not stats or stats["count"] < 5:
            # Thin market — single offer at max(FRR, book)
            rate = max(frr, book_rate) if book_rate else frr
            offers.append((period, rate, period_amount))
            continue

        median = stats["median"]
        p75 = stats["p75"]

        # How many tranches can we fit? (each ≥ MIN_OFFER)
        n = min(TRANCHES_PER_PERIOD, int(period_amount // MIN_OFFER))
        n = max(n, 1)
        tranche_amount = period_amount / n

        for i in range(n):
            # Linear interpolation: median → P75
            frac = i / (n - 1) if n > 1 else 0.5
            rate = median + frac * (p75 - median)
            # Floor: don't go below book best bid
            if book_rate:
                rate = max(rate, book_rate)
            offers.append((period, rate, tranche_amount))

    return offers


# ── Main ──────────────────────────────────────────────────────────────────
def run():
    symbol = f"f{CURRENCY}"
    ann = lambda r: f"{r * 365 * 100:.2f}%"

    # 1. FRR → allocation weights
    frr = get_frr(symbol)
    frr_ann = frr * 365 * 100
    weights, threshold = choose_weights(frr)
    print(f"FRR: {ann(frr)} (≥ {threshold}%)")
    print(f"Allocation: {', '.join(f'{p}d={w:.0%}' for p, w in weights.items())}")

    # 2. Fetch market data
    print(f"Fetching 3d trades...")
    trades = fetch_trades_3d(symbol)
    print(f"  {len(trades)} trades")

    book_rate, book_depth = get_book_best_bid(symbol, DEMAND_THRESHOLD)
    if book_rate:
        print(f"  Book bid (≥{DEMAND_THRESHOLD/1000:.0f}K): {ann(book_rate)} ({book_depth:,.0f} UST)")

    # 3. Check balance
    available = get_available_balance(CURRENCY)
    print(f"\nAvailable {CURRENCY}: {available:.2f}")

    if available < MIN_OFFER:
        print(f"Below minimum ({MIN_OFFER})")
        return

    # 4. Cancel all existing offers (rebuild ladder fresh each run)
    offers = get_active_offers(symbol)
    if offers:
        print(f"Cancelling {len(offers)} existing offers...")
        for o in offers:
            cancel_offer(o[0])
            available += abs(o[4])
            time.sleep(0.3)

    # 5. Build ladder
    ladder = build_ladder(available, weights, trades, book_rate, frr)

    if not ladder:
        print("No valid offers to submit")
        return

    # 6. Submit
    print(f"\n{'Period':>6} {'Rate':>10} {'Amount':>12}")
    print("-" * 32)
    submitted = 0
    for period, rate, amount in ladder:
        if amount < MIN_OFFER:
            continue
        print(f"{period:>4}d {ann(rate):>10} {amount:>11,.0f}", end="")
        ok, result = submit_offer(CURRENCY, amount, rate, period)
        if ok:
            offer = result[4][0] if isinstance(result[4][0], list) else result[4]
            print(f"  ✓ {offer[0]}")
            submitted += 1
        else:
            print(f"  ✗ {result}")
        time.sleep(0.3)

    print(f"\nSubmitted {submitted} offers")

    # 7. Summary
    credits = get_active_credits(symbol)
    if credits:
        total_lent = sum(abs(c[5]) for c in credits)
        rates = [c[11] for c in credits]
        periods = [c[12] for c in credits]
        print(f"Lent out: {total_lent:,.0f} {CURRENCY} in {len(credits)} credits")
        print(f"  Rates: {ann(min(rates))} — {ann(max(rates))}")
        print(f"  Periods: {min(periods)}d — {max(periods)}d")


if __name__ == "__main__":
    run()
```

---

## How the Ladder Works

### Period allocation (FRR decides)

| FRR | 2d | 7d | 30d | 120d |
|---|---|---|---|---|
| ≥ 10% | 10% | — | 20% | **70%** |
| 6–10% | 20% | 20% | 30% | 30% |
| 3–6% | **40%** | 30% | 20% | 10% |
| < 3% | **70%** | 20% | 10% | — |

### Rate ladder (per period)

Within each period, the amount is split into `TRANCHES_PER_PERIOD` (default 3) offers with rates linearly spaced from **median** to **P75** of 3-day historical trades:

```
Tranche 1: median         (most competitive, fills first)
Tranche 2: (median+P75)/2 (mid)
Tranche 3: P75            (highest rate, fills last)
```

**All rates floored by order book best bid** — never offer below what borrowers are already willing to pay.

### Example output (10,000 UST at FRR 8.87%)

```
FRR: 8.87% (≥ 6%)
Allocation: 2d=20%, 7d=20%, 30d=30%, 120d=30%

Period       Rate       Amount
--------------------------------
   2d      5.20%       667  ✓  (book floor)
   2d      5.20%       667  ✓  (book floor)
   2d      5.20%       667  ✓  (book floor)
   7d      5.20%       667  ✓  (book floor)
   7d      5.20%       667  ✓  (book floor)
   7d      5.20%       667  ✓  (book floor)
  30d      5.20%     1,000  ✓  (median, floored by book)
  30d      7.06%     1,000  ✓  (mid)
  30d      9.44%     1,000  ✓  (P75)
 120d      9.69%     1,000  ✓  (median)
 120d      9.84%     1,000  ✓  (mid)
 120d     10.00%     1,000  ✓  (P75)

Submitted 12 offers
```

Short periods (2d, 7d) hit the book floor so all tranches are at the same rate. Long periods (30d, 120d) have natural spread between median and P75.

---

## Small amounts (< $1,000)

If total amount is small, fewer tranches fit (each must be ≥ $150). The script automatically reduces tranches:
- $150–$449: 1 offer at best single period
- $450–$899: up to 3 offers
- $900+: full ladder

---

## Deployment

```bash
*/15 * * * * cd /path/to/project && python3 bitfinex_auto_lend.py >> /var/log/bfx_lend.log 2>&1
```

Each run:
1. FRR → pick period weights
2. Fetch 3d trades → rate stats per period
3. Fetch order book → floor rate
4. Cancel all existing offers (rebuild fresh)
5. Build ladder → submit offers
6. Report lent-out credits

---

## Customising

### More aggressive (lock long earlier)

```python
PERIOD_WEIGHTS = {
    8.0:  {2: 0.1, 30: 0.2, 120: 0.7},
    5.0:  {2: 0.2, 7: 0.2, 30: 0.3, 120: 0.3},
    2.0:  {2: 0.4, 7: 0.3, 30: 0.2, 120: 0.1},
    0.0:  {2: 0.7, 7: 0.2, 30: 0.1},
}
```

### More tranches (finer rate spread)

```python
TRANCHES_PER_PERIOD = 5   # 5 levels from median to P75
```

---

## Notes

- **Minimum offer:** $150 USD equivalent per tranche
- **Rebuild vs update:** each run cancels all offers and rebuilds. Simple and idempotent — no stale offer tracking needed
- **Book floor:** prevents offering below current borrower demand. Short periods often have their median below the book bid, so they get raised
- **Thin periods:** if a period has <5 trades in 3 days, a single offer at max(FRR, book) is used instead of a ladder
- **Amount sign:** positive = lend, negative = borrow
