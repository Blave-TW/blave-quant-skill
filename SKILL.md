---
name: blave-quant
description: "Use for: (1) Blave market alpha data — 籌碼集中度 Holder Concentration, 多空力道 Taker Intensity, 巨鯨警報 Whale Hunter, 擠壓動能 Squeeze Momentum, 市場方向 Market Direction, 資金稀缺 Capital Shortage, 板塊輪動 Sector Rotation, Blave頂尖交易員 Top Trader Exposure, kline, alpha table, 市場情緒 Market Sentiment, screener saved conditions, Hyperliquid top trader tracking (leaderboard, positions, history, performance, bucket stats); (2) BitMart futures/contract trading — opening/closing positions, leverage, plan orders, TP/SL, trailing stops, account management, sub-account transfers; (3) BitMart spot trading — buy/sell, limit/market orders, account balance, order history, sub-account transfers; (4) OKX trading — spot and perpetual swap, order placement, positions, balance; (5) Bybit trading — spot and derivatives/perpetual swap, order placement, positions, balance, TP/SL; (6) BingX trading — spot and perpetual swap, order placement, position management, leverage, TWAP orders, OCO orders; (7) Bitget trading — spot and futures, order placement, position management, leverage, plan orders; (8) Binance trading — spot and USDS-M futures, order placement, positions, leverage, algo orders, OCO/OTO/OTOCO."
version: 1.2.1
metadata:
  openclaw:
    emoji: "📊"
    homepage: https://blave.org
    requires:
      env:
        - blave_api_key
        - blave_secret_key
    optional:
      env:
        - BITMART_API_KEY
        - BITMART_API_SECRET
        - BITMART_API_MEMO
        - OKX_API_KEY
        - OKX_SECRET_KEY
        - OKX_PASSPHRASE
        - BYBIT_API_KEY
        - BYBIT_API_SECRET
        - BINGX_API_KEY
        - BINGX_SECRET_KEY
        - BITGET_API_KEY
        - BITGET_SECRET_KEY
        - BITGET_PASSPHRASE
        - BINANCE_API_KEY
        - BINANCE_SECRET_KEY
---

# Blave Quant Skill

Seven capabilities: **Blave** market alpha data, **BitMart** trading, **OKX** trading, **Bybit** trading, **BingX** trading, **Bitget** trading, **Binance** trading.

## Examples

Workflow templates for common use cases. **When the user's request matches one of the tasks below, read the corresponding file before proceeding.**

| File | When to read |
|---|---|
| `examples/hyperliquid-copy-trading.md` | User wants to find traders to follow / copy trade on Hyperliquid |
| `examples/blave-alpha-screening.md` | User wants to screen or find high-conviction / small-cap tokens |
| `examples/backtest-holder-concentration.md` | User wants to backtest a strategy using Blave alpha signals |

## Output Rule — Chart Auto-Send

**Whenever you generate a chart or visualization, send it through the user's notification channel (e.g., Telegram) if and only if the user has explicitly configured one in their environment. Only send to the channel the user themselves set up — never infer or guess an endpoint. If no channel is configured, display the chart inline as usual.**

---

# PART 1: Blave Market Data

## Setup

No API key or 401/403 → guide user to:

