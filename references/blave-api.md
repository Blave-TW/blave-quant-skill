# Blave API Reference

The single reference for the Blave data API: every endpoint's path, parameters, response,
errors, and a Python example.

## Conventions

**Base URL:** `https://api.blave.org` — every path below is relative to it.

**Auth headers:** `api-key` + `secret-key` on every request (create a key at
<https://blave.org/landing/en/api?tab=blave>).

**Access** — what the key's account needs, per endpoint (`Access` row in each block):

| Value | Meaning |
|---|---|
| `API plan or data fee` | Valid key, and the account has an active API plan, or owns a Blave Agent machine, or is billed the hourly API data fee in credit. Out of credit → `403 ERR007` |
| `Any valid key` | Valid key only — no plan check, no data fee |

**Rate limit** — unless a block says otherwise: 500 requests / 5 min per API key, and
500 requests / 5 min per IP. The window resets after 5 minutes.

**Shared errors** (endpoint-specific errors are listed in each block):

| Status | Body | When |
|---|---|---|
| 403 | `{"error_code": "ERR005", "message": "API key and Secret key are required."}` | Header missing (`API plan or data fee` endpoints) |
| 422 | `{"error_code": "ERR001", "message": "Token is invalid or expired."}` | Header missing (`Any valid key` endpoints) |
| 403 | `{"error_code": "ERR005", "message": "Invalid API key."}` / `"Invalid Secret key."` | Wrong key pair |
| 403 | `{"error_code": "ERR007", "message": "Insufficient credit. Please top up."}` | Data fee could not be charged |
| 429 | `{"error_code": "ERR429", "message": "Rate limit exceeded."}` | Rate limit hit |
| 500 | `{"error": "Internal error"}` or an HTML error page | Unexpected server error |

**Timestamps** are UTC unless a block says otherwise. Taiwan market `date` fields are
Taipei trading days (`YYYY-MM-DD`).

**Endpoint block format.** Each endpoint is a `##` heading of the form `` `METHOD /path` ``,
followed in fixed order by: an attribute table (`Name`, `Group`, `Access`, `Rate limit`,
`Data from`, `Update`, `Source`), **Parameters**, **Response**, **Errors**, **Example**,
**Notes**. Top-level `#` headings are categories. `待確認` marks a value not yet verified
against the live API — including example responses that were not captured from a live call.

### Crypto indicator conventions

Shared by every crypto `get_alpha` / `get_exposure` endpoint:

- **`period`** — bar size, `{n}min` / `{n}h` / `{n}d` (`{n}m` is read as minutes). Documented
  values are `5min`, `15min`, `1h`, `4h`, `8h`, `1d`; indicators with a coarser minimum say so
  in their block. A missing or unparseable `period` is a `403 {"error": "period is required"}`
  (a `400` on `unusual_movement` and `liquidation`).
- **`start_date` / `end_date`** — `YYYY-MM-DD` (UTC). `end_date` defaults to today; `start_date`
  defaults to `end_date` − 365 days. A range longer than 365 days is **silently clamped**
  (`start_date` moved to `end_date` − 365 days). A malformed date is not validated and ends in
  a `500` — always send `YYYY-MM-DD`.
- **`symbol`** — Binance USDT-M perpetual, e.g. `BTCUSDT`; `BTC`, `btc`, `BTC/USDT`, `BTC-USDT`
  are also accepted (a bare token gets `USDT` appended). The `get_symbols` endpoints list the
  covered symbols.
- **Only closed bars** are returned — the still-forming last bar is dropped.
- Response is `{"data": {"timestamp": [...], "alpha": [...], ...}}` — parallel arrays, one
  element per bar. `timestamp` is Unix seconds (UTC), the bar label.
- For history beyond 365 days, send one request per year and concatenate.

**`stat` object** — returned by indicators whose block lists it. A logistic model fitted on
the symbol's past year of this indicator versus the next-24h price move:

| Field | Type | Description |
|---|---|---|
| `up_prob` | float | Probability of a 24h up move given the latest indicator value (0–1) |
| `avg_up_return` | float | Mean 24h return over past up moves (decimal, 0.02 = +2%) |
| `avg_down_return` | float | Mean 24h return over past down moves (decimal, negative) |
| `return_ratio` | float | `-avg_up_return / avg_down_return` |
| `exp_value` | float | `up_prob × avg_up_return + (1 − up_prob) × avg_down_return` |
| `is_data_sufficient` | bool | `false` when the symbol has less than one year of history — do not rely on the other fields then |

When there is no data the object falls back to `up_prob` 0.5 and zeros.

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

## Related references

These Blave services have their own reference files and are not duplicated here:

- Hyperliquid top-trader tracking (`/hyperliquid/*`) → `references/hyperliquid-api.md`
- TradingView alert stream (`/sse/tradingview/stream`) → `references/tradingview-stream.md`
- Strategy marketplace (`/openclaw/marketplace/*`) → `references/marketplace.md`
- Indicator interpretation (what alpha values mean) → `references/blave-indicator-guide.md`

---

# Crypto

## `GET /price`

| | |
|---|---|
| Name | 即時價格 Current Price |
| Group | Crypto › General |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot only (no history) |
| Update | Server cache 5 s |
| Source | Blave price feed for USDT pairs（待確認：上游交易所） |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | `BTCUSDT` or `BTC` (case-insensitive) | Token or USDT pair |

**Response** — a flat object.

| Field | Type | Unit | Description |
|---|---|---|---|
| `symbol` | string | — | The **token** without `USDT` (e.g. `BTC`, even when `BTCUSDT` was sent) |
| `price` | float | USDT | Latest price |
| `change_24h` | float | decimal | 24h change as a fraction (`0.025` = +2.5%) |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "symbol is required"}` | `symbol` missing |
| 404 | `{"error": "symbol <SYMBOL> not found"}` | No price for that token |

**Example**

```python
response = requests.get(f"{BASE_URL}/price", headers=headers, params={"symbol": "BTCUSDT"}, timeout=30)
print(response.json())
# {"symbol": "BTC", "price": 95000.0, "change_24h": 0.025}   ← 待確認：未實抓
```

---

## `GET /alpha_table`

| | |
|---|---|
| Name | Alpha 總表 Alpha Table |
| Group | Crypto › General |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot only (latest value per symbol) |
| Update | Every 5 minutes |
| Source | Blave |

**Parameters** — none.

**Response** — `{"data": {<TOKEN>: {...}}, "fields": [...], "note": {...}}`.

`data` is keyed by token (`BTC`, `1INCH`, …). Each token maps indicator name → `{param: value}`
(`"-"` when the indicator has no parameter). `""` = insufficient data. Besides the indicators:

| Key | Description |
|---|---|
| `statistics` | `up_prob` (prob. of a 24h up move), `exp_value` (expected return), `avg_up_return`, `avg_down_return`, `return_ratio`, `is_data_sufficient` |
| `price` | `{"-": 70000}` — current price |
| `price_change` | `{"15min": ..., "1h": ..., "24h": ...}` — % change |
| `market_cap` | `{"-": 1234567890}` — USD market cap |
| `market_cap_percentile` | `{"-": 85.3}` — percentile among all listed coins |
| `funding_rate` | `{"binance": -0.01, ...}` — per exchange |
| `oi_imbalance` | `{"-": 0.12}` — OI imbalance (full detail: `/oi_imbalance/get_overview_data`) |

`fields` — one entry per indicator: `id`, `name` (key used in `data`), `param` (parameter
name or `null`), `name_en`, `name_zh`.

`note` — keyed by indicator id: a list of value bands `{min, max, note: {en, zh}, direction:
{en, zh}, color, background_color}` used to label a value (e.g. `max: -3` → "Overly Bearish").

**Errors** — shared errors only.

**Example**

```python
response = requests.get(f"{BASE_URL}/alpha_table", headers=headers, timeout=60)
body = response.json()
btc = body["data"]["BTC"]
# {"holder_concentration": {"-": -2.35}, "holder_concentration_chg": {"15min": -0.001, ...},
#  "funding_rate": {"binance": 0.01, ...}, "statistics": {...}, ...}   ← 待確認：未實抓
```

**Notes**
- Use this first for any multi-coin screen or ranking — one request covers every symbol.
- Always check `statistics.is_data_sufficient` before using `statistics`.
- Always fetch fresh; do not reuse an earlier response.

---

## `GET /kline`

| | |
|---|---|
| Name | K 線 Kline (OHLCV) |
| Group | Crypto › General |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | The symbol's Binance USDT-M perpetual listing date |
| Update | Near-real-time. Server cache: 30 s (`1min`), 300 s (`1h` / `4h` / `1d`), 60 s (every other period) |
| Source | Binance USDT-M futures (live API for recent bars, Binance official archive for older months) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | `BTCUSDT`; also `BTC`, `btc`, `BTC/USDT`, `BTC-USDT` | Binance USDT-M perpetual. A bare token gets `USDT` appended |
| `period` | query | string | yes | — | `{n}min` / `{n}h` / `{n}d`, minimum `1min` (e.g. `1min`, `3min`, `15min`, `2h`, `1d`, `7d`). `{n}m` is read as minutes (`15m` = `15min`) | Bar size. Any whole-minute size is accepted, not only the listed examples |
| `start_date` | query | string | no | `end_date` − 365 days (period ≥ `5min`); `end_date` − 30 days (period < `5min`) | `YYYY-MM-DD` (UTC) | First day, inclusive |
| `end_date` | query | string | no | now | `YYYY-MM-DD` (UTC) | Last day, inclusive (bars through the end of that UTC day) |

Per-request window: period ≥ `5min` → at most 365 days; a longer range is **silently
clamped** (`start_date` moved to `end_date` − 365 days, no error). Period < `5min` → at most
30 days; a longer range is a `400`.

**Response** — a bare JSON array (not wrapped in `{"data": ...}`), ascending by time.

| Field | Type | Unit | Description |
|---|---|---|---|
| `time` | float | Unix seconds (UTC) | Bar open time |
| `open` / `high` / `low` / `close` | float | quote currency (USDT) | Prices |
| `volume` | float \| null | base asset | Traded volume; `null` when the source has no volume for that bar |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "symbol is required"}` | `symbol` missing |
| 403 | `{"error": "period is required"}` | `period` missing **or not parseable** |
| 400 | `{"error": "minimum supported period is 1min"}` | `period` below one minute |
| 400 | `{"error": "periods below 5min must be a whole number of minutes"}` | e.g. `90s` |
| 400 | `{"error": "date range exceeds max 30 days for periods below 5min"}` | Period < `5min` and range > 30 days |
| 400 | `{"error": "invalid date format, expected YYYY-MM-DD"}` | Malformed `start_date` / `end_date` |
| 400 | `{"error": "unknown symbol or no data: <symbol>"}` | Symbol not on Binance USDT-M |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2026-08-04", "end_date": "2026-08-07"}
response = requests.get(f"{BASE_URL}/kline", headers=headers, params=params, timeout=120)
data = response.json()
# [{"time": 1785801600.0, "open": 63497.1, "high": 63558.8, "low": 63290.2, "close": 63337.6, "volume": 4583.87}, ...]
```

**Notes**
- A window entirely before the symbol's listing date returns `200` with `[]`, not an error.
- The last bar can still be forming when `end_date` is today — drop it if you need closed bars only.
- For history beyond one window, send one request per window and concatenate (e.g. 3 years of
  `5min` = 3 requests; 1 year of `1min` = 13 requests of ≤30 days).
- The first request for a symbol/range not yet cached server-side can take tens of seconds;
  use a generous `timeout`.

---

## `GET /market_direction/get_alpha`

| | |
|---|---|
| Name | 市場方向 Market Direction |
| Group | Crypto › Tool |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Every 5 minutes |
| Source | Blave (computed on BTCUSDT) |

**Parameters** — no `symbol`; always BTCUSDT. See *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `period` | query | string | yes | — | `1h`, `4h`, `8h`, `1d` (minimum `1h`) | Bar size |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...]}}`. No `stat`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | Market direction value |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "period is required"}` | `period` missing or unparseable |

**Example**

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/market_direction/get_alpha", headers=headers, params=params, timeout=60)
# {"data": {"alpha": [-0.233, -0.234, ...], "timestamp": [1735803900.0, ...]}}   ← 待確認：未實抓
```

---

## `GET /screener/get_saved_conditions`

