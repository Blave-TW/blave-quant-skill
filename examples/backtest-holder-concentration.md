# Example: Backtest — Holder Concentration Long Strategy

## Strategy Logic

Go long when smart money (institutions / large players) is concentrating into a coin. Exit when they start distributing.

- **Entry:** HC alpha > `1.0` → open long
- **Exit:** HC alpha < `-0.5` → close long
- **Hold:** between thresholds, maintain current position ("strict entry, loose exit")
- **Vol-targeting:** size each position so the strategy targets 30% annualized volatility regardless of the coin's own volatility
- **Long only** — no short positions

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
import matplotlib.pyplot as plt
import os

# ── Config ──────────────────────────────────────────────────────────────────
SYMBOL         = "BTCUSDT"
START_DATE     = "2023-01-01"
END_DATE       = "2024-12-31"
PERIOD         = "1h"
ENTRY_TH       = 1.0            # HC alpha > 1.0 → open long
EXIT_TH        = -0.5           # HC alpha < -0.5 → close long
TARGET_VOL     = 0.30           # 30% annualized target volatility
MAX_LEV        = 2.0            # max position size (leverage cap)
VOL_WINDOW     = 720            # 30 days × 24h
HOURS_PER_YEAR = 8760
FEE            = 0.0005         # 0.05% per side (taker fee)

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


# ── Backtest ──────────────────────────────────────────────────────────────────
def run_backtest(df):
    close = df["close"].values
    hc    = df["hc"].values
    n     = len(df)

    # Forward returns
    fwd_ret = np.empty(n)
    fwd_ret[:-1] = np.diff(close) / close[:-1]
    fwd_ret[-1]  = 0.0

    # Rolling realized vol (annualized)
    log_ret = np.concatenate([[0.0], np.log(close[1:] / close[:-1])])
    realized_vol = np.full(n, np.nan)
    for i in range(VOL_WINDOW, n):
        realized_vol[i] = log_ret[i - VOL_WINDOW:i].std() * np.sqrt(HOURS_PER_YEAR)

    # Signal: long only
    position = np.zeros(n)
    in_pos = False
    for i in range(n):
        if np.isnan(hc[i]):
            position[i] = float(in_pos)
            continue
        if not in_pos and hc[i] > ENTRY_TH:
            in_pos = True
        elif in_pos and hc[i] < EXIT_TH:
            in_pos = False
        position[i] = float(in_pos)

    # Vol-targeting
    vol_scalar = np.where(
        (realized_vol > 0) & ~np.isnan(realized_vol),
        np.clip(TARGET_VOL / realized_vol, 0, MAX_LEV),
        1.0
    )
    sized = position * vol_scalar

    # Transaction cost
    fee_cost  = np.abs(np.diff(sized, prepend=0)) * FEE
    strat_ret = sized * fwd_ret - fee_cost

    # ── Bar-level metrics ────────────────────────────────────────────────────
    r = strat_ret[~np.isnan(strat_ret)]
    cum      = np.cumprod(1 + r)
    peak     = np.maximum.accumulate(cum)
    total_years = len(r) / HOURS_PER_YEAR

    total_return  = cum[-1] - 1
    ann_ret       = (1 + total_return) ** (1 / total_years) - 1
    ann_vol       = r.std() * np.sqrt(HOURS_PER_YEAR)
    sharpe        = ann_ret / ann_vol if ann_vol > 0 else np.nan
    max_dd        = ((cum - peak) / peak).min()

    # ── Trade-level metrics ──────────────────────────────────────────────────
    # Each trade = one entry→exit cycle; compute per-trade net return
    entries = np.where(np.diff(position.astype(int)) == 1)[0] + 1
    exits   = np.where(np.diff(position.astype(int)) == -1)[0] + 1
    if position[-1] == 1:                          # still in position at end
        exits = np.append(exits, len(position) - 1)

    trade_returns = []
    for entry_i, exit_i in zip(entries, exits):
        trade_r = strat_ret[entry_i:exit_i]
        trade_r = trade_r[~np.isnan(trade_r)]
        if len(trade_r) > 0:
            trade_returns.append(np.prod(1 + trade_r) - 1)

    trade_returns = np.array(trade_returns)
    n_trades      = len(trade_returns)
    win_rate      = (trade_returns > 0).mean() if n_trades > 0 else np.nan
    avg_win       = trade_returns[trade_returns > 0].mean() if (trade_returns > 0).any() else np.nan
    avg_loss      = trade_returns[trade_returns <= 0].mean() if (trade_returns <= 0).any() else np.nan
    avg_trades_yr = n_trades / total_years

    return {
        "total_return":  total_return,
        "ann_ret":       ann_ret,
        "ann_vol":       ann_vol,
        "sharpe":        sharpe,
        "max_dd":        max_dd,
        "win_rate":      win_rate,
        "avg_win":       avg_win,
        "avg_loss":      avg_loss,
        "n_trades":      n_trades,
        "avg_trades_yr": avg_trades_yr,
        "position": position,
        "sized":    sized,
        "strat_ret": strat_ret,
        "cum":      cum,
    }


