# Blave API Examples

Full Python examples for all Blave API endpoints.

## Setup

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

headers = {
    "api-key": os.getenv("blave_api_key"),
    "secret-key": os.getenv("blave_secret_key"),
}
BASE_URL = "https://api.blave.org"
```

---

## Price

```python
params = {"symbol": "BTCUSDT"}
response = requests.get(f"{BASE_URL}/price", headers=headers, params=params, timeout=60)
print(response.json())
# {"symbol": "BTCUSDT", "price": 95000.0, "change_24h": 2.5}
```

---

## Alpha Table

```python
response = requests.get(f"{BASE_URL}/alpha_table", headers=headers, timeout=60)
print(response.json())
```

---

## Kline

```python
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/kline", headers=headers, params=params, timeout=60)
raw = response.json()
# returns a list directly (NOT {"data": [...]}):
# [{"date": "2025-01-01 00:00:00", "open": 94000.0, "high": 95500.0, "low": 93200.0, "close": 95000.0, "volume": 1234.5}, ...]
data = raw if isinstance(raw, list) else raw.get("data", [])
```

---

## Market Direction

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/market_direction/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Market Sentiment

```python
# Get symbols
response = requests.get(f"{BASE_URL}/market_sentiment/get_symbols", headers=headers, timeout=60)

# Get alpha
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/market_sentiment/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Capital Shortage

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/capital_shortage/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Holder Concentration

```python
# Get symbols
response = requests.get(f"{BASE_URL}/holder_concentration/get_symbols", headers=headers, timeout=60)

# Get alpha
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/holder_concentration/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Taker Intensity

```python
# Get symbols
response = requests.get(f"{BASE_URL}/taker_intensity/get_symbols", headers=headers, timeout=60)

# Get alpha
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/taker_intensity/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Whale Hunter

```python
# Get symbols
response = requests.get(f"{BASE_URL}/whale_hunter/get_symbols", headers=headers, timeout=60)

# Get alpha
params = {"symbol": "BTCUSDT", "period": "1h", "timeframe": "24h", "score_type": "score_oi"}
response = requests.get(f"{BASE_URL}/whale_hunter/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Squeeze Momentum

```python
# Get symbols
response = requests.get(f"{BASE_URL}/squeeze_momentum/get_symbols", headers=headers, timeout=60)

