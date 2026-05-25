"""schema 模块单元测试。"""
import sys
from pathlib import Path

import pytest

# 让 tests 能 import 到 scripts/evalbot
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from evalbot.schema import (  # noqa: E402
    EVALUATE_SPECS,
    list_evaluate_types,
    resolve_evaluate_type,
    validate_params,
)


def test_alias_mapping_for_new_types():
    assert resolve_evaluate_type("text-prompt_follow") == "prompt_follow"
    assert resolve_evaluate_type("text-gsb") == "gsb"
    assert resolve_evaluate_type("knowledge-satisfaction_of_needs") == "satisfaction_of_needs"
    assert resolve_evaluate_type("t2i-consistency") == "t2i_consistency_check"


def test_alias_mapping_for_legacy_types_passthrough():
    # 老 5 个 knowledge-* 走直传
    assert resolve_evaluate_type("knowledge-instruction_following") == "knowledge-instruction_following"
    assert resolve_evaluate_type("knowledge-richness") == "knowledge-richness"


def test_alias_mapping_for_unknown_type_passthrough():
    assert resolve_evaluate_type("non-existent-type") == "non-existent-type"


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
    assert {"evaluate_type", "workflow", "required"} == set(sample.keys())
    assert isinstance(sample["required"], list)


def test_all_specs_have_non_empty_workflow():
    for name, spec in EVALUATE_SPECS.items():
        assert spec.workflow, f"{name} 的 workflow 不能为空"
        assert isinstance(spec.required, set)
