---
name: evalbot
description: 直接调用 Evalbot HTTP API，支持数据生成和模型评估
license: MIT
metadata:
  author: bytedance-evalbot
  version: "1.0.0"
  homepage: "https://evalbot.bytedance.com"
  tags: ["data-generation", "model-evaluation", "evalbot"]
compatibility: "需要Python 3.8+ 和 Evalbot API访问权限，支持所有AgentSkills兼容平台"
---

# Evalbot 技能使用说明

## 功能简介
本技能提供直接调用 Evalbot HTTP API 的能力，支持以下功能：
- 数据生成：如热点话题生成
- 模型评估：评估模型回复质量的多个维度

## 快速开始

### 环境准备
1. 确保已安装 Python 3.8+
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量（可选）：
   ```bash
   export EVALBOT_TOKEN="your-evalbot-token"
   ```

### 数据生成
```bash
python scripts/evalbot_skill.py data-generation --generate_type hot_topic --top_n 5
```

### 模型评估
```bash
python scripts/evalbot_skill.py model-evaluation \
  --evaluate_type knowledge-instruction_following \
  --params '{"query": "你的问题", "response": "模型回复"}'
```

## 命令详情

### data-generation
生成数据（如热点话题）

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| generate_type | string | hot_topic | 生成数据类型，目前仅支持 hot_topic |
| top_n | integer | 5 | 获取前 N 个热点话题 |

### model-evaluation
评估模型回复质量

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| evaluate_type | string | 是 | 评估类型，支持：<br>- knowledge-instruction_following: 指令遵循评估<br>- knowledge-scalable-comprehensive_key_points: 综合要点评估<br>- knowledge-authentic_and_accurate-general: 真实准确性评估<br>- knowledge-richness: 丰富度评估<br>- knowledge-gsb-compare: GSB 对比评估 |
| params | string | 是 | 评估参数（JSON 格式字符串） |

## 详细文档
请参考 `references/README.md` 获取完整说明和 API 文档。

## 版本历史
- v1.0.0: 初始版本，支持数据生成和模型评估功能
