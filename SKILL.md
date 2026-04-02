---
name: ai-content-studio
description: |
  AI Content Studio — 专业级 AI 音频内容创作工具。
  Use this skill whenever working in or with the ai-content-studio project: generating podcasts/TTS audio, running the orchestrator, fixing TTS bugs, extending engines, adding new voices, configuring role libraries, running tests, or reading the project's architecture. Make sure to invoke this skill for any task involving MiniMax T2A V2, Qwen TTS, Qwen Omni, voice synthesis, role configuration, or the audio studio workflow — even if the user doesn't explicitly name the project.
---

# AI Content Studio Skill

专业级 AI 音频内容创作工具。三引擎编排（MiniMax → Qwen TTS → Qwen Omni），通过 LLM 编排播客脚本 + 高保真语音合成，生成广播级立体声音频。

## 架构总览

```
studio_orchestrator.py     # 推荐入口，三引擎编排 + 自动 Fallback
       │
       ├── content_studio.py        # MiniMax LLM 脚本生成
       ├── minimax_tts_tool.py      # MiniMax T2A V2 TTS
       │
       ├── qwen_tts_studio.py       # Qwen LLM 脚本生成
       ├── qwen_tts_tool.py         # Qwen qwen3-tts-flash TTS
       │
       └── qwen_omni_studio.py      # Qwen Omni 全模态单次调用
           qwen_omni_tts_tool.py    # Qwen qwen3-omni-flash TTS

audio_utils.py             # 共享工具（FFmpeg 混音、正则解析、VoicePool）
config_utils.py            # 统一配置加载（opencode.json）
```

**Fallback 链路**: `MiniMax → Qwen TTS → Qwen Omni`（全部失败才报错）

---

## 常用命令

### 一句话跑通
```bash
python studio_orchestrator.py --source "源文本.txt" --stereo -o out.mp3
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
python studio_orchestrator.py --source "文本" --engine minimax    # 仅 MiniMax
python studio_orchestrator.py --source "文本" --engine qwen_tts   # 仅 Qwen TTS（49音色）
python studio_orchestrator.py --source "文本" --engine qwen       # 仅 Qwen Omni
python studio_orchestrator.py --source "文本" --engine auto       # 自动 Fallback（默认）
```

### 引擎状态检查
```bash
python studio_orchestrator.py --check
```

### 立体声 + 背景音乐
```bash
python studio_orchestrator.py --source "文本.txt" --stereo --bgm ambient.mp3 -o out.mp3
```

### 独立 TTS 工具（绕过 LLM，直接合成已有脚本）
```bash
# MiniMax（多角色对话文件）
python minimax_tts_tool.py -s dialogue.txt -r configs/studio_roles.json --stereo -o multi.mp3

# Qwen TTS Studio
python qwen_tts_studio.py --source "文本.txt" -r configs/qwen_voices.json -o out.mp3

# Qwen Omni（单文本）
python qwen_omni_tts_tool.py "待合成文本" -o output.wav -v cherry
```

### 运行测试
```bash
cd tests && python test_minimax_tts.py
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

- `role` 必须在角色库（`configs/studio_roles.json` / `configs/qwen_voices.json`）中定义
- `emotion` 可选，默认 `neutral`；MiniMax 支持：`happy`, `calm`, `angry`, `sad`
- 角色切换自动插入 0.2s 停顿（`--pause` 可调）

---

## 配置文件速查

| 文件 | 引擎 | 用途 |
|------|------|------|
| `configs/studio_roles.json` | MiniMax | 推荐工作角色库（36 角色，6 大场景） |
| `configs/roles.json` | MiniMax | 轻量角色库（3 角色，快速测试） |
| `configs/minimax_voices.json` | MiniMax | 音色参考文档 + 参数指南（纯查阅） |
| `configs/qwen_voices.json` | Qwen TTS | Qwen 角色库（24 角色 + 29 音色轮询池） |

详见 `configs/README.md`。

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

## 关键代码模式

### 共享工具（所有引擎通用）
```python
from audio_utils import (
    parse_dialogue_segments_from_text,  # 正则解析对话文本
    merge_audio_files,                     # FFmpeg 混音引擎
    compute_role_pan_values,               # 立体声声道分配
    VoicePool,                             # 音色轮询分配器
    split_text,                            # 智能文本切分
    stream_qwen_omni_events,               # SSE 流解析
    make_wav_header,                       # PCM WAV header 构造
)

# 解析对话脚本
segments = parse_dialogue_segments_from_text(script_text)

# 立体声声道分配（等距 [-0.8, +0.8]）
pan_map = compute_role_pan_values(list(dict.fromkeys(s["role"] for s in segments)))

# 音色池（轮询 + 显式分配）
pool = VoicePool(voices=["cherry", "ethan", "chelsie"])
for role_label, voice in explicit_voice_map.items():
    pool.assign(role_label, voice)
voice = pool.get("role_name")
```

### SHA256 缓存模式（TTS 片段缓存）
```python
import hashlib
def segment_cache_key(voice, text, params):
    h = hashlib.sha256()
    h.update(f"{voice}:{text}:{params}".encode())
    return h.hexdigest()[:16]
# 缓存文件命名：seg_<16位hash>.mp3
```

### MiniMax T2A V2 API 端点
- LLM: `/v1/messages`（Anthropic 兼容）
- TTS: `/v1/t2a_v2`

### Qwen API 端点
- Qwen TTS: `/api/v1/services/aigc/multimodal-generation/generation`
- Qwen Omni: `/chat/completions`（流式 SSE）

---

## 扩展项目

### 新增音色/角色
1. 在 `configs/studio_roles.json`（MiniMax）或 `configs/qwen_voices.json`（Qwen TTS）中添加条目
2. 角色名须与脚本中 `[role]` 标签完全匹配
3. 运行 `python studio_orchestrator.py --check` 验证

### 新增 TTS 引擎
1. 在 `studio_orchestrator.py` 中添加 `EnginePriority` 枚举值
2. 实现对应的 `run_<engine>_studio()` 函数
3. 在 `check_engines()` 中添加可用性检测
4. 在 `EnginePriority.AUTO` 的 Fallback 链路中注册

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

## 文件索引

| 文件 | 用途 |
|------|------|
| `studio_orchestrator.py` | 推荐入口，编排 + Fallback |
| `audio_utils.py` | 共享音频工具（解析/混音/VoicePool） |
| `config_utils.py` | opencode.json 配置加载 |
| `content_studio.py` | MiniMax LLM 脚本生成 |
| `minimax_tts_tool.py` | MiniMax TTS 引擎 |
| `qwen_tts_studio.py` | Qwen TTS Studio |
| `qwen_tts_tool.py` | Qwen TTS 工具 |
| `qwen_omni_studio.py` | Qwen Omni Studio |
| `qwen_omni_tts_tool.py` | Qwen Omni TTS 工具 |
| `configs/README.md` | 配置文件详细说明 |
| `USER_MANUAL.md` | 终端用户使用指南 |
| `README.md` | 项目级说明文档 |
