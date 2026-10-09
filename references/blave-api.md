# Blave API Reference

The single reference for the Blave data API: every endpoint's path, parameters, response,
errors, and a Python example.

## Index

One row per endpoint: the line its `` ## `GET /path` `` block starts on (block = attribute
table, parameters, response, errors, example, notes — 30–80 lines). Read a block with
`offset=<line>` instead of the whole file, or locate the heading with
`` grep -n '^## `GET /price`' ``. The index is static text: regenerate it after any edit that
moves lines (command in the comment under the table).

<!-- index:start -->
| Line | Endpoint | Category |
|:-|:-|:-|
| 236 | `GET /price` | Crypto |
| 279 | `GET /alpha_table` | Crypto |
| 338 | `GET /kline` | Crypto |
| 415 | `GET /market_direction/get_alpha` | Crypto |
| 461 | `GET /screener/get_saved_conditions` | Crypto |
| 493 | `GET /screener/get_saved_condition_result` | Crypto |
| 532 | `GET /holder_concentration/get_symbols` | Crypto |
| 561 | `GET /holder_concentration/get_alpha` | Crypto |
| 610 | `GET /funding_rate/get_alpha` | Crypto |
| 662 | `GET /market_sentiment/get_symbols` | Crypto |
| 688 | `GET /market_sentiment/get_alpha` | Crypto |
| 732 | `GET /capital_shortage/get_alpha` | Crypto |
| 775 | `GET /sector_rotation/get_history_data` | Crypto |
| 814 | `GET /sector_rotation/get_overview_data` | Crypto |
| 848 | `GET /oi_imbalance/get_overview_data` | Crypto |
| 889 | `GET /whale_hunter/get_symbols` | Crypto |
| 915 | `GET /whale_hunter/get_alpha` | Crypto |
| 967 | `GET /taker_intensity/get_symbols` | Crypto |
| 993 | `GET /taker_intensity/get_alpha` | Crypto |
| 1038 | `GET /unusual_movement/get_symbols` | Crypto |
| 1064 | `GET /unusual_movement/get_alpha` | Crypto |
| 1111 | `GET /squeeze_momentum/get_symbols` | Crypto |
| 1137 | `GET /squeeze_momentum/get_alpha` | Crypto |
| 1187 | `GET /blave_top_trader/get_exposure` | Crypto |
| 1232 | `GET /liquidation/get_symbols` | Crypto |
| 1258 | `GET /liquidation/get_alpha` | Crypto |
| 1309 | `GET /liquidation/get_map` | Crypto |
| 1355 | `GET /liquidation/get_map_change` | Crypto |
| 1400 | `GET /liquidation/get_coin` | Crypto |
| 1487 | `GET /liquidation/get_exchanges` | Crypto |
| 1569 | `GET /long_short_ratio/get_table` | Crypto |
| 1665 | `GET /long_short_ratio/get_coin` | Crypto |
| 1742 | `GET /oi_imbalance/get_table` | Crypto |
| 1831 | `GET /oi_imbalance/get_coin` | Crypto |
| 1897 | `GET /oi_imbalance/get_history` | Crypto |
| 1987 | `GET /taker_intensity/get_cvd_table` | Crypto |
| 2064 | `GET /taker_intensity/get_cvd_coin` | Crypto |
| 2126 | `GET /cme_cot/get_latest` | Crypto |
| 2179 | `GET /cme_cot/get_history` | Crypto |
| 2283 | `GET /studio/market/twstock/list` | Taiwan Stock |
| 2326 | `GET /studio/market/twstock/info/<stock_id>` | Taiwan Stock |
| 2362 | `GET /studio/market/twstock/price/<stock_id>` | Taiwan Stock |
| 2423 | `GET /studio/market/twstock/price_adj/<stock_id>` | Taiwan Stock |
| 2456 | `GET /studio/market/twstock/quote/<stock_id>` | Taiwan Stock |
| 2517 | `GET /studio/market/twstock/quote` | Taiwan Stock |
| 2557 | `GET /studio/market/twstock/quote/all` | Taiwan Stock |
| 2587 | `GET /studio/market/twstock/minute/ohlcv/<stock_id>/<schema>` | Taiwan Stock |
| 2651 | `GET /studio/market/twstock/minute/ohlcv/symbols` | Taiwan Stock |
| 2678 | `GET /studio/market/twstock/kbar/<stock_id>` | Taiwan Stock |
| 2729 | `GET /studio/market/twstock/market_value/<stock_id>` | Taiwan Stock |
| 2762 | `GET /studio/market/twstock/market_value/all` | Taiwan Stock |
| 2842 | `GET /studio/market/twstock/per/<stock_id>` | Taiwan Stock |
| 2887 | `GET /studio/market/twstock/financials/<stock_id>` | Taiwan Stock |
| 2931 | `GET /studio/market/twstock/balance_sheet/<stock_id>` | Taiwan Stock |
| 2960 | `GET /studio/market/twstock/cashflow/<stock_id>` | Taiwan Stock |
| 3011 | `GET /studio/market/twstock/monthly_revenue/<stock_id>` | Taiwan Stock |
| 3061 | `GET /studio/market/twstock/dividend/<stock_id>` | Taiwan Stock |
| 3126 | `GET /studio/market/twstock/news/<stock_id>` | Taiwan Stock |
| 3172 | `GET /studio/market/twstock/institutional/<stock_id>` | Taiwan Stock |
| 3225 | `GET /studio/market/twstock/margin/<stock_id>` | Taiwan Stock |
| 3278 | `GET /studio/market/twstock/shareholding/<stock_id>` | Taiwan Stock |
| 3320 | `GET /studio/market/twstock/foreign_shareholding/<stock_id>` | Taiwan Stock |
| 3364 | `GET /studio/market/twstock/gov_bank/<stock_id>` | Taiwan Stock |
| 3409 | `GET /studio/market/twstock/lending/<stock_id>` | Taiwan Stock |
| 3452 | `GET /studio/market/twstock/broker/search` | Taiwan Stock |
| 3489 | `GET /studio/market/twstock/broker/stock/<stock_id>` | Taiwan Stock |
| 3544 | `GET /studio/market/twstock/broker/trader/<trader_id>` | Taiwan Stock |
| 3579 | `GET /studio/market/twstock/batch/<data_type>` | Taiwan Stock |
| 3641 | `GET /studio/market/twmarket/index/<index_id>` | Taiwan Market (大盤) |
| 3682 | `GET /studio/market/twmarket/turnover` | Taiwan Market (大盤) |
| 3722 | `GET /studio/market/twmarket/institutional` | Taiwan Market (大盤) |
| 3767 | `GET /studio/market/twmarket/margin` | Taiwan Market (大盤) |
| 3808 | `GET /studio/market/twmarket/dividend_points` | Taiwan Market (大盤) |
| 3869 | `GET /studio/market/twfutures/ohlcv/<symbol>/<schema>` | Taiwan Futures & Options |
| 3952 | `GET /studio/market/twfutures/ohlcv/symbols` | Taiwan Futures & Options |
| 3980 | `GET /studio/market/twfutures/ohlcv/<symbol>/export/<year>` | Taiwan Futures & Options |
| 4033 | `GET /studio/market/twfutures/bid_ask_vol/<symbol>` | Taiwan Futures & Options |
| 4086 | `GET /studio/market/twfutures/daily/<futures_id>` | Taiwan Futures & Options |
| 4137 | `GET /studio/market/twfutures/stock_futures/batch/daily` | Taiwan Futures & Options |
| 4178 | `GET /studio/market/twfutures/institutional/<futures_id>` | Taiwan Futures & Options |
| 4234 | `GET /studio/market/twfutures/large_traders/<futures_id>` | Taiwan Futures & Options |
| 4283 | `GET /studio/market/twfutures/option/institutional/<option_id>` | Taiwan Futures & Options |
| 4318 | `GET /studio/market/twfutures/option/large_traders/<option_id>` | Taiwan Futures & Options |
| 4354 | `GET /studio/market/twfutures/option/pcr` | Taiwan Futures & Options |
| 4402 | `GET /studio/market/twfutures/carrying_cost/<identity>` | Taiwan Futures & Options |
| 4501 | `GET /studio/market/db/ohlcv/<dataset>/<symbol>/<schema>` | Commodities |
| 4563 | `GET /studio/market/anue/economic_calendar` | Macro |
<!-- index:end -->
<!-- regenerate (from the repo root): python3 - <<'EOF'
import re
p = "references/blave-api.md"
L = open(p, encoding="utf-8").read().split("\n")
def rows(L):
    out, cat, fence = [], "", False
    for i, l in enumerate(L, 1):
        if l.startswith("```"): fence = not fence; continue
        if fence: continue
        if l.startswith("# "): cat = l[2:].strip()
        m = re.match(r"^## `((?:GET|POST) [^`]+)`", l)
        if m: out.append((i, m.group(1), cat))
    return out
a = L.index("<!-" + "- index:start -" + "->"); b = L.index("<!-" + "- index:end -" + "->")
for _ in range(2):
    tbl = ["| Line | Endpoint | Category |", "|:-|:-|:-|"] + [f"| {i} | `{e}` | {c} |" for i, e, c in rows(L)]
    L[a + 1:b] = tbl; b = a + 1 + len(tbl)
open(p, "w", encoding="utf-8").write("\n".join(L))
EOF
-->

## Conventions

**Base URL:** `https://api.blave.org` — every path below is relative to it.

