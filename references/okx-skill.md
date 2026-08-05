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

## Field-Verified Lessons (live account, 2026-08-05)

- **Swap `sz` is CONTRACTS, not base units** — convert base qty ÷ `ctVal` (public instruments endpoint), and do the division in Decimal: float `0.01 / 0.1 = 0.09999…` floors to one whole lot short (measured: a 0.01 ETH order filled 0.009)
- **The positions response's `ctVal` field is null** — for exact position sizes, look up `ctVal` from `GET /api/v5/public/instruments` and use `pos × ctVal`; deriving from `notionalUsd / markPx` reads back imprecise (0.001 ETH → 0.00099911 → floors to 0 contracts → unclosable dust)
- **The real error is `data[].sCode`/`sMsg`** — the top-level `code`/`msg` often just says "Operation failed"
- Hedge (`long_short_mode`) accounts have NO `reduceOnly` — closing is expressed by `posSide` + opposite order side; net mode uses native `reduceOnly` (mode from `GET /api/v5/account/config` → `posMode`)
- Spot market BUYs size in quote currency (`tgtCcy=quote_ccy`, `sz` = USDT amount); SELLs in base (`tgtCcy=base_ccy`); `51020` = below minimum
- SL/TP are algo orders (`/api/v5/trade/order-algo`, `ordType=conditional`, market exec `slOrdPx=-1`, whole position `closeFraction=1`) with their own `algoId` + pending/cancel endpoints — regular order queries never see them
- Broker tag `96ee7de3fd4bBCDE` goes in the BODY of every order-creating POST
- `clOrdId` dedup covers only the UN-FILLED window — a reused id is accepted once the original order is terminal (measured live: second market order with the same clOrdId filled). Treat it as a retry-window guard, not a permanent ledger

## References
- `references/okx-api-reference.md` — endpoints, signature, order params

---
