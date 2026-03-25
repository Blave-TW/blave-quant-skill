# BitMart Futures API Reference

> Complete reference for all 53 futures endpoints. See [SKILL.md](../SKILL.md) for authentication, routing, and quickstart.

> **Credentials:** Read from `.env` — `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`.

> **IMPORTANT:** Always include `X-BM-BROKER-ID: BlaveData666666` on **every** request (NONE / KEYED / SIGNED). This is required for broker fee tracking.

---

## Market Data Endpoints (NONE auth)

### 1. Contract Details

`GET /contract/public/details`

**Rate Limit:** 12 req/2sec per IP

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | No | Contract symbol, e.g. `BTCUSDT`. Omit for all contracts |

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/details?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": {
    "symbols": [{
      "symbol": "BTCUSDT",
      "product_type": 1,
      "open_timestamp": 1594080000000,
      "expire_timestamp": 0,
      "settle_timestamp": 0,
      "base_currency": "BTC",
      "quote_currency": "USDT",
      "last_price": "67123.4",
      "volume_24h": "123456789",
      "turnover_24h": "8234567890.12",
      "index_price": "67120.5",
      "index_name": "BTCUSDT",
      "contract_size": "0.001",
      "min_leverage": "1",
      "max_leverage": "100",
      "price_precision": "0.1",
      "vol_precision": "1",
      "max_volume": "1000000",
      "market_max_volume": "50000",
      "min_volume": "1",
      "funding_rate": "0.0001",
      "expected_funding_rate": "0.0001",
      "open_interest": "12345678",
      "open_interest_value": "823456789.12",
      "high_24h": "68000.0",
      "low_24h": "66500.0",
      "change_24h": "0.015",
      "funding_interval_hours": 8,
      "funding_time": 1773158400000,
      "status": "Trading",
      "delist_time": 0
    }]
  }
}
```

| Field | Description |
|-------|-------------|
| symbol | Contract symbol |
| product_type | 1 = perpetual, 2 = futures |
| open_timestamp | Contract listing timestamp (ms) |
| expire_timestamp | Expiry timestamp (0 for perpetual) |
| base_currency | Base currency (e.g. BTC) |
| quote_currency | Quote currency (e.g. USDT) |
| last_price | Last trade price |
| volume_24h | 24h volume in contracts |
| turnover_24h | 24h turnover in quote currency |
| index_price | Current index price |
| contract_size | Size of one contract in base currency |
| min_leverage / max_leverage | Leverage range |
| price_precision | Minimum price tick |
| vol_precision | Minimum volume tick |
| max_volume | Maximum order volume |
| market_max_volume | Maximum market order volume |
| min_volume | Minimum order volume |
| funding_rate | Current funding rate |
| expected_funding_rate | Next expected funding rate |
| open_interest | Total open interest (contracts) |
| open_interest_value | Total open interest (quote currency) |
| high_24h / low_24h | 24h high / low |
| change_24h | 24h price change ratio |
| funding_interval_hours | Funding interval in hours |
| funding_time | Next funding settlement timestamp (ms) |
| status | Contract status: `"Trading"` or `"Delisted"` |

**Live verification (2026-03-13):** `GET /contract/public/details` returns both `vol_precision` and `funding_time` in JSON data. Official field-table text that says `volume_precision` is inconsistent with live payload.

**Important:** Always check `contract_size`, `min_volume`, `max_volume`, `price_precision`, and `max_leverage` before placing orders.

---

### 2. Order Book Depth

`GET /contract/public/depth`

**Rate Limit:** 12 req/2sec per IP

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/depth?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": {
    "asks": [["67125.0", "150", "150"], ["67130.0", "320", "470"]],
    "bids": [["67120.0", "200", "200"], ["67115.0", "180", "380"]],
    "symbol": "BTCUSDT",
    "timestamp": 1709971200000
  }
}
```

| Field | Description |
|-------|-------------|
| asks | Ask levels `[price, volume, cumulative_volume]`, sorted ascending |
| bids | Bid levels `[price, volume, cumulative_volume]`, sorted descending |
| symbol | Contract symbol |
| timestamp | Timestamp (ms) |

---

### 3. Recent Market Trades

`GET /contract/public/market-trade`

**Rate Limit:** 12 req/2sec per IP

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |
| limit | Long | No | Number of trades, default 50, max 100 |

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/market-trade?symbol=BTCUSDT&limit=5'
```

**Response:**
```json
{
  "code": 1000,
  "message": "Ok",
  "data": [
    {
      "symbol": "BTCUSDT",
      "price": "67123.4",
      "qty": "1.506",
      "quote_qty": "101127.7404",
      "time": 1709971200,
      "is_buyer_maker": false
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| symbol | Contract symbol |
| price | Trade price |
| qty | Trade quantity |
| quote_qty | Quote currency amount (`price * qty`) |
| time | Trade timestamp (seconds) |
| is_buyer_maker | `true` if buyer is maker, `false` if taker |

---

### 4. Current Funding Rate

`GET /contract/public/funding-rate`

**Rate Limit:** 12 req/2sec per IP

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/funding-rate?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": {
    "symbol": "BTCUSDT",
    "rate_value": "0.0001",
    "expected_rate": "0.00012",
    "funding_time": 1709971200000,
    "funding_upper_limit": "0.003",
    "funding_lower_limit": "-0.003",
    "timestamp": 1709971200000
  }
}
```

| Field | Description |
|-------|-------------|
| symbol | Contract symbol |
| rate_value | Current funding rate |
| expected_rate | Next expected funding rate |
| funding_time | Next funding settlement time (ms) |
| funding_upper_limit | Funding rate upper limit |
| funding_lower_limit | Funding rate lower limit |
| timestamp | Timestamp (ms) |

---

### 5. Funding Rate History

`GET /contract/public/funding-rate-history`

**Rate Limit:** 12 req/2sec per IP

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |
| limit | String | No | Records per page, default 100, max 100 |

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/funding-rate-history?symbol=BTCUSDT&limit=5'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": {
    "list": [{
      "symbol": "BTCUSDT",
      "funding_rate": "0.0001",
      "funding_time": 1709971200000
    }]
  }
}
```

| Field | Description |
|-------|-------------|
| symbol | Contract symbol |
| funding_rate | Funding rate at settlement |
| funding_time | Settlement timestamp (ms) |

---

### 6. K-Line / Candlestick

`GET /contract/public/kline`

**Rate Limit:** 12 req/2sec per IP | **Max Records:** 500 per request

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |
| step | Long | No | Interval in minutes: 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 4320, 10080 (default 1) |
| start_time | Long | Yes | Start timestamp in **seconds** |
| end_time | Long | Yes | End timestamp in **seconds** |

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/kline?symbol=BTCUSDT&step=60&start_time=1709942400&end_time=1709971200'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": [{
    "timestamp": 1709971200,
    "open_price": "67100.0",
    "high_price": "67200.0",
    "low_price": "67050.0",
    "close_price": "67123.4",
    "volume": "12345"
  }]
}
```

| Field | Description |
|-------|-------------|
| timestamp | Candle open time in seconds |
| open_price | Open price |
| high_price | High price |
| low_price | Low price |
| close_price | Close price |
| volume | Volume in contracts |

---

### 7. Mark Price K-Line

`GET /contract/public/markprice-kline`

**Rate Limit:** 12 req/2sec per IP | **Max Records:** 500 per request

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |
| step | Long | No | Interval in minutes (same values as kline) |
| start_time | Long | Yes | Start timestamp in **seconds** |
| end_time | Long | Yes | End timestamp in **seconds** |

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/markprice-kline?symbol=BTCUSDT&step=60&start_time=1709942400&end_time=1709971200'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": [{
    "timestamp": 1709971200,
    "open_price": "67098.5",
    "high_price": "67198.0",
    "low_price": "67048.2",
    "close_price": "67120.5",
    "volume": "0"
  }]
}
```

