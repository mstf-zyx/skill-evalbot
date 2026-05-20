#!/usr/bin/env python3
# coding: utf-8
"""
Evalbot Skill
直接调用 Evalbot HTTP API，无需 MCP 协议封装
"""

import os
import sys
import json
import argparse
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import requests

try:
    from dotenv import load_dotenv
    # 尝试加载.env文件
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TRIGGER_SOURCE = "public_skill"


def validate_params(evaluate_type: str, params: Dict[str, str]) -> None:
    """
    验证评估参数是否符合要求
    
    Args:
        evaluate_type: 评估类型
        params: 评估参数
    
    Raises:
        ValueError: 参数不符合要求时
    """
    required_params = {
        "knowledge-instruction_following": {"location", "scene", "query", "reply"},
        "knowledge-scalable-comprehensive_key_points": {"scene", "query", "reply"},
        "knowledge-authentic_and_accurate-general": {"base_time", "query", "reply"},
        "knowledge-richness": {"query", "reply"},
        "knowledge-gsb-compare": {"query", "domain", "reply_a", "reply_b", "evaluation_criteria"},
    }
    
    if evaluate_type not in required_params:
        return
    
    missing_params = required_params[evaluate_type] - set(params.keys())
    if missing_params:
        raise ValueError(
            f"{evaluate_type} 评估需要以下参数: {', '.join(missing_params)}"
        )


# ==================== 数据模型 ====================


@dataclass
class BaseResp:
    error_msg: str = ""
    ret: int = 0
    log_id: str = ""


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


# ==================== Evalbot 客户端 ====================

class EvalbotClient:
    """Evalbot HTTP API 客户端 - 直接调用底层三个接口"""

    BASE_URL = "https://evalbot.zijieapi.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("EVALBOT_TOKEN", "")
        self._logger = logging.getLogger(__name__)

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def ability_trigger(self, evaluate_type: str, params: str) -> Optional[AbilityTriggerRespData]:
        """
        能力评估触发（流式响应）
        POST /evaluate/ability/trigger
        """
        url = f"{self.BASE_URL}/evaluate/ability/trigger"
        payload = {
            "evaluate_type": evaluate_type,
            "params": params,
            "query": "",
            "eval_str": "",
            "creator": "",
            "trigger_source": TRIGGER_SOURCE
        }

        try:
            self._logger.info(f"Triggering ability evaluation: type={evaluate_type}")
            with requests.post(url, json=payload, headers=self._get_headers(), stream=True) as resp:
                resp.raise_for_status()

                for line in resp.iter_lines(decode_unicode=True):
                    if not line or "data" not in line:
                        continue
                    resp_data = line.lstrip("data: ")
                    data = json.loads(resp_data)
                    self._logger.info("Ability trigger success")
                    return AbilityTriggerRespData(**data)

            return None
        except Exception as e:
            self._logger.error(f"Exception in ability_trigger: {e}")
            return None

    def plugin_trigger(self, generate_type: str, params: Dict[str, str], quantity: int) -> Optional[List[PluginTriggerData]]:
        """
        插件触发（流式响应）
        POST /evaluate/plugin/trigger
        """
        url = f"{self.BASE_URL}/evaluate/plugin/trigger"
        payload = {
            "generate_type": generate_type,
            "params": params,
            "quantity": quantity,
            "trigger_source": TRIGGER_SOURCE
        }

        try:
            self._logger.info(f"Triggering plugin: type={generate_type}, quantity={quantity}")
            results = []
            with requests.post(url, json=payload, headers=self._get_headers(), stream=True) as resp:
                resp.raise_for_status()

                tmp = {}
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    # 每一个 event 按照 id: int 起始
                    if "id" in line and tmp:
                        results.append(PluginTriggerData(**tmp))
                        tmp = {}
                    split_data = line.split(": ", 1)
                    if len(split_data) == 2:
                        tmp[split_data[0]] = split_data[1]

                if tmp:
                    results.append(PluginTriggerData(**tmp))

            self._logger.info(f"Plugin trigger success: events={len(results)}")
            return results
        except Exception as e:
            self._logger.error(f"Exception in plugin_trigger: {e}")
            return None


# ==================== Skill 主类 ====================

