# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains one skill: **blave** — the agent calls the Blave REST API directly using credentials from `.env`. No CLI or wrapper involved.

Required `.env` variables:
- `blave_api_key`, `blave_secret_key` — Blave API auth

## Blave API Endpoints

See `blave/SKILL.md` for full documentation.

- `alpha_table` — latest alpha for all symbols across all indicators; use this to screen coins
- `kline` — OHLCV candlestick data; params: symbol, period, start_date, end_date
- `market_direction/get_alpha` — market direction alpha (BTCUSDT); params: period, start_date, end_date
- `market_sentiment/get_symbols` / `get_alpha` — market sentiment time series + stat
- `capital_shortage/get_alpha` — capital shortage alpha (market-wide); params: period, start_date, end_date
- `sector_rotation/get_history_data` — sector rotation history; no params
- `holder_concentration/get_symbols` / `get_alpha` — holder concentration time series + stat
- `taker_intensity/get_symbols` / `get_alpha` — taker intensity time series + stat
- `whale_hunter/get_symbols` / `get_alpha` — whale activity score time series + stat; supports `score_type` (`score_oi` / `score_volume`)
- `squeeze_momentum/get_symbols` / `get_alpha` — squeeze momentum time series + stat + scolor; period fixed to `1d`
- `blave_top_trader/get_exposure` — top trader net exposure (BTCUSDT); params: period, start_date, end_date