# ── PnL Chart ─────────────────────────────────────────────────────────────────
def plot_pnl(df, result, symbol):
    close  = df["close"].values
    hc     = df["hc"].values
    dates  = df.index
    cum    = result["cum"]
    pos    = result["position"]

    peak = np.maximum.accumulate(cum)
    dd   = (cum - peak) / peak

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True,
                              gridspec_kw={'height_ratios': [3, 1, 1]})

    # Panel 1: Price (left y) + Strategy PnL (right y)
    ax1 = axes[0]
    ax2 = ax1.twinx()

    ax1.plot(dates, close, color="#3498db", lw=1, alpha=0.7, label="Price")
    ax1.set_ylabel("Price (USD)", fontsize=11, color="#3498db")
    ax1.tick_params(axis='y', labelcolor="#3498db")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    ax2.plot(dates, (cum - 1) * 100, color="#2ecc71", lw=1.5, label="HC Strategy (+fees)")
    ax2.axhline(0, color="#888", lw=0.5, ls="--")
    ax2.set_ylabel("Strategy Return (%)", fontsize=11, color="#2ecc71")
    ax2.tick_params(axis='y', labelcolor="#2ecc71")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    # Shade in-position periods
    prev = False
    for i, (date, inp) in enumerate(zip(dates, pos > 0)):
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
        f"{symbol} — HC Strategy (entry>{ENTRY_TH}, exit<{EXIT_TH})\n"
        f"Vol-Target {TARGET_VOL*100:.0f}% | Max Lev {MAX_LEV}x | Fee {FEE*100:.2f}%/side",
        fontsize=13
    )

    # Panel 2: Drawdown
    axes[1].fill_between(dates, dd * 100, 0, color="#e74c3c", alpha=0.6)
    axes[1].set_ylabel("Drawdown (%)", fontsize=11)
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    axes[1].axhline(0, color="#888", lw=0.5)

    # Panel 3: HC signal
    axes[2].plot(dates, hc, color="#9b59b6", lw=0.8, alpha=0.8)
    axes[2].axhline(ENTRY_TH, color="#2ecc71", lw=1, ls="--", label=f"Entry={ENTRY_TH}")
    axes[2].axhline(EXIT_TH,  color="#e74c3c", lw=1, ls="--", label=f"Exit={EXIT_TH}")
    axes[2].axhline(0, color="#888", lw=0.5)
    axes[2].set_ylabel("HC Alpha", fontsize=11)
    axes[2].legend(fontsize=9, loc="upper right")

    plt.tight_layout()
    fname = f"{symbol}_hc_pnl.png"
    plt.savefig(fname, dpi=150)
    plt.show()
    print(f"Saved: {fname}")


# ── 2D Parameter Scan ────────────────────────────────────────────────────────
THRESHOLDS = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]

def param_scan(df):
    sharpe_grid = np.full((len(THRESHOLDS), len(THRESHOLDS)), np.nan)
    for i, entry in enumerate(THRESHOLDS):
        for j, exit_ in enumerate(THRESHOLDS):
            if exit_ > entry:
                continue
            r = run_backtest_params(df, entry, exit_)
            if r is not None:
                sharpe_grid[i, j] = r["sharpe"]
    return sharpe_grid


