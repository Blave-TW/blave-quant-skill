# TWSE / TPEX API Reference — 台股市場資料（原始 API，僅限 Blave 沒有對應資料時使用）

**⚠️ 這份文件只涵蓋 Blave API 沒有對應端點的兩種情況：停復牌狀態、全市場 PE/殖利率/PB 一次性掃描。**
股票代號/名稱查詢、收盤價、單支 PE/殖利率/PB 一律用 Blave API（見 `references/twse-skill.md` 的對照表 /
`blave-api.md`），不要用這份文件裡的原始端點——原始 API 沒有 Blave API 的 official-first + fallback +
cache 保護，資料時效可能落後。

**Authentication:** 公開 API，無需 API Key，無需帳號

**日期格式:** 民國年 (ROC) — `YYYMMDD`，例如 `1150507` = 2026/05/07（民國 115 年 5 月 7 日）

---

## `GET /v1/exchangeReport/TWTB4U` — 上市股票停復牌狀態（Blave 沒有對應端點）

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

## `GET /v1/exchangeReport/BWIBBU_ALL` — 全市場 PE/殖利率/PB 掃描（Blave 沒有批次版）

**用途:** 一次取得**全部上市股票**的 PE/殖利率/PB，用於篩選/掃描（單支股票查詢請用 Blave API 的
`/studio/market/twstock/per/<stock_id>`）

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

上櫃股票的對應掃描（含完整行情，非只 PE/PB）：

```bash
curl "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes"
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

## Python 範例

```python
import requests

# 停復牌狀態
def fetch_suspension_status():
    res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/TWTB4U")
    res.raise_for_status()
    return res.json()

# 全市場 PE/殖利率/PB 掃描（例如篩選 PE < 10 的股票）
def scan_low_pe(max_pe=10.0):
    res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
    res.raise_for_status()
    result = []
    for s in res.json():
        try:
            pe = float(s["PEratio"])
        except (ValueError, TypeError):
            continue
        if pe <= max_pe:
            result.append({"code": s["Code"], "name": s["Name"], "pe": pe})
    return result

# 民國年轉西元年
def roc_to_ce(roc_date_str):
    """'1150507' → '2026-05-07'"""
    roc = int(roc_date_str[:3])
    month = roc_date_str[3:5]
    day = roc_date_str[5:7]
    return f"{roc + 1911}-{month}-{day}"
```

---

## 注意事項

- 上面兩個 endpoint 均為 **GET**，無需任何 header 或認證
- 資料為**當日收盤後**更新；非交易日（週末、國定假日）回傳最近一個交易日資料
- 台股代號規則：
  - 一般股票：4 位數字（`1101`～`9999`）
  - ETF：以 `00` 開頭（`0050`、`0056`）
  - 債券/海外 ETF：含英文字母（`00679B`、`00687B`）
  - 上市公司認購權證：以 `0` 開頭的 5～6 位
- TPEX 的代號格式與 TWSE 相同但不重疊（兩市場代號不會相同）
- 全部為唯讀查詢，**不需要 Safety Mode CONFIRM**
