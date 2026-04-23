# Binance Trading

**Spot Base URL:** `https://api.binance.com` | **Futures Base URL:** `https://fapi.binance.com`

**Spot:** `BTCUSDT` | **Futures:** `BTCUSDT` | **Testnet:** `https://testnet.binance.vision` (spot) / `https://demo-fapi.binance.com` (futures)

Full details in `references/binance-api-reference.md`

## Authentication

**Credentials** (from `.env`): `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`

No Binance account? Register at **[https://www.binance.com/](https://www.binance.com/)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `HMAC-SHA256(secret, queryString + requestBody)` → hex
- `timestamp`: Unix milliseconds (always required)
- `signature` must be the **last** parameter

**Headers:**
```
X-MBX-APIKEY: <api_key>
Content-Type: application/x-www-form-urlencoded   (POST)
```

> Python signature implementation: `references/binance-api-reference.md`

## Broker ID (Blave — MANDATORY on every order)

Binance brokers are attached **per order** via `newClientOrderId`, not via a header. Every place-order call **MUST** include `newClientOrderId` starting with `x-<BROKER_ID>`:

| Product | Broker ID | `newClientOrderId` prefix |
|---|---|---|
| Spot | `GBN6HWR2` | `x-GBN6HWR2` |
| USDS-M Futures | `52DDFAFN` | `x-52DDFAFN` |

Rules:
- Prefix starts with literal `x-` (lowercase), then the broker ID
- Total length ≤ 36 chars; append a unique suffix (timestamp/uuid fragment) to keep each ID unique
- Applies to: `/api/v3/order`, `/api/v3/order/cancelReplace`, `/api/v3/sor/order`, `/api/v3/orderList/oco|oto|otoco`, `/fapi/v1/order`, `/fapi/v1/batchOrders`, `/fapi/v1/algoOrder`, and their test/modify variants
- Batch orders: **every** order in the batch needs its own qualifying `newClientOrderId`
- If user supplies a custom `newClientOrderId`, reject it or prepend the broker prefix — never strip the prefix

```python
import time, uuid

def spot_cid(suffix: str = "") -> str:
    tag = suffix or uuid.uuid4().hex[:8]
    return f"x-GBN6HWR2{tag}"[:36]

def fut_cid(suffix: str = "") -> str:
    tag = suffix or uuid.uuid4().hex[:8]
    return f"x-52DDFAFN{tag}"[:36]

# Spot place order
spot_post("/api/v3/order", {
    "symbol": "BTCUSDT", "side": "BUY", "type": "MARKET",
    "quantity": "0.001",
    "newClientOrderId": spot_cid(),
})

# Futures place order
fapi_post("/fapi/v1/order", {
    "symbol": "BTCUSDT", "side": "BUY", "type": "MARKET",
    "quantity": "0.001",
    "newClientOrderId": fut_cid(),
})
```

## Operation Flow

### Step 0: Credential Check
Verify `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`. If missing — **STOP**. Default to **Mainnet** unless user explicitly requests Testnet.

### Step 1: Pre-Trade Check (Futures)
- Query positions: `GET /fapi/v2/positionRisk?symbol=<SYMBOL>`
- If position exists → inherit leverage and margin type, do NOT override

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → query order status. After close → query positions.

## Quick Reference — Spot

| Operation | Method | Path |
|---|---|---|
| Account info | GET | `/api/v3/account` |
| Place order | POST | `/api/v3/order` |
| Cancel order | DELETE | `/api/v3/order` |
| Cancel all | DELETE | `/api/v3/openOrders` |
| Query order | GET | `/api/v3/order` |
| Open orders | GET | `/api/v3/openOrders` |
| Order history | GET | `/api/v3/allOrders` |
| Trade fills | GET | `/api/v3/myTrades` |

## Quick Reference — USDS-M Futures

| Operation | Method | Path |
|---|---|---|
| Account balance | GET | `/fapi/v2/balance` |
| Account info | GET | `/fapi/v2/account` |
| Positions | GET | `/fapi/v2/positionRisk` |
| Place order | POST | `/fapi/v1/order` |
| Batch place | POST | `/fapi/v1/batchOrders` |
| Cancel order | DELETE | `/fapi/v1/order` |
| Cancel all | DELETE | `/fapi/v1/allOpenOrders` |
| Modify order | PUT | `/fapi/v1/order` |
| Open orders | GET | `/fapi/v1/openOrders` |
| Order history | GET | `/fapi/v1/allOrders` |
| Set leverage | POST | `/fapi/v1/leverage` |
| Set margin type | POST | `/fapi/v1/marginType` |
| Set position mode | POST | `/fapi/v1/positionSide/dual` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/binance-api-reference.md` — spot + futures endpoints, Python signature

