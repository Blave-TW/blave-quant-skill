# Example: KD Stochastic Golden/Death Cross Strategy (Type A)

Trade BTC on the 1-hour chart using the KD Stochastic Oscillator.

- **Entry:** %K crosses above %D (Golden Cross) → long
- **Exit:** %K crosses below %D (Death Cross) → flat
- **Dead zone:** between crossovers → hold current position (`nan`)
- **Long only** — no short positions

This file shows the two functions you write for a Type A strategy.
`lib/runner.py` handles everything else: vectorbt backtest, stats output, PnL chart, live execution.

Requires: `pip install vectorbt`

---

## KD Formula

1. Raw %K = (Close − LowestLow_N) / (HighestHigh_N − LowestLow_N) × 100
2. Slow %K = SMA(Raw %K, K_SMOOTH)
3. %D = SMA(Slow %K, D_SMOOTH)

---

## Code

```python
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import dotenv_values

sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # → blaveclaw-config/

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
def add_indicators(df):
    low_min  = df["Low"].rolling(K_PERIOD, min_periods=K_PERIOD).min()
    high_max = df["High"].rolling(K_PERIOD, min_periods=K_PERIOD).max()
    denom    = high_max - low_min
    raw_k    = np.where(denom > 0, (df["Close"] - low_min) / denom * 100, np.nan)
    df["K"]  = pd.Series(raw_k, index=df.index).rolling(K_SMOOTH, min_periods=K_SMOOTH).mean()
    df["D"]  = df["K"].rolling(D_SMOOTH, min_periods=D_SMOOTH).mean()
    return df


# ── compute_signals ───────────────────────────────────────────────────────────
# Vectorized — receives the full df (with indicators + realized_vol if VOL_TARGETING).
# Returns pd.Series: positive float = long (size fraction), 0.0 = flat, nan = hold.
def compute_signals(df) -> pd.Series:
    k, d = df["K"], df["D"]
    golden = (k > d) & (k.shift(1) <= d.shift(1))
    death  = (k < d) & (k.shift(1) >= d.shift(1))

    signal = pd.Series(np.nan, index=df.index)

    if VOL_TARGETING and "realized_vol" in df.columns:
        vol      = df["realized_vol"]
        vol_size = (TARGET_VOL / vol).clip(upper=VOL_CAP)
        signal[golden] = vol_size[golden]
    else:
        signal[golden] = 1.0

    signal[death] = 0.0
    return signal


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from lib.runner import run
    run(locals(), add_indicators, compute_signals)
```

---

## What lib/runner.py handles (you do NOT write these)

- Adds `realized_vol` column when `VOL_TARGETING = True`
- Runs vectorbt `Portfolio.from_signals()` — signal at bar i, fill at bar i open
- Stats output: Total Return, Sharpe, Max Drawdown, Win Rate, # Trades
- PnL chart saved to `strategies/<name>/<name>_pnl.png`
- Live mode: calls `compute_signals(df).iloc[-1]` on each cron tick

---

## Notes

- **Long only** — no short positions
- **NaN = hold**: `ffill()` in runner.py propagates the last non-nan signal between crossovers
- **OB/OS filter (optional):** add `& (k < 20)` to `golden` for oversold-only entries
- **Smoothing method:** SMA for both %K and %D. Swap `.rolling().mean()` for `.ewm(span=...)` if preferred

### Live Execution Timing

Signal fires at bar i close → `compute_signals(df).iloc[-1]` → place order → fill at bar i+1 open.
