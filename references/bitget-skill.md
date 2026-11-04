# Bitget Trading

**Base URL:** `https://api.bitget.com` | **Spot:** `BTCUSDT` | **Futures:** `BTCUSDT` + `productType=USDT-FUTURES` | **Success:** `"code": "00000"`

**Symbols:** spot and USDT-M perpetuals both use `BTCUSDT` — identical to the platform
canonical form (dashless uppercase), so `lib/data.normalize_symbol()` needs no dash / case mapping (stock-perp names below are the exception).
USDT-M also lists US-stock perps (`isRwa: "YES"` in the contract list) — usually the bare
ticker (`NVDAUSDT`), but `<T>STOCKUSDT` (`ACNSTOCKUSDT`, `BBSTOCKUSDT` …) where a coin owns
the bare name; the shipped libs map those back to the strategy's ticker
(`references/stock-perps.md`). Also eight Taiwan-stock perps (`TWTSMUSDT` …). Sizes are in
the BASE coin on every USDT-M endpoint (`sizeMultiplier` is the step, `minTradeNum` the
minimum, `minTradeUSDT` the minimum order value) — there is no contract-count conversion.

Full endpoint list in `references/bitget-api-reference.md`

## Account types — Classic and UTA, both supported

Bitget runs two account types with two different private APIs. One key works on both; the
account's type decides which API answers (an upgraded account's existing key gains UTA
access).

| Type | Private API | How a key tells you |
|---|---|---|
| **Classic** | v2 (`/api/v2/...`) | `GET /api/v3/account/settings` answers `40084` "You are in Classic Account mode" (measured) |
| **Unified Trading Account (UTA)** | v3 (`/api/v3/...`) | `GET /api/v3/account/settings` → `accountMode: "unified"`; any v2 private endpoint answers `40085` |

**Blave Agent supports both Classic and UTA accounts** — each passed a real-account run
(Classic: main account, both position modes; UTA: the full live-verify script, stop-loss
included). The shipped libs read the type per key and pick the API themselves; never
hand-write v3 (or v2) calls to route around them. Any other `accountMode` (e.g. `hybrid`)
is refused on every read with a sentence telling the user to bind a Classic or UTA key, or
another exchange. A UTA key that cannot read the account settings is refused with "tick the
UTA read permission when creating the key".

### When the account type changes

When the user upgrades a Classic account to UTA (or Bitget does), or Bitget reports the
account as `upgrading` / `switching`, Blave holds: each round reads the account but places
nothing (entries refused for at least 2 minutes), and the legs held before the switch
(symbol, side, quantity) are kept on record. Then:

