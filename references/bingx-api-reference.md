# BingX API Reference

## Base URL

| Environment | Primary | Fallback |
|---|---|---|
| Live Trading | `https://open-api.bingx.com` | `https://open-api.bingx.pro` |
| Paper Trading (VST) | `https://open-api-vst.bingx.com` | `https://open-api-vst.bingx.pro` |

Prefer `.com`; only fall back to `.pro` on network-level failures. Default to live unless user explicitly requests paper trading.

---

## Authentication

**Credentials** (from `.env`): `BINGX_API_KEY`, `BINGX_SECRET_KEY`

**Signature:** HMAC-SHA256

```
1. Collect all params (query + body) + timestamp (Unix ms)
2. Sort alphabetically by key (unencoded)
3. Concatenate as key=value&key=value
4. signature = HMAC-SHA256(secret, canonical_string) → hex
5. Append &signature=<hex> to query string or body
```

**Headers (all requests):**
```
X-BX-APIKEY: <api_key>
X-SOURCE-KEY: BX-AI-SKILL
```

**Response format:** `{"code": 0, "msg": "", "data": ...}` — `code == 0` is success.

---

## Python Signature Implementation

```python
import time, hmac, hashlib, json, os, requests
from dotenv import dotenv_values
from urllib.parse import urlencode

_env       = dotenv_values()
API_KEY    = _env["BINGX_API_KEY"]
SECRET_KEY = _env["BINGX_SECRET_KEY"]
BASE_URL   = "https://open-api.bingx.com"
FALLBACK   = "https://open-api.bingx.pro"
HEADERS    = {"X-BX-APIKEY": API_KEY, "X-SOURCE-KEY": "BX-AI-SKILL"}


def _sign(params: dict) -> str:
    """Build canonical string from sorted params and return HMAC-SHA256 hex signature."""
    params["timestamp"] = str(int(time.time() * 1000))
    canonical = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    sig = hmac.new(SECRET_KEY.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    return canonical + f"&signature={sig}"


def bingx_get(path: str, params: dict = {}):
    """Signed GET request with domain fallback."""
    qs = _sign(dict(params))
    for base in [BASE_URL, FALLBACK]:
        try:
            r = requests.get(f"{base}{path}?{qs}", headers=HEADERS, timeout=10)
            data = r.json()
            if data.get("code") != 0:
                raise Exception(f"BingX error {data.get('code')}: {data.get('msg')}")
            return data.get("data")
        except requests.exceptions.ConnectionError:
            if base == FALLBACK: raise
    return None


def bingx_post(path: str, params: dict = {}):
    """Signed POST request (form-encoded) with domain fallback."""
    body = _sign(dict(params))
    for base in [BASE_URL, FALLBACK]:
        try:
            r = requests.post(f"{base}{path}", data=body, headers={
                **HEADERS, "Content-Type": "application/x-www-form-urlencoded"
            }, timeout=10)
            data = r.json()
            if data.get("code") != 0:
                raise Exception(f"BingX error {data.get('code')}: {data.get('msg')}")
            return data.get("data")
        except requests.exceptions.ConnectionError:
            if base == FALLBACK: raise
    return None


def bingx_delete(path: str, params: dict = {}):
    """Signed DELETE request with domain fallback."""
    qs = _sign(dict(params))
    for base in [BASE_URL, FALLBACK]:
        try:
            r = requests.delete(f"{base}{path}?{qs}", headers=HEADERS, timeout=10)
            data = r.json()
            if data.get("code") != 0:
                raise Exception(f"BingX error {data.get('code')}: {data.get('msg')}")
            return data.get("data")
        except requests.exceptions.ConnectionError:
            if base == FALLBACK: raise
    return None
```

---

## Account Balance Endpoints

BingX has three separate accounts: Fund, Spot, Swap. Assets don't auto-transfer — query all three to see full picture.

