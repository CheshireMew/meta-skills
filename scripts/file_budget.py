#!/usr/bin/env python3
"""Measure active Skill text against the outer-tool output budget."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path


MAX_OUTER_TOOL_TOKENS = 9_000
BYTES_PER_OUTER_TOOL_TOKEN = 4
IGNORED_DIRECTORY_NAMES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "archive",
    "artifacts",
    "build",
    "dist",
    "node_modules",
    "output",
    "outputs",
    "venv",
}
TEXT_ASSET_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".toml",
    ".tsv",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class FileBudget:
    """One active UTF-8 text file and its outer-tool estimate."""

    path: Path
    byte_count: int
    estimated_tokens: int


def estimate_outer_tool_tokens(byte_count: int) -> int:
    """Return the outer tool's approximate token count for UTF-8 bytes.

    @param byte_count: Number of UTF-8 bytes emitted for the file.
    @returns: Approximate output tokens, rounded up.
    """

    return (byte_count + BYTES_PER_OUTER_TOOL_TOKEN - 1) // BYTES_PER_OUTER_TOOL_TOKEN


def _is_budgeted_path(root: Path, path: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in IGNORED_DIRECTORY_NAMES for part in relative.parts[:-1]):
        return False
    if relative.parts and relative.parts[0] == "assets":
        return path.suffix.lower() in TEXT_ASSET_SUFFIXES
    return True


def collect_file_budgets(root: Path) -> list[FileBudget]:
    """Collect every active UTF-8 text file covered by the Skill budget.

    @param root: Skill directory to inspect.
    @returns: Stable path-sorted file budget records.
    """

    records: list[FileBudget] = []
    for current, directories, files in os.walk(root):
        directories[:] = sorted(
            name for name in directories if name not in IGNORED_DIRECTORY_NAMES
        )
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            if not _is_budgeted_path(root, path):
                continue
            data = path.read_bytes()
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            byte_count = len(data)
            records.append(
                FileBudget(
                    path=path.relative_to(root),
                    byte_count=byte_count,
                    estimated_tokens=estimate_outer_tool_tokens(byte_count),
                )
            )
    return sorted(records, key=lambda record: record.path.as_posix())


def validate_file_budgets(root: Path) -> list[str]:
    """Report active text files that exceed the outer-tool safety budget.

    @param root: Skill directory to inspect.
    @returns: Validation errors for files above the hard limit.
    """

    errors: list[str] = []
    for record in collect_file_budgets(root):
        if record.estimated_tokens <= MAX_OUTER_TOOL_TOKENS:
            continue
        errors.append(
            "active text file exceeds the outer-tool budget: "
            f"{record.path.as_posix()} "
            f"({record.estimated_tokens} estimated tokens, "
            f"{record.byte_count} UTF-8 bytes, limit {MAX_OUTER_TOOL_TOKENS})"
        )
    return errors


def main(argv: list[str]) -> int:
    """Print the complete active-file ledger and fail on an oversized file."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_folder",
        nargs="?",
        default=".",
        help="Skill directory to inspect; defaults to the current directory",
    )
    args = parser.parse_args(argv[1:])
    root = Path(args.skill_folder).resolve()
    records = collect_file_budgets(root)
    for record in sorted(
        records,
        key=lambda item: (-item.estimated_tokens, item.path.as_posix()),
    ):
        print(
            f"{record.estimated_tokens:>6} tokens  "
            f"{record.byte_count:>7} bytes  {record.path.as_posix()}"
        )

    errors = validate_file_budgets(root)
    if errors:
        print("FILE BUDGET FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"FILE BUDGET PASS {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
