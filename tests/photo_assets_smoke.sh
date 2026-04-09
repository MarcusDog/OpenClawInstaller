#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

GENERATOR="$ROOT_DIR/scripts/generate_ui_screenshots.py"

[ -f "$GENERATOR" ] || {
    echo "Missing screenshot generator: $GENERATOR" >&2
    exit 1
}

for image in install menu status llm anthropic social telegram identity security service messages advanced config; do
    [ -f "$ROOT_DIR/photo/$image.png" ] || {
        echo "Missing screenshot asset: photo/$image.png" >&2
        exit 1
    }
done

python3 - <<'PY' "$ROOT_DIR"
from pathlib import Path
from PIL import Image
import sys

root = Path(sys.argv[1])
for name in ["install", "menu", "status", "llm", "anthropic", "social", "telegram", "identity", "security", "service", "messages", "advanced", "config"]:
    path = root / "photo" / f"{name}.png"
    image = Image.open(path)
    width, height = image.size
    if width < 1000 or height < 650:
        raise SystemExit(f"Image too small: {path} -> {width}x{height}")

print("photo_assets_smoke: ok")
PY
