#!/usr/bin/env bash
# review-package.sh — Tạo file diff handoff cho code reviewer
#
# Học từ obra/superpowers skills/subagent-driven-development/scripts/review-package
# (xem docs/research/RESEARCH-superpowers-2026-07-12.md, §1.3.3 File Handoff Protocol)
#
# Mục đích: tránh paste toàn bộ diff vào prompt (context window inflation).
# Reviewer nhận 1 đường dẫn file, đọc 1 lần, không phải copy-paste thủ công.
#
# Usage: scripts/review-package.sh <BASE> <HEAD>
#   BASE : git ref điểm bắt đầu (VD: main, origin/main, abc1234)
#   HEAD : git ref điểm kết thúc (VD: HEAD, feature/my-branch, def5678)
#
# Output: tạo file trong _workspace/ chứa:
#   - Danh sách commit (git log BASE..HEAD --oneline)
#   - Diffstat (git diff BASE..HEAD --stat)
#   - Full diff (git diff BASE..HEAD)
# In đường dẫn file ra stdout.
#
# Ví dụ:
#   scripts/review-package.sh origin/main HEAD
#   scripts/review-package.sh abc1234 HEAD
#   FILE=$(scripts/review-package.sh main HEAD) && echo "Review file: $FILE"

set -euo pipefail

BASE="${1:?Thiếu tham số BASE. Usage: scripts/review-package.sh <BASE> <HEAD>}"
HEAD="${2:?Thiếu tham số HEAD. Usage: scripts/review-package.sh <BASE> <HEAD>}"

WORKSPACE_DIR="_workspace"
mkdir -p "$WORKSPACE_DIR"

TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
OUTPUT_FILE="${WORKSPACE_DIR}/review-package-${TIMESTAMP}.txt"

{
  echo "=== REVIEW PACKAGE: ${BASE}..${HEAD} ==="
  echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""

  echo "=== COMMITS ==="
  git log "${BASE}..${HEAD}" --oneline
  echo ""

  echo "=== DIFFSTAT ==="
  git diff "${BASE}..${HEAD}" --stat
  echo ""

  echo "=== FULL DIFF ==="
  git diff "${BASE}..${HEAD}"
} > "$OUTPUT_FILE"

echo "$OUTPUT_FILE"
