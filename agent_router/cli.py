"""agent-router CLI."""
import argparse

from .router import route, estimate_cost


def main():
    ap = argparse.ArgumentParser(prog="agent-router")
    ap.add_argument("prompt", nargs="?", help="prompt text to route")
    args = ap.parse_args()
    if args.prompt:
        print(route(args.prompt))
        print(estimate_cost(args.prompt))


if __name__ == "__main__":
    main()
