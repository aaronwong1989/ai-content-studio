# Clean Architecture CLI 合并设计方案

**日期**: 2026-04-02
**状态**: 已批准
**目标**: 将旧 CLI 工具链合并到 Clean Architecture，实现统一入口

---

## 背景

项目存在两套并行的代码路径：
- **旧架构**：`src/cli/` 下的多个独立工具脚本（orchestrator、studio、tts_tool 等），通过 `src/core/` 和 `src/services/` 运行
- **新架构**：Clean Architecture（entities / use_cases / adapters / infrastructure），`src/infrastructure/cli.py` 仅有单文本合成功能

需要将旧工具链全部功能合并到新架构，消除重复，统一入口。

---

## CLI 界面设计

### 单一入口

```
ai-studio <子命令> [参数]
```

### 子命令列表

#### 1. `synthesize` — 单文本 TTS 合成

```bash
ai-studio synthesize --source TEXT_OR_FILE -o OUTPUT
  [--engine {minimax,qwen_tts,qwen_omni}]
  [--voice VOICE_ID]
  [--speed SPEED]        # 0.5-2.0, 默认 1.0
  [--emotion EMOTION]     # neutral/happy/sad/angry/calm/surprised/fearful/disgusted/fluent
  [--format {mp3,wav}]   # 默认 mp3
```

#### 2. `dialogue` — 对话脚本解析 + 多角色 TTS

```bash
ai-studio dialogue --source FILE -o OUTPUT
  [--engine {minimax,qwen_tts,qwen_omni}]
  [--roles ROLE_JSON_FILE]   # 角色音色映射文件
  [--bgm BGM_FILE]           # 可选背景音乐
```

**输入格式**（`--source` 文件内容）：
```
[Alex]: 你好，很高兴见到你
[Sam]: 我也很高兴，今天我们聊聊AI
[Alex]: 你觉得AI的未来如何？
[Sam]: 我觉得会改变一切
```

#### 3. `studio` — LLM 生成 + TTS 全流程

```bash
ai-studio studio --topic TEXT -o OUTPUT
  [--llm {minimax,qwen}]        # LLM 引擎（独立选择）
  [--tts {minimax,qwen_tts,qwen_omni}]  # TTS 引擎
  [--roles ROLE_JSON_FILE]
  [--bgm BGM_FILE]
```

#### 4. `batch` — 批量片段合成

```bash
ai-studio batch --segments "SEGMENT1|SEGMENT2|..." -o OUTPUT
  [--engine {minimax,qwen_tts,qwen_omni}]
```

---

## 架构设计

### 目录结构

```
src/
├── entities/                 # 不变，已有
│   ├── audio_segment.py
│   ├── engine_result.py
│   ├── enums.py
│   ├── tts_request.py
│   └── voice_config.py
│
├── use_cases/               # 扩展，新增 4 个用例
│   ├── synthesize_speech.py        # 单文本合成
│   ├── dialogue_speech.py          # 对话脚本解析 + 多角色 TTS
│   ├── studio_podcast.py           # LLM 生成 → TTS → 混音
│   └── batch_speech.py             # 批量合成
│
├── adapters/                # 扩展，新增 LLM adapters
│   ├── base_tts_engine.py          # 不变
│   ├── tts_adapters.py              # 已有，扩展
│   ├── audio_adapters.py             # 不变，已有 FFmpegAudioProcessor
│   └── llm_adapters.py              # 新增：MiniMaxLLMEngine、QwenLLMEngine
│
├── infrastructure/          # CLI 重写
│   ├── cli.py                      # 统一 CLI（4 个子命令）
│   ├── container.py                # DI 容器扩展
│   └── config_manager.py           # ConfigManager（向后兼容 opencode.json）
│
├── core/                    # 保留（过渡期被 adapters 引用）
├── services/               # 保留（被 adapters 引用）
└── cli/                    # 废弃，完成迁移后删除
```

### 新增 Use Cases

#### `SynthesizeSpeechUseCase`（拆分自 `tts_use_cases.py`）

```
输入：text, output_file, voice_config
处理：构建 TTSRequest → 调用 TTS 引擎
输出：EngineResult
```

