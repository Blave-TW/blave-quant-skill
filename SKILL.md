---
name: blave-quant
description: "Use for: (1) Blave market alpha data — 籌碼集中度 Holder Concentration, 多空力道 Taker Intensity, 巨鯨警報 Whale Hunter, 擠壓動能 Squeeze Momentum, 市場方向 Market Direction, 資金稀缺 Capital Shortage, 板塊輪動 Sector Rotation, Blave頂尖交易員 Top Trader Exposure, kline, alpha table, 市場情緒 Market Sentiment, screener saved conditions, Hyperliquid top trader tracking (leaderboard, positions, history, performance, bucket stats); (2) BitMart futures/contract trading — opening/closing positions, leverage, plan orders, TP/SL, trailing stops, account management, sub-account transfers; (3) BitMart spot trading — buy/sell, limit/market orders, account balance, order history, sub-account transfers; (4) OKX trading — spot and perpetual swap, order placement, positions, balance; (5) Bybit trading — spot and derivatives/perpetual swap, order placement, positions, balance, TP/SL; (6) BingX trading — spot and perpetual swap, order placement, position management, leverage, TWAP orders, OCO orders; (7) Bitget trading — spot and futures, order placement, position management, leverage, plan orders; (8) Binance trading — spot and USDS-M futures, order placement, positions, leverage, algo orders, OCO/OTO/OTOCO; (9) Bitfinex trading & funding — spot, margin, funding/lending (submit offers, loans, credits), wallet transfers."
version: 1.6.1
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
        - BITFINEX_API_KEY
        - BITFINEX_API_SECRET
---

# Blave Quant Skill

Eight capabilities: **Blave** market alpha data, **BitMart** trading, **OKX** trading, **Bybit** trading, **BingX** trading, **Bitget** trading, **Binance** trading, **Bitfinex** trading & funding.

## Examples

Workflow templates for common use cases. **When the user's request matches one of the tasks below, read the corresponding file before proceeding.**

| File | When to read |
|---|---|
| `examples/hyperliquid-copy-trading.md` | User wants to find traders to follow / copy trade on Hyperliquid |
| `examples/blave-alpha-screening.md` | User wants to screen or find high-conviction / small-cap tokens |
| `examples/backtest-holder-concentration.md` | User wants to backtest a strategy using Blave alpha signals |
| `examples/truth-social-trump-monitor.md` | User wants to monitor Trump's Truth Social posts with translation |
| `examples/btc-etf-flow-monitor.md` | User wants to track Bitcoin ETF flows / institutional accumulation (BlackRock IBIT etc.) |
| `examples/bitfinex-auto-lending.md` | User wants to auto-lend on Bitfinex (rate-adaptive period + ladder offers) |

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

# Exchange Trading

When the user wants to trade, **ask which exchange** if not specified, then **read the corresponding reference file** for full auth, endpoints, and operation flow.

| Exchange | .env keys | Reference |
|---|---|---|
| BitMart (Futures) | `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO` | `references/bitmart-futures-skill.md` |
| BitMart (Spot) | same as above | `references/bitmart-spot-skill.md` |
| OKX | `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE` | `references/okx-skill.md` |
| Bybit | `BYBIT_API_KEY`, `BYBIT_API_SECRET` | `references/bybit-skill.md` |
| BingX | `BINGX_API_KEY`, `BINGX_SECRET_KEY` | `references/bingx-skill.md` |
| Bitget | `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE` | `references/bitget-skill.md` |
| Binance | `BINANCE_API_KEY`, `BINANCE_SECRET_KEY` | `references/binance-skill.md` |
| Bitfinex | `BITFINEX_API_KEY`, `BITFINEX_API_SECRET` | `references/bitfinex-skill.md` |

**Workflow for all exchanges:**
1. Verify credentials from `.env` — if missing, **STOP**
2. READ → call, parse, display
3. WRITE → present summary → ask **"CONFIRM"** → execute
4. After order → verify status

