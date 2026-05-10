# Blave API Examples

Full Python examples for all Blave API endpoints.

## Setup

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {
    "api-key": os.getenv("blave_api_key"),
    "secret-key": os.getenv("blave_secret_key"),
}
BASE_URL = "https://api.blave.org"
```

---

## Price

```python
params = {"symbol": "BTCUSDT"}
response = requests.get(f"{BASE_URL}/price", headers=headers, params=params, timeout=60)
print(response.json())
# {"symbol": "BTCUSDT", "price": 95000.0, "change_24h": 2.5}
```

---

## Alpha Table

```python
response = requests.get(f"{BASE_URL}/alpha_table", headers=headers, timeout=60)
print(response.json())
```

---

## Kline

```python
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/kline", headers=headers, params=params, timeout=60)
raw = response.json()
# returns a list directly (NOT {"data": [...]}):
# [{"date": "2025-01-01 00:00:00", "open": 94000.0, "high": 95500.0, "low": 93200.0, "close": 95000.0, "volume": 1234.5}, ...]
data = raw if isinstance(raw, list) else raw.get("data", [])
```

---

## Market Direction

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/market_direction/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Market Sentiment

```python
# Get symbols
response = requests.get(f"{BASE_URL}/market_sentiment/get_symbols", headers=headers, timeout=60)

# Get alpha
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/market_sentiment/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Capital Shortage

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/capital_shortage/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Holder Concentration

```python
# Get symbols
response = requests.get(f"{BASE_URL}/holder_concentration/get_symbols", headers=headers, timeout=60)

# Get alpha
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/holder_concentration/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Taker Intensity

```python
# Get symbols
response = requests.get(f"{BASE_URL}/taker_intensity/get_symbols", headers=headers, timeout=60)

# Get alpha
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/taker_intensity/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Whale Hunter

```python
# Get symbols
response = requests.get(f"{BASE_URL}/whale_hunter/get_symbols", headers=headers, timeout=60)

# Get alpha
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h", "score_type": "score_oi"}
response = requests.get(f"{BASE_URL}/whale_hunter/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Squeeze Momentum

```python
# Get symbols
response = requests.get(f"{BASE_URL}/squeeze_momentum/get_symbols", headers=headers, timeout=60)

# Get alpha (period fixed to 1d)
params = {"symbol": "BTCUSDT", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/squeeze_momentum/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Sector Rotation

```python
response = requests.get(f"{BASE_URL}/sector_rotation/get_history_data", headers=headers, timeout=60)
print(response.json())
```

---

## Blave Top Trader Exposure

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/blave_top_trader/get_exposure", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Taiwan Stock Daily Price

Raw unadjusted daily OHLCV. `start` / `end` are optional (omit for full history).

```python
params = {"start": "2020-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/price/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "2020-01-02", "stock_id": "2330", "open": 335.0, "high": 338.5,
#   "low": 334.0, "close": 337.0, "spread": 2.0,
#   "volume": 33282120, "turnover_value": 11224165450, "turnover_count": 17160}, ...]
```

---

## Taiwan Stock Daily Price — Forward Adjusted (向後調整)

Prices adjusted for cash and stock dividends using forward (後復權) method:
historical prices are unchanged; prices from each ex-dividend date onward are
multiplied by the cumulative adjustment factor. Suitable for backtesting total return.

```python
params = {"start": "2020-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/price_adj/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# Same schema as /price but close/open/high/low are dividend-adjusted.
# Adjusted prices will be higher than raw for recent periods (dividends compound forward).
```

**Stock ID examples:** `2330` (台積電), `0050` (元大台灣50), `2317` (鴻海), `006208` (富邦台50)

---

## Taiwan Stock Institutional Investors — 三大法人

Daily buy/sell shares by institutional investor type (wide format, one row per trading day).
`start` / `end` optional (omit for full history).

```python
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/institutional/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "2024-01-02", "stock_id": "2330",
#   "foreign_buy": 28464159, "foreign_sell": 47404324,
#   "trust_buy": 5553520,   "trust_sell": 269712,
#   "dealer_self_buy": 452000, "dealer_self_sell": 366190,
#   "dealer_hedge_buy": 942546, "dealer_hedge_sell": 780090,
#   "foreign_dealer_self_buy": 0, "foreign_dealer_self_sell": 0}, ...]
```

**Field meanings:**
| Field | Investor type |
|---|---|
| `foreign_*` | 外資 (Foreign Investor) — 最常被追蹤 |
| `trust_*` | 投信 (Investment Trust) |
| `dealer_self_*` | 自營商自行買賣 (Dealer self) |
| `dealer_hedge_*` | 自營商避險 (Dealer hedging) |
| `foreign_dealer_self_*` | 外資自營 (Foreign Dealer Self) — 多為 0 |

Net buy = `*_buy - *_sell`. Use for 籌碼面分析、外資進出追蹤、與股價走勢交叉比對。
Values are **shares** (股), not dollars.

---

## alpha_table Field Reference

Each symbol in `/alpha_table` contains:

| Field | Description |
|---|---|
| `statistics` | `up_prob` (prob of 24h upward move), `exp_value` (expected return), `avg_up_return`, `avg_down_return`, `return_ratio`, `is_data_sufficient` |
| `price` | `{"-": 70000}` — current price |
| `price_change` | `{"15min": ..., "1h": ..., "24h": ...}` — % change |
| `market_cap` | `{"-": 1234567890}` — USD market cap |
| `market_cap_percentile` | `{"-": 85.3}` — percentile among all listed coins |
| `funding_rate` | `{"binance": -0.01, ...}` — per exchange |
| `oi_imbalance` | `{"-": 0.12}` — OI imbalance |

`fields` = indicator metadata. `note` = color ranges. `""` = insufficient data.

Use `statistics.up_prob` and `statistics.exp_value` for screening. Always check `is_data_sufficient` before using `statistics`.
