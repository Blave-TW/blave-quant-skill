import json
import argparse
from hyperliquid_bot.info import get_account_value, get_current_positions
from hyperliquid_bot.trade import adjust_portfolio

commands = {}


def command(fn):
    commands[fn.__name__] = fn
    return fn


@command
def check():
    print("Hello World")


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


if __name__ == "__main__":
    import sys, inspect

    parser = argparse.ArgumentParser(prog="hyperliquid")
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
