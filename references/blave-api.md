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

## Funding Rate

```python
# Binance only. alpha = funding rate × 100 (percent); positive = longs pay shorts.
params = {"symbol": "BTCUSDT", "period": "1h", "start_date": "2025-01-01", "end_date": "2025-03-01"}
response = requests.get(f"{BASE_URL}/funding_rate/get_alpha", headers=headers, params=params, timeout=60)
print(response.json())
# → {"data": {"timestamp": [1735689600.0, ...], "alpha": [0.01, ...], "close": [93000.0, ...], "stat": {...}}}
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

## Taiwan Stock Financial Statements — 季報基本面

Quarterly fundamental data. All three endpoints share the same **long format** response (one row per financial item per quarter). `start` / `end` optional (default: 2013-01-01 to today). Redis-cached for 24 h.

| Statement | Path |
|---|---|
| 綜合損益表 Comprehensive Income | `/studio/market/twstock/financials/<stock_id>` |
| 資產負債表 Balance Sheet | `/studio/market/twstock/balance_sheet/<stock_id>` |
| 現金流量表 Cash Flow | `/studio/market/twstock/cashflow/<stock_id>` |

```python
params = {"start": "2022-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/financials/2330", headers=headers, params=params, timeout=30)
data = response.json()["data"]
# [{"date": "2022-03-31", "stock_id": "2330", "type": "Revenue",     "value": 491075000000.0, "origin_name": "營業收入"},
#  {"date": "2022-03-31", "stock_id": "2330", "type": "GrossProfit", "value": 258033000000.0, "origin_name": "毛利（損）"},
#  {"date": "2022-03-31", "stock_id": "2330", "type": "NetIncome",   "value": 202730000000.0, "origin_name": "本期淨利（淨損）"},
#  {"date": "2022-03-31", "stock_id": "2330", "type": "EPS",         "value": 7.82,           "origin_name": "每股盈餘（基本）"}, ...]
```

**Response fields:**
| Field | Description |
|---|---|
| `date` | Quarter-end date (`YYYY-MM-DD`): Q1=03-31, Q2=06-30, Q3=09-30, Q4=12-31 |
| `type` | Financial item code (English) |
| `value` | Numeric value in TWD; balance sheet items with `_per` suffix are % of total assets |
| `origin_name` | Chinese label — use this to identify unfamiliar `type` codes |

**Key `type` codes — `/financials` (損益表):**
| `type` | 中文 |
|---|---|
| `Revenue` | 營業收入 |
| `GrossProfit` | 毛利（損） |
| `OperatingIncome` | 營業利益（損失） |
| `NetIncome` | 本期淨利（淨損） |
| `EPS` | 每股盈餘（基本） |
| `TAX` | 所得稅費用（利益） |
| `OtherComprehensiveIncome` | 其他綜合損益（淨額） |

**Key `type` codes — `/balance_sheet` (資產負債表):**
| `type` | 中文 |
|---|---|
| `CashAndCashEquivalents` | 現金及約當現金 |
| `TotalAssets` | 資產總計 |
| `TotalLiabilities` | 負債總計 |
| `TotalEquity` | 權益總計 |
| `CashAndCashEquivalents_per` | 現金及約當現金（佔資產 %） |

**Key `type` codes — `/cashflow` (現金流量表):**
| `type` | 中文 |
|---|---|
| `OperatingActivities` | 營業活動之淨現金流入（出） |
| `InvestingActivities` | 投資活動之淨現金流入（出） |
| `FinancingActivities` | 籌資活動之淨現金流入（出） |
| `CashBalancesEndOfPeriod` | 期末現金及約當現金餘額 |
| `PropertyAndPlantAndEquipment` | 取得不動產、廠房及設備 |

**Pivot long → wide for analysis:**
```python
import pandas as pd
df = pd.DataFrame(data)
wide = df.pivot_table(index="date", columns="type", values="value", aggfunc="first")
# wide["NetIncome"]  → quarterly net income series
# wide["EPS"]        → quarterly EPS series
```

---

## Taiwan Stock Monthly Revenue — 月營收

Monthly revenue data. One row per stock per month. `start` / `end` optional (default: 2000-01-01 to today). Redis-cached for 24 h.

```python
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(f"{BASE_URL}/studio/market/twstock/monthly_revenue/2330", headers=headers, params=params, timeout=30)
data = response.json()["data"]
# [{"date": "2024-02-10", "stock_id": "2330", "country": "台灣", "revenue": 215274000, "revenue_month": 1, "revenue_year": 2024},
#  {"date": "2024-03-08", "stock_id": "2330", "country": "台灣", "revenue": 195348000, "revenue_month": 2, "revenue_year": 2024}, ...]
```

**Response fields:**
| Field | Description |
|---|---|
| `date` | 月份起始日 (`YYYY-MM-01`) — e.g. `2024-02-01` means the revenue is for `revenue_month=1` (January) |
| `stock_id` | Stock code |
| `country` | Listed market (e.g. `台灣`) |
| `revenue` | Monthly revenue (NTD 元, full amount — not thousands) |
| `revenue_month` | Revenue month (1–12) |
| `revenue_year` | Revenue year |

**MoM / YoY analysis:**
```python
import pandas as pd
df = pd.DataFrame(data)
df = df.sort_values("date").reset_index(drop=True)
df["mom_pct"] = df["revenue"].pct_change() * 100          # month-over-month %
df["yoy_pct"] = df["revenue"].pct_change(periods=12) * 100  # year-over-year %
```

---

## Taiwan Futures OHLCV — 台灣期貨

```
GET /studio/market/twfutures/ohlcv/<symbol>/<schema>
```

`start` / `end` optional (YYYY-MM-DD). Data from 2013-12-30 (`1d`) and 2014-01-02 (intraday: `1m`/`5m`/`15m`/`30m`/`60m`). Intraday bars before 2017-05-15 cover the day session only — the night session (15:00–next day 05:00 Taipei) launched 2017-05-15, so bars-per-day jumps from ~300 to ~1140 at that boundary. Timestamps UTC. Requires API plan auth.

| `symbol` | 商品 |
|---|---|
| `TXF` | 台指期（大台，近月連續） |

| `schema` | 週期 | 單次最大範圍 |
|---|---|---|
| `1d` | 日K | 3650 天（10年） |
| `1m` | 分K | 31 天 |
| `5m` | 5分K | 31 天 |
| `15m` | 15分K | 31 天 |
| `30m` | 30分K | 31 天 |
| `60m` | 小時K | 31 天 |

超出限制回傳 400：`{"error": "date_range_too_large", "max_days": <n>}`

```python
# 台指期日K
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(
    f"{BASE_URL}/studio/market/twfutures/ohlcv/TXF/1d",
    headers=headers, params=params, timeout=60,
)
data = response.json()["data"]
# [{"ts": "2024-01-02 00:00:00+00:00", "open": 17500.0, "high": 17620.0,
#   "low": 17480.0, "close": 17610.0, "volume": 98234}, ...]

