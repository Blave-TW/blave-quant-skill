# Example: KD Stochastic Golden/Death Cross Strategy (Type A)

Trade BTC on the 1-hour chart using the KD Stochastic Oscillator.

- **Entry:** %K crosses above %D (Golden Cross) → long
- **Exit:** %K crosses below %D (Death Cross) → flat
- **Dead zone:** between crossovers → hold current position (`nan`)
- **Long only** — no short positions

This file shows the two functions you write for a Type A strategy.
`lib/runner.py` handles everything else: `BlaveStrategy`, `Backtest`, stats output, PnL chart, live execution.

---

## KD Formula

1. Raw %K = (Close − LowestLow_N) / (HighestHigh_N − LowestLow_N) × 100
2. Slow %K = SMA(Raw %K, K_SMOOTH)
3. %D = SMA(Slow %K, D_SMOOTH)

All three are computed in `add_indicators()` and stored as df columns.
`K_prev` / `D_prev` (previous bar) are also stored so `compute_signal` can detect crossovers from a single row.

---

## Code

```python
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import dotenv_values

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "blave-quant"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ── Config ────────────────────────────────────────────────────────────────────
MODE             = "backtest"
STRATEGY_NAME    = "btc_kd_long"
SYMBOL           = "BTCUSDT"
EXCHANGE         = "binance"
INTERVAL         = "1h"
START            = "2022-01-01"
END              = None
FEE              = 0.0005

K_PERIOD         = 9
K_SMOOTH         = 3
D_SMOOTH         = 3

VOL_TARGETING    = True
TARGET_VOL       = 0.30
VOL_LOOKBACK     = 720          # 30 days × 24h
PERIODS_PER_YEAR = 8760
VOL_CAP          = 2.0

_env  = dotenv_values(Path(__file__).parent.parent.parent / ".env")
_HDRS = {"api-key": _env.get("blave_api_key", ""), "secret-key": _env.get("blave_secret_key", "")}


# ── add_indicators ────────────────────────────────────────────────────────────
# Computes %K, %D, and their previous-bar values.
# K_prev / D_prev let compute_signal detect crossovers from a single row
# without needing access to previous state — they are INDICATOR columns, not signal logic.
def add_indicators(df):
    low_min  = df["Low"].rolling(K_PERIOD, min_periods=K_PERIOD).min()
    high_max = df["High"].rolling(K_PERIOD, min_periods=K_PERIOD).max()
    denom    = high_max - low_min
    raw_k    = np.where(denom > 0, (df["Close"] - low_min) / denom * 100, np.nan)
    df["K"]      = pd.Series(raw_k, index=df.index).rolling(K_SMOOTH, min_periods=K_SMOOTH).mean()
    df["D"]      = df["K"].rolling(D_SMOOTH, min_periods=D_SMOOTH).mean()
    df["K_prev"] = df["K"].shift(1)
    df["D_prev"] = df["D"].shift(1)
    return df


# ── compute_signal ────────────────────────────────────────────────────────────
# Pure function — reads K, D, K_prev, D_prev (and realized_vol) from row.
# Returns: 1.0 or fraction (long), 0.0 (flat), float("nan") (hold).
def compute_signal(row) -> float:
    k  = float(row["K"])
    d  = float(row["D"])
    kp = float(row["K_prev"])
    dp = float(row["D_prev"])

    if any(np.isnan(v) for v in (k, d, kp, dp)):
        return float("nan")         # warmup: hold

    if kp <= dp and k > d:          # golden cross → long
        if not VOL_TARGETING:
            return 1.0
        vol = float(row.get("realized_vol", float("nan")))
        if np.isnan(vol) or vol <= 0:
            return float("nan")     # vol not ready: hold
        return min(TARGET_VOL / vol, VOL_CAP)

    if kp >= dp and k < d:          # death cross → flat
        return 0.0

    return float("nan")             # between crossovers: hold


# ── Run ───────────────────────────────────────────────────────────────────────
# lib/runner.py provides BlaveStrategy(Strategy) with nan=hold logic,
# Backtest(trade_on_close=False), stats print, PnL chart, and live/paper mode.
if __name__ == "__main__":
    from lib.runner import run
    run(locals(), add_indicators, compute_signal)
```

---

## What lib/runner.py handles (you do NOT write these)

- `BlaveStrategy(Strategy)` with `next()` that calls `compute_signal(row)` and interprets `nan` as hold
- `Backtest(..., trade_on_close=False)` — signal at bar i close, fill at bar i+1 open
- Stats output: Return, Sharpe, Max Drawdown, # Trades
- PnL chart saved to `strategies/<name>/<name>_pnl.png`
- Vol-targeting: adds `realized_vol` column to df when `VOL_TARGETING = True`
- Bootstrap (live mode): replays history to find initial position before first cron tick

---

## Notes

- **Long only** — no short positions
- **K_prev / D_prev in add_indicators**: storing the previous bar's values as indicator columns is the correct pattern for crossover detection. It keeps `compute_signal` stateless (reads only from `row`) while still seeing two consecutive bars
- **OB/OS filter (optional):** add `and k < 20` to the golden cross condition for oversold-only entries
- **Smoothing method:** uses SMA for both %K and %D (classic formula). Swap `rolling().mean()` for `ewm(span=...)` if you prefer exponential weighting

### Live Execution Timing

`trade_on_close=False`: signal fires at bar i close → fill at bar i+1 open.

```
bar i closes
  → KD recomputes with new close
  → crossover detected → place market order immediately
  → fill at bar i+1 open
```
