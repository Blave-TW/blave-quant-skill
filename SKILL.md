---
name: blave-quant
description: "Use for: (1) Blave market alpha data — 籌碼集中度 Holder Concentration, 多空力道 Taker Intensity, 巨鯨警報 Whale Hunter, 擠壓動能 Squeeze Momentum, 市場方向 Market Direction, 資金稀缺 Capital Shortage, 板塊輪動 Sector Rotation (history + heat-map overview), OI 失衡 OI Imbalance, Blave頂尖交易員 Top Trader Exposure, kline (1min K線 included), alpha table, 市場情緒 Market Sentiment, screener saved conditions, Hyperliquid top trader tracking (leaderboard, positions, history, performance, bucket stats), Taiwan stock daily OHLCV, minute-line intraday OHLCV (1m/5m/15m/30m/60m/1d), forward-adjusted prices, institutional investor buy/sell, margin trading data, shareholding distribution, quarterly fundamental statements — income statement, balance sheet, cash flow, dividend events — cash/stock dividends with announce/ex/pay dates, market value ranking — whole-market market-cap snapshot / top-N stock pool, and broker/dealer daily buy/sell by branch (台股日K/現股分線/向後調整/三大法人/融資融券/股權持股分級表/綜合損益表/資產負債表/現金流量表/股利事件/市值排名/分點買賣超), plus Taiwan market-wide 大盤 series — TAIEX index daily OHLC, whole-market turnover, whole-market institutional net buy/sell, whole-market margin balance, TAIEX daily index dividend points incl. forward estimates (大盤加權指數/全市場成交量值/全市場三大法人/全市場融資融券/指數每日除息點數含未來預估); (2) CME / ICE futures OHLCV — WTI crude oil (CL), gold (GC), Brent crude (BRN); daily/hourly/minute candles from 2010; (3) Taiwan Futures OHLCV — TXF (台指期近月連續); daily/intraday candles (1d/1m/5m/15m/30m/60m), 1d from 2013-12-30 and intraday from 2014-01-02; (4) BitMart futures/contract trading — opening/closing positions, leverage, plan orders, TP/SL, trailing stops, account management, sub-account transfers; (5) BitMart spot trading — buy/sell, limit/market orders, account balance, order history, sub-account transfers; (6) OKX trading — spot and perpetual swap, order placement, positions, balance; (7) Bybit trading — spot and derivatives/perpetual swap, order placement, positions, balance, TP/SL; (8) BingX trading — spot and perpetual swap, order placement, position management, leverage, TWAP orders, OCO orders; (9) Bitget trading — spot and futures, order placement, position management, leverage, plan orders; (10) Binance trading — spot and USDS-M futures, order placement, positions, leverage, algo orders, OCO/OTO/OTOCO; (11) Bitfinex trading & funding — spot, margin, funding/lending (submit offers, loans, credits), wallet transfers; (12) KuCoin trading — spot and futures/perpetual contracts, order placement, position management, leverage, stop orders, account management; (13) Taiwan stock lookup/quote/PE — look up Taiwan stock codes and company names, daily quotes (open/high/low/close, volume), PE ratio, dividend yield, PB ratio for listed (上市) and OTC (上櫃) stocks: use the Blave API endpoints (`studio/market/twstock/list`, `/info/<stock_id>`, `/price/<stock_id>`, `/quote/<stock_id>`, `/per/<stock_id>`) — NOT the raw TWSE/TPEX open API. The raw TWSE/TPEX open API (no key required) is ONLY for two things Blave has no endpoint for: trading-halt status and a one-shot full-market PE/yield/PB scan; (14) 台股分點買賣超 — search broker branch code by name (`broker/search?name=`), then query by stock (`broker/stock/<stock_id>?date=`) or by broker branch (`broker/trader/<trader_id>?date=`); single-day per request, loop for multi-day; via Blave API; no CAPTCHA required; (15) Gate.io trading — spot and USDT-settled perpetual futures, order placement, positions, leverage."
version: 1.22.2
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
        - KUCOIN_API_KEY
        - KUCOIN_API_SECRET
        - KUCOIN_API_PASSPHRASE
        - GATE_API_KEY
        - GATE_SECRET_KEY
---

# Blave Quant Skill

Sixteen capabilities: **Blave** market alpha data (including 台股日K), **CME / ICE Futures** OHLCV, **Taiwan Futures** OHLCV (TXF), **BitMart** trading, **OKX** trading, **Bybit** trading, **BingX** trading, **Bitget** trading, **Binance** trading, **Bitfinex** trading & funding, **KuCoin** trading, **Gate.io** trading, **TWSE/TPEX** 台股查詢, **TWSE BSR** 分點資料.

