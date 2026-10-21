# StockCoin Trading

**Base URL:** `https://api.stockcoin.ai` | **Private prefix:** `/openapi/v1` | **Symbols:** `{BASE}-PERP-USDT` (e.g. `NVDA-PERP-USDT`) | **Errors:** HTTP 400 + `{"code": <negative>, "msg": ...}`

StockCoin is a USDT-perpetual venue for US / KR stocks, ETFs, commodities, pre-IPO names and a few coins
(BlueHelix / BHEX broker OpenAPI white label). **Perpetuals only — there is no spot API.**

Everything below was measured on a live key unless marked otherwise; the venue's own doc is incomplete
(post-only, several error codes and the contract multiplier are not in it).

## Broker Attribution

**None.** StockCoin has no broker / referral id, so no attribution header or field is sent.

## Authentication

**Credentials** (from `.env`): `STOCKCOIN_API_KEY`, `STOCKCOIN_SECRET_KEY`

Verify credentials before any private call. If missing — **STOP**.

**The key must be a FUTURES-type (contract) key.** Any other key type answers `-1005` on every call —
tell the user to recreate it as a contract key. Recommend trade-only, withdrawal off.

**Signature:** `HMAC-SHA256(secret, sorted_query_string + sorted_form_body)` → hex
- `timestamp` (ms) always goes in the **query string**, also on POST
- Both sides are `key=value&…` sorted alphabetically by key; they are concatenated with **no separator**
- POST parameters go in a **form-urlencoded body** (`Content-Type: application/x-www-form-urlencoded`), not JSON
- Append `&signature=<hex>` to the query string
- Sign the exact bytes you send — serialize once, never let the HTTP client re-encode

**Header:** `X-BH-APIKEY: <api_key>`

Clock skew answers `-1021`: read `GET /openapi/v1/time` (`serverTime`, public), offset your clock, retry once.

```python
import hashlib, hmac, time, requests
from urllib.parse import urlencode

HOST, PREFIX = "https://api.stockcoin.ai", "/openapi/v1"

def stockcoin(method, path, key, secret, params=None):
    params = dict(params or {})
    if method == "POST":
        query, body = {"timestamp": int(time.time() * 1000)}, params
    else:
        query, body = {**params, "timestamp": int(time.time() * 1000)}, {}
    qs = urlencode(sorted((k, str(v)) for k, v in query.items()))
    bs = urlencode(sorted((k, str(v)) for k, v in body.items()))
    sig = hmac.new(secret.encode(), (qs + bs).encode(), hashlib.sha256).hexdigest()
    headers = {"X-BH-APIKEY": key}
    if bs:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = requests.request(method, f"{HOST}{PREFIX}{path}?{qs}&signature={sig}",
                         headers=headers, data=bs or None, timeout=15)
    data = r.json()          # read the body BEFORE the status: errors are 400 + {"code": -xxxx}
    if r.status_code >= 400 or (isinstance(data, dict) and str(data.get("code", "0")).startswith("-")):
        raise Exception(f"stockcoin {path}: {data}")
    return data
```

A wrong key answers `-1002`, a wrong secret `-1022` — HTTP 400 in both cases, never 401.

## Account Structure

| Wallet | What it is | Read |
|---|---|---|
| Main account | Where deposits land | **Not readable with a FUTURES key** |
| Futures account | The trading account. **This is the equity / sizing base.** | `GET /futures/balance` |

