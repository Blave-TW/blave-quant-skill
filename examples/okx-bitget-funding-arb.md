# Example: OKX × Bitget 永續合約 Funding Rate 套利

掃描兩交易所所有 USDT 永續合約的 Funding Rate 差異，找出套利機會：
- 在 Funding Rate 較低（或為負）的交易所做多
- 在 Funding Rate 較高的交易所做空
- 收取兩邊的 Funding Rate 差額，delta 完全對沖

---

## 策略邏輯

```
淨年化報酬 = |OKX_rate - Bitget_rate| × 3次/天 × 365天 - 手續費
手續費估算：taker 0.02% × 4腿 = ~0.08% 單次進出
```

Funding Rate 每 8 小時結算一次（每天 3 次）。持倉期間不承擔方向性風險。

---

## Dependencies

```bash
pip install requests python-dotenv
```

---

## Code

```python
#!/usr/bin/env python3
"""
OKX × Bitget Funding Rate 套利：
  1. 掃描兩交易所共同上市的 USDT 永續合約
  2. 計算 Funding Rate 差值與年化報酬
  3. 顯示 Top 機會
  4. 可選：執行對沖建倉
"""

import hmac, hashlib, base64, json, time, os
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from dotenv import dotenv_values

_env = dotenv_values()

# ── OKX ────────────────────────────────────────────────────────────────────
OKX_BASE   = "https://www.okx.com"
OKX_KEY    = _env.get("OKX_API_KEY", "")
OKX_SECRET = _env.get("OKX_SECRET_KEY", "")
OKX_PASS   = _env.get("OKX_PASSPHRASE", "")

def _okx_ts():
    now = datetime.now(timezone.utc)
    return now.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now.microsecond // 1000:03d}Z"

def _okx_sign(secret, ts, method, path, body=""):
    prehash = ts + method.upper() + path + body
    return base64.b64encode(
        hmac.new(secret.encode(), prehash.encode(), hashlib.sha256).digest()
    ).decode()

def _okx_auth_headers(method, path, body=""):
    ts = _okx_ts()
    return {
        "OK-ACCESS-KEY":       OKX_KEY,
        "OK-ACCESS-SIGN":      _okx_sign(OKX_SECRET, ts, method, path, body),
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-PASSPHRASE": OKX_PASS,
        "Content-Type":        "application/json",
        "User-Agent":          "Mozilla/5.0",
    }

def okx_get(path, params=None, auth=False):
    qs = ""
    if params:
        qs = "?" + "&".join(f"{k}={v}" for k, v in params.items())
    headers = _okx_auth_headers("GET", path + qs) if auth else {"User-Agent": "Mozilla/5.0"}
    r = requests.get(f"{OKX_BASE}{path}", params=params, headers=headers, timeout=10)
    data = r.json()
    if data.get("code") != "0":
        raise Exception(f"OKX error {data.get('code')}: {data.get('msg')}")
    return data.get("data", [])

def okx_post(path, body: dict):
    body_str = json.dumps(body, separators=(",", ":"))
    headers  = _okx_auth_headers("POST", path, body_str)
    r = requests.post(f"{OKX_BASE}{path}", data=body_str, headers=headers, timeout=10)
    data = r.json()
    if data.get("code") != "0":
        raise Exception(f"OKX error {data.get('code')}: {data.get('msg')}")
    return data.get("data", [])

# ── Bitget ──────────────────────────────────────────────────────────────────
BG_BASE   = "https://api.bitget.com"
BG_KEY    = _env.get("BITGET_API_KEY", "")
BG_SECRET = _env.get("BITGET_SECRET_KEY", "")
BG_PASS   = _env.get("BITGET_PASSPHRASE", "")

def _bg_sign(ts, method, path, body_str=""):
    msg = f"{ts}{method}{path}{body_str}"
    mac = hmac.new(BG_SECRET.encode(), msg.encode(), hashlib.sha256).digest()
    return base64.b64encode(mac).decode()

def _bg_headers(method, path, body_str=""):
    ts = str(int(time.time() * 1000))
    return {
        "ACCESS-KEY":        BG_KEY,
        "ACCESS-SIGN":       _bg_sign(ts, method, path, body_str),
        "ACCESS-PASSPHRASE": BG_PASS,
        "ACCESS-TIMESTAMP":  ts,
        "Content-Type":      "application/json",
        "locale":            "en-US",
    }

def bg_get(path, params=None, auth=False):
    qs = ""
    if params:
        qs = "?" + "&".join(f"{k}={v}" for k, v in params.items())
    headers = _bg_headers("GET", path + qs) if auth else {}
    r = requests.get(f"{BG_BASE}{path}", params=params, headers=headers, timeout=10)
    data = r.json()
    if data.get("code") != "00000":
        raise Exception(f"Bitget error {data.get('code')}: {data.get('msg')}")
    return data.get("data")

def bg_post(path, body: dict):
    body_str = json.dumps(body, separators=(",", ":"))
    headers  = _bg_headers("POST", path, body_str)
    r = requests.post(f"{BG_BASE}{path}", data=body_str, headers=headers, timeout=10)
    data = r.json()
    if data.get("code") != "00000":
        raise Exception(f"Bitget error {data.get('code')}: {data.get('msg')}")
    return data.get("data")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: 掃描 Funding Rate
# ═══════════════════════════════════════════════════════════════════════════

def get_okx_instruments() -> set[str]:
    """取得 OKX 所有 USDT 永續合約的 base symbol，如 BTC, ETH, SOL"""
    items = okx_get("/api/v5/public/instruments", {"instType": "SWAP"})
    symbols = set()
    for i in items:
        inst = i.get("instId", "")  # BTC-USDT-SWAP
        if inst.endswith("-USDT-SWAP"):
            symbols.add(inst.replace("-USDT-SWAP", ""))
    return symbols

def get_bitget_instruments() -> set[str]:
    """取得 Bitget 所有 USDT 永續合約的 base symbol"""
    items = bg_get("/api/v2/mix/market/tickers", {"productType": "USDT-FUTURES"})
    symbols = set()
    for i in (items or []):
        sym = i.get("symbol", "")  # BTCUSDT
        if sym.endswith("USDT"):
            symbols.add(sym[:-4])  # 去掉 USDT
    return symbols

def fetch_okx_funding(base: str) -> dict | None:
    """抓取單個幣種的 OKX Funding Rate"""
    try:
        inst_id = f"{base}-USDT-SWAP"
        data = okx_get("/api/v5/public/funding-rate", {"instId": inst_id})
        if not data:
            return None
        d = data[0]
        return {
            "symbol":       base,
            "rate":         float(d.get("fundingRate", 0)),
            "next_rate":    float(d.get("nextFundingRate", 0)),
            "funding_time": int(d.get("fundingTime", 0)),
        }
    except Exception:
        return None

def fetch_bitget_funding(base: str) -> dict | None:
    """抓取單個幣種的 Bitget Funding Rate"""
    try:
        symbol = f"{base}USDT"
        data = bg_get("/api/v2/mix/market/current-fund-rate",
                      {"symbol": symbol, "productType": "USDT-FUTURES"})
        if not data:
            return None
        return {
            "symbol":    base,
            "rate":      float(data[0].get("fundingRate", 0)),
            "next_time": int(data[0].get("nextUpdate", 0)),
        }
    except Exception:
        return None

def scan_opportunities(top_n: int = 20) -> list[dict]:
    """
    掃描兩交易所共同上市幣種的 Funding Rate 差值，回傳排序後的套利機會清單。
    每次 Funding 間隔 8h，每天 3 次。
    """
    print("正在取得上市合約清單...")
    okx_syms    = get_okx_instruments()
    bitget_syms = get_bitget_instruments()
    common      = sorted(okx_syms & bitget_syms)
    print(f"OKX: {len(okx_syms)} | Bitget: {len(bitget_syms)} | 共同: {len(common)}")

    okx_rates    = {}
    bitget_rates = {}

    print(f"並行抓取 {len(common)} 個幣種的 Funding Rate...")
    with ThreadPoolExecutor(max_workers=20) as ex:
        okx_futs = {ex.submit(fetch_okx_funding, s): s for s in common}
        bg_futs  = {ex.submit(fetch_bitget_funding, s): s for s in common}

        for f in as_completed(okx_futs):
            res = f.result()
            if res:
                okx_rates[res["symbol"]] = res

        for f in as_completed(bg_futs):
            res = f.result()
            if res:
                bitget_rates[res["symbol"]] = res

    opportunities = []
    for sym in common:
        if sym not in okx_rates or sym not in bitget_rates:
            continue
        okx_r = okx_rates[sym]["rate"]
        bg_r  = bitget_rates[sym]["rate"]
        spread = okx_r - bg_r  # 正值 = OKX 高, 負值 = Bitget 高

        # 套利方向
        if spread > 0:
            long_ex, short_ex = "Bitget", "OKX"
            long_rate, short_rate = bg_r, okx_r
        else:
            long_ex, short_ex = "OKX", "Bitget"
            long_rate, short_rate = okx_r, bg_r

        abs_spread = abs(spread)
        annual_pct = abs_spread * 3 * 365 * 100  # 年化 %

        opportunities.append({
            "symbol":       sym,
            "okx_rate":     okx_r,
            "bitget_rate":  bg_r,
            "spread":       abs_spread,
            "annual_pct":   annual_pct,
            "long_ex":      long_ex,
            "short_ex":     short_ex,
            "long_rate":    long_rate,
            "short_rate":   short_rate,
        })

    opportunities.sort(key=lambda x: x["annual_pct"], reverse=True)
    return opportunities[:top_n]

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: 顯示機會表格
# ═══════════════════════════════════════════════════════════════════════════

def display_opportunities(opps: list[dict]):
    print(f"\n{'─'*90}")
    print(f"{'幣種':<8} {'OKX Rate':>10} {'Bitget Rate':>12} {'Spread':>9} "
          f"{'年化報酬':>10}  做多@          做空@")
    print(f"{'─'*90}")

    for o in opps:
        print(
            f"{o['symbol']:<8} "
            f"{o['okx_rate']*100:>9.4f}%  "
            f"{o['bitget_rate']*100:>10.4f}%  "
            f"{o['spread']*100:>8.4f}%  "
            f"{o['annual_pct']:>8.1f}%  "
            f"  {o['long_ex']:<8} "
            f"  {o['short_ex']}"
        )

    print(f"{'─'*90}")
    print("注意：年化報酬未扣除手續費（Taker 約 0.08% 四腿）\n")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: 執行建倉（對沖）
# ═══════════════════════════════════════════════════════════════════════════

def get_okx_contract_info(base: str) -> dict:
    """取得 OKX 合約規格：ctVal, lotSz, minSz"""
    inst_id = f"{base}-USDT-SWAP"
    data = okx_get("/api/v5/public/instruments",
                   {"instType": "SWAP", "instId": inst_id})
    if not data:
        raise ValueError(f"找不到 OKX 合約: {inst_id}")
    d = data[0]
    return {
        "ctVal":  float(d["ctVal"]),
        "lotSz":  float(d["lotSz"]),
        "minSz":  float(d["minSz"]),
    }

def get_okx_price(base: str) -> float:
    data = okx_get("/api/v5/market/ticker", {"instId": f"{base}-USDT-SWAP"})
    return float(data[0]["last"])

def get_bitget_price(base: str) -> float:
    data = bg_get("/api/v2/mix/market/ticker",
                  {"symbol": f"{base}USDT", "productType": "USDT-FUTURES"})
    return float(data[0]["lastPr"])

def open_okx_swap(base: str, side: str, usd_notional: float, leverage: int = 3):
    """
    OKX 開倉永續合約。
    side: 'long' 或 'short'
    """
    inst_id  = f"{base}-USDT-SWAP"
    contract = get_okx_contract_info(base)
    price    = get_okx_price(base)

    raw_contracts = usd_notional / (price * contract["ctVal"])
    lot = contract["lotSz"]
    contracts = max(contract["minSz"], (raw_contracts // lot) * lot)

    # 設定槓桿（cross 模式）
    okx_post("/api/v5/account/set-leverage", {
        "instId":  inst_id,
        "lever":   str(leverage),
        "mgnMode": "cross",
        "tag":     "96ee7de3fd4bBCDE",  # broker tag 雖然 set-leverage 不是 order，保留無害
    })

    body = {
        "instId":  inst_id,
        "tdMode":  "cross",
        "side":    "buy" if side == "long" else "sell",
        "posSide": side,
        "ordType": "market",
        "sz":      str(int(contracts)),
        "tag":     "96ee7de3fd4bBCDE",
    }
    result = okx_post("/api/v5/trade/order", body)
    return result[0] if result else {}

def open_bitget_perp(base: str, side: str, usd_notional: float, leverage: int = 3):
    """
    Bitget 開倉永續合約。
    side: 'long' 或 'short'
    """
    symbol = f"{base}USDT"
    price  = get_bitget_price(base)
    size   = round(usd_notional / price, 4)  # base 數量，取 4 位

    # 設定槓桿與保證金模式
    bg_post("/api/v2/mix/account/set-leverage", {
        "symbol":      symbol,
        "productType": "USDT-FUTURES",
        "marginCoin":  "USDT",
        "leverage":    str(leverage),
        "holdSide":    side,
    })
    bg_post("/api/v2/mix/account/set-margin-mode", {
        "symbol":      symbol,
        "productType": "USDT-FUTURES",
        "marginCoin":  "USDT",
        "marginMode":  "crossed",
    })

    body = {
        "symbol":      symbol,
        "productType": "USDT-FUTURES",
        "marginMode":  "crossed",
        "marginCoin":  "USDT",
        "size":        str(size),
        "side":        "buy" if side == "long" else "sell",
        "tradeSide":   "open",
        "orderType":   "market",
        "leverage":    str(leverage),
    }
    return bg_post("/api/v2/mix/order/place-order", body)

def execute_arb(opp: dict, usd_per_leg: float = 500, leverage: int = 3):
    """
    對最佳機會執行雙邊建倉。
    opp: scan_opportunities() 回傳的單筆機會
    usd_per_leg: 每腿名義金額（USD）
    """
    sym      = opp["symbol"]
    long_ex  = opp["long_ex"]
    short_ex = opp["short_ex"]

    print(f"\n建立 {sym} 套利倉位 ({usd_per_leg} USD/腿, {leverage}x):")
    print(f"  做多 @ {long_ex}  (Funding: {opp['long_rate']*100:.4f}%)")
    print(f"  做空 @ {short_ex} (Funding: {opp['short_rate']*100:.4f}%)")
    print(f"  預期年化: {opp['annual_pct']:.1f}%\n")

    results = {}
    if long_ex == "OKX":
        results["okx_long"]     = open_okx_swap(sym, "long",  usd_per_leg, leverage)
        results["bitget_short"] = open_bitget_perp(sym, "short", usd_per_leg, leverage)
    else:
        results["bitget_long"] = open_bitget_perp(sym, "long",  usd_per_leg, leverage)
        results["okx_short"]   = open_okx_swap(sym, "short", usd_per_leg, leverage)

    print("建倉完成：")
    for k, v in results.items():
        print(f"  {k}: {v}")
    return results

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 1. 掃描機會
    opps = scan_opportunities(top_n=20)
    display_opportunities(opps)

    if not opps:
        print("目前無顯著套利機會。")
        exit()

    best = opps[0]
    print(f"最佳機會：{best['symbol']}  年化 {best['annual_pct']:.1f}%")
    print(f"  做多 @ {best['long_ex']}  ({best['long_rate']*100:.4f}%)")
    print(f"  做空 @ {best['short_ex']} ({best['short_rate']*100:.4f}%)")

    # 2. 執行建倉（取消下方注釋並輸入 CONFIRM 執行）
    # confirm = input("\n輸入 CONFIRM 執行建倉，其他鍵跳過: ").strip()
    # if confirm == "CONFIRM":
    #     execute_arb(best, usd_per_leg=500, leverage=3)
    # else:
    #     print("已跳過執行。")
```

