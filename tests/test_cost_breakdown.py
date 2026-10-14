"""Tests for agent-router cost_breakdown."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_router.router import cost_breakdown


def test_rollup_by_model():
    prompts = ["hello", "world", "word " * 100]  # haiku + sonnet
    bd = cost_breakdown(prompts)
    assert set(bd["by_model"]) == {"haiku", "sonnet"}
    assert bd["total"] == round(sum(bd["by_model"].values()), 6)
    assert bd["total"] > 0
    print("test_rollup_by_model: ok")


def test_all_same_model():
    bd = cost_breakdown(["a", "b", "c"])
    assert set(bd["by_model"]) == {"haiku"}
    print("test_all_same_model: ok")


def test_empty_batch():
    bd = cost_breakdown([])
    assert bd["total"] == 0.0
    assert bd["by_model"] == {}
    print("test_empty_batch: ok")


if __name__ == "__main__":
    test_rollup_by_model()
    test_all_same_model()
    test_empty_batch()
    print("agent-router cost_breakdown tests passed")
