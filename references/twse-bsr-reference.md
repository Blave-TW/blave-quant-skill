# TWSE BSR 分點資料 — 買賣日報表查詢

## Overview

| 項目 | 說明 |
|---|---|
| 網站 | https://bsr.twse.com.tw/bshtm/ |
| 主頁面 | `https://bsr.twse.com.tw/bshtm/bsMenu.aspx` |
| 用途 | 查詢各券商（分點）對特定股票的當日買賣明細 |
| 驗證 | 需通過 5 字元圖形 CAPTCHA |
| 技術 | ASP.NET WebForms，需帶 `__VIEWSTATE` 等隱藏欄位 |

---

## 查詢流程

```
Step 1: GET bsMenu.aspx
        → 取得 ASP.NET 隱藏欄位 + CAPTCHA 圖片 URL

Step 2: 下載 CAPTCHA 圖片，存成本地檔案
        → 用自己的 vision 讀取圖片，取得 5 個字元的答案

Step 3: POST bsMenu.aspx（帶齊所有表單欄位）
        → 若回應頁面找不到 bsContent 連結 → CAPTCHA 失敗，回到 Step 1 重試
        → 若找到 bsContent 連結 → 繼續 Step 4

Step 4: GET bsContent.aspx?StkNo=<股票代號>（同一 session）
        → 回傳逗號分隔純文字，解析後輸出各券商資料
```

---

## Step 1 — GET 頁面，提取表單欄位

```python
import requests
from bs4 import BeautifulSoup

BASE = "https://bsr.twse.com.tw/bshtm"
session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

r = session.get(f"{BASE}/bsMenu.aspx", timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

# 提取所有 ASP.NET 隱藏欄位（__VIEWSTATE 等）
form_data = {inp["name"]: inp.get("value", "")
             for inp in soup.find_all("input", type="hidden")}

# 找 CAPTCHA 圖片 URL（格式：CaptchaImage.aspx?guid=<uuid>）
img_tag = soup.find("img", src=lambda s: s and "CaptchaImage.aspx" in s)
captcha_url = f"{BASE}/{img_tag['src']}"
```

---

## Step 2 — 下載 CAPTCHA 圖片並用 vision 解碼

```python
# 下載圖片，存到本地暫存檔
img_bytes = session.get(captcha_url, timeout=10).content
with open("/tmp/bsr_captcha.png", "wb") as f:
    f.write(img_bytes)
```

**重要：** 下載後，用 `Read` tool 讀取 `/tmp/bsr_captcha.png`，直接用自己的 vision 識別圖中的 5 個字元（英數混合），不需要呼叫任何外部 API。

---

## Step 3 — POST 表單

```python
# captcha_text = 從圖片讀取到的 5 字元答案
form_data.update({
    "RadioButton_Normal": "RadioButton_Normal",
    "TextBox_Stkno": "2330",      # 股票代號
    "CaptchaControl1": captcha_text,
    "btnOK": "查詢",
    "__EVENTTARGET": "",
    "__EVENTARGUMENT": "",
    "__LASTFOCUS": "",
})

post_r = session.post(f"{BASE}/bsMenu.aspx", data=form_data, timeout=15)
result_soup = BeautifulSoup(post_r.text, "html.parser")

# 判斷 CAPTCHA 是否成功：只有成功才會出現 bsContent 連結
bscontent_link = result_soup.find("a", href=lambda h: h and "bsContent" in h)
if not bscontent_link:
    raise RuntimeError("CAPTCHA wrong, retry from Step 1")
```

---

## Step 4 — GET bsContent.aspx 取得實際資料

POST 回應本身沒有資料表格，需用同一 session GET `bsContent.aspx`，回傳逗號分隔純文字。

```python
data_r = session.get(f"{BASE}/bsContent.aspx", params={"StkNo": stock_code}, timeout=15)
data_r.encoding = "utf-8"

rows = []
for line in data_r.text.splitlines():
    if "," in line:
        rows.append(line.split(","))

for row in rows:
    print(row)
```

---

## 表單欄位一覽

| 欄位名稱 | 來源 | 說明 |
|---|---|---|
| `__VIEWSTATE` | GET 頁面 hidden input | ASP.NET 狀態（每次 GET 都不同，必須帶） |
| `__VIEWSTATEGENERATOR` | GET 頁面 hidden input | |
| `__EVENTVALIDATION` | GET 頁面 hidden input | |
| `__EVENTTARGET` | 固定空字串 `""` | |
| `__EVENTARGUMENT` | 固定空字串 `""` | |
| `__LASTFOCUS` | 固定空字串 `""` | |
| `RadioButton_Normal` | 固定 `"RadioButton_Normal"` | 一般股（預設選項） |
| `TextBox_Stkno` | 股票代號 | 最多 6 碼，例如 `2330` |
| `CaptchaControl1` | vision 讀取圖片 | 5 字元英數答案 |
| `btnOK` | 固定 `"查詢"` | 送出按鈕 |

---

## 預期輸出欄位（分點資料）

| 欄位 | 說明 |
|---|---|
| 券商代號 | 券商編號 |
| 券商名稱 | 券商分點名稱 |
| 買進股數 | 當日買進張數（股） |
| 買進金額 | 買進金額（元） |
| 賣出股數 | 當日賣出張數（股） |
| 賣出金額 | 賣出金額（元） |

> 非交易日或輸入不存在的股票代號時，結果表格為空。

---

## 注意事項

- `requests.Session()` 必須在整個流程中保持，伺服器用 Cookie 追蹤 Session
- `__VIEWSTATE` 等 ASP.NET 欄位每次 GET 都會更新，**不可重複使用舊值**
- CAPTCHA 圖片與 `__VIEWSTATE` 綁定同一 GUID，必須用同一 session 下載
- 查詢為唯讀，**不需要 Safety Mode CONFIRM**
