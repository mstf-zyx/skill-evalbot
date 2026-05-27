"""schema 模块单元测试。"""
import sys
from pathlib import Path

import pytest

# 让 tests 能 import 到 scripts/evalbot
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from evalbot.schema import (  # noqa: E402
    EVALUATE_SPECS,
    apply_defaults,
    list_evaluate_types,
    validate_params,
)


def test_validate_params_passes_when_required_present():
    validate_params("text-expression", {"query": "q", "reply": "r"})
    validate_params(
        "image-general_evaluation",
        {
            "image_url_list": ["http://x"],
            "evaluation_criteria": "c",
            "scoring_criteria": "s",
        },
    )


def test_validate_params_raises_on_missing():
    with pytest.raises(ValueError, match="reply"):
        validate_params("text-expression", {"query": "q"})

    with pytest.raises(ValueError, match="check_points"):
        validate_params("text-repeatability", {"query": "q", "reply": "r"})


def test_validate_params_unknown_type_skipped():
    # 未注册类型不应报错（让后端去判定）
    validate_params("non-existent-type", {})


def test_validate_params_allows_extra_fields():
    # 额外字段（如 model_name）应被允许，由后端透传
    validate_params(
        "text-expression",
        {"query": "q", "reply": "r", "vision_model_name": "x", "history": ""},
    )


def test_list_evaluate_types_shape():
    items = list_evaluate_types()
    assert len(items) == len(EVALUATE_SPECS)
    sample = items[0]
    assert {"evaluate_type", "required", "defaults"} == set(sample.keys())
    assert isinstance(sample["required"], list)
    assert isinstance(sample["defaults"], dict)


def test_all_specs_have_required_set():
    for name, spec in EVALUATE_SPECS.items():
        assert isinstance(spec.required, set), f"{name} 的 required 必须是 set"
        assert spec.required, f"{name} 至少应有一个必填字段"


# ---------------------- apply_defaults ----------------------

def test_apply_defaults_fills_c_type_for_t2i():
    """t2i-instruction_following 的 c_type 默认值由 schema 提供，调用方可不传。"""
    merged = apply_defaults(
        "t2i-instruction_following",
        {"query": "q", "reply": "r"},
    )
    assert merged["c_type"] == "instruction_following"
    # 此时校验应通过
    validate_params("t2i-instruction_following", merged)


def test_apply_defaults_user_value_wins():
    """用户传入的值优先于 schema 默认值。"""
    merged = apply_defaults(
        "t2i-instruction_following",
        {"query": "q", "reply": "r", "c_type": "custom_type"},
    )
    assert merged["c_type"] == "custom_type"


def test_apply_defaults_no_op_when_no_defaults():
    """无默认值的指标返回新 dict，不修改入参。"""
    src = {"query": "q", "reply": "r"}
    merged = apply_defaults("text-expression", src)
    assert merged == src
    assert merged is not src  # 必须是新 dict


def test_apply_defaults_unknown_type_passthrough():
    src = {"foo": "bar"}
    merged = apply_defaults("non-existent", src)
    assert merged == src


def test_list_evaluate_types_includes_defaults_field():
    items = list_evaluate_types()
    by_name = {it["evaluate_type"]: it for it in items}
    assert by_name["t2i-instruction_following"]["defaults"] == {
        "c_type": "instruction_following"
    }
    assert by_name["text-expression"]["defaults"] == {}


def test_all_multimodal_specs_have_c_type_default():
    """所有需要 c_type 的指标都应在 schema 中给出默认值，避免用户记忆。"""
    for name, spec in EVALUATE_SPECS.items():
        if "c_type" in spec.required:
            assert "c_type" in spec.defaults, f"{name} 缺少 c_type 默认值"

