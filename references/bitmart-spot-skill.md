# BitMart Spot Trading

**Base URL:** `https://api-cloud.bitmart.com` | **Symbol:** `BTC_USDT` (underscore) | **Success:** `code == 1000`

34 endpoints — full details in `references/bitmart-spot-api-reference.md`

## Authentication

Same signature method as Futures. Credentials from `.env`: `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`

No BitMart account? Register at **[https://www.bitmart.com/invite/cMEArf](https://www.bitmart.com/invite/cMEArf)**

**Always include `X-BM-BROKER-ID: BlaveData666666` on ALL requests.**

**IP Whitelist:** Use **public IP** (`curl https://checkip.amazonaws.com`), not private IP.

> Signature Python implementation: `references/bitmart-signature.md`

## Operation Flow

### Step 0: Credential Check

Verify credentials. If missing — **STOP**.

### Step 1: Identify Intent

- **READ:** market data, balance, order history
- **WRITE:** submit/cancel orders, withdraw
- **TRANSFER:** spot ↔ futures → see Part 2 **Spot ↔ Futures Transfer**

### Step 2: Execute Orders

- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

**Endpoint:** `POST /spot/v2/submit_order`

| Scenario     | side   | type     | Key param                   |
| ------------ | ------ | -------- | --------------------------- |
| Buy, market  | `buy`  | `market` | `notional` (USDT to spend)  |
| Buy, limit   | `buy`  | `limit`  | `size` (base qty) + `price` |
| Sell, market | `sell` | `market` | `size` (base qty)           |
| Sell, limit  | `sell` | `limit`  | `size` + `price`            |

> Market buy uses `notional`, NOT `size`.

### Step 3: Verify

After order → query order detail. After cancel → check open orders.

## Order Reference

**Side:** `buy` / `sell` | **Type:** `limit` / `market` / `limit_maker` / `ioc`

**Status:** `new` / `partially_filled` / `filled` / `canceled` / `partially_canceled`

**Timestamps:** ms — always convert to local time.

## Error Handling

| Code               | Action                                                  |
| ------------------ | ------------------------------------------------------- |
| 30005              | Wrong signature → see `references/bitmart-signature.md` |
| 30007              | Timestamp drift → sync clock                            |
| 50000              | Insufficient balance                                    |
| 429                | Rate limited → wait                                     |
| 403/503 Cloudflare | Wait 30-60s, retry max 3×                               |

## Security

- WRITE operations require **"CONFIRM"**
- "Not financial advice. Spot trading carries risk of loss."

## References

- `references/bitmart-spot-api-reference.md` — 34 endpoints
- `references/bitmart-signature.md` — Python signature implementation
- `references/bitmart-spot-authentication.md` / `bitmart-spot-scenarios.md`

---
