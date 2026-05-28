# TWSE / TPEX API Reference — 台股市場資料

## Overview

| 市場 | 說明 | Base URL |
|---|---|---|
| TWSE 上市 | 台灣證券交易所（集中市場） | `https://openapi.twse.com.tw` |
| TPEX 上櫃 | 證券櫃檯買賣中心（OTC 市場） | `https://www.tpex.org.tw` |

**Authentication:** 公開 API，無需 API Key，無需帳號

**日期格式:** 民國年 (ROC) — `YYYMMDD`，例如 `1150507` = 2026/05/07（民國 115 年 5 月 7 日）

---

## TWSE Endpoints

### `GET /v1/exchangeReport/BWIBBU_ALL` — 上市股票清單 + 本益比/殖利率/PB

**用途:** 取得所有上市股票的代號、名稱，以及基本估值數據

**Request:**
```bash
curl "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL"
```

**Response:** JSON array
```json
[
  {
    "Date": "1150507",
    "Code": "2330",
    "Name": "台積電",
    "PEratio": "34.87",
    "DividendYield": "0.95",
    "PBratio": "11.05"
  },
  ...
]
```

| 欄位 | 型態 | 說明 |
|---|---|---|
| `Date` | string | 資料日期（民國年格式） |
| `Code` | string | 股票代號 |
| `Name` | string | 股票簡稱 |
| `PEratio` | string | 本益比（`""` 表示無資料） |
| `DividendYield` | string | 殖利率（%） |
| `PBratio` | string | 股價淨值比 |

---

### `GET /v1/exchangeReport/STOCK_DAY_ALL` — 上市股票全日收盤行情

**用途:** 取得所有上市股票當日完整行情（開高低收、成交量、成交金額）

**Request:**
```bash
curl "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
```

**Response:** JSON array
```json
[
  {
    "Date": "1150507",
    "Code": "2330",
    "Name": "台積電",
    "TradeVolume": "32451780",
    "TradeValue": "31011950820",
    "OpeningPrice": "955.00",
    "HighestPrice": "960.00",
    "LowestPrice": "950.00",
    "ClosingPrice": "956.00",
    "Change": "2.0000",
    "Transaction": "46821"
  },
  ...
]
```

| 欄位 | 說明 |
|---|---|
| `TradeVolume` | 成交股數（股） |
| `TradeValue` | 成交金額（元） |
| `OpeningPrice` | 開盤價 |
| `HighestPrice` | 最高價 |
| `LowestPrice` | 最低價 |
| `ClosingPrice` | 收盤價 |
| `Change` | 漲跌（正為漲，負為跌） |
| `Transaction` | 成交筆數 |

---

### `GET /v1/exchangeReport/TWTB4U` — 上市股票停復牌狀態

**用途:** 查詢今日各股票是否停牌

**Request:**
```bash
curl "https://openapi.twse.com.tw/v1/exchangeReport/TWTB4U"
```

**Response:**
```json
[
  {"Date": "1150508", "Code": "0050", "Name": "元大台灣50", "Suspension": ""},
  {"Date": "1150508", "Code": "2330", "Name": "台積電", "Suspension": ""},
  ...
]
```

`Suspension` 為空字串 = 正常交易；有值 = 停牌。

---

## TPEX Endpoints

### `GET /openapi/v1/tpex_mainboard_quotes` — 上櫃股票清單 + 行情

**用途:** 取得所有上櫃股票的代號、名稱，以及當日完整行情

**Request:**
```bash
curl "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes"
```

**Response:** JSON array
```json
[
  {
    "Date": "1150507",
    "SecuritiesCompanyCode": "6863",
    "CompanyName": "精元電腦",
    "Close": "45.20",
    "Change": "0.50",
    "Open": "44.80",
    "High": "45.30",
    "Low": "44.70",
    "TradingShares": "1234000",
    "TransactionAmount": "55762800",
    "TransactionNumber": "1203",
    "Capitals": "500000000",
    "NextLimitUp": "49.75",
    "NextLimitDown": "40.70"
  },
  ...
]
```

| 欄位 | 說明 |
|---|---|
| `SecuritiesCompanyCode` | 股票代號 |
| `CompanyName` | 公司名稱 |
| `Close` | 收盤價 |
| `Change` | 漲跌 |
| `Open` / `High` / `Low` | 開高低 |
| `TradingShares` | 成交股數 |
| `TransactionAmount` | 成交金額 |
| `TransactionNumber` | 成交筆數 |
| `Capitals` | 實收資本額 |
| `NextLimitUp` | 次日漲停價 |
| `NextLimitDown` | 次日跌停價 |

---

### `GET /v1/opendata/t187ap03_L` — 上市股票完整清單（含產業別、上市日期）

**用途:** 取得全部 TWSE 上市股票的基本資料，最適合用來建立回測 universe

**Request:**
```bash
curl "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
```

