# KuCoin Broker Pro Program (BPP) Reference

Blave is an enrolled broker in the KuCoin Broker Pro Program. This file is for agent reference when users ask about commission rates, referral links, or BPP program details.

---

## Broker Identifiers (Blave)

| | Value |
|---|---|
| Spot Broker Tag | `blave` |
| Futures Broker Tag | `blaveFutures` |
| Broker Dashboard | https://www.kucoin.com/broker |
| Commission API | `GET https://www.kucoin.com/docs-new/rest/broker/api-broker/get-broker-rebate` |
| API Notifications | https://t.me/KuCoin_API_Notify |
| Broker Support | Telegram @KuCoin_Broker |

---

## Commission Tier Tables

Assessment is **independent** for Spot and Futures — different KPI thresholds, same rate structure.

### Spot Commission Rates

| Level | Monthly Volume KPI (USDT) | Non-Affiliated | Affiliated (broker invited + API) | Affiliated (broker invited, independent) | Affiliated (other inviter + API) |
|---|---|---|---|---|---|
| 0 | 0 | 0% | 50% | 40% | 0% |
| 1 | 500,000 | 40% | 50% | 40% | 40% |
| 2 | 10,000,000 | 45% | 55% | 45% | 45% |
| 3 | 25,000,000 | 50% | 60% | 50% | 50% |
| 4 | 100,000,000 | 55% | 70% | 70% | 55% |

### Futures Commission Rates

| Level | Monthly Volume KPI (USDT) | Non-Affiliated | Affiliated (broker invited + API) | Affiliated (broker invited, independent) | Affiliated (other inviter + API) |
|---|---|---|---|---|---|
| 0 | 0 | 0% | 50% | 40% | 0% |
| 1 | 1,000,000 | 40% | 50% | 40% | 40% |
| 2 | 20,000,000 | 45% | 55% | 45% | 45% |
| 3 | 50,000,000 | 50% | 60% | 50% | 50% |
| 4 | 200,000,000 | 55% | 70% | 70% | 55% |

---

## Four Commission Situations

| Situation | User affiliation | Trading method | Commission column |
|---|---|---|---|
| 1 | Broker-invited (R-code) | Via broker API | "Affiliated (broker invited + API)" |
| 2 | Broker-invited (R-code) | Independent (no broker API) | "Affiliated (broker invited, independent)" |
| 3 | None | Via broker API | "Non-Affiliated" |
| 4 | Another inviter | Via broker API | "Affiliated (other inviter + API)" |

**Situation 4 note:** By default, Blave's commission is split 50:50 with the user's original inviter. Blave can adjust this ratio with KuCoin's approval (requires proof of mutual agreement).

**VIP level limits:**
- Situations 1 & 2 (broker-invited): VIP0–VIP4 → 40%–70% tier; VIP5–VIP6 → capped at 40%–55% (Situation 4 rate)
- Situations 3 & 4 (non-broker-invited API): VIP0–VIP6 → 40%–55% tier
- VIP7+ and market makers → excluded from broker commission sharing

---

## Distribution Policy

- Commission = net trading fee × commission rate (net fee = after KCS discount, maker rebates, coupon deductions)
- Commission is distributed daily with a **1-day deferral** (T+1)
- New brokers get a **2-month exemption period** (fixed ≥40%, no KPI requirement) after API integration
- Level is determined by **last month's cumulative trading volume** of all broker users
- Brokers can split their commission with sub-brokers, influencer partners, or end users

---

## User Onboarding Bonuses (Co-Marketing)

New users who register via Blave's R-code and complete KYC within 14 days:

| Condition | Reward |
|---|---|
| Register + KYC | Spot fee coupon: 20 USDT |
| Register + KYC + deposit ≥50 USDT | Spot fee coupon: 100 USDT |
| Trade ≥100 USDT | VIP1 voucher |
| Trade ≥1,000 USDT | Futures trial fund: 25 USDT |
| Trade ≥6,000 USDT | Futures trial fund: 75 USDT |
| Trade ≥20,000 USDT | VIP3 voucher |
| Trade ≥100,000 USDT | Futures trial fund: 300 USDT |
| Trade ≥300,000 USDT | Futures trial fund: 600 USDT |

Additionally: KuCoin shares **5% cashback** of trading fees for all broker users in a rolling 30-day period (T+1 settlement).

---

## Checking Commissions

**API (daily records):**
```
GET https://api.kucoin.com/api/v1/broker/rebate  (authenticated, requires broker API key)
```

**Dashboard:** https://www.kucoin.com/broker (login required)

---

## Sub-Broker Program

Blave (master broker) can invite sub-brokers using the Broker R-code. Blave sets the sub-broker's commission rate and earns when sub-brokers bring end users.
