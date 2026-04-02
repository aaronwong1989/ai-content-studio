#!/usr/bin/env bash
#────────────────────────────────────────────────────────────────────────────
# ai-content-studio Skill 安装脚本
#────────────────────────────────────────────────────────────────────────────
# 功能：将 ai-content-studio skill 安装到通用 agent skills 目录
# 用法：bash scripts/install.sh [--uninstall]
#
# 安装路径：
#   - 主路径：~/.agents/skills/ai-content-studio/（通用标准路径）
#   - Claude Code 兼容：~/.claude/skills/ai-content-studio → ~/.agents/skills/ai-content-studio（符号链接）
#
# Skill Bundle 结构：
#   SKILL.md        ← 主入口
#   scripts/        ← 安装脚本、TTS 引擎源码
#   references/     ← 参考文档（配置文件、故障排查）
#   tests/          ← 测试脚本
#────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SKILL_NAME="ai-content-studio"

# 主安装路径（通用标准）
SKILL_DEST="${HOME}/.agents/skills/${SKILL_NAME}"
# Claude Code 兼容路径（符号链接）
CLAUDE_SKILL_LINK="${HOME}/.claude/skills/${SKILL_NAME}"
INSTALL_MARKER="${SKILL_DEST}/.installed_from_ai_content_studio_repo"

# 解析参数
UNINSTALL=false
if [[ "${1:-}" == "--uninstall" ]]; then
    UNINSTALL=true
fi

#────────────────────────────────────────────────────────────────────────────
# 卸载
#────────────────────────────────────────────────────────────────────────────
uninstall_skill() {
    echo "→ 卸载 ai-content-studio skill..."

    # 删除符号链接（如果存在）
    if [[ -L "$CLAUDE_SKILL_LINK" ]]; then
        echo "  → 删除 Claude Code 符号链接：${CLAUDE_SKILL_LINK}"
        rm "$CLAUDE_SKILL_LINK"
    fi

    # 删除主安装
    if [[ -d "$SKILL_DEST" ]]; then
        echo "  → 删除主安装：${SKILL_DEST}"
        rm -rf "$SKILL_DEST"
        echo "✓ 已卸载 ${SKILL_NAME}"
    else
        echo "  → 未找到已安装的 skill"
    fi
}

#────────────────────────────────────────────────────────────────────────────
# 安装：复制完整 skill bundle + 创建符号链接
#────────────────────────────────────────────────────────────────────────────
install_skill() {
    if [[ ! -f "${REPO_ROOT}/SKILL.md" ]]; then
        echo "✗ 错误：找不到 ${REPO_ROOT}/SKILL.md"
        echo "  请确保在 ai-content-studio 项目根目录运行此脚本。"
        exit 1
    fi

    echo "→ 安装 ai-content-studio skill..."
    echo "  源：${REPO_ROOT}/"
    echo "  主路径：${SKILL_DEST}/"
    echo "  Claude Code 兼容：${CLAUDE_SKILL_LINK} → ${SKILL_DEST}"

    # 备份已有安装（如果存在）
    if [[ -d "$SKILL_DEST" ]]; then
        BACKUP="${HOME}/.agents/skills/${SKILL_NAME}.backup_$(date +%Y%m%d_%H%M%S)"
        echo "  ! 已存在同名 skill，备份到：${BACKUP}"
        mv "$SKILL_DEST" "$BACKUP"
    fi

    # 备份已有符号链接（如果存在）
    if [[ -L "$CLAUDE_SKILL_LINK" ]]; then
        echo "  ! 备份已有符号链接"
        mv "$CLAUDE_SKILL_LINK" "${CLAUDE_SKILL_LINK}.backup_$(date +%Y%m%d_%H%M%S)"
    fi

    # 删除已有实体目录（如果存在，且不是符号链接）
    if [[ -d "$CLAUDE_SKILL_LINK" && ! -L "$CLAUDE_SKILL_LINK" ]]; then
        echo "  ! 检测到旧安装（实体目录），备份后删除以创建符号链接"
        mv "$CLAUDE_SKILL_LINK" "${CLAUDE_SKILL_LINK}.legacy_$(date +%Y%m%d_%H%M%S)"
    fi

    # 确保目标目录存在
    mkdir -p "$SKILL_DEST"
    mkdir -p "$(dirname "$CLAUDE_SKILL_LINK")"

    # 复制完整 skill bundle 到主路径
    cp "${REPO_ROOT}/SKILL.md" "${SKILL_DEST}/SKILL.md"

    for subdir in scripts references tests; do
        if [[ -d "${REPO_ROOT}/${subdir}" ]]; then
            cp -r "${REPO_ROOT}/${subdir}" "${SKILL_DEST}/${subdir}"
        fi
    done

    # 标记安装来源
    touch "$INSTALL_MARKER"

    # 创建符号链接（Claude Code 兼容）
    ln -sf "$SKILL_DEST" "$CLAUDE_SKILL_LINK"

    echo "✓ skill 已安装到：${SKILL_DEST}/"
    echo "✓ Claude Code 符号链接：${CLAUDE_SKILL_LINK} → ${SKILL_DEST}"
    echo ""
    ls -la "${SKILL_DEST}/"
    echo ""
    echo "  重启 Claude Code 会话即可使用此 skill。"
}

#────────────────────────────────────────────────────────────────────────────
# 入口
#────────────────────────────────────────────────────────────────────────────
if [[ "$UNINSTALL" == "true" ]]; then
    uninstall_skill
else
    install_skill
fi
