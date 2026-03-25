# Take-Profit / Stop-Loss Workflow

> **Credentials:** Read from `.env` — `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`.

## Overview

TP/SL orders automatically close a position when the price reaches a specified take-profit or stop-loss level. They are essential for risk management in futures trading.

**Endpoint:** `POST /contract/private/submit-tp-sl-order`

**Important:** Each API call submits a single TP or SL order. To set both TP and SL, make two separate calls — one with `type:"take_profit"` and one with `type:"stop_loss"`.

**Plan categories:**
| Category | Value | Description |
|----------|-------|-------------|
| TP/SL Order | 1 | Applies to a specific quantity of contracts |
| Position TP/SL | 2 | Applies to the entire position (default, recommended) |

**TP/SL Side mapping:**
| Position | Close Side | TP Trigger | SL Trigger |
|----------|------------|------------|------------|
| Long | 3 (sell_close_long) | Price rises above TP price | Price falls below SL price |
| Short | 2 (buy_close_short) | Price falls below TP price | Price rises above SL price |

---

## Scenario 1: Set TP/SL for a Long Position

**User prompt:** "Set take profit at 72000 and stop loss at 64000 for my BTC long"

### Step 1: Get current position

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/position-v2?symbol=BTCUSDT'
```

Expected response:

```json
{
  "code": 1000,
  "data": [
    {
      "symbol": "BTCUSDT",
      "current_amount": "100",
      "position_amount": "100",
      "position_side": "long",
      "entry_price": "67000.0",
      "mark_price": "67123.4",
      "leverage": "10"
    }
  ]
}
```

If no long position exists, inform the user and STOP.

### Step 2: Calculate risk/reward

```
Entry Price:     67,000.0 USDT
Take Profit:     72,000.0 USDT  (+5,000.0, +7.46%)
Stop Loss:       64,000.0 USDT  (-3,000.0, -4.48%)
Risk/Reward:     1:1.67

Potential Profit: +500.00 USDT (100 contracts x 0.001 BTC x 5000)
Potential Loss:   -300.00 USDT (100 contracts x 0.001 BTC x 3000)
```

### Step 3: Present TP/SL summary and ask for CONFIRM

```
TP/SL Order Summary:
  Symbol: BTCUSDT
  Position: Long, 100 contracts @ 67,000.0 USDT
  Take Profit: 72,000.0 USDT (+7.46% from entry)
  Stop Loss: 64,000.0 USDT (-4.48% from entry)
  Type: Position TP/SL (entire position)
  Execution: Market
  Price Trigger: Last Price
  Risk/Reward Ratio: 1:1.67

  When BTCUSDT reaches 72,000 → position closes with ~+500 USDT profit
  When BTCUSDT reaches 64,000 → position closes with ~-300 USDT loss

Please type CONFIRM to proceed.
```

### Step 4: Submit TP order (after user confirms)

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","type":"take_profit","side":3,"trigger_price":"72000","executive_price":"0","price_type":1,"plan_category":2}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-tp-sl-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 5: Submit SL order

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","type":"stop_loss","side":3,"trigger_price":"64000","executive_price":"0","price_type":1,"plan_category":2}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-tp-sl-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 6: Verify and report

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/current-plan-order?symbol=BTCUSDT&plan_type=profit_loss'
```

```
TP/SL Order Set Successfully:
  Symbol: BTCUSDT
  Position: Long, 100 contracts
  Entry Price: 67,000.0 USDT
  Take Profit: 72,000.0 USDT (+7.46%)
  Stop Loss: 64,000.0 USDT (-4.48%)
  Risk/Reward: 1:1.67
  Status: Active

Not financial advice. Futures trading carries significant risk of loss.
```

---

## Scenario 2: Set TP/SL for a Short Position

**User prompt:** "Set TP at 62000 and SL at 70000 for my ETH short"

For short positions:
- **Side:** 2 (buy_close_short)
- **TP price** is *below* entry price (profit when price drops)
- **SL price** is *above* entry price (loss when price rises)

Submit TP:

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"ETHUSDT","type":"take_profit","side":2,"trigger_price":"62000","executive_price":"0","price_type":1,"plan_category":2}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-tp-sl-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

Submit SL:

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"ETHUSDT","type":"stop_loss","side":2,"trigger_price":"70000","executive_price":"0","price_type":1,"plan_category":2}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-tp-sl-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

---

## Scenario 3: TP/SL by Percentage

**User prompt:** "Set 5% take profit and 3% stop loss on my BTC long"

### Calculate TP/SL prices from percentage

Given entry_price = 67000:
- TP = 67000 * (1 + 0.05) = 70350.0
- SL = 67000 * (1 - 0.03) = 64990.0

Present the calculated prices and proceed with the standard flow.

---

## Scenario 4: Take-Profit Only

**User prompt:** "Set take profit at 75000 for BTC, no stop loss"

```json
{"symbol":"BTCUSDT","type":"take_profit","side":3,"trigger_price":"75000","executive_price":"0","price_type":1,"plan_category":2}
```

---

## Scenario 5: Stop-Loss Only

**User prompt:** "Set a stop loss at 63000 for my BTC long"

```json
{"symbol":"BTCUSDT","type":"stop_loss","side":3,"trigger_price":"63000","executive_price":"0","price_type":1,"plan_category":2}
```

---

## Scenario 6: Limit Execution TP/SL (Partial Position)

**User prompt:** "Set a limit take profit at 72000 with execution at 71900 for 50 contracts"

When using `plan_category=1` (partial position) with limit execution, provide `executive_price` and `category:"limit"`:

```json
{"symbol":"BTCUSDT","type":"take_profit","side":3,"trigger_price":"72000","executive_price":"71900","price_type":1,"plan_category":1,"size":50,"category":"limit"}
```

---

## Modifying TP/SL

**User prompt:** "Move my BTC take profit from 72000 to 74000"

### Step 1: Find existing TP/SL order

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/current-plan-order?symbol=BTCUSDT&plan_type=profit_loss'
```

### Step 2: Modify the TP/SL order

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":"45678901234567890","trigger_price":"74000","price_type":1,"plan_category":2}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/modify-tp-sl-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 3: Report updated TP/SL

```
TP/SL Updated:
  Take Profit: 72,000.0 → 74,000.0 USDT (+10.45% from entry)
  Stop Loss: 64,000.0 USDT (unchanged)
  New Risk/Reward: 1:2.33
```

---

## TP/SL Validation Rules

Before submitting, validate:

**Long positions (side=3):**
- TP `trigger_price` must be > current mark price
- SL `trigger_price` must be < current mark price
- SL `trigger_price` must be > liquidation price (otherwise liquidation triggers first)

**Short positions (side=2):**
- TP `trigger_price` must be < current mark price
- SL `trigger_price` must be > current mark price
- SL `trigger_price` must be < liquidation price

If validation fails, inform the user with a clear explanation:

```
Invalid Stop Loss: 60,000 USDT is below your liquidation price of 60,500 USDT.
Your position would be liquidated before the stop loss triggers.
Suggested minimum stop loss: 61,000 USDT (above liquidation price).
```

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| No position found | Position was closed or does not exist | Inform user |
| Invalid TP price | TP is on the wrong side of current price | Explain correct TP direction |
| Invalid SL price | SL is on the wrong side of current price | Explain correct SL direction |
| SL below liquidation | Position would liquidate first | Suggest SL above liquidation price |
| Order already exists | Duplicate TP/SL | Suggest modifying the existing order instead |
