#!/usr/bin/env python3

from __future__ import annotations

import os
import pty
import select
import signal
import subprocess
import time
import unicodedata
from dataclasses import dataclass, field, replace
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT_DIR = Path(__file__).resolve().parent.parent
PHOTO_DIR = ROOT_DIR / "photo"
CONFIG_SCRIPT_PATH = ROOT_DIR / "config-menu.sh"
INSTALL_SCRIPT_PATH = ROOT_DIR / "install.sh"

SCREENSHOTS = {
    "install": {
        "script": "install",
        "inputs": [],
        "title": "Installer Welcome",
        "subtitle": "OpenClaw Auto Deploy first-run experience",
    },
    "menu": {
        "script": "config",
        "inputs": [],
        "title": "Main Menu",
        "subtitle": "OpenClaw Control Center",
    },
    "status": {
        "script": "config",
        "inputs": ["1\n"],
        "title": "System Status",
        "subtitle": "Install / gateway / config health overview",
    },
    "llm": {
        "script": "config",
        "inputs": ["2\n"],
        "title": "Model Setup",
        "subtitle": "AI provider selection",
    },
    "anthropic": {
        "script": "config",
        "inputs": ["2\n", "1\n"],
        "title": "Anthropic Setup",
        "subtitle": "Provider-specific configuration page",
    },
    "social": {
        "script": "config",
        "inputs": ["3\n"],
        "title": "Channel Setup",
        "subtitle": "Telegram / Discord / Slack / Feishu",
    },
    "telegram": {
        "script": "config",
        "inputs": ["3\n", "1\n"],
        "title": "Telegram Setup",
        "subtitle": "Pairing flow and bot configuration",
    },
    "identity": {
        "script": "config",
        "inputs": ["4\n"],
        "title": "Identity Setup",
        "subtitle": "Assistant name, user name, timezone",
    },
    "security": {
        "script": "config",
        "inputs": ["5\n"],
        "title": "Security Setup",
        "subtitle": "Capability boundary and whitelist options",
    },
    "service": {
        "script": "config",
        "inputs": ["6\n"],
        "title": "Service Console",
        "subtitle": "Gateway lifecycle and watchdog control",
    },
    "messages": {
        "script": "config",
        "inputs": ["7\n"],
        "title": "Quick Test",
        "subtitle": "API / channel / health checks",
    },
    "advanced": {
        "script": "config",
        "inputs": ["8\n"],
        "title": "Advanced Settings",
        "subtitle": "Backup, restore, reset, upgrade, uninstall",
    },
    "config": {
        "script": "config",
        "inputs": ["9\n"],
        "title": "Current Config",
        "subtitle": "Environment variables and OpenClaw config view",
    },
}

ROWS = 34
COLS = 78
PUMP_SECONDS = 0.7

DEFAULT_FG = (232, 240, 255)
DEFAULT_BG = (10, 18, 33)

FG_COLORS = {
    30: (34, 39, 46),
    31: (248, 113, 113),
    32: (74, 222, 128),
    33: (250, 204, 21),
    34: (96, 165, 250),
    35: (216, 180, 254),
    36: (103, 232, 249),
    37: (248, 250, 252),
    90: (148, 163, 184),
    91: (252, 165, 165),
    92: (134, 239, 172),
    93: (253, 224, 71),
    94: (147, 197, 253),
    95: (233, 213, 255),
    96: (165, 243, 252),
    97: (255, 255, 255),
}

BG_COLORS = {
    40: (34, 39, 46),
    41: (127, 29, 29),
    42: (20, 83, 45),
    43: (113, 63, 18),
    44: (30, 64, 175),
    45: (88, 28, 135),
    46: (22, 78, 99),
    47: (203, 213, 225),
    100: (71, 85, 105),
    101: (185, 28, 28),
    102: (22, 101, 52),
    103: (161, 98, 7),
    104: (37, 99, 235),
    105: (126, 34, 206),
    106: (14, 116, 144),
    107: (248, 250, 252),
}


@dataclass
class Style:
    fg: tuple[int, int, int] = DEFAULT_FG
    bg: tuple[int, int, int] | None = None
    bold: bool = False


@dataclass
class Cell:
    char: str = " "
    style: Style = field(default_factory=Style)


