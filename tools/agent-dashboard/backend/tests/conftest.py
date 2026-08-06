"""Shared pytest fixtures."""
from __future__ import annotations

import pathlib
import pytest


FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_jsonl_path() -> pathlib.Path:
    return FIXTURES_DIR / "sample.jsonl"


@pytest.fixture
def tmp_jsonl(tmp_path) -> pathlib.Path:
    """Empty JSONL file in a project-like structure: <tmp>/proj-slug/<uuid>.jsonl"""
    proj = tmp_path / "my-project"
    proj.mkdir()
    return proj / "aaaabbbb-1234-5678-abcd-000000000001.jsonl"
