# KuCoin API Reference

## Base URLs

| | Spot | Futures (Perpetual) |
|---|---|---|
| Production | `https://api.kucoin.com` | `https://api-futures.kucoin.com` |
| Sandbox | `https://openapi-sandbox.kucoin.com` | `https://api-sandbox-futures.kucoin.com` |

**Success:** `"code": "200000"` in every response.

---

## Authentication

**Credentials** (from `.env`): `KUCOIN_API_KEY`, `KUCOIN_API_SECRET`, `KUCOIN_API_PASSPHRASE`

**Signature:** `Base64(HMAC-SHA256(api_secret, timestamp + METHOD + path + body))`
- `timestamp`: Unix milliseconds as string
- `METHOD`: uppercase (`GET`, `POST`, `DELETE`)
- `path`: full path including query string for GET (e.g., `/api/v1/orders?status=active`)
- `body`: JSON string for POST/DELETE with body; empty string `""` for GET

**Passphrase (v2/v3 keys):** `Base64(HMAC-SHA256(api_secret, api_passphrase))` — **not** plain text

**Headers (all authenticated requests):**
```
KC-API-KEY: $KUCOIN_API_KEY
KC-API-SIGN: <signature>
KC-API-TIMESTAMP: <unix ms>
KC-API-PASSPHRASE: <signed passphrase>
KC-API-KEY-VERSION: 3
Content-Type: application/json   (POST only)
```

---

## Broker Attribution (Blave — MANDATORY on all requests)

KuCoin broker attribution requires **4 additional headers** on every REST request (public + private, spot + futures). Omitting them disqualifies rebate eligibility.

| Header | Spot value | Futures value |
|---|---|---|
| `KC-BROKER-NAME` | `blave` | `blaveFutures` |
| `KC-API-PARTNER` | `blave` | `blaveFutures` |
| `KC-API-PARTNER-SIGN` | computed (see below) | computed (see below) |
| `KC-API-PARTNER-VERIFY` | `true` | `true` |

**Partner sign formula:** `Base64(HMAC-SHA256(BROKER_KEY, timestamp + partner + userApiKey))`
- Spot broker key: `1c10e0c0-bc3e-4a18-ad53-e41e6df5f757` | Futures broker key: `520815df-b324-4494-9bc8-b1015732b902` (hardcoded Blave BPP constants)
- `timestamp`: same unix-ms string used in `KC-API-TIMESTAMP`
- `partner`: the partner/broker tag (`blave` or `blaveFutures`)
- `userApiKey`: the user's `KUCOIN_API_KEY`

---

## Python Implementation

