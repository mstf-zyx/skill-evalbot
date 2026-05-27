#!/usr/bin/env python3
# coding: utf-8
"""Evalbot Skill CLI 入口。

子命令：
- ``data-generation``：生成数据（如热点话题）
- ``model-evaluation``：评估模型回复质量
- ``list-types``：列出所有支持的评估类型与必填参数
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path

# 允许以 ``python scripts/evalbot_skill.py`` 直接运行：把脚本所在目录加入 sys.path。
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from evalbot import EvalbotSkill, list_evaluate_types  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evalbot Skill - 直接调用 Evalbot HTTP API")
    parser.add_argument(
        "--token", type=str, default=os.getenv("EVALBOT_TOKEN", ""),
        help="Evalbot 授权 Token（亦可通过 EVALBOT_TOKEN 环境变量提供）",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    gen = subparsers.add_parser("data-generation", help="生成数据")
    gen.add_argument("--generate-type", type=str, default="hot_topic", help="生成数据类型")
    gen.add_argument("--top-n", type=int, default=5, help="获取前 N 个热点话题")

    eval_p = subparsers.add_parser("model-evaluation", help="评估模型")
    eval_p.add_argument("--evaluate-type", type=str, required=True, help="评估类型，可用 list-types 查看")
    eval_p.add_argument("--params", type=str, required=True, help="评估参数（JSON 字符串）")

    subparsers.add_parser("list-types", help="列出所有支持的评估类型与必填参数")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list-types":
        print(json.dumps(list_evaluate_types(), ensure_ascii=False, indent=2))
        return

    skill = EvalbotSkill(args.token)

    if args.command == "data-generation":
        result = skill.data_generation(args.generate_type, args.top_n)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.command == "model-evaluation":
        params = json.loads(args.params)
        try:
            result = skill.model_evaluation(args.evaluate_type, params)
        except ValueError as e:
            # 必填参数缺失等参数级错误：给独立退出码，方便脚本编排区分
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
            sys.exit(3)
        except RuntimeError as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
            sys.exit(2)
        if result is None:
            print(json.dumps({"error": "Evaluation returned no data"}, ensure_ascii=False))
            sys.exit(1)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