def run_backtest_params(df, entry_th, exit_th):
    """Lightweight version for scanning — returns only Sharpe."""
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
    sized     = position * vol_scalar
    fee_cost  = np.abs(np.diff(sized, prepend=0)) * FEE
    strat_ret = sized * fwd_ret - fee_cost

    r = strat_ret[~np.isnan(strat_ret)]
    if len(r) == 0 or r.std() == 0:
        return None

    total_years = len(r) / HOURS_PER_YEAR
    ann_ret = (1 + np.prod(1 + r) - 1) ** (1 / total_years) - 1
    ann_vol = r.std() * np.sqrt(HOURS_PER_YEAR)
    return {"sharpe": ann_ret / ann_vol}


def find_plateau(sharpe_grid, window=1):
    """
    Find the parameter plateau: the cell whose neighborhood has the
    highest mean Sharpe. Uses a (2*window+1) × (2*window+1) window.
    This is more robust than picking the single best cell, as it
    avoids isolated peaks that may be overfitted.
    """
    rows, cols = sharpe_grid.shape
    neighborhood_mean = np.full((rows, cols), np.nan)

    for i in range(rows):
        for j in range(cols):
            if np.isnan(sharpe_grid[i, j]):
                continue
            neighbors = []
            for di in range(-window, window + 1):
                for dj in range(-window, window + 1):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        v = sharpe_grid[ni, nj]
                        if not np.isnan(v):
                            neighbors.append(v)
            if neighbors:
                neighborhood_mean[i, j] = np.mean(neighbors)

    best_idx = np.unravel_index(np.nanargmax(neighborhood_mean), neighborhood_mean.shape)
    return best_idx, neighborhood_mean


def plot_heatmap(sharpe_grid, neighborhood_mean, plateau_idx, symbol):
    peak_idx = np.unravel_index(np.nanargmax(sharpe_grid), sharpe_grid.shape)

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    for ax, mark_idx, title, note in [
        (axes[0], peak_idx,    "Peak — highest single Sharpe",
         f"Selected: entry={THRESHOLDS[peak_idx[0]]}, exit={THRESHOLDS[peak_idx[1]]}\n"
         f"Sharpe={sharpe_grid[peak_idx]:.2f} — may be overfitted if isolated"),
        (axes[1], plateau_idx, "Plateau — most stable region",
         f"Selected: entry={THRESHOLDS[plateau_idx[0]]}, exit={THRESHOLDS[plateau_idx[1]]}\n"
         f"Sharpe={sharpe_grid[plateau_idx]:.2f} — neighbors also perform well → more robust"),
    ]:
        masked = np.ma.masked_invalid(sharpe_grid)
        cmap = plt.cm.RdYlGn.copy()
        cmap.set_bad(color="#cccccc")
        vals = sharpe_grid[~np.isnan(sharpe_grid)]
        im = ax.imshow(masked, cmap=cmap, vmin=min(0, vals.min()),
                       vmax=np.percentile(vals, 95), aspect="auto")

        ax.add_patch(plt.Rectangle(
            (mark_idx[1] - 0.5, mark_idx[0] - 0.5), 1, 1,
            fill=False, edgecolor="gold", linewidth=3
        ))
        for i in range(len(THRESHOLDS)):
            for j in range(len(THRESHOLDS)):
                v = sharpe_grid[i, j]
                ax.text(j, i, f"{v:.2f}" if not np.isnan(v) else "N/A",
                        ha="center", va="center", fontsize=8,
                        color="#888" if np.isnan(v) else "black")

        ax.set_xticks(range(len(THRESHOLDS))); ax.set_xticklabels(THRESHOLDS)
        ax.set_yticks(range(len(THRESHOLDS))); ax.set_yticklabels(THRESHOLDS)
        ax.set_xlabel("Exit Threshold")
        ax.set_ylabel("Entry Threshold")
        ax.set_title(f"{symbol} — {title}\n{note}", fontsize=10)
        plt.colorbar(im, ax=ax, label="Sharpe Ratio")

    plt.suptitle("Same Sharpe grid, different selection method — prefer Plateau", fontsize=12)
    plt.tight_layout()
    fname = f"{symbol}_hc_heatmap.png"
    plt.savefig(fname, dpi=150)
    plt.show()
    print(f"Saved: {fname}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Loading data for {SYMBOL} ({START_DATE} → {END_DATE}, {PERIOD})...")
    kline = load_kline(SYMBOL, START_DATE, END_DATE, PERIOD)
    hc    = load_hc(SYMBOL, START_DATE, END_DATE, PERIOD)

    df = kline[["close"]].join(hc[["hc"]], how="inner").dropna(subset=["close"])
    print(f"Aligned rows: {len(df)}")

    # Step 1: 2D scan → find plateau
    print("Running 2D parameter scan...")
    sharpe_grid = param_scan(df)
    plateau_idx, neighborhood_mean = find_plateau(sharpe_grid, window=1)

    best_entry = THRESHOLDS[plateau_idx[0]]
    best_exit  = THRESHOLDS[plateau_idx[1]]
    print(f"Plateau center: entry={best_entry}, exit={best_exit} "
          f"(neighborhood mean Sharpe={neighborhood_mean[plateau_idx]:.2f})")

    plot_heatmap(sharpe_grid, neighborhood_mean, plateau_idx, SYMBOL)

    # Step 2: full backtest with plateau parameters
    global ENTRY_TH, EXIT_TH
    ENTRY_TH, EXIT_TH = best_entry, best_exit

    result = run_backtest(df)
    print(f"\nResults (entry>{ENTRY_TH}, exit<{EXIT_TH}):")
    print(f"  總報酬率            : {result['total_return']*100:.1f}%")
    print(f"  年化報酬率           : {result['ann_ret']*100:.1f}%")
    print(f"  年化波動度           : {result['ann_vol']*100:.1f}%")
    print(f"  Sharpe Ratio      : {result['sharpe']:.2f}")
    print(f"  最大回撤 (MDD)      : {result['max_dd']*100:.1f}%")
    print(f"  勝率                : {result['win_rate']*100:.1f}%")
    print(f"  平均獲利 (per trade): {result['avg_win']*100:.2f}%")
    print(f"  平均虧損 (per trade): {result['avg_loss']*100:.2f}%")
    print(f"  總交易次數           : {result['n_trades']}")
    print(f"  平均年交易次數        : {result['avg_trades_yr']:.1f}")

    plot_pnl(df, result, SYMBOL)
