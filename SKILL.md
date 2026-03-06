---
name: blave-quant
description: Fetch data, backtest, trade, and fetch news on Blave.
---

# blave-quant-skill

Fetch data, backtest, trade, and fetch news on Blave.

## When to Use

Use this skill when the user asks about:

- Fetching financial news or market news
- Searching news by keyword
- Backtesting strategies
- Trading operations on Blave

## Skills

### fetch_news

Fetch news articles from Google News.

**Parameters:**

- `keyword` (str, required) — search keyword
- `max_results` (int, optional, default=10) — max number of articles
- `lang` (str, optional, default='en') — language code
- `period` (str, optional, default='7d') — time period (e.g. 1d, 7d, 30d)

**Usage:**

```bash
python src/main.py fetch_news --keyword "TSMC" --max_results 5 --lang zh-TW
```