# 分K（需拆分，每次最多 31 天）
from datetime import date, timedelta

def fetch_txf_chunked(schema, start, end, chunk_days=28):
    result = []
    cur = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    while cur < end_date:
        chunk_end = min(cur + timedelta(days=chunk_days), end_date)
        resp = requests.get(
            f"{BASE_URL}/studio/market/twfutures/ohlcv/TXF/{schema}",
            headers=headers,
            params={"start": cur.isoformat(), "end": chunk_end.isoformat()},
            timeout=60,
        )
        result.extend(resp.json().get("data", []))
        cur = chunk_end
    return result

bars = fetch_txf_chunked("1m", "2026-05-01", "2026-05-25")
```

**Response fields:**
| Field | Description |
|---|---|
| `ts` | Bar 開盤時間（UTC ISO 字串） |
| `open` / `high` / `low` / `close` | 指數點數 |
| `volume` | 成交口數 |

---

## Taiwan Option Put/Call Ratio — 台指選擇權買賣權未平倉量比率

```
GET /studio/market/twfutures/option/pcr
```

`start` / `end` optional (YYYY-MM-DD). Data from 2001-12-24. Daily, trading days only. Requires API plan auth. Official TAIFEX 買賣權未平倉量比率% (OI-based) — **not** derived from option institutional / large-trader data.

```python
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(
    f"{BASE_URL}/studio/market/twfutures/option/pcr",
    headers=headers, params=params, timeout=60,
)
data = response.json()["data"]
# [{"date": "2024-01-02", "pcr": 78.5}, {"date": "2024-01-03", "pcr": 81.2}, ...]
```

**Response fields:**
| Field | Description |
|---|---|
| `date` | 交易日（YYYY-MM-DD） |
| `pcr` | 買賣權未平倉量比率%（float） |

---

## Taiwan Futures Bid/Ask Volume — 台指期內外盤

```
GET /studio/market/twfutures/bid_ask_vol/<symbol>
```

`start` / `end` optional (YYYY-MM-DD). Data from 2018-02-22. Timestamps UTC. Max 31 days per request. Requires API plan auth.

1-minute bars aggregated from tick data. Day session (08:45–13:45 Taipei) and night session (15:00–next day 05:00 Taipei) are both included.

| `symbol` | 商品 |
|---|---|
| `TXF` | 台指期（大台，近月連續） |

```python
# 台指期內外盤（單日，含日盤+夜盤）
params = {"start": "2026-05-29", "end": "2026-05-29"}
response = requests.get(
    f"{BASE_URL}/studio/market/twfutures/bid_ask_vol/TXF",
    headers=headers, params=params, timeout=60,
)
data = response.json()["data"]
# [{"ts": "2026-05-29 00:45:00+00:00", "bid_vol": 669, "ask_vol": 447, "total_vol": 1156}, ...]

