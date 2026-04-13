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

