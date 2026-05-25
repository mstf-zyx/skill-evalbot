"""评估类型注册表与参数校验。

单一数据源 ``EVALUATE_SPECS``：对外的 evaluate_type → (后端 workflow_name, 必填参数集合)。
新增/重命名指标只需修改此表。
"""
from typing import Any, Dict, List, NamedTuple, Set


class EvaluateSpec(NamedTuple):
    """单个评估类型的元信息。"""

    workflow: str
    required: Set[str]


# 单一注册表。键为对外 evaluate_type，值为 (后端 workflow_name, 必填字段集合)。
# 注：knowledge-* 老指标的 workflow 与 evaluate_type 同名（即直传）。
EVALUATE_SPECS: Dict[str, EvaluateSpec] = {
    # 知识类（老指标，直传）
    "knowledge-instruction_following": EvaluateSpec(
        "knowledge-instruction_following", {"location", "scene", "query", "reply"}
    ),
    "knowledge-scalable-comprehensive_key_points": EvaluateSpec(
        "knowledge-scalable-comprehensive_key_points", {"scene", "query", "reply"}
    ),
    "knowledge-authentic_and_accurate-general": EvaluateSpec(
        "knowledge-authentic_and_accurate-general", {"base_time", "query", "reply"}
    ),
    "knowledge-richness": EvaluateSpec(
        "knowledge-richness", {"query", "reply"}
    ),
    "knowledge-gsb-compare": EvaluateSpec(
        "knowledge-gsb-compare",
        {"query", "domain", "reply_a", "reply_b", "evaluation_criteria"},
    ),
    "knowledge-satisfaction_of_needs": EvaluateSpec(
        "satisfaction_of_needs", {"query", "reply"}
    ),
    # 文本类
    "text-prompt_follow": EvaluateSpec("prompt_follow", {"sp", "query", "reply"}),
    "text-expression": EvaluateSpec("text_expression", {"query", "reply"}),
    "text-structure": EvaluateSpec("text_structure", {"query", "reply"}),
    "text-repeatability": EvaluateSpec(
        "text_repeatability", {"query", "reply", "check_points"}
    ),
    "text-redundancy": EvaluateSpec("text_redundancy", {"query", "reply"}),
    "text-logicality": EvaluateSpec("text_logicality", {"query", "reply"}),
    "text-gsb": EvaluateSpec("gsb", {"query", "reply_a", "reply_b"}),
    # 图像类
    "image-general_evaluation": EvaluateSpec(
        "general_evaluation",
        {"image_url_list", "evaluation_criteria", "scoring_criteria"},
    ),
    "image-realism": EvaluateSpec("image_realism", {"image_url_list"}),
    "image-aesthetic": EvaluateSpec("image_aesthetic", {"image_url_list"}),
    # 图文混合类
    "image_text-logicality": EvaluateSpec(
        "image_text_logicality", {"query", "reply", "image_url_list"}
    ),
    # 多模态生成类
    "t2i-instruction_following": EvaluateSpec(
        "t2i_instruction_following_check", {"query", "reply", "c_type"}
    ),
    "t2i-consistency": EvaluateSpec(
        "t2i_consistency_check",
        {"query", "reference_imgs", "reply_imgs", "c_type"},
    ),
    "t2v-instruction_following": EvaluateSpec(
        "t2v_instruction_following_check", {"query", "reply_videos", "c_type"}
    ),
    "v2v-instruction_following": EvaluateSpec(
        "v2v_instruction_following_check", {"query", "reply", "c_type"}
    ),
    "i2v-instruction_following": EvaluateSpec(
        "i2v_instruction_following_check", {"query", "reply", "c_type"}
    ),
}


def list_evaluate_types() -> List[Dict[str, Any]]:
    """返回所有注册的评估类型，便于 CLI 输出。"""
    return [
        {
            "evaluate_type": name,
            "workflow": spec.workflow,
            "required": sorted(spec.required),
        }
        for name, spec in EVALUATE_SPECS.items()
    ]


def resolve_evaluate_type(evaluate_type: str) -> str:
    """将对外的 evaluate_type 转换为后端真实 workflow_name；未注册则原样返回。"""
    spec = EVALUATE_SPECS.get(evaluate_type)
    return spec.workflow if spec else evaluate_type


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
