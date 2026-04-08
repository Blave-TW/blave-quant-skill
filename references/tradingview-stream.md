# TradingView Signal Stream

## Architecture

```
TradingView Alert  →  POST /tradingview/webhook  →  Redis Stream
                                                           ↓
                                        GET /sse/tradingview/stream  →  Agent
```

1. TradingView fires an alert → sends POST to Blave webhook with your channel code
2. Blave stores the payload in a Redis Stream
3. Agent connects via SSE and receives each signal in real time
4. On disconnect, agent can reconnect with `last_id` to resume from the exact point

---

## Stream Connection

> **Webhook & channel activation:** Handled by the Blave team. Contact Blave to set up your TradingView webhook and get your channel name.

**Params:**

| Param | Required | Description |
|---|---|---|
| `channel` | ✓ | Your channel name (mapped from webhook code) |
| `last_id` | — | Redis Stream ID of last received message. Omit (or use `"$"`) to get only new signals. Pass on reconnect to resume from that point. |

**SSE event format:**
```
data: {"id": "1712054400000-0", "action": "buy", "symbol": "BTCUSD", "price": "95000"}

: keepalive
```

---

## Python: Listen for Signals

```python
import requests
import json
import time
from dotenv import dotenv_values

_env     = dotenv_values()
HEADERS  = {"api-key": _env["blave_api_key"], "secret-key": _env["blave_secret_key"]}
BASE_URL = "https://api.blave.org"
CHANNEL  = "your_channel"   # mapped name (not the raw code)


def handle_signal(data: dict):
    """Called once per TradingView alert. Put your trading logic here."""
    print(f"Signal received: {data}")
    action = data.get("action", "").lower()
    symbol = data.get("symbol", "")
    price  = data.get("price", "")

    if action == "buy":
        print(f"→ BUY {symbol} @ {price}")
        # place order here
    elif action == "sell":
        print(f"→ SELL {symbol} @ {price}")
        # place order here


def stream(channel: str, last_id: str = "$"):
    """Open SSE stream and yield (last_id, data) for each signal."""
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
                    last_id = data.get("id", last_id)   # save for reconnect
                    yield last_id, data
            # ": keepalive" lines are ignored automatically


def run():
    last_id = "$"                              # "$" = only new signals
    while True:
        try:
            print(f"Connecting to channel '{CHANNEL}' (last_id={last_id})...")
            for last_id, data in stream(CHANNEL, last_id):
                handle_signal(data)
        except Exception as e:
            print(f"Disconnected: {e} — reconnecting in 3 s...")
            time.sleep(3)                      # last_id preserved → resumes from exact point


if __name__ == "__main__":
    run()
```

---

## Notes

- **Reconnection:** Always pass `last_id` from the last received message. The Redis Stream buffers the last 1000 messages, so signals are not lost during short disconnections.
- **Keepalive:** The server sends `: keepalive` every 15 s. Your HTTP client ignores these — no special handling needed.
- **One signal per connect (test):** To grab just the next signal without looping, call `next(stream(channel))`.
- **Execution timing:** Act on the signal immediately when received, not on the next bar close — see backtest execution timing note in `examples/backtest-holder-concentration.md`.
