---
name: blave
description: Fetch market alpha data from Blave API.
---

# Blave Skill

This skill enables direct access to the Blave Data API for fetching crypto market alpha data.

## API Access & Troubleshooting

If the user does not have an API key, or receives a `401 Unauthorized` / `403 Forbidden` error, guide them to subscribe to the **API Plan**:

> 👉 **[https://blave.org/landing/en/pricing](https://blave.org/landing/en/pricing)**
>
> - **API Plan** — $629/year, includes full data API access and commercial use.
> - **First-time subscribers** get a **14-day free trial** (credit card required, cancel anytime before trial ends and you won't be charged).

Once subscribed, create your API key at:

> 👉 **[https://blave.org/landing/en/api?tab=blave](https://blave.org/landing/en/api?tab=blave)**

Then add the credentials to your `.env` file:

```
blave_api_key=YOUR_API_KEY
blave_secret_key=YOUR_SECRET_KEY
```

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

---

## Kline（K線）

Retrieve OHLCV candlestick data for a symbol.

- **Method:** GET
- **Endpoint:** `https://api.blave.org/kline`
- **Parameters:**
  - `symbol` (required) — e.g. `BTCUSDT`
  - `period` (required) — `"5min"` / `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"1d"`
  - `start_date` (optional) — `YYYY-MM-DD`
  - `end_date` (optional) — `YYYY-MM-DD`

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get("https://api.blave.org/kline", headers=headers, params=params, timeout=60)
print(response.json())
```

**Response:**

```json
[
  {"time": 1735803900.0, "open": 94000.0, "high": 94500.0, "low": 93800.0, "close": 94200.0},
  {"time": 1735807500.0, "open": 94200.0, "high": 94800.0, "low": 94100.0, "close": 94600.0}
]
```

- `time` is Unix timestamp in UTC+0.

---

## Market Direction（市場方向）

Retrieve the Market Direction alpha (based on BTCUSDT).

- **Method:** GET
- **Endpoint:** `https://api.blave.org/market_direction/get_alpha`
- **Parameters:**
  - `period` (required) — `"5min"` / `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"1d"`
  - `start_date` (optional) — `YYYY-MM-DD`
  - `end_date` (optional) — `YYYY-MM-DD`
  - > No `symbol` parameter — always uses BTCUSDT.

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get("https://api.blave.org/market_direction/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": {
    "alpha": [-0.233, -0.234, "..."],
    "timestamp": [1735803900.0, 1735804800.0, "..."]
  }
}
```

---

## Market Sentiment（市場情緒）

### Get Symbols

- **Method:** GET
- **Endpoint:** `https://api.blave.org/market_sentiment/get_symbols`

**Response:**

```json
{ "data": ["BNBUSDT", "BTCUSDT", "ETHUSDT", "..."] }
```

---

### Get Alpha

- **Method:** GET
- **Endpoint:** `https://api.blave.org/market_sentiment/get_alpha`
- **Parameters:**
  - `symbol` (required) — e.g. `BTCUSDT`
  - `period` (required) — `"5min"` / `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"1d"`
  - `start_date` (optional) — `YYYY-MM-DD`
  - `end_date` (optional) — `YYYY-MM-DD`

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get("https://api.blave.org/market_sentiment/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": {
    "alpha": [-0.233, -0.234, "..."],
    "timestamp": [1735803900.0, 1735804800.0, "..."],
    "stat": {
      "avg_down_return": -0.026, "avg_up_return": 0.028,
      "exp_value": -0.001, "is_data_sufficient": true,
      "return_ratio": 1.065, "up_prob": 0.462
    }
  }
}
```

---

## Capital Shortage（資金稀缺）

Retrieve the Capital Shortage alpha (market-wide, based on BTC).

- **Method:** GET
- **Endpoint:** `https://api.blave.org/capital_shortage/get_alpha`
- **Parameters:**
  - `period` (required) — `"5min"` / `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"1d"`
  - `start_date` (optional) — `YYYY-MM-DD`
  - `end_date` (optional) — `YYYY-MM-DD`
  - > No `symbol` parameter — market-wide indicator.

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get("https://api.blave.org/capital_shortage/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": {
    "alpha": [-0.233, -0.234, "..."],
    "timestamp": [1735803900.0, 1735804800.0, "..."],
    "stat": {
      "avg_down_return": -0.026, "avg_up_return": 0.028,
      "exp_value": -0.001, "is_data_sufficient": true,
      "return_ratio": 1.065, "up_prob": 0.462
    }
  }
}
```

---

## Sector Rotation（板塊輪動）

Retrieve sector rotation history data.

- **Method:** GET
- **Endpoint:** `https://api.blave.org/sector_rotation/get_history_data`
- **Parameters:** none

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
response = requests.get("https://api.blave.org/sector_rotation/get_history_data", headers=headers, timeout=60)
print(response.json())
```

**Response:**

```json
{ "data": { "...": "..." } }
```

---

## Squeeze Momentum（擠壓動能）

### Get Symbols

- **Method:** GET
- **Endpoint:** `https://api.blave.org/squeeze_momentum/get_symbols`

**Response:**

```json
{ "data": ["BNBUSDT", "BTCUSDT", "ETHUSDT", "..."] }
```

---

### Get Alpha

- **Method:** GET
- **Endpoint:** `https://api.blave.org/squeeze_momentum/get_alpha`
- **Parameters:**
  - `symbol` (required) — e.g. `BTCUSDT`
  - `start_date` (optional) — `YYYY-MM-DD`
  - `end_date` (optional) — `YYYY-MM-DD`
  - > Period is fixed to `"1d"` — no `period` parameter needed.

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
params = {"symbol": "BTCUSDT", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get("https://api.blave.org/squeeze_momentum/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": {
    "alpha": [-0.233, -0.234, "..."],
    "timestamp": [1735803900.0, 1735804800.0, "..."],
    "scolor": ["green", "red", "..."],
    "stat": {
      "avg_down_return": -0.026, "avg_up_return": 0.028,
      "exp_value": -0.001, "is_data_sufficient": true,
      "return_ratio": 1.065, "up_prob": 0.462
    }
  }
}
```

- `scolor` — color label aligned with alpha/timestamp arrays; indicates momentum direction.

---

## Blave Top Trader Exposure（頂級交易員曝險）

Retrieve Blave Top Trader net exposure (based on BTCUSDT).

- **Method:** GET
- **Endpoint:** `https://api.blave.org/blave_top_trader/get_exposure`
- **Parameters:**
  - `period` (required) — `"5min"` / `"15min"` / `"1h"` / `"4h"` / `"8h"` / `"1d"`
  - `start_date` (optional) — `YYYY-MM-DD`
  - `end_date` (optional) — `YYYY-MM-DD`
  - > No `symbol` parameter — always uses BTCUSDT.

**Example:**

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {"api-key": os.getenv("blave_api_key"), "secret-key": os.getenv("blave_secret_key")}
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get("https://api.blave.org/blave_top_trader/get_exposure", headers=headers, params=params, timeout=60)
print(response.json())
```

**Response:**

```json
{
  "data": {
    "alpha": [-0.233, -0.234, "..."],
    "timestamp": [1735803900.0, 1735804800.0, "..."]
  }
}
```