| Field | Description |
|-------|-------------|
| timestamp | Candle open time in seconds |
| open_price | Mark price open |
| high_price | Mark price high |
| low_price | Mark price low |
| close_price | Mark price close |
| volume | Volume (typically 0 for mark price klines) |

---

### 8. Open Interest

`GET /contract/public/open-interest`

**Rate Limit:** 2 req/2sec per IP

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/open-interest?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": {
    "symbol": "BTCUSDT",
    "open_interest": "12345678",
    "open_interest_value": "823456789.12",
    "timestamp": 1709971200000
  }
}
```

| Field | Description |
|-------|-------------|
| symbol | Contract symbol |
| open_interest | Total open interest (contracts) |
| open_interest_value | Total open interest (quote currency) |
| timestamp | Timestamp (ms) |

---

### 9. Leverage Brackets / Risk Limits

`GET /contract/public/leverage-bracket`

**Rate Limit:** 12 req/2sec per IP

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | No | Contract symbol, e.g. `BTCUSDT`. Omit for all |

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/public/leverage-bracket?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": {
    "rules": [{
      "symbol": "BTCUSDT",
      "brackets": [{
        "bracket": 1,
        "initial_leverage": 100,
        "notional_cap": "500000",
        "notional_floor": "0",
        "maint_margin_ratio": "0.004",
        "cum": "0"
      }]
    }]
  }
}
```

| Field | Description |
|-------|-------------|
| symbol | Contract symbol |
| bracket | Bracket tier number |
| initial_leverage | Maximum leverage at this tier |
| notional_cap | Upper bound of notional value |
| notional_floor | Lower bound of notional value |
| maint_margin_ratio | Maintenance margin rate |
| cum | Cumulative value |

**Important:** Higher position sizes require lower leverage. Check brackets before setting leverage to avoid rejection.

---

## Account Endpoints (KEYED auth)

### 10. Futures Account Balance

`GET /contract/private/assets-detail`

**Rate Limit:** 12 req/2sec per KEY

**Parameters:** None

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/assets-detail'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": [{
    "currency": "USDT",
    "available_balance": "50000.00",
    "frozen_balance": "5000.00",
    "position_deposit": "10000.00",
    "equity": "65000.00",
    "unrealized": "0.00"
  }]
}
```

| Field | Description |
|-------|-------------|
| currency | Currency symbol |
| available_balance | Available balance for trading |
| frozen_balance | Frozen balance (in open orders) |
| position_deposit | Margin used by positions |
| equity | Total equity (balance + unrealized PnL) |
| unrealized | Unrealized profit/loss |

---

### 11. Trade Fee Rate

`GET /contract/private/trade-fee-rate`

**Rate Limit:** 2 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/trade-fee-rate?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": {
    "symbol": "BTCUSDT",
    "taker_fee_rate": "0.0006",
    "maker_fee_rate": "0.0002"
  }
}
```

---

### 12. Current Positions

`GET /contract/private/position`

**Rate Limit:** 6 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | No | Contract symbol. Omit for all positions |
| account | String | No | `"futures"` (default) or `"copy_trading"` |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/position?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": [{
    "symbol": "BTCUSDT",
    "leverage": "10",
    "timestamp": 1709971200000,
    "current_fee": "12.50",
    "open_timestamp": 1709942400000,
    "current_value": "6712.34",
    "mark_price": "67123.4",
    "mark_value": "6712.34",
    "position_value": "6700.00",
    "position_cross": "100",
    "maintenance_margin": "26.80",
    "margin_type": "Cross",
    "position_mode": "hedge_mode",
    "close_vol": "0",
    "close_avg_price": "0",
    "open_avg_price": "67000.0",
    "entry_price": "67000.0",
    "current_amount": "100",
    "unrealized_value": "12.34",
    "realized_value": "0",
    "position_type": 1,
    "account": "futures"
  }]
}
```

| Field | Description |
|-------|-------------|
| symbol | Contract symbol |
| leverage | Current leverage |
| mark_price | Current mark price |
| position_value | Position value in quote currency |
| entry_price | Average entry price |
| current_amount | Position size (contracts) |
| unrealized_value | Unrealized PnL |
| realized_value | Realized PnL |
| position_type | 1 = long, 2 = short |
| margin_type | `"Cross"` or `"Isolated"` |
| position_mode | `"hedge_mode"` or `"one_way_mode"` |
| current_fee | Accumulated fees |
| close_vol | Closed volume |
| close_avg_price | Average close price |
| current_value | Current value based on mark price |
| maintenance_margin | Maintenance margin |
| account | Account type |

---

### 13. Positions V2 (Extended Info)

`GET /contract/private/position-v2`

**Rate Limit:** 6 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | No | Contract symbol. Without symbol returns only positions with holdings; with symbol returns all positions |
| account | String | No | `"futures"` (default) or `"copy_trading"` |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/position-v2?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": [{
    "symbol": "BTCUSDT",
    "leverage": "10",
    "position_amount": "100",
    "position_side": "long",
    "entry_price": "67000.0",
    "mark_price": "67123.4",
    "liquidation_price": "60500.0",
    "unrealized_pnl": "12.34",
    "initial_margin": "670.00",
    "maintenance_margin": "26.80",
    "position_value": "6712.34",
    "open_type": "cross",
    "max_notional_value": "500000",
    "timestamp": 1709971200000,
    "current_fee": "12.50",
    "open_timestamp": 1709942400000,
    "current_value": "6712.34",
    "close_vol": "0",
    "close_avg_price": "0",
    "open_avg_price": "67000.0",
    "current_amount": "100",
    "realized_value": "0",
    "mark_value": "6712.34",
    "account": "futures"
  }]
}
```

