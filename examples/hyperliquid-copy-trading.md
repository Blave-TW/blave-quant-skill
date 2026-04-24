# Example: Hyperliquid Copy Trading — Find High-Sharpe Traders to Follow

## Strategy

Find Hyperliquid traders suitable for copy trading based on:
- **Sharpe ratio ≥ 1.5** — consistent risk-adjusted returns
- **≥ 90 data points** in performance history — enough sample to rule out luck
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

Returns `{chart: {timestamp: [...], pnl: [...]}}` — cumulative PnL (USD) over time.

```python
import numpy as np

pnl_arr    = np.array(chart['pnl'],       dtype=float)
timestamps = np.array(chart['timestamp'], dtype=float)  # Unix seconds

# Require at least 90 data points
if len(pnl_arr) < 90:
    continue

# Per-period PnL changes (NOT "daily" — spacing varies by trader/activity)
period_returns = np.diff(pnl_arr)
if period_returns.std() == 0:
    continue

# Annualize based on actual timestamp spacing, not a fixed "365 days" assumption.
# avg_dt is the mean seconds between consecutive data points.
# periods_per_year = how many such intervals fit in a year.
avg_dt         = np.diff(timestamps).mean()            # seconds per period
periods_per_year = (365 * 24 * 3600) / avg_dt

sharpe = (period_returns.mean() / period_returns.std()) * np.sqrt(periods_per_year)
if sharpe < 1.5:
    continue

# Max drawdown (absolute USD, from running cumulative-PnL peak)
peak       = np.maximum.accumulate(pnl_arr)
max_dd_usd = (pnl_arr - peak).min()

# Win rate
win_rate = (period_returns > 0).mean()

# Track record length in days
track_days = (timestamps[-1] - timestamps[0]) / 86400
```

**Final filter:** keep only traders where both `month_pnl > 0` and `week_pnl > 0` — confirms recent consistency, not just historical glory.

---

## Step 3: Rank, Select, and Plot

Sort passing traders by Sharpe ratio (descending). Present as a table and generate a PnL chart.

### Ranking Table

| Rank | Name / Address | Sharpe | Win Rate | Max DD (USD) | Turnover | Month PnL | Account |
|---|---|---|---|---|---|---|---|
| 1 | ... | 4.8 | 58.7% | -$6.7M | 0.1x | +$7.3M | $41M |
| 2 | ... | 3.1 | 59.0% | -$24.6M | 3.9x | +$1.6M | $20M |

Select the **top 1–3** for deeper inspection.

### PnL Chart (top 3 qualifying traders)

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Assume `qualifying` is a list of dicts, each with keys:
#   address, displayName, pnl_arr, timestamps, sharpe, win_rate, max_dd_usd

top3 = qualifying[:3]

fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=False,
                         gridspec_kw={'height_ratios': [3, 1]})

colors = ['#2ecc71', '#3498db', '#e67e22']

# Panel 1: Cumulative PnL curves
ax_pnl = axes[0]
for trader, color in zip(top3, colors):
    ts  = trader['timestamps']
    pnl = trader['pnl_arr']
    dates = [datetime.utcfromtimestamp(t) for t in ts]
    label = (trader['displayName'] or trader['address'][:10] + '...')
    label += f"  Sharpe={trader['sharpe']:.2f}  WR={trader['win_rate']*100:.1f}%"
    ax_pnl.plot(dates, pnl / 1e6, lw=1.5, color=color, label=label)

ax_pnl.axhline(0, color='#888', lw=0.6, ls='--')
ax_pnl.set_ylabel('Cumulative PnL (USD million)', fontsize=11)
ax_pnl.set_title('Hyperliquid Top Traders — Cumulative PnL', fontsize=13, fontweight='bold')
ax_pnl.legend(fontsize=9, loc='upper left')
ax_pnl.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax_pnl.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax_pnl.xaxis.get_majorticklabels(), rotation=30, ha='right')
ax_pnl.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.1f}M'))

# Panel 2: Drawdown
ax_dd = axes[1]
for trader, color in zip(top3, colors):
    pnl  = trader['pnl_arr']
    ts   = trader['timestamps']
    dates = [datetime.utcfromtimestamp(t) for t in ts]
    peak = np.maximum.accumulate(pnl)
    dd   = pnl - peak          # absolute USD drawdown from running peak
    ax_dd.plot(dates, dd / 1e6, lw=1, color=color, alpha=0.8)
    ax_dd.fill_between(dates, dd / 1e6, 0, color=color, alpha=0.15)

ax_dd.axhline(0, color='#888', lw=0.6)
ax_dd.set_ylabel('Drawdown (USD million)', fontsize=11)
ax_dd.set_title('Drawdown', fontsize=12)
ax_dd.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax_dd.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax_dd.xaxis.get_majorticklabels(), rotation=30, ha='right')
ax_dd.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.1f}M'))

plt.tight_layout()
plt.savefig('hyperliquid_top_traders.png', dpi=150, bbox_inches='tight')
plt.show()
print('Saved: hyperliquid_top_traders.png')
```

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

## Notes

- **Sharpe annualization:** `trader_performance` timestamps are not evenly spaced — data points reflect actual trading activity, so gaps vary. The Sharpe formula computes `avg_dt` from real timestamp differences and derives `periods_per_year = (365 × 24 × 3600) / avg_dt`. Using a hardcoded `√365` would overstate or understate the Sharpe depending on the trader's data density.
- **Max drawdown in USD:** computed on cumulative PnL, not on account value. A large USD drawdown on a $40M account is proportionally small; always compare `max_dd_usd / accountValue` for relative context.
- **Slippage:** large traders open big positions. By the time you copy, the price may have moved. For illiquid altcoins, be cautious.
- **Liquidation risk:** even high-Sharpe traders can have bad months. Never copy with more than you can afford to lose.
- **Lag:** this is manual or semi-automated copy trading. Real-time automated copy requires on-chain hooks or exchange copy trading features.
