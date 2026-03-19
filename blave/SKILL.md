---
name: blave
description: Fetch market alpha data from Blave API.
---

# Blave Skill

This skill enables direct access to the Blave Data API for fetching crypto market alpha data.

## Authentication

All requests require the following headers (read from environment variables):

```
api-key: $blave_api_key
secret-key: $blave_secret_key
```

**Base URL:** `https://api.blave.org`

---

## Alpha Table

Retrieve the latest alpha values for all symbols across all indicators. Use this to screen and filter coins based on current alpha signals.

- **Method:** GET
- **Endpoint:** `https://api.blave.org/alpha_table`
- **Parameters:** none

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
response = requests.get("https://api.blave.org/alpha_table", headers=headers, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": {
    "BTCUSDT": {
      "funding_rate": {
        "binance": 0.01,
        "bybit": 0.01
      },
      "holder_concentration": {
        "-": -2.357
      },
      "holder_concentration_chg": {
        "15min": -0.001,
        "1h": -0.014,
        "4h": -0.267,
        "8h": -0.378,
        "24h": 0.261,
        "3d": -0.334,
        "7d": "",
        "30d": ""
      }
    }
  },
  "fields": [
    {
      "id": 1,
      "name": "holder_concentration",
      "name_en": "Holder Concentration",
      "name_zh": "籌碼集中度",
      "param": null
    }
  ],
  "note": {
    "1": [
      {
        "background_color": "#E46B6B",
        "color": "#591C1C",
        "max": -3,
        "min": "-Infinity",
        "note": { "en": "Overly Bearish", "zh": "過度看跌" }
      }
    ]
  }
}
```

- `data` — keyed by symbol; each symbol contains the latest alpha values per indicator.
- `fields` — metadata for each indicator (`id`, `name`, `name_en`, `name_zh`, `param`).
- `note` — keyed by indicator ID; defines color-coded interpretation ranges for each alpha value.
- Empty string `""` in `holder_concentration_chg` means insufficient data for that timeframe.

---

## Holder Concentration（籌碼集中度）

### Get Symbols

Retrieve all available symbols for Holder Concentration.

- **Method:** GET
- **Endpoint:** `https://api.blave.org/holder_concentration/get_symbols`

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
response = requests.get("https://api.blave.org/holder_concentration/get_symbols", headers=headers, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": ["BNBUSDT", "BTCUSDT", "ETHUSDT", "UMAUSDT"]
}
```

---

### Get Alpha

Retrieve Holder Concentration alpha values.

- **Method:** GET
- **Endpoint:** `https://api.blave.org/holder_concentration/get_alpha`
- **Parameters:**
  - `symbol` (required) — e.g. `BTCUSDT`
  - `period` (required) — `"5min"` / `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"1d"`
  - `start_date` (optional) — `YYYY-MM-DD`, e.g. `2024-01-04`
  - `end_date` (optional) — `YYYY-MM-DD`, e.g. `2025-01-04`
  - > The range between start_date and end_date cannot exceed 1 year.

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get("https://api.blave.org/holder_concentration/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": {
    "alpha": [-0.233, -0.234, -0.194, "..."],
    "timestamp": [1735803900.0, 1735804800.0, 1735805700.0, "..."],
    "stat": {
      "avg_down_return": -0.026,
      "avg_up_return": 0.028,
      "exp_value": -0.001,
      "is_data_sufficient": true,
      "return_ratio": 1.065,
      "up_prob": 0.462
    }
  }
}
```

- `alpha` and `timestamp` arrays are aligned by index.
- `timestamp` is Unix timestamp in UTC+0.
- Higher alpha = more concentrated holdings.
- `stat.up_prob` — 24h probability of upward movement.
- `stat.exp_value` — 24h expected return value.
- `stat.avg_up_return` / `stat.avg_down_return` — average 24h return when up/down.
- `stat.return_ratio` — ratio of avg up return to avg down return (absolute).

---

## Taker Intensity（多空力道）

### Get Symbols

Retrieve all available symbols for Taker Intensity.

- **Method:** GET
- **Endpoint:** `https://api.blave.org/taker_intensity/get_symbols`

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
response = requests.get("https://api.blave.org/taker_intensity/get_symbols", headers=headers, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": ["BNBUSDT", "BTCUSDT", "ETHUSDT", "UMAUSDT"]
}
```

---

### Get Alpha

Retrieve Taker Intensity alpha values.

- **Method:** GET
- **Endpoint:** `https://api.blave.org/taker_intensity/get_alpha`
- **Parameters:**
  - `symbol` (required) — e.g. `BTCUSDT`
  - `period` (required) — `"5min"` / `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"1d"`
  - `start_date` (optional) — `YYYY-MM-DD`, e.g. `2024-01-04`
  - `end_date` (optional) — `YYYY-MM-DD`, e.g. `2025-01-04`
  - `timeframe` (optional, default `"24h"`) — `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"24h"` / `"3d"`
  - > The range between start_date and end_date cannot exceed 1 year.

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get("https://api.blave.org/taker_intensity/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": {
    "alpha": [-0.233, -0.234, -0.194, "..."],
    "timestamp": [1735803900.0, 1735804800.0, 1735805700.0, "..."],
    "stat": {
      "avg_down_return": -0.026,
      "avg_up_return": 0.028,
      "exp_value": -0.001,
      "is_data_sufficient": true,
      "return_ratio": 1.065,
      "up_prob": 0.462
    }
  }
}
```

- `alpha` and `timestamp` arrays are aligned by index.
- `timestamp` is Unix timestamp in UTC+0.
- Positive alpha = taker buying dominance; negative = taker selling dominance.
- `stat.up_prob` — 24h probability of upward movement.
- `stat.exp_value` — 24h expected return value.
- `stat.avg_up_return` / `stat.avg_down_return` — average 24h return when up/down.
- `stat.return_ratio` — ratio of avg up return to avg down return (absolute).

---

## Whale Hunter（巨鯨警報）

### Get Symbols

Retrieve all available symbols for Whale Hunter.

- **Method:** GET
- **Endpoint:** `https://api.blave.org/whale_hunter/get_symbols`

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
response = requests.get("https://api.blave.org/whale_hunter/get_symbols", headers=headers, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": ["BNBUSDT", "BTCUSDT", "ETHUSDT", "UMAUSDT"]
}
```

---

### Get Alpha

Retrieve Whale Hunter alpha values.

- **Method:** GET
- **Endpoint:** `https://api.blave.org/whale_hunter/get_alpha`
- **Parameters:**
  - `symbol` (required) — e.g. `BTCUSDT`
  - `period` (required) — `"5min"` / `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"1d"`
  - `start_date` (optional) — `YYYY-MM-DD`, e.g. `2024-01-04`
  - `end_date` (optional) — `YYYY-MM-DD`, e.g. `2025-01-04`
  - `timeframe` (optional, default `"24h"`) — `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"24h"` / `"3d"`
  - `score_type` (optional, default `"score_oi"`) — `"score_oi"` / `"score_volume"`
  - > The range between start_date and end_date cannot exceed 1 year.

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h", "score_type": "score_oi"}
response = requests.get("https://api.blave.org/whale_hunter/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": {
    "alpha": [-0.233, -0.234, -0.194, "..."],
    "timestamp": [1735803900.0, 1735804800.0, 1735805700.0, "..."],
    "stat": {
      "avg_down_return": -0.026,
      "avg_up_return": 0.028,
      "exp_value": -0.001,
      "is_data_sufficient": true,
      "return_ratio": 1.065,
      "up_prob": 0.462
    }
  }
}
```

- `alpha` and `timestamp` arrays are aligned by index.
- `timestamp` is Unix timestamp in UTC+0.
- `score_oi` — whale activity scored by open interest; `score_volume` — scored by trading volume.
- `stat.up_prob` — 24h probability of upward movement.
- `stat.exp_value` — 24h expected return value.
- `stat.avg_up_return` / `stat.avg_down_return` — average 24h return when up/down.
- `stat.return_ratio` — ratio of avg up return to avg down return (absolute).
