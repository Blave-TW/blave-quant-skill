# Example: Strategy Validation — MCPT + Out-of-Sample (KD vs Taker Intensity)

## What This Does

Validates two DOGE 1h long-only strategies side by side using:

1. **IS (In-Sample) Parameter Optimization** — 2D param scan on the first 2 years to find the most robust (plateau) parameters for each strategy
2. **OOS (Out-of-Sample) Validation** — run the IS-selected params on the held-out final year; a strategy with real edge should degrade gracefully, not collapse
3. **MCPT (Monte Carlo Permutation Test)** — shuffle the forward return series 2000 times while keeping positions fixed, recompute Sharpe on each shuffle; p-value = fraction of shuffled Sharpes ≥ actual OOS Sharpe; p < 0.05 means the timing adds statistically significant value

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
# NOTE: This is a validation-only research script.
# Requires: pip install vectorbt
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # → blaveclaw-config/
from lib.data import fetch_kline, fetch_taker_intensity
from lib.param_scan import find_plateau, plot_heatmap
from lib.validation import mcpt, plot_mcpt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
SYMBOL         = "DOGEUSDT"
INTERVAL       = "1h"

KD_PERIOD_SCAN = [5, 9, 14, 21, 34]
KD_SMOOTH_SCAN = [2, 3, 5, 8]
D_SMOOTH       = 3

TI_THRESHOLDS  = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]

TARGET_VOL     = 0.30
MAX_LEV        = 2.0
VOL_WINDOW     = 720
HOURS_PER_YEAR = 8760
FEE            = 0.0005
N_PERMUTATIONS = 2000

HEADERS = {"api-key": _env["blave_api_key"], "secret-key": _env["blave_secret_key"]}


def load_kline(start, end):
    return fetch_kline(SYMBOL, INTERVAL, start, end, HEADERS)


def load_ti(start, end):
    df = fetch_taker_intensity(SYMBOL, INTERVAL, start, end, HEADERS, timeframe="24h")
    return df.rename(columns={"alpha": "ti"})


# ── Signal Computation ────────────────────────────────────────────────────────
def compute_kd(df, k_period, k_smooth, d_smooth=D_SMOOTH):
    low_min  = df["Low"].rolling(k_period).min()
    high_max = df["High"].rolling(k_period).max()
    denom    = high_max - low_min
    raw_k    = pd.Series(
        np.where(denom > 0, (df["Close"] - low_min) / denom * 100, 50.0),
        index=df.index,
    )
    slow_k = raw_k.rolling(k_smooth).mean()
    d      = slow_k.rolling(d_smooth).mean()
    return slow_k.values, d.values


def _compute_kd_signal(k, k_prev, d, d_prev) -> float:
    """Pure signal function — matches compute_signal() semantics from TEMPLATE.py.
    Returns 1.0 (long), 0.0 (flat), or nan (hold current position).
    in_long is NOT a parameter — nan handles hold regardless of current state.
    """
    if np.isnan(k) or np.isnan(d) or np.isnan(k_prev) or np.isnan(d_prev):
        return float("nan")              # warmup: hold
    if k_prev <= d_prev and k > d:       # golden cross → long
        return 1.0
    if k_prev >= d_prev and k < d:       # death cross → flat
        return 0.0
    return float("nan")                  # between crossovers: hold


def _compute_ti_signal(ti: float, entry_th: float, exit_th: float) -> float:
    """Pure signal function — matches compute_signal() semantics from TEMPLATE.py.
    Returns 1.0 (long), 0.0 (flat), or nan (hold current position).
    in_long is NOT a parameter — nan handles hold regardless of current state.
    """
    if np.isnan(ti):     return float("nan")  # warmup / missing: hold
    if ti > entry_th:    return 1.0            # above entry: long
    if ti < exit_th:     return 0.0            # below exit: flat
    return float("nan")                        # dead zone: hold


def _build_kd_signals(k_series, d_series) -> pd.Series:
    """Vectorized KD crossover signals: 1.0=long, 0.0=flat, nan=hold."""
    golden = (k_series > d_series) & (k_series.shift(1) <= d_series.shift(1))
    death  = (k_series < d_series) & (k_series.shift(1) >= d_series.shift(1))
    signal = pd.Series(np.nan, index=k_series.index)
    signal[golden] = 1.0
    signal[death]  = 0.0
    return signal


