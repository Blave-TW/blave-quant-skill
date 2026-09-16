# 台股分點買賣超 — Blave API 參考

> 資料來源：[FinMind](https://finmindtrade.com)
>
> 資料起始 **2021-06-30**。每個交易日的資料在台灣時間約 21:30 後才有，之前查當日回空陣列；假日同樣回空陣列。 回 503 代表資料暫不可用，稍後重試，不要當成沒有交易。

兩種查詢方式：**用股票代號**查哪些券商買賣該股，或**用券商代號**查該券商買賣哪些股票。每種都可查單日（`date`）或區間（`start`/`end`）。

> 端點規格以 `references/blave-api.md` › `broker/*` 為準，本檔只放工作流程與範例。

---

## Endpoint 0 — 查券商分點代碼（broker_id）

**不知道 broker_id 時先用此端點查詢，再帶入 Endpoint 1/2。**

```
GET /studio/market/twstock/broker/search?name=<name>
```

| 參數 | 說明 |
|---|---|
| `name` | 分點名稱（模糊比對），例如 `松山`、`凱基` |

**回傳：** `{"query": "松山", "data": [{"broker_id": "9217", "broker_name": "凱基-松山"}, ...]}`

> 分點名稱格式為「券商-分點」，例如 `凱基-松山`、`元大-松山`。搜尋時用分點地名即可。

---

## Endpoint 1 — 用股票代號查分點（單日或區間）

```
GET /studio/market/twstock/broker/stock/<stock_id>
```

| 參數 | 類型 | 必填 | 說明 |
|---|---|---|---|
| `stock_id` | path | 是 | 股票代號，例如 `2330` |
| `date` | query | 否 | 單日 `YYYY-MM-DD`（預設今天） |
| `start` | query | 否 | 區間起日 `YYYY-MM-DD`；與 `date` 同送時以 `start` 為準 |
| `end` | query | 否 | 區間迄日 `YYYY-MM-DD`（預設 = `start`）；含頭尾最多 366 天，超過回 400 `{"error": "start/end range is <n> days; max 366 (inclusive) — split into smaller ranges"}` |

**回傳：** `{"stock_id": "2330", "data": [...]}`

每筆為一個券商分點在某一天的交易紀錄（區間查詢時每天各一組）：

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

## Endpoint 2 — 用券商代號查分點（單日或區間）

```
GET /studio/market/twstock/broker/trader/<trader_id>
```

| 參數 | 類型 | 必填 | 說明 |
|---|---|---|---|
| `trader_id` | path | 是 | 券商分點代碼，例如 `9217`（凱基-松山）。字母數字皆支援，如 `920A` |
| `date` | query | 否 | 單日 `YYYY-MM-DD`（預設今天） |
| `start` | query | 否 | 區間起日 `YYYY-MM-DD`；與 `date` 同送時以 `start` 為準 |
| `end` | query | 否 | 區間迄日 `YYYY-MM-DD`（預設 = `start`）；含頭尾最多 366 天，超過回 400 `{"error": "start/end range is <n> days; max 366 (inclusive) — split into smaller ranges"}` |

**回傳：** `{"trader_id": "9898", "data": [...]}`

每筆為該券商分點在某一天對某支股票的交易紀錄（欄位同上，`stock_id` 為查到的股票）。

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

def get_broker_by_stock(stock_id, date=None):
    params = {"date": date} if date else {}
    r = requests.get(f"{BASE_URL}/studio/market/twstock/broker/stock/{stock_id}", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()["data"]

def get_broker_by_trader(trader_id, date=None):
    params = {"date": date} if date else {}
    r = requests.get(f"{BASE_URL}/studio/market/twstock/broker/trader/{trader_id}", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()["data"]

# 查台積電 2024-01-02 買賣超前10大分點
rows = get_broker_by_stock("2330", date="2024-01-02")
for row in sorted(rows, key=lambda x: x["buy"] - x["sell"], reverse=True)[:10]:
    net = row["buy"] - row["sell"]
    print(f"{row['broker_name']:20s}  買 {row['buy']:>8,}  賣 {row['sell']:>8,}  超 {net:>+8,}")

# 查凱基-松山 (9217) 2024-01-02 買了哪些股
rows2 = get_broker_by_trader("9217", date="2024-01-02")
for row in sorted(rows2, key=lambda x: x["buy"] - x["sell"], reverse=True)[:10]:
    net = row["buy"] - row["sell"]
    print(f"{row['stock_id']}  買 {row['buy']:>8,}  賣 {row['sell']:>8,}  超 {net:>+8,}")
```

---

## 多日聚合範例

多日範圍用 `start`/`end` 一次查（每次含頭尾最多 366 天，更長就切段）。每筆回傳自帶 `date`：

```python
import os, requests, pandas as pd
from datetime import date, timedelta

BASE_URL = "https://api.blave.org"
HEADERS = {
    "api-key": os.environ["blave_api_key"],
    "secret-key": os.environ["blave_secret_key"],
}

def get_trader_flows(trader_id, start, end):
    """回傳 DataFrame，欄位：date, stock_id, net（買超股數）"""
    records = []
    cur, end_d = date.fromisoformat(start), date.fromisoformat(end)
    while cur <= end_d:
        chunk_end = min(cur + timedelta(days=365), end_d)
        r = requests.get(
            f"{BASE_URL}/studio/market/twstock/broker/trader/{trader_id}",
            headers=HEADERS, params={"start": cur.isoformat(), "end": chunk_end.isoformat()},
            timeout=60,
        )
        r.raise_for_status()
        for row in r.json().get("data", []):
            records.append({
                "date": row["date"],
                "stock_id": row["stock_id"],
                "net": row["buy"] - row["sell"],
            })
        cur = chunk_end + timedelta(days=1)
    return pd.DataFrame(records)

# 凱基-松山 (9217) 近一個月買超排名
flows = get_trader_flows("9217", "2026-04-01", "2026-05-01")
net = flows.groupby("stock_id")["net"].sum().sort_values(ascending=False)
print(net.head(10))
```

**CRITICAL — 用 trader flows 選股的 Lookahead Bias：**

回測時若用 trader flows 建立候選池，**禁止**用全期累計 net 排名過濾：

```python
# ❌ 錯誤：用整段回測期累計排名篩選，洩漏未來資訊
top50 = flows.groupby("stock_id")["net"].sum().nlargest(50).index

# ✅ 正確：每個調倉日只用截至當日的 lookback 視窗內資料排名
# 或預先定義固定宇宙（例如台灣50大型股），完全不依賴 flows 篩選
```

---

## 注意事項

- 查詢為唯讀，**不需要 Safety Mode CONFIRM**
- 非交易日回傳空 `data` 陣列
- Endpoint 1/2 單日帶 `date`，多日帶 `start`/`end`（含頭尾 ≤ 366 天，見上方範例）
- 資料快取於 server 端 parquet，同一日期二次查詢不重新抓取