| | |
|---|---|
| Name | 篩選器已存條件 Screener Saved Conditions |
| Group | Crypto › Tool |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | — |
| Update | Live (reads the account's saved conditions) |
| Source | Blave |

**Parameters** — none.

**Response** — `{"data": {<condition_id>: {"filters": [...], ...}}}`, keyed by condition id
（待確認：每個條件物件的完整欄位）.

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "unsupported api feature"}` | Key not tied to a user account |

**Example**

```python
response = requests.get(f"{BASE_URL}/screener/get_saved_conditions", headers=headers, timeout=30)
conditions = response.json()["data"]
```

---

## `GET /screener/get_saved_condition_result`

| | |
|---|---|
| Name | 篩選器結果 Screener Condition Result |
| Group | Crypto › Tool |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot (current alpha values) |
| Update | Every 5 minutes |
| Source | Blave |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `condition_id` | query | int | yes | — | An id from `get_saved_conditions` | Condition to run |

**Response** — `{"data": ...}` with the symbols matching the condition（待確認：Notion 寫
`{"alpha_names": [...], "symbols": [...]}`，需實抓確認）.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Missing parameter: condition_id is required."}` | Missing |
| 400 | `{"error": "Invalid parameter: condition_id must be an integer."}` | Not an integer |
| 404 | `{"error": "Invalid condition_id: <id> not found for user."}` | Not one of this account's conditions |
| 403 | `{"error": "unsupported api feature"}` | Key not tied to a user account |

**Example**

```python
response = requests.get(f"{BASE_URL}/screener/get_saved_condition_result", headers=headers,
                        params={"condition_id": 12}, timeout=60)
```

---

## `GET /holder_concentration/get_symbols`

| | |
|---|---|
| Name | 籌碼集中度幣種清單 Holder Concentration Symbols |
| Group | Crypto › Alpha › Holder Concentration |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | — |
| Update | 待確認 |
| Source | Blave (Binance USDT-M symbol list) |

**Parameters** — none.

**Response** — `{"data": ["BNBUSDT", "BTCUSDT", ...]}`, sorted.

**Errors** — shared errors only.

**Example**

```python
symbols = requests.get(f"{BASE_URL}/holder_concentration/get_symbols", headers=headers, timeout=30).json()["data"]
```

**Notes**
- Every `*/get_symbols` crypto endpoint currently returns the same Binance USDT-M symbol list.

---

## `GET /holder_concentration/get_alpha`

| | |
|---|---|
| Name | 籌碼集中度 Holder Concentration |
| Group | Crypto › Alpha › Holder Concentration |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Every 5 minutes |
| Source | Blave (Binance global long/short account ratio) |

**Parameters** — see *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `period` | query | string | yes | — | `5min`, `15min`, `1h`, `4h`, `8h`, `1d` | Bar size |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...], "stat": {...}}}`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | Z-score of the log long/short account ratio vs its 30-day mean, sign-flipped — higher = more concentrated |
| `stat` | object | See *`stat` object* |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "symbol is required"}` / `{"error": "period is required"}` | Missing parameter |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/holder_concentration/get_alpha", headers=headers, params=params, timeout=60)
# {"data": {"alpha": [-0.233, ...], "timestamp": [1735803900.0, ...],
#           "stat": {"up_prob": 0.46, "exp_value": -0.0012, "is_data_sufficient": true, ...}}}   ← 待確認：未實抓
```

---

## `GET /funding_rate/get_alpha`

| | |
|---|---|
| Name | 資金費率 Funding Rate |
| Group | Crypto › Alpha › Funding Rate |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Every 5 minutes |
| Source | Binance USDT-M funding rate |

**Parameters** — see *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `period` | query | string | yes | — | `5min`, `15min`, `1h`, `4h`, `8h`, `1d` | Bar size |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...], "close": [...], "stat": {...}}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) | Bar label |
| `alpha` | float[] | percent | Funding rate × 100 (`0.01` = 0.01%); positive = longs pay shorts |
| `close` | float[] | USDT | Perpetual close price |
| `stat` | object | — | See *`stat` object* |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "symbol is required"}` / `{"error": "period is required"}` | Missing parameter |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/funding_rate/get_alpha", headers=headers, params=params, timeout=60)
# {"data": {"timestamp": [1735689600.0, ...], "alpha": [0.01, ...], "close": [93000.0, ...], "stat": {...}}}   ← 待確認：未實抓
```

---

## `GET /market_sentiment/get_symbols`

| | |
|---|---|
| Name | 市場情緒幣種清單 Market Sentiment Symbols |
| Group | Crypto › Alpha › Market Sentiment |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | — |
| Update | 待確認 |
| Source | Blave (Binance USDT-M symbol list) |

**Parameters** — none.

**Response** — `{"data": ["BNBUSDT", "BTCUSDT", ...]}`, sorted.

**Errors** — shared errors only.

**Example**

```python
symbols = requests.get(f"{BASE_URL}/market_sentiment/get_symbols", headers=headers, timeout=30).json()["data"]
```

---

## `GET /market_sentiment/get_alpha`

| | |
|---|---|
| Name | 市場情緒 Market Sentiment |
| Group | Crypto › Alpha › Market Sentiment |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Every 5 minutes |
| Source | Blave |

**Parameters** — see *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `period` | query | string | yes | — | `5min`, `15min`, `1h`, `4h`, `8h`, `1d` | Bar size |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...], "stat": {...}}}`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | Market sentiment value |
| `stat` | object | See *`stat` object* |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "symbol is required"}` / `{"error": "period is required"}` | Missing parameter |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/market_sentiment/get_alpha", headers=headers, params=params, timeout=60)
```

---

## `GET /capital_shortage/get_alpha`

| | |
|---|---|
| Name | 資金稀缺 Capital Shortage |
| Group | Crypto › Alpha › Capital Shortage |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Every 5 minutes |
| Source | Blave (market-wide, Binance USDT lending APR) |

**Parameters** — no `symbol`; market-wide. See *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `period` | query | string | yes | — | `1h`, `4h`, `8h`, `1d`（待確認：最小週期） | Bar size |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...], "stat": {...}}}`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | Capital shortage value |
| `stat` | object | See *`stat` object* (computed against BTC) |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "period is required"}` | Missing parameter |

**Example**

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/capital_shortage/get_alpha", headers=headers, params=params, timeout=60)
```

---

## `GET /sector_rotation/get_history_data`

| | |
|---|---|
| Name | 板塊輪動歷史 Sector Rotation History |
| Group | Crypto › Alpha › Sector Rotation |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | 待確認 |
| Source | Blave |

**Parameters** — none.

**Response** — `{"data": {"alpha": {<sector>: {"data": [...], "name_en": ..., "name_zh": ...}}}}`
（待確認：`data` 陣列對應的時間軸欄位）.

**Errors** — shared errors only.

**Example**

```python
response = requests.get(f"{BASE_URL}/sector_rotation/get_history_data", headers=headers, timeout=60)
# {"data": {"alpha": {"AI": {"data": [0.0, -0.0113, ...], "name_en": "AI", "name_zh": "人工智能"}, ...}}}
```

---

## `GET /sector_rotation/get_overview_data`

| | |
|---|---|
| Name | 板塊輪動熱圖 Sector Rotation Overview |
| Group | Crypto › Alpha › Sector Rotation |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot |
| Update | 待確認 |
| Source | Blave |

**Parameters** — none.

**Response** — `{"data": {<sector>: {"name_en", "name_zh", "data", "symbols"}}}` (~48 sectors).

| Field | Description |
|---|---|
| `data` | `{<timeframe>: {"pct_change": float}}` for `1h`, `8h`, `24h`, `3d`, `7d`, `30d`, `90d`; `pct_change` is a decimal (`0.0061` = +0.61%) |
| `symbols` | `{<token>: {"id": int, "data": {<timeframe>: {"pct_change": float}}}}` — per-token breakdown |

**Errors** — shared errors only.

**Example**

```python
data = requests.get(f"{BASE_URL}/sector_rotation/get_overview_data", headers=headers, timeout=60).json()["data"]
# {"AI": {"name_en": "AI", "name_zh": "人工智能",
#         "data": {"1h": {"pct_change": 0.0076}, "8h": ..., "90d": ...},
#         "symbols": {"0G": {"id": 38337, "data": {"1h": {"pct_change": 0.0061}, ...}}, ...}}, ...}
```

---

## `GET /oi_imbalance/get_overview_data`

| | |
|---|---|
| Name | OI 失衡 OI Imbalance |
| Group | Crypto › Alpha › OI Imbalance |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot |
| Update | 待確認 |
| Source | Blave (Binance / OKX / BingX futures OI) |

**Parameters** — none.

**Response** — `{"data": [...]}`, sorted by `alpha` descending.

| Field | Type | Unit | Description |
|---|---|---|---|
| `token` | string | — | Token |
| `token_id` | int | — | Blave token id |
| `token_price` | float | USD | Price |
| `token_chg` | float | decimal | Price change |
| `market_cap` | float | USD | Market cap |
| `oi_total` | float | USD | Futures OI summed across Binance / OKX / BingX |
| `alpha` | float | ratio | `oi_total / market_cap` — high = OI crowded relative to size (squeeze / volatility risk) |

**Errors** — shared errors only.

**Example**

```python
data = requests.get(f"{BASE_URL}/oi_imbalance/get_overview_data", headers=headers, timeout=60).json()["data"]
# [{"token": "TSLA", "token_id": 39618, "token_price": 313.33, "token_chg": 0.031,
#   "market_cap": 40415.98, "oi_total": 59916616.78, "alpha": 1482.5}, ...]
```

**Notes**
- `/alpha_table`'s `oi_imbalance` carries only the final `alpha`; this endpoint has the full table.

---

## `GET /whale_hunter/get_symbols`

| | |
|---|---|
| Name | 巨鯨警報幣種清單 Whale Hunter Symbols |
| Group | Crypto › Alpha › Whale Hunter |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | — |
| Update | 待確認 |
| Source | Blave (Binance USDT-M symbol list) |

**Parameters** — none.

**Response** — `{"data": ["BNBUSDT", "BTCUSDT", ...]}`, sorted.

**Errors** — shared errors only.

**Example**

```python
symbols = requests.get(f"{BASE_URL}/whale_hunter/get_symbols", headers=headers, timeout=30).json()["data"]
```

---

## `GET /whale_hunter/get_alpha`

| | |
|---|---|
| Name | 巨鯨警報 Whale Hunter |
| Group | Crypto › Alpha › Whale Hunter |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Every 5 minutes |
| Source | Blave (Binance USDT-M open interest and volume) |

**Parameters** — see *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `period` | query | string | yes | — | `5min`, `15min`, `1h`, `4h`, `8h`, `1d` | Bar size |
| `timeframe` | query | string | no | `24h` | `15min`, `1h`, `4h`, `8h`, `24h`, `3d` | Rolling window the flow is summed over |
| `score_type` | query | string | no | `score_oi` | `score_oi`, `score_volume` | Open-interest change or volume |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...], "stat": {...}}}`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | Z-score of the `timeframe`-summed OI change (or volume) vs its 30-day mean |
| `stat` | object | See *`stat` object* |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "symbol is required"}` / `{"error": "period is required"}` | Missing parameter |
| 403 | `{"error": "Invalid score_type"}` | `score_type` not allowed |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h", "score_type": "score_oi"}
response = requests.get(f"{BASE_URL}/whale_hunter/get_alpha", headers=headers, params=params, timeout=60)
```

**Notes**
- `timeframe` is not validated server-side; values outside the list are 待確認.

---

## `GET /taker_intensity/get_symbols`

| | |
|---|---|
| Name | 多空力道幣種清單 Taker Intensity Symbols |
| Group | Crypto › Alpha › Taker Intensity |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | — |
| Update | 待確認 |
| Source | Blave (Binance USDT-M symbol list) |

**Parameters** — none.

**Response** — `{"data": ["BNBUSDT", "BTCUSDT", ...]}`, sorted.

**Errors** — shared errors only.

**Example**

```python
symbols = requests.get(f"{BASE_URL}/taker_intensity/get_symbols", headers=headers, timeout=30).json()["data"]
```

---

## `GET /taker_intensity/get_alpha`

| | |
|---|---|
| Name | 多空力道 Taker Intensity |
| Group | Crypto › Alpha › Taker Intensity |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Every 5 minutes |
| Source | Blave (Binance USDT-M taker buy/sell volume) |

**Parameters** — see *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `period` | query | string | yes | — | `5min`, `15min`, `1h`, `4h`, `8h`, `1d` | Bar size |
| `timeframe` | query | string | no | `24h` | `15min`, `1h`, `4h`, `8h`, `24h`, `3d` | Rolling window |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...], "stat": {...}}}`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | Z-score of `timeframe`-summed (taker buy − taker sell) volume vs its 30-day mean; positive = net buying |
| `stat` | object | See *`stat` object* |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "symbol is required"}` / `{"error": "period is required"}` | Missing parameter |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/taker_intensity/get_alpha", headers=headers, params=params, timeout=60)
```

---

## `GET /unusual_movement/get_symbols`

| | |
|---|---|
| Name | 異常漲跌幣種清單 Unusual Movement Symbols |
| Group | Crypto › Alpha › Unusual Movement |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | — |
| Update | 待確認 |
| Source | Blave (Binance USDT-M symbol list) |

**Parameters** — none.

**Response** — `{"data": ["BNBUSDT", "BTCUSDT", ...]}`, sorted.

**Errors** — shared errors only.

**Example**

```python
symbols = requests.get(f"{BASE_URL}/unusual_movement/get_symbols", headers=headers, timeout=30).json()["data"]
```

---

## `GET /unusual_movement/get_alpha`

| | |
|---|---|
| Name | 異常漲跌 Unusual Movement |
| Group | Crypto › Alpha › Unusual Movement |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Every 5 minutes |
| Source | Blave (Binance USDT-M price) |

**Parameters** — see *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `period` | query | string | yes | — | `5min`, `15min`, `1h`, `4h`, `8h`, `1d` | Bar size |
| `timeframe` | query | string | no | `24h` | `15min`, `1h`, `4h`, `8h`, `24h`, `3d`, `7d` | Window the move is measured over |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...], "close": [...], "stat": {...}}}`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | Return over `timeframe` divided by 365-day volatility scaled to that window — large \|alpha\| = outlier |
| `close` | float[] | Close price (USDT) |
| `stat` | object | See *`stat` object* |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "symbol is required"}` / `{"error": "period is required"}` | Missing parameter |
| 500 | server error | `timeframe` outside the allowed list |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h"}
response = requests.get(f"{BASE_URL}/unusual_movement/get_alpha", headers=headers, params=params, timeout=60)
```

