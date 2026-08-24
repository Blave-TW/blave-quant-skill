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
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2026-08-04", "end_date": "2026-08-07"}
response = requests.get(f"{BASE_URL}/kline", headers=headers, params=params, timeout=60)
raw = response.json()
# returns a list directly (NOT {"data": [...]}):
# [{"time": 1785801600.0, "open": 63497.1, "high": 63558.8, "low": 63290.2, "close": 63337.6, "volume": 4583.87}, ...]
# time is Unix seconds UTC+0; volume is base-asset volume
data = raw if isinstance(raw, list) else raw.get("data", [])
```

Sub-5min periods (`1min`/`2min`/`3min`/`4min`) are supported with a tighter
per-request window: max 30 days per request (400 with an explanatory error
beyond). History reaches back to the symbol's listing date; a window before
listing returns an empty list. 5min and above keep the normal
1-year-per-request limit.

```python
params = {"symbol": "BTCUSDT", "period": "1min", "start_date": "2026-08-04", "end_date": "2026-08-07"}
response = requests.get(f"{BASE_URL}/kline", headers=headers, params=params, timeout=60)
# [{"time": 1785801600.0, "open": 63497.1, "high": 63513.1, "low": 63458.5, "close": 63464.4, "volume": 94.226}, ...]
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

## Funding Rate

```python
# Binance only. alpha = funding rate × 100 (percent); positive = longs pay shorts.
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/funding_rate/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
# → {"data": {"timestamp": [1735689600.0, ...], "alpha": [0.01, ...], "close": [93000.0, ...], "stat": {...}}}
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

## Unusual Movement

```python
# Get symbols
response = requests.get(f"{BASE_URL}/unusual_movement/get_symbols", headers=headers, timeout=60)

# Get alpha
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h"}
response = requests.get(f"{BASE_URL}/unusual_movement/get_alpha", headers=headers, params=params, timeout=60)
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
# Rolling alpha history per sector (time series)
response = requests.get(f"{BASE_URL}/sector_rotation/get_history_data", headers=headers, timeout=60)
print(response.json())

# Heat-map snapshot: per-sector % change over 7 timeframes, with per-token breakdown
response = requests.get(f"{BASE_URL}/sector_rotation/get_overview_data", headers=headers, timeout=60)
data = response.json()["data"]
# {"AI": {"name_en": "AI", "name_zh": "人工智能",
#         "data": {"1h": {"pct_change": ...}, "8h": ..., "24h": ..., "3d": ..., "7d": ..., "30d": ..., "90d": ...},
#         "symbols": {"0G": {"id": 38337, "data": {"1h": {"pct_change": ...}, ...}}, ...}},
#  ...}  # ~48 sectors; pct_change is a decimal (0.0061 = +0.61%)
```

---

## OI Imbalance

Open-interest-to-market-cap ranking across all listed tokens (snapshot, sorted by
`alpha` descending). `alpha = oi_total / market_cap`; `oi_total` sums Binance/OKX/BingX
futures OI in USD. High alpha = OI crowded relative to size — squeeze/volatility risk.
The `/alpha_table` field `oi_imbalance` carries only the final `alpha`; this endpoint
returns the full detail table.

```python
response = requests.get(f"{BASE_URL}/oi_imbalance/get_overview_data", headers=headers, timeout=60)
data = response.json()["data"]
# [{"token": "TSLA", "token_id": 39618, "token_price": 313.33, "token_chg": 0.031,
#   "market_cap": 40415.98, "oi_total": 59916616.78, "alpha": 1482.5}, ...]
```

---

## Blave Top Trader Exposure

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/blave_top_trader/get_exposure", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Taiwan Stock Universe / Basic Info — 股票清單/基本資料

Full-market list (上市+上櫃, incl. ETFs), or a single-stock lookup with the same shape.
Both are basic company data, not a time series — Redis-cached 24h server-side.

```python
response = requests.get(f"{BASE_URL}/studio/market/twstock/list", headers=headers, timeout=60)
data = response.json()["data"]
# [{"stock_id": "2330", "name": "台積電", "close": 2410.0, "industry_code": "24", "listing_date": "1994-09-05"}, ...]