| Field | Description |
|-------|-------------|
| position_side | `"both"`, `"long"`, or `"short"` |
| liquidation_price | Estimated liquidation price |
| unrealized_pnl | Unrealized profit/loss |
| initial_margin | Initial margin used |
| maintenance_margin | Maintenance margin required |
| current_amount | Current position size (contracts, string, always ≥ 0). **Use this field to determine whether a position exists** (parse as number, check ≠ 0) |
| position_amount | Current position direction amount (hedge mode: always positive; one-way mode: positive=long, negative=short) |
| open_type | `"cross"` or `"isolated"` |
| max_notional_value | Maximum notional value for current leverage |
| *(other fields same as endpoint 12)* | |

---

### 14. Position Risk

`GET /contract/private/position-risk`

**Rate Limit:** 24 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | No | Contract symbol. Omit for all positions |
| account | String | No | `"futures"` (default) or `"copy_trading"` |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/position-risk?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": [{
    "symbol": "BTCUSDT",
    "position_amt": "100",
    "mark_price": "67123.4",
    "unrealized_profit": "12.34",
    "liquidation_price": "60500.0",
    "leverage": "10",
    "max_notional_value": "500000",
    "margin_type": "cross",
    "isolated_margin": "0",
    "position_side": "Long",
    "notional": "6712.34",
    "update_time": 1709971200000,
    "account": "futures"
  }]
}
```

| Field | Description |
|-------|-------------|
| position_amt | Position size |
| mark_price | Current mark price |
| unrealized_profit | Unrealized PnL |
| liquidation_price | Estimated liquidation price |
| leverage | Current leverage |
| max_notional_value | Max notional value |
| margin_type | `"cross"` or `"isolated"` |
| isolated_margin | Isolated margin amount |
| position_side | `"Long"` or `"Short"` |
| notional | Position notional value |

---

### 15. Get Position Mode

`GET /contract/private/get-position-mode`

**Rate Limit:** 2 req/2sec per KEY

**Parameters:** None

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/get-position-mode'
```

**Live verification (2026-03-13):** KEYED request (only `X-BM-KEY`) and SIGNED request both returned `code=1000`. Use KEYED as the minimum required auth level.

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": {
    "position_mode": "hedge_mode"
  }
}
```

---

### 16. Transaction History

`GET /contract/private/transaction-history`

**Rate Limit:** 6 req/2sec per KEY | **Default Range:** Last 7 days

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | No | Contract symbol |
| flow_type | Int | No | 0=All, 1=Transfer, 2=Realized PNL, 3=Funding Fee, 4=Commission, 5=Liquidation |
| account | String | No | `"futures"` (default) or `"copy_trading"` |
| start_time | Long | No | Start timestamp in **milliseconds** |
| end_time | Long | No | End timestamp in **milliseconds** |
| page_size | Int | No | Page size, 1-1000, default 100 |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/transaction-history?symbol=BTCUSDT&flow_type=2&page_size=10'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": [{
    "symbol": "BTCUSDT",
    "flow_type": 2,
    "type": "Realized PNL",
    "amount": "12.34",
    "asset": "USDT",
    "account": "futures",
    "time": 1709971200000,
    "tran_id": "123456789"
  }]
}
```

| Field | Description |
|-------|-------------|
| symbol | Contract symbol |
| flow_type | Numeric transaction type code: 0=All, 1=Transfer, 2=Realized PNL, 3=Funding Fee, 4=Commission, 5=Liquidation |
| type | Transaction type: Transfer, Realized PNL, Funding Fee, Commission Fee, Liquidation Clearance |
| amount | Transaction amount (negative = outflow) |
| asset | Currency |
| account | Account type |
| time | Transaction timestamp (ms) |
| tran_id | Transaction ID |

---

## Trading Endpoints (SIGNED auth)

### 17. Place Order

`POST /contract/private/submit-order`

**Rate Limit:** 24 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |
| side | Int | Yes | 1=buy_open_long, 2=buy_close_short, 3=sell_close_long, 4=sell_open_short |
| type | String | No | `"limit"` (default) or `"market"` |
| price | String | Conditional | Order price. **Required for `type=limit`; do NOT send for `type=market`** (ignored and causes confusion) |
| size | Int | Yes | Order quantity (number of contracts, integer) |
| leverage | String | Conditional | Leverage multiplier (e.g. `"10"`). **Required for opening positions (side=1 or 4)**; ignored for closing (side=2 or 3). If an open position already exists, you MUST use the existing position's leverage (see Step 1.5). |
| open_type | String | Conditional | `"cross"` or `"isolated"`. **Required for opening positions (side=1 or 4)**; ignored for closing (side=2 or 3). If an open position already exists, you MUST use the existing position's `open_type`. |
| mode | Int | No | 1=GTC (default), 2=FOK, 3=IOC, 4=Maker Only. **`mode=4` (Maker Only) is NOT valid with `type=market`** — use only with `type=limit`. |
| client_order_id | String | No | Client-defined order ID (1-32 chars, alphanumeric) |
| stp_mode | Int | No | Self-trade prevention: 1=Cancel Maker (default), 2=Cancel Taker, 3=Cancel Both |
| preset_take_profit_price_type | Int | No | 1=Last Price (default), 2=Mark Price. **Only applies to opening orders (side=1 or 4).** |
| preset_stop_loss_price_type | Int | No | 1=Last Price (default), 2=Mark Price. **Only applies to opening orders (side=1 or 4).** |
| preset_take_profit_price | String | No | Inline preset TP price on this order. **Only applies to opening orders (side=1 or 4).** For TP/SL on an existing position, use `submit-tp-sl-order` instead. |
| preset_stop_loss_price | String | No | Inline preset SL price on this order. **Only applies to opening orders (side=1 or 4).** For TP/SL on an existing position, use `submit-tp-sl-order` instead. |

