# 台股財報資料 Taiwan Stock Fundamental Data

**資料來源：** Blave API（台股資料由 [FinMind](https://finmindtrade.com) 提供）  
**認證：** Bearer token（同其他 Blave API）  
**Redis cache：** 24 小時

---

## API Endpoints

### 單股（Single-stock）

| Endpoint | 資料 | 頻率 | 預設起始 |
|---|---|---|---|
| `GET /studio/market/twstock/financials/<stock_id>` | 綜合損益表 | 季頻 | 2013-01-01 |
| `GET /studio/market/twstock/balance_sheet/<stock_id>` | 資產負債表 | 季頻 | 2013-01-01 |
| `GET /studio/market/twstock/cashflow/<stock_id>` | 現金流量表 | 季頻 | 2013-01-01 |
| `GET /studio/market/twstock/monthly_revenue/<stock_id>` | 月營收 | 月頻 | 2000-01-01 |

Query params: `start` / `end`（YYYY-MM-DD，可省略）

### 批次（Batch）— 最多 50 支 / 次

| Endpoint | 資料 |
|---|---|
| `GET /studio/market/twstock/batch/financials?stock_ids=2330,2317,...` | 綜合損益表 |
| `GET /studio/market/twstock/batch/balance_sheet?stock_ids=...` | 資產負債表 |
| `GET /studio/market/twstock/batch/monthly_revenue?stock_ids=...` | 月營收 |
| `GET /studio/market/twstock/batch/price_adj?stock_ids=...&start=...&end=...` | 向後調整日K |
| `GET /studio/market/twstock/batch/institutional?stock_ids=...&start=...&end=...` | 三大法人 |
| `GET /studio/market/twstock/batch/shareholding?stock_ids=...&start=...&end=...` | 股東人數 |

Batch 回傳格式：`{"data_type": "financials", "data": {"2330": [...], "2317": [...]}}`

---

## Response Schema

### 損益表 / 資產負債表 / 現金流量表（long format）

```json
{
  "data": [
    {"date": "2023-03-31", "stock_id": "2330", "type": "Revenue", "value": 508630000000, "origin_name": "營業收入"},
    {"date": "2023-03-31", "stock_id": "2330", "type": "GrossProfit", "value": 267000000000, "origin_name": "營業毛利（毛損）"},
    ...
  ]
}
```

常見 `type` 值：

**綜合損益表 (financials)**

| type | origin_name | 說明 |
|---|---|---|
| `Revenue` | 營業收入 | 營業收入合計 |
| `GrossProfit` | 營業毛利（毛損） | |
| `OperatingIncome` | 營業利益（損失） | |
| `IncomeAfterTaxes` | 本期淨利（淨損） | ROE 分子用此 |
| `EPS` | 基本每股盈餘 | 元 |
| `PreTaxIncome` | 稅前淨利（淨損） | |
| `OperatingExpenses` | 營業費用 | |
| `CostOfGoodsSold` | 營業成本 | |

**資產負債表 (balance_sheet)**

| type | origin_name | 說明 |
|---|---|---|
| `TotalAssets` | 資產總額 | |
| `Equity` | 權益總額 | ROE 分母用此 |
| `Liabilities` | 負債總額 | |
| `CashAndCashEquivalents` | 現金及約當現金 | |
| `RetainedEarnings` | 保留盈餘合計 | |
| `CapitalStock` | 股本合計 | |

`_per` 結尾的 type 代表佔總資產百分比（例如 `Equity_per`）。

### 月營收

```json
{
  "data": [
    {"date": "2023-04-10", "stock_id": "2330", "revenue": 176100000, "revenue_month": 3, "revenue_year": 2023},
    ...
  ]
}
```

---

## BlaveClaw lib 用法

所有台股資料一律用 batch 函式（即使只有 1 支）：

```python
from lib.data import (
    fetch_twstock_price_adj_batch,       # (stock_ids, start, end, headers)
    fetch_twstock_institutional_batch,   # (stock_ids, start, end, headers)
    fetch_twstock_shareholding_batch,    # (stock_ids, start, end, headers)
    fetch_twstock_financials_batch,      # (stock_ids, headers)
    fetch_twstock_balance_sheet_batch,   # (stock_ids, headers)
    fetch_twstock_monthly_revenue_batch, # (stock_ids, headers)
)

universe = ['2330', '2317', '2454', ...]  # 可達 500 支，超過 50 支自動切塊

prices      = fetch_twstock_price_adj_batch(universe, START, END, hdrs)
inst        = fetch_twstock_institutional_batch(universe, START, END, hdrs)
financials  = fetch_twstock_financials_batch(universe, hdrs)      # dict {sid: df}
bal_sheets  = fetch_twstock_balance_sheet_batch(universe, hdrs)
revenues    = fetch_twstock_monthly_revenue_batch(universe, hdrs)
```

---

## 常用因子計算

```python
import pandas as pd

def compute_fundamental_scores(universe, hdrs):
    fin_all = fetch_twstock_financials_batch(universe, hdrs)
    bs_all  = fetch_twstock_balance_sheet_batch(universe, hdrs)
    rev_all = fetch_twstock_monthly_revenue_batch(universe, hdrs)

    scores = {}
    for sid in universe:
        try:
            fin = fin_all[sid].pivot_table(index='date', columns='type', values='value', aggfunc='last')
            bs  = bs_all[sid].pivot_table(index='date', columns='type', values='value', aggfunc='last')
            rev = rev_all[sid]

            roe          = fin['IncomeAfterTaxes'] / bs['Equity']
            gross_margin = fin['GrossProfit'] / fin['Revenue']
            eps_yoy      = fin['EPS'].pct_change(4)          # 同季比
            rev_yoy      = rev['revenue'].pct_change(12)     # 月營收年增率

            scores[sid] = {
                'roe':          roe.iloc[-1],
                'gross_margin': gross_margin.iloc[-1],
                'eps_yoy':      eps_yoy.dropna().iloc[-1] if not eps_yoy.dropna().empty else float('nan'),
                'rev_yoy':      rev_yoy.dropna().iloc[-1] if not rev_yoy.dropna().empty else float('nan'),
            }
        except Exception:
            continue

    return pd.DataFrame(scores).T
```

---

## 季度 Rebalance — Lookahead Bias 避免

財報公告截止日（台灣法規）：

| 季別 | 財報公告截止日 | 策略可用日 |
|------|-------------|-----------|
| Q1（1–3月） | 5/15 | 5/16 起 |
| Q2（4–6月） | 8/14 | 8/15 起 |
| Q3（7–9月） | 11/14 | 11/15 起 |
| Q4（10–12月） | 翌年 3/31 | 翌年 4/1 起 |

實作方式 — 取「最近一次已發布季報」對應的 rebalance 日：

```python
import pandas as pd

# 季度 rebalance 日期（財報公告截止日後第一個交易日）
REBALANCE_MONTHS_DAYS = [(4, 1), (5, 16), (8, 15), (11, 15)]

def get_rebalance_dates(start_year, end_year, price_index):
    """回傳所有季度 rebalance 日（確保為交易日）."""
    dates = []
    for year in range(start_year, end_year + 1):
        for month, day in REBALANCE_MONTHS_DAYS:
            d = pd.Timestamp(year, month, day)
            # 往後找最近的交易日
            while d not in price_index:
                d += pd.Timedelta(days=1)
            dates.append(d)
    return sorted(set(dates))
```

---

## 注意事項

- 財報資料為 long format；用 `pivot_table` 轉寬，`aggfunc='last'` 去重
- `_per` 結尾的 type（資產負債表）代表佔總資產百分比
- EPS 為每季數字，YoY 用 `.pct_change(4)`（4 季前同期比）
- 月營收發布日約在次月 10 日前；`date` 欄是發布日，`revenue_month` 是對應月份
- 大型 universe（> 50 支）必須用 batch 函式，**不要** ThreadPoolExecutor + 單股 fetch
- lib 快取有效期 30 天；如需最新季報，刪除 `cache/twstock_fin_*.parquet`
