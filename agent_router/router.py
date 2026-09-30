"""agent-router: route LLM calls to the cheapest model that can handle them.

Heuristic: count words/symbols in the prompt. Simple tasks go to cheap
models, complex ones to expensive ones. No ML, just rules.
"""
from __future__ import annotations

from dataclasses import dataclass


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


def route(prompt: str) -> str:
    """Pick the cheapest model that can handle the prompt length."""
    words = len(prompt.split())
    for tier in TIERS:
        if words <= tier.max_words:
            return tier.name
    return TIERS[-1].name


def estimate_cost(prompt: str, output_words: int = 100) -> dict:
    """Estimate cost for a prompt + expected output."""
    model = route(prompt)
    m = next(t for t in TIERS if t.name == model)
    in_cost = (len(prompt.split()) / 1000) * m.cost_per_1k
    out_cost = (output_words / 1000) * m.cost_per_1k * 3  # output costs more
    return {"model": model, "input_words": len(prompt.split()),
            "estimated_cost": round(in_cost + out_cost, 6)}
