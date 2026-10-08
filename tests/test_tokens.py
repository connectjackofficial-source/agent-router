"""Tests for CJK-aware token counting and routing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_router.router import count_tokens, route


def test_count_tokens_english():
    assert count_tokens("hello world") == 2
    assert count_tokens("a b c d e f g h i j") == 10
    print("test_count_tokens_english: ok")


def test_count_tokens_cjk():
    # 30 CJK chars ≈ 20 tokens, not 1 word
    text = "这是一段很长的中文提示词用于测试路由功能是否正确处理中文字符计数逻辑" * 2
    assert count_tokens(text) > 20
    print("test_count_tokens_cjk: ok")


def test_route_cjk_long_prompt():
    # a long Chinese prompt should not be routed to the cheapest model
    long_zh = "请分析这段中文文本并给出详细的改进建议" * 20
    assert route(long_zh) != "haiku"
    print("test_route_cjk_long_prompt: ok")


def test_route_short_english():
    assert route("hi") == "haiku"
    print("test_route_short_english: ok")


if __name__ == "__main__":
    test_count_tokens_english()
    test_count_tokens_cjk()
    test_route_cjk_long_prompt()
    test_route_short_english()
    print("agent-router token tests passed")
