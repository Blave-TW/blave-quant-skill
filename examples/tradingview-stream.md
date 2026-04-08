# Example: Receive TradingView Signals via SSE

Listen to a TradingView alert stream in real time and act on each signal.

---

## Code

```python
import json
import time
import requests
from dotenv import dotenv_values

_env     = dotenv_values()
HEADERS  = {"api-key": _env["blave_api_key"], "secret-key": _env["blave_secret_key"]}
BASE_URL = "https://api.blave.org"
CHANNEL  = "test"


def handle_signal(data: dict):
    """Called once per TradingView alert. Put your trading logic here."""
    action = data.get("action", "").lower()
    symbol = data.get("symbol", "")
    price  = data.get("price", "")

    if action == "buy":
        print(f"→ BUY  {symbol} @ {price}")
        # place_order(symbol, "buy", ...)
    elif action == "sell":
        print(f"→ SELL {symbol} @ {price}")
        # place_order(symbol, "sell", ...)
    else:
        print(f"→ Unknown action: {data}")


def stream(channel: str, last_id: str = "$"):
    """Open SSE connection and yield (last_id, data) for each signal."""
    url    = f"{BASE_URL}/sse/tradingview/stream"
    params = {"channel": channel, "last_id": last_id}
    with requests.get(url, headers=HEADERS, params=params,
                      stream=True, timeout=None) as resp:
        resp.raise_for_status()
        buf = ""
        for chunk in resp.iter_content(chunk_size=1, decode_unicode=True):
            buf += chunk
            if buf.endswith("\n"):
                line = buf.strip()
                buf  = ""
                if line.startswith("data: "):
                    data    = json.loads(line[6:])
                    last_id = data.get("id", last_id)
                    yield last_id, data


def run():
    last_id = "$"   # only new signals; pass saved last_id on restart to replay missed ones
    while True:
        try:
            print(f"Connecting to channel '{CHANNEL}' (last_id={last_id})...")
            for last_id, data in stream(CHANNEL, last_id):
                print(f"Signal: {data}")
                handle_signal(data)
        except Exception as e:
            print(f"Disconnected: {e} — reconnecting in 3 s...")
            time.sleep(3)


if __name__ == "__main__":
    run()
```

---

## Notes

- **`last_id`** — saved automatically from each signal; passed on reconnect so no signals are missed (Redis buffers the last 1,000)
- **`last_id="$"`** — only signals arriving after the connection opens; change to a saved ID to replay from that point
- **Keepalive** — server sends `: keepalive` every 15 s; `iter_lines` ignores it automatically
- **Webhook & channel setup** — contact the Blave team to activate your channel
