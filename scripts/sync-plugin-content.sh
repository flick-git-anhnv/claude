#!/usr/bin/env bash
# Dong bo noi dung tu .claude/ (nguon chinh, dung de tu bao tri repo nay qua Claude Code)
# sang cac thu muc root agents/ commands/ hooks/ (noi dung thuc su duoc Claude Code Plugin
# system doc va nap khi cac project khac cai plugin kztek-agents).
#
# Ly do can script nay: Claude Code Plugin YEU CAU agents/commands/hooks nam ngay tai
# ROOT cua plugin package (khong duoc long trong .claude/) - da xac nhan qua test thuc te
# ngay 2026-07-22. Repo nay van giu .claude/ de tu bao tri (Claude Code doc .claude/ khi
# mo chinh repo nay), nen phai co ban sao rieng o root cho plugin tieu thu.
#
# Chay lai script nay MOI LAN sau khi sua .claude/agents, .claude/commands, .claude/hooks,
# TRUOC KHI commit + push, de tranh 2 nguon bi lech nhau.

set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Dong bo agents/ tu .claude/agents/*.md"
rm -f agents/*.md
cp .claude/agents/*.md agents/

echo "==> Dong bo commands/ tu .claude/commands/*.md (bo qua .skill, .docx, .pdf)"
rm -f commands/*.md
cp .claude/commands/*.md commands/

echo "==> Dong bo hooks/ tu .claude/hooks/*.js (giu nguyen hooks/hooks.json)"
rm -f hooks/*.js
cp .claude/hooks/*.js hooks/

echo "==> Xong. Nho bump version trong .claude-plugin/marketplace.json va .claude-plugin/plugin.json"
echo "    (plugin cache cua Claude Code duoc luu theo thu muc ten = version, khong bump se bi cache cu)."
