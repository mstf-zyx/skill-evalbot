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

## Token 获取方式

访问 [Evalbot 官网](https://evalbot.bytedance.com/) 注册账号即可获取授权 Token。

## 配置方式

### 方法1：使用 .env 文件（推荐）

1. 创建 .env 文件：
```bash
echo "EVALBOT_TOKEN=your_token_here" > .env
```

2. 设置文件权限（推荐）：
```bash
chmod 600 .env
```

3. 直接运行即可自动加载 token

### 方法2：设置环境变量

```bash
export EVALBOT_TOKEN="your_token_here"
```

### 方法3：命令行参数传递

```bash
python3 evalbot_skill.py --token "your_token_here" data-generation --generate-type hot_topic
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

## 支持的评估类型

- `knowledge-instruction_following`: 指令遵循评估
- `knowledge-scalable-comprehensive_key_points`: 综合要点评估
- `knowledge-authentic_and_accurate-general`: 真实准确性评估
- `knowledge-richness`: 丰富度评估
- `knowledge-gsb-compare`: GSB 对比评估

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
