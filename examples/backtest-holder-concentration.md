# Example: Holder Concentration Long Strategy (Type A)

Go long when smart money is concentrating into a coin; exit when they distribute.

- **Entry:** HC alpha > `ENTRY_TH` → long
- **Exit:** HC alpha < `EXIT_TH` → flat
- **Dead zone:** between thresholds → hold current position (`nan`)
- **Long only** — no short positions

This file shows the two functions you write for a Type A strategy.
`lib/runner.py` handles everything else: vectorbt backtest, stats output, PnL chart, live execution.

Requires: `pip install vectorbt`

---

## Key data-fetch pattern: annual chunking

Blave API returns max 1 year per request. Fetch in 365-day chunks and concatenate.
Align alpha timestamps to kline index with `.join()` + `.ffill()`.

---

## Code

```python
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import dotenv_values

sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # → blaveclaw-config/
from lib.data import fetch_holder_concentration

# ── Config ────────────────────────────────────────────────────────────────────
MODE             = "backtest"
STRATEGY_NAME    = "btc_hc_long"
SYMBOL           = "BTCUSDT"
EXCHANGE         = "binance"
INTERVAL         = "1h"
START            = "2022-01-01"
END              = None
FEE              = 0.0005

ENTRY_TH         = 1.0
EXIT_TH          = -0.5

VOL_TARGETING    = True
TARGET_VOL       = 0.30
VOL_LOOKBACK     = 720          # 30 days × 24h
PERIODS_PER_YEAR = 8760
VOL_CAP          = 2.0

_env  = dotenv_values(Path(__file__).parent.parent.parent / ".env")
_HDRS = {"api-key": _env.get("blave_api_key", ""), "secret-key": _env.get("blave_secret_key", "")}


# ── add_indicators ────────────────────────────────────────────────────────────
def add_indicators(df):
    hc = fetch_holder_concentration(SYMBOL, INTERVAL, START, END, _HDRS)
    df = df.join(hc.rename(columns={"alpha": "HC"}))
    df["HC"] = df["HC"].ffill()
    return df


# ── compute_signals ───────────────────────────────────────────────────────────
# Vectorized — receives the full df (with "HC" and "realized_vol" if VOL_TARGETING).
# Returns pd.Series: positive float = long (size fraction), 0.0 = flat, nan = hold.
def compute_signals(df) -> pd.Series:
    hc     = df["HC"]
    signal = pd.Series(np.nan, index=df.index)

    long_mask = hc > ENTRY_TH
    flat_mask = hc < EXIT_TH

    if VOL_TARGETING and "realized_vol" in df.columns:
        vol      = df["realized_vol"]
        vol_size = (TARGET_VOL / vol).clip(upper=VOL_CAP)
        signal[long_mask] = vol_size[long_mask]
    else:
        signal[long_mask] = 1.0

    signal[flat_mask] = 0.0
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

## Alpha Scale Reference

| HC Alpha | Interpretation |
|---|---|
| > 3 | Over Concentrated |
| 2 – 3 | Highly Concentrated |
| **> 1** | **→ default ENTRY_TH** |
| 0.5 – 1 | Concentrated |
| -0.5 – 0.5 | Neutral |
| **< -0.5** | **→ default EXIT_TH** |
| < -2 | Concentrated (short side) |

---

## Notes

- Entry threshold stricter than exit — gives the position room through short-term noise
- With `VOL_TARGETING = True`, `compute_signals` returns a vol-scaled fraction at each long bar
- HC updates every 5 min; on `1h` interval each bar reflects the last finalized hourly value
- Dead zone (between thresholds): position is held unchanged via `ffill()` in runner.py