**Example — Market open long:**
```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","side":1,"type":"market","size":1,"leverage":"10","open_type":"cross"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Example — Limit open short with preset TP/SL:**
```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","side":4,"type":"limit","price":"70000","size":10,"leverage":"20","open_type":"isolated","mode":1,"preset_take_profit_price":"68000","preset_stop_loss_price":"72000","preset_take_profit_price_type":1,"preset_stop_loss_price_type":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
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
  "message": "OK",
  "data": {
    "order_id": 23456789012345678,
    "price": "70000"
  }
}
```

---

### 18. Cancel Order

`POST /contract/private/cancel-order`

**Rate Limit:** 40 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol, e.g. `BTCUSDT` |
| order_id | String | No | Order ID (provide order_id or client_order_id) |
| client_order_id | String | No | Client order ID (provide order_id or client_order_id) |

**Note:** If neither `order_id` nor `client_order_id` is provided, cancels all orders for the symbol.

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":"23456789012345678"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/cancel-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:** `{ "code": 1000, "data": {} }`

---

### 19. Batch Cancel Orders

`POST /contract/private/cancel-orders`

**Rate Limit:** 2 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol. Cancels all open orders for this symbol |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/cancel-orders' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:** `{ "code": 1000, "data": {} }`

---

### 20. Modify Limit Order

`POST /contract/private/modify-limit-order`

**Rate Limit:** 24 req/2sec per UID

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| order_id | Int | Conditional | Order ID (required if no client_order_id) |
| client_order_id | String | Conditional | Client order ID (required if no order_id) |
| price | String | No | New price (at least one of price/size required) |
| size | Int | No | New size (at least one of price/size required) |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":23456789012345678,"price":"66500"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/modify-limit-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "order_id": 23456789012345678, "client_order_id": "" } }
```

---

### 21. Cancel All After (Timed Cancel)

`POST /contract/private/cancel-all-after`

**Rate Limit:** 4 req/2sec per UID

Sets a countdown timer. When the timer expires, all open orders for the specified symbol are canceled. Useful as a dead-man switch.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| timeout | Int | Yes | Timeout in seconds (minimum 5, set to 0 to disable) |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","timeout":60}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/cancel-all-after' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "result": true, "set_time": 1709971200, "cancel_time": 1709971260 } }
```

---

### 22. Set Leverage

`POST /contract/private/submit-leverage`

**Rate Limit:** 24 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| leverage | String | No | Leverage multiplier (e.g. `"10"`) |
| open_type | String | Yes | `"cross"` or `"isolated"` |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","leverage":"20","open_type":"cross"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-leverage' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "symbol": "BTCUSDT", "leverage": "20", "open_type": "cross", "max_value": "500000" } }
```

**Important:** You cannot change leverage while there is an open position with a different margin type.

---

### 23. Set Position Mode

`POST /contract/private/set-position-mode`

**Rate Limit:** 2 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| position_mode | String | Yes | `"hedge_mode"` or `"one_way_mode"` |

**Note:** No `symbol` parameter — this applies globally to the account.

```bash
TIMESTAMP=$(date +%s000)
BODY='{"position_mode":"hedge_mode"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/set-position-mode' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "position_mode": "hedge_mode" } }
```

**Important:** You cannot change position mode while you have open positions. Close all positions first.

---

### 24. Spot-Futures Transfer

`POST /account/v1/transfer-contract`

**Rate Limit:** 1 req/2sec per KEY

> **Note:** Although the path prefix is `/account/v1/`, this endpoint uses the **futures Base URL** (`https://api-cloud-v2.bitmart.com`), not the spot Base URL.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| currency | String | Yes | Currency symbol (currently USDT only) |
| amount | String | Yes | Transfer amount [0.01-10000000000] |
| type | String | Yes | `"spot_to_contract"` or `"contract_to_spot"` |
| recvWindow | Long | No | Valid duration (0-60000]ms, default 5000 |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"currency":"USDT","amount":"1000","type":"spot_to_contract"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/account/v1/transfer-contract' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "currency": "USDT", "amount": "1000" } }
```

---

## Plan Order Endpoints (SIGNED auth)

### 25. Submit Plan Order (Conditional/Trigger)

`POST /contract/private/submit-plan-order`

**Rate Limit:** 24 req/2sec per UID

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| side | Int | Yes | 1=buy_open_long, 2=buy_close_short, 3=sell_close_long, 4=sell_open_short |
| type | String | No | `"limit"` (default), `"market"`, `"take_profit"`, `"stop_loss"` |
| leverage | String | Yes | Leverage multiplier |
| open_type | String | Yes | `"cross"` or `"isolated"` |
| mode | Int | No | 1=GTC (default), 2=FOK, 3=IOC, 4=Maker Only |
| size | Int | Yes | Order quantity (contracts) |
| trigger_price | String | Yes | Price that triggers the order |
| executive_price | String | Conditional | Execution price (required when type=limit) |
| price_way | Int | Yes | 1=Bullish (trigger when price rises above), 2=Bearish (trigger when price drops below) |
| price_type | Int | Yes | 1=Last Price, 2=Mark Price |
| plan_category | Int | No | 1=TP/SL, 2=Position TP/SL |
| preset_take_profit_price_type | Int | No | 1=Last Price (default), 2=Mark Price |
| preset_stop_loss_price_type | Int | No | 1=Last Price (default), 2=Mark Price |
| preset_take_profit_price | String | No | Preset TP price |
| preset_stop_loss_price | String | No | Preset SL price |

**Example — Trigger buy long when price drops to 65000:**
```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","side":1,"type":"market","size":10,"leverage":"10","open_type":"cross","trigger_price":"65000","price_way":2,"price_type":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-plan-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "order_id": 34567890123456789 } }
```

---

### 26. Cancel Plan Order

`POST /contract/private/cancel-plan-order`

**Rate Limit:** 40 req/2sec per UID

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| order_id | String | Conditional | Order ID (required if no client_order_id) |
| client_order_id | String | Conditional | Client order ID (required if no order_id) |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":"34567890123456789"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/cancel-plan-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:** `{ "code": 1000, "data": {} }`

---

### 27. Modify Plan Order

`POST /contract/private/modify-plan-order`

**Rate Limit:** 24 req/2sec per UID

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| order_id | String | No | Plan order ID |
| type | String | Yes | `"limit"` or `"market"` |
| trigger_price | String | Yes | New trigger price |
| executive_price | String | Conditional | New execution price (required when type=limit) |
| price_type | Int | Yes | 1=Last Price, 2=Mark Price |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":"34567890123456789","type":"market","trigger_price":"64000","price_type":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/modify-plan-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "order_id": "34567890123456789" } }
```

---

## TP/SL Endpoints (SIGNED auth)

### 28. Submit TP/SL Order

`POST /contract/private/submit-tp-sl-order`

