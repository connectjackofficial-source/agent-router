"""agent-router CLI."""
import argparse
import json

from .router import batch_route, estimate_cost, route


def main():
    ap = argparse.ArgumentParser(prog="agent-router")
    ap.add_argument("prompt", nargs="?", help="prompt text to route")
    ap.add_argument("--file", default=None,
                    help="route every non-empty line of a file (batch mode)")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable output")
    args = ap.parse_args()

    if args.file:
        prompts = [l for l in open(args.file, encoding="utf-8") if l.strip()]
        results = batch_route(prompts)
        print(json.dumps(results, indent=2))
        return
    if not args.prompt:
        ap.print_help()
        return
    model = route(args.prompt)
    est = estimate_cost(args.prompt)
    if args.json:
        print(json.dumps(est, indent=2))
    else:
        print(model)
        print(json.dumps(est))


if __name__ == "__main__":
    main()
