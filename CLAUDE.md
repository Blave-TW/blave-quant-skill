# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains one skill: **blave** — the agent calls the Blave REST API directly using credentials from `.env`. No CLI or wrapper involved.

Required `.env` variables:
- `blave_api_key`, `blave_secret_key` — Blave API auth

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Agent-facing skill doc — endpoints, params, usage guidelines |
| `API.md` | Python code examples for all endpoints |
| `README.md` | User-facing setup guide |

## Blave API Endpoints

- `alpha_table` — latest alpha for all symbols; use for multi-coin queries or screening
- `kline` — OHLCV candlestick data
- `market_direction/get_alpha` — market direction (BTCUSDT, no symbol param)
- `market_sentiment/get_symbols` / `get_alpha` — market sentiment time series + stat
- `capital_shortage/get_alpha` — capital shortage (market-wide, no symbol param)
- `sector_rotation/get_history_data` — sector rotation history
- `holder_concentration/get_symbols` / `get_alpha` — holder concentration time series + stat
- `taker_intensity/get_symbols` / `get_alpha` — taker intensity time series + stat
- `whale_hunter/get_symbols` / `get_alpha` — whale activity; supports `score_type` (`score_oi` / `score_volume`)
- `squeeze_momentum/get_symbols` / `get_alpha` — squeeze momentum + scolor; period fixed to `1d`
- `blave_top_trader/get_exposure` — top trader net exposure (BTCUSDT, no symbol param)
