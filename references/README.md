# Evalbot Skill

直接调用 Evalbot HTTP API 的 Python Skill，无需 MCP 协议封装。

## 底层 API

该 Skill 直接调用 Evalbot 的三个 HTTP 接口：

1. **GET** `/evaluate/get_ids?id_type={type}&id_key={key}` - 获取评估 ID
2. **POST** `/evaluate/ability/trigger` - 能力评估触发（流式响应）
3. **POST** `/evaluate/plugin/trigger` - 插件触发（流式响应）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 环境变量配置

```bash
export EVALBOT_TOKEN="your_token"  # Evalbot 授权 Token
```

### 命令行使用

**数据生成:**
```bash
python evalbot_skill.py data-generation --generate-type hot_topic --top-n 5
```

**模型评估:**
```bash
python evalbot_skill.py model-evaluation \
  --evaluate-type "knowledge-authentic_and_accurate-general" \
  --params '{"query": "问题", "reply": "回复", "base_time": "2025-09-16"}'
```

**使用 Token 参数:**
```bash
python evalbot_skill.py --token "your_token" data-generation --top-n 5
```

## 支持的评估类型及参数要求

### 1. 指令遵循评估 (knowledge-instruction_following)
**描述**：评估模型是否正确遵循用户指令
**参数要求**：
- `location`: 用户地理位置，例如"深圳南山"
- `scene`: 场景类型，例如"知识问答 - 本地生活"
- `question`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python evalbot_skill.py model-evaluation --evaluate-type "knowledge-instruction_following" --params '{"location": "深圳南山", "scene": "知识问答 - 本地生活", "question": "优衣库199元的牛仔裤为什么被消费者觉得价格偏高？", "reply": "优衣库199元牛仔裤价格偏高主要是因为品牌定位和市场竞争两方面原因。"}'
```

### 2. 可扩展-要点完整评估 (knowledge-scalable-comprehensive_key_points)
**描述**：评估模型回复的要点完整性
**参数要求**：
- `scene`: 场景类型，例如"知识问答 - 本地生活"
- `question`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python evalbot_skill.py model-evaluation --evaluate-type "knowledge-scalable-comprehensive_key_points" --params '{"scene": "知识问答 - 本地生活", "question": "优衣库199元的牛仔裤为什么被消费者觉得价格偏高？", "reply": "优衣库199元牛仔裤价格偏高主要是因为品牌定位和市场竞争两方面原因。"}'
```

### 3. 真实准确性评估 (knowledge-authentic_and_accurate-general)
**描述**：评估模型回复内容的真实性和准确性
**参数要求**：
- `base_time`: 基准时间，例如"2025-09-16"
- `question`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python evalbot_skill.py model-evaluation --evaluate-type "knowledge-authentic_and_accurate-general" --params '{"base_time": "2025-09-16", "question": "优衣库199元的牛仔裤为什么被消费者觉得价格偏高？", "reply": "优衣库199元牛仔裤价格偏高主要是因为品牌定位和市场竞争两方面原因。"}'
```

### 4. 丰富度评估 (knowledge-richness)
**描述**：评估模型回复内容的丰富度和详细程度
**参数要求**：
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python evalbot_skill.py model-evaluation --evaluate-type "knowledge-richness" --params '{"query": "优衣库199元的牛仔裤为什么被消费者觉得价格偏高？", "reply": "优衣库199元牛仔裤价格偏高主要是因为品牌定位和市场竞争两方面原因。"}'
```

### 5. GSB对比评估 (knowledge-gsb-compare)
**描述**：对比两个模型回复的优劣
**参数要求**：
- `query`: 用户问题
- `domain`: 问题领域，例如"消费"或"科技"
- `reply_a`: 模型A的回复
- `reply_b`: 模型B的回复
- `evaluation_criteria`: 评估标准，例如"准确性, 全面性, 深度"

**示例**：
```bash
python evalbot_skill.py model-evaluation --evaluate-type "knowledge-gsb-compare" --params '{"query": "优衣库199元的牛仔裤为什么被消费者觉得价格偏高？", "domain": "消费", "reply_a": "优衣库199元牛仔裤价格偏高主要是因为品牌定位原因", "reply_b": "优衣库199元牛仔裤价格偏高主要是因为品牌定位和市场竞争两方面原因", "evaluation_criteria": "准确性, 全面性"}'
```

## 代码中使用

```python
from evalbot_skill import EvalbotSkill

skill = EvalbotSkill(token="your_token")

# 数据生成
result = skill.data_generation("hot_topic", 5)

# 模型评估
result = skill.model_evaluation(
    "knowledge-authentic_and_accurate-general",
    {"query": "问题", "reply": "回复", "base_time": "2025-09-16"}
)
```