def _build_ti_signals(ti_series, entry_th, exit_th) -> pd.Series:
    """Vectorized TI threshold signals: 1.0=long, 0.0=flat, nan=hold."""
    signal = pd.Series(np.nan, index=ti_series.index)
    signal[ti_series > entry_th] = 1.0
    signal[ti_series < exit_th]  = 0.0
    return signal


def _signals_to_position(signals: pd.Series) -> np.ndarray:
    return signals.ffill().fillna(0.0).values


# ── Core Backtest Engine (shared) ─────────────────────────────────────────────
def _run(close_series, signals):
    """Run vectorbt backtest; returns metrics dict compatible with mcpt()."""
    import vectorbt as vbt

    log_ret      = np.concatenate([[0.0], np.log(close_series.values[1:] / close_series.values[:-1])])
    realized_vol = pd.Series(log_ret, index=close_series.index).rolling(VOL_WINDOW).std() * np.sqrt(HOURS_PER_YEAR)

    size = signals.where(signals > 0).copy()
    size[signals > 0] = (TARGET_VOL / realized_vol[signals > 0]).clip(upper=MAX_LEV).fillna(1.0)
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
    position  = _signals_to_position(signals)
    total_ret = float(stats.get('Total Return [%]', 0)) / 100
    yrs       = len(close_series) / HOURS_PER_YEAR
    ann_ret   = (1 + total_ret) ** (1 / yrs) - 1 if yrs > 0 else np.nan

    return dict(
        sharpe   = float(stats.get('Sharpe Ratio', np.nan)),
        ann_ret  = ann_ret,
        max_dd   = float(stats.get('Max Drawdown [%]', 0)) / -100,
        cum      = cum,
        strat_ret= strat_ret,
        position = position,
    )


# ── MCPT ──────────────────────────────────────────────────────────────────────
# mcpt() and plot_mcpt() imported from lib.validation
# Call signature: mcpt(close, position, n=N_PERMUTATIONS, fee=FEE,
#                      target_vol=TARGET_VOL, max_lev=MAX_LEV,
#                      vol_window=VOL_WINDOW, periods_per_year=HOURS_PER_YEAR)


# ── IS Param Scans ────────────────────────────────────────────────────────────
# find_plateau imported from lib.param_scan


def kd_param_scan(df_kline):
    grid = np.full((len(KD_PERIOD_SCAN), len(KD_SMOOTH_SCAN)), np.nan)
    for i, kp in enumerate(KD_PERIOD_SCAN):
        for j, ks in enumerate(KD_SMOOTH_SCAN):
            k_arr, d_arr = compute_kd(df_kline, kp, ks)
            k_s = pd.Series(k_arr, index=df_kline.index)
            d_s = pd.Series(d_arr, index=df_kline.index)
            sigs = _build_kd_signals(k_s, d_s)
            res = _run(df_kline["Close"], sigs)
            if not np.isnan(res["sharpe"]): grid[i, j] = res["sharpe"]
    return grid


