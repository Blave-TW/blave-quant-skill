---
name: blave-quant
description: Fetch data, backtest and trade with Blave.
---

# Blave CLI Skill

This skill provides a comprehensive interface to the `blave` command-line tool. Before executing any commands, ensure that `blave` is installed and the virtual environment is properly set up.

## 1. Fetch News

**Purpose**: Retrieve news articles using keywords with customizable language, period, and result limits.  
**When to Use**: When you want to gather recent news for analysis or strategy signals.  
**Parameters**:

- `keyword` (str) — The search term to fetch news for. **Required.**
- `max_results` (int, default=10) — Maximum number of news articles to return.
- `lang` (str, default="en") — Language of the news articles (e.g., "en" for English, "zh" for Chinese).
- `period` (str, default="7d") — Time range for news articles (e.g., "1d", "7d", "30d").
  **Execution Steps**:
- Run the `fetch_news` command with a keyword:
  ```bash
  blave fetch_news "bitcoin" --max_results 10 --lang en --period 7d
  ```
