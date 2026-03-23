# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains one skill: **blave** — the agent calls the Blave REST API directly using credentials from `.env`. No CLI or wrapper involved.

Required `.env` variables:
- `blave_api_key`, `blave_secret_key` — Blave API auth

## Blave API Endpoints

See `blave/SKILL.md` for full documentation.

- `alpha_table` — latest alpha for all symbols across all indicators; use this to screen coins
- `holder_concentration/get_symbols` / `get_alpha` — holder concentration time series + stat
- `taker_intensity/get_symbols` / `get_alpha` — taker intensity time series + stat
- `whale_hunter/get_symbols` / `get_alpha` — whale activity score time series + stat; supports `score_type` (`score_oi` / `score_volume`)
