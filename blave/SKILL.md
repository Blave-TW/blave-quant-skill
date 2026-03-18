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
    "timestamp": [1735803900.0, 1735804800.0, 1735805700.0, "..."]
  }
}
```

- `alpha` and `timestamp` arrays are aligned by index.
- `timestamp` is Unix timestamp in UTC+0.
- Higher alpha = more concentrated holdings.

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
    "timestamp": [1735803900.0, 1735804800.0, 1735805700.0, "..."]
  }
}
```

- `alpha` and `timestamp` arrays are aligned by index.
- `timestamp` is Unix timestamp in UTC+0.
- Positive alpha = taker buying dominance; negative = taker selling dominance.
