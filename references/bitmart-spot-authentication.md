# BitMart Spot API Authentication Guide

## 1. Getting API Credentials

### Step-by-Step

1. Log in to [BitMart](https://www.bitmart.com)
2. Navigate to **Account** → **API Management** (or go directly to [https://www.bitmart.com/api-config/en](https://www.bitmart.com/api-config/en))
3. Click **Create API Key**
4. Set a **label** for your API key (e.g., "AI Trading Bot")
5. Enter your **memo** — this is a passphrase you choose (required for signature generation)
6. Set **permissions**:
   - **Read-Only** — Required for balance and order queries
   - **Spot Trade** — Required for placing and canceling orders
   - Do NOT enable **Withdraw** permission unless absolutely necessary
7. (Recommended) Set **IP whitelist** to restrict API access to your server's IP
8. Complete 2FA verification
9. Save your credentials securely:
   - **API Key** (also called Access Key)
   - **Secret Key**
   - **Memo** (the passphrase you entered)

**Important:** The Secret Key is shown only once. Save it immediately. If lost, you must delete and recreate the API key.

---

## 2. Environment Variables Setup

Add the following to your `.env` file:

```
BITMART_API_KEY=your-api-key
BITMART_API_SECRET=your-secret-key
BITMART_API_MEMO=your-memo
```

**Security:** Never display the full secret key or memo.

---

## 3. Signature Generation

BitMart uses HMAC-SHA256 signatures for authenticated (SIGNED) API calls.

### Signature Formula

```
message   = "{timestamp}#{memo}#{body}"
signature = HMAC-SHA256(secret_key, message) → hex string
```

Where:
- `timestamp` — Current UTC time in milliseconds (e.g., `1709971200000`)
- `memo` — Your API memo string
- `body` — JSON body string for POST requests, or empty string `""` for GET requests
- The `#` character is a literal separator

### Example: POST Request Signature

For a limit buy order:

```bash
# Step 1: Set timestamp
TIMESTAMP=$(date +%s000)
# Example: 1709971200000

# Step 2: Define JSON body
BODY='{"symbol":"BTC_USDT","side":"buy","type":"limit","size":"0.001","price":"60000"}'

# Step 3: Build message string
# Format: {timestamp}#{memo}#{body}
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}"
# Example: 1709971200000#my_memo#{"symbol":"BTC_USDT","side":"buy","type":"limit","size":"0.001","price":"60000"}

# Step 4: Generate HMAC-SHA256 signature
SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
# Result: a hex string like "a1b2c3d4e5f6..."
```

### Example: GET Request Signature

For GET requests, the body portion is an empty string:

```bash
TIMESTAMP=$(date +%s000)

# For GET: body is empty, so message is "{timestamp}#{memo}#"
MESSAGE="${TIMESTAMP}#${BITMART_API_MEMO}#"

SIGN=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
```

### Required Headers

| Header | Value | When |
|--------|-------|------|
| `X-BM-KEY` | Your API key | KEYED and SIGNED |
| `X-BM-SIGN` | Hex HMAC-SHA256 signature | SIGNED only |
| `X-BM-TIMESTAMP` | UTC milliseconds timestamp | SIGNED only |
| `Content-Type` | `application/json` | POST requests |

---

## 5. Verification

Test your credentials with a simple balance query.

### KEYED Verification (simplest)

```bash
curl -s -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  'https://api-cloud.bitmart.com/account/v1/wallet' | python3 -m json.tool
```

Expected successful response:

```json
{
  "code": 1000,
  "message": "OK",
  "trace": "...",
  "data": {
    "wallet": [...]
  }
}
```

### SIGNED Verification (full auth test)

```bash
TIMESTAMP=$(date +%s000)
BODY='{}'
SIGN=$(echo -n "${TIMESTAMP}#${BITMART_API_MEMO}#${BODY}" | openssl dgst -sha256 -hmac "$BITMART_API_SECRET" | awk '{print $NF}')
curl -s -X POST 'https://api-cloud.bitmart.com/spot/v4/query/open-orders' \
  -H "User-Agent: bitmart-skills/spot/v2026.3.23" \
  -H "X-BM-BROKER-ID: BlaveData666666" \
  -H "Content-Type: application/json" \
  -H "X-BM-KEY: $BITMART_API_KEY" \
  -H "X-BM-SIGN: $SIGN" \
  -H "X-BM-TIMESTAMP: $TIMESTAMP" \
  -d "$BODY" | python3 -m json.tool
```

If `code` is `1000`, your credentials are working correctly.

---

## 6. Troubleshooting

| Error Code | Message | Cause | Fix |
|------------|---------|-------|-----|
| 30002 | `X-BM-KEY not found` | API key header missing or empty | Verify `BITMART_API_KEY` env var is set. Check for typos in the header name `X-BM-KEY`. |
| 30005 | `X-BM-SIGN is wrong` | Signature mismatch | 1) Verify memo matches exactly what you set on BitMart. 2) Ensure timestamp is in milliseconds. 3) For POST: body JSON must match exactly (no extra spaces). 4) For GET: body must be empty string. |
| 30006 | `X-BM-TIMESTAMP is wrong` | `X-BM-TIMESTAMP` header missing or empty | Ensure `X-BM-TIMESTAMP` is present on signed requests and uses Unix milliseconds (for example `date +%s000`). |
| 30007 | `Timestamp/recvWindow validation failed` | Timestamp is outside the allowed `recvWindow`, or `recvWindow` is invalid | Sync your system clock, send `X-BM-TIMESTAMP` in Unix milliseconds, and for v4 endpoints ensure `recvWindow` is a Long in `(0,60000]` (default `5000`, max `60000`). Treat `recvWindow` as the effective validity window for current signed v4 requests. |
| 30010 | `IP forbidden` | Request IP not in whitelist | Add your current IP to the API key whitelist on BitMart, or remove IP restriction for testing. |
| 30011 | `No permission` | API key lacks required permission | Enable the required permission (Read-Only, Spot Trade) in API Management. |

### Common Pitfalls

1. **Memo mismatch**: The memo in your signature must match exactly what you entered when creating the API key. It is case-sensitive.

2. **Timestamp drift / recvWindow mismatch**: For signed v4 requests, BitMart validates `X-BM-TIMESTAMP` against `recvWindow` (default `5000ms`, maximum `60000ms`). In practice, use `recvWindow` as the request-validity source of truth. Keep your system clock synchronized, and increase `recvWindow` only when necessary:
   ```bash
   # macOS
   sudo sntp -sS time.apple.com

   # Linux
   sudo ntpdate pool.ntp.org
   ```

3. **Body formatting**: For POST requests, the JSON body used in the signature must be exactly the same string sent in the request. Do not add whitespace or reorder keys between signature generation and the actual request.

4. **Empty body for GET**: When signing GET requests, the body portion of the message is an empty string (not `"{}"`, not `null` — just `""`). The message format is: `{timestamp}#{memo}#`

5. **URL encoding**: Query parameters in GET requests are NOT included in the signature. Only the body is signed.