class EvalbotSkill:
    """Evalbot Skill - 直接调用 HTTP API"""

    def __init__(self, token: Optional[str] = None):
        self.client = EvalbotClient(token)

    def data_generation(self, generate_type: str, top_n: int) -> List[str]:
        """
        生成数据（如热点话题）

        Args:
            generate_type: 生成数据类型，目前仅支持 hot_topic
            top_n: 获取前 N 个热点话题

        Returns:
            生成的数据列表
        """
        # 1. 转换参数格式
        resolve_params = {}
        for k, v in {"top_n": str(top_n)}.items():
            new_k = k if k.startswith("{{") and k.endswith("}}") else f"{{{{{k}}}}}"
            resolve_params[new_k] = v

        # 2. 调用插件触发
        quantity = min(10, top_n)
        results = self.client.plugin_trigger(generate_type, resolve_params, quantity)
        if not results:
            return []

        # 3. 提取 message 事件的数据
        messages = []
        for item in results:
            if item.event == "message" and item.data:
                messages.append(item.data)

        return messages

    def model_evaluation(self, evaluate_type: str, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        评估模型回复质量

        Args:
            evaluate_type: 评估类型
                - knowledge-instruction_following: 指令遵循评估（需要 location, scene, query, reply 参数）
                - knowledge-scalable-comprehensive_key_points: 可扩展-要点完整评估（需要 scene, query, reply 参数）
                - knowledge-authentic_and_accurate-general: 真实准确性评估（需要 base_time, query, reply 参数）
                - knowledge-richness: 丰富度评估（需要 query, reply 参数）
                - knowledge-gsb-compare: GSB对比评估（需要 query, domain, reply_a, reply_b, evaluation_criteria 参数）
            params: 评估参数字典

        Returns:
            评估结果字典
        """
        # 验证参数
        try:
            validate_params(evaluate_type, params)
        except ValueError as e:
            logger.error(f"参数验证失败: {e}")
            return None

        # 1. 转换参数格式
        resolve_params = {}
        for k, v in params.items():
            new_k = k if k.startswith("{{") and k.endswith("}}") else f"{{{{{k}}}}}"
            resolve_params[new_k] = v

        # 2. 调用能力评估
        result = self.client.ability_trigger(evaluate_type, json.dumps(resolve_params, ensure_ascii=False))
        if not result:
            return None

        # 3. 转换为字典返回
        return {
            "is_available": result.is_available,
            "is_expected": result.is_expected,
            "task_id": result.task_id,
            "ability_id": result.ability_id,
            "round_idx": result.round_idx,
            "eval_pass_result": result.eval_pass_result,
            "is_valid": result.is_valid,
            "task_status": result.task_status,
            "eval_ability_type": result.eval_ability_type,
            "result_str": result.result_str,
            "extra_info_str": result.extra_info_str,
            "ability_name": result.ability_name,
            "query": result.query,
            "source_data_id": result.source_data_id,
        }


# ==================== 命令行接口 ====================

def main():
    parser = argparse.ArgumentParser(description="Evalbot Skill - 直接调用 Evalbot HTTP API")
    parser.add_argument(
        "--token",
        type=str,
        default=os.getenv("EVALBOT_TOKEN", ""),
        help="Evalbot 授权 Token"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # data-generation 命令
    data_gen_parser = subparsers.add_parser("data-generation", help="生成数据")
    data_gen_parser.add_argument(
        "--generate-type",
        type=str,
        default="hot_topic",
        help="生成数据类型"
    )
    data_gen_parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="获取前 N 个热点话题"
    )

    # model-evaluation 命令
    eval_parser = subparsers.add_parser("model-evaluation", help="评估模型")
    eval_parser.add_argument(
        "--evaluate-type",
        type=str,
        required=True,
        help="评估类型"
    )
    eval_parser.add_argument(
        "--params",
        type=str,
        required=True,
        help="评估参数（JSON 格式字符串）"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    skill = EvalbotSkill(args.token)

    try:
        if args.command == "data-generation":
            result = skill.data_generation(args.generate_type, args.top_n)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.command == "model-evaluation":
            params = json.loads(args.params)
            result = skill.model_evaluation(args.evaluate_type, params)
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(json.dumps({"error": "Evaluation failed"}, ensure_ascii=False))
                sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