**Rate Limit:** 24 req/2sec per UID

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| type | String | Yes | `"take_profit"` or `"stop_loss"` |
| side | Int | Yes | 2=Close Short, 3=Close Long (hedge mode); 2=Reduce Buy, 3=Reduce Sell (one-way) |
| trigger_price | String | Yes | Trigger/activation price |
| executive_price | String | Yes | Execution price |
| price_type | Int | Yes | 1=Last Price, 2=Mark Price |
| size | Int | No | Order quantity (default: full position size) |
| plan_category | Int | No | 1=TP/SL, 2=Position TP/SL (default) |
| client_order_id | String | No | Custom ID (1-32 chars) |
| category | String | No | `"limit"` or `"market"` (default market for full position) |

**Example — Set TP for a long position:**
```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","type":"take_profit","side":3,"trigger_price":"72000","executive_price":"71900","price_type":1,"plan_category":2}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-tp-sl-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Example — Set SL for a short position:**
```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","type":"stop_loss","side":2,"trigger_price":"72000","executive_price":"72100","price_type":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-tp-sl-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "order_id": "45678901234567890", "client_order_id": "" } }
```

**TP/SL Logic:**
- **Long position TP**: type=take_profit, side=3, trigger_price > entry_price
- **Long position SL**: type=stop_loss, side=3, trigger_price < entry_price
- **Short position TP**: type=take_profit, side=2, trigger_price < entry_price
- **Short position SL**: type=stop_loss, side=2, trigger_price > entry_price

---

### 29. Modify TP/SL Order

`POST /contract/private/modify-tp-sl-order`

**Rate Limit:** 24 req/2sec per UID

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| order_id | String | Conditional | Order ID (required if no client_order_id) |
| client_order_id | String | Conditional | Client order ID |
| trigger_price | String | Yes | New trigger price |
| executive_price | String | No | New execution price (required when plan_category=1) |
| price_type | Int | Yes | 1=Last Price, 2=Mark Price |
| plan_category | Int | No | 1=TP/SL, 2=Position TP/SL |
| category | String | No | `"limit"` or `"market"` |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":"45678901234567890","trigger_price":"73000","price_type":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/modify-tp-sl-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "order_id": "45678901234567890" } }
```

---

### 30. Modify Preset Plan Order (Preset TP/SL on Order)

`POST /contract/private/modify-preset-plan-order`

**Rate Limit:** 24 req/2sec per UID

Modify the preset take-profit/stop-loss attached to an existing order.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| order_id | String | Yes | Order ID |
| preset_take_profit_price_type | Int | No | 1=Last Price (default), 2=Mark Price |
| preset_stop_loss_price_type | Int | No | 1=Last Price (default), 2=Mark Price |
| preset_take_profit_price | String | No | New preset TP price |
| preset_stop_loss_price | String | No | New preset SL price |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":"23456789012345678","preset_take_profit_price":"73000","preset_stop_loss_price":"64000","preset_take_profit_price_type":1,"preset_stop_loss_price_type":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/modify-preset-plan-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "order_id": "23456789012345678" } }
```

---

## Trailing Order Endpoints (SIGNED auth)

### 31. Submit Trailing Stop Order

`POST /contract/private/submit-trail-order`

**Rate Limit:** 24 req/2sec per UID

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| side | Int | Yes | 1=buy_open_long, 2=buy_close_short, 3=sell_close_long, 4=sell_open_short |
| leverage | String | Yes | Leverage multiplier |
| open_type | String | Yes | `"cross"` or `"isolated"` |
| size | Int | Yes | Order quantity (contracts) |
| activation_price | String | Yes | Price that activates trailing behavior |
| callback_rate | String | Yes | Callback rate as percentage (0.1-5, where 1=1%) |
| activation_price_type | Int | Yes | 1=Last Price, 2=Mark Price |

**Example — Trailing stop to close long at 2% pullback from 72000:**
```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","side":3,"leverage":"10","open_type":"cross","size":10,"activation_price":"72000","callback_rate":"2","activation_price_type":1}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/submit-trail-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "data": { "order_id": 56789012345678901 } }
```

**How trailing stops work:**
1. When the market price reaches `activation_price`, the trailing stop activates.
2. It tracks the highest price (for sell/close long) or lowest price (for buy/close short).
3. If the price reverses by `callback_rate` percent from the tracked extreme, a market order is placed.

---

### 32. Cancel Trailing Stop Order

`POST /contract/private/cancel-trail-order`

**Rate Limit:** 24 req/2sec per UID

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| order_id | String | No | Trailing order ID |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"symbol":"BTCUSDT","order_id":"56789012345678901"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/contract/private/cancel-trail-order' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:** `{ "code": 1000, "data": {} }`

---

## Order Query Endpoints (KEYED auth)

### 33. Query Order by ID

`GET /contract/private/order`

**Rate Limit:** 50 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| order_id | String | Yes | Order ID |
| account | String | No | `"futures"` or `"copy_trading"` |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/order?symbol=BTCUSDT&order_id=23456789012345678'
```

**Response:**
```json
{
  "code": 1000,
  "data": {
    "order_id": "23456789012345678",
    "client_order_id": "",
    "symbol": "BTCUSDT",
    "side": 1,
    "type": "market",
    "leverage": "10",
    "open_type": "cross",
    "size": "1",
    "price": "0",
    "deal_avg_price": "67123.4",
    "deal_size": "1",
    "state": 4,
    "create_time": 1709971200000,
    "update_time": 1709971200500,
    "position_mode": "hedge_mode",
    "account": "futures",
    "activation_price": "",
    "callback_rate": "",
    "activation_price_type": 0,
    "preset_take_profit_price_type": 0,
    "preset_stop_loss_price_type": 0,
    "preset_take_profit_price": "",
    "preset_stop_loss_price": ""
  }
}
```

| Field | Description |
|-------|-------------|
| order_id | BitMart-assigned order ID |
| client_order_id | Client-defined order ID |
| symbol | Contract symbol |
| side | Order side (1-4) |
| type | limit, market, liquidate, bankruptcy, adl |
| leverage | Leverage used |
| open_type | `"cross"` or `"isolated"` |
| size | Order size (contracts) |
| price | Order price (0 for market) |
| deal_avg_price | Average fill price |
| deal_size | Filled size |
| state | 1=Approving, 2=Pending, 4=Closed |
| create_time | Creation timestamp (ms) |
| update_time | Last update timestamp (ms) |
| position_mode | hedge_mode / one_way_mode |
| account | Account type |
| preset_take_profit_price | Preset TP price |
| preset_stop_loss_price | Preset SL price |

---

### 34. Order History

`GET /contract/private/order-history`

