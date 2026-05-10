# Taiwan Stock Foreign TS Z-Score Strategy — Backtest

Multi-stock portfolio backtest using the unified `Backtest` + `Strategy` framework (portfolio mode).

Universe: 50 representative TWSE-listed stocks across 6 sectors.
Signal: 20-day rolling foreign net buy → 252-day time-series Z-Score per stock.
Allocation: weight ∝ z (clipped at 0); all cash when every stock's z ≤ 0.
Rebalancing: weekly (Friday signal → Monday open execution).
Transaction cost: 0.1% one-way applied to |Δweight|.
Benchmarks: equal-weight, 2000 random-weight simulations (vectorized, ~100× faster than loop).

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
# ── Path setup: use backtesting package from this skill, not PyPI ─────────────
import sys
from pathlib import Path
# When running from strategies/<name>/ inside blaveclaw-config:
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "blave-quant"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ── Imports ───────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from dotenv import dotenv_values
from backtesting import Backtest, Strategy

# ── Config ────────────────────────────────────────────────────────────────────
START         = '2020-01-01'
END           = None          # None → today
ROLL_WINDOW   = 20            # days: rolling sum to smooth foreign net buy
ZSCORE_WINDOW = 252           # trading days for TS Z-Score
FEE           = 0.001         # 0.1% one-way transaction cost
N_SIM         = 2000          # random allocation simulations for benchmark

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

