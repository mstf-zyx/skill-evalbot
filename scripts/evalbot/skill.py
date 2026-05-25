"""Evalbot Skill 业务封装。"""
import json
import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .client import EvalbotClient
from .schema import resolve_evaluate_type, validate_params

logger = logging.getLogger(__name__)


def _wrap_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """后端模板要求 key 形如 ``{{name}}``，此处统一包装。"""
    wrapped: Dict[str, Any] = {}
    for k, v in params.items():
        new_k = k if k.startswith("{{") and k.endswith("}}") else f"{{{{{k}}}}}"
        wrapped[new_k] = v
    return wrapped


class EvalbotSkill:
    """Evalbot Skill 高层封装。详细评估类型与参数说明见 ``references/README.md``。"""

    def __init__(self, token: Optional[str] = None):
        self.client = EvalbotClient(token)

    def data_generation(self, generate_type: str, top_n: int) -> List[str]:
        """生成数据（如热点话题），返回 message 事件载荷列表。"""
        wrapped = _wrap_params({"top_n": str(top_n)})
        quantity = min(10, top_n)
        results = self.client.plugin_trigger(generate_type, wrapped, quantity) or []
        return [item.data for item in results if item.event == "message" and item.data]

    def model_evaluation(
        self, evaluate_type: str, params: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """评估模型回复质量。

        Args:
            evaluate_type: 对外的评估类型，详见 ``references/README.md``。
            params: 评估参数字典，必填字段由 ``schema.EVALUATE_SPECS`` 约束。

        Returns:
            评估结果字典；调用失败时由底层抛出异常。

        Raises:
            ValueError: 必填参数缺失。
        """
        validate_params(evaluate_type, params)
        wrapped = _wrap_params(params)
        backend_type = resolve_evaluate_type(evaluate_type)
        result = self.client.ability_trigger(
            backend_type, json.dumps(wrapped, ensure_ascii=False),
        )
        return asdict(result) if result else None
