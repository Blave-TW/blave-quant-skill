# Gate.io API Reference (APIv4)

**Base URL:** `https://api.gateio.ws/api/v4`

> **IMPORTANT:** Always include `X-Gate-Channel-Id: blave` on **every** request (public and authenticated). This is required for broker fee tracking.

Error responses return `{"label": "<ERROR_LABEL>", "message": "..."}` with a 4xx/5xx status. Successful order creation returns HTTP 201.

## Authentication

APIv4 signed requests use three headers:

| Header | Value |
|---|---|
| `KEY` | API key |
| `Timestamp` | Unix time in **seconds** (string) |
| `SIGN` | Hex HMAC-SHA512 signature |

**Signature string** (five lines joined with `\n`):

```
METHOD
/api/v4/<path>
<query_string>
<SHA512 hex of request body ("" for GET)>
<timestamp>
```

## Python Implementation

```python
import hashlib
import hmac
import json
import os
import time

import requests

HOST = "https://api.gateio.ws"
PREFIX = "/api/v4"
COMMON_HEADERS = {
    "Content-Type": "application/json",
    "X-Gate-Channel-Id": "blave",  # broker attribution — MANDATORY
}


def gen_sign(method, path, query_string="", body=""):
    key = os.environ["GATE_API_KEY"]
    secret = os.environ["GATE_SECRET_KEY"]
    t = str(time.time())
    hashed_payload = hashlib.sha512((body or "").encode("utf-8")).hexdigest()
    s = "\n".join([method, PREFIX + path, query_string, hashed_payload, t])
    sign = hmac.new(secret.encode("utf-8"), s.encode("utf-8"), hashlib.sha512).hexdigest()
    return {"KEY": key, "Timestamp": t, "SIGN": sign}


def request(method, path, query_string="", body=None):
    body_str = json.dumps(body) if body is not None else ""
    headers = dict(COMMON_HEADERS)
    headers.update(gen_sign(method, path, query_string, body_str))
    url = HOST + PREFIX + path + ("?" + query_string if query_string else "")
    resp = requests.request(method, url, headers=headers, data=body_str or None)
    if not resp.ok:
        raise RuntimeError(f"{resp.status_code} {resp.text}")
    return resp.json()
```

**Common mistakes:**
- Signing `/spot/orders` instead of `/api/v4/spot/orders` — the `/api/v4` prefix is part of the signed path
- Using milliseconds for `Timestamp` — Gate.io uses **seconds**
- Hashing a re-serialized body that differs from the bytes actually sent — sign the exact string you send
- Query string must match exactly what is sent (unencoded form, e.g. `currency_pair=BTC_USDT&limit=10`)

## Spot

| Operation | Method | Path | Auth |
|---|---|---|---|
| Ticker | GET | `/spot/tickers?currency_pair=BTC_USDT` | public |
| Order book | GET | `/spot/order_book?currency_pair=BTC_USDT` | public |
| Candlesticks | GET | `/spot/candlesticks?currency_pair=BTC_USDT&interval=1h` | public |
| Balances | GET | `/spot/accounts` | signed |
| Create order | POST | `/spot/orders` | signed |
| Batch orders | POST | `/spot/batch_orders` | signed |
| List orders | GET | `/spot/orders?currency_pair=...&status=open` | signed |
| Open orders (all pairs) | GET | `/spot/open_orders` | signed |
| Get order | GET | `/spot/orders/{order_id}?currency_pair=...` | signed |
| Cancel order | DELETE | `/spot/orders/{order_id}?currency_pair=...` | signed |
| Cancel all in pair | DELETE | `/spot/orders?currency_pair=...` | signed |
| Amend order | PATCH | `/spot/orders/{order_id}` | signed |

**Create spot order** — `POST /spot/orders`

```python
order = {
    "currency_pair": "BTC_USDT",
    "side": "buy",              # buy | sell
    "type": "limit",            # limit | market
    "amount": "0.001",          # limit: base currency; market buy: QUOTE currency, market sell: base
    "price": "60000",           # required for limit
    "time_in_force": "gtc",     # gtc | ioc | poc | fok (market: only ioc/fok)
    "account": "spot",          # spot | margin | unified
    # "text": "t-mystrategy1",  # optional custom id: t- prefix, ≤28 bytes after prefix, [0-9A-Za-z_.-]
}
request("POST", "/spot/orders", body=order)
```

