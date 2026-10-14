# Changelog

## 0.6.0 - 2026-10-14

- `cost_breakdown(prompts)` — per-model cost share for a batch, for
  capacity and spend planning

## 0.5.0 - 2026-10-14

- `dry_run()` — explain a routing decision (skipped tiers, token count,
  cost) without dispatching; built for threshold debugging and audits

## 0.4.0 - 2026-10-10

- `validate_tiers()` — check custom tier configs before they mis-route

## 0.3.0 - 2026-10-10

- `batch_route()` for routing many prompts at once
- CLI `--file` batch mode and `--json` output

## 0.2.0 - 2026-10-08

- CJK-aware token counting (中文提示词正确路由)
- `count_tokens()` public helper

## 0.1.0 - 2026-09-30

- Initial release
- Route by prompt length
- Cost estimation
