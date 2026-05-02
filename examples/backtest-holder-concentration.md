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
import gzip, json, sys, requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from backtesting import Backtest, Strategy
from dotenv import dotenv_values

_env = dotenv_values()

# ── Config ──────────────────────────────────────────────────────────────────
MODE          = "backtest"
STRATEGY_NAME = "btc_hc_long"
SYMBOL        = "BTCUSDT"
INTERVAL      = "1h"
START         = "2024-01-01"
END           = None
FEE           = 0.0005
BUDGET_USDT   = 1_000       # set to your actual trading capital before backtesting
VOL_LOOKBACK  = 720         # 30d × 24h
VOL_TARGET    = 0.30
VOL_FLOOR     = 0.02
HOURS_PER_YEAR = 8760

PARAM_GRID = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]

_HDRS = {"api-key": _env.get("blave_api_key", ""), "secret-key": _env.get("blave_secret_key", "")}


# ── Data ─────────────────────────────────────────────────────────────────────
def fetch_data(symbol, start, end):
    """Fetch klines + HC alpha; return merged DataFrame ready for Backtest()."""
    from datetime import datetime, timedelta
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.utcnow() if not end else datetime.strptime(end, "%Y-%m-%d")
    krows, ts_list, alpha_list = [], [], []
    cursor = s
    while cursor < e:
        chunk_end = min(cursor + timedelta(days=365), e)
        p = {"symbol": symbol, "period": INTERVAL,
             "start_date": cursor.strftime("%Y-%m-%d"),
             "end_date":   chunk_end.strftime("%Y-%m-%d")}
        r = requests.get("https://api.blave.org/kline", headers=_HDRS, params=p, timeout=60)
        r.raise_for_status()
        krows.extend(r.json())
        r2 = requests.get("https://api.blave.org/holder_concentration/get_alpha",
                          headers=_HDRS, params=p, timeout=60)
        r2.raise_for_status()
        data = r2.json().get("data", {})
        ts_list.extend(data.get("timestamp", []))
        alpha_list.extend(data.get("alpha", []))
        cursor = chunk_end

    df = pd.DataFrame(krows)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time").sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"})
    df["Volume"] = 0
    df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

    hc = pd.DataFrame({"time": pd.to_datetime(ts_list, unit="s", utc=True), "HC": alpha_list})
    hc = hc.set_index("time").sort_index()
    hc = hc[~hc.index.duplicated(keep="first")]
    hc["HC"] = pd.to_numeric(hc["HC"], errors="coerce")
    df = df.join(hc["HC"], how="left")
    df["HC"] = df["HC"].ffill()
    return df


# ── Signal (pure function — identical in backtest and live) ──────────────────
def compute_signal(hc: float, in_long: bool, entry_th: float, exit_th: float) -> str:
    """Returns desired position state: 'LONG' or 'FLAT'."""
    if np.isnan(hc):
        return "LONG" if in_long else "FLAT"
    if not in_long and hc > entry_th:
        return "LONG"
    if in_long and hc < exit_th:
        return "FLAT"
    return "LONG" if in_long else "FLAT"


# ── Vol-targeting helper ─────────────────────────────────────────────────────
def _vol_series(close):
    log_ret = np.concatenate([[0], np.diff(np.log(close))])
    return (pd.Series(log_ret)
              .rolling(VOL_LOOKBACK, min_periods=1)
              .std()
              .fillna(VOL_TARGET / np.sqrt(HOURS_PER_YEAR))
              .values * np.sqrt(HOURS_PER_YEAR))


# ── Backtest strategy ────────────────────────────────────────────────────────
class BlaveStrategy(Strategy):
    entry_th = 1.0
    exit_th  = -0.5

    def init(self):
        self.hc  = self.I(lambda x: x, self.data.HC,    name="HC")
        self.vol = self.I(_vol_series,  self.data.Close, name="Vol")

    def next(self):
        hc      = float(self.hc[-1])
        in_long = self.position.is_long
        sig     = compute_signal(hc, in_long, self.entry_th, self.exit_th)
        size    = min(VOL_TARGET / max(float(self.vol[-1]), VOL_FLOOR), 0.99)
        if sig == "LONG" and not in_long:
            self.buy(size=size)
        elif sig == "FLAT" and in_long:
            self.position.close()


