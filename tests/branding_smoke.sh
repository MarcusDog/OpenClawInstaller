#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

INSTALL_SH="$ROOT_DIR/install.sh"
CONFIG_MENU_SH="$ROOT_DIR/config-menu.sh"
README_MD="$ROOT_DIR/README.md"

TARGET_REPO="MarcusDog/openclaw-auto-deploy"
OLD_REPO="MarcusDog/OpenClawInstaller"

assert_contains() {
    local file="$1"
    local pattern="$2"
    if ! grep -Fq "$pattern" "$file"; then
        echo "Missing pattern in $file: $pattern" >&2
        return 1
    fi
}

assert_not_contains() {
    local file="$1"
    local pattern="$2"
    if grep -Fq "$pattern" "$file"; then
        echo "Unexpected legacy pattern in $file: $pattern" >&2
        return 1
    fi
}

assert_contains "$INSTALL_SH" "$TARGET_REPO"
assert_contains "$CONFIG_MENU_SH" "$TARGET_REPO"
assert_contains "$README_MD" "$TARGET_REPO"

assert_not_contains "$INSTALL_SH" "$OLD_REPO"
assert_not_contains "$CONFIG_MENU_SH" "$OLD_REPO"
assert_not_contains "$README_MD" "$OLD_REPO"

assert_contains "$INSTALL_SH" "OpenClaw Auto Deploy"
assert_contains "$INSTALL_SH" "安装旅程总览"
assert_contains "$INSTALL_SH" "体验亮点"
assert_contains "$CONFIG_MENU_SH" "OpenClaw Control Center"
assert_contains "$CONFIG_MENU_SH" "状态速览"
assert_contains "$CONFIG_MENU_SH" "核心配置"
assert_contains "$CONFIG_MENU_SH" "页面导航"
assert_contains "$CONFIG_MENU_SH" "输入区"
assert_contains "$CONFIG_MENU_SH" "操作提示"
assert_contains "$README_MD" "openclaw-auto-deploy"
assert_contains "$README_MD" "推荐工作流"
assert_contains "$README_MD" "平台支持矩阵"

echo "branding_smoke: ok"
