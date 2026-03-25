# BitMart Spot Trading Scenarios

> **Credentials:** Read from `.env` — `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`.

## Scenario 1: Market Buy

**User prompt:** "Buy 100 USDT worth of BTC on BitMart"

### Step 1: Get current ticker price

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud.bitmart.com/spot/quotation/v3/ticker?symbol=BTC_USDT'
```

Expected response:

```json
{
  "code": 1000,
  "data": {
    "symbol": "BTC_USDT",
    "last": "67123.45",
    "ask_px": "67125.00",
    "bid_px": "67120.00"
  }
}
```

### Step 2: Check available balance

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud.bitmart.com/spot/v1/wallet'
```

Verify the user has at least 100 USDT available. If insufficient, inform the user and STOP.

### Step 3: Present order summary and ask for confirmation

Display to user:
```
Order Summary:
  Action: Market Buy BTC_USDT
  Amount: 100 USDT (notional)
  Estimated Price: ~67,125.00
  Estimated BTC: ~0.00149

Please type CONFIRM to proceed.
```

### Step 4: Submit market buy order (after user confirms)

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","side":"buy","type":"market","notional":"100"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v2/submit_order' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
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
    "order_id": "12345678901234567"
  }
}
```

### Step 5: Verify fill

```bash
TIMESTAMP=$(date +%s000)
BODY='{"orderId":"12345678901234567"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v4/query/order' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

Verify `state` is `"filled"`. Report to user: filled size, average price, and total cost.

### Error Handling

- If `code != 1000` on submit: report error message to user, do not retry automatically.
- If `state` is `"failed"`: report failure reason.
- If balance is insufficient: inform user before attempting order.

---

## Scenario 2: Limit Sell

**User prompt:** "Sell 0.5 ETH at 4000 USDT on BitMart"

### Step 1: Get current price to validate limit price

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud.bitmart.com/spot/quotation/v3/ticker?symbol=ETH_USDT'
```

Check that the limit price (4000) is reasonable relative to the current market price. Warn the user if it deviates significantly.

### Step 2: Check ETH balance

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud.bitmart.com/spot/v1/wallet'
```

Verify the user has at least 0.5 ETH available.

### Step 3: Present order summary and ask for confirmation

```
Order Summary:
  Action: Limit Sell ETH_USDT
  Size: 0.5 ETH
  Price: 4,000.00 USDT
  Total: ~2,000.00 USDT (if fully filled)

Please type CONFIRM to proceed.
```

### Step 4: Submit limit sell order

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"ETH_USDT","side":"sell","type":"limit","size":"0.5","price":"4000"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v2/submit_order' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 5: Monitor order status

```bash
TIMESTAMP=$(date +%s000)
BODY='{"orderId":"ORDER_ID"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v4/query/order' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

Report order status: `new` (pending), `partially_filled` (partially matched), or `filled` (complete).

### Error Handling

- `40044`: Invalid order size — check `GET /spot/v1/symbols/details` for min size.
- Price too far from market: warn user the order may not fill.
- Insufficient balance: inform user before submitting.

---

## Scenario 3: Batch Orders

**User prompt:** "Place buy orders for BTC at 60000, 59000, and 58000, each 0.001 BTC"

### Step 1: Check balance

Verify the user has at least `0.001 * 60000 + 0.001 * 59000 + 0.001 * 58000 = 177 USDT` available.

### Step 2: Present order summary

```
Batch Order Summary:
  1. Limit Buy 0.001 BTC @ 60,000 USDT = 60.00 USDT
  2. Limit Buy 0.001 BTC @ 59,000 USDT = 59.00 USDT
  3. Limit Buy 0.001 BTC @ 58,000 USDT = 58.00 USDT
  Total: 177.00 USDT

