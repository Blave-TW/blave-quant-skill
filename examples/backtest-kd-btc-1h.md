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
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numba
from dotenv import dotenv_values

_env = dotenv_values()

# ── Config ────────────────────────────────────────────────────────────────────
from datetime import datetime, timedelta, timezone

SYMBOL         = "BTCUSDT"
END_DATE       = datetime.now(timezone.utc).strftime("%Y-%m-%d")
START_DATE     = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
PERIOD         = "1h"
K_PERIOD       = 9          # stochastic lookback window (raw %K)
K_SMOOTH       = 3          # %K smoothing period (SMA → slow %K)
D_SMOOTH       = 3          # %D smoothing period (SMA of slow %K)
TARGET_VOL     = 0.30       # 30% annualized target volatility
MAX_LEV        = 2.0        # position size cap
VOL_WINDOW     = 720        # rolling vol window: 30 days × 24h
HOURS_PER_YEAR = 8760
FEE            = 0.0005     # 0.05% per side (taker fee)

API_BASE   = "https://api.blave.org"
API_KEY    = _env["blave_api_key"]
API_SECRET = _env["blave_secret_key"]
HEADERS    = {"api-key": API_KEY, "secret-key": API_SECRET}


# ── Fetch ─────────────────────────────────────────────────────────────────────
def load_kline(symbol, start, end, period):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end,   "%Y-%m-%d")
    rows = []
    cursor = s
    while cursor < e:
        chunk_end = min(cursor + timedelta(days=365), e)
        r = requests.get(f"{API_BASE}/kline", headers=HEADERS, params={
            "symbol": symbol, "period": period,
            "start_date": cursor.strftime("%Y-%m-%d"),
            "end_date":   chunk_end.strftime("%Y-%m-%d"),
        }, timeout=20)
        r.raise_for_status()
        rows.extend(r.json())
        cursor = chunk_end

    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close"])
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time").sort_index().drop_duplicates()
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    return df


# ── KD Computation ────────────────────────────────────────────────────────────
def compute_kd(df, k_period, k_smooth, d_smooth):
    low_min  = df["low"].rolling(k_period).min()
    high_max = df["high"].rolling(k_period).max()
    denom    = high_max - low_min
    raw_k    = pd.Series(
        np.where(denom > 0, (df["close"] - low_min) / denom * 100, 50.0),
        index=df.index,
    )
    slow_k = raw_k.rolling(k_smooth).mean()
    d      = slow_k.rolling(d_smooth).mean()
    return slow_k, d


# ── Helpers ───────────────────────────────────────────────────────────────────
def _sharpe(r):
    s = r.std()
    if s == 0:
        return np.nan
    return (r.mean() / s) * np.sqrt(HOURS_PER_YEAR)


# ── Numba: crossover signal loop ──────────────────────────────────────────────
# Each bar depends on the previous bar's K/D values and position state →
# must be sequential; Numba njit gives ~20× speedup over pure Python.

@numba.njit(cache=True)
def _kd_signal_loop(k, d):
    n = len(k)
    position = np.zeros(n)
    in_pos = False
    for i in range(1, n):
        ki,  di  = k[i],   d[i]
        kp,  dp  = k[i-1], d[i-1]
        if np.isnan(ki) or np.isnan(di) or np.isnan(kp) or np.isnan(dp):
            position[i] = 1.0 if in_pos else 0.0
            continue
        if not in_pos and kp <= dp and ki > di:   # golden cross → enter
            in_pos = True
        elif in_pos and kp >= dp and ki < di:     # death cross → exit
            in_pos = False
        position[i] = 1.0 if in_pos else 0.0
    return position


