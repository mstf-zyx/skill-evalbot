---
name: evalbot
description: 通过 Evalbot API 评测大模型回复质量并生成评测用数据。当用户需要对模型回复做指令遵循 / 要点完整 / 真实准确 / 丰富度 / GSB 对比等评估，或需要拉取热点话题作为评测输入时使用。
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
3. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑.env文件，填入你的Evalbot Token
   ```

### 数据生成
```bash
python scripts/evalbot_skill.py data-generation --generate-type hot_topic --top-n 5
```

### 模型评估
```bash
python scripts/evalbot_skill.py model-evaluation \
  --evaluate-type knowledge-instruction_following \
  --params '{"location": "上海", "scene": "聊天", "query": "你的问题", "reply": "模型回复"}'
```

## 命令详情

### data-generation
生成数据（如热点话题）

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| generate-type | string | hot_topic | 生成数据类型，目前仅支持 hot_topic |
| top-n | integer | 5 | 获取前 N 个热点话题 |

### model-evaluation
评估模型回复质量

#### 评估类型与所需参数

| 评估类型 | 所需参数 | 说明 |
|----------|----------|------|
| knowledge-instruction_following | location, scene, query, reply | 指令遵循评估（需要地点、场景、用户查询和模型回复参数） |
| knowledge-scalable-comprehensive_key_points | scene, query, reply | 综合要点评估（需要场景、用户查询和模型回复参数） |
| knowledge-authentic_and_accurate-general | base_time, query, reply | 真实准确性评估（需要基准时间、用户查询和模型回复参数） |
| knowledge-richness | query, reply | 丰富度评估（需要用户查询和模型回复参数） |
| knowledge-gsb-compare | query, domain, reply_a, reply_b, evaluation_criteria | GSB对比评估（需要用户查询、领域、两个模型回复和评估标准参数） |

#### 示例参数

```json
# 指令遵循评估示例参数
{
  "location": "上海",
  "scene": "聊天",
  "query": "请用3句话介绍人工智能",
  "reply": "人工智能是一种模拟人类智能的技术，它可以学习、推理和解决问题。人工智能在各个领域都有应用，比如医疗、金融和教育。随着技术的发展，人工智能将会越来越普及。"
}

# GSB对比评估示例参数
{
  "query": "请解释什么是机器学习",
  "domain": "人工智能",
  "reply_a": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习模式并做出预测。",
  "reply_b": "机器学习是人工智能的一个子集，它涉及算法的开发，这些算法可以从数据中学习模式，进行预测或决策，而无需明确编程。",
  "evaluation_criteria": "评估回复的准确性、完整性和清晰度。"
}
```

## 详细文档
请参考 `references/README.md` 获取完整说明。