**Auth headers:** `api-key` + `secret-key` on every request (create a key at
<https://blave.org/landing/en/api?tab=blave>).

**Access** — what the key's account needs, per endpoint (`Access` row in each block):

| Value | Meaning |
|---|---|
| `API plan or data fee` | Valid key, and the account's billing covers data — see *Which key, which plan* below. Not covered → `403 ERR007` |
| `Any valid key` | Valid key only — no plan check, no data fee |

**Which key, which plan.** Blave Agent is moving from hourly billing to plan billing; each account
switches on a date the platform emails that user.

- **A key you created yourself** (API page above — what scripts, external agents and this skill
  use outside Blave Agent): on plan billing it needs an **API plan**, even if the account also has
  a Blave Agent plan or trial. Before the account switches, it also works when the account owns a
  Blave Agent machine, or with the hourly data fee charged from credit.
- **Keys Blave Agent issues** (the cloud machine's own key, the desktop app's sign-in key):
  covered by the card trial, an active Blave Agent plan (every tier includes data) or an API
  plan.
- Not covered → `403 ERR007`; its `message` and `next_steps` name the way out — follow them, do
  not guess a price.

**Rate limit** — unless a block says otherwise: 500 requests / 5 min per API key, and
500 requests / 5 min per IP. The window resets after 5 minutes.

**Shared errors** (endpoint-specific errors are listed in each block):

| Status | Body | When |
|---|---|---|
| 403 | `{"error_code": "ERR005", "message": "API key and Secret key are required."}` | Header missing (`API plan or data fee` endpoints) |
| 422 | `{"error_code": "ERR001", "message": "Token is invalid or expired."}` | Header missing (`Any valid key` endpoints) |
| 403 | `{"error_code": "ERR005", "message": "Invalid API key."}` / `"Invalid Secret key."` | Wrong key pair |
| 403 | `{"error_code": "ERR007", "message": "…", "next_steps": {…}}` | The key's account is not covered (see *Which key, which plan*): a self-created key without an API plan, no Blave Agent plan, or the hourly data fee could not be charged — `message` says which |
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
# {"symbol": "BTC", "price": 75838.2, "change_24h": -0.01739}
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
row = body["data"]["0G"]   # one token out of the 716 keys this response carried
# {"holder_concentration": {"-": 0.9267}, "holder_concentration_chg": {"15min": -0.0118, "1h": 0.0075, "24h": 0.4723, "3d": -0.1852, "30d": "", ...},
#  "funding_rate": {"binance": 0.005, "bybit": 0.005, "okx": 0.005, "pionex": "", ...},
#  "liquidation": {"15min": 0.0, "1h": -0.2665, "24h": -0.5637, "1min": "", ...},
#  "market_cap": {"-": 42204386.29}, "market_cap_percentile": {"-": 56.55},
#  "price": {"-": 0.1832}, "price_change": {"15min": -0.00215, "24h": -0.05792, ...},
#  "statistics": {"up_prob": 0.4277, "exp_value": -0.00478, "is_data_sufficient": false, ...}, ...}
# (shape captured from a live response; `""` marks insufficient data)
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
| Data from | 2020-01-01, or the contract's listing date if later — every interval, `1min` included |
| Update | The latest closed 1-minute bar is usually available within the next minute; in rare degraded cases the newest bars can lag about 5–10 minutes. Server cache: 30 s (`1min`), 300 s (`1h` / `4h` / `1d`), 60 s (every other period); only 5 s when the latest closed bar is not in yet |
| Source | Binance USDⓈ-M futures |

**Coverage.** Every Binance USDⓈ-M perpetual whose symbol ends in `USDT` — 740 contracts as of
October 2026, including tokenized stocks, commodities and other TradFi USDT perpetuals. All 740
have their full 1-minute history stored server-side, from 2020-01-01 or the listing date.
A newly listed perpetual becomes queryable about 5–10 minutes after listing.

**Not covered:** contracts quoted in USDC, USD1, U or BTC (e.g. `BTCUSDC`, `ETHBTC`) and
quarterly delivery contracts — these return the `400 unknown symbol or no data` error below.
Delisted contracts are not guaranteed: one may answer with whatever history is still stored or
with that same `400` (those delisted before October 2026 have no `1min`–`4min` history).

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | `BTCUSDT`; also `BTC`, `btc`, `BTC/USDT`, `BTC-USDT` | Binance USDⓈ-M `USDT` perpetual. A bare token gets `USDT` appended; a bare token that only exists with a multiplier prefix resolves to it (`PEPE` → `1000PEPEUSDT`) |
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
| 400 | `{"error": "unknown symbol or no data: <symbol>"}` | Symbol not covered (see *Not covered*) or not a real contract, e.g. `BTCUSDC`, `ETHBTC`, a typo. `<symbol>` echoes the value you sent. Not transient — do not retry |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2026-10-01", "end_date": "2026-10-02"}
response = requests.get(f"{BASE_URL}/kline", headers=headers, params=params, timeout=60)
data = response.json()
# [{"time": 1790812800.0, "open": 83576.8, "high": 83612.6, "low": 83370.0, "close": 83460.0, "volume": 3123.991}, ...]
```

**Notes**
- A window entirely before the listing date of a covered contract returns `200` with `[]`, not
  an error.
- At `1min` every bar returned is closed. A longer period can end in a partial bar when
  `end_date` is today — it is built from the bars closed so far (at 07:09 UTC the `07:00` `1h`
  bar holds 07:00–07:05); drop it if you need closed bars only.
- For history beyond one window, send one request per window and concatenate (e.g. 3 years of
  `5min` = 3 requests; 1 year of `1min` = 13 requests of ≤30 days).
- All 740 USDT perps have full 1-minute history on disk, so a deep request is answered from
  stored data — there is no slow first fetch.

---

## `GET /market_direction/get_alpha`

| | |
|---|---|
| Name | 市場方向 Market Direction |
| Group | Crypto › Tool |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2024-12-27 (earliest `1d` bar returned; market-wide series, no symbol dimension) |
| Update | Every 5 minutes |
| Source | Blave — one market-wide series (composite of Blave's crypto indicator overviews, no symbol dimension) |

**Parameters** — no `symbol`: `alpha` is a single market-wide series, not a per-coin one.
BTCUSDT is used internally only to align the bars; it is not returned and does not change
`alpha`. See *Crypto indicator conventions*.

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
params = {"period": "1h", "start_date": "2026-09-13", "end_date": "2026-09-15"}
response = requests.get(f"{BASE_URL}/market_direction/get_alpha", headers=headers, params=params, timeout=60)
# {"data": {"alpha": [-0.5195979478976323, -0.5223392571665055, -0.5612490182062327, ...],
#           "timestamp": [1789257600.0, 1789261200.0, 1789264800.0, ...]}}   # 72 bars
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
| Data from | 2021-05-11 (BTCUSDT `1d`; other symbols can start later) |
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
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2026-09-13", "end_date": "2026-09-15"}
response = requests.get(f"{BASE_URL}/holder_concentration/get_alpha", headers=headers, params=params, timeout=60)
# {"data": {"alpha": [-1.1931909718306861, -1.2035898186867282, -1.2037004015202886, ...],
#           "timestamp": [1789257600.0, 1789261200.0, 1789264800.0, ...],
#           "stat": {"up_prob": 0.509739818557561, "exp_value": -0.00051954905018229,
#                    "avg_up_return": 0.015512131150026753, "avg_down_return": -0.017188220228787618,
#                    "return_ratio": 0.9024861762037658, "is_data_sufficient": true}}}   # 72 bars
```

---

## `GET /funding_rate/get_alpha`

| | |
|---|---|
| Name | 資金費率 Funding Rate |
| Group | Crypto › Alpha › Funding Rate |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2025-09-30 (BTCUSDT `1d`; other symbols can start later; `exchange=bybit` starts later — read the first timestamp) |
| Update | Every 5 minutes |
| Source | USDT-M perpetual funding rate of the chosen `exchange` (Binance by default); `close` is always the Binance perp |

**Parameters** — see *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | e.g. `BTCUSDT` | Symbol (Binance form, whichever exchange) |
| `period` | query | string | yes | — | `5min`, `15min`, `1h`, `4h`, `8h`, `1d` | Bar size |
| `exchange` | query | string | no | `binance` | `binance`, `okx`, `bingx`, `bybit` | Whose perp funding rate to read; any other value is `400` |
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
| 400 | `{"error": "exchange must be one of binance, okx, bingx, bybit"}` | `exchange` outside the list |

**Example**

```python
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2026-09-13", "end_date": "2026-09-15"}
response = requests.get(f"{BASE_URL}/funding_rate/get_alpha", headers=headers, params=params, timeout=60)
# {"data": {"timestamp": [1789257600.0, 1789261200.0, 1789264800.0, ...],
#           "alpha": [0.005064, 0.006165, 0.007765, ...],
#           "close": [77239.5, 77285.5, 77263.9, ...],
#           "stat": {"up_prob": 0.5009438427095587, "exp_value": -0.0008769555139270298,
#                    "is_data_sufficient": false, ...}}}   # 72 bars
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
| Data from | 2020-01-01 (BTCUSDT `1d`; other symbols can start later) |
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
| Data from | 2023-12-09 (`1d`; market-wide series, no symbol dimension) |
| Update | Every 5 minutes |
| Source | Blave (market-wide, Binance USDT lending APR) |

**Parameters** — no `symbol`; market-wide. See *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `period` | query | string | yes | — | `5min`, `15min`, `1h`, `4h`, `8h`, `1d` | Bar size — `5min` and `15min` both return data |
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
| Data from | Trailing one-year daily window — a call returned 366 daily points, 2025-09-16 → 2026-09-16, each sector seen starting at `0.0`. There are no parameters, so a longer history is not reachable through this endpoint; whether one exists upstream is 待確認 |
| Update | 待確認 |
| Source | Blave |

**Parameters** — none.

**Response** — `{"data": {"alpha": {<sector>: {"data": [...], "name_en": ..., "name_zh": ...}},
"timestamp": [...]}}`. `timestamp` sits next to `alpha` at the top of `data`, not inside each
sector; it is the shared time axis for every sector series.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC), one per point — 366 daily points in the observed response |
| `alpha.<sector>.data` | float[] | The sector series, same length and order as `timestamp` (366); the first element is `0.0` |
| `alpha.<sector>.name_en` / `name_zh` | string | Sector display name |

**Errors** — shared errors only.

**Example**

```python
response = requests.get(f"{BASE_URL}/sector_rotation/get_history_data", headers=headers, timeout=60)
# {"data": {"alpha": {"AI": {"data": [0.0, 0.04377017039444864, 0.04922749428543449, ...],
#                           "name_en": "AI", "name_zh": "人工智能"},
#                     "BNB Eco": {"data": [0.0, 0.008847752133756215, ...],
#                                 "name_en": "BNB Eco", "name_zh": "BNB 生態"}, ...},
#           "timestamp": [1757980800.0, 1758067200.0, 1758153600.0, ...]}}   # 51 sectors, 366 points
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
| Data from | 2021-12-01 (BTCUSDT `1d`; other symbols can start later) |
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
- `timeframe` is not validated server-side. One value outside the list was tried, `2h`, and it
  returned `200` with data. That is a single observation — it does **not** establish that any
  `{n}h` works. Stay on the listed values unless you verify the one you need.

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
| Data from | 2020-01-01 (BTCUSDT `1d`; other symbols can start later) |
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
| Data from | 2020-01-02 (BTCUSDT `1d`; other symbols can start later) |
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
| Data from | 2020-02-09 — first non-zero `alpha` for BTCUSDT (other symbols can start later) |
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

**Notes**
- The series is padded: BTCUSDT rows exist from 2020-01-01, but `alpha` is `0.0` until
  2020-02-09. A request starting earlier than the *Data from* date returns those padded rows —
  they are filler, not signal. Drop leading zeros, or start at the *Data from* date.

---

## `GET /blave_top_trader/get_exposure`

| | |
|---|---|
| Name | Blave 頂尖交易員曝險 Blave Top Trader Exposure |
| Group | Crypto › Alpha › Blave Top Trader |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2025-03-03 |
| Update | Every 5 minutes |
| Source | Blave — one market-wide series (all coins these traders hold, no symbol dimension) |

**Parameters** — no `symbol`: `alpha` is a single market-wide series, not a per-coin one.
BTCUSDT is used internally only to align the bars; it is not returned and does not change
`alpha`. See *Crypto indicator conventions*.

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `period` | query | string | yes | — | `1h`, `4h`, `8h`, `1d` | Bar size |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` | First day |
| `end_date` | query | string | no | today | `YYYY-MM-DD` | Last day |

**Response** — `{"data": {"timestamp": [...], "alpha": [...]}}`. No `stat`.

| Field | Type | Description |
|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) |
| `alpha` | float[] | Net exposure of Blave's top traders (top 10% by account assets) — the median, across those traders, of each trader's net notional position ÷ own assets, ×100 (positive = net long). A raw ratio, not a z-score |

**Errors**

| Status | Body | When |
|---|---|---|
| 403 | `{"error": "period is required"}` | Missing parameter |

**Example**

```python
params = {"period": "1h", "start_date": "2025-05-01", "end_date": "2025-07-01"}
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

**Notes**
- The series is padded: BTCUSDT rows exist from 2020-01-01, but `alpha` is `0.0` until
  2023-01-01. A request starting earlier than the *Data from* date returns those padded rows —
  they are filler, not signal. Drop leading zeros, or start at the *Data from* date. Symbols
  other than BTC/ETH turn non-zero later still, so check per symbol.

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

## `GET /liquidation/get_coin`

| | |
|---|---|
| Name | 每幣爆倉 Liquidation by Coin |
| Group | Crypto › Alpha › Liquidation |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot (last 24 h) |
| Update | Every 5 minutes (server cache 5 min) |
| Source | Blave (Binance, Bybit, Gate.io, OKX, HTX, Bitfinex liquidation feeds; USD notional converted at collection time, so exchanges can be summed) |

One coin's forced liquidations across every exchange feed Blave collects: four rolling
windows with the per-exchange split, an hourly 24-point series, and each feed's coverage
notes. This is real liquidation flow (like `get_alpha`'s input), not the model estimate
behind `get_map`.

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | `BTC`, `BTCUSDT`, `btc`, `BTC-USDT-SWAP`, `BTC_USDT` (≤ 32 chars) | Coin. The quote suffix is stripped; the response `symbol` is the normalised coin name |

**Response** — `{"data": {"symbol", "rank", "updated_at", "windows", "exchanges", "detail_complete", "series"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `symbol` | string | — | Normalised coin name, e.g. `BTC` |
| `rank` | int / null | — | Position among the top 50 coins by 24 h total across exchanges; `null` outside the top 50 or with no event |
| `updated_at` | string / null | ISO 8601 UTC | Time of the latest 5-minute bucket used |
| `windows` | object | — | Keys are the strings `"1"`, `"4"`, `"12"`, `"24"` (hours). Each is a **rolling** window ending at the latest 5-minute bucket, with the fields below |
| `windows.<h>.total_liq_usd` / `long_liq_usd` / `short_liq_usd` | float | USD | Summed across exchanges; `long` = long positions liquidated (price fell), `short` = shorts liquidated (price rose) |
| `windows.<h>.long_pct` / `short_pct` | float / null | ratio 0–1 | Share of the window total; `null` when the window total is 0 |
| `windows.<h>.covered_hours` | float | h | How many hours of the window actually have buckets (< `h` right after a collector restart) |
| `windows.<h>.by_exchange` | object | USD | `{exchange: {total_liq_usd, long_liq_usd, short_liq_usd}}`. An exchange with **no event** in the window has **no key** — read `exchanges[]` to tell "feed alive, this coin quiet" from "feed absent" |
| `exchanges[]` | object[] | — | One row per feed (six today, present even with no event), sorted by 24 h total desc, then roster order |
| `exchanges[].exchange` | string | — | `binance`, `bybit`, `gate`, `okx`, `htx`, `bitfinex` |
| `exchanges[].listed` | bool / null | — | Whether that exchange lists a USDT-margined perpetual for the coin; `null` when the contract list could not be fetched (Bitfinex always `null`) |
| `exchanges[].last_event_at` | string / null | ISO 8601 UTC | Latest bucket seen from that feed (any coin); `null` if never seen |
| `exchanges[].price_basis` | string | — | Price used for USD conversion: `trade_avg`, `bankruptcy`, `unverified` |
| `exchanges[].coverage` | string | — | Feed completeness: `full`, `full_unstated`, `sampled_1s`, `aggregated_1s`, `sampled_undisclosed` |
| `exchanges[].time_basis` | string | — | `event` — bucketed by the event's own timestamp |
| `detail_complete` | bool | — | `false` when the coin may have been cut from a full per-bucket detail list (feeds keep the top 100 coins per 5-minute bucket): `windows` can then under-count. Top-50 coins are almost always `true` |
| `series.bucket_seconds` | int | s | Always `3600` |
| `series.points` | object[] | — | **Always 24** entries, oldest → newest, on clock hours; the last is the current hour up to `updated_at` (the snapshot is rebuilt every 5 min, so it can trail the request by a few minutes). Each `{ts, long_liq_usd, short_liq_usd}`; hours with no event are `0`, never missing |

`windows["24"]` is the same rolling frame as the exchange matrix, so the same coin shows the
same 24 h number there. `series` is on clock hours, so Σ `points` ≠ `windows["24"]` by design:
take totals from `windows`, timing from `series`.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "symbol is required"}` | `symbol` missing, blank, longer than 32 chars, or nothing left after the quote suffix is stripped (e.g. `symbol=USDT`) |
| 404 | `{"error": "<SYMBOL> is not a collected symbol"}` | No exchange lists the coin and no feed reported it in the last 24 h — an answer, not a transient |
| 503 | `{"error": "liquidation data unavailable"}` | Upstream buckets did not answer — retry later; never read as "0 liquidations" |

**Example**

```python
response = requests.get(f"{BASE_URL}/liquidation/get_coin", headers=headers, params={"symbol": "BTC"}, timeout=30)
data = response.json()["data"]
day = data["windows"]["24"]
print(data["symbol"], data["rank"], day["total_liq_usd"], day["long_pct"])
peak = max(data["series"]["points"], key=lambda p: p["long_liq_usd"] + p["short_liq_usd"])
# Live capture 2026-09-20 (abridged with ...; same payload the studio page serves):
# {"data": {"symbol": "BTC", "rank": 1, "updated_at": "2026-09-20T17:15:00+00:00",
#           "windows": {"1": {"covered_hours": 1.0, "total_liq_usd": 3429619.97, "long_liq_usd": 129200.73, "short_liq_usd": 3300419.23,
#                             "long_pct": 0.0377, "short_pct": 0.9623, "by_exchange": {...}},
#                       "4": {...}, "12": {...},
#                       "24": {"covered_hours": 24.0, "total_liq_usd": 58723607.89, "long_liq_usd": 38063430.51, "short_liq_usd": 20660177.37,
#                              "long_pct": 0.6482, "short_pct": 0.3518,
#                              "by_exchange": {"binance": {"long_liq_usd": 17075740.21, "short_liq_usd": 6697256.41, "total_liq_usd": 23772996.62}, ...}}},
#           "exchanges": [{"coverage": "sampled_1s", "exchange": "binance", "last_event_at": "2026-09-20T17:15:00+00:00", "listed": true, "price_basis": "trade_avg", "time_basis": "event"}, ... 6 rows],
#           "detail_complete": true,
#           "series": {"bucket_seconds": 3600, "points": [..., {"long_liq_usd": 60660.74, "short_liq_usd": 6129662.69, "ts": "2026-09-20T16:00:00+00:00"}, {"long_liq_usd": 95373.53, "short_liq_usd": 5473.13, "ts": "2026-09-20T17:00:00+00:00"}]}}}
```

**Notes**
- Snapshot only: no `start_date` / `end_date`, and nothing older than 24 h. For history use
  `get_alpha` (a normalised long/short imbalance, not USD amounts).
- Symbol handling differs from the other liquidation endpoints: `get_alpha` / `get_map` need the
  Binance perp form (`BTCUSDT`); here `BTC` and `BTCUSDT` are the same coin.

---

## `GET /liquidation/get_exchanges`

| | |
|---|---|
| Name | 爆倉矩陣 Liquidation Exchange Matrix |
| Group | Crypto › Alpha › Liquidation |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Rolling window, 5-minute aligned (default last 24 h) |
| Update | Every 5 minutes (server cache 5 min) |
| Source | Blave (Binance, Bybit, Gate.io, OKX, HTX, Bitfinex liquidation feeds; USD notional converted at collection time, so exchanges can be summed) |

Whole-market forced liquidations, aggregated per exchange and as a coin × exchange matrix —
the market-wide companion to `/liquidation/get_coin`. Same rolling 5-minute-aligned frame,
so a coin's 24 h total is the same number on both.

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `hours` | query | int | no | `24` | 1–168 | Window length. Outside the range → `400` (it is not clamped); a non-integer value silently falls back to the default |
| `top_n` | query | int | no | `10` | 1–50 | How many coins to list individually; the rest go to `others`. Same range / non-integer rules as `hours` |

**Response** — `{"data": {"exchanges", "coins", "others", "total", "buckets", "covered_hours", "window_hours", "window_start", "window_end", "updated_at"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `exchanges[]` | object[] | — | One row per feed, sorted by total desc: `exchange`, `total_liq_usd`, `long_liq_usd`, `short_liq_usd`, `long_pct`, `short_pct`, `events`, `last_event_at`. Every feed is always listed: amounts `null` = no data received from that feed in the window (sorted last), `0.0` = connected but no liquidations |
| `exchanges[].price_basis` / `.coverage` / `.time_basis` | string | — | How comparable that row is: `trade_avg` / `bankruptcy` / `unverified`; `full`, `full_unstated`, `sampled_1s`, `aggregated_1s`, `sampled_undisclosed`; `event`. **Keep them when re-publishing the numbers** — a sampled feed is not a full one |
| `coins[]` | object[] | — | The top `top_n` by cross-exchange total: `token`, `token_id` (`0` when the symbol has no CoinMarketCap id), `total_liq_usd`, `long_liq_usd`, `short_liq_usd`, `by_exchange{name: {total/long/short_liq_usd}}`. `by_exchange` is sparse — a feed with nothing for that coin has no key; read it as `0` when that feed's `exchanges[]` total is not `null` |
| `others` | object | — | Everything `top_n` cut off, same fields plus `coin_count`, so `coins[] + others` adds back to each exchange's total |
| `total` | object | USD / ratio | `total_liq_usd`, `long_liq_usd`, `short_liq_usd`, `long_pct`, `short_pct` |
| `covered_hours` | float | h | Hours of the window that actually have buckets (< `hours` right after a collector restart) |
| `buckets` | int | — | Number of 5-minute buckets aggregated |
| `window_hours` / `window_start` / `window_end` | int / string | h / ISO 8601 UTC | The window as the server resolved it |
| `updated_at` | string | ISO 8601 UTC | Latest bucket used |

`long_liq_usd` = long positions liquidated (price fell); `short_liq_usd` = shorts liquidated
(price rose).

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "hours must be between 1 and 168"}` / `{"error": "top_n must be between 1 and 50"}` | Out-of-range parameter |

**Example**

```python
params = {"hours": 24, "top_n": 10}
data = requests.get(f"{BASE_URL}/liquidation/get_exchanges", headers=headers, params=params, timeout=30).json()["data"]
print(data["total"]["total_liq_usd"], data["total"]["short_pct"])
print([(e["exchange"], e["total_liq_usd"], e["coverage"]) for e in data["exchanges"]])
# Live capture 2026-09-22 (abridged with ...; anonymous studio twin /studio/charts/liquidation/exchanges,
# same inner shape — the API-key response wraps it in "data" and allows top_n up to 50):
# {"exchanges": [{"exchange": "binance", "total_liq_usd": 390250999.16, "long_liq_usd": 69367041.38,
#                 "short_liq_usd": 320883957.78, "long_pct": 0.1777, "short_pct": 0.8223, "events": 46200,
#                 "last_event_at": "2026-09-22T05:50:00+00:00", "price_basis": "trade_avg",
#                 "coverage": "sampled_1s", "time_basis": "event"}, ... 6 rows],
#  "coins": [{"token": "BTC", "token_id": 1, "total_liq_usd": 397165128.6, "long_liq_usd": 68908479.16,
#             "short_liq_usd": 328256649.44,
#             "by_exchange": {"binance": {"long_liq_usd": 17994806.07, "short_liq_usd": 173732353.71,
#                                         "total_liq_usd": 191727159.78}, ... 6 exchanges}}, ... 10 coins],
#  "others": {"coin_count": 835, "total_liq_usd": 82658628.27, "long_liq_usd": 34622797.57,
#             "short_liq_usd": 48035830.7, "by_exchange": {...}},
#  "total": {"total_liq_usd": 743631889.64, "long_liq_usd": 175240866.53, "short_liq_usd": 568391023.1,
#            "long_pct": 0.2357, "short_pct": 0.7643},
#  "buckets": 1846, "covered_hours": 24.0, "window_hours": 24,
#  "window_start": "2026-09-21T05:55:00+00:00", "window_end": "2026-09-22T05:55:00+00:00",
#  "updated_at": "2026-09-22T05:50:00+00:00"}
```

**Notes**
- No data at all (feeds down, or the data source unreachable) is still a `200` with the same
  shape and every amount `null`, `buckets: 0` — never a table of zeros. Check `total.total_liq_usd`
  before using the numbers.
- Totals only — no time series. Hourly shape for one coin is `/liquidation/get_coin`; a
  normalised long-history signal is `/liquidation/get_alpha`.
- The window is rolling, not a calendar day, and it is the same frame `/liquidation/get_coin`
  uses for `windows["24"]`.

---
## `GET /long_short_ratio/get_table`

| | |
|---|---|
| Name | 多空比總表 Long/Short Ratio Table |
| Group | Crypto › Raw data › Long/short ratio |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot (latest cross-section) |
| Update | 5-minute buckets; the snapshot is the latest bucket each source published (Gate / OKX land ≈ 10 min late) |
| Source | Blave (Binance, OKX, Gate.io, Bybit long/short-ratio feeds) |

Every collected coin × every long/short-ratio source, as of now. **Ten sources:** Binance,
OKX and Gate.io each publish three kinds — all accounts, top-trader accounts, top-trader
positions — and Bybit publishes accounts only. Rows are ordered by Binance open-interest
notional. Only coins that resolve to a CoinMarketCap crypto are listed; the API-key
response is the full table (`full: true`), the anonymous studio twin only the rows of its
30-coin whitelist.

**Parameters** — none.

**Response** — `{"data": {"coins", "sources", "summary", "tokens_shown", "tokens_total", "full", "updated_at"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `coins[]` | object[] | — | One row per coin: `token`, `token_id`, plus one value per source key |
| `coins[].<source key>` | float / null | ratio | Long accounts (or positions) ÷ short. `null` = that exchange has no such feed for the coin. Long share = `r / (1 + r)` — the API does not precompute it |
| `sources[]` | object[] | — | The ten feeds, in column order. **Read this, never a hard-coded key list** |
| `sources[].key` | string | — | `<exchange>_<type>`, e.g. `binance_top_position` — the key used in `coins[]` |
| `sources[].exchange` / `.type` | string | — | `binance` / `okx` / `gate` / `bybit`; `account` / `top_account` / `top_position` |
| `sources[].last_at` | string | ISO 8601 UTC | Newest sample from that feed |
| `sources[].stale` | bool | — | That feed's newest sample is over 1 hour old (measured against now). Top-level `updated_at` is the newest source and says nothing about any single one — judge a source by its own `last_at` / `stale` |
| `summary.binance_tokens` / `.binance_long_majority` | int | — | Coins with a Binance account ratio / of those, how many are above 1. Computed over the whole table, not the rows shown |
| `tokens_shown` / `tokens_total` | int | — | Rows returned / rows in the table. Equal on an API key |
| `full` | bool | — | `true` on an API key; `false` on the anonymous studio twin |
| `updated_at` | string | ISO 8601 UTC | Newest bucket across sources |

**"Top trader" is a different population at each exchange — do not compare the levels across exchanges.**

| Exchange | Who counts as a top trader (official wording) |
|---|---|
| Binance | "the top 20% users with the highest margin balance" |
| OKX | "the top 5% of traders with the largest open position value" |
| Gate.io | Never published — the docs only name the fields |

So `binance_top_account` above `okx_top_account` says nothing about which venue's big
traders are more long. Compare each source against **its own** history instead.

**Errors**

| Status | Body | When |
|---|---|---|
| 503 | `{"error": "long short ratio data unavailable"}` | No fresh snapshot — retry later; never read as an empty market |

**Example**

```python
data = requests.get(f"{BASE_URL}/long_short_ratio/get_table", headers=headers, timeout=30).json()["data"]
keys = [s["key"] for s in data["sources"] if not s["stale"]]
btc = next(c for c in data["coins"] if c["token"] == "BTC")
print({k: btc[k] for k in keys if btc[k] is not None})
# Live capture 2026-09-22 via the anonymous studio twin (/studio/charts/long_short_ratio/table) —
# same inner shape; the API-key response wraps it in "data" and has full: true with every row.
# {"coins": [{"binance_account": 0.8818, "binance_top_account": 1.0149, "binance_top_position": 2.2666,
#             "bybit_account": 1.0375, "gate_account": 0.7294, "gate_top_account": 0.6944,
#             "gate_top_position": 1.6436, "okx_account": 0.9084, "okx_top_account": 0.8655,
#             "okx_top_position": 1.0222, "token": "BTC", "token_id": 1}, ...],
#  "sources": [{"exchange": "binance", "key": "binance_account", "last_at": "2026-09-22T05:50:00+00:00",
#               "stale": false, "type": "account"}, ...,
#              {"exchange": "bybit", "key": "bybit_account", "last_at": "2026-09-22T05:50:00+00:00",
#               "stale": false, "type": "account"}],
#  "summary": {"binance_long_majority": 436, "binance_tokens": 509},
#  "tokens_shown": 30, "tokens_total": 611, "full": false, "updated_at": "2026-09-22T05:50:00+00:00"}
```

**Collection start** (first stored bucket, measured on BTC 2026-09-22)

| Source key | Collecting since |
|---|---|
| `binance_account` | 2021-05-11 |
| `binance_top_account` / `binance_top_position` | 2026-08-22 |
| `okx_account` / `okx_top_account` / `okx_top_position` | 2025-02-18 |
| `gate_account` / `gate_top_account` / `gate_top_position` | 2026-08-12 |
| `bybit_account` | 2026-08-12 |

Every source is now older than the 7 days this dataset serves, so none of them limits a query —
the dates matter only if you are told a source "has no history".

**Notes**
- A cross-section, not history. For a series use `/long_short_ratio/get_coin` (7 days) — there
  is no long-history endpoint for this dataset.
- Granularity is 5 minutes, but each source publishes on its own clock — do not describe it as
  "updates every 5 minutes".

---

## `GET /long_short_ratio/get_coin`

| | |
|---|---|
| Name | 每幣多空比 Long/Short Ratio by Coin |
| Group | Crypto › Raw data › Long/short ratio |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Last 7 days, hourly + the latest 5-minute point |
| Update | 5-minute buckets (Gate / OKX land ≈ 10 min late) |
| Source | Blave (Binance, OKX, Gate.io, Bybit long/short-ratio feeds) |

One coin, all ten sources: the latest 5-minute value of each, a 7-day hourly series per
source, and the Binance perp close on the same frame.

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | `BTC`, `BTCUSDT`, `btc` (≤ 32 chars) | Coin. The quote suffix is stripped; the response `symbol` is the normalised coin name |

**Response** — `{"data": {"latest", "series", "sources", "symbol", "token_id", "updated_at"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `latest.<source key>` | object / null | — | `{value, ts}` — that source's newest 5-minute sample; `null` when the source does not list the coin |
| `series.bucket_seconds` / `.days` | int | s / d | `3600` / `7` |
| `series.timestamp` | int[] | epoch s | **168 slots**, oldest → newest, one per hour |
| `series.<source key>` | float[] / null | ratio | Last sample of each hour; `null` for an hour with no sample. The whole field is a single `null` (not an array) for a source that does not list the coin |
| `series.price` | float[] / null | USD | Binance perp close on the same frame. A single `null` (with `price_symbol` / `price_multiplier` also `null`) when the coin has no Binance perp |
| `series.price_symbol` / `.price_multiplier` | string / int | — | Which perp the price came from and its contract multiplier (`1000PEPEUSDT` → `1000`; `price ÷ price_multiplier` = price per coin) |
| `series.provisional_from` | int / null | epoch s | First slot that can still change (sources finalise up to ~10 min late); `null` when no source has data |
| `sources[]` | object[] | — | The full roster, same fields as the table plus `listed` |
| `sources[].listed` | bool | — | `false` = that exchange has no such feed for this coin; its `latest` and `series` entries are `null` |
| `symbol` / `token_id` / `updated_at` | — | — | As in the table |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "symbol is required"}` | `symbol` missing, blank, over 32 chars, or nothing left after the quote suffix is stripped |
| 404 | `{"error": "<SYMBOL> is not a collected symbol"}` | No source collects the coin — an answer, not a transient |
| 503 | `{"error": "long short ratio data unavailable"}` | A listed source could not be read. `null` only ever means "that venue does not list it" |

**Example**

```python
params = {"symbol": "BTC"}
data = requests.get(f"{BASE_URL}/long_short_ratio/get_coin", headers=headers, params=params, timeout=30).json()["data"]
latest = data["latest"]["binance_top_position"]  # null when Binance does not list the coin
if latest is not None:
    r = latest["value"]
    print("top-trader long share:", round(r / (1 + r), 4))
# Live capture 2026-09-22 (abridged with ...; anonymous studio twin, same inner shape):
# {"latest": {"binance_account": {"ts": "2026-09-22T05:50:00+00:00", "value": 0.8818},
#             "binance_top_account": {"ts": "2026-09-22T05:50:00+00:00", "value": 1.0149}, ... 10 keys},
#  "series": {"bucket_seconds": 3600, "days": 7, "price_symbol": "BTCUSDT", "price_multiplier": 1,
#             "provisional_from": 1790053200,
#             "timestamp": [..., 1790049600, 1790053200],
#             "binance_account": [..., 0.8699, 0.8818], "price": [..., 85424.7, 85495.8], ... one array per source},
#  "sources": [{"exchange": "binance", "key": "binance_account", "last_at": "2026-09-22T05:50:00+00:00",
#               "listed": true, "stale": false, "type": "account"}, ... 10 rows],
#  "symbol": "BTC", "token_id": 1, "updated_at": "2026-09-22T05:50:00+00:00"}
```

**Notes**
- The cross-exchange "top trader" caveat on `/long_short_ratio/get_table` applies here too.
- 7 days is the whole history this endpoint serves; there is no `start_date` / `end_date`.
- **About the "anonymous studio twin" in every capture on this page's raw-data endpoints:** the
  studio pages (`/studio/charts/...`) serve the same payload from the same builder without a key,
  which is where these examples were taken. They are not a substitute for the API-key endpoints:
  the tables are cut to 30 coins (`full: false`), and a coin outside the studio whitelist answers
  `403 {"error_code": "ERR001", ..., "anon_whitelist": [...]}` instead of data. The API-key
  endpoints documented here have no whitelist and no row cut.

---

## `GET /oi_imbalance/get_table`

| | |
|---|---|
| Name | 未平倉量總表 Open Interest Table |
| Group | Crypto › Raw data › Open interest |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot (latest cross-section, with 1 h / 4 h / 24 h changes) |
| Update | Built by a scheduled job, ≈ every 15 minutes (5-minute source buckets; Gate / OKX land ≈ 10 min late) |
| Source | Blave (Binance, OKX, BingX, Bybit, Gate.io open-interest feeds) |

Every collected coin × five exchanges, in USD notional. **Basis: USDT-margined
perpetuals only, USD notional, one side.** An exchange that reports both sides is halved
(`exchanges[].side_factor`, Gate.io = 0.5). Because every value is already USD notional,
multiplied contracts (`1000PEPE` and friends) add across exchanges with no rescaling.

**Parameters** — none.

**Response** — `{"data": {"coins", "exchanges", "total", "summary", "tokens_shown", "tokens_total", "full", "updated_at"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `coins[].token` / `.token_id` | string / int | — | Coin |
| `coins[].oi_total` | float | USD | Summed across the five exchanges |
| `coins[].chg_1h` / `.chg_4h` / `.chg_24h` | float / null | fraction | Decimal change (`0.0675` = +6.75 %). Each window counts **only the exchanges that have a baseline at that window's start**, numerator and denominator over the same set; `null` when none does |
| `coins[].market_cap` | float / null | USD | CoinMarketCap market cap; `null` when there is no usable one |
| `coins[].oi_mcap` | float / null | ratio | `oi_total ÷ market_cap`; `null` when `market_cap` is |
| `coins[].by_exchange` | object | — | `{exchange: {oi, chg_1h, chg_4h, chg_24h}}`, one key per exchange; `null` when the coin is not listed there. A per-window `null` means that exchange had no baseline that far back — a feed younger than the window |
| `exchanges[]` | object[] | — | `binance`, `okx`, `bingx`, `bybit`, `gate` — whole-market `oi`, `side_factor`, `since`, `full_7d`, `last_at`, `stale` |
| `exchanges[].since` / `.full_7d` | string / bool | date | The feed's first day when it has under 7 days of history (`full_7d: false`), else `null` / `true`. Informational on this table (it has no 7-day window); on `/oi_imbalance/get_coin` such a feed has no 7 d baseline and is left out of `series.total` |
| `total` | object | — | Whole-market `oi`, `chg_1h/4h/24h`, `n_exchanges`, `n_full_7d` |
| `summary.oi_mcap_leader` / `_value` | string / float | — | Highest OI ÷ market cap among the top 100 coins by OI |
| `tokens_shown` / `tokens_total` / `full` / `updated_at` | — | — | As in the long/short-ratio table |

**Not the same number as the OI 失衡 indicator.** `/oi_imbalance/get_overview_data` (and the
`oi_imbalance` alpha behind screener conditions and alerts) is a **three-exchange**
aggregate — Binance + OKX + BingX. This table is five exchanges on the basis above. The two
`oi_total` values differ, so a threshold tuned on one does not carry over to the other.

**Errors**

| Status | Body | When |
|---|---|---|
| 503 | `{"error": "open interest data unavailable"}` | The job has no fresh result (missing or over an hour old) — never a table of zeros |

**Example**

```python
data = requests.get(f"{BASE_URL}/oi_imbalance/get_table", headers=headers, timeout=30).json()["data"]
crowded = sorted((c for c in data["coins"] if c["oi_mcap"] is not None), key=lambda c: -c["oi_mcap"])[:10]
print(data["total"]["oi"], [(c["token"], round(c["oi_mcap"], 4)) for c in crowded])
# Live capture 2026-09-22 (abridged with ...; anonymous studio twin, same inner shape):
# {"coins": [{"token": "BTC", "token_id": 1, "oi_total": 18645450917.48, "chg_1h": -0.001775,
#             "chg_4h": -0.001046, "chg_24h": 0.128725, "market_cap": 1629947967503.241, "oi_mcap": 0.011439,
#             "by_exchange": {"binance": {"oi": 9417422808.02, "chg_1h": 2e-05, "chg_4h": 0.010203, "chg_24h": 0.067527},
#                             "bingx": {"oi": 1328003926.8, ...},
#                             "bybit": {"oi": 2569097877.96, "chg_1h": -0.008636, "chg_4h": -0.030159, "chg_24h": null},
#                             "gate": {...}, "okx": {"oi": 2575361192.92, ..., "chg_24h": null}}}, ...],
#  "exchanges": [{"key": "binance", "oi": 24712717530.01, "side_factor": 1.0, "since": null, "full_7d": true,
#                 "last_at": "2026-09-22T05:25:00+00:00", "stale": false}, ... 5 rows],
#  "total": {"oi": 47428938620.05, "chg_1h": -0.008919, "chg_4h": -0.010508, "chg_24h": 0.073881,
#            "n_exchanges": 5, "n_full_7d": 3},
#  "summary": {"oi_mcap_leader": "SAGA", "oi_mcap_leader_value": 1.718336},
#  "tokens_shown": 30, "tokens_total": 622, "full": false, "updated_at": "2026-09-22T05:30:00+00:00"}
```

**Collection start** (first stored bucket, measured on BTC 2026-09-22)

| Exchange | Collecting since |
|---|---|
| `binance` | 2021-12-01 |
| `bingx` | 2025-04-15 |
| `gate` | 2026-08-12 |
| `okx` | 2026-09-21 |
| `bybit` | 2026-09-21 |

OKX and Bybit are why `n_full_7d` is 3 of 5 and why their `chg_24h` was still `null` on
2026-09-22 — read `exchanges[].since` / `full_7d` rather than these dates, which age out.

**Notes**
- `chg_24h: null` on OKX / Bybit in the capture above is the young-feed rule, not a gap in the
  market: those two started on 2026-09-21, so they had no 24 h baseline yet.
- A cross-section, not history. One coin's last 7 days (hourly, all five exchanges) is
  `/oi_imbalance/get_coin`; backtest-length history for one coin on one exchange is
  `/oi_imbalance/get_history`.

---

## `GET /oi_imbalance/get_coin`

| | |
|---|---|
| Name | 每幣未平倉量 Open Interest by Coin |
| Group | Crypto › Raw data › Open interest |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Last 7 days, hourly + current values |
| Update | 5-minute buckets (Gate / OKX land ≈ 10 min late) |
| Source | Blave (Binance, OKX, BingX, Bybit, Gate.io open-interest feeds) |

One coin's open interest per exchange, on the same basis as the table: current value and
share, four change windows with the exchanges each counted, and a 7-day hourly total line.

**Parameters** — `symbol`, exactly as in `/long_short_ratio/get_coin`.

**Response** — `{"data": {"exchanges", "windows", "series", "oi_total", "market_cap", "oi_mcap", "oi_mcap_rank", "tokens_total", "symbol", "token_id", "updated_at"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `exchanges[]` | object[] | — | The full five-exchange roster: `key`, `oi` (USD), `share` (of `oi_total`), `chg_1h/4h/24h/7d`, `side_factor`, `listed`, `since`, `full_7d`, `last_at`, `stale` |
| `exchanges[].listed` | bool | — | `false` = the coin is not listed there; its values are `null` |
| `oi_total` / `market_cap` / `oi_mcap` | float | USD / ratio | As in the table |
| `oi_mcap_rank` / `tokens_total` | int / null | — | Rank by `oi_mcap` in the table job's last round; `null` when that job has no fresh result |
| `windows.<1h\|4h\|24h\|7d>.chg` / `.chg_usd` | float / null | fraction / USD | Change of the counted exchanges' total |
| `windows.<w>.exchanges` | string[] | — | **Which exchanges were counted in that window** — a young feed is absent, so 24 h / 7 d can count fewer exchanges than 1 h |
| `series.timestamp` | int[] | epoch s | 168 hourly slots, oldest → newest |
| `series.total` | float[] / null | USD | Total OI per slot — **only the `series.total_exchanges` (the `full_7d` feeds) are in this line**, so it is not comparable in level to `oi_total`. A slot is `null` when any of those exchanges has no sample that hour; the whole field is `null` when no exchange is `full_7d` for the coin |
| `series.total_exchanges` | string[] | — | Which exchanges the line adds up |
| `series.price` / `.price_symbol` / `.price_multiplier` / `.provisional_from` | — | — | As in `/long_short_ratio/get_coin` |

**Errors** — `400` / `404` / `503` exactly as `/long_short_ratio/get_coin`, with
`{"error": "open interest data unavailable"}` on 503.

**Example**

```python
data = requests.get(f"{BASE_URL}/oi_imbalance/get_coin", headers=headers, params={"symbol": "BTC"}, timeout=30).json()["data"]
day = data["windows"]["24h"]
print(data["oi_total"], day["chg"], "counted:", day["exchanges"])
# Live capture 2026-09-22 (abridged with ...; anonymous studio twin, same inner shape):
# {"exchanges": [{"key": "binance", "oi": 9454606424.48, "share": 0.5055, "chg_1h": 0.00037, "chg_4h": 0.014471,
#                 "chg_24h": 0.064607, "chg_7d": 0.17205, "side_factor": 1.0, "listed": true, "since": null,
#                 "full_7d": true, "last_at": "2026-09-22T05:50:00+00:00", "stale": false},
#                {"key": "okx", ..., "since": "2026-09-21", "full_7d": false}, ... 5 rows],
#  "windows": {"1h": {"chg": -0.000462, "chg_usd": -8636171.48, "exchanges": ["binance", "okx", "bingx", "bybit", "gate"]},
#              "4h": {...},
#              "24h": {"chg": 0.12231, "chg_usd": 1474912315.85, "exchanges": ["binance", "bingx", "gate"]},
#              "7d": {"chg": 0.212184, "chg_usd": 2368974857.56, "exchanges": ["binance", "bingx", "gate"]}},
#  "series": {"bucket_seconds": 3600, "days": 7, "timestamp": [1789452000, 1789455600, ...],
#             "total": [11171863169.89, 11167043101.84, ...], "total_exchanges": ["binance", "bingx", "gate"],
#             "price": [...], "price_symbol": "BTCUSDT", "price_multiplier": 1, "provisional_from": 1790053200},
#  "oi_total": 18704068031.08, "market_cap": 1629947967503.241, "oi_mcap": 0.011475, "oi_mcap_rank": 580,
#  "tokens_total": 622, "symbol": "BTC", "token_id": 1, "updated_at": "2026-09-22T05:55:00+00:00"}
```

**Notes**
- `windows["1h"]["exchanges"]` having five entries while `windows["24h"]` has three is the
  young-feed rule, not missing data — read that list before comparing windows.
- The OI 失衡 caveat from `/oi_imbalance/get_table` applies to this `oi_total` too.
- Seven days only. For a longer series to backtest on, use `/oi_imbalance/get_history` (one
  exchange, coins rather than USD — a different basis from `oi_total`).

---

## `GET /oi_imbalance/get_history`

| | |
|---|---|
| Name | 未平倉量歷史 Open Interest History |
| Group | Crypto › Raw data › Open interest |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 5-minute resolution — `binance` 2021-12-01, `bybit` 2025-08-21, `gate` 2026-03-28 (each: or the coin's listing date there, if later). Currently listed contracts only |
| Update | 5-minute buckets |
| Source | Blave (Binance, Bybit, Gate.io open-interest feeds; `close` from the Binance USDT-M perpetual) |

One coin's open interest on **one exchange**, as a time series you can backtest on — the same
basis as the Studio dashboard 未平倉量 card. **`alpha` is one-sided open interest in coins, not
USD.** Multiplied contracts are converted back to coins (`1000PEPE` returns a PEPE count).
Each bucket is the last reading of its period — open interest is a stock, never summed.

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `symbol` | query | string | yes | — | `BTC`, `BTCUSDT`, `btc` | Coin, same rule as `/oi_imbalance/get_coin` |
| `period` | query | string | yes | — | `{n}min` / `{n}h` / `{n}d`, minimum `5min` (e.g. `5min`, `1h`, `4h`, `1d`) | Bucket size. `1w` is a `400` (unit not supported); `1m` is read as `1min`, so it is a `400` for being below `5min` |
| `start_date` | query | string | no | `end_date` − 365 days | `YYYY-MM-DD` (UTC) | First day, inclusive |
| `end_date` | query | string | no | today | `YYYY-MM-DD` (UTC) | Last day, inclusive |
| `oi_exchange` | query | string | no | `binance` | `binance`, `bybit`, `gate` (case-insensitive) | Whose open interest to read |

Per-request window: at most 365 days; a longer range is **silently clamped** (`start_date`
moved to `end_date` − 365 days, no error), as in `/kline`.

**Response** — `{"data": {"timestamp", "alpha", "close", "exchanges"}}`, parallel arrays, oldest → newest.

| Field | Type | Unit | Description |
|---|---|---|---|
| `timestamp` | float[] | Unix seconds (UTC) | Bucket start |
| `alpha` | float[] | coins | One-sided open interest on `oi_exchange`, last reading of the bucket |
| `close` | float[] | USDT | Binance USDT-M perpetual price — per contract unit, so per 1000 coins for `1000PEPE` |
| `exchanges` | string[] | — | The exchange actually read, e.g. `["binance"]` |

**`alpha × close` is not USD open interest on a multiplied contract.** `close` there is the
price per contract unit (per 1000 coins for `1000PEPE`) while `alpha` is in single coins — divide `close` by the multiplier
first. For non-multiplied contracts such as BTC, `alpha × close` ≈ USD open interest.

**Gate.io: always send `start_date` ≥ `2026-03-28`** — the default window (`end_date` − 365 days)
starts before Gate's history and is a `400`.

**Not the same number as `/oi_imbalance/get_table` / `get_coin`** (five exchanges summed, USD)
**and not the OI 失衡 indicator** (`/oi_imbalance/get_overview_data`).

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "symbol is required"}` / `{"error": "period is required"}` | Missing (a `400` here, not the `403` of the indicator endpoints) |
| 400 | `{"error": "period must be at least 5min, in min / h / d units"}` | `period` below `5min` (including `1m`, read as `1min`) or in a unit other than min / h / d (`1w`) |
| 400 | `{"error": "invalid date format, expected YYYY-MM-DD"}` | Malformed `start_date` / `end_date` |
| 400 | `{"error": "start_date must not be after end_date"}` | `start_date` > `end_date` |
| 400 | `{"error": "oi_exchange must be one of binance, bybit, gate"}` | `oi_exchange` outside the list |
| 400 | `{"error": "no <exchange> open interest for <TOKEN> at start_date; this exchange's history may start later — try a later start_date"}` | The window starts before that exchange's history (see *Data from*). **Without `start_date`, `oi_exchange=gate` always hits this** until its history passes 365 days (≈ 2027-03) — for Gate always send `start_date` ≥ `2026-03-28` |
| 404 | `{"error": "<TOKEN> is not a collected symbol on <exchange>"}` | That exchange does not list the coin, the coin has no Binance perpetual, or it is delisted — an answer, not a transient |
| 503 | `{"error": "<exchange> open interest data unavailable for <TOKEN>"}` | Data could not be read right now — retry |

**Example**

```python
params = {"symbol": "BTC", "period": "1d", "start_date": "2022-01-01", "end_date": "2022-01-03"}
data = requests.get(f"{BASE_URL}/oi_imbalance/get_history", headers=headers, params=params, timeout=120).json()["data"]
# Live capture 2026-10-02:
# {"data": {"alpha": [72913.725, 73310.482, 79515.424], "close": [47704.35, 47280.0, 46445.81],
#           "exchanges": ["binance"], "timestamp": [1640995200.0, 1641081600.0, 1641168000.0]}}

params = {"symbol": "SOL", "period": "4h", "oi_exchange": "bybit", "start_date": "2026-09-30", "end_date": "2026-09-30"}
# {"data": {"alpha": [3443506.2, 3344470.1, 3269534.6, 3108222.6, 3082040.9, 3042368.1],
#           "close": [119.08, 118.41, 119.47, 119.25, 117.17, 118.05], "exchanges": ["bybit"],
#           "timestamp": [1790726400.0, 1790740800.0, 1790755200.0, 1790769600.0, 1790784000.0, 1790798400.0]}}

params = {"symbol": "1000PEPE", "period": "1d", "start_date": "2026-09-01", "end_date": "2026-09-02"}
# alpha is PEPE coins; close is per 1000 PEPE, so USD OI = alpha × close / 1000
# {"data": {"alpha": [19073240707000.0, 17615934147000.0], "close": [0.0034752, 0.0034306],
#           "exchanges": ["binance"], "timestamp": [1788220800.0, 1788307200.0]}}
```

**Notes**
- `200` with empty arrays means no bucket in that window (e.g. the coin listed after it) — do
  not cache it as a permanent "no data".
- The last bucket keeps moving until its period closes when `end_date` is today.
- For history beyond 365 days, send one request per year and concatenate.

---

## `GET /taker_intensity/get_cvd_table`

| | |
|---|---|
| Name | 主動買賣淨額總表 CVD Table |
| Group | Crypto › Raw data › CVD |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Snapshot (rolling 1 h / 4 h / 24 h windows) |
| Update | Built by a scheduled job, ≈ every 15 minutes (5-minute source buckets; Gate / OKX land ≈ 10 min late) |
| Source | Blave (Binance, OKX, Gate.io taker-flow feeds) |

Taker (market-order) buy and sell turnover per coin, in USD, across **three exchanges**:
Binance from the 5-minute kline's taker-buy quote volume (sell = the bar's total minus it),
OKX from its USD taker volume, Gate.io from taker contracts × the same row's multiplier and
mark price. **Perpetuals only — no spot — and aggregated from 5-minute bars, not from
trade-by-trade prints.** Each exchange's own reported turnover is used; volume is never
multiplied by a price borrowed from another venue.

**Parameters** — none.

**Response** — `{"data": {"coins", "exchanges", "total", "tokens_shown", "tokens_total", "full", "updated_at"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `coins[].token` / `.token_id` | string / int | — | Coin |
| `coins[].buy_24h` / `.sell_24h` | float / null | USD | Taker buy / sell turnover over the rolling 24 h, summed over the coin's non-stale exchanges; `null` when all of them are stale |
| `coins[].net_1h` / `.net_4h` / `.net_24h` | float / null | USD | `buy − sell` over each rolling window (same `null` rule) |
| `coins[].by_exchange` | object | — | `{exchange: {buy_24h, sell_24h, net_1h, net_4h, net_24h}}`, one key per exchange; `null` when the coin is not listed there or that exchange's data for it is stale |
| `exchanges[]` | object[] | — | `binance`, `okx`, `gate` — whole-market `buy_24h`, `sell_24h`, `net_24h`, `last_at`, `stale` |
| `exchanges[].stale` | bool | — | That feed's last bar is over an hour old: its windows come back `null` and it is **left out of the totals** rather than contributing a sum that silently covers less than the window |
| `total` | object | USD | Whole-market `buy_24h`, `sell_24h`, `net_24h` over the fresh exchanges |
| `tokens_shown` / `tokens_total` / `full` / `updated_at` | — | — | As in the other raw tables |

**Errors**

| Status | Body | When |
|---|---|---|
| 503 | `{"error": "cvd data unavailable"}` | The job has no fresh result — never zeros |

**Example**

```python
data = requests.get(f"{BASE_URL}/taker_intensity/get_cvd_table", headers=headers, timeout=30).json()["data"]
buying = sorted((c for c in data["coins"] if c["net_24h"] is not None), key=lambda c: -c["net_24h"])[:10]
print(data["total"]["net_24h"], [(c["token"], c["net_24h"]) for c in buying])
# Live capture 2026-09-22 (abridged with ...; anonymous studio twin, same inner shape):
# {"coins": [{"token": "BTC", "token_id": 1, "buy_24h": 24607245298.03, "sell_24h": 23128502231.73,
#             "net_1h": -212647361.27, "net_4h": -207128163.51, "net_24h": 1478743066.31,
#             "by_exchange": {"binance": {"buy_24h": 12663681424.94, "sell_24h": 12135756153.44,
#                                         "net_1h": -191133129.94, "net_4h": -217337267.5, "net_24h": 527925271.5},
#                             "gate": {...}, "okx": {...}}}, ...],
#  "exchanges": [{"key": "binance", "buy_24h": 34978603608.55, "sell_24h": 35112588381.38,
#                 "net_24h": -133984772.74, "last_at": "2026-09-22T05:25:00+00:00", "stale": false}, ... 3 rows],
#  "total": {"buy_24h": 63543431942.93, "sell_24h": 62491177680.21, "net_24h": 1052254262.8},
#  "tokens_shown": 30, "tokens_total": 591, "full": false, "updated_at": "2026-09-22T05:25:00+00:00"}
```

**Collection start** (first stored bucket, measured on BTC 2026-09-22)

| Exchange | Source field | Collecting since |
|---|---|---|
| `binance` | 5-minute `kline` (taker-buy quote volume) | 2020-01-01 |
| `gate` | `contract_stats` | 2026-08-12 |
| `okx` | `taker_volume_usd` | 2026-09-21 |

OKX is additionally capped by the venue keeping only 5 days, so it stays `full_7d: false`
until a week after that date. This table carries no `since` / `full_7d` (it has no 7-day
window) — read them per coin from `/taker_intensity/get_cvd_coin`'s `exchanges[]`, not from these dates.

**Notes**
- Not the same as the `taker_intensity` alpha (`/taker_intensity/get_alpha`), which is a
  normalised z-score-like signal with years of history. This is raw USD turnover, now.
- Windows are rolling and end at the last closed 5-minute bar, so `net_24h` is not a calendar day.

---

## `GET /taker_intensity/get_cvd_coin`

| | |
|---|---|
| Name | 每幣主動買賣淨額 CVD by Coin |
| Group | Crypto › Raw data › CVD |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Last 7 days, hourly + rolling windows |
| Update | 5-minute buckets (Gate / OKX land ≈ 10 min late) |
| Source | Blave (Binance, OKX, Gate.io taker-flow feeds) |

One coin's taker buy / sell / net per exchange (same basis as the table) plus a 7-day
hourly net and its running cumulative — the CVD line itself.

**Parameters** — `symbol`, exactly as in `/long_short_ratio/get_coin`.

**Response** — `{"data": {"exchanges", "windows", "series", "symbol", "token_id", "updated_at"}}`.

| Field | Type | Unit | Description |
|---|---|---|---|
| `windows.<1h\|4h\|24h\|7d>` | object | USD | `{buy, sell, net}` summed over the fresh exchanges |
| `exchanges[]` | object[] | — | The full roster: `key`, `listed`, `windows` (same four, per exchange), `since`, `full_7d`, `last_at`, `stale` |
| `exchanges[].full_7d` | bool | — | `false` = under 7 days of history for this coin there: its 7 d window is `null` and it is excluded from the 7 d total **and from the series**. OKX keeps only 5 days, so it is `false` until a week after the feed's start |
| `series.timestamp` | int[] | epoch s | 168 hourly slots, oldest → newest |
| `series.net` | float[] | USD | Net taker flow per clock hour, summed over `series.exchanges`; `null` for an hour with no data. When `series.exchanges` is empty every slot is `null` and `cvd` stays flat at 0 — the line carries no information then |
| `series.cvd` | float[] | USD | Running total of `net`; **`cvd[0] = 0`** — the line is a shape, not an absolute level |
| `series.exchanges` | string[] | — | Which exchanges the line adds up |
| `series.price` / `.price_symbol` / `.price_multiplier` / `.provisional_from` | — | — | As in `/long_short_ratio/get_coin` |

**Errors** — `400` / `404` / `503` exactly as `/long_short_ratio/get_coin`, with
`{"error": "cvd data unavailable"}` on 503.

**Example**

```python
data = requests.get(f"{BASE_URL}/taker_intensity/get_cvd_coin", headers=headers, params={"symbol": "BTC"}, timeout=30).json()["data"]
print(data["windows"]["24h"]["net"], "line covers:", data["series"]["exchanges"], "last cvd:", data["series"]["cvd"][-1])
# Live capture 2026-09-22 (abridged with ...; anonymous studio twin, same inner shape):
# {"exchanges": [{"key": "binance", "listed": true, "since": null, "full_7d": true, "stale": false,
#                 "last_at": "2026-09-22T05:50:00+00:00",
#                 "windows": {"1h": {"buy": 334079345.8, "sell": 432484304.99, "net": -98404959.2},
#                             "4h": {...}, "24h": {"buy": 12764594401.23, "sell": 12156150828.71, "net": 608443572.52},
#                             "7d": {"buy": 48395824125.78, "sell": 48033568140.24, "net": 362255985.54}}},
#                {"key": "okx", "full_7d": false, "since": "2026-09-21", ...}, {"key": "gate", ...}],
#  "windows": {"1h": {"buy": 661443769.03, "sell": 760343818.66, "net": -98900049.65}, "4h": {...},
#              "24h": {"buy": 24795988390.84, "sell": 23206873390.07, "net": 1589115000.77},
#              "7d": {"buy": 69832361511.62, "sell": 68794205279.31, "net": 1038156232.31}},
#  "series": {"bucket_seconds": 3600, "days": 7, "timestamp": [1789452000, 1789455600, ...],
#             "net": [-53629060.26, -75636445.35, ...], "cvd": [0.0, -75636445.35, ...],
#             "exchanges": ["binance", "gate"], "price": [...], "price_symbol": "BTCUSDT",
#             "price_multiplier": 1, "provisional_from": 1790053200},
#  "symbol": "BTC", "token_id": 1, "updated_at": "2026-09-22T05:50:00+00:00"}
```

**Notes**
- `series.exchanges` being shorter than `exchanges[]` is the `full_7d` rule — compare the series
  against itself, not against `windows["24h"]`, which counts more venues.
- `cvd[0] = 0` by construction: only the slope and the turning points carry information.

---

## `GET /cme_cot/get_latest`

| | |
|---|---|
| Name | CME 比特幣／以太幣期貨持倉報告 CME Bitcoin / Ether Futures Commitments of Traders (latest) |
| Group | Crypto › Raw data › CME positioning |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Latest report only (history: `/cme_cot/get_history`) |
| Update | Weekly — positions as of Tuesday (Monday when Tuesday is a US holiday), published by CFTC on that week's Friday 15:30 US Eastern; a federal holiday Wed–Fri moves it to the next business day, a government shutdown delays it by weeks; server cache 1 h |
| Source | U.S. CFTC Commitments of Traders, futures only — Traders in Financial Futures (TFF) + Legacy reports |

The latest weekly CFTC row for each of the four CME crypto futures, plus standard + micro summed
in coins per asset. Same shape as one row of `/cme_cot/get_history`, without `price`.

**Parameters** — none.

**Response** — `{"data": {"contracts": [...], "combined": [...], "report", "units", "source", "source_updated", "fetched_at", "stale"}}`

| Field | Description |
|---|---|
| `contracts[]` | One per contract: `key` (`btc`, `micro_btc`, `eth`, `micro_eth`), `name`, `cftc_code`, `coin`, `coin_per_contract` (5 / 0.1 / 50 / 0.1), `latest` (a row, see `get_history`; `null` if the contract has no rows) |
| `combined[]` | `btc_combined`, `eth_combined`: `name`, `coin`, `components`, `units`, `micro_since`, `note`, `latest` (a combined row, in coins) |
| `report` | `futures_only` |
| `units` | Unit of `contracts[].latest` positions: contracts (× `coin_per_contract` for coins) |
| `source` | CFTC attribution line — show it with any figure you publish |
| `source_updated` | When CFTC last updated the dataset |
| `fetched_at` | When Blave fetched it (UTC) |
| `stale` | `true` = CFTC was unreachable and the last stored copy is served |

**Errors**

| Status | Body | When |
|---|---|---|
| 503 | `{"error": "CFTC data unavailable. Please retry shortly."}` | CFTC unreachable and no stored copy |

**Example**

```python
data = requests.get(f"{BASE_URL}/cme_cot/get_latest", headers=headers, timeout=60).json()["data"]
btc = next(c for c in data["contracts"] if c["key"] == "btc")
# Live capture 2026-10-07 (abridged):
# {"key": "btc", "name": "Bitcoin Futures (CME)", "cftc_code": "133741", "coin": "BTC", "coin_per_contract": 5,
#  "latest": {"date": "2026-09-29", "open_interest": 19596, "open_interest_change": -2719,
#             "tff": {"leveraged_funds": {"long": 4980, "short": 11836, "spread": 538, "net": -6856,
#                                         "long_change": 235, "short_change": -862, "spread_change": -2187, "net_change": 1097},
#                     "asset_manager": {"long": 5069, "short": 1483, "spread": 297, "net": 3586, ...}, ...},
#             "legacy": {"non_commercial": {...}, "commercial": {...}, "nonreportable": {...}}}}
# data["source_updated"] == "Fri, 02 Oct 2026 19:30:08 GMT", data["stale"] == False
```

---

## `GET /cme_cot/get_history`

| | |
|---|---|
| Name | CME 比特幣／以太幣期貨持倉報告歷史 CME Bitcoin / Ether Futures Commitments of Traders (history) |
| Group | Crypto › Raw data › CME positioning |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | `btc` 2018-04-10, `micro_btc` 2021-05-04, `eth` 2021-04-06, `micro_eth` 2021-12-14 (CME's own BTC futures enter the COT on 2018-04-10, not at their 2017-12 launch) |
| Update | Weekly — positions as of Tuesday (Monday when Tuesday is a US holiday), published by CFTC on that week's Friday 15:30 US Eastern; a federal holiday Wed–Fri moves it to the next business day, a government shutdown delays it by weeks; server cache 1 h |
| Source | U.S. CFTC Commitments of Traders, futures only — TFF + Legacy reports; `price` = Binance spot UTC daily close |

One contract's weekly positioning by trader category. Rows are dated by the report date — the
day the positions are as of, usually a Tuesday (a Monday when Tuesday is a US holiday). **The data
became public later**: normally that week's Friday 15:30 ET; a federal holiday Wednesday–Friday
moves the release to the next business day, and a government shutdown delays it by weeks (the
2018-12-24 … 2019-02-26 reports came out 2019-02-01 … 03-05; the 2025-09-30 … 2026-01-20 reports
2025-11-19 … 2026-01-23 — CFTC Releases 7864-19 and 9138-25). A backtest must not act on a row
before its release.

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `contract` | query | string | no | `btc` | `btc`, `micro_btc`, `eth`, `micro_eth`, `btc_combined`, `eth_combined` (case-insensitive) | Single contracts are in **contracts**; `*_combined` = standard + micro summed in **coins** |
| `start_date` | query | string | no | today (UTC) − 365 days | `YYYY-MM-DD` | First report date, inclusive. **Omitted = last year only — pass an early date (e.g. `2018-01-01`) for full history** |
| `end_date` | query | string | no | latest | `YYYY-MM-DD` | Last report date, inclusive |

**Response** — `{"data": {"contract": {...}, "rows": [...], "price_source", "report", "units", "source", "source_updated", "fetched_at", "stale"}}`, rows oldest → newest.

`contract`: `key`, `name`, `coin`, and `cftc_code` + `coin_per_contract` (single contract) or
`components` + `micro_since` + `note` (combined).

Each row:

| Field | Type | Description |
|---|---|---|
| `date` | string | Report date — usually a Tuesday, a Monday when Tuesday is a US holiday |
| `open_interest` / `open_interest_change` | number | Total open interest and its week-over-week change |
| `tff` | object | Groups `dealer`, `asset_manager`, `leveraged_funds`, `other_reportables`, `nonreportable` |
| `legacy` | object \| null | Groups `non_commercial`, `commercial`, `nonreportable`; `null` if CFTC has no Legacy row for that week |
| `price` | float \| null | Binance spot `BTCUSDT` / `ETHUSDT` UTC daily close on the report date; `null` when unavailable |
| `included` | string[] | Combined contracts only: which contracts this row sums (`["btc"]` before `micro_since`) |

Each group: `long`, `short`, `spread` (not for `nonreportable` / `commercial`), `net` (= long − short),
and `long_change`, `short_change`, `spread_change`, `net_change`. Units: contracts for a single
contract, coins for a combined one. The `*_change` fields are **CFTC's own** week-over-week
figures, not row-to-row differences — CFTC skips weeks (e.g. government shutdowns), so never diff
rows yourself.

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "contract must be one of btc, micro_btc, eth, micro_eth, btc_combined, eth_combined"}` | Unknown contract |
| 400 | `{"error": "Invalid start_date, expected YYYY-MM-DD"}` (or `end_date`) / `{"error": "start_date must not be after end_date"}` | Bad date / reversed range |
| 503 | `{"error": "CFTC data unavailable. Please retry shortly."}` | CFTC unreachable and no stored copy |

**Example**

```python
data = requests.get(f"{BASE_URL}/cme_cot/get_history", headers=headers,
                    params={"contract": "btc_combined", "start_date": "2026-09-01"}, timeout=60).json()["data"]
lev_net = {r["date"]: r["tff"]["leveraged_funds"]["net"] for r in data["rows"]}   # BTC
# Live capture 2026-10-07 (abridged): 5 rows 2026-09-01 … 2026-09-29
# {"contract": {"key": "btc_combined", "name": "Bitcoin + Micro Bitcoin Futures (CME), in BTC", "coin": "BTC",
#               "components": ["btc", "micro_btc"], "micro_since": "2021-05-04", "units": "coins (...)", "note": "..."},
#  "rows": [..., {"date": "2026-09-29", "included": ["btc", "micro_btc"], "price": 83663.66,
#                 "open_interest": 100612.0, "open_interest_change": -14522.7,
#                 "tff": {"leveraged_funds": {"long": 25889.6, "short": 61305.6, "spread": 2742.4, "net": -35416.0,
#                                             "long_change": 680.4, "short_change": -4283.9,
#                                             "spread_change": -11214.8, "net_change": 4964.3},
#                         "asset_manager": {"long": 25570.8, "short": 7421.7, "net": 18149.1, ...},
#                         "dealer": {"net": 13483.9, ...}, "other_reportables": {...}, "nonreportable": {...}},
#                 "legacy": {"non_commercial": {"net": 11754.9, ...}, "commercial": {"net": -13695.5, ...},
#                            "nonreportable": {...}}}],
#  "price_source": "Binance spot BTCUSDT, UTC daily close on the report date (Tuesday)",
#  "report": "futures_only", "source": "Source: U.S. Commodity Futures Trading Commission (CFTC), ...",
#  "source_updated": "Fri, 02 Oct 2026 19:30:08 GMT", "fetched_at": "2026-10-07T09:16:35Z", "stale": false}
```

**Notes**
- `*_combined` has a break at `micro_since`: the week micro joins, the totals step up and that
  week's `*_change` includes micro's whole first position. Start a combined backtest after
  `micro_since`, or use the single `btc` / `eth` contract.
- Full BTC history is ~440 weekly rows (~0.5 MB) — one request, no paging.
- Licence: CFTC data is public domain, but CFTC asks to be acknowledged — keep `source` next to
  any figure you show. Not endorsed by the CFTC.
- Interpretation (leveraged funds net short ≠ bearish): `references/blave-indicator-guide.md` › CME 持倉報告.

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
| `market` | string | `TWSE` (上市) or `TPEx` (上櫃) |
| `industry_code` | string \| null | TWSE/TPEx raw numeric 產業別 code, passthrough (not decoded). `null` for ETFs / non-company securities. Common codes: `15` 航運業, `17` 金融保險業, `22` 生技醫療業, `24` 半導體業, `25` 電腦及週邊設備業, `26` 光電業, `27` 通信網路業, `28` 電子零組件業, `29` 電子通路業, `30` 資訊服務業, `31` 其他電子業 |
| `listing_date` | string \| null | `YYYY-MM-DD`; `null` for ETFs / non-company securities |

**Errors** — shared errors only (`500` if both markets fail).

**Example**

```python
data = requests.get(f"{BASE_URL}/studio/market/twstock/list", headers=headers, timeout=60).json()["data"]
# [{"stock_id": "00400A", "name": "主動國泰動能高息", "close": 14.72, "market": "TWSE",
#   "industry_code": None, "listing_date": None}, ...]   # 2,392 rows in this response
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
| Data from | 1994-10-01 — the floor the server asks upstream from. `2330` with no `start` / `end` returned 8,069 rows starting at exactly that floor. Codes listed later start later |
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
response = requests.get(f"{BASE_URL}/studio/market/twstock/price/2330", headers=headers, timeout=60)
data = response.json()["data"]   # no start/end → full history, 8,069 rows
# [{"date": "1994-10-01", "stock_id": "2330", "open": 171.0, "high": 172.0,
#   "low": 171.0, "close": 172.0, "spread": 1.0,
#   "volume": 1660506, "turnover_value": 284858008, "turnover_count": 684},
#  {"date": "1994-10-03", "stock_id": "2330", "open": 172.0, "high": 173.0,
#   "low": 171.0, "close": 172.0, "spread": 0.0,
#   "volume": 1560000, "turnover_value": 268084000, "turnover_count": 711}, ...]
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
| Data from | Same as `/price` — 1994-10-01 for `2330`, same 8,069 rows |
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
| `volume` | int | lots (張), not shares | Volume. Every `TAIEX` `1d` bar observed carried `volume: 0`, so index volume is effectively unavailable here — do not read it as a turnover figure（待確認：`TAIEX` 的 volume 單位） |

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

**Response** — `{"date": "YYYY-MM-DD", "twse_ex_etf_market_value": int, "data": [...]}`, sorted by market value descending.

| Field | Type | Description |
|---|---|---|
| `date` | string | As-of day actually used (latest published; can lag today by a day) |
| `twse_ex_etf_market_value` | int | TWD. Sum of the `market == "TWSE"` rows that are not ETFs, on the same as-of day. Whole-market denominator — **not** reduced by `top` |
| `data[].rank` | int | 1-based rank |
| `data[].stock_id` | string | Code |
| `data[].name` | string | Name |
| `data[].market` | string | `"TWSE"` (上市) or `"TPEx"` (上櫃), from the TWSE / TPEx listing rosters |
| `data[].market_value` | int | TWD |
| `data[].is_etf` | bool | `true` for the ETFs in the ranking (359 of 2,370 rows on 2026-09-17). `false` means "not in the ETF set", **not** "confirmed not an ETF": a security FinMind publishes no `industry_category` for — e.g. REIT `01010T` — is `false`, and it stays inside `twse_ex_etf_market_value` |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "top must be an integer between 1 and 3000"}` | Bad `top` |
| 404 | `{"error": "No recent market value data available"}` (or a listing-incomplete message) | No recent data |
| 503 | `{"error": "Upstream rate limit. Please retry shortly."}` | Upstream quota exhausted |

**Example**

```python
body = requests.get(f"{BASE_URL}/studio/market/twstock/market_value/all", headers=headers, params={"top": 10}, timeout=60).json()
# {"date": "2026-09-17", "twse_ex_etf_market_value": 150952470507848,
#  "data": [{"is_etf": false, "market": "TWSE", "market_value": 62885997412475,
#            "name": "台積電", "rank": 1, "stock_id": "2330"},
#           ...,
#           {"is_etf": true, "market": "TWSE", "market_value": 2383312875000,
#            "name": "元大台灣50", "rank": 6, "stock_id": "0050"}, ...]}

# Index weight of a 上市 non-ETF stock (works with any `top`, the denominator is whole-market)
row = body["data"][0]                                    # 2330 — market "TWSE", is_etf false
share = row["market_value"] / body["twse_ex_etf_market_value"]

# ETFs rank alongside stocks (0050 is rank 6) — filter them with `is_etf`. Never by code prefix,
# and never by re-fetching a classification: `is_etf` already IS that classification.
rows = requests.get(f"{BASE_URL}/studio/market/twstock/market_value/all", headers=headers, params={"top": 100}, timeout=60).json()["data"]
top50 = [r["stock_id"] for r in rows if not r["is_etf"]][:50]       # ETF-free market-cap top 50
tpex_only = [r["stock_id"] for r in rows if r["market"] == "TPEx"]   # board filter is exact
```

**Notes**
- Universe is 上市 + 上櫃 + ETF (興櫃 excluded; ETNs have no data). Use this instead of looping
  `/market_value/<stock_id>` for "top N by market cap" questions.
- **`rank` and `twse_ex_etf_market_value` are different universes.** `rank` is whole-market —
  上市 + 上櫃, ETFs included — and did not change when the denominator was added. The
  denominator is 上市 only and excludes ETFs (FinMind `industry_category` in
  `{ETF, 上櫃ETF, 上櫃指數股票型基金(ETF)}`); REITs and preferred shares are **not**
  excluded from it. So `market_value / twse_ex_etf_market_value` is an index weight only for a
  row whose `market` is `"TWSE"` and which is not an ETF — a TPEx or ETF row over this
  denominator is not a weight — while `rank` stays a whole-market rank. Don't read the two as
  one ranking.
- `market` is a listing-board tag, not an ETF flag — **`is_etf` is the ETF flag.** Use it for an
  ETF-free universe. Don't infer ETFs from the `stock_id` prefix (`00` is a market convention
  rather than a contract, and it misses REITs `01xxxT`) and don't re-fetch a classification from
  FinMind. `is_etf` is exactly the criterion `twse_ex_etf_market_value` is computed on, so an
  `is_etf` filter and the denominator can never disagree.

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
| Data from | 2013-01-01 is only the **default** `start`. Send an earlier `start` and earlier rows come back — `2330` with `start=2000-01-01` returned rows from 2000-06-30 |
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
| Data from | 2013-01-01 is only the **default** `start`. Send an earlier `start` and earlier rows come back — `2330` with `start=2000-01-01` returned rows from 2012-12-31 |
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
| Data from | 2013-01-01 is only the **default** `start`. Send an earlier `start` and earlier rows come back — `2330` with `start=2000-01-01` returned rows from 2012-03-31 |
| Update | Quarterly; server cache 24 h |
| Source | FinMind TaiwanStockCashFlowsStatement |

**Parameters** — same as `/financials/<stock_id>`.

**Response** — same long format as `/financials/<stock_id>`. Main `type` codes (FinMind's own
codes; the full set varies by company and year, so treat the response as the authoritative list
and use `origin_name` for anything not below). Filter on `type`, not `origin_name` — the same code's
label switches between full- and half-width brackets across years:

| `type` | `origin_name` |
|---|---|
| `CashFlowsFromOperatingActivities` | 營業活動之淨現金流入（流出） |
| `CashProvidedByInvestingActivities` | 投資活動之淨現金流入（流出） |
| `CashFlowsProvidedFromFinancingActivities` | 籌資活動之淨現金流入（流出） |
| `PropertyAndPlantAndEquipment` | 取得不動產、廠房及設備 (capex, negative) |
| `Depreciation` / `AmortizationExpense` | 折舊費用 / 攤銷費用 |
| `CashBalancesIncrease` | 本期現金及約當現金增加（減少）數 |
| `CashBalancesBeginningOfPeriod` / `CashBalancesEndOfPeriod` | 期初（年初）/ 期末現金及約當現金餘額 |

Flow items are **year-to-date (YTD) cumulative**, as filed in Taiwan: the `03-31` row is Q1 alone,
`06-30` is Q1–Q2, `09-30` is Q1–Q3, `12-31` is the full year. For a single quarter subtract the
previous quarter of the same year (Q1 needs no subtraction) — so fetch from a January `start`.
`CashBalancesEndOfPeriod` is the balance at the quarter end; `CashBalancesBeginningOfPeriod` is the
balance at the start of the year. This endpoint has no `period` parameter — it always returns YTD
(the `?period=quarter` single-quarter view exists only on the web chart route, not here).

**Errors** — `400` invalid `stock_id`, `404` no data, `503` upstream quota.

**Example**

```python
import pandas as pd
data = requests.get(f"{BASE_URL}/studio/market/twstock/cashflow/2330", headers=headers,
                    params={"start": "2022-01-01"}, timeout=30).json()["data"]
cfo = (pd.DataFrame(data).query("type == 'CashFlowsFromOperatingActivities'")
         .assign(date=lambda d: pd.to_datetime(d["date"])).set_index("date")["value"].sort_index())
cfo_q = cfo - cfo.groupby(cfo.index.year).shift(1).fillna(0)   # YTD → single quarter
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
| `date` | string | First day of the month **after** the revenue month — `2024-01-01` carries `revenue_year: 2023`, `revenue_month: 12`. Never use it as the period |
| `stock_id` | string | Code |
| `country` | string | Market — observed value is `Taiwan` |
| `create_time` | string | Observed empty (`""`) on every row |
| `revenue` | int | Monthly revenue in TWD (元), not thousands — **inferred from magnitude, not stated upstream**: `2330` for `revenue_year 2024, revenue_month 1` returned `215785127000`, which is only a sane figure read as 元 (NT$215.8bn) |
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
# [{"date": "2024-01-01", "stock_id": "2330", "country": "Taiwan", "create_time": "",
#   "revenue": 176299866000, "revenue_year": 2023, "revenue_month": 12},
#  {"date": "2024-02-01", "stock_id": "2330", "country": "Taiwan", "create_time": "",
#   "revenue": 215785127000, "revenue_year": 2024, "revenue_month": 1}, ...]
```

---

## `GET /studio/market/twstock/dividend/<stock_id>`

| | |
|---|---|
| Name | 股利事件 Taiwan Stock Dividend Events |
| Group | Taiwan Stock › Fundamentals |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Per stock — `2330` with no `start` / `end` returned 43 rows, earliest effective date 2005-06-19 |
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
- Effective dates can be in the future (announced but not yet ex) — the `2330` full-history call
  ran to a date a week ahead of the request. Filter by date yourself if you need past events only.
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
| Data from | Per stock — `2330` with no `start` / `end` returned 3,523 daily rows from 2012-05-02 |
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
- **Per-stock layer — no bucketing.** These are the raw per-category columns; how you group them is
  your call. Blave's own per-stock surfaces (web, app, AI chat) count 外資自營商 as part of 外資,
  matching the exchanges' own column naming, and treat 自營商 as 自行買賣 plus 避險. The whole-market
  endpoint (`GET /studio/market/twmarket/institutional`) groups it differently — see that section.

---

## `GET /studio/market/twstock/margin/<stock_id>`

| | |
|---|---|
| Name | 融資融券 Taiwan Stock Margin Trading |
| Group | Taiwan Stock › Institutional Flow |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | Per stock — `2330` with no `start` / `end` returned 6,323 daily rows from 2001-01-05 |
| Update | Daily; server cache 5 min |
| Source | FinMind TaiwanStockMarginPurchaseShortSale |

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `stock_id` | path | string | yes | — | See category conventions | Code |
| `start` | query | string | no | full history | `YYYY-MM-DD` | First date |
| `end` | query | string | no | latest | `YYYY-MM-DD` | Last date |

**Response** — `{"stock_id", "data": [...]}`, one row per day. Values are lots (張), not shares —
**verified against TWSE MI_MARGN**: for 2026-09-15 `2330` returned `margin_balance: 29282` and
`margin_limit: 6483092`, matching TWSE's own 今日餘額 29,282 and 次一營業日限額 6,483,092 for
that date exactly. Every row carries its own `date` and `stock_id`; when reading full history
(no `start` / `end`) take every figure from the same row — `margin_limit` is re-published per
day and changes over time.

| Field | Description |
|---|---|
| `margin_buy` / `margin_sell` | 融資買進 / 賣出 |
| `margin_cash_repay` | 融資現金償還 |
| `margin_balance` / `margin_prev_balance` | 融資今日 / 前日餘額 |
| `margin_limit` | 融資限額 — TWSE's 次一營業日限額 as published on that row's date, i.e. the cap that applies to the NEXT business day (`2330` on 2026-09-15: 6,483,092 lots) |
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
| Data from | Per stock — `2330` with no `start` / `end` returned 10,656 rows across 649 weekly dates, earliest 2010-01-29 |
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
| Data from | 2013-01-01 is only the **default** `start`. Send an earlier `start` and earlier rows come back — `2330` with `start=2000-01-01` returned rows from 2004-02-12 |
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
- Range queries are live: `start` / `end` over 2026-09-06 → 2026-09-13 returned rows spanning
  five distinct trading days, for both `broker/stock/<stock_id>` and `broker/trader/<trader_id>`.

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
#   "dealer": -4448119903.0, "total": -3211404085.0}, ...]
```

**Notes**
- **Whole-market layer.** `foreign` is 外資及陸資 excluding foreign dealers' own-account trading
  (外資自營商); `dealer` is 自營商 (自行買賣 + 避險), which TWSE already counts 外資自營商 inside. The
  per-stock endpoint (`GET /studio/market/twstock/institutional/<stock_id>`) is a different layer:
  it returns the raw per-category columns and buckets nothing. Don't mix the two.
- `foreign + investment_trust + dealer` equals `total`, the exchange's published 三大法人合計, on
  every day (verified against FinMind for all 5,537 days 2004-04-07 → 2026-10-06). 外資自營商 is not
  a separate column: it sits on warrants/ETNs, which Blave does not serve, and has been 0 every day
  after 2024-08-16.

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
| Data from | TXF: 2011-01-03 (`1d` and intraday). MXF: 2020-03-22 (`1d`). Stock futures start per contract — `CAF` returned `1d` bars at least as early as 2016-09-18 (the probe window began there, so it may reach further back) |
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
# [{"ts": "2024-01-01 16:00:00+00:00", "open": 17838.0, "high": 17920.0, "low": 17751.0, "close": 17798.0, "volume": 82820},
#  {"ts": "2024-01-02 16:00:00+00:00", "open": 17793.0, "high": 17817.0, "low": 17507.0, "close": 17546.0, "volume": 149638}, ...]

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
- Roll rule (all schemas; `TXF`, `MXF`, and stock futures alike): monthly settlement day — the
  3rd Wednesday, or the next trading day when that Wednesday is closed — is the expiring month
  for the whole day. It trades through its 13:30 Taipei close, no bar is stamped 13:31–14:59
  Taipei on that day, and the series is the next month from the 15:00 night session on. The
  settlement day's `1d` bar is the expiring month's, so its close is that contract's last
  trade at 13:30.
- For years of history use `ohlcv/<symbol>/export/<year>` instead of chunked JSON.
- A range with no data returns `200` with `[]`.
- Do not assume the series runs to the last trading day — `MXF` and `CAF` asked for everything up
  to the request date both came back with a last bar months old. Read `data[-1]["ts"]`.
- `1d` bars carry a `16:00:00+00:00` time component (00:00 Taipei), not midnight UTC — take the
  date from `ts` rather than assuming the timestamp is date-aligned.

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
| Data from | 2011 (TXF) |
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
- Same near-month continuous series as `ohlcv/<symbol>/1m`, under the same settlement-day roll
  rule (no bars stamped 13:31–14:59 Taipei on monthly settlement day).

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
| `symbol` | path | string | yes | — | `TXF`, `MXF` (both verified to return data); other `ohlcv/symbols` ids untested | Symbol |
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

**Notes**
- Rows are the near-month continuous contract under the same roll rule as `ohlcv`: on monthly
  settlement day there are no rows between the expiring month's 13:30 Taipei close and the
  15:00 night open; from the night session on the rows are the next month.

---

## `GET /studio/market/twfutures/daily/<futures_id>`

| | |
|---|---|
| Name | 期貨日行情 Taiwan Futures Daily by Contract |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 1998-07-21 for `TX`; other products start later — `MTX` from 2001-04-09, `CDF` (stock futures) from 2010-01-25 |
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
| Data from | Per contract listing — `CDF` asked from 1998-07-01 returned rows starting 2010-01-25 |
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
| `futures_id` | path | string | yes | — | Index futures — `TX`, `MTX`, `TMF`, `TE`, `TF` (all verified to return data); stock futures not supported | Product |
| `start` | query | string | no | `2018-06-05` | `YYYY-MM-DD` | First date |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last date |

**Response** — `{"futures_id", "data": [...]}`, 3 rows per day (自營商 / 投信 / 外資).

| Field | Description |
|---|---|
| `date`, `futures_id` | Day, product |
| `institutional_investors` | Investor type |
| `long_deal_volume` / `long_deal_amount` | Long trades (contracts / TWD thousand) |
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

**Notes**
- `*_amount` is TWD thousand — **inferred from magnitude, not stated upstream**, but the
  arithmetic backs it: a `TX` row with `long_open_interest_balance_amount 722870036` over
  `..._volume 78292` is 9,233 per contract, and a `TX` contract is index × 200, so 9,233 thousand
  ÷ 200 ≈ 46,160 index points, which is where the index was trading that day. Read as TWD it
  would be 1,000× too small.

---

## `GET /studio/market/twfutures/large_traders/<futures_id>`

| | |
|---|---|
| Name | 期貨大額交易人 Taiwan Futures Large Traders |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2007-01-02 — `TX` asked from 1998-07-01 returned nothing before that date |
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
| Data from | 2007-01-02 — `TXO` asked from 1998-07-01 returned nothing before that date |
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
# [{"date": "2024-01-02", "put_volume": 309583, "call_volume": 404231, "volume_pcr": 76.59,
#   "put_oi": 263673, "call_oi": 246495, "oi_pcr": 106.97, "pcr": 106.97},
#  {"date": "2024-01-03", "put_volume": 622854, "call_volume": 729547, "volume_pcr": 85.38,
#   "put_oi": 177203, "call_oi": 178062, "oi_pcr": 99.52, "pcr": 99.52}, ...]
```

**Notes**
- The official TAIFEX ratio — not derived from option institutional or large-trader data.

---

## `GET /studio/market/twfutures/carrying_cost/<identity>`

| | |
|---|---|
| Name | 法人台指期持倉成本 Taiwan Index Futures Institutional Carrying Cost |
| Group | Taiwan Futures & Options |
| Access | API plan or data fee |
| Rate limit | 500 / 5 min per key + per IP |
| Data from | 2023-10-18 (TAIFEX publishes only about the last three years) |
| Update | Daily after TAIFEX publishes — Blave jobs at 15:40 and 17:40 Taipei; server cache 5 min |
| Source | Blave estimate from TAIFEX data only: 三大法人-區分各期貨契約 (TX / MTX / TMF) and 期貨每日交易行情 (TX close) |

Blave's estimate of the average cost of one institution's net TAIEX-futures position, with its
unrealized and realized PnL. **An estimate from daily aggregates, not the institution's real fills.**

Method:
- Position = long OI − short OI, converted to 大台 (TX) contracts: TX × 1, MTX × 1/4, TMF × 1/20
  (`scope=all`), or TX only (`scope=tx`).
- Adding to the position uses that institution's own average trade price of the day on the side it
  added (TAIFEX 交易契約金額 ÷ (口數 × 200)) and updates a weighted-average cost. Reducing books
  realized PnL at the opposite side's average price and leaves the cost unchanged. A flip, or going
  flat, realizes the whole old position; the new direction starts at that day's price.
- **Every monthly settlement day** (third Wednesday; the next trading day if closed) starts a new
  cycle: cost resets to the mark price and realized PnL to 0. This makes the cost independent of
  where the data starts.
- Mark price = TAIFEX's own valuation of the open position (OI contract value ÷ (contracts × 200),
  i.e. at each month's settlement price). Unrealized PnL = (mark − cost) × net contracts × 200.

**Parameters**

| Name | In | Type | Required | Default | Allowed / format | Description |
|---|---|---|---|---|---|---|
| `identity` | path | string | yes | — | `foreign`, `investment_trust`, `dealer` | 外資 / 投信 / 自營商 |
| `start` | query | string | no | `2023-10-18` (whole history) | `YYYY-MM-DD` | First trading date, inclusive |
| `end` | query | string | no | today | `YYYY-MM-DD` | Last trading date, inclusive |
| `scope` | query | string | no | `all` | `all`, `tx` | `all` = TX + MTX + TMF in TX-equivalent contracts; `tx` = 大台 only (the basis most Taiwanese sites quote) |

The ledger always runs from the start of the stored history; `start` / `end` only cut the window,
so the same day has the same values whatever window you ask for.

**Response** — `{"identity", "scope", "data": [...]}`, one row per trading day, oldest → newest;
`"stale": true` is added only when the server's copy is behind TAIFEX's last published day (the
newest row may be missing).

| Field | Type | Unit | Description |
|---|---|---|---|
| `date` | string | — | Trading day (Taipei) |
| `net_open_interest` | float | TX-equivalent contracts | Long − short OI (negative = net short) |
| `net_open_interest_change` | float | contracts | Change vs the previous trading day |
| `cost` | float \| null | index points | Weighted-average cost of the net position; `null` when flat |
| `txf_close` | float \| null | index points | TX near-month day-session close (the expiring contract is skipped on settlement day) |
| `mark_price` | float \| null | index points | TAIFEX valuation of the position, at settlement prices |
| `unrealized_pnl` | int | TWD | (mark − cost) × net contracts × 200 |
| `realized_pnl` | int | TWD | Realized since `cycle_start`; resets to 0 on every settlement day |
| `total_pnl` | int | TWD | `unrealized_pnl + realized_pnl` |
| `cycle_start` | string | — | The settlement day that opened the current cycle |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid identity. Allowed: ['dealer', 'foreign', 'investment_trust']"}` | Unknown identity |
| 400 | `{"error": "Invalid scope. Allowed: ['all', 'tx']"}` | Unknown scope |
| 400 | `{"error": "Invalid start date, expected YYYY-MM-DD"}` (or `end`) / `{"error": "start must not be after end"}` | Bad date / reversed range |
| 503 | `{"error": "Market data is not ready on this server. Please retry later."}` | Store not ready — retry later, never read as "no position" |
| 500 | `{"error": "Internal error"}` | Unexpected server error |

**Example**

```python
body = requests.get(f"{BASE_URL}/studio/market/twfutures/carrying_cost/foreign", headers=headers,
                    params={"start": "2026-10-06"}, timeout=60).json()
rows = body["data"]
# Live capture 2026-10-07 (scope=all):
# {"identity": "foreign", "scope": "all", "data": [
#   {"date": "2026-10-06", "net_open_interest": -78570.7, "net_open_interest_change": -3923.5,
#    "cost": 46527.57, "txf_close": 50060.0, "mark_price": 50088.51,
#    "unrealized_pnl": -55957022956, "realized_pnl": -5893982992, "total_pnl": -61851005948,
#    "cycle_start": "2026-09-16"},
#   {"date": "2026-10-07", "net_open_interest": -78435.8, "net_open_interest_change": 134.9,
#    "cost": 46527.57, "txf_close": 49979.0, "mark_price": 49974.38,
#    "unrealized_pnl": -54070636128, "realized_pnl": -5988669182, "total_pnl": -60059305310,
#    "cycle_start": "2026-09-16"}]}
gap = rows[-1]["txf_close"] - rows[-1]["cost"]   # points the market is above (+) / below (−) their cost
```

**Notes**
- Futures only: option positions (including dealers' hedges) are not in the ledger, so a dealer's
  "loss" here may be offset elsewhere.
- Right after a settlement day the cost equals the mark by construction — the first days of a
  cycle say little about where the position was really built.
- Other sites' 外資成本 figures use different rules (TX only, near-month close as the trade price, or
  undisclosed) — numbers will differ; compare like with like (`scope=tx`).
- Interpretation: `references/blave-indicator-guide.md` › 法人台指期持倉成本.

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
| `instrument_id` | int | — | Databento instrument id carried through from the source bar |

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
# [{"ts": "2024-01-02 00:00:00+00:00", "open": 71.95, "high": 73.64, "low": 70.06, "close": 70.5,
#   "volume": 263594, "instrument_id": 686071},
#  {"ts": "2024-01-03 00:00:00+00:00", "open": 70.49, "high": 73.23, "low": 69.28, "close": 73.05,
#   "volume": 253755, "instrument_id": 686071}, ...]
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

A live response carried these further fields, passed through from the upstream feed. Only what was
observed is stated; do not read more into them than that.

| Field | Type | Observed |
|---|---|---|
| `id` | int | Upstream event id, e.g. `79382` |
| `date` | int | Epoch seconds for the **period the reading covers**, not the release — rows labelled `subjectTitle: "<9月>"` carried `date` = 2026-09-01 while `startDate` was 2026-09-23 |
| `dateUnit` | string | `month` |
| `type` | int | `2` |
| `areaId` | string | `"4"` |
| `place` | string \| null | `null` |
| `correct` | number \| null | `null` |
| `correctMark` | string | `"N"` |

**Errors**

| Status | Body | When |
|---|---|---|
| 400 | `{"error": "Invalid date format. Use YYYY-MM-DD"}` | Malformed `start` / `end` |
| 400 | `{"error": "max_priority must be an integer"}` | Non-integer `max_priority` |
| 400 | `{"error": "limit must be an integer"}` / `{"error": "limit must be >= 1"}` | Bad `limit` |
| 429 | `{"error_code": "ERR429", "message": "User rate limit exceeded"}` | Over 100 requests / min |

**Example**

```python
params = {"start": "2026-09-16", "end": "2026-09-23", "max_priority": 1, "lang": "zh"}
response = requests.get(
    f"{BASE_URL}/studio/market/anue/economic_calendar",
    headers=headers, params=params, timeout=60,
)
data = response.json()
# [{"id": 79382, "startDate": 1790121600, "date": 1788220800, "dateUnit": "month", "time": "16:30",
#   "countryId": "GB", "countryName": "英國", "areaId": "4",
#   "subject": "S&P Global Manufacturing PMI - 初值", "subjectTitle": "<9月>", "unit": "point",
#   "predict": 51.7, "last": 51.7, "real": None, "correct": None, "correctMark": "N",
#   "place": None, "priority": 1, "type": 2}, ...]
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
