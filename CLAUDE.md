# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains one skill covering sixteen capabilities:
1. **Blave** — Agent calls the Blave REST API directly for crypto market alpha data, Taiwan stock data, and Hyperliquid top trader tracking
2. **CME / ICE Futures** — Agent fetches WTI crude (CL), gold (GC), and Brent crude (BRN) OHLCV from 2010 via Blave API
3. **Taiwan Futures** — Agent fetches TXF (台指期近月連續) OHLCV (1d from 2013-12-30, intraday from 2014-01-02) via Blave API; schemas 1d/1m/5m/15m/30m/60m
4. **BitMart Futures** — Agent calls the BitMart API for perpetual futures trading
5. **BitMart Spot** — Agent calls the BitMart API for spot trading
6. **OKX** — Agent calls the OKX API for spot and perpetual swap trading
7. **Bybit** — Agent calls the Bybit API for spot and derivatives/perpetual swap trading
8. **BingX** — Agent calls the BingX API for spot and perpetual swap trading
9. **Bitget** — Agent calls the Bitget API for spot and futures trading
10. **Binance** — Agent calls the Binance API for spot and USDS-M futures trading
11. **Bitfinex** — Agent calls the Bitfinex API for spot, margin, and funding/lending
12. **KuCoin** — Agent calls the KuCoin API for spot and futures/perpetual contract trading
13. **Taiwan stock lookup/quote/PE** — Agent queries stock code/name lookup, daily quotes, PE/yield/PB via **Blave API** (`studio/market/twstock/list`, `/info`, `/price`, `/quote`, `/per`), NOT the raw TWSE/TPEX public API. That public API (no key required) is used only as a fallback for the two things Blave has no endpoint for: trading-halt status and a one-shot full-market PE/yield/PB scan
14. **台股分點買賣超** — Agent calls Blave API `GET /studio/market/twstock/broker/stock/<stock_id>` (by stock) or `GET /studio/market/twstock/broker/trader/<trader_id>` (by broker branch) for daily buy/sell data; no CAPTCHA required
15. **Taiwan Futures** — Agent calls Blave API `GET /studio/market/twfutures/ohlcv/TXF/<schema>` for TXF OHLCV; schemas: 1d/1m/5m/15m/30m/60m; 1d from 2013-12-30, intraday from 2014-01-02
16. **Gate.io** — Agent calls the Gate.io APIv4 for spot and USDT-settled perpetual futures trading

No CLI or wrapper involved. All API calls are made directly by the agent.

## Required `.env` Variables

- `blave_api_key`, `blave_secret_key` — Blave API auth
- `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO` — BitMart API auth
- `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE` — OKX API auth
- `BYBIT_API_KEY`, `BYBIT_SECRET_KEY` — Bybit API auth
- `BINGX_API_KEY`, `BINGX_SECRET_KEY` — BingX API auth
- `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE` — Bitget API auth
- `BINANCE_API_KEY`, `BINANCE_SECRET_KEY` — Binance API auth
- `BITFINEX_API_KEY`, `BITFINEX_API_SECRET` — Bitfinex API auth
- `KUCOIN_API_KEY`, `KUCOIN_API_SECRET`, `KUCOIN_API_PASSPHRASE` — KuCoin API auth
- `GATE_API_KEY`, `GATE_SECRET_KEY` — Gate.io API auth

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Main skill doc — Blave, BitMart Futures, and BitMart Spot sections |
| `references/blave-api.md` | Blave data API — single complete reference: every endpoint's parameters, defaults, response fields, errors, data start date, Python example (fixed per-endpoint block format) |
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
| `references/bingx-api-reference.md` | BingX 63 endpoints, Python signature, public market data + spot + perpetual swap |
| `references/bitget-api-reference.md` | Bitget spot + futures endpoints, Python signature |
| `references/binance-api-reference.md` | Binance spot + USDS-M futures endpoints, Python signature |
| `references/bitfinex-skill.md` | Bitfinex spot, margin, funding/lending endpoints, HMAC-SHA384 signature |
| `references/kucoin-skill.md` | KuCoin spot + futures overview — auth, broker headers, operation flow, quick reference |
| `references/kucoin-api-reference.md` | KuCoin spot + futures full endpoints, Python signature + broker sign helper |
| `references/kucoin-bpp.md` | KuCoin Broker Pro Program — commission tiers, referral bonuses, dashboard guide |
| `references/gateio-skill.md` | Gate.io spot + futures overview — auth, broker channel header, operation flow, quick reference |
| `references/gateio-api-reference.md` | Gate.io spot + futures full endpoints, Python signature + broker channel header |
| `references/twse-skill.md` | 停復牌狀態 + 全市場 PE 批次掃描（Blave API 沒有對應端點時才用）— 快速參考 |
| `references/twse-api-reference.md` | 同上，完整 API 參考：欄位說明、Python 範例、民國年轉換 |
| `references/twse-bsr-reference.md` | 台股分點買賣超 — 工作流程與 Python 範例（端點規格見 `references/blave-api.md`） |

## Blave API Endpoints

Every Blave data API endpoint is documented in `references/blave-api.md` (single source; `/hyperliquid/*` → `references/hyperliquid-api.md`). Do not list endpoints here.

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

## Gate.io Broker Channel Header

Always include `X-Gate-Channel-Id: blave` on **all** Gate.io API requests (spot and futures, public and authenticated). Omitting it disqualifies broker rebates.

## Gate.io

Base URL: `https://api.gateio.ws/api/v4`

Symbol format: `BTC_USDT` (spot and futures) | Futures settle: `usdt`

Signature: `HMAC-SHA512(secret, METHOD + "\n" + /api/v4/path + "\n" + query + "\n" + SHA512_hex(body) + "\n" + timestamp_seconds)` → hex
Headers: `KEY`, `Timestamp` (unix seconds), `SIGN`, `X-Gate-Channel-Id: blave`

## Bitfinex

Base URL: `https://api.bitfinex.com` (auth) | `https://api-pub.bitfinex.com` (public)

Signature: `HMAC-SHA384(secret, "/api/" + path + nonce + body)` → hex
Headers: `bfx-apikey`, `bfx-nonce`, `bfx-signature`
Affiliate code: `"meta": {"aff_code": "ZZDLtrXMF"}` on every order

## TWSE / TPEX — 台股市場查詢

**Blave API first.** Stock code/name lookup (`studio/market/twstock/list`, `/info/<stock_id>`), daily
quote/price (`/price/<stock_id>`, `/quote/<stock_id>`), and single-stock PE/yield/PB (`/per/<stock_id>`)
all go through Blave API — see `references/blave-api.md`. The raw TWSE/TPEX public API below (no key
required) is a fallback for only two things Blave has no endpoint for:

| Need | Base URL / endpoint |
|---|---|
| Trading-halt status | `GET https://openapi.twse.com.tw/v1/exchangeReport/TWTB4U` |
| One-shot full-market PE/yield/PB scan (not per-stock) | `GET https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL` (TWSE) / `GET https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes` (TPEX) |

Date format: ROC calendar — `1150507` = 2026/05/07 (民國115年05月07日)

All queries are read-only — **Safety Mode CONFIRM is NOT required.**

> Quick reference: `references/twse-skill.md`
> Full API reference with Python examples: `references/twse-api-reference.md`