---

## `GET /squeeze_momentum/get_symbols`

| | |
|---|---|
| Name | 擠壓動能幣種清單 Squeeze Momentum Symbols |
| Group | Crypto › Alpha › Squeeze Momentum |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | — |
| Update | 待確認 |
| Source | Blave (Binance USDT-M symbol list) |

**Parameters** — none.

**Response** — `{"data": ["BNBUSDT", "BTCUSDT", ...]}`, sorted.

**Errors** — shared errors only.

**Example**

```python
symbols = requests.get(f"{BASE_URL}/squeeze_momentum/get_symbols", headers=headers, timeout=30).json()["data"]
```

---

## `GET /squeeze_momentum/get_alpha`

| | |
|---|---|
| Name | 擠壓動能 Squeeze Momentum |
| Group | Crypto › Alpha › Squeeze Momentum |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Daily bars |
| Source | Blave (Binance USDT-M price) |

**Parameters** — no `period`; fixed to `1d`. See *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...], "scolor": [...], "stat": {...}}}`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC), daily |
| `alpha` | float[] | Momentum value |
| `scolor` | string[] | `black` = squeeze on (Bollinger Bands inside Keltner Channels), `grey` = squeeze off |
| `stat` | object | See *`stat` object* |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "symbol is required"}` | Missing parameter |

**Example**

```python
params = {"symbol": "BTCUSDT", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/squeeze_momentum/get_alpha", headers=headers, params=params, timeout=60)
# {"data": {"alpha": [-0.2256, ...], "scolor": ["black", ...], "timestamp": [...], "stat": {...}}}
```

---

## `GET /blave_top_trader/get_exposure`

| | |
|---|---|
| Name | Blave 頂尖交易員曝險 Blave Top Trader Exposure |
| Group | Crypto › Alpha › Blave Top Trader |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Every 5 minutes |
| Source | Blave (BTCUSDT) |

**Parameters** — no `symbol`; always BTCUSDT. See *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `period` | query | string | yes | — | `1h`, `4h`, `8h`, `1d` | Bar size |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...]}}`. No `stat`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | Net exposure of Blave's top traders (top 10% by account assets) |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "period is required"}` | Missing parameter |

**Example**

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/blave_top_trader/get_exposure", headers=headers, params=params, timeout=60)
# {"data": {"alpha": [34.32, 40.52, ...], "timestamp": [1747130400.0, ...]}}
```

---

## `GET /liquidation/get_symbols`

| | |
|---|---|
| Name | 爆倉幣種清單 Liquidation Symbols |
| Group | Crypto › Alpha › Liquidation |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | — |
| Update | 待確認 |
| Source | Blave (Binance USDT-M symbol list) |

**Parameters** — none.

**Response** — `{"data": ["BNBUSDT", "BTCUSDT", ...]}`, sorted.

**Errors** — shared errors only.

**Example**

```python
symbols = requests.get(f"{BASE_URL}/liquidation/get_symbols", headers=headers, timeout=30).json()["data"]
```

---

## `GET /liquidation/get_alpha`

| | |
|---|---|
| Name | 爆倉指標 Liquidation |
| Group | Crypto › Alpha › Liquidation |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2023-01-01 for BTC/ETH; other symbols may start later |
| Update | Every 5 minutes |
| Source | Blave (exchange liquidation feeds) |

**Parameters** — see *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `period` | query | string | yes | — | `5min`, `15min`, `1h`, `4h`, `8h`, `1d` | Bar size |
| `timeframe` | query | string | no | `24h` | `15min`, `1h`, `4h`, `8h`, `24h`, `3d` | Rolling window |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...], "stat": {...}}}`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | (short − long liquidations, in coins) summed over `timeframe` ÷ its 30-day rolling std; mean not subtracted. > 0 = more shorts than longs liquidated, < 0 = more longs |
| `stat` | object | See *`stat` object* |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "symbol is required"}` / `{"error": "period is required"}` | Missing parameter |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h"}
response = requests.get(f"{BASE_URL}/liquidation/get_alpha", headers=headers, params=params, timeout=60)
```

---

## `GET /liquidation/get_map`

| | |
|---|---|
| Name | 爆倉地圖 Liquidation Map |
| Group | Crypto › Alpha › Liquidation |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot |
| Update | Server cache 5 s |
| Source | Blave |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `price_max` | query | float | no | server-chosen range | price | Upper bound of the price axis |
| `price_min` | query | float | no | server-chosen range | price | Lower bound of the price axis |

**Response** — `{"data": {"price", "labels", "oi_value", "cumsum", "liquidation"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `price` | float | USDT | Current price |
| `labels` | float[] | USDT | 200 price buckets |
| `oi_value` | float[] | USD | Estimated allocation of Binance open interest to each bucket (model estimate, not real positions) |
| `cumsum` | float[] | USD | Cumulative liquidation exposure across buckets |
| `liquidation` | object | USD | `{"24h": {"buy_liq": [...], "sell_liq": [...]}}` — actual Binance force-order liquidations over the last 24 h per bucket, each divided by a fixed 0.3 Binance-share assumption: `buy_liq` = short liquidations, `sell_liq` = long liquidations |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "symbol is required"}` | Missing parameter |

**Example**

```python
response = requests.get(f"{BASE_URL}/liquidation/get_map", headers=headers, params={"symbol": "BTCUSDT"}, timeout=60)
# {"data": {"price": 77554.1, "labels": [54287.9, ...], "oi_value": [57693.86, ...],
#           "cumsum": [1543109619.0, ...], "liquidation": {"24h": {"buy_liq": [...], "sell_liq": [...]}}}}
```

---

## `GET /liquidation/get_map_change`

| | |
|---|---|
| Name | 爆倉地圖變化 Liquidation Map Change |
| Group | Crypto › Alpha › Liquidation |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Last 24 hours |
| Update | 待確認 |
| Source | Blave |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol |
| `price_max` | query | float | no | server-chosen range | price | Upper bound of the price axis |
| `price_min` | query | float | no | server-chosen range | price | Lower bound of the price axis |

**Response** — `{"data": {"price", "labels", "hist_0_1h", "hist_1_8h", "hist_8_24h"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `price` | float | USDT | Current price |
| `labels` | float[] | USDT | 200 price buckets (lower edges) |
| `hist_0_1h` | float[] | USD | New estimated liquidation exposure over the last 0–1 h, per bucket: positive difference between model map snapshots, not actual liquidations |
| `hist_1_8h` | float[] | USD | Last 1–8 h |
| `hist_8_24h` | float[] | USD | Last 8–24 h |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "symbol is required"}` | Missing parameter |

**Example**

```python
response = requests.get(f"{BASE_URL}/liquidation/get_map_change", headers=headers, params={"symbol": "BTCUSDT"}, timeout=60)
# {"data": {"price": 77554.1, "labels": [54287.9, ...], "hist_0_1h": [0.0, ...], "hist_1_8h": [...], "hist_8_24h": [...]}}
```

---

# Taiwan Stock

Conventions for this category:
- `stock_id` — TWSE (上市) / TPEx (上櫃) code, e.g. `2330`, `0050`, `00878`, `006208`. Letters and
  digits (dots allowed), ≤ 8 chars, else `400 {"error": "Invalid stock_id"}`.
- `start` / `end` — `YYYY-MM-DD`, inclusive. Unless a block says otherwise they are **not
  format-validated** (filtering is a string comparison), so always send `YYYY-MM-DD`.
- Upstream quota exhausted → `503 {"error": "Upstream rate limit. Please retry shortly."}` — retry later.
- For many stocks use `batch/<data_type>` (≤ 50 ids per call); never loop a single-stock endpoint
  over a universe.

## `GET /studio/market/twstock/list`

| | |
|---|---|
| Name | 台股清單 Taiwan Stock List |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot (currently listed securities) |
| Update | Server cache 24 h (10 min when one market failed to load) |
| Source | TWSE STOCK_DAY_ALL + TPEx mainboard quotes; company profiles from TWSE t187ap03_L / TPEx mopsfin_t187ap03_O |

**Parameters** — none.

**Response** — `{"data": [...]}`, ~2,400 rows (上市 + 上櫃, incl. ETFs; 興櫃 excluded).

| Field | Type | Description |
|---|---|---|
| `stock_id` | string | Code |
| `name` | string | Name |
| `close` | float \| null | Latest daily close (`null` when upstream had none, e.g. halted) |
| `market` | string | `TWSE` (上市) or `TPEx` (上櫃)（待確認：此欄位的 commit 尚未確認已部署） |
| `industry_code` | string \| null | TWSE/TPEx raw numeric 產業別 code, passthrough (not decoded). `null` for ETFs / non-company securities. Common codes: `15` 航運業, `17` 金融保險業, `22` 生技醫療業, `24` 半導體業, `25` 電腦及週邊設備業, `26` 光電業, `27` 通信網路業, `28` 電子零組件業, `29` 電子通路業, `30` 資訊服務業, `31` 其他電子業 |
| `listing_date` | string \| null | `YYYY-MM-DD`; `null` for ETFs / non-company securities |

**Errors** — shared errors only (`500` if both markets fail).

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/list", headers=headers, timeout=60).json()["data"]
# [{"stock_id": "2330", "name": "台積電", "close": 2410.0, "industry_code": "24", "listing_date": "1994-09-05"}, ...]
```

**Notes**
- Use for universe building. When sampling, spread across industries — codes are grouped by
  sector, so `[:N]` truncation concentrates in a few sectors.
- A list noticeably shorter than ~2,400 means one market failed to load — treat as degraded,
  not as delistings.

---

## `GET /studio/market/twstock/info/<stock_id>`

| | |
|---|---|
| Name | 個股基本資料 Taiwan Stock Info |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot |
| Update | Same cache as `/list` (24 h) |
| Source | Same as `/list` |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |

**Response** — `{"stock_id": "<stock_id>", "data": {...}}`; `data` has the same fields as one `/list` row.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid stock_id"}` | Format check failed |
| 404 | `{"error": "Stock not found"}` | Not a currently listed security |

**Example**

```python
info = requests.get(f"{BASE_URL}/studio/market/twstock/info/2330", headers=headers, timeout=30).json()["data"]
# {"stock_id": "2330", "name": "台積電", "close": 2410.0, "industry_code": "24", "listing_date": "1994-09-05"}
```

---

## `GET /studio/market/twstock/price/<stock_id>`

| | |
|---|---|
| Name | 台股日K（原始）Taiwan Stock Daily Price (Raw) |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2000-01-04（待確認：出自 Notion；伺服器向上游要 1994-10-01 起，實際最早一筆取決於上游） |
| Update | Daily. Same-day row after the official TWSE/TPEx close publication (~14:00 Taipei); server cache 5 min |
| Source | FinMind (history); TWSE / TPEx official daily quotes (same-day row) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | Letters/digits (dots allowed), ≤ 8 chars — e.g. `2330`, `0050`, `00878`, `006208` | Listed (上市) or OTC (上櫃) stock / ETF code |
| `start` | query | string | no | full history | `YYYY-MM-DD` | First date, inclusive |
| `end` | query | string | no | latest available | `YYYY-MM-DD` | Last date, inclusive |

**Response** — `{"stock_id": "<stock_id>", "data": [ ... ]}`, rows ascending by `date`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `date` | string | `YYYY-MM-DD` | Trading day |
| `stock_id` | string | — | Stock code |
| `open` / `high` / `low` / `close` | float | TWD | Unadjusted prices |
| `spread` | float | TWD | Change vs the previous close |
| `volume` | int | shares (股) | Trading volume |
| `turnover_value` | int | TWD | Trading value |
| `turnover_count` | int | trades (筆) | Number of trades |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid stock_id"}` | `stock_id` fails the format check |
| 404 | `{"error": "No data found for stock_id: <stock_id>"}` | Unknown code / no data upstream |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted — retry later |

