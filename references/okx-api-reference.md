# OKX API Reference

**Base URL:** `https://www.okx.com`

**Success:** HTTP 200 + `"code": "0"` in response body

---

## Authentication

**Algorithm:** `Base64(HMAC-SHA256(secret, prehash))`

**Pre-hash:** `timestamp + METHOD + requestPath + body`

- `timestamp` — ISO 8601 milliseconds UTC: `2024-01-01T00:00:00.000Z`
- `METHOD` — `GET` or `POST` (uppercase)
- `requestPath` — full path + query string, e.g. `/api/v5/account/balance?ccy=BTC`
- `body` — raw JSON string for POST; `""` for GET

**Required headers (all private endpoints):**

| Header | Value |
|---|---|
| `OK-ACCESS-KEY` | API key |
| `OK-ACCESS-SIGN` | Base64(HMAC-SHA256 signature) |
| `OK-ACCESS-TIMESTAMP` | ISO 8601 ms timestamp |
| `OK-ACCESS-PASSPHRASE` | Passphrase set at key creation |
| `Content-Type` | `application/json` (POST only) |

**Credentials from `.env`:** `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE`

```python
import hmac, hashlib, base64
from datetime import datetime, timezone

def okx_sign(secret, timestamp, method, path, body=""):
    prehash = timestamp + method.upper() + path + body
    return base64.b64encode(
        hmac.new(secret.encode(), prehash.encode(), hashlib.sha256).digest()
    ).decode()

def okx_timestamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + \
           f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
```

---

## Broker Code

**`"tag": "96ee7de3fd4bBCDE"` — include in the body of EVERY POST that creates or modifies an order. This is non-negotiable.**

Required on (all POST order-creation endpoints):
- `POST /api/v5/trade/order` — single order
- `POST /api/v5/trade/batch-orders` — batch orders
- `POST /api/v5/trade/order-algo` — algo orders (TP/SL, trailing stop, TWAP, iceberg)
- `POST /api/v5/trade/amend-order` — amend order
- Any other POST endpoint that creates or updates an order

Not applicable on: GET queries, `POST /api/v5/trade/cancel-order`, `POST /api/v5/trade/cancel-batch-orders`, `POST /api/v5/trade/close-position` (these do not accept `tag`).

**Checklist before every POST order call:** Does the body contain `"tag": "96ee7de3fd4bBCDE"`? If not — add it now.

---

## Instrument ID Format

| Type | Format | Example |
|---|---|---|
| Spot | `{BASE}-{QUOTE}` | `BTC-USDT` |
| Perpetual Swap | `{BASE}-{QUOTE}-SWAP` | `BTC-USDT-SWAP` |
| Delivery Futures | `{BASE}-{QUOTE}-{YYMMDD}` | `BTC-USDT-250328` |

---

## Key Endpoints

### Account

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v5/account/balance` | SIGNED | Account balance. `?ccy=USDT` to filter |
| GET | `/api/v5/account/positions` | SIGNED | Open positions. `?instType=SWAP` |

### Spot Trading

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v5/trade/order` | SIGNED | Place order |
| POST | `/api/v5/trade/cancel-order` | SIGNED | Cancel order |
| GET | `/api/v5/trade/orders-pending` | SIGNED | Active orders |
| GET | `/api/v5/trade/order` | SIGNED | Order detail |
| GET | `/api/v5/trade/orders-history` | SIGNED | Order history (7 days) |

### Perpetual Swap Trading

Same endpoints as spot — differentiate via `instId` (`BTC-USDT-SWAP`) and `tdMode`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v5/trade/order` | SIGNED | Open/close position |
| POST | `/api/v5/trade/close-position` | SIGNED | Close full position |
| GET | `/api/v5/account/positions` | SIGNED | Open positions |

### Market Data (Public)

| Method | Path | Description |
|---|---|---|
| GET | `/api/v5/market/ticker?instId=BTC-USDT` | Last price, 24h stats |
| GET | `/api/v5/market/candles?instId=BTC-USDT&bar=1H` | OHLCV candles |
| GET | `/api/v5/public/funding-rate?instId=BTC-USDT-SWAP` | Funding rate |
| GET | `/api/v5/public/instruments?instType=SWAP&instId=BTC-USDT-SWAP` | Instrument specs — **query before every swap order** |

---

## Swap Contract Size — Always Query `ctVal`

**Never hardcode contract sizes.** Each instrument has a different `ctVal` (contract value in base currency). Always fetch it before calculating swap order size.

**Step 1 — Query instrument specs:**
```
GET /api/v5/public/instruments?instType=SWAP&instId={instId}
```
Extract from response: `ctVal` (base units per contract), `minSz` (minimum contracts), `lotSz` (contract size step).

**Step 2 — Calculate contracts:**
```
contracts = usd_amount / (current_price * ctVal)
# Round down to lotSz precision, must be >= minSz
```

**Example (do NOT hardcode these — query live):**
- BTC-USDT-SWAP: ctVal=0.01 → 1 contract ≈ 0.01 BTC
- ETH-USDT-SWAP: ctVal=0.1 → 1 contract ≈ 0.1 ETH

**Error 51008 (Insufficient margin):** Recalculate using the actual `ctVal` from the API — do not guess.

---

## Place Order Parameters

**`POST /api/v5/trade/order`**

| Param | Required | Description |
|---|---|---|
| `instId` | ✓ | e.g. `BTC-USDT` or `BTC-USDT-SWAP` |
| `tdMode` | ✓ | `cash` (spot) / `cross` / `isolated` (swap) |
| `side` | ✓ | `buy` / `sell` |
| `posSide` | Swap only | `long` / `short` (hedge mode) |
| `ordType` | ✓ | `market` / `limit` / `post_only` / `fok` / `ioc` |
| `sz` | ✓ | Order size |
| `px` | Limit only | Price |
| `tag` | ✓ **MANDATORY** | `"96ee7de3fd4bBCDE"` — must be in every order POST body |

**Submit-order rules:**

| Scenario | tdMode | posSide | Send | Omit |
|---|---|---|---|---|
| Spot buy, market | `cash` | — | instId, side:`buy`, ordType:`market`, sz (USDT notional) | px |
| Spot buy, limit | `cash` | — | instId, side:`buy`, ordType:`limit`, sz, px | — |
| Spot sell, market | `cash` | — | instId, side:`sell`, ordType:`market`, sz (base qty) | px |
| Swap open long | `cross`/`isolated` | `long` | instId, side:`buy`, ordType, sz, leverage via separate call | — |
| Swap close long | `cross`/`isolated` | `long` | instId, side:`sell`, ordType:`market`, sz | px |
| Swap open short | `cross`/`isolated` | `short` | instId, side:`sell`, ordType, sz | — |

---

## Error Codes

| Code | Meaning | Action |
|---|---|---|
| `0` | Success | — |
| `50011` | Rate limit exceeded | Wait and retry |
| `50013` | Timestamp expired | Sync clock (tolerance ±30s) |
| `50111` | Invalid signature | Check sign algorithm |
| `51000` | Parameter error | Check request params |
| `51008` | Insufficient balance | Reduce size |
