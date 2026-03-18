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
chmod +x blave_cli.py
sudo ln -s /full/path/to/blave_cli.py /usr/local/bin/blave
```

Required `.env` variables:
- `blave_api_key`, `blave_secret_key` — Blave platform auth
- `arbitrum_address`, `arbitrum_secret_key` — Hyperliquid wallet
- `threads_user_id`, `threads_access_token`, `threads_secret`, `threads_original_token` — Threads API

## Running Commands

```bash
blave check                          # Health check
blave fetch_news --keyword bitcoin   # Fetch news
blave fetch_hyperliquid_account      # Get account value and positions
blave adjust_hyperliquid_portfolio   # Rebalance portfolio
blave fetch_holder_concentration     # Blave alpha data
blave fetch_taker_intensity          # Blave alpha data
blave fetch_threads_insight_table    # Threads analytics
blave create_text_post               # Publish to Threads
```

## Architecture

**CLI flow:** `blave_cli.py` (launches venv) → `src/main.py` (command router) → module functions

**Command dispatch** (`src/main.py`): Uses a `@command` decorator with `inspect` to dynamically parse CLI arguments and route to registered functions.

**Modules:**
- `src/data_fetch.py` — `DataFetcher` class; calls `https://api.blave.org/{indicator}/get_alpha`
- `src/googlenews_fetch.py` — `GoogleNewsFetcher` wrapping the GoogleNews library
- `src/threads.py` — Threads Graph API; post creation is two-step (create container → publish)
- `src/hyperliquid_bot/info.py` — Queries account balances and perpetual positions
- `src/hyperliquid_bot/trade.py` — `adjust_portfolio()` diffs target vs. current positions and fires market orders; skips orders below `min_usd_order` (default 10 USD); handles per-token decimal precision via `fetch_sz_decimals()`
- `src/hyperliquid_bot/utils.py` — Hyperliquid SDK initialization from `.env` credentials
