#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đồng bộ 1 chiều: Claude-Git (nguồn sự thật) -> GeminiGit (đích).

Vấn đề gốc: agents/skills/lessons/scripts cho Claude Code được sửa trong repo
Claude-Git, còn bản dùng cho Gemini Agent/Antigravity ở repo GeminiGit phải
copy tay + tự dịch thuật ngữ (Claude Code -> Gemini Agent, claude-sonnet-4-6
-> gemini-3.6-flash, .claude/ -> .gemini/, ...) mỗi khi có thay đổi -> dễ quên,
dễ lệch.

Script này tự động hoá đúng việc "copy tay" đó:
  - File .md trong các thư mục dùng chung  -> đọc, áp bảng thay thế thuật ngữ
    (REPLACEMENTS bên dưới), ghi ra đúng vị trí tương ứng trong GeminiGit.
  - File khác (.py/.ps1/.js/.json/.png/.sh) -> copy nguyên văn, không sửa nội
    dung (tránh làm hỏng code/logic bên trong).
  - File .docx/.pdf -> KHÔNG copy, KHÔNG tự sinh mặc định (dùng --docx để bật
    regenerate qua md_to_docx_kztek.py cho những file .md vừa thay đổi).

KHÔNG tự commit/push. Xem lại `git diff` trong repo GeminiGit rồi tự quyết
định commit.