**Example**

```python
params = {"start": "2020-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/price/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "2020-01-02", "stock_id": "2330", "open": 335.0, "high": 338.5,
#   "low": 334.0, "close": 337.0, "spread": 2.0,
#   "volume": 33282120, "turnover_value": 11224165450, "turnover_count": 17160}, ...]   ← 待確認：未實抓
```

**Notes**
- `start` / `end` are not format-validated: a malformed value filters by string comparison
  instead of returning `400`, so always send `YYYY-MM-DD`.
- Use `price_adj` for backtesting total return; this endpoint is unadjusted.
- For many stocks use `batch/price` (≤ 50 ids per call) instead of looping this endpoint.

---

## `GET /studio/market/twstock/price_adj/<stock_id>`

| | |
|---|---|
| Name | 台股日K（還原）Taiwan Stock Daily Price (Forward-Adjusted) |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Same as `/price`（待確認） |
| Update | Daily, rebuilt when the raw series advances; server cache 5 min |
| Source | `/price` series adjusted with FinMind dividend data |

**Parameters** — same as `/price/<stock_id>`.

**Response** — same shape and fields as `/price/<stock_id>`; `open` / `high` / `low` / `close`
are adjusted, `volume` / `turnover_*` are identical to the raw series.

**Errors** — same as `/price/<stock_id>`.

**Example**

```python
params = {"start": "2020-01-01", "end": "2024-12-31"}
data = requests.get(f"{BASE_URL}/studio/market/twstock/price_adj/2330", headers=headers, params=params, timeout=60).json()["data"]
```

**Notes**
- Forward adjustment (後復權 / 向後調整) for cash and stock dividends: early prices stay as
  traded; from each ex-dividend date onward prices are multiplied by the cumulative factor, so
  recent adjusted prices sit above raw. Use for total-return backtests.

---

## `GET /studio/market/twstock/quote/<stock_id>`

| | |
|---|---|
| Name | 即時報價 Taiwan Stock Real-Time Quote |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot only — no history |
| Update | ~10 s (server cache 10 s) |
| Source | FinMind real-time snapshot |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |

**Response** — `{"stock_id": "<stock_id>", "data": {...}}`; `data` is a flat object.

| Field | Type | Description |
|---|---|---|
| `open` / `high` / `low` / `close` | float | Today's OHLC so far |
| `change_price` / `change_rate` | float | Change vs previous close (TWD / %) |
| `average_price` | float | Average traded price |
| `volume` | int | Latest tick's volume |
| `total_volume` | int | Cumulative volume today |
| `amount` / `total_amount` | float | Latest tick / cumulative traded value |
| `yesterday_volume` | int | Previous day's volume |
| `buy_price` / `buy_volume` | float / int | Best bid |
| `sell_price` / `sell_volume` | float / int | Best ask |
| `volume_ratio` | float | Volume ratio |
| `quote_time` | string | `YYYY-MM-DD HH:MM:SS` — a full timestamp, unlike other endpoints' bare `date` |
| `stock_id` | string | Code |
| `tick_type` | int | `0` indeterminate, `1` sell-initiated (賣盤成交), `2` buy-initiated (買盤成交) |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid stock_id"}` | Format check failed |
| 404 | `{"error": "No data found for stock_id: <stock_id>"}` | No quote |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/quote/2330", headers=headers, timeout=30).json()["data"]
# {"open": 2415.0, "high": 2465.0, "low": 2415.0, "close": 2445.0,
#  "change_price": -20.0, "change_rate": -0.81, "average_price": 2432.58,
#  "volume": 4245, "total_volume": 26403, "amount": 10379025000, "total_amount": 64227410000,
#  "yesterday_volume": 27390, "buy_price": 2445.0, "buy_volume": 17,
#  "sell_price": 2450.0, "sell_volume": 11, "volume_ratio": 0.96,
#  "quote_time": "2026-07-03 14:30:00", "stock_id": "2330", "tick_type": 2}
```

**Notes**
- For intraday price checks only — no history, not for backtesting.

---

## `GET /studio/market/twstock/quote`

| | |
|---|---|
| Name | 即時報價（批次）Taiwan Stock Real-Time Quote (Batch) |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot only — no history |
| Update | ~10 s (server cache 10 s) |
| Source | FinMind real-time snapshot |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_ids` | query | string | yes | — | Comma-separated, ≤ 50 ids | Codes |

**Response** — `{"data": {"<stock_id>": {...quote fields...}, ...}}`; fields as `/quote/<stock_id>`.
Ids with no quote are absent.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "stock_ids parameter required"}` | Missing |
| 400 | `{"error": "stock_ids exceeds max 50 per request"}` | Too many |
| 400 | `{"error": "Invalid stock_id in list"}` | A code fails the format check |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/quote", headers=headers,
                    params={"stock_ids": "2330,2317"}, timeout=30).json()["data"]
# {"2330": {...}, "2317": {...}}
```

---

## `GET /studio/market/twstock/quote/all`

| | |
|---|---|
| Name | 即時報價（全市場）Taiwan Stock Real-Time Quote (All) |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot only — no history |
| Update | ~10 s (server cache 10 s) |
| Source | FinMind real-time snapshot |

**Parameters** — none.

**Response** — `{"data": [{...quote fields...}, ...]}` (~2,800 rows); fields as `/quote/<stock_id>`.

**Errors**

| Status | Body | When |
|---|---|---|
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
rows = requests.get(f"{BASE_URL}/studio/market/twstock/quote/all", headers=headers, timeout=30).json()["data"]
```

---

## `GET /studio/market/twstock/minute/ohlcv/<stock_id>/<schema>`

| | |
|---|---|
| Name | 現股分線 Taiwan Stock Minute-Line OHLCV |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2019-01 (backfilled per stock) |
| Update | Intraday live bars; official correction after the close |
| Source | Shioaji (live) + FinMind (official history) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | A currently listed TWSE/TPEx code, or `TAIEX` (加權指數) | Code |
| `schema` | path | string | yes | — | `1m`, `5m`, `15m`, `30m`, `60m`, `1d` | Bar size |
| `start` | query | string | no | `end` − the schema's max range | `YYYY-MM-DD` | First day |
| `end` | query | string | no | today (UTC) | `YYYY-MM-DD` | Last day, inclusive |
| `adjust` | query | string | no | `0` | `0`, `1`, `true`, `false` | `1` = forward-adjusted (後復權) OHLC, same factors as `/price_adj`; `volume` is never adjusted |

Max range per request (`end` − `start`): `1m` 31 d · `5m` 62 d · `15m` 93 d · `30m` 186 d ·
`60m` 365 d · `1d` 3650 d.

**Response** — `{"stock_id", "schema", "data": [...]}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `ts` | string | UTC ISO | Bar open time (minute-start label); the 13:30 Taipei bar is the closing auction |
| `open` / `high` / `low` / `close` | float | TWD | Prices |
| `volume` | int | lots (張), not shares | Volume（待確認：`TAIEX` 的 volume 單位） |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid stock_id (must be a listed TWSE/TPEx security)"}` | Not listed |
| 400 | `{"error": "Invalid schema. Allowed: [...]"}` | Bad schema |
| 400 | `{"error": "Invalid adjust (use 0 or 1)"}` | Bad `adjust` |
| 400 | `{"error": "Invalid date format. Use YYYY-MM-DD"}` | Malformed date |
| 400 | `{"error": "date_range_too_large", "message": "...", "max_days": <n>}` | Range over the cap |
| 503 | `{"error": "market data temporarily unavailable"}` | Store read failure |
| 503 | `{"error": "adjust factors temporarily unavailable"}` | `adjust=1` and factors unavailable — never silently served unadjusted |

**Example**

```python
body = requests.get(f"{BASE_URL}/studio/market/twstock/minute/ohlcv/2330/1m", headers=headers,
                    params={"start": "2026-08-06", "end": "2026-08-06"}, timeout=60).json()
# {"stock_id": "2330", "schema": "1m", "data": [
#   {"close": 2385.0, "high": 2395.0, "low": 2385.0, "open": 2395.0, "ts": "2026-08-06 01:00:00+00:00", "volume": 2540}, ...]}
```

**Notes**
- Coverage is demand-driven: any listed stock can be queried; the first query seeds ~30 recent
  days and enrolls the stock for live tracking, and deep history (2019-01 →) backfills
  afterwards. Check `minute/ohlcv/symbols` before requesting years of history.
- A range with no data returns `200` with `[]`.
- A still-forming bar is not returned; use `/quote/<stock_id>` for the live price.
- Split long spans into chunks within the per-schema cap.

---

## `GET /studio/market/twstock/minute/ohlcv/symbols`

| | |
|---|---|
| Name | 現股分線覆蓋清單 Minute-Line Covered Symbols |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot |
| Update | Live |
| Source | Blave minute store |

**Parameters** — none.

**Response** — `{"data": ["2330", "TAIEX", ...]}` — ids that already have minute-line data on
disk (currently listed stocks plus `TAIEX`), sorted.

**Errors** — shared errors only.

**Example**

```python
covered = requests.get(f"{BASE_URL}/studio/market/twstock/minute/ohlcv/symbols", headers=headers, timeout=30).json()["data"]
```

---

## `GET /studio/market/twstock/kbar/<stock_id>`

| | |
|---|---|
| Name | 分K（舊版）Taiwan Stock 1-Minute Bars (Legacy) |
| Group | Taiwan Stock › Market Data |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2019-01-01, for ids covered by `minute/ohlcv/symbols` |
| Update | Server cache 60 s when the range includes today, else 5 min |
| Source | Same store as `minute/ohlcv` (no upstream call) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | A currently listed TWSE/TPEx code, or `TAIEX` | Code |
| `start` | query | string | no | today − 6 days | `YYYY-MM-DD` | First day |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last day; `end` − `start` ≤ 31 days |

**Response** — `{"stock_id", "data": [...]}`, ascending.

| Field | Type | Description |
|---|---|---|
| `date` | string | `YYYY-MM-DD` (Taipei) |
| `minute` | string | `HH:MM:SS` Taipei, bar start (09:00–13:30) |
| `stock_id` | string | Code |
| `open` / `high` / `low` / `close` | float | TWD |
| `volume` | int | Lots (張) |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid stock_id (must be a listed TWSE/TPEx security)"}` | Not listed |
| 400 | `{"error": "Date range exceeds 31 days"}` | Range too long, or malformed date |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/kbar/2330", headers=headers,
                    params={"start": "2026-08-03", "end": "2026-08-07"}, timeout=60).json()["data"]
```

**Notes**
- Legacy — prefer `minute/ohlcv/<stock_id>/1m`. A listed stock with no minute data returns `[]`
  (this endpoint does not trigger seeding).
- Today's bars are provisional intraday and replaced by official bars after ~16:10 Taipei.

---

## `GET /studio/market/twstock/market_value/<stock_id>`

| | |
|---|---|
| Name | 市值 Taiwan Stock Market Value |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2004-01-01 |
| Update | Daily; server cache 5 min |
| Source | FinMind TaiwanStockMarketValue |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | full history | `YYYY-MM-DD` | First date |
| `end` | query | string | no | latest | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [{"date", "stock_id", "market_value"}]}`; `market_value` in TWD.

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/market_value/2330", headers=headers,
                    params={"start": "2026-01-01"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twstock/market_value/all`

| | |
|---|---|
| Name | 市值排名 Taiwan Stock Market Value Ranking |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot (latest published day) |
| Update | Daily (EOD); server cache 30 min |
| Source | FinMind TaiwanStockMarketValue, filtered to `/list` |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `top` | query | int | no | all (~2,400) | 1–3000 | Keep only the top N by market value |

**Response** — `{"date": "YYYY-MM-DD", "data": [...]}`, sorted by market value descending.

| Field | Type | Description |
|---|---|---|
| `date` | string | As-of day actually used (latest published; can lag today by a day) |
| `data[].rank` | int | 1-based rank |
| `data[].stock_id` | string | Code |
| `data[].name` | string | Name |
| `data[].market_value` | int | TWD |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "top must be an integer between 1 and 3000"}` | Bad `top` |
| 404 | `{"error": "No recent market value data available"}` (or a listing-incomplete message) | No recent data |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
body = requests.get(f"{BASE_URL}/studio/market/twstock/market_value/all", headers=headers, params={"top": 10}, timeout=60).json()
# {"date": "2026-08-20",
#  "data": [{"rank": 1, "stock_id": "2330", "name": "台積電", "market_value": 61589378909125}, ...]}

# Top-50 non-ETF pool: ETFs rank too, so over-fetch then drop ids starting with "00"
rows = requests.get(f"{BASE_URL}/studio/market/twstock/market_value/all", headers=headers, params={"top": 100}, timeout=60).json()["data"]
top50 = [r["stock_id"] for r in rows if not r["stock_id"].startswith("00")][:50]
```

**Notes**
- Universe is 上市 + 上櫃 + ETF (興櫃 excluded; ETNs have no data). Use this instead of looping
  `/market_value/<stock_id>` for "top N by market cap" questions.

---

## `GET /studio/market/twstock/per/<stock_id>`

| | |
|---|---|
| Name | 本益比／淨值比／殖利率 Taiwan Stock PER / PBR / Dividend Yield |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2005-10-01 |
| Update | Daily; same-day row from TWSE / TPEx the same afternoon; server cache 5 min |
| Source | FinMind TaiwanStockPER; TWSE BWIBBU_d / TPEx pera_result (same day) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | full history | `YYYY-MM-DD` | First date |
| `end` | query | string | no | latest | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [...]}`.

| Field | Type | Description |
|---|---|---|
| `date` | string | Trading day |
| `stock_id` | string | Code |
| `dividend_yield` | float | Dividend yield (%) |
| `PER` | float | Price / earnings |
| `PBR` | float | Price / book |

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/per/2330", headers=headers,
                    params={"start": "2026-01-01", "end": "2026-07-22"}, timeout=60).json()["data"]
