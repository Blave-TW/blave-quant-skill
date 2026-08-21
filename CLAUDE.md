# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repo contains one skill covering sixteen capabilities:
1. **Blave** — Agent calls the Blave REST API directly for crypto market alpha data, Taiwan stock data, and Hyperliquid top trader tracking
2. **CME / ICE Futures** — Agent fetches WTI crude (CL), gold (GC), and Brent crude (BRN) OHLCV from 2010 via Blave API
3. **Taiwan Futures** — Agent fetches TXF (台指期近月連續) OHLCV (1d from 2013-12-30, intraday from 2014-01-02) via Blave API; schemas 1d/1m/5m/15m/30m/60m
4. **BitMart Futures** — Agent calls the BitMart API for perpetual futures trading
5. **BitMart Spot** — Agent calls the BitMart API for spot trading
6. **OKX** — Agent calls the OKX API for spot and perpetual swap trading
7. **Bybit** — Agent calls the Bybit API for spot and derivatives/perpetual swap trading
8. **BingX** — Agent calls the BingX API for spot and perpetual swap trading
9. **Bitget** — Agent calls the Bitget API for spot and futures trading
10. **Binance** — Agent calls the Binance API for spot and USDS-M futures trading
11. **Bitfinex** — Agent calls the Bitfinex API for spot, margin, and funding/lending
12. **KuCoin** — Agent calls the KuCoin API for spot and futures/perpetual contract trading
13. **Taiwan stock lookup/quote/PE** — Agent queries stock code/name lookup, daily quotes, PE/yield/PB via **Blave API** (`studio/market/twstock/list`, `/info`, `/price`, `/quote`, `/per`), NOT the raw TWSE/TPEX public API. That public API (no key required) is used only as a fallback for the two things Blave has no endpoint for: trading-halt status and a one-shot full-market PE/yield/PB scan
14. **台股分點買賣超** — Agent calls Blave API `GET /studio/market/twstock/broker/stock/<stock_id>` (by stock) or `GET /studio/market/twstock/broker/trader/<trader_id>` (by broker branch) for daily buy/sell data; no CAPTCHA required
15. **Taiwan Futures** — Agent calls Blave API `GET /studio/market/twfutures/ohlcv/TXF/<schema>` for TXF OHLCV; schemas: 1d/1m/5m/15m/30m/60m; 1d from 2013-12-30, intraday from 2014-01-02
16. **Gate.io** — Agent calls the Gate.io APIv4 for spot and USDT-settled perpetual futures trading

No CLI or wrapper involved. All API calls are made directly by the agent.

## Required `.env` Variables