**Rate Limit:** 6 req/2sec per KEY | **Default Range:** Last 7 days | **Max Range:** 90 days | **Max Records:** 200

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | Yes | Contract symbol |
| order_id | String | No | Filter by order ID |
| client_order_id | String | No | Filter by client order ID |
| account | String | No | `"futures"` or `"copy_trading"` |
| start_time | Long | No | Start timestamp in **seconds** |
| end_time | Long | No | End timestamp in **seconds** |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/order-history?symbol=BTCUSDT'
```

**Response:** Array of order objects with the same fields as endpoint 33.

**Additional fields in order history:**

| Field | Description |
|-------|-------------|
| `trigger_price` | Trigger price (for plan/conditional orders) |
| `execution_price` | Execution price (for triggered orders) |
| `executive_order_id` | ID of the order created when plan order triggers |

---

### 35. All Open Orders

`GET /contract/private/get-open-orders`

**Rate Limit:** 50 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | No | Contract symbol. Omit for all symbols |
| type | String | No | Filter: `"limit"`, `"market"`, `"trailing"` (default all) |
| order_state | String | No | `"all"` (default) or `"partially_filled"` |
| limit | Int | No | Max results, max 100, default 100 |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/get-open-orders?symbol=BTCUSDT&limit=50'
```

**Response:** Array of order objects with the same fields as endpoint 33.

---

### 36. Active Plan Orders

`GET /contract/private/current-plan-order`

**Rate Limit:** 50 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | No | Contract symbol. Omit for all symbols |
| type | String | No | Filter: `"limit"` or `"market"` (default all) |
| limit | Int | No | Max results, max 100, default 100 |
| plan_type | String | No | `"plan"` (conditional), `"profit_loss"` (TP/SL) (default all) |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/current-plan-order?symbol=BTCUSDT&limit=50'
```

**Response:**
```json
{
  "code": 1000,
  "data": [{
    "order_id": "34567890123456789",
    "client_order_id": "",
    "symbol": "BTCUSDT",
    "side": 1,
    "type": "market",
    "leverage": "10",
    "open_type": "cross",
    "size": "10",
    "executive_price": "0",
    "trigger_price": "65000",
    "price_way": 2,
    "price_type": 1,
    "plan_category": 1,
    "state": "active",
    "mode": 1,
    "position_mode": "hedge_mode",
    "create_time": 1709971200000,
    "update_time": 1709971200000,
    "preset_take_profit_price_type": 0,
    "preset_stop_loss_price_type": 0,
    "preset_take_profit_price": "",
    "preset_stop_loss_price": ""
  }]
}
```

| Field | Description |
|-------|-------------|
| executive_price | Execution price (0 for market) |
| trigger_price | Trigger price |
| price_way | 1=Bullish, 2=Bearish |
| price_type | 1=Last Price, 2=Mark Price |
| plan_category | 1=TP/SL, 2=Position TP/SL |
| mode | 1=GTC, 2=FOK, 3=IOC, 4=Maker Only |
| *(other fields same as endpoint 33)* | |

---

### 37. Trade / Fill History

`GET /contract/private/trades`

**Rate Limit:** 6 req/2sec per KEY | **Default Range:** Last 7 days | **Max Range:** 90 days | **Max Records:** 200

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | String | No | Contract symbol (optional) |
| account | String | No | `"futures"` or `"copy_trading"` |
| start_time | Long | No | Start timestamp in **seconds** |
| end_time | Long | No | End timestamp in **seconds** |
| order_id | Long | No | Filter by order ID |
| client_order_id | String | No | Filter by client order ID |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/trades?symbol=BTCUSDT'
```

**Response:**
```json
{
  "code": 1000,
  "data": [{
    "order_id": "23456789012345678",
    "trade_id": "98765432101234568",
    "symbol": "BTCUSDT",
    "side": 1,
    "price": "67123.4",
    "vol": "1",
    "exec_type": "Taker",
    "profit": false,
    "realised_profit": "0",
    "paid_fees": "0.04027",
    "account": "futures",
    "create_time": 1709971200500
  }]
}
```

| Field | Description |
|-------|-------------|
| order_id | Associated order ID |
| trade_id | Unique trade ID |
| symbol | Contract symbol |
| side | Trade side (1-4) |
| price | Fill price |
| vol | Fill volume (contracts) |
| exec_type | `"Taker"` or `"Maker"` |
| profit | Whether this trade has profit (Boolean) |
| realised_profit | Realized profit |
| paid_fees | Fees paid |
| account | Account type |
| create_time | Trade timestamp (ms) |

---

### 38. Transfer Records

`POST /account/v1/transfer-contract-list`

**Rate Limit:** 1 req/2sec per KEY | **Auth:** SIGNED

> **Note:** Although the path prefix is `/account/v1/`, this endpoint uses the **futures Base URL** (`https://api-cloud-v2.bitmart.com`), not the spot Base URL.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| currency | String | No | Currency (e.g. USDT) |
| time_start | Long | No | Start time in milliseconds |
| time_end | Long | No | End time in milliseconds |
| page | Int | Yes | Page number [1-1000] |
| limit | Int | Yes | Records per page [10-100] |
| recvWindow | Long | No | Valid duration (0-60000]ms, default 5000 |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"page":1,"limit":20}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/account/v1/transfer-contract-list' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
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
  "data": {
    "records": [{
      "transfer_id": "123456",
      "currency": "USDT",
      "amount": "1000",
      "type": "spot_to_contract",
      "state": "FINISHED",
      "timestamp": 1709971200000
    }]
  }
}
```

| Field | Description |
|-------|-------------|
| transfer_id | Transfer ID |
| currency | Currency |
| amount | Transfer amount |
| type | `"spot_to_contract"` or `"contract_to_spot"` |
| state | `"PROCESSING"`, `"FINISHED"`, `"FAILED"` |
| timestamp | Transfer timestamp (ms) |

---

## Sub-Account Endpoints (SIGNED / KEYED auth)

> Institutional verification required for all sub-account features.

### 39. Sub-Account to Main-Account Transfer (from Main Account)

`POST /account/contract/sub-account/main/v1/sub-to-main`

**Rate Limit:** 8 req/2sec per KEY | **Auth:** SIGNED

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| requestNo | String | Yes | UUID, unique request identifier (max 64 chars) |
| subAccount | String | Yes | Sub-account username |
| amount | String | Yes | Transfer amount |
| currency | String | Yes | Currency code (currently only `USDT` supported) |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"requestNo":"550e8400-e29b-41d4-a716-446655440000","subAccount":"mysubuser","amount":"100","currency":"USDT"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/account/contract/sub-account/main/v1/sub-to-main' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "message": "OK", "data": {} }
```

---

### 40. Main-Account to Sub-Account Transfer (from Main Account)

`POST /account/contract/sub-account/main/v1/main-to-sub`

