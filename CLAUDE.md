# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

Global CLI install:
```bash
chmod +x blave_cli.py hyperliquid_cli.py
sudo ln -s /full/path/to/blave_cli.py /usr/local/bin/blave
sudo ln -s /full/path/to/hyperliquid_cli.py /usr/local/bin/hyperliquid
```

Required `.env` variables:
- `blave_api_key`, `blave_secret_key` — Blave platform auth
- `arbitrum_address`, `arbitrum_secret_key` — Hyperliquid wallet

## Running Commands

**Blave skill:**
```bash
blave check
blave fetch_news "bitcoin"
blave fetch_holder_concentration BTC
blave fetch_taker_intensity BTC --timeframe 24h
```

**Hyperliquid skill:**
```bash
hyperliquid check
hyperliquid fetch_hyperliquid_account
hyperliquid adjust_hyperliquid_portfolio '{"BTC": 500, "ETH": 300}'
```


## Architecture

This repo contains two independent skills sharing the same venv and dependencies.

| Skill | CLI entry | Main script | Skill doc |
|---|---|---|---|
| blave | `blave_cli.py` | `src/blave_main.py` | `blave/SKILL.md` |
| hyperliquid | `hyperliquid_cli.py` | `src/hyperliquid_main.py` | `hyperliquid/SKILL.md` |

**Command dispatch** (both main scripts): Uses a `@command` decorator with `inspect` to dynamically parse CLI arguments and route to registered functions.

**Modules:**
- `src/data_fetch.py` — `DataFetcher` class; calls `https://api.blave.org/{indicator}/get_alpha`
- `src/googlenews_fetch.py` — `GoogleNewsFetcher` wrapping the GoogleNews library
- `src/hyperliquid_bot/info.py` — Queries account balances and perpetual positions
- `src/hyperliquid_bot/trade.py` — `adjust_portfolio()` diffs target vs. current positions and fires market orders; skips orders below `min_usd_order` (default 10 USD); handles per-token decimal precision via `fetch_sz_decimals()`
- `src/hyperliquid_bot/utils.py` — Hyperliquid SDK initialization from `.env` credentials
