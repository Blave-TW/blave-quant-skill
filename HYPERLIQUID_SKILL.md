---
name: hyperliquid
description: Fetch account info and trade on Hyperliquid.
---

# Hyperliquid Skill

This skill provides access to the `hyperliquid` command-line tool for querying and trading on the Hyperliquid exchange. Before executing any commands, ensure that `hyperliquid` is installed and the virtual environment is properly set up.

## 1. Fetch Hyperliquid Account

**Purpose**: Retrieve your account value and open positions on Hyperliquid.
**When to Use**: To monitor your assets and positions.

**Execution Steps**:

```bash
hyperliquid fetch_hyperliquid_account
```

## 2. Adjust Hyperliquid Portfolio

**Purpose**: Automatically adjust your Hyperliquid positions to match a target portfolio. Supports both buying and selling based on current holdings.
**When to Use**: To align your current positions with a predefined strategy or target portfolio.
**Parameters**:

- `target_portfolio_json` (str) — JSON string mapping token symbols to target USD amounts. **Required.**

**Execution Steps**:

- Define your target portfolio as a JSON string and run the command:

  ```bash
  hyperliquid adjust_hyperliquid_portfolio '{"BTC": 500, "ETH": 300}'
  ```

- The skill will:
  1. Fetch your current Hyperliquid positions (perp and/or spot).
  2. Calculate the difference between current positions and target portfolio.
  3. Place market orders to buy or sell tokens as needed.
  4. Return a list of executed orders with details.

**Notes**:

- Target portfolio amounts are in USD.
- Orders below the minimum threshold (`min_usd_order`, default 10 USD) are skipped.