# ── Backtest ──────────────────────────────────────────────────────────────────
def run_backtest(df, k_period=None, k_smooth=None, d_smooth=None):
    k_period = k_period or K_PERIOD
    k_smooth = k_smooth or K_SMOOTH
    d_smooth = d_smooth or D_SMOOTH

    slow_k, d = compute_kd(df, k_period, k_smooth, d_smooth)
    close = df["close"].values.astype(np.float64)
    k_arr = slow_k.values.astype(np.float64)
    d_arr = d.values.astype(np.float64)
    n     = len(df)

    log_ret = np.concatenate([[0.0], np.log(close[1:] / close[:-1])])
    fwd_ret = np.empty(n)
    fwd_ret[:-1] = np.diff(close) / close[:-1]
    fwd_ret[-1]  = 0.0

    realized_vol = pd.Series(log_ret).rolling(VOL_WINDOW).std().values * np.sqrt(HOURS_PER_YEAR)
    position     = _kd_signal_loop(k_arr, d_arr)

    vol_scalar = np.where(
        (realized_vol > 0) & ~np.isnan(realized_vol),
        np.clip(TARGET_VOL / realized_vol, 0, MAX_LEV),
        1.0,
    )
    sized     = position * vol_scalar
    fee_cost  = np.abs(np.diff(sized, prepend=0)) * FEE
    strat_ret = sized * fwd_ret - fee_cost

    r   = strat_ret[~np.isnan(strat_ret)]
    cum = np.cumprod(1 + r)
    pk  = np.maximum.accumulate(cum)
    total_years = len(r) / HOURS_PER_YEAR

    total_return = cum[-1] - 1
    ann_ret      = (1 + total_return) ** (1 / total_years) - 1
    ann_vol      = r.std() * np.sqrt(HOURS_PER_YEAR)
    sharpe       = _sharpe(r)
    max_dd       = ((cum - pk) / pk).min()

    entries = np.where(np.diff(position.astype(int)) == 1)[0] + 1
    exits   = np.where(np.diff(position.astype(int)) == -1)[0] + 1
    # Do NOT force-close the last open position — leave it open if still in trade at end of data

    trade_returns = []
    for e_i, x_i in zip(entries, exits):
        tr = strat_ret[e_i:x_i]
        tr = tr[~np.isnan(tr)]
        if len(tr) > 0:
            trade_returns.append(np.prod(1 + tr) - 1)

    trade_returns  = np.array(trade_returns)
    n_trades       = len(trade_returns)
    win_rate       = (trade_returns > 0).mean() if n_trades > 0 else np.nan
    avg_win        = trade_returns[trade_returns > 0].mean() if (trade_returns > 0).any() else np.nan
    avg_loss       = trade_returns[trade_returns <= 0].mean() if (trade_returns <= 0).any() else np.nan
    avg_trades_yr  = n_trades / total_years

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
        "position":      position,
        "sized":         sized,
        "strat_ret":     strat_ret,
        "realized_vol":  realized_vol,
        "cum":           cum,
        "slow_k":        slow_k.values,
        "d":             d.values,
    }


# ── Regime Analysis ───────────────────────────────────────────────────────────
def regime_analysis(df, result):
    strat_ret    = result["strat_ret"]
    realized_vol = result["realized_vol"]
    close        = df["close"].values
    dates        = df.index

    ma_window = VOL_WINDOW * 200 // 30
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
        sh      = _sharpe(r)
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
def plot_pnl(df, result, symbol):
    close  = df["close"].values
    dates  = df.index
    cum    = result["cum"]
    pos    = result["position"]
    slow_k = result["slow_k"]
    d_line = result["d"]
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
        f"{symbol} — KD Strategy  K({K_PERIOD},{K_SMOOTH})  D({D_SMOOTH})\n"
        f"Vol-Target {TARGET_VOL*100:.0f}%  |  Max Lev {MAX_LEV}x  |  Fee {FEE*100:.2f}%/side",
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
    close        = df["close"].values
    dates        = df.index
    ma_window    = VOL_WINDOW * 200 // 30
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
        return dict(ann_ret=ann_r, sharpe=_sharpe(r), max_dd=((cc - pk) / pk).min())

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


# ── 2D Parameter Scan (K_PERIOD × K_SMOOTH) ──────────────────────────────────
K_PERIOD_SCAN = [5, 9, 14, 21, 34, 55]
K_SMOOTH_SCAN = [2, 3, 5, 8, 13]

def param_scan(df):
    grid = np.full((len(K_PERIOD_SCAN), len(K_SMOOTH_SCAN)), np.nan)
    for i, kp in enumerate(K_PERIOD_SCAN):
        for j, ks in enumerate(K_SMOOTH_SCAN):
            res = run_backtest(df, k_period=kp, k_smooth=ks, d_smooth=D_SMOOTH)
            if res is not None and not np.isnan(res["sharpe"]):
                grid[i, j] = res["sharpe"]
    return grid


def find_plateau(grid, window=1):
    rows, cols = grid.shape
    nbr_mean = np.full((rows, cols), np.nan)
    for i in range(rows):
        for j in range(cols):
            if np.isnan(grid[i, j]): continue
            neighbors = [grid[i+di, j+dj]
                         for di in range(-window, window+1)
                         for dj in range(-window, window+1)
                         if 0 <= i+di < rows and 0 <= j+dj < cols
                         and not np.isnan(grid[i+di, j+dj])]
            if neighbors: nbr_mean[i, j] = np.mean(neighbors)
    best = np.unravel_index(np.nanargmax(nbr_mean), nbr_mean.shape)
    return best, nbr_mean