# [{"date": "2026-07-21", "stock_id": "2330", "dividend_yield": 0.95, "PER": 34.87, "PBR": 11.05}, ...]
```

**Notes**
- For value screens across many stocks use `batch/per`.

---

## `GET /studio/market/twstock/financials/<stock_id>`

| | |
|---|---|
| Name | 綜合損益表 Taiwan Stock Income Statement |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2013-01-01 (default lower bound)（待確認：更早資料是否可用） |
| Update | Quarterly; server cache 24 h |
| Source | FinMind TaiwanStockFinancialStatements |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | `2013-01-01` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [...]}`, long format (one row per item per quarter).

| Field | Type | Description |
|---|---|---|
| `date` | string | Quarter end (`03-31` / `06-30` / `09-30` / `12-31`) |
| `stock_id` | string | Code |
| `type` | string | Item code, e.g. `Revenue`, `GrossProfit`, `OperatingIncome`, `NetIncome`, `EPS`, `TAX`, `OtherComprehensiveIncome` |
| `value` | float | Value (TWD; `EPS` in TWD per share) |
| `origin_name` | string | Chinese label — use it to identify unfamiliar `type` codes |

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
import pandas as pd
data = requests.get(f"{BASE_URL}/studio/market/twstock/financials/2330", headers=headers,
                    params={"start": "2022-01-01", "end": "2024-12-31"}, timeout=30).json()["data"]
# [{"date": "2022-03-31", "stock_id": "2330", "type": "Revenue", "value": 491075000000.0, "origin_name": "營業收入"}, ...]
wide = pd.DataFrame(data).pivot_table(index="date", columns="type", values="value", aggfunc="first")
```

---

## `GET /studio/market/twstock/balance_sheet/<stock_id>`

| | |
|---|---|
| Name | 資產負債表 Taiwan Stock Balance Sheet |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2013-01-01 (default lower bound)（待確認：更早資料是否可用） |
| Update | Quarterly; server cache 24 h |
| Source | FinMind TaiwanStockBalanceSheet |

**Parameters** — same as `/financials/<stock_id>`.

**Response** — same long format as `/financials/<stock_id>`. Key `type` codes:
`CashAndCashEquivalents`, `TotalAssets`, `TotalLiabilities`, `TotalEquity`. Codes ending in
`_per` are % of total assets.

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/balance_sheet/2330", headers=headers,
                    params={"start": "2022-01-01"}, timeout=30).json()["data"]
```

---

## `GET /studio/market/twstock/cashflow/<stock_id>`

| | |
|---|---|
| Name | 現金流量表 Taiwan Stock Cash Flow Statement |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2013-01-01 (default lower bound)（待確認：更早資料是否可用） |
| Update | Quarterly; server cache 24 h |
| Source | FinMind TaiwanStockCashFlowsStatement |

**Parameters** — same as `/financials/<stock_id>`.

**Response** — same long format as `/financials/<stock_id>`. Key `type` codes:
`OperatingActivities`, `InvestingActivities`, `FinancingActivities`, `CashBalancesEndOfPeriod`,
`PropertyAndPlantAndEquipment`.

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/cashflow/2330", headers=headers,
                    params={"start": "2022-01-01"}, timeout=30).json()["data"]
```

---

## `GET /studio/market/twstock/monthly_revenue/<stock_id>`

| | |
|---|---|
| Name | 月營收 Taiwan Stock Monthly Revenue |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2000-01-01 |
| Update | Monthly; server cache 24 h |
| Source | FinMind TaiwanStockMonthRevenue (passed through unchanged) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | `2000-01-01` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [...]}`, one row per month.

| Field | Type | Description |
|---|---|---|
| `date` | string | 待確認：月初（`YYYY-MM-01`）還是申報日，來源說法互相矛盾 |
| `stock_id` | string | Code |
| `country` | string | Market, e.g. `台灣` |
| `revenue` | int | Monthly revenue — 待確認：單位是元還是千元，來源說法互相矛盾 |
| `revenue_month` | int | Revenue month (1–12) — use this, not `date`, for the period |
| `revenue_year` | int | Revenue year |

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
import pandas as pd
data = requests.get(f"{BASE_URL}/studio/market/twstock/monthly_revenue/2330", headers=headers,
                    params={"start": "2024-01-01", "end": "2024-12-31"}, timeout=30).json()["data"]
df = pd.DataFrame(data).sort_values(["revenue_year", "revenue_month"])
df["yoy_pct"] = df["revenue"].pct_change(periods=12) * 100
# example rows: 待確認（未實抓）
```

---

## `GET /studio/market/twstock/dividend/<stock_id>`

| | |
|---|---|
| Name | 股利事件 Taiwan Stock Dividend Events |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 1994（待確認：出自 Notion） |
| Update | Refreshed on request when stale |
| Source | FinMind dividend data |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | Currently listed code (4–6 digits, optional trailing letter) | Code |
| `start` | query | string | no | full history | strict `YYYY-MM-DD` | First effective date |
| `end` | query | string | no | full history | strict `YYYY-MM-DD` | Last effective date |

Range filtering uses a three-tier effective date: `cash_ex_date` if set, else `stock_ex_date`,
else `record_date` — freshly announced events without an ex date still show up.

**Response** — `{"stock_id", "data": [...]}`, one row per announcement row.

| Field | Type | Description |
|---|---|---|
| `record_date` | string | 權利分派基準日 `YYYY-MM-DD` |
| `period` | string | 股利所屬期間 — an **opaque label** (`114年第3季`, `113`, `不適用`, …); compare as string, do not parse into a year |
| `announce_date` | string | 公告日; `""` when unknown |
| `cash_ex_date` | string | 除息交易日; `""` when none / not decided |
| `stock_ex_date` | string | 除權交易日; `""` when none |
| `pay_date` | string | 現金股利發放日; `""` when unknown |
| `cash` | float | Cash dividend per share (TWD, 盈餘 + 公積) |
| `stock` | float | Stock dividend per share (元面額, 盈餘 + 公積) |
| `stock_ratio` | float | `stock / 10` — split-style adjustment ratio |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid stock_id"}` | Format check failed |
| 400 | `{"error": "Invalid start date, expected YYYY-MM-DD"}` (or `end`) | Malformed date |
| 404 | `{"error": "No data found for stock_id: <id>"}` / `{"error": "No dividend records for stock_id: <id>"}` | Not listed, or no dividend history at all |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/dividend/2330", headers=headers,
                    params={"start": "2025-01-01", "end": "2025-12-31"}, timeout=30).json()["data"]
# [{"record_date": "2025-03-24", "period": "113年第3季", "announce_date": "2025-03-03",
#   "cash_ex_date": "2025-03-18", "stock_ex_date": "", "pay_date": "2025-04-10",
#   "cash": 4.50002042, "stock": 0.0, "stock_ratio": 0.0}, ...]
```

**Notes**
- Zero-value rows (`cash == 0` and `stock == 0`) are kept — an announced no-distribution decision.
- A valid stock with history but no events in range returns `200` + `[]` (distinct from `404`).
- Delisted stocks are `404`.

---

## `GET /studio/market/twstock/news/<stock_id>`

| | |
|---|---|
| Name | 個股新聞 Taiwan Stock News |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Fetched per day on first request; server cache 5 min |
| Source | FinMind TaiwanStockNews |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | today − 6 days | `YYYY-MM-DD` | First day |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last day; `end` − `start` ≤ 31 days |

**Response** — `{"stock_id", "data": [...]}`, several articles per day (weekdays only are fetched).

| Field | Type | Description |
|---|---|---|
| `date` | string | Publish datetime |
| `stock_id` | string | Code |
| `title` | string | Headline |
| `source` | string | Publisher |
| `link` | string | URL |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Date range exceeds 31 days"}` or a date-parse message | Range too long / malformed date |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/news/2330", headers=headers,
                    params={"start": "2026-08-01", "end": "2026-08-07"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twstock/institutional/<stock_id>`

| | |
|---|---|
| Name | 三大法人買賣超 Taiwan Stock Institutional Investors |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Daily; same-day row from TWSE / TPEx when available; server cache 5 min |
| Source | FinMind TaiwanStockInstitutionalInvestorsBuySell; TWSE / TPEx official (same day) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | full history | `YYYY-MM-DD` | First date |
| `end` | query | string | no | latest | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [...]}`, wide format, one row per day. All values in shares (股).

| Field | Description |
|---|---|
| `date`, `stock_id` | Day, code |
| `foreign_buy` / `foreign_sell` | 外資 (excl. foreign dealers) |
| `trust_buy` / `trust_sell` | 投信 |
| `dealer_self_buy` / `dealer_self_sell` | 自營商自行買賣 |
| `dealer_hedge_buy` / `dealer_hedge_sell` | 自營商避險 |
| `foreign_dealer_self_buy` / `foreign_dealer_self_sell` | 外資自營商 (mostly 0) |

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/institutional/2330", headers=headers,
                    params={"start": "2024-01-01", "end": "2024-12-31"}, timeout=60).json()["data"]
# [{"date": "2024-01-02", "stock_id": "2330", "foreign_buy": 28464159, "foreign_sell": 47404324,
#   "trust_buy": 5553520, "trust_sell": 269712, "dealer_self_buy": 452000, "dealer_self_sell": 366190,
#   "dealer_hedge_buy": 942546, "dealer_hedge_sell": 780090,
#   "foreign_dealer_self_buy": 0, "foreign_dealer_self_sell": 0}, ...]
```

**Notes**
- Net buy = `*_buy − *_sell`.

---

## `GET /studio/market/twstock/margin/<stock_id>`

| | |
|---|---|
| Name | 融資融券 Taiwan Stock Margin Trading |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 1994-10-01（待確認：出自 Notion，程式向上游要此日起） |
| Update | Daily; server cache 5 min |
| Source | FinMind TaiwanStockMarginPurchaseShortSale |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | full history | `YYYY-MM-DD` | First date |
| `end` | query | string | no | latest | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [...]}`, one row per day. Values in shares（待確認：股或張）.

| Field | Description |
|---|---|
| `margin_buy` / `margin_sell` | 融資買進 / 賣出 |
| `margin_cash_repay` | 融資現金償還 |
| `margin_balance` / `margin_prev_balance` | 融資今日 / 前日餘額 |
| `margin_limit` | 融資限額 |
| `short_buy` / `short_sell` | 融券買進 / 賣出 |
| `short_cash_repay` | 融券現金償還 |
| `short_balance` / `short_prev_balance` | 融券今日 / 前日餘額 |
| `short_limit` | 融券限額 |
| `offset_loan_short` | 資券相抵 |

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
import pandas as pd
data = requests.get(f"{BASE_URL}/studio/market/twstock/margin/2330", headers=headers,
                    params={"start": "2024-01-01"}, timeout=60).json()["data"]
df = pd.DataFrame(data)
df["margin_util"] = df["margin_balance"] / df["margin_limit"]   # 融資使用率
```

---

## `GET /studio/market/twstock/shareholding/<stock_id>`

| | |
|---|---|
| Name | 股權持股分級表 Taiwan Stock Shareholding Distribution |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 待確認 |
| Update | Weekly (TDCC, Fridays); server cache 5 min |
| Source | FinMind TaiwanStockHoldingSharesPer |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | full history | `YYYY-MM-DD` | First date |
| `end` | query | string | no | latest | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [...]}`, one row per date × level.

