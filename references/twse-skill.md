# 台股查詢 Taiwan Stock Market Data

**⚠️ Blave API 優先，不是這份文件裡的原始 TWSE/TPEX API。** 這份文件裡的原始 TWSE/TPEX 端點**只在
Blave API 沒有對應資料時**才使用（目前只剩「停復牌狀態」+「全市場 PE/殖利率/PB 一次性掃描」兩種情況）。
股票代號/名稱查詢、收盤價、單支 PE/殖利率/PB，一律先走 Blave API：

| 需求 | 用 Blave API | 端點 |
|---|---|---|
| 股票代號/名稱查詢、建 universe | ✅ Blave | `GET /studio/market/twstock/list`（含 industry_code、listing_date）或 `/info/<stock_id>` |
| 收盤價 / 今天收盤 / 走勢 | ✅ Blave | `GET /studio/market/twstock/price/<stock_id>`（日K）或 `/quote/<stock_id>`（即時） |
| 單支 PE / 殖利率 / PB | ✅ Blave | `GET /studio/market/twstock/per/<stock_id>` |
| 停復牌狀態 | ❌ Blave 沒有 | 見下方 TWSE `TWTB4U`（唯一沒有 Blave 對應的查詢） |
| 全市場 PE/殖利率/PB 一次性掃描（非單支） | ❌ Blave 沒有批次版 | 見下方 TWSE `BWIBBU_ALL` |

不要為了「查代號/收盤價」去打 `STOCK_DAY_ALL`、`t187ap03_L`、`tpex_mainboard_quotes`——這些原始
API 的資料時效落後 Blave API（Blave 是 official-first + fallback + cache，原始 API 沒有這層保護），
且 Blave 的 `/list`/`/info` 已經把兩個交易所（上市+上櫃，含 ETF）合併好了，不需要自己分別打 TWSE + TPEX
再合併。

---

## 停復牌狀態（Blave 沒有對應端點，唯一合法的原始 API 用途之一）

**資料來源:** TWSE `https://openapi.twse.com.tw`，無需認證

**日期格式:** 民國年 (ROC calendar) — 例如 `1150507` = 民國115年05月07日 = 2026/05/07

```
GET https://openapi.twse.com.tw/v1/exchangeReport/TWTB4U
```

回傳全部上市股票的停牌狀態：
```json
[{"Date": "1150508", "Code": "0050", "Name": "元大台灣50", "Suspension": ""}, ...]
```
`Suspension` 為空字串 = 正常交易；有值 = 停牌。

---

## 全市場 PE/殖利率/PB 一次性掃描（Blave 沒有批次版，唯一合法的原始 API 用途之二）

單支股票的 PE/殖利率/PB 用 Blave `/studio/market/twstock/per/<stock_id>`；但如果要**一次掃描全市場**
（例如篩選低本益比股票），Blave 目前沒有批次端點，才用這個：

```
GET https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL   （上市）
GET https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes   （上櫃，含行情非只 PE/PB）
```

上市回傳欄位：`Date`、`Code`、`Name`、`PEratio`、`DividendYield`、`PBratio`。
詳細欄位與 Python 範例：`references/twse-api-reference.md`。

---

## 注意事項

- 上面兩個原始 API 都是唯讀查詢，不需要 Safety Mode CONFIRM
- 資料約每個交易日收盤後更新；非交易日回傳前一交易日資料
- 台股代號格式：一般股票為 4 位數字（如 `2330`）、ETF 以 `00` 開頭（如 `0050`）、債券 ETF 含英文字母（如 `00679B`）

---

## 分點資料（BSR 買賣日報表）

查詢各券商對特定股票的當日買賣明細——這個一律走 Blave API（`/studio/market/twstock/broker/stock/<stock_id>`
或 `/broker/trader/<trader_id>`），不需要 CAPTCHA。詳見 `references/twse-bsr-reference.md`。
