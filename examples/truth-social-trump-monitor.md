# Example: Truth Social Trump Post Monitor

Monitor Trump's Truth Social posts in real time, translate to Traditional Chinese via Google Translate (no LLM tokens), and push new posts.

---

## Dependencies

```bash
pip install curl-cffi deep-translator
```

- **curl_cffi** — TLS fingerprint impersonation to bypass Cloudflare (required; plain `requests` gets 403)
- **deep-translator** — free Google Translate wrapper, no API key needed

---

## Code

```python
import re
import time
import json
from curl_cffi import requests as cf_requests
from deep_translator import GoogleTranslator

# ── Config ──────────────────────────────────────────────────────────────────
ACCOUNT_ID   = "107780257626128497"   # @realDonaldTrump
POLL_SECONDS = 60                      # check every 60s
IMPERSONATE  = "chrome110"             # TLS fingerprint that passes Cloudflare
BASE         = "https://truthsocial.com/api/v1"
TRANSLATOR   = GoogleTranslator(source="en", target="zh-TW")


# ── Helpers ─────────────────────────────────────────────────────────────────
def strip_html(html: str) -> str:
    """Remove HTML tags, convert <br> to newline, decode entities."""
    text = re.sub(r"<br\s*/?>", "\n", html)
    text = re.sub(r"<[^>]+>", "", text)
    for old, new in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                     ("&#39;", "'"), ("&quot;", '"')]:
        text = text.replace(old, new)
    return text.strip()


def translate(text: str) -> str:
    """Translate to zh-TW via Google Translate. Returns original on failure."""
    if not text:
        return ""
    try:
        return TRANSLATOR.translate(text)
    except Exception:
        return text


def push_message(post: dict):
    """
    Send the translated post to your notification channel.
    Replace this with your actual push logic (Telegram, Slack, webhook, etc.)
    """
    print("=" * 60)
    print(f"[{post['created_at']}]")
    print(f"{post['content_en']}")
    print()
    print(f"{post['content_zh']}")
    print(f"-- Reblogs: {post['reblogs']} | Favourites: {post['favourites']}")
    print(f"-- https://truthsocial.com/@realDonaldTrump/{post['id']}")
    print("=" * 60)
    print()


# ── Fetch ───────────────────────────────────────────────────────────────────
def fetch_posts(session, since_id=None, limit=20):
    """Fetch latest posts. Returns list of dicts, newest first."""
    params = {"limit": limit, "exclude_replies": "true"}
    if since_id:
        params["since_id"] = since_id

    r = session.get(
        f"{BASE}/accounts/{ACCOUNT_ID}/statuses",
        params=params,
        headers={"Accept": "application/json", "Referer": "https://truthsocial.com/"},
    )
    r.raise_for_status()
    raw = r.json()

    posts = []
    for p in raw:
        content = strip_html(p.get("content", ""))
        if not content:
            continue  # skip image/video-only posts
        posts.append({
            "id":         p["id"],
            "created_at": p["created_at"],
            "content_en": content,
            "content_zh": "",
            "reblogs":    p.get("reblogs_count", 0),
            "favourites": p.get("favourites_count", 0),
        })
    return posts


# ── Main Loop ───────────────────────────────────────────────────────────────
def run():
    session = cf_requests.Session(impersonate=IMPERSONATE)
    last_id = None

    # First run: fetch latest 5 and display them
    posts = fetch_posts(session, limit=5)
    if posts:
        last_id = posts[0]["id"]
        for p in reversed(posts):  # oldest first
            p["content_zh"] = translate(p["content_en"])
            push_message(p)

    # Poll loop
    while True:
        time.sleep(POLL_SECONDS)
        try:
            new_posts = fetch_posts(session, since_id=last_id)
            if not new_posts:
                continue
            last_id = new_posts[0]["id"]
            for p in reversed(new_posts):  # oldest first
                p["content_zh"] = translate(p["content_en"])
                push_message(p)
        except Exception as e:
            print(f"Error: {e} — retrying in {POLL_SECONDS}s")


if __name__ == "__main__":
    run()
```

---

## How It Works

| Step | Detail |
|---|---|
| **Fetch** | `GET /api/v1/accounts/{id}/statuses` via Mastodon-compatible API. `since_id` param ensures only new posts are returned on subsequent polls |
| **Translate** | `deep-translator` calls Google Translate web API (free, no key). EN → zh-TW |
| **Push** | `push_message()` — replace with your Telegram bot / Slack webhook / any channel |
| **Anti-block** | `curl_cffi` with `impersonate="chrome110"` matches Chrome's TLS fingerprint. Plain `requests` gets Cloudflare 403 |

---

## Customising the Push Channel

### Telegram Bot

```python
import requests as std_requests

TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID   = "your_chat_id"

def push_message(post: dict):
    text = (
        f"*{post['created_at']}*\n\n"
        f"{post['content_en']}\n\n"
        f"---\n"
        f"{post['content_zh']}\n\n"
        f"[Link](https://truthsocial.com/@realDonaldTrump/{post['id']})"
    )
    std_requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"},
    )
```

### Slack Webhook

```python
import requests as std_requests

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T.../B.../xxx"

def push_message(post: dict):
    std_requests.post(SLACK_WEBHOOK_URL, json={
        "text": f"{post['created_at']}\n{post['content_en']}\n\n{post['content_zh']}"
    })
```

---

## Notes

- **Rate limit:** Truth Social has no documented rate limit, but polling faster than every 30s is aggressive. 60s is safe
- **Cloudflare:** if `chrome110` stops working, try `chrome`, `chrome120`, `safari`, or `safari15_5`
- **Google Translate limit:** `deep-translator` uses the free web endpoint; extremely heavy use (thousands of calls/hour) may trigger temporary IP blocks. At 1 call per minute this is not a concern
- **Empty posts:** posts with only images/videos have empty `content` and are skipped. If you want media posts too, check `p.get("media_attachments", [])`
- **Reblogs (retweets):** `exclude_replies=true` still includes reblogs. To filter those out, check `if p.get("reblog") is None`