| Method | Path | Description |
|---|---|---|
| GET | `/openApi/fund/v1/account/balance` | Fund account (deposits land here) |
| GET | `/openApi/spot/v1/account/balance` | Spot account |
| GET | `/openApi/swap/v3/user/balance` | Swap/futures account (USDT + USDC) |
| GET | `/openApi/account/v1/allAccountBalance` | All accounts overview |

---

## Perpetual Futures (Swap) Endpoints

### Order Management

| Method | Path | Description |
|---|---|---|
| POST | `/openApi/swap/v2/trade/order` | Place order |
| POST | `/openApi/swap/v2/trade/order/test` | Test order (validate only) |
| POST | `/openApi/swap/v2/trade/batchOrders` | Batch place (up to 5) |

**Place order params:**

| Param | Required | Description |
|---|---|---|
| `symbol` | ✓ | e.g. `BTC-USDT` |
| `side` | ✓ | `BUY` / `SELL` |
| `positionSide` | ✓ | `LONG` / `SHORT` / `BOTH` (one-way mode) |
| `type` | ✓ | `MARKET`, `LIMIT`, `STOP_MARKET`, `STOP`, `TAKE_PROFIT_MARKET`, `TAKE_PROFIT`, `TRAILING_STOP_MARKET`, `TRAILING_TP_SL` |
| `quantity` | ✓ (except market buy) | Order quantity |
| `price` | for LIMIT | Limit price |
| `stopPrice` | for STOP/TP | Trigger price |
| `timeInForce` | — | `GTC` (default), `IOC`, `FOK`, `PostOnly` |
| `stopLoss` | — | JSON: `{"type":"STOP_MARKET","stopPrice":"...","price":"...","workingType":"..."}` |
| `takeProfit` | — | JSON: same structure as stopLoss |
| `recvWindow` | — | Default 5000ms |

### Cancel Orders

| Method | Path | Description |
|---|---|---|
| DELETE | `/openApi/swap/v2/trade/order` | Cancel single order |
| DELETE | `/openApi/swap/v2/trade/batchOrders` | Batch cancel (up to 10) |
| DELETE | `/openApi/swap/v2/trade/allOpenOrders` | Cancel all open orders |
| POST | `/openApi/swap/v2/trade/cancelAllAfter` | Kill switch (auto-cancel after 10-120s) |

### Query Orders

| Method | Path | Description |
|---|---|---|
| GET | `/openApi/swap/v2/trade/openOrder` | Single open order status |
| GET | `/openApi/swap/v2/trade/order` | Order details |
| GET | `/openApi/swap/v2/trade/openOrders` | All current open orders |
| GET | `/openApi/swap/v2/trade/allOrders` | Order history (max 7-day range) |
| GET | `/openApi/swap/v2/trade/forceOrders` | Liquidation / force close orders |
| GET | `/openApi/swap/v2/trade/allFillOrders` | Trade fill history with fees & PnL |

### Position Management

| Method | Path | Description |
|---|---|---|
| POST | `/openApi/swap/v2/trade/closeAllPositions` | Close all positions |
| POST | `/openApi/swap/v1/trade/closePosition` | Close position by positionId |
| POST | `/openApi/swap/v2/trade/positionMargin` | Adjust isolated margin (add/reduce) |

### Leverage & Mode Settings

| Method | Path | Description |
|---|---|---|
| GET | `/openApi/swap/v2/trade/marginType` | Query margin mode |
| POST | `/openApi/swap/v2/trade/marginType` | Set margin mode (`ISOLATED`/`CROSSED`/`SEPARATE_ISOLATED`) |
| GET | `/openApi/swap/v2/trade/leverage` | Query leverage (current + max) |
| POST | `/openApi/swap/v2/trade/leverage` | Set leverage |
| GET | `/openApi/swap/v1/positionSide/dual` | Query position mode (hedge/one-way) |
| POST | `/openApi/swap/v1/positionSide/dual` | Set position mode |

### Order Modification

