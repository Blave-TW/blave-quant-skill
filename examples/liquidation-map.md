# Example: Liquidation Map (爆倉地圖)

**爆倉地圖（Liquidation Map）** 顯示合約市場交易者持倉的潛在爆倉價位區間與爆倉量。爆倉地圖是根據整合價格走勢、交易員持倉與槓桿率統計出整體市場的多空持倉分佈與潛在的清算風險，當市場上漲或下跌至爆倉價位時，交易員部位會被強制平倉。

**爆倉地圖變化（Liquidation Map Change）** 主要呈現不同時間段建立的交易員持倉（爆倉柱），從 0–1 小時到 8–24 小時以不同顏色顯示。可以通過觀察不同時間段建立的爆倉柱來觀察行情接下來的發展方向。

Two charts are generated:
1. **Liquidation Heatmap** — OI distribution + 24h long/short liquidation exposure at each price level + cumulative exposure line
2. **Liquidation Map Change** — 不同時間段建立的爆倉點位 (0–1h / 1–8h / 8–24h)

---

## Full Code

```python
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import dotenv_values

_env = dotenv_values()

SYMBOL  = "BTCUSDT"
BASE    = "https://api.blave.org"
HEADERS = {"api-key": _env["blave_api_key"], "secret-key": _env["blave_secret_key"]}


def fetch(path, params=None):
    r = requests.get(f"{BASE}/{path}", headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()["data"]


# ── Fetch ─────────────────────────────────────────────────────────────────────
map_data    = fetch("liquidation/get_map",        {"symbol": SYMBOL})
change_data = fetch("liquidation/get_map_change", {"symbol": SYMBOL})

labels   = np.array(map_data["labels"],   dtype=float)
cumsum   = np.array(map_data["cumsum"],   dtype=float)
oi_val   = np.array(map_data["oi_value"], dtype=float)
price    = float(map_data["price"])

liq_24h  = map_data.get("liquidation", {}).get("24h", {})
buy_liq  = np.array(liq_24h.get("buy_liq",  [0] * len(labels)), dtype=float)
sell_liq = np.array(liq_24h.get("sell_liq", [0] * len(labels)), dtype=float)

ch_labels = np.array(change_data["labels"], dtype=float)
ch_price  = float(change_data["price"])
hist_1h   = np.array(change_data["hist_0_1h"],  dtype=float)
hist_8h   = np.array(change_data["hist_1_8h"],  dtype=float)
hist_24h  = np.array(change_data["hist_8_24h"], dtype=float)

bar_w    = (labels[1]    - labels[0])    * 0.85
ch_bar_w = (ch_labels[1] - ch_labels[0]) * 0.85


# ── Chart helpers ─────────────────────────────────────────────────────────────
BG     = "#161b22"
GRID   = "#30363d"
TEXT   = "#c9d1d9"
ORANGE = "#ff9960"
RED    = "#e55c5c"
GREEN  = "#a6d16c"
GREY   = "#8b949e"

def fmt_m(x, _=None):
    if abs(x) >= 1e9: return f"{x/1e9:.1f}B"
    if abs(x) >= 1e6: return f"{x/1e6:.1f}M"
    if abs(x) >= 1e3: return f"{x/1e3:.0f}K"
    return f"{x:.0f}"

def fmt_price(x, _=None):
    if x <= labels[0] or x >= labels[-1]: return ""
    return f"{x:,.0f}"


# ── Chart 1: get_map ──────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(20, 7), facecolor=BG)
fig.suptitle(f"{SYMBOL} — Liquidation Map", fontsize=14, fontweight="bold",
             color=TEXT, y=1.01)

ax_bar = axes[0]
ax_cum = ax_bar.twinx()
ax_bar.set_facecolor(BG)

# OI bars (right axis)
ax_bar.bar(labels, oi_val, width=bar_w, color=GREY, alpha=0.55, label="OI", zorder=2)

# Long liq (buy_liq) exposure stacked on OI
ax_bar.bar(labels, buy_liq, width=bar_w, bottom=oi_val,
           color=GREEN, alpha=0.9, label="Long Liq", zorder=3)

# Short liq (sell_liq) exposure on top
ax_bar.bar(labels, sell_liq, width=bar_w, bottom=oi_val + buy_liq,
           color=RED, alpha=0.9, label="Short Liq", zorder=3)

# Cumsum line — red below price, green above (left axis)
if labels[0] < price < labels[-1]:
    cum_at_price = float(np.interp(price, labels, cumsum))
    mask_lo = labels <= price
    x_lo = np.append(labels[mask_lo], price)
    y_lo = np.append(cumsum[mask_lo], cum_at_price)
    ax_cum.plot(x_lo, y_lo, color=RED, lw=1.8, zorder=5)
    ax_cum.fill_between(x_lo, y_lo, alpha=0.12, color=RED)
    mask_hi = labels >= price
    x_hi = np.insert(labels[mask_hi], 0, price)
    y_hi = np.insert(cumsum[mask_hi], 0, cum_at_price)
    ax_cum.plot(x_hi, y_hi, color=GREEN, lw=1.8, zorder=5, label="Cumulative")
    ax_cum.fill_between(x_hi, y_hi, alpha=0.12, color=GREEN)
else:
    ax_cum.plot(labels, cumsum, color=GREEN, lw=1.8, zorder=5, label="Cumulative")
    ax_cum.fill_between(labels, cumsum, alpha=0.12, color=GREEN)

# Price annotation
ax_bar.axvline(price, color=ORANGE, lw=2, ls="--", zorder=6)
y_anno = oi_val.max() * 0.95 if oi_val.max() > 0 else 1
ax_bar.text(price, y_anno, f"  ${price:,.0f}", color=ORANGE, fontsize=10,
            va="top", zorder=7)

ax_bar.set_xlim(labels[0], labels[-1])
ax_bar.set_xlabel("Price", color=TEXT, fontsize=11)
ax_bar.set_ylabel("OI / Liq Exposure (USD)", color=TEXT, fontsize=10)
ax_cum.set_ylabel("Cumulative Liq Exposure", color=TEXT, fontsize=10)
ax_bar.set_title("Liquidation Heatmap\nOI + 24h Exposure", color=TEXT, fontsize=11)
ax_bar.tick_params(colors=TEXT)
ax_cum.tick_params(colors=TEXT)
ax_bar.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax_cum.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax_bar.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_price))
for sp in ax_bar.spines.values(): sp.set_color(GRID)
for sp in ax_cum.spines.values(): sp.set_color(GRID)
ax_bar.tick_params(axis="x", rotation=30)

lines1, lbl1 = ax_bar.get_legend_handles_labels()
lines2, lbl2 = ax_cum.get_legend_handles_labels()
ax_bar.legend(lines1 + lines2, lbl1 + lbl2,
              fontsize=9, facecolor="#21262d", labelcolor=TEXT, loc="upper left")


# ── Chart 2: get_map_change ───────────────────────────────────────────────────
ax2 = axes[1]
ax2.set_facecolor(BG)

ax2.bar(ch_labels, hist_24h, width=ch_bar_w, color=RED,   alpha=0.50, label="8h–24h", zorder=2)
ax2.bar(ch_labels, hist_8h,  width=ch_bar_w, color=GREEN, alpha=0.75, label="1h–8h",  zorder=3)
ax2.bar(ch_labels, hist_1h,  width=ch_bar_w, color=TEXT,  alpha=0.95, label="0–1h",   zorder=4)

ax2.axvline(ch_price, color=ORANGE, lw=2, ls="--", zorder=6)
y_top = max(hist_24h.max(), hist_8h.max(), hist_1h.max(), 1)
ax2.text(ch_price, y_top * 0.95, f"  ${ch_price:,.0f}", color=ORANGE, fontsize=10,
         va="top", zorder=7)

ax2.set_xlim(ch_labels[0], ch_labels[-1])
ax2.set_xlabel("Price", color=TEXT, fontsize=11)
ax2.set_ylabel("Liquidated (USD)", color=TEXT, fontsize=10)
ax2.set_title("Recent Liquidation Events\nby Time Window", color=TEXT, fontsize=11)
ax2.tick_params(colors=TEXT)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_price))
for sp in ax2.spines.values(): sp.set_color(GRID)
ax2.tick_params(axis="x", rotation=30)
ax2.legend(fontsize=9, facecolor="#21262d", labelcolor=TEXT, loc="upper left")


# ── Save ──────────────────────────────────────────────────────────────────────
plt.tight_layout()
fname = f"{SYMBOL.lower()}_liquidation_map.png"
plt.savefig(fname, dpi=150, bbox_inches="tight", facecolor=BG)
plt.show()
print(f"Saved: {fname}")
```

