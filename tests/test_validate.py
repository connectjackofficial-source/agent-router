"""Tests for tier validation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_router.router import Model, TIERS, validate_tiers


def test_builtin_tiers_valid():
    assert validate_tiers(TIERS) == []
    print("test_builtin_tiers_valid: ok")


def test_unsorted_price_rejected():
    bad = [Model("expensive", 0.01, 100),
           Model("cheap", 0.001, 200)]
    problems = validate_tiers(bad)
    assert any("cheaper than" in p for p in problems)
    print("test_unsorted_price_rejected: ok")


def test_flat_thresholds_rejected():
    bad = [Model("a", 0.001, 100), Model("b", 0.002, 100)]
    problems = validate_tiers(bad)
    assert any("max_words not above" in p for p in problems)
    print("test_flat_thresholds_rejected: ok")


def test_empty_and_negative():
    assert validate_tiers([]) != []
    assert any("negative cost" in p
               for p in validate_tiers([Model("neg", -1, 10)]))
    print("test_empty_and_negative: ok")


if __name__ == "__main__":
    test_builtin_tiers_valid()
    test_unsorted_price_rejected()
    test_flat_thresholds_rejected()
    test_empty_and_negative()
    print("agent-router validation tests passed")
