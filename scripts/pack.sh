#!/usr/bin/env bash
# 将本项目打包成 zip，用于火山 Skillshub 上架提交。
# 自动排除 .env、.git、__pycache__、dist/、已有 zip 包等敏感与无用文件。
#
# 默认会先跑一遍 pytest 单测，全过才打包；可用 SKIP_TESTS=1 跳过。

set -euo pipefail

# 切换到仓库根目录（脚本位于 scripts/ 下）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

# 从 SKILL.md 解析 name 与 version
NAME="$(awk -F': *' '/^name:/ {print $2; exit}' SKILL.md | tr -d '"' | tr -d "'")"
VERSION="$(awk -F': *' '/^[[:space:]]*version:/ {print $2; exit}' SKILL.md | tr -d '"' | tr -d "'")"
NAME="${NAME:-skill-evalbot}"
VERSION="${VERSION:-0.0.0}"

# 打包前自检：跑单测（可通过 SKIP_TESTS=1 跳过，例如 CI 已单独跑过）
if [[ "${SKIP_TESTS:-0}" != "1" ]]; then
  if [[ -d tests ]]; then
    PYTHON_BIN="${PYTHON:-python3}"
    if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
      echo "[pack] 未找到 ${PYTHON_BIN}，无法跑测试。设置 SKIP_TESTS=1 可跳过。" >&2
      exit 1
    fi
    if ! "${PYTHON_BIN}" -m pytest --version >/dev/null 2>&1; then
      echo "[pack] 未安装 pytest，请先 pip install pytest。设置 SKIP_TESTS=1 可跳过。" >&2
      exit 1
    fi
    echo "[pack] 运行单测 (SKIP_TESTS=1 可跳过)"
    "${PYTHON_BIN}" -m pytest tests/ -q
  fi
fi

OUT_DIR="${ROOT_DIR}/dist"
OUT_FILE="${OUT_DIR}/${NAME}-${VERSION}.zip"

mkdir -p "${OUT_DIR}"
rm -f "${OUT_FILE}"

# 安全检查：禁止把 .env 打进包里
if [[ -f ".env" ]]; then
  echo "[pack] 检测到 .env 文件，已自动从打包中排除（请勿提交真实 token）"
fi

echo "[pack] 打包 ${NAME} v${VERSION} -> ${OUT_FILE}"

zip -r "${OUT_FILE}" . \
  -x "*.git*" \
  -x ".env" \
  -x "*.env" \
  -x "__pycache__/*" \
  -x "*/__pycache__/*" \
  -x "*.pyc" \
  -x "*.pyo" \
  -x "dist/*" \
  -x "*.zip" \
  -x ".DS_Store" \
  -x "*/.DS_Store" \
  -x "venv/*" \
  -x ".venv/*" \
  -x ".venv-test/*" \
  -x "env/*" \
  -x "tests/*" \
  -x ".pytest_cache/*" \
  -x ".idea/*" \
  -x ".vscode/*" \
  -x "node_modules/*" \
  -x "scripts/pack.sh"

# 一致性自检：zip 文件名应与 SKILL.md 中的 name+version 严格一致
EXPECTED_BASENAME="${NAME}-${VERSION}.zip"
ACTUAL_BASENAME="$(basename "${OUT_FILE}")"
if [[ "${EXPECTED_BASENAME}" != "${ACTUAL_BASENAME}" ]]; then
  echo "[pack] 一致性校验失败：期望 ${EXPECTED_BASENAME}，实际 ${ACTUAL_BASENAME}" >&2
  exit 1
fi

echo "[pack] 完成：${OUT_FILE}"
echo "[pack] 包内文件清单："
unzip -l "${OUT_FILE}"

