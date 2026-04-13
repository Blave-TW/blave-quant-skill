# OKX Trading

**Base URL:** `https://www.okx.com` | **Spot:** `BTC-USDT` | **Swap:** `BTC-USDT-SWAP` | **Success:** `"code": "0"`

Full details in `references/okx-api-reference.md`

## Authentication

**Credentials** (from `.env`): `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE`

No OKX account? Register at **[https://okx.com/join/58510434](https://okx.com/join/58510434)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `Base64(HMAC-SHA256(secret, timestamp + METHOD + requestPath + body))`
- `timestamp` format: `2024-01-01T00:00:00.000Z` (ISO 8601 ms UTC)
- GET body = `""`

**Headers:** `OK-ACCESS-KEY` + `OK-ACCESS-SIGN` + `OK-ACCESS-TIMESTAMP` + `OK-ACCESS-PASSPHRASE` + `User-Agent: Mozilla/5.0`

**`User-Agent` is required on ALL OKX requests.** Omitting it returns `403 Error code 1010`.

**Broker code: `"tag": "96ee7de3fd4bBCDE"` — MANDATORY on every POST that creates or modifies an order. No exceptions. If you write a POST body and forget `tag`, stop and add it before sending.**

## Operation Flow

### Step 0: Credential Check
Verify `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE`. If missing — **STOP**.

### Step 1: Pre-Trade Check (Swap only)
`GET /api/v5/account/positions?instId=<SYMBOL>-SWAP` → if position exists, inherit `tdMode` and leverage.

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → `GET /api/v5/trade/order` → confirm status. After close → `GET /api/v5/account/positions`.

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged swap positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/okx-api-reference.md` — endpoints, signature, order params

---