| Method | Path | Description |
|---|---|---|
| POST | `/openApi/swap/v1/trade/amend` | Amend open order quantity |
| POST | `/openApi/swap/v1/trade/cancelReplace` | Cancel and replace (atomic) |
| POST | `/openApi/swap/v1/trade/batchCancelReplace` | Batch cancel and replace |

### TWAP Orders

| Method | Path | Description |
|---|---|---|
| POST | `/openApi/swap/v1/twap/order` | Place TWAP order (split into child orders, 5-120s intervals) |
| POST | `/openApi/swap/v1/twap/cancelOrder` | Cancel TWAP order |
| GET | `/openApi/swap/v1/twap/openOrders` | Query TWAP open orders |
| GET | `/openApi/swap/v1/twap/historyOrders` | Query TWAP history |
| GET | `/openApi/swap/v1/twap/orderDetail` | TWAP order details with child records |

### Additional

| Method | Path | Description |
|---|---|---|
| GET | `/openApi/swap/v1/trade/fullOrder` | All orders V2 |
| GET | `/openApi/swap/v2/trade/fillHistory` | Historical transaction details |
| GET | `/openApi/swap/v1/trade/positionHistory` | Position history (max 3-month) |
| GET | `/openApi/swap/v1/positionMargin/history` | Isolated margin change history |
| GET | `/openApi/swap/v1/maintMarginRatio` | Position & maintenance margin ratio |
| POST | `/openApi/swap/v1/trade/autoAddMargin` | Auto margin addition |
| POST | `/openApi/swap/v1/trade/reverse` | One-click reverse position |
| POST | `/openApi/swap/v2/trade/getVst` | Apply VST (paper trading) balance |

---

## Spot Endpoints

### Order Management

| Method | Path | Description |
|---|---|---|
| POST | `/openApi/spot/v1/trade/order` | Place order (MARKET/LIMIT/STOP types) |
| POST | `/openApi/spot/v1/trade/batchOrders` | Batch place (up to 5) |
| POST | `/openApi/spot/v1/trade/cancel` | Cancel single order |
| POST | `/openApi/spot/v1/trade/cancelOrders` | Bulk cancel |
| POST | `/openApi/spot/v1/trade/cancelOpenOrders` | Cancel all open orders for a pair |
| POST | `/openApi/spot/v1/trade/cancelAllAfter` | Kill switch (10-120s timeout) |
| POST | `/openApi/spot/v1/trade/order/cancelReplace` | Cancel and replace (atomic) |

**Spot order types:** `MARKET`, `LIMIT`, `TAKE_STOP_LIMIT`, `TAKE_STOP_MARKET`, `TRIGGER_LIMIT`, `TRIGGER_MARKET`

### Query Orders

| Method | Path | Description |
|---|---|---|
| GET | `/openApi/spot/v1/trade/query` | Single order details |
| GET | `/openApi/spot/v1/trade/openOrders` | Active orders by pair |
| GET | `/openApi/spot/v1/trade/historyOrders` | Order history (max 10K results) |
| GET | `/openApi/spot/v1/trade/myTrades` | Trade fills with commissions |
| GET | `/openApi/spot/v1/user/commissionRate` | Commission rates (maker/taker) |

### OCO Orders

| Method | Path | Description |
|---|---|---|
| POST | `/openApi/spot/v1/oco/order` | Create OCO order |
| POST | `/openApi/spot/v1/oco/cancel` | Cancel OCO order |
| GET | `/openApi/spot/v1/oco/orderList` | Query OCO order details |
| GET | `/openApi/spot/v1/oco/openOrderList` | Open OCO orders |
| GET | `/openApi/spot/v1/oco/historyOrderList` | Historical OCO orders |

---

## Symbol Format

- Perpetual futures: `BTC-USDT` (with hyphen)
- Spot: `BTC-USDT` (with hyphen)

## Notes

- `orderID` (string) is preferred over `orderId` (numeric) for large IDs to avoid precision loss
- Order history queries have a max 7-day range per request
- Position history max 3-month span
- Kill switch countdown: 10-120 seconds, must send heartbeat to reset
