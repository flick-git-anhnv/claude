#!/usr/bin/env python3
"""skillgen_kztek.py — Skill generator MVP cho hệ thống KZTEK.

Ý tưởng học từ tools/skillgen/gen.py + platforms.toml của graphify (Graphify-Labs/graphify).
Phiên bản này là MVP đơn giản hoá, chứng minh khái niệm với 3 platform: Claude Code, Cursor, Kiro.

Mục tiêu: 1 skill source (.claude/commands/*.md) → nhiều platform output, đồng bộ tự động.

Cách dùng:
    python scripts/skillgen_kztek.py                          # sinh tất cả skill cho tất cả platform
    python scripts/skillgen_kztek.py --skill verify-pr       # chỉ sinh skill verify-pr cho tất cả platform
    python scripts/skillgen_kztek.py --platform cursor        # chỉ sinh tất cả skill cho cursor
    python scripts/skillgen_kztek.py --list-platforms         # liệt kê platform có sẵn
    python scripts/skillgen_kztek.py --check                  # kiểm tra drift (so sánh output vs committed)
    python scripts/skillgen_kztek.py --dry-run                # in output ra stdout, không ghi file

Platform hiện hỗ trợ (xem platforms-kztek.toml để cấu hình thêm):
    claude  → .claude/commands/{name}.md        (source gốc, identity transform)
    cursor  → .cursor/rules/{name}.mdc          (Cursor MDC format với frontmatter riêng)
    kiro    → .kiro/steering/{name}.md          (Kiro steering doc format)

NOTE: Đây là bản MVP — không có tất cả tính năng của graphify skillgen.
      Fragment template, shared references, audit coverage... sẽ bổ sung khi cần.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import tomllib  # Python 3.11+ stdlib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        print("ERROR: Cần Python 3.11+ hoặc cài tomli: pip install tomli", file=sys.stderr)
        sys.exit(1)

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent
PLATFORMS_TOML = SCRIPT_DIR / "platforms-kztek.toml"
SKILLS_SOURCE_DIR = WORKSPACE_ROOT / ".claude" / "commands"


# ──────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class PlatformConfig:
    """Cấu hình một platform đích."""
    key: str
    output_dir: str            # đường dẫn relative từ workspace root
    file_ext: str              # .md hoặc .mdc
    frontmatter_format: str    # "claude" | "cursor" | "kiro" | "none"
    description: str           # mô tả platform để sinh header
    install_note: str          # ghi chú cài đặt cho platform này


@dataclass
class SkillSource:
    """Một skill file nguồn đã parse."""
    name: str
    description: str
    body: str                  # phần body sau frontmatter (không tính --- block)
    source_path: Path


# ──────────────────────────────────────────────
# Parse skill source
# ──────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Tách YAML frontmatter (---...---) khỏi body.

    Trả về (frontmatter_dict, body_text).
    Nếu không có frontmatter → ({}, text).
    Chỉ parse đơn giản key: value, không dùng PyYAML để tránh thêm dependency.
    """
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return {}, text

    end_idx = text.find("\n---\n", 4)
    if end_idx == -1:
        return {}, text

    fm_block = text[4:end_idx]
    body = text[end_idx + 5:]  # bỏ qua "\n---\n"

    fm: dict[str, str] = {}
    for line in fm_block.splitlines():
        m = re.match(r'^(\w[\w-]*)\s*:\s*(.+)$', line)
        if m:
            key, val = m.group(1), m.group(2).strip().strip('"')
            fm[key] = val
    return fm, body.lstrip("\n")


def load_skill(path: Path) -> Optional[SkillSource]:
    """Đọc và parse một skill file. Trả về None nếu không có name/description."""
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    name = fm.get("name") or path.stem
    description = fm.get("description", "")

    if not description:
        # Skill không có description → bỏ qua (không phải skill file thực sự)
        return None

    return SkillSource(name=name, description=description, body=body, source_path=path)


def load_all_skills() -> list[SkillSource]:
    """Tải tất cả skill từ .claude/commands/."""
    skills = []
    for md_file in sorted(SKILLS_SOURCE_DIR.glob("*.md")):
        skill = load_skill(md_file)
        if skill is not None:
            skills.append(skill)
    return skills


# ──────────────────────────────────────────────
# Load platform config
# ──────────────────────────────────────────────

def load_platforms() -> dict[str, PlatformConfig]:
    """Parse platforms-kztek.toml thành dict[key → PlatformConfig]."""
    if not PLATFORMS_TOML.exists():
        # Tạo file mặc định nếu chưa có
        _write_default_platforms_toml()

    data = tomllib.loads(PLATFORMS_TOML.read_text(encoding="utf-8"))
    out: dict[str, PlatformConfig] = {}

    for key, cfg in data.get("platform", {}).items():
        out[key] = PlatformConfig(
            key=key,
            output_dir=cfg["output_dir"],
            file_ext=cfg.get("file_ext", ".md"),
            frontmatter_format=cfg.get("frontmatter_format", "none"),
            description=cfg.get("description", key),
            install_note=cfg.get("install_note", ""),
        )
    return out


