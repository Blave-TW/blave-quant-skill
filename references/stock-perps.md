# US Stock Perpetuals Across Venues

Tokenized US stocks / ETFs (`NVDAUSDT`, `AAPLUSDT`, `TSLAUSDT`, `SPYUSDT`, `QQQUSDT` …) trade as USDT
perpetuals on several venues. Blave `/kline` candles for these symbols are **Binance USDⓈ-M** (listed from
2026-01 onward — a window before listing is empty, not missing). A strategy backtested on `NVDAUSDT` was
backtested on Binance's NVDA stock perp, so on every other venue you must trade **the same stock**, which is
not always under the same name.

Binance, Bybit, BingX, OKX and Gate.io trade stock perps **24/7, weekends included**, even while the underlying exchange is closed. StockCoin's trading hours have not been verified — read them off the venue.

## Rule 1 — Identify the instrument from the venue's own list, never by guessing a name

- **Binance** (the reference): `GET https://fapi.binance.com/fapi/v1/exchangeInfo` → a stock perp has
  `underlyingType: "EQUITY"`; `baseAsset` is the ticker. Anything else (`COIN`, …) is not a stock.
- **Same ticker, different instrument is real.** Binance `CATUSDT` is Caterpillar, not the CAT memecoin;
  OKX `BB-USDT-SWAP` and Bybit `ONUSDT` are stocks, while Binance lists those tickers as coins. Before trading a
  ticker on another venue, check that both venues classify it the same way (stock vs coin). If they differ, the
  backtest does not apply — tell the user and do not place it.
- A near-name is a different instrument: BingX `NCSKSKHYNIX2USD` is a KRW listing at ~7× the price of SKHY.
  Use only a name that the venue's list ties to the exact ticker; zero or several matches → do not trade it.

## Venue naming

| Venue | Stock perp name for NVDA | How to resolve it |
|---|---|---|
| Binance | `NVDAUSDT` | `exchangeInfo` row with `underlyingType: "EQUITY"` |
| OKX, Gate.io | typically the same ticker in the venue's normal USDT swap naming | check the venue classifies it as a stock (see Rule 1) |
| Bybit | `NVDAUSDT`, or `<T>STOCKUSDT` (e.g. `AMDSTOCKUSDT`, `NOKIAUSDT`) where a coin owns the bare name | `GET /v5/market/instruments-info?category=linear` → rows with `symbolType` `stock` / `ETF`; `underlyingTicker` carries the ticker (use rows with `marketRegion: "US"`) |
| BingX | `NCSK<T>2USD-USDT` (e.g. `NCSKNVDA2USD-USDT`; ETFs/indices may be `NCSI…`) | `GET /openApi/swap/v2/quote/contracts` → `asset` `NCSK<T>2USD`, `displayName` `<T>-USDT`; a few are renamed (`NCSKCISCO2USD` = CSCO) and a few use another form where a coin owns the ticker (`AMDUS-USDT`) |
| StockCoin | `NVDA-PERP-USDT` | see `references/stockcoin-skill.md` (size is contracts of 0.0001 base; some names are not open to the API) |

Positions come back under the venue's name — map them back to the strategy's ticker before comparing with a
target, or one position reads as two.

## Stock-perp agreement

Some venues refuse stock-perp orders until the account has signed a separate agreement:

- **Binance `-4411`** — the TradFi-Perps agreement is not signed. Neither the Binance app nor the website shows a
  place to sign it; the API does: signed `POST /fapi/v1/stock/contract` (no parameters; success replies the bare
  text `SUCCESS`). **Signing an exchange agreement is the user's decision**: explain what it is, ask, and call it
  only after the user explicitly agrees (and replies CONFIRM). Never call it on your own, never as an automatic
  retry of a refused order.
- **Bybit `110126`** — the user signs it on the Bybit website or app with the **main account** by opening that
  contract's trade page. Sub-accounts cannot sign; the API route needs a transfer / withdrawal permission a
  trade-only key should not have.

## BingX status 25

A BingX contract with `status: 25` forbids **opening** only (orders answer `109415` "…is pause currently"):
entries and adds wait, reduces and closes still go through, and a flip can only close.