response = requests.get(f"{BASE_URL}/studio/market/twstock/info/2330", headers=headers, timeout=30)
info = response.json()["data"]
# {"stock_id": "2330", "name": "台積電", "close": 2410.0, "industry_code": "24", "listing_date": "1994-09-05"}
# 404 {"error": "Stock not found"} if stock_id isn't a currently-active listing
```

**Field meanings:**
| Field | Description |
|---|---|
| `close` | Most recent daily closing price (`null` if upstream field was missing, e.g. halted stock) |
| `industry_code` | TWSE/TPEx raw numeric 產業別 code, passthrough (not decoded to a name) — group/filter by it, don't hardcode a label mapping. `null` for ETFs/non-company securities. Common codes: `15` 航運業, `17` 金融保險業, `22` 生技醫療業, `24` 半導體業, `25` 電腦及週邊設備業, `26` 光電業, `27` 通信網路業, `28` 電子零組件業, `29` 電子通路業, `30` 資訊服務業, `31` 其他電子業 |
| `listing_date` | `YYYY-MM-DD`, `null` for ETFs/non-company securities |

Use `/list` for universe building / industry-based sampling (must sample across
industries — stock IDs are grouped by sector, so `[:N]` truncation concentrates in a
few sectors). Use `/info/<stock_id>` for a single-stock lookup only.

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

## Taiwan Stock Real-Time Quote — 即時報價

Real-time last-quote snapshot: current price, best bid/ask, and today's OHLC so far.
Refreshes approximately every 10 seconds during market and post-market sessions. **No
history** — every call returns the current moment only, no `start`/`end` params exist.
Unlike every other Taiwan stock endpoint, `"data"` is a flat object (single query) or a
dict/list (batch/all), never a list of daily records.

**Single stock:**
```python
response = requests.get(f"{BASE_URL}/studio/market/twstock/quote/2330", headers=headers, timeout=30)
data = response.json()["data"]
# {"open": 2415.0, "high": 2465.0, "low": 2415.0, "close": 2445.0,
#  "change_price": -20.0, "change_rate": -0.81, "average_price": 2432.58,
#  "volume": 4245, "total_volume": 26403, "amount": 10379025000, "total_amount": 64227410000,
#  "yesterday_volume": 27390, "buy_price": 2445.0, "buy_volume": 17,
#  "sell_price": 2450.0, "sell_volume": 11, "volume_ratio": 0.96,
#  "quote_time": "2026-07-03 14:30:00", "stock_id": "2330", "tick_type": 2}
```

**Batch (max 50 ids):**
```python
params = {"stock_ids": "2330,2317"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/quote", headers=headers, params=params, timeout=30)
data = response.json()["data"]
# {"2330": {...quote fields...}, "2317": {...quote fields...}}
```

**Entire market in one call (~2839 stocks):**
```python
response = requests.get(f"{BASE_URL}/studio/market/twstock/quote/all", headers=headers, timeout=30)
data = response.json()["data"]
# [{...quote fields...}, {...quote fields...}, ...]
```

**Field meanings:**
| Field | Meaning |
|---|---|
| `open`/`high`/`low`/`close` | Today's OHLC so far (not a full-day final close until after market close) |
| `buy_price` / `buy_volume` | Best bid price / volume |
| `sell_price` / `sell_volume` | Best ask price / volume |
| `volume` | Latest tick's trade volume |
| `total_volume` | Cumulative volume for the day so far |
| `quote_time` | Full timestamp (`YYYY-MM-DD HH:MM:SS`) — NOT a bare date like other endpoints' `date` field |
| `tick_type` | `0` = indeterminate, `1` = sell-initiated (賣盤成交), `2` = buy-initiated (買盤成交) |

Use for 盤中報價查詢、下單前確認現價、多檔持股即時檢查. Do **not** use for backtesting —
there is no history, only the current snapshot.

---

## Taiwan Stock Minute-Line OHLCV — 台股現股分線

```
GET /studio/market/twstock/minute/ohlcv/<stock_id>/<schema>
GET /studio/market/twstock/minute/ohlcv/symbols
```

`schema` ∈ `1m` / `5m` / `15m` / `30m` / `60m` / `1d`. `start` / `end` optional
(YYYY-MM-DD; default `end` = today, default `start` = `end` minus the schema's max
range). `adjust` optional (`0`/`1`/`true`/`false`, default `0` = raw traded prices):
`adjust=1` returns forward-adjusted (後復權) OHLC — same factor pipeline as the
Studio daily adjusted series (`/twstock/price_adj`), numbers match exactly; `volume`
is never adjusted. If the factor source is unavailable the API returns 503 — it
never silently serves unadjusted prices as adjusted. History from 2019-01 (FinMind
official data, backfilled per stock).
Timestamps are UTC ISO, minute-START labels — the 13:30 Taipei bar is the closing
auction. **`volume` is in lots (張), not shares.** Requires API plan auth.

| `schema` | max range per request |
|---|---|
| `1d` | 3650 days |
| `1m` | 31 days |
| `5m` | 62 days |
| `15m` | 93 days |
| `30m` | 186 days |
| `60m` | 365 days |

Beyond the cap → 400 `{"error": "date_range_too_large", "max_days": <n>}`. Split
longer spans into chunks (same pattern as `fetch_txf_chunked` below).

**Coverage is demand-driven.** `/ohlcv/symbols` lists the stock_ids that already have
minute-line data. Any listed TWSE/TPEx stock_id can be queried though — the first-ever
query auto-seeds recent data (~30 days) and enrolls the stock for ongoing tracking:
from the next day onward it gets intraday real-time bars plus a daily official
correction after market close. Deep history (2019-01 →) backfills server-side after
first touch, so check `/ohlcv/symbols` before requesting years of history.

```python
response = requests.get(f"{BASE_URL}/studio/market/twstock/minute/ohlcv/symbols", headers=headers, timeout=30)
print(response.json())
# {"data": ["2330"]}

params = {"start": "2026-08-06", "end": "2026-08-06"}
response = requests.get(
    f"{BASE_URL}/studio/market/twstock/minute/ohlcv/2330/1m",
    headers=headers, params=params, timeout=60,
)
body = response.json()
# {"stock_id": "2330", "schema": "1m", "data": [
#   {"close": 2385.0, "high": 2395.0, "low": 2385.0, "open": 2395.0, "ts": "2026-08-06 01:00:00+00:00", "volume": 2540},
#   {"close": 2385.0, "high": 2385.0, "low": 2380.0, "open": 2380.0, "ts": "2026-08-06 01:01:00+00:00", "volume": 204},
#   ...
#   {"close": 2365.0, "high": 2365.0, "low": 2365.0, "open": 2365.0, "ts": "2026-08-06 05:30:00+00:00", "volume": 4217}]}
```

**Response fields:**
| Field | Description |
|---|---|
| `ts` | Bar open time (UTC ISO string, minute-start label) |
| `open` / `high` / `low` / `close` | Price (TWD) |
| `volume` | Lots (張) |

A still-forming bar is never returned — the last bar of the current interval is
dropped until it closes. Use `/studio/market/twstock/quote/<stock_id>` for the live
tick instead.

---

## Taiwan Stock PE / PB / Dividend Yield — 本益比/淨值比/殖利率

Single-stock daily PE ratio, PB ratio, and dividend yield. `start`/`end` optional (omit for
full history); data from 2005-10-01. For value screens across many stocks use
`batch/per` (see *Taiwan Stock Batch Fetch* below) — the whole market is ~40 batch calls.

```python
response = requests.get(
    f"{BASE_URL}/studio/market/twstock/per/2330",
    headers=headers, params={"start": "2026-01-01", "end": "2026-07-22"}, timeout=60,
)
data = response.json()["data"]
# [{"date": "2026-07-21", "dividend_yield": 0.95, "PER": 34.87, "PBR": 11.05}, ...]
```

---

## Taiwan Stock Market Value — 市值 / 市值排名

Two endpoints. `/market_value/<stock_id>` is the single-stock daily market-cap time series
(`start`/`end` optional; data from 2004-01-01; fields `date`, `market_value`).
`/market_value/all` is the **whole-market ranking snapshot** — every stock's latest market
cap, sorted desc, in one call. Use `/all` for "前十大權值股" / "市值前 N 檔當股池" type
questions instead of fanning out to `/market_value/<stock_id>` per stock.

`/all` params: `top` optional int 1–3000 — keep only the top N by market cap (omit for the
full list, ~2,400 rows). Out-of-range / non-integer → 400
`{"error": "top must be an integer between 1 and 3000"}`; 404 = no recent data; 503 =
upstream rate limit (retry later).

Universe = 上市 + 上櫃 + ETF (興櫃 excluded; ETNs have no data). `market_value` is NTD 元
(integer); `rank` is 1-based. `date` is the as-of date actually used — the latest published
day of the upstream source (FinMind TaiwanStockMarketValue, EOD daily), so it can lag today
by a day. Server-cached 30 min. ETFs such as 0050 rank among the large caps — to drop ETFs,
filter out `stock_id` starting with `00`.

```python
# Single stock — daily time series
params = {"start": "2026-01-01", "end": "2026-08-20"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/market_value/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "...", "market_value": ...}, ...]

