# BitMart API Signature Guide

> **Credentials:** Read from `.env` — `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO`.

## Formula

```
timestamp = current UTC milliseconds
message   = "{timestamp}#{memo}#{body}"   # GET: body = ""
signature = HMAC-SHA256(secret, message) → hex
```

## Python Implementation

```python
import time, hmac, hashlib, json, os, requests

api_key    = os.environ["BITMART_API_KEY"]
api_secret = os.environ["BITMART_API_SECRET"]
memo       = os.environ["BITMART_API_MEMO"]

def sign(body_str: str):
    ts = str(int(time.time() * 1000))
    msg = f"{ts}#{memo}#{body_str}"
    sig = hmac.new(api_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
    return ts, sig

# POST — use data= not json=, and sign the exact same string
body = {"symbol": "ETHUSDT", "side": 1, "type": "market", "size": 1, "leverage": "5", "open_type": "isolated"}
body_str = json.dumps(body, separators=(",", ":"))
ts, sig = sign(body_str)

resp = requests.post(
    "https://api-cloud-v2.bitmart.com/contract/private/submit-order",
    headers={
        "Content-Type": "application/json",
        "X-BM-KEY": api_key,
        "X-BM-SIGN": sig,
        "X-BM-TIMESTAMP": ts,
        "User-Agent": "bitmart-skills/futures/v2026.3.23",
        "X-BM-BROKER-ID": "BlaveData666666",
    },
    data=body_str,
)

# GET — body is empty string ""
ts, sig = sign("")
resp = requests.get(
    "https://api-cloud-v2.bitmart.com/contract/private/position-v2",
    headers={
        "X-BM-KEY": api_key,
        "X-BM-SIGN": sig,
        "X-BM-TIMESTAMP": ts,
        "User-Agent": "bitmart-skills/futures/v2026.3.23",
        "X-BM-BROKER-ID": "BlaveData666666",
    },
)
```

## Common Mistakes

| Mistake | Correct |
|---|---|
| GET body = `"{}"` or `None` | GET body = `""` (empty string) |
| `requests.post(json=body)` | `requests.post(data=body_str)` — sign and send the exact same string |
| Timestamp in seconds | Timestamp in **milliseconds**: `int(time.time() * 1000)` |
| `hmac.new(secret, msg, ...)` without `.encode()` | `hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()` |
