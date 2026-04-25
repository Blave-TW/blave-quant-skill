# Example: Strategy Validation — MCPT + Out-of-Sample (KD vs Taker Intensity)

## What This Does

Validates two DOGE 1h long-only strategies side by side using:

1. **IS (In-Sample) Parameter Optimization** — 2D param scan on the first 2 years to find the most robust (plateau) parameters for each strategy
2. **OOS (Out-of-Sample) Validation** — run the IS-selected params on the held-out final year; a strategy with real edge should degrade gracefully, not collapse
3. **MCPT (Monte Carlo Permutation Test)** — shuffle the position array 1000 times, recompute Sharpe on each shuffle; p-value = fraction of shuffled Sharpes ≥ actual OOS Sharpe; p < 0.05 means the timing adds statistically significant value

**Strategies compared:**

| | KD Stochastic | Taker Intensity (多空力道) |
|---|---|---|
| Signal source | Price-derived (OHLCV) | Market microstructure (Blave alpha) |
| Entry | K crosses above D | alpha > ENTRY_TH |
| Exit | K crosses below D | alpha < EXIT_TH |
| Params scanned | K_PERIOD × K_SMOOTH | ENTRY_TH × EXIT_TH |

Same DOGE 1h data, same vol-targeting, same fees — apples-to-apples.

---

## Data Required

```
GET /kline?symbol=DOGEUSDT&period=1h                          (for KD + fwd_ret)
GET /taker_intensity/get_alpha?symbol=DOGEUSDT&period=1h      (for TI signal)
```

IS: trailing 3 → 1 year ago | OOS: trailing 1 year → today

---

## Full Code