# Whole market ranking — top 10
response = requests.get(f"{BASE_URL}/studio/market/twstock/market_value/all", headers=headers, params={"top": 10}, timeout=60)
body = response.json()
# {"date": "2026-08-20",
#  "data": [{"rank": 1, "stock_id": "2330", "name": "台積電",   "market_value": 61589378909125},
#           {"rank": 2, "stock_id": "2454", "name": "聯發科",   "market_value": 5934413005900},
#           {"rank": 3, "stock_id": "2308", "name": "台達電",   "market_value": 4532713109105}, ...]}

# Top-50 non-ETF stock pool (ETFs are ranked too, so over-fetch then filter)
response = requests.get(f"{BASE_URL}/studio/market/twstock/market_value/all", headers=headers, params={"top": 100}, timeout=60)
top50 = [r["stock_id"] for r in response.json()["data"] if not r["stock_id"].startswith("00")][:50]
```

---

## Taiwan Stock Dividend Events — 台股股利事件

Full per-stock dividend event history (cash + stock dividends), one row per announcement
row. `start` / `end` optional (omit for full history), strict `YYYY-MM-DD` — anything else
(e.g. `2025-6-01`) is a 400. Range filtering uses a three-tier effective date:
`cash_ex_date` when set, else `stock_ex_date`, else `record_date` — so freshly announced
events whose ex date is not yet decided still show up in range queries.

```python
response = requests.get(
    f"{BASE_URL}/studio/market/twstock/dividend/2330",
    headers=headers, params={"start": "2025-01-01", "end": "2025-12-31"}, timeout=30,
)
data = response.json()["data"]
# [{"record_date": "2025-03-24", "period": "113年第3季", "announce_date": "2025-03-03",
#   "cash_ex_date": "2025-03-18", "stock_ex_date": "", "pay_date": "2025-04-10",
#   "cash": 4.50002042, "stock": 0.0, "stock_ratio": 0.0}, ...]
```

**Response fields:**
| Field | Description |
|---|---|
| `record_date` | 權利分派基準日 (`YYYY-MM-DD`) |
| `period` | 股利所屬期間 — an **opaque label** (`114年第3季`, `113`, `不適用`, …). Do NOT parse it into a Western calendar year; compare/group by string only |
| `announce_date` | 董事會/股東會公告日 — empty string when unknown |
| `cash_ex_date` | 除息交易日 — empty string when not yet decided / no cash dividend |
| `stock_ex_date` | 除權交易日 — empty string when none |
| `pay_date` | 現金股利發放日 — empty string when unknown |
| `cash` | 現金股利 per share (盈餘+公積 combined, NTD) |
| `stock` | 股票股利 per share (盈餘+公積 combined, 元面額) |
| `stock_ratio` | `stock / 10` — the split-style adjustment ratio |

Notes:
- **Zero-value rows are kept**: `cash == 0 and stock == 0` means the company announced a
  no-distribution decision — a real, tradeable piece of information, not noise.
- Empty date fields are empty strings `""`, never null.
- Universe is **currently-listed 上市/上櫃 stocks only** — a delisted or unknown id is 404.
- `404` = unknown stock_id OR the stock has no dividend history at all. A valid stock with
  history but no events in your range returns `200` + `[]` (the two are distinguishable).
- Quota exhaustion upstream → `503` (retry shortly).

**Batch form** (up to **50** ids — use this for screens, never fan out the single endpoint):

```python
response = requests.get(
    f"{BASE_URL}/studio/market/twstock/batch/dividend",
    headers=headers,
    params={"stock_ids": "2330,1101", "start": "2026-01-01"}, timeout=120,
)
payload = response.json()
# {"data_type": "dividend",
#  "data": {"2330": [{"record_date": "2026-03-23", "period": "114年第3季",
#                     "announce_date": "2026-03-02", "cash_ex_date": "2026-03-17",
#                     "stock_ex_date": "", "pay_date": "2026-04-09",
#                     "cash": 6.00003573, "stock": 0.0, "stock_ratio": 0.0}, ...],
#           "1101": [...]},
#  "failed": []}
```

The batch contract is deliberately **asymmetric** with the single endpoint: an unknown id
or a stock with no dividend history is **silently absent** from both `data` and `failed`
(no 404); `failed` only lists server-side fetch failures (retry those). Quota exhaustion
in batch is `200` + the affected ids in `failed`, not a 503.

---

## Taiwan Stock Batch Fetch — 批次查詢（選股/大型 universe）

One call fetches up to **50 stocks** of the same data type — the right tool for any
multi-stock screen. Never fan out per-stock endpoints across a universe (rate limits);
the whole market (~2,000 stocks) is ~40 batch calls.

`data_type` ∈ `price` (raw daily OHLCV incl. High/Low — KD/breakout screens) /
`price_adj` / `per` (value screens) / `institutional` / `shareholding` /
`foreign_shareholding` / `financials` / `balance_sheet` / `monthly_revenue` /
`dividend` (stricter date validation + silent-absence contract — see *Taiwan Stock
Dividend Events* above). Per-id rows are identical to the corresponding single-stock
endpoint; `start`/`end` as per type.

```python
response = requests.get(
    f"{BASE_URL}/studio/market/twstock/batch/per",
    headers=headers,
    params={"stock_ids": "2330,6182", "start": "2026-08-04", "end": "2026-08-08"},
    timeout=120,
)
payload = response.json()
# {"data_type": "per",
#  "data": {"2330": [{"date": "2026-08-04", "dividend_yield": 0.95, "PER": 31.19,
#                     "PBR": 10.21, "stock_id": "2330"}, ...],
#           "6182": [...]},
#  "failed": []}
```

`failed` lists stock_ids whose server-side fetch failed (rate limit or upstream error) —
retry those. A stock absent from both `data` and `failed` genuinely has no data in the
range. `batch/price` rows carry `open/high/low/close/volume` plus `spread`,
`turnover_count`, `turnover_value` — same as `/twstock/price/<stock_id>`.

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

## Taiwan Stock Margin Trading — 融資融券

Daily margin purchase and short sale data (one row per trading day).
`start` / `end` optional (omit for full history).

```python
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/margin/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "2024-01-02", "stock_id": "2330",
#   "margin_buy": 310,               # 融資買進
#   "margin_sell": 513,              # 融資賣出
#   "margin_balance": 12844,         # 融資餘額（當日）
#   "margin_prev_balance": 13057,    # 融資餘額（前日）
#   "margin_limit": 6483017,         # 融資限額
#   "margin_cash_repay": 10,         # 融資現金償還
#   "short_sell": 21,                # 融券賣出
#   "short_buy": 2,                  # 融券買進
#   "short_balance": 208,            # 融券餘額（當日）
#   "short_prev_balance": 189,       # 融券餘額（前日）
#   "short_limit": 6483017,          # 融券限額
#   "short_cash_repay": 0,           # 融券現金償還
#   "offset_loan_short": 1}, ...]    # 資券相抵
```

**Field meanings:**
| Field | 說明 |
|---|---|
| `margin_buy` | 融資買進 — shares purchased on margin today |
| `margin_sell` | 融資賣出 — margin shares sold today |
| `margin_balance` | 融資餘額 — today's outstanding margin balance (shares) |
| `margin_prev_balance` | 融資前日餘額 — yesterday's margin balance |
| `margin_limit` | 融資限額 — margin purchase ceiling |
| `margin_cash_repay` | 融資現金償還 — cash repayment of margin |
| `short_sell` | 融券賣出 — shares sold short today |
| `short_buy` | 融券買進 — short shares covered today |
| `short_balance` | 融券餘額 — today's outstanding short balance (shares) |
| `short_prev_balance` | 融券前日餘額 — yesterday's short balance |
| `short_limit` | 融券限額 — short sale ceiling |
| `short_cash_repay` | 融券現金償還 — cash repayment of short |
| `offset_loan_short` | 資券相抵 — shares offset between margin long and short |

**Common derived signals:**
```python
df["margin_net"] = df["margin_buy"] - df["margin_sell"]        # 融資淨增減
df["short_net"]  = df["short_sell"] - df["short_buy"]          # 融券淨增減
df["margin_util"] = df["margin_balance"] / df["margin_limit"]  # 融資使用率
```

Values are **shares** (股), not dollars. Data available from 1994-10-01.

---

## Taiwan Stock Shareholding Distribution — 股權持股分級表

Weekly shareholding distribution by bracket (one row per date × level).
`start` / `end` optional (omit for full history). Data updates every Friday.

```python
params = {"start": "2024-01-01", "end": "2024-03-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/shareholding/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "2024-01-05", "stock_id": "2330",
#   "level": "1-999",          "people": 732503,  "unit": 136261142,  "percent": 0.52},
#  {"date": "2024-01-05", "stock_id": "2330",
#   "level": "1,000-5,000",    "people": 371837,  "unit": 713353901,  "percent": 2.75},
#  {"date": "2024-01-05", "stock_id": "2330",
#   "level": "total",          "people": 1234567, "unit": 25932070992, "percent": 100.0}, ...]
```

**Field meanings:**
| Field | 說明 |
|---|---|
| `level` | 持股級距 — holding bracket (e.g. `"1-999"`, `"1,000-5,000"`, … `"more than 1,000,001"`, `"total"`) |
| `people` | 持股人數 — number of shareholders in this bracket |
| `unit` | 持股股數 — total shares held by this bracket |
| `percent` | 持股比例 (%) — percentage of total issued shares |

**All 17 levels (in data order):**
`1-999`, `1,000-5,000`, `5,001-10,000`, `10,001-15,000`, `15,001-20,000`, `20,001-30,000`,
`30,001-40,000`, `40,001-50,000`, `50,001-100,000`, `100,001-200,000`, `200,001-400,000`,
`400,001-600,000`, `600,001-800,000`, `800,001-1,000,000`, `more than 1,000,001`,
`total`, `差異數調整（說明4）`

**Common derived signals:**
```python
import pandas as pd
df = pd.DataFrame(data)

# 大股東集中度：持股 > 400,000 股的比例合計
large_holder_levels = ["400,001-600,000", "600,001-800,000", "800,001-1,000,000", "more than 1,000,001"]
df_large = df[df["level"].isin(large_holder_levels)].groupby("date")["percent"].sum().reset_index()
df_large.columns = ["date", "large_holder_pct"]

# 散戶比例：持股 1–999 股 (零股) 的人數趨勢
df_retail = df[df["level"] == "1-999"][["date", "people", "percent"]]
```

Use for 籌碼面分析 — tracking whether large holders are accumulating or distributing over time.

---

## Taiwan Stock Financial Statements — 季報基本面

Quarterly fundamental data. All three endpoints share the same **long format** response (one row per financial item per quarter). `start` / `end` optional (default: 2013-01-01 to today). Redis-cached for 24 h.

| Statement | Path |
|---|---|
| 綜合損益表 Comprehensive Income | `/studio/market/twstock/financials/<stock_id>` |
| 資產負債表 Balance Sheet | `/studio/market/twstock/balance_sheet/<stock_id>` |
| 現金流量表 Cash Flow | `/studio/market/twstock/cashflow/<stock_id>` |

```python
params = {"start": "2022-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/financials/2330", headers=headers, params=params, timeout=30)
data = response.json()["data"]
# [{"date": "2022-03-31", "stock_id": "2330", "type": "Revenue",     "value": 491075000000.0, "origin_name": "營業收入"},
#  {"date": "2022-03-31", "stock_id": "2330", "type": "GrossProfit", "value": 258033000000.0, "origin_name": "毛利（損）"},
#  {"date": "2022-03-31", "stock_id": "2330", "type": "NetIncome",   "value": 202730000000.0, "origin_name": "本期淨利（淨損）"},
#  {"date": "2022-03-31", "stock_id": "2330", "type": "EPS",         "value": 7.82,           "origin_name": "每股盈餘（基本）"}, ...]
```

**Response fields:**
| Field | Description |
|---|---|
| `date` | Quarter-end date (`YYYY-MM-DD`): Q1=03-31, Q2=06-30, Q3=09-30, Q4=12-31 |
| `type` | Financial item code (English) |
| `value` | Numeric value in TWD; balance sheet items with `_per` suffix are % of total assets |
| `origin_name` | Chinese label — use this to identify unfamiliar `type` codes |

**Key `type` codes — `/financials` (損益表):**
| `type` | 中文 |
|---|---|
| `Revenue` | 營業收入 |
| `GrossProfit` | 毛利（損） |
| `OperatingIncome` | 營業利益（損失） |
| `NetIncome` | 本期淨利（淨損） |
| `EPS` | 每股盈餘（基本） |
| `TAX` | 所得稅費用（利益） |
| `OtherComprehensiveIncome` | 其他綜合損益（淨額） |

**Key `type` codes — `/balance_sheet` (資產負債表):**
| `type` | 中文 |
|---|---|
| `CashAndCashEquivalents` | 現金及約當現金 |
| `TotalAssets` | 資產總計 |
| `TotalLiabilities` | 負債總計 |
| `TotalEquity` | 權益總計 |
| `CashAndCashEquivalents_per` | 現金及約當現金（佔資產 %） |

**Key `type` codes — `/cashflow` (現金流量表):**
| `type` | 中文 |
|---|---|
| `OperatingActivities` | 營業活動之淨現金流入（出） |
| `InvestingActivities` | 投資活動之淨現金流入（出） |
| `FinancingActivities` | 籌資活動之淨現金流入（出） |
| `CashBalancesEndOfPeriod` | 期末現金及約當現金餘額 |
| `PropertyAndPlantAndEquipment` | 取得不動產、廠房及設備 |

**Pivot long → wide for analysis:**
```python
import pandas as pd
df = pd.DataFrame(data)
wide = df.pivot_table(index="date", columns="type", values="value", aggfunc="first")
# wide["NetIncome"]  → quarterly net income series
# wide["EPS"]        → quarterly EPS series
```

---

## Taiwan Stock Monthly Revenue — 月營收

Monthly revenue data. One row per stock per month. `start` / `end` optional (default: 2000-01-01 to today). Redis-cached for 24 h.

```python
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/monthly_revenue/2330", headers=headers, params=params, timeout=30)
data = response.json()["data"]
# [{"date": "2024-02-10", "stock_id": "2330", "country": "台灣", "revenue": 215274000, "revenue_month": 1, "revenue_year": 2024},
#  {"date": "2024-03-08", "stock_id": "2330", "country": "台灣", "revenue": 195348000, "revenue_month": 2, "revenue_year": 2024}, ...]
```

**Response fields:**
| Field | Description |
|---|---|
| `date` | 月份起始日 (`YYYY-MM-01`) — e.g. `2024-02-01` means the revenue is for `revenue_month=1` (January) |
| `stock_id` | Stock code |
| `country` | Listed market (e.g. `台灣`) |
| `revenue` | Monthly revenue (NTD 元, full amount — not thousands) |
| `revenue_month` | Revenue month (1–12) |
| `revenue_year` | Revenue year |

**MoM / YoY analysis:**
```python
import pandas as pd
df = pd.DataFrame(data)
df = df.sort_values("date").reset_index(drop=True)
df["mom_pct"] = df["revenue"].pct_change() * 100          # month-over-month %
df["yoy_pct"] = df["revenue"].pct_change(periods=12) * 100  # year-over-year %
```

---

## Taiwan Market-Wide — 大盤

Whole-market series (no `stock_id` dimension). Four endpoints, all daily, all with optional
`start` / `end` (omit for full history) and all returning `{"data": [...]}` sorted by date.
Do **not** sum the per-stock endpoints above as a substitute — coverage and units differ.

```python
params = {"start": "2024-01-01", "end": "2024-12-31"}

# 加權指數 TAIEX 日 OHLC — from 1999-01-05. TAIEX is the only supported index id (else 400).
r = requests.get(f"{BASE_URL}/studio/market/twmarket/index/TAIEX", headers=headers, params=params, timeout=60)
# {"index_id": "TAIEX", "data": [{"date": "2024-01-02", "open": 17939.79, "high": 17956.74,
#                                 "low": 17784.97, "close": 17853.76}, ...]}

# 全市場成交量值 — from 1990-01-04
r = requests.get(f"{BASE_URL}/studio/market/twmarket/turnover", headers=headers, params=params, timeout=60)
# [{"date": "2024-01-02", "volume": 6411778806.0, "value": 301290668897.0, "trades": 2267660.0}, ...]

# 全市場三大法人買賣超 — from 2004-04-07
r = requests.get(f"{BASE_URL}/studio/market/twmarket/institutional", headers=headers, params=params, timeout=60)
# [{"date": "2024-01-02", "foreign": 1047078183.0, "investment_trust": 189637635.0,
#   "dealer": -4447440583.0, "total": -3211404085.0}, ...]

# 全市場融資融券餘額 — from 2001-01-03
r = requests.get(f"{BASE_URL}/studio/market/twmarket/margin", headers=headers, params=params, timeout=60)
# [{"date": "2024-01-02", "margin_balance": 8012561, "margin_balance_prev": 7999081,
#   "margin_balance_value": 248424271000, "short_balance": 369678,
#   "short_balance_prev": 359738}, ...]
```

**Field meanings:**
| Endpoint | Field | Unit |
|---|---|---|
| `index/TAIEX` | `open` `high` `low` `close` | index points (no volume — use `turnover`) |
| `turnover` | `volume` / `value` / `trades` | 成交股數 shares / 成交金額 TWD 元 / 成交筆數 count |
| `institutional` | `foreign` `investment_trust` `dealer` `total` | TWD 元, **net** (buy − sell) |
| `margin` | `margin_balance` `margin_balance_prev` `short_balance` `short_balance_prev` | 張 (lots) |
| `margin` | `margin_balance_value` | TWD 元 |

外資自營商 (foreign dealers' own account) is bucketed into `dealer`, not `foreign` — same
convention FinMind uses, so `foreign` here is 外資及陸資(不含外資自營商).

TXO put/call ratio is a futures/options dataset — see *Taiwan Option Put/Call Ratio* below.

---

## Taiwan Index Dividend Points — 台股加權指數每日除息點數

Daily dividend points removed from TAIEX by constituent ex-dividend events — the series
you subtract when computing the fair basis of index futures (正逆價差). One row per day,
`{date, points, estimated}` plus a response-level `meta`.

- `estimated: false` — **realized** value, derived exactly from the total-return index vs
  price index spread (data from 2003). Non-ex days are ~0 (numerical noise ≤ 0.01 pt).
- `estimated: true` — **forecast** for future dates: announced-but-not-yet-ex dividends
  synthesized from per-stock weights, plus a last-year template for periods not announced
  yet. Future weekdays with no expected event are zero-filled, so cumulative sums over any
  window need no gap handling.
- `start` / `end` optional, strict `YYYY-MM-DD` (else 400). `end` is silently clamped to
  **today + 120 days** (two settlement cycles).
- The realized leg updates each trading day **~17:00 Taipei** (the total-return index
  publishes ~16:50); before that the latest realized row is the previous trading day.

```python
response = requests.get(
    f"{BASE_URL}/studio/market/twmarket/dividend_points",
    headers=headers, params={"start": "2026-08-01"}, timeout=60,
)
payload = response.json()
# {"data": [{"date": "2026-08-03", "points": 2.853, "estimated": false}, ...,
#           {"date": "2026-08-28", "points": 3.846, "estimated": true}, ...],
#  "meta": {"estimated_coverage": 0.9999, "degraded": false}}
```

`meta.estimated_coverage` is the fraction of TAIEX market-value weight whose inputs were
readable when synthesizing the estimated leg (`null` when the range has no estimated
rows); `meta.degraded: true` flags a materially under-covered estimate — treat the
estimated leg as a lower bound in that case. Coverage below 90% is refused outright
(`503`) rather than served silently low.

Typical use (fair basis of TXF):
```python
import pandas as pd
df = pd.DataFrame(payload["data"])
future_div = df[df["estimated"]].set_index("date")["points"]
# fair basis at date t for settlement date T:
#   futures_price - (spot_index - future_div.loc[t_plus_1:T].sum())
```

Estimates far from settlement lean on the last-year template — more than ~2 weeks out,
expect part of the sum to be template-based rather than announced.

---

## Taiwan Futures OHLCV — 台灣期貨

```
GET /studio/market/twfutures/ohlcv/<symbol>/<schema>
```

`start` / `end` optional (YYYY-MM-DD). Data from 2013-12-30 (`1d`) and 2014-01-02 (intraday: `1m`/`5m`/`15m`/`30m`/`60m`). Intraday bars before 2017-05-15 cover the day session only — the night session (15:00–next day 05:00 Taipei) launched 2017-05-15, so bars-per-day jumps from ~300 to ~1140 at that boundary. Timestamps UTC. Requires API plan auth.

| `symbol` | 商品 |
|---|---|
| `TXF` | 台指期（大台，近月連續） |

| `schema` | 週期 | 單次最大範圍 |
|---|---|---|
| `1d` | 日K | 3650 天（10年） |
| `1m` | 分K | 31 天 |
| `5m` | 5分K | 62 天 |
| `15m` | 15分K | 93 天 |
| `30m` | 30分K | 186 天 |
| `60m` | 小時K | 365 天 |

超出限制回傳 400：`{"error": "date_range_too_large", "max_days": <n>}`

**大量歷史分線（回測）請改用 bulk export** — 直接下載該 symbol 該年的原始 1m parquet 檔（零伺服器運算），自行 resample 成需要的週期：

```
GET /studio/market/twfutures/ohlcv/<symbol>/export/<year>
```

- `year`：2014 ≤ year ≤ 當年，超出回 400
- 回傳 `application/octet-stream`（parquet 檔，欄位 `ts`/`open`/`high`/`low`/`close`/`volume`，1m bars）
- 該 symbol 該年無資料 → 404 `{"error": "no_data"}`
- 一年一請求：抓 7 年只要 7 次請求，取代分段 JSON 的近百次

```python
import io
import pandas as pd

r = requests.get(
    f"{BASE_URL}/studio/market/twfutures/ohlcv/TXF/export/2024",
    headers=headers, timeout=120,
)
raw = pd.read_parquet(io.BytesIO(r.content))          # 1m bars
raw.index = pd.to_datetime(raw["ts"], utc=True)
bars_60m = (raw[["open", "high", "low", "close", "volume"]]
            .resample("60min")
            .agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                 close=("close", "last"), volume=("volume", "sum"))
            .dropna(subset=["open"]))                  # 與伺服器 resample 語義一致