- Subscribe: **[https://blave.org/landing/en/pricing](https://blave.org/landing/en/pricing)** — $629/year, 14-day free trial
- Create key: **[https://blave.org/landing/en/api?tab=blave](https://blave.org/landing/en/api?tab=blave)**

Add to `.env`: `blave_api_key=...` and `blave_secret_key=...`

**Auth headers:** `api-key: $blave_api_key` | `secret-key: $blave_secret_key`

**Base URL:** `https://api.blave.org` | **Support:** info@blave.org | [Discord](https://discord.gg/D6cv5KDJja)

## Limits

| Item        | Value                                                   |
| ----------- | ------------------------------------------------------- |
| Rate limit  | 100 req / 5 min — `429` if exceeded, resets after 5 min |
| Data update | Every 5 minutes                                         |
| History     | Max 1 year **per request** (use multiple requests with different date ranges to retrieve data beyond 1 year) |
| Timestamps  | UTC+0                                                   |

## Usage Guidelines

- **Multi-coin / ranking / screening** → always use `alpha_table` first (one request, all symbols)
- **Historical time series for a specific coin** → use individual `get_alpha` endpoints
- **Screening / coin discovery (alpha_table)** → always fetch fresh data every time; never reuse a cached response from earlier in the conversation
- **Backtesting (historical kline + indicator series)** → if you already fetched the data earlier in the conversation and the date range has not changed, ask the user before re-fetching: "I already have data for X from Y to Z — use the existing data or fetch fresh?"

## Endpoints

### `GET /price` — Current price + 24h change

`symbol` (required) → `{"symbol": "BTCUSDT", "price": 95000.0, "change_24h": 2.5}`

### `GET /alpha_table` — All symbols, latest alpha, no params

Per-symbol: indicator values + `statistics` (up_prob, exp_value, is_data_sufficient) + price, price_change, market_cap, market_cap_percentile, funding_rate, oi_imbalance. `""` = insufficient data. → Full field reference: `references/blave-api.md`

---

### `GET /kline` — OHLCV candles

`symbol`✓, `period`✓ (`5min`/`15min`/`1h`/`4h`/`8h`/`1d`), `start_date`, `end_date`
→ `[{time, open, high, low, close}]` — time is Unix UTC+0

**`period` format:** `{number}{unit}` — unit: `min` / `h` / `d`. Examples: `15min`, `1h`, `4h`, `1d`, `7d`, `30d`.

**Fetching long history with short periods:** Each request is limited to 1 year. For short periods (e.g. `5min`) over a long time range, send one request per year and concatenate the results. Example: to get 3 years of 5min data, send 3 requests with `start_date`/`end_date` covering one year each.

### `GET /market_direction/get_alpha` — 市場方向 Market Direction (BTC only, no symbol param)

`period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp}}`

### `GET /market_sentiment/get_alpha` — 市場情緒 Market Sentiment

`symbol`✓, `period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp, stat}}`

### `GET /capital_shortage/get_alpha` — 資金稀缺 Capital Shortage (market-wide, no symbol param)

`period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp, stat}}`

### `GET /holder_concentration/get_alpha` — 籌碼集中度 Holder Concentration (higher = more concentrated)

`symbol`✓, `period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp, stat}}`

### `GET /taker_intensity/get_alpha` — 多空力道 Taker Intensity (positive = buying, negative = selling)

`symbol`✓, `period`✓, `timeframe` (`15min`/`1h`/`4h`/`8h`/`24h`/`3d`), `start_date`, `end_date`

### `GET /whale_hunter/get_alpha` — 巨鯨警報 Whale Hunter

`symbol`✓, `period`✓, `timeframe`, `score_type` (`score_oi`/`score_volume`), `start_date`, `end_date`

### `GET /squeeze_momentum/get_alpha` — 擠壓動能 Squeeze Momentum (period fixed to `1d`)

`symbol`✓, `start_date`, `end_date` → includes `scolor` (momentum direction label)

### `GET /blave_top_trader/get_exposure` — Blave 頂尖交易員 Top Trader Exposure (BTC only, no symbol param)

`period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp}}`

### `GET /sector_rotation/get_history_data` — 板塊輪動 Sector Rotation, no params

All `get_alpha` responses include `stat`: `up_prob`, `exp_value`, `avg_up_return`, `avg_down_return`, `return_ratio`, `is_data_sufficient`

Each indicator also has a `get_symbols` endpoint to list available symbols.

---

### Screener

#### `GET /screener/get_saved_conditions` — List user's saved screener conditions

No params. Returns `{data: {<condition_id>: {filters: [...], ...}}}` — a map of condition IDs to their filter configs.

#### `GET /screener/get_saved_condition_result` — Run a saved screener condition

`condition_id`✓ (integer) → `{data: [<symbols matching filters>]}`

Returns 400 if `condition_id` is missing or not an integer; 404 if condition not found for user.

---

### Hyperliquid Top Trader Tracking

> Full response formats: `references/hyperliquid-api.md`

| Endpoint | Params | Cache |
|---|---|---|
| `GET /hyperliquid/leaderboard` | `sort_by` (accountValue/week/month/allTime) | 5 min |
| `GET /hyperliquid/traders` | — | — |
| `GET /hyperliquid/trader_position` | `address`✓ → perp positions, spot balances, net_equity | 15 s |
| `GET /hyperliquid/trader_history` | `address`✓ → fills with closedPnl, dir | 60 s |
| `GET /hyperliquid/trader_performance` | `address`✓ → `{chart: {timestamp, pnl}}` cumulative PnL | 60 s |
| `GET /hyperliquid/trader_open_order` | `address`✓ → open orders | 60 s |
| `GET /hyperliquid/top_trader_position` | — → aggregated long/short across top 100 | 5 min |
| `GET /hyperliquid/top_trader_exposure_history` | `symbol`✓, `period`✓, dates | — |
| `GET /hyperliquid/bucket_stats` | — → stats by account size bucket; 202 while warming up | ~5 min |

### TradingView Signal Stream (SSE)

Receive TradingView alerts in real time via Server-Sent Events.

**Endpoint:** `GET /sse/tradingview/stream?channel=<ch>&last_id=<id>`

**Event format:** `data: {"id": "1712054400000-0", ...alert_fields}`
- `id` — pass as `last_id` on reconnect to resume without losing signals
- Default (`last_id=$`) — only new signals; omit on first connect
- `: keepalive` sent every 15 s — ignore
- Buffer: last 1000 messages in Redis — short disconnections lose no data

> Full Python example with reconnect loop: `references/tradingview-stream.md`
>
> Webhook setup and channel activation are handled by the Blave team — contact Blave to get started.

---

> Python examples: `references/blave-api.md`
> Indicator interpretation: `references/blave-indicator-guide.md`

---

# PART 2: BitMart Futures Trading

**Base URL:** `https://api-cloud-v2.bitmart.com` | **Symbol:** `BTCUSDT` (no underscore) | **Success:** `code == 1000`

53 endpoints — full details in `references/bitmart-api-reference.md`

## Authentication

**Credentials** (from `.env`): `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`

No BitMart account? Register at **[https://www.bitmart.com/invite/cMEArf](https://www.bitmart.com/invite/cMEArf)**

Verify credentials before any private call. If missing — **STOP**.

| Level  | Endpoints          | Headers                                     |
| ------ | ------------------ | ------------------------------------------- |
| NONE   | Public market data | —                                           |
| KEYED  | Read-only private  | `X-BM-KEY`                                  |
| SIGNED | Write operations   | `X-BM-KEY` + `X-BM-SIGN` + `X-BM-TIMESTAMP` |

**Signature:** `HMAC-SHA256(secret, "{timestamp}#{memo}#{body}")` — GET body = `""`

**Always include `X-BM-BROKER-ID: BlaveData666666` on ALL requests.**

**IP Whitelist:** Use **public IP** (`curl https://checkip.amazonaws.com`), not private IP (`10.x`, `172.x`, `192.168.x`).

> Signature Python implementation and common mistakes: `references/bitmart-signature.md`

## Operation Flow

### Step 0: Credential Check

Verify `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`. If missing — **STOP**.

### Step 1.1: Query Positions (READ)

`GET /contract/private/position-v2` (KEYED, no signature needed)
Filter `current_amount != "0"` → display symbol, position_side, current_amount, entry_price, leverage, open_type, liquidation_price, unrealized_pnl

### Step 1.5: Pre-Trade Check (MANDATORY before open/leverage)

1. Call `GET /contract/private/position-v2?symbol=<SYMBOL>`
2. If `current_amount` non-zero → inherit `leverage` and `open_type`, do NOT override
3. If user wants different values → **STOP**, warn to close position first

### Step 1.55: Pre-Mode-Switch Check

Confirm no positions (Step 1.5) AND no open orders (`GET /contract/private/get-open-orders`). If either exists → **STOP**.

### Step 1.6: TP/SL on Existing Position

`POST /contract/private/submit-tp-sl-order` — submit TP and SL as **two separate calls**

| Param             | Value                            |
| ----------------- | -------------------------------- |
| `type`            | `"take_profit"` or `"stop_loss"` |
| `side`            | `3` close long / `2` close short |
| `trigger_price`   | Activation price                 |
| `executive_price` | `"0"` for market fill            |
| `price_type`      | `1` last / `2` mark              |
| `plan_category`   | `2`                              |

### Step 2: Execute

- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

**submit-order rules:**

| Scenario      | Send                                                           | Omit                       |
| ------------- | -------------------------------------------------------------- | -------------------------- |
| Open, market  | symbol, side, type:`"market"`, size, leverage, open_type       | price                      |
| Open, limit   | symbol, side, type:`"limit"`, price, size, leverage, open_type | —                          |
| Close, market | symbol, side, type:`"market"`, size                            | price, leverage, open_type |
| Close, limit  | symbol, side, type:`"limit"`, price, size                      | leverage, open_type        |

### Step 3: Verify

- After open: `position-v2` → report entry price, size, leverage, liquidation price
- After close: `position-v2` → report realized PnL
- After order: `GET /contract/private/order` → confirm status

## Order Reference

**Side:** `1` Open Long / `2` Close Short / `3` Close Long / `4` Open Short

**Mode:** `1` GTC / `2` FOK / `3` IOC / `4` Maker Only

**Timestamps:** ms — always convert to local time for display.

## Error Handling

| Code               | Action                                                    |
| ------------------ | --------------------------------------------------------- |
| 30005              | Wrong signature → see `references/bitmart-signature.md`   |
| 30007              | Timestamp drift → sync clock                              |
| 40012/40040        | Leverage/mode conflict → inherit existing position values |
| 40027/42000        | Insufficient balance → transfer from spot or reduce size  |
| 429                | Rate limited → wait                                       |
| 403/503 Cloudflare | Wait 30-60s, retry max 3×                                 |

## Spot ↔ Futures Transfer

Present summary → ask **"CONFIRM"** → execute.

**Endpoint:** `POST https://api-cloud-v2.bitmart.com/account/v1/transfer-contract` (SIGNED)

| Param      | Value                                        |
| ---------- | -------------------------------------------- |
| `currency` | `USDT` only                                  |
| `amount`   | transfer amount                              |
| `type`     | `"spot_to_contract"` or `"contract_to_spot"` |

Rate limit: 1 req/2sec. ⚠️ `/spot/v1/transfer-contract` does NOT exist.

## Security

- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Futures trading carries significant risk of loss."

## References

- `references/bitmart-api-reference.md` — 53 endpoints
- `references/bitmart-signature.md` — Python signature implementation
- `references/bitmart-open-position.md` / `bitmart-close-position.md` / `bitmart-plan-order.md` / `bitmart-tp-sl.md`

---

# PART 3: BitMart Spot Trading

**Base URL:** `https://api-cloud.bitmart.com` | **Symbol:** `BTC_USDT` (underscore) | **Success:** `code == 1000`

34 endpoints — full details in `references/bitmart-spot-api-reference.md`

## Authentication

Same signature method as Futures. Credentials from `.env`: `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`

No BitMart account? Register at **[https://www.bitmart.com/invite/cMEArf](https://www.bitmart.com/invite/cMEArf)**

**Always include `X-BM-BROKER-ID: BlaveData666666` on ALL requests.**

**IP Whitelist:** Use **public IP** (`curl https://checkip.amazonaws.com`), not private IP.

> Signature Python implementation: `references/bitmart-signature.md`

## Operation Flow

### Step 0: Credential Check

Verify credentials. If missing — **STOP**.

### Step 1: Identify Intent

- **READ:** market data, balance, order history
- **WRITE:** submit/cancel orders, withdraw
- **TRANSFER:** spot ↔ futures → see Part 2 **Spot ↔ Futures Transfer**

### Step 2: Execute Orders

- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

**Endpoint:** `POST /spot/v2/submit_order`

| Scenario     | side   | type     | Key param                   |
| ------------ | ------ | -------- | --------------------------- |
| Buy, market  | `buy`  | `market` | `notional` (USDT to spend)  |
| Buy, limit   | `buy`  | `limit`  | `size` (base qty) + `price` |
| Sell, market | `sell` | `market` | `size` (base qty)           |
| Sell, limit  | `sell` | `limit`  | `size` + `price`            |

> Market buy uses `notional`, NOT `size`.

### Step 3: Verify

After order → query order detail. After cancel → check open orders.

## Order Reference

**Side:** `buy` / `sell` | **Type:** `limit` / `market` / `limit_maker` / `ioc`

**Status:** `new` / `partially_filled` / `filled` / `canceled` / `partially_canceled`

**Timestamps:** ms — always convert to local time.

## Error Handling

| Code               | Action                                                  |
| ------------------ | ------------------------------------------------------- |
| 30005              | Wrong signature → see `references/bitmart-signature.md` |
| 30007              | Timestamp drift → sync clock                            |
| 50000              | Insufficient balance                                    |
| 429                | Rate limited → wait                                     |
| 403/503 Cloudflare | Wait 30-60s, retry max 3×                               |

## Security

- WRITE operations require **"CONFIRM"**
- "Not financial advice. Spot trading carries risk of loss."

## References

- `references/bitmart-spot-api-reference.md` — 34 endpoints
- `references/bitmart-signature.md` — Python signature implementation
- `references/bitmart-spot-authentication.md` / `bitmart-spot-scenarios.md`

---

# PART 4: OKX Trading

**Base URL:** `https://www.okx.com` | **Spot:** `BTC-USDT` | **Swap:** `BTC-USDT-SWAP` | **Success:** `"code": "0"`

Full details in `references/okx-api-reference.md`

## Authentication

**Credentials** (from `.env`): `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE`

No OKX account? Register at **[https://okx.com/join/58510434](https://okx.com/join/58510434)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `Base64(HMAC-SHA256(secret, timestamp + METHOD + requestPath + body))`
- `timestamp` format: `2024-01-01T00:00:00.000Z` (ISO 8601 ms UTC)
- GET body = `""`

**Headers:** `OK-ACCESS-KEY` + `OK-ACCESS-SIGN` + `OK-ACCESS-TIMESTAMP` + `OK-ACCESS-PASSPHRASE` + `User-Agent: Mozilla/5.0`

**`User-Agent` is required on ALL OKX requests.** Omitting it returns `403 Error code 1010`.

**Broker code: `"tag": "96ee7de3fd4bBCDE"` — MANDATORY on every POST that creates or modifies an order. No exceptions. If you write a POST body and forget `tag`, stop and add it before sending.**

## Operation Flow

### Step 0: Credential Check
Verify `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE`. If missing — **STOP**.

### Step 1: Pre-Trade Check (Swap only)
`GET /api/v5/account/positions?instId=<SYMBOL>-SWAP` → if position exists, inherit `tdMode` and leverage.

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → `GET /api/v5/trade/order` → confirm status. After close → `GET /api/v5/account/positions`.

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged swap positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/okx-api-reference.md` — endpoints, signature, order params

---

# PART 5: Bybit Trading

**Base URL (Mainnet):** `https://api.bybit.com` | **Backup:** `https://api.bytick.com` | **Testnet:** `https://api-testnet.bybit.com`

**Spot:** `BTCUSDT` | **Perpetual:** `BTCUSDT` (Linear) | **Success:** `"retCode": 0`

## Authentication

**Credentials** (from `.env`): `BYBIT_API_KEY`, `BYBIT_API_SECRET`

No Bybit account? Register at **[https://partner.bybit.com/b/BLAVE](https://partner.bybit.com/b/BLAVE)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `HMAC-SHA256(secret, {timestamp}{apiKey}{recvWindow}{queryString|jsonBody})`
- GET: sign `{timestamp}{apiKey}{recvWindow}{queryString}`
- POST: sign `{timestamp}{apiKey}{recvWindow}{jsonBody}` — use **compact JSON** (no spaces, no newlines)

**Headers (all authenticated requests):**
```
X-BAPI-API-KEY: $BYBIT_API_KEY
X-BAPI-TIMESTAMP: <unix ms>
X-BAPI-SIGN: <hmac signature>
X-BAPI-RECV-WINDOW: 5000
referer: Ue001036
Content-Type: application/json   (POST only)
```

**`referer: Ue001036` is MANDATORY on every request — no exceptions.**

## Operation Flow

### Step 0: Credential Check
Verify `BYBIT_API_KEY`, `BYBIT_API_SECRET`. If missing — **STOP**. Default to **Mainnet** unless user explicitly requests Testnet.

### Step 1: Pre-Trade Check
`GET /v5/position/list?category=linear&symbol=<SYMBOL>` → if position exists, inherit side and leverage.

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → `GET /v5/order/realtime` → confirm status. After close → `GET /v5/position/list`.

## Key Endpoints

| Action | Method | Path |
|---|---|---|
| Market info | GET | `/v5/market/instruments-info` |
| Ticker | GET | `/v5/market/tickers` |
| Wallet balance | GET | `/v5/account/wallet-balance` |
| Place order | POST | `/v5/order/create` |
| Cancel order | POST | `/v5/order/cancel` |
| Open orders | GET | `/v5/order/realtime` |
| Positions | GET | `/v5/position/list` |
| Set leverage | POST | `/v5/position/set-leverage` |
| Set TP/SL | POST | `/v5/position/set-tpsl` |
| Order history | GET | `/v5/order/history` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

---

# PART 6: BingX Trading

**Base URL:** `https://open-api.bingx.com` | **Fallback:** `https://open-api.bingx.pro` | **Paper (VST):** `https://open-api-vst.bingx.com`

**Spot:** `BTC-USDT` | **Perpetual:** `BTC-USDT` | **Success:** `"code": 0`

42 swap endpoints + 17 spot endpoints — full details in `references/bingx-api-reference.md`

## Authentication

**Credentials** (from `.env`): `BINGX_API_KEY`, `BINGX_SECRET_KEY`

No BingX account? Register at **[https://bingxdao.com/invite/SU0SEU/](https://bingxdao.com/invite/SU0SEU/)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `HMAC-SHA256(secret, sorted_params_canonical_string)` → hex, appended as `&signature=<hex>`
- Collect all params + `timestamp` (Unix ms)
- Sort alphabetically by key, concatenate as `key=value&key=value`

**Headers (all requests):**
```
X-BX-APIKEY: <api_key>
X-SOURCE-KEY: BX-AI-SKILL
```

**`X-SOURCE-KEY: BX-AI-SKILL` is MANDATORY on every request — no exceptions.**

> Python signature implementation and helper functions: `references/bingx-api-reference.md`

## Operation Flow

### Step 0: Credential Check
Verify `BINGX_API_KEY`, `BINGX_SECRET_KEY`. If missing — **STOP**. Default to **Live** unless user explicitly requests paper trading (VST).

### Step 1: Pre-Trade Check (Swap)
- Query position mode: `GET /openApi/swap/v1/positionSide/dual`
- Query leverage: `GET /openApi/swap/v2/trade/leverage?symbol=<SYMBOL>`
- If position exists → inherit leverage and margin type, do NOT override

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → query order status. After close → query positions.

## Quick Reference

| Operation | Method | Path |
|---|---|---|
| Place swap order | POST | `/openApi/swap/v2/trade/order` |
| Cancel swap order | DELETE | `/openApi/swap/v2/trade/order` |
| Open swap orders | GET | `/openApi/swap/v2/trade/openOrders` |
| Order details | GET | `/openApi/swap/v2/trade/order` |
| Close all positions | POST | `/openApi/swap/v2/trade/closeAllPositions` |
| Set leverage | POST | `/openApi/swap/v2/trade/leverage` |
| Set margin mode | POST | `/openApi/swap/v2/trade/marginType` |
| Place spot order | POST | `/openApi/spot/v1/trade/order` |
| Cancel spot order | POST | `/openApi/spot/v1/trade/cancel` |
| Spot open orders | GET | `/openApi/spot/v1/trade/openOrders` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/bingx-api-reference.md` — 59 endpoints, Python signature, full params

---

# PART 7: Bitget Trading

**Base URL:** `https://api.bitget.com` | **Spot:** `BTCUSDT` | **Futures:** `BTCUSDT` + `productType=USDT-FUTURES` | **Success:** `"code": "00000"`

Full details in `references/bitget-api-reference.md`

## Authentication

**Credentials** (from `.env`): `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE`

No Bitget account? Register at **[https://www.bitget.com/](https://www.bitget.com/)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `Base64(HMAC-SHA256(secret, timestamp + METHOD + path + body))`
- `timestamp`: Unix milliseconds
- GET body = `""`
- POST body = compact JSON (no spaces)

**Headers (authenticated requests):**
```
ACCESS-KEY: <api_key>
ACCESS-SIGN: <base64 signature>
ACCESS-PASSPHRASE: <passphrase>
ACCESS-TIMESTAMP: <unix ms>
Content-Type: application/json
locale: en-US
```

> Python signature implementation: `references/bitget-api-reference.md`

## Operation Flow

### Step 0: Credential Check
Verify `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE`. If missing — **STOP**.

### Step 1: Pre-Trade Check (Futures)
- Query positions: `GET /api/v2/mix/position/all-position?productType=USDT-FUTURES`
- If position exists → inherit leverage and margin mode, do NOT override

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → query order status. After close → query positions.

## Quick Reference

| Operation | Method | Path |
|---|---|---|
| Spot balances | GET | `/api/v2/spot/account/assets` |
| Futures account | GET | `/api/v2/mix/account/accounts?productType=USDT-FUTURES` |
| All balances | GET | `/api/v2/account/all-account-balance` |
| Place spot order | POST | `/api/v2/spot/trade/place-order` |
| Cancel spot order | POST | `/api/v2/spot/trade/cancel-order` |
| Spot open orders | GET | `/api/v2/spot/trade/unfilled-orders` |
| Place futures order | POST | `/api/v2/mix/order/place-order` |
| Cancel futures order | POST | `/api/v2/mix/order/cancel-order` |
| Futures positions | GET | `/api/v2/mix/position/all-position` |
| Set leverage | POST | `/api/v2/mix/account/set-leverage` |
| Set margin mode | POST | `/api/v2/mix/account/set-margin-mode` |
| Spot ticker | GET | `/api/v2/spot/market/tickers` |
| Futures ticker | GET | `/api/v2/mix/market/ticker` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/bitget-api-reference.md` — spot + futures endpoints, Python signature

---

# PART 8: Binance Trading

**Spot Base URL:** `https://api.binance.com` | **Futures Base URL:** `https://fapi.binance.com`

**Spot:** `BTCUSDT` | **Futures:** `BTCUSDT` | **Testnet:** `https://testnet.binance.vision` (spot) / `https://demo-fapi.binance.com` (futures)

Full details in `references/binance-api-reference.md`

## Authentication

**Credentials** (from `.env`): `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`

No Binance account? Register at **[https://www.binance.com/](https://www.binance.com/)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `HMAC-SHA256(secret, queryString + requestBody)` → hex
- `timestamp`: Unix milliseconds (always required)
- `signature` must be the **last** parameter

**Headers:**
```
X-MBX-APIKEY: <api_key>
Content-Type: application/x-www-form-urlencoded   (POST)
```

> Python signature implementation: `references/binance-api-reference.md`

## Operation Flow

### Step 0: Credential Check
Verify `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`. If missing — **STOP**. Default to **Mainnet** unless user explicitly requests Testnet.

### Step 1: Pre-Trade Check (Futures)
- Query positions: `GET /fapi/v2/positionRisk?symbol=<SYMBOL>`
- If position exists → inherit leverage and margin type, do NOT override

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → query order status. After close → query positions.

## Quick Reference — Spot

| Operation | Method | Path |
|---|---|---|
| Account info | GET | `/api/v3/account` |
| Place order | POST | `/api/v3/order` |
| Cancel order | DELETE | `/api/v3/order` |
| Cancel all | DELETE | `/api/v3/openOrders` |
| Query order | GET | `/api/v3/order` |
| Open orders | GET | `/api/v3/openOrders` |
| Order history | GET | `/api/v3/allOrders` |
| Trade fills | GET | `/api/v3/myTrades` |

## Quick Reference — USDS-M Futures

| Operation | Method | Path |
|---|---|---|
| Account balance | GET | `/fapi/v2/balance` |
| Account info | GET | `/fapi/v2/account` |
| Positions | GET | `/fapi/v2/positionRisk` |
| Place order | POST | `/fapi/v1/order` |
| Batch place | POST | `/fapi/v1/batchOrders` |
| Cancel order | DELETE | `/fapi/v1/order` |
| Cancel all | DELETE | `/fapi/v1/allOpenOrders` |
| Modify order | PUT | `/fapi/v1/order` |
| Open orders | GET | `/fapi/v1/openOrders` |
| Order history | GET | `/fapi/v1/allOrders` |
| Set leverage | POST | `/fapi/v1/leverage` |
| Set margin type | POST | `/fapi/v1/marginType` |
| Set position mode | POST | `/fapi/v1/positionSide/dual` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/binance-api-reference.md` — spot + futures endpoints, Python signature

