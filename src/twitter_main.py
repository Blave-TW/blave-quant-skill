import argparse
from twitter import create_tweet

commands = {}


def command(fn):
    commands[fn.__name__] = fn
    return fn


@command
def check():
    print("Hello World")


@command
def post_tweet(text: str):
    return create_tweet(text)


if __name__ == "__main__":
    import sys, inspect

    parser = argparse.ArgumentParser(prog="twitter")
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