```python
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numba
from datetime import datetime, timedelta, timezone
from dotenv import dotenv_values

_env = dotenv_values()

# ── Date Ranges ───────────────────────────────────────────────────────────────
_now      = datetime.now(timezone.utc)
END_DATE  = _now.strftime("%Y-%m-%d")
OOS_START = (_now - timedelta(days=365)).strftime("%Y-%m-%d")
IS_START  = (_now - timedelta(days=3 * 365)).strftime("%Y-%m-%d")
# IS : [IS_START,  OOS_START)  — 2 years
# OOS: [OOS_START, END_DATE)   — 1 year

# ── Strategy Params ───────────────────────────────────────────────────────────
# KD
KD_PERIOD_SCAN = [5, 9, 14, 21, 34]
KD_SMOOTH_SCAN = [2, 3, 5, 8]
D_SMOOTH       = 3

# TI (same threshold grid as HC example)
TI_THRESHOLDS  = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]

# Shared backtest settings
TARGET_VOL     = 0.30
MAX_LEV        = 2.0
VOL_WINDOW     = 720        # 30 days × 24h
HOURS_PER_YEAR = 8760
FEE            = 0.0005
N_PERMUTATIONS = 2000

API_BASE   = "https://api.blave.org"
API_KEY    = _env["blave_api_key"]
API_SECRET = _env["blave_secret_key"]
HEADERS    = {"api-key": API_KEY, "secret-key": API_SECRET}


# ── Fetch ─────────────────────────────────────────────────────────────────────
def _fetch_year_chunks(endpoint, params):
    s = datetime.strptime(params["start_date"], "%Y-%m-%d")
    e = datetime.strptime(params["end_date"],   "%Y-%m-%d")
    out = []
    while s < e:
        chunk_end = min(s + timedelta(days=365), e)
        r = requests.get(f"{API_BASE}/{endpoint}", headers=HEADERS, params={
            **params,
            "start_date": s.strftime("%Y-%m-%d"),
            "end_date":   chunk_end.strftime("%Y-%m-%d"),
        }, timeout=20)
        r.raise_for_status()
        out.append(r.json())
        s = chunk_end
    return out


def load_kline(start, end):
    chunks = _fetch_year_chunks("kline", {"symbol": "DOGEUSDT", "period": "1h",
                                           "start_date": start, "end_date": end})
    rows = [row for chunk in chunks for row in chunk]
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close"])
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time").sort_index().drop_duplicates()
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    return df


def load_ti(start, end):
    chunks = _fetch_year_chunks("taker_intensity/get_alpha",
                                {"symbol": "DOGEUSDT", "period": "1h",
                                 "start_date": start, "end_date": end})
    ts, alphas = [], []
    for chunk in chunks:
        data = chunk.get("data", {})
        ts.extend(data.get("timestamp", []))
        alphas.extend(data.get("alpha", []))
    df = pd.DataFrame({"time": pd.to_datetime(ts, unit="s", utc=True), "ti": alphas})
    df = df.set_index("time").sort_index().drop_duplicates()
    df["ti"] = pd.to_numeric(df["ti"], errors="coerce")
    return df


# ── Signal Computation ────────────────────────────────────────────────────────
def compute_kd(df, k_period, k_smooth, d_smooth=D_SMOOTH):
    low_min  = df["low"].rolling(k_period).min()
    high_max = df["high"].rolling(k_period).max()
    denom    = high_max - low_min
    raw_k    = pd.Series(
        np.where(denom > 0, (df["close"] - low_min) / denom * 100, 50.0),
        index=df.index,
    )
    slow_k = raw_k.rolling(k_smooth).mean()
    d      = slow_k.rolling(d_smooth).mean()
    return slow_k.values, d.values


@numba.njit(cache=True)
def _kd_signal_loop(k, d):
    n = len(k); position = np.zeros(n); in_pos = False
    for i in range(1, n):
        ki, di, kp, dp = k[i], d[i], k[i-1], d[i-1]
        if np.isnan(ki) or np.isnan(di) or np.isnan(kp) or np.isnan(dp):
            position[i] = 1.0 if in_pos else 0.0; continue
        if not in_pos and kp <= dp and ki > di:  in_pos = True
        elif in_pos  and kp >= dp and ki < di:   in_pos = False
        position[i] = 1.0 if in_pos else 0.0
    return position


@numba.njit(cache=True)
def _ti_signal_loop(signal, entry_th, exit_th):
    n = len(signal); position = np.zeros(n); in_pos = False
    for i in range(n):
        if np.isnan(signal[i]):
            position[i] = 1.0 if in_pos else 0.0; continue
        if not in_pos and signal[i] > entry_th:  in_pos = True
        elif in_pos  and signal[i] < exit_th:    in_pos = False
        position[i] = 1.0 if in_pos else 0.0
    return position


# ── Core Backtest Engine (shared) ─────────────────────────────────────────────
def _run(close, position):
    """Given close prices and a position array, return strategy metrics."""
    n       = len(close)
    log_ret = np.concatenate([[0.0], np.log(close[1:] / close[:-1])])
    fwd_ret = np.empty(n)
    fwd_ret[:-1] = np.diff(close) / close[:-1]
    fwd_ret[-1]  = 0.0

    realized_vol = pd.Series(log_ret).rolling(VOL_WINDOW).std().values * np.sqrt(HOURS_PER_YEAR)
    vol_scalar   = np.where(
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
    total_years  = len(r) / HOURS_PER_YEAR
    total_return = cum[-1] - 1
    ann_ret      = (1 + total_return) ** (1 / total_years) - 1
    sharpe       = (r.mean() / r.std()) * np.sqrt(HOURS_PER_YEAR) if r.std() > 0 else np.nan
    max_dd       = ((cum - pk) / pk).min()
    return dict(sharpe=sharpe, ann_ret=ann_ret, max_dd=max_dd,
                cum=cum, strat_ret=strat_ret, position=position)


# ── MCPT ──────────────────────────────────────────────────────────────────────
def mcpt(close, position, n=N_PERMUTATIONS):
    """
    Permute the forward return series (not positions).
    Position is held fixed, so fees and vol-scaling are identical for all permutations.
    Null: the return periods selected by this strategy are no better than random.
    p-value: fraction of permuted Sharpes >= actual OOS Sharpe.

    Why not permute position?
    A random shuffle of a binary 0/1 array produces ~N*p*(1-p) transitions vs the
    strategy's much smaller number. With FEE=0.0005 that creates 30-40x more fee drag
    on every permutation, forcing all permuted Sharpes deeply negative and producing
    a biased p-value regardless of whether the strategy has real edge.
    """
    log_ret = np.concatenate([[0.0], np.log(close[1:] / close[:-1])])
    fwd_ret = np.concatenate([np.diff(close) / close[:-1], [0.0]])

    realized_vol = pd.Series(log_ret).rolling(VOL_WINDOW).std().values * np.sqrt(HOURS_PER_YEAR)
    vol_scalar   = np.where(
        (realized_vol > 0) & ~np.isnan(realized_vol),
        np.clip(TARGET_VOL / realized_vol, 0, MAX_LEV),
        1.0,
    )
    sized    = position * vol_scalar
    fee_cost = np.abs(np.diff(sized, prepend=0)) * FEE  # identical for all permutations

    def _sharpe_from_ret(ret):
        sr = sized * ret - fee_cost
        r  = sr[~np.isnan(sr)]
        return (r.mean() / r.std()) * np.sqrt(HOURS_PER_YEAR) if r.std() > 0 else np.nan

    actual  = _sharpe_from_ret(fwd_ret)
    dist    = np.array([_sharpe_from_ret(np.random.permutation(fwd_ret)) for _ in range(n)])
    p_value = float((dist >= actual).mean())
    return actual, p_value, dist


# ── IS Param Scans ────────────────────────────────────────────────────────────
def find_plateau(grid, row_vals, col_vals, window=1):
    rows, cols  = grid.shape
    nbr_mean    = np.full((rows, cols), np.nan)
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
    return best, nbr_mean, row_vals[best[0]], col_vals[best[1]]


def kd_param_scan(df_kline):
    grid = np.full((len(KD_PERIOD_SCAN), len(KD_SMOOTH_SCAN)), np.nan)
    close = df_kline["close"].values.astype(np.float64)
    for i, kp in enumerate(KD_PERIOD_SCAN):
        for j, ks in enumerate(KD_SMOOTH_SCAN):
            k_arr, d_arr = compute_kd(df_kline, kp, ks)
            pos = _kd_signal_loop(k_arr, d_arr)
            res = _run(close, pos)
            if not np.isnan(res["sharpe"]): grid[i, j] = res["sharpe"]
    return grid


def ti_param_scan(df_kline, df_ti):
    df = df_kline[["close"]].join(df_ti[["ti"]], how="inner").dropna(subset=["close"])
    close = df["close"].values.astype(np.float64)
    ti    = df["ti"].values.astype(np.float64)
    n     = len(TI_THRESHOLDS)
    grid  = np.full((n, n), np.nan)
    for i, entry in enumerate(TI_THRESHOLDS):
        for j, exit_ in enumerate(TI_THRESHOLDS):
            if exit_ > entry: continue
            pos = _ti_signal_loop(ti, entry, exit_)
            res = _run(close, pos)
            if not np.isnan(res["sharpe"]): grid[i, j] = res["sharpe"]
    return grid, df


# ── Chart ─────────────────────────────────────────────────────────────────────
def plot_results(symbol, results):
    """
    results: dict with keys "kd" and "ti", each containing:
      is_res, oos_res, mcpt_actual, mcpt_pvalue, mcpt_dist,
      is_dates, oos_dates, is_label, oos_label
    """
    fig = plt.figure(figsize=(16, 13))
    fig.suptitle(f"{symbol} — Strategy Validation: KD vs Taker Intensity",
                 fontsize=14, fontweight="bold", y=0.98)

    gs = fig.add_gridspec(3, 2, hspace=0.45, wspace=0.3)

    for col, (key, label, color) in enumerate([
        ("kd", "KD Stochastic",     "#3498db"),
        ("ti", "Taker Intensity",   "#e67e22"),
    ]):
        r = results[key]

        # Row 0: IS PnL
        ax_is = fig.add_subplot(gs[0, col])
        ax_is.plot(r["is_dates"], (r["is_res"]["cum"] - 1) * 100, color=color, lw=1.5)
        ax_is.axhline(0, color="#888", lw=0.6, ls="--")
        ax_is.set_title(
            f"{label} — IS (2y)\n"
            f"Sharpe={r['is_res']['sharpe']:.2f}  "
            f"Ann={r['is_res']['ann_ret']*100:.1f}%  "
            f"MDD={r['is_res']['max_dd']*100:.1f}%",
            fontsize=10,
        )
        ax_is.set_ylabel("Return (%)")
        ax_is.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))

        # Row 1: OOS PnL
        ax_oos = fig.add_subplot(gs[1, col])
        oos_color = "#2ecc71" if r["oos_res"]["sharpe"] > 0 else "#e74c3c"
        ax_oos.plot(r["oos_dates"], (r["oos_res"]["cum"] - 1) * 100, color=oos_color, lw=1.5)
        ax_oos.axhline(0, color="#888", lw=0.6, ls="--")
        sig_str = f"p={r['mcpt_pvalue']:.3f} {'✅' if r['mcpt_pvalue'] < 0.05 else '❌'}"
        ax_oos.set_title(
            f"{label} — OOS (1y)\n"
            f"Sharpe={r['oos_res']['sharpe']:.2f}  "
            f"Ann={r['oos_res']['ann_ret']*100:.1f}%  "
            f"MDD={r['oos_res']['max_dd']*100:.1f}%  {sig_str}",
            fontsize=10,
        )
        ax_oos.set_ylabel("Return (%)")
        ax_oos.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))

        # Row 2: MCPT distribution
        ax_mc = fig.add_subplot(gs[2, col])
        ax_mc.hist(r["mcpt_dist"], bins=40, color="#95a5a6", alpha=0.7, edgecolor="white")
        ax_mc.axvline(r["mcpt_actual"], color="#e74c3c", lw=2,
                      label=f"Actual={r['mcpt_actual']:.2f}")
        pct = np.percentile(r["mcpt_dist"], 95)
        ax_mc.axvline(pct, color="#f39c12", lw=1.5, ls="--",
                      label=f"95th pct={pct:.2f}")
        ax_mc.set_title(
            f"MCPT — OOS ({N_PERMUTATIONS} permutations)\np={r['mcpt_pvalue']:.3f}  "
            f"{'Significant (p<0.05)' if r['mcpt_pvalue'] < 0.05 else 'Not significant'}",
            fontsize=10,
        )
        ax_mc.set_xlabel("Permuted Sharpe"); ax_mc.set_ylabel("Count")
        ax_mc.legend(fontsize=9)

    fname = f"{symbol}_mcpt_oos.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved: {fname}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"IS : {IS_START} → {OOS_START}")
    print(f"OOS: {OOS_START} → {END_DATE}")

    # ── Load data ─────────────────────────────────────────────────────────────
    print("\nLoading IS data...")
    kline_is = load_kline(IS_START, OOS_START)
    ti_is    = load_ti(IS_START, OOS_START)
    print(f"  kline IS : {len(kline_is)} bars")

    print("Loading OOS data...")
    kline_oos = load_kline(OOS_START, END_DATE)
    ti_oos    = load_ti(OOS_START, END_DATE)
    print(f"  kline OOS: {len(kline_oos)} bars")

    # ── KD: IS param scan ────────────────────────────────────────────────────
    print("\n── KD: IS param scan ──")
    kd_grid = kd_param_scan(kline_is)
    kd_idx, _, best_kp, best_ks = find_plateau(
        kd_grid, KD_PERIOD_SCAN, KD_SMOOTH_SCAN)
    print(f"  Plateau: K_PERIOD={best_kp}, K_SMOOTH={best_ks}  "
          f"IS Sharpe={kd_grid[kd_idx]:.2f}")

    # ── KD: IS full backtest ──────────────────────────────────────────────────
    kd_k_is, kd_d_is = compute_kd(kline_is, best_kp, best_ks)
    kd_pos_is        = _kd_signal_loop(kd_k_is, kd_d_is)
    kd_is_res        = _run(kline_is["close"].values.astype(np.float64), kd_pos_is)

    # ── KD: OOS validation ────────────────────────────────────────────────────
    kd_k_oos, kd_d_oos = compute_kd(kline_oos, best_kp, best_ks)
    kd_pos_oos         = _kd_signal_loop(kd_k_oos, kd_d_oos)
    kd_oos_res         = _run(kline_oos["close"].values.astype(np.float64), kd_pos_oos)

    # ── KD: MCPT on OOS ──────────────────────────────────────────────────────
    print("  Running MCPT (KD OOS)...")
    kd_actual, kd_pvalue, kd_dist = mcpt(
        kline_oos["close"].values.astype(np.float64), kd_pos_oos)

    # ── TI: IS param scan ────────────────────────────────────────────────────
    print("\n── TI: IS param scan ──")
    ti_grid, df_ti_is = ti_param_scan(kline_is, ti_is)
    ti_idx, _, best_entry, best_exit = find_plateau(
        ti_grid, TI_THRESHOLDS, TI_THRESHOLDS)
    print(f"  Plateau: entry={best_entry}, exit={best_exit}  "
          f"IS Sharpe={ti_grid[ti_idx]:.2f}")

    # ── TI: IS full backtest ──────────────────────────────────────────────────
    ti_close_is  = df_ti_is["close"].values.astype(np.float64)
    ti_signal_is = df_ti_is["ti"].values.astype(np.float64)
    ti_pos_is    = _ti_signal_loop(ti_signal_is, best_entry, best_exit)
    ti_is_res    = _run(ti_close_is, ti_pos_is)

    # ── TI: OOS validation ────────────────────────────────────────────────────
    df_ti_oos   = kline_oos[["close"]].join(ti_oos[["ti"]], how="inner").dropna(subset=["close"])
    ti_close_oos  = df_ti_oos["close"].values.astype(np.float64)
    ti_signal_oos = df_ti_oos["ti"].values.astype(np.float64)
    ti_pos_oos    = _ti_signal_loop(ti_signal_oos, best_entry, best_exit)
    ti_oos_res    = _run(ti_close_oos, ti_pos_oos)

    # ── TI: MCPT on OOS ──────────────────────────────────────────────────────
    print("  Running MCPT (TI OOS)...")
    ti_actual, ti_pvalue, ti_dist = mcpt(ti_close_oos, ti_pos_oos)

    # ── Summary table ─────────────────────────────────────────────────────────
    kd_deg = kd_oos_res["sharpe"] / kd_is_res["sharpe"] if kd_is_res["sharpe"] != 0 else np.nan
    ti_deg = ti_oos_res["sharpe"] / ti_is_res["sharpe"] if ti_is_res["sharpe"] != 0 else np.nan

    hdr = f"  {'Metric':<28} {'KD':>12} {'TI':>12}"
    sep = "─" * len(hdr)
    print(f"\n{sep}\n  Validation Summary\n{sep}")
    print(hdr); print(sep)
    rows = [
        ("IS Sharpe",             f"{kd_is_res['sharpe']:.2f}",   f"{ti_is_res['sharpe']:.2f}"),
        ("OOS Sharpe",            f"{kd_oos_res['sharpe']:.2f}",  f"{ti_oos_res['sharpe']:.2f}"),
        ("Degradation (OOS/IS)",  f"{kd_deg:.2f}",               f"{ti_deg:.2f}"),
        ("IS Ann Return",         f"{kd_is_res['ann_ret']*100:.1f}%", f"{ti_is_res['ann_ret']*100:.1f}%"),
        ("OOS Ann Return",        f"{kd_oos_res['ann_ret']*100:.1f}%", f"{ti_oos_res['ann_ret']*100:.1f}%"),
        ("IS MDD",                f"{kd_is_res['max_dd']*100:.1f}%", f"{ti_is_res['max_dd']*100:.1f}%"),
        ("OOS MDD",               f"{kd_oos_res['max_dd']*100:.1f}%", f"{ti_oos_res['max_dd']*100:.1f}%"),
        ("MCPT p-value (OOS)",    f"{kd_pvalue:.3f}",             f"{ti_pvalue:.3f}"),
        ("MCPT significant?",     "✅" if kd_pvalue < 0.05 else "❌", "✅" if ti_pvalue < 0.05 else "❌"),
    ]
    for label, kd_val, ti_val in rows:
        print(f"  {label:<28} {kd_val:>12} {ti_val:>12}")
    print(sep)
    print("  Degradation > 0.5 is acceptable; < 0 means strategy broke down in OOS.")
    print("  MCPT p < 0.05: entry/exit timing is statistically significant.")

    # ── Chart ─────────────────────────────────────────────────────────────────
    plot_results("DOGEUSDT", {
        "kd": dict(
            is_res=kd_is_res, oos_res=kd_oos_res,
            mcpt_actual=kd_actual, mcpt_pvalue=kd_pvalue, mcpt_dist=kd_dist,
            is_dates=kline_is.index[~np.isnan(kd_is_res["strat_ret"])],
            oos_dates=kline_oos.index[~np.isnan(kd_oos_res["strat_ret"])],
        ),
        "ti": dict(
            is_res=ti_is_res, oos_res=ti_oos_res,
            mcpt_actual=ti_actual, mcpt_pvalue=ti_pvalue, mcpt_dist=ti_dist,
            is_dates=df_ti_is.index[~np.isnan(ti_is_res["strat_ret"])],
            oos_dates=df_ti_oos.index[~np.isnan(ti_oos_res["strat_ret"])],
        ),
    })
```

