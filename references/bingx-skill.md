# BingX Trading

**Base URL:** `https://open-api.bingx.com` | **Fallback:** `https://open-api.bingx.pro` | **Paper (VST):** `https://open-api-vst.bingx.com`

**Spot:** `BTC-USDT` | **Perpetual:** `BTC-USDT` | **Success:** `"code": 0`

42 swap endpoints + 17 spot endpoints — full details in `references/bingx-api-reference.md`

## Authentication

**Credentials** (from `.env`): `BINGX_API_KEY`, `BINGX_SECRET_KEY`

No BingX account? Register at **[https://bingxdao.com/invite/SU0SEU/](https://bingxdao.com/invite/SU0SEU/)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `HMAC-SHA256(secret, sorted_params_canonical_string)` → hex, appended as `&signature=<hex>`
- Collect all params + `timestamp` (Unix ms)
- Sort alphabetically by key, concatenate as `key=value&key=value`

**Headers (all requests):**
```
X-BX-APIKEY: <api_key>
X-SOURCE-KEY: BX-AI-SKILL
```

**`X-SOURCE-KEY: BX-AI-SKILL` is MANDATORY on every request — no exceptions.**

> Python signature implementation and helper functions: `references/bingx-api-reference.md`

## Operation Flow

### Step 0: Credential Check
Verify `BINGX_API_KEY`, `BINGX_SECRET_KEY`. If missing — **STOP**. Default to **Live** unless user explicitly requests paper trading (VST).

### Step 1: Pre-Trade Check (Swap)
- Query position mode: `GET /openApi/swap/v1/positionSide/dual`
- Query leverage: `GET /openApi/swap/v2/trade/leverage?symbol=<SYMBOL>`
- If position exists → inherit leverage and margin type, do NOT override

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → query order status. After close → query positions.

## Quick Reference

| Operation | Method | Path |
|---|---|---|
| Place swap order | POST | `/openApi/swap/v2/trade/order` |
| Cancel swap order | DELETE | `/openApi/swap/v2/trade/order` |
| Open swap orders | GET | `/openApi/swap/v2/trade/openOrders` |
| Order details | GET | `/openApi/swap/v2/trade/order` |
| Close all positions | POST | `/openApi/swap/v2/trade/closeAllPositions` |
| Set leverage | POST | `/openApi/swap/v2/trade/leverage` |
| Set margin mode | POST | `/openApi/swap/v2/trade/marginType` |
| Place spot order | POST | `/openApi/spot/v1/trade/order` |
| Cancel spot order | POST | `/openApi/spot/v1/trade/cancel` |
| Spot open orders | GET | `/openApi/spot/v1/trade/openOrders` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/bingx-api-reference.md` — 59 endpoints, Python signature, full params

---
