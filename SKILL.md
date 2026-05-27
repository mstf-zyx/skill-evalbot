---
name: evalbot
description: 通过 Evalbot API 评测大模型回复质量并生成评测用数据。当用户需要对模型回复做指令遵循 / 要点完整 / 真实准确 / 丰富度 / GSB 对比等评估，或需要拉取热点话题作为评测输入时使用。
license: MIT
metadata:
  author: bytedance-evalbot
  version: "1.2.1"
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

#### 评估类型一览

> 各指标的所需参数与示例请见 `references/README.md`，或运行 `python scripts/evalbot_skill.py list-types` 获取最新机器可读列表（含必填字段与默认值）。

##### 文本类（text-*）
| 评估类型 | 说明 |
|----------|------|
| text-prompt_follow | Prompt 遵循评估（含 system prompt 的指令遵循评估） |
| text-expression | 文本表达评估（语言流畅度、表达自然度） |
| text-structure | 文本结构评估（段落组织、层次清晰度） |
| text-repeatability | 文本重复度评估（需提供 check_points 检查点） |
| text-redundancy | 文本冗余度评估（识别无效或重复信息） |
| text-logicality | 文本逻辑性评估（推理过程合理性） |
| text-gsb | 文本 GSB 对比评估（无需 domain，相比 knowledge-gsb-compare 更通用） |

##### 知识类（knowledge-*）
| 评估类型 | 说明 |
|----------|------|
| knowledge-instruction_following | 指令遵循评估（基于地点与场景） |
| knowledge-scalable-comprehensive_key_points | 可扩展-要点完整评估 |
| knowledge-authentic_and_accurate-general | 真实准确性评估（基于基准时间） |
| knowledge-richness | 丰富度评估 |
| knowledge-gsb-compare | GSB 对比评估（含 domain 与评估标准） |
| knowledge-satisfaction_of_needs | 需求满足度评估 |

##### 图像类（image-*）
| 评估类型 | 说明 |
|----------|------|
| image-general_evaluation | 图像通用评估（按自定义评估准则与评分准则打分） |
| image-realism | 图像真实性评估（评估图像是否符合现实物理规律） |
| image-aesthetic | 图像美学评估（评估构图、色彩等美学维度） |

##### 多模态生成类（t2i / t2v / v2v / i2v）
| 评估类型 | 说明 |
|----------|------|
| t2i-instruction_following | 文生图指令遵循评估 |
| t2i-consistency | 文生图一致性评估（编辑前后图像一致性） |
| t2v-instruction_following | 文生视频指令遵循评估 |
| v2v-instruction_following | 视频生视频指令遵循评估 |
| i2v-instruction_following | 图生视频指令遵循评估 |

## 详细文档
请参考 `references/README.md` 获取完整说明（含每个指标的所需参数与可运行示例）。
