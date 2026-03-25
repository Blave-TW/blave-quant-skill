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