**Market order `amount` semantics:** `side=buy` → amount is in **quote** currency (USDT); `side=sell` → amount is in **base** currency (BTC).

## USDT-Settled Perpetual Futures

All paths use `settle=usdt`.

| Operation | Method | Path | Auth |
|---|---|---|---|
| Ticker | GET | `/futures/usdt/tickers?contract=BTC_USDT` | public |
| Order book | GET | `/futures/usdt/order_book?contract=BTC_USDT` | public |
| Candlesticks | GET | `/futures/usdt/candlesticks?contract=BTC_USDT&interval=1h` | public |
| Contract detail | GET | `/futures/usdt/contracts/{contract}` | public |
| Account | GET | `/futures/usdt/accounts` | signed |
| Positions | GET | `/futures/usdt/positions` | signed |
| Single position | GET | `/futures/usdt/positions/{contract}` | signed |
| Set leverage | POST | `/futures/usdt/positions/{contract}/leverage?leverage=10` | signed |
| Create order | POST | `/futures/usdt/orders` | signed |
| Batch orders | POST | `/futures/usdt/batch_orders` | signed |
| List orders | GET | `/futures/usdt/orders?contract=...&status=open` | signed |
| Get order | GET | `/futures/usdt/orders/{order_id}` | signed |
| Cancel order | DELETE | `/futures/usdt/orders/{order_id}` | signed |
| Cancel all open | DELETE | `/futures/usdt/orders?contract=...` | signed |

**Create futures order** — `POST /futures/usdt/orders`

```python
# Limit long 1 contract
order = {
    "contract": "BTC_USDT",
    "size": 1,                  # int; positive = long/buy, negative = short/sell
    "price": "60000",
    "tif": "gtc",               # gtc | ioc | poc | fok
    # "reduce_only": True,      # reduce position only
    # "text": "t-mystrategy1",  # optional custom id: t- prefix, ≤28 bytes after prefix, [0-9A-Za-z_.-]
}
request("POST", "/futures/usdt/orders", body=order)

# Market order: price "0" + tif "ioc"
market_order = {"contract": "BTC_USDT", "size": -1, "price": "0", "tif": "ioc"}

# Close entire position: size 0 + close true
close_order = {"contract": "BTC_USDT", "size": 0, "close": True, "price": "0", "tif": "ioc"}
```

**`size` is in contracts, not coins.** 1 contract = `quanto_multiplier` of base coin (from `GET /futures/usdt/contracts/{contract}`). Example: BTC_USDT `quanto_multiplier=0.0001` → 1 contract = 0.0001 BTC. Coins → contracts: `size = round(coin_amount / quanto_multiplier)`.

**Dual-position (hedge) mode:** close one side with `size: 0` + `auto_size: "close_long"` / `"close_short"`.

## Asset Transfer (between accounts)

`POST /wallet/transfers` — same HMAC-SHA512 five-line signature as any private endpoint;
JSON body. Live-verified 2026-08 (spot↔futures round trip, `tx_id` returned, balances
reflected within seconds).

| Field | Required | Notes |
|---|---|---|
| `currency` | yes | e.g. `USDT` |
| `from` / `to` | yes | `spot` \| `futures` \| `delivery` \| `margin` \| `options` — futures↔margin has no direct route, hop via `spot` |
| `amount` | yes | STRING, not a number |
| `settle` | when futures/delivery | lowercase settle currency, e.g. `usdt` |
| `currency_pair` | when margin | isolated-margin pair, e.g. `BTC_USDT` |

Example spot→futures: `{"currency":"USDT","from":"spot","to":"futures","amount":"3","settle":"usdt"}`.
Success = HTTP 2xx (response carries `tx_id`; older API versions returned an empty
body, so judge by status code first). Status lookup: `GET /wallet/order_status?tx_id=...`.

## Sources

Verified 2026-07-14 against the official Gate.io Python SDK (`gateio/gateapi-python`: `api_client.py` `gen_sign`, `docs/Order.md`, `docs/FuturesOrder.md`, `docs/SpotApi.md`, `docs/FuturesApi.md`) and cross-checked with CCXT `gate.ts` (`X-Gate-Channel-Id` header) and Gate.io official WebSocket SDK `gateio/gatews` (same header).