- **Every recorded leg reads back the same, with nothing new → trading resumes by itself.**
  Blave then checks on Bitget the stop-losses it placed itself (only legs whose last
  Blave-placed stop is still standing by Blave's own record; a stop the user placed in the
  app is not checked): all still there → one quiet event-list line, no notification; one
  gone (or Bitget's stop orders cannot be read) → one urgent notification listing those
  legs. **Nothing is re-placed automatically** — re-place a stop only if the user asks.
  If Blave's own record cannot be read, there is no urgent notification; the quiet line
  says the stops could not be confirmed — ask the user to check them on Bitget.
- **Anything else (a leg missing, a new leg, a different quantity) → trading is paused at
  once.** Tell the user which legs differ, to check them on Bitget, then press 啟動下單.
  Resuming does not trade the difference — Blave sizes against its own book, so if a
  quantity really changed, say the book and Bitget now differ for that symbol; never place
  an order to "fix" it, and never bind a new key for it.
- A switch still not settled after 30 minutes is reported as stuck.
- Bitget refuses a manual upgrade while orders are open, and keeps position size and
  average price. Whether a position's TP/SL survive an upgrade is not documented by Bitget
  and not measured — that is why the stop check exists.

## Authentication

**Credentials** (from `.env`): `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE`
(names are locked — bound machines already carry them).

No Bitget account? Register at **[https://www.bitget.com/](https://www.bitget.com/)**

Verify credentials before any private call. If missing — **STOP**.

**Key permissions:** futures read + trade. **No withdrawal, no transfer** — Blave never
moves money between wallets; the user transfers in the Bitget app.

**Signature:** `Base64(HMAC-SHA256(secret, timestamp + METHOD + path + body))`
- `timestamp`: Unix milliseconds
- GET body = `""`; the path includes the query string
- POST body = compact JSON (no spaces)

**Headers (authenticated requests):**
```
ACCESS-KEY: <api_key>
ACCESS-SIGN: <base64 signature>
ACCESS-PASSPHRASE: <passphrase>
ACCESS-TIMESTAMP: <unix ms>
Content-Type: application/json
locale: en-US
```

**Broker attribution: none — Bitget orders currently carry no attribution.** Blave's
Bitget channel code has not been issued, so no attribution header is sent on any request
(spot or futures, public or authenticated). Do not invent a code or send the header empty.
Bitget's channel header is `X-CHANNEL-API-CODE`; once the code is issued it goes in
`lib/account_bitget.BROKER_CHANNEL_CODE` (the only place either lib reads it), the repo
root `CLAUDE.md` attribution table, and this section.

> Python signature implementation: `references/bitget-api-reference.md`

## Account Structure

### UTA

- **Equity = `equity` of the USDT asset row of the unified account**
  (`GET /api/v3/account/assets`: balance + frozen margin + unrealized PnL). Other coins
  count as collateral at Bitget but are holdings here, not equity — same USDT-only base as
  on Classic.
- The **funding account** (`GET /api/v3/account/funding-assets`) cannot trade: shown in
  the breakdown only, never a sizing base.

### Classic

Wallets named by the transfer API (`fromType` / `toType`; source: ccxt `bitget.py`
`accountsByType` — not yet checked against a live transfer menu):

| Wallet (`fromType` / `toType`) | What it is |
|---|---|
| `usdt_futures` | USDT-M perpetuals. **The trading account — equity / sizing base** |
| `spot` | Spot wallet (ccxt also maps its "funding" alias here) |
| `usdc_futures` | USDC-M perpetuals (not traded by Blave) |
| `coin_futures` | Coin-M futures (not traded by Blave) |
| `crossed_margin` / `isolated_margin` | Spot margin (not traded by Blave) |
| `p2p` | P2P wallet |

- **Equity = the USDT row of the USDT-FUTURES account, `accountEquity`** (balance + frozen
  + unrealized PnL — measured: with a position open it matched the App's USDT-M equity).
  Other coins are holdings, not equity.
- **Money outside USDT-M is invisible to the trading account.** The user must transfer it
  to USDT-M in the app before trading. Show every non-zero row of
  `GET /api/v2/account/all-account-balance` (`accountType`, `usdtBalance`) so it never
  looks lost — display only, not a sizing base. That endpoint may list a separate funding
  row; its exact `accountType` names have not been measured yet.
- Not yet established: whether the App's wallet menu (copy trading, Earn …) has wallets
  neither endpoint lists, and which wallet a deposit lands in.

### Transfers

`POST /api/v2/spot/wallet/transfer` `{fromType, toType, amount, coin}` (optional `symbol`
for isolated margin, `clientOid`) → `{transferId, clientOrderId}`. Needs transfer
permission, which a Blave key does not have — tell the user to do it in the app.

## Blave Agent shipped libs

`lib/account_bitget.py` (equity, positions, holdings, cash flows, signing) and
`lib/order_bitget.py` (market / limit / post-only, chase and TWAP via `lib/execute`,
position SL/TP, cancel). **NEVER hand-write Bitget order calls; import from these.**
USDT-M perpetuals only — no spot.

- Every call picks the API by the account type (above). A request that meets a type change
  is never re-sent to the other API — the round is skipped and the switch hold opens.
- Position mode (one-way / hedge) is account-wide (Classic `posMode`, UTA `holdMode`) and
  read before every order; margin mode is per symbol. Switching position mode only works
  with no positions and no orders.
- **`side` means different things on the two APIs** (the one place a mistake opens the
  opposite position):

  | | Classic v2 | UTA v3 |
  |---|---|---|
  | hedge open long | `buy` + `tradeSide open` | `buy` + `posSide long` |
  | hedge close long | `buy` + `tradeSide close` | `sell` + `posSide long` |
  | hedge open short | `sell` + `tradeSide open` | `sell` + `posSide short` |
  | hedge close short | `sell` + `tradeSide close` | `buy` + `posSide short` |
  | one-way open | `side` = direction | `side` = direction |
  | one-way close | opposite side + `reduceOnly YES` | opposite side + `reduceOnly yes` |

  UTA hedge closes carry **no** `reduceOnly` (Bitget refuses it next to `posSide`); the lib
  caps the close at the leg's available size instead.
- SL/TP trigger on the mark price, market execution. **Classic:** position TP/SL
  (`planType` `pos_loss` / `pos_profit`, `POST /api/v2/mix/order/place-tpsl-order`).
  **UTA:** one `tpsl` strategy order in `full` mode per leg carrying both the SL and the TP
  (`POST /api/v3/trade/place-strategy-order`, `type: "tpsl"`, `tpslMode: "full"`, `side` =
  the closing direction, `posSide` = the leg). A second place on the same leg rewrites that
  order in place and empties the field it omits — the lib carries the other kind over.
- `clientOid`: 1–32 characters of `[A-Za-z0-9_-]` (the lib's own cap; Bitget accepted 33
  and 50, but `:` and `/` would be URL-encoded and break the signature).

## Field-Verified Lessons (live Classic account, 2026-10-22)

- **Side table, hedge mode:** `side` is the LEG — `buy + tradeSide close` closes a long.
  Over-closing by one step closed only the held size, no reverse leg.
- **Side table, one-way mode:** `side` is the order direction (buy then sell of the same
  size ended flat). A `reduceOnly YES` close larger than the position is **refused whole**
  with `40804` "closed positions cannot exceed positions held" — nothing closes; the lib
  re-reads the position and sends the remainder.
- `40762` "The order amount exceeds the balance" = insufficient margin (no position left).
- `40786` "Duplicate clientOid" — Bitget rejects a reused clientOid; look the order up by
  clientOid instead of resubmitting.
- Cancel a missing order → `43001` "The order does not exist" (HTTP 400). Cancel a missing
  plan order → `{"successList": [], "failureList": []}` with no error; re-read the plan list
  to know.
- Post-only that would cross is cancelled by Bitget without a fill; one that rests stays live.
- Both a full-position SL and TP stay listed together; **closing the position auto-cancels
  its TP/SL**.
- **`40092`** "This service is currently unavailable due to applicable regulatory
  requirements or account eligibility conditions" — opening `TWTSMUSDT` on a main account
  registered in Taiwan. The lib tags it `symbol_unavailable`: this account may not trade
  that product, the strategy is not at fault. Which regions / account types it covers is
  not in Bitget's API docs or announcements; do not tell the user it is permanent or
  Taiwan-wide — say this account cannot trade that symbol; suggest another symbol, or that
  the user ask Bitget support about the account's eligibility. US-stock perps (`NVDAUSDT`)
  traded normally on the same account.
- Not yet measured: whether a withdrawal's `size` includes the fee.

## Field-Verified Lessons (live UTA, 2026-10-23 – 10-26)

- **Hedge close:** `sell + posSide long` closed a long without opening a short.
  `reduceOnly` next to `posSide` is refused whole — `25238`.
- **One-way:** a reduce-only close larger than the position is refused whole — `25231`
  "Close quantity cannot exceed the held position quantity"; the lib re-reads and sends the
  remainder.
- **A UTA does NOT refuse the `clientOid` of a filled order — it fills it again.** Look the
  `clientOid` up before every v3 place (the lib does); never resubmit blindly.
- Unknown order id on order-info / cancel → `25204`; unknown `tpsl` id on cancel → `25575`
  (re-read the pending list to know).
- An SL then a TP placed separately on one leg left the TP only (the rewrite above).
- On a one-way account a long's TP listed `posSide short` — match `tpsl` orders by `side`
  (the closing direction), not `posSide`.
- A flat account's positions read `{"list": null}` (or `[]`).

Documented, not measured: an isolated leg's `tpsl` needs `marginMode` in the body, or
Bitget does not find the leg (`31008`).

## Operation Flow

### Step 0: Credential Check
Verify `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE`. If missing — **STOP**.

### Step 1: Pre-Trade Check (Futures)
- Account type: Classic or UTA (see above) — it picks the API for every call below.
  Any other type → stop; ask for a Classic or UTA key, or another exchange.
- Query positions: Classic `GET /api/v2/mix/position/all-position?productType=USDT-FUTURES`;
  UTA `GET /api/v3/position/current-position?category=USDT-FUTURES`
- If position exists → inherit leverage and margin mode, do NOT override

### Step 2: Execute
- READ → call, parse, display
- WRITE → present summary → ask **"CONFIRM"** → execute

### Step 3: Verify
After order → query order status (by `clientOid` if the reply had no `orderId`). After close → query positions.

## Quick Reference (Classic, v2)

| Operation | Method | Path |
|---|---|---|
| Account type | GET | `/api/v3/account/settings` (Classic → `40084`) |
| Spot balances | GET | `/api/v2/spot/account/assets` |
| Futures account | GET | `/api/v2/mix/account/accounts?productType=USDT-FUTURES` |
| All balances | GET | `/api/v2/account/all-account-balance` |
| Wallet transfer | POST | `/api/v2/spot/wallet/transfer` |
| Place spot order | POST | `/api/v2/spot/trade/place-order` |
| Cancel spot order | POST | `/api/v2/spot/trade/cancel-order` |
| Spot open orders | GET | `/api/v2/spot/trade/unfilled-orders` |
| Place futures order | POST | `/api/v2/mix/order/place-order` |
| Cancel futures order | POST | `/api/v2/mix/order/cancel-order` |
| Place position TP/SL | POST | `/api/v2/mix/order/place-tpsl-order` |
| Cancel TP/SL / plan order | POST | `/api/v2/mix/order/cancel-plan-order` |
| Futures open orders | GET | `/api/v2/mix/order/orders-pending` |
| Futures positions | GET | `/api/v2/mix/position/all-position` |
| Pending TP/SL / plan orders | GET | `/api/v2/mix/order/orders-plan-pending` (`planType` = `profit_loss` / `normal_plan` / `track_plan`) |
| Set leverage | POST | `/api/v2/mix/account/set-leverage` |
| Set margin mode | POST | `/api/v2/mix/account/set-margin-mode` |
| Spot ticker | GET | `/api/v2/spot/market/tickers` |
| Futures ticker | GET | `/api/v2/mix/market/ticker` |

## Quick Reference (UTA, v3)

Public market data (contracts, tickers) stays on v2 in either mode.

| Operation | Method | Path |
|---|---|---|
| Account type / hold mode / per-symbol margin mode | GET | `/api/v3/account/settings` |
| Unified account assets (equity) | GET | `/api/v3/account/assets` |
| Funding account | GET | `/api/v3/account/funding-assets` |
| Futures positions | GET | `/api/v3/position/current-position?category=USDT-FUTURES` |
| Place order | POST | `/api/v3/trade/place-order` |
| Cancel order | POST | `/api/v3/trade/cancel-order` |
| Order detail | GET | `/api/v3/trade/order-info` |
| Open orders | GET | `/api/v3/trade/unfilled-orders` |
| Place TP/SL (`type: "tpsl"`) | POST | `/api/v3/trade/place-strategy-order` |
| Cancel TP/SL | POST | `/api/v3/trade/cancel-strategy-order` |
| Pending TP/SL | GET | `/api/v3/trade/unfilled-strategy-orders?category=USDT-FUTURES&type=tpsl` |
| Deposit / withdrawal records | GET | `/api/v3/account/deposit-records` · `/api/v3/account/withdrawal-records` |

## Security
- WRITE operations require **"CONFIRM"**
- Always show liquidation price before opening leveraged positions

## References
- `references/bitget-api-reference.md` — spot + futures endpoints, Python signature
- Broker attribution table — repo root `CLAUDE.md`