def ti_param_scan(df_kline, df_ti):
    df = df_kline[["Close"]].join(df_ti[["ti"]], how="inner").dropna(subset=["Close"])
    n  = len(TI_THRESHOLDS)
    grid = np.full((n, n), np.nan)
    for i, entry in enumerate(TI_THRESHOLDS):
        for j, exit_ in enumerate(TI_THRESHOLDS):
            if exit_ > entry: continue
            sigs = _build_ti_signals(df["ti"], entry, exit_)
            res = _run(df["Close"], sigs)
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
        sig_str = f"p={r['mcpt_pvalue']:.3f} {'[sig]' if r['mcpt_pvalue'] < 0.05 else '[ns]'}"
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
    kd_sigs_is = _build_kd_signals(
        pd.Series(kd_k_is, index=kline_is.index),
        pd.Series(kd_d_is, index=kline_is.index))
    kd_is_res  = _run(kline_is["Close"], kd_sigs_is)
    kd_pos_is  = kd_is_res["position"]

    # ── KD: OOS validation ────────────────────────────────────────────────────
    kd_k_oos, kd_d_oos = compute_kd(kline_oos, best_kp, best_ks)
    kd_sigs_oos = _build_kd_signals(
        pd.Series(kd_k_oos, index=kline_oos.index),
        pd.Series(kd_d_oos, index=kline_oos.index))
    kd_oos_res  = _run(kline_oos["Close"], kd_sigs_oos)
    kd_pos_oos  = kd_oos_res["position"]

    # ── KD: MCPT on OOS ──────────────────────────────────────────────────────
    print("  Running MCPT (KD OOS)...")
    kd_actual, kd_pvalue, kd_dist = mcpt(
        kline_oos["Close"].values.astype(np.float64), kd_pos_oos,
        n=N_PERMUTATIONS, fee=FEE, target_vol=TARGET_VOL, max_lev=MAX_LEV,
        vol_window=VOL_WINDOW, periods_per_year=HOURS_PER_YEAR)

    # ── TI: IS param scan ────────────────────────────────────────────────────
    print("\n── TI: IS param scan ──")
    ti_grid, df_ti_is = ti_param_scan(kline_is, ti_is)
    ti_idx, _, best_entry, best_exit = find_plateau(
        ti_grid, TI_THRESHOLDS, TI_THRESHOLDS)
    print(f"  Plateau: entry={best_entry}, exit={best_exit}  "
          f"IS Sharpe={ti_grid[ti_idx]:.2f}")

    # ── TI: IS full backtest ──────────────────────────────────────────────────
    df_ti_is_aligned = df_ti_is[["Close"]].join(df_ti_is[["ti"]], how="inner").dropna()
    ti_sigs_is = _build_ti_signals(df_ti_is_aligned["ti"], best_entry, best_exit)
    ti_is_res  = _run(df_ti_is_aligned["Close"], ti_sigs_is)
    ti_pos_is  = ti_is_res["position"]

    # ── TI: OOS validation ────────────────────────────────────────────────────
    df_ti_oos = kline_oos[["Close"]].join(ti_oos[["ti"]], how="inner").dropna(subset=["Close"])
    ti_sigs_oos = _build_ti_signals(df_ti_oos["ti"], best_entry, best_exit)
    ti_oos_res  = _run(df_ti_oos["Close"], ti_sigs_oos)
    ti_pos_oos  = ti_oos_res["position"]

    # ── TI: MCPT on OOS ──────────────────────────────────────────────────────
    print("  Running MCPT (TI OOS)...")
    ti_actual, ti_pvalue, ti_dist = mcpt(
        df_ti_oos["Close"].values.astype(np.float64), ti_pos_oos,
        n=N_PERMUTATIONS, fee=FEE, target_vol=TARGET_VOL, max_lev=MAX_LEV,
        vol_window=VOL_WINDOW, periods_per_year=HOURS_PER_YEAR)

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
        ("MCPT significant?",     "[sig]" if kd_pvalue < 0.05 else "[ns]", "[sig]" if ti_pvalue < 0.05 else "[ns]"),
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

- **MCPT method — return permutation:** shuffles the forward return series while keeping the position array fixed. Fees and vol-scaling are therefore identical across all permutations. Tests: "given this strategy's entry/exit timing, are the return periods it selects better than a random draw?"
- **Why not permute position?** A random shuffle of a binary 0/1 array produces ~N×p×(1−p) transitions vs. the strategy's much smaller number. With FEE=0.0005 that creates 30–40× more fee drag on every permutation, forcing all permuted Sharpes deeply negative and producing a biased p-value regardless of whether the strategy has real edge.
- **IS/OOS split is time-based, not random.** Shuffling time order for a financial backtest introduces look-ahead bias. The IS period always precedes OOS.
- **Walk-forward extension:** for more rigorous validation, replace the single IS/OOS split with multiple expanding windows (e.g., 12-month IS → 3-month OOS, rolling forward). Not implemented here to keep the example readable.
- **Both strategies use the same backtest engine** (`_run` via vectorbt), same vol-targeting, same fee model — the only difference is how signals are computed.
