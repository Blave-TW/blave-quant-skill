# Example: BTC Taker Intensity 24h — Parameter Scan & Plateau Chart

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

_env     = dotenv_values(Path(__file__).parent.parent.parent / ".env")
HEADERS  = {"api-key": _env["blave_api_key"], "secret-key": _env["blave_secret_key"]}
API_BASE = "https://api.blave.org"

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
def _fetch_chunks(endpoint, params, data_keys):
    """Fetch in 365-day chunks; returns concatenated arrays for each key in data_keys."""
    s = datetime.strptime(params["start_date"], "%Y-%m-%d")
    e = datetime.strptime(params.get("end_date") or
                          datetime.now(timezone.utc).strftime("%Y-%m-%d"), "%Y-%m-%d")
    out = {k: [] for k in data_keys}
    while s < e:
        chunk_end = min(s + timedelta(days=365), e)
        r = requests.get(
            f"{API_BASE}/{endpoint}", headers=HEADERS,
            params={**params,
                    "start_date": s.strftime("%Y-%m-%d"),
                    "end_date":   chunk_end.strftime("%Y-%m-%d")},
            timeout=60,
        )
        r.raise_for_status()
        payload = r.json()
        # kline returns a list of dicts; alpha endpoints return {data: {key: [...]}}
        if isinstance(payload, list):
            out[data_keys[0]].extend(payload)
        else:
            data = payload.get("data", {})
            for k in data_keys:
                out[k].extend(data.get(k, []))
        s = chunk_end
    return out


def load_kline(start, end):
    raw = _fetch_chunks("kline",
                        {"symbol": SYMBOL, "period": INTERVAL,
                         "start_date": start, "end_date": end or ""},
                        ["rows"])
    rows = raw["rows"]
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time").sort_index()
    df = df[~df.index.duplicated(keep="first")]
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    return df


def load_ti(start, end):
    raw = _fetch_chunks("taker_intensity/get_alpha",
                        {"symbol": SYMBOL, "period": INTERVAL, "timeframe": "24h",
                         "start_date": start, "end_date": end or ""},
                        ["timestamp", "alpha"])
    df = pd.DataFrame({
        "time":  pd.to_datetime(raw["timestamp"], unit="s", utc=True),
        "ti":    pd.to_numeric(raw["alpha"], errors="coerce"),
    }).set_index("time").sort_index()
    return df[~df.index.duplicated(keep="first")]


# ── Signal & backtest engine ───────────────────────────────────────────────────
def _signals_to_position(sigs):
    return pd.Series(sigs, dtype=float).ffill().fillna(0.0).values


def _build_ti_position(ti_arr, entry_th, exit_th):
    def _sig(ti):
        if np.isnan(ti):      return float("nan")
        if ti > entry_th:     return 1.0
        if ti < exit_th:      return 0.0
        return float("nan")
    return _signals_to_position([_sig(v) for v in ti_arr])


def _run(close, position):
    n       = len(close)
    log_ret = np.concatenate([[0.0], np.log(close[1:] / close[:-1])])
    fwd_ret = np.empty(n); fwd_ret[:-1] = np.diff(close) / close[:-1]; fwd_ret[-1] = 0.0

    realized_vol = pd.Series(log_ret).rolling(VOL_WINDOW).std().values * np.sqrt(HOURS_PER_YEAR)
    vol_scalar   = np.where(
        (realized_vol > 0) & ~np.isnan(realized_vol),
        np.clip(TARGET_VOL / realized_vol, 0, VOL_CAP), 1.0)

    sized     = position * vol_scalar
    fee_cost  = np.abs(np.diff(sized, prepend=0)) * FEE
    strat_ret = sized * fwd_ret - fee_cost

    r   = strat_ret[~np.isnan(strat_ret)]
    cum = np.cumprod(1 + r)
    pk  = np.maximum.accumulate(cum)
    yrs = len(r) / HOURS_PER_YEAR
    return dict(
        sharpe   = (r.mean() / r.std()) * np.sqrt(HOURS_PER_YEAR) if r.std() > 0 else np.nan,
        ann_ret  = (1 + cum[-1] - 1) ** (1 / yrs) - 1,
        max_dd   = ((cum - pk) / pk).min(),
        cum      = cum,
        strat_ret= strat_ret,
        n_trades = int((np.diff(position, prepend=0) != 0).sum()),
    )


# ── Param scan ────────────────────────────────────────────────────────────────
def param_scan(close, ti_arr):
    n = len(THRESHOLDS)
    grid = np.full((n, n), np.nan)
    for i, entry in enumerate(THRESHOLDS):
        for j, exit_ in enumerate(THRESHOLDS):
            if exit_ > entry:
                continue        # invalid: exit must be <= entry
            pos = _build_ti_position(ti_arr, entry, exit_)
            res = _run(close, pos)
            if not np.isnan(res["sharpe"]):
                grid[i, j] = res["sharpe"]
    return grid


