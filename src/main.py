import argparse
from googlenews_fetch import GoogleNewsFetcher
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
def fetch_holder_concentration(symbol, period="5min"):
    return DataFetcher().get_latest_alpha(
        indicator="holder_concentration", symbol=symbol, period=period
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
