# Changelog

## [1.0.2] - 2026-04-02

### Added
- **安装自动化增强**: `scripts/install.sh` 脚本现在会自动安装 Python 依赖。
- **Skill Bundle 结构补全**: 在安装包中补齐了 `requirements.txt`，确保 Agent 环境依赖完整。
- **文档校准**: 更新 `INSTALL.md` 中的 API 配置说明，使其与 `opencode.json` 的实际 JSON 路径一致。

## [1.0.1] - 2026-04-02

### Added
- **正式化表述**: 全面改写 `README.md`，采用专业的中立视角。
- **Token Plan 价值提升**: 优化了 MiniMax 套餐复用的引导描述，明确 Builder 权益。
- **GitHub 链接优化**: 将文档中的本地路径替换为完整的 GitHub 路径，确保外部访问准确性。

## [1.0.0] - 2026-04-02

### Added
- **AI Content Studio Skill**: 本地工具正式重构为多 Agent 兼容的 Skill (支持 Claude Code, OpenCode, OpenClaw)。
- **存储整合**: 将所有临时文件和缓存统一至 `work/` 目录，简化结构。
- **结构优化**: 核心逻辑移至 `scripts/studio/`，文档移至 `references/`，提升 AI 检索效率。
- **MiniMax 优先策略**: 默认使用 MiniMax T2A V2，支持自动故障转移至 Qwen 模型。
- **套餐复用 (Token Plan) 赋能**: 深度整合 MiniMax Token Plan，支持复用“编码套餐”以大幅度降低生成成本。
- **全新文档体系**: 包含 `README.md`、`INSTALL.md` (含全流程 Agent 自动安装脚本) 及针对 Agent 优化的说明。

### Changed
- 重构项目文件布局，对齐 AI Agent Skill 目录标准。
- 简化 `.gitignore` 配置，仅忽略 `work/` 目录。
- 更新 `README.md`，使用更正式的非第一人称表述。
