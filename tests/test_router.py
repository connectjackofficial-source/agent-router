"""Tests for agent-router."""
from agent_router.router import route, estimate_cost


def test_short_goes_cheap():
    assert route("hi") == "haiku"
    print("test_short_goes_cheap: ok")


def test_long_goes_expensive():
    assert route("word " * 300) == "opus"
    print("test_long_goes_expensive: ok")


def test_medium():
    assert route("word " * 100) == "sonnet"
    print("test_medium: ok")


def test_cost_estimate():
    cost = estimate_cost("hello")
    assert cost["model"] == "haiku"
    assert cost["estimated_cost"] > 0
    print("test_cost_estimate: ok")


if __name__ == "__main__":
    test_short_goes_cheap()
    test_long_goes_expensive()
    test_medium()
    test_cost_estimate()
    print("all agent-router tests passed")
