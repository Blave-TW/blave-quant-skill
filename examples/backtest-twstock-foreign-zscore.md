# Taiwan Stock Foreign TS Z-Score Strategy — Backtest

Multi-stock portfolio backtest using vectorbt.

Universe: 50 representative TWSE-listed stocks across 6 sectors.
Signal: 20-day rolling foreign net buy → 252-day time-series Z-Score per stock.
Allocation: weight ∝ z (clipped at 0); all cash when every stock's z ≤ 0.
Rebalancing: weekly (Friday signal → next bar execution).
Transaction cost: 0.1% one-way applied to |Δweight|.
Benchmarks: equal-weight, 2000 random-weight simulations (vectorized).

Requires: `pip install vectorbt`

---

## Stock Universe

| Sector | Stock IDs |
|---|---|
| 半導體 | 2330, 2454, 3711, 3034, 8299, 2303, 2408, 2379, 6415, 2449 |
| 電子/EMS | 2317, 4938, 2324, 2382, 3231, 2357, 2353, 2301, 3008, 2474 |
| 電信 | 2412, 3045, 4904 |
| 金融 | 2882, 2881, 2886, 2891, 2892, 2884, 2885, 2880, 2883, 5880 |
| 石化/材料 | 1301, 1303, 1326, 6505, 2002, 1101, 1102, 1434, 1802 |
| 消費/其他 | 2912, 1216, 2207, 9910, 5904, 2915, 2105, 9933 |

---

## Code

