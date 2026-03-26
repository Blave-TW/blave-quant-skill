# BitMart Spot Trading API Reference

> **Credentials:** Read from `.env` — `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`.

> **Broker ID:** Always include `X-BM-BROKER-ID: BlaveData666666` header on ALL requests.

> **Base URL:** `https://api-cloud.bitmart.com`
>
> **Sources of truth:**
> - Go SDK v1.4.0 for method signatures and parameter names
> - BitMart API docs for HTTP methods and response formats

---

## Parameter Naming Convention

> **IMPORTANT:** Parameter naming varies by API version:
>
> - **v1-v3 endpoints:** `snake_case` (e.g., `client_order_id`, `order_id`, `start_time`)
> - **v4 endpoints:** `camelCase` (e.g., `clientOrderId`, `orderId`, `orderMode`, `startTime`)
> - **Exception:** v2 `submit_order` uses `stpMode` (camelCase) alongside `client_order_id` (snake_case)
> - **Exception:** v1 `margin/submit_order` uses `clientOrderId` (camelCase in a v1 endpoint)

---

## Authentication Levels

| Level | Header | Description |
|-------|--------|-------------|
| **NONE** | None | Public endpoints, no credentials needed |
| **KEYED** | `X-BM-KEY` | Requires API key only |
| **SIGNED** | `X-BM-KEY`, `X-BM-SIGN`, `X-BM-TIMESTAMP` | Requires full HMAC-SHA256 signature |

**Signature construction:**

- GET requests: message = `{timestamp}#{memo}#`
- POST requests: message = `{timestamp}#{memo}#{body}`
- Sign with HMAC-SHA256 using your secret key

---

## Table of Contents

