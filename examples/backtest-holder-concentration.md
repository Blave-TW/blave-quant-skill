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

    # Metrics
    r = strat_ret[~np.isnan(strat_ret)]
    ann_ret  = r.mean() * HOURS_PER_YEAR
    ann_vol  = r.std()  * np.sqrt(HOURS_PER_YEAR)
    sharpe   = ann_ret / ann_vol
    cum      = np.cumprod(1 + r)
    peak     = np.maximum.accumulate(cum)
    max_dd   = ((cum - peak) / peak).min()
    n_trades = int((np.diff(position.astype(int)) == 1).sum())

    return {
        "sharpe": sharpe,
        "total_return": cum[-1] - 1,
        "max_dd": max_dd,
        "n_trades": n_trades,
        "position": position,
        "sized": sized,
        "strat_ret": strat_ret,
        "cum": cum,
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


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Loading data for {SYMBOL} ({START_DATE} → {END_DATE}, {PERIOD})...")
    kline = load_kline(SYMBOL, START_DATE, END_DATE, PERIOD)
    hc    = load_hc(SYMBOL, START_DATE, END_DATE, PERIOD)

    df = kline[["close"]].join(hc[["hc"]], how="inner").dropna(subset=["close"])
    print(f"Aligned rows: {len(df)}")

    result = run_backtest(df)
    print(f"\nResults (entry>{ENTRY_TH}, exit<{EXIT_TH}):")
    print(f"  Sharpe       : {result['sharpe']:.2f}")
    print(f"  Total Return : {result['total_return']*100:.1f}%")
    print(f"  Max Drawdown : {result['max_dd']*100:.1f}%")
    print(f"  # Trades     : {result['n_trades']}")

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
- Entry threshold (1.0) is stricter than exit (-0.5) — gives the position room to breathe through short-term noise
- Vol-targeting scales down automatically during high-volatility periods; a coin with 3× BTC vol receives ~1/3 the position size for the same signal
- Signals update every 5 minutes; on `1h` period each bar reflects the last finalized hourly HC value