**Rate Limit:** 8 req/2sec per KEY | **Auth:** SIGNED

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| requestNo | String | Yes | UUID, unique request identifier (max 64 chars) |
| subAccount | String | Yes | Sub-account username |
| amount | String | Yes | Transfer amount |
| currency | String | Yes | Currency code (currently only `USDT` supported) |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"requestNo":"550e8400-e29b-41d4-a716-446655440001","subAccount":"mysubuser","amount":"100","currency":"USDT"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/account/contract/sub-account/main/v1/main-to-sub' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "message": "OK", "data": {} }
```

---

### 41. Sub-Account to Main-Account Transfer (from Sub Account)

`POST /account/contract/sub-account/sub/v1/sub-to-main`

**Rate Limit:** 8 req/2sec per KEY | **Auth:** SIGNED

> **Note:** This endpoint must be called using the **sub-account's own API key**. The sub-account is inferred from the auth credentials — no `subAccount` parameter needed.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| requestNo | String | Yes | UUID, unique request identifier (max 64 chars) |
| amount | String | Yes | Transfer amount |
| currency | String | Yes | Currency code (currently only `USDT` supported) |

```bash
TIMESTAMP=$(date +%s000)
BODY='{"requestNo":"550e8400-e29b-41d4-a716-446655440002","amount":"100","currency":"USDT"}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud-v2.bitmart.com/account/contract/sub-account/sub/v1/sub-to-main' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY"
```

**Response:**
```json
{ "code": 1000, "message": "OK", "data": {} }
```

---

### 42. Get Sub-Account Futures Wallet Balance (from Main Account)

`GET /account/contract/sub-account/main/v1/wallet`

**Rate Limit:** 12 req/2sec per KEY | **Auth:** KEYED

> Returns only assets with balance greater than 0.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| subAccount | String | Yes | Sub-account username |
| currency | String | No | Currency filter (e.g. `USDT`) |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/account/contract/sub-account/main/v1/wallet?subAccount=mysubuser'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": {
    "wallet": [{
      "currency": "USDT",
      "name": "Tether",
      "available": "400.00",
      "frozen": "100.00"
    }]
  }
}
```

| Field | Description |
|-------|-------------|
| data.wallet[] | Wallet item array |
| currency | Token symbol (e.g. `USDT`) |
| name | Token name (e.g. `Tether`) |
| available | Available balance |
| frozen | Frozen balance |

---

### 43. Get Sub-Account Transfer History (from Main Account)

`GET /account/contract/sub-account/main/v1/transfer-list`

**Rate Limit:** 8 req/2sec per KEY | **Auth:** KEYED

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| subAccount | String | Yes | Sub-account username |
| limit | Int | Yes | Number of recent records [1-100] |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/account/contract/sub-account/main/v1/transfer-list?subAccount=mysubuser&limit=20'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": [{
    "fromAccount": "main",
    "fromWalletType": "future",
    "toAccount": "mysubuser",
    "toWalletType": "future",
    "currency": "USDT",
    "amount": "100",
    "submissionTime": 1709971200
  }]
}
```

| Field | Description |
|-------|-------------|
| fromAccount | Transfer-out account username |
| fromWalletType | Transfer-out wallet type (`future`) |
| toAccount | Transfer-in account username |
| toWalletType | Transfer-in wallet type (`future`) |
| currency | Currency symbol |
| amount | Transfer amount |
| submissionTime | Request timestamp in seconds (UTC) |

---

### 44. Get Account Futures Asset Transfer History (Main/Sub)

`GET /account/contract/sub-account/v1/transfer-history`

**Rate Limit:** 8 req/2sec per KEY | **Auth:** KEYED

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| limit | Int | Yes | Number of recent records [1-100] |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/account/contract/sub-account/v1/transfer-history?limit=20'
```

**Response:**
```json
{
  "code": 1000,
  "message": "OK",
  "data": [{
    "fromAccount": "main",
    "fromWalletType": "future",
    "toAccount": "mysubuser",
    "toWalletType": "future",
    "currency": "USDT",
    "amount": "100",
    "submissionTime": 1709971200
  }]
}
```

| Field | Description |
|-------|-------------|
| fromAccount | Transfer-out account username |
| fromWalletType | Transfer-out wallet type (`future`) |
| toAccount | Transfer-in account username |
| toWalletType | Transfer-in wallet type (`future`) |
| currency | Currency symbol |
| amount | Transfer amount |
| submissionTime | Request timestamp in seconds (UTC) |

---

## Affiliate Endpoints (KEYED auth)

> All affiliate endpoints use **KEYED** authentication with rate limit of **24 req/2sec**. Timestamps in parameters are in **seconds** (not milliseconds). Maximum time range for endpoints 47, 48, 50 is **60 days**.

### 45. Get Futures Rebate List

`GET /contract/private/affiliate/rebate-list`

**Rate Limit:** 24 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| page | Int | Yes | Page number |
| size | Int | Yes | Records per page |
| currency | String | Yes | Currency to query (e.g. `USDT`) |
| user_id | Long | No | User ID filter |
| rebate_start_time | Long | No | Rebate start timestamp (seconds) |
| rebate_end_time | Long | No | Rebate end timestamp (seconds) |
| register_start_time | Long | No | Registration start timestamp (seconds) |
| register_end_time | Long | No | Registration end timestamp (seconds) |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/affiliate/rebate-list?page=1&size=10&currency=USDT'
```

**Response:**
```json
{
  "code": "1000",
  "message": "OK",
  "data": {
    "total": 0,
    "page": 1,
    "size": 10,
    "btc_rebate_sum": 0,
    "usdt_rebate_sum": 0,
    "eth_rebate_sum": 0,
    "rebate_detail_page_data": []
  }
}
```

| Field | Description |
|-------|-------------|
| total | Total count |
| btc_rebate_sum / usdt_rebate_sum / eth_rebate_sum | Total rebate per currency |
| rebate_detail_page_data | Array of rebate records |
| ↳ rebate_coin | Currency |
| ↳ trade_user_id | Trading user ID |
| ↳ total_rebate_amount | Total commission |
| ↳ user_type | 0=Indirect, 1=Direct |

---

### 46. Get Futures Trade List

`GET /contract/private/affiliate/trade-list`

**Rate Limit:** 24 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | Long | Yes | User ID |
| type | Int | Yes | Query type: 1=U-based, 2=Coin-based |
| page | Int | Yes | Page number |
| size | Int | Yes | Records per page |
| start_time | Long | No | Start timestamp (seconds) |
| end_time | Long | No | End timestamp (seconds) |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/affiliate/trade-list?user_id=123456&type=1&page=1&size=10'
```

