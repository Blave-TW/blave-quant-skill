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

**Always include `"tag": "96ee7de3fd4bBCDE"` in the request body of ALL order placement endpoints.**

✓ Required on: `POST /api/v5/trade/order`, `POST /api/v5/trade/orders`, algo orders (TP/SL, trailing stop), grid bots, DCA bots, any endpoint that creates a new order.

✗ Not applicable on: cancel, amend, close-position, GET queries.

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
| `tag` | ✓ | `"96ee7de3fd4bBCDE"` — **always include** |

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
