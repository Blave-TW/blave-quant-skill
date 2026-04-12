# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains one skill covering five capabilities:
1. **Blave** — Agent calls the Blave REST API directly for crypto market alpha data
2. **BitMart Futures** — Agent calls the BitMart API for perpetual futures trading
3. **BitMart Spot** — Agent calls the BitMart API for spot trading
4. **Bybit** — Agent calls the Bybit API for spot and derivatives/perpetual swap trading
5. **BingX** — Agent calls the BingX API for spot and perpetual swap trading
6. **Bitget** — Agent calls the Bitget API for spot and futures trading
7. **Binance** — Agent calls the Binance API for spot and USDS-M futures trading

No CLI or wrapper involved. All API calls are made directly by the agent.

## Required `.env` Variables

- `blave_api_key`, `blave_secret_key` — Blave API auth
- `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO` — BitMart API auth
- `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE` — OKX API auth
- `BYBIT_API_KEY`, `BYBIT_API_SECRET` — Bybit API auth
- `BINGX_API_KEY`, `BINGX_SECRET_KEY` — BingX API auth
- `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE` — Bitget API auth
- `BINANCE_API_KEY`, `BINANCE_SECRET_KEY` — Binance API auth

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
