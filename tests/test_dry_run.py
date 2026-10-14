"""Tests for agent-router dry_run."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_router.router import TIERS, dry_run


def test_cheap_route_trail():
    info = dry_run("hello")
    assert info["model"] == "haiku"
    assert info["input_words"] == 1
    assert info["skipped"] == []  # nothing skipped, first tier fits
    assert "max_words" in info["reason"]
    print("test_cheap_route_trail: ok")


def test_skipped_tiers_recorded():
    info = dry_run("word " * 100)  # ~100 tokens
    assert info["model"] == "sonnet"
    assert len(info["skipped"]) == 1
    assert info["skipped"][0]["model"] == "haiku"
    assert "max_words" in info["skipped"][0]["reason"]
    print("test_skipped_tiers_recorded: ok")


def test_fallback_to_most_capable():
    info = dry_run("word " * 100001)  # beyond every tier (opus max 100000)
    assert info["model"] == TIERS[-1].name
    assert len(info["skipped"]) == len(TIERS) - 1
    assert "fell back" in info["reason"]
    print("test_fallback_to_most_capable: ok")


def test_cost_fields():
    info = dry_run("hello")
    assert "estimated_cost" in info and info["estimated_cost"] > 0
    assert isinstance(info["input_words"], int)
    print("test_cost_fields: ok")


if __name__ == "__main__":
    test_cheap_route_trail()
    test_skipped_tiers_recorded()
    test_fallback_to_most_capable()
    test_cost_fields()
    print("agent-router dry_run tests passed")