Cách dùng:
    python scripts/sync-to-gemini.py                  # dry-run, chỉ liệt kê
    python scripts/sync-to-gemini.py --apply           # thực sự ghi file
    python scripts/sync-to-gemini.py --apply --docx    # + xuất lại .docx/.pdf
    python scripts/sync-to-gemini.py --apply --prune   # + xoá file bên Gemini
                                                          không còn ở nguồn
    python scripts/sync-to-gemini.py --source <path> --target <path>
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Bảng thay thế thuật ngữ Claude -> Gemini (áp dụng theo ĐÚNG thứ tự này,
# pattern cụ thể hơn phải nằm trước pattern chung để không bị ghi đè nhầm).
# ---------------------------------------------------------------------------
REPLACEMENTS: list[tuple[str, str]] = [
    (r"claude-opus-4-7", "gemini-3.6-pro"),
    (r"claude-sonnet-4-6", "gemini-3.6-flash"),
    (r"claude-haiku-4-5", "gemini-3.6-flash-lite"),
    (r"Claude Code", "Gemini Agent"),
    (r"Claude Flow", "Gemini Flow"),
    (r"Agent tool", "invoke_subagent tool"),
    (r"C:/Users/nguye/\.claude", "C:/Users/nguye/.gemini"),
    (r"C:\\Users\\nguye\\\.claude", r"C:\\Users\\nguye\\.gemini"),
    (r"\.claude/", ".gemini/"),
    (r"CLAUDE\.md", "GEMINI.md"),
    (r"\bClaude\b", "Gemini"),
]
_COMPILED = [(re.compile(p), r) for p, r in REPLACEMENTS]


def transform_text(text: str) -> str:
    for pattern, repl in _COMPILED:
        text = pattern.sub(repl, text)
    return text


# ---------------------------------------------------------------------------
# Các đơn vị đồng bộ: (đường dẫn tương đối trong SOURCE, đường dẫn tương đối
# trong TARGET). File đơn lẻ hoặc thư mục (đồng bộ đệ quy) đều khai báo ở đây.
# ---------------------------------------------------------------------------
SYNC_UNITS: list[tuple[str, str]] = [
    ("CLAUDE.md", "GEMINI.md"),
    ("RULES.md", "RULES.md"),
    ("WORKFLOW.md", "WORKFLOW.md"),
    (".claude/agents", ".gemini/agents"),
    (".claude/commands", ".gemini/commands"),
    (".claude/evals", ".gemini/evals"),
    (".claude/templates", ".gemini/templates"),
    (".claude/shared", ".gemini/shared"),
    (".claude/references", ".gemini/references"),
    (".claude/hooks", ".gemini/hooks-kztek"),
    (".claude/lessons", ".gemini/lessons"),
    ("scripts", "scripts"),
]

EXCLUDE_DIR_NAMES = {"__pycache__", ".git", "windows-tools"}  # windows-tools: GUI tool đã hand-fork riêng cho từng bên (ClaudeConfigAudit.ps1 vs GeminiConfigAudit.ps1), KHÔNG mirror
EXCLUDE_FILE_NAMES = {"link-global.ps1"}  # chỉ dùng cho junction phía Claude
SKIP_SUFFIXES = {".docx", ".pdf"}


class Change:
    def __init__(self, kind: str, target: Path):
        self.kind = kind  # "create" | "update" | "unchanged" | "orphan"
        self.target = target


def iter_source_files(src_root: Path, src_rel: str):
    src_path = src_root / src_rel
    if src_path.is_file():
        yield src_path
        return
    if not src_path.exists():
        return
    for p in src_path.rglob("*"):
        if p.is_dir():
            continue
        if any(part in EXCLUDE_DIR_NAMES for part in p.relative_to(src_root).parts):
            continue
        if p.name in EXCLUDE_FILE_NAMES:
            continue
        if p.suffix.lower() in SKIP_SUFFIXES:
            continue
        yield p


def sync(source_root: Path, target_root: Path, apply: bool, prune: bool, docx: bool) -> list[Change]:
    changes: list[Change] = []
    expected_targets: set[Path] = set()
    changed_md_targets: list[Path] = []

    for src_rel, dst_rel in SYNC_UNITS:
        src_base = source_root / src_rel
        dst_base = target_root / dst_rel
        if not src_base.exists():
            print(f"[skip] Không tồn tại ở nguồn: {src_rel}")
            continue

        for src_file in iter_source_files(source_root, src_rel):
            if src_base.is_file():
                rel_from_base = Path()
            else:
                rel_from_base = src_file.relative_to(src_base)
            dst_file = dst_base / rel_from_base if not src_base.is_file() else dst_base
            expected_targets.add(dst_file)

            if src_file.suffix.lower() == ".md":
                new_text = transform_text(src_file.read_text(encoding="utf-8"))
                old_text = dst_file.read_text(encoding="utf-8") if dst_file.exists() else None
                if old_text == new_text:
                    changes.append(Change("unchanged", dst_file))
                    continue
                changes.append(Change("create" if old_text is None else "update", dst_file))
                if apply:
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    dst_file.write_text(new_text, encoding="utf-8")
                    changed_md_targets.append(dst_file)
            else:
                new_bytes = src_file.read_bytes()
                old_bytes = dst_file.read_bytes() if dst_file.exists() else None
                if old_bytes == new_bytes:
                    changes.append(Change("unchanged", dst_file))
                    continue
                changes.append(Change("create" if old_bytes is None else "update", dst_file))
                if apply:
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    dst_file.write_bytes(new_bytes)

        # Phát hiện orphan: file có ở target nhưng không còn nguồn tương ứng.
        if dst_base.is_dir():
            for existing in dst_base.rglob("*"):
                if existing.is_dir():
                    continue
                if existing.suffix.lower() in SKIP_SUFFIXES:
                    continue  # docx/pdf tự quản lý riêng, không prune theo nguồn .md
                if existing not in expected_targets:
                    changes.append(Change("orphan", existing))
                    if apply and prune:
                        existing.unlink()

    if apply and docx and changed_md_targets:
        md_script = target_root / "scripts" / "md_to_docx_kztek.py"
        if md_script.exists():
            for f in changed_md_targets:
                print(f"  -> xuất DOCX/PDF: {f}")
                subprocess.run(
                    [sys.executable, str(md_script), str(f)],
                    env={"PYTHONIOENCODING": "utf-8"},
                    cwd=str(target_root),
                )
        else:
            print(f"[warn] Không thấy {md_script}, bỏ qua bước xuất DOCX/PDF")

    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=None, help="Đường dẫn repo Claude-Git (mặc định: 2 cấp trên script này)")
    parser.add_argument("--target", default=None, help="Đường dẫn repo GeminiGit (mặc định: Desktop/GeminiGit)")
    parser.add_argument("--apply", action="store_true", help="Thực sự ghi file (mặc định chỉ dry-run)")
    parser.add_argument("--prune", action="store_true", help="Xoá file orphan bên Gemini không còn ở nguồn (chỉ có hiệu lực cùng --apply)")
    parser.add_argument("--docx", action="store_true", help="Xuất lại .docx/.pdf cho các file .md vừa thay đổi (chậm hơn)")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    source_root = Path(args.source).resolve() if args.source else script_dir.parent
    target_root = Path(args.target).resolve() if args.target else (source_root.parent.parent / "GeminiGit")

    if not source_root.exists():
        print(f"[error] Không tìm thấy source: {source_root}")
        return 1
    if not target_root.exists():
        print(f"[error] Không tìm thấy target: {target_root}")
        return 1

    print(f"Nguồn : {source_root}")
    print(f"Đích  : {target_root}")
    print(f"Mode  : {'APPLY' if args.apply else 'DRY-RUN (thêm --apply để ghi thật)'}\n")

    changes = sync(source_root, target_root, apply=args.apply, prune=args.prune, docx=args.docx)

    by_kind: dict[str, list[Path]] = {"create": [], "update": [], "orphan": [], "unchanged": []}
    for c in changes:
        by_kind[c.kind].append(c.target)

    for kind, label in [("create", "MỚI"), ("update", "CẬP NHẬT"), ("orphan", "ORPHAN (không còn ở nguồn)")]:
        items = by_kind[kind]
        if not items:
            continue
        print(f"=== {label} ({len(items)}) ===")
        for p in items:
            print(f"  {p.relative_to(target_root)}")
        print()

    print(f"Tổng: {len(by_kind['create'])} mới, {len(by_kind['update'])} cập nhật, "
          f"{len(by_kind['orphan'])} orphan, {len(by_kind['unchanged'])} không đổi.")

    if by_kind["orphan"] and not args.prune:
        print("(Chạy thêm --prune --apply nếu muốn xoá các file orphan trên.)")
    if not args.apply and (by_kind["create"] or by_kind["update"]):
        print("\nĐây là dry-run — chưa ghi gì cả. Thêm --apply để thực sự đồng bộ.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