# 跨多天需拆分（每次最多 31 天）
def fetch_bid_ask_vol_chunked(start, end, chunk_days=28):
    result = []
    cur = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    while cur < end_date:
        chunk_end = min(cur + timedelta(days=chunk_days), end_date)
        resp = requests.get(
            f"{BASE_URL}/studio/market/twfutures/bid_ask_vol/TXF",
            headers=headers,
            params={"start": cur.isoformat(), "end": chunk_end.isoformat()},
            timeout=60,
        )
        result.extend(resp.json().get("data", []))
        cur = chunk_end
    return result
```

**Response fields:**
| Field | Description |
|---|---|
| `ts` | Bar 開盤時間（UTC ISO 字串） |
| `bid_vol` | 內盤成交量（tick 打到 bid，賣方主動） |
| `ask_vol` | 外盤成交量（tick 打到 ask，買方主動） |
| `total_vol` | 總成交量（含無法分類的 tick） |

---

## CME / ICE Futures OHLCV — 原油/黃金/Brent 期貨

```
GET /studio/market/db/ohlcv/<dataset>/<symbol>/<schema>
```

`start` / `end` optional (ISO 8601, e.g. `2024-01-01`). Data from 2010-06-06. Timestamps UTC.

| `dataset` | `symbol` | 商品 |
|---|---|---|
| `GLBX.MDP3` | `CL` | WTI 原油期貨（CME NYMEX，近月連續） |
| `GLBX.MDP3` | `GC` | 黃金期貨（CME COMEX，近月連續） |
| `IFEU.IMPACT` | `BRN` | Brent 原油期貨（ICE，近月連續） |

| `schema` | 週期 | 單次最大範圍 |
|---|---|---|
| `ohlcv-1d` | 日K | 3650 天（10年） |
| `ohlcv-1h` | 小時K | 365 天（1年） |
| `ohlcv-1m` | 分K | **30 天** |

超出限制回傳 400：`{"error": "date_range_too_large", "max_days": <n>}`
→ 需拆分多次請求、分段拼接。拉長歷史時每個 chunk 約 6 秒，年度分K 約 1.5 分鐘。

```python
# 分段拉取長歷史（以 ohlcv-1m 為例，chunk_days=30）
from datetime import date, timedelta

def fetch_ohlcv_chunked(dataset, symbol, schema, start, end, chunk_days=30):
    result = []
    cur = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    while cur < end_date:
        chunk_end = min(cur + timedelta(days=chunk_days), end_date)
        resp = requests.get(
            f"{BASE_URL}/studio/market/db/ohlcv/{dataset}/{symbol}/{schema}",
            headers=headers,
            params={"start": cur.isoformat(), "end": chunk_end.isoformat()},
            timeout=30,
        )
        result.extend(resp.json().get("data", []))
        cur = chunk_end
    return result

# 近一年 WTI 原油分K
bars = fetch_ohlcv_chunked("GLBX.MDP3", "CL", "ohlcv-1m", "2025-05-01", "2026-05-01")
```

```python
# WTI 原油日K
params = {"start": "2024-01-01", "end": "2024-12-31"}
response = requests.get(
    f"{BASE_URL}/studio/market/db/ohlcv/GLBX.MDP3/CL/ohlcv-1d",
    headers=headers, params=params, timeout=60,
)
data = response.json()["data"]
# [{"ts": "2024-01-02 00:00:00+00:00", "open": 72.50, "high": 73.10,
#   "low": 71.80, "close": 72.90, "volume": 180432}, ...]

# Brent 原油小時K
response = requests.get(
    f"{BASE_URL}/studio/market/db/ohlcv/IFEU.IMPACT/BRN/ohlcv-1h",
    headers=headers, params={"start": "2024-01-01"}, timeout=60,
)

# 黃金期貨分K
response = requests.get(
    f"{BASE_URL}/studio/market/db/ohlcv/GLBX.MDP3/GC/ohlcv-1m",
    headers=headers, params={"start": "2026-05-10", "end": "2026-05-11"}, timeout=60,
)
```

**Response fields:**
| Field | Description |
|---|---|
| `ts` | Bar 開盤時間（UTC ISO 字串） |
| `open` / `high` / `low` / `close` | 美元（原油單位：USD/桶；黃金：USD/oz） |
| `volume` | 合約口數 |

Note: 資料有約 4 小時延遲，最新幾小時不可用。

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