---

## Output Interpretation

### Chart 1 — Liquidation Heatmap

| Element | Meaning |
|---|---|
| Grey bars | Open interest (USD) at each price level — where leveraged positions are concentrated |
| Green bars | Long liquidation exposure — positions that get liquidated if price drops to this level |
| Red bars | Short liquidation exposure — positions that get liquidated if price rises to this level |
| Green line (above price) | Cumulative liq exposure — total exposure to the right of current price |
| Red line (below price) | Cumulative liq exposure — total exposure to the left of current price |
| Orange dashed line | Current price |

**Key insight:** Large green bars below current price = big long liquidation clusters. If price drops to those levels, a cascade of forced selling can accelerate the move down. Large red bars above price = short squeeze clusters.

### Chart 2 — Liquidation Map Change (爆倉地圖變化)

呈現不同時間段建立的爆倉柱，每根柱代表該價格區間在對應時段內的爆倉金額。可通過觀察不同時間段的爆倉柱分布，判斷行情接下來的發展方向。

| Bar | Meaning |
|---|---|
| White (0–1h) | 最近 1 小時內在該點位發生的爆倉 |
| Green (1–8h) | 1–8 小時前在該點位發生的爆倉 |
| Red (8–24h) | 8–24 小時前在該點位發生的爆倉 |

**Key insight:** 白色柱密集的區間代表剛剛發生大規模爆倉，市場正在主動清算該點位的槓桿倉位，可能引發短線反向行情。紅色柱代表較早前已被清洗過的點位，再次經過時阻力相對較低。

---

## Notes

- `get_map` shows **pending exposure** (what could happen). `get_map_change` shows **what already happened**.
- `price_min` / `price_max` optional params let you zoom into a specific price range.
- Re-run before key technical levels or news events to see if clusters have shifted.