**Public Market Data (1-9)**
1. [Get Single Pair Ticker](#1-get-single-pair-ticker)
2. [Get All Pair Tickers](#2-get-all-pair-tickers)
3. [Order Book Depth](#3-order-book-depth)
4. [Recent Public Trades](#4-recent-public-trades)
5. [Historical K-Line](#5-historical-k-line)
6. [Latest K-Line](#6-latest-k-line)
7. [Trading Pair Details](#7-trading-pair-details)
8. [Trading Pair List](#8-trading-pair-list)
9. [All Supported Currencies](#9-all-supported-currencies)

**Account & Margin Account (10-17)**
10. [Account Balance (All Wallets)](#10-account-balance-all-wallets)
11. [Spot Wallet Balance](#11-spot-wallet-balance)
12. [Actual Trade Fee Rate](#12-actual-trade-fee-rate)
13. [Base Fee Rate](#13-base-fee-rate)
14. [Isolated Margin Account Details](#14-isolated-margin-account-details)
15. [Trading Pair Borrowing Rate & Amount](#15-trading-pair-borrowing-rate--amount)
16. [Borrow Record (Isolated)](#16-borrow-record-isolated)
17. [Repayment Record (Isolated)](#17-repayment-record-isolated)

**Spot Trading (18-23)**
18. [Place Single Order](#18-place-single-order)
19. [Place Margin Order](#19-place-margin-order)
20. [Batch Place Orders](#20-batch-place-orders)
21. [Cancel Single Order](#21-cancel-single-order)
22. [Cancel Multiple Orders](#22-cancel-multiple-orders)
23. [Cancel All Open Orders](#23-cancel-all-open-orders)

**Order Query (24-29)**
24. [Query Order by Order ID](#24-query-order-by-order-id)
25. [Query Order by Client Order ID](#25-query-order-by-client-order-id)
26. [All Open Orders](#26-all-open-orders)
27. [Historical Orders](#27-historical-orders)
28. [Account Trade History](#28-account-trade-history)
29. [Trades for Specific Order](#29-trades-for-specific-order)

**Margin Loan (30-32)**
30. [Margin Borrow (Isolated)](#30-margin-borrow-isolated)
31. [Margin Repay (Isolated)](#31-margin-repay-isolated)
32. [Margin Asset Transfer](#32-margin-asset-transfer)

**System (33-34)**
33. [Get System Time](#33-get-system-time)
34. [Get System Service Status](#34-get-system-service-status)

---

# Public Market Data

## 1. Get Single Pair Ticker

`GET /spot/quotation/v3/ticker`

**Auth:** NONE | **Rate Limit:** 15 req/2sec per IP

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/quotation/v3/ticker?symbol=BTC_USDT"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "symbol": "BTC_USDT",
    "last": "67000.00",
    "v_24h": "12345.6789",
    "qv_24h": "827045678.90",
    "open_24h": "66500.00",
    "high_24h": "67500.00",
    "low_24h": "66000.00",
    "fluctuation": "+0.0075",
    "bid_px": "66999.50",
    "bid_sz": "0.5000",
    "ask_px": "67000.50",
    "ask_sz": "0.3200",
    "ts": "1700000000000"
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `symbol` | Trading pair |
| `last` | Last trade price |
| `v_24h` | 24h volume in base currency |
| `qv_24h` | 24h volume in quote currency |
| `open_24h` | Opening price 24h ago |
| `high_24h` | 24h high price |
| `low_24h` | 24h low price |
| `fluctuation` | 24h price change ratio (signed) |
| `bid_px` | Best bid price |
| `bid_sz` | Best bid size |
| `ask_px` | Best ask price |
| `ask_sz` | Best ask size |
| `ts` | Timestamp in milliseconds (String) |

---

## 2. Get All Pair Tickers

`GET /spot/quotation/v3/tickers`

**Auth:** NONE | **Rate Limit:** 10 req/2sec per IP

**Parameters:** None

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/quotation/v3/tickers"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": [
    ["BTC_USDT", "67000.00", "12345.6789", "827045678.90", "66500.00", "67500.00", "66000.00", "+0.0075", "66999.50", "0.5000", "67000.50", "0.3200", "1700000000000"],
    ["ETH_USDT", "3500.00", "98765.4321", "345678901.23", "3480.00", "3520.00", "3460.00", "+0.0057", "3499.80", "5.0000", "3500.20", "3.2000", "1700000000000"]
  ]
}
```

**Response Fields (array positions):**

| Index | Field | Description |
|-------|-------|-------------|
| 0 | symbol | Trading pair |
| 1 | last | Last trade price |
| 2 | v_24h | 24h volume in base currency |
| 3 | qv_24h | 24h volume in quote currency |
| 4 | open_24h | Opening price 24h ago |
| 5 | high_24h | 24h high price |
| 6 | low_24h | 24h low price |
| 7 | fluctuation | 24h price change ratio |
| 8 | bid_px | Best bid price |
| 9 | bid_sz | Best bid size |
| 10 | ask_px | Best ask price |
| 11 | ask_sz | Best ask size |
| 12 | timestamp | Timestamp in milliseconds (String) |

---

## 3. Order Book Depth

`GET /spot/quotation/v3/books`

**Auth:** NONE | **Rate Limit:** 15 req/2sec per IP

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `limit` | Integer | No | Number of levels, max 50, default 35 |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/quotation/v3/books?symbol=BTC_USDT&limit=5"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "ts": "1700000000000",
    "symbol": "BTC_USDT",
    "asks": [
      ["67000.50", "0.3200"],
      ["67001.00", "1.5000"],
      ["67002.50", "0.8000"],
      ["67005.00", "2.1000"],
      ["67010.00", "0.4500"]
    ],
    "bids": [
      ["66999.50", "0.5000"],
      ["66999.00", "1.2000"],
      ["66998.00", "0.7500"],
      ["66995.00", "3.0000"],
      ["66990.00", "1.8000"]
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `ts` | Timestamp in milliseconds |
| `symbol` | Trading pair |
| `asks` | Ask levels as `[[price, amount], ...]`, sorted ascending by price |
| `bids` | Bid levels as `[[price, amount], ...]`, sorted descending by price |

---

## 4. Recent Public Trades

`GET /spot/quotation/v3/trades`

**Auth:** NONE | **Rate Limit:** 15 req/2sec per IP

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `limit` | Integer | No | Number of trades, max 50, default 50 |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/quotation/v3/trades?symbol=BTC_USDT&limit=3"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": [
    ["BTC_USDT", "1700000000000", "67000.00", "0.1500", "buy"],
    ["BTC_USDT", "1699999999500", "66999.50", "0.2300", "sell"],
    ["BTC_USDT", "1699999999000", "67000.50", "0.0800", "buy"]
  ]
}
```

**Response Fields (array positions):**

| Index | Field | Description |
|-------|-------|-------------|
| 0 | symbol | Trading pair |
| 1 | timestamp | Trade time in milliseconds |
| 2 | price | Trade price |
| 3 | size | Trade size in base currency |
| 4 | side | `"buy"` or `"sell"` |

---

## 5. Historical K-Line

`GET /spot/quotation/v3/klines`

**Auth:** NONE | **Rate Limit:** 10 req/2sec per IP

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `before` | Long | No | Start timestamp in **seconds** |
| `after` | Long | No | End timestamp in **seconds** |
| `step` | Integer | No | K-line interval in minutes. Allowed values: `1`, `5`, `15`, `30`, `60`, `120`, `240`, `1440`, `10080`, `43200` (10 values). Default: `1` |
| `limit` | Integer | No | Number of candles, max 200, default 100 |

**Kline step reference:**

| Step | Interval |
|------|----------|
| 1 | 1 minute |
| 5 | 5 minutes |
| 15 | 15 minutes |
| 30 | 30 minutes |
| 60 | 1 hour |
| 120 | 2 hours |
| 240 | 4 hours |
| 1440 | 1 day |
| 10080 | 1 week |
| 43200 | 1 month |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/quotation/v3/klines?symbol=BTC_USDT&step=60&limit=3"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": [
    ["1700000000", "66800.00", "67100.00", "66750.00", "67000.00", "125.5000", "8398250.00"],
    ["1699996400", "66600.00", "66900.00", "66550.00", "66800.00", "98.3200", "6557568.00"],
    ["1699992800", "66700.00", "66750.00", "66500.00", "66600.00", "110.1500", "7336990.50"]
  ]
}
```

**Response Fields (array positions):**

| Index | Field | Description |
|-------|-------|-------------|
| 0 | t | Candle open time in **seconds** (String) |
| 1 | o | Opening price |
| 2 | h | Highest price |
| 3 | l | Lowest price |
| 4 | c | Closing price |
| 5 | v | Volume in base currency |
| 6 | qv | Volume in quote currency |

---

## 6. Latest K-Line

`GET /spot/quotation/v3/lite-klines`

**Auth:** NONE | **Rate Limit:** 15 req/2sec per IP

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `before` | Long | No | Start timestamp in **seconds** |
| `after` | Long | No | End timestamp in **seconds** |
| `step` | Integer | No | K-line interval in minutes. Allowed values: `1`, `5`, `15`, `30`, `60`, `120`, `240`, `1440`, `10080`, `43200` (10 values). Default: `1` |
| `limit` | Integer | No | Number of candles, max 200, default 100 |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/quotation/v3/lite-klines?symbol=BTC_USDT&step=15&limit=2"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": [
    ["1700000000", "66950.00", "67100.00", "66900.00", "67050.00", "45.2300", "3028906.50"],
    ["1699999100", "66900.00", "66980.00", "66850.00", "66950.00", "38.1500", "2553427.50"]
  ]
}
```

**Response Fields (array positions):**

| Index | Field | Description |
|-------|-------|-------------|
| 0 | t | Candle open time in **seconds** (String) |
| 1 | o | Opening price |
| 2 | h | Highest price |
| 3 | l | Lowest price |
| 4 | c | Closing price |
| 5 | v | Volume in base currency |
| 6 | qv | Volume in quote currency |

---

## 7. Trading Pair Details

`GET /spot/v1/symbols/details`

**Auth:** NONE | **Rate Limit:** 12 req/2sec per IP

**Parameters:** None

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/symbols/details"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "symbols": [
      {
        "symbol": "BTC_USDT",
        "symbol_id": 1234,
        "base_currency": "BTC",
        "quote_currency": "USDT",
        "quote_increment": "0.01",
        "base_min_size": "0.00001",
        "price_min_precision": 2,
        "price_max_precision": 6,
        "trade_status": "trading",
        "min_buy_amount": "5.00",
        "min_sell_amount": "5.00",
        "expiration": "",
        "planned_down_time": ""
      }
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `symbol` | Trading pair name |
| `symbol_id` | Numeric symbol identifier |
| `base_currency` | Base currency (e.g., `BTC`) |
| `quote_currency` | Quote currency (e.g., `USDT`) |
| `quote_increment` | Minimum price increment |
| `base_min_size` | Minimum order size in base currency |
| `price_min_precision` | Minimum decimal places for price |
| `price_max_precision` | Maximum decimal places for price |
| `trade_status` | `"trading"` if active |
| `min_buy_amount` | Minimum buy order value in quote currency |
| `min_sell_amount` | Minimum sell order value in quote currency |
| `expiration` | Token expiration info (empty for most tokens) |
| `planned_down_time` | Planned downtime info (empty if none) |

---

## 8. Trading Pair List

`GET /spot/v1/symbols`

**Auth:** NONE | **Rate Limit:** 8 req/2sec per IP

**Parameters:** None

**SDK:** `GetSpotSymbol()` -> `requestWithoutParams(GET, API_SPOT_SYMBOLS_URL, NONE)`

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/symbols"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "symbols": [
      "BTC_USDT",
      "ETH_USDT",
      "ETH_BTC",
      "SOL_USDT",
      "XRP_USDT"
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `symbols` | Array of trading pair name strings |

---

## 9. All Supported Currencies

`GET /spot/v1/currencies`

**Auth:** NONE | **Rate Limit:** 8 req/2sec per IP

**Parameters:** None

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/currencies"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "currencies": [
      {
        "id": "BTC",
        "name": "Bitcoin",
        "withdraw_enabled": true,
        "deposit_enabled": true
      },
      {
        "id": "USDT",
        "name": "Tether",
        "withdraw_enabled": true,
        "deposit_enabled": true
      }
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `id` | Currency symbol (e.g., `BTC`) |
| `name` | Full currency name |
| `withdraw_enabled` | Whether withdrawals are enabled |
| `deposit_enabled` | Whether deposits are enabled |

---

# Account & Margin Account

## 10. Account Balance (All Wallets)

`GET /account/v1/wallet`

**Auth:** KEYED | **Rate Limit:** 12 req/2sec per KEY

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `currency` | String | No | Filter by currency, e.g., `BTC` |
| `needUsdValuation` | Boolean | No | Include USD valuation in response |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/account/v1/wallet" \
  -H "X-BM-KEY: $BITMART_API_KEY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "wallet": [
      {
        "currency": "BTC",
        "name": "Bitcoin",
        "available": "1.25000000",
        "frozen": "0.10000000",
        "unAvailable": "0.00000000",
        "available_usd_valuation": "83750.00"
      },
      {
        "currency": "USDT",
        "name": "Tether",
        "available": "50000.00000000",
        "frozen": "5000.00000000",
        "unAvailable": "0.00000000",
        "available_usd_valuation": "50000.00"
      }
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `currency` | Currency symbol |
| `name` | Currency full name |
| `available` | Available balance |
| `frozen` | Frozen balance (in open orders, etc.) |
| `unAvailable` | Unavailable balance |
| `available_usd_valuation` | USD valuation of available balance (only if `needUsdValuation=true`) |

---

## 11. Spot Wallet Balance

`GET /spot/v1/wallet`

**Auth:** KEYED | **Rate Limit:** 12 req/2sec per KEY

**Parameters:** None

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/wallet" \
  -H "X-BM-KEY: $BITMART_API_KEY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "wallet": [
      {
        "id": "BTC",
        "available": "1.25000000",
        "name": "Bitcoin",
        "frozen": "0.10000000"
      },
      {
        "id": "USDT",
        "available": "50000.00000000",
        "name": "Tether",
        "frozen": "5000.00000000"
      }
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `id` | Currency symbol |
| `available` | Available balance for trading |
| `name` | Currency full name |
| `frozen` | Balance locked in open orders |

---

## 12. Actual Trade Fee Rate

`GET /spot/v1/trade_fee`

**Auth:** KEYED | **Rate Limit:** 2 req/2sec per KEY

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/trade_fee?symbol=BTC_USDT" \
  -H "X-BM-KEY: $BITMART_API_KEY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "symbol": "BTC_USDT",
    "buy_taker_fee_rate": "0.0025",
    "sell_taker_fee_rate": "0.0025",
    "buy_maker_fee_rate": "0.0025",
    "sell_maker_fee_rate": "0.0025"
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `symbol` | Trading pair |
| `buy_taker_fee_rate` | Fee rate for buy taker orders |
| `sell_taker_fee_rate` | Fee rate for sell taker orders |
| `buy_maker_fee_rate` | Fee rate for buy maker orders |
| `sell_maker_fee_rate` | Fee rate for sell maker orders |

---

## 13. Base Fee Rate

`GET /spot/v1/user_fee`

**Auth:** KEYED | **Rate Limit:** 2 req/2sec per KEY

**Parameters:** None

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/user_fee" \
  -H "X-BM-KEY: $BITMART_API_KEY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "user_rate_type": 1,
    "level": "level_1",
    "taker_fee_rate_A": "0.0025",
    "maker_fee_rate_A": "0.0025",
    "taker_fee_rate_B": "0.0025",
    "maker_fee_rate_B": "0.0025",
    "taker_fee_rate_C": "0.0025",
    "maker_fee_rate_C": "0.0025",
    "taker_fee_rate_D": "0.0025",
    "maker_fee_rate_D": "0.0025"
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `user_rate_type` | User rate type identifier |
| `level` | User fee level |
| `taker_fee_rate_A` | Taker fee rate for class A pairs |
| `maker_fee_rate_A` | Maker fee rate for class A pairs |
| `taker_fee_rate_B` | Taker fee rate for class B pairs |
| `maker_fee_rate_B` | Maker fee rate for class B pairs |
| `taker_fee_rate_C` | Taker fee rate for class C pairs |
| `maker_fee_rate_C` | Maker fee rate for class C pairs |
| `taker_fee_rate_D` | Taker fee rate for class D pairs |
| `maker_fee_rate_D` | Maker fee rate for class D pairs |

---

## 14. Isolated Margin Account Details

`GET /spot/v1/margin/isolated/account`

**Auth:** KEYED | **Rate Limit:** 12 req/2sec per KEY

**SDK:** `GetMarginAccountDetailsIsolated(options)` with optional `symbol`

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | No | Trading pair. Omit to get all isolated margin assets |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/margin/isolated/account?symbol=BTC_USDT" \
  -H "X-BM-KEY: $BITMART_API_KEY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "symbols": [
      {
        "symbol": "BTC_USDT",
        "risk_rate": "999.00",
        "risk_level": "1",
        "buy_enabled": true,
        "sell_enabled": true,
        "liquidate_price": "0.00",
        "liquidate_rate": "1.15",
        "base": {
          "currency": "BTC",
          "borrow_enabled": true,
          "borrowed": "0.00000000",
          "available": "1.00000000",
          "frozen": "0.00000000",
          "net_asset": "1.00000000",
          "net_assetBTC": "1.00000000",
          "total_asset": "1.00000000",
          "borrow_unpaid": "0.00000000",
          "interest_unpaid": "0.00000000"
        },
        "quote": {
          "currency": "USDT",
          "borrow_enabled": true,
          "borrowed": "0.00000000",
          "available": "50000.00000000",
          "frozen": "0.00000000",
          "net_asset": "50000.00000000",
          "net_assetBTC": "0.74626866",
          "total_asset": "50000.00000000",
          "borrow_unpaid": "0.00000000",
          "interest_unpaid": "0.00000000"
        }
      }
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `symbol` | Trading pair |
| `risk_rate` | Current risk rate |
| `risk_level` | Risk level as numeric string: `"1"`=low, `"2"`=medium, `"3"`=high |
| `buy_enabled` | Whether buying is enabled |
| `sell_enabled` | Whether selling is enabled |
| `liquidate_price` | Estimated liquidation price |
| `liquidate_rate` | Liquidation rate threshold |
| `base.currency` | Base currency symbol |
| `base.borrow_enabled` | Whether borrowing is enabled for base |
| `base.borrowed` | Amount currently borrowed |
| `base.available` | Available balance |
| `base.frozen` | Frozen balance |
| `base.net_asset` | Net asset value |
| `base.net_assetBTC` | Net asset value in BTC |
| `base.total_asset` | Total asset value |
| `base.borrow_unpaid` | Outstanding borrowed amount |
| `base.interest_unpaid` | Outstanding interest |
| `quote.*` | Same fields as base, for quote currency |

---

## 15. Trading Pair Borrowing Rate & Amount

`GET /spot/v1/margin/isolated/pairs`

**Auth:** KEYED | **Rate Limit:** 2 req/2sec per KEY

**SDK:** `GetTradingPairBorrowingRateAndAmount(symbol)` with optional symbol

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | No | Trading pair. Omit to get all pairs |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/margin/isolated/pairs?symbol=BTC_USDT" \
  -H "X-BM-KEY: $BITMART_API_KEY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "symbols": [
      {
        "symbol": "BTC_USDT",
        "max_leverage": "5",
        "symbol_enabled": true,
        "base": {
          "currency": "BTC",
          "daily_interest": "0.00100000",
          "hourly_interest": "0.00004167",
          "max_borrow_amount": "100.00000000",
          "min_borrow_amount": "0.00100000",
          "borrowable_amount": "50.00000000"
        },
        "quote": {
          "currency": "USDT",
          "daily_interest": "0.00100000",
          "hourly_interest": "0.00004167",
          "max_borrow_amount": "1000000.00000000",
          "min_borrow_amount": "10.00000000",
          "borrowable_amount": "500000.00000000"
        }
      }
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `symbol` | Trading pair |
| `max_leverage` | Maximum leverage allowed |
| `symbol_enabled` | Whether margin trading is enabled for this pair |
| `base.currency` | Base currency symbol |
| `base.daily_interest` | Daily interest rate for borrowing |
| `base.hourly_interest` | Hourly interest rate for borrowing |
| `base.max_borrow_amount` | Maximum borrowable amount |
| `base.min_borrow_amount` | Minimum borrowable amount |
| `base.borrowable_amount` | Currently available amount to borrow |
| `quote.*` | Same fields as base, for quote currency |

---

## 16. Borrow Record (Isolated)

`GET /spot/v1/margin/isolated/borrow_record`

**Auth:** KEYED | **Rate Limit:** 150 req/2sec per KEY

**SDK:** `GetBorrowRecordIsolated(symbol, borrowId, startTime, endTime, N)`

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `borrow_id` | String | No | Filter by specific borrow ID |
| `start_time` | Long | No | Start time in milliseconds |
| `end_time` | Long | No | End time in milliseconds |
| `N` | Integer | No | Number of records, max 100, default 50 |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/margin/isolated/borrow_record?symbol=BTC_USDT&N=10" \
  -H "X-BM-KEY: $BITMART_API_KEY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "records": [
      {
        "borrow_id": "123456789",
        "symbol": "BTC_USDT",
        "currency": "USDT",
        "borrow_amount": "10000.00000000",
        "daily_interest": "0.00100000",
        "hourly_interest": "0.00004167",
        "interest_amount": "1.00000000",
        "create_time": 1700000000
      }
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `borrow_id` | Unique borrow record ID |
| `symbol` | Trading pair |
| `currency` | Borrowed currency |
| `borrow_amount` | Amount borrowed |
| `daily_interest` | Daily interest rate at time of borrowing |
| `hourly_interest` | Hourly interest rate at time of borrowing |
| `interest_amount` | Accrued interest amount |
| `create_time` | Borrow time in seconds |

---

## 17. Repayment Record (Isolated)

`GET /spot/v1/margin/isolated/repay_record`

**Auth:** KEYED | **Rate Limit:** 150 req/2sec per KEY

**SDK:** `GetRepaymentRecordIsolated(symbol, repayId, currency, startTime, endTime, N)`

**Parameters (query string):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `repay_id` | String | No | Filter by specific repay ID |
| `currency` | String | No | Filter by currency |
| `start_time` | Long | No | Start time in milliseconds |
| `end_time` | Long | No | End time in milliseconds |
| `N` | Integer | No | Number of records, max 100, default 50 |

**Example:**

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  "https://api-cloud.bitmart.com/spot/v1/margin/isolated/repay_record?symbol=BTC_USDT&N=10" \
  -H "X-BM-KEY: $BITMART_API_KEY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "records": [
      {
        "repay_id": "987654321",
        "symbol": "BTC_USDT",
        "currency": "USDT",
        "repaid_amount": "10001.00000000",
        "repaid_principal": "10000.00000000",
        "repaid_interest": "1.00000000",
        "repay_time": 1700086400
      }
    ]
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `repay_id` | Unique repayment record ID |
| `symbol` | Trading pair |
| `currency` | Repaid currency |
| `repaid_amount` | Total repayment amount (principal + interest) |
| `repaid_principal` | Principal amount repaid |
| `repaid_interest` | Interest amount repaid |
| `repay_time` | Repayment time in seconds |

---

# Spot Trading

## 18. Place Single Order

`POST /spot/v2/submit_order`

**Auth:** SIGNED | **Rate Limit:** 40 req/2sec per UID

> **Note on parameter naming:** This v2 endpoint uses `client_order_id` (snake_case) but `stpMode` (camelCase). This is a known inconsistency.

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `side` | String | Yes | `"buy"` or `"sell"` |
| `type` | String | Yes | `"limit"`, `"market"`, `"limit_maker"`, `"ioc"` |
| `client_order_id` | String | No | User-defined order ID (snake_case!) |
| `size` | String | Conditional | Order quantity in base currency. Required for `limit`, `limit_maker`, `ioc`, and `market` sell |
| `price` | String | Conditional | Order price. Required for `limit`, `limit_maker`, `ioc` |
| `notional` | String | Conditional | Order value in quote currency. Required for `market` buy orders |
| `stpMode` | String | No | Self-trade prevention mode (camelCase exception in v2) |

**Order type rules:**

| Type | `price` | `size` | `notional` |
|------|---------|--------|------------|
| `limit` | Required | Required | - |
| `market` buy | - | - | Required |
| `market` sell | - | Required | - |
| `limit_maker` | Required | Required | - |
| `ioc` | Required | Required | - |

**Example (limit buy):**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","side":"buy","type":"limit","price":"60000.00","size":"0.001"}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v2/submit_order" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Example (market buy — use `notional`, NOT `size`):**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","side":"buy","type":"market","notional":"50"}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v2/submit_order" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "order_id": "1234567890"
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `order_id` | Server-assigned order ID |

---

## 19. Place Margin Order

`POST /spot/v1/margin/submit_order`

**Auth:** SIGNED | **Rate Limit:** 20 req/1sec per UID

**SDK:** `PostMarginSubmitOrder(MarginOrder)` -- uses `clientOrderId` (camelCase, exception in v1)

> **Note on parameter naming:** This v1 endpoint uses `clientOrderId` (camelCase), which is an exception to the v1 snake_case convention.

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `side` | String | Yes | `"buy"` or `"sell"` |
| `type` | String | Yes | `"limit"`, `"market"`, `"limit_maker"`, `"ioc"` |
| `clientOrderId` | String | No | User-defined order ID (camelCase exception!) |
| `size` | String | Conditional | Order quantity in base currency |
| `price` | String | Conditional | Order price |
| `notional` | String | Conditional | Order value in quote currency. Required for `market` buy orders |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","side":"buy","type":"limit","price":"60000.00","size":"0.001","clientOrderId":"margin_order_001"}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v1/margin/submit_order" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "order_id": "1234567891"
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `order_id` | Server-assigned order ID |

---

## 20. Batch Place Orders

`POST /spot/v4/batch_orders`

**Auth:** SIGNED | **Rate Limit:** 40 req/2sec per UID

> **IMPORTANT:** The body format wraps orders inside an `orderParams` array with a top-level `symbol`. Individual orders do NOT repeat the `symbol` field.

**Top-level Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `orderParams` | Array | Yes | Array of order objects, max 10 |
| `recvWindow` | Long | No | Request timeout in ms, range 0-60000, default 5000 |

**Each order in `orderParams`:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `side` | String | Yes | `"buy"` or `"sell"` |
| `type` | String | Yes | `"limit"`, `"market"`, `"limit_maker"`, `"ioc"` |
| `clientOrderId` | String | No | User-defined order ID (camelCase, v4) |
| `size` | String | Conditional | Order quantity in base currency |
| `price` | String | Conditional | Order price |
| `notional` | String | Conditional | Order value in quote currency. Required for `market` buy orders |
| `stpMode` | String | No | Self-trade prevention mode |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","orderParams":[{"side":"buy","type":"limit","price":"60000.00","size":"0.001","clientOrderId":"batch_001"},{"side":"sell","type":"limit","price":"70000.00","size":"0.001","clientOrderId":"batch_002"}],"recvWindow":5000}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v4/batch_orders" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "code": 0,
    "msg": "success",
    "data": {
      "orderIds": ["1234567892", "1234567893"]
    }
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `data.code` | Batch result code (0 = success) |
| `data.msg` | Batch result message |
| `data.data.orderIds` | Array of created order ID strings |

---

## 21. Cancel Single Order

`POST /spot/v3/cancel_order`

**Auth:** SIGNED | **Rate Limit:** 40 req/2sec per UID

> **Note:** Supports cancellation by either `order_id` or `client_order_id`. They are mutually exclusive -- provide one or the other, not both. Both parameters use snake_case (v3 endpoint).

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `order_id` | String | Conditional | Server-assigned order ID (mutually exclusive with `client_order_id`) |
| `client_order_id` | String | Conditional | User-defined order ID (mutually exclusive with `order_id`) |

**Example (cancel by order_id):**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","order_id":"1234567890"}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v3/cancel_order" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Example (cancel by client_order_id):**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","client_order_id":"my_order_001"}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v3/cancel_order" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "result": true
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `data.result` | `true` if cancellation request accepted |

---

## 22. Cancel Multiple Orders

`POST /spot/v4/cancel_orders`

**Auth:** SIGNED | **Rate Limit:** 40 req/2sec per UID

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `orderIds` | Array[String] | Conditional | Server-assigned order IDs, max 10 (camelCase, v4). Mutually exclusive with `clientOrderIds` |
| `clientOrderIds` | Array[String] | Conditional | User-defined order IDs, max 10 (camelCase, v4). Mutually exclusive with `orderIds` |
| `recvWindow` | Long | No | Request timeout in ms, range 0-60000 |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","orderIds":["1234567890","1234567891","1234567892"]}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v4/cancel_orders" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "successIds": ["1234567890", "1234567891"],
    "failIds": ["1234567892"],
    "totalCount": 3,
    "successCount": 2,
    "failedCount": 1
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `successIds` | Array of successfully cancelled order IDs |
| `failIds` | Array of order IDs that failed to cancel |
| `totalCount` | Total number of orders in request |
| `successCount` | Number of successfully cancelled orders |
| `failedCount` | Number of orders that failed to cancel |

---

## 23. Cancel All Open Orders

`POST /spot/v4/cancel_all`

**Auth:** SIGNED | **Rate Limit:** 1 req/3sec per UID

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | No | Trading pair. Omit to cancel across all pairs |
| `side` | String | No | Cancel only orders on one side: `"buy"` or `"sell"`. Omit to cancel both sides |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","side":"buy"}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v4/cancel_all" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {}
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `data` | Empty object on success |

---

# Order Query

> **IMPORTANT:** All v4 query endpoints use the **POST** method, NOT GET. Parameters are sent as a JSON body. The signature includes the JSON body: `{timestamp}#{memo}#{body}`.

## 24. Query Order by Order ID

`POST /spot/v4/query/order`

**Auth:** SIGNED | **Rate Limit:** 50 req/2sec per KEY

> **Method is POST.** Parameters go in the JSON body, not the query string. Signature includes the body.

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `orderId` | String | Yes | Server-assigned order ID (camelCase, v4) |
| `queryState` | String | No | `"open"` for active orders, `"history"` for completed/cancelled. Default searches both |
| `recvWindow` | Long | No | Request timeout in ms, range 0-60000 |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"orderId":"1234567890","queryState":"open","recvWindow":5000}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v4/query/order" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "orderId": "1234567890",
    "clientOrderId": "my_order_001",
    "symbol": "BTC_USDT",
    "side": "buy",
    "orderMode": "spot",
    "type": "limit",
    "state": "new",
    "cancelSource": "",
    "stpMode": "",
    "price": "60000.00",
    "priceAvg": "0.00",
    "size": "0.00100000",
    "filledSize": "0.00000000",
    "notional": "60.00000000",
    "filledNotional": "0.00000000",
    "createTime": 1700000000000,
    "updateTime": 1700000000000
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `orderId` | Server-assigned order ID |
| `clientOrderId` | User-defined order ID (empty string if not set) |
| `symbol` | Trading pair |
| `side` | `"buy"` or `"sell"` |
| `orderMode` | `"spot"` or `"iso_margin"` |
| `type` | Order type: `"limit"`, `"market"`, `"limit_maker"`, `"ioc"` |
| `state` | Order state: `"new"`, `"partially_filled"`, `"filled"`, `"canceled"`, `"partially_canceled"` |
| `cancelSource` | Reason for cancellation (empty if not cancelled) |
| `stpMode` | Self-trade prevention mode |
| `price` | Order price |
| `priceAvg` | Average fill price (**NOT** `avgPrice`) |
| `size` | Order quantity |
| `filledSize` | Filled quantity |
| `notional` | Order value in quote currency |
| `filledNotional` | Filled value in quote currency |
| `createTime` | Order creation time in milliseconds |
| `updateTime` | Last update time in milliseconds |

---

## 25. Query Order by Client Order ID

`POST /spot/v4/query/client-order`

**Auth:** SIGNED | **Rate Limit:** 50 req/2sec per KEY

> **Method is POST.** Parameters go in the JSON body, not the query string. Signature includes the body.

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `clientOrderId` | String | Yes | User-defined order ID (camelCase, v4) |
| `queryState` | String | No | `"open"` for active orders, `"history"` for completed/cancelled |
| `recvWindow` | Long | No | Request timeout in ms, range 0-60000 |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"clientOrderId":"my_order_001","queryState":"open","recvWindow":5000}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v4/query/client-order" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

Same format as [endpoint 24](#24-query-order-by-order-id).

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "orderId": "1234567890",
    "clientOrderId": "my_order_001",
    "symbol": "BTC_USDT",
    "side": "buy",
    "orderMode": "spot",
    "type": "limit",
    "state": "new",
    "cancelSource": "",
    "stpMode": "",
    "price": "60000.00",
    "priceAvg": "0.00",
    "size": "0.00100000",
    "filledSize": "0.00000000",
    "notional": "60.00000000",
    "filledNotional": "0.00000000",
    "createTime": 1700000000000,
    "updateTime": 1700000000000
  }
}
```

---

## 26. All Open Orders

`POST /spot/v4/query/open-orders`

**Auth:** SIGNED | **Rate Limit:** 12 req/2sec per KEY

> **Method is POST.** Parameters go in the JSON body, not the query string. Signature includes the body.

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | No | Filter by trading pair |
| `orderMode` | String | No | `"spot"` or `"iso_margin"` |
| `startTime` | Long | No | Start time in milliseconds (camelCase, v4) |
| `endTime` | Long | No | End time in milliseconds (camelCase, v4) |
| `limit` | Integer | No | Number of results, range 1-200, default 200 |
| `recvWindow` | Long | No | Request timeout in ms, range 0-60000 |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","orderMode":"spot","limit":50,"recvWindow":5000}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v4/query/open-orders" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": [
    {
      "orderId": "1234567890",
      "clientOrderId": "my_order_001",
      "symbol": "BTC_USDT",
      "side": "buy",
      "orderMode": "spot",
      "type": "limit",
      "state": "new",
      "cancelSource": "",
      "stpMode": "",
      "price": "60000.00",
      "priceAvg": "0.00",
      "size": "0.00100000",
      "filledSize": "0.00000000",
      "notional": "60.00000000",
      "filledNotional": "0.00000000",
      "createTime": 1700000000000,
      "updateTime": 1700000000000
    }
  ]
}
```

**Response Fields:**

Array of order objects. Each order has the same fields as [endpoint 24](#24-query-order-by-order-id).

---

## 27. Historical Orders

`POST /spot/v4/query/history-orders`

**Auth:** SIGNED | **Rate Limit:** 12 req/2sec per KEY

> **Method is POST.** Parameters go in the JSON body, not the query string. Signature includes the body.

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | No | Filter by trading pair |
| `orderMode` | String | No | `"spot"` or `"iso_margin"` |
| `startTime` | Long | No | Start time in milliseconds (camelCase, v4) |
| `endTime` | Long | No | End time in milliseconds (camelCase, v4) |
| `limit` | Integer | No | Number of results, range 1-200, default 200 |
| `recvWindow` | Long | No | Request timeout in ms, range 0-60000 |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","orderMode":"spot","limit":50,"recvWindow":5000}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v4/query/history-orders" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": [
    {
      "orderId": "1234567880",
      "clientOrderId": "",
      "symbol": "BTC_USDT",
      "side": "sell",
      "orderMode": "spot",
      "type": "limit",
      "state": "filled",
      "cancelSource": "",
      "stpMode": "",
      "price": "67000.00",
      "priceAvg": "67000.00",
      "size": "0.00100000",
      "filledSize": "0.00100000",
      "notional": "67.00000000",
      "filledNotional": "67.00000000",
      "createTime": 1699990000000,
      "updateTime": 1699990001000
    }
  ]
}
```

**Response Fields:**

Array of order objects. Each order has the same fields as [endpoint 24](#24-query-order-by-order-id).

---

## 28. Account Trade History

`POST /spot/v4/query/trades`

**Auth:** SIGNED | **Rate Limit:** 12 req/2sec per KEY

> **Method is POST.** Parameters go in the JSON body, not the query string. Signature includes the body.

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | No | Filter by trading pair |
| `orderMode` | String | No | `"spot"` or `"iso_margin"` |
| `startTime` | Long | No | Start time in milliseconds (camelCase, v4) |
| `endTime` | Long | No | End time in milliseconds (camelCase, v4) |
| `limit` | Integer | No | Number of results, range 1-200, default 200 |
| `recvWindow` | Long | No | Request timeout in ms, range 0-60000 |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","orderMode":"spot","limit":20,"recvWindow":5000}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v4/query/trades" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": [
    {
      "tradeId": "9876543210",
      "orderId": "1234567880",
      "clientOrderId": "",
      "symbol": "BTC_USDT",
      "side": "sell",
      "orderMode": "spot",
      "type": "limit",
      "stpMode": "",
      "price": "67000.00",
      "size": "0.00100000",
      "notional": "67.00000000",
      "fee": "0.06700000",
      "feeCoinName": "USDT",
      "tradeRole": "taker",
      "createTime": 1699990001000,
      "updateTime": 1699990001000
    }
  ]
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `tradeId` | Unique trade ID |
| `orderId` | Server-assigned order ID |
| `clientOrderId` | User-defined order ID (empty string if not set) |
| `symbol` | Trading pair |
| `side` | `"buy"` or `"sell"` |
| `orderMode` | `"spot"` or `"iso_margin"` |
| `type` | Order type |
| `stpMode` | Self-trade prevention mode |
| `price` | Trade execution price |
| `size` | Trade size in base currency |
| `notional` | Trade value in quote currency |
| `fee` | Trading fee |
| `feeCoinName` | Currency of fee |
| `tradeRole` | `"taker"` or `"maker"` |
| `createTime` | Trade time in milliseconds |
| `updateTime` | Last update time in milliseconds |

---

## 29. Trades for Specific Order

`POST /spot/v4/query/order-trades`

**Auth:** SIGNED | **Rate Limit:** 12 req/2sec per KEY

> **Method is POST.** Parameters go in the JSON body, not the query string. Signature includes the body.

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `orderId` | String | Yes | Server-assigned order ID (camelCase, v4) |
| `recvWindow` | Long | No | Request timeout in ms, range 0-60000 |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"orderId":"1234567880","recvWindow":5000}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v4/query/order-trades" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

Same format as [endpoint 28](#28-account-trade-history).

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": [
    {
      "tradeId": "9876543210",
      "orderId": "1234567880",
      "clientOrderId": "",
      "symbol": "BTC_USDT",
      "side": "sell",
      "orderMode": "spot",
      "type": "limit",
      "stpMode": "",
      "price": "67000.00",
      "size": "0.00100000",
      "notional": "67.00000000",
      "fee": "0.06700000",
      "feeCoinName": "USDT",
      "tradeRole": "taker",
      "createTime": 1699990001000,
      "updateTime": 1699990001000
    }
  ]
}
```

---

# Margin Loan

## 30. Margin Borrow (Isolated)

`POST /spot/v1/margin/isolated/borrow`

**Auth:** SIGNED | **Rate Limit:** 2 req/2sec per KEY

**SDK:** `MarginBorrowIsolated(symbol, currency, amount)`

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `currency` | String | Yes | Currency to borrow, e.g., `USDT` |
| `amount` | String | Yes | Amount to borrow |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","currency":"USDT","amount":"10000"}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v1/margin/isolated/borrow" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "borrow_id": "123456789"
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `borrow_id` | Unique borrow record ID |

---

## 31. Margin Repay (Isolated)

`POST /spot/v1/margin/isolated/repay`

**Auth:** SIGNED | **Rate Limit:** 2 req/2sec per KEY

**SDK:** `MarginRepayIsolated(symbol, currency, amount)`

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `currency` | String | Yes | Currency to repay, e.g., `USDT` |
| `amount` | String | Yes | Amount to repay |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","currency":"USDT","amount":"10001"}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v1/margin/isolated/repay" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "repay_id": "987654321"
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `repay_id` | Unique repayment record ID |

---

## 32. Margin Asset Transfer

`POST /spot/v1/margin/isolated/transfer`

**Auth:** SIGNED | **Rate Limit:** 2 req/2sec per KEY

**SDK:** `MarginAssetTransfer(transfer MarginAssetTransfer)` with fields: symbol, currency, amount, side

**Parameters (JSON body):**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | String | Yes | Trading pair, e.g., `BTC_USDT` |
| `currency` | String | Yes | Currency to transfer, e.g., `USDT` |
| `amount` | String | Yes | Amount to transfer |
| `side` | String | Yes | `"in"` = spot to margin, `"out"` = margin to spot |

**Example:**

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTC_USDT","currency":"USDT","amount":"5000","side":"in"}'
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')

curl -s -X POST "https://api-cloud.bitmart.com/spot/v1/margin/isolated/transfer" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**

```json
{
  "code": 1000,
  "trace": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "success",
  "data": {
    "transfer_id": "456789123"
  }
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `transfer_id` | Unique transfer record ID |

---

# Quick Reference: Error Codes

Spot business error codes are endpoint/version specific. Do **not** assume the same numeric code has the same meaning across all spot flows. The table below is limited to authentication / transport issues and a small set of common current order-query errors that are useful across this guide. For margin borrow / repay / transfer errors, rely on the endpoint section and the official business-code table rather than a global mapping.

| Code | Meaning |
|------|---------|
| `1000` | Success |
| `30002` | Header X-BM-KEY not found (authentication) |
| `30005` | Header X-BM-SIGN is wrong (authentication) |
| `30006` | Header X-BM-TIMESTAMP is wrong / missing (authentication) |
| `30007` | Timestamp/recvWindow validation failed (authentication) |
| `30010` | IP is forbidden (authentication) |
| `30011` | API key expired (authentication) |
| `30012` | API key has no required permission (authentication) |
| `30013` | Request too many requests |
| `50000` | Bad Request |
| `50001` | Symbol not found |
| `50002` | From Or To format error |
| `50004` | Kline size over 500 |
| `50005` | Order Id not found / query returned no data |
| `50006` | Minimum size is %s |
| `50007` | Maximum size is %s |
| `50008` | Minimum price is %s |
| `50021` | Market buy No size required / param error |
| `51011` | Limit order quantity * price below minimum transaction amount |
| `51012` | Market buy amount below minimum transaction amount |
| `52000` | Unsupported OrderMode Type |

**Margin-only / endpoint-specific business-code examples (non-global):**

| Code | Meaning | Notes |
|------|---------|-------|
| `51003` | Account Limit | Use in margin borrow / repay / transfer context; do not use as a generic v4 order-query error |
| `51006` | Exceeds the amount to be repaid | Isolated margin repay context |
| `51007` | order_mode not found | Official business-code-table entry; current invalid `orderMode` requests on v4 query endpoints return `52000` instead |

---

# System Endpoints

## 33. Get System Time

`GET /system/time`

**Auth:** NONE | **Rate Limit:** 10 req/sec per IP

No parameters required.

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud.bitmart.com/system/time'
```

**Response:**
```json
{
  "code": 1000,
  "trace": "886fb6ae-456b-4654-b4e0-d681ac05cea1",
  "message": "OK",
  "data": {
    "server_time": 1527777538000
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| server_time | Long | Current server time (UTC milliseconds) |

---

## 34. Get System Service Status

`GET /system/service`

**Auth:** NONE | **Rate Limit:** 10 req/sec per IP

No parameters required.

```bash
curl -s -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud.bitmart.com/system/service'
```

**Response:**
```json
{
  "code": 1000,
  "trace": "886fb6ae-456b-4654-b4e0-d681ac05cea1",
  "message": "OK",
  "data": {
    "service": [
      {
        "title": "Spot API Stop",
        "service_type": "spot",
        "status": "2",
        "start_time": 1527777538000,
        "end_time": 1527777538000
      }
    ]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| title | String | Maintenance description title |
| service_type | String | `spot` / `contract` / `account` |
| status | Long | `0`=Waiting `1`=Working `2`=Completed |
| start_time | Long | Maintenance start time (UTC milliseconds) |
| end_time | Long | Maintenance end time (UTC milliseconds) |

---

# Quick Reference: Rate Limits Summary

| Category | Typical Limit | Per |
|----------|--------------|-----|
| Public market data | 10-15 req/2sec | IP |
| Account queries (KEYED) | 12 req/2sec | KEY |
| Trade fee / User fee | 2 req/2sec | KEY |
| Order placement/cancellation | 40 req/2sec | UID |
| Cancel all | 1 req/3sec | UID |
| Margin order placement | 20 req/1sec | UID |
| v4 single order query | 50 req/2sec | KEY |
| v4 list/history queries | 12 req/2sec | KEY |
| v4 order-trades | 12 req/2sec | KEY |
| Margin loan operations | 2 req/2sec | KEY |
| Borrow/repay records | 150 req/2sec | KEY |
| System time / service status | 10 req/sec | IP |