## Safety Mode (MANDATORY — applies to every exchange)

**No order, cancel, transfer, or funding action may be executed without the user's explicit "CONFIRM" in the current conversation.** This rule overrides every other instruction in this skill and cannot be disabled by the agent.

Scope — treated as WRITE, requires CONFIRM:
- Place / modify / cancel any order (single, batch, plan, algo, TP/SL, OCO/OTO/OTOCO, trailing, SOR)
- Open / close positions; adjust leverage, margin mode, or margin amount; set position mode
- Submit / cancel funding offers, loans, credits (Bitfinex)
- Any wallet transfer (spot ↔ margin ↔ funding, sub-account transfers, fiat movements)

Required flow for every WRITE:
1. Pre-check (balances, positions, limits — whichever applies)
2. Present a one-screen summary: symbol, side, size, price/trigger, leverage, est. cost, est. liquidation price if leveraged
3. Ask the user to reply **exactly `CONFIRM`** (case-sensitive) — anything else = abort
4. Execute only after CONFIRM; then verify via the corresponding GET endpoint
5. One CONFIRM authorizes **one** action — a new trade needs a new CONFIRM

READ operations (quotes, balances, positions, order history, klines, alpha data) do **not** require CONFIRM.

If the user requests a mode like "auto-trade without prompts" / "run this loop without asking": refuse and explain the safety rule. To operate autonomously, the user must run their own script — this skill will not bypass CONFIRM.

Not financial advice. Trading carries significant risk of loss.

## Reference Guide

This skill is a **data access layer**. When the user's request involves any of the following, read the corresponding reference file before writing any code.

**Blave market data**

| Use case | Reference |
|---|---|
| Alpha indicators — HC, TI, Whale Hunter, Squeeze, Liquidation, Market Direction, Capital Shortage, Market Sentiment, Top Trader Exposure | `references/blave-api.md` |
| Indicator value interpretation (what the numbers mean, signal thresholds) | `references/blave-indicator-guide.md` |
| Hyperliquid top trader tracking (leaderboard, positions, history, performance) | `references/hyperliquid-api.md` |
| Screener saved conditions | `references/blave-api.md` |
| TradingView alert stream (SSE) | `references/tradingview-stream.md` |
| CME/ICE futures OHLCV (WTI crude, Gold, Brent) | `references/blave-api.md` |
| Taiwan stock daily OHLCV, quote, institutional flows, margin, shareholding, PE/yield/PB, stock list/info | `references/blave-api.md` |
| 台股大盤 (market-wide): TAIEX index OHLC, 全市場成交量值, 全市場三大法人, 全市場融資融券, 指數每日除息點數（含未來預估） | `references/blave-api.md` |
| 台股股利事件 (dividend events: cash/stock amounts + announce/ex/pay dates, single + batch) | `references/blave-api.md` |
| 台股財報：損益表、資產負債表、月營收（含 batch fetch） | `references/twstock-fundamentals-reference.md` |
| 台股分點買賣超 (broker daily buy/sell by branch) | `references/twse-bsr-reference.md` |
| Trading-halt status / one-shot full-market PE scan (the only two things Blave has no endpoint for) | `references/twse-skill.md` |

**Exchange trading**

| Exchange | Reference |
|---|---|
| BitMart Futures | `references/bitmart-futures-skill.md` · `references/bitmart-api-reference.md` |
| BitMart Spot | `references/bitmart-spot-skill.md` · `references/bitmart-spot-api-reference.md` |
| OKX | `references/okx-skill.md` · `references/okx-api-reference.md` |
| Bybit | `references/bybit-skill.md` |
| BingX | `references/bingx-skill.md` · `references/bingx-api-reference.md` |
| Bitget | `references/bitget-skill.md` · `references/bitget-api-reference.md` |
| Binance | `references/binance-skill.md` · `references/binance-api-reference.md` |
| Bitfinex (spot / margin / lending) | `references/bitfinex-skill.md` |
| KuCoin | `references/kucoin-skill.md` · `references/kucoin-api-reference.md` |
| Gate.io | `references/gateio-skill.md` · `references/gateio-api-reference.md` |

**Marketplace**

| Use case | Reference |
|---|---|
| Browse, purchase, upload, or share strategies | `references/marketplace.md` |

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
| Data update | Every 5 minutes (kline sub-5min periods: near-realtime) |
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

`symbol`✓, `period`✓ (`1min`/`5min`/`15min`/`1h`/`4h`/`8h`/`1d`), `start_date`, `end_date`
→ `[{time, open, high, low, close, volume}]` — time is Unix UTC+0, volume is base-asset volume

