# 版本变更日志

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
