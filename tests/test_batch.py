"""Tests for batch routing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_router.router import batch_route, route


def test_batch_route_length():
    prompts = ["hi", "write an essay about distributed systems and retries", "short"]
    results = batch_route(prompts)
    assert len(results) == 3
    assert [r["index"] for r in results] == [0, 1, 2]
    print("test_batch_route_length: ok")


def test_batch_route_models():
    results = batch_route(["hi", "word " * 600])
    assert results[0]["model"] == "haiku"
    assert results[1]["model"] == "opus"
    # long prompt should cost more
    assert results[1]["estimated_cost"] > results[0]["estimated_cost"]
    print("test_batch_route_models: ok")


def test_batch_route_matches_route():
    for p in ["hello", "请分析这段中文文本并给出详细建议" * 10, "x" * 300]:
        r = batch_route([p])[0]
        assert r["model"] == route(p)
    print("test_batch_route_matches_route: ok")


if __name__ == "__main__":
    test_batch_route_length()
    test_batch_route_models()
    test_batch_route_matches_route()
    print("agent-router batch tests passed")
