# AI Content Studio — 多 Agent 兼容安装增强设计

**日期**：2026-04-02
**状态**：已批准
**目标**：完善 `install.sh` 和 `INSTALL.md`，支持 Claude Code、OpenCode、OpenClaw 等多种 AI Agent

---

## 1. 背景与目标

当前的 `install.sh` 仅支持 Claude Code (`~/.claude/skills/`) 和通用标准 (`~/.agents/skills/`)。调研发现：

- **OpenCode**：使用 `~/.config/opencode/skills/` 作为 skill 路径
- **OpenClaw**：使用 `~/.openclaw/skills/`，并支持 `metadata.openclaw` 元数据格式（依赖声明、安装器）
- **Claude Code**：通过符号链接兼容
- **通用标准**：Codex、Cursor、Cline 等原生支持 `~/.agents/skills/`

**目标**：一次安装，覆盖所有主流 Agent。

---

## 2. 安装路径矩阵

| Agent | 主路径 | 符号链接 | 备注 |
|-------|--------|---------|------|
| 通用标准 | `~/.agents/skills/ai-content-studio/` | — | Codex、Cursor、Cline 原生支持 |
| Claude Code | `~/.claude/skills/ai-content-studio` | → 主路径 | 兼容性符号链接 |
| OpenCode | `~/.config/opencode/skills/ai-content-studio` | → 主路径 | 兼容性符号链接 |
| OpenClaw | `~/.openclaw/skills/ai-content-studio` | → 主路径 | 兼容性符号链接 + metadata |

**安装优先级**：`~/.agents/skills/` 作为主路径，其他 Agent 通过符号链接指向它。

---

## 3. install.sh 增强设计

### 3.1 参数接口

```bash
bash scripts/install.sh [OPTIONS]

OPTIONS:
  --uninstall              卸载 skill
  --agent <name>           安装到指定 Agent（默认: all）
                           可选值: all, claude-code, opencode, openclaw
  --help                   显示帮助
```

### 3.2 Agent 路径变量

```bash
SKILL_NAME="ai-content-studio"
SKILL_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DEST_AGENTS="${HOME}/.agents/skills/${SKILL_NAME}"           # 主路径
LINK_CLAUDE="${HOME}/.claude/skills/${SKILL_NAME}"          # Claude Code
LINK_OPENCODE="${HOME}/.config/opencode/skills/${SKILL_NAME}" # OpenCode
LINK_OPENCLAW="${HOME}/.openclaw/skills/${SKILL_NAME}"       # OpenClaw
```

### 3.3 安装逻辑

```
1. 解析参数（--uninstall, --agent）
2. 检查目标目录是否存在 → 存在则备份到 .backup_<timestamp>/
3. 创建主目录 ~/.agents/skills/ai-content-studio/
4. 复制 skill bundle（SKILL.md, scripts/, references/, tests/）
5. 根据 --agent 参数创建符号链接：
   - all: 全部创建
   - claude-code: 仅 ~/.claude/skills/
   - opencode: 仅 ~/.config/opencode/skills/
   - openclaw: 仅 ~/.openclaw/skills/
6. 记录安装元数据（.installed 文件）
```

### 3.4 卸载逻辑

```
1. 删除各 Agent 路径的符号链接（如存在）
2. 删除主安装目录 ~/.agents/skills/ai-content-studio/
3. 清理备份（可选）
```

### 3.5 错误处理

| 场景 | 处理方式 |
|------|---------|
| 旧版目录（非符号链接） | 检测到 `~/.claude/skills/ai-content-studio/` 是目录而非链接时，先备份再替换为符号链接 |
| 符号链接已断开 | `rm -f` 安全删除，不报错 |
| 目标目录不存在 | `mkdir -p` 自动创建 |
| 脚本无执行权限 | 提示 `chmod +x scripts/install.sh` |

---

## 4. SKILL.md frontmatter 增强

### 4.1 完整 frontmatter

```yaml
---
name: ai-content-studio
description: |
  AI Content Studio — 专业级 AI 音频内容创作工具。
  Use this skill whenever working in or with the ai-content-studio project:
  generating podcasts/TTS audio, running the orchestrator, fixing TTS bugs,
  extending engines, adding new voices, configuring role libraries,
  running tests, or reading the project's architecture.
  触发词：播客生成、TTS 音频合成、多角色对话、语音合成、辩论播客

# OpenClaw 元数据
metadata:
  openclaw:
    version: "1.0"
    requires:
      bins:
        - ffmpeg
      env:
        - DASHSCOPE_API_KEY
        - MINIMAX_API_KEY
    install:
      - kind: brew
        formula: ffmpeg
        description: "音频处理引擎（macOS）"
---
```

### 4.2 字段说明

| 字段 | 用途 |
|------|------|
| `metadata.openclaw.version` | skill 版本号 |
| `metadata.openclaw.requires.bins` | 必需的系统二进制（ffmpeg） |
| `metadata.openclaw.requires.env` | 必需的环境变量 |
| `metadata.openclaw.install` | OpenClaw 内置安装器声明 |

---

## 5. INSTALL.md 重构设计

### 5.1 章节结构

```
1. 概述
   - 适用 Agent 列表
   - 兼容性矩阵表格

2. 快速安装
   - 通用命令（一行安装所有 Agent）
   - Agent 选择性安装命令

3. Agent 特定安装
   3.1 Claude Code
       - 符号链接路径
       - 激活验证
   3.2 OpenCode
       - skill add 命令
       - 激活验证
   3.3 OpenClaw
       - claw skill add 命令
       - ClawHub 集成说明
       - 激活验证
   3.4 其他 Agent（Codex、Cursor、Cline）
       - 使用通用路径 ~/.agents/skills/

4. 手动安装（无脚本环境）
   - 逐 Agent 安装命令

5. 卸载
   - 通用卸载命令
   - Agent 选择性卸载

6. 故障排查
   - 激活失败检查清单
   - 路径验证命令

7. 依赖
   - 系统依赖（ffmpeg）
   - Python 依赖（requirements.txt）
   - API Key 配置
```

### 5.2 核心原则

- **AI 可读优先**：每个步骤用清晰的注释标注，Agent 能逐行执行
- **无绝对路径**：所有路径使用 `$HOME`、`~` 或相对于 `SKILL_SOURCE` 的路径
- **幂等性**：安装脚本可重复执行，不报错的
- **可回滚**：每次安装前备份旧版本

---

## 6. 实现清单

| # | 任务 | 文件 |
|---|------|------|
| 1 | 增强 `install.sh`：添加 OpenCode/OpenClaw 路径、--agent 参数、严格模式 | `scripts/install.sh` |
| 2 | 更新 `SKILL.md` frontmatter：添加 OpenClaw metadata | `SKILL.md` |
| 3 | 重写 `INSTALL.md`：按 Agent 章节重构、多路径说明 | `INSTALL.md` |
| 4 | 添加 `tests/test_install.sh`：安装脚本集成测试 | `tests/test_install.sh` |

---

## 7. 验收标准

1. `bash scripts/install.sh` 安装后，4 个路径均可访问 skill
2. `bash scripts/install.sh --agent claude-code` 仅创建 Claude Code 链接
3. `bash scripts/install.sh --uninstall` 完全卸载包括备份
4. OpenCode 能识别 skill（`~/.config/opencode/skills/ai-content-studio/SKILL.md`）
5. OpenClaw 能读取 `metadata.openclaw.requires` 并提示依赖
6. 重复安装不报错，自动备份旧版本
7. 安装脚本使用 `set -euo pipefail` 严格模式
