# Open Position Workflow

> **Credentials:** Read from `.env` — `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`.

## Scenario: Open a Long Position

**User prompt:** "Open a 10x long BTC position with 100 contracts on BitMart"

### Step 1: Pre-flight — Check futures balance

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/assets-detail'
```

Verify the user has sufficient `available_balance` in USDT. If insufficient, suggest transferring from spot:

```
Insufficient futures balance. Available: 50.00 USDT, Required: ~670 USDT (estimated).
Would you like to transfer USDT from your spot wallet?
```

### Step 2: Pre-flight — Check contract details

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/details?symbol=BTCUSDT'
```

Validate:
- `contract_size` — to calculate margin requirement
- `min_volume` — ensure order size meets minimum
- `max_volume` — ensure order size does not exceed maximum
- `max_leverage` — ensure requested leverage is supported
- `price_precision` — for limit orders

### Step 3: Pre-flight — Check leverage brackets

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/leverage-bracket?symbol=BTCUSDT'
```

Verify the requested leverage (10x) is available for the position size. If position size exceeds the tier limit, warn the user:

```
Warning: At 10x leverage, maximum position is 500,000 contracts.
Your requested 100 contracts is within limits.
```

### Step 3.5: Check existing position (MANDATORY)

Before setting leverage or submitting an order, check for existing positions:

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/position-v2?symbol=BTCUSDT'
```

`position-v2` returns a `data[]` array. Do **not** assume there is only one row:
- In `one_way_mode`, you will typically see one row with `position_side="both"`
- In some account / mode combinations, you may see multiple rows for the same symbol (for example `position_side="long"` and `position_side="short"`), even when both sides are zero

Use this step to answer two questions only:
- Does a position already exist?
- If yes, which `leverage` and `open_type` must be inherited?

Do **not** rely on `position-v2` for `position_mode`. Query `get-position-mode` later only when the workflow becomes mode-sensitive (for example, deciding whether to switch modes or explaining hedge vs one-way behavior).

Evaluate the **entire** `data[]` array:

Parse each row's `current_amount` as a number before comparing it. The API returns string values such as `"0"`.

**If any row's parsed `current_amount` is non-zero (existing position found):**
- Treat the symbol as having an existing position
- Use the relevant non-zero position row's `leverage` and `open_type` values in the order — do NOT send different values
- If user requested different leverage or margin mode → **STOP** and warn:
  > "You have an existing position. Close it first before changing leverage or margin mode."
- Do NOT call `submit-leverage` with different values — API will return 40012/40040
- Do **not** attempt to change `position_mode` while an existing position is present
- Skip Step 4 and continue with the current account mode in Step 5

**If every row's parsed `current_amount` is 0 (no existing position):**
- Proceed with user-requested leverage and margin mode (Step 4)

### Step 4: Set leverage (if needed — skip if existing position found in Step 3.5)

Only execute this step when no existing position was found in Step 3.5:

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","leverage":"10","open_type":"cross"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-leverage' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 5: Check current position mode and set it only if safe

Query the account-wide `position_mode` only when you need a mode-sensitive decision, such as deciding whether a mode switch is needed or explaining current hedge/one-way behavior:

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/get-position-mode'
```

Read the current account-wide position mode first:

- If Step 3.5 found any existing position (any row's parsed `current_amount` is non-zero), **do not call** `set-position-mode`
- If the user requested a different position mode while an existing position is present, **STOP** and tell them to close the existing position first
- Before any mode switch, check that there are no open orders on the account:

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/get-open-orders'
```

- If any open orders are present, **STOP** and tell the user to cancel them before changing `position_mode`
- Only consider calling `set-position-mode` when Step 3.5 found **no** existing position and `get-open-orders` is empty

If the user wants hedge mode (to hold long and short simultaneously), Step 3.5 found no existing position, and the current mode is not already `hedge_mode`, set it:

```bash
TIMESTAMP=$(date +%s000)
BODY='{"position_mode":"hedge_mode"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/set-position-mode' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Note:** BitMart rejects `set-position-mode` when the account is not in a clean state for mode switching. Existing positions will fail, and open orders may also fail with `40059` (`"Some positions exist and the mode switching fails."`). If mode switching fails, stop and ask the user to clear existing positions / open orders before retrying.

### Step 6: Present order summary and ask for CONFIRM

Display to user:

```
Position Summary:
  Symbol: BTCUSDT
  Direction: Long (buy_open_long, side=1)
  Type: Market
  Size: 100 contracts
  Leverage: 10x
  Margin Mode: Cross
  Estimated Entry: ~67,123 USDT
  Estimated Margin: ~671 USDT
  Estimated Liquidation: ~60,500 USDT

  WARNING: Futures trading carries significant risk. Higher leverage
  amplifies both gains and losses. You could lose your entire margin.

Please type CONFIRM to proceed.
```

### Step 7: Submit order (after user confirms)

**Parameter rules (must match SKILL.md Step 2a):**
- **Market order:** do NOT include `price` field — it is ignored and causes confusion
- **If existing position found in Step 3.5:** use `leverage` and `open_type` from the relevant non-zero position row, not user-requested values
- **`size` must be an integer** (number of contracts) — check min/max via `GET /contract/public/details`
- **Maker Only (`mode=4`):** only valid with `type=limit`, never with `type=market`

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","side":1,"type":"market","size":100,"leverage":"10","open_type":"cross"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

Expected response:

```json
{
  "code": 1000,
  "data": {
    "order_id": 23456789012345678
  }
}
```

### Step 8: Verify position

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/position-v2?symbol=BTCUSDT'
```

### Step 9: Report results

```
Position Opened Successfully:
  Symbol: BTCUSDT
  Direction: Long
  Size: 100 contracts
  Entry Price: 67,123.4 USDT
  Leverage: 10x
  Margin Mode: Cross
  Margin Used: 671.23 USDT
  Liquidation Price: 60,500.0 USDT
  Mark Price: 67,125.0 USDT
  Unrealized PnL: +0.16 USDT

Not financial advice. Futures trading carries significant risk of loss.
```

---

## Scenario: Open a Short Position

**User prompt:** "Short ETH with 20x leverage, 50 contracts, isolated margin"

The flow is the same as above, with these differences:

- **Side:** 4 (sell_open_short) instead of 1
- **Leverage:** 20x
- **Open type:** isolated
- **Liquidation direction:** above entry price (for shorts, liquidation is at higher price)

Order body:

```json
{"symbol":"ETHUSDT","side":4,"type":"market","size":50,"leverage":"20","open_type":"isolated"}
```

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| `code != 1000` on submit | Various | Report error message; do not retry automatically |
| Insufficient balance | Not enough margin | Suggest transferring from spot or reducing position size |
| Invalid leverage | Exceeds bracket limit | Show leverage brackets and suggest a valid leverage |
| Position mode conflict | Has open positions | Cannot change mode; inform user to close positions first |
| Invalid size | Below min or above max | Show contract details with min/max volume |
