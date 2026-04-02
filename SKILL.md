---
name: ai-content-studio
description: |
  AI Content Studio — 专业级 AI 音频内容创作工具。
  **当你听到用户说"帮我把 X 做成播客"、"生成一段 TTS 音频"、"把文章转成语音"、"做一个辩论节目"、"写一个播客脚本"时，立即激活本 skill。**
  触发词：播客生成、TTS 音频合成、多角色对话、语音合成、辩论播客、文本转音频、内容转语音、文章转播客

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

# AI Content Studio Skill

专业级 AI 音频内容创作工具。三引擎编排（MiniMax → Qwen TTS → Qwen Omni），通过 LLM 编排播客脚本 + 高保真语音合成，生成广播级立体声音频。

**Fallback 链路**: `MiniMax → Qwen TTS → Qwen Omni`（全部失败才报错）

---

## 场景化交互引导

当用户请求将文本内容转换为播客音频时，按以下流程引导：

### 步骤 1：确认场景

先问用户想要哪种风格（如果用户已明确说明，可跳过）：

| 用户意图 | 推荐模式 | 说明 |
|---------|---------|------|
| "做一个播客/对话" | `--mode deep_dive` | 两人/多人深度对谈，有提问、有反驳 |
| "快速摘要/播报一下" | `--mode summary` | 单人专业播报，清晰简洁 |
| "专家评论/点评一下" | `--mode review` | 含优缺点的专家评析 |
| "辩论/正反方对辩" | `--mode debate` | 正反方对辩，有主持人引导 |

**默认选择**：用户未指定时，使用 `--mode deep_dive`

### 步骤 2：生成命令

根据用户选择的场景生成命令：

```bash
# 基础命令结构
cd scripts/studio
python studio_orchestrator.py \
  --source "你的内容.txt" \
  --mode <选择的模式> \
  -o output.mp3
```

### 步骤 3：增强选项（可选）

根据需要添加：

| 选项 | 用法 | 示例 |
|------|------|------|
| `--stereo` | 立体声（不同角色左右声道） | 几乎所有场景都建议开启 |
| `--bgm music.mp3` | 添加背景音乐 | 选择轻柔纯音乐，人声时自动降低音量 |
| `--engine <engine>` | 指定引擎 | `minimax`（推荐）/ `qwen_tts` / `qwen` |
| `--roles <config>` | 自定义角色音色 | 参考 `references/configs_guide.md` |

### 步骤 4：典型命令示例

```bash
# 深度播客（最常用）
python studio_orchestrator.py \
  --source "文章.txt" \
  --mode deep_dive \
  --stereo \
  --bgm ambient.mp3 \
  -o "播客.mp3"

# 快速摘要
python studio_orchestrator.py \
  --source "报告.txt" \
  --mode summary \
  -o "摘要.mp3"

# 辩论节目
python studio_orchestrator.py \
  --source "争议话题.txt" \
  --mode debate \
  --stereo \
  -o "辩论.mp3"
```

---

## 常用命令速查

### 一句话跑通
```bash
cd scripts/studio && python studio_orchestrator.py --source "源文本.txt" --stereo -o out.mp3
```

### 生成模式（`--mode`）
| 值 | 说明 | 输出格式 |
|----|------|---------|
| `deep_dive` | 广播级深度对谈，含认知冲突与突破 | `[Alex, curious]: ...` |
| `summary` | 专业简报，快速概要 | `[Narrator, neutral]: ...` |
| `review` | 建设性专家评论，含优缺点 | `[Expert, calm]: ...` |
| `debate` | 正反方辩论，主持人引导 | `[Proponent]: ... [Opponent]: ...` |

### 指定引擎
```bash
cd scripts/studio
python studio_orchestrator.py --source "文本" --engine minimax    # 仅 MiniMax
python studio_orchestrator.py --source "文本" --engine qwen_tts   # 仅 Qwen TTS（49音色）
python studio_orchestrator.py --source "文本" --engine qwen       # 仅 Qwen Omni
python studio_orchestrator.py --source "文本" --engine auto       # 自动 Fallback（默认）
```

### 引擎状态检查
```bash
cd scripts/studio && python studio_orchestrator.py --check
```

### 立体声 + 背景音乐
```bash
python studio_orchestrator.py --source "文本.txt" --stereo --bgm ambient.mp3 -o out.mp3
```

### 独立 TTS 工具（绕过 LLM，直接合成已有脚本）
```bash
cd scripts/studio

# MiniMax（多角色对话文件）
python minimax_tts_tool.py -s dialogue.txt -r ../../references/configs/studio_roles.json --stereo -o out.mp3

# Qwen TTS Studio
python qwen_tts_studio.py --source "文本.txt" -r ../../references/configs/qwen_voices.json -o out.mp3

# Qwen Omni（单文本）
python qwen_omni_tts_tool.py "待合成文本" -o output.wav -v cherry
```

### 运行测试
```bash
python tests/test_minimax_tts.py
python tests/test_qwen_omni_tts.py
```

---

## 对话脚本格式

文件格式（`[role, emotion]: text`）：
```txt
[Alex, curious]: 这项技术的核心原理是什么？
[Sam, skeptical]: 我认为这个方向还很不成熟。
[Alex, excited]: 但最新实验数据显示...
```

- `role` 必须在角色库（`references/configs/studio_roles.json` / `references/configs/qwen_voices.json`）中定义
- `emotion` 可选，默认 `neutral`；MiniMax 支持：`happy`, `calm`, `angry`, `sad`
- 角色切换自动插入 0.2s 停顿（`--pause` 可调）

---

## 参考文档

| 文档 | 用途 |
|------|------|
| `references/user_manual.md` | **面向终端用户的完整场景引导**（四大场景详解、角色定制、FAQ） |
| `references/configs_guide.md` | 角色库配置详解（36+ 音色、自定义角色、高级参数） |
| `references/troubleshooting.md` | 故障排查（错误码、API 问题、FFmpeg） |
| `references/configs/` | 预置角色库 JSON 文件 |

---

## API 配置

从 `~/.config/opencode/opencode.json` 自动读取：
- `provider.bailian` → Qwen（DASHSCOPE_API_KEY + baseURL）
- `provider.minimax` → MiniMax（MINIMAX_API_KEY）

环境变量覆盖：
```bash
export DASHSCOPE_API_KEY="..."
export MINIMAX_API_KEY="..."
export MINIMAX_LLM_API_URL="..."   # MiniMax LLM API URL（可选）
export MINIMAX_TTS_API_URL="..."   # MiniMax TTS API URL（可选）
```

---

## 故障排查

**Rich 标签错误**：`MarkupError` 通常来自 subprocess 传递的路径字符串中包含未转义的 `[]` 字符。确保 `[` 不被 rich 解析为标签。

**FFmpeg 不可用**：`ffmpeg` 和 `ffprobe` 是系统级依赖，必须安装：
```bash
brew install ffmpeg   # macOS
sudo apt install ffmpeg  # Linux
```

**TTS 返回错误码**：`1001`/`1013`/`1021` = 业务限流（tenacity 自动重试 3 次）；其他非零码触发 Fallback。

**Qwen Omni 生成多余文本**：Omni 是全模态模型，可能在音频之外附带文本元数据。后处理时需过滤非音频字段。

---

## 安装 Skill

```bash
bash scripts/install.sh        # 安装到 ~/.claude/skills/ai-content-studio/
bash scripts/install.sh --uninstall  # 卸载
```

详见 `INSTALL.md`。
