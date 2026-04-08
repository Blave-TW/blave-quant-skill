# Hyperliquid API Reference

All endpoints are prefixed with `https://api.blave.org/hyperliquid/`. Auth headers required: `api-key`, `secret-key`.

---

## `GET /hyperliquid/leaderboard`

`sort_by` — default `accountValue`; pass any window key (`week`, `month`, `allTime`) to sort by PnL.

Returns top 100 traders:
- `ethAddress` — wallet address
- `accountValue` — USD account size
- `windowPerformances` — list of `[window, {pnl, roi, vlm}]` for day/week/month/allTime
- `displayName` — name if Blave-tracked, otherwise null

Cached 5 min.

---

## `GET /hyperliquid/traders`

No params. Returns Blave-curated dict:
```json
{
  "0xABC...": {
    "name": {"en": "Machi Big Brother", "zh": "麻吉大哥"},
    "description": {"en": "...", "zh": "..."}
  }
}
```

---

## `GET /hyperliquid/trader_position`

`address`✓ → `{perp, spot, abstraction, net_equity, trader_name, description}`

- `perp.assetPositions[].position` — `coin`, `szi` (size, negative = short), `entryPx`, `unrealizedPnl`, `token_id`
- `spot.balances` — spot token balances
- `net_equity` — total account value (USD)

Cached 15 s.

---

## `GET /hyperliquid/trader_history`

`address`✓ → list of fills:

| Field | Description |
|---|---|
| `coin` | Asset |
| `px` | Fill price |
| `sz` | Fill size |
| `dir` | `Open Long` / `Close Long` / `Open Short` / `Close Short` |
| `closedPnl` | Realized PnL (non-zero on close fills) |
| `time` | Unix timestamp (seconds) |
| `token_id` | Internal token identifier |

Cached 60 s.

---

## `GET /hyperliquid/trader_performance`

`address`✓ → `{chart: {timestamp: [...], pnl: [...]}}`

- `timestamp` — Unix seconds array
- `pnl` — cumulative PnL in USD (same index as timestamp)

Use `np.diff(pnl)` for daily returns. Cached 60 s.

---

## `GET /hyperliquid/trader_open_order`

`address`✓ → list of open orders:
- `coin`, `sz`, `px`, `side` (`B`=buy / `A`=ask), `token_id`, `oid`

Cached 60 s.

---

## `GET /hyperliquid/top_trader_position`

No params. Aggregates positions across top 100 leaderboard traders.

```json
{
  "long":  [{"coin": "BTC", "position": 12.5, ...}],
  "short": [{"coin": "ETH", "position": -200, ...}]
}
```

Cached 5 min.

---

## `GET /hyperliquid/top_trader_exposure_history`

`symbol`✓, `period`✓, `start_date`, `end_date` → `{data: {...}}`

Time series of net long/short exposure for the given symbol across top traders.

---

## `GET /hyperliquid/bucket_stats`

No params. Returns trader stats grouped by account size:

| Bucket | Range |
|---|---|
| `lt_100` | < $100 |
| `100_to_1k` | $100–$1K |
| `1k_to_10k` | $1K–$10K |
| `10k_to_100k` | $10K–$100K |
| `100k_to_1M` | $100K–$1M |
| `gt_1M` | > $1M |
| `top_traders` | Blave-curated list |

Each bucket: `{stats: {count, profit_ratio, loss_ratio}, positions: {long, short}, long_exposure, short_exposure, net_exposure}`

Returns `{"status": "warming_up"}` with HTTP 202 while cache is building — retry after a few seconds. Cached ~5 min.