```

---

## Parameters

| Parameter | Value | Notes |
|---|---|---|
| `ENTRY_TH` | `1.0` | HC alpha must exceed this to open long |
| `EXIT_TH` | `-0.5` | HC alpha must fall below this to close |
| `PERIOD` | `1h` | HC signal + kline timeframe |
| `VOL_WINDOW` | `720` | 30 days × 24h rolling vol |
| `TARGET_VOL` | `0.30` | 30% annualized target |
| `MAX_LEV` | `2.0` | Position size cap |
| `FEE` | `0.0005` | 0.05% per side (taker fee, e.g. Hyperliquid) |

---

## Alpha Scale Reference

| HC Alpha | Signal |
|---|---|
| > 3 | Over Concentrated (long) |
| 2 – 3 | Highly Concentrated (long) |
| **> 1** | **→ Entry threshold** |
| 0.5 – 1 | Concentrated (long) |
| -0.5 – 0.5 | Neutral |
| **< -0.5** | **→ Exit threshold** |
| < -2 | Concentrated (short) |

---

## Notes

- **Long only** — no short positions taken
- Entry threshold is stricter than exit — gives the position room to breathe through short-term noise
- Vol-targeting scales down automatically during high-volatility periods; a coin with 3× BTC vol receives ~1/3 the position size for the same signal
- Signals update every 5 minutes; on `1h` period each bar reflects the last finalized hourly HC value

### Parameter Selection: Plateau vs Peak

**Do not simply pick the highest Sharpe cell.** A single peak is often an overfitted outlier — it performs well in-sample but is fragile out-of-sample.

Instead, use `find_plateau()` to compute the **neighborhood mean Sharpe** for each cell (average of the cell and its surrounding valid cells within a 3×3 window). The cell with the highest neighborhood mean sits at the center of a stable region — a **parameter plateau** — where nearby combinations also perform well. This indicates robustness: small changes to the thresholds do not collapse performance.

The heatmap shows the same Sharpe grid twice. Left panel marks the **peak** (highest single cell); right panel marks the **plateau center** (cell whose neighborhood has the highest mean Sharpe). Both show the true Sharpe value in each cell — the difference is only which cell is highlighted. Prefer the plateau selection even if its raw Sharpe is slightly lower than the peak.
