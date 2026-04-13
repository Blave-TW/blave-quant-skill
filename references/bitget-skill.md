# Bitget Trading

**Base URL:** `https://api.bitget.com` | **Spot:** `BTCUSDT` | **Futures:** `BTCUSDT` + `productType=USDT-FUTURES` | **Success:** `"code": "00000"`

Full details in `references/bitget-api-reference.md`

## Authentication

**Credentials** (from `.env`): `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE`

No Bitget account? Register at **[https://www.bitget.com/](https://www.bitget.com/)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `Base64(HMAC-SHA256(secret, timestamp + METHOD + path + body))`
- `timestamp`: Unix milliseconds
- GET body = `""`
- POST body = compact JSON (no spaces)

**Headers (authenticated requests):**
```
ACCESS-KEY: <api_key>
ACCESS-SIGN: <base64 signature>
ACCESS-PASSPHRASE: <passphrase>
ACCESS-TIMESTAMP: <unix ms>
Content-Type: application/json
locale: en-US
```

> Python signature implementation: `references/bitget-api-reference.md`

## Operation Flow

### Step 0: Credential Check
Verify `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE`. If missing — **STOP**.

### Step 1: Pre-Trade Check (Futures)
- Query positions: `GET /api/v2/mix/position/all-position?productType=USDT-FUTURES`
- If position exists → inherit leverage and margin mode, do NOT override

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → query order status. After close → query positions.

## Quick Reference

| Operation | Method | Path |
|---|---|---|
| Spot balances | GET | `/api/v2/spot/account/assets` |
| Futures account | GET | `/api/v2/mix/account/accounts?productType=USDT-FUTURES` |
| All balances | GET | `/api/v2/account/all-account-balance` |
| Place spot order | POST | `/api/v2/spot/trade/place-order` |
| Cancel spot order | POST | `/api/v2/spot/trade/cancel-order` |
| Spot open orders | GET | `/api/v2/spot/trade/unfilled-orders` |
| Place futures order | POST | `/api/v2/mix/order/place-order` |
| Cancel futures order | POST | `/api/v2/mix/order/cancel-order` |
| Futures positions | GET | `/api/v2/mix/position/all-position` |
| Set leverage | POST | `/api/v2/mix/account/set-leverage` |
| Set margin mode | POST | `/api/v2/mix/account/set-margin-mode` |
| Spot ticker | GET | `/api/v2/spot/market/tickers` |
| Futures ticker | GET | `/api/v2/mix/market/ticker` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/bitget-api-reference.md` — spot + futures endpoints, Python signature

---
