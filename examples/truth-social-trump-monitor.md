# Example: Truth Social Trump Post Monitor

Monitor Trump's Truth Social posts, translate to Traditional Chinese via Google Translate (no LLM tokens), and push to Telegram.

Uses `trumpstruth.org/feed` RSS — works from any server (including AWS) with plain `requests`, no Cloudflare bypass needed.

---

## Dependencies

```bash
pip install deep-translator requests
```

---

## Code

```python
#!/usr/bin/env python3
"""
川普 Truth Social 監控 → 翻譯中文 → 推送 Telegram
透過 trumpstruth.org RSS Feed，每 5 分鐘執行一次（cron）
"""

import re, json, time
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import requests
from deep_translator import GoogleTranslator

# ── Config ────────────────────────────────────────────────────────────────
RSS_URL          = "https://www.trumpstruth.org/feed"
TRANSLATOR       = GoogleTranslator(source="en", target="zh-TW")
TELEGRAM_TOKEN   = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
STATE_FILE       = Path(__file__).parent / "trump_monitor_state.json"
HEADERS          = {"User-Agent": "Mozilla/5.0 (compatible; TrumpMonitor/1.0)"}


# ── Helpers ───────────────────────────────────────────────────────────────
def strip_html(html):
    text = re.sub(r"<br\s*/?>", "\n", html or "")
    text = re.sub(r"<[^>]+>", "", text)
    for old, new in [("&amp;","&"),("&lt;","<"),("&gt;",">"),("&#39;","'"),("&quot;",'"')]:
        text = text.replace(old, new)
    return text.strip()


def translate(text):
    try:
        return TRANSLATOR.translate(text) if text else ""
    except Exception:
        return text


def tg(msg):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": msg,
              "parse_mode": "Markdown", "disable_web_page_preview": True},
        timeout=10,
    )


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"seen_ids": []}


def save_state(state):
    state["seen_ids"] = state["seen_ids"][-200:]  # keep last 200 to avoid bloat
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# ── Fetch ─────────────────────────────────────────────────────────────────
def fetch_posts():
    r = requests.get(RSS_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    ns   = {"truth": "https://truthsocial.com/ns"}
    posts = []
    for item in root.findall(".//item"):
        orig_id  = item.findtext("truth:originalId", namespaces=ns)
        guid     = item.findtext("guid", "")
        post_id  = orig_id or guid.split("/")[-1]
        title    = item.findtext("title", "")
        desc     = strip_html(item.findtext("description", ""))
        pub_date = item.findtext("pubDate", "")
        orig_url = item.findtext("truth:originalUrl", namespaces=ns) or guid

        content = desc if len(desc) > len(title) else title
        content = content.strip()
        if not content or content == "[No Title]":
            continue

        try:
            dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            ts_str = dt.strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            ts_str = pub_date[:25] if pub_date else ""

        posts.append({"id": post_id, "content": content,
                      "url": orig_url, "pub_date": ts_str})
    return posts


# ── Main ──────────────────────────────────────────────────────────────────
def run():
    state    = load_state()
    seen_ids = set(state["seen_ids"])
    is_first = len(seen_ids) == 0

    posts = fetch_posts()
    if not posts:
        return

    if is_first:
        # First run: push latest 3, mark all as seen
        to_push = posts[:3]
        for p in posts:
            seen_ids.add(p["id"])
    else:
        to_push = [p for p in posts if p["id"] not in seen_ids]
        for p in to_push:
            seen_ids.add(p["id"])

    for p in reversed(to_push):  # oldest first
        zh = translate(p["content"])
        msg = (f"🇺🇸 *川普 Truth Social*\n"
               f"🕐 `{p['pub_date']}`\n\n"
               f"*🇬🇧 英文原文*\n{p['content']}\n\n"
               f"*🇹🇼 中文翻譯*\n{zh}\n\n"
               f"[原文連結]({p['url']})")
        tg(msg)
        time.sleep(1)

    state["seen_ids"] = list(seen_ids)
    save_state(state)


if __name__ == "__main__":
    run()
```

---

## Deployment

### Cron (every 5 minutes)

```bash
*/5 * * * * cd /path/to/project && python3 trump_monitor.py >> /var/log/trump_monitor.log 2>&1
```

### Systemd Timer (alternative)

```ini
# /etc/systemd/system/trump-monitor.timer
[Unit]
Description=Trump Truth Social Monitor

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
```

---

## How It Works

| Step | Detail |
|---|---|
| **Fetch** | `GET https://www.trumpstruth.org/feed` — RSS feed with `truth:originalId` and `truth:originalUrl` custom XML namespaces |
| **Dedup** | `trump_monitor_state.json` stores last 200 seen post IDs; only new posts get pushed |
| **Translate** | `deep-translator` calls Google Translate free endpoint. EN → zh-TW |
| **Push** | Telegram Bot API with Markdown formatting |
| **First run** | Pushes latest 3 posts, marks all 100 as seen so next run only gets truly new ones |

---

## Customising the Push Channel

### Slack Webhook

Replace `tg(msg)` with:

```python
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T.../B.../xxx"

def slack(msg):
    requests.post(SLACK_WEBHOOK_URL, json={"text": msg}, timeout=10)
```

### Discord Webhook

```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."

def discord(msg):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": msg}, timeout=10)
```

---

## Notes

- **RSS source:** `trumpstruth.org` is a third-party RSS mirror of Trump's Truth Social posts. It returns standard RSS XML with custom `truth:` namespace fields
- **No Cloudflare issue:** unlike Truth Social's own API, this RSS feed works with plain `requests` from any IP (including AWS/GCP)
- **Feed size:** returns ~100 most recent posts per request
- **Google Translate limit:** `deep-translator` uses the free web endpoint; at 5-min intervals this is well within limits
- **State file:** keeps last 200 IDs to prevent duplicate pushes across restarts. Safe to delete to reset
