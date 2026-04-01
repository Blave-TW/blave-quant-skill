# Blave Quant Skill

A skill that gives your agent three capabilities:
1. **Blave** — Fetch crypto market alpha data (holder concentration, whale hunter, taker intensity, and more)
2. **BitMart Futures** — Trade perpetual futures contracts on BitMart
3. **BitMart Spot** — Buy and sell spot assets on BitMart

## Security

This skill is **documentation only** — it contains no executable code, scripts, or binaries.

- All files are plain Markdown (`.md`)
- No `package.json`, no scripts, no dependencies
- All API calls are made directly by your agent — this skill only provides the instructions
- Your API keys stay in your local `.env` file. This skill contains no executable code and does not transmit keys itself — however, following the instructions will cause your agent to send keys to Blave, BitMart, and OKX APIs when making calls. We recommend using API keys with minimum required permissions and enabling IP whitelisting where possible.
- API request signing (HMAC-SHA256) is performed by your agent in code — the reference docs include `openssl`/`curl` shell examples for illustration only. No local shell tools are required by this skill.

You can inspect the full source at: [https://github.com/Blave-TW/blave-quant-skill](https://github.com/Blave-TW/blave-quant-skill)

---

## Install

```bash
npx skills add https://github.com/Blave-TW/blave-quant-skill
```

## Update

Just tell your agent: **"Update the blave-quant skill"** — no CLI commands needed.

---

## Setup

### Blave API

#### 1. Get a Blave API Plan

Subscribe to the **API Plan** to get API access. First-time subscribers get a **14-day free trial** (credit card required).

👉 [https://blave.org/landing/en/pricing](https://blave.org/landing/en/pricing)

#### 2. Create Your Blave API Key

👉 [https://blave.org/landing/en/api?tab=blave](https://blave.org/landing/en/api?tab=blave)

#### 3. Add Blave Credentials

Add the following to your `.env` file:

```
blave_api_key=YOUR_API_KEY
blave_secret_key=YOUR_SECRET_KEY
```

---

### BitMart API (Futures & Spot)

#### 1. Create Your BitMart API Key

1. Log in to [BitMart](https://www.bitmart.com)
2. Go to **Account → API Management**:
   👉 [https://www.bitmart.com/api-config/en](https://www.bitmart.com/api-config/en)
3. Click **Create API Key**
4. Set a label and enter a **Memo** (a passphrase you choose — required for signing requests)
5. Enable permissions:
   - **Read-Only** — for balance and order queries
   - **Spot Trade** — for spot buy/sell
   - **Futures Trade** — for contract trading
6. Complete 2FA and save your credentials:
   - **API Key**
   - **Secret Key** (shown only once — save it immediately)
   - **Memo** (the passphrase you entered)

#### 2. Add BitMart Credentials

Add the following to your `.env` file:

```
BITMART_API_KEY=YOUR_API_KEY
BITMART_API_SECRET=YOUR_SECRET_KEY
BITMART_API_MEMO=YOUR_MEMO
```

---

## Usage Examples

### Blave Market Data

- "Use Blave to check the Holder Concentration trend for BTCUSDT over the past week"
- "Use Blave to fetch the alpha table and find the top 5 coins with the highest holder concentration"
- "Use Blave to get the Whale Hunter signal for ETHUSDT using score_oi"
- "Use Blave to check the current market direction and capital shortage indicators"
- "Use Blave to fetch 1h candlestick data for BTCUSDT over the past 3 months"

---

- "用 Blave 幫我看 BTCUSDT 的籌碼集中度過去一週的趨勢"
- "用 Blave 抓 alpha table，篩選出籌碼集中度最高的前 5 個幣"
- "用 Blave 查 ETHUSDT 的巨鯨警報，score_type 用 score_oi"
- "用 Blave 看一下目前市場方向和資金稀缺指標"
- "用 Blave 抓 BTCUSDT 過去三個月的 K 線（1h）"

---

### BitMart Futures

- "Open a long position on BTCUSDT with 10x leverage, 0.01 BTC, market order"
- "Check my current futures positions on BitMart"
- "Set a take profit at 100000 and stop loss at 90000 for my BTCUSDT long"
- "Cancel all open orders for ETHUSDT futures"

---

- "用 BitMart 開一個 BTCUSDT 10倍槓桿多單，0.01 BTC，市價"
- "查看我目前的 BitMart 合約倉位"
- "幫我的 BTCUSDT 多單設定止盈 100000、止損 90000"
- "取消 ETHUSDT 所有掛單"

---

### BitMart Spot

- "Buy 100 USDT worth of BTC on BitMart spot"
- "Sell 0.5 ETH at 4000 USDT limit order on BitMart"
- "Show my BitMart spot balance"
- "Cancel my open BTC buy order"

---

- "用 BitMart 現貨買 100 USDT 的 BTC"
- "用 BitMart 現貨掛限價單賣 0.5 ETH，價格 4000"
- "查看我的 BitMart 現貨餘額"
- "取消我的 BTC 現貨買單"

---

## Disclaimer

This skill is provided for informational and automation purposes only. It does not constitute financial, investment, or trading advice. Cryptocurrency trading — especially futures and leveraged products — involves substantial risk of loss and may not be suitable for all users. Past performance is not indicative of future results.

By using this skill, you acknowledge that:
- All trading decisions are solely your own responsibility
- The authors and maintainers of this skill are not liable for any losses incurred
- You should consult a qualified financial advisor before making investment decisions

**本 Skill 僅供資訊參考與自動化操作使用，不構成任何投資建議。加密貨幣交易（尤其是合約與槓桿產品）具有高度風險，可能導致重大損失。過去績效不代表未來結果。使用本 Skill 即表示您同意，所有交易決策均由您自行負責，作者與維護者不對任何損失承擔責任。**