def _write_default_platforms_toml() -> None:
    """Tạo platforms-kztek.toml mặc định nếu chưa tồn tại."""
    default = '''\
# platforms-kztek.toml — Cấu hình platform cho KZTEK Skill Generator
# Học từ tools/skillgen/platforms.toml của Graphify-Labs/graphify (MVP đơn giản hóa)
#
# Thêm platform mới: thêm [platform.<key>] block tương ứng
# Chạy: python scripts/skillgen_kztek.py để sinh lại tất cả

[platform.claude]
output_dir = ".claude/commands"
file_ext = ".md"
frontmatter_format = "claude"
description = "Claude Code (claude.ai / VSCode Extension)"
install_note = "Skill đặt trong .claude/commands/, Claude Code tự nhận diện."

[platform.cursor]
output_dir = ".cursor/rules"
file_ext = ".mdc"
frontmatter_format = "cursor"
description = "Cursor AI IDE"
install_note = "Rule đặt trong .cursor/rules/, Cursor tự áp dụng khi mở project."

[platform.kiro]
output_dir = ".kiro/steering"
file_ext = ".md"
frontmatter_format = "kiro"
description = "Kiro AI IDE (Amazon)"
install_note = "Steering doc đặt trong .kiro/steering/, Kiro đọc khi khởi động project."
'''
    PLATFORMS_TOML.write_text(default, encoding="utf-8")
    print(f"[skillgen] Tạo cấu hình mặc định: {PLATFORMS_TOML.relative_to(WORKSPACE_ROOT)}")


# ──────────────────────────────────────────────
# Render per platform
# ──────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Chuẩn hoá line endings, đảm bảo 1 newline cuối file."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.rstrip("\n") + "\n"


def render_claude(skill: SkillSource, platform: PlatformConfig) -> str:
    """Platform claude — giữ nguyên source (identity transform).

    Claude Code đã có file nguồn trong .claude/commands/; render này dùng cho
    --check để xác nhận source không bị drift so với committed version.
    """
    frontmatter = (
        f"---\n"
        f"name: {skill.name}\n"
        f'description: "{skill.description}"\n'
        f"---\n\n"
    )
    return _normalise(frontmatter + skill.body)


def render_cursor(skill: SkillSource, platform: PlatformConfig) -> str:
    """Platform cursor — sinh .mdc file với frontmatter Cursor MDC.

    Cursor dùng .cursor/rules/*.mdc với frontmatter:
        ---
        description: <mô tả khi nào áp dụng rule>
        globs: <glob pattern, tuỳ chọn>
        alwaysApply: false
        ---

    Xem: https://docs.cursor.com/context/rules
    """
    frontmatter = (
        f"---\n"
        f"description: >{skill.description}\n"
        f"alwaysApply: false\n"
        f"---\n\n"
    )
    platform_header = (
        f"<!-- Generated by scripts/skillgen_kztek.py — KHÔNG sửa trực tiếp.\n"
        f"     Sửa source tại .claude/commands/{skill.name}.md rồi chạy lại skillgen. -->\n\n"
    )
    # Cursor rule không cần install_note dài — chỉ cần frontmatter đúng và body
    body = skill.body
    return _normalise(frontmatter + platform_header + body)


def render_kiro(skill: SkillSource, platform: PlatformConfig) -> str:
    """Platform kiro — sinh steering doc cho Kiro AI IDE.

    Kiro dùng .kiro/steering/*.md — file Markdown thường (không có frontmatter bắt buộc
    theo chuẩn, nhưng một số convention dùng YAML frontmatter với 'inclusion' field).

    Xem: https://docs.kiro.dev/docs/steering
    """
    frontmatter = (
        f"---\n"
        f"# Kiro steering doc — generated by scripts/skillgen_kztek.py\n"
        f"# Source: .claude/commands/{skill.name}.md\n"
        f"inclusion: manual\n"
        f"---\n\n"
    )
    kiro_header = (
        f"<!-- Platform: Kiro AI IDE | Source: .claude/commands/{skill.name}.md -->\n"
        f"<!-- KHÔNG sửa trực tiếp — sửa source rồi chạy: python scripts/skillgen_kztek.py -->\n\n"
    )
    body = skill.body
    return _normalise(frontmatter + kiro_header + body)


# Dispatch table: frontmatter_format → render function
_RENDERERS = {
    "claude": render_claude,
    "cursor": render_cursor,
    "kiro": render_kiro,
}


def render(skill: SkillSource, platform: PlatformConfig) -> str:
    """Sinh nội dung file output cho skill × platform."""
    renderer = _RENDERERS.get(platform.frontmatter_format)
    if renderer is None:
        raise ValueError(
            f"Platform '{platform.key}' có frontmatter_format='{platform.frontmatter_format}' "
            f"chưa được hỗ trợ. Các giá trị hợp lệ: {list(_RENDERERS)}"
        )
    return renderer(skill, platform)


