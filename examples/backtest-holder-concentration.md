# Example: Backtest — Holder Concentration Long Strategy

## Strategy Logic

Go long when smart money (institutions / large players) is concentrating into a coin. Exit when they start distributing.

- **Entry:** HC alpha > `entry_threshold` → open long
- **Exit:** HC alpha < `exit_threshold` → close long
- **Hold:** between thresholds, maintain current position ("strict entry, loose exit")
- **Vol-targeting:** size each position so the strategy targets 30% annualized volatility regardless of the coin's own volatility

---

## Data Required

```
GET /kline?symbol=<SYMBOL>&period=1h&start_date=<YYYY-MM-DD>&end_date=<YYYY-MM-DD>
GET /holder_concentration/get_alpha?symbol=<SYMBOL>&period=1h&start_date=<YYYY-MM-DD>&end_date=<YYYY-MM-DD>
```

Both return time series. Align them on timestamp before backtesting.

For history beyond 1 year, send one request per year and concatenate.

---

## Full Backtest Code

```python
import numpy as np
import pandas as pd
import requests
import itertools
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os

# ── Config ──────────────────────────────────────────────────────────────────
SYMBOL       = "BTCUSDT"
START_DATE   = "2023-01-01"
END_DATE     = "2024-12-31"
PERIOD       = "1h"
TARGET_VOL   = 0.30          # 30% annualized target volatility
MAX_LEV      = 2.0           # max position size (leverage cap)
VOL_WINDOW   = 720           # 30 days × 24h
HOURS_PER_YEAR = 8760        # for annualizing hourly vol
THRESHOLDS   = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]
FEE          = 0.0005        # 0.05% per side (taker fee)

API_BASE  = "https://api.blave.org"
API_KEY    = os.environ["blave_api_key"]
API_SECRET = os.environ["blave_secret_key"]
HEADERS    = {"api-key": API_KEY, "secret-key": API_SECRET}


# ── Fetch helpers ────────────────────────────────────────────────────────────
def fetch_range(endpoint, params):
    """Fetch one year at a time and concatenate if needed."""
    from datetime import datetime, timedelta

    start = datetime.strptime(params["start_date"], "%Y-%m-%d")
    end   = datetime.strptime(params["end_date"],   "%Y-%m-%d")
    all_data = []

    cursor = start
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=365), end)
        p = {**params, "start_date": cursor.strftime("%Y-%m-%d"),
                        "end_date":   chunk_end.strftime("%Y-%m-%d")}
        r = requests.get(f"{API_BASE}/{endpoint}", headers=HEADERS, params=p)
        r.raise_for_status()
        all_data.append(r.json())
        cursor = chunk_end

    return all_data


def load_kline(symbol, start, end, period):
    chunks = fetch_range("kline", {"symbol": symbol, "period": period,
                                   "start_date": start, "end_date": end})
    rows = [row for chunk in chunks for row in chunk]
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close"])
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time").sort_index().drop_duplicates()
    df["close"] = df["close"].astype(float)
    return df


def load_hc(symbol, start, end, period):
    chunks = fetch_range("holder_concentration/get_alpha",
                         {"symbol": symbol, "period": period,
                          "start_date": start, "end_date": end})
    timestamps, alphas = [], []
    for chunk in chunks:
        data = chunk.get("data", {})
        timestamps.extend(data.get("timestamp", []))
        alphas.extend(data.get("alpha", []))

    df = pd.DataFrame({"time": pd.to_datetime(timestamps, unit="s", utc=True),
                       "hc": alphas})
    df = df.set_index("time").sort_index().drop_duplicates()
    df["hc"] = pd.to_numeric(df["hc"], errors="coerce")
    return df


# ── Backtest core ─────────────────────────────────────────────────────────────
def run_backtest(df, entry_th, exit_th):
    """
    df must have columns: close, hc
    Returns dict with sharpe, total_return, max_dd, n_trades
    """
    close = df["close"].values
    hc    = df["hc"].values
    n     = len(df)

    # Forward returns (1-period ahead)
    fwd_ret = np.empty(n)
    fwd_ret[:-1] = np.diff(close) / close[:-1]
    fwd_ret[-1]  = 0.0

    # Rolling realized vol (annualized), using past VOL_WINDOW returns
    log_ret = np.log(close[1:] / close[:-1])
    log_ret = np.concatenate([[0.0], log_ret])

    realized_vol = np.full(n, np.nan)
    for i in range(VOL_WINDOW, n):
        realized_vol[i] = log_ret[i - VOL_WINDOW:i].std() * np.sqrt(HOURS_PER_YEAR)

    # Signal: 1 = long, 0 = flat (no short)
    position = np.zeros(n)
    in_position = False
    for i in range(n):
        if np.isnan(hc[i]):
            position[i] = in_position * 1.0
            continue
        if not in_position and hc[i] > entry_th:
            in_position = True
        elif in_position and hc[i] < exit_th:
            in_position = False
        position[i] = 1.0 if in_position else 0.0

    # Vol-targeting: scale position by target_vol / realized_vol
    vol_scalar = np.where(
        (realized_vol > 0) & ~np.isnan(realized_vol),
        np.clip(TARGET_VOL / realized_vol, 0, MAX_LEV),
        1.0
    )
    sized_position = position * vol_scalar

    # Transaction cost: fee on each position change (entry + exit each pay FEE)
    pos_change = np.abs(np.diff(sized_position, prepend=0))
    fee_cost   = pos_change * FEE

    # Strategy returns (net of fees)
    strat_ret = sized_position * fwd_ret - fee_cost

    # Metrics
    valid = ~np.isnan(strat_ret)
    r = strat_ret[valid]
    if len(r) == 0 or r.std() == 0:
        return None

    annualized_ret   = r.mean() * HOURS_PER_YEAR
    annualized_vol_s = r.std()  * np.sqrt(HOURS_PER_YEAR)
    sharpe           = annualized_ret / annualized_vol_s

    cum = np.cumprod(1 + r)
    peak = np.maximum.accumulate(cum)
    max_dd = ((cum - peak) / peak).min()

    total_return = cum[-1] - 1

    # Count trades (entries)
    entries = np.diff(position.astype(int))
    n_trades = (entries == 1).sum()

    return {
        "sharpe": sharpe,
        "total_return": total_return,
        "max_dd": max_dd,
        "n_trades": n_trades,
    }


# ── 2D Parameter Scan ─────────────────────────────────────────────────────────
def param_scan(df):
    sharpe_grid = np.full((len(THRESHOLDS), len(THRESHOLDS)), np.nan)

    for i, entry_th in enumerate(THRESHOLDS):
        for j, exit_th in enumerate(THRESHOLDS):
            if exit_th > entry_th:
                continue  # invalid combination
            result = run_backtest(df, entry_th, exit_th)
            if result:
                sharpe_grid[i, j] = result["sharpe"]

    return sharpe_grid


def plot_heatmap(sharpe_grid, symbol):
    fig, ax = plt.subplots(figsize=(10, 8))

    # Mask invalid cells
    masked = np.ma.masked_invalid(sharpe_grid)
    cmap = plt.cm.RdYlGn
    cmap.set_bad(color="#cccccc")

    vmax = np.nanpercentile(sharpe_grid[~np.isnan(sharpe_grid)], 95) if not np.all(np.isnan(sharpe_grid)) else 1
    vmin = min(0, np.nanmin(sharpe_grid))

    im = ax.imshow(masked, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")

    # Highlight best cell
    best_idx = np.unravel_index(np.nanargmax(sharpe_grid), sharpe_grid.shape)
    ax.add_patch(plt.Rectangle(
        (best_idx[1] - 0.5, best_idx[0] - 0.5), 1, 1,
        fill=False, edgecolor="gold", linewidth=3, label="Best"
    ))

    # Annotate cells
    for i in range(len(THRESHOLDS)):
        for j in range(len(THRESHOLDS)):
            val = sharpe_grid[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)
            else:
                ax.text(j, i, "N/A", ha="center", va="center", fontsize=7, color="#888")

    ax.set_xticks(range(len(THRESHOLDS)))
    ax.set_yticks(range(len(THRESHOLDS)))
    ax.set_xticklabels(THRESHOLDS)
    ax.set_yticklabels(THRESHOLDS)
    ax.set_xlabel("Exit Threshold")
    ax.set_ylabel("Entry Threshold")
    ax.set_title(f"{symbol} — HC Strategy Sharpe Heatmap\n(Vol-Target {TARGET_VOL*100:.0f}%, Max Lev {MAX_LEV}x, Vol Window {VOL_WINDOW}h)")
    plt.colorbar(im, ax=ax, label="Sharpe Ratio")
    plt.tight_layout()
    plt.savefig(f"{symbol}_hc_heatmap.png", dpi=150)
    plt.show()
    print(f"Saved: {symbol}_hc_heatmap.png")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Loading data for {SYMBOL} ({START_DATE} → {END_DATE}, {PERIOD})...")
    kline = load_kline(SYMBOL, START_DATE, END_DATE, PERIOD)
    hc    = load_hc(SYMBOL, START_DATE, END_DATE, PERIOD)

    # Align on timestamp
    df = kline[["close"]].join(hc[["hc"]], how="inner")
    df = df.dropna(subset=["close"])
    print(f"Aligned rows: {len(df)}")

    # Full scan
    print("Running 2D parameter scan...")
    sharpe_grid = param_scan(df)

    # Best combo
    best_idx = np.unravel_index(np.nanargmax(sharpe_grid), sharpe_grid.shape)
    best_entry = THRESHOLDS[best_idx[0]]
    best_exit  = THRESHOLDS[best_idx[1]]
    best_sharpe = sharpe_grid[best_idx]
    print(f"\nBest combo: entry={best_entry}, exit={best_exit}, Sharpe={best_sharpe:.2f}")

    # Detailed result for best combo
    best = run_backtest(df, best_entry, best_exit)
    print(f"Total return : {best['total_return']*100:.1f}%")
    print(f"Max drawdown : {best['max_dd']*100:.1f}%")
    print(f"# Trades     : {best['n_trades']}")

    # Plot heatmap
    plot_heatmap(sharpe_grid, SYMBOL)

    # Plot PnL chart for best combo
    plot_pnl(df, best_entry, best_exit, SYMBOL)


def plot_pnl(df, entry_th, exit_th, symbol):
    close = df["close"].values
    hc    = df["hc"].values
    n     = len(df)

    fwd_ret = np.empty(n)
    fwd_ret[:-1] = np.diff(close) / close[:-1]
    fwd_ret[-1]  = 0.0

    log_ret = np.concatenate([[0.0], np.log(close[1:] / close[:-1])])
    realized_vol = np.full(n, np.nan)
    for i in range(VOL_WINDOW, n):
        realized_vol[i] = log_ret[i - VOL_WINDOW:i].std() * np.sqrt(HOURS_PER_YEAR)

    position = np.zeros(n)
    in_pos = False
    for i in range(n):
        if np.isnan(hc[i]):
            position[i] = float(in_pos)
            continue
        if not in_pos and hc[i] > entry_th:
            in_pos = True
        elif in_pos and hc[i] < exit_th:
            in_pos = False
        position[i] = float(in_pos)

    vol_scalar = np.where(
        (realized_vol > 0) & ~np.isnan(realized_vol),
        np.clip(TARGET_VOL / realized_vol, 0, MAX_LEV),
        1.0
    )
    sized    = position * vol_scalar
    fee_cost = np.abs(np.diff(sized, prepend=0)) * FEE
    strat_ret = sized * fwd_ret - fee_cost

    cum_strat = np.cumprod(1 + np.nan_to_num(strat_ret))
    peak = np.maximum.accumulate(cum_strat)
    dd   = (cum_strat - peak) / peak
    dates = df.index

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True,
                              gridspec_kw={'height_ratios': [3, 1, 1]})

    # Panel 1: Price (left y-axis) + Strategy PnL (right y-axis)
    ax1 = axes[0]
    ax2 = ax1.twinx()

    ax1.plot(dates, close, color="#3498db", lw=1, alpha=0.7, label="BTC Price")
    ax1.set_ylabel("Price (USD)", fontsize=11, color="#3498db")
    ax1.tick_params(axis='y', labelcolor="#3498db")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    ax2.plot(dates, (cum_strat - 1) * 100, color="#2ecc71", lw=1.5, label="HC Strategy (+fees)")
    ax2.axhline(0, color="#888", lw=0.5, ls="--")
    ax2.set_ylabel("Strategy Return (%)", fontsize=11, color="#2ecc71")
    ax2.tick_params(axis='y', labelcolor="#2ecc71")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    # Shade in-position periods
    in_pos_arr = position > 0
    prev = False
    for i, (date, inp) in enumerate(zip(dates, in_pos_arr)):
        if inp and not prev:
            start = date
        if not inp and prev:
            ax1.axvspan(start, date, alpha=0.08, color="#2ecc71")
        prev = inp
    if prev:
        ax1.axvspan(start, dates[-1], alpha=0.08, color="#2ecc71")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=10, loc="upper left")
    ax1.set_title(
        f"{symbol} — HC Strategy vs Price\n"
        f"entry={entry_th}, exit={exit_th} | Vol-Target {TARGET_VOL*100:.0f}% | Fee {FEE*100:.2f}%/side",
        fontsize=13
    )

    # Panel 2: Drawdown
    axes[1].fill_between(dates, dd * 100, 0, color="#e74c3c", alpha=0.6)
    axes[1].set_ylabel("Drawdown (%)", fontsize=11)
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    axes[1].axhline(0, color="#888", lw=0.5)

    # Panel 3: HC signal
    axes[2].plot(dates, hc, color="#9b59b6", lw=0.8, alpha=0.8)
    axes[2].axhline(entry_th, color="#2ecc71", lw=1, ls="--", label=f"Entry={entry_th}")
    axes[2].axhline(exit_th,  color="#e74c3c", lw=1, ls="--", label=f"Exit={exit_th}")
    axes[2].axhline(0, color="#888", lw=0.5)
    axes[2].set_ylabel("HC Alpha", fontsize=11)
    axes[2].legend(fontsize=9, loc="upper right")

    plt.tight_layout()
    fname = f"{symbol}_hc_pnl.png"
    plt.savefig(fname, dpi=150)
    plt.show()
    print(f"Saved: {fname}")
```

