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
assert_contains "$CONFIG_MENU_SH" "OpenClaw Control Center"
assert_contains "$README_MD" "openclaw-auto-deploy"

echo "branding_smoke: ok"
