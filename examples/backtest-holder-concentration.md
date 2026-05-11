# Example: Holder Concentration Long Strategy (Type A)

Go long when smart money is concentrating into a coin; exit when they distribute.

- **Entry:** HC alpha > `ENTRY_TH` → long
- **Exit:** HC alpha < `EXIT_TH` → flat
- **Dead zone:** between thresholds → hold current position (`nan`)
- **Long only** — no short positions

This file shows the two functions you write for a Type A strategy.
`lib/runner.py` handles everything else: `BlaveStrategy`, `Backtest`, stats output, PnL chart, live execution.

---

## Key data-fetch pattern: annual chunking

Blave API returns max 1 year per request. Fetch in 365-day chunks and concatenate.
Align alpha timestamps to kline index with `.join()` + `.ffill()`.

---

## Code

```python
import sys, requests
import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import dotenv_values

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "blave-quant"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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
# Fetches HC alpha (annual chunking), aligns to df index, adds "HC" column.
# df already has OHLCV — lib/runner.py fetches klines via lib/data.fetch_kline.
def add_indicators(df):
    from datetime import datetime, timedelta
    s = datetime.strptime(START, "%Y-%m-%d")
    e = datetime.utcnow() if not END else datetime.strptime(END, "%Y-%m-%d")

    ts_list, alpha_list = [], []
    cursor = s
    while cursor < e:
        chunk_end = min(cursor + timedelta(days=365), e)
        r = requests.get(
            "https://api.blave.org/holder_concentration/get_alpha",
            headers=_HDRS,
            params={"symbol": SYMBOL, "period": INTERVAL,
                    "start_date": cursor.strftime("%Y-%m-%d"),
                    "end_date":   chunk_end.strftime("%Y-%m-%d")},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json().get("data", {})
        ts_list.extend(data.get("timestamp", []))
        alpha_list.extend(data.get("alpha", []))
        cursor = chunk_end

    hc = pd.DataFrame({
        "time": pd.to_datetime(ts_list, unit="s", utc=True),
        "HC":   pd.to_numeric(alpha_list, errors="coerce"),
    }).set_index("time").sort_index()
    hc = hc[~hc.index.duplicated(keep="first")]

    df = df.join(hc["HC"], how="left")
    df["HC"] = df["HC"].ffill()
    return df


# ── compute_signal ────────────────────────────────────────────────────────────
# Pure function — reads "HC" (and "realized_vol" if VOL_TARGETING) from row.
# Returns: 1.0 or fraction (long), 0.0 (flat), float("nan") (hold).
def compute_signal(row) -> float:
    hc = float(row["HC"])
    if np.isnan(hc):
        return float("nan")         # warmup / missing data: hold

    if hc > ENTRY_TH:
        if not VOL_TARGETING:
            return 1.0
        vol = float(row.get("realized_vol", float("nan")))
        if np.isnan(vol) or vol <= 0:
            return float("nan")     # vol not ready yet: hold
        return min(TARGET_VOL / vol, VOL_CAP)

    if hc < EXIT_TH:
        return 0.0                  # below exit threshold: flat

    return float("nan")             # dead zone between thresholds: hold


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
- With `VOL_TARGETING = True`, `compute_signal` returns a fraction (e.g. `0.4`) instead of `1.0`; the fraction scales position so annualized vol targets 30%
- HC updates every 5 min; on `1h` interval each bar reflects the last finalized hourly value
- To adjust thresholds: change `ENTRY_TH` / `EXIT_TH` in config and re-run backtest

### Live Execution Timing

`trade_on_close=False`: signal fires at bar i close → fill at bar i+1 open.

```
bar i closes
  → compute_signal fires
  → signal changed → place market order immediately
  → fill at bar i+1 open
```
