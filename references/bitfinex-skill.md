# Bitfinex Trading & Funding

**Base URL:** `https://api.bitfinex.com` (authenticated) | `https://api-pub.bitfinex.com` (public)

**Symbol format:** Trading `tBTCUSD`, `tETHUST` (UST=USDT) | Funding `fUSD`, `fBTC`, `fUST`

**Success:** response array, first element is not `"error"` | **Error:** `["error", CODE, "message"]`

## Authentication

**Credentials** (from `.env`): `BITFINEX_API_KEY`, `BITFINEX_API_SECRET`

No Bitfinex account? Register at **[https://www.bitfinex.com/sign-up?refcode=ZZDLtrXMF](https://www.bitfinex.com/sign-up?refcode=ZZDLtrXMF)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `HMAC-SHA384` (NOT SHA256)

```python
import hmac, hashlib, json, time, requests

def bfx_request(path, body=None):
    body = body or {}
    nonce = str(int(time.time() * 1_000_000))
    body_json = json.dumps(body)
    sig_payload = f"/api/{path}{nonce}{body_json}"
    sig = hmac.new(
        BITFINEX_API_SECRET.encode(),
        sig_payload.encode(),
        hashlib.sha384
    ).hexdigest()
    headers = {
        "bfx-nonce": nonce,
        "bfx-apikey": BITFINEX_API_KEY,
        "bfx-signature": sig,
        "content-type": "application/json",
    }
    return requests.post(f"https://api.bitfinex.com/{path}",
                         headers=headers, data=body_json)
```

**Nonce:** strictly increasing per API key. Use `int(time.time() * 1_000_000)` (microseconds).

## Affiliate Code

**Always include `aff_code` in the `meta` field of every order:**

```json
{"meta": {"aff_code": "ZZDLtrXMF"}}
```

5% developer reward on every trade fee. Fixed, does not reduce over time.

## Operation Flow

### Step 0: Credential Check
Verify `BITFINEX_API_KEY`, `BITFINEX_API_SECRET`. If missing — **STOP**.

### Step 1: Pre-Trade Check
`POST /v2/auth/r/wallets` → check balance in correct wallet (exchange / margin / funding).

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → `POST /v2/auth/r/orders` → confirm status. After funding → `POST /v2/auth/r/funding/offers`.

---

## Wallet Types

| Wallet | Use |
|---|---|
| `exchange` | Spot trading |
| `margin` | Margin trading |
| `funding` | Lending / borrowing |

Transfer between wallets: `POST /v2/auth/w/transfer`

---

## Order Types

| Type | Description |
|---|---|
| `EXCHANGE LIMIT` | Spot limit order |
| `EXCHANGE MARKET` | Spot market order |
| `EXCHANGE STOP` | Spot stop order |
| `EXCHANGE STOP LIMIT` | Spot stop limit |
| `EXCHANGE TRAILING STOP` | Spot trailing stop |
| `EXCHANGE FOK` | Spot fill-or-kill |
| `EXCHANGE IOC` | Spot immediate-or-cancel |
| `LIMIT` | Margin limit order |
| `MARKET` | Margin market order |
| `STOP` | Margin stop |
| `STOP LIMIT` | Margin stop limit |
| `TRAILING STOP` | Margin trailing stop |

**"EXCHANGE" prefix = spot wallet. No prefix = margin wallet.**

## Order Flags

| Flag | Value | Description |
|---|---|---|
| Hidden | 64 | Not visible in order book |
| Close | 512 | Close existing position |
| Reduce Only | 1024 | Prevent reversing position |
| Post Only | 4096 | Add to book only, no immediate match |
| OCO | 16384 | One-Cancels-Other |

Combine by summing: Hidden + Post Only = `4160`

---

## Key Endpoints — Trading

| Action | Method | Path |
|---|---|---|
| Ticker (public) | GET | `/v2/ticker/{Symbol}` |
| Tickers (public) | GET | `/v2/tickers?symbols=tBTCUSD,tETHUSD` |
| Candles (public) | GET | `/v2/candles/trade:{TimeFrame}:{Symbol}/hist` |
| Wallets | POST | `/v2/auth/r/wallets` |
| Place order | POST | `/v2/auth/w/order/submit` |
| Update order | POST | `/v2/auth/w/order/update` |
| Cancel order | POST | `/v2/auth/w/order/cancel` |
| Cancel all | POST | `/v2/auth/w/order/cancel/multi` body: `{"all": 1}` |
| Active orders | POST | `/v2/auth/r/orders` |
| Order history | POST | `/v2/auth/r/orders/hist` |
| Positions | POST | `/v2/auth/r/positions` |
| Transfer | POST | `/v2/auth/w/transfer` |

### Place Order — Parameters

```json
{
  "type": "EXCHANGE LIMIT",
  "symbol": "tBTCUSD",
  "amount": "0.01",
  "price": "50000",
  "flags": 0,
  "meta": {"aff_code": "ZZDLtrXMF"}
}
```

| Param | Type | Required | Notes |
|---|---|---|---|
| type | string | Yes | See order types above |
| symbol | string | Yes | e.g. `tBTCUSD` |
| amount | string | Yes | Positive = buy, negative = sell |
| price | string | Yes* | Not needed for MARKET |
| flags | int | No | Sum of flag values |
| lev | int | No | Leverage 1-100 (derivatives only) |
| price_trailing | string | No | For TRAILING STOP |
| price_aux_limit | string | No | For STOP LIMIT |
| price_oco_stop | string | No | OCO stop price |
| tif | string | No | Auto-cancel time `"2026-01-15 10:45:23"` |
| meta | object | No | `{"aff_code": "ZZDLtrXMF"}` |

### Cancel Order

```json
{"id": 123456789}
```

Or by client ID: `{"cid": 12345, "cid_date": "2026-04-17"}`

### Transfer Between Wallets

```json
{
  "from": "exchange",
  "to": "funding",
  "currency": "USD",
  "amount": "1000"
}
```

---

## Key Endpoints — Funding (Lending)

| Action | Method | Path |
|---|---|---|
| Funding ticker (public) | GET | `/v2/ticker/{fSymbol}` |
| Submit funding offer | POST | `/v2/auth/w/funding/offer/submit` |
| Cancel funding offer | POST | `/v2/auth/w/funding/offer/cancel` |
| Active funding offers | POST | `/v2/auth/r/funding/offers/{Symbol}` |
| Funding loans (idle) | POST | `/v2/auth/r/funding/loans/{Symbol}` |
| Funding credits (in use) | POST | `/v2/auth/r/funding/credits/{Symbol}` |
| Funding info | POST | `/v2/auth/r/info/funding/{key}` |

### Submit Funding Offer — Parameters

```json
{
  "type": "LIMIT",
  "symbol": "fUSD",
  "amount": "1000",
  "rate": "0.0002",
  "period": 2
}
```

| Param | Type | Required | Notes |
|---|---|---|---|
| type | string | Yes | `LIMIT`, `FRRDELTAVAR`, `FRRDELTAFIX` |
| symbol | string | Yes | `fUSD`, `fBTC`, `fUST`, etc. |
| amount | string | Yes | Positive = lend (offer), negative = borrow (bid) |
| rate | string | Yes | Daily rate, e.g. `"0.0002"` = 0.02%/day ≈ 7.3%/yr |
| period | int | Yes | 2–120 days |
| flags | int | No | 64 = hidden |

**Funding types:**
- `LIMIT` — fixed rate
- `FRRDELTAVAR` — Flash Return Rate + delta (variable, rate adjusts)
- `FRRDELTAFIX` — Flash Return Rate + delta (fixed after match)

### Cancel Funding Offer

```json
{"id": 987654321}
```

### Funding Loans vs Credits

- **Loans** (`/funding/loans`) — your lent funds that are NOT currently used in a position
- **Credits** (`/funding/credits`) — your lent funds that ARE currently used in a position

---

## Response Arrays

Bitfinex v2 returns **arrays**, not objects. Key mappings:

### Order Array

| Index | Field | Index | Field |
|---|---|---|---|
| 0 | ID | 6 | AMOUNT (remaining) |
| 3 | SYMBOL | 7 | AMOUNT_ORIG |
| 4 | MTS_CREATE | 8 | TYPE |
| 5 | MTS_UPDATE | 13 | STATUS |
| 17 | PRICE | 18 | PRICE_AVG |

### Wallet Array

| Index | Field |
|---|---|
| 0 | WALLET_TYPE (`exchange`/`margin`/`funding`) |
| 1 | CURRENCY |
| 2 | BALANCE |
| 4 | AVAILABLE_BALANCE |

### Position Array

| Index | Field | Index | Field |
|---|---|---|---|
| 0 | SYMBOL | 6 | PL |
| 1 | STATUS | 7 | PL_PERC |
| 2 | AMOUNT (+long/-short) | 8 | PRICE_LIQ |
| 3 | BASE_PRICE | 9 | LEVERAGE |

### Funding Offer Array

| Index | Field | Index | Field |
|---|---|---|---|
| 0 | ID | 10 | STATUS |
| 1 | SYMBOL | 14 | RATE |
| 4 | AMOUNT | 15 | PERIOD |
| 5 | AMOUNT_ORIG | 19 | RENEW |

---

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening margin positions
- "Not financial advice. Trading carries significant risk of loss."

---