| Field | Type | Description |
|---|---|---|
| `date` | string | Week date |
| `stock_id` | string | Code |
| `level` | string | Holding bracket: `1-999`, `1,000-5,000`, `5,001-10,000`, `10,001-15,000`, `15,001-20,000`, `20,001-30,000`, `30,001-40,000`, `40,001-50,000`, `50,001-100,000`, `100,001-200,000`, `200,001-400,000`, `400,001-600,000`, `600,001-800,000`, `800,001-1,000,000`, `more than 1,000,001`, `total`, `差異數調整（說明4）` |
| `people` | int | Number of holders |
| `unit` | int | Shares held |
| `percent` | float | % of issued shares |

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/shareholding/2330", headers=headers,
                    params={"start": "2024-01-01", "end": "2024-03-31"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twstock/foreign_shareholding/<stock_id>`

| | |
|---|---|
| Name | 外資持股 Taiwan Stock Foreign Shareholding |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2013-01-01 (default lower bound)（待確認：更早資料是否可用） |
| Update | Daily; server cache 24 h |
| Source | FinMind TaiwanStockShareholding |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | `2013-01-01` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [...]}`, one row per day.

| Field | Description |
|---|---|
| `date`, `stock_id` | Day, code |
| `ForeignInvestmentShares` | Shares held by foreign investors |
| `ForeignInvestmentSharesRatio` | Foreign holding ratio (%) |
| `ForeignInvestmentRemainingShares` | Remaining shares foreigners may buy |
| `ForeignInvestmentRemainRatio` | Remaining ratio (%) |
| `ForeignInvestmentUpperLimitRatio` | Foreign holding cap (%) |
| `ChineseInvestmentUpperLimitRatio` | PRC-investor holding cap (%) |
| `NumberOfSharesIssued` | Shares issued |

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/foreign_shareholding/2330", headers=headers,
                    params={"start": "2026-01-01"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twstock/gov_bank/<stock_id>`

| | |
|---|---|
| Name | 八大行庫買賣超 Taiwan Stock Government Bank Buy/Sell |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2021-06-30 |
| Update | Daily; server cache 5 min |
| Source | FinMind TaiwanStockGovernmentBankBuySell |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | today − 6 days | `YYYY-MM-DD` | First day |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last day; `end` − `start` ≤ 31 days |

**Response** — `{"stock_id", "data": [...]}`, up to 8 rows per day (one per bank), sorted by date, bank.

| Field | Description |
|---|---|
| `date`, `stock_id` | Day, code |
| `bank_name` | Bank |
| `buy` / `sell` | Shares bought / sold |
| `buy_amount` / `sell_amount` | TWD bought / sold |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Date range exceeds 31 days"}` or a date-parse message | Range too long / malformed date |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/gov_bank/2330", headers=headers,
                    params={"start": "2026-08-01", "end": "2026-08-07"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twstock/lending/<stock_id>`

| | |
|---|---|
| Name | 借券成交明細 Taiwan Stock Securities Lending |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2001-05-01 |
| Update | Daily; server cache 5 min |
| Source | FinMind TaiwanStockSecuritiesLending |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | full history | `YYYY-MM-DD` | First date |
| `end` | query | string | no | latest | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [...]}`, several rows per day.

| Field | Description |
|---|---|
| `date`, `stock_id` | Day, code |
| `transaction_type` | `競價` / `議借` |
| `volume` | Volume |
| `fee_rate` | Lending fee rate |
| `close` | Close price |
| `original_return_date` | Original return date |
| `original_lending_period` | Original lending period |

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/lending/2330", headers=headers,
                    params={"start": "2026-08-01"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twstock/broker/search`

| | |
|---|---|
| Name | 券商分點查詢 Broker Branch Search |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot (~1,000 branches) |
| Update | Loaded once per server process |
| Source | FinMind TaiwanSecuritiesTraderInfo |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `name` | query | string | yes | — | Any substring, case-insensitive | Branch name to search |

**Response** — `{"query": "<name>", "data": [{"broker_id", "broker_name"}]}`.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "name parameter required"}` | Missing |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
rows = requests.get(f"{BASE_URL}/studio/market/twstock/broker/search", headers=headers,
                    params={"name": "松山"}, timeout=30).json()["data"]
# [{"broker_id": "9217", "broker_name": "凱基-松山"}, ...]
```

---

## `GET /studio/market/twstock/broker/stock/<stock_id>`

| | |
|---|---|
| Name | 分點買賣超（依個股）Broker Buy/Sell by Stock |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2021-06-30 |
| Update | Daily, after ~21:30 Taipei; server cache 5 min |
| Source | FinMind TaiwanStockTradingDailyReport (whole-market daily file) |

**Parameters** — send `date` for one day, or `start` (+ `end`) for a range; `start` wins if both are sent.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `date` | query | string | no | today | `YYYY-MM-DD` | Single day |
| `start` | query | string | no | — | `YYYY-MM-DD` | Range start |
| `end` | query | string | no | `start` | `YYYY-MM-DD` | Range end; range ≤ 366 days inclusive |

**Response** — `{"stock_id", "data": [...]}`, one row per branch per day.

| Field | Type | Description |
|---|---|---|
| `date` | string | Trading day |
| `stock_id` | string | Code |
| `broker_id` | string | Branch code (may be alphanumeric, e.g. `920A`) |
| `broker_name` | string | Branch name |
| `price` | float | Volume-weighted average traded price |
| `buy` / `sell` | int | Shares bought / sold |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid stock_id"}` | Format check failed |
| 400 | `{"error": "Invalid date (YYYY-MM-DD)"}` | Malformed date |
| 400 | `{"error": "start/end range is <n> days; max 366 (inclusive) — split into smaller ranges"}` | Range too long |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Data temporarily unavailable — retry; do not read as "no trades" |

**Example**

```python
rows = requests.get(f"{BASE_URL}/studio/market/twstock/broker/stock/2330", headers=headers,
                    params={"start": "2026-08-03", "end": "2026-08-07"}, timeout=60).json()["data"]
```

**Notes**
- A day with no data (holiday, before 2021-06-28, or today before ~21:30) is `200` + `[]`.
- Range queries（待確認：start/end 區間讀取的 commit 尚未確認已部署）.

---

## `GET /studio/market/twstock/broker/trader/<trader_id>`

| | |
|---|---|
| Name | 分點買賣超（依分點）Broker Buy/Sell by Branch |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2021-06-30 |
| Update | Daily, after ~21:30 Taipei; server cache 5 min |
| Source | FinMind TaiwanStockTradingDailyReport (whole-market daily file) |

**Parameters** — same `date` / `start` / `end` rules as `/broker/stock/<stock_id>`.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `trader_id` | path | string | yes | — | Letters, digits, `-` (e.g. `9217`, `920A`) | Branch code from `/broker/search` |
| `date` | query | string | no | today | `YYYY-MM-DD` | Single day |
| `start` | query | string | no | — | `YYYY-MM-DD` | Range start |
| `end` | query | string | no | `start` | `YYYY-MM-DD` | Range end; range ≤ 366 days inclusive |

**Response** — `{"trader_id", "data": [...]}`, one row per stock per day; fields `date`,
`broker_id`, `broker_name`, `stock_id`, `price`, `buy`, `sell` (as `/broker/stock`).

**Errors** — as `/broker/stock/<stock_id>`, with `400 {"error": "Invalid trader_id"}` for a bad code.

**Example**

```python
rows = requests.get(f"{BASE_URL}/studio/market/twstock/broker/trader/9217", headers=headers,
                    params={"date": "2026-08-07"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twstock/batch/<data_type>`

| | |
|---|---|
| Name | 台股批次查詢 Taiwan Stock Batch Fetch |
| Group | Taiwan Stock › Other |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Per `data_type` (same as the single-stock endpoint) |
| Update | Per `data_type` |
| Source | Per `data_type` |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `data_type` | path | string | yes | — | `price`, `price_adj`, `per`, `institutional`, `shareholding`, `foreign_shareholding`, `financials`, `balance_sheet`, `monthly_revenue`, `dividend` | Dataset |
| `stock_ids` | query | string | yes | — | Comma-separated, ≤ 50 | Codes |
| `start` | query | string | no | per `data_type` | `YYYY-MM-DD` (strictly validated for `dividend` only) | First date |
| `end` | query | string | no | per `data_type` | `YYYY-MM-DD` | Last date |

**Response** — `{"data_type", "data": {"<stock_id>": [...rows...]}, "failed": [...]}`. Rows are
identical to the matching single-stock endpoint.

- `failed` — ids whose server-side fetch failed (rate limit or upstream error); retry those.
- An id absent from both `data` and `failed` genuinely has no data.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Unsupported data_type '<x>'. Supported: [...]"}` | Bad `data_type` |
| 400 | `{"error": "stock_ids parameter required"}` | Missing |
| 400 | `{"error": "stock_ids exceeds max 50 per request"}` | Too many |
| 400 | `{"error": "Invalid stock_id in list"}` | A code fails the format check |
| 400 | `{"error": "Invalid start date, expected YYYY-MM-DD"}` | `dividend` only |

**Example**

```python
payload = requests.get(f"{BASE_URL}/studio/market/twstock/batch/per", headers=headers,
                       params={"stock_ids": "2330,6182", "start": "2026-08-04", "end": "2026-08-08"},
                       timeout=120).json()
# {"data_type": "per",
#  "data": {"2330": [{"date": "2026-08-04", "dividend_yield": 0.95, "PER": 31.19, "PBR": 10.21, "stock_id": "2330"}, ...],
#           "6182": [...]},
#  "failed": []}
```

**Notes**
- The whole market (~2,000 stocks) is ~40 calls; never fan out single-stock endpoints.
- `dividend` differs from `/dividend/<stock_id>`: it reads stored data only (no refresh), an
  unknown id or a stock with no dividend history is silently absent (no `404`), and an upstream
  quota problem shows up in `failed`, not as a `503`.

---

# Taiwan Market (大盤)

Whole-market daily series (no `stock_id`). `start` / `end` are optional `YYYY-MM-DD`; omit for
full history. Do not sum per-stock endpoints as a substitute — coverage and units differ.

## `GET /studio/market/twmarket/index/<index_id>`

| | |
|---|---|
| Name | 加權指數日K TAIEX Daily OHLC |
| Group | Taiwan Market |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 1999-01-05 |
| Update | Daily; server cache 5 min |
| Source | TWSE MI_5MINS_HIST |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `index_id` | path | string | yes | — | `TAIEX` (case-insensitive) | Only TAIEX is supported |
| `start` | query | string | no | `1999-01-05` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"index_id": "TAIEX", "data": [{"date", "open", "high", "low", "close"}]}`;
prices in index points. No volume — use `/twmarket/turnover`.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Unsupported index"}` | Not `TAIEX` |
| 404 | error message | No data |
| 503 | `{"error": "Market data is not ready on this server. Please retry later."}` / upstream rate limit | Store not ready / upstream down |

**Example**

```python
body = requests.get(f"{BASE_URL}/studio/market/twmarket/index/TAIEX", headers=headers,
                    params={"start": "2024-01-01", "end": "2024-12-31"}, timeout=60).json()
# {"index_id": "TAIEX", "data": [{"date": "2024-01-02", "open": 17939.79, "high": 17956.74, "low": 17784.97, "close": 17853.76}, ...]}
```

---

## `GET /studio/market/twmarket/turnover`

| | |
|---|---|
| Name | 全市場成交量值 Market Turnover |
| Group | Taiwan Market |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 1990-01-04 |
| Update | Daily; server cache 5 min |
| Source | TWSE FMTQIK |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `start` | query | string | no | `1990-01-04` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"data": [...]}`.

| Field | Unit | Description |
|---|---|---|
| `date` | — | Trading day |
| `volume` | shares | 成交股數 |
| `value` | TWD | 成交金額 |
| `trades` | count | 成交筆數 |

**Errors** — `404` no data; `503` store not ready or upstream rate limit.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twmarket/turnover", headers=headers,
                    params={"start": "2024-01-01"}, timeout=60).json()["data"]
# [{"date": "2024-01-02", "volume": 6411778806.0, "value": 301290668897.0, "trades": 2267660.0}, ...]
```

---

## `GET /studio/market/twmarket/institutional`

| | |
|---|---|
| Name | 全市場三大法人買賣超 Market Institutional Net Buy/Sell |
| Group | Taiwan Market |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2004-04-07 |
| Update | Daily; server cache 5 min |
| Source | FinMind; TWSE BFI82U before FinMind publishes the day |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `start` | query | string | no | `2004-04-07` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"data": [{"date", "foreign", "investment_trust", "dealer", "total"}]}`; all
values are **net** (buy − sell) in TWD.

**Errors** — `404` no data; `503` upstream rate limit.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twmarket/institutional", headers=headers,
                    params={"start": "2024-01-01"}, timeout=60).json()["data"]
# [{"date": "2024-01-02", "foreign": 1047078183.0, "investment_trust": 189637635.0,
#   "dealer": -4447440583.0, "total": -3211404085.0}, ...]
```

**Notes**
- Foreign dealers' own-account trading (外資自營商) is bucketed into `dealer`, not `foreign`.

---

## `GET /studio/market/twmarket/margin`

| | |
|---|---|
| Name | 全市場融資融券餘額 Market Margin Balance |
| Group | Taiwan Market |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2001-01-03 |
| Update | Daily; server cache 5 min |
| Source | FinMind |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `start` | query | string | no | `2001-01-03` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"data": [...]}`.

| Field | Unit | Description |
|---|---|---|
| `date` | — | Trading day |
| `margin_balance` / `margin_balance_prev` | lots (張) | 融資餘額 today / previous day |
| `margin_balance_value` | TWD | 融資餘額金額 |
| `short_balance` / `short_balance_prev` | lots (張) | 融券餘額 today / previous day |

**Errors** — `404` no data; `503` upstream rate limit.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twmarket/margin", headers=headers,
                    params={"start": "2024-01-01"}, timeout=60).json()["data"]
# [{"date": "2024-01-02", "margin_balance": 8012561, "margin_balance_prev": 7999081,
#   "margin_balance_value": 248424271000, "short_balance": 369678, "short_balance_prev": 359738}, ...]
```