```python
import base64, hashlib, hmac, json, time
import requests
from dotenv import dotenv_values

env = dotenv_values(".env")
API_KEY        = env["KUCOIN_API_KEY"]
API_SECRET     = env["KUCOIN_API_SECRET"]
API_PASSPHRASE = env["KUCOIN_API_PASSPHRASE"]

SPOT_BROKER_KEY    = "1c10e0c0-bc3e-4a18-ad53-e41e6df5f757"
FUTURES_BROKER_KEY = "520815df-b324-4494-9bc8-b1015732b902"

SPOT_URL    = "https://api.kucoin.com"
FUTURES_URL = "https://api-futures.kucoin.com"


def _b64_hmac(secret: str, msg: str) -> str:
    return base64.b64encode(
        hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()
    ).decode()


def _headers(method: str, path: str, body: str = "", market: str = "spot") -> dict:
    ts = str(int(time.time() * 1000))
    partner = "blave" if market == "spot" else "blaveFutures"
    return {
        "KC-API-KEY":            API_KEY,
        "KC-API-SIGN":           _b64_hmac(API_SECRET, ts + method.upper() + path + body),
        "KC-API-TIMESTAMP":      ts,
        "KC-API-PASSPHRASE":     _b64_hmac(API_SECRET, API_PASSPHRASE),
        "KC-API-KEY-VERSION":    "3",
        "KC-BROKER-NAME":        partner,
        "KC-API-PARTNER":        partner,
        "KC-API-PARTNER-SIGN":   _b64_hmac(SPOT_BROKER_KEY if market == "spot" else FUTURES_BROKER_KEY, ts + partner + API_KEY),
        "KC-API-PARTNER-VERIFY": "true",
        "Content-Type":          "application/json",
    }


def spot_get(path: str, params: dict = None) -> dict:
    qs = ("?" + "&".join(f"{k}={v}" for k, v in params.items())) if params else ""
    full_path = path + qs
    r = requests.get(SPOT_URL + full_path, headers=_headers("GET", full_path))
    return r.json()


def spot_post(path: str, payload: dict) -> dict:
    body = json.dumps(payload)
    r = requests.post(SPOT_URL + path, headers=_headers("POST", path, body), data=body)
    return r.json()


def spot_delete(path: str, params: dict = None) -> dict:
    qs = ("?" + "&".join(f"{k}={v}" for k, v in params.items())) if params else ""
    full_path = path + qs
    r = requests.delete(SPOT_URL + full_path, headers=_headers("DELETE", full_path))
    return r.json()


def fut_get(path: str, params: dict = None) -> dict:
    qs = ("?" + "&".join(f"{k}={v}" for k, v in params.items())) if params else ""
    full_path = path + qs
    r = requests.get(FUTURES_URL + full_path, headers=_headers("GET", full_path, market="futures"))
    return r.json()


def fut_post(path: str, payload: dict) -> dict:
    body = json.dumps(payload)
    r = requests.post(FUTURES_URL + path, headers=_headers("POST", path, body, market="futures"), data=body)
    return r.json()


def fut_delete(path: str, params: dict = None) -> dict:
    qs = ("?" + "&".join(f"{k}={v}" for k, v in params.items())) if params else ""
    full_path = path + qs
    r = requests.delete(FUTURES_URL + full_path, headers=_headers("DELETE", full_path, market="futures"))
    return r.json()


# ── Examples ────────────────────────────────────────────────────────────────

# Spot: place limit buy
spot_post("/api/v1/orders", {
    "clientOid": "blave-" + str(int(time.time() * 1000)),
    "side":      "buy",
    "symbol":    "BTC-USDT",
    "type":      "limit",
    "price":     "60000",
    "size":      "0.001",
    "timeInForce": "GTC",
})

# Futures: place market long
fut_post("/api/v1/orders", {
    "clientOid": "blave-" + str(int(time.time() * 1000)),
    "side":      "buy",
    "symbol":    "XBTUSDTM",
    "type":      "market",
    "size":      1,           # number of contracts
    "leverage":  "10",
})
```

---

## Symbol Format

**Spot:** `BTC-USDT`, `ETH-USDT`, `SOL-USDT` (hyphen-separated, uppercase)

**Futures Perpetual (USDT-M):** `XBTUSDTM`, `ETHUSDTM`, `SOLUSDTM`
- BTC uses `XBT` prefix, not `BTC`
- Append `USDTM` for linear/USDT-margined perpetuals
- Append `USDM` for inverse/coin-margined perpetuals (e.g., `XBTUSDM`)
- Contract size: typically 1 contract = 0.001 BTC for XBTUSDTM; check `/api/v1/contracts/{symbol}` for lotSize

---

## Spot Endpoints

### Account

| Action | Method | Path | Key params |
|---|---|---|---|
| List accounts | GET | `/api/v1/accounts` | `type` (main/trade/margin) |
| Account detail | GET | `/api/v1/accounts/{accountId}` | — |
| Account ledger | GET | `/api/v1/accounts/ledgers` | `currency`, `direction`, `startAt`, `endAt` |
| Transferable balance | GET | `/api/v1/accounts/transferable` | `currency`✓, `type`✓ |

### Market Data (public — broker headers still required)

| Action | Method | Path | Key params |
|---|---|---|---|
| All symbols | GET | `/api/v2/symbols` | — |
| Symbol detail | GET | `/api/v2/symbols/{symbol}` | — |
| Best bid/ask | GET | `/api/v1/market/orderbook/level1` | `symbol`✓ |
| 24h stats | GET | `/api/v1/market/stats` | `symbol`✓ |
| All tickers | GET | `/api/v1/market/allTickers` | — |
| Klines | GET | `/api/v1/market/candles` | `symbol`✓, `type`✓ (1min/5min/15min/30min/1hour/4hour/8hour/1day/1week), `startAt`, `endAt` |
| Order book (20 levels) | GET | `/api/v1/market/orderbook/level2_20` | `symbol`✓ |

### Orders

