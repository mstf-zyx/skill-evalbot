"""client 模块的纯函数与 SSE 解析单元测试（不发起真实网络请求）。"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from evalbot.client import EvalbotClient, _strip_prefix  # noqa: E402


# ---------------------- _strip_prefix ----------------------

def test_strip_prefix_normal():
    assert _strip_prefix("data: hello", "data:") == " hello"


def test_strip_prefix_no_match():
    assert _strip_prefix("event: msg", "data:") == "event: msg"


def test_strip_prefix_does_not_chew_charset():
    """与 str.lstrip 的字符集语义对比：lstrip 会把 d/a/t/:/空格 都吃掉。"""
    raw = "data: data_xx"
    # 错误的旧实现 lstrip("data: ") 会变成 "_xx"
    assert raw.lstrip("data: ") == "_xx"
    # 正确实现保留剩余内容
    assert _strip_prefix(raw, "data:") == " data_xx"


# ---------------------- ability_trigger ----------------------

def _mock_response(lines):
    resp = MagicMock()
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False
    resp.iter_lines.return_value = iter(lines)
    resp.raise_for_status.return_value = None
    return resp


def test_ability_trigger_parses_data_frame():
    lines = [
        "event: message",
        'data: {"task_id": 42, "task_status": "done", "result_str": "ok"}',
    ]
    with patch("evalbot.client.requests.post", return_value=_mock_response(lines)):
        client = EvalbotClient(token="t")
        result = client.ability_trigger("text-expression", "{}")

    assert result is not None
    assert result.task_id == 42
    assert result.task_status == "done"
    assert result.result_str == "ok"


def test_ability_trigger_skips_non_data_lines():
    lines = ["", "event: message", "id: 1", 'data: {"task_id": 1}']
    with patch("evalbot.client.requests.post", return_value=_mock_response(lines)):
        client = EvalbotClient(token="t")
        result = client.ability_trigger("text-expression", "{}")
    assert result is not None and result.task_id == 1


# ---------------------- plugin_trigger ----------------------

def test_plugin_trigger_splits_events_by_id_prefix():
    """data 字段值里含 'id' 子串，旧实现 ('id' in line) 会误分帧。"""
    lines = [
        "id: 1",
        "event: message",
        'data: {"task_id": 100}',  # 含 "id" 子串，但不是新事件起始
        "id: 2",
        "event: message",
        "data: hello",
    ]
    with patch("evalbot.client.requests.post", return_value=_mock_response(lines)):
        client = EvalbotClient(token="t")
        results = client.plugin_trigger("hot_topic", {"top_n": "5"}, 5)

    assert results is not None
    assert len(results) == 2
    assert results[0].event == "message"
    assert results[0].data == '{"task_id": 100}'
    assert results[1].data == "hello"


def test_plugin_trigger_propagates_exception():
    """网络/后端异常应抛出，而非静默吞掉。"""
    with patch("evalbot.client.requests.post", side_effect=RuntimeError("boom")):
        client = EvalbotClient(token="t")
        try:
            client.plugin_trigger("hot_topic", {}, 1)
        except RuntimeError as e:
            assert "boom" in str(e)
        else:
            raise AssertionError("expected RuntimeError to be raised")
