---
name: blave-quant
description: "Blave quant data layer and exchange-trading reference for AI agents. Use when the task needs crypto alpha/market data, Taiwan stock, futures or market-wide data, CME/ICE or TXF OHLCV, Hyperliquid top traders, or trading on BitMart, OKX, Bybit, BingX, Bitget, Binance, Bitfinex, KuCoin or Gate.io."
version: 1.23.21
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
        - BYBIT_SECRET_KEY
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

Quant infrastructure for AI agents. Capabilities: **Blave** market alpha data (including 台股日K), **CME / ICE Futures** OHLCV, **Taiwan Futures** OHLCV (TXF), **BitMart** trading, **OKX** trading, **Bybit** trading, **BingX** trading, **Bitget** trading, **Binance** trading, **Bitfinex** trading & funding, **KuCoin** trading, **Gate.io** trading, **TWSE/TPEX** 台股查詢, **TWSE BSR** 分點資料.

**Keywords (zh ↔ en, so a request in either language lands on the right reference):** 籌碼集中度 Holder Concentration · 多空力道 Taker Intensity · 巨鯨警報 Whale Hunter · 擠壓動能 Squeeze Momentum · 市場方向 Market Direction · 資金稀缺 Capital Shortage · 板塊輪動 Sector Rotation · OI 失衡 OI Imbalance · Blave頂尖交易員 Top Trader Exposure · 市場情緒 Market Sentiment · 每幣爆倉 / 爆倉矩陣 liquidation by coin / exchange matrix · 多空比 long/short ratio · 未平倉量 open interest (table, per coin, history) · 主動買賣淨額 CVD · CME 持倉報告 COT · kline (every Binance USDT perpetual incl. tokenized stocks, 1min from 2020-01) · alpha table · screener saved conditions · Hyperliquid leaderboard / positions · 台股日K / 現股分線 / 向後調整 / 三大法人 / 融資融券 / 股權持股分級表 / 綜合損益表 / 資產負債表 / 現金流量表 / 月營收 / 股利事件 / 市值排名（市場別、ETF 旗標、上市扣除 ETF 市值分母）/ 分點買賣超 / 本益比・殖利率・淨值比 · 大盤加權指數 / 全市場成交量值 / 全市場三大法人 / 全市場融資融券 / 指數每日除息點數（含未來預估） · 台指期 TXF 日線與分線 / 選擇權 PCR / 法人持倉成本 · WTI `CL` / 黃金 `GC` / 布蘭特 `BRN` · 總經日曆 economic calendar.

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
| **Any Blave data endpoint** — parameters, defaults, response fields, errors, data start date (single source) | `references/blave-api.md` |
| Alpha indicators — HC, TI, Whale Hunter, Squeeze, Liquidation, Market Direction, Capital Shortage, Market Sentiment, Top Trader Exposure | `references/blave-api.md` |
| Raw cross-exchange base data — 多空比 long/short ratio, 未平倉量 open interest, CVD, 爆倉矩陣 liquidation matrix (cross-sections of now; open interest alone also has backtest history, `/oi_imbalance/get_history`) | `references/blave-api.md` |
| CME 持倉報告 CME Bitcoin / Ether futures Commitments of Traders (CFTC COT, weekly) | `references/blave-api.md` (endpoints) · `references/blave-indicator-guide.md` (leveraged funds net short ≠ bearish) |
| Indicator value interpretation (what the numbers mean, signal thresholds) | `references/blave-indicator-guide.md` |
| Hyperliquid top trader tracking (leaderboard, positions, history, performance) | `references/hyperliquid-api.md` |
| Screener saved conditions | `references/blave-api.md` |
| CME/ICE futures OHLCV (WTI crude, Gold, Brent) | `references/blave-api.md` |
| Taiwan stock daily OHLCV, quote, institutional flows, margin, shareholding, PE/yield/PB, stock list/info | `references/blave-api.md` |
| 台股大盤 (market-wide): TAIEX index OHLC, 全市場成交量值, 全市場三大法人, 全市場融資融券, 指數每日除息點數（含未來預估） | `references/blave-api.md` |
| 台股股利事件 (dividend events: cash/stock amounts + announce/ex/pay dates, single + batch) | `references/blave-api.md` |
| 台股財報：損益表、資產負債表、月營收（含 batch fetch） | `references/blave-api.md` (endpoints) · `references/twstock-fundamentals-reference.md` (analysis guide) |
| 台股分點買賣超 (broker daily buy/sell by branch) | `references/blave-api.md` (endpoints) · `references/twse-bsr-reference.md` (workflow) |
| 法人台指期持倉成本 institutional carrying cost (外資/投信/自營商 TAIEX futures cost + PnL) | `references/blave-api.md` (endpoint) · `references/blave-indicator-guide.md` (method & limits) |
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
- Once the account is on plan billing, a key the user created themselves needs an **API plan**; a Blave Agent plan covers only the keys Blave Agent issues (cloud machine, desktop app) — `references/blave-api.md` › *Which key, which plan*
- Create key: **[https://blave.org/landing/en/api?tab=blave](https://blave.org/landing/en/api?tab=blave)**

Add to `.env`: `blave_api_key=...` and `blave_secret_key=...`

**Auth headers:** `api-key: $blave_api_key` | `secret-key: $blave_secret_key`

**Base URL:** `https://api.blave.org` | **Support:** info@blave.org | [Discord](https://discord.gg/D6cv5KDJja)

## Limits

| Item        | Value                                                   |
| ----------- | ------------------------------------------------------- |
| Rate limit  | 500 requests / 5 min per API key, and 500 / 5 min per IP — `429` if exceeded, resets after 5 min. `studio/market/anue/economic_calendar` has its own limit: 100 requests / min per account |
| Data update | Varies by endpoint (crypto indicators every 5 minutes) — see each endpoint's `Update` row in `references/blave-api.md` |
| History     | Per-request range caps vary by endpoint (crypto indicators: 1 year, silently clamped; minute bars: 30–365 days, `400 date_range_too_large` beyond) — split long ranges into several requests |
| Timestamps  | UTC unless the endpoint says otherwise                  |

## Usage Guidelines

- **Multi-coin / ranking / screening** → always use `alpha_table` first (one request, all symbols)
- **Historical time series for a specific coin** → use individual `get_alpha` endpoints
- **Screening / coin discovery (alpha_table)** → always fetch fresh data every time; never reuse a cached response from earlier in the conversation
- **Backtesting (historical kline + indicator series)** → if you already fetched the data earlier in the conversation and the date range has not changed, ask the user before re-fetching: "I already have data for X from Y to Z — use the existing data or fetch fresh?"
- **Many Taiwan stocks** → use `studio/market/twstock/batch/<data_type>` (≤ 50 ids per call); never loop a single-stock endpoint over a universe (429). For "top N by market cap" use `twstock/market_value/all`
- **`503` from a Taiwan data endpoint** means "temporarily unavailable, retry later" — never treat it as "no data" or "no trades"
- **Macro events and their numbers** → only `studio/market/anue/economic_calendar`; never a web search or a remembered value. If it cannot answer, say so

## Endpoints

**Every endpoint's parameters, defaults, response fields, errors, data start date, and a Python example live in `references/blave-api.md`. Read the relevant block there before writing any call.** That file opens with an endpoint → line index: read the index, then `Read` the block at its `offset` (or grep the `` ## `GET /path` `` heading) — never the whole 4,500-line file. Index by category:

| Category | Endpoints (all `GET`, relative to `https://api.blave.org`) |
|---|---|
| Crypto › General | `price`, `alpha_table`, `kline` |
| Crypto › Tool | `market_direction/get_alpha`, `screener/get_saved_conditions`, `screener/get_saved_condition_result` |
| Crypto › Alpha | `holder_concentration/*`, `funding_rate/get_alpha`, `market_sentiment/*`, `capital_shortage/get_alpha`, `sector_rotation/get_history_data` / `get_overview_data`, `oi_imbalance/get_overview_data`, `whale_hunter/*`, `taker_intensity/*`, `unusual_movement/*`, `squeeze_momentum/*`, `blave_top_trader/get_exposure`, `liquidation/get_symbols` / `get_alpha` / `get_map` / `get_map_change` / `get_coin` / `get_exchanges` |
| Crypto › Raw data | `long_short_ratio/get_table` / `get_coin` (多空比), `oi_imbalance/get_table` / `get_coin` / `get_history` (未平倉量 — **not** the `oi_imbalance/get_overview_data` indicator), `taker_intensity/get_cvd_table` / `get_cvd_coin` (CVD 主動買賣淨額), `cme_cot/get_latest` / `get_history` (CME 持倉報告 COT) |
| Taiwan Stock › Market Data | `studio/market/twstock/list`, `info/<stock_id>`, `price/<stock_id>`, `price_adj/<stock_id>`, `quote/<stock_id>`, `quote?stock_ids=`, `quote/all`, `minute/ohlcv/<stock_id>/<schema>`, `minute/ohlcv/symbols`, `kbar/<stock_id>` (legacy) |
| Taiwan Stock › Fundamentals | `market_value/<stock_id>`, `market_value/all`, `per/<stock_id>`, `financials/<stock_id>`, `balance_sheet/<stock_id>`, `cashflow/<stock_id>`, `monthly_revenue/<stock_id>`, `dividend/<stock_id>`, `news/<stock_id>` |
| Taiwan Stock › Institutional Flow | `institutional/<stock_id>`, `margin/<stock_id>`, `shareholding/<stock_id>`, `foreign_shareholding/<stock_id>`, `gov_bank/<stock_id>`, `lending/<stock_id>`, `broker/search`, `broker/stock/<stock_id>`, `broker/trader/<trader_id>` |
| Taiwan Stock › Other | `batch/<data_type>` |
| Taiwan Market (大盤) | `studio/market/twmarket/index/TAIEX`, `turnover`, `institutional`, `margin`, `dividend_points` |
| Taiwan Futures & Options | `studio/market/twfutures/ohlcv/<symbol>/<schema>`, `ohlcv/symbols`, `ohlcv/<symbol>/export/<year>`, `bid_ask_vol/<symbol>`, `daily/<futures_id>`, `stock_futures/batch/daily`, `institutional/<futures_id>`, `large_traders/<futures_id>`, `option/institutional/<option_id>`, `option/large_traders/<option_id>`, `option/pcr`, `carrying_cost/<identity>` (法人持倉成本) |
| Commodities | `studio/market/db/ohlcv/<dataset>/<symbol>/<schema>` (WTI `CL`, gold `GC`, Brent `BRN`) |
| Macro | `studio/market/anue/economic_calendar` |

> 台股資料（日K、三大法人、融資融券、股權分級、財報、月營收、分點買賣超、即時報價）由 [FinMind](https://finmindtrade.com) 提供。

### Hyperliquid Top Trader Tracking

`/hyperliquid/*` — leaderboard, curated traders, positions, fills, PnL, open orders, top-100 aggregate positions, exposure history, bucket stats. Full reference: `references/hyperliquid-api.md`.

> Indicator interpretation: `references/blave-indicator-guide.md`

---

# Exchange Trading

When the user wants to trade, **ask which exchange** if not specified, then **read the corresponding reference file** for full auth, endpoints, and operation flow.

| Exchange | .env keys | Reference |
|---|---|---|
| BitMart (Futures) | `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO` | `references/bitmart-futures-skill.md` |
| BitMart (Spot) | same as above | `references/bitmart-spot-skill.md` |
| OKX | `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE` | `references/okx-skill.md` |
| Bybit | `BYBIT_API_KEY`, `BYBIT_SECRET_KEY` | `references/bybit-skill.md` |
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

**Endpoint reference: `references/blave-api.md` › `broker/*`; workflow and examples: `references/twse-bsr-reference.md`**

**步驟 1 — 查 broker_id（若不知道代碼）：**

```
GET /studio/market/twstock/broker/search?name=松山
→ [{"broker_id": "9217", "broker_name": "凱基-松山"}, ...]
```

**步驟 2 — 查分點資料（擇一，單日或區間）：**

```
GET /studio/market/twstock/broker/stock/<stock_id>?date=YYYY-MM-DD
GET /studio/market/twstock/broker/trader/<trader_id>?date=YYYY-MM-DD
```

`date` 預設今天。多日可改用 `start=YYYY-MM-DD&end=YYYY-MM-DD` 一次查區間，區間最多 366 天（超過回 400），更長請分段。區間查詢待確認已部署：若回傳每筆 `date` 沒有跨日，退回逐日帶 `date` 查詢。資料起始 2021-06-30；當日資料台灣時間約 21:30 後才有，之前查當日回空陣列。回 503 代表資料暫不可用，稍後重試，不要當成沒有交易。

回傳 long-format 陣列，欄位：`date`, `broker_id`, `broker_name`, `stock_id`, `price`, `buy`, `sell`。

查詢為唯讀，**不需要 Safety Mode CONFIRM**。