# ── Plateau selection ────────────────────────────────────────────────────────
def _find_plateau(heatmap, window=1):
    grid_df  = heatmap.unstack()
    grid     = grid_df.values.astype(float)
    row_vals = grid_df.index.tolist()
    col_vals = grid_df.columns.tolist()
    rows, cols = grid.shape
    nbr_mean   = np.full((rows, cols), np.nan)
    for i in range(rows):
        for j in range(cols):
            if np.isnan(grid[i, j]): continue
            nb = [grid[i+di, j+dj]
                  for di in range(-window, window+1)
                  for dj in range(-window, window+1)
                  if 0 <= i+di < rows and 0 <= j+dj < cols
                  and not np.isnan(grid[i+di, j+dj])]
            if nb: nbr_mean[i, j] = np.mean(nb)
    best = np.unravel_index(np.nanargmax(nbr_mean), nbr_mean.shape)
    return row_vals[best[0]], col_vals[best[1]]


# ── Reconstruct arrays for visualization ─────────────────────────────────────
def _reconstruct_arrays(df, stats):
    equity = stats["_equity_curve"]["Equity"].reindex(df.index, method="ffill")
    strat_ret = equity.pct_change().fillna(0).values
    position = np.zeros(len(df))
    for _, row in stats["_trades"].iterrows():
        i0 = df.index.searchsorted(row["EntryTime"])
        i1 = df.index.searchsorted(row["ExitTime"])
        position[i0:i1] = 1.0
    close = df["Close"].values
    log_ret = np.concatenate([[0.0], np.log(close[1:] / close[:-1])])
    realized_vol = pd.Series(log_ret).rolling(VOL_LOOKBACK).std().values * np.sqrt(HOURS_PER_YEAR)
    cum = equity.values / equity.values[0]
    return {"strat_ret": strat_ret, "position": position,
            "realized_vol": realized_vol, "cum": cum}


# ── Regime Analysis ──────────────────────────────────────────────────────────
def regime_analysis(df, result):
    """Break down performance by: calendar year, Bull/Bear, High/Low volatility."""
    strat_ret    = result["strat_ret"]
    realized_vol = result["realized_vol"]
    close        = df["Close"].values
    dates        = df.index

    # Bull/Bear: price vs 200-period rolling MA (window scales with VOL_LOOKBACK)
    ma_window = VOL_LOOKBACK * 200 // 30          # 200 days expressed in bars
    ma200     = pd.Series(close).rolling(ma_window).mean().values
    valid_ma  = ~np.isnan(ma200)

    # High/Low vol: above vs below median realized vol
    vol_median  = np.nanmedian(realized_vol)
    valid_vol   = ~np.isnan(realized_vol)

    def _stats(mask):
        r = strat_ret[mask]
        r = r[~np.isnan(r)]
        if len(r) < 2:
            return None
        total_years = len(r) / HOURS_PER_YEAR
        cum_r   = np.prod(1 + r) - 1
        ann_r   = (1 + cum_r) ** (1 / total_years) - 1 if total_years > 0 else np.nan
        ann_vol = r.std() * np.sqrt(HOURS_PER_YEAR)
        sharpe  = (r.mean() / r.std()) * np.sqrt(HOURS_PER_YEAR) if r.std() > 0 else np.nan
        cum_curve = np.cumprod(1 + r)
        peak    = np.maximum.accumulate(cum_curve)
        mdd     = ((cum_curve - peak) / peak).min()
        n_total = len(strat_ret[~np.isnan(strat_ret)])
        return dict(ann_ret=ann_r, ann_vol=ann_vol, sharpe=sharpe,
                    max_dd=mdd, pct_time=len(r) / n_total)

    rows = []

    # ── By calendar year ────────────────────────────────────────────────────
    for yr in sorted(dates.year.unique()):
        mask = (dates.year == yr)
        s = _stats(mask)
        if s:
            rows.append({"label": str(yr), **s})

    rows.append({"label": "─" * 20})   # separator

    # ── Bull vs Bear ─────────────────────────────────────────────────────────
    bull = close > ma200
    for label, mask in [("Bull (price > MA200)", bull & valid_ma),
                         ("Bear (price < MA200)", ~bull & valid_ma)]:
        s = _stats(mask)
        if s:
            rows.append({"label": label, **s})

    rows.append({"label": "─" * 20})

    # ── High vol vs Low vol ───────────────────────────────────────────────────
    highvol = realized_vol > vol_median
    for label, mask in [("High Vol (>median)",  highvol & valid_vol),
                         ("Low  Vol (≤median)",  ~highvol & valid_vol)]:
        s = _stats(mask)
        if s:
            rows.append({"label": label, **s})

    # ── Print table ───────────────────────────────────────────────────────────
    hdr = f"  {'Regime':<22} {'Ann Ret':>9} {'Ann Vol':>9} {'Sharpe':>8} {'MDD':>8} {'Time%':>7}"
    print(f"\n{'─' * len(hdr)}")
    print("  Regime Analysis")
    print('─' * len(hdr))
    print(hdr)
    print('─' * len(hdr))
    for row in rows:
        if "ann_ret" not in row:          # separator row
            print(f"  {row['label']}")
            continue
        print(f"  {row['label']:<22} {row['ann_ret']*100:>8.1f}% {row['ann_vol']*100:>8.1f}%"
              f" {row['sharpe']:>8.2f} {row['max_dd']*100:>7.1f}% {row['pct_time']*100:>6.1f}%")
    print('─' * len(hdr))


