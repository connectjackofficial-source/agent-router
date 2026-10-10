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
