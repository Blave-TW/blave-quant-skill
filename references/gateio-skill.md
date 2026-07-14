# Gate.io Trading

**Base URL:** `https://api.gateio.ws/api/v4` | **Spot:** `BTC_USDT` | **Futures:** `BTC_USDT` + `settle=usdt` | **Success:** HTTP 2xx (errors return `{"label": ..., "message": ...}`)

Full details in `references/gateio-api-reference.md`

## Broker Channel ID (Blave — MANDATORY on every request)

**Always include `X-Gate-Channel-Id: blave` on ALL Gate.io API requests (public and authenticated).** This is required for broker fee tracking — omitting it disqualifies broker rebates.

```
X-Gate-Channel-Id: blave
```

## Authentication

**Credentials** (from `.env`): `GATE_API_KEY`, `GATE_SECRET_KEY`

No Gate.io account? Register at **[https://www.gate.io/](https://www.gate.io/)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `HMAC-SHA512(secret, METHOD + "\n" + path + "\n" + query_string + "\n" + SHA512_hex(body) + "\n" + timestamp)` → hex
- `timestamp`: Unix **seconds** (string)
- `path`: full path including `/api/v4` prefix (e.g. `/api/v4/spot/orders`)
- `body`: raw JSON string; empty string for GET (SHA512 of `""` still required)

**Headers (authenticated requests):**
```
KEY: <api_key>
Timestamp: <unix seconds>
SIGN: <hex signature>
Content-Type: application/json
X-Gate-Channel-Id: blave
```

> Python signature implementation: `references/gateio-api-reference.md`

## Operation Flow

### Step 0: Credential Check
Verify `GATE_API_KEY`, `GATE_SECRET_KEY`. If missing — **STOP**.

### Step 1: Pre-Trade Check (Futures)
- Query positions: `GET /futures/usdt/positions`
- If position exists → inherit leverage and margin mode, do NOT override
- Futures `size` is in **contracts**, not coins — check `quanto_multiplier` via `GET /futures/usdt/contracts/{contract}` (e.g. BTC_USDT: 1 contract = `quanto_multiplier` BTC)

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → query order status. After close → query positions.

## Quick Reference

| Operation | Method | Path |
|---|---|---|
| Spot balances | GET | `/spot/accounts` |
| Spot ticker | GET | `/spot/tickers?currency_pair=BTC_USDT` |
| Place spot order | POST | `/spot/orders` |
| Cancel spot order | DELETE | `/spot/orders/{order_id}?currency_pair=...` |
| Spot open orders | GET | `/spot/open_orders` |
| Futures account | GET | `/futures/usdt/accounts` |
| Futures ticker | GET | `/futures/usdt/tickers?contract=BTC_USDT` |
| Contract detail (multiplier) | GET | `/futures/usdt/contracts/{contract}` |
| Place futures order | POST | `/futures/usdt/orders` |
| Cancel futures order | DELETE | `/futures/usdt/orders/{order_id}` |
| Futures positions | GET | `/futures/usdt/positions` |
| Set leverage | POST | `/futures/usdt/positions/{contract}/leverage?leverage=...` |

**Futures order rules:** `size` positive = buy, negative = sell (integer contracts). Market order = `price: "0"` + `tif: "ioc"`. Close position = `size: 0` + `close: true`. Custom order id via `text` field: must start with `t-`, ≤ 28 bytes after prefix, charset `0-9 A-Z a-z _ - .`

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/gateio-api-reference.md` — spot + futures endpoints, Python signature

---
