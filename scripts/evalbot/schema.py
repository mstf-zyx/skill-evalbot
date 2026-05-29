"""评估类型注册表与参数校验。"""
from typing import Any, Dict, List, NamedTuple, Set


class EvaluateSpec(NamedTuple):
    """单个评估类型的元信息。

    - ``required``：必填参数集合
    - ``defaults``：可选字段的推荐默认值（用户未传时由 Skill 自动补齐）。
      典型用例：多模态 ``c_type`` 字段对不同评估类型有固定值，避免用户记忆。
    """

    required: Set[str]
    defaults: Dict[str, Any] = {}


# 单一注册表。键即对外 evaluate_type，也就是后端 ``/evaluate/ability/trigger`` 接收的字符串。
EVALUATE_SPECS: Dict[str, EvaluateSpec] = {
    # 知识类
    "knowledge-scalable-comprehensive_key_points": EvaluateSpec({"scene", "query", "reply"}),
    "knowledge-authentic_and_accurate-general": EvaluateSpec({"base_time", "query", "reply"}),
    "knowledge-richness": EvaluateSpec({"query", "reply"}),
    "knowledge-gsb-compare": EvaluateSpec(
        {"query", "domain", "reply_a", "reply_b", "evaluation_criteria"},
    ),
    "knowledge-satisfaction_of_needs": EvaluateSpec({"query", "reply"}),
    # 文本类
    "text-prompt_follow": EvaluateSpec({"sp", "query", "reply"}),
    "text-expression": EvaluateSpec({"query", "reply"}),
    "text-structure": EvaluateSpec({"query", "reply"}),
    "text-repeatability": EvaluateSpec({"query", "reply", "check_points"}),
    "text-redundancy": EvaluateSpec({"query", "reply"}),
    "text-logicality": EvaluateSpec({"query", "reply"}),
    "text-gsb": EvaluateSpec({"query", "reply_a", "reply_b"}),
    # 图像类
    "image-general_evaluation": EvaluateSpec(
        {"image_url_list", "evaluation_criteria", "scoring_criteria"},
    ),
    "image-realism": EvaluateSpec({"image_url_list"}),
    "image-aesthetic": EvaluateSpec({"image_url_list"}),
    # 多模态生成类：c_type 是固定的能力 key，由 schema 提供默认值，调用方可不传
    "t2i-instruction_following": EvaluateSpec(
        {"query", "reply", "c_type"},
        {"c_type": "instruction_following"},
    ),
    "t2i-consistency": EvaluateSpec(
        {"query", "reference_imgs", "reply_imgs", "c_type"},
        {"c_type": "consistency"},
    ),
    "t2v-instruction_following": EvaluateSpec(
        {"query", "reply_videos", "c_type"},
        {"c_type": "t2v_instruction_following"},
    ),
    "v2v-instruction_following": EvaluateSpec(
        {"query", "reply", "c_type"},
        {"c_type": "instruction_following"},
    ),
    "i2v-instruction_following": EvaluateSpec(
        {"query", "reply", "c_type"},
        {"c_type": "t2v_instruction_following"},
    ),
}


def list_evaluate_types() -> List[Dict[str, Any]]:
    """返回所有注册的评估类型，便于 CLI 输出。"""
    return [
        {
            "evaluate_type": name,
            "required": sorted(spec.required),
            "defaults": dict(spec.defaults),
        }
        for name, spec in EVALUATE_SPECS.items()
    ]


def apply_defaults(evaluate_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """为未传字段补齐 schema 中的默认值。返回新 dict，不修改入参。"""
    spec = EVALUATE_SPECS.get(evaluate_type)
    if spec is None or not spec.defaults:
        return dict(params)
    merged = dict(spec.defaults)
    merged.update(params)  # 用户传入优先，覆盖默认
    return merged


def validate_params(evaluate_type: str, params: Dict[str, Any]) -> None:
    """校验必填参数是否齐全。

    Args:
        evaluate_type: 对外的评估类型。
        params: 评估参数。

    Raises:
        ValueError: 必填参数缺失时抛出。
    """
    spec = EVALUATE_SPECS.get(evaluate_type)
    if spec is None:
        return  # 未注册的类型不做校验，允许后端自行处理
    missing = spec.required - set(params.keys())
    if missing:
        raise ValueError(
            f"{evaluate_type} 评估需要以下参数: {', '.join(sorted(missing))}"
        )
