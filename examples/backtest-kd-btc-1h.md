# Example: Backtest — KD Stochastic Golden/Death Cross (BTC 1h)

## Strategy Logic

Trade BTC on the 1-hour chart using the KD Stochastic Oscillator.

- **Entry:** %K crosses above %D (Golden Cross) → open long
- **Exit:** %K crosses below %D (Death Cross) → close long
- **Long only** — no short positions
- **Vol-targeting:** size each position to target 30% annualized volatility

KD formula:
1. Raw %K = (Close − LowestLow_N) / (HighestHigh_N − LowestLow_N) × 100
2. Slow %K = SMA(Raw %K, K_SMOOTH)
3. %D     = SMA(Slow %K, D_SMOOTH)

---

## Data Required

```
GET /kline?symbol=BTCUSDT&period=1h&start_date=<YYYY-MM-DD>&end_date=<YYYY-MM-DD>
```

Returns `[time, open, high, low, close]`. KD is computed locally from OHLCV — no additional endpoint needed.

For history beyond 1 year, send one request per year and concatenate.

---

## Full Backtest Code

```python
import sys, requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from backtesting import Backtest, Strategy
from dotenv import dotenv_values

_env = dotenv_values()

# ── Config ────────────────────────────────────────────────────────────────────
from datetime import datetime, timedelta, timezone

MODE          = "backtest"
STRATEGY_NAME = "btc_kd_long"
SYMBOL        = "BTCUSDT"
INTERVAL      = "1h"
START         = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
END           = None
D_SMOOTH      = 3           # %D smoothing — fixed, not optimized
VOL_TARGET    = 0.30
VOL_LOOKBACK  = 720         # 30 days × 24h
VOL_FLOOR     = 0.02
HOURS_PER_YEAR = 8760
FEE           = 0.0005
BUDGET_USDT   = 1_000       # set to your actual trading capital

K_PERIOD_SCAN = [5, 9, 14, 21, 34, 55]
K_SMOOTH_SCAN = [2, 3, 5, 8, 13]

_HDRS = {"api-key": _env.get("blave_api_key", ""), "secret-key": _env.get("blave_secret_key", "")}


# ── Fetch ─────────────────────────────────────────────────────────────────────
def fetch_historical(symbol, start, end):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.utcnow() if not end else datetime.strptime(end, "%Y-%m-%d")
    rows, cursor = [], s
    while cursor < e:
        chunk_end = min(cursor + timedelta(days=365), e)
        r = requests.get("https://api.blave.org/kline", headers=_HDRS, params={
            "symbol": symbol, "period": INTERVAL,
            "start_date": cursor.strftime("%Y-%m-%d"),
            "end_date":   chunk_end.strftime("%Y-%m-%d"),
        }, timeout=60)
        r.raise_for_status()
        rows.extend(r.json())
        cursor = chunk_end
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time").sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"})
    df["Volume"] = 0
    return df[["Open", "High", "Low", "Close", "Volume"]].astype(float)


# ── KD Computation (for visualization only) ───────────────────────────────────
def compute_kd(df, k_period, k_smooth, d_smooth):
    low_min  = df["Low"].rolling(k_period).min()
    high_max = df["High"].rolling(k_period).max()
    denom    = high_max - low_min
    raw_k    = pd.Series(
        np.where(denom > 0, (df["Close"] - low_min) / denom * 100, 50.0),
        index=df.index,
    )
    slow_k = raw_k.rolling(k_smooth).mean()
    d      = slow_k.rolling(d_smooth).mean()
    return slow_k, d


# ── Signal (pure function — identical in backtest and live) ──────────────────
def compute_signal(k: float, k_prev: float, d: float, d_prev: float, in_long: bool) -> str:
    """Returns desired position state: 'LONG' or 'FLAT'."""
    if np.isnan(k) or np.isnan(d) or np.isnan(k_prev) or np.isnan(d_prev):
        return "LONG" if in_long else "FLAT"
    if not in_long and k_prev <= d_prev and k > d:   # golden cross → enter
        return "LONG"
    if in_long and k_prev >= d_prev and k < d:        # death cross → exit
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
    k_period = 9
    k_smooth = 3
    d_smooth = 3

    def init(self):
        low_min  = pd.Series(self.data.Low).rolling(self.k_period).min().values
        high_max = pd.Series(self.data.High).rolling(self.k_period).max().values
        denom    = high_max - low_min
        raw_k    = np.where(denom > 0, (self.data.Close - low_min) / denom * 100, 50.0)
        slow_k   = pd.Series(raw_k).rolling(self.k_smooth).mean().values
        d_line   = pd.Series(slow_k).rolling(self.d_smooth).mean().values
        self.slow_k = self.I(lambda x: x, slow_k,         name="%K")
        self.d_line = self.I(lambda x: x, d_line,         name="%D")
        self.vol    = self.I(_vol_series,  self.data.Close, name="Vol")

    def next(self):
        k      = float(self.slow_k[-1])
        k_prev = float(self.slow_k[-2]) if len(self.slow_k) > 1 else np.nan
        d      = float(self.d_line[-1])
        d_prev = float(self.d_line[-2]) if len(self.d_line) > 1 else np.nan
        in_long = self.position.is_long
        sig    = compute_signal(k, k_prev, d, d_prev, in_long)
        size   = min(VOL_TARGET / max(float(self.vol[-1]), VOL_FLOOR), 0.99)
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


# ── Regime Analysis ───────────────────────────────────────────────────────────
def regime_analysis(df, result):
    strat_ret    = result["strat_ret"]
    realized_vol = result["realized_vol"]
    close        = df["Close"].values
    dates        = df.index

    ma_window = VOL_LOOKBACK * 200 // 30
    ma200     = pd.Series(close).rolling(ma_window).mean().values
    valid_ma  = ~np.isnan(ma200)
    vol_med   = np.nanmedian(realized_vol)
    valid_vol = ~np.isnan(realized_vol)

    def _stats(mask):
        r = strat_ret[mask]; r = r[~np.isnan(r)]
        if len(r) < 2: return None
        years   = len(r) / HOURS_PER_YEAR
        cum_r   = np.prod(1 + r) - 1
        ann_r   = (1 + cum_r) ** (1 / years) - 1 if years > 0 else np.nan
        ann_v   = r.std() * np.sqrt(HOURS_PER_YEAR)
        sh      = (r.mean() / r.std()) * np.sqrt(HOURS_PER_YEAR) if r.std() > 0 else np.nan
        cc      = np.cumprod(1 + r); pk = np.maximum.accumulate(cc)
        mdd     = ((cc - pk) / pk).min()
        n_tot   = len(strat_ret[~np.isnan(strat_ret)])
        return dict(ann_ret=ann_r, ann_vol=ann_v, sharpe=sh,
                    max_dd=mdd, pct_time=len(r) / n_tot)

    rows = []
    for yr in sorted(dates.year.unique()):
        s = _stats(dates.year == yr)
        if s: rows.append({"label": str(yr), **s})

    rows.append({"label": "─" * 20})
    bull = close > ma200
    for label, mask in [("Bull (price > MA200)", bull & valid_ma),
                         ("Bear (price < MA200)", ~bull & valid_ma)]:
        s = _stats(mask)
        if s: rows.append({"label": label, **s})

    rows.append({"label": "─" * 20})
    hv = realized_vol > vol_med
    for label, mask in [("High Vol (>median)",  hv & valid_vol),
                         ("Low  Vol (≤median)", ~hv & valid_vol)]:
        s = _stats(mask)
        if s: rows.append({"label": label, **s})

    hdr = f"  {'Regime':<22} {'Ann Ret':>9} {'Ann Vol':>9} {'Sharpe':>8} {'MDD':>8} {'Time%':>7}"
    print(f"\n{'─' * len(hdr)}\n  Regime Analysis\n{'─' * len(hdr)}")
    print(hdr); print('─' * len(hdr))
    for row in rows:
        if "ann_ret" not in row:
            print(f"  {row['label']}"); continue
        print(f"  {row['label']:<22} {row['ann_ret']*100:>8.1f}% {row['ann_vol']*100:>8.1f}%"
              f" {row['sharpe']:>8.2f} {row['max_dd']*100:>7.1f}% {row['pct_time']*100:>6.1f}%")
    print('─' * len(hdr))


# ── PnL Chart ─────────────────────────────────────────────────────────────────
def plot_pnl(df, result, slow_k, d_line, best_kp, best_ks, symbol):
    close  = df["Close"].values
    dates  = df.index
    cum    = result["cum"]
    pos    = result["position"]
    peak   = np.maximum.accumulate(cum)
    dd     = (cum - peak) / peak

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1, 1.2]})

    # Panel 1: Price + cumulative PnL
    ax1 = axes[0]; ax2 = ax1.twinx()
    ax1.plot(dates, close, color="#3498db", lw=1, alpha=0.7, label="Price")
    ax1.set_ylabel("Price (USD)", fontsize=11, color="#3498db")
    ax1.tick_params(axis="y", labelcolor="#3498db")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    ax2.plot(dates, (cum - 1) * 100, color="#2ecc71", lw=1.5, label="KD Strategy (+fees)")
    ax2.axhline(0, color="#888", lw=0.5, ls="--")
    ax2.set_ylabel("Strategy Return (%)", fontsize=11, color="#2ecc71")
    ax2.tick_params(axis="y", labelcolor="#2ecc71")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    prev = False
    for i, (date, inp) in enumerate(zip(dates, pos > 0)):
        if inp and not prev: start = date
        if not inp and prev: ax1.axvspan(start, date, alpha=0.08, color="#2ecc71")
        prev = inp
    if prev: ax1.axvspan(start, dates[-1], alpha=0.08, color="#2ecc71")

    l1, lb1 = ax1.get_legend_handles_labels()
    l2, lb2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lb1 + lb2, fontsize=10, loc="upper left")
    ax1.set_title(
        f"{symbol} — KD Strategy  K({best_kp},{best_ks})  D({D_SMOOTH})\n"
        f"Vol-Target {VOL_TARGET*100:.0f}%  |  Fee {FEE*100:.2f}%/side",
        fontsize=13,
    )

    # Panel 2: Drawdown
    axes[1].fill_between(dates, dd * 100, 0, color="#e74c3c", alpha=0.6)
    axes[1].set_ylabel("Drawdown (%)", fontsize=11)
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    axes[1].axhline(0, color="#888", lw=0.5)

    # Panel 3: KD lines + entry/exit markers
    valid = ~np.isnan(slow_k) & ~np.isnan(d_line)
    axes[2].plot(dates[valid], slow_k[valid], color="#f39c12", lw=0.9, label="%K")
    axes[2].plot(dates[valid], d_line[valid], color="#9b59b6", lw=0.9, label="%D")
    axes[2].axhline(80, color="#e74c3c", lw=0.7, ls="--", alpha=0.6, label="OB 80")
    axes[2].axhline(20, color="#2ecc71", lw=0.7, ls="--", alpha=0.6, label="OS 20")
    axes[2].set_ylabel("KD", fontsize=11)
    axes[2].set_ylim(-5, 105)
    axes[2].legend(fontsize=9, loc="upper right", ncol=2)

    plt.tight_layout()
    fname = f"{symbol}_kd_pnl.png"
    plt.savefig(fname, dpi=150)
    plt.show()
    print(f"Saved: {fname}")


# ── Regime Chart ──────────────────────────────────────────────────────────────
def plot_regime(df, result, symbol):
    strat_ret    = result["strat_ret"]
    realized_vol = result["realized_vol"]
    close        = df["Close"].values
    dates        = df.index
    ma_window    = VOL_LOOKBACK * 200 // 30
    ma200        = pd.Series(close).rolling(ma_window).mean().values
    valid_ma     = ~np.isnan(ma200)
    vol_med      = np.nanmedian(realized_vol)
    valid_vol    = ~np.isnan(realized_vol)
    bull         = close > ma200
    hv           = realized_vol > vol_med

    def _stats(mask):
        r = strat_ret[mask]; r = r[~np.isnan(r)]
        if len(r) < 2: return None
        years = len(r) / HOURS_PER_YEAR; cum_r = np.prod(1 + r) - 1
        ann_r = (1 + cum_r) ** (1 / years) - 1 if years > 0 else np.nan
        cc = np.cumprod(1 + r); pk = np.maximum.accumulate(cc)
        sh = (r.mean() / r.std()) * np.sqrt(HOURS_PER_YEAR) if r.std() > 0 else np.nan
        return dict(ann_ret=ann_r, sharpe=sh, max_dd=((cc - pk) / pk).min())

    groups = {
        "By Year":           [(str(yr), _stats(dates.year == yr))
                               for yr in sorted(dates.year.unique())],
        "Trend Regime":      [("Bull\n(>MA200)", _stats(bull & valid_ma)),
                               ("Bear\n(<MA200)", _stats(~bull & valid_ma))],
        "Volatility Regime": [("High Vol\n(>median)", _stats(hv & valid_vol)),
                               ("Low  Vol\n(≤median)", _stats(~hv & valid_vol))],
    }
    groups = {k: [(lb, s) for lb, s in v if s is not None] for k, v in groups.items()}

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    for ax, (gname, items) in zip(axes, groups.items()):
        labels  = [lb for lb, _ in items]
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
        ax.set_title(gname, fontsize=13, fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
        ax.set_ylabel("Value", fontsize=10); ax.legend(fontsize=9)
        all_vals = ann_ret + sharpe + mdd
        ax.set_ylim(min(all_vals) - 5, max(all_vals) + 8)

    fig.suptitle(f"{symbol} — KD Regime Analysis", fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    fname = f"{symbol}_kd_regime.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved: {fname}")


# ── Heatmap Plot ──────────────────────────────────────────────────────────────
def plot_heatmap(heatmap, best_kp, best_ks, symbol):
    grid_df  = heatmap.unstack()           # rows=k_period, cols=k_smooth
    kp_vals  = grid_df.index.tolist()
    ks_vals  = grid_df.columns.tolist()
    grid     = grid_df.values.astype(float)
    peak_idx = np.unravel_index(np.nanargmax(grid), grid.shape)
    plat_idx = (kp_vals.index(best_kp), ks_vals.index(best_ks))

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ax, mark_idx, title, note in [
        (axes[0], peak_idx, "Peak — highest single Sharpe",
         f"K_PERIOD={kp_vals[peak_idx[0]]}, K_SMOOTH={ks_vals[peak_idx[1]]}\n"
         f"Sharpe={grid[peak_idx]:.2f} — may be overfitted if isolated"),
        (axes[1], plat_idx, "Plateau — most stable region",
         f"K_PERIOD={best_kp}, K_SMOOTH={best_ks}\n"
         f"Sharpe={grid[plat_idx]:.2f} — neighbors also perform well → more robust"),
    ]:
        masked = np.ma.masked_invalid(grid)
        cmap = plt.cm.RdYlGn.copy(); cmap.set_bad(color="#cccccc")
        vals = grid[~np.isnan(grid)]
        im = ax.imshow(masked, cmap=cmap, vmin=min(0, vals.min()),
                       vmax=np.percentile(vals, 95), aspect="auto")
        ax.add_patch(plt.Rectangle(
            (mark_idx[1] - 0.5, mark_idx[0] - 0.5), 1, 1,
            fill=False, edgecolor="gold", linewidth=3,
        ))
        for i in range(len(kp_vals)):
            for j in range(len(ks_vals)):
                v = grid[i, j]
                ax.text(j, i, f"{v:.2f}" if not np.isnan(v) else "N/A",
                        ha="center", va="center", fontsize=9,
                        color="#888" if np.isnan(v) else "black")
        ax.set_xticks(range(len(ks_vals)));  ax.set_xticklabels(ks_vals)
        ax.set_yticks(range(len(kp_vals)));  ax.set_yticklabels(kp_vals)
        ax.set_xlabel("K_SMOOTH (slow %K period)")
        ax.set_ylabel("K_PERIOD (stochastic lookback)")
        ax.set_title(f"{symbol} — {title}\n{note}", fontsize=10)
        plt.colorbar(im, ax=ax, label="Sharpe Ratio")

    plt.suptitle("Same Sharpe grid, different selection method — prefer Plateau", fontsize=12)
    plt.tight_layout()
    fname = f"{symbol}_kd_heatmap.png"
    plt.savefig(fname, dpi=150)
    plt.show()
    print(f"Saved: {fname}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = fetch_historical(SYMBOL, START, END)
    print(f"Bars loaded: {len(df)}")

    # Step 1: optimize K_PERIOD × K_SMOOTH → find plateau
    print("Optimizing K_PERIOD × K_SMOOTH...")
    bt = Backtest(df, BlaveStrategy, cash=BUDGET_USDT, commission=FEE, trade_on_close=True)
    _, heatmap = bt.optimize(
        k_period=K_PERIOD_SCAN,
        k_smooth=K_SMOOTH_SCAN,
        maximize="Sharpe Ratio",
        return_heatmap=True,
    )
    best_kp, best_ks = _find_plateau(heatmap)
    print(f"Plateau: K_PERIOD={best_kp}, K_SMOOTH={best_ks}")
    plot_heatmap(heatmap, best_kp, best_ks, SYMBOL)

    # Step 2: full backtest with plateau parameters
    BlaveStrategy.k_period = best_kp
    BlaveStrategy.k_smooth = best_ks
    bt2   = Backtest(df, BlaveStrategy, cash=BUDGET_USDT, commission=FEE, trade_on_close=True)
    stats = bt2.run()
    print(stats[["Return [%]", "Sharpe Ratio", "Max. Drawdown [%]", "Win Rate [%]", "# Trades"]])

    result           = _reconstruct_arrays(df, stats)
    slow_k, d_line   = compute_kd(df, best_kp, best_ks, D_SMOOTH)

    regime_analysis(df, result)
    plot_regime(df, result, SYMBOL)
    plot_pnl(df, result, slow_k.values, d_line.values, best_kp, best_ks, SYMBOL)
```

