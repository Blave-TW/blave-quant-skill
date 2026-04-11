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
print(response.json())
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
