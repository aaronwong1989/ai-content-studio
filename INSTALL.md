# AI Content Studio Skill 安装指南

> **适用对象**：Claude Code、OpenCode、OpenClaw 等 AI Agent
> **安装目标**：将 skill 安装到 `~/.claude/skills/ai-content-studio/`，使 Agent 在 `ai-content-studio` 项目工作时自动激活

---

## 快速安装（推荐）

### 步骤 1：定位 Skill 源目录

```bash
# 当前目录即为 skill 源码仓库
SKILL_SOURCE="$(pwd)"  # 或显式指定：/Users/huangzhonghui/ai-content-studio
```

### 步骤 2：运行安装脚本

```bash
cd "$SKILL_SOURCE"
bash scripts/install.sh
```

安装脚本自动执行：
1. 检查目标路径 `~/.claude/skills/ai-content-studio/` 是否存在
2. 如已存在，自动备份到 `~/.claude/skills/ai-content-studio.backup_<timestamp>/`
3. 复制完整 bundle 结构（`SKILL.md` + `scripts/` + `references/` + `tests/`）
4. 输出安装路径和验证指引

### 步骤 3：验证安装

```bash
# 检查安装结果
ls -la ~/.claude/skills/ai-content-studio/SKILL.md

# 预期输出：文件存在且非空
```

---

## 卸载 Skill

```bash
cd /Users/huangzhonghui/ai-content-studio
bash scripts/install.sh --uninstall
```

---

## 手动安装（备选）

如果安装脚本不可用，Agent 可直接执行复制命令：

```bash
SKILL_SOURCE="/Users/huangzhonghui/ai-content-studio"
SKILL_DEST="$HOME/.claude/skills/ai-content-studio"

# 创建目标目录
mkdir -p "$SKILL_DEST"

# 复制核心文件
cp -r "$SKILL_SOURCE/SKILL.md" "$SKILL_DEST/"
cp -r "$SKILL_SOURCE/scripts/" "$SKILL_DEST/"
cp -r "$SKILL_SOURCE/references/" "$SKILL_DEST/"
cp -r "$SKILL_SOURCE/tests/" "$SKILL_DEST/"
```

---

## Git Clone 方式（版本管理）

如果 skill 已托管到 Git 仓库：

```bash
# 先备份已存在的安装
if [[ -d ~/.claude/skills/ai-content-studio ]]; then
    mv ~/.claude/skills/ai-content-studio ~/.claude/skills/ai-content-studio.backup_$(date +%Y%m%d_%H%M%S)
fi

# Clone 新技能
git clone <skill-repo-url> ~/.claude/skills/ai-content-studio
```

---

## 安装后验证

### 1. 文件结构检查

```bash
tree -L 2 ~/.claude/skills/ai-content-studio/
# 应包含：SKILL.md, scripts/, references/, tests/
```

### 2. Skill 激活测试

在 `ai-content-studio` 项目目录发起任务，例如：

```
生成一段产品公告的 TTS 音频
```

Agent 应能：
- 自动识别 `ai-content-studio` skill
- 引用 `SKILL.md` 中的命令和架构说明
- 正确执行 TTS 合成任务

---

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| Skill 未激活 | 确认当前工作目录为 `ai-content-studio` 项目根目录 |
| 脚本执行失败 | 检查 `scripts/install.sh` 执行权限：`chmod +x scripts/install.sh` |
| 备份冲突 | 手动删除 `~/.claude/skills/ai-content-studio.backup_*` 后重试 |
| 安装后仍无效 | 重启 Claude Code 会话，确保 skill 元数据重新加载 |

---

## 依赖检查

Skill 安装完成后，确保项目运行时依赖已就绪：

```bash
# Python 依赖
pip install -r requirements.txt

# FFmpeg（音频处理必需）
brew install ffmpeg   # macOS
sudo apt install ffmpeg  # Linux

# 环境变量（可选，从 ~/.config/opencode/opencode.json 自动读取）
export DASHSCOPE_API_KEY="..."
export MINIMAX_API_KEY="..."
```

---

## 文件结构说明

安装后的 skill 目录结构：

```
~/.claude/skills/ai-content-studio/
├── SKILL.md                 # Skill 主入口（Agent 自动读取）
├── scripts/
│   ├── install.sh           # 安装脚本
│   └── studio/              # TTS 引擎源码
│       ├── paths.py         # 路径配置
│       ├── studio_orchestrator.py
│       ├── minimax_tts_tool.py
│       ├── qwen_tts_tool.py
│       └── ...
├── references/
│   └── configs/             # 角色库配置
└── tests/                   # 测试脚本
```

---

## 更新 Skill

如果 skill 源码有更新，重新运行安装脚本即可：

```bash
cd /Users/huangzhonghui/ai-content-studio
bash scripts/install.sh  # 自动备份旧版本
```
