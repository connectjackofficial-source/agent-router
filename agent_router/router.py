"""agent-router: route LLM calls to the cheapest model that can handle them.

Heuristic: count words/symbols in the prompt. Simple tasks go to cheap
models, complex ones to expensive ones. No ML, just rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


def load_tiers_json(path: str) -> list:
    """Load custom tiers from a JSON file: [{name, cost_per_1k, max_words}]."""
    import json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [Model(**item) for item in data]


@dataclass
class Model:
    name: str
    cost_per_1k: float  # in dollars
    max_words: int      # prompts shorter than this go here


# Tiered pricing (approximate, 2026)
TIERS = [
    Model("haiku", 0.00025, 30),
    Model("sonnet", 0.003, 200),
    Model("opus", 0.015, 100000),
]


def count_tokens(text: str) -> int:
    """Approximate token count, English- and CJK-aware.

    English tokens ≈ whitespace-separated words; CJK characters are counted
    at ~1 token per 1.5 chars so a long Chinese prompt is not treated as one
    giant "word".
    """
    import re
    cjk = re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]", text)
    words = len(text.split())
    return words + int(len(cjk) / 1.5)


def validate_tiers(tiers: list) -> list:
    """Check a tier list for the invariants routing depends on.

    Returns a list of problem strings (empty = valid).
    """
    problems = []
    if not tiers:
        return ["tier list is empty"]
    for i, t in enumerate(tiers):
        if not t.name:
            problems.append(f"tier #{i} has no name")
        if t.cost_per_1k < 0:
            problems.append(f"tier '{t.name}': negative cost")
        if t.max_words <= 0:
            problems.append(f"tier '{t.name}': max_words must be > 0")
        if i > 0:
            prev = tiers[i - 1]
            if t.cost_per_1k < prev.cost_per_1k:
                problems.append(
                    f"tier '{t.name}' cheaper than '{prev.name}'; "
                    "sort tiers by price ascending")
            if t.max_words <= prev.max_words:
                problems.append(
                    f"tier '{t.name}' max_words not above '{prev.name}'; "
                    "routing thresholds must increase")
    return problems


def route(prompt: str, tiers: Optional[list] = None) -> str:
    """Pick the cheapest model that can handle the prompt length."""
    tiers = tiers or TIERS
    words = count_tokens(prompt)
    for tier in tiers:
        if words <= tier.max_words:
            return tier.name
    return tiers[-1].name


def estimate_cost(prompt: str, output_words: int = 100) -> dict:
    """Estimate cost for a prompt + expected output."""
    model = route(prompt)
    m = next(t for t in TIERS if t.name == model)
    in_cost = (count_tokens(prompt) / 1000) * m.cost_per_1k
    out_cost = (output_words / 1000) * m.cost_per_1k * 3  # output costs more
    return {"model": model, "input_words": count_tokens(prompt),
            "estimated_cost": round(in_cost + out_cost, 6)}


def batch_route(prompts: list, tiers: Optional[list] = None,
                output_words: int = 100) -> list:
    """Route many prompts at once. Returns one dict per prompt:
    {index, model, input_words, estimated_cost}."""
    tiers = tiers or TIERS
    out = []
    for i, p in enumerate(prompts):
        model = route(p, tiers=tiers)
        m = next(t for t in tiers if t.name == model)
        tokens = count_tokens(p)
        in_cost = (tokens / 1000) * m.cost_per_1k
        out_cost = (output_words / 1000) * m.cost_per_1k * 3
        out.append({"index": i, "model": model, "input_words": tokens,
                    "estimated_cost": round(in_cost + out_cost, 6)})
    return out


def dry_run(prompt: str, tiers: Optional[list] = None) -> dict:
    """Explain a routing decision without dispatching anything.

    Returns the chosen model plus the full decision trail: token count,
    which tiers were skipped and why, and the estimated cost — useful for
    debugging thresholds and for audits ("why did this go to opus?").
    """
    tiers = tiers or TIERS
    tokens = count_tokens(prompt)
    skipped = []
    chosen = None
    for tier in tiers:
        if tokens <= tier.max_words:
            chosen = tier
            break
        skipped.append({"model": tier.name,
                        "reason": f"{tokens} > max_words {tier.max_words}"})
    if chosen is None:
        chosen = tiers[-1]
        skipped = [{"model": t.name,
                    "reason": f"{tokens} > max_words {t.max_words}"}
                   for t in tiers[:-1]]
    in_cost = (tokens / 1000) * chosen.cost_per_1k
    out_cost = (100 / 1000) * chosen.cost_per_1k * 3
    return {
        "model": chosen.name,
        "input_words": tokens,
        "skipped": skipped,
        "reason": (f"input {tokens} words <= max_words {chosen.max_words}"
                   if tokens <= chosen.max_words else
                   f"no tier fits; fell back to most capable '{chosen.name}'"),
        "estimated_cost": round(in_cost + out_cost, 6),
    }


def cost_breakdown(prompts: list, tiers: Optional[list] = None,
                   output_words: int = 100) -> dict:
    """Per-model cost share for a batch of prompts.

    Runs :func:`batch_route` over the whole batch and rolls the results
    up by model: how much of this workload's spend lands on each tier.
    Returns {"total": float, "by_model": {model: cost}}.
    """
    totals: dict[str, float] = {}
    for item in batch_route(prompts, tiers=tiers,
                            output_words=output_words):
        model = item["model"]
        totals[model] = totals.get(model, 0.0) + item["estimated_cost"]
    return {"total": round(sum(totals.values()), 6),
            "by_model": {m: round(c, 6) for m, c in totals.items()}}