- `GET /futures/balance` returns a list of per-token rows. **Equity = USDT row `total` + `totalUnRealizedPnl`**
  (equals the row's `futureAssetTotal`). `total` alone is the wallet balance and does not move with price.
- An empty futures account answers `[]` — that is equity 0, not an error.
- **Money stuck in the main account is invisible.** A deposit must be moved to futures **in the StockCoin app**.
- **No transfer, deposit, withdrawal, fund-flow or sub-account API** for this key type: `/account` answers
  `-1005`, and balance-flow / deposit / withdrawal / transfer-history / futures-income reads answer `-1008 Not Found`.
  The agent cannot move money between wallets — the user does it in the app. A deposit or withdrawal therefore
  only shows up as an equity jump.
- No account-id endpoint: the account id is the `accountId` on the latest row of `GET /futures/orders/history`
  (unreadable before the first order).

## Contracts and Sizing

- **`quantity` is CONTRACTS. One contract = 0.0001 base** for every listed symbol (no endpoint publishes the
  multiplier; derived from public 24h `volume` vs `quoteVolume` and confirmed by `contractMultiplier` on live
  order replies). Minimum = 1 contract, step = 1 contract.
- Sanity-check before sizing: `quoteVolume ÷ (volume × 0.0001)` is the 24h VWAP and must sit inside
  `lowPrice`–`highPrice` from the ticker. If it does not, the multiplier is wrong for that symbol — **stop**;
  a wrong multiplier is an N-times order. If an order reply's `contractMultiplier` differs, stop too.
- No tick size is published: use the number of decimals the public depth shows. Too many decimals answers
  `-1134` "Order price decimal too long" — drop one decimal and retry once.
- There is no mark price: use the ticker's `lastPrice` (positions also carry `lastPrice`).

## Hedge Mode Only

There is no one-way mode — the `side` names the leg, so a close can never open the opposite side:

| Side | Effect |
|---|---|
| `BUY_OPEN` | open / add long |
| `SELL_CLOSE` | reduce / close long |
| `SELL_OPEN` | open / add short |
| `BUY_CLOSE` | reduce / close short |

A close is capped at the leg's `available` contracts (from `GET /futures/positions?symbol=…&side=LONG|SHORT`).
A symbol can hold a LONG and a SHORT row at the same time.

## Not Every Contract Is Open to the API

Some listed contracts answer **`-1157` "not available for api trading"** — they can only be traded by hand in the
StockCoin app. Measured 2026-10: a one-contract open + close filled on 31 of 36 listed contracts; BTC, ETH, XRP,
SAMSUNG and SKHYNIX answered `-1157`. Which ones are open is the venue's call and can change — read it off the
reply, do not keep a list. On `-1157`, tell the user to trade that name on another venue.

## Operation Flow

### Step 0: Credential Check
Verify `STOCKCOIN_API_KEY`, `STOCKCOIN_SECRET_KEY`. If missing — **STOP**. Read `GET /futures/balance`
once: `-1005` = wrong key type, `-1002` / `-1022` = wrong key / secret.

### Step 1: Pre-Trade Check
- Read the ticker (`lastPrice`) and run the multiplier sanity check above
- Read `GET /futures/positions` — existing legs, `available`, `leverage`
- Convert the intended base quantity to whole contracts (floor); under 1 contract → do not send
- Leverage is set in the StockCoin app; no API for it has been verified — do not guess one

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After an order → `GET /futures/order` by `orderId` until terminal. After a close → `GET /futures/positions`,
**then cancel the leg's leftover STOP orders** (see below).

## Quick Reference

Public (no signature, no prefix beyond what is shown):

| Operation | Method | Path |
|---|---|---|
| Server time | GET | `/openapi/v1/time` |
| 24h ticker (`lastPrice`, `bestBidPrice`, `bestAskPrice`, `volume`, `quoteVolume`, `highPrice`, `lowPrice`, `openInterest`) | GET | `/openapi/quote/v1/contract/ticker/24hr?symbol=NVDA-PERP-USDT` (returns a one-row list) |
| Order book (`bids` / `asks` as `[price, contracts]`) | GET | `/openapi/quote/v1/contract/depth?symbol=NVDA-PERP-USDT&limit=20` |

Private (signed, under `/openapi/v1`):

| Operation | Method | Path |
|---|---|---|
| Futures balance | GET | `/futures/balance` |
| Positions | GET | `/futures/positions` (optional `symbol`, `side`) |
| Place order (LIMIT, MARKET, STOP) | POST | `/futures/order` |
| Query order | GET | `/futures/order?symbol=…&orderId=…` (or `clientOrderId`; add `orderType=STOP` for a stop) |
| Cancel order | DELETE | `/futures/order?symbol=…&orderId=…` (add `orderType=STOP` for a stop) |
| Open orders | GET | `/futures/orders/open?orderType=LIMIT\|STOP&symbol=…&limit=500` |
| Order history | GET | `/futures/orders/history?limit=…` |
| Fills (fees) | GET | `/futures/trades?symbol=…&startTime=…&limit=500` |

### Order parameters

| Order | Parameters |
|---|---|
| Market | `symbol`, `side`, `orderType=LIMIT`, `priceType=MARKET`, `price=0`, `quantity` (contracts), `clientOrderId` |
| Limit | `symbol`, `side`, `orderType=LIMIT`, `priceType=INPUT`, `price`, `quantity`, `timeInForce` (`GTC` / `IOC` / `FOK`), `clientOrderId` |
| Post-only | as Limit with **`timeInForce=LIMIT_MAKER`** (not in the venue doc); one that would cross answers `-1158` |
| Stop-loss / take-profit | `symbol`, `side` = the leg's `*_CLOSE`, `orderType=STOP`, `priceType=MARKET`, `price=0`, `triggerPrice`, `quantity`, `clientOrderId` |

- **`clientOrderId` is mandatory** (charset `A-Z a-z 0-9 _ -`). Reusing one answers `-1141` — query that id instead of
  resending. On a timeout or 5xx after a POST, **look the order up by `clientOrderId` before anything else; never
  blindly resend** (the first one may have filled).
- A market order's unfilled rest comes back `CANCELED` — check `executedQty`, it may be partly filled.
- Terminal order statuses: `FILLED` / `CANCELED` / `REJECTED` — anything else is still open. STOP orders use
  `ORDER_NEW` / `ORDER_CANCELED`.

## Field-Verified Lessons (live key, 2026-10)

1. **STOP orders are NOT cancelled when the position closes.** After a market close the stop was still listed;
   left there, it acts on the next position opened on that leg. After every close that leaves a leg at zero,
   list `orderType=STOP` open orders and cancel that leg's `*_CLOSE` stops. Same after a stop-loss fires: the
   matching take-profit is still resting (and vice versa).
2. **A partial close does not resize stops** — there is no close-whole-position flag, a stop covers the contracts it
   was placed for. After reducing, cancel and re-place the stop at the new size.
3. STOP orders do not lock `available`; one below and one above the price can rest together (the venue picks the
   direction). SL/TP is two steps — the position is naked for one round trip after the entry.
4. **A cancel's reply is the order as it stood BEFORE the cancel** (`NEW`), and cancelling an already-cancelled order
   answers that order (`CANCELED`), not an error. Confirm a cancel with a follow-up `GET /futures/order`.
5. **Fees are on `/futures/trades`, not the order**, and the rows can lag the fill — re-read briefly; if still missing,
   report the fee as unknown, never 0.
6. `-1131` "Balance insufficient" = order past the account's margin.

### Error codes

| Code | Meaning |
|---|---|
| `-1002` / `-1022` | wrong key / wrong secret |
| `-1005` | key is not a FUTURES-type key |
| `-1008` | endpoint not available (flows, transfers, deposits, withdrawals) |
| `-1021` | timestamp outside the window — resync with `/openapi/v1/time` |
| `-1001` / `-1003` / `-1006` / `-1007` | transient (`-1003` = rate limited — back off) |
| `-1121` / `-1157` | symbol unavailable / contract not open to API trading |
| `-1131` | balance insufficient |
| `-1136` / `-1200` | below minimum size |
| `-1134` | price has too many decimals |
| `-1141` | duplicated `clientOrderId` |
| `-1158` | post-only (`LIMIT_MAKER`) would cross |
| `-2013` / `-1142` | cancel of an order that is gone or never existed |
| `-1150` | cancel failed — the order may still rest; re-read it |

## Security
- WRITE operations require **"CONFIRM"**
- Trading hours are not verified — check them on the venue before relying on a stop outside the underlying's
  exchange hours; a gap at the underlying's open can move the price past a stop
- "Not financial advice. Trading carries significant risk of loss."
