# 台股分點買賣超 — Blave API 參考

兩種查詢方式：**用股票代號**查哪些券商買賣該股，或**用券商代號**查該券商當天買賣哪些股票。

---

## Endpoint 1 — 用股票代號查分點

```
GET /studio/market/twstock/broker/stock/<stock_id>
```

| 參數 | 類型 | 必填 | 說明 |
|---|---|---|---|
| `stock_id` | path | 是 | 股票代號，例如 `2330` |
| `start` | query | 否 | 開始日期 `YYYY-MM-DD`（預設今天） |
| `end` | query | 否 | 結束日期 `YYYY-MM-DD`（預設今天） |

**回傳：** `{"stock_id": "2330", "data": [...]}`

每筆為一個券商分點在當天的交易紀錄：

| 欄位 | 型別 | 說明 |
|---|---|---|
| `date` | string | 日期（YYYY-MM-DD） |
| `stock_id` | string | 股票代號 |
| `broker_id` | string | 券商分點代碼 |
| `broker_name` | string | 券商分點名稱 |
| `price` | float | 當日成交均價 |
| `buy` | int | 當日買進股數 |
| `sell` | int | 當日賣出股數 |

---

## Endpoint 2 — 用券商代號查分點

```
GET /studio/market/twstock/broker/trader/<trader_id>
```

| 參數 | 類型 | 必填 | 說明 |
|---|---|---|---|
| `trader_id` | path | 是 | 券商分點代碼，例如 `9898`（元大新莊） |
| `start` | query | 否 | 開始日期 `YYYY-MM-DD`（預設今天） |
| `end` | query | 否 | 結束日期 `YYYY-MM-DD`（預設今天） |

**回傳：** `{"trader_id": "9898", "data": [...]}`

每筆為該券商分點在當天對某支股票的交易紀錄（欄位同上，`stock_id` 為查到的股票）。

---

## Python 範例

```python
import os
import requests

BASE_URL = "https://api.blave.org"
HEADERS = {
    "api-key": os.environ["blave_api_key"],
    "secret-key": os.environ["blave_secret_key"],
}

def get_broker_by_stock(stock_id, start=None, end=None):
    params = {k: v for k, v in {"start": start, "end": end}.items() if v}
    r = requests.get(f"{BASE_URL}/studio/market/twstock/broker/stock/{stock_id}", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()["data"]

def get_broker_by_trader(trader_id, start=None, end=None):
    params = {k: v for k, v in {"start": start, "end": end}.items() if v}
    r = requests.get(f"{BASE_URL}/studio/market/twstock/broker/trader/{trader_id}", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()["data"]

# 查台積電 2024-01-02 買賣超前10大分點
rows = get_broker_by_stock("2330", start="2024-01-02", end="2024-01-02")
for row in sorted(rows, key=lambda x: x["buy"] - x["sell"], reverse=True)[:10]:
    net = row["buy"] - row["sell"]
    print(f"{row['broker_name']:20s}  買 {row['buy']:>8,}  賣 {row['sell']:>8,}  超 {net:>+8,}")

# 查元大新莊 (9898) 2024-01-02 買了哪些股
rows2 = get_broker_by_trader("9898", start="2024-01-02", end="2024-01-02")
for row in sorted(rows2, key=lambda x: x["buy"] - x["sell"], reverse=True)[:10]:
    net = row["buy"] - row["sell"]
    print(f"{row['stock_id']}  買 {row['buy']:>8,}  賣 {row['sell']:>8,}  超 {net:>+8,}")
```

---

## 注意事項

- 查詢為唯讀，**不需要 Safety Mode CONFIRM**
- 非交易日回傳空 `data` 陣列
- 建議使用 `start` / `end` 限制日期範圍；日期範圍每天呼叫一次 FinMind API，超過一週建議分段查詢
- 資料快取於 server 端 parquet，同一日期二次查詢不重打 FinMind
