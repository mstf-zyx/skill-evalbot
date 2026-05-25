---
name: evalbot
description: 通过 Evalbot API 评测大模型回复质量并生成评测用数据。当用户需要对模型回复做指令遵循 / 要点完整 / 真实准确 / 丰富度 / GSB 对比等评估，或需要拉取热点话题作为评测输入时使用。
license: MIT
metadata:
  author: bytedance-evalbot
  version: "1.2.0"
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

##### 文本类（text-*）
| 评估类型 | 所需参数 | 说明 |
|----------|----------|------|
| text-prompt_follow | sp, query, reply | Prompt 遵循评估（含 system prompt 的指令遵循评估） |
| text-expression | query, reply | 文本表达评估（语言流畅度、表达自然度） |
| text-structure | query, reply | 文本结构评估（段落组织、层次清晰度） |
| text-repeatability | query, reply, check_points | 文本重复度评估（需提供 check_points 检查点） |
| text-redundancy | query, reply | 文本冗余度评估（识别无效或重复信息） |
| text-logicality | query, reply | 文本逻辑性评估（推理过程合理性） |
| text-gsb | query, reply_a, reply_b | 文本 GSB 对比评估（无需 domain，相比 knowledge-gsb-compare 更通用） |

##### 知识类（knowledge-*）
| 评估类型 | 所需参数 | 说明 |
|----------|----------|------|
| knowledge-instruction_following | location, scene, query, reply | 指令遵循评估（需要地点、场景、用户查询和模型回复参数） |
| knowledge-scalable-comprehensive_key_points | scene, query, reply | 综合要点评估（需要场景、用户查询和模型回复参数） |
| knowledge-authentic_and_accurate-general | base_time, query, reply | 真实准确性评估（需要基准时间、用户查询和模型回复参数） |
| knowledge-richness | query, reply | 丰富度评估（需要用户查询和模型回复参数） |
| knowledge-gsb-compare | query, domain, reply_a, reply_b, evaluation_criteria | GSB 对比评估（需要用户查询、领域、两个模型回复和评估标准参数） |
| knowledge-satisfaction_of_needs | query, reply | 需求满足度评估（评估回复对用户需求的满足程度） |

##### 图像类（image-*）
| 评估类型 | 所需参数 | 说明 |
|----------|----------|------|
| image-general_evaluation | image_url_list, evaluation_criteria, scoring_criteria | 图像通用评估（按自定义评估准则与评分准则打分） |
| image-realism | image_url_list | 图像真实性评估（评估图像是否符合现实物理规律） |
| image-aesthetic | image_url_list | 图像美学评估（评估构图、色彩等美学维度） |

##### 图文混合类（image_text-*）
| 评估类型 | 所需参数 | 说明 |
|----------|----------|------|
| image_text-logicality | query, reply, image_url_list | 图文逻辑性评估（基于图像的回复逻辑性） |

##### 多模态生成类（t2i / t2v / v2v / i2v）
| 评估类型 | 所需参数 | 说明 |
|----------|----------|------|
| t2i-instruction_following | query, reply, c_type | 文生图指令遵循评估 |
| t2i-consistency | query, reference_imgs, reply_imgs, c_type | 文生图一致性评估（编辑前后图像一致性） |
| t2v-instruction_following | query, reply_videos, c_type | 文生视频指令遵循评估 |
| v2v-instruction_following | query, reply, c_type | 视频生视频指令遵循评估 |
| i2v-instruction_following | query, reply, c_type | 图生视频指令遵循评估 |

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

# 文本 Prompt 遵循示例参数（text-prompt_follow）
{
  "sp": "你是一个心理咨询助手，回复需控制在 200 字以内。",
  "query": "最近压力很大，怎么办？",
  "reply": "我理解你现在的感受……（200 字以内的回复）"
}

# 文本重复度评估示例参数（text-repeatability）
{
  "query": "推荐几部法律题材的韩国电影",
  "reply": "...（待评估的模型回复）...",
  "check_points": "{\"主需\":\"推荐韩国法律题材电影\", \"考察维度\":[\"需求满足\",\"精炼性\"]}"
}

# 文本 GSB 示例参数（text-gsb）
{
  "query": "写一篇美式辣妹写真文案",
  "reply_a": "...回复 A...",
  "reply_b": "...回复 B..."
}

# 图像通用评估示例参数（image-general_evaluation）
{
  "image_url_list": ["https://example.com/img1.png"],
  "evaluation_criteria": "识别图片中是否包含危险元素",
  "scoring_criteria": "0分：存在危险元素；2分：不存在任何危险元素"
}

# 图像真实性 / 美学示例参数（image-realism / image-aesthetic）
{
  "image_url_list": ["https://example.com/img.png"]
}

# 图文逻辑性示例参数（image_text-logicality）
{
  "query": "按时间顺序描述图片中的画面",
  "reply": "...模型回复...",
  "image_url_list": ["https://example.com/a.png", "https://example.com/b.png"]
}

# 文生图指令遵循示例参数（t2i-instruction_following）
{
  "query": "画一只戴着蓝色领结的企鹅",
  "reply": "![image](https://example.com/output.png)",
  "c_type": "instruction_following"
}

# 文生图一致性示例参数（t2i-consistency）
{
  "query": "把图里的桌子换成一只白色的狗",
  "reference_imgs": ["https://example.com/input.png"],
  "reply_imgs": ["https://example.com/output.png"],
  "c_type": "consistency"
}

# 文生视频指令遵循示例参数（t2v-instruction_following）
{
  "query": "年轻女孩在公园长椅上看书并微笑说话",
  "reply_videos": ["https://example.com/video.mp4"],
  "c_type": "t2v_instruction_following"
}
```

## 详细文档
请参考 `references/README.md` 获取完整说明。
