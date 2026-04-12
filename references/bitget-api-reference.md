# Bitget API Reference

## Base URL

`https://api.bitget.com`

**Success response:** `"code": "00000"` — all other codes are errors.

---

## Authentication

**Credentials** (from `.env`): `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE`

**Signature:** `Base64(HMAC-SHA256(secret, timestamp + METHOD + path + body))`
- `timestamp`: Unix milliseconds
- GET body = `""`
- POST body = compact JSON

**Headers (authenticated requests):**
```
ACCESS-KEY: <api_key>
ACCESS-SIGN: <base64 signature>
ACCESS-PASSPHRASE: <passphrase>
ACCESS-TIMESTAMP: <unix ms>
Content-Type: application/json
locale: en-US
```

---

## Python Signature Implementation

```python
import time, hmac, hashlib, base64, json, os, requests
from dotenv import dotenv_values

_env        = dotenv_values()
API_KEY     = _env["BITGET_API_KEY"]
SECRET_KEY  = _env["BITGET_SECRET_KEY"]
PASSPHRASE  = _env["BITGET_PASSPHRASE"]
BASE_URL    = "https://api.bitget.com"


def _sign(ts, method, path, body_str=""):
    msg = f"{ts}{method}{path}{body_str}"
    mac = hmac.new(SECRET_KEY.encode(), msg.encode(), hashlib.sha256).digest()
    return base64.b64encode(mac).decode()


def _headers(method, path, body_str=""):
    ts = str(int(time.time() * 1000))
    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": _sign(ts, method, path, body_str),
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": ts,
        "Content-Type": "application/json",
        "locale": "en-US",
    }


def bitget_get(path, params=None):
    qs = ""
    if params:
        qs = "?" + "&".join(f"{k}={v}" for k, v in params.items())
    h = _headers("GET", path + qs)
    r = requests.get(f"{BASE_URL}{path}", params=params, headers=h, timeout=10)
    data = r.json()
    if data.get("code") != "00000":
        raise Exception(f"Bitget error {data.get('code')}: {data.get('msg')}")
    return data.get("data")


def bitget_post(path, body=None):
    body_str = json.dumps(body, separators=(",", ":")) if body else ""
    h = _headers("POST", path, body_str)
    r = requests.post(f"{BASE_URL}{path}", data=body_str, headers=h, timeout=10)
    data = r.json()
    if data.get("code") != "00000":
        raise Exception(f"Bitget error {data.get('code')}: {data.get('msg')}")
    return data.get("data")
```

---

## Account Balance

| Method | Path | Description |
|---|---|---|
| GET | `/api/v2/spot/account/assets` | Spot balances |
| GET | `/api/v2/mix/account/accounts` | Futures account info (`productType` required: `USDT-FUTURES`, `USDC-FUTURES`, `COIN-FUTURES`) |
| GET | `/api/v2/account/funding-assets` | Funding account assets |
| GET | `/api/v2/account/all-account-balance` | All accounts overview |

---

## Spot Endpoints

### Market Data (Public)

| Method | Path | Description |
|---|---|---|
| GET | `/api/v2/spot/market/tickers` | Ticker (`symbol` optional — omit for all) |
| GET | `/api/v2/spot/market/orderbook` | Orderbook (`symbol` required, `type`=step0-5) |
| GET | `/api/v2/spot/market/candles` | Kline (`symbol`, `granularity`, `startTime`, `endTime`) |
| GET | `/api/v2/spot/market/trades` | Recent trades |
| GET | `/api/v2/spot/public/symbols` | Symbol info |

### Trading (Private)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v2/spot/trade/place-order` | Place order |
| POST | `/api/v2/spot/trade/batch-orders` | Batch place orders |
| POST | `/api/v2/spot/trade/cancel-order` | Cancel order |
| POST | `/api/v2/spot/trade/batch-cancel-order` | Batch cancel |
| POST | `/api/v2/spot/trade/cancel-symbol-order` | Cancel all for symbol |
| POST | `/api/v2/spot/trade/cancel-replace-order` | Atomic modify order |
| GET | `/api/v2/spot/trade/orderInfo` | Order details |
| GET | `/api/v2/spot/trade/unfilled-orders` | Open orders |
| GET | `/api/v2/spot/trade/history-orders` | Order history |
| GET | `/api/v2/spot/trade/fills` | Execution fills |

