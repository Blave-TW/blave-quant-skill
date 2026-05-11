# KuCoin Trading

**Spot Base URL:** `https://api.kucoin.com` | **Futures Base URL:** `https://api-futures.kucoin.com`

**Spot symbol:** `BTC-USDT` | **Futures symbol:** `XBTUSDTM` | **Success:** `"code": "200000"`

Full details in `references/kucoin-api-reference.md`

## Authentication

**User credentials** (from `.env`): `KUCOIN_API_KEY`, `KUCOIN_API_SECRET`, `KUCOIN_API_PASSPHRASE`

No KuCoin account? Register at **[https://www.kucoin.com/r/af/blave](https://www.kucoin.com/r/af/blave)** (Blave referral link)

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `Base64(HMAC-SHA256(api_secret, timestamp + METHOD + path + body))`
- GET: `path` includes query string (e.g., `/api/v1/orders?status=active`)
- POST: `body` is compact JSON string
- `timestamp`: Unix milliseconds

**Passphrase:** `Base64(HMAC-SHA256(api_secret, api_passphrase))` — v2/v3 keys are signed, NOT plain text

**Headers (all authenticated requests):**
```
KC-API-KEY: $KUCOIN_API_KEY
KC-API-SIGN: <signature>
KC-API-TIMESTAMP: <unix ms>
KC-API-PASSPHRASE: <signed passphrase>
KC-API-KEY-VERSION: 3
```

> Python implementation: `references/kucoin-api-reference.md`

## Broker Attribution (MANDATORY on every request)

All KuCoin API requests — public and private, spot and futures — **must** include these 4 broker headers. Omitting them disqualifies rebate eligibility.

```
KC-BROKER-NAME: blave              (spot)  |  blaveFutures         (futures)
KC-API-PARTNER: blave              (spot)  |  blaveFutures         (futures)
KC-API-PARTNER-SIGN: <partner_sig>
KC-API-PARTNER-VERIFY: true
```

**Partner sign:** `Base64(HMAC-SHA256(BROKER_KEY, timestamp + partner + KUCOIN_API_KEY))`
- Spot `BROKER_KEY`: `1c10e0c0-bc3e-4a18-ad53-e41e6df5f757` | Futures `BROKER_KEY`: `520815df-b324-4494-9bc8-b1015732b902` — hardcoded in `references/kucoin-api-reference.md` (not a user env var)
- `partner`: `blave` (spot) or `blaveFutures` (futures)

> Full Python helper in `references/kucoin-api-reference.md`

## Operation Flow

### Step 0: Credential Check
Verify `KUCOIN_API_KEY`, `KUCOIN_API_SECRET`, `KUCOIN_API_PASSPHRASE`. If any missing — **STOP**. Default to **Production** unless user explicitly requests Sandbox.

### Step 1: Pre-Trade Check
- Spot: `GET /api/v1/accounts?type=trade` → check available balance for the quote/base currency
- Futures: `GET /api/v1/position?symbol=<SYMBOL>` → check existing position, inherit leverage if position exists

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → `GET /api/v1/orders/{orderId}`. After close → `GET /api/v1/position?symbol=<SYMBOL>` (futures) or `GET /api/v1/accounts?type=trade` (spot).

## Quick Reference — Spot

| Action | Method | Path |
|---|---|---|
| Accounts | GET | `/api/v1/accounts` |
| Ticker | GET | `/api/v1/market/stats?symbol=BTC-USDT` |
| Place order | POST | `/api/v1/orders` |
| Cancel order | DELETE | `/api/v1/orders/{orderId}` |
| Cancel all | DELETE | `/api/v1/orders` |
| Active orders | GET | `/api/v1/orders?status=active` |
| Order detail | GET | `/api/v1/orders/{orderId}` |
| Recent fills | GET | `/api/v1/fills` |
| Klines | GET | `/api/v1/market/candles` |

## Quick Reference — Futures

| Action | Method | Path |
|---|---|---|
| Account balance | GET | `/api/v1/account-overview` |
| All positions | GET | `/api/v1/positions` |
| Position detail | GET | `/api/v1/position?symbol=XBTUSDTM` |
| Ticker | GET | `/api/v1/ticker?symbol=XBTUSDTM` |
| Place order | POST | `/api/v1/orders` |
| Place stop order | POST | `/api/v1/stopOrders` |
| Cancel order | DELETE | `/api/v1/orders/{orderId}` |
| Cancel all | DELETE | `/api/v1/orders` |
| Active orders | GET | `/api/v1/orders?status=active` |
| Funding rate | GET | `/api/v1/funding-rate/XBTUSDTM/current` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged futures positions
- "Not financial advice. Trading carries significant risk of loss."

## References
- `references/kucoin-api-reference.md` — full endpoints, Python signature, broker sign helper
- `references/kucoin-bpp.md` — BPP commission tiers, referral bonuses, dashboard guide
