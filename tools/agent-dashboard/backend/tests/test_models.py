"""Unit tests for models.py — SUBAGENT_DISPLAY, get_subagent_display_name, decode_project_slug."""
from __future__ import annotations

import pytest

from agent_dashboard.models import (
    SUBAGENT_DISPLAY,
    decode_project_slug,
    get_subagent_display_name,
)


# ── SUBAGENT_DISPLAY mapping ──────────────────────────────────────────────────

EXPECTED_AGENTS = [
    ("cto",                    "CTO"),
    ("product-manager",        "Product Manager"),
    ("business-analyst",       "Business Analyst"),
    ("engineering-manager",    "Engineering Manager"),
    ("tech-lead",              "Tech Lead"),
    ("senior-developer",       "Senior Developer"),
    ("junior-developer",       "Junior Developer"),
    ("qa-lead",                "QA Lead"),
    ("qa-engineer",            "QA Engineer"),
    ("devops-lead",            "DevOps Lead"),
    ("devops-engineer",        "DevOps Engineer"),
    ("project-manager",        "Project Manager"),
    ("ui-ux-designer",         "UI/UX Designer"),
    ("ux-ui-reviewer",         "UX/UI Reviewer"),
    ("documentation-writer",   "Documentation Writer"),
    ("code-migrator",          "Code Migrator"),
    ("github-repo-researcher", "GitHub Repo Researcher"),
    ("task-planner",           "Task Planner"),
    ("md-optimizer",           "MD Optimizer"),
]


@pytest.mark.parametrize("slug,expected", EXPECTED_AGENTS)
def test_subagent_display_known_agents(slug: str, expected: str):
    assert SUBAGENT_DISPLAY[slug] == expected


def test_subagent_display_covers_all_kztek_agents():
    """All 19 agents defined in CLAUDE.md §1 must be present in the mapping."""
    slugs = {pair[0] for pair in EXPECTED_AGENTS}
    assert slugs == set(SUBAGENT_DISPLAY.keys())


# ── get_subagent_display_name ─────────────────────────────────────────────────

def test_get_subagent_display_name_known():
    assert get_subagent_display_name("senior-developer") == "Senior Developer"
    assert get_subagent_display_name("cto") == "CTO"
    assert get_subagent_display_name("ux-ui-reviewer") == "UX/UI Reviewer"


def test_get_subagent_display_name_fallback_title_case():
    """Unknown subagent_type must fall back to title-case + hyphen → space."""
    assert get_subagent_display_name("my-custom-agent") == "My Custom Agent"
    assert get_subagent_display_name("new-role") == "New Role"


def test_get_subagent_display_name_single_word():
    assert get_subagent_display_name("dispatcher") == "Dispatcher"


# ── decode_project_slug ───────────────────────────────────────────────────────

def test_decode_windows_drive_prefix():
    """Real slug from KZTEK dev machine must decode correctly."""
    slug = "c--Users-nguye-Desktop-Claude-Git-claude"
    result = decode_project_slug(slug)
    assert result.startswith("C:\\")
    # '--' separators become '\', single '-' stay
    assert result == "C:\\Users-nguye-Desktop-Claude-Git-claude"


def test_decode_multiple_double_dash_separators():
    slug = "d--Projects--my-app"
    result = decode_project_slug(slug)
    assert result == "D:\\Projects\\my-app"


def test_decode_no_drive_prefix_returns_slug_unchanged():
    slug = "some-project-without-drive"
    assert decode_project_slug(slug) == slug


def test_decode_uppercase_drive_not_matched():
    """Convention is lowercase drive; uppercase should be returned as-is."""
    slug = "C--Projects--something"
    assert decode_project_slug(slug) == slug


def test_decode_empty_string():
    assert decode_project_slug("") == ""


def test_decode_drive_only():
    slug = "c--"
    result = decode_project_slug(slug)
    assert result == "C:\\"
