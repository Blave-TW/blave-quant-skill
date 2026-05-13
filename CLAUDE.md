# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains one skill covering fourteen capabilities:
1. **Blave** — Agent calls the Blave REST API directly for crypto market alpha data, Taiwan stock data, and Hyperliquid top trader tracking
2. **CME / ICE Futures** — Agent fetches WTI crude (CL), gold (GC), and Brent crude (BRN) OHLCV from 2010 via Blave API
3. **BitMart Futures** — Agent calls the BitMart API for perpetual futures trading
4. **BitMart Spot** — Agent calls the BitMart API for spot trading
5. **OKX** — Agent calls the OKX API for spot and perpetual swap trading
6. **Bybit** — Agent calls the Bybit API for spot and derivatives/perpetual swap trading
7. **BingX** — Agent calls the BingX API for spot and perpetual swap trading
8. **Bitget** — Agent calls the Bitget API for spot and futures trading
9. **Binance** — Agent calls the Binance API for spot and USDS-M futures trading
10. **Bitfinex** — Agent calls the Bitfinex API for spot, margin, and funding/lending
11. **KuCoin** — Agent calls the KuCoin API for spot and futures/perpetual contract trading
12. **TWSE / TPEX（台股）** — Agent queries Taiwan stock market data (stock code lookup, quotes, PE/yield/PB) via public APIs; no API key required
13. **TWSE BSR 分點資料** — Agent queries broker/dealer daily trading report via CAPTCHA-protected form; agent solves CAPTCHA using its own vision

No CLI or wrapper involved. All API calls are made directly by the agent.

## Required `.env` Variables

- `blave_api_key`, `blave_secret_key` — Blave API auth
- `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO` — BitMart API auth
- `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE` — OKX API auth
- `BYBIT_API_KEY`, `BYBIT_API_SECRET` — Bybit API auth
- `BINGX_API_KEY`, `BINGX_SECRET_KEY` — BingX API auth
- `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE` — Bitget API auth
- `BINANCE_API_KEY`, `BINANCE_SECRET_KEY` — Binance API auth
- `BITFINEX_API_KEY`, `BITFINEX_API_SECRET` — Bitfinex API auth
- `KUCOIN_API_KEY`, `KUCOIN_API_SECRET`, `KUCOIN_API_PASSPHRASE` — KuCoin API auth

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Main skill doc — Blave, BitMart Futures, and BitMart Spot sections |
| `references/blave-api.md` | Blave Python examples |
| `references/blave-indicator-guide.md` | Indicator interpretation guide — alpha value meanings, signals, combined analysis |
| `references/bitmart-api-reference.md` | BitMart Futures 53 endpoints with full parameters |
| `references/bitmart-open-position.md` | Futures open position workflow |
| `references/bitmart-close-position.md` | Futures close position workflow |
| `references/bitmart-plan-order.md` | Futures plan order workflow |
| `references/bitmart-tp-sl.md` | Futures TP/SL workflow |
| `references/bitmart-spot-api-reference.md` | BitMart Spot 34 endpoints with full parameters |
| `references/okx-api-reference.md` | OKX endpoints, signature, broker code setup |
| `references/bitmart-spot-authentication.md` | Spot auth details and examples |
| `references/bitmart-spot-scenarios.md` | Spot common trading scenarios |
| `references/bitmart-signature.md` | Python HMAC-SHA256 signature implementation + common mistakes |
| `references/hyperliquid-api.md` | Hyperliquid API — all 9 endpoints with params, response format, cache times |
| `references/tradingview-stream.md` | TradingView SSE stream — webhook setup, Python streaming client with reconnect |
| `references/bingx-api-reference.md` | BingX 59 endpoints, Python signature, spot + perpetual swap |
| `references/bitget-api-reference.md` | Bitget spot + futures endpoints, Python signature |
| `references/binance-api-reference.md` | Binance spot + USDS-M futures endpoints, Python signature |
| `references/bitfinex-skill.md` | Bitfinex spot, margin, funding/lending endpoints, HMAC-SHA384 signature |
| `references/kucoin-skill.md` | KuCoin spot + futures overview — auth, broker headers, operation flow, quick reference |
| `references/kucoin-api-reference.md` | KuCoin spot + futures full endpoints, Python signature + broker sign helper |
| `references/kucoin-bpp.md` | KuCoin Broker Pro Program — commission tiers, referral bonuses, dashboard guide |
| `references/twse-skill.md` | TWSE/TPEX 台股查詢 — 快速參考：endpoints、欄位說明、Python 搜尋範例 |
| `references/twse-api-reference.md` | TWSE/TPEX 完整 API 參考：上市/上櫃清單、行情、停復牌、民國年轉換 |
| `references/twse-bsr-reference.md` | TWSE BSR 分點資料 — 表單結構、CAPTCHA vision 解碼流程、Python 範例 |

## Blave API Endpoints

Base URL: `https://api.blave.org`