- `blave_api_key`, `blave_secret_key` — Blave API auth
- `BITMART_API_KEY`, `BITMART_API_SECRET`, `BITMART_API_MEMO` — BitMart API auth
- `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE` — OKX API auth
- `BYBIT_API_KEY`, `BYBIT_API_SECRET` — Bybit API auth
- `BINGX_API_KEY`, `BINGX_SECRET_KEY` — BingX API auth
- `BITGET_API_KEY`, `BITGET_SECRET_KEY`, `BITGET_PASSPHRASE` — Bitget API auth
- `BINANCE_API_KEY`, `BINANCE_SECRET_KEY` — Binance API auth
- `BITFINEX_API_KEY`, `BITFINEX_API_SECRET` — Bitfinex API auth
- `KUCOIN_API_KEY`, `KUCOIN_API_SECRET`, `KUCOIN_API_PASSPHRASE` — KuCoin API auth
- `GATE_API_KEY`, `GATE_SECRET_KEY` — Gate.io API auth

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Main skill doc — Blave, BitMart Futures, and BitMart Spot sections |
| `references/blave-api.md` | Blave Python examples |
| `references/blave-indicator-guide.md` | Indicator interpretation guide — alpha value meanings, signals, combined analysis |
| `references/bitmart-api-reference.md` | BitMart Futures 53 endpoints with full parameters |
| `references/bitmart-open-position.md` | Futures open position workflow |
| `references/bitmart-close-position.md` | Futures close position workflow |
| `references/bitmart-plan-order.md` | Futures plan order workflow |
| `references/bitmart-tp-sl.md` | Futures TP/SL workflow |
| `references/bitmart-spot-api-reference.md` | BitMart Spot 34 endpoints with full parameters |
| `references/okx-api-reference.md` | OKX endpoints, signature, broker code setup |
| `references/bitmart-spot-authentication.md` | Spot auth details and examples |
| `references/bitmart-spot-scenarios.md` | Spot common trading scenarios |
| `references/bitmart-signature.md` | Python HMAC-SHA256 signature implementation + common mistakes |
| `references/hyperliquid-api.md` | Hyperliquid API — all 9 endpoints with params, response format, cache times |
| `references/tradingview-stream.md` | TradingView SSE stream — webhook setup, Python streaming client with reconnect |
| `references/bingx-api-reference.md` | BingX 63 endpoints, Python signature, public market data + spot + perpetual swap |
| `references/bitget-api-reference.md` | Bitget spot + futures endpoints, Python signature |
| `references/binance-api-reference.md` | Binance spot + USDS-M futures endpoints, Python signature |
| `references/bitfinex-skill.md` | Bitfinex spot, margin, funding/lending endpoints, HMAC-SHA384 signature |
| `references/kucoin-skill.md` | KuCoin spot + futures overview — auth, broker headers, operation flow, quick reference |
| `references/kucoin-api-reference.md` | KuCoin spot + futures full endpoints, Python signature + broker sign helper |
| `references/kucoin-bpp.md` | KuCoin Broker Pro Program — commission tiers, referral bonuses, dashboard guide |
| `references/gateio-skill.md` | Gate.io spot + futures overview — auth, broker channel header, operation flow, quick reference |
| `references/gateio-api-reference.md` | Gate.io spot + futures full endpoints, Python signature + broker channel header |
| `references/twse-skill.md` | 停復牌狀態 + 全市場 PE 批次掃描（Blave API 沒有對應端點時才用）— 快速參考 |
| `references/twse-api-reference.md` | 同上，完整 API 參考：欄位說明、Python 範例、民國年轉換 |
| `references/twse-bsr-reference.md` | 台股分點買賣超 — Blave API endpoints（by stock / by trader）、欄位說明、Python 範例 |

## Blave API Endpoints

Base URL: `https://api.blave.org`