# ── Data fetch ────────────────────────────────────────────────────────────────
def fetch_institutional(stock_id):
    end_str = END or datetime.utcnow().strftime('%Y-%m-%d')
    r = requests.get(
        f'{BASE}/studio/market/twstock/institutional/{stock_id}',
        headers=HDRS, params={'start': START, 'end': end_str}, timeout=60,
    )
    r.raise_for_status()
    df = pd.DataFrame(r.json()['data'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    df['foreign_net'] = df['foreign_buy'] - df['foreign_sell']
    return df['foreign_net'].rename(stock_id)


def fetch_price_adj(stock_id):
    end_str = END or datetime.utcnow().strftime('%Y-%m-%d')
    r = requests.get(
        f'{BASE}/studio/market/twstock/price_adj/{stock_id}',
        headers=HDRS, params={'start': START, 'end': end_str}, timeout=60,
    )
    r.raise_for_status()
    df = pd.DataFrame(r.json()['data'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    return df[['open', 'close']].rename(columns={'open': 'Open', 'close': 'Close'}).rename_axis(stock_id, axis=1)


# ── Build data matrices ───────────────────────────────────────────────────────
print(f'Fetching institutional data for {len(ALL_STOCKS)} stocks...')
inst_df = pd.concat([fetch_institutional(s) for s in ALL_STOCKS], axis=1).sort_index()

print('Fetching forward-adjusted price data...')
price_frames = []
for s in ALL_STOCKS:
    df = fetch_price_adj(s)
    df.columns = pd.MultiIndex.from_product([[s], df.columns])
    price_frames.append(df)
prices_mi = pd.concat(price_frames, axis=1).sort_index()  # MultiIndex columns: (stock, Open/Close)

# Align to common dates
common_idx = inst_df.index.intersection(prices_mi.index)
inst_df   = inst_df.loc[common_idx].fillna(0)
prices_mi = prices_mi.loc[common_idx]

# ── Signal: 20-day rolling sum → 252-day TS Z-Score ──────────────────────────
roll_net  = inst_df.rolling(ROLL_WINDOW, min_periods=1).sum()
z_mean    = roll_net.rolling(ZSCORE_WINDOW, min_periods=ZSCORE_WINDOW // 2).mean()
z_std     = roll_net.rolling(ZSCORE_WINDOW, min_periods=ZSCORE_WINDOW // 2).std()
z_score   = (roll_net - z_mean) / z_std.replace(0, np.nan)
# shape: (n_days, 50); NaN during warm-up period (~first year)

# ── Strategy ──────────────────────────────────────────────────────────────────
class ForeignZScoreStrategy(Strategy):
    """
    Weight ∝ positive Z-Score of foreign net buy.
    Rebalances every Friday; executes at following Monday's open.
    Holds cash when all Z-Scores ≤ 0.
    """
    def init(self):
        pass  # signals are pre-computed and passed via Backtest(signals=z_score)

    def next(self):
        if self.data.index[-1].weekday() != 4:   # rebalance on Friday only
            return
        z = self.signals.iloc[-1]
        raw = z.clip(lower=0).fillna(0)
        total = raw.sum()
        self.allocate(raw / total if total > 0 else raw * 0)


# ── Backtest ──────────────────────────────────────────────────────────────────
bt    = Backtest(prices_mi, ForeignZScoreStrategy, commission=FEE, signals=z_score)
stats = bt.run()
print(stats[['Return [%]', 'Return (Ann.) [%]', 'Sharpe Ratio',
             'Max. Drawdown [%]']].round(2))

# ── Benchmarks ────────────────────────────────────────────────────────────────
print(f'\nRunning {N_SIM} random simulations...')
bench = bt.run_benchmarks(rebal_freq='W-FRI', n_sim=N_SIM)

# Quick stats for benchmarks
def _stats(s, label):
    r   = s.pct_change().dropna()
    tot = s.iloc[-1] / s.iloc[0] - 1
    sr  = r.mean() / r.std() * 252**0.5
    mdd = (s / s.cummax() - 1).min()
    print(f'{label:30s}  Total={tot:.1%}  Sharpe={sr:.2f}  MaxDD={mdd:.1%}')

_stats(stats['_equity_curve']['Equity'],  'Foreign Z-Score Strategy')
_stats(bench['equal_weight'],             'Equal Weight')
_stats(bench['random_mean'],              f'Random Mean ({N_SIM} sims)')
print(f'  Random P10/P90 final: {bench["random_p10"].iloc[-1]:.2f} / {bench["random_p90"].iloc[-1]:.2f}')

# ── Chart ─────────────────────────────────────────────────────────────────────
eq  = stats['_equity_curve']['Equity']
idx = eq.index

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9),
                                gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

ax1.plot(idx, eq.values / eq.iloc[0],                   label='Foreign Z-Score', color='#2196F3', linewidth=2)
ax1.plot(idx, bench['equal_weight'] / bench['equal_weight'].iloc[0],
                                                          label='Equal Weight',   color='#FF9800', linewidth=1.5, linestyle='--')
ax1.plot(idx, bench['random_mean'],                       label=f'Random mean ({N_SIM})', color='gray', linewidth=1, linestyle=':')
ax1.fill_between(idx, bench['random_p10'], bench['random_p90'],
                 alpha=0.12, color='gray', label='Random P10–P90')
ax1.set_ylabel('Portfolio Value (start = 1)')
ax1.set_title('Taiwan Stock Foreign TS Z-Score — Portfolio Backtest')
ax1.legend(loc='upper left')
ax1.grid(alpha=0.3)

dd = eq / eq.cummax() - 1
ax2.fill_between(idx, dd.values, 0, color='#2196F3', alpha=0.4)
ax2.set_ylabel('Drawdown')
ax2.set_xlabel('Date')
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('twstock_foreign_zscore_pnl.png', dpi=150)
print('\nSaved twstock_foreign_zscore_pnl.png')
```

---

## Portfolio Mode — Key Notes

**Data format:** MultiIndex columns `(stock_id, 'Open'/'Close')` — same structure as single-asset OHLCV, just with N assets stacked.

**Execution timing:** Signal fires at Friday's close (`strategy.next()`). Execution at Monday's open (`_PortfolioBroker.next()`). Internally split into:
1. Gap return `close[Fri] → open[Mon]` with **old** weights
2. Transaction cost on `|Δweight|`
3. Intraday return `open[Mon] → close[Mon]` with **new** weights

**`run_benchmarks()` speed:** Vectorized with BLAS matrix multiply (`period_rets @ all_weights.T`). 2000 sims take seconds instead of minutes.

**`self.signals`:** Sliced to current bar, available inside `next()`. Passed as `signals=z_score` to `Backtest`.

**`self.I()` not supported** in portfolio mode — pre-compute signals externally and pass via `signals=`.

---

## Notes

- **Z-Score warm-up:** First ~252 trading days have no valid signal; strategy holds cash. Set `START` earlier for a longer active history.
- **Suspended stocks:** `prices_mi` passes 0-price handling to `_PortfolioBroker` (replace 0 → NaN → ffill).
- **Long-only:** Weights clipped at 0. Short selling in Taiwan requires margin approval.
- **Cash drag:** When all Z-Scores ≤ 0, portfolio earns 0% (no risk-free modeled).
- **Forward-adjusted prices** (`/price_adj`) account for dividends — use these for backtesting to avoid spurious return spikes on ex-dividend dates.
