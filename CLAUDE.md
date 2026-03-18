# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

Only required for the Hyperliquid skill:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

Global CLI install:
```bash
chmod +x hyperliquid_cli.py
sudo ln -s /full/path/to/hyperliquid_cli.py /usr/local/bin/hyperliquid
```

Required `.env` variables:
- `blave_api_key`, `blave_secret_key` — Blave API auth
- `arbitrum_address`, `arbitrum_secret_key` — Hyperliquid wallet

## Architecture

This repo contains two independent skills.

| Skill | Type | Skill doc |
|---|---|---|
| blave | Direct API calls (no CLI) | `blave/SKILL.md` |
| hyperliquid | CLI (`hyperliquid_cli.py` → `src/hyperliquid_main.py`) | `hyperliquid/SKILL.md` |

**Blave skill** — Agent calls the Blave REST API directly using credentials from `.env`. No CLI or wrapper involved. See `blave/SKILL.md` for all endpoints.

**Hyperliquid skill** — CLI-based. `hyperliquid_cli.py` launches the venv and runs `src/hyperliquid_main.py`. Uses a `@command` decorator with `inspect` to parse CLI arguments.

**Hyperliquid modules:**
- `src/hyperliquid_bot/info.py` — Queries account balances and perpetual positions
- `src/hyperliquid_bot/trade.py` — `adjust_portfolio()` diffs target vs. current positions and fires market orders; skips orders below `min_usd_order` (default 10 USD); handles per-token decimal precision via `fetch_sz_decimals()`
- `src/hyperliquid_bot/utils.py` — Hyperliquid SDK initialization from `.env` credentials
