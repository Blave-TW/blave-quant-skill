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
| `GET /studio/market/twstock/ratios/<stock_id>` | 財務比率（寬表，見 *Financial Ratios*） | 季頻 | 2013-03-31 |

Query params: `start` / `end`（YYYY-MM-DD，可省略）

### 批次（Batch）— 最多 50 支 / 次

| Endpoint | 資料 |
|---|---|
| `GET /studio/market/twstock/batch/financials?stock_ids=2330,2317,...` | 綜合損益表 |
| `GET /studio/market/twstock/batch/balance_sheet?stock_ids=...` | 資產負債表 |
| `GET /studio/market/twstock/batch/monthly_revenue?stock_ids=...` | 月營收 |
| `GET /studio/market/twstock/batch/ratios?stock_ids=...&start=...&end=...` | 財務比率 |
| `GET /studio/market/twstock/batch/price_adj?stock_ids=...&start=...&end=...` | 向後調整日K |
| `GET /studio/market/twstock/batch/price?stock_ids=...&start=...&end=...` | 原始日K OHLCV（含 High/Low） |
| `GET /studio/market/twstock/batch/per?stock_ids=...&start=...&end=...` | PER／PBR／殖利率 |
| `GET /studio/market/twstock/batch/institutional?stock_ids=...&start=...&end=...` | 三大法人 |
| `GET /studio/market/twstock/batch/shareholding?stock_ids=...&start=...&end=...` | 股東人數 |

Batch 回傳格式：`{"data_type": "financials", "data": {"2330": [...], "2317": [...]}, "failed": []}`——
`failed` 為 server 端抓取失敗（rate limit 或上游錯誤）的股票，應重試；不在 `data` 也不在 `failed`
才是真的沒資料。每型 `data` 內欄位與對應單檔 endpoint 完全一致。

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

**現金流量表 (cashflow)**——主要科目如下，完整清單依公司與年度不同，以實際回傳為準（不熟的 type 看 `origin_name`）。篩選請用 `type`，同一科目的 `origin_name` 括號全形／半形隨年度不同：

| type | origin_name | 說明 |
|---|---|---|
| `CashFlowsFromOperatingActivities` | 營業活動之淨現金流入（流出） | 營業現金流 |
| `CashProvidedByInvestingActivities` | 投資活動之淨現金流入（流出） | |
| `CashFlowsProvidedFromFinancingActivities` | 籌資活動之淨現金流入（流出） | |
| `PropertyAndPlantAndEquipment` | 取得不動產、廠房及設備 | 資本支出，負值 |
| `Depreciation` | 折舊費用 | |
| `CashBalancesEndOfPeriod` | 期末現金及約當現金餘額 | 時點餘額，非累計 |

現金流量表的流量科目是**年度累計（YTD）**：`03-31` 為 Q1 單季，`06-30`／`09-30`／`12-31`
為當年累計至該季。要單季值需減去同年前一季（Q1 不用減），`start` 請從 1 月起抓。此 endpoint
沒有 `period` 參數，一律回傳累計值。

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

## Financial Ratios (財務比率)

Blave computes these from the three statements above, so every caller gets the same
definitions. Use them instead of re-deriving a ratio by hand; when you do derive one yourself,
do not mix it with these columns unless the formula below matches.

- Single stock: `GET /studio/market/twstock/ratios/<stock_id>` (`start` / `end` optional)
- Many stocks: `GET /studio/market/twstock/batch/ratios?stock_ids=2330,2317,...` (≤ 50 ids,
  `start` / `end` optional) — `{"data_type": "ratios", "data": {"<stock_id>": [rows]}, "failed": []}`
- Wide format: one row per quarter, `date` = quarter end, oldest first. History starts at
  2013-03-31 (2013 Q1). Values are floats rounded to 4 decimals, or `null`.

### Columns

`_q` = the quarter alone. `_ttm` = trailing four quarters. Each ratio below comes as both
`<ratio>_q` and `<ratio>_ttm`:

| Ratio | Formula | Unit |
|---|---|---|
| `gross_margin` | GrossProfit ÷ Revenue | % |
| `operating_margin` | OperatingIncome ÷ Revenue | % |
| `pretax_margin` | PreTaxIncome ÷ Revenue | % |
| `net_margin` | net income ÷ Revenue | % |
| `opex_ratio` | OperatingExpenses ÷ Revenue | % |
| `roe` | net income ÷ average total Equity | % |
| `roa` | net income ÷ average TotalAssets | % |
| `eps` | EPS as filed (`_ttm` = the four quarterly EPS summed) | TWD per share |
| `revenue_per_share` | Revenue ÷ shares | TWD per share |
| `revenue_yoy` / `operating_income_yoy` / `net_income_yoy` / `eps_yoy` | growth vs the same period a year earlier | % |
| `revenue_qoq` | growth vs the previous quarter | % |
| `interest_coverage` | (PreTaxIncome + InterestExpense) ÷ InterestExpense | times |
| `receivable_turnover` | Revenue ÷ average receivables | times |
| `inventory_turnover` | CostOfGoodsSold ÷ average Inventories | times |
| `asset_turnover` | Revenue ÷ average TotalAssets | times |
| `cfo_to_net_income` | operating cash flow ÷ net income | times |
| `fcf` | operating cash flow − \|capex\| | TWD, raw amount |
| `fcf_per_share` | `fcf` ÷ shares | TWD per share |