```

```python
# 台指期日K
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(
    f"{BASE_URL}/studio/market/twfutures/ohlcv/TXF/1d",
    headers=headers, params=params, timeout=60,
)
data = response.json()["data"]
# [{"ts": "2024-01-02 00:00:00+00:00", "open": 17500.0, "high": 17620.0,
#   "low": 17480.0, "close": 17610.0, "volume": 98234}, ...]

# 分K（需拆分，每次最多 31 天）
from datetime import date, timedelta

def fetch_txf_chunked(schema, start, end, chunk_days=28):
    result = []
    cur = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    while cur < end_date:
        chunk_end = min(cur + timedelta(days=chunk_days), end_date)
        resp = requests.get(
            f"{BASE_URL}/studio/market/twfutures/ohlcv/TXF/{schema}",
            headers=headers,
            params={"start": cur.isoformat(), "end": chunk_end.isoformat()},
            timeout=60,
        )
        result.extend(resp.json().get("data", []))
        cur = chunk_end
    return result

bars = fetch_txf_chunked("1m", "2026-05-01", "2026-05-25")
```

**Response fields:**
| Field | Description |
|---|---|
| `ts` | Bar 開盤時間（UTC ISO 字串） |
| `open` / `high` / `low` / `close` | 指數點數 |
| `volume` | 成交口數 |

---

## Taiwan Option Put/Call Ratio — 台指選擇權買賣權未平倉量比率

```
GET /studio/market/twfutures/option/pcr
```

`start` / `end` optional (YYYY-MM-DD). Data from 2001-12-24. Daily, trading days only. Requires API plan auth. Official TAIFEX 買賣權未平倉量比率% (OI-based) — **not** derived from option institutional / large-trader data.

```python
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(
    f"{BASE_URL}/studio/market/twfutures/option/pcr",
    headers=headers, params=params, timeout=60,
)
data = response.json()["data"]
# [{"date": "2024-01-02", "pcr": 78.5}, {"date": "2024-01-03", "pcr": 81.2}, ...]
```

**Response fields:**
| Field | Description |
|---|---|
| `date` | 交易日（YYYY-MM-DD） |
| `pcr` | 買賣權未平倉量比率%（float） |

---

## Taiwan Futures Bid/Ask Volume — 台指期內外盤

```
GET /studio/market/twfutures/bid_ask_vol/<symbol>
```

`start` / `end` optional (YYYY-MM-DD). Data from 2018-02-22. Timestamps UTC. Max 31 days per request. Requires API plan auth.

1-minute bars aggregated from tick data. Day session (08:45–13:45 Taipei) and night session (15:00–next day 05:00 Taipei) are both included.

| `symbol` | 商品 |
|---|---|
| `TXF` | 台指期（大台，近月連續） |

```python
# 台指期內外盤（單日，含日盤+夜盤）
params = {"start": "2026-05-29", "end": "2026-05-29"}
response = requests.get(
    f"{BASE_URL}/studio/market/twfutures/bid_ask_vol/TXF",
    headers=headers, params=params, timeout=60,
)
data = response.json()["data"]
# [{"ts": "2026-05-29 00:45:00+00:00", "bid_vol": 669, "ask_vol": 447, "total_vol": 1156}, ...]