#### `DialogueSpeechUseCase`（新增）

```
输入：dialogue_script(str), output_file, engine, roles, bgm
处理：
  1. parse_dialogue_segments() 解析脚本 → List[AudioSegment]
  2. 遍历 segments 调用 TTS 引擎
  3. FFmpeg 混音（支持立体声 + BGM）
输出：EngineResult
```

#### `StudioPodcastUseCase`（新增）

```
输入：topic, output_file, llm_engine, tts_engine, roles, bgm
处理：
  1. LLM 生成对话脚本
  2. 解析为 AudioSegment 列表
  3. 调用 TTS 引擎批量合成
  4. FFmpeg 混音
输出：EngineResult
```

#### `BatchSpeechUseCase`（拆分自 `tts_use_cases.py`）

```
输入：List[AudioSegment], output_file, merge
处理：批量 TTS 合成 → 可选合并
输出：EngineResult
```

### 新增 LLM Adapters

从 `src/core/llm_engines/` 迁移到 `src/adapters/llm_adapters.py`：

```python
class BaseLLMEngine(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str: ...

class MiniMaxLLMEngine(BaseLLMEngine): ...
class QwenLLMEngine(BaseLLMEngine): ...
```

### Container DI 扩展

```python
class Container:
    # 现有（重构）
    def synthesize_speech_use_case(self, engine: str) -> SynthesizeSpeechUseCase
    def batch_speech_use_case(self, engine: str) -> BatchSpeechUseCase

    # 新增
    def dialogue_speech_use_case(self, engine: str) -> DialogueSpeechUseCase
    def studio_podcast_use_case(self, llm: str, tts: str) -> StudioPodcastUseCase

    # LLM 引擎获取
    def get_llm_engine(self, engine: str) -> BaseLLMEngine
```

### API Key 配置

**加载顺序**（优先级从高到低）：
1. 环境变量：`MINIMAX_API_KEY`、`DASHSCOPE_API_KEY`、`MINIMAX_LLM_API_KEY`
2. `opencode.json`（`~/.config/opencode/opencode.json`）：向后兼容

**ConfigManager**（`infrastructure/config_manager.py`）封装此逻辑。

---

## 错误处理策略

| 场景 | 策略 |
|:-----|:-----|
| API Key 缺失 | 友好提示 + 退出码 1 |
| 网络请求失败 | tenacity 重试 3 次，指数退避 |
| TTS 引擎返回失败 | 记录日志，退出码 1 |
| 输入文件不存在 | 友好提示 + 退出码 2 |
| LLM 生成失败 | 降级到对话输入模式或退出 |

---

## 迁移与清理计划

### Phase 1：基础框架
- [ ] 创建 `src/adapters/llm_adapters.py`（迁移 LLM 引擎）
- [ ] 创建 `src/use_cases/dialogue_speech.py`
- [ ] 创建 `src/use_cases/studio_podcast.py`
- [ ] 扩展 `src/infrastructure/container.py`

### Phase 2：CLI 实现
- [ ] 重写 `src/infrastructure/cli.py`（4 个子命令）
- [ ] 实现 `src/infrastructure/config_manager.py`

### Phase 3：验证
- [ ] 所有 4 个子命令功能验证
- [ ] 确认 `src/cli/` 无外部引用
- [ ] 批量删除 `src/cli/` 目录

---

## 依赖关系图

```
cli.py (infrastructure)
  └── Container (infrastructure)
        ├── SynthesizeSpeechUseCase (use_cases)
        │     └── TTSEngine (adapters)
        ├── DialogueSpeechUseCase (use_cases)
        │     ├── TTSEngine (adapters)
        │     └── FFmpegAudioProcessor (adapters)
        ├── StudioPodcastUseCase (use_cases)
        │     ├── LLMEngine (adapters) ← 独立选择
        │     ├── TTSEngine (adapters) ← 独立选择
        │     └── FFmpegAudioProcessor (adapters)
        └── BatchSpeechUseCase (use_cases)
              ├── TTSEngine (adapters)
              └── FFmpegAudioProcessor (adapters)
```
