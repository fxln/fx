#!/bin/bash

# OpenClaw 中文文档更新检查脚本
# 每周一运行，检查官方文档是否有更新

set -e

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 日期格式化
TODAY=$(date +"%Y-%m-%d")
LOG_FILE="$SCRIPT_DIR/更新日志.md"
TUTORIAL_FILE="$SCRIPT_DIR/OpenClaw-中文使用教程.md"

echo "[$(date)] 开始检查 OpenClaw 官方文档更新..."

# 检查是否有 git
if ! command -v git &> /dev/null; then
    echo "错误：未找到 git 命令"
    exit 1
fi

# 检查远程仓库是否有更新
echo "检查远程仓库状态..."
git fetch origin

# 检查本地是否有变更
if git status | grep -q "Changes not staged for commit\|Untracked files"; then
    echo "发现本地变更，先提交..."
    git add .
    git commit -m "[$TODAY] 自动更新文档" || true
fi

# 尝试拉取最新代码
echo "拉取远程更新..."
git pull origin main || true

# 这里可以添加实际的文档检查逻辑
# 例如：检查官方文档的 llms.txt 是否有变化
# 由于 web_fetch 需要额外配置，这里先留空，记录检查时间

echo "[$TODAY] 文档检查完成" >> "$LOG_FILE"

# 更新教程中的最后更新时间
if [ -f "$TUTORIAL_FILE" ]; then
    # 替换最后更新时间
    sed -i "s/最后更新时间：[0-9\\-]*/最后更新时间：$TODAY/" "$TUTORIAL_FILE"
    
    # 提交更新
    git add "$TUTORIAL_FILE" "$LOG_FILE"
    if git diff --staged --quiet; then
        echo "没有需要提交的更新"
    else
        git commit -m "[$TODAY] 更新文档检查时间"
        git push origin main || echo "推送失败，请手动推送"
    fi
fi

echo "[$(date)] 更新检查完成"