**Response:** JSON array（約 1,089 筆）

| 欄位 | 說明 | 注意 |
|---|---|---|
| `公司代號` | 股票代號 | **需要 `.strip()`**，原始值可能含空白 |
| `公司簡稱` | 股票簡稱 | |
| `產業別` | 產業別代碼（見下表） | |
| `上市日期` | 格式 `YYYYMMDD`（西元年） | |
| `實收資本額` | 實收資本額（元） | |

常見產業別代碼：

| 代碼 | 產業 |
|---|---|
| `01` | 水泥 |
| `02` | 食品 |
| `05` | 紡織纖維 |
| `11` | 化學 |
| `13` | 玻璃陶瓷 |
| `14` | 造紙 |
| `17` | 電機機械 |
| `18` | 電器電纜 |
| `19` | 化學生技醫療 |
| `20` | 半導體 |
| `21` | 電腦及周邊設備 |
| `22` | 光電 |
| `23` | 通信網路 |
| `24` | 電子零組件 |
| `25` | 電子通路 |
| `26` | 資訊服務 |
| `27` | 其他電子 |
| `29` | 建材營造 |
| `31` | 航運 |
| `32` | 觀光餐旅 |
| `33` | 金融保險 |
| `36` | 鋼鐵 |
| `37` | 橡膠 |
| `38` | 汽車 |

**建立 universe 範例：**
```python
import requests

r = requests.get('https://openapi.twse.com.tw/v1/opendata/t187ap03_L', timeout=15)
stocks = r.json()

# 全部上市股票
universe = [item['公司代號'].strip() for item in stocks]

# 只取半導體 + 電腦及周邊（產業別 20, 21）
tech = [item['公司代號'].strip() for item in stocks if item['產業別'] in ('20', '21')]
```

---

## Python 完整範例

```python
import requests

# ─────────────────────────────────────────────
# 1. 查詢股票代號（上市 + 上櫃合併搜尋）
# ─────────────────────────────────────────────

def fetch_twse_stocks():
    res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
    res.raise_for_status()
    return res.json()

def fetch_tpex_stocks():
    res = requests.get("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes")
    res.raise_for_status()
    return res.json()

def search_stock(keyword):
    """依代號或名稱關鍵字搜尋，同時查上市與上櫃"""
    results = []

    # 上市
    for s in fetch_twse_stocks():
        if keyword in s["Code"] or keyword in s["Name"]:
            results.append({
                "market": "上市 (TWSE)",
                "code": s["Code"],
                "name": s["Name"],
                "pe": s.get("PEratio", ""),
                "yield_pct": s.get("DividendYield", ""),
                "pb": s.get("PBratio", ""),
            })

    # 上櫃
    for s in fetch_tpex_stocks():
        if keyword in s["SecuritiesCompanyCode"] or keyword in s["CompanyName"]:
            results.append({
                "market": "上櫃 (TPEX)",
                "code": s["SecuritiesCompanyCode"],
                "name": s["CompanyName"],
                "close": s.get("Close", ""),
                "change": s.get("Change", ""),
            })

    return results

# 範例
print(search_stock("台積"))   # → [{"market": "上市 (TWSE)", "code": "2330", "name": "台積電", ...}]
print(search_stock("2330"))   # 同上
print(search_stock("0050"))   # → ETF 元大台灣50


# ─────────────────────────────────────────────
# 2. 取得今日行情（上市）
# ─────────────────────────────────────────────

def get_daily_quote_twse(code):
    res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
    res.raise_for_status()
    stocks = res.json()
    matches = [s for s in stocks if s["Code"] == code]
    return matches[0] if matches else None

quote = get_daily_quote_twse("2330")
# → {"Code": "2330", "Name": "台積電", "ClosingPrice": "956.00", "Change": "2.0000", ...}


# ─────────────────────────────────────────────
# 3. 民國年轉西元年
# ─────────────────────────────────────────────

def roc_to_ce(roc_date_str):
    """'1150507' → '2026-05-07'"""
    roc = int(roc_date_str[:3])
    month = roc_date_str[3:5]
    day = roc_date_str[5:7]
    return f"{roc + 1911}-{month}-{day}"
```

---

## 注意事項

- 所有 endpoint 均為 **GET**，無需任何 header 或認證
- 資料為**當日收盤後**更新；非交易日（週末、國定假日）回傳最近一個交易日資料
- 台股代號規則：
  - 一般股票：4 位數字（`1101`～`9999`）
  - ETF：以 `00` 開頭（`0050`、`0056`）
  - 債券/海外 ETF：含英文字母（`00679B`、`00687B`）
  - 上市公司認購權證：以 `0` 開頭的 5～6 位
- TPEX 的代號格式與 TWSE 相同但不重疊（兩市場代號不會相同）
- 全部為唯讀查詢，**不需要 Safety Mode CONFIRM**