- `price` — current price + 24h change for a symbol (`symbol` required)
- `alpha_table` — latest alpha for all symbols; use for multi-coin queries or screening
- `kline` — OHLCV candlestick data
- `market_direction/get_alpha` — 市場方向 Market Direction (BTCUSDT)
- `market_sentiment/get_symbols` / `get_alpha` — 市場情緒 Market Sentiment time series + stat
- `capital_shortage/get_alpha` — 資金稀缺 Capital Shortage (market-wide)
- `sector_rotation/get_history_data` — 板塊輪動 Sector Rotation history
- `holder_concentration/get_symbols` / `get_alpha` — 籌碼集中度 Holder Concentration time series + stat
- `taker_intensity/get_symbols` / `get_alpha` — 多空力道 Taker Intensity time series + stat
- `whale_hunter/get_symbols` / `get_alpha` — 巨鯨警報 Whale Hunter; supports `score_type`
- `squeeze_momentum/get_symbols` / `get_alpha` — 擠壓動能 Squeeze Momentum + scolor; period fixed to `1d`
- `blave_top_trader/get_exposure` — Blave頂尖交易員 Top Trader Exposure (BTCUSDT)
- `liquidation/get_symbols` — list of symbols with liquidation data
- `liquidation/get_alpha` — 爆倉指標 Liquidation alpha time series + stat; `timeframe` default `24h`
- `liquidation/get_map` — liquidation heatmap: price levels vs USD exposure (`labels`, `liquidation`, `cumsum`, `oi_value`, `price`)
- `liquidation/get_map_change` — recent liquidation events by time window (`hist_0_1h`, `hist_1_8h`, `hist_8_24h`)
- `studio/market/twstock/price/<stock_id>` — Taiwan stock raw daily OHLCV; `start`/`end` optional (YYYY-MM-DD); data from 2000-01-04
- `studio/market/twstock/price_adj/<stock_id>` — Taiwan stock forward-adjusted (向後調整/後復權) daily OHLCV; same params; use for backtesting total return
- `studio/market/twstock/institutional/<stock_id>` — Taiwan stock 三大法人每日買賣超 (wide format: foreign / investment trust / dealer self / dealer hedging × buy / sell, in shares); `start`/`end` optional
- `studio/market/twstock/margin/<stock_id>` — Taiwan stock 融資融券每日資料 (`margin_buy`, `margin_sell`, `margin_balance`, `margin_prev_balance`, `margin_limit`, `margin_cash_repay`, `short_sell`, `short_buy`, `short_balance`, `short_prev_balance`, `short_limit`, `short_cash_repay`, `offset_loan_short`; all in shares); `start`/`end` optional; data from 1994-10-01
- `studio/market/twstock/shareholding/<stock_id>` — Taiwan stock 股權持股分級表 (weekly; `level`, `people`, `unit`, `percent` per bracket; 17 levels incl. `total`); `start`/`end` optional
- `studio/market/twstock/financials/<stock_id>` — 綜合損益表 quarterly fundamental (long format: `date`, `type`, `value`, `origin_name`); `start`/`end` optional; Redis-cached 24 h
- `studio/market/twstock/balance_sheet/<stock_id>` — 資產負債表 quarterly fundamental; same schema; `_per` suffix types are % of total assets
- `studio/market/twstock/cashflow/<stock_id>` — 現金流量表 quarterly fundamental; same schema
- `studio/market/twstock/monthly_revenue/<stock_id>` — 月營收 monthly revenue (`date`, `stock_id`, `country`, `revenue` in thousands NTD, `revenue_month`, `revenue_year`); `start`/`end` optional; data from 2000-01-01; Redis-cached 24 h
- `screener/get_saved_conditions` — user's saved screener conditions
- `screener/get_saved_condition_result` — symbols matching a saved condition (`condition_id` required)
- `hyperliquid/leaderboard` — top 100 Hyperliquid traders (`sort_by` param)
- `hyperliquid/traders` — Blave-curated tracked trader list with names/descriptions
- `hyperliquid/trader_position` — perp/spot positions + net equity (`address` required)
- `hyperliquid/trader_history` — fill history (`address` required)
- `hyperliquid/trader_performance` — cumulative PnL chart (`address` required)
- `hyperliquid/trader_open_order` — open orders (`address` required)
- `hyperliquid/top_trader_position` — aggregated long/short positions of top 100 traders
- `hyperliquid/top_trader_exposure_history` — historical net exposure (`symbol`, `period` required)
- `hyperliquid/bucket_stats` — profit/loss stats + positions by account value bucket

## BitMart Futures

Base URL: `https://api-cloud-v2.bitmart.com`

53 endpoints across market data, account, trading, plan orders, TP/SL, trailing stops, sub-accounts, affiliate, and simulated trading. See `references/bitmart-api-reference.md` for full details.

## BitMart Spot

Base URL: `https://api-cloud.bitmart.com`

34 endpoints across market data, account/wallet, trading (buy/sell), order queries, margin, and sub-accounts. Symbol format uses underscore: `BTC_USDT`. See `references/bitmart-spot-api-reference.md` for full details.

## BitMart Broker ID

Always include `X-BM-BROKER-ID: BlaveData666666` on **all** BitMart API requests (both futures and spot, regardless of auth level).

