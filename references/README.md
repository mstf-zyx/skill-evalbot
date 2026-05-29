# Evalbot Skill

直接调用 Evalbot HTTP API 的 Python Skill，无需 MCP 协议封装。

## 底层 API

该 Skill 直接调用 Evalbot 的两个 HTTP 接口：

1. **POST** `/evaluate/ability/trigger` - 能力评估触发（流式响应）
2. **POST** `/evaluate/plugin/trigger` - 插件触发（流式响应）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 环境变量配置

```bash
export EVALBOT_TOKEN="your_token"  # Evalbot 授权 Token
```

#### 获取 Evalbot Token

登录 [https://evalbot.bytedance.com](https://evalbot.bytedance.com)，按下图步骤创建并复制 Token：

![获取 Evalbot Token](../assets/get-token.gif)

若动图无法加载，可按以下文字步骤操作：

1. 浏览器打开 [https://evalbot.bytedance.com](https://evalbot.bytedance.com) 并完成登录。
2. 点击右上角头像进入个人设置页面，点击左侧「Token生成」。
3. 点击「生成新Token」创建一个新的 Token 并复制。
4. 填入本地 `.env` 文件的 `EVALBOT_TOKEN` 字段。

### 命令行使用

**数据生成:**
```bash
python scripts/evalbot_skill.py data-generation --generate-type hot_topic --top-n 5
```

**模型评估:**
```bash
python scripts/evalbot_skill.py model-evaluation \
  --evaluate-type "knowledge-authentic_and_accurate-general" \
  --params '{"query": "问题", "reply": "回复", "base_time": "2025-09-16"}'
```

**使用 Token 参数:**
```bash
python scripts/evalbot_skill.py --token "your_token" data-generation --top-n 5
```

## 支持的评估类型及参数要求

> 评估类型按业务领域分组，命名规则为 `{领域}-{指标}`。

### 一、知识类（knowledge-*）

#### 1. 可扩展-要点完整评估 (knowledge-scalable-comprehensive_key_points)
**描述**：评估模型回复的要点完整性
**参数要求**：
- `scene`: 场景类型，例如"知识问答 - 本地生活"
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "knowledge-scalable-comprehensive_key_points" --params '{"scene": "知识问答 - 本地生活", "query": "优衣库199元的牛仔裤为什么被消费者觉得价格偏高？", "reply": "优衣库199元牛仔裤价格偏高主要是因为品牌定位和市场竞争两方面原因。"}'
```

#### 2. 真实准确性评估 (knowledge-authentic_and_accurate-general)
**描述**：评估模型回复内容的真实性和准确性
**参数要求**：
- `base_time`: 基准时间，例如"2025-09-16"
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "knowledge-authentic_and_accurate-general" --params '{"base_time": "2025-09-16", "query": "优衣库199元的牛仔裤为什么被消费者觉得价格偏高？", "reply": "优衣库199元牛仔裤价格偏高主要是因为品牌定位和市场竞争两方面原因。"}'
```

#### 3. 丰富度评估 (knowledge-richness)
**描述**：评估模型回复内容的丰富度和详细程度
**参数要求**：
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "knowledge-richness" --params '{"query": "优衣库199元的牛仔裤为什么被消费者觉得价格偏高？", "reply": "优衣库199元牛仔裤价格偏高主要是因为品牌定位和市场竞争两方面原因。"}'
```

#### 4. GSB 对比评估 (knowledge-gsb-compare)
**描述**：对比两个模型回复的优劣（带领域信息）
**参数要求**：
- `query`: 用户问题
- `domain`: 问题领域，例如"消费"或"科技"
- `reply_a`: 模型 A 的回复
- `reply_b`: 模型 B 的回复
- `evaluation_criteria`: 评估标准，例如"准确性, 全面性, 深度"

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "knowledge-gsb-compare" --params '{"query": "优衣库199元的牛仔裤为什么被消费者觉得价格偏高？", "domain": "消费", "reply_a": "优衣库199元牛仔裤价格偏高主要是因为品牌定位原因", "reply_b": "优衣库199元牛仔裤价格偏高主要是因为品牌定位和市场竞争两方面原因", "evaluation_criteria": "准确性, 全面性"}'
```

#### 5. 需求满足度评估 (knowledge-satisfaction_of_needs)
**描述**：评估回复对用户原始需求的满足程度
**参数要求**：
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "knowledge-satisfaction_of_needs" --params '{"query": "双流那个地方按肩颈按摩比较好？", "reply": "推荐醉仙蟲·推拿按摩(三强西路店)..."}'
```

### 二、文本类（text-*）

#### 6. Prompt 遵循评估 (text-prompt_follow)
**描述**：在给定 system prompt 场景下评估模型是否严格遵循约束
**参数要求**：
- `sp`: system prompt
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "text-prompt_follow" --params '{"sp": "你是一个心理咨询助手，回复需控制在200字内。", "query": "最近压力很大", "reply": "我理解你现在的感受..."}'
```

#### 7. 文本表达评估 (text-expression)
**描述**：评估回复的语言表达自然度、流畅度
**参数要求**：
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "text-expression" --params '{"query": "1月18号是什么星座？", "reply": "1月18日出生的人是摩羯座..."}'
```

#### 8. 文本结构评估 (text-structure)
**描述**：评估回复的段落组织、层次清晰度
**参数要求**：
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "text-structure" --params '{"query": "做鼻子进口假体多少钱", "reply": "进口假体隆鼻的价格一般为8000-15000元..."}'
```

#### 9. 文本重复度评估 (text-repeatability)
**描述**：评估回复中是否存在内容重复，需提供检查点
**参数要求**：
- `query`: 用户问题
- `reply`: 模型回复
- `check_points`: 检查点（JSON 字符串，描述主需/次需/考察维度等）

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "text-repeatability" --params '{"query": "推荐韩国法律电影", "reply": "...", "check_points": "{\"主需\":\"推荐韩国法律题材电影\"}"}'
```

#### 10. 文本冗余度评估 (text-redundancy)
**描述**：评估回复中是否存在与用户需求无关的冗余信息
**参数要求**：
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "text-redundancy" --params '{"query": "mbb是什么", "reply": "MBB有多种含义..."}'
```

#### 11. 文本逻辑性评估 (text-logicality)
**描述**：评估回复中推理过程的合理性
**参数要求**：
- `query`: 用户问题
- `reply`: 模型回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "text-logicality" --params '{"query": "从0到3之间随机选两个数x和y，用1、x、y当边长能组成三角形的概率？", "reply": "概率为4.5÷9=1/2。"}'
```

#### 12. 文本 GSB 评估 (text-gsb)
**描述**：通用文本 GSB 对比，无需 domain
**参数要求**：
- `query`: 用户问题
- `reply_a`: 模型 A 的回复
- `reply_b`: 模型 B 的回复

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "text-gsb" --params '{"query": "写一篇美式辣妹写真文案", "reply_a": "...A...", "reply_b": "...B..."}'
```

### 三、图像类（image-*）

#### 13. 图像通用评估 (image-general_evaluation)
**描述**：基于自定义评估准则与评分准则对图像打分
**参数要求**：
- `image_url_list`: 图像 URL 列表
- `evaluation_criteria`: 评估准则
- `scoring_criteria`: 评分准则（如"0分：xxx；1分：xxx；2分：xxx"）

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "image-general_evaluation" --params '{"image_url_list": ["https://example.com/img.png"], "evaluation_criteria": "识别图片中是否包含危险元素", "scoring_criteria": "0分：存在危险元素\n2分：不存在任何危险元素"}'
```

#### 14. 图像真实性评估 (image-realism)
**描述**：评估图像是否符合现实物理与视觉规律
**参数要求**：
- `image_url_list`: 图像 URL 列表

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "image-realism" --params '{"image_url_list": ["https://example.com/img.png"]}'
```

#### 15. 图像美学评估 (image-aesthetic)
**描述**：评估图像的构图、色彩、光影等美学维度
**参数要求**：
- `image_url_list`: 图像 URL 列表

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "image-aesthetic" --params '{"image_url_list": ["https://example.com/img.png"]}'
```

### 四、多模态生成类（t2i / t2v / v2v / i2v）

#### 16. 文生图指令遵循评估 (t2i-instruction_following)
**描述**：评估文生图模型对 prompt 的遵循程度
**参数要求**：
- `query`: 文生图 prompt
- `reply`: 模型回复（含图像 markdown 链接）
- `c_type`: 检测类型，例如 `instruction_following`

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "t2i-instruction_following" --params '{"query": "画一只戴蓝色领结的企鹅", "reply": "![image](https://example.com/out.png)", "c_type": "instruction_following"}'
```

#### 17. 文生图一致性评估 (t2i-consistency)
**描述**：评估图像编辑前后的一致性（按指令修改 + 保留无关区域）
**参数要求**：
- `query`: 编辑指令
- `reference_imgs`: 原图 URL 列表
- `reply_imgs`: 编辑后图像 URL 列表
- `c_type`: 检测类型，例如 `consistency`

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "t2i-consistency" --params '{"query": "把图里的桌子换成一只白色的狗", "reference_imgs": ["https://example.com/in.png"], "reply_imgs": ["https://example.com/out.png"], "c_type": "consistency"}'
```

#### 18. 文生视频指令遵循评估 (t2v-instruction_following)
**描述**：评估文生视频模型对 prompt 的遵循程度
**参数要求**：
- `query`: 文生视频 prompt
- `reply_videos`: 视频 URL 列表
- `c_type`: 检测类型，例如 `t2v_instruction_following`

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "t2v-instruction_following" --params '{"query": "年轻女孩在公园长椅上看书并微笑说话", "reply_videos": ["https://example.com/video.mp4"], "c_type": "t2v_instruction_following"}'
```

#### 19. 视频生视频指令遵循评估 (v2v-instruction_following)
**描述**：评估视频生视频模型对 prompt 的遵循程度
**参数要求**：
- `query`: prompt
- `reply`: 模型回复（含视频或图像链接）
- `c_type`: 检测类型，例如 `instruction_following`

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "v2v-instruction_following" --params '{"query": "...", "reply": "...", "c_type": "instruction_following"}'
```

#### 20. 图生视频指令遵循评估 (i2v-instruction_following)
**描述**：评估图生视频模型对 prompt 的遵循程度
**参数要求**：
- `query`: prompt
- `reply`: 模型回复（含视频或图像链接）
- `c_type`: 检测类型，例如 `t2v_instruction_following`

**示例**：
```bash
python scripts/evalbot_skill.py model-evaluation --evaluate-type "i2v-instruction_following" --params '{"query": "把这张图放进野餐场景，老奶奶笑着说今天野餐真开心", "reply": "...", "c_type": "t2v_instruction_following"}'
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
