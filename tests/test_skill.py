"""skill 业务封装单元测试。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from evalbot.skill import _wrap_params  # noqa: E402


def test_wrap_params_basic_string_passthrough():
    out = _wrap_params({"query": "q", "reply": "r"})
    assert out == {"{{query}}": "q", "{{reply}}": "r"}


def test_wrap_params_idempotent_for_already_wrapped_key():
    out = _wrap_params({"{{query}}": "q"})
    assert out == {"{{query}}": "q"}


def test_wrap_params_list_serialized_to_json_string():
    """list 必须 JSON 序列化为字符串，否则后端模板替换无法注入 URL。"""
    out = _wrap_params({"image_url_list": ["https://x/a.png", "https://x/b.png"]})
    assert isinstance(out["{{image_url_list}}"], str)
    assert json.loads(out["{{image_url_list}}"]) == [
        "https://x/a.png",
        "https://x/b.png",
    ]


def test_wrap_params_dict_serialized_to_json_string():
    out = _wrap_params({"check_points": {"main": "x"}})
    assert isinstance(out["{{check_points}}"], str)
    assert json.loads(out["{{check_points}}"]) == {"main": "x"}


def test_wrap_params_preserves_chinese_in_list():
    out = _wrap_params({"reply_videos": ["https://x/视频.mp4"]})
    assert "视频.mp4" in out["{{reply_videos}}"]
