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

## Usage Guidelines

- If the user asks to **compare multiple coins**, **recommend a coin**, **rank coins**, **find the best/worst performing**, or **screen across the market** — always use `alpha_table` first. It returns the latest alpha for all symbols in a single request.
- Only use individual `get_alpha` endpoints when the user asks for the **historical time series** of a specific coin.

## Authentication

All requests require headers:
```
api-key: $blave_api_key
secret-key: $blave_secret_key
```

**Base URL:** `https://api.blave.org`

> For full Python examples, see `API.md`.

---

## Endpoints

### Alpha Table
`GET /alpha_table` — Latest alpha for all symbols across all indicators. No params.

**Response:** `{ data: { BTCUSDT: { holder_concentration: {"-": -2.35}, holder_concentration_chg: {"1h": -0.01, ...}, ... } }, fields: [...], note: {...} }`
- `fields` — indicator metadata (id, name, name_en, name_zh, param)
- `note` — color-coded interpretation ranges keyed by indicator ID
- Empty string `""` = insufficient data for that timeframe

---

### Kline（K線）
`GET /kline` — OHLCV candlestick data.

| Param | Required | Values |
|---|---|---|
| symbol | ✓ | e.g. `BTCUSDT` |
| period | ✓ | `5min` / `15min` / `1h` / `4h` / `8h` / `1d` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `[{ time, open, high, low, close }, ...]` — `time` is Unix timestamp UTC+0.

---

### Market Direction（市場方向）
`GET /market_direction/get_alpha` — Market direction alpha based on BTCUSDT. No `symbol` param.

| Param | Required | Values |
|---|---|---|
| period | ✓ | `5min` / `15min` / `1h` / `4h` / `8h` / `1d` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `{ data: { alpha: [...], timestamp: [...] } }`

---

### Market Sentiment（市場情緒）
`GET /market_sentiment/get_symbols` — Available symbols.
`GET /market_sentiment/get_alpha` — Time series + stat.

| Param | Required | Values |
|---|---|---|
| symbol | ✓ | e.g. `BTCUSDT` |
| period | ✓ | `5min` / `15min` / `1h` / `4h` / `8h` / `1d` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `{ data: { alpha: [...], timestamp: [...], stat: {...} } }`

---

### Capital Shortage（資金稀缺）
`GET /capital_shortage/get_alpha` — Market-wide indicator. No `symbol` param.

| Param | Required | Values |
|---|---|---|
| period | ✓ | `5min` / `15min` / `1h` / `4h` / `8h` / `1d` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `{ data: { alpha: [...], timestamp: [...], stat: {...} } }`

---

### Holder Concentration（籌碼集中度）
`GET /holder_concentration/get_symbols` — Available symbols.
`GET /holder_concentration/get_alpha` — Time series + stat. Higher alpha = more concentrated holdings.

| Param | Required | Values |
|---|---|---|
| symbol | ✓ | e.g. `BTCUSDT` |
| period | ✓ | `5min` / `15min` / `1h` / `4h` / `8h` / `1d` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `{ data: { alpha: [...], timestamp: [...], stat: {...} } }`

---

### Taker Intensity（多空力道）
`GET /taker_intensity/get_symbols` — Available symbols.
`GET /taker_intensity/get_alpha` — Time series + stat. Positive = taker buying; negative = taker selling.

| Param | Required | Values |
|---|---|---|
| symbol | ✓ | e.g. `BTCUSDT` |
| period | ✓ | `5min` / `15min` / `1h` / `4h` / `8h` / `1d` |
| timeframe | — | `15min` / `1h` / `4h` / `8h` / `24h` (default) / `3d` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `{ data: { alpha: [...], timestamp: [...], stat: {...} } }`

---

### Whale Hunter（巨鯨警報）
`GET /whale_hunter/get_symbols` — Available symbols.
`GET /whale_hunter/get_alpha` — Time series + stat.

| Param | Required | Values |
|---|---|---|
| symbol | ✓ | e.g. `BTCUSDT` |
| period | ✓ | `5min` / `15min` / `1h` / `4h` / `8h` / `1d` |
| timeframe | — | `15min` / `1h` / `4h` / `8h` / `24h` (default) / `3d` |
| score_type | — | `score_oi` (default) / `score_volume` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `{ data: { alpha: [...], timestamp: [...], stat: {...} } }`

---

### Squeeze Momentum（擠壓動能）
`GET /squeeze_momentum/get_symbols` — Available symbols.
`GET /squeeze_momentum/get_alpha` — Time series + stat + scolor. Period fixed to `1d`.

| Param | Required | Values |
|---|---|---|
| symbol | ✓ | e.g. `BTCUSDT` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `{ data: { alpha: [...], timestamp: [...], scolor: [...], stat: {...} } }`
- `scolor` — momentum direction color label, aligned with alpha/timestamp.

---

### Blave Top Trader Exposure（頂級交易員曝險）
`GET /blave_top_trader/get_exposure` — Top trader net exposure based on BTCUSDT. No `symbol` param.

| Param | Required | Values |
|---|---|---|
| period | ✓ | `5min` / `15min` / `1h` / `4h` / `8h` / `1d` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `{ data: { alpha: [...], timestamp: [...] } }`

---

## Common Response Fields

**`stat` object** (included in most `get_alpha` endpoints):
- `up_prob` — 24h probability of upward movement
- `exp_value` — 24h expected return value
- `avg_up_return` / `avg_down_return` — average 24h return when up/down
- `return_ratio` — ratio of avg up to avg down return (absolute)
- `is_data_sufficient` — whether enough data exists for reliable stats

**Date range:** max 1 year between `start_date` and `end_date`. If exceeded, `start_date` is auto-set to 1 year before `end_date`.

**Timestamps:** all Unix timestamps are UTC+0.