# 跨多天需拆分（每次最多 31 天）
def fetch_bid_ask_vol_chunked(start, end, chunk_days=28):
    result = []
    cur = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    while cur < end_date:
        chunk_end = min(cur + timedelta(days=chunk_days), end_date)
        resp = requests.get(
            f"{BASE_URL}/studio/market/twfutures/bid_ask_vol/TXF",
            headers=headers,
            params={"start": cur.isoformat(), "end": chunk_end.isoformat()},
            timeout=60,
        )
        result.extend(resp.json().get("data", []))
        cur = chunk_end
    return result
```

**Response fields:**
| Field | Description |
|---|---|
| `ts` | Bar 開盤時間（UTC ISO 字串） |
| `bid_vol` | 內盤成交量（tick 打到 bid，賣方主動） |
| `ask_vol` | 外盤成交量（tick 打到 ask，買方主動） |
| `total_vol` | 總成交量（含無法分類的 tick） |

---

## CME / ICE Futures OHLCV — 原油/黃金/Brent 期貨

```
GET /studio/market/db/ohlcv/<dataset>/<symbol>/<schema>
```

`start` / `end` optional (ISO 8601, e.g. `2024-01-01`). Data from 2010-06-06. Timestamps UTC.

| `dataset` | `symbol` | 商品 |
|---|---|---|
| `GLBX.MDP3` | `CL` | WTI 原油期貨（CME NYMEX，近月連續） |
| `GLBX.MDP3` | `GC` | 黃金期貨（CME COMEX，近月連續） |
| `IFEU.IMPACT` | `BRN` | Brent 原油期貨（ICE，近月連續） |

| `schema` | 週期 | 單次最大範圍 |
|---|---|---|
| `ohlcv-1d` | 日K | 3650 天（10年） |
| `ohlcv-1h` | 小時K | 730 天（2年） |
| `ohlcv-1m` | 分K | **30 天** |

超出限制回傳 400：`{"error": "date_range_too_large", "max_days": <n>}`
→ 需拆分多次請求、分段拼接。拉長歷史時每個 chunk 約 6 秒，年度分K 約 1.5 分鐘。

```python
# 分段拉取長歷史（以 ohlcv-1m 為例，chunk_days=30）
from datetime import date, timedelta