# ── Regime Chart ──────────────────────────────────────────────────────────────
def plot_regime(df, result, symbol):
    strat_ret    = result["strat_ret"]
    realized_vol = result["realized_vol"]
    close        = df["Close"].values
    dates        = df.index

    ma_window  = VOL_LOOKBACK * 200 // 30
    ma200      = pd.Series(close).rolling(ma_window).mean().values
    valid_ma   = ~np.isnan(ma200)
    vol_median = np.nanmedian(realized_vol)
    valid_vol  = ~np.isnan(realized_vol)
    bull       = close > ma200
    highvol    = realized_vol > vol_median

    def _stats(mask):
        r = strat_ret[mask]; r = r[~np.isnan(r)]
        if len(r) < 2: return None
        total_years = len(r) / HOURS_PER_YEAR; cum_r = np.prod(1 + r) - 1
        ann_r   = (1 + cum_r) ** (1 / total_years) - 1 if total_years > 0 else np.nan
        ann_vol = r.std() * np.sqrt(HOURS_PER_YEAR)
        sharpe  = (r.mean() / r.std()) * np.sqrt(HOURS_PER_YEAR) if r.std() > 0 else np.nan
        cc = np.cumprod(1 + r); pk = np.maximum.accumulate(cc)
        return dict(ann_ret=ann_r, sharpe=sharpe, max_dd=((cc - pk) / pk).min())

    groups = {
        "By Year":           [(str(yr), _stats(dates.year == yr))
                               for yr in sorted(dates.year.unique())],
        "Trend Regime":      [("Bull\n(>MA200)", _stats(bull & valid_ma)),
                               ("Bear\n(<MA200)", _stats(~bull & valid_ma))],
        "Volatility Regime": [("High Vol\n(>median)", _stats(highvol & valid_vol)),
                               ("Low Vol\n(≤median)",  _stats(~highvol & valid_vol))],
    }
    groups = {k: [(lbl, s) for lbl, s in v if s is not None] for k, v in groups.items()}

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    for ax, (group_name, items) in zip(axes, groups.items()):
        labels  = [lbl for lbl, _ in items]
        ann_ret = [s["ann_ret"] * 100 for _, s in items]
        sharpe  = [s["sharpe"]        for _, s in items]
        mdd     = [s["max_dd"] * 100  for _, s in items]
        x = np.arange(len(labels)); w = 0.25
        b1 = ax.bar(x - w, ann_ret, w, label="Ann Ret (%)", color="#3498db", alpha=0.85)
        b2 = ax.bar(x,     sharpe,  w, label="Sharpe",      color="#2ecc71", alpha=0.85)
        b3 = ax.bar(x + w, mdd,     w, label="MDD (%)",     color="#e74c3c", alpha=0.85)
        for bars in [b1, b2, b3]:
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2,
                        h + (0.3 if h >= 0 else -1.5),
                        f"{h:.1f}", ha="center",
                        va="bottom" if h >= 0 else "top", fontsize=8)
        ax.axhline(0, color="#555", lw=0.8)
        ax.set_title(group_name, fontsize=13, fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
        ax.set_ylabel("Value", fontsize=10); ax.legend(fontsize=9)
        all_vals = ann_ret + sharpe + mdd
        ax.set_ylim(min(all_vals) - 5, max(all_vals) + 8)

    fig.suptitle(f"{symbol} — Regime Analysis", fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    fname = f"{symbol}_hc_regime.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved: {fname}")


# ── PnL Chart ─────────────────────────────────────────────────────────────────
def plot_pnl(df, result, symbol, entry_th=1.0, exit_th=-0.5):
    close  = df["Close"].values
    hc     = df["HC"].values
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
        f"{symbol} — HC Strategy (entry>{entry_th}, exit<{exit_th})\n"
        f"Vol-Target {VOL_TARGET*100:.0f}% | Fee {FEE*100:.2f}%/side",
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


# ── Heatmap Chart ────────────────────────────────────────────────────────────
def plot_heatmap(heatmap, best_entry, best_exit, symbol):
    """Visualize bt.optimize() heatmap: peak vs plateau selection."""
    grid_df   = heatmap.unstack()
    grid      = grid_df.values.astype(float)
    row_vals  = grid_df.index.tolist()
    col_vals  = grid_df.columns.tolist()
    peak_idx  = np.unravel_index(np.nanargmax(grid), grid.shape)
    plat_idx  = (row_vals.index(best_entry), col_vals.index(best_exit))

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    for ax, mark_idx, title, note in [
        (axes[0], peak_idx,  "Peak — highest single Sharpe",
         f"entry={row_vals[peak_idx[0]]}, exit={col_vals[peak_idx[1]]}\n"
         f"Sharpe={grid[peak_idx]:.2f} — may be overfitted if isolated"),
        (axes[1], plat_idx,  "Plateau — most stable region",
         f"entry={best_entry}, exit={best_exit}\n"
         f"Sharpe={grid[plat_idx]:.2f} — neighbors also perform well → more robust"),
    ]:
        masked = np.ma.masked_invalid(grid)
        cmap = plt.cm.RdYlGn.copy(); cmap.set_bad(color="#cccccc")
        vals = grid[~np.isnan(grid)]
        im = ax.imshow(masked, cmap=cmap, vmin=min(0, vals.min()),
                       vmax=np.percentile(vals, 95), aspect="auto")
        ax.add_patch(plt.Rectangle(
            (mark_idx[1] - 0.5, mark_idx[0] - 0.5), 1, 1,
            fill=False, edgecolor="gold", linewidth=3))
        for i in range(len(row_vals)):
            for j in range(len(col_vals)):
                v = grid[i, j]
                ax.text(j, i, f"{v:.2f}" if not np.isnan(v) else "N/A",
                        ha="center", va="center", fontsize=8,
                        color="#888" if np.isnan(v) else "black")
        ax.set_xticks(range(len(col_vals))); ax.set_xticklabels(col_vals)
        ax.set_yticks(range(len(row_vals))); ax.set_yticklabels(row_vals)
        ax.set_xlabel("Exit Threshold"); ax.set_ylabel("Entry Threshold")
        ax.set_title(f"{symbol} — {title}\n{note}", fontsize=10)
        plt.colorbar(im, ax=ax, label="Sharpe Ratio")
    plt.suptitle("Same Sharpe grid, different selection method — prefer Plateau", fontsize=12)
    plt.tight_layout()
    fname = f"{symbol}_hc_heatmap.png"
    plt.savefig(fname, dpi=150); plt.show(); print(f"Saved: {fname}")


# ── Upload Report ─────────────────────────────────────────────────────────────
def upload_report(df, stats):
    ts_arr = (df.index.astype(np.int64) // 10**9).tolist()
    klines = [[int(ts), float(o), float(h), float(l), float(c)]
               for ts, o, h, l, c in zip(ts_arr, df["Open"], df["High"], df["Low"], df["Close"])]
    trades = []
    for _, row in stats["_trades"].iterrows():
        trades.append({"time": int(row["EntryTime"].timestamp()), "action": "BUY",  "price": float(row["EntryPrice"])})
        trades.append({"time": int(row["ExitTime"].timestamp()),  "action": "SELL", "price": float(row["ExitPrice"])})
    trades.sort(key=lambda t: t["time"])
    equity  = stats["_equity_curve"]["Equity"].reindex(df.index, method="ffill").values
    log_ret = np.diff(np.log(np.where(equity > 0, equity, 1)))
    returns = [0.0] + [float(r) for r in log_ret]
    hc_vals = df["HC"].values
    indicators = [{"name": "HC Alpha", "type": "line",
                   "data": [[int(ts), float(v)] for ts, v in zip(ts_arr, hc_vals) if not np.isnan(v)]}]
    body = json.dumps({
        "strategy_name": STRATEGY_NAME, "symbol": SYMBOL, "interval": INTERVAL,
        "mode": "backtest", "code": open(__file__).read(),
        "trades": trades, "klines": klines, "indicators": indicators, "returns": returns,
    }).encode()
    requests.post("https://api.blave.org/openclaw/strategy/report", headers={
        "api-key": _env.get("blave_api_key", ""), "secret-key": _env.get("blave_secret_key", ""),
        "Content-Type": "application/json", "Content-Encoding": "gzip",
    }, data=gzip.compress(body), timeout=60).raise_for_status()
    print("Report uploaded.")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from datetime import datetime
    today = datetime.utcnow().strftime("%Y-%m-%d")
    end   = END if MODE == "backtest" else today
    print(f"Fetching data {START} → {end} ...")
    df = fetch_data(SYMBOL, START, end)
    print(f"  → {len(df):,} bars")

    bt = Backtest(df, BlaveStrategy, cash=BUDGET_USDT, commission=FEE, trade_on_close=True)

    # Step 1: 2D param scan → find plateau
    print("Running parameter scan ...")
    _, heatmap = bt.optimize(
        entry_th=PARAM_GRID,
        exit_th=PARAM_GRID,
        constraint=lambda p: p.exit_th < p.entry_th,
        maximize="Sharpe Ratio",
        return_heatmap=True,
    )
    best_entry, best_exit = _find_plateau(heatmap)
    print(f"Plateau: entry_th={best_entry:+.1f}  exit_th={best_exit:+.1f}")
    plot_heatmap(heatmap, best_entry, best_exit, SYMBOL)

    # Step 2: full backtest with plateau params
    stats = bt.run(entry_th=best_entry, exit_th=best_exit)
    print(stats[["Return [%]", "Sharpe Ratio", "Max. Drawdown [%]", "Win Rate [%]", "# Trades"]])
    bt.plot(filename=f"{SYMBOL}_{STRATEGY_NAME}_pnl.html", open_browser=False)

    result = _reconstruct_arrays(df, stats)
    regime_analysis(df, result)
    plot_regime(df, result, SYMBOL)
    plot_pnl(df, result, SYMBOL, entry_th=best_entry, exit_th=best_exit)
    upload_report(df, stats)
```

---

## Parameters

| Parameter | Value | Notes |
|---|---|---|
| `entry_th` | `1.0` | HC alpha must exceed this to open long (optimized via `bt.optimize`) |
| `exit_th` | `-0.5` | HC alpha must fall below this to close (optimized via `bt.optimize`) |
| `INTERVAL` | `1h` | HC signal + kline timeframe |
| `VOL_LOOKBACK` | `720` | 30 days × 24h rolling vol window |
| `VOL_TARGET` | `0.30` | 30% annualized target volatility |
| `VOL_FLOOR` | `0.02` | Minimum vol — prevents extreme leverage when market is calm |
| `BUDGET_USDT` | `1_000` | Set to your actual trading capital — backtest P&L reflects real dollars |
| `FEE` | `0.0005` | 0.05% per side (taker fee) |

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
- **Performance stack:** Rolling vol uses `pd.Series.rolling().std()` (Pandas Cython/C — fastest for window statistics). The entry/exit signal loop uses `@numba.njit` — this is the only loop that benefits from JIT because each bar depends on the previous bar's state (cannot be vectorized). Everything else (fwd_ret, vol-targeting, fees, returns) uses NumPy vectorized ops. First call triggers JIT compilation (~2–5 s, once per session). If numba is not installed: `pip install numba`

### Live Trading Execution Timing

The backtest computes `fwd_ret[i] = (close[i+1] - close[i]) / close[i]`, which means it assumes the order is **executed at bar i's close price** — the same bar where the signal fires.

In live trading, the correct sequence is:

```
bar i closes
  → fetch the latest signal
  → signal changed → place market order immediately
  → fill ≈ bar i+1 open (for liquid pairs like BTC, this is effectively bar i close)
```

**Do NOT wait for bar i+1 to close before placing the order.** Waiting an extra bar means your execution price is one full bar later than what the backtest assumes, causing live performance to diverge from backtest results.

---

### Parameter Selection: Plateau vs Peak

**Do not simply pick the highest Sharpe cell.** A single peak is often an overfitted outlier — it performs well in-sample but is fragile out-of-sample.

Instead, use `find_plateau()` to compute the **neighborhood mean Sharpe** for each cell (average of the cell and its surrounding valid cells within a 3×3 window). The cell with the highest neighborhood mean sits at the center of a stable region — a **parameter plateau** — where nearby combinations also perform well. This indicates robustness: small changes to the thresholds do not collapse performance.

The heatmap shows the same Sharpe grid twice. Left panel marks the **peak** (highest single cell); right panel marks the **plateau center** (cell whose neighborhood has the highest mean Sharpe). Both show the true Sharpe value in each cell — the difference is only which cell is highlighted. Prefer the plateau selection even if its raw Sharpe is slightly lower than the peak.
