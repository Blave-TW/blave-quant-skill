# Bybit Trading

**Base URL (Mainnet):** `https://api.bybit.com` | **Backup:** `https://api.bytick.com` | **Testnet:** `https://api-testnet.bybit.com`

**Spot:** `BTCUSDT` | **Perpetual:** `BTCUSDT` (Linear) | **Success:** `"retCode": 0`

## Authentication

**Credentials** (from `.env`): `BYBIT_API_KEY`, `BYBIT_API_SECRET`

No Bybit account? Register at **[https://partner.bybit.com/b/BLAVE](https://partner.bybit.com/b/BLAVE)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `HMAC-SHA256(secret, {timestamp}{apiKey}{recvWindow}{queryString|jsonBody})`
- GET: sign `{timestamp}{apiKey}{recvWindow}{queryString}`
- POST: sign `{timestamp}{apiKey}{recvWindow}{jsonBody}` — use **compact JSON** (no spaces, no newlines)

**Headers (all authenticated requests):**
```
X-BAPI-API-KEY: $BYBIT_API_KEY
X-BAPI-TIMESTAMP: <unix ms>
X-BAPI-SIGN: <hmac signature>
X-BAPI-RECV-WINDOW: 5000
referer: Ue001036
Content-Type: application/json   (POST only)
```

**`referer: Ue001036` is MANDATORY on every request — no exceptions.**

## Operation Flow

### Step 0: Credential Check
Verify `BYBIT_API_KEY`, `BYBIT_API_SECRET`. If missing — **STOP**. Default to **Mainnet** unless user explicitly requests Testnet.

### Step 1: Pre-Trade Check
`GET /v5/position/list?category=linear&symbol=<SYMBOL>` → if position exists, inherit side and leverage.

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → `GET /v5/order/realtime` → confirm status. After close → `GET /v5/position/list`.

## Key Endpoints

| Action | Method | Path |
|---|---|---|
| Market info | GET | `/v5/market/instruments-info` |
| Ticker | GET | `/v5/market/tickers` |
| Wallet balance | GET | `/v5/account/wallet-balance` |
| Place order | POST | `/v5/order/create` |
| Cancel order | POST | `/v5/order/cancel` |
| Open orders | GET | `/v5/order/realtime` |
| Positions | GET | `/v5/position/list` |
| Set leverage | POST | `/v5/position/set-leverage` |
| Set TP/SL | POST | `/v5/position/set-tpsl` |
| Order history | GET | `/v5/order/history` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

---