def fetch_ohlcv_chunked(dataset, symbol, schema, start, end, chunk_days=30):
    result = []
    cur = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    while cur < end_date:
        chunk_end = min(cur + timedelta(days=chunk_days), end_date)
        resp = requests.get(
            f"{BASE_URL}/studio/market/db/ohlcv/{dataset}/{symbol}/{schema}",
            headers=headers,
            params={"start": cur.isoformat(), "end": chunk_end.isoformat()},
            timeout=30,
        )
        result.extend(resp.json().get("data", []))
        cur = chunk_end
    return result

# 近一年 WTI 原油分K
bars = fetch_ohlcv_chunked("GLBX.MDP3", "CL", "ohlcv-1m", "2025-05-01", "2026-05-01")
```

```python
# WTI 原油日K
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(
    f"{BASE_URL}/studio/market/db/ohlcv/GLBX.MDP3/CL/ohlcv-1d",
    headers=headers, params=params, timeout=60,
)
data = response.json()["data"]
# [{"ts": "2024-01-02 00:00:00+00:00", "open": 72.50, "high": 73.10,
#   "low": 71.80, "close": 72.90, "volume": 180432}, ...]

# Brent 原油小時K
response = requests.get(
    f"{BASE_URL}/studio/market/db/ohlcv/IFEU.IMPACT/BRN/ohlcv-1h",
    headers=headers, params={"start": "2024-01-01"}, timeout=60,
)

