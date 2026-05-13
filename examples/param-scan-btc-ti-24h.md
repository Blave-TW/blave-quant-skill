# Example: BTC Taker Intensity 24h — Parameter Scan & Plateau Chart

Requires: `pip install vectorbt`


Scan all entry × exit threshold combinations for a BTC 1h long-only strategy
driven by the Taker Intensity 24h alpha, then select the most **robust** (plateau)
parameters and plot the full backtest PnL.

- **Entry:** TI alpha > `ENTRY_TH` → long
- **Exit:** TI alpha < `EXIT_TH` → flat (EXIT_TH ≤ ENTRY_TH always)
- **Dead zone:** between thresholds → hold current position (`nan`)
- **Long only** — no short positions

---

## Code

```python
import sys, requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import dotenv_values

sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # → blaveclaw-config/
from lib.data import fetch_kline, fetch_taker_intensity
from lib.param_scan import find_plateau, plot_heatmap

_env    = dotenv_values(Path(__file__).parent.parent.parent / ".env")
HEADERS = {"api-key": _env["blave_api_key"], "secret-key": _env["blave_secret_key"]}

# ── Config ────────────────────────────────────────────────────────────────────
SYMBOL      = "BTCUSDT"
INTERVAL    = "1h"
START       = "2022-01-01"
END         = None          # None = today

THRESHOLDS  = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]

TARGET_VOL       = 0.30
VOL_WINDOW       = 720      # 30 days × 24h
HOURS_PER_YEAR   = 8760
VOL_CAP          = 2.0
FEE              = 0.0005

PLATEAU_WINDOW   = 1        # neighbourhood radius for plateau detection


# ── Fetch ─────────────────────────────────────────────────────────────────────
# lib.data handles annual chunking for both kline and alpha endpoints


# ── Signal & backtest engine ───────────────────────────────────────────────────
def _build_ti_signals(close_series, ti_series, entry_th, exit_th):
    """Build vectorbt-compatible signal series for a TI threshold strategy."""
    signal = pd.Series(np.nan, index=close_series.index)
    signal[ti_series > entry_th] = 1.0
    signal[ti_series < exit_th]  = 0.0
    return signal


def _run(close_series, ti_series, entry_th, exit_th):
    import vectorbt as vbt

    signals = _build_ti_signals(close_series, ti_series, entry_th, exit_th)
    log_ret  = np.concatenate([[0.0], np.log(close_series.values[1:] / close_series.values[:-1])])
    real_vol = pd.Series(log_ret, index=close_series.index).rolling(VOL_WINDOW).std() * np.sqrt(HOURS_PER_YEAR)

    # Vol-targeting: scale size by vol at each entry bar
    size = signals.where(signals > 0).copy()
    size[signals > 0] = (TARGET_VOL / real_vol[signals > 0]).clip(upper=VOL_CAP).fillna(1.0)
    size = size.ffill().fillna(1.0)

    pos     = signals.ffill().fillna(0)
    entries = (pos > 0) & (pos.shift(1, fill_value=0) == 0)
    exits   = (pos == 0) & (pos.shift(1, fill_value=0) > 0)

    # Signal at bar i close → execute at bar i+1 (no look-ahead)
    pf = vbt.Portfolio.from_signals(
        close_series,
        entries.shift(1).fillna(False),
        exits.shift(1).fillna(False),
        size=size.shift(1).fillna(1.0),
        size_type='percent',
        fees=FEE, freq='1h',
        init_cash=100_000,
    )

    stats     = pf.stats()
    equity    = pf.value()
    cum       = (equity / equity.iloc[0]).values
    strat_ret = pf.returns().values
    total_ret = float(stats.get('Total Return [%]', 0)) / 100
    yrs       = len(close_series) / HOURS_PER_YEAR
    ann_ret   = (1 + total_ret) ** (1 / yrs) - 1 if yrs > 0 else np.nan

    return dict(
        sharpe   = float(stats.get('Sharpe Ratio', np.nan)),
        ann_ret  = ann_ret,
        max_dd   = float(stats.get('Max Drawdown [%]', 0)) / -100,
        cum      = cum,
        strat_ret= strat_ret,
        n_trades = int(stats.get('Total Trades', 0)),
    )


# ── Param scan ────────────────────────────────────────────────────────────────
def param_scan(close_series, ti_series):
    n = len(THRESHOLDS)
    grid = np.full((n, n), np.nan)
    for i, entry in enumerate(THRESHOLDS):
        for j, exit_ in enumerate(THRESHOLDS):
            if exit_ > entry:
                continue        # invalid: exit must be <= entry
            res = _run(close_series, ti_series, entry, exit_)
            if not np.isnan(res["sharpe"]):
                grid[i, j] = res["sharpe"]
    return grid


# find_plateau and plot_heatmap imported from lib.param_scan


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    end_str = END or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Fetching {SYMBOL} kline {INTERVAL}  {START} → {end_str}")
    df_kline = fetch_kline(SYMBOL, INTERVAL, START, end_str, HEADERS)
    print(f"  {len(df_kline)} bars")

    print(f"Fetching TI 24h  {START} → {end_str}")
    df_ti = fetch_taker_intensity(SYMBOL, INTERVAL, START, end_str, HEADERS, timeframe="24h")
    df_ti = df_ti.rename(columns={"alpha": "ti"})
    print(f"  {len(df_ti)} alpha points")

    # align: inner join on timestamp, forward-fill TI into kline index
    df = df_kline[["Close"]].join(df_ti[["ti"]], how="left")
    df["ti"] = df["ti"].ffill()
    df = df.dropna(subset=["Close", "ti"])
    print(f"  Aligned rows: {len(df)}")

    close_series = df["Close"]
    ti_series    = df["ti"]

    print("\nRunning param scan…")
    grid = param_scan(close_series, ti_series)

    print("Finding plateau…")
    best_idx, nbr_mean, best_entry, best_exit = find_plateau(
        grid, THRESHOLDS, THRESHOLDS, window=PLATEAU_WINDOW)
    bi, bj = best_idx
    print(f"  Best plateau: ENTRY_TH={best_entry}, EXIT_TH={best_exit}  "
          f"Sharpe={grid[bi, bj]:.2f}  nbr-avg={nbr_mean[bi, bj]:.2f}")

    # print full scan table
    hdr = f"  {'ENTRY':>7} {'EXIT':>7} {'Sharpe':>8}"
    print(f"\n{'-'*30}\n{hdr}\n{'-'*30}")
    for i, entry in enumerate(THRESHOLDS):
        for j, exit_ in enumerate(THRESHOLDS):
            if np.isnan(grid[i, j]):
                continue
            mark = " ★" if (i, j) == best_idx else ""
            print(f"  {entry:>7.1f} {exit_:>7.1f} {grid[i,j]:>8.2f}{mark}")
    print(f"{'-'*30}")

    # heatmap
    fname = f"{SYMBOL}_ti24h_param_scan.png"
    plot_heatmap(grid, THRESHOLDS, THRESHOLDS, best_idx,
                 row_label="ENTRY_TH", col_label="EXIT_TH",
                 title=f"{SYMBOL} TI 24h — Sharpe Heatmap",
                 output_path=fname)

    # PnL chart with best params
    best_res = _run(close_series, ti_series, best_entry, best_exit)
    valid    = ~np.isnan(best_res["strat_ret"])
    dates    = df.index[valid]
    cum_pct  = (best_res["cum"] - 1) * 100

    import matplotlib.pyplot as plt, matplotlib.ticker as mticker
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(dates, cum_pct, color="#3498db", lw=1.5)
    ax.axhline(0, color="#888", lw=0.6, ls="--")
    ax.fill_between(dates, cum_pct, 0, where=(cum_pct >= 0), alpha=0.12, color="#2ecc71")
    ax.fill_between(dates, cum_pct, 0, where=(cum_pct < 0),  alpha=0.12, color="#e74c3c")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.set_title(f"ENTRY_TH={best_entry} EXIT_TH={best_exit}  "
                 f"Sharpe={best_res['sharpe']:.2f}  Ann={best_res['ann_ret']*100:.1f}%  "
                 f"MDD={best_res['max_dd']*100:.1f}%  Trades={best_res['n_trades']}")
    pnl_fname = f"{SYMBOL}_ti24h_best_pnl.png"
    plt.tight_layout()
    plt.savefig(pnl_fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {pnl_fname}")
```

