# 台股查詢 Taiwan Stock Market Data

**資料來源 / Data Sources:**
- **TWSE（台灣證券交易所）上市** Base URL: `https://openapi.twse.com.tw`
- **TPEX（證券櫃檯買賣中心）上櫃** Base URL: `https://www.tpex.org.tw`

**Authentication:** 無需 API Key — 公開資料，無需認證

**日期格式 / Date Format:** 民國年 (ROC calendar) — 例如 `1150507` = 民國115年05月07日 = 2026/05/07

---

## 查詢流程 — 依名稱或代號查股票

1. 根據交易所類型選擇 endpoint：
   - 上市（TWSE）→ `GET /v1/exchangeReport/BWIBBU_ALL`
   - 上櫃（TPEX）→ `GET https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes`
   - 不確定在哪一市場 → 兩個都查，合併搜尋結果

2. 下載完整清單，在本地端按 `Code`（上市）或 `SecuritiesCompanyCode`（上櫃）/ `Name` / `CompanyName` 進行篩選

3. 顯示代號、名稱，以及基本數據（殖利率、PE、PB 等）

---

## Key Endpoints

| 用途 | Method | URL |
|---|---|---|
| 上市股票清單 + PE/殖利率/PB | GET | `https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL` |
| 上市股票全日收盤行情 | GET | `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL` |
| 上市股票停復牌狀態 | GET | `https://openapi.twse.com.tw/v1/exchangeReport/TWTB4U` |
| 上櫃股票清單 + 行情 | GET | `https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes` |

---

## Response 欄位

### TWSE `BWIBBU_ALL`（上市清單，最常用）
| 欄位 | 說明 |
|---|---|
| `Code` | 股票代號 |
| `Name` | 股票簡稱 |
| `Date` | 資料日期（民國年，如 `1150507`） |
| `PEratio` | 本益比 |
| `DividendYield` | 殖利率（%） |
| `PBratio` | 股價淨值比 |

### TPEX `tpex_mainboard_quotes`（上櫃清單）
| 欄位 | 說明 |
|---|---|
| `SecuritiesCompanyCode` | 股票代號 |
| `CompanyName` | 公司名稱 |
| `Close` | 收盤價 |
| `Change` | 漲跌 |
| `Open` | 開盤價 |
| `High` | 最高價 |
| `Low` | 最低價 |
| `TradingShares` | 成交股數 |
| `TransactionAmount` | 成交金額 |

---

## Python 範例

```python
import requests

# 查詢上市股票，依名稱搜尋
res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
stocks = res.json()

# 依代號搜尋
def find_by_code(code):
    return [s for s in stocks if s["Code"] == code]

# 依名稱關鍵字搜尋
def find_by_name(keyword):
    return [s for s in stocks if keyword in s["Name"]]

# 範例：查台積電
results = find_by_code("2330")
# 或
results = find_by_name("台積")
# → [{"Code": "2330", "Name": "台積電", "PEratio": "34.87", "DividendYield": "0.95", "PBratio": "11.05", ...}]

# 查詢上櫃股票
res_otc = requests.get("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes")
otc_stocks = res_otc.json()

def find_otc_by_code(code):
    return [s for s in otc_stocks if s["SecuritiesCompanyCode"] == code]

def find_otc_by_name(keyword):
    return [s for s in otc_stocks if keyword in s["CompanyName"]]
```

---

## 注意事項

- TWSE API 資料約每個交易日收盤後更新；非交易日回傳前一交易日資料
- 資料免費、無需 API Key、無 rate limit 限制（合理使用）
- 台股代號格式：一般股票為 4 位數字（如 `2330`）、ETF 以 `00` 開頭（如 `0050`）、債券 ETF 含英文字母（如 `00679B`）
- 查詢不確定在上市或上櫃時，兩個 API 都下載後合併搜尋
- 全部為唯讀查詢，不需要 Safety Mode CONFIRM

---

## 分點資料（BSR 買賣日報表）

查詢各券商對特定股票的當日買賣明細，需通過 CAPTCHA 驗證。

**流程：** GET 頁面取表單欄位 → 下載 CAPTCHA 圖片 → 用自己的 vision 讀取答案 → POST 表單 → 解析結果表格

詳細流程與 Python 程式碼：`references/twse-bsr-reference.md`