def output_path(skill: SkillSource, platform: PlatformConfig) -> Path:
    """Tính đường dẫn output file cho skill × platform."""
    out_dir = WORKSPACE_ROOT / platform.output_dir
    filename = f"{skill.name}{platform.file_ext}"
    return out_dir / filename


# ──────────────────────────────────────────────
# Main actions
# ──────────────────────────────────────────────

def action_generate(
    skills: list[SkillSource],
    platforms: dict[str, PlatformConfig],
    dry_run: bool = False,
) -> int:
    """Sinh (hoặc in) file output cho tất cả skill × platform."""
    count = 0
    for platform in platforms.values():
        for skill in skills:
            # Skip claude source — file đã tồn tại, không ghi đè
            if platform.key == "claude":
                continue

            content = render(skill, platform)
            dst = output_path(skill, platform)

            if dry_run:
                print(f"\n{'='*60}")
                print(f"[DRY-RUN] {dst.relative_to(WORKSPACE_ROOT)}")
                print(f"{'='*60}")
                print(content[:500] + ("...<truncated>" if len(content) > 500 else ""))
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(content, encoding="utf-8", newline="\n")
                print(f"  [OK] {dst.relative_to(WORKSPACE_ROOT)}")
                count += 1

    if not dry_run:
        print(f"\n[skillgen] Sinh xong {count} file(s).")
    return 0


def action_check(
    skills: list[SkillSource],
    platforms: dict[str, PlatformConfig],
) -> int:
    """Kiểm tra drift: so sánh output đã sinh với file committed trên disk."""
    problems: list[str] = []

    for platform in platforms.values():
        if platform.key == "claude":
            continue  # source gốc, không check drift

        for skill in skills:
            content = render(skill, platform)
            dst = output_path(skill, platform)

            if not dst.exists():
                problems.append(f"MISSING: {dst.relative_to(WORKSPACE_ROOT)} (chưa sinh — chạy skillgen)")
            else:
                committed = dst.read_text(encoding="utf-8")
                if _normalise(committed) != content:
                    problems.append(
                        f"DRIFT:   {dst.relative_to(WORKSPACE_ROOT)} "
                        f"(khác với render hiện tại — chạy lại skillgen)"
                    )

    if problems:
        print("[skillgen] CHECK FAILED — phát hiện drift:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    print(f"[skillgen] CHECK OK — tất cả {len(skills) * (len(platforms) - 1)} file(s) đồng bộ.")
    return 0


def action_list_platforms(platforms: dict[str, PlatformConfig]) -> int:
    """Liệt kê platform có sẵn."""
    print("[skillgen] Platform được hỗ trợ:\n")
    for key, cfg in platforms.items():
        print(f"  {key:<12} → {cfg.output_dir}/{{name}}{cfg.file_ext}")
        print(f"             {cfg.description}")
        if cfg.install_note:
            print(f"             Cài đặt: {cfg.install_note}")
        print()
    return 0


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python scripts/skillgen_kztek.py",
        description="KZTEK Skill Generator MVP — sinh skill file cho nhiều AI platform từ 1 source.",
    )
    p.add_argument("--skill", help="Chỉ sinh skill có name này (VD: verify-pr)")
    p.add_argument("--platform", help="Chỉ sinh cho platform này (VD: cursor)")
    p.add_argument("--list-platforms", action="store_true", help="Liệt kê platform có sẵn rồi thoát")
    p.add_argument("--check", action="store_true", help="Kiểm tra drift giữa render và committed file, exit 1 nếu có drift")
    p.add_argument("--dry-run", action="store_true", help="In output ra stdout, không ghi file")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])

    platforms = load_platforms()

    if args.list_platforms:
        return action_list_platforms(platforms)

    # Lọc platform nếu --platform được chỉ định
    if args.platform:
        if args.platform not in platforms:
            print(
                f"ERROR: Platform '{args.platform}' không tồn tại. "
                f"Dùng --list-platforms để xem danh sách.",
                file=sys.stderr,
            )
            return 1
        platforms = {args.platform: platforms[args.platform]}

    # Tải skills
    all_skills = load_all_skills()
    if not all_skills:
        print(f"WARNING: Không tìm thấy skill nào trong {SKILLS_SOURCE_DIR}", file=sys.stderr)
        return 1

    # Lọc skill nếu --skill được chỉ định
    if args.skill:
        all_skills = [s for s in all_skills if s.name == args.skill]
        if not all_skills:
            print(
                f"ERROR: Không tìm thấy skill '{args.skill}' trong {SKILLS_SOURCE_DIR}",
                file=sys.stderr,
            )
            return 1

    print(f"[skillgen] {len(all_skills)} skill(s) × {len(platforms)} platform(s)")
    for s in all_skills:
        print(f"  skill: {s.name}")
    for p in platforms:
        print(f"  platform: {p}")
    print()

    if args.check:
        return action_check(all_skills, platforms)

    return action_generate(all_skills, platforms, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
