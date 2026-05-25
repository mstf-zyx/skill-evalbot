"""Evalbot HTTP 客户端。"""
import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

TRIGGER_SOURCE = "public_skill"

# (连接超时, 读取超时)，读取留 10 分钟以匹配后端流式评估耗时上限。
DEFAULT_TIMEOUT: Tuple[int, int] = (5, 600)


@dataclass
class PluginTriggerData:
    id: int = 0
    event: str = ""
    data: Optional[str] = None


@dataclass
class AbilityTriggerRespData:
    is_available: bool = False
    is_expected: bool = False
    task_id: int = 0
    ability_id: int = 0
    round_idx: int = 0
    eval_pass_result: int = 0
    is_valid: bool = False
    task_status: str = ""
    eval_ability_type: str = ""
    result_str: str = ""
    extra_info_str: str = ""
    ability_name: str = ""
    query: str = ""
    source_data_id: str = ""


def _strip_prefix(line: str, prefix: str) -> str:
    """安全的前缀剥离。等价于 Python 3.9+ 的 ``str.removeprefix``，显式实现以避免 ``str.lstrip`` 的字符集语义。"""
    return line[len(prefix):] if line.startswith(prefix) else line


class EvalbotClient:
    """Evalbot HTTP API 客户端。"""

    BASE_URL = "https://evalbot.zijieapi.com"

    def __init__(self, token: Optional[str] = None, timeout: Tuple[int, int] = DEFAULT_TIMEOUT):
        self.token = token or os.getenv("EVALBOT_TOKEN", "")
        self.timeout = timeout

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def ability_trigger(self, evaluate_type: str, params: str) -> Optional[AbilityTriggerRespData]:
        """能力评估触发（流式响应，POST /evaluate/ability/trigger）。

        注：后端为 SSE 流，但能力评估只关心最终结果。这里取**首条** ``data:`` 帧
        作为最终结果——当前后端在评估完成后只发送一条 data 帧。若未来后端改为
        多帧输出，需要改为收集到结束事件后再返回。
        """
        url = f"{self.BASE_URL}/evaluate/ability/trigger"
        payload = {
            "evaluate_type": evaluate_type,
            "params": params,
            "query": "",
            "eval_str": "",
            "creator": "",
            "trigger_source": TRIGGER_SOURCE,
        }

        logger.info("Triggering ability evaluation: type=%s", evaluate_type)
        try:
            with requests.post(
                url, json=payload, headers=self._get_headers(),
                stream=True, timeout=self.timeout,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data:"):
                        continue
                    raw = _strip_prefix(line, "data:").lstrip()
                    data = json.loads(raw)
                    logger.info("Ability trigger success")
                    return AbilityTriggerRespData(**data)
            return None
        except Exception:
            logger.exception("Exception in ability_trigger")
            raise

    def plugin_trigger(
        self, generate_type: str, params: Dict[str, str], quantity: int,
    ) -> Optional[List[PluginTriggerData]]:
        """插件触发（流式响应，POST /evaluate/plugin/trigger）。

        SSE 帧格式::

            id: 1
            event: message
            data: ...

        上一帧以新的 ``id:`` 行结束，故按 ``startswith("id:")`` 严格分帧。
        """
        url = f"{self.BASE_URL}/evaluate/plugin/trigger"
        payload = {
            "generate_type": generate_type,
            "params": params,
            "quantity": quantity,
            "trigger_source": TRIGGER_SOURCE,
        }

        logger.info("Triggering plugin: type=%s, quantity=%s", generate_type, quantity)
        results: List[PluginTriggerData] = []
        tmp: Dict[str, str] = {}
        try:
            with requests.post(
                url, json=payload, headers=self._get_headers(),
                stream=True, timeout=self.timeout,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    # 新事件起始：严格按 SSE 字段名前缀判定，避免误匹配 data 中含 "id" 字符。
                    if line.startswith("id:") and tmp:
                        results.append(PluginTriggerData(**tmp))
                        tmp = {}
                    key, sep, value = line.partition(": ")
                    if sep:
                        tmp[key] = value
                if tmp:
                    results.append(PluginTriggerData(**tmp))
            logger.info("Plugin trigger success: events=%d", len(results))
            return results
        except Exception:
            logger.exception("Exception in plugin_trigger")
            raise