# ── Plateau detection ─────────────────────────────────────────────────────────
def find_plateau(grid, window=PLATEAU_WINDOW):
    rows, cols = grid.shape
    nbr_mean   = np.full((rows, cols), np.nan)
    for i in range(rows):
        for j in range(cols):
            if np.isnan(grid[i, j]):
                continue
            nb = [grid[i+di, j+dj]
                  for di in range(-window, window + 1)
                  for dj in range(-window, window + 1)
                  if 0 <= i+di < rows and 0 <= j+dj < cols
                  and not np.isnan(grid[i+di, j+dj])]
            if nb:
                nbr_mean[i, j] = np.mean(nb)
    best = np.unravel_index(np.nanargmax(nbr_mean), nbr_mean.shape)
    return best, nbr_mean


# ── Chart ─────────────────────────────────────────────────────────────────────
def plot_all(grid, nbr_mean, best_idx, best_res, dates):
    from matplotlib.patches import Rectangle

    bi, bj     = best_idx
    best_entry = THRESHOLDS[bi]
    best_exit  = THRESHOLDS[bj]
    labels     = [str(v) for v in THRESHOLDS]
    n          = len(THRESHOLDS)

    fig = plt.figure(figsize=(14, 12))
    fig.suptitle(
        f"{SYMBOL} Taker Intensity 24h — Parameter Scan (1h, vol-targeting 30%, fee {FEE*100:.2f}%)",
        fontsize=13, fontweight="bold", y=0.99,
    )
    gs = fig.add_gridspec(2, 1, hspace=0.45, height_ratios=[1.1, 1])

    # ── Heatmap: raw Sharpe, box on plateau cell ───────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    masked = np.ma.masked_invalid(grid)
    valid  = grid[~np.isnan(grid)]
    vmax   = np.nanpercentile(valid, 95)
    vmin   = np.nanpercentile(valid, 5)
    im     = ax1.imshow(masked, aspect="auto", cmap="RdYlGn",
                        origin="upper", vmin=vmin, vmax=vmax)
    plt.colorbar(im, ax=ax1, label="Sharpe")
    ax1.set_xticks(range(n)); ax1.set_xticklabels(labels, fontsize=8)
    ax1.set_yticks(range(n)); ax1.set_yticklabels(labels, fontsize=8)
    ax1.set_xlabel("EXIT_TH", fontsize=9)
    ax1.set_ylabel("ENTRY_TH", fontsize=9)
    for i in range(n):
        for j in range(n):
            v = grid[i, j]
            if not np.isnan(v):
                ax1.text(j, i, f"{v:.2f}", ha="center", va="center",
                         fontsize=7, color="black")
    # highlight the plateau cell with a white rectangle border
    ax1.add_patch(Rectangle(
        (bj - 0.5, bi - 0.5), 1, 1,
        linewidth=2.5, edgecolor="white", facecolor="none",
    ))
    ax1.set_title(
        f"Sharpe Heatmap — plateau selected: ENTRY_TH={best_entry}, EXIT_TH={best_exit}  "
        f"(Sharpe={grid[bi, bj]:.2f})",
        fontsize=10,
    )

    # ── PnL: best plateau params ───────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    cum_pct = (best_res["cum"] - 1) * 100
    ax2.plot(dates, cum_pct, color="#3498db", lw=1.5)
    ax2.axhline(0, color="#888", lw=0.6, ls="--")
    ax2.fill_between(dates, cum_pct, 0,
                     where=(cum_pct >= 0), alpha=0.12, color="#2ecc71")
    ax2.fill_between(dates, cum_pct, 0,
                     where=(cum_pct < 0),  alpha=0.12, color="#e74c3c")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax2.set_ylabel("Cumulative Return (%)")
    ax2.set_title(
        f"Best Plateau Params — ENTRY_TH={best_entry}, EXIT_TH={best_exit}\n"
        f"Sharpe={best_res['sharpe']:.2f}  "
        f"Ann={best_res['ann_ret']*100:.1f}%  "
        f"MDD={best_res['max_dd']*100:.1f}%  "
        f"Trades={best_res['n_trades']}",
        fontsize=10,
    )

    fname = f"{SYMBOL}_ti24h_param_scan.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {fname}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    end_str   = END or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Fetching {SYMBOL} kline {INTERVAL}  {START} → {end_str}")
    df_kline  = load_kline(START, end_str)
    print(f"  {len(df_kline)} bars")

    print(f"Fetching TI 24h  {START} → {end_str}")
    df_ti     = load_ti(START, end_str)
    print(f"  {len(df_ti)} alpha points")

    # align: inner join on timestamp, forward-fill TI into kline index
    df = df_kline[["close"]].join(df_ti[["ti"]], how="left")
    df["ti"] = df["ti"].ffill()
    df = df.dropna(subset=["close", "ti"])
    close  = df["close"].values.astype(np.float64)
    ti_arr = df["ti"].values.astype(np.float64)
    print(f"  Aligned rows: {len(df)}")

    print("\nRunning param scan…")
    grid = param_scan(close, ti_arr)

    print("Finding plateau…")
    best_idx, nbr_mean = find_plateau(grid)
    bi, bj = best_idx
    best_entry = THRESHOLDS[bi]
    best_exit  = THRESHOLDS[bj]
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

    # run backtest with best params and plot
    best_pos = _build_ti_position(ti_arr, best_entry, best_exit)
    best_res = _run(close, best_pos)
    valid    = ~np.isnan(best_res["strat_ret"])
    dates    = df.index[valid]

    plot_all(grid, nbr_mean, best_idx, best_res, dates)
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
