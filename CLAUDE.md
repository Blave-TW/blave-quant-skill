# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains one skill covering three capabilities:
1. **Blave** — Agent calls the Blave REST API directly for crypto market alpha data
2. **BitMart Futures** — Agent calls the BitMart API for perpetual futures trading
3. **BitMart Spot** — Agent calls the BitMart API for spot trading

No CLI or wrapper involved. All API calls are made directly by the agent.

## Required `.env` Variables

- `blave_api_key`, `blave_secret_key` — Blave API auth
- `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO` — BitMart API auth

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

## Blave API Endpoints

Base URL: `https://api.blave.org`

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

## BitMart Futures

Base URL: `https://api-cloud-v2.bitmart.com`

53 endpoints across market data, account, trading, plan orders, TP/SL, trailing stops, sub-accounts, affiliate, and simulated trading. See `references/bitmart-api-reference.md` for full details.

## BitMart Spot

Base URL: `https://api-cloud.bitmart.com`

34 endpoints across market data, account/wallet, trading (buy/sell), order queries, margin, and sub-accounts. Symbol format uses underscore: `BTC_USDT`. See `references/bitmart-spot-api-reference.md` for full details.

## BitMart Broker ID

Always include `X-BM-BROKER-ID: BlaveData666666` on **all** BitMart API requests (both futures and spot, regardless of auth level).