| Action | Method | Path | Key params |
|---|---|---|---|
| Place order | POST | `/api/v1/orders` | `clientOid`✓, `side`✓ (buy/sell), `symbol`✓, `type` (limit/market), `price` (limit), `size` (limit/market base), `funds` (market quote), `timeInForce` (GTC/IOC/FOK) |
| Place stop order | POST | `/api/v1/stop-order` | same as above + `stopPrice`✓, `stop` (loss/entry) |
| Cancel order | DELETE | `/api/v1/orders/{orderId}` | — |
| Cancel by clientOid | DELETE | `/api/v1/order/client-order/{clientOid}` | `symbol`✓ |
| Cancel all | DELETE | `/api/v1/orders` | `symbol`, `tradeType` |
| Order detail | GET | `/api/v1/orders/{orderId}` | — |
| By clientOid | GET | `/api/v1/order/client-order/{clientOid}` | — |
| Active orders | GET | `/api/v1/orders` | `status=active`, `symbol`, `side`, `type` |
| Done orders | GET | `/api/v1/orders` | `status=done`, `symbol`, `startAt`, `endAt` |
| Recent fills | GET | `/api/v1/fills` | `symbol`, `side`, `orderId` |

**`clientOid`:** max 128 chars, unique per order. Convention: `blave-{timestamp}`.

---

## Futures Endpoints

### Account

| Action | Method | Path | Key params |
|---|---|---|---|
| Account overview | GET | `/api/v1/account-overview` | `currency` (USDT/XBT) |
| Account history | GET | `/api/v1/transaction-history` | `type`, `startAt`, `endAt`, `maxCount` |

### Market Data (public)

| Action | Method | Path | Key params |
|---|---|---|---|
| All active contracts | GET | `/api/v1/contracts/active` | — |
| Contract detail | GET | `/api/v1/contracts/{symbol}` | — |
| Ticker | GET | `/api/v1/ticker` | `symbol`✓ |
| Level2 orderbook | GET | `/api/v1/level2/snapshot` | `symbol`✓ |
| Klines | GET | `/api/v1/kline/query` | `symbol`✓, `granularity`✓ (1/5/15/30/60/120/240/480/720/1440/10080 minutes), `from`, `to` |
| Funding rate | GET | `/api/v1/funding-rate/{symbol}/current` | — |
| Mark price | GET | `/api/v1/mark-price/{symbol}/current` | — |
| Premium index | GET | `/api/v1/premium/query` | `symbol`✓, `startAt`, `endAt`, `reverse`, `maxCount` |

### Positions

| Action | Method | Path | Key params |
|---|---|---|---|
| All positions | GET | `/api/v1/positions` | `currency` |
| Position detail | GET | `/api/v1/position` | `symbol`✓ |
| Enable auto-deposit | POST | `/api/v1/position/margin/auto-deposit-status` | `symbol`✓, `status`✓ (bool) |
| Add margin | POST | `/api/v1/position/margin/deposit-margin` | `symbol`✓, `margin`✓, `bizNo`✓ |

### Orders

| Action | Method | Path | Key params |
|---|---|---|---|
| Place order | POST | `/api/v1/orders` | `clientOid`✓, `side`✓ (buy/sell), `symbol`✓, `type` (limit/market), `size`✓ (contracts), `price` (limit), `leverage`✓, `timeInForce` (GTC/IOC/FOK/GTT), `postOnly`, `hidden`, `iceberg`, `closeOrder` (bool for close) |
| Place stop order | POST | `/api/v1/stopOrders` | same + `stopPrice`✓, `stop` (up/down) |
| Cancel order | DELETE | `/api/v1/orders/{orderId}` | — |
| Cancel by clientOid | DELETE | `/api/v1/orders/client-order/{clientOid}` | — |
| Cancel all | DELETE | `/api/v1/orders` | `symbol` |
| Order detail | GET | `/api/v1/orders/{orderId}` | — |
| Active orders | GET | `/api/v1/orders` | `status=active`, `symbol`, `side`, `type` |
| Done orders | GET | `/api/v1/orders` | `status=done`, `symbol`, `startAt`, `endAt` |
| Recent fills | GET | `/api/v1/fills` | `symbol`, `side`, `orderId` |

**Opening long:** `side=buy` | **Closing long / opening short:** `side=sell` with `closeOrder=true` to close, or `side=sell` for new short.

---

## Rate Limits

| Endpoint group | Rate limit |
|---|---|
| Public endpoints | 30 req/3s per IP |
| Private endpoints | 30–40 req/3s per key |
| Order placement | 45 req/3s per key |

HTTP `429` = rate limited. `X-RateLimit-Remaining` header shows remaining quota.
