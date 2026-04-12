# Binance API Reference

## Base URLs

| | Spot | USDS-M Futures |
|---|---|---|
| Production | `https://api.binance.com` | `https://fapi.binance.com` |
| Testnet | `https://testnet.binance.vision` | `https://demo-fapi.binance.com` |

**Success:** Spot returns order fields directly; Futures returns `"code": 200` or fields directly.

---

## Authentication

**Credentials** (from `.env`): `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`

**Signature:** `HMAC-SHA256(secret, totalParams)` → hex
- `totalParams` = queryString + requestBody (concatenated, no separator)
- `timestamp`: Unix milliseconds (always required for signed endpoints)
- `signature` must be the **last** parameter

**Headers:**
```
X-MBX-APIKEY: <api_key>
Content-Type: application/x-www-form-urlencoded   (POST)
```

---

## Python Signature Implementation

```python
import time, hmac, hashlib, requests
from dotenv import dotenv_values
from urllib.parse import urlencode

_env       = dotenv_values()
API_KEY    = _env["BINANCE_API_KEY"]
SECRET_KEY = _env["BINANCE_SECRET_KEY"]
SPOT_URL   = "https://api.binance.com"
FAPI_URL   = "https://fapi.binance.com"


def _sign(params: dict) -> dict:
    params["timestamp"] = int(time.time() * 1000)
    qs = urlencode(params)
    params["signature"] = hmac.new(SECRET_KEY.encode(), qs.encode(), hashlib.sha256).hexdigest()
    return params


def bn_get(base, path, params=None):
    p = _sign(dict(params or {}))
    r = requests.get(f"{base}{path}", params=p,
                     headers={"X-MBX-APIKEY": API_KEY}, timeout=10)
    return r.json()


def bn_post(base, path, params=None):
    p = _sign(dict(params or {}))
    r = requests.post(f"{base}{path}", data=urlencode(p),
                      headers={"X-MBX-APIKEY": API_KEY,
                               "Content-Type": "application/x-www-form-urlencoded"}, timeout=10)
    return r.json()


def bn_delete(base, path, params=None):
    p = _sign(dict(params or {}))
    r = requests.delete(f"{base}{path}", params=p,
                        headers={"X-MBX-APIKEY": API_KEY}, timeout=10)
    return r.json()


def bn_put(base, path, params=None):
    p = _sign(dict(params or {}))
    r = requests.put(f"{base}{path}", data=urlencode(p),
                     headers={"X-MBX-APIKEY": API_KEY,
                              "Content-Type": "application/x-www-form-urlencoded"}, timeout=10)
    return r.json()


# Shortcuts
def spot_get(path, params=None):    return bn_get(SPOT_URL, path, params)
def spot_post(path, params=None):   return bn_post(SPOT_URL, path, params)
def spot_delete(path, params=None): return bn_delete(SPOT_URL, path, params)
def fapi_get(path, params=None):    return bn_get(FAPI_URL, path, params)
def fapi_post(path, params=None):   return bn_post(FAPI_URL, path, params)
def fapi_delete(path, params=None): return bn_delete(FAPI_URL, path, params)
def fapi_put(path, params=None):    return bn_put(FAPI_URL, path, params)
```

---

## Spot Endpoints

### Account

| Method | Path | Description |
|---|---|---|
| GET | `/api/v3/account` | Account info + balances (`omitZeroBalances` optional) |
| GET | `/api/v3/myTrades` | Trade history (`symbol` required) |
| GET | `/api/v3/account/commission` | Commission rates (`symbol` required) |
| GET | `/api/v3/rateLimit/order` | Unfilled order count |

### Order Placement

| Method | Path | Description |
|---|---|---|
| POST | `/api/v3/order` | Place order |
| POST | `/api/v3/order/test` | Test order (validate only) |
| DELETE | `/api/v3/order` | Cancel order |
| DELETE | `/api/v3/openOrders` | Cancel all open orders for symbol |
| POST | `/api/v3/order/cancelReplace` | Atomic cancel & replace |
| PUT | `/api/v3/order/amend/keepPriority` | Amend quantity (keep queue priority) |

**Spot order params:** `symbol`, `side` (BUY/SELL), `type` (LIMIT/MARKET/STOP_LOSS/TAKE_PROFIT/STOP_LOSS_LIMIT/TAKE_PROFIT_LIMIT/LIMIT_MAKER), `timeInForce` (GTC/IOC/FOK), `quantity`, `quoteOrderQty` (market buy by quote), `price`

