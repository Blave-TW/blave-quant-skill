# Example: Blave Alpha Screening — Find High-Conviction Small-Cap Tokens

## Strategy

Screen for small-cap tokens where smart money is quietly accumulating:
- **Small cap** — market cap percentile ≤ 50 (bottom half of all listed coins)
- **High Holder Concentration** (籌碼集中) — alpha > 0.5, long side concentrated
- **High Whale Activity** (巨鯨警報) — 24h OI score > 0.5, large players moving in
- **Output** — top 10 ranked by combined signal strength

When both signals are high on a small-cap coin, it often means accumulation is happening before a sharp move. The coin may already be moving (+24h%) or still coiling — both are worth watching.

---

## Complete Script

Copy and run this directly — no modifications needed if `.env` has `blave_api_key` and `blave_secret_key`.

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {
    "api-key": os.getenv("blave_api_key"),
    "secret-key": os.getenv("blave_secret_key"),
}
BASE_URL = "https://api.blave.org"

# Fetch all symbols at once
resp = requests.get(f"{BASE_URL}/alpha_table", headers=headers, timeout=60)
resp.raise_for_status()
alpha_table = resp.json()

results = []
for symbol, d in alpha_table['data'].items():
    try:
        mc_pct = float(d.get('market_cap_percentile', {}).get('-', '') or '')
        hc     = float(d.get('holder_concentration', {}).get('-', '') or '')
        wh_24h = float(d.get('whale_hunter', {}).get('24h-score_oi', '') or '')
        stats  = d.get('statistics', {})
        mc_usd = float(d.get('market_cap', {}).get('-', 0) or 0)
        up_prob = float(stats.get('up_prob', 0) or 0)
        exp_val = float(stats.get('exp_value', 0) or 0)
        sufficient = stats.get('is_data_sufficient', False)

        if mc_pct <= 50 and hc > 0.5 and wh_24h > 0.5:
            results.append({
                'symbol':     symbol,
                'hc':         hc,
                'whale':      wh_24h,
                'mc_pct':     mc_pct,
                'mc_usd':     mc_usd,
                'up_prob':    up_prob,
                'exp_value':  exp_val,
                'sufficient': sufficient,
                'price_chg_24h': d.get('price_change', {}).get('24h', None),
            })
    except (ValueError, TypeError):
        continue

results.sort(key=lambda x: x['hc'] + x['whale'], reverse=True)
top10 = results[:10]

print(f"Matched {len(results)} coins (showing top {len(top10)})\n")
print(f"{'#':<3} {'Symbol':<10} {'HC':>5} {'Whale':>6} {'MC%':>4} {'24h':>7} {'✓':>2}")
print("-" * 44)
for i, r in enumerate(top10, 1):
    chg = f"{r['price_chg_24h']:+.1f}%" if r['price_chg_24h'] is not None else "  N/A"
    ok  = "✓" if r['sufficient'] else "~"
    print(f"{i:<3} {r['symbol']:<10} {r['hc']:>5.2f} {r['whale']:>6.2f} {r['mc_pct']:>3.0f}% {chg:>7} {ok:>2}")

print("\n✓ = is_data_sufficient (statistics reliable)  ~ = insufficient history")
```

> **Note on `is_data_sufficient`:** coins marked `~` have less history but the HC/Whale signals are still valid. Only `up_prob`/`exp_value` stats are less reliable for those coins.

---

## Reading the Results

- **Already moving** (large 24h change + strong signals) — accumulation phase may be ending, entering now is chasing
- **Not yet moved** (flat 24h + strong signals) — potential setup still coiling, higher risk/reward
- `up_prob` and `exp_value` give a historical base rate — context only, not a trigger

---

## Alpha Scale Reference

| Alpha Value | Holder Concentration | Whale Hunter |
|---|---|---|
| > 3 | Over Concentrated (long) | Overly Bullish |
| 2 – 3 | Highly Concentrated (long) | Highly Bullish |
| 0.5 – 2 | Concentrated (long) | Bullish |
| -0.5 – 0.5 | Neutral | Neutral |
| < -0.5 | Concentrated (short) | Bearish |

---

## Optional: Add Taker Intensity for Confirmation

Confirm buying pressure is actually present (not just silent accumulation). Add inside the loop, after extracting `hc` and `wh_24h`:

```python
taker = float(d.get('taker_intensity', {}).get('24h', '') or '')

# Tighten filter to require net buying:
if mc_pct <= 50 and hc > 0.5 and wh_24h > 0.5 and taker > 0:
    ...
```

---

## Risk Notes

- Small-cap coins are illiquid — large slippage on entry/exit
- Strong signals on coins that already pumped 50%+ today = chasing; look for flat price with strong signals
- Check funding rate (`funding_rate` field in alpha_table) — high positive funding on a small cap = crowded long, squeeze risk
- Use position sizing accordingly: higher signal strength does not mean lower risk