```python
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
import matplotlib.pyplot as plt
import vectorbt as vbt
from datetime import datetime
from dotenv import dotenv_values
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # → blaveclaw-config/
from lib.data import fetch_twstock_institutional, fetch_twstock_price_adj

# ── Config ────────────────────────────────────────────────────────────────────
START         = '2020-01-01'
END           = None
ROLL_WINDOW   = 20
ZSCORE_WINDOW = 252
FEE           = 0.001
N_SIM         = 2000

UNIVERSE = {
    '半導體':    ['2330', '2454', '3711', '3034', '8299',
                  '2303', '2408', '2379', '6415', '2449'],
    '電子/EMS':  ['2317', '4938', '2324', '2382', '3231',
                  '2357', '2353', '2301', '3008', '2474'],
    '電信':      ['2412', '3045', '4904'],
    '金融':      ['2882', '2881', '2886', '2891', '2892',
                  '2884', '2885', '2880', '2883', '5880'],
    '石化/材料': ['1301', '1303', '1326', '6505', '2002',
                  '1101', '1102', '1434', '1802'],
    '消費/其他': ['2912', '1216', '2207', '9910', '5904',
                  '2915', '2105', '9933'],
}
ALL_STOCKS = [s for stocks in UNIVERSE.values() for s in stocks]

env  = dotenv_values()
HDRS = {'api-key': env['blave_api_key'], 'secret-key': env['blave_secret_key']}
BASE = 'https://api.blave.org'

# ── Build data matrices ───────────────────────────────────────────────────────
print(f'Fetching institutional data for {len(ALL_STOCKS)} stocks...')
inst_df = pd.concat([
    fetch_twstock_institutional(s, START, END, HDRS)['foreign_net'].rename(s)
    for s in ALL_STOCKS
], axis=1).sort_index()

print('Fetching adjusted price data...')
close_df = pd.concat([
    fetch_twstock_price_adj(s, START, END, HDRS)['Close'].rename(s)
    for s in ALL_STOCKS
], axis=1).sort_index()

common_idx = inst_df.index.intersection(close_df.index)
inst_df  = inst_df.loc[common_idx].fillna(0)
close_df = close_df.loc[common_idx].ffill()

# ── Signal: 20-day rolling sum → 252-day TS Z-Score ──────────────────────────
roll_net = inst_df.rolling(ROLL_WINDOW, min_periods=1).sum()
z_mean   = roll_net.rolling(ZSCORE_WINDOW, min_periods=ZSCORE_WINDOW // 2).mean()
z_std    = roll_net.rolling(ZSCORE_WINDOW, min_periods=ZSCORE_WINDOW // 2).std()
z_score  = (roll_net - z_mean) / z_std.replace(0, np.nan)

# ── Build weekly weight matrix ────────────────────────────────────────────────
n        = len(close_df)
n_stocks = len(ALL_STOCKS)
daily_ret = close_df.pct_change().fillna(0).values          # (n, n_stocks)

weights_mat  = np.zeros((n, n_stocks))
current_w    = np.zeros(n_stocks)
friday_mask  = close_df.index.dayofweek == 4

for i in range(n):
    if friday_mask[i]:
        z   = z_score.iloc[i].values
        raw = np.where(np.isnan(z), 0.0, np.clip(z, 0, None))
        tot = raw.sum()
        current_w = raw / tot if tot > 0 else raw * 0
    weights_mat[i] = current_w

# ── Portfolio returns with transaction costs ──────────────────────────────────
delta_w  = np.diff(weights_mat, axis=0, prepend=weights_mat[:1] * 0)
tc_daily = (np.abs(delta_w) * FEE).sum(axis=1)
pf_ret   = (weights_mat * daily_ret).sum(axis=1) - tc_daily
pf_equity = np.cumprod(1 + pf_ret)

# ── Stats via vectorbt ────────────────────────────────────────────────────────
pf_series = pd.Series(pf_ret, index=close_df.index)
rets_acc  = pf_series.vbt.returns(freq='1D')
print('\n── Foreign Z-Score Strategy ──')
print(f"  Total Return:  {pf_equity[-1]-1:.1%}")
print(f"  Sharpe Ratio:  {rets_acc.sharpe_ratio():.2f}")
print(f"  Max Drawdown:  {rets_acc.max_drawdown():.1%}")
print(f"  Ann. Return:   {rets_acc.annualized():.1%}")

# ── Benchmarks ────────────────────────────────────────────────────────────────
print(f'\nRunning {N_SIM} random benchmark simulations...')

# Equal-weight benchmark
ew_ret    = daily_ret.mean(axis=1)
ew_equity = np.cumprod(1 + ew_ret)

# Random weight simulations (vectorized)
rng      = np.random.default_rng(42)
sim_w    = rng.dirichlet(np.ones(n_stocks), size=N_SIM)          # (N_SIM, n_stocks)
sim_ret  = daily_ret @ sim_w.T                                    # (n, N_SIM) — BLAS matmul
sim_eq   = np.cumprod(1 + sim_ret, axis=0)
sim_mean = sim_eq.mean(axis=1)
sim_p10  = np.percentile(sim_eq, 10, axis=1)
sim_p90  = np.percentile(sim_eq, 90, axis=1)

def _print_stats(equity, label):
    r   = np.diff(equity) / equity[:-1]
    ann = (equity[-1]) ** (252 / len(equity)) - 1
    sr  = r.mean() / r.std() * 252**0.5
    mdd = ((equity / np.maximum.accumulate(equity)) - 1).min()
    print(f'  {label:<35} Ann={ann:.1%}  Sharpe={sr:.2f}  MaxDD={mdd:.1%}')

_print_stats(pf_equity,  'Foreign Z-Score Strategy')
_print_stats(ew_equity,  'Equal Weight')
_print_stats(sim_mean,   f'Random Mean ({N_SIM} sims)')

# ── Chart ─────────────────────────────────────────────────────────────────────
idx = close_df.index
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9),
                                gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
ax1.plot(idx, pf_equity,    label='Foreign Z-Score', color='#2196F3', linewidth=2)
ax1.plot(idx, ew_equity,    label='Equal Weight',    color='#FF9800', linewidth=1.5, linestyle='--')
ax1.plot(idx, sim_mean,     label=f'Random mean ({N_SIM})', color='gray', linewidth=1, linestyle=':')
ax1.fill_between(idx, sim_p10, sim_p90, alpha=0.12, color='gray', label='Random P10–P90')
ax1.set_ylabel('Portfolio Value (start = 1)')
ax1.set_title('Taiwan Stock Foreign TS Z-Score — Portfolio Backtest')
ax1.legend(loc='upper left'); ax1.grid(alpha=0.3)

dd = pf_equity / np.maximum.accumulate(pf_equity) - 1
ax2.fill_between(idx, dd, 0, color='#2196F3', alpha=0.4)
ax2.set_ylabel('Drawdown'); ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('twstock_foreign_zscore_pnl.png', dpi=150)
print('\nSaved twstock_foreign_zscore_pnl.png')
```

---

## Notes

- **Z-Score warm-up:** First ~252 trading days have no valid signal; strategy holds cash
- **Weekly rebalancing:** Weight vector computed on Friday, applied from Monday open (one-bar lag built in via `weights_mat[i]` being set before return calculation)
- **Transaction costs:** Applied to absolute weight change at each rebalance
- **Random benchmark:** Dirichlet(1,...,1) = uniform over the simplex; no rebalancing costs applied (upper bound on random performance)
- **Forward-adjusted prices** (`/price_adj`) account for dividends — use for backtesting to avoid spurious return spikes
