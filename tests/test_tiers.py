"""Test custom tiers."""
from agent_router.router import Model, route, load_tiers_json


def test_custom_tiers():
    tiers = [Model("cheap", 0.0001, 10), Model("big", 0.01, 1000)]
    assert route("hi", tiers=tiers) == "cheap"
    assert route("word " * 50, tiers=tiers) == "big"
    print("test_custom_tiers: ok")


def test_load_tiers_json(tmp_path=None):
    import json, tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "tiers.json"
        p.write_text(json.dumps([
            {"name": "t1", "cost_per_1k": 0.001, "max_words": 5}]), encoding="utf-8")
        tiers = load_tiers_json(str(p))
        assert tiers[0].name == "t1"
        assert route("hi", tiers=tiers) == "t1"
    print("test_load_tiers_json: ok")


if __name__ == "__main__":
    test_custom_tiers()
    test_load_tiers_json()
    print("custom tiers tests passed")
