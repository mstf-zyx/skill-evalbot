# 版本变更日志

## v1.2.3 (2026-05-29)
- **指标精简**：下线 `knowledge-instruction_following`（知识类指令遵循评估，后端能力已下线），从 `EVALUATE_SPECS` 注册表、SKILL.md 类型一览与快速开始示例、`references/README.md` 详细参数文档中一并移除；知识类详细章节剩余指标连续重编号 1-5，整体编号 1-20，评估指标总数 21 → 20

## v1.2.2 (2026-05-28)
- **文档**：`references/README.md` 新增「获取 Evalbot Token」小节，含演示动图（`assets/get-token.gif`）与文字兜底步骤；`SKILL.md` 简化环境变量注释，引导到 README 查看 Token 获取方式

## v1.2.1 (2026-05-27)
- **评估能力对齐**：`evaluate_type` 改为直接透传给后端，与 SKILL.md / README 列出的名称完全一致；解决 `text-*`、`image-*`、`t2i/t2v/v2v/i2v-*` 等指标返回 `400 no id found for given id_key` 的问题
- **指标精简**：下线 `image_text-logicality`（图文逻辑性评估，后端 workflow `image_text_logicality` 已下线），从 `EVALUATE_SPECS` 注册表、SKILL.md 类型一览、`references/README.md` 详细参数文档中一并移除；评估指标总数 22 → 21
- **健壮性**：`AbilityTriggerRespData` / `PluginTriggerData` 反序列化容忍后端新增字段（新增 `_from_dict` 帮助函数自动丢弃未知键），避免后端字段扩展时客户端 `TypeError` 崩溃
- **可观测性**：HTTP 4xx/5xx 失败时在日志中打印响应体（前 500 字节），联调时无需另写脚本即可看到 `error_msg` 等关键信息
- **易用性**：
  - `EvalbotClient` 在 token 缺失时抛 `RuntimeError("缺少 EVALBOT_TOKEN…")`，CLI 捕获后退出码 2，避免发出无效的 401 请求
  - CLI 单独捕获 `ValueError`（必填参数缺失）并以退出码 3 返回，便于脚本编排区分错误类型
  - `EvaluateSpec` 新增 `defaults` 字段，多模态指标（`t2i-*` / `t2v-*` / `v2v-*` / `i2v-*`）的 `c_type` 由 schema 提供推荐默认值，调用方可不传；用户传入值优先生效
  - 新增 `apply_defaults(...)` API，`list-types` JSON 输出包含 `defaults` 字段（移除 `workflow` 字段）
- **文档**：修复 `references/README.md` 多模态章节序号错乱（原有重复的 #21 与缺失的 #18），现 17-21 连续编号
- **构建**：`scripts/pack.sh` 打包前自动跑 `pytest tests/`，全过才打包，并校验 zip 文件名与 SKILL.md 中 `name+version` 一致；可用 `SKIP_TESTS=1` 跳过
- **测试**：补充 12 个用例覆盖 `_from_dict` 容错、HTTP 错误体日志、token 缺失、`apply_defaults` 行为、`_wrap_params` JSON 序列化等关键路径，单测从 16 → 28

## v1.2.0 (2026-05-21)
- 评估能力扩展：从 5 个指标扩展到 22 个，覆盖文本类（`text-*` 7 个）、知识类（`knowledge-*` 6 个）、图像类（`image-*` 3 个）、图文混合类（`image_text-*` 1 个）和多模态生成类（`t2i-*` / `t2v-*` / `v2v-*` / `i2v-*` 5 个）
- 新增对外评估类型 → 后端 workflow 名的 alias 映射机制（`scripts/evalbot/schema.py` 中 `EVALUATE_SPECS` 单一注册表），新增/重命名指标只需改一处；老 5 个 `knowledge-*` 指标保持直传，向后兼容
- `validate_params` 在请求发出前完成必填字段校验，避免无效请求打到后端
- 新增单测 `tests/test_schema.py` / `tests/test_client.py`：覆盖 alias 映射、必填校验、SSE 帧解析（`_strip_prefix` 字符集语义、`plugin_trigger` 严格按 `id:` 前缀分帧）等关键回归点
- 整理 `.gitignore`：
  - 修复无效规则 `./scripts/pack.sh`（gitignore 不支持 `./` 前缀，且 `pack.sh` 是上架打包工具，本就该入库）
  - 新增 `*.env` + `!.env.example` 例外，避免误伤示例配置
  - 新增测试/静态检查产物：`.pytest_cache/`、`.coverage`、`htmlcov/`、`.tox/`、`.mypy_cache/`、`.ruff_cache/`
  - `tests/` 不入 `.gitignore`，由 `scripts/pack.sh` 在打包阶段排除以避免进入上架 zip

## v1.1.0 (2026-05-20)
- 适配火山引擎 Skillshub 上架规范：
  - `SKILL.md` 新增 `When to use this skill` 章节，`description` 改为带触发条件的描述
  - 修正快速开始示例参数（`response` → `reply`，补全 `location` / `scene`）
- 修复 `references/README.md` 中参数说明字段笔误（`question` → `query`），与代码实际字段保持一致
- 修复 `.env` 自动加载失败：`requirements.txt` 补上 `python-dotenv` 依赖（此前因缺包被静默忽略，导致只能通过 `--token` 显式传值）
- 跟进服务端 `/trigger` 接口优化：去掉对 `/evaluate/get_ids` 的前置调用；`/evaluate/plugin/trigger` 请求体新增 `generate_type` 字段，`/evaluate/ability/trigger` 请求体新增 `evaluate_type` 字段，由服务端按类型字符串直接路由
- 新增 `scripts/pack.sh` 一键打包脚本，自动排除 `.env`、`.git`、`__pycache__`、`venv/`、`dist/`、`scripts/pack.sh` 自身等敏感与无用文件，产出 `dist/<name>-<version>.zip` 用于上架提交
- `.gitignore` 增加 `dist/`、`*.zip`、`.DS_Store`、`venv/`、`.idea/`、`.vscode/` 等

## v1.0.0 (2026-03-25)
- 初始版本发布
- 支持数据生成功能（热点话题）
- 支持5种模型评估类型
- 完全符合AgentSkills开放标准
