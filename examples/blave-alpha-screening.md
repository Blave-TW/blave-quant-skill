# Example: Blave Alpha Screening — Find High-Conviction Small-Cap Tokens

## Strategy

Screen for small-cap tokens where smart money is quietly accumulating:
- **Small cap** — market cap percentile ≤ 50 (bottom half of all listed coins)
- **High Holder Concentration** (籌碼集中) — alpha > 0.5, long side concentrated
- **High Whale Activity** (巨鯨警報) — 24h OI score > 0.5, large players moving in
- **Output** — top 10 ranked by combined signal strength

When both signals are high on a small-cap coin, it often means accumulation is happening before a sharp move. The coin may already be moving (+24h%) or still coiling — both are worth watching.

---

## Step 1: Pull Alpha Table

```
GET /alpha_table
```

One request covers all symbols. Each symbol contains all indicator values plus `statistics`.

---

## Step 2: Screen

```python
results = []

for symbol, d in alpha_table['data'].items():
    try:
        mc_pct  = float(d.get('market_cap_percentile', {}).get('-', ''))
        hc      = float(d.get('holder_concentration', {}).get('-', ''))
        wh_24h  = float(d.get('whale_hunter', {}).get('24h-score_oi', ''))
        stats   = d.get('statistics', {})
        mc_usd  = float(d.get('market_cap', {}).get('-', 0) or 0)
        up_prob = float(stats.get('up_prob', 0) or 0)
        exp_val = float(stats.get('exp_value', 0) or 0)

        if not stats.get('is_data_sufficient', False):
            continue

        # Filter
        if mc_pct <= 50 and hc > 0.5 and wh_24h > 0.5:
            results.append({
                'symbol':   symbol,
                'hc':       hc,
                'whale':    wh_24h,
                'mc_pct':   mc_pct,
                'mc_usd':   mc_usd,
                'up_prob':  up_prob,
                'exp_value': exp_val,
                'price_chg_24h': d.get('price_change', {}).get('24h', None),
            })
    except (ValueError, TypeError):
        continue

# Rank by combined signal strength
results.sort(key=lambda x: x['hc'] + x['whale'], reverse=True)
top10 = results[:10]
```

---

## Step 3: Output

Present as a ranked table:

| Rank | Symbol | HC | Whale | MC% | Market Cap | Up Prob | Exp Value | 24h Change |
|---|---|---|---|---|---|---|---|---|
| 1 | TRU | 8.16 | 14.66 | 7.4% | $8M | 2.2% | -3.78% | +72.0% |
| 2 | KOMA | 4.91 | 5.58 | 1.7% | $4M | 37.7% | -0.79% | +56.3% |
| 3 | HIPPO | 3.09 | 7.46 | 3.2% | $6M | 42.1% | -0.20% | -4.0% |

**Reading the results:**
- **Already moving** (large 24h change + strong signals) — accumulation phase may be ending, entering now is chasing
- **Not yet moved** (flat 24h + strong signals) — potential setup still coiling, higher risk/reward
- `up_prob` and `exp_value` from `statistics` give a historical base rate — use as context, not as a trigger

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

If you want to confirm buying pressure is actually present (not just silent accumulation):

```python
wh_vol = float(d.get('whale_hunter', {}).get('24h-score_volume', ''))
taker  = float(d.get('taker_intensity', {}).get('24h', ''))  # field name may vary

# Add to filter:
if taker > 0:  # net buying pressure
    ...
```

---

## Risk Notes

- Small-cap coins are illiquid — large slippage on entry/exit
- Strong signals on coins that already pumped 50%+ today = chasing; look at coins with signals but flat price instead
- Always check funding rate (`funding_rate` field in alpha_table) — high positive funding on a small cap = crowded long, squeeze risk
- Use position sizing accordingly: higher signal strength does not mean lower risk
