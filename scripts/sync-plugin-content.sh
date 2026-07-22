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

# QUAN TRONG: dung `sed 's/\r$//'` thay vi `cp` thuan - CRLF lam YAML frontmatter
# parser cua Claude Code fail ngam (metadata rong). File nguon trong .claude/ co the
# bi Windows autocrlf ghi lai thanh CRLF bat cu luc nao, nen luon normalize ve LF
# ngay tai buoc sync nay, khong dua vao .gitattributes mot minh.

echo "==> Dong bo agents/ tu .claude/agents/*.md (normalize LF)"
rm -f agents/*.md
for f in .claude/agents/*.md; do sed 's/\r$//' "$f" > "agents/$(basename "$f")"; done

echo "==> Dong bo commands/ tu .claude/commands/*.md (normalize LF, bo qua .skill/.docx/.pdf)"
rm -f commands/*.md
for f in .claude/commands/*.md; do sed 's/\r$//' "$f" > "commands/$(basename "$f")"; done

echo "==> Dong bo hooks/ tu .claude/hooks/*.js (normalize LF, giu nguyen hooks/hooks.json)"
rm -f hooks/*.js
for f in .claude/hooks/*.js; do sed 's/\r$//' "$f" > "hooks/$(basename "$f")"; done

echo "==> Kiem tra YAML frontmatter (phat hien loi dau ':' trong description chua bi quote)"
for f in agents/*.md commands/*.md; do
  python3 -c "
import yaml, sys
content = open('$f', encoding='utf-8').read()
parts = content.split('---')
if len(parts) < 3:
    print('$f: KHONG CO FRONTMATTER'); sys.exit(1)
try:
    yaml.safe_load(parts[1])
except Exception as e:
    print('$f: YAML LOI -', str(e).splitlines()[0]); sys.exit(1)
" || echo "  ^ SUA FILE TREN TRUOC KHI COMMIT (thuong do dau ':' trong description chua duoc quote)"
done

echo "==> Xong. Nho bump version trong .claude-plugin/marketplace.json va .claude-plugin/plugin.json"
echo "    (plugin cache cua Claude Code duoc luu theo thu muc ten = version, khong bump se bi cache cu)."
echo "    Sau do chay: claude plugin validate .claude-plugin/plugin.json"