---

## Output Interpretation

### Degradation Ratio (OOS Sharpe / IS Sharpe)

| Ratio | Meaning |
|---|---|
| > 0.8 | Excellent — almost no degradation |
| 0.5 – 0.8 | Acceptable — typical for real strategies |
| 0.2 – 0.5 | Weak — likely overfitted to IS period |
| < 0 | Failed — strategy broke down in OOS |

### MCPT p-value

| p-value | Meaning |
|---|---|
| < 0.01 | Highly significant — timing very unlikely to be random |
| 0.01 – 0.05 | Significant — timing adds measurable value |
| 0.05 – 0.10 | Borderline — marginal evidence |
| > 0.10 | Not significant — strategy may be luck |

### What to look for

- A strategy that passes both tests (degradation > 0.5 AND p < 0.05) has genuine, robust edge.
- High IS Sharpe + poor OOS = overfitted. Common with technical indicators on short IS windows.
- Low IS Sharpe + maintains in OOS = underfit but potentially real. Widen the param search.
- MCPT passing but high OOS degradation = edge exists but parameter selection was too specific to IS data. Use the plateau (not peak) cell, or widen the plateau window.

---

## Notes

- **MCPT method — position permutation:** shuffles the entry/exit timing (position array) while keeping the return series fixed. Tests: "given BTC's actual return distribution, does the timing of this strategy's trades matter?" This is comparable across both strategies because neither strategy has its signal permuted — only when it acts.
- **Why not permute returns?** For KD, the signal is derived from price; permuting returns changes the price path and therefore the KD signal itself, making it circular. Position permutation is clean for both strategies.
- **IS/OOS split is time-based, not random.** Shuffling time order for a financial backtest introduces look-ahead bias. The IS period always precedes OOS.
- **Walk-forward extension:** for more rigorous validation, replace the single IS/OOS split with multiple expanding windows (e.g., 12-month IS → 3-month OOS, rolling forward). Not implemented here to keep the example readable.
- **Both strategies use the same backtest engine** (`_run`), same vol-targeting, same fee model — the only difference is how `position` is computed.