---

## What the script produces

| Output | Description |
|---|---|
| **Heatmap** | Each cell = raw Sharpe of that `(ENTRY_TH, EXIT_TH)` combo; NaN cells (EXIT > ENTRY) are masked grey; white rectangle = plateau-selected cell |
| **PnL chart** | Cumulative return of the plateau-selected params over the full period |
| `BTCUSDT_ti24h_param_scan.png` | Saved figure |

---

## Reading the heatmap

- A **peak** (single bright cell surrounded by dark cells) is overfitted — it performs well only at that exact threshold.
- A **plateau** (bright cell in a uniformly bright region) is robust — small changes to the threshold degrade gracefully.
- The white rectangle marks the cell with the highest average Sharpe across its neighbourhood, not necessarily the single highest Sharpe cell.

---

## Notes

- TI alpha is fetched with `timeframe=24h` — this is the 24-hour rolling window.
- `EXIT_TH > ENTRY_TH` cells are skipped (NaN in the grid) — the dead zone logic requires EXIT ≤ ENTRY.
- Vol-targeting scales position size so annualized realized volatility targets 30%; cap at 2× leverage.
- To change the scan grid, edit `THRESHOLDS` (any sorted list of floats).
- To validate against out-of-sample data, see `examples/backtest-validation-mcpt-oos.md`.