---

## Parameters

| Parameter | Value | Notes |
|---|---|---|
| `PERIOD` | `1h` | HC signal + kline timeframe |
| `VOL_WINDOW` | `720` | 30 days × 24h rolling vol |
| `TARGET_VOL` | `0.30` | 30% annualized target |
| `MAX_LEV` | `2.0` | Position size cap |
| `THRESHOLDS` | `[-2, -1.5, …, 2]` | Step 0.5, 9 values |
| `FEE` | `0.0005` | 0.05% per side (taker fee, e.g. Hyperliquid) |

---

## Reading the Heatmap

- **Green cells** — high Sharpe, good parameter combo
- **Gold border** — best combo found
- **Grey N/A** — invalid (exit > entry)
- **Red cells** — negative Sharpe, avoid

Look for **clusters of green**, not just one isolated best cell. An isolated peak may be overfitted; a cluster means the strategy is robust across nearby parameter values.

---

## Notes

- This strategy is **long-only** — no short positions
- Signals are based on HC alpha, which updates every 5 minutes; on `1h` period, each bar reflects the last finalized hourly value
- Vol-targeting scales down positions during high-volatility periods automatically — DOGE at 3× BTC vol will receive ~1/3 the position size for the same signal
- **Overfitting warning:** parameter scan on in-sample data will always find a "best" combo. Always validate the best combo on out-of-sample data before using it live
