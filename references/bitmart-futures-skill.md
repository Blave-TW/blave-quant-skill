# BitMart Futures Trading

**Base URL:** `https://api-cloud-v2.bitmart.com` | **Symbol:** `BTCUSDT` (no underscore) | **Success:** `code == 1000`

53 endpoints — full details in `references/bitmart-api-reference.md`

## Authentication

**Credentials** (from `.env`): `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`

No BitMart account? Register at **[https://www.bitmart.com/invite/cMEArf](https://www.bitmart.com/invite/cMEArf)**

Verify credentials before any private call. If missing — **STOP**.

| Level  | Endpoints          | Headers                                     |
| ------ | ------------------ | ------------------------------------------- |
| NONE   | Public market data | —                                           |
| KEYED  | Read-only private  | `X-BM-KEY`                                  |
| SIGNED | Write operations   | `X-BM-KEY` + `X-BM-SIGN` + `X-BM-TIMESTAMP` |

**Signature:** `HMAC-SHA256(secret, "{timestamp}#{memo}#{body}")` — GET body = `""`

**Always include `X-BM-BROKER-ID: BlaveData666666` on ALL requests.**

**IP Whitelist:** Use **public IP** (`curl https://checkip.amazonaws.com`), not private IP (`10.x`, `172.x`, `192.168.x`).

> Signature Python implementation and common mistakes: `references/bitmart-signature.md`

## Operation Flow

### Step 0: Credential Check

Verify `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`. If missing — **STOP**.

### Step 1.1: Query Positions (READ)

`GET /contract/private/position-v2` (KEYED, no signature needed)
Filter `current_amount != "0"` → display symbol, position_side, current_amount, entry_price, leverage, open_type, liquidation_price, unrealized_pnl

### Step 1.5: Pre-Trade Check (MANDATORY before open/leverage)

1. Call `GET /contract/private/position-v2?symbol=<SYMBOL>`
2. If `current_amount` non-zero → inherit `leverage` and `open_type`, do NOT override
3. If user wants different values → **STOP**, warn to close position first

### Step 1.55: Pre-Mode-Switch Check

Confirm no positions (Step 1.5) AND no open orders (`GET /contract/private/get-open-orders`). If either exists → **STOP**.

### Step 1.6: TP/SL on Existing Position

`POST /contract/private/submit-tp-sl-order` — submit TP and SL as **two separate calls**

| Param             | Value                            |
| ----------------- | -------------------------------- |
| `type`            | `"take_profit"` or `"stop_loss"` |
| `side`            | `3` close long / `2` close short |
| `trigger_price`   | Activation price                 |
| `executive_price` | `"0"` for market fill            |
| `price_type`      | `1` last / `2` mark              |
| `plan_category`   | `2`                              |

### Step 2: Execute

- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

**submit-order rules:**

| Scenario      | Send                                                           | Omit                       |
| ------------- | -------------------------------------------------------------- | -------------------------- |
| Open, market  | symbol, side, type:`"market"`, size, leverage, open_type       | price                      |
| Open, limit   | symbol, side, type:`"limit"`, price, size, leverage, open_type | —                          |
| Close, market | symbol, side, type:`"market"`, size                            | price, leverage, open_type |
| Close, limit  | symbol, side, type:`"limit"`, price, size                      | leverage, open_type        |

### Step 3: Verify

- After open: `position-v2` → report entry price, size, leverage, liquidation price
- After close: `position-v2` → report realized PnL
- After order: `GET /contract/private/order` → confirm status

## Order Reference

**Side:** `1` Open Long / `2` Close Short / `3` Close Long / `4` Open Short

**Mode:** `1` GTC / `2` FOK / `3` IOC / `4` Maker Only

**Timestamps:** ms — always convert to local time for display.

## Error Handling

| Code               | Action                                                    |
| ------------------ | --------------------------------------------------------- |
| 30005              | Wrong signature → see `references/bitmart-signature.md`   |
| 30007              | Timestamp drift → sync clock                              |
| 40012/40040        | Leverage/mode conflict → inherit existing position values |
| 40027/42000        | Insufficient balance → transfer from spot or reduce size  |
| 429                | Rate limited → wait                                       |
| 403/503 Cloudflare | Wait 30-60s, retry max 3×                                 |

## Spot ↔ Futures Transfer

Present summary → ask **"CONFIRM"** → execute.

**Endpoint:** `POST https://api-cloud-v2.bitmart.com/account/v1/transfer-contract` (SIGNED)

| Param      | Value                                        |
| ---------- | -------------------------------------------- |
| `currency` | `USDT` only                                  |
| `amount`   | transfer amount                              |
| `type`     | `"spot_to_contract"` or `"contract_to_spot"` |

Rate limit: 1 req/2sec. ⚠️ `/spot/v1/transfer-contract` does NOT exist.

## Security

- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Futures trading carries significant risk of loss."

## References

- `references/bitmart-api-reference.md` — 53 endpoints
- `references/bitmart-signature.md` — Python signature implementation
- `references/bitmart-open-position.md` / `bitmart-close-position.md` / `bitmart-plan-order.md` / `bitmart-tp-sl.md`

---