**Response:**
```json
{
  "code": "1000",
  "message": "OK",
  "data": {
    "total": 0,
    "page": 1,
    "size": 10,
    "list": [{
      "user_id": 10048829,
      "user_type": 1,
      "create_time": 1689933471000,
      "symbol": "BTCUSDT",
      "leverage": 20,
      "open_type": 2,
      "way": 1,
      "category": 2,
      "select_copy_trade": 1,
      "deal_price": 29771.9,
      "deal_vol": 32,
      "fee": 0.57162048,
      "realised_profit": 0
    }]
  }
}
```

| Field | Description |
|-------|-------------|
| list[].user_id | User ID |
| list[].user_type | User type (direct/indirect) |
| list[].create_time | Creation timestamp |
| list[].symbol | Trading symbol |
| list[].leverage | Leverage |
| list[].open_type | Position type: `1`=Isolated, `2`=Cross |
| list[].way | Order direction: `1`=Long, `2`=Close Short, `3`=Close Long, `4`=Short |
| list[].category | Order type: `1`=Limit, `2`=Market |
| list[].select_copy_trade | Type: `1`=Copy Trading, `2`=Non-Copy Trading |
| list[].deal_price | Average deal price |
| list[].deal_vol | Deal volume |
| list[].fee | Fee |
| list[].realised_profit | Realized PnL |

---

### 47. Get Single User Rebate Data

`GET /contract/private/affiliate/rebate-user`

**Rate Limit:** 24 req/2sec per KEY | **Max Range:** 60 days

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| cid | Long | Yes | User CID to query |
| start_time | Long | Yes | Start timestamp (seconds) |
| end_time | Long | Yes | End timestamp (seconds) |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/affiliate/rebate-user?cid=123456&start_time=1706745600&end_time=1709251200'
```

**Response:**
```json
{
  "code": "1000",
  "message": "OK",
  "data": {
    "cid": 123456,
    "back_rate": "0.3",
    "trading_vol_total": "10000",
    "trading_fee_total": "6.0",
    "rebate_total": "1.8",
    "trading_vol": "10000",
    "trading_fee": "6.0",
    "rebate": "1.8"
  }
}
```

| Field | Description |
|-------|-------------|
| cid | User CID |
| back_rate | Rebate rate |
| trading_vol_total | Total trading volume |
| trading_fee_total | Total trading fee |
| rebate_total | Total rebate |
| trading_vol / trading_fee / rebate | Period-specific values |

---

### 48. Get Single API User Rebate Data

`GET /contract/private/affiliate/rebate-api`

**Rate Limit:** 24 req/2sec per KEY | **Max Range:** 60 days

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| cid | Long | Yes | User CID to query |
| start_time | Long | Yes | Start timestamp (seconds) |
| end_time | Long | Yes | End timestamp (seconds) |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/affiliate/rebate-api?cid=123456&start_time=1706745600&end_time=1709251200'
```

**Response:**
```json
{
  "code": "1000",
  "message": "OK",
  "data": {
    "api_trading_fee_total": "6.0",
    "api_rebate_total": "1.8"
  }
}
```

| Field | Description |
|-------|-------------|
| api_trading_fee_total | API trading fee rebate |
| api_rebate_total | API rebate amount |

---

### 49. Check If Invited User

`GET /contract/private/affiliate/invite-check`

**Rate Limit:** 24 req/2sec per KEY

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| cid | Long | Yes | User CID to query |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/affiliate/invite-check?cid=123456'
```

**Response:**
```json
{
  "code": "1000",
  "message": "OK",
  "data": {
    "isInviteUser": true
  }
}
```

| Field | Description |
|-------|-------------|
| isInviteUser | `true` = invited user, `false` = not invited |

---

### 50. Get Invited Customer List

`GET /contract/private/affiliate/rebate-inviteUser`

**Rate Limit:** 24 req/2sec per KEY | **Max Range:** 60 days

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| start_time | Long | Yes | Start timestamp (seconds) |
| end_time | Long | Yes | End timestamp (seconds) |
| page | Int | Yes | Page number |
| size | Int | Yes | Records per page (max 50) |
| cid | Long | No | User CID filter |

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud-v2.bitmart.com/contract/private/affiliate/rebate-inviteUser?start_time=1706745600&end_time=1709251200&page=1&size=10'
```

**Response:**
```json
{
  "code": "1000",
  "message": "OK",
  "data": {
    "total": 0,
    "page": 1,
    "size": 10,
    "list": []
  }
}
```

| Field | Description |
|-------|-------------|
| total | Total records |
| list[].cid | User CID |
| list[].rebateTotal | Cumulative rebate (USDT) |
| list[].tradingVolTotal | Cumulative trading volume (USDT) |
| list[].cashbackRate | Cashback percentage |
| list[].tradingFeeTotal | Total trading fees (USDT) |
| list[].backRate | Rebate rate |
| list[].status | 1=Rebate issued, 0=Not issued |

---

## Simulated Trading Endpoint (SIGNED auth)

### 51. Demo Account Claim (Demo Only)

`POST /contract/private/claim`

**Auth:** SIGNED

> **IMPORTANT:** This endpoint only works with the demo base URL: `https://demo-api-cloud-v2.bitmart.com`
> It resets/refreshes simulated account balance for continued testing.

| Component | URL |
|-----------|-----|
| Demo REST API | `https://demo-api-cloud-v2.bitmart.com` |
| Demo WebSocket Public | `wss://openapi-wsdemo-v2.bitmart.com/api?protocol=1.1` |
| Demo WebSocket Private | `wss://openapi-wsdemo-v2.bitmart.com/user?protocol=1.1` |

```bash
TIMESTAMP=$(date +%s000)
BODY='{}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://demo-api-cloud-v2.bitmart.com/contract/private/claim' \
  -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
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
  "message": "OK",
  "data": {
    "currency": "USDT",
    "amount": "10"
  }
}
```

| Field | Description |
|-------|-------------|
| currency | Claimed asset currency |
| amount | Claimed amount |

> All standard futures endpoints work identically in the demo environment. Just use the demo base URL instead of the production URL.

---

# System Endpoints

## 52. Get System Time

`GET /system/time`

**Auth:** NONE | **Rate Limit:** 10 req/sec per IP

No parameters required.

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
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

## 53. Get System Service Status

`GET /system/service`

**Auth:** NONE | **Rate Limit:** 10 req/sec per IP

No parameters required.

```bash
curl -s -H "User-Agent: bitmart-skills/futures/v2026.3.23" \
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
        "title": "Contract API Stop",
        "service_type": "contract",
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
