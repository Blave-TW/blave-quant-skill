# Close Position Workflow

> **Credentials:** Read from `.env` — `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`.

## Scenario: Close a Long Position

**User prompt:** "Close my BTC long position on BitMart"

### Step 1: Get current positions

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
      "leverage": "10",
      "current_amount": "100",
      "position_amount": "100",
      "position_side": "long",
      "entry_price": "67000.0",
      "mark_price": "67500.0",
      "liquidation_price": "60500.0",
      "unrealized_pnl": "50.00",
      "initial_margin": "670.00",
      "open_type": "cross"
    }
  ]
}
```

If no position is found, inform the user:

```
No open BTCUSDT long position found. Nothing to close.
```

If multiple positions exist (e.g., both long and short in hedge mode), ask the user which one to close.

### Step 2: Determine close side

| Position | Close Side | Description |
|----------|------------|-------------|
| Long | 3 (sell_close_long) | Sell to close the long position |
| Short | 2 (buy_close_short) | Buy to cover the short position |

For a long position: **side = 3**

### Step 3: Present close summary and ask for CONFIRM

```
Close Position Summary:
  Symbol: BTCUSDT
  Direction: Close Long (sell_close_long, side=3)
  Size: 100 contracts (entire position)
  Type: Market
  Entry Price: 67,000.0 USDT
  Current Mark Price: 67,500.0 USDT
  Unrealized PnL: +50.00 USDT (profit)
  Estimated Realized PnL: ~+50.00 USDT

Please type CONFIRM to proceed.
```

### Step 4: Submit close order (after user confirms)

> **Note:** Close orders only require `symbol`, `side`, `type`, and `size`.
> Do NOT include `leverage` or `open_type` — these fields are ignored for close orders and may cause confusion.
> For limit close, add `price`. For partial close, use a smaller `size`.

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","side":3,"type":"market","size":100}'
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
    "order_id": 23456789012345680
  }
}
```

### Step 5: Verify position closed

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/position-v2?symbol=BTCUSDT'
```

Verify the position no longer appears or the parsed `current_amount` is `0`.

Also check the fill details:

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/order?symbol=BTCUSDT&order_id=23456789012345680'
```

### Step 6: Report realized PnL

```
Position Closed Successfully:
  Symbol: BTCUSDT
  Direction: Closed Long
  Size: 100 contracts
  Entry Price: 67,000.0 USDT
  Exit Price: 67,498.5 USDT
  Realized PnL: +49.85 USDT
  Fees: 4.05 USDT
  Net PnL: +45.80 USDT
  Margin Released: 670.00 USDT

Not financial advice. You are solely responsible for your investment decisions.
```

---

## Scenario: Partial Close

**User prompt:** "Close half of my BTC long"

The flow is the same, but with size = 50 (half of 100):

```json
{"symbol":"BTCUSDT","side":3,"type":"market","size":50}
```

After partial close, report both the closed portion and the remaining position.

---

## Scenario: Close a Short Position

**User prompt:** "Close my ETH short position"

- Query positions for ETHUSDT
- Use **side = 2** (buy_close_short)
- For short positions, profit occurs when exit price < entry price

```json
{"symbol":"ETHUSDT","side":2,"type":"market","size":50}
```

---

## Scenario: Limit Close

**User prompt:** "Close my BTC long at 70000"

Use a limit order instead of market:

```json
{"symbol":"BTCUSDT","side":3,"type":"limit","price":"70000","size":100,"mode":1}
```

Inform the user that the order will remain open until the price reaches 70000 or they cancel it.

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| No position found | Position already closed or does not exist | Inform user |
| Size exceeds position | Trying to close more than held | Use the actual position amount |
| `code != 1000` on submit | Various | Report error message; do not retry automatically |
| Order state `failed` | System rejection | Check order details for failure reason |
| Partially filled close | Slippage or liquidity | Report partial fill; suggest retrying for remainder |
