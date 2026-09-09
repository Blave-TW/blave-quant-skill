# Bybit Trading

**Base URL (Mainnet):** `https://api.bybit.com` | **Backup:** `https://api.bytick.com` | **Testnet:** `https://api-testnet.bybit.com`

**Symbols:** Spot and Linear perpetual both use `BTCUSDT` — identical to the platform
canonical form (dashless uppercase), so no mapping is needed and `lib/data.normalize_symbol()`
already covers it. **Success:** `"retCode": 0`.

**UTA only.** Everything below is verified against a Unified Trading Account
(`/v5/account/info` → `uta: 1`). A classic (non-UTA) account exposes different
account types and is NOT supported — fail loudly rather than guessing.

## Authentication

**Credentials** (from `.env`): `BYBIT_API_KEY`, `BYBIT_SECRET_KEY`

> `BYBIT_SECRET_KEY` is canonical — the web 自動下單 bind and `lib/venue.py` both
> write the `{ID}_SECRET_KEY` shape. This doc said `BYBIT_API_SECRET` until
> 2026-09, so the shipped libs still accept that name as a fallback; write new
> `.env` files with `BYBIT_SECRET_KEY`.

No Bybit account? Register at **[https://partner.bybit.com/b/BLAVE](https://partner.bybit.com/b/BLAVE)**

Verify credentials before any private call. If missing — **STOP**.

**Signature:** `HMAC-SHA256(secret, {timestamp}{apiKey}{recvWindow}{queryString|jsonBody})`
- GET: sign `{timestamp}{apiKey}{recvWindow}{queryString}`
- POST: sign `{timestamp}{apiKey}{recvWindow}{jsonBody}` — use **compact JSON** (no spaces, no newlines)

**Headers (all authenticated requests):**
```
X-BAPI-API-KEY: $BYBIT_API_KEY
X-BAPI-TIMESTAMP: <unix ms>
X-BAPI-SIGN: <hmac signature>
X-BAPI-RECV-WINDOW: 5000
referer: Ue001036
Content-Type: application/json   (POST only)
```

**`referer: Ue001036` is MANDATORY on every request — no exceptions.**

Rate limiting is real: bursts of back-to-back private calls return
`retCode 10006 "Too many visits"`. Pace account sweeps.

## Account Structure

A UTA account has exactly **two** wallets, and they are read through **two different
endpoints** — there is no single call that lists both:

| Wallet | What it is | How to read it |
|---|---|---|
| `UNIFIED` | The trading account. Spot, linear perps and options all settle here. **This is the equity / sizing base.** | `GET /v5/account/wallet-balance?accountType=UNIFIED` → `list[0].totalEquity` plus a `coin[]` array |
| `FUND` | Funding account. Deposits land here; it cannot trade. | `GET /v5/asset/transfer/query-account-coins-balance?accountType=FUND` |

- `wallet-balance` accepts **only** `accountType=UNIFIED`; `CONTRACT` / `SPOT` /
  `FUND` / `OPTION` all return `retCode 10001 "accountType only support UNIFIED"`.
- `query-account-coins-balance` has a *different* allowlist: `FUND` works,
  `CONTRACT` / `SPOT` / `OPTION` return `131203 "accountType is invalid for current user"`,
  and `UNIFIED` works but **requires an explicit `coin` list of 1–10 coins**, so it
  cannot enumerate the unified wallet.
- **Money parked in FUND is invisible in equity.** `totalEquity` counts UNIFIED only.
  A balance report that omits FUND makes the user's money disappear — always show both.
- **There is no separate spot wallet.** A spot buy on UTA lands in the UNIFIED coin
  array and simultaneously counts as margin. Spot inventory and holdings are read
  from that same `coin[]` array, not from a spot-specific endpoint.
- `totalEquity` is **USD-valued, not USDT face value** (measured: a 90 USDT balance
  read back as `totalEquity` 89.97579 with `walletBalance` 90 / `usdValue` 89.97579).

### Transfers (moving money to the trading account)

`POST /v5/asset/transfer/inter-transfer` with
`{transferId: <UUID>, coin, amount, fromAccountType, toAccountType}` →
`{transferId, status: "SUCCESS"}`, effective immediately. `transferId` must be a
client-generated UUID. Use this to move deposits `FUND → UNIFIED` before trading.

## Deposits / Withdrawals

Bybit separates internal from external transfers **by endpoint, not by a flag** —
do NOT port Binance's `transferType` or BingX's direction-flag assumptions here:

| Endpoint | Contents |
|---|---|
| `GET /v5/asset/deposit/query-record` | on-chain deposits only |
| `GET /v5/asset/deposit/query-internal-record` | internal (off-chain) deposits — separate endpoint |
| `GET /v5/asset/withdraw/query-record` | withdrawals; `withdrawType` 0 = on-chain, 1 = internal, 2 = all |
| `GET /v5/asset/transfer/query-inter-transfer-list` | transfers between your own wallets |

External on-chain flow = `deposit/query-record` + `withdraw/query-record?withdrawType=0`.
The internal endpoints are naturally excluded; no post-filtering is needed.

Deposit fields: `amount`, `coin`, `chain`, `txID`, `status` (3 = success),
`successAt` (unix ms), `depositFee`. Wallet-transfer records carry `transferId`,
`coin`, `amount`, `fromAccountType`, `toAccountType`, `timestamp` (ms), `status`.

Withdrawal fields: `amount`, `withdrawFee`, `coin`, `chain`, `txID`,
`status` (`"success"`), `createTime` / `updateTime` (unix ms), `withdrawId`,
`withdrawType` (0 = on-chain).

**The withdrawal fee is charged ON TOP of `amount`.** A 10 USDT withdrawal with a
1 USDT fee debits the account 11 — confirmed against `/v5/account/transaction-log`,
which shows a single `TRANSFER_OUT` of `-11`. Anything that needs the real balance
change must use `amount + withdrawFee`; using `amount` alone leaves the fee looking
like a trading loss. Withdrawals are debited from **UNIFIED, not FUND**, even when
FUND holds a balance.

## Trading Rules

Spot and linear use **separate filters with different field names** — never share them:

| | Linear (`category=linear`) | Spot (`category=spot`) |
|---|---|---|
| Size step | `lotSizeFilter.qtyStep` | `lotSizeFilter.basePrecision` |
| Min size | `lotSizeFilter.minOrderQty` | `lotSizeFilter.minOrderQty` |
| Min notional | `lotSizeFilter.minNotionalValue` | `lotSizeFilter.minOrderAmt` (quote) |
| Tick | `priceFilter.tickSize` | `priceFilter.tickSize` |

Both come from `GET /v5/market/instruments-info?category=<cat>&symbol=<SYMBOL>`.
The binding constraint is often the size step, not the min notional — BTCUSDT linear
has `minNotionalValue 5` but `minOrderQty 0.001`, which at ~79,000 is a ~79 USDT floor.

**Best bid/ask** come from `GET /v5/market/tickers` directly (`bid1Price`, `ask1Price`,
`bid1Size`, `ask1Size`) — no order-book call, and never substitute mark or last price.

## Operation Flow

### Step 0: Credential Check
Verify `BYBIT_API_KEY`, `BYBIT_SECRET_KEY`, then `GET /v5/user/query-api` and confirm
`uta: 1`. **The `uta` flag is on `/v5/user/query-api`, not `/v5/account/info`** — the
latter returns `marginMode` / `unifiedMarginStatus` / `dcpStatus` and no `uta` key,
so a guard written against it passes for every account. The same response carries
`permissions`, worth checking before reporting a bare venue error code.
If missing or not UTA — **STOP**. Default to **Mainnet** unless the user
explicitly requests Testnet.

### Step 1: Pre-Trade Check
`GET /v5/position/list?category=linear&symbol=<SYMBOL>` → if a position exists,
inherit side and leverage. `positionIdx` 0 = one-way mode; 1/2 = hedge mode.

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → `GET /v5/order/realtime` and `GET /v5/execution/list`; after close →
`GET /v5/position/list`.

## Key Endpoints

| Action | Method | Path |
|---|---|---|
| Account info (UTA check) | GET | `/v5/account/info` |
| API key permissions | GET | `/v5/user/query-api` |
| Wallet balance (UNIFIED) | GET | `/v5/account/wallet-balance` |
| Coin balance (FUND) | GET | `/v5/asset/transfer/query-account-coins-balance` |
| Wallet transfer | POST | `/v5/asset/transfer/inter-transfer` |
| Market info | GET | `/v5/market/instruments-info` |
| Ticker / BBO | GET | `/v5/market/tickers` |
| Place order | POST | `/v5/order/create` |
| Cancel order | POST | `/v5/order/cancel` |
| Open orders | GET | `/v5/order/realtime` |
| Fills | GET | `/v5/execution/list` |
| Positions | GET | `/v5/position/list` |
| Set leverage | POST | `/v5/position/set-leverage` |
| Amend TP/SL on an open position | POST | `/v5/position/trading-stop` |
| Order history | GET | `/v5/order/history` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions
- "Not financial advice. Trading carries significant risk of loss."

## Field-Verified Lessons (live UTA account, 2026-09-09)

- **Stop-loss and take-profit are native and atomic** — pass `takeProfit`, `stopLoss`
  and `tpslMode: "Full"` on `POST /v5/order/create` itself. Measured: the position
  came back carrying both prices and two server-side conditional orders appeared
  immediately. No naked window, no client-side fallback needed.
- **`/v5/order/realtime` lists those TP/SL orders as open orders** (`reduceOnly: true`,
  `stopOrderType: TakeProfit` / `StopLoss`). Any orphan-order sweep MUST skip rows
  with a non-empty `stopOrderType` — cancelling them strips the position's protection.
- **Flat position auto-cancels its TP/SL.** After a reduce-only close took size to 0,
  both conditional orders were gone with no explicit cancel.
- **Market orders split into several fills** (a 64-contract close reported 3 executions).
  Aggregate `/v5/execution/list` for VWAP; never read a single fill as the result.
- Closing is `side` reversed + `reduceOnly: true` (+ `positionIdx` matching the position).
- `orderLinkId` is the idempotency field for **both** spot and linear — unlike Binance,
  there is no separate spot parameter name.
- Account defaults observed on a fresh UTA account: `leverage 10`, `tradeMode 0` (cross),
  `positionIdx 0` (one-way).
- Fills report `execFee` in `feeCurrency` (USDT for linear USDT perps), plus `isMaker`
  and `closedSize` for reduce legs.
- **A price formatted as `"0"` is accepted silently and means NO protection.** Passing
  `stopLoss: "0"` (which is what a tick size of `0.00001` turns into if it is put
  through `float()` first — `str(0.00001)` is `"1e-05"`, whose decimal count reads as
  zero) returns retCode 0 and an order that fills into a NAKED position. Always format
  prices from the instrument filter's original string, and always read the position
  back to confirm protection actually attached.
- Spot market BUYs charge the fee in the BASE coin — a 6 USDT buy reporting
  `cumExecQty` 66.3 credits 66.2337 to the wallet. Size the sell leg from the WALLET
  balance, never from the buy's `cumExecQty`.
- Both spot sides gate on `minOrderAmt` (quote value): selling 1 DOGE (~0.09 USDT) is
  rejected with retCode 170140 "Order value exceeded lower limit".

## References
- Broker attribution table — repo root `CLAUDE.md`
