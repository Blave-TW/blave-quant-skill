# Plan (Conditional) Order Workflow

> **Credentials:** Read from `.env` — `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`.

## What Are Plan Orders?

Plan orders are conditional/trigger orders that remain dormant until a specified trigger price is reached. When the market price hits the trigger, the plan order is automatically submitted as a regular order (market or limit).

**Use cases:**
- **Buy the dip**: Set a trigger to open long when BTC drops to a support level
- **Breakout entry**: Set a trigger to open long when BTC breaks above resistance
- **Automated close**: Set a trigger to close a position at a target or stop price
- **Conditional strategy**: Enter positions based on price conditions without manual monitoring

**`price_way` (required):**
| Value | Name | Trigger Condition | Typical Use |
|-------|------|-------------------|-------------|
| 1 | Bullish | When market price **rises above** trigger_price | Breakout entry, stop loss for short |
| 2 | Bearish | When market price **drops below** trigger_price | Buy the dip, stop loss for long |

---

## Scenario 1: Trigger Buy Long on Dip

**User prompt:** "Open a long BTC position when price drops to 65000"

### Step 1: Validate parameters

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/details?symbol=BTCUSDT'
```

Check current price and validate trigger price is reasonable. If current price is 67000 and trigger is 65000, the order will wait until price drops to 65000.

### Step 2: Present plan order summary and ask for CONFIRM

```
Plan Order Summary:
  Symbol: BTCUSDT
  Type: Conditional / Trigger Order
  Direction: Open Long (buy_open_long, side=1)
  Trigger Price: 65,000.0 USDT (when last price reaches this)
  Execution Type: Market
  Size: 10 contracts
  Leverage: 10x
  Margin Mode: Cross
  Price Trigger: Last Price

  This order will remain pending until BTCUSDT reaches 65,000.0 USDT.
  When triggered, a market buy order for 10 contracts will be submitted.

Please type CONFIRM to proceed.
```

### Step 3: Submit plan order (after user confirms)

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","side":1,"trigger_price":"65000","type":"market","size":10,"leverage":"10","open_type":"cross","price_way":2,"price_type":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-plan-order' \
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
    "order_id": 34567890123456789
  }
}
```

### Step 4: Verify plan order is active

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/current-plan-order?symbol=BTCUSDT'
```

Confirm the plan order appears in the active plan orders list.

```
Plan Order Created Successfully:
  Order ID: 34567890123456789
  Symbol: BTCUSDT
  Trigger: Buy Long when price <= 65,000.0 USDT
  Execution: Market, 10 contracts, 10x leverage
  Status: Active (waiting for trigger)

Not financial advice. Futures trading carries significant risk of loss.
```

---

## Scenario 2: Trigger Limit Order on Breakout

**User prompt:** "Open a limit long at 72100 when BTC breaks above 72000"

### Submit plan order with limit type

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","side":1,"trigger_price":"72000","type":"limit","executive_price":"72100","size":10,"leverage":"10","open_type":"cross","price_way":1,"price_type":1,"mode":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-plan-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Key difference:** When triggered, a limit order at 72100 is placed instead of a market order. This gives price control but risks not filling if the price moves too quickly.

---

## Monitoring Plan Orders

### List all active plan orders

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/current-plan-order?symbol=BTCUSDT&plan_type=plan&limit=50'
```

Report active plan orders in a table:

```
Active Plan Orders (BTCUSDT):
┌───────────────────┬──────────┬─────────────┬──────────┬──────┬────────┐
│ Order ID          │ Side     │ Trigger      │ Type     │ Size │ Status │
├───────────────────┼──────────┼─────────────┼──────────┼──────┼────────┤
│ 34567890123456789 │ Open Long│ <= 65,000.0 │ Market   │ 10   │ Active │
│ 34567890123456790 │ Open Long│ >= 72,000.0 │ Limit    │ 10   │ Active │
└───────────────────┴──────────┴─────────────┴──────────┴──────┴────────┘
```

---

## Modifying a Plan Order

**User prompt:** "Change my plan order trigger from 65000 to 64000"

### Step 1: Find the plan order

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/current-plan-order?symbol=BTCUSDT&plan_type=plan'
```

Identify the order by trigger price or ask user for order ID if ambiguous.

### Step 2: Modify the plan order

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":"34567890123456789","type":"market","trigger_price":"64000","price_type":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/modify-plan-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

For **limit** type orders, also include `executive_price`:

```bash
BODY='{"symbol":"BTCUSDT","order_id":"34567890123456789","type":"limit","trigger_price":"64000","executive_price":"63500","price_type":1}'
```

Report the modification result.

---

## Canceling a Plan Order

**User prompt:** "Cancel my 65000 trigger order on BTC"

### Step 1: Find the plan order

Query active plan orders and identify the target by trigger price.

### Step 2: Cancel

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":"34567890123456789"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/cancel-plan-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 3: Verify cancellation

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/current-plan-order?symbol=BTCUSDT&plan_type=plan'
```

Confirm the order no longer appears in the active list.

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| Invalid trigger price | Trigger price is at or past current price | Adjust trigger price to be in the correct direction |
| Plan order not found | Already triggered or canceled | Check order history |
| Insufficient balance | Not enough margin when triggered | Ensure sufficient balance is maintained |
| Rate limit | Too many plan order requests | Wait for rate limit window to reset |
