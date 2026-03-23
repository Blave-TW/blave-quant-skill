# Blave Quant Skill

A skill that allows an agent to fetch crypto market alpha data from the Blave API.

## Install

```bash
npx skills add https://github.com/Blave-TW/blave-quant-skill
```

## Setup

After installing the skill, follow these steps:

### 1. Get a Blave API Plan

Subscribe to the **API Plan** to get API access. First-time subscribers get a **14-day free trial** (credit card required).

👉 [https://blave.org/landing/en/pricing](https://blave.org/landing/en/pricing)

### 2. Create Your API Key

Once subscribed, create your API key here:

👉 [https://blave.org/landing/en/api?tab=blave](https://blave.org/landing/en/api?tab=blave)

### 3. Add Your Credentials

Add the following to your `.env` file:

```
blave_api_key=YOUR_API_KEY
blave_secret_key=YOUR_SECRET_KEY
```

You're all set! The skill will use these credentials to call the Blave API.

---

## Usage Examples

Once set up, you can ask your agent:

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