**Spot order params:** `symbol`, `side` (buy/sell), `orderType` (limit/market), `price`, `size`, `force` (gtc/ioc/fok/post_only)

### Plan Orders (Private)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v2/spot/trade/place-plan-order` | Create trigger order |
| POST | `/api/v2/spot/trade/modify-plan-order` | Modify trigger order |
| POST | `/api/v2/spot/trade/cancel-plan-order` | Cancel trigger order |
| POST | `/api/v2/spot/trade/batch-cancel-plan-order` | Batch cancel triggers |
| GET | `/api/v2/spot/trade/current-plan-order` | Open plan orders |
| GET | `/api/v2/spot/trade/history-plan-order` | Plan order history |

---

## Futures (Mix) Endpoints

### Market Data (Public)

| Method | Path | Description |
|---|---|---|
| GET | `/api/v2/mix/market/ticker` | Futures ticker (`symbol` or `productType`) |
| GET | `/api/v2/mix/market/depth` | Orderbook (`symbol`, `limit`) |
| GET | `/api/v2/mix/market/candles` | Kline (trade/index/mark price types) |
| GET | `/api/v2/mix/market/trades` | Recent trades |
| GET | `/api/v2/mix/public/contracts` | Contract info |
| GET | `/api/v2/mix/market/funding-rate` | Funding rate (current/historical) |
| GET | `/api/v2/mix/market/open-interest` | Open interest |

### Trading (Private)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v2/mix/order/place-order` | Place order |
| POST | `/api/v2/mix/order/batch-place-order` | Batch place (max 50) |
| POST | `/api/v2/mix/order/modify-order` | Modify order (size, price, TP/SL) |
| POST | `/api/v2/mix/order/cancel-order` | Cancel order |
| POST | `/api/v2/mix/order/batch-cancel-orders` | Batch cancel |
| POST | `/api/v2/mix/order/cancel-all-orders` | Cancel all |
| GET | `/api/v2/mix/order/detail` | Order details |
| GET | `/api/v2/mix/order/orders-pending` | Open orders |
| GET | `/api/v2/mix/order/orders-history` | Order history |
| GET | `/api/v2/mix/order/fills` | Fills |
| GET | `/api/v2/mix/order/fill-history` | Fill history |

**Futures order params:** `symbol`, `productType` (USDT-FUTURES/USDC-FUTURES/COIN-FUTURES), `side` (buy/sell), `tradeSide` (open/close), `orderType` (limit/market), `price`, `size`, `marginCoin`, `leverage`

### Position Management (Private)

| Method | Path | Description |
|---|---|---|
| GET | `/api/v2/mix/position/single-position` | Single position |
| GET | `/api/v2/mix/position/all-position` | All positions |
| GET | `/api/v2/mix/position/history-position` | Position history |

### Configuration (Private)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v2/mix/account/set-leverage` | Set leverage |
| POST | `/api/v2/mix/account/set-margin-mode` | Set margin mode (crossed/isolated) |
| POST | `/api/v2/mix/account/set-position-mode` | Set position mode |
| POST | `/api/v2/mix/account/set-auto-margin` | Auto margin addition |

---

## Transfers

| Method | Path | Description |
|---|---|---|
| POST | `/api/v2/spot/wallet/transfer` | Internal transfer between accounts |
| POST | `/api/v2/spot/wallet/subaccount-transfer` | Transfer to subaccount |

---

## Symbol Format

- Spot: `BTCUSDT`
- Futures: `BTCUSDT` with `productType=USDT-FUTURES`

## Rate Limits

- Public: 10-20 req/s per IP
- Private: 5-10 req/s per UID
- Configuration: 5 req/s per UID