Four period-end ratios have **no suffix** (balance-sheet values at the quarter end):

| Column | Formula | Unit |
|---|---|---|
| `debt_ratio` | Liabilities ÷ TotalAssets | % |
| `current_ratio` | CurrentAssets ÷ CurrentLiabilities | % |
| `quick_ratio` | (CurrentAssets − Inventories − Prepayments) ÷ CurrentLiabilities | % |
| `equity_multiplier` | TotalAssets ÷ Equity | times |

**Units.** Every `%` column is already multiplied by 100 (`roe_q: 11.3934` is 11.39%;
`current_ratio: 245.7635` is 2.46×). `fcf_q` / `fcf_ttm` are raw TWD (`287363030000.0` =
NT$287.4bn), not thousands. Everything else is a plain multiple or TWD per share.

### Definitions (read before comparing with another source)

- **Net income** is `IncomeAfterTaxes` (banks file it as `IncomeAfterTax`) — total net income
  including non-controlling interests; ROE's denominator is total `Equity`, also including them.
- **Single-quarter ROE / ROA are not annualised.** `roe_q` = the quarter's net income ÷ the
  average of the previous quarter-end and this quarter-end equity. Multiply by 4 yourself if you
  want an annual rate, or use `roe_ttm`.
- **TTM** = the four single quarters summed. If any of the four is missing, the `_ttm` value is
  `null` (no partial sums). `roe_ttm` / `roa_ttm` divide the TTM flow by the average of the
  balance four quarters back and the balance now, so they are the annual figure.
- **Turnover** follows the same averaging: `_q` = the quarter's flow ÷ the average of the
  previous and current quarter-end balance (not annualised); `_ttm` = the TTM flow ÷ the average
  of the balance four quarters back and the balance now. Receivables = `AccountsReceivableNet`
  plus related-party receivables (`AccountsReceivableDuefromRelatedPartiesNet`, treated as 0
  when not filed).
- **Growth** = (now − base) ÷ |base| × 100 — the absolute value keeps the sign meaningful when
  the base is negative. A base of exactly 0 → `null`. `_q` compares single quarters
  (`*_yoy_q`: same quarter last year; `revenue_qoq_q`: previous quarter); `_ttm` compares TTM
  with the TTM four quarters earlier (`*_yoy_ttm`) or one quarter earlier (`revenue_qoq_ttm`).
- **Share count for per-share columns** = parent-company net income
  (`EquityAttributableToOwnersOfParent` on the income statement) ÷ `EPS`, i.e. the weighted
  share count implied by the filing. It does not use share capital ÷ 10, which is wrong for
  stocks whose par value is not NT$10. Because EPS has only two decimals, the quarter with the
  largest |EPS| among the last four is used; if all four are below 0.1 in absolute value the
  share count — and `revenue_per_share` / `fcf_per_share` — is `null`.
- **Interest coverage** takes interest from the **cash flow statement** (`InterestExpense`, the
  add-back line, turned from year-to-date into a single quarter) because the income statement
  data carries no finance-cost line. `null` unless interest is above 0.
- **Quick ratio** subtracts both inventories and prepayments (預付款項) from current assets; a
  company that files neither line is treated as having 0 of it.
- **Free cash flow** = operating cash flow − |capex|, capex being
  `PropertyAndPlantAndEquipment` (取得不動產、廠房及設備) on the cash flow statement. The
  absolute value is taken so the result does not depend on the sign the line was filed with; a
  company that filed a cash flow statement without that line has capex 0. Cash-flow items are
  single-quarter here (the statement endpoint itself returns year-to-date).
- **`cfo_to_net_income`** is `null` when net income is ≤ 0.
- **ROE** is `null` when average equity is ≤ 0, and **`equity_multiplier`** is `null` when
  period-end equity is ≤ 0 — a negative denominator would flip the sign.

### `null` rules

A missing line item or a zero denominator gives `null`, never `0` — drop or skip it, do not
fill it with 0. The only lines read as 0 when absent are the ones named above (inventories,
prepayments, related-party receivables, capex).

**Financial-sector issuers** have many `null` columns because their statements do not carry
the line items — this follows the filing, there is no sector switch. Checked on the 2026-06-30
row of nine issuers:

| Issuer type (codes checked) | Always `null` in the check |
|---|---|
| Every one of the nine | `gross_margin`, `operating_margin`, `receivable_turnover`, `inventory_turnover` |
| Financial holdings (`2882`, `2891`, `2886`, `5880`) | the four above + `operating_income_yoy`, `current_ratio`, `quick_ratio` |
| Banks (`2801`, `5876`) | no `Revenue` line: also `pretax_margin`, `net_margin`, `opex_ratio`, `revenue_yoy`, `revenue_qoq`, `revenue_per_share`, `asset_turnover`; plus `operating_income_yoy`, `current_ratio`, `quick_ratio`, `interest_coverage` |
| Securities firms (`2855`, `6005`) | no `Revenue` line (same revenue-based columns as banks); `current_ratio` / `quick_ratio` are present |
| Insurer (`2816`) | no `Revenue` line (as banks) + `current_ratio`, `quick_ratio`, `fcf_per_share` |

`roe`, `roa`, `eps`, `debt_ratio`, `equity_multiplier`, `net_income_yoy` and `eps_yoy` were
present for all nine — those are the columns to use for a cross-sector screen. Check for
`null` rather than assuming a sector list.

**No statements → `404`.** ETFs and other codes without financial statements (`0050`, `00878`)
return `404 {"error": "No data found for stock_id: <id>"}` on the single-stock endpoint, and are
simply absent from `data` (and from `failed`) on the batch endpoint.

### Not in this dataset

- **PER / PBR / dividend yield** — daily, price-based: `GET /studio/market/twstock/per/<stock_id>`
  or `batch/per`.
- **Monthly-revenue ratios** (YoY / MoM) — monthly frequency does not fit a quarterly row:
  compute them from `GET /studio/market/twstock/monthly_revenue/<stock_id>` or
  `batch/monthly_revenue`.

### Point in time — lookahead

A row is stamped with the **quarter end** (`2026-06-30`), but the filing it is computed from
becomes public weeks later. Joining ratios to prices on `date` uses numbers nobody had yet.
Shift every row to the availability date of its quarter — the same table as the statements in
*季度 Rebalance — Lookahead Bias 避免* below (Q1 → 5/16, Q2 → 8/15, Q3 → 11/15, Q4 → next 4/1).
Financial holdings, banks, securities, futures and insurance issuers have until 8/31 for Q2
(usable 9/1; 公開發行公司財務報告及營運情形公告申報特殊適用範圍辦法 §3(3)).

Two more limits: the ratios carry no per-company announcement date, so a company that filed
early is still only usable from the deadline; and the store keeps the **latest** version of each
quarter — a restated filing replaces the old numbers, so history is not an as-first-reported
vintage.

```python
import pandas as pd
AVAILABLE = {3: (5, 16, 0), 6: (8, 15, 0), 9: (11, 15, 0), 12: (4, 1, 1)}   # quarter-end month → (month, day, +years)

def available_from(quarter_end):
    m, d, dy = AVAILABLE[quarter_end.month]
    return pd.Timestamp(quarter_end.year + dy, m, d)

df = pd.DataFrame(data).assign(date=lambda x: pd.to_datetime(x["date"]))   # data = the endpoint's "data" list
df["available"] = df["date"].map(available_from)
roe = df.set_index("available")["roe_ttm"]          # then reindex(prices.index, method="ffill")
```

---

## Blave Agent lib 用法

所有台股資料一律用 batch 函式（即使只有 1 支）：

```python
from lib.data import (
    fetch_twstock_price_adj_batch,       # (stock_ids, start, end, headers)
    fetch_twstock_institutional_batch,   # (stock_ids, start, end, headers)
    fetch_twstock_shareholding_batch,    # (stock_ids, start, end, headers)
    fetch_twstock_financials_batch,      # (stock_ids, headers)
    fetch_twstock_balance_sheet_batch,   # (stock_ids, headers)
    fetch_twstock_monthly_revenue_batch, # (stock_ids, headers)
    fetch_twstock_ratios_batch,          # (stock_ids, headers, start=None, end=None) → 財務比率寬表
)

universe = ['2330', '2317', '2454', ...]  # 可達 500 支，超過 50 支自動切塊

prices      = fetch_twstock_price_adj_batch(universe, START, END, hdrs)
inst        = fetch_twstock_institutional_batch(universe, START, END, hdrs)
financials  = fetch_twstock_financials_batch(universe, hdrs)      # dict {sid: df}
bal_sheets  = fetch_twstock_balance_sheet_batch(universe, hdrs)
revenues    = fetch_twstock_monthly_revenue_batch(universe, hdrs)
ratios      = fetch_twstock_ratios_batch(universe, hdrs)          # dict {sid: df}, columns roe_q, roe_ttm, ...
```

---

## 常用因子計算

> ROE、毛利率、成長率等已有現成欄位（*Financial Ratios*）。下面是自己從報表算的寫法，口徑與該節不同（例如這裡的 ROE 分母是期末權益、不是期初期末平均），兩者不要混用。

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
