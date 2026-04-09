# 🦞 OpenClaw Auto Deploy

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Auto%20Deploy-0ea5e9?style=for-the-badge" alt="OpenClaw Auto Deploy">
  <img src="https://img.shields.io/badge/Windows-WSL2-Linux-macOS-22c55e?style=for-the-badge" alt="Platforms">
  <img src="https://img.shields.io/badge/Node.js-22%2B-f59e0b?style=for-the-badge" alt="Node.js 22+">
  <img src="https://img.shields.io/badge/Focus-One%20Click%20Install-a855f7?style=for-the-badge" alt="One click install">
</p>

> 面向 OpenClaw 的跨平台一键安装与配置仓库。重点优化 Windows、WSL2、Linux、macOS 的落地体验，把安装、诊断、模型配置、渠道接入、服务管理和后续维护尽量收拢到一套清晰的脚本流程里。

<p align="center">
  <img src="photo/install.png" alt="OpenClaw installer welcome screen" width="860">
</p>

## 项目简介

`openclaw-auto-deploy` 不是 OpenClaw 本体，而是围绕 OpenClaw 的部署与配置体验做的一层自动化安装壳。

它的核心目标很直接：

- 尽量让第一次接触 OpenClaw 的用户也能安装成功。
- 重点解决 Windows 和 WSL2 这两个最容易踩坑的场景。
- 给 Linux 和 macOS 用户提供更顺手的命令行安装与控制中心体验。
- 把模型配置、渠道配置、服务控制、配置查看、快速测试整合成一套清晰菜单。
- 提供可复用的项目截图素材，方便在 README、个人网站、文章页里直接展示。

## 为什么这个仓库值得展示

- 不只是“给几条命令”，而是把引导流程做成了可理解、可维护的安装器。
- 脚本里已经考虑了一部分真实部署场景里的权限、缓存、端口、npm 和 Windows 兼容问题。
- `config-menu.sh` 已经不只是菜单，而是一个命令行控制中心。
- 仓库内自带截图生成器，后续 UI 变化后可以重新生成网站展示图，不需要手工重截。

## 平台支持矩阵

| 平台 | 支持情况 | 说明 |
| --- | --- | --- |
| Windows 10/11 | 强支持 | 优先考虑 Git Bash、PowerShell、WSL2 过渡体验 |
| WSL2 + Ubuntu | 强支持 | 推荐给第一次部署 OpenClaw 的 Windows 用户 |
| Linux | 强支持 | 已覆盖常见依赖、权限、端口、npm 问题 |
| macOS | 强支持 | 支持本地安装、配置管理与服务控制 |

## 快速开始

