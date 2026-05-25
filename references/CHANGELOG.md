# 版本变更日志

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