Please type CONFIRM to proceed.
```

### Step 3: Submit batch orders

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","orderParams":[{"side":"buy","type":"limit","size":"0.001","price":"60000"},{"side":"buy","type":"limit","size":"0.001","price":"59000"},{"side":"buy","type":"limit","size":"0.001","price":"58000"}]}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v4/batch_orders' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 4: Query each order

For each returned `order_id`, query its status:

```bash
TIMESTAMP=$(date +%s000)
BODY='{"orderId":"ORDER_ID"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v4/query/order' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

Report the status of all three orders.

### Error Handling

- If some orders in the batch fail while others succeed, report each individually.
- Partial failures do not affect successful orders.

---

## Scenario 4: Cancel and Replace

**User prompt:** "Change my BTC limit buy from 60000 to 59500"

### Step 1: Query open orders to find the target order

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v4/query/open-orders' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

Find the order with `price: "60000"` and `side: "buy"`. If multiple matches, ask the user to specify.

### Step 2: Cancel the existing order

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","order_id":"FOUND_ORDER_ID"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v3/cancel_order' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 3: Submit new order at updated price

Present the replacement order for confirmation:

```
Replace Order:
  Cancel: Buy 0.001 BTC @ 60,000 (order: FOUND_ORDER_ID)
  New: Buy 0.001 BTC @ 59,500

Please type CONFIRM to proceed.
```

After confirmation:

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","side":"buy","type":"limit","size":"0.001","price":"59500"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v2/submit_order' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 4: Verify new order

Query the new order to confirm it was placed successfully.

### Error Handling

- If cancel fails (order already filled): inform user the order has been filled and cannot be modified.
- If the original order was partially filled: report the filled portion and place the new order for the remaining size.
- Always cancel before placing the new order to avoid double exposure.

---

## Scenario 5: Portfolio Check

**User prompt:** "Show me my BitMart spot balance"

### Step 1: Get all balances with USD valuation

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud.bitmart.com/account/v1/wallet?needUsdValuation=true'
```

### Step 2: Filter and format

From the response, filter out currencies with zero balances (`available == "0"` and `frozen == "0"`).

### Step 3: Present portfolio summary

```
BitMart Spot Portfolio:
┌──────────┬───────────────┬────────────┬────────────────┐
│ Currency │ Available     │ Frozen     │ USD Value      │
├──────────┼───────────────┼────────────┼────────────────┤
│ BTC      │ 1.23456789    │ 0.10000000 │ $82,934.56     │
│ ETH      │ 15.50000000   │ 0.00000000 │ $53,580.90     │
│ USDT     │ 50,000.00     │ 1,000.00   │ $50,000.00     │
└──────────┴───────────────┴────────────┴────────────────┘
Total Portfolio Value: ~$186,515.46

Note: Not financial advice. Values are approximate based on current market prices.
```

### Error Handling

- If `code == 30002`: API key not configured. Guide user to set up credentials.
- If response contains no wallets: inform user the account has no assets.

---

## Scenario 6: Margin Trade

**User prompt:** "Borrow 1000 USDT on margin and buy ETH on BitMart"

### Step 1: Check margin account

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud.bitmart.com/spot/v1/margin/isolated/account?symbol=ETH_USDT'
```

Verify the margin account is enabled and check available borrowing limit.

### Step 2: Borrow assets

Present borrow details for confirmation:

```
Margin Borrow:
  Pair: ETH_USDT (isolated)
  Borrow: 1,000 USDT

Please type CONFIRM to proceed.
```

After confirmation:

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"ETH_USDT","currency":"USDT","amount":"1000"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v1/margin/isolated/borrow' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 3: Place margin order

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"ETH_USDT","side":"buy","type":"market","notional":"1000"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v1/margin/submit_order' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Step 4: Monitor and repay

After the user is ready to close the margin position and repay:

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"ETH_USDT","currency":"USDT","amount":"1000"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v1/margin/isolated/repay' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

### Error Handling

- If margin account not enabled: guide user to enable isolated margin for the pair on BitMart.
- If borrow limit exceeded: inform user of maximum borrowable amount.
- Always remind user about interest costs and liquidation risk for margin trading.
- Margin trading carries higher risk — always include appropriate warnings.