- `price` — current price + 24h change for a symbol (`symbol` required)
- `alpha_table` — latest alpha for all symbols; use for multi-coin queries or screening
- `kline` — OHLCV candlestick data
- `market_direction/get_alpha` — 市場方向 Market Direction (BTCUSDT)
- `market_sentiment/get_symbols` / `get_alpha` — 市場情緒 Market Sentiment time series + stat
- `capital_shortage/get_alpha` — 資金稀缺 Capital Shortage (market-wide)
- `sector_rotation/get_history_data` — 板塊輪動 Sector Rotation history
- `holder_concentration/get_symbols` / `get_alpha` — 籌碼集中度 Holder Concentration time series + stat
- `funding_rate/get_alpha` — 資金費率 Funding Rate time series (Binance) + close + stat; `alpha` = funding rate × 100 (percent)
- `taker_intensity/get_symbols` / `get_alpha` — 多空力道 Taker Intensity time series + stat
- `whale_hunter/get_symbols` / `get_alpha` — 巨鯨警報 Whale Hunter; supports `score_type`
- `unusual_movement/get_symbols` / `get_alpha` — 異常漲跌 Unusual Movement time series + stat
- `squeeze_momentum/get_symbols` / `get_alpha` — 擠壓動能 Squeeze Momentum + scolor; period fixed to `1d`
- `blave_top_trader/get_exposure` — Blave頂尖交易員 Top Trader Exposure (BTCUSDT)
- `liquidation/get_symbols` — list of symbols with liquidation data
- `liquidation/get_alpha` — 爆倉指標 Liquidation alpha time series + stat; `timeframe` default `24h`
- `liquidation/get_map` — liquidation heatmap: price levels vs USD exposure (`labels`, `liquidation`, `cumsum`, `oi_value`, `price`)
- `liquidation/get_map_change` — recent liquidation events by time window (`hist_0_1h`, `hist_1_8h`, `hist_8_24h`)
- `studio/market/twstock/list` — Taiwan stock universe (上市+上櫃, incl. ETFs): `[{stock_id, name, close, industry_code, listing_date}, ...]`; `industry_code` is TWSE/TPEx's raw numeric 產業別 code (e.g. `24`=半導體業), not a decoded name; `listing_date` is `YYYY-MM-DD`; ETFs/non-company securities have both as `null`; Redis-cached 24h — use for universe building / industry-based sampling, not for per-stock lookups
- `studio/market/twstock/info/<stock_id>` — single-stock basic info, same shape as one row of `/list`; 404 if not a currently-active listing
- `studio/market/twstock/price/<stock_id>` — Taiwan stock raw daily OHLCV; `start`/`end` optional (YYYY-MM-DD); data from 2000-01-04
- `studio/market/twstock/price_adj/<stock_id>` — Taiwan stock forward-adjusted (向後調整/後復權) daily OHLCV; same params; use for backtesting total return
- `studio/market/twstock/institutional/<stock_id>` — Taiwan stock 三大法人每日買賣超 (wide format: foreign / investment trust / dealer self / dealer hedging × buy / sell, in shares); `start`/`end` optional
- `studio/market/twstock/margin/<stock_id>` — Taiwan stock 融資融券每日資料 (`margin_buy`, `margin_sell`, `margin_balance`, `margin_prev_balance`, `margin_limit`, `margin_cash_repay`, `short_sell`, `short_buy`, `short_balance`, `short_prev_balance`, `short_limit`, `short_cash_repay`, `offset_loan_short`; all in shares); `start`/`end` optional; data from 1994-10-01
- `studio/market/twstock/shareholding/<stock_id>` — Taiwan stock 股權持股分級表 (weekly; `level`, `people`, `unit`, `percent` per bracket; 17 levels incl. `total`); `start`/`end` optional
- `studio/market/twstock/financials/<stock_id>` — 綜合損益表 quarterly fundamental (long format: `date`, `type`, `value`, `origin_name`); `start`/`end` optional; Redis-cached 24 h
- `studio/market/twstock/balance_sheet/<stock_id>` — 資產負債表 quarterly fundamental; same schema; `_per` suffix types are % of total assets
- `studio/market/twstock/cashflow/<stock_id>` — 現金流量表 quarterly fundamental; same schema
- `studio/market/twstock/monthly_revenue/<stock_id>` — 月營收 monthly revenue (`date`, `stock_id`, `country`, `revenue` in thousands NTD, `revenue_month`, `revenue_year`); `start`/`end` optional; data from 2000-01-01; Redis-cached 24 h
- `studio/market/twstock/foreign_shareholding/<stock_id>` — 外資持股表（日頻）: `ForeignInvestmentSharesRatio`（持股比率%）、`ForeignInvestmentShares`（持股股數）、`ForeignInvestmentRemainingShares`、`ForeignInvestmentRemainRatio`、`NumberOfSharesIssued`; `start`/`end` optional; Redis-cached 24h
- `studio/market/twstock/batch/<data_type>` — **批次查詢（大型 universe / 選股用）**: `data_type` ∈ {`price`, `price_adj`, `per`, `institutional`, `shareholding`, `foreign_shareholding`, `financials`, `balance_sheet`, `monthly_revenue`, `dividend`}; `?stock_ids=2330,2317,...`（最多 50 支）+ `start`/`end`（視類型而定）; 回傳 `{"data_type": "...", "data": {"2330": [...], ...}, "failed": [...]}`——`failed` 是 server 端抓取失敗（rate limit 或上游錯誤）的股票,呼叫端應重試;不在 `data` 也不在 `failed` 才是真的沒資料; 每型欄位與對應單檔 endpoint 完全一致; server-side 平行 fetch + Redis cache；在 Blave Agent 中用對應 `_batch` lib 函式而非直接呼叫此 endpoint。多股篩選一律用 batch,不要對單檔 endpoint fan-out（會 429）
- `studio/market/twstock/broker/search` — 券商分點代碼查詢: fuzzy search by `name` param; returns `[{broker_id, broker_name}]`; 1007 branches
- `studio/market/twstock/broker/stock/<stock_id>` — 分點買賣超 by stock (single day): all broker branches for the given stock (`broker_id`, `broker_name`, `price`, `buy`, `sell`); `date` optional (YYYY-MM-DD, defaults to today); for multi-day, call once per day
- `studio/market/twstock/broker/trader/<trader_id>` — 分點買賣超 by broker branch (single day): all stocks traded by the given branch (`stock_id`, `broker_name`, `price`, `buy`, `sell`); `date` optional; trader_id supports alphanumeric (e.g. `920A`)
- `studio/market/twstock/kbar/<stock_id>` — 分K（1分鐘 OHLCV）: `start`/`end` YYYY-MM-DD required; max 31 days per request; fields: `date`, `minute` (HH:MM:SS), `open`, `high`, `low`, `close`, `volume`; data from 2019-01-01; Sponsor only
- `studio/market/twstock/minute/ohlcv/<stock_id>/<schema>` — 現股分線 minute-line OHLCV: `schema` ∈ `1m`/`5m`/`15m`/`30m`/`60m`/`1d`; `start`/`end` optional (YYYY-MM-DD); `adjust` optional (`0`/`1`/`true`/`false`, default `0` = raw traded prices; `1` = forward-adjusted 後復權 OHLC via the same factor pipeline as `/twstock/price_adj`, volume never adjusted, 503 fail-loud if factors unavailable); max range per request 1m 31d / 5m 62d / 15m 93d / 30m 186d / 60m 365d / 1d 3650d (400 `date_range_too_large` beyond); `ts` UTC ISO minute-start label (13:30 Taipei bar = closing auction); `volume` in lots (張); data from 2019-01; coverage demand-driven — first query of a listed stock auto-seeds ~30 recent days + enrolls it for intraday live collection and daily official correction, deep history backfills afterwards
- `studio/market/twstock/minute/ohlcv/symbols` — stock ids that currently have minute-line data on disk (the covered set for the endpoint above)
- `studio/market/twstock/quote/<stock_id>` — 即時報價 real-time last-quote snapshot (~10s refresh, no history — always "now"); no `start`/`end`; fields: `open`/`high`/`low`/`close` (today so far), `change_price`, `change_rate`, `average_price`, `volume` (latest tick), `total_volume` (day cumulative), `amount`, `total_amount`, `yesterday_volume`, `buy_price`/`buy_volume` (best bid), `sell_price`/`sell_volume` (best ask), `volume_ratio`, `quote_time` (full timestamp, unlike every other endpoint's bare-date `date`), `tick_type` (0=indeterminate/1=sell-initiated/2=buy-initiated); returns a flat object (`"data": {...}`), not a list; Sponsor only
- `studio/market/twstock/quote?stock_ids=<a>,<b>` — batch real-time quote; max 50 ids; `"data": {"<id>": {...}, ...}`
- `studio/market/twstock/quote/all` — real-time quote for the entire market (~2839 stocks) in one call; `"data": [{...}, ...]`
- `studio/market/twstock/per/<stock_id>` — PE/PB/殖利率（日頻）: `start`/`end` optional (YYYY-MM-DD); fields: `date`, `dividend_yield`, `PER`, `PBR`; data from 2005-10-01
- `studio/market/twstock/dividend/<stock_id>` — 股利事件 dividend events (one row per announcement row): fields `record_date`, `period`（opaque label,勿 parse 成西元年）, `announce_date`, `cash_ex_date`, `stock_ex_date`, `pay_date`, `cash`, `stock`, `stock_ratio`（空日期為 `""`）; `start`/`end` optional（嚴格 YYYY-MM-DD,否則 400;範圍過濾用 cash_ex→stock_ex→record_date 三層 effective date）; 零值列（宣告不分派）保留; 僅現役上市櫃（已下市 404）; 404=查無標的或無股利史,範圍外=200+`[]`; 配額耗盡 503; batch 版 `batch/dividend`（≤50,查無者靜默缺席、不回 404）
- `studio/market/twmarket/dividend_points` — 加權指數每日除息點數: `{date, points, estimated}` + `meta.estimated_coverage`/`degraded`; `estimated: false`=已實現（報酬指數推導,2003 起）、`true`=預估（已公告合成+去年模板,未來平日 zero-fill）; `end` 上限 today+120（靜默 clamp）; 每交易日 ~17:00（台北）後更新當日; 正逆價差 fair basis 必扣此數列
- `studio/market/twstock/market_value/<stock_id>` — market capitalization (市值, NTD); `start`/`end` optional; data from 2004-01-01; fields: `date`, `market_value`
- `studio/market/twstock/market_value/all` — 市值排名 whole-market market-cap ranking snapshot (上市+上櫃+ETF, ~2,400 rows; 興櫃 excluded, ETN no data); `top` optional int 1–3000 (else 400 `top must be an integer between 1 and 3000`); returns `{"date", "data": [{rank, stock_id, name, market_value}]}` sorted desc, 1-based `rank`, `market_value` NTD 元 integer, `date` = latest published EOD day (FinMind TaiwanStockMarketValue); server-cached 30 min; use for 前十大權值股 / 市值前 N 檔股池 instead of per-stock fan-out; ETFs = `stock_id` starting `00`
- `studio/market/twstock/news/<stock_id>` — stock news (新聞): `start`/`end` YYYY-MM-DD; max 31 days; multiple articles per day; fields: `date` (datetime string), `title`, `source`, `link`
- `studio/market/twstock/gov_bank/<stock_id>` — 八大行庫買賣超: `start`/`end` YYYY-MM-DD required; max 31 days; data from 2021-06-30; 8 rows/day (one per bank); fields: `date`, `bank_name`, `buy`, `buy_amount`, `sell`, `sell_amount`
- `studio/market/twstock/lending/<stock_id>` — 借券成交明細（日頻，每天多筆）: `start`/`end` optional; fields: `date`, `transaction_type`（競價/議借）, `volume`, `fee_rate`, `close`, `original_return_date`, `original_lending_period`; data from 2001-05-01
- `studio/market/twfutures/ohlcv/<symbol>/<schema>` — Taiwan futures OHLCV (`ts` UTC ISO, `open`, `high`, `low`, `close` in index points, `volume` in contracts); symbol: `TXF`; schema: `1d`/`1m`/`5m`/`15m`/`30m`/`60m`; `start`/`end` optional (YYYY-MM-DD); max range: 1d→3650 / 60m→365 / 30m→186 / 15m→93 / 5m→62 / 1m→31 days; data from 2013-12-30 (1d) / 2014-01-02 (intraday; pre-2017-05-15 day-session only, no night session); requires API plan auth. Also accepts individual stock futures symbols, but only a dynamically-growing subset with backfilled minute-line data (most of the 231 don't have it — 400 if unsupported); check `ohlcv/symbols` below first
- `studio/market/twfutures/ohlcv/symbols` — currently-allowed symbols for the endpoint above; no params; fields: `data` (list, always includes `TXF` plus whatever stock futures ids currently have backfilled minute-line data)
- `studio/market/twfutures/ohlcv/<symbol>/export/<year>` — bulk export: streams the raw 1m year parquet file for the symbol (`application/octet-stream`; columns `ts`/`open`/`high`/`low`/`close`/`volume`); one request per calendar year, zero server-side computation — resample locally; 2014 ≤ year ≤ current year else 400; no file for that year → 404 `{"error": "no_data"}`; use for long-history backtest fetches instead of chunked JSON; requires API plan auth
- `studio/market/twfutures/bid_ask_vol/<symbol>` — TXF 1-minute bid/ask volume aggregated from tick data; `bid_vol` = 內盤 (seller-initiated), `ask_vol` = 外盤 (buyer-initiated), `total_vol` = total incl. unclassified; symbol: `TXF`; `start`/`end` optional (YYYY-MM-DD); max 31 days; data from 2018-02-22; includes both day + night sessions; requires API plan auth
- `studio/market/twfutures/option/large_traders/<option_id>` — Taiwan option large traders (選擇權大額交易人); 6 rows/day (call/put × week/current month/all); `option_id`: TXO; `start`/`end` optional; data from 2007-01-02; fields: `date`, `option_id`, `put_call`, `contract_type`, `buy/sell_top5/top10_trader_open_interest(_per)`, `market_open_interest`
- `studio/market/twfutures/large_traders/<futures_id>` — Taiwan futures large traders open interest (大額交易人); 3 rows/day (week/current month/all); `start`/`end` optional; data from 2007-01-02; fields: `date`, `futures_id`, `contract_type`, `buy/sell_top5/top10_trader_open_interest(_per)`, `market_open_interest`, `buy/sell_top5/top10_specific_open_interest(_per)`
- `studio/market/twfutures/option/institutional/<option_id>` — Taiwan option institutional investors (6 rows/day: 3 investors × call/put); `option_id`: TXO; `start`/`end` optional; data from 2018-06-05; fields: `date`, `option_id`, `call_put`, `institutional_investors`, `long/short_deal_volume/amount`, `long/short_open_interest_balance_volume/amount`
- `studio/market/twfutures/institutional/<futures_id>` — Taiwan futures institutional investors (3 rows/day: 自營商/投信/外資); `start`/`end` optional; data from 2018-06-05; fields: `date`, `futures_id`, `institutional_investors`, `long/short_deal_volume/amount`, `long/short_open_interest_balance_volume/amount`
- `studio/market/twfutures/daily/<futures_id>` — Taiwan futures daily OHLCV by contract (FinMind); `futures_id`: TX, MTX, TE, TF, etc. — also accepts any of the 231 individual stock futures ids (股票期貨, e.g. `CDF`); `start`/`end` optional (YYYY-MM-DD); data from 1998-07-21; multiple rows/day (all contract months × trading_session: position/after_market); fields: `date`, `futures_id`, `contract_date`, `open`, `max`, `min`, `close`, `spread`, `spread_per`, `volume`, `settlement_price`, `open_interest`, `trading_session`
- `studio/market/twfutures/stock_futures/batch/daily` — batch form of `daily/<futures_id>` scoped to stock futures ids; `futures_ids` required (comma-separated, max 250, must be valid stock-futures ids — 400 otherwise); `start`/`end` optional; returns `{"data": {futures_id: [...]}, "failed": [...]}` (`failed` = ids dropped after persistent upstream rate-limiting, not a genuine empty result)
- `studio/market/twfutures/option/pcr` — official TAIFEX 台指選擇權買賣權未平倉量比率 (OI-based put/call ratio); one row/day (trading days only); `start`/`end` optional (YYYY-MM-DD); data from 2001-12-24; fields: `date`, `pcr` (買賣權未平倉量比率%); NOT derived from option institutional / large-trader data
- `studio/market/anue/economic_calendar` — 總經事件行事曆 (global macro calendar, licensed feed): release time, market consensus (`predict`), prior (`last`), actual (`real`, `null` until released); all params optional — `start`/`end` (YYYY-MM-DD, Taipei dates, inclusive), `country` (ISO-2, comma-separated), `max_priority`, `limit`, `lang` (`zh`/`en`); unfiltered returns ~1,400 rows so always filter; `time` is Taipei `HH:MM` (`null` when unpublished), `startDate` is the epoch-seconds of the event's Taipei date. **`priority` is inverted from the intuitive reading — 1 is the MOST important** (non-farm payrolls, rate decisions), 3 the least (rig counts), and `max_priority` keeps `priority <=` it, so the big events are `max_priority=1`. Coverage is a rolling ~5-week window, not a history archive; an out-of-window range returns an empty list, not an error. **The only source for macro events and their numbers — never substitute a web search or a remembered value**
- `screener/get_saved_conditions` — user's saved screener conditions
- `screener/get_saved_condition_result` — symbols matching a saved condition (`condition_id` required)
- `hyperliquid/leaderboard` — top 100 Hyperliquid traders (`sort_by` param)
- `hyperliquid/traders` — Blave-curated tracked trader list with names/descriptions
- `hyperliquid/trader_position` — perp/spot positions + net equity (`address` required)
- `hyperliquid/trader_history` — fill history (`address` required)
- `hyperliquid/trader_performance` — cumulative PnL chart (`address` required)
- `hyperliquid/trader_open_order` — open orders (`address` required)
- `hyperliquid/top_trader_position` — aggregated long/short positions of top 100 traders
- `hyperliquid/top_trader_exposure_history` — historical net exposure (`symbol`, `period` required)
- `hyperliquid/bucket_stats` — profit/loss stats + positions by account value bucket

## BitMart Futures

Base URL: `https://api-cloud-v2.bitmart.com`

53 endpoints across market data, account, trading, plan orders, TP/SL, trailing stops, sub-accounts, affiliate, and simulated trading. See `references/bitmart-api-reference.md` for full details.

## BitMart Spot

Base URL: `https://api-cloud.bitmart.com`

34 endpoints across market data, account/wallet, trading (buy/sell), order queries, margin, and sub-accounts. Symbol format uses underscore: `BTC_USDT`. See `references/bitmart-spot-api-reference.md` for full details.

## BitMart Broker ID

Always include `X-BM-BROKER-ID: BlaveData666666` on **all** BitMart API requests (both futures and spot, regardless of auth level).

## Bybit Broker Header

Always include `referer: Ue001036` on **all** Bybit API requests (both public and authenticated).

## Bybit

Base URL: `https://api.bybit.com` | Backup: `https://api.bytick.com` | Testnet: `https://api-testnet.bybit.com`

Signature: `HMAC-SHA256(secret, {timestamp}{apiKey}{recvWindow}{queryString|jsonBody})`
Headers: `X-BAPI-API-KEY`, `X-BAPI-TIMESTAMP`, `X-BAPI-SIGN`, `X-BAPI-RECV-WINDOW: 5000`, `referer: Ue001036`

## BingX Source Header

Always include `X-SOURCE-KEY: BX-AI-SKILL` on **all** BingX API requests (both public and authenticated).

## BingX

Base URL: `https://open-api.bingx.com` | Fallback: `https://open-api.bingx.pro` | Paper: `https://open-api-vst.bingx.com`

Signature: `HMAC-SHA256(secret, sorted_params_canonical_string)` → hex, appended as `&signature=<hex>`
Headers: `X-BX-APIKEY`, `X-SOURCE-KEY: BX-AI-SKILL`

## Bitget

Base URL: `https://api.bitget.com`

Signature: `Base64(HMAC-SHA256(secret, timestamp + METHOD + path + body))`
Headers: `ACCESS-KEY`, `ACCESS-SIGN`, `ACCESS-PASSPHRASE`, `ACCESS-TIMESTAMP`

## Binance

Spot Base URL: `https://api.binance.com` | Futures Base URL: `https://fapi.binance.com`

Signature: `HMAC-SHA256(secret, queryString + requestBody)` → hex, `signature` as last param
Headers: `X-MBX-APIKEY`

## Binance Broker ID (Blave)

Broker attribution is per-order via `newClientOrderId` (NOT a header). Every order placement MUST include `newClientOrderId` starting with:
- Spot: `x-GBN6HWR2` (broker ID `GBN6HWR2`)
- USDS-M Futures: `x-52DDFAFN` (broker ID `52DDFAFN`)

Total length ≤ 36 chars. Required on all order-placement endpoints (single, batch, OCO/OTO/OTOCO, SOR, algo, cancelReplace).

## KuCoin Broker Attribution

Always include **4 broker headers** on **all** KuCoin API requests (spot and futures, public and private). Omitting them disqualifies broker rebates.

| Header | Spot | Futures |
|---|---|---|
| `KC-BROKER-NAME` | `blave` | `blaveFutures` |
| `KC-API-PARTNER` | `blave` | `blaveFutures` |
| `KC-API-PARTNER-SIGN` | `Base64(HMAC-SHA256("1c10e0c0-bc3e-4a18-ad53-e41e6df5f757", ts + "blave" + apiKey))` | `Base64(HMAC-SHA256("520815df-b324-4494-9bc8-b1015732b902", ts + "blaveFutures" + apiKey))` |
| `KC-API-PARTNER-VERIFY` | `true` | `true` |

## KuCoin

Spot Base URL: `https://api.kucoin.com` | Futures Base URL: `https://api-futures.kucoin.com`

Symbol format: Spot `BTC-USDT` | Futures `XBTUSDTM` (BTC uses `XBT`, append `USDTM` for linear perpetual)

Signature: `Base64(HMAC-SHA256(secret, timestamp + METHOD + path + body))` → headers: `KC-API-KEY`, `KC-API-SIGN`, `KC-API-TIMESTAMP`, `KC-API-PASSPHRASE` (signed), `KC-API-KEY-VERSION: 3`

## Gate.io Broker Channel Header

Always include `X-Gate-Channel-Id: blave` on **all** Gate.io API requests (spot and futures, public and authenticated). Omitting it disqualifies broker rebates.

## Gate.io

Base URL: `https://api.gateio.ws/api/v4`

Symbol format: `BTC_USDT` (spot and futures) | Futures settle: `usdt`

Signature: `HMAC-SHA512(secret, METHOD + "\n" + /api/v4/path + "\n" + query + "\n" + SHA512_hex(body) + "\n" + timestamp_seconds)` → hex
Headers: `KEY`, `Timestamp` (unix seconds), `SIGN`, `X-Gate-Channel-Id: blave`

## Bitfinex

Base URL: `https://api.bitfinex.com` (auth) | `https://api-pub.bitfinex.com` (public)

Signature: `HMAC-SHA384(secret, "/api/" + path + nonce + body)` → hex
Headers: `bfx-apikey`, `bfx-nonce`, `bfx-signature`
Affiliate code: `"meta": {"aff_code": "ZZDLtrXMF"}` on every order

## TWSE / TPEX — 台股市場查詢

**Blave API first.** Stock code/name lookup (`studio/market/twstock/list`, `/info/<stock_id>`), daily
quote/price (`/price/<stock_id>`, `/quote/<stock_id>`), and single-stock PE/yield/PB (`/per/<stock_id>`)
all go through Blave API — see `references/blave-api.md`. The raw TWSE/TPEX public API below (no key
required) is a fallback for only two things Blave has no endpoint for:

| Need | Base URL / endpoint |
|---|---|
| Trading-halt status | `GET https://openapi.twse.com.tw/v1/exchangeReport/TWTB4U` |
| One-shot full-market PE/yield/PB scan (not per-stock) | `GET https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL` (TWSE) / `GET https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes` (TPEX) |

Date format: ROC calendar — `1150507` = 2026/05/07 (民國115年05月07日)

All queries are read-only — **Safety Mode CONFIRM is NOT required.**

> Quick reference: `references/twse-skill.md`
> Full API reference with Python examples: `references/twse-api-reference.md`