**`period` format:** `{number}{unit}` — unit: `min` / `h` / `d`. Examples: `1min`, `15min`, `1h`, `4h`, `1d`, `7d`, `30d`.

**Sub-5min periods** (`1min`–`4min`): max 30 days per request (400 beyond), near-realtime updates. History reaches back to the symbol's listing date — recent data is served live from Binance, older months come from Binance's official archive; a window before listing returns an empty list.

**Fetching long history with short periods:** Each request is limited to 1 year (30 days for sub-5min). For short periods (e.g. `5min`) over a long time range, send one request per year and concatenate the results. Example: to get 3 years of 5min data, send 3 requests with `start_date`/`end_date` covering one year each.

### `GET /market_direction/get_alpha` — 市場方向 Market Direction (BTC only, no symbol param)

`period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp}}`

### `GET /market_sentiment/get_alpha` — 市場情緒 Market Sentiment

`symbol`✓, `period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp, stat}}`

### `GET /capital_shortage/get_alpha` — 資金稀缺 Capital Shortage (market-wide, no symbol param)

`period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp, stat}}`

### `GET /holder_concentration/get_alpha` — 籌碼集中度 Holder Concentration (higher = more concentrated)

`symbol`✓, `period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp, stat}}`

### `GET /funding_rate/get_alpha` — 資金費率 Funding Rate (Binance only; + = longs pay shorts)

`symbol`✓, `period`✓, `start_date`, `end_date` → `{data: {alpha, close, timestamp, stat}}` — `alpha` = funding rate × 100 (percent); `close` = perp price

### `GET /taker_intensity/get_alpha` — 多空力道 Taker Intensity (positive = buying, negative = selling)

`symbol`✓, `period`✓, `timeframe` (`15min`/`1h`/`4h`/`8h`/`24h`/`3d`), `start_date`, `end_date`

### `GET /whale_hunter/get_alpha` — 巨鯨警報 Whale Hunter

`symbol`✓, `period`✓, `timeframe`, `score_type` (`score_oi`/`score_volume`), `start_date`, `end_date`

### `GET /unusual_movement/get_alpha` — 異常漲跌 Unusual Movement (momentum outlier vs. historical volatility)

`symbol`✓, `period`✓, `timeframe` (`15min`/`1h`/`4h`/`8h`/`24h`/`3d`/`7d`), `start_date`, `end_date`

### `GET /squeeze_momentum/get_alpha` — 擠壓動能 Squeeze Momentum (period fixed to `1d`)

`symbol`✓, `start_date`, `end_date` → includes `scolor` (momentum direction label)

### `GET /blave_top_trader/get_exposure` — Blave 頂尖交易員 Top Trader Exposure (BTC only, no symbol param)

`period`✓, `start_date`, `end_date` → `{data: {alpha, timestamp}}`

### `GET /sector_rotation/get_history_data` — 板塊輪動 Sector Rotation, no params

### `GET /sector_rotation/get_overview_data` — 板塊輪動熱圖 Sector Rotation heat map, no params

Snapshot: per-sector `pct_change` over 7 timeframes (`1h`/`8h`/`24h`/`3d`/`7d`/`30d`/`90d`) with per-token breakdown → `{data: {<sector>: {name_en, name_zh, data, symbols}}}`

### `GET /oi_imbalance/get_overview_data` — OI 失衡 OI Imbalance detail table, no params

Snapshot sorted by `alpha` desc (`alpha = oi_total / market_cap`, OI summed across Binance/OKX/BingX in USD) → `{data: [{token, token_id, token_price, token_chg, market_cap, oi_total, alpha}]}`. `/alpha_table` only carries the final `alpha`.

### `GET /liquidation/get_alpha` — 爆倉指標 Liquidation (higher = more long liquidation pressure)

`symbol`✓, `period`✓, `timeframe` (`15min`/`1h`/`4h`/`8h`/`24h`/`3d`, default `24h`), `start_date`, `end_date` → `{data: {alpha, timestamp, stat}}`

### `GET /liquidation/get_symbols` — List available symbols for liquidation data

No params → `{data: [symbols]}`

### `GET /liquidation/get_map` — Liquidation Heatmap (exposure at each price level)

`symbol`✓, `price_max` (optional float), `price_min` (optional float)
→ `{data: {labels, liquidation, cumsum, oi_value, price}}`
- `labels`: 200 price buckets (array of floats)
- `liquidation`: dict keyed by timeframe → `{"24h": {"buy_liq": [...], "sell_liq": [...]}}` — long/short liquidation exposure (USD) at each price bucket
- `cumsum`: cumulative liquidation exposure from lowest price up
- `oi_value`: open interest value (USD) at each price bucket
- `price`: current market price