class TerminalBuffer:
    def __init__(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.reset()

    def reset(self) -> None:
        self.cursor_x = 0
        self.cursor_y = 0
        self.style = Style()
        self.grid = [[Cell(" ", Style()) for _ in range(self.cols)] for _ in range(self.rows)]
        self.state = "normal"
        self.csi = ""
        self.osc = ""
        self.osc_escape = False

    def newline(self) -> None:
        self.cursor_x = 0
        self.cursor_y += 1
        if self.cursor_y >= self.rows:
            self.grid.pop(0)
            self.grid.append([Cell(" ", Style()) for _ in range(self.cols)])
            self.cursor_y = self.rows - 1

    def put_char(self, char: str) -> None:
        width = 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
        if width == 2 and self.cursor_x == self.cols - 1:
            self.newline()

        if self.cursor_y >= self.rows:
            self.newline()

        self.grid[self.cursor_y][self.cursor_x] = Cell(char, replace(self.style))
        if width == 2 and self.cursor_x + 1 < self.cols:
            self.grid[self.cursor_y][self.cursor_x + 1] = Cell("", replace(self.style))

        self.cursor_x += width
        if self.cursor_x >= self.cols:
            self.newline()

    def clear_screen(self) -> None:
        self.grid = [[Cell(" ", Style()) for _ in range(self.cols)] for _ in range(self.rows)]
        self.cursor_x = 0
        self.cursor_y = 0

    def clear_line(self) -> None:
        for i in range(self.cursor_x, self.cols):
            self.grid[self.cursor_y][i] = Cell(" ", Style())

    def handle_csi(self, final: str, payload: str) -> None:
        clean = payload.lstrip("?")
        parts = [int(part) if part else 0 for part in clean.split(";")] if clean else []

        if final in {"H", "f"}:
            row = parts[0] - 1 if len(parts) >= 1 and parts[0] else 0
            col = parts[1] - 1 if len(parts) >= 2 and parts[1] else 0
            self.cursor_y = max(0, min(self.rows - 1, row))
            self.cursor_x = max(0, min(self.cols - 1, col))
        elif final == "J":
            mode = parts[0] if parts else 0
            if mode in {2, 3}:
                self.clear_screen()
        elif final == "K":
            self.clear_line()
        elif final == "m":
            if not parts:
                parts = [0]
            for code in parts:
                if code == 0:
                    self.style = Style()
                elif code == 1:
                    self.style.bold = True
                elif code == 22:
                    self.style.bold = False
                elif code == 39:
                    self.style.fg = DEFAULT_FG
                elif code == 49:
                    self.style.bg = None
                elif code in FG_COLORS:
                    self.style.fg = FG_COLORS[code]
                elif code in BG_COLORS:
                    self.style.bg = BG_COLORS[code]

    def feed(self, data: bytes) -> None:
        text = data.decode("utf-8", errors="ignore")
        for char in text:
            if self.state == "normal":
                if char == "\x1b":
                    self.state = "escape"
                elif char == "\n":
                    self.newline()
                elif char == "\r":
                    self.cursor_x = 0
                elif char == "\b":
                    self.cursor_x = max(0, self.cursor_x - 1)
                elif char >= " ":
                    self.put_char(char)
            elif self.state == "escape":
                if char == "[":
                    self.state = "csi"
                    self.csi = ""
                elif char == "]":
                    self.state = "osc"
                    self.osc = ""
                    self.osc_escape = False
                else:
                    self.state = "normal"
            elif self.state == "csi":
                if "@":  # keep parser branch explicit
                    if char.isalpha() or char in {"@", "`"}:
                        self.handle_csi(char, self.csi)
                        self.state = "normal"
                    else:
                        self.csi += char
            elif self.state == "osc":
                if char == "\a":
                    self.state = "normal"
                elif char == "\x1b":
                    self.osc_escape = True
                elif self.osc_escape and char == "\\":
                    self.state = "normal"
                    self.osc_escape = False
                else:
                    self.osc_escape = False


def load_font(path_candidates: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in path_candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def choose_fonts() -> tuple[
    ImageFont.FreeTypeFont | ImageFont.ImageFont,
    ImageFont.FreeTypeFont | ImageFont.ImageFont,
]:
    mono_font = load_font(
        [
            "/System/Library/Fonts/SFNSMono.ttf",
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Courier.dfont",
        ],
        20,
    )
    cjk_font = load_font(
        [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
        ],
        22,
    )
    return mono_font, cjk_font


def is_emoji(char: str) -> bool:
    if not char:
        return False
    code = ord(char)
    return (
        0x1F300 <= code <= 0x1FAFF
        or 0x2600 <= code <= 0x27BF
        or 0xFE00 <= code <= 0xFE0F
    )


EMOJI_MAP = {
    "📊": "◫",
    "🤖": "◎",
    "📱": "◈",
    "👤": "◉",
    "🔒": "◆",
    "⚡": "✦",
    "🧪": "✶",
    "🔧": "▣",
    "📋": "▤",
    "🚪": "↩",
    "🎨": "✦",
    "🔗": "↗",
    "📍": "⌂",
    "🗺": "◇",
    "✨": "✧",
    "⚠": "!",
    "📦": "▣",
    "📝": "✎",
    "🎛": "◌",
    "📖": "◫",
}


def substitute_char(char: str) -> str:
    return EMOJI_MAP.get(char, char)


def capture_buffer(script_kind: str, inputs: list[str]) -> TerminalBuffer:
    env = os.environ.copy()
    env.update(
        {
            "TERM": "xterm-256color",
            "COLUMNS": str(COLS),
            "LINES": str(ROWS),
            "LC_ALL": "en_US.UTF-8",
            "LANG": "en_US.UTF-8",
        }
    )

    master, slave = pty.openpty()
    script_path = CONFIG_SCRIPT_PATH if script_kind == "config" else INSTALL_SCRIPT_PATH
    process = subprocess.Popen(
        ["bash", str(script_path)],
        cwd=ROOT_DIR,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        env=env,
        preexec_fn=os.setsid,
    )
    os.close(slave)

    buffer = bytearray()

    def pump(seconds: float) -> None:
        deadline = time.time() + seconds
        while time.time() < deadline:
            ready, _, _ = select.select([master], [], [], 0.05)
            if master in ready:
                try:
                    chunk = os.read(master, 8192)
                except OSError:
                    break
                if not chunk:
                    break
                buffer.extend(chunk)

    try:
        pump(PUMP_SECONDS)
        for command in inputs:
            os.write(master, command.encode("utf-8"))
            pump(PUMP_SECONDS)
        pump(0.35)
    finally:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        process.wait(timeout=2)
        os.close(master)

    terminal = TerminalBuffer(ROWS, COLS)
    terminal.feed(bytes(buffer))
    return terminal


def last_content_row(buffer: TerminalBuffer) -> int:
    last = 0
    for idx, row in enumerate(buffer.grid):
        text = "".join(cell.char for cell in row if cell.char).strip()
        if text:
            last = idx
    return min(buffer.rows - 1, last + 1)


def draw_gradient_background(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    width, height = image.size
    top = (12, 20, 39)
    bottom = (8, 47, 73)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)


def render_buffer(name: str, terminal: TerminalBuffer, title: str, subtitle: str) -> None:
    mono_font, cjk_font = choose_fonts()
    char_width = 12
    line_height = 24
    padding_x = 54
    padding_y = 42
    top_bar = 68
    content_rows = min(terminal.rows, max(20, last_content_row(terminal) + 2))

    terminal_width = padding_x * 2 + COLS * char_width
    terminal_height = padding_y * 2 + top_bar + content_rows * line_height

    canvas = Image.new("RGBA", (terminal_width + 120, terminal_height + 120), (0, 0, 0, 0))
    draw_gradient_background(canvas)
    draw = ImageDraw.Draw(canvas)

    shadow_box = (42, 36, 42 + terminal_width, 36 + terminal_height)
    draw.rounded_rectangle(shadow_box, radius=30, fill=(3, 8, 20, 110))

    window_box = (36, 28, 36 + terminal_width, 28 + terminal_height)
    draw.rounded_rectangle(window_box, radius=28, fill=(7, 14, 28))

    bar_box = (36, 28, 36 + terminal_width, 28 + top_bar)
    draw.rounded_rectangle(bar_box, radius=28, fill=(14, 23, 42))
    draw.rectangle((36, 28 + 32, 36 + terminal_width, 28 + top_bar), fill=(14, 23, 42))

    for idx, color in enumerate([(251, 113, 133), (250, 204, 21), (74, 222, 128)]):
        cx = 68 + idx * 22
        cy = 62
        draw.ellipse((cx, cy, cx + 12, cy + 12), fill=color)

    title_font = load_font(
        [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/PingFang.ttc",
        ],
        21,
    )
    subtitle_font = load_font(
        [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/PingFang.ttc",
        ],
        15,
    )

    draw.text((122, 50), f"OpenClaw UI Capture · {title}", font=title_font, fill=(234, 241, 255))
    draw.text((122, 76), subtitle, font=subtitle_font, fill=(123, 141, 171))

    badge_text = name.upper()
    badge_width = 18 + len(badge_text) * 10
    draw.rounded_rectangle(
        (36 + terminal_width - badge_width - 24, 46, 36 + terminal_width - 24, 82),
        radius=18,
        fill=(30, 64, 175),
    )
    draw.text(
        (36 + terminal_width - badge_width - 6, 57),
        badge_text,
        font=subtitle_font,
        fill=(239, 246, 255),
    )

    origin_x = 36 + padding_x
    origin_y = 28 + top_bar + padding_y

    for row_index in range(content_rows):
        row = terminal.grid[row_index]
        for col_index, cell in enumerate(row):
            if cell.char in {"", " "}:
                continue
            x = origin_x + col_index * char_width
            y = origin_y + row_index * line_height

            if cell.style.bg:
                draw.rectangle(
                    (x - 1, y + 3, x + char_width * 1.9, y + line_height + 1),
                    fill=cell.style.bg,
                )

            display_char = substitute_char(cell.char)
            if unicodedata.east_asian_width(display_char) in {"W", "F"} or ord(display_char) > 127:
                font = cjk_font
            else:
                font = mono_font
            draw.text((x, y), display_char, font=font, fill=cell.style.fg)

    out_path = PHOTO_DIR / f"{name}.png"
    canvas.save(out_path)
    print(out_path)


def main() -> None:
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    for name, config in SCREENSHOTS.items():
        terminal = capture_buffer(config["script"], config["inputs"])
        render_buffer(name, terminal, config["title"], config["subtitle"])


if __name__ == "__main__":
    main()