### Order Query

| Method | Path | Description |
|---|---|---|
| GET | `/api/v3/order` | Query single order |
| GET | `/api/v3/openOrders` | Current open orders |
| GET | `/api/v3/allOrders` | All orders (active/canceled/filled) |

### Advanced Order Types

| Method | Path | Description |
|---|---|---|
| POST | `/api/v3/orderList/oco` | OCO (One-Cancels-Other) |
| POST | `/api/v3/orderList/oto` | OTO (One-Triggers-Other) |
| POST | `/api/v3/orderList/otoco` | OTOCO (One-Triggers-OCO) |
| DELETE | `/api/v3/orderList` | Cancel order list |
| GET | `/api/v3/orderList` | Query order list |
| GET | `/api/v3/openOrderList` | Open order lists |

### Smart Order Routing (SOR)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v3/sor/order` | SOR order |
| POST | `/api/v3/sor/order/test` | Test SOR order |

---

## USDS-Margined Futures Endpoints

### Account & Position

| Method | Path | Description |
|---|---|---|
| GET | `/fapi/v2/account` | Account info V2 |
| GET | `/fapi/v3/account` | Account info V3 (single/multi-asset) |
| GET | `/fapi/v2/balance` | Account balance |
| GET | `/fapi/v2/positionRisk` | Position info V2 |
| GET | `/fapi/v3/positionRisk` | Position info V3 |
| GET | `/fapi/v1/userTrades` | Trade list (`symbol` required, max 7d range) |
| GET | `/fapi/v1/forceOrders` | Liquidation/ADL orders |

### Order Placement

| Method | Path | Description |
|---|---|---|
| POST | `/fapi/v1/order` | Place order |
| POST | `/fapi/v1/batchOrders` | Batch place (max 5) |
| POST | `/fapi/v1/algoOrder` | Algo/conditional order (STOP/TP/TRAILING) |

**Futures order params:** `symbol`, `side` (BUY/SELL), `positionSide` (BOTH/LONG/SHORT), `type` (LIMIT/MARKET/STOP/STOP_MARKET/TAKE_PROFIT/TAKE_PROFIT_MARKET/TRAILING_STOP_MARKET), `quantity`, `price`, `stopPrice`, `timeInForce`, `reduceOnly`

### Order Modification

| Method | Path | Description |
|---|---|---|
| PUT | `/fapi/v1/order` | Modify order (LIMIT only) |
| PUT | `/fapi/v1/batchOrders` | Batch modify (max 5) |

### Order Cancellation

| Method | Path | Description |
|---|---|---|
| DELETE | `/fapi/v1/order` | Cancel order |
| DELETE | `/fapi/v1/batchOrders` | Batch cancel (max 10) |
| DELETE | `/fapi/v1/allOpenOrders` | Cancel all open orders |
| DELETE | `/fapi/v1/algoOrder` | Cancel algo order |
| DELETE | `/fapi/v1/algoOpenOrders` | Cancel all algo open orders |

### Order Query

| Method | Path | Description |
|---|---|---|
| GET | `/fapi/v1/order` | Query single order |
| GET | `/fapi/v1/openOrder` | Single open order |
| GET | `/fapi/v1/openOrders` | All open orders |
| GET | `/fapi/v1/allOrders` | All orders (max 7d range) |
| GET | `/fapi/v1/openAlgoOrders` | Open algo orders |
| GET | `/fapi/v1/allAlgoOrders` | All algo orders |

### Leverage & Margin

| Method | Path | Description |
|---|---|---|
| POST | `/fapi/v1/leverage` | Set leverage (1-125x) |
| POST | `/fapi/v1/marginType` | Set margin type (ISOLATED/CROSSED) |
| POST | `/fapi/v1/positionSide/dual` | Set position mode (hedge/one-way) |
| POST | `/fapi/v1/positionMargin` | Adjust isolated margin (type: 1=add, 2=reduce) |
| GET | `/fapi/v1/positionMargin/history` | Margin change history |
| GET | `/fapi/v1/leverageBracket` | Leverage brackets |

---

## Symbol Format

- Spot: `BTCUSDT` (no separator)
- Futures: `BTCUSDT` (no separator)

## Rate Limits

- Orders: tracked per 10s and per 1min per UID
- Public market data: IP-based
- Repeated violations → auto IP ban (2min to 3 days)