# 黃金期貨分K
response = requests.get(
    f"{BASE_URL}/studio/market/db/ohlcv/GLBX.MDP3/GC/ohlcv-1m",
    headers=headers, params={"start": "2026-05-10", "end": "2026-05-11"}, timeout=60,
)
```

**Response fields:**
| Field | Description |
|---|---|
| `ts` | Bar 開盤時間（UTC ISO 字串） |
| `open` / `high` / `low` / `close` | 美元（原油單位：USD/桶；黃金：USD/oz） |
| `volume` | 合約口數 |

Note: 資料有約 4 小時延遲，最新幾小時不可用。

---

## Economic Calendar — 總經事件行事曆

```
GET /studio/market/anue/economic_calendar
```

全球總經事件的發布時間、市場預期值、前值與實際值（授權資料源）。所有參數皆選填；不帶參數時回傳完整清單（約 1,400 筆），**務必用參數篩選**。

| Param | Description |
|---|---|
| `start` / `end` | `YYYY-MM-DD`，台北日期，含頭含尾 |
| `country` | ISO 兩碼，逗號分隔，如 `US,CN,TW` |
| `max_priority` | 只回 `priority <=` 此值。**1 最重要、3 最不重要**，所以「只要大事件」是 `max_priority=1` |
| `limit` | 筆數上限（依事件時間排序後截斷） |
| `lang` | `zh` / `en`，指標與國名的顯示語言；伺服器只換掉對照表裡有的名稱，`en` 會拿到中英混雜 |

資料是**滾動約五週的窗口**（前一個月加未來數週），不是歷史庫；區間落在窗外會回空陣列而非錯誤。

```python
params = {"start": "2026-07-28", "end": "2026-07-31", "country": "US,CN", "max_priority": 2}
response = requests.get(
    f"{BASE_URL}/studio/market/anue/economic_calendar",
    headers=headers, params=params, timeout=60,
)
data = response.json()
# [{"startDate": 1785715200, "time": "20:30", "countryId": "US", "countryName": "美國",
#   "subjectTitle": "<2季>", "subject": "GDP成長率(QoQ)初值", "unit": "%",
#   "predict": 1.6, "last": 2.1, "real": None, "priority": 3}, ...]
```

**Response fields:**
| Field | Description |
|---|---|
| `startDate` | 事件當天（台北日期）的 epoch 秒 |
| `time` | `HH:MM`，**台北時間**；部分事件未公布時間，為 `null` |
| `countryId` / `countryName` | ISO 兩碼 / 中文國名 |
| `subject` / `subjectTitle` | 指標名稱 / 期別（如 `<7月>`、`<2季>`） |
| `predict` | 市場預期值（consensus）；未提供為 `null` |
| `last` | 前值 |
| `real` | 實際值；尚未公布為 `null` |
| `unit` | 單位（`%`、`point`、`億USD` …） |
| `priority` | 1–3，**1 最重要**（1 = 非農/利率決議，3 = 鑽機數這類） |

**這是總經事件與其數字的唯一來源——不要改用網路搜尋，也不要憑記憶填數字。** 泛用搜尋會撿到行事曆聚合站,那些表格本身就有錯（實測有站把已公布的實際值當成預期值），沒被頁面涵蓋的欄位則會被訓練資料填空：連「前值」這種唯一解的數字都寫錯過。這支查不到的就說查不到。

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
| `oi_imbalance` | `{"-": 0.12}` — OI imbalance (full detail table: `/oi_imbalance/get_overview_data`) |

`fields` = indicator metadata. `note` = color ranges. `""` = insufficient data.

Use `statistics.up_prob` and `statistics.exp_value` for screening. Always check `is_data_sufficient` before using `statistics`.
