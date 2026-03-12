import json
import argparse
from googlenews_fetch import GoogleNewsFetcher
from hyperliquid_bot.info import get_account_value, get_current_positions
from hyperliquid_bot.trade import adjust_portfolio
from threads import ThreadsAPI
from data_fetch import DataFetcher

commands = {}


def command(fn):
    commands[fn.__name__] = fn
    return fn


@command
def check():
    print("Hello World")


@command
def fetch_news(
    keyword: str, max_results: int = 10, lang: str = "en", period: str = "7d"
):
    fetcher = GoogleNewsFetcher(lang=lang, period=period)
    results = fetcher.search(keyword, max_results=max_results)

    return results


@command
def fetch_hyperliquid_account():
    result = {}
    account_value = get_account_value()
    result["account_value"] = account_value["spot"]["balances"][0]["total"]
    result["position"] = get_current_positions()
    return result


@command
def adjust_hyperliquid_portfolio(target_portfolio_json: str):
    target_portfolio = json.loads(target_portfolio_json)
    return adjust_portfolio(target_portfolio)


@command
def fetch_threads_insight_table():
    return ThreadsAPI().arrange_insight_table()


@command
def create_text_post(text):
    return ThreadsAPI().create_text_post(text)


@command
def fetch_holder_concentration(symbol):
    return DataFetcher().get_latest_alpha(
        indicator="holder_concentration", symbol=symbol, period="5min"
    )


@command
def fetch_taker_intensity(symbol, timeframe="24h"):
    return DataFetcher().get_latest_alpha(
        indicator="taker_intensity", symbol=symbol, period="5min", timeframe=timeframe
    )


if __name__ == "__main__":
    import sys, inspect

    parser = argparse.ArgumentParser(prog="blave")
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd not in commands:
        print(f"unknown command: {cmd}")
        sys.exit(1)

    fn = commands[cmd]
    sig = inspect.signature(fn)
    for name, param in sig.parameters.items():
        arg_type = param.annotation if param.annotation != param.empty else str
        if param.default != param.empty:
            parser.add_argument(f"--{name}", type=arg_type, default=param.default)
        else:
            parser.add_argument(name, type=arg_type)

    args = parser.parse_args(sys.argv[2:])
    fn(**vars(args))
