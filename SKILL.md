---
name: blave-quant
description: "Use for: (1) Blave market alpha data — holder concentration, taker intensity, whale hunter, squeeze momentum, market direction, capital shortage, sector rotation, top trader exposure, kline, alpha table; (2) BitMart futures/contract trading — opening/closing positions, leverage, plan orders, TP/SL, trailing stops, account management, sub-account transfers; (3) BitMart spot trading — buy/sell, limit/market orders, account balance, order history, sub-account transfers."
---

# Blave Quant Skill

This skill covers two capabilities:
1. **Blave** — Fetch crypto market alpha data from the Blave API
2. **BitMart Futures** — Trade crypto perpetual futures on BitMart exchange

---

# PART 1: Blave Market Data

## API Access & Troubleshooting

If the user does not have a Blave API key, or receives `401 Unauthorized` / `403 Forbidden`:

> 👉 Subscribe: **[https://blave.org/landing/en/pricing](https://blave.org/landing/en/pricing)**
> - **API Plan** — $629/year. **14-day free trial** for first-time subscribers (credit card required).
>
> 👉 Create API key: **[https://blave.org/landing/en/api?tab=blave](https://blave.org/landing/en/api?tab=blave)**

Add to `.env`:
```
blave_api_key=YOUR_API_KEY
blave_secret_key=YOUR_SECRET_KEY
```

## Usage Guidelines

- For **multi-coin queries, rankings, recommendations, or market screening** — always use `alpha_table` first (returns all symbols in one request).
- Use individual `get_alpha` endpoints only for **historical time series** of a specific coin.

## Authentication

```
api-key: $blave_api_key
secret-key: $blave_secret_key
```

**Base URL:** `https://api.blave.org`

> For Python examples, see `references/blave-api.md`.

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
`GET /market_direction/get_alpha` — Market direction alpha (BTCUSDT). No `symbol` param.

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
`GET /capital_shortage/get_alpha` — Market-wide. No `symbol` param.

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
`GET /blave_top_trader/get_exposure` — Top trader net exposure (BTCUSDT). No `symbol` param.

| Param | Required | Values |
|---|---|---|
| period | ✓ | `5min` / `15min` / `1h` / `4h` / `8h` / `1d` |
| start_date | — | `YYYY-MM-DD` |
| end_date | — | `YYYY-MM-DD` |

**Response:** `{ data: { alpha: [...], timestamp: [...] } }`

---

### Sector Rotation（板塊輪動）
`GET /sector_rotation/get_history_data` — No params.

---

## Blave Common Response Fields

**`stat` object:**
- `up_prob` — 24h probability of upward movement
- `exp_value` — 24h expected return value
- `avg_up_return` / `avg_down_return` — average 24h return when up/down
- `return_ratio` — ratio of avg up to avg down return (absolute)
- `is_data_sufficient` — whether enough data exists for reliable stats

**Date range:** max 1 year. **Timestamps:** UTC+0.

---

---

# PART 2: BitMart Futures Trading

## Overview

53 endpoints for contract trading. See `references/bitmart-api-reference.md` for full parameter details.

| # | Category | Endpoint | Type |
|---|---|---|---|
| 1-9 | Market Data | `/contract/public/...` | READ |
| 10-16 | Account | `/contract/private/assets-detail`, `position`, `position-v2`, `position-risk`, `get-position-mode`, `transaction-history`, `trade-fee-rate` | READ |
| 17-24 | Trading | `submit-order`, `cancel-order`, `cancel-orders`, `modify-limit-order`, `cancel-all-after`, `submit-leverage`, `set-position-mode`, `transfer-contract` | WRITE |
| 25-27 | Plan Order | `submit-plan-order`, `cancel-plan-order`, `modify-plan-order` | WRITE |
| 28-30 | TP/SL | `submit-tp-sl-order`, `modify-tp-sl-order`, `modify-preset-plan-order` | WRITE |
| 31-32 | Trailing | `submit-trail-order`, `cancel-trail-order` | WRITE |
| 33-38 | Order Query | `order`, `order-history`, `get-open-orders`, `current-plan-order`, `trades`, `transfer-contract-list` | READ |
| 39-44 | Sub-Account | Sub-account transfers and balance | READ/WRITE |
| 45-50 | Affiliate | Rebate and invite queries | READ |
| 51 | Simulated | `claim` (demo top-up) | WRITE |
| 52-53 | System | `time`, `service` | READ |

## Authentication

**Credentials** (from `.env`):
- `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`

**Before any private API call:** verify credentials are available. If missing — **STOP** and guide user to set them up.

**Key display:** show only first 5 + last 4 characters (e.g. `bmk12...9xyz`). Never display full secret or memo.

| Level | Endpoints | Headers |
|---|---|---|
| NONE | Public market data (1-9) | None |
| KEYED | Read-only private (10-16, 33-50) | `X-BM-KEY` |
| SIGNED | Write operations (17-32, 38-41, 51) | `X-BM-KEY` + `X-BM-SIGN` + `X-BM-TIMESTAMP` |

**Signature:**
```
timestamp = current UTC milliseconds
message   = "{timestamp}#{memo}#{request_body_json}"   # GET: body = ""
signature = HMAC-SHA256(secret, message) → hex
```

Required headers for SIGNED: `Content-Type: application/json`, `X-BM-KEY`, `X-BM-SIGN`, `X-BM-TIMESTAMP`, `User-Agent: bitmart-skills/futures/v2026.3.23`, `X-BM-BROKER-ID: BlaveData666666`

**Always include `X-BM-BROKER-ID: BlaveData666666` on ALL requests (NONE / KEYED / SIGNED).**

## API Base

- **Base URL:** `https://api-cloud-v2.bitmart.com`
- **Symbol format:** `BTCUSDT` (no underscore — unlike spot `BTC_USDT`)
- **Success:** `code == 1000`. Any other code is an error.

## Operation Flow

### Step 0: Credential Check
Verify `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`. If missing — **STOP**.

### Step 1: Identify Intent
- **READ:** market data, positions, balance, orders, funding rates
- **WRITE:** open/close position, leverage, plan order, TP/SL, trailing stop, transfer

### Step 1.5: Pre-Trade Position Check (MANDATORY for open/leverage)

Before opening a position or setting leverage:
1. Call `GET /contract/private/position-v2?symbol=<SYMBOL>`
2. Parse each row's `current_amount` as a number
3. **If any row's `current_amount` is non-zero:**
   - Inherit that row's `leverage` and `open_type` — do NOT send different values
   - If user wants different leverage/margin mode: **STOP** and warn to close position first
4. **If all rows are 0:** proceed with user-specified values

### Step 1.55: Pre-Mode-Switch Check (MANDATORY when changing position_mode)
1. Confirm Step 1.5 found no positions
2. Call `GET /contract/private/get-open-orders` — verify no open orders
3. If any open orders exist: **STOP**

### Step 1.6: TP/SL Rules (MANDATORY when setting TP/SL on existing position)

Use `POST /contract/private/submit-tp-sl-order` with these required params:

| Param | Value |
|---|---|
| `type` | `"take_profit"` or `"stop_loss"` |
| `side` | `3` (close long) or `2` (close short) |
| `trigger_price` | Activation price |
| `executive_price` | `"0"` for market fill |
| `price_type` | `1` last price / `2` mark price |
| `plan_category` | `2` (position TP/SL) |

Submit TP and SL as **two separate calls**.

### Step 2: Execute
- **READ:** call, parse, display
- **WRITE:** present summary → ask for **"CONFIRM"** → execute

**submit-order param rules:**

| Scenario | Send | Omit |
|---|---|---|
| Open, market | symbol, side, type:"market", size, leverage, open_type | price |
| Open, limit | symbol, side, type:"limit", price, size, leverage, open_type | — |
| Close, market | symbol, side, type:"market", size | price, leverage, open_type |
| Close, limit | symbol, side, type:"limit", price, size | leverage, open_type |

### Step 3: Verify (WRITE only)
- After open: call `position-v2` → report entry price, size, leverage, liquidation price
- After close: call `position-v2` → report realized PnL
- After order: call `GET /contract/private/order` → confirm status
- After cancel: call `get-open-orders` → confirm removed

## Order Reference

**Side:**
| Value | Hedge Mode | One-Way Mode |
|---|---|---|
| 1 | Open Long | Buy |
| 2 | Close Short | Buy (Reduce Only) |
| 3 | Close Long | Sell (Reduce Only) |
| 4 | Open Short | Sell |

**Mode:** `1` GTC / `2` FOK / `3` IOC / `4` Maker Only

**Timestamp units:** `create_time`/`update_time` = ms; K-line `timestamp` = seconds. Always convert to human-readable local time for display.

## Error Handling

| Code | Action |
|---|---|
| 1000 | Success |
| 30005 | Wrong signature — verify timestamp/memo/body format |
| 30007 | Timestamp out of window — sync system clock |
| 40012/40040 | Leverage/mode conflict — inherit existing position values |
| 40027/42000 | Insufficient balance — transfer from spot or reduce size |
| 429 | Rate limited — wait for reset |
| 403/503 + Cloudflare body | Wait 30-60s, retry max 3 times |

> Always send `User-Agent: bitmart-skills/futures/v2026.3.23` to avoid Cloudflare 1010 blocks.

## Security
- All WRITE operations require explicit **"CONFIRM"** before execution
- Leverage warning: always show liquidation price before opening leveraged positions
- Disclaimer: "Not financial advice. Futures trading carries significant risk of loss."

## References
- `references/bitmart-api-reference.md` — All 53 endpoints, full parameters and responses
- `references/bitmart-open-position.md` — Open position workflow
- `references/bitmart-close-position.md` — Close position workflow
- `references/bitmart-plan-order.md` — Plan order workflow
- `references/bitmart-tp-sl.md` — TP/SL workflow
- `references/blave-api.md` — Blave Python examples

---

---

# PART 3: BitMart Spot Trading

## Overview

34 endpoints for spot trading. See `references/bitmart-spot-api-reference.md` for full parameter details.

| # | Category | Endpoints | Type |
|---|---|---|---|
| 1-5 | Market Data | currencies, trading pairs, ticker, depth, history trades, kline | READ |
| 6-11 | Account | wallet balance, deposit address, withdraw, deposit/withdraw history | READ/WRITE |
| 12-19 | Trading | submit order, cancel order, cancel orders, batch submit/cancel | WRITE |
| 20-25 | Order Query | order detail, order history, open orders, trade list | READ |
| 26-30 | Margin | borrow, repay, borrow record, repay record, borrowing ratio | READ/WRITE |
| 31-34 | Sub-Account | sub-account transfer, sub-wallet | READ/WRITE |

## Authentication

**Credentials** (from `.env`):
- `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`

**Before any private API call:** verify credentials are available. If missing — **STOP** and guide user to set them up.

**Key display:** show only first 5 + last 4 characters. Never display full secret or memo.

| Level | Endpoints | Headers |
|---|---|---|
| NONE | Public market data | None |
| KEYED | Read-only private | `X-BM-KEY` |
| SIGNED | Write operations | `X-BM-KEY` + `X-BM-SIGN` + `X-BM-TIMESTAMP` |

**Signature:**
```
timestamp = current UTC milliseconds
message   = "{timestamp}#{memo}#{request_body_json}"   # GET: body = ""
signature = HMAC-SHA256(secret, message) → hex
```

Required headers for SIGNED: `Content-Type: application/json`, `X-BM-KEY`, `X-BM-SIGN`, `X-BM-TIMESTAMP`, `User-Agent: bitmart-skills/spot/v2026.3.23`, `X-BM-BROKER-ID: BlaveData666666`

**Always include `X-BM-BROKER-ID: BlaveData666666` on ALL requests (NONE / KEYED / SIGNED).**

## API Base

- **Base URL:** `https://api-cloud.bitmart.com`
- **Symbol format:** `BTC_USDT` (with underscore — unlike futures `BTCUSDT`)
- **Success:** `code == 1000`. Any other code is an error.

## Operation Flow

### Step 0: Credential Check
Verify `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`. If missing — **STOP**.

### Step 1: Identify Intent
- **READ:** market data, balance, order history
- **WRITE:** submit/cancel orders, withdraw, transfer

### Step 2: Execute
- **READ:** call, parse, display
- **WRITE:** present summary → ask for **"CONFIRM"** → execute

**submit-order param rules:**

| Scenario | side | type | Required params |
|---|---|---|---|
| Buy, market | `buy` | `market` | symbol, side, type, size (quote qty) |
| Buy, limit | `buy` | `limit` | symbol, side, type, price, size (base qty) |
| Sell, market | `sell` | `market` | symbol, side, type, size (base qty) |
| Sell, limit | `sell` | `limit` | symbol, side, type, price, size (base qty) |

### Step 3: Verify (WRITE only)
- After order: call order detail endpoint → confirm status
- After cancel: call open orders → confirm removed

## Order Reference

**Side:** `buy` / `sell`

**Type:** `limit` / `market` / `limit_maker` / `ioc`

**Order status:** `new` / `partially_filled` / `filled` / `canceled` / `partially_canceled`

**Timestamp units:** `create_time`/`update_time` = ms. Always convert to human-readable local time for display.

## Error Handling

| Code | Action |
|---|---|
| 1000 | Success |
| 30005 | Wrong signature — verify timestamp/memo/body format |
| 30007 | Timestamp out of window — sync system clock |
| 50000 | Insufficient balance — check wallet |
| 429 | Rate limited — wait for reset |
| 403/503 + Cloudflare body | Wait 30-60s, retry max 3 times |

> Always send `User-Agent: bitmart-skills/spot/v2026.3.23` to avoid Cloudflare 1010 blocks.

## Security
- All WRITE operations require explicit **"CONFIRM"** before execution
- Disclaimer: "Not financial advice. Spot trading carries risk of loss."

## References
- `references/bitmart-spot-api-reference.md` — All 34 endpoints, full parameters and responses
- `references/bitmart-spot-authentication.md` — Auth details and examples
- `references/bitmart-spot-scenarios.md` — Common trading scenarios