---

## `GET /studio/market/twmarket/dividend_points`

| | |
|---|---|
| Name | 加權指數每日除息點數 TAIEX Daily Dividend Points |
| Group | Taiwan Market |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2003-01-02 (realized); forecasts up to today + 120 days |
| Update | Realized leg each trading day ~17:00 Taipei; server cache 5 min (forecast inputs 1 h) |
| Source | FinMind total-return vs price index (realized); announced dividends + last-year template (forecast) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `start` | query | string | no | `2003-01-02` | strict `YYYY-MM-DD` | First date |
| `end` | query | string | no | today + 120 days | strict `YYYY-MM-DD` | Last date; silently clamped to today + 120 days |

**Response** — `{"data": [{"date", "points", "estimated"}], "meta": {"estimated_coverage", "degraded"}}`.

| Field | Type | Description |
|---|---|---|
| `data[].date` | string | Day |
| `data[].points` | float | Index points removed by ex-dividend events that day |
| `data[].estimated` | bool | `false` = realized (from the TR/price index spread; non-ex days ≈ 0); `true` = forecast (future weekdays, zero-filled where no event) |
| `meta.estimated_coverage` | float \| null | Fraction of TAIEX weight whose inputs were readable for the forecast; `null` when no estimated rows |
| `meta.degraded` | bool | `true` = forecast materially under-covered — treat as a lower bound |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid start date, expected YYYY-MM-DD"}` (or `end`) | Malformed date |
| 404 | `{"error": "No TAIEX index data available from FinMind"}` | Cold store and no upstream data |
| 503 | error message | Forecast coverage below 90%, store not ready, or upstream rate limit |

**Example**

```python
import pandas as pd
payload = requests.get(f"{BASE_URL}/studio/market/twmarket/dividend_points", headers=headers,
                       params={"start": "2026-08-01"}, timeout=60).json()
# {"data": [{"date": "2026-08-03", "points": 2.853, "estimated": false}, ...,
#           {"date": "2026-08-28", "points": 3.846, "estimated": true}, ...],
#  "meta": {"estimated_coverage": 0.9999, "degraded": false}}
df = pd.DataFrame(payload["data"])
future_div = df[df["estimated"]].set_index("date")["points"]
# fair basis at t for settlement T: futures_price - (spot_index - future_div.loc[t_plus_1:T].sum())
```

**Notes**
- Before ~17:00 Taipei the latest realized row is the previous trading day.
- Forecasts more than ~2 weeks out lean on the last-year template.
- Forecast rows are always returned from tomorrow through `end`, even when `start` is later
  than tomorrow — filter client-side.

---

# Taiwan Futures & Options

## `GET /studio/market/twfutures/ohlcv/<symbol>/<schema>`

| | |
|---|---|
| Name | 台灣期貨分線 Taiwan Futures OHLCV |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | TXF: 2013-12-30 (`1d`), 2014-01-02 (intraday). Other symbols: 待確認 |
| Update | Near-real-time from the on-disk 1m store, refreshed on request |
| Source | Sinopac Shioaji (near-month continuous series) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | path | string | yes | — | `TXF` (台指期), `MXF` (小台), or a stock-futures id listed by `ohlcv/symbols` (case-insensitive) | Near-month continuous contract |
| `schema` | path | string | yes | — | `1m`, `5m`, `15m`, `30m`, `60m`, `1d` | Bar size |
| `start` | query | string | no | `end` − the schema's max range | `YYYY-MM-DD` | First day |
| `end` | query | string | no | today (UTC) | `YYYY-MM-DD` | Last day |

Max range per request (`end` − `start`): `1m` 31 d · `5m` 62 d · `15m` 93 d · `30m` 186 d ·
`60m` 365 d · `1d` 3650 d.

**Response** — `{"symbol", "schema", "data": [...]}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `ts` | string | UTC ISO | Bar open time |
| `open` / `high` / `low` / `close` | float | index points (price for stock futures) | Prices |
| `volume` | int | contracts (口) | Volume |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid symbol. Allowed: [...]"}` | Symbol not covered |
| 400 | `{"error": "Invalid schema. Allowed: [...]"}` | Bad schema |
| 400 | `{"error": "Invalid date format. Use YYYY-MM-DD"}` | Malformed date |
| 400 | `{"error": "date_range_too_large", "message": "...", "max_days": <n>}` | Range over the cap |
| 503 | error message | Data source temporarily unavailable |

**Example**

```python
from datetime import date, timedelta

data = requests.get(f"{BASE_URL}/studio/market/twfutures/ohlcv/TXF/1d", headers=headers,
                    params={"start": "2024-01-01", "end": "2024-12-31"}, timeout=60).json()["data"]
# [{"ts": "2024-01-02 00:00:00+00:00", "open": 17500.0, "high": 17620.0, "low": 17480.0, "close": 17610.0, "volume": 98234}, ...]   ← 待確認：未實抓

def fetch_txf_chunked(schema, start, end, chunk_days=28):
    result, cur, end_date = [], date.fromisoformat(start), date.fromisoformat(end)
    while cur < end_date:
        chunk_end = min(cur + timedelta(days=chunk_days), end_date)
        resp = requests.get(f"{BASE_URL}/studio/market/twfutures/ohlcv/TXF/{schema}", headers=headers,
                            params={"start": cur.isoformat(), "end": chunk_end.isoformat()}, timeout=60)
        result.extend(resp.json().get("data", []))
        cur = chunk_end
    return result
```

**Notes**
- Intraday bars before 2017-05-15 are day session only (the night session 15:00–05:00 Taipei
  launched then), so bars per day jump from ~300 to ~1,140 at that date.
- The series rolls contracts at monthly settlement without price adjustment — mask the roll in
  backtests.
- For years of history use `ohlcv/<symbol>/export/<year>` instead of chunked JSON.
- A range with no data returns `200` with `[]`.

---

## `GET /studio/market/twfutures/ohlcv/symbols`

| | |
|---|---|
| Name | 期貨分線覆蓋清單 Taiwan Futures Minute-Line Symbols |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot |
| Update | Live |
| Source | Blave |

**Parameters** — none.

**Response** — `{"data": ["CDF", "DHF", "MXF", "TXF", ...]}` — symbols accepted by `ohlcv`,
`ohlcv/export`, and `bid_ask_vol`: `TXF`, `MXF`, plus the liquidity-picked subset of stock
futures with minute-line coverage (most of the 231 stock futures are not covered).

**Errors** — shared errors only.

**Example**

```python
symbols = requests.get(f"{BASE_URL}/studio/market/twfutures/ohlcv/symbols", headers=headers, timeout=30).json()["data"]
```

---

## `GET /studio/market/twfutures/ohlcv/<symbol>/export/<year>`

| | |
|---|---|
| Name | 期貨分線年檔下載 Taiwan Futures 1m Yearly Export |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2014 (TXF) |
| Update | Past years immutable; the current year's file is refreshed before download |
| Source | Sinopac Shioaji |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | path | string | yes | — | As `ohlcv/symbols` | Symbol |
| `year` | path | int | yes | — | 2014 – current year | Calendar year |

**Response** — `application/octet-stream`, a parquet file (`<SYMBOL>_<year>_1m.parquet`) with
columns `ts`, `open`, `high`, `low`, `close`, `volume` (1m bars).

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid symbol. Allowed: [...]"}` | Symbol not covered |
| 400 | `{"error": "Invalid year. Allowed: 2014-<current>"}` | Year out of range |
| 404 | `{"error": "no_data", "message": "No 1m data on disk for <symbol> in <year>"}` | No file |

**Example**

```python
import io
import pandas as pd

r = requests.get(f"{BASE_URL}/studio/market/twfutures/ohlcv/TXF/export/2024", headers=headers, timeout=120)
raw = pd.read_parquet(io.BytesIO(r.content))
raw.index = pd.to_datetime(raw["ts"], utc=True)
bars_60m = (raw[["open", "high", "low", "close", "volume"]]
            .resample("60min")
            .agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                 close=("close", "last"), volume=("volume", "sum"))
            .dropna(subset=["open"]))
```

**Notes**
- One request per year, zero server-side computation — resample locally.

---

## `GET /studio/market/twfutures/bid_ask_vol/<symbol>`

| | |
|---|---|
| Name | 台指期內外盤 Taiwan Futures Bid/Ask Volume |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2018-02-22 (TXF) |
| Update | Aggregated from ticks, refreshed on request |
| Source | Tick data (Sinopac Shioaji) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | path | string | yes | — | `TXF`（待確認：其他 `ohlcv/symbols` 代號是否有資料） | Symbol |
| `start` | query | string | no | `end` − 31 days | `YYYY-MM-DD` | First day |
| `end` | query | string | no | today (UTC) | `YYYY-MM-DD` | Last day; `end` − `start` ≤ 31 days |

**Response** — `{"symbol", "start", "end", "data": [...]}`, 1-minute rows, day and night sessions.

| Field | Type | Unit | Description |
|---|---|---|---|
| `ts` | string | UTC ISO | Bar open time |
| `bid_vol` | int | contracts | 內盤 — trades hitting the bid (seller-initiated) |
| `ask_vol` | int | contracts | 外盤 — trades lifting the ask (buyer-initiated) |
| `total_vol` | int | contracts | Total, including unclassified ticks |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid symbol. Allowed: [...]"}` | Symbol not covered |
| 400 | `{"error": "Invalid date format. Use YYYY-MM-DD"}` | Malformed date |
| 400 | `{"error": "date_range_too_large", "message": "...", "max_days": 31}` | Range over 31 days |
| 503 | error message | Data source temporarily unavailable |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twfutures/bid_ask_vol/TXF", headers=headers,
                    params={"start": "2026-05-29", "end": "2026-05-29"}, timeout=60).json()["data"]
# [{"ts": "2026-05-29 00:45:00+00:00", "bid_vol": 669, "ask_vol": 447, "total_vol": 1156}, ...]
```

---

## `GET /studio/market/twfutures/daily/<futures_id>`

| | |
|---|---|
| Name | 期貨日行情 Taiwan Futures Daily by Contract |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 1998-07-21 for TX; other products start later（待確認：出自 Notion） |
| Update | Daily after ~15:00 Taipei (TAIFEX direct before FinMind catches up); server cache 5 min |
| Source | FinMind TaiwanFuturesDaily; TAIFEX (latest day for TX / MTX / TMF) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `futures_id` | path | string | yes | — | 2–6 letters, case-insensitive — e.g. `TX`, `MTX`, `TMF`, `TE`, `TF`, or a stock-futures id (e.g. `CDF`) | Product |
| `start` | query | string | no | `1998-07-01` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"futures_id", "data": [...]}`; several rows per day (every contract month ×
trading session).

| Field | Description |
|---|---|
| `date`, `futures_id` | Day, product |
| `contract_date` | Contract month (spread contracts contain `/`) |
| `open` / `max` / `min` / `close` | Prices (`max` = high, `min` = low) |
| `spread` / `spread_per` | Change / change % |
| `volume` | Contracts |
| `settlement_price` | Settlement price |
| `open_interest` | Open interest |
| `trading_session` | `position` (regular) or `after_market` (night) |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid futures_id"}` | Format check failed |
| 404 | `{"error": "No data found for futures_id: <id>"}` | No data |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twfutures/daily/TX", headers=headers,
                    params={"start": "2026-08-01"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twfutures/stock_futures/batch/daily`

| | |
|---|---|
| Name | 股票期貨批次日行情 Stock Futures Batch Daily |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Per contract listing（待確認） |
| Update | As `/daily/<futures_id>` |
| Source | As `/daily/<futures_id>` |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `futures_ids` | query | string | yes | — | Comma-separated stock-futures ids, ≤ 250 | Ids |
| `start` | query | string | no | `1998-07-01` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"data": {"<futures_id>": [...rows as /daily...]}, "failed": [...]}`.
`failed` = ids whose fetch failed (retry); an id absent from both genuinely has no data.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "futures_ids parameter required"}` | Missing |
| 400 | `{"error": "futures_ids exceeds max 250 per request"}` | Too many |
| 400 | `{"error": "Invalid stock futures_id(s): [...]"}` | Any id is not a stock future |
| 503 | `{"error": "Stock futures symbol list temporarily unavailable. Please retry shortly."}` | Symbol list unavailable |

**Example**

```python
body = requests.get(f"{BASE_URL}/studio/market/twfutures/stock_futures/batch/daily", headers=headers,
                    params={"futures_ids": "CDF,DHF", "start": "2026-08-01"}, timeout=120).json()