---

## Parameters

| Parameter | Default | Notes |
|---|---|---|
| `K_PERIOD_SCAN` | `[5,9,14,21,34,55]` | Stochastic lookback values swept during optimization |
| `K_SMOOTH_SCAN` | `[2,3,5,8,13]` | Slow %K smoothing values swept during optimization |
| `D_SMOOTH` | `3` | %D smoothing (SMA of slow %K) — fixed, not optimized |
| `INTERVAL` | `1h` | Kline timeframe |
| `VOL_LOOKBACK` | `720` | 30 days × 24h rolling vol window |
| `VOL_TARGET` | `0.30` | 30% annualized vol target |
| `FEE` | `0.0005` | 0.05% per side (taker fee) |
| `BUDGET_USDT` | `1000` | Starting capital for backtest |

---

## Notes

- **Long only** — no short positions
- **Parameter scan** sweeps K_PERIOD (5/9/14/21/34/55) × K_SMOOTH (2/3/5/8/13); D_SMOOTH is fixed at 3. The plateau selection (neighborhood mean Sharpe) is preferred over the single best cell — see HC backtest example for explanation
- **OB/OS filter (optional):** only enter golden cross when %K < 20 (oversold zone) for a stricter variant. Not implemented by default — add `and k < 20` to the golden cross condition in `compute_signal`
- **Smoothing method:** this example uses SMA for both %K and %D, matching the classic formula. EWM (`pd.Series.ewm(span=k_smooth)`) gives more weight to recent bars and is common in real-time systems; swap in if preferred
- **Performance stack:** rolling vol via Pandas rolling (C/Cython), crossover loop via pure Python (stateful, can't vectorize — but fast enough for any reasonable history length), everything else NumPy vectorized

### Live Execution Timing

Backtest uses `fwd_ret[i] = (close[i+1] - close[i]) / close[i]`, meaning the order is filled at bar i's close price — the same bar where the crossover fires.

In live trading:
```
bar i closes
  → KD recomputes with new close
  → crossover detected → place market order immediately
  → fill ≈ bar i+1 open (for BTC 1h this is effectively bar i close)
```

Do NOT wait for bar i+1 to close. Waiting an extra bar introduces one-bar slippage that compounds over hundreds of trades and causes live PnL to diverge from backtest.

### KD vs RSI

KD (Stochastic) measures where the close sits within the recent high-low range; RSI measures the speed of price change. KD tends to generate more signals and responds faster to reversals, making it better suited for range-bound conditions. In strong trending markets, frequent death-cross exits can cut profitable trades short — consider adding a trend filter (e.g. price > MA200 to only trade bull regime signals) if regime analysis shows poor bear/high-vol performance.
