# BlaveClaw Strategy Marketplace API

Use Blave API credentials for all requests.
Base URL: `https://api.blave.org`
Headers: `api-key: {blave_api_key}`, `secret-key: {blave_secret_key}`

## Browse

List all available strategies:
```
GET /openclaw/marketplace/strategies
```
Response: `[{id, title, description, price, category, created_at}, ...]`

Strategy detail (includes `purchased: true/false`):
```
GET /openclaw/marketplace/strategies/{id}
```

## Load purchased strategies

List purchased strategies:
```
GET /openclaw/marketplace/my/purchases
```

Fetch strategy code (requires purchase):
```
GET /openclaw/marketplace/strategies/{id}/code
```
Response: `{"code": "..."}` — save to `.py` and run with `python3`.

**Flow when user wants to run a purchased strategy:**
1. `GET /openclaw/marketplace/my/purchases` — show the list
2. User picks one → `GET /openclaw/marketplace/strategies/{id}/code`
3. Save to `/tmp/<filename>.py`
4. **Check for multi-strategy bundle** — scan for `# ===== STRATEGY \d+:` markers:
   - If found: split into separate files and deploy each (see "Multi-strategy bundle" below)
   - If not found: `python3 filename.py`

## Submit a strategy for sale

```
POST /openclaw/marketplace/strategies/submit
Content-Type: application/json

{
  "title": "Strategy Name",
  "description": "What it does and how",
  "price": 300,
  "category": "trend",
  "code": "...full source code..."
}
```
Status starts as `pending`. Blave reviews and publishes it.

Check submission status:
```
GET /openclaw/marketplace/my/submissions
```
Response: `[{id, title, price, status, visibility, created_at}, ...]`
Status values: `pending` | `approved` | `unlisted`

## Multi-strategy bundle

**Submitting** — pack two or more strategies into one file using `# ===== STRATEGY N: <name> =====` delimiters, submit via the normal endpoint:

```python
# ===== STRATEGY 1: BTC SMA Cross =====
MODE          = "live"
STRATEGY_NAME = "btc_sma_cross"
SYMBOL        = "BTCUSDT"
# ... full strategy 1 code ...

# ===== STRATEGY 2: ETH RSI Fade =====
MODE          = "live"
STRATEGY_NAME = "eth_rsi_fade"
SYMBOL        = "ETHUSDT"
# ... full strategy 2 code ...
```

```
POST /openclaw/marketplace/strategies/submit
{"title": "BTC SMA + ETH RSI Bundle", "description": "...", "price": 500, "category": "bundle", "code": "..."}
```

In `description`, write a structured block for each strategy separated by `---`.

**Deploying** — when downloaded code contains `# ===== STRATEGY N:` markers:
1. Split at each marker into N separate strings
2. Save each to `/tmp/<name_slug>.py` (slug from the name after the colon)
3. Security scan each file separately; skip any that exit 2 (critical)
4. Move approved files to `strategies/<name_slug>.py` and run each with `python3`

## Private strategies

Upload a private strategy (no review, immediately accessible):
```
POST /openclaw/marketplace/strategies/private
Content-Type: application/json

{
  "title": "My Private Strategy",
  "description": "Optional",
  "category": "trend",
  "code": "...full source code..."
}
```
Response: `{"status": "ok", "strategy_id": 123}`

Share with specific user IDs:
```
POST /openclaw/marketplace/strategies/{id}/share
Content-Type: application/json

{"user_ids": [456, 789]}
```

Remove a user's access:
```
DELETE /openclaw/marketplace/strategies/{id}/share
Content-Type: application/json

{"user_id": 456}
```

View share list (owner only):
```
GET /openclaw/marketplace/strategies/{id}/shares
```
Response: `{"shares": [{"user_id": 456, "shared_at": "..."}]}`

View strategies shared with you:
```
GET /openclaw/marketplace/my/shared-with-me
```

Download code (works for owned, purchased, or shared strategies):
```
GET /openclaw/marketplace/strategies/{id}/code
```
Response: `{"code": "..."}` — save to `.py` and run with `python3`.