```

---

## `GET /studio/market/twfutures/institutional/<futures_id>`

| | |
|---|---|
| Name | 期貨三大法人 Taiwan Futures Institutional Investors |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2018-06-05 |
| Update | Daily after ~15:00 Taipei (TAIFEX direct before FinMind catches up); server cache 5 min |
| Source | FinMind TaiwanFuturesInstitutionalInvestors; TAIFEX (latest day) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `futures_id` | path | string | yes | — | Index futures, e.g. `TX`, `MTX`, `TMF`（待確認：`TE` / `TF`）; stock futures not supported | Product |
| `start` | query | string | no | `2018-06-05` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"futures_id", "data": [...]}`, 3 rows per day (自營商 / 投信 / 外資).

| Field | Description |
|---|---|
| `date`, `futures_id` | Day, product |
| `institutional_investors` | Investor type |
| `long_deal_volume` / `long_deal_amount` | Long trades (contracts / TWD thousand（待確認：金額單位）) |
| `short_deal_volume` / `short_deal_amount` | Short trades |
| `long_open_interest_balance_volume` / `long_open_interest_balance_amount` | Long OI |
| `short_open_interest_balance_volume` / `short_open_interest_balance_amount` | Short OI |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid futures_id"}` | Format check failed |
| 404 | `{"error": "institutional data not available for stock futures (<id>)"}` | Stock future |
| 404 | error message | No data |
| 503 | upstream rate limit / symbol list unavailable | Retry later |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twfutures/institutional/TX", headers=headers,
                    params={"start": "2026-08-01"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twfutures/large_traders/<futures_id>`

| | |
|---|---|
| Name | 期貨大額交易人 Taiwan Futures Large Traders |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2007-01-02（待確認：出自 Notion；程式向上游要 1998-07-01 起） |
| Update | Daily; server cache 5 min |
| Source | FinMind TaiwanFuturesOpenInterestLargeTraders |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `futures_id` | path | string | yes | — | Index futures, e.g. `TX`; stock futures not supported | Product |
| `start` | query | string | no | `1998-07-01` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"futures_id", "data": [...]}`, 3 rows per day (`contract_type`: week / current month / all).

| Field | Description |
|---|---|
| `date`, `futures_id`, `name`, `contract_type` | Day, product, product name, contract scope |
| `buy_top5_trader_open_interest` / `buy_top10_trader_open_interest` (+ `_per`) | Long OI of top 5 / 10 traders (contracts, % of market) |
| `sell_top5_trader_open_interest` / `sell_top10_trader_open_interest` (+ `_per`) | Short OI of top 5 / 10 traders |
| `buy_top5_specific_open_interest` / `buy_top10_specific_open_interest` (+ `_per`) | Long OI of top 5 / 10 specific legal persons |
| `sell_top5_specific_open_interest` / `sell_top10_specific_open_interest` (+ `_per`) | Short OI of top 5 / 10 specific legal persons |
| `market_open_interest` | Total market OI |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid futures_id"}` | Format check failed |
| 404 | `{"error": "large_traders data not available for stock futures (<id>)"}` | Stock future |
| 404 | error message | No data |
| 503 | upstream rate limit / symbol list unavailable | Retry later |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twfutures/large_traders/TX", headers=headers,
                    params={"start": "2026-08-01"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twfutures/option/institutional/<option_id>`

| | |
|---|---|
| Name | 選擇權三大法人 Taiwan Options Institutional Investors |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2018-06-05 |
| Update | Daily; server cache 5 min |
| Source | FinMind |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `option_id` | path | string | yes | — | `TXO` (2–6 letters accepted) | Option product |
| `start` | query | string | no | `2018-06-05` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"option_id", "data": [...]}`, 6 rows per day (3 investor types × call / put).
Fields: `date`, `option_id`, `call_put` (買權 / 賣權), `institutional_investors`, and the same
`long_*` / `short_*` deal and open-interest volume / amount fields as futures institutional.

**Errors** — `400 {"error": "Invalid option_id"}`; `404` no data; `503` upstream rate limit.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twfutures/option/institutional/TXO", headers=headers,
                    params={"start": "2026-08-01"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twfutures/option/large_traders/<option_id>`

| | |
|---|---|
| Name | 選擇權大額交易人 Taiwan Options Large Traders |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2007-01-02（待確認：出自 Notion；程式向上游要 1998-07-01 起） |
| Update | Daily; server cache 5 min |
| Source | FinMind |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `option_id` | path | string | yes | — | `TXO` (2–6 letters accepted) | Option product |
| `start` | query | string | no | `1998-07-01` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"option_id", "data": [...]}`, 6 rows per day (call / put × week / current
month / all). Fields: `date`, `option_id`, `name`, `put_call`, `contract_type`, and the same
top-5 / top-10 trader and specific-legal-person open-interest fields as futures large traders,
plus `market_open_interest`.

**Errors** — `400 {"error": "Invalid option_id"}`; `404` no data; `503` upstream rate limit.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twfutures/option/large_traders/TXO", headers=headers,
                    params={"start": "2026-08-01"}, timeout=60).json()["data"]
```

---

## `GET /studio/market/twfutures/option/pcr`

| | |
|---|---|
| Name | 台指選擇權買賣權比 TXO Put/Call Ratio |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2001-12-24 |
| Update | Daily; server cache 5 min |
| Source | TAIFEX pcRatio (official) |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `start` | query | string | no | `2001-12-24` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"data": [...]}`, one row per trading day.

| Field | Unit | Description |
|---|---|---|
| `date` | — | Trading day |
| `put_volume` / `call_volume` | contracts | Put / call volume |
| `volume_pcr` | % | Put/call volume ratio |
| `put_oi` / `call_oi` | contracts | Put / call open interest |
| `oi_pcr` | % | Put/call open-interest ratio (買賣權未平倉量比率) |
| `pcr` | % | Same as `oi_pcr` (kept for compatibility) |

**Errors** — `404` no data; `503` store not ready or upstream rate limit.

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twfutures/option/pcr", headers=headers,
                    params={"start": "2024-01-01", "end": "2024-12-31"}, timeout=60).json()["data"]
# [{"date": "2024-01-02", "put_volume": ..., "call_volume": ..., "volume_pcr": ..., "put_oi": ...,
#   "call_oi": ..., "oi_pcr": 78.5, "pcr": 78.5}, ...]   ← 待確認：未實抓
```

**Notes**
- The official TAIFEX ratio — not derived from option institutional or large-trader data.

---

# Commodities

## `GET /studio/market/db/ohlcv/<dataset>/<symbol>/<schema>`

| | |
|---|---|
| Name | CME / ICE 期貨 K 線 CME / ICE Futures OHLCV |
| Group | Commodities |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2010-06-06 |
| Update | ~4 h delay |
| Source | Databento |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `dataset` | path | string | yes | — | `GLBX.MDP3` (CME), `IFEU.IMPACT` (ICE) | Venue dataset |
| `symbol` | path | string | yes | — | `GLBX.MDP3`: `CL` (WTI crude), `GC` (gold); `IFEU.IMPACT`: `BRN` (Brent) | Near-month continuous contract |
| `schema` | path | string | yes | — | `ohlcv-1d`, `ohlcv-1h`, `ohlcv-1m` | Bar size |
| `start` | query | string | no | `end` − the schema's max range | `YYYY-MM-DD` | First day |
| `end` | query | string | no | today (UTC) | `YYYY-MM-DD` | Last day |

Max range per request (`end` − `start`): `ohlcv-1d` 3650 d · `ohlcv-1h` 730 d · `ohlcv-1m` 31 d.

**Response** — `{"dataset", "symbol", "schema", "data": [...]}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `ts` | string | UTC ISO | Bar open time |
| `open` / `high` / `low` / `close` | float | USD (crude: per barrel; gold: per oz) | Prices |
| `volume` | int | contracts | Volume |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid schema. Allowed: [...]"}` | Bad schema |
| 400 | `{"error": "Invalid dataset/symbol combination"}` | Bad pair |
| 400 | `{"error": "Invalid date format. Use YYYY-MM-DD"}` | Malformed date |
| 400 | `{"error": "date_range_too_large", "message": "...", "max_days": <n>}` | Range over the cap |
| 404 | error message | No data |

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/db/ohlcv/GLBX.MDP3/CL/ohlcv-1d", headers=headers,
                    params={"start": "2024-01-01", "end": "2024-12-31"}, timeout=60).json()["data"]
# [{"ts": "2024-01-02 00:00:00+00:00", "open": 72.50, "high": 73.10, "low": 71.80, "close": 72.90, "volume": 180432}, ...]   ← 待確認：未實抓
```

**Notes**
- The most recent ~4 hours are not available.
- For long `ohlcv-1m` history, request in ≤ 31-day chunks and concatenate (a chunk takes a few seconds).

---

# Macro

## `GET /studio/market/anue/economic_calendar`

| | |
|---|---|
| Name | 總經事件行事曆 Economic Calendar |
| Group | Macro |
| Access | Any valid key |
| Rate limit | 100 requests / min per account |
| Data from | Rolling window of roughly the past month plus the next few weeks — not a history archive |
| Update | Server cache 5 min; `real` is filled in after the release |
| Source | Anue 鉅亨網 (licensed feed) |

**Parameters** — all optional; unfiltered returns the whole feed (~1,400 rows), so always filter.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `start` | query | string | no | no lower bound | `YYYY-MM-DD` (Taipei date) | Events on or after this date |
| `end` | query | string | no | no upper bound | `YYYY-MM-DD` (Taipei date) | Events on or before this date |
| `country` | query | string | no | all countries | ISO-2 codes, comma-separated, case-insensitive — e.g. `US,CN,TW` | Country filter |
| `max_priority` | query | int | no | all priorities | `1` / `2` / `3` | Keep `priority <= max_priority`. **1 is the most important**, so big events only = `max_priority=1` |
| `limit` | query | int | no | no limit | ≥ 1 | Sort by event time, then keep the first N |
| `lang` | query | string | no | `en` | `en` / `zh` | Display language for `countryName` / `subject`; names missing from the server's lookup table stay as-is, so `en` returns a zh/en mix |

**Response** — a bare JSON array (not wrapped in `{"data": ...}`). Order is the feed's own
order unless `limit` is set (then sorted by `startDate`, `time`).

| Field | Type | Unit | Description |
|---|---|---|---|
| `startDate` | int | epoch seconds | The event's Taipei calendar date |
| `time` | string \| null | `HH:MM` **Taipei time** | Release time; `null` if not published |
| `countryId` | string | ISO-2 | Country code |
| `countryName` | string | — | Country name (per `lang`) |
| `subject` | string | — | Indicator name (per `lang`) |
| `subjectTitle` | string | — | Period label, e.g. `<7月>`, `<2季>` |
| `predict` | number \| null | `unit` | Market consensus |
| `last` | number \| null | `unit` | Prior value |
| `real` | number \| null | `unit` | Actual; `null` until released |
| `unit` | string | — | e.g. `%`, `point`, `億USD` |
| `priority` | int | 1–3 | 1 = most important (non-farm payrolls, rate decisions), 3 = least (rig counts) |

The feed carries more upstream fields than listed; only the fields above are documented（待確認：完整欄位需以真實回應核對）.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid date format. Use YYYY-MM-DD"}` | Malformed `start` / `end` |
| 400 | `{"error": "max_priority must be an integer"}` | Non-integer `max_priority` |
| 400 | `{"error": "limit must be an integer"}` / `{"error": "limit must be >= 1"}` | Bad `limit` |
| 429 | `{"error_code": "ERR429", "message": "User rate limit exceeded"}` | Over 100 requests / min |

**Example**

```python
params = {"start": "2026-07-28", "end": "2026-07-31", "country": "US,CN", "max_priority": 2, "lang": "zh"}
response = requests.get(
    f"{BASE_URL}/studio/market/anue/economic_calendar",
    headers=headers, params=params, timeout=60,
)
data = response.json()
# [{"startDate": 1785715200, "time": "20:30", "countryId": "US", "countryName": "美國",
#   "subjectTitle": "<2季>", "subject": "GDP成長率(QoQ)初值", "unit": "%",
#   "predict": 1.6, "last": 2.1, "real": None, "priority": 3}, ...]   ← 待確認：未實抓
```

**Notes**
- A range outside the rolling window returns `200` with `[]` — that means "not covered", not
  "no events scheduled".
- With `start` / `end` set, events without a date are dropped; with `max_priority` set, events
  without a priority are dropped.
- **This is the only source for macro events and their numbers — never substitute a web search
  or a remembered value.** Calendar aggregator sites carry wrong tables (one listed a published
  actual as the consensus), and fields a page does not cover get filled in from training data —
  a prior value, which has exactly one right answer, has been written wrong this way. If this
  endpoint cannot answer, say so.
