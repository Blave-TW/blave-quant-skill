# Example: Hyperliquid Copy Trading — Find High-Sharpe Traders to Follow

## Strategy

Find Hyperliquid traders suitable for copy trading based on:
- **Sharpe ratio ≥ 1.5** — consistent risk-adjusted returns
- **≥ 90 days of performance data** — enough sample to rule out luck
- **Account value ≥ $100K** — meaningful track record
- **Exclude high-frequency / bots** — weekly turnover ratio ≤ 10x (weekly volume / account value)
- **Copy method** — proportional full position copy (if trader allocates 10% to BTC long, you allocate 10% of your capital too)

---

## Step 1: Get Leaderboard

```
GET /hyperliquid/leaderboard?sort_by=allTime
```

Returns top 100 traders. Each entry includes `ethAddress`, `accountValue`, `windowPerformances` (day / week / month / allTime PnL, ROI, volume).

**Pre-filter in one pass:**

```python
candidates = []
for trader in leaderboard:
    av = float(trader['accountValue'])
    if av < 100_000:
        continue

    windows = dict(trader['windowPerformances'])
    all_time_pnl = float(windows.get('allTime', {}).get('pnl', 0))
    if all_time_pnl <= 0:
        continue

    # Turnover ratio: weekly volume / account value
    week_vol = float(windows.get('week', {}).get('vlm', 0))
    turnover = week_vol / av
    if turnover > 10:
        continue  # likely bot or high-frequency

    candidates.append({
        'address': trader['ethAddress'],
        'displayName': trader.get('displayName'),
        'accountValue': av,
        'allTimePnl': all_time_pnl,
        'turnover': turnover,
        'month_pnl': float(windows.get('month', {}).get('pnl', 0)),
        'week_pnl': float(windows.get('week', {}).get('pnl', 0)),
    })
```

---

## Step 2: Compute Sharpe Ratio

For each candidate, fetch the PnL curve:

```
GET /hyperliquid/trader_performance?address=<ethAddress>
```

Returns `{chart: {timestamp: [...], pnl: [...]}}` — cumulative PnL over time.

```python
import numpy as np

pnl_arr = np.array(chart['pnl'], dtype=float)
timestamps = np.array(chart['timestamp'], dtype=float)

# Require at least 90 data points
if len(pnl_arr) < 90:
    continue

# Daily returns
daily_returns = np.diff(pnl_arr)
if daily_returns.std() == 0:
    continue

# Annualized Sharpe
sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(365)
if sharpe < 1.5:
    continue

# Max drawdown (absolute USD, from running peak)
peak = np.maximum.accumulate(pnl_arr)
max_dd_usd = (pnl_arr - peak).min()

# Win rate
win_rate = (daily_returns > 0).mean()
```

**Final filter:** keep only traders where both `month_pnl > 0` and `week_pnl > 0` — confirms recent consistency, not just historical glory.

---

## Step 3: Rank and Select

Sort passing traders by Sharpe ratio (descending). Present as a table:

| Rank | Name / Address | Sharpe | Win Rate | Max DD (USD) | Turnover | Month PnL | Account |
|---|---|---|---|---|---|---|---|
| 1 | ... | 4.8 | 58.7% | -$6.7M | 0.1x | +$7.3M | $41M |
| 2 | ... | 3.1 | 59.0% | -$24.6M | 3.9x | +$1.6M | $20M |

Select the **top 1–3** for deeper inspection.

---

## Step 4: Inspect Current Positions

```
GET /hyperliquid/trader_position?address=<ethAddress>
```

Returns:
- `perp.assetPositions` — open perpetual positions
- `net_equity` — total account value (USD)

```python
for pos in perp['assetPositions']:
    p = pos['position']
    szi = float(p['szi'])
    if szi == 0:
        continue
    direction = 'LONG' if szi > 0 else 'SHORT'
    size_usd = abs(szi) * float(p.get('entryPx', 0))
    allocation_pct = size_usd / net_equity  # trader's allocation %

    # Your position size = allocation_pct × your_capital
    your_size_usd = allocation_pct * YOUR_CAPITAL

    print(f"{p['coin']} {direction} | Trader: ${size_usd:,.0f} ({allocation_pct*100:.1f}%) | You: ${your_size_usd:,.0f}")
```

**Copy rule:** replicate each position at the same allocation percentage as the trader, using your own capital as the base.

---

## Step 5: Check Open Orders

```
GET /hyperliquid/trader_open_order?address=<ethAddress>
```

Review pending limit orders to understand their entry/exit plan. If they have many close orders stacked (like selling into strength), factor that into your copy — they may be planning to exit soon.

---

## Step 6: Monitor

Re-run Steps 4–5 periodically (e.g. every 15–30 minutes) to detect:
- New positions opened → open the same on your account
- Positions closed or reduced → close/reduce proportionally
- Sudden large drawdown → consider pausing copy until situation is clear

---

## Risk Notes

- **Slippage:** Large traders open big positions. By the time you copy, the price may have moved. For illiquid altcoins, be cautious.
- **Liquidation risk:** Even high-Sharpe traders can have bad months. Never copy with more than you can afford to lose.
- **Lag:** This is manual or semi-automated copy trading. Real-time automated copy requires on-chain hooks or exchange copy trading features.