## Bybit Broker Header

Always include `referer: Ue001036` on **all** Bybit API requests (both public and authenticated).

## Bybit

Base URL: `https://api.bybit.com` | Backup: `https://api.bytick.com` | Testnet: `https://api-testnet.bybit.com`

Signature: `HMAC-SHA256(secret, {timestamp}{apiKey}{recvWindow}{queryString|jsonBody})`
Headers: `X-BAPI-API-KEY`, `X-BAPI-TIMESTAMP`, `X-BAPI-SIGN`, `X-BAPI-RECV-WINDOW: 5000`, `referer: Ue001036`

## BingX Source Header

Always include `X-SOURCE-KEY: BX-AI-SKILL` on **all** BingX API requests (both public and authenticated).

## BingX

Base URL: `https://open-api.bingx.com` | Fallback: `https://open-api.bingx.pro` | Paper: `https://open-api-vst.bingx.com`

Signature: `HMAC-SHA256(secret, sorted_params_canonical_string)` → hex, appended as `&signature=<hex>`
Headers: `X-BX-APIKEY`, `X-SOURCE-KEY: BX-AI-SKILL`

## Bitget

Base URL: `https://api.bitget.com`

Signature: `Base64(HMAC-SHA256(secret, timestamp + METHOD + path + body))`
Headers: `ACCESS-KEY`, `ACCESS-SIGN`, `ACCESS-PASSPHRASE`, `ACCESS-TIMESTAMP`

## Binance

Spot Base URL: `https://api.binance.com` | Futures Base URL: `https://fapi.binance.com`

Signature: `HMAC-SHA256(secret, queryString + requestBody)` → hex, `signature` as last param
Headers: `X-MBX-APIKEY`

## Binance Broker ID (Blave)

Broker attribution is per-order via `newClientOrderId` (NOT a header). Every order placement MUST include `newClientOrderId` starting with:
- Spot: `x-GBN6HWR2` (broker ID `GBN6HWR2`)
- USDS-M Futures: `x-52DDFAFN` (broker ID `52DDFAFN`)

Total length ≤ 36 chars. Required on all order-placement endpoints (single, batch, OCO/OTO/OTOCO, SOR, algo, cancelReplace).

## KuCoin Broker Attribution

Always include **4 broker headers** on **all** KuCoin API requests (spot and futures, public and private). Omitting them disqualifies broker rebates.

| Header | Spot | Futures |
|---|---|---|
| `KC-BROKER-NAME` | `blave` | `blaveFutures` |
| `KC-API-PARTNER` | `blave` | `blaveFutures` |
| `KC-API-PARTNER-SIGN` | `Base64(HMAC-SHA256("1c10e0c0-bc3e-4a18-ad53-e41e6df5f757", ts + "blave" + apiKey))` | `Base64(HMAC-SHA256("520815df-b324-4494-9bc8-b1015732b902", ts + "blaveFutures" + apiKey))` |
| `KC-API-PARTNER-VERIFY` | `true` | `true` |

## KuCoin

Spot Base URL: `https://api.kucoin.com` | Futures Base URL: `https://api-futures.kucoin.com`

Symbol format: Spot `BTC-USDT` | Futures `XBTUSDTM` (BTC uses `XBT`, append `USDTM` for linear perpetual)

Signature: `Base64(HMAC-SHA256(secret, timestamp + METHOD + path + body))` → headers: `KC-API-KEY`, `KC-API-SIGN`, `KC-API-TIMESTAMP`, `KC-API-PASSPHRASE` (signed), `KC-API-KEY-VERSION: 3`

## Bitfinex

Base URL: `https://api.bitfinex.com` (auth) | `https://api-pub.bitfinex.com` (public)

Signature: `HMAC-SHA384(secret, "/api/" + path + nonce + body)` → hex
Headers: `bfx-apikey`, `bfx-nonce`, `bfx-signature`
Affiliate code: `"meta": {"aff_code": "ZZDLtrXMF"}` on every order

## TWSE / TPEX — 台股市場查詢

**No API key required.** Public data, no authentication.

| Market | Base URL |
|---|---|
| TWSE 上市 | `https://openapi.twse.com.tw` |
| TPEX 上櫃 | `https://www.tpex.org.tw` |

Key endpoints:
- `GET /v1/exchangeReport/BWIBBU_ALL` — all listed stocks: `Code`, `Name`, `PEratio`, `DividendYield`, `PBratio`
- `GET /v1/exchangeReport/STOCK_DAY_ALL` — all listed stocks daily quote: open/high/low/close, volume
- `GET https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes` — all OTC stocks: `SecuritiesCompanyCode`, `CompanyName`, quote data

**Lookup flow:** Download full list → filter locally by `Code` or `Name` keyword.
When market is unknown, query both TWSE and TPEX and merge results.

Date format: ROC calendar — `1150507` = 2026/05/07 (民國115年05月07日)

All queries are read-only — **Safety Mode CONFIRM is NOT required.**

> Quick reference: `references/twse-skill.md`
> Full API reference with Python examples: `references/twse-api-reference.md`