### 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/MarcusDog/openclaw-auto-deploy/main/install.sh | bash
```

### 本地运行

```bash
git clone https://github.com/MarcusDog/openclaw-auto-deploy.git
cd openclaw-auto-deploy
chmod +x install.sh config-menu.sh
./install.sh
```

## 仓库结构

### `install.sh`

首次安装入口，负责：

- 平台识别
- 依赖检查
- OpenClaw 安装
- 常见报错自动修复
- 配置向导和后续操作指引

### `config-menu.sh`

安装后的长期控制中心，负责：

- 模型配置
- 消息渠道配置
- 身份与个性配置
- 安全开关与白名单
- 服务管理
- 快速测试
- 配置查看、备份、恢复、重置

### `scripts/generate_ui_screenshots.py`

自动截图生成器。会直接运行脚本并渲染关键界面为 PNG，用于：

- README 展示
- 个人网站项目页
- 发布文章配图
- UI 版本更新后的素材重建

## 推荐工作流

### 第一次使用

1. 运行 `install.sh`
2. 跟着安装向导完成环境准备
3. 进入 `config-menu.sh`
4. 先配置模型
5. 再配置消息渠道
6. 最后执行“快速测试”

### 日常维护

1. 用 `config-menu.sh` 调整模型、渠道和服务
2. 有异常先看“系统状态”
3. 服务有问题先看“服务管理”
4. 配置不确定时查看“当前配置”
5. 需要排查时运行“快速测试”或 `openclaw doctor`

## 完整截图画廊

下面这组截图覆盖了这个项目最值得展示的主要部分，已经可以直接作为个人网站项目页素材使用。

### 1. 安装器欢迎页

适合放在网站 Hero 区，突出“一键安装、跨平台、自动修复”。

<p align="center">
  <img src="photo/install.png" alt="Installer" width="860">
</p>

### 2. 控制中心主菜单

展示项目的整体信息架构，说明这不是单一脚本，而是一个命令行控制中心。

<p align="center">
  <img src="photo/menu.png" alt="Main Menu" width="860">
</p>

### 3. 系统状态页

展示安装状态、服务状态、当前配置和目录结构，适合说明“可观测性”和“运维友好”。

<p align="center">
  <img src="photo/status.png" alt="System Status" width="860">
</p>

### 4. 模型总览页

展示 OpenClaw 可接入的主流模型、网关、本地模型和实验性入口。

<p align="center">
  <img src="photo/llm.png" alt="Model Overview" width="860">
</p>

### 5. Anthropic 详细配置页

展示“不是只有列表，而是对每个 Provider 都有具体配置页”的深度能力。

<p align="center">
  <img src="photo/anthropic.png" alt="Anthropic Setup" width="860">
</p>

### 6. 消息渠道总览页

展示 Telegram、Discord、Slack、微信、飞书等渠道接入能力。

<p align="center">
  <img src="photo/social.png" alt="Channel Overview" width="860">
</p>

### 7. Telegram 详细配置页

适合展示真实接入流程，包括 Token、User ID、Pairing 逻辑和操作指引。

<p align="center">
  <img src="photo/telegram.png" alt="Telegram Setup" width="860">
</p>

### 8. 身份与个性页

展示这个项目不是只关心安装，也考虑到了助手人格和最终体验。

<p align="center">
  <img src="photo/identity.png" alt="Identity Setup" width="860">
</p>

### 9. 安全设置页

展示文件访问、命令执行、网络访问和白名单等边界控制能力。

<p align="center">
  <img src="photo/security.png" alt="Security Setup" width="860">
</p>

### 10. 服务管理页

展示 Gateway 生命周期管理、日志、守护监控和卸载入口。

<p align="center">
  <img src="photo/service.png" alt="Service Management" width="860">
</p>

### 11. 快速测试页

展示配置后的最终验收能力，适合强调“装完能测，测完能定位问题”。

<p align="center">
  <img src="photo/messages.png" alt="Quick Test" width="860">
</p>

### 12. 高级设置页

展示备份、恢复、升级、重置、卸载等高级维护能力。

<p align="center">
  <img src="photo/advanced.png" alt="Advanced Settings" width="860">
</p>

### 13. 当前配置页

展示环境变量、模型状态、渠道列表和配置查看能力，适合网站上说明“可维护性”。

<p align="center">
  <img src="photo/config.png" alt="Current Config" width="860">
</p>

## 网站展示素材清单

如果你后续要在个人网站里展示这个项目，建议按下面这套方式使用：

| 素材 | 文件 | 推荐用途 |
| --- | --- | --- |
| 安装器首屏 | `photo/install.png` | 网站首屏、社交媒体封面、文章头图 |
| 控制中心主菜单 | `photo/menu.png` | 展示整体 IA 和产品全貌 |
| 系统状态 | `photo/status.png` | 展示可观测性和诊断能力 |
| 模型总览 | `photo/llm.png` | 展示模型支持范围 |
| Anthropic 详细配置 | `photo/anthropic.png` | 展示具体 Provider 配置深度 |
| 渠道总览 | `photo/social.png` | 展示多渠道接入能力 |
| Telegram 配置 | `photo/telegram.png` | 展示真实接入工作流 |
| 身份与个性 | `photo/identity.png` | 展示用户体验层设计 |
| 安全设置 | `photo/security.png` | 展示边界控制和安全意识 |
| 服务管理 | `photo/service.png` | 展示运维控制台能力 |
| 快速测试 | `photo/messages.png` | 展示测试与验收闭环 |
| 高级设置 | `photo/advanced.png` | 展示维护和恢复能力 |
| 当前配置 | `photo/config.png` | 展示透明度和可维护性 |

## 支持的能力

### 多模型接入

支持但不限于：

- Anthropic Claude
- OpenAI GPT
- DeepSeek
- Kimi / Moonshot
- Google Gemini
- OpenRouter
- Groq
- Mistral AI
- Ollama
- Azure OpenAI
- 自定义 Provider + 自定义模型

### 多渠道接入

支持但不限于：

- Telegram
- Discord
- WhatsApp
- Slack
- 微信
- iMessage
- 飞书

### 自动修复

脚本会尽量处理这些常见问题：

- npm 权限错误
- npm 网络超时
- npm 缓存损坏
- apt / dpkg 锁冲突
- 端口占用
- PowerShell 执行策略导致的脚本拦截
- Windows npm PATH 问题

## Windows / WSL2 说明

这个仓库特别适合以下人群：

- 想在 Windows 本机快速试跑 OpenClaw 的用户
- 不确定 PowerShell / Git Bash / WSL2 应该怎么配合的人
- 希望有更稳安装方式的 Windows 用户

推荐顺序是：

1. 先安装 Git Bash
2. 安装 Node.js 22+
3. 运行 `install.sh`
4. 如果不确定选择什么安装方式，优先选 `WSL2 + Ubuntu`

## 常用命令

### 打开控制中心

```bash
bash ./config-menu.sh
```

### 启动服务

```bash
openclaw gateway start
```

### 查看服务状态

```bash
openclaw gateway status
```

### 运行诊断

```bash
openclaw doctor
```

### 查看 Dashboard 地址

```bash
openclaw dashboard --no-open
```

### 重新生成展示截图

```bash
python3 scripts/generate_ui_screenshots.py
```

## 常见问题

### 安装时提示 Node.js 版本过低

本仓库默认要求 Node.js 22+。先升级 Node.js，再重新执行安装脚本。

### Windows 下 `npm.ps1` 被禁用

脚本已经尝试自动修复执行策略。如果仍然失败，建议以管理员身份打开 PowerShell 检查执行策略。

### 端口 18789 被占用

脚本和配置菜单都包含端口检测与部分自动释放逻辑。也可以手动确认占用该端口的进程。

### 模型能配置但消息发不出去

优先检查：

- Token 是否正确
- 机器人是否已加入对应服务器、频道或群组
- Pairing / Allowlist 是否完成
- Gateway 是否已经成功启动

## 仓库地址

- GitHub: [https://github.com/MarcusDog/openclaw-auto-deploy](https://github.com/MarcusDog/openclaw-auto-deploy)
- 安装脚本: [install.sh](https://raw.githubusercontent.com/MarcusDog/openclaw-auto-deploy/main/install.sh)
- 配置脚本: [config-menu.sh](https://raw.githubusercontent.com/MarcusDog/openclaw-auto-deploy/main/config-menu.sh)

## 与 OpenClaw 的关系

- 本仓库专注于安装、部署和配置体验。
- OpenClaw 的核心功能与官方产品文档，请以官方项目和官方文档为准。
- 这个仓库更像一个“适合真实部署与展示”的安装器和命令行控制中心。

## 维护建议

如果你计划长期把它作为自己的分发仓库，建议保持以下内容同步：

- `install.sh` 里的仓库链接与命令
- `config-menu.sh` 里的帮助提示与仓库地址
- `photo/*.png` 展示素材
- `README.md` 的命令、截图和说明

## License

MIT
