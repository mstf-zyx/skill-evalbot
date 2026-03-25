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
  --params '{"query": "你的问题", "response": "模型回复"}'
```

## 详细文档
请参考 `references/README.md` 获取完整说明。