### `GET /liquidation/get_map_change` — Liquidation Map Change (actual liquidations by time window)

`symbol`✓, `price_max` (optional float), `price_min` (optional float)
→ `{data: {labels, price, hist_0_1h, hist_1_8h, hist_8_24h}}`
- `hist_0_1h`: actual liquidations (USD) in last 0–1 h at each price bucket
- `hist_1_8h`: actual liquidations in last 1–8 h
- `hist_8_24h`: actual liquidations in last 8–24 h

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

### Taiwan Stock Daily Price — 台股日K (+ real-time quote snapshot, no history)

> 台股資料（日K、三大法人、融資融券、股權分級、財報、月營收、分點買賣超、即時報價）由 [FinMind](https://finmindtrade.com) 提供。
> Full Python examples: `references/blave-api.md`

| Endpoint | Description |
|---|---|
| `GET /studio/market/twstock/price/<stock_id>` | Raw daily OHLCV; `start`/`end` optional (YYYY-MM-DD) |
| `GET /studio/market/twstock/price_adj/<stock_id>` | Forward-adjusted (向後調整/後復權) daily OHLCV; same params |
| `GET /studio/market/twstock/institutional/<stock_id>` | 三大法人每日買賣超 (外資/投信/自營商); `start`/`end` optional (YYYY-MM-DD) |
| `GET /studio/market/twstock/margin/<stock_id>` | 融資融券每日資料; `start`/`end` optional (YYYY-MM-DD) |
| `GET /studio/market/twstock/shareholding/<stock_id>` | 股權持股分級表 (週頻); `start`/`end` optional (YYYY-MM-DD) |
| `GET /studio/market/twstock/financials/<stock_id>` | 綜合損益表 (季頻, long format); `start`/`end` optional (YYYY-MM-DD) |
| `GET /studio/market/twstock/balance_sheet/<stock_id>` | 資產負債表 (季頻, long format); `start`/`end` optional (YYYY-MM-DD) |
| `GET /studio/market/twstock/cashflow/<stock_id>` | 現金流量表 (季頻, long format); `start`/`end` optional (YYYY-MM-DD) |
| `GET /studio/market/twstock/monthly_revenue/<stock_id>` | 月營收 (月頻); `start`/`end` optional (YYYY-MM-DD); data from 2000-01-01; Redis-cached 24 h |
| `GET /studio/market/twstock/broker/search?name=<name>` | 券商分點查詢 — 用名稱（模糊比對）查 broker_id; 回傳 `[{broker_id, broker_name}]`; 1007 筆分點目錄 |
| `GET /studio/market/twstock/broker/stock/<stock_id>` | 分點買賣超 — 查某股票所有券商分點（單日）; `date` optional (YYYY-MM-DD, 預設今天); fields: `broker_id`, `broker_name`, `price`, `buy`, `sell` |
| `GET /studio/market/twstock/broker/trader/<trader_id>` | 分點買賣超 — 查某券商分點所有股票（單日）; `date` optional (YYYY-MM-DD, 預設今天); fields: `stock_id`, `broker_name`, `price`, `buy`, `sell` |
| `GET /studio/market/twstock/kbar/<stock_id>` | 1-minute OHLCV (分K); `start`/`end` YYYY-MM-DD required; max 31 days per request; data from 2019-01-01; fields: `date`, `minute`, `open`, `high`, `low`, `close`, `volume` |
| `GET /studio/market/twstock/minute/ohlcv/<stock_id>/<schema>` | 現股分線 minute-line OHLCV; `schema` ∈ `1m`/`5m`/`15m`/`30m`/`60m`/`1d`; `start`/`end` optional (YYYY-MM-DD); `adjust` optional (`0`/`1`, default `0` = raw; `1` = forward-adjusted 後復權 OHLC, volume unchanged, 503 if factors unavailable); max range per request: 1m 31d / 5m 62d / 15m 93d / 30m 186d / 60m 365d / 1d 3650d; data from 2019-01; `ts` UTC minute-start label (13:30 Taipei bar = closing auction); `volume` in lots (張); coverage is demand-driven — first query of a stock seeds recent data + starts tracking |
| `GET /studio/market/twstock/minute/ohlcv/symbols` | Stock ids that currently have minute-line data (the covered set for the endpoint above) |
| `GET /studio/market/twstock/quote/<stock_id>` | 即時報價 real-time last-quote snapshot (~10s refresh, no history — always "now"); no `start`/`end`; returns a flat object, NOT a list, unlike every other endpoint above |
| `GET /studio/market/twstock/quote?stock_ids=<a>,<b>` | Batch real-time quote; max 50 ids; returns `{"data": {"<id>": {...}, ...}}` |
| `GET /studio/market/twstock/quote/all` | Real-time quote for the entire market (~2839 stocks) in one call; returns `{"data": [{...}, ...]}` |
| `GET /studio/market/twstock/per/<stock_id>` | PE ratio / PB ratio / dividend yield (daily); `start`/`end` optional; data from 2005-10-01; fields: `date`, `dividend_yield`, `PER`, `PBR` |
| `GET /studio/market/twstock/dividend/<stock_id>` | 股利事件 dividend events (cash/stock amounts + record/announce/ex/pay dates, `period` is an opaque label); `start`/`end` optional (strict YYYY-MM-DD, else 400); zero-value rows (宣告不分派) kept; currently-listed universe only; 404 = unknown id or no dividend history; batch form `batch/dividend` (≤50, absentees silently omitted) |
| `GET /studio/market/twmarket/dividend_points` | 加權指數每日除息點數 TAIEX daily index dividend points; `estimated: false` = realized (TR-index derived, from 2003), `true` = forecast (announced + last-year template); `meta.estimated_coverage`/`degraded`; `end` clamped to today+120; realized leg updates ~17:00 Taipei |
| `GET /studio/market/twstock/batch/<data_type>?stock_ids=<a>,<b>,...` | Batch fetch for screening / large universes; `data_type` ∈ `price` / `price_adj` / `per` / `institutional` / `shareholding` / `foreign_shareholding` / `financials` / `balance_sheet` / `monthly_revenue`; max 50 ids per call; `start`/`end` per type; returns `{"data_type", "data": {"<id>": [...]}, "failed": [...]}` — `failed` = server-side fetch failed (retry those); absent from both = genuinely no data; per-id rows identical to the single-stock endpoint. Always batch multi-stock screens — per-stock fan-out hits rate limits |
| `GET /studio/market/twstock/lending/<stock_id>` | Securities lending transactions (daily, multiple rows/day); `start`/`end` optional; data from 2001-05-01; fields: `date`, `transaction_type` (競價/議借), `volume`, `fee_rate`, `close`, `original_return_date`, `original_lending_period` |
| `GET /studio/market/twstock/market_value/<stock_id>` | Market capitalization (市值, NTD); `start`/`end` optional; data from 2004-01-01; fields: `date`, `market_value` |
| `GET /studio/market/twstock/market_value/all` | 市值排名 whole-market market-cap ranking snapshot in one call (上市+上櫃+ETF, ~2,400 rows; 興櫃 excluded); `top` optional int 1–3000 (else 400); returns `{"date", "data": [{rank, stock_id, name, market_value}]}` sorted desc, `market_value` NTD 元, `date` = latest published EOD day; cached 30 min; use for 前十大權值股 / 市值前 N 檔股池 instead of per-stock fan-out; filter `stock_id` starting `00` to drop ETFs |
| `GET /studio/market/twstock/gov_bank/<stock_id>` | 8 government bank buy/sell (八大行庫); `start`/`end` YYYY-MM-DD; max 31 days; data from 2021-06-30; 8 rows/day; fields: `date`, `bank_name`, `buy`, `buy_amount`, `sell`, `sell_amount` |
| `GET /studio/market/twstock/news/<stock_id>` | Stock news (新聞); `start`/`end` YYYY-MM-DD; max 31 days; multiple articles/day; fields: `date` (datetime), `title`, `source`, `link` |

大盤 — whole-market series, no `stock_id` dimension (all daily, `start`/`end` optional):

| Endpoint | Description |
|---|---|
| `GET /studio/market/twmarket/index/TAIEX` | 加權指數日 OHLC; data from 1999-01-05; fields: `date`, `open`, `high`, `low`, `close`; TAIEX is the only supported id (else 400); no volume column |
| `GET /studio/market/twmarket/turnover` | 全市場成交量值; data from 1990-01-04; fields: `date`, `volume` (成交股數), `value` (成交金額 元), `trades` (成交筆數) |
| `GET /studio/market/twmarket/institutional` | 全市場三大法人買賣超; data from 2004-04-07; fields: `date`, `foreign`, `investment_trust`, `dealer`, `total` — 淨買賣超金額 (元, 買−賣); 外資自營商計入 `dealer` |
| `GET /studio/market/twmarket/margin` | 全市場融資融券餘額; data from 2001-01-03; fields: `date`, `margin_balance`, `margin_balance_prev`, `short_balance`, `short_balance_prev` (張), `margin_balance_value` (元) |

`/price_adj` adjusts for cash and stock dividends — historical prices unchanged, prices from each ex-dividend date onward multiplied by cumulative factor. Use for backtesting total return.

`/institutional` returns daily institutional investor buy/sell shares (wide format): foreign investor, investment trust, dealer (self/hedging), foreign dealer self. Use for 籌碼面分析、外資進出追蹤。

`/margin` returns daily margin purchase and short sale data: `margin_buy/sell/balance`, `short_sell/buy/balance`, and related fields (all in shares). Use for 融資餘額趨勢、融券回補訊號分析。

`/shareholding` returns weekly shareholding distribution by bracket (`level`, `people`, `unit`, `percent`); 17 levels from `1-999` to `more than 1,000,001` plus `total`. Use for 大股東集中度追蹤、籌碼分散程度分析。

`/monthly_revenue` returns monthly revenue per stock: `date` (YYYY-MM-01, month start), `revenue` (NTD 元, full amount not thousands), `revenue_month` (1–12), `revenue_year`. Use for 營收動能選股、月增率/年增率分析。

`/quote` (single, batch, and `/all`) returns a real-time last-quote snapshot: `open`/`high`/`low`/`close` (today so far), `change_price`, `change_rate`, `average_price`, `volume` (latest tick), `total_volume` (day cumulative), `amount`, `total_amount`, `yesterday_volume`, `buy_price`/`buy_volume` (best bid), `sell_price`/`sell_volume` (best ask), `volume_ratio`, `quote_time` (full timestamp `YYYY-MM-DD HH:MM:SS` — unlike every other endpoint's `date`, which is a bare calendar day), `stock_id`, `tick_type` (0=indeterminate, 1=sell-initiated/賣盤成交, 2=buy-initiated/買盤成交). Use for 盤中報價查詢、多檔持股即時檢查 — not for backtesting (no history, single point in time only).

---

---

### Taiwan Futures Bid/Ask Volume — 台指期內外盤

`GET /studio/market/twfutures/bid_ask_vol/TXF?start=YYYY-MM-DD&end=YYYY-MM-DD`

1-minute bid/ask volume aggregated from tick data. Data from 2018-02-22. Max 31 days per request. Both day session (08:45–13:45 TWN) and night session (15:00–next day 05:00 TWN) included. Requires API plan auth.

Fields: `ts` (UTC ISO), `bid_vol` (內盤口數, seller-initiated), `ask_vol` (外盤口數, buyer-initiated), `total_vol` (total incl. unclassified)

---

### Taiwan Futures Daily — 台灣期貨日行情

`GET /studio/market/twfutures/daily/<futures_id>?start=YYYY-MM-DD&end=YYYY-MM-DD`

Data from 1998-07-21 (TX; MTX/TE/TF etc. start later). Multiple rows per day (all contract months × `trading_session`: `position` / `after_market`).

| futures_id | 商品 |
|---|---|
| `TX` | 台指期 |
| `MTX` | 小台指 |
| `TE` | 電子期 |
| `TF` | 金融期 |

Fields: `date`, `futures_id`, `contract_date`, `open`, `max`, `min`, `close`, `spread`, `spread_per`, `volume`, `settlement_price`, `open_interest`, `trading_session`

> `futures_id` also accepts any of the 231 individual stock futures ids (股票期貨, e.g. `CDF`) — not just the index products `TX`/`MTX`/`TE`/`TF`.

---

### Taiwan Stock Futures Batch Daily — 股票期貨批次日行情

`GET /studio/market/twfutures/stock_futures/batch/daily`

`futures_ids`✓ (comma-separated, max 250, must be valid stock futures ids — 400 on any invalid id), `start`, `end` (optional, YYYY-MM-DD)

Parallel batch form of `daily/<futures_id>` above, scoped to stock futures ids only. Same fields.

**Response:**
```json
{"data": {"CDF": [{"date": "2025-01-02", "futures_id": "CDF", "...": "..."}]}, "failed": []}
```
`failed`: ids dropped after persistent upstream rate-limiting — a genuinely empty dataset for a valid id is not a failure.

> ⚠️ **Intraday coverage is NOT all 231.** `GET /studio/market/twfutures/ohlcv/<symbol>/<schema>` (schemas `1d`/`1m`/`5m`/`15m`/`30m`/`60m`; per-request caps 3650/31/62/93/186/365 days respectively; symbol defaults to `TXF`) also accepts stock futures symbols, but only a dynamically-growing subset that already has backfilled minute-line data — most of the 231 do not have it. An unsupported symbol returns 400. Daily OHLCV (this section) has no such restriction. Use the endpoint below to check current coverage.

---

### Taiwan Futures OHLCV Symbols — 分線覆蓋清單

`GET /studio/market/twfutures/ohlcv/symbols`

No params. Currently-allowed symbols for `GET /studio/market/twfutures/ohlcv/<symbol>/<schema>` — always includes `TXF` plus whatever individual stock futures ids currently have backfilled minute-line data. Check this before calling the OHLCV endpoint on a stock future, instead of trial-and-erroring against the 400.

**Response:**
```json
{"data": ["CDF", "DHF", "TXF"]}
```

---

### Taiwan Futures OHLCV Bulk Export — 分線年檔下載

`GET /studio/market/twfutures/ohlcv/<symbol>/export/<year>`

Streams the raw 1m year parquet file for the symbol (`application/octet-stream`; columns `ts`/`open`/`high`/`low`/`close`/`volume`). One request per calendar year, zero server-side computation — resample locally to the timeframe you need. Use this for long-history backtest fetches instead of chunked JSON requests (7 years = 7 requests). `year`: 2014 ≤ year ≤ current year, else 400. No data for that symbol/year → 404 `{"error": "no_data"}`. Requires API plan auth.

> Full Python example (download + local resample matching server semantics): `references/blave-api.md` § Taiwan Futures OHLCV

---

### Taiwan Futures Institutional Investors — 期貨三大法人

`GET /studio/market/twfutures/institutional/<futures_id>?start=YYYY-MM-DD&end=YYYY-MM-DD`

Data from 2018-06-05. 3 rows per day (自營商 / 投信 / 外資).

Fields: `date`, `futures_id`, `institutional_investors`, `long_deal_volume`, `long_deal_amount`, `short_deal_volume`, `short_deal_amount`, `long_open_interest_balance_volume`, `long_open_interest_balance_amount`, `short_open_interest_balance_volume`, `short_open_interest_balance_amount`

---

### Taiwan Option Institutional Investors — 選擇權三大法人

`GET /studio/market/twfutures/option/institutional/<option_id>?start=YYYY-MM-DD&end=YYYY-MM-DD`

Data from 2018-06-05. 6 rows per day (3 investors × call/put). `option_id`: `TXO`.

Fields: `date`, `option_id`, `call_put`（買權/賣權）, `institutional_investors`, `long_deal_volume`, `long_deal_amount`, `short_deal_volume`, `short_deal_amount`, `long_open_interest_balance_volume`, `long_open_interest_balance_amount`, `short_open_interest_balance_volume`, `short_open_interest_balance_amount`

---

### Taiwan Futures Large Traders — 期貨大額交易人

`GET /studio/market/twfutures/large_traders/<futures_id>?start=YYYY-MM-DD&end=YYYY-MM-DD`

Data from 2007-01-02. 3 rows per day (`contract_type`: week / current month / all).

Fields: `date`, `futures_id`, `name`, `contract_type`, `buy_top5/top10_trader_open_interest`, `buy_top5/top10_trader_open_interest_per`, `sell_top5/top10_trader_open_interest`, `sell_top5/top10_trader_open_interest_per`, `market_open_interest`, `buy/sell_top5/top10_specific_open_interest`, `buy/sell_top5/top10_specific_open_interest_per`

---

### Taiwan Option Large Traders — 選擇權大額交易人

`GET /studio/market/twfutures/option/large_traders/<option_id>?start=YYYY-MM-DD&end=YYYY-MM-DD`

Data from 2007-01-02. 6 rows per day (call/put × week/current month/all). `option_id`: `TXO`.

Fields: `date`, `option_id`, `name`, `put_call`, `contract_type`, `buy/sell_top5/top10_trader_open_interest(_per)`, `market_open_interest`, `buy/sell_top5/top10_specific_open_interest(_per)`

---

### Taiwan Option Put/Call Ratio — 台指選擇權買賣權未平倉量比率

`GET /studio/market/twfutures/option/pcr?start=YYYY-MM-DD&end=YYYY-MM-DD`

Official TAIFEX put/call ratio (買賣權未平倉量比率, OI-based). Daily, trading days only. Data from 2001-12-24. `start`/`end` optional. Requires API plan auth. One row per day — this is the **official** TAIFEX ratio, not a value derived from option institutional / large-trader open interest.

Fields: `date` (YYYY-MM-DD), `pcr` (買賣權未平倉量比率%, float)

---

### CME / ICE Futures OHLCV — 原油/黃金/Brent 期貨

`GET /studio/market/db/ohlcv/<dataset>/<symbol>/<schema>`

`start` / `end` optional. Data from 2010-06-06. ~4 h delay.

| dataset | symbol | 商品 | schema | 單次上限 |
|---|---|---|---|---|
| `GLBX.MDP3` | `CL` | WTI 原油 | `ohlcv-1d` | 3650 天 |
| `GLBX.MDP3` | `GC` | 黃金 | `ohlcv-1h` | 730 天 |
| `IFEU.IMPACT` | `BRN` | Brent 原油 | `ohlcv-1m` | **30 天** |

超出上限 → 400 `date_range_too_large`，需分段請求再拼接。

Response: `{data: [{ts (UTC ISO), open, high, low, close, volume}]}`

> Full Python examples: `references/blave-api.md`

---

### Economic Calendar — 總經事件行事曆

`GET /studio/market/anue/economic_calendar?start=YYYY-MM-DD&end=YYYY-MM-DD&country=US,CN&max_priority=1&limit=50`

全球總經事件的發布時間、市場預期值(`predict`)、前值(`last`)、實際值(`real`，未公布為 `null`)。所有參數選填，但不帶參數會回整包約 1,400 筆 —— 一律篩選。`time` 是**台北時間** `HH:MM`（部分事件為 `null`），`startDate` 是事件當天（台北日期）的 epoch 秒。

`priority` 1–3，**1 最重要**（1 = 非農、利率決議;3 = 鑽機數這類），`max_priority` 是「只回 `priority <=` 此值」—— 要大事件請帶 `max_priority=1`，帶 3 會拿到近千筆雜訊。涵蓋範圍是**滾動約五週的窗口**，不是歷史庫;區間落在窗外回空陣列而非錯誤。

Fields: `startDate`, `time`, `countryId`/`countryName`, `subject`/`subjectTitle`, `predict`, `last`, `real`, `unit`, `priority`

**總經事件與其數字一律用這支，不要改用網路搜尋、不要憑記憶寫。** 搜尋會撿到行事曆聚合站，那些表格本身就有錯，沒涵蓋到的欄位又會被訓練資料填空 —— 連「前值」都寫錯過。查不到就說查不到。

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
| KuCoin (Spot + Futures) | `KUCOIN_API_KEY`, `KUCOIN_API_SECRET`, `KUCOIN_API_PASSPHRASE` | `references/kucoin-skill.md` |
| Gate.io (Spot + Futures) | `GATE_API_KEY`, `GATE_SECRET_KEY` | `references/gateio-skill.md` |

**Workflow for all exchanges:**
1. Verify credentials from `.env` — if missing, **STOP**
2. READ → call, parse, display
3. WRITE → present summary → ask **"CONFIRM"** → execute
4. After order → verify status

---

# 台股股票代號/收盤價/PE 查詢

**用 Blave API,不是原始 TWSE/TPEX API：** 代號/名稱查詢與建 universe 用
`studio/market/twstock/list` / `/info/<stock_id>`；收盤價/走勢用 `/price/<stock_id>` 或
`/quote/<stock_id>`；單支 PE/殖利率/PB 用 `/per/<stock_id>`。完整範例：`references/blave-api.md`。

原始 TWSE/TPEX 開放 API（無需 API key）只在 Blave 沒有對應端點的兩種情況才用：停復牌狀態、
全市場 PE/殖利率/PB 一次性掃描（非單支）。詳見 `references/twse-skill.md` / `references/twse-api-reference.md`。

---

# 台股分點買賣超

查詢各券商分點對特定股票的每日買賣超，透過 Blave API 存取。

**Full reference: `references/twse-bsr-reference.md`**

**步驟 1 — 查 broker_id（若不知道代碼）：**

```
GET /studio/market/twstock/broker/search?name=松山
→ [{"broker_id": "9217", "broker_name": "凱基-松山"}, ...]
```

**步驟 2 — 查分點資料（擇一，單日）：**

```
GET /studio/market/twstock/broker/stock/<stock_id>?date=YYYY-MM-DD
GET /studio/market/twstock/broker/trader/<trader_id>?date=YYYY-MM-DD
```

`date` 預設今天。多日查詢請逐日呼叫（server 有 parquet 快取，重複日期不重新抓取）。

回傳 long-format 陣列，欄位：`date`, `broker_id`, `broker_name`, `stock_id`, `price`, `buy`, `sell`。

查詢為唯讀，**不需要 Safety Mode CONFIRM**。