def plot_heatmap(grid, nbr_mean, plateau_idx, symbol):
    peak_idx = np.unravel_index(np.nanargmax(grid), grid.shape)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, mark_idx, title, note in [
        (axes[0], peak_idx,    "Peak — highest single Sharpe",
         f"K_PERIOD={K_PERIOD_SCAN[mark_idx[0]]}, K_SMOOTH={K_SMOOTH_SCAN[mark_idx[1]]}\n"
         f"Sharpe={grid[mark_idx]:.2f} — may be overfitted if isolated"),
        (axes[1], plateau_idx, "Plateau — most stable region",
         f"K_PERIOD={K_PERIOD_SCAN[plateau_idx[0]]}, K_SMOOTH={K_SMOOTH_SCAN[plateau_idx[1]]}\n"
         f"Sharpe={grid[plateau_idx]:.2f} — neighbors also perform well → more robust"),
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
        for i in range(len(K_PERIOD_SCAN)):
            for j in range(len(K_SMOOTH_SCAN)):
                v = grid[i, j]
                ax.text(j, i, f"{v:.2f}" if not np.isnan(v) else "N/A",
                        ha="center", va="center", fontsize=9,
                        color="#888" if np.isnan(v) else "black")
        ax.set_xticks(range(len(K_SMOOTH_SCAN)));  ax.set_xticklabels(K_SMOOTH_SCAN)
        ax.set_yticks(range(len(K_PERIOD_SCAN)));  ax.set_yticklabels(K_PERIOD_SCAN)
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
    print(f"Loading kline for {SYMBOL} ({START_DATE} → {END_DATE}, {PERIOD})...")
    df = load_kline(SYMBOL, START_DATE, END_DATE, PERIOD)
    print(f"Bars loaded: {len(df)}")

    # Step 1: 2D scan → find plateau
    print("Running 2D parameter scan (K_PERIOD × K_SMOOTH)...")
    grid = param_scan(df)
    plateau_idx, nbr_mean = find_plateau(grid, window=1)

    best_kp = K_PERIOD_SCAN[plateau_idx[0]]
    best_ks = K_SMOOTH_SCAN[plateau_idx[1]]
    print(f"Plateau: K_PERIOD={best_kp}, K_SMOOTH={best_ks}  "
          f"(neighborhood mean Sharpe={nbr_mean[plateau_idx]:.2f})")

    plot_heatmap(grid, nbr_mean, plateau_idx, SYMBOL)

    # Step 2: full backtest with plateau parameters
    K_PERIOD, K_SMOOTH = best_kp, best_ks
    result = run_backtest(df, k_period=K_PERIOD, k_smooth=K_SMOOTH, d_smooth=D_SMOOTH)

    print(f"\nResults — KD({K_PERIOD},{K_SMOOTH},{D_SMOOTH}):")
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

    regime_analysis(df, result)
    plot_regime(df, result, SYMBOL)
    plot_pnl(df, result, SYMBOL)
```

---

## Parameters

| Parameter | Default | Notes |
|---|---|---|
| `K_PERIOD` | `9` | Stochastic lookback — lower = faster, more signals |
| `K_SMOOTH` | `3` | Slow %K smoothing (SMA) — higher = smoother |
| `D_SMOOTH` | `3` | %D smoothing (SMA of slow %K) — fixed at 3 in scan |
| `PERIOD` | `1h` | Kline timeframe |
| `VOL_WINDOW` | `720` | 30 days × 24h rolling vol |
| `TARGET_VOL` | `0.30` | 30% annualized target |
| `MAX_LEV` | `2.0` | Position size cap |
| `FEE` | `0.0005` | 0.05% per side (taker fee) |

---

## Notes

- **Long only** — no short positions
- **Parameter scan** sweeps K_PERIOD (5/9/14/21/34/55) × K_SMOOTH (2/3/5/8/13); D_SMOOTH is fixed at 3. The plateau selection (neighborhood mean Sharpe) is preferred over the single best cell — see HC backtest example for explanation
- **OB/OS filter (optional):** only enter golden cross when %K < 20 (oversold zone) for a stricter variant. Not implemented by default — add `and ki < 20` to the golden cross condition in `_kd_signal_loop`
- **Smoothing method:** this example uses SMA for both %K and %D, matching the classic formula. EWM (`pd.Series.ewm(span=k_smooth)`) gives more weight to recent bars and is common in real-time systems; swap in if preferred
- **Performance stack:** same as HC backtest — rolling vol via Pandas rolling (C/Cython), crossover loop via `@numba.njit` (stateful, can't vectorize), everything else NumPy vectorized

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