---

## 範例輸出

```
正在取得上市合約清單...
OKX: 312 | Bitget: 287 | 共同: 241
並行抓取 241 個幣種的 Funding Rate...

──────────────────────────────────────────────────────────────────────────────────────────
幣種     OKX Rate   Bitget Rate    Spread     年化報酬  做多@          做空@
──────────────────────────────────────────────────────────────────────────────────────────
WIF      -0.0250%      0.0100%    0.0350%      38.3%    OKX       Bitget
BONK      0.0800%     -0.0100%    0.0900%      98.6%    Bitget    OKX
SOL       0.0100%      0.0420%    0.0320%      35.0%    OKX       Bitget
BTC       0.0100%      0.0300%    0.0200%      21.9%    OKX       Bitget
ETH       0.0080%      0.0250%    0.0170%      18.6%    OKX       Bitget
...
──────────────────────────────────────────────────────────────────────────────────────────
注意：年化報酬未扣除手續費（Taker 約 0.08% 四腿）
```

---

## 注意事項

| 項目 | 說明 |
|---|---|
| Funding Rate 波動 | 建倉後利差可能縮窄或反轉，需設定停損閾值 |
| 滑價風險 | 市價單在流動性低的幣種可能有較大滑點，建議用限價 |
| 價差風險 | 兩交易所價格不完全一致，建倉時需快速同步下單 |
| 保證金管理 | 兩邊各需維持足夠保證金，建議使用 cross 模式且不過度槓桿 |
| 到期前平倉 | 在下次 Funding 結算後可評估是否繼續持有或平倉 |