# Get alpha (period fixed to 1d)
params = {"symbol": "BTCUSDT", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/squeeze_momentum/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Sector Rotation

```python
response = requests.get(f"{BASE_URL}/sector_rotation/get_history_data", headers=headers, timeout=60)
print(response.json())
```

---

## Blave Top Trader Exposure

```python
params = {"period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/blave_top_trader/get_exposure", headers=headers, params=params, timeout=60)
print(response.json())
```

---

## Taiwan Stock Daily Price

Raw unadjusted daily OHLCV. `start` / `end` are optional (omit for full history).

```python
params = {"start": "2020-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/price/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "2020-01-02", "stock_id": "2330", "open": 335.0, "high": 338.5,
#   "low": 334.0, "close": 337.0, "spread": 2.0,
#   "volume": 33282120, "turnover_value": 11224165450, "turnover_count": 17160}, ...]
```

---

## Taiwan Stock Daily Price — Forward Adjusted (向後調整)

Prices adjusted for cash and stock dividends using forward (後復權) method:
historical prices are unchanged; prices from each ex-dividend date onward are
multiplied by the cumulative adjustment factor. Suitable for backtesting total return.

```python
params = {"start": "2020-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/price_adj/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# Same schema as /price but close/open/high/low are dividend-adjusted.
# Adjusted prices will be higher than raw for recent periods (dividends compound forward).
```

**Stock ID examples:** `2330` (台積電), `0050` (元大台灣50), `2317` (鴻海), `006208` (富邦台50)

---

## Taiwan Stock Institutional Investors — 三大法人

Daily buy/sell shares by institutional investor type (wide format, one row per trading day).
`start` / `end` optional (omit for full history).

```python
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/institutional/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "2024-01-02", "stock_id": "2330",
#   "foreign_buy": 28464159, "foreign_sell": 47404324,
#   "trust_buy": 5553520,   "trust_sell": 269712,
#   "dealer_self_buy": 452000, "dealer_self_sell": 366190,
#   "dealer_hedge_buy": 942546, "dealer_hedge_sell": 780090,
#   "foreign_dealer_self_buy": 0, "foreign_dealer_self_sell": 0}, ...]
```

**Field meanings:**
| Field | Investor type |
|---|---|
| `foreign_*` | 外資 (Foreign Investor) — 最常被追蹤 |
| `trust_*` | 投信 (Investment Trust) |
| `dealer_self_*` | 自營商自行買賣 (Dealer self) |
| `dealer_hedge_*` | 自營商避險 (Dealer hedging) |
| `foreign_dealer_self_*` | 外資自營 (Foreign Dealer Self) — 多為 0 |

Net buy = `*_buy - *_sell`. Use for 籌碼面分析、外資進出追蹤、與股價走勢交叉比對。
Values are **shares** (股), not dollars.

---

## Taiwan Stock Margin Trading — 融資融券

Daily margin purchase and short sale data (one row per trading day).
`start` / `end` optional (omit for full history).

```python
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/margin/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "2024-01-02", "stock_id": "2330",
#   "margin_buy": 310,               # 融資買進
#   "margin_sell": 513,              # 融資賣出
#   "margin_balance": 12844,         # 融資餘額（當日）
#   "margin_prev_balance": 13057,    # 融資餘額（前日）
#   "margin_limit": 6483017,         # 融資限額
#   "margin_cash_repay": 10,         # 融資現金償還
#   "short_sell": 21,                # 融券賣出
#   "short_buy": 2,                  # 融券買進
#   "short_balance": 208,            # 融券餘額（當日）
#   "short_prev_balance": 189,       # 融券餘額（前日）
#   "short_limit": 6483017,          # 融券限額
#   "short_cash_repay": 0,           # 融券現金償還
#   "offset_loan_short": 1}, ...]    # 資券相抵
```

**Field meanings:**
| Field | 說明 |
|---|---|
| `margin_buy` | 融資買進 — shares purchased on margin today |
| `margin_sell` | 融資賣出 — margin shares sold today |
| `margin_balance` | 融資餘額 — today's outstanding margin balance (shares) |
| `margin_prev_balance` | 融資前日餘額 — yesterday's margin balance |
| `margin_limit` | 融資限額 — margin purchase ceiling |
| `margin_cash_repay` | 融資現金償還 — cash repayment of margin |
| `short_sell` | 融券賣出 — shares sold short today |
| `short_buy` | 融券買進 — short shares covered today |
| `short_balance` | 融券餘額 — today's outstanding short balance (shares) |
| `short_prev_balance` | 融券前日餘額 — yesterday's short balance |
| `short_limit` | 融券限額 — short sale ceiling |
| `short_cash_repay` | 融券現金償還 — cash repayment of short |
| `offset_loan_short` | 資券相抵 — shares offset between margin long and short |

**Common derived signals:**
```python
df["margin_net"] = df["margin_buy"] - df["margin_sell"]        # 融資淨增減
df["short_net"]  = df["short_sell"] - df["short_buy"]          # 融券淨增減
df["margin_util"] = df["margin_balance"] / df["margin_limit"]  # 融資使用率
```

Values are **shares** (股), not dollars. Data available from 1994-10-01.

---

## Taiwan Stock Shareholding Distribution — 股權持股分級表

Weekly shareholding distribution by bracket (one row per date × level).
`start` / `end` optional (omit for full history). Data updates every Friday.

```python
params = {"start": "2024-01-01", "end": "2024-03-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/shareholding/2330", headers=headers, params=params, timeout=60)
data = response.json()["data"]
# [{"date": "2024-01-05", "stock_id": "2330",
#   "level": "1-999",          "people": 732503,  "unit": 136261142,  "percent": 0.52},
#  {"date": "2024-01-05", "stock_id": "2330",
#   "level": "1,000-5,000",    "people": 371837,  "unit": 713353901,  "percent": 2.75},
#  {"date": "2024-01-05", "stock_id": "2330",
#   "level": "total",          "people": 1234567, "unit": 25932070992, "percent": 100.0}, ...]
```

**Field meanings:**
| Field | 說明 |
|---|---|
| `level` | 持股級距 — holding bracket (e.g. `"1-999"`, `"1,000-5,000"`, … `"more than 1,000,001"`, `"total"`) |
| `people` | 持股人數 — number of shareholders in this bracket |
| `unit` | 持股股數 — total shares held by this bracket |
| `percent` | 持股比例 (%) — percentage of total issued shares |

**All 17 levels (in data order):**
`1-999`, `1,000-5,000`, `5,001-10,000`, `10,001-15,000`, `15,001-20,000`, `20,001-30,000`,
`30,001-40,000`, `40,001-50,000`, `50,001-100,000`, `100,001-200,000`, `200,001-400,000`,
`400,001-600,000`, `600,001-800,000`, `800,001-1,000,000`, `more than 1,000,001`,
`total`, `差異數調整（說明4）`

**Common derived signals:**
```python
import pandas as pd
df = pd.DataFrame(data)

# 大股東集中度：持股 > 400,000 股的比例合計
large_holder_levels = ["400,001-600,000", "600,001-800,000", "800,001-1,000,000", "more than 1,000,001"]
df_large = df[df["level"].isin(large_holder_levels)].groupby("date")["percent"].sum().reset_index()
df_large.columns = ["date", "large_holder_pct"]

# 散戶比例：持股 1–999 股 (零股) 的人數趨勢
df_retail = df[df["level"] == "1-999"][["date", "people", "percent"]]
```

Use for 籌碼面分析 — tracking whether large holders are accumulating or distributing over time.

---

## alpha_table Field Reference

Each symbol in `/alpha_table` contains:

| Field | Description |
|---|---|
| `statistics` | `up_prob` (prob of 24h upward move), `exp_value` (expected return), `avg_up_return`, `avg_down_return`, `return_ratio`, `is_data_sufficient` |
| `price` | `{"-": 70000}` — current price |
| `price_change` | `{"15min": ..., "1h": ..., "24h": ...}` — % change |
| `market_cap` | `{"-": 1234567890}` — USD market cap |
| `market_cap_percentile` | `{"-": 85.3}` — percentile among all listed coins |
| `funding_rate` | `{"binance": -0.01, ...}` — per exchange |
| `oi_imbalance` | `{"-": 0.12}` — OI imbalance |

`fields` = indicator metadata. `note` = color ranges. `""` = insufficient data.

Use `statistics.up_prob` and `statistics.exp_value` for screening. Always check `is_data_sufficient` before using `statistics`.
