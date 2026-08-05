#!/usr/bin/env python3
"""Regression checks for quick_validate activity-directory scope."""

from __future__ import annotations

import tempfile
from pathlib import Path

from quick_validate import validate


def write_minimal_skill(root: Path) -> None:
    (root / "agents").mkdir(parents=True)
    (root / "SKILL.md").write_text(
        """---
name: scope-sample
description: Validate deterministic structure for an isolated sample skill.
---

# Scope sample

## Workflow

Validate the active skill structure and stop.
""",
        encoding="utf-8",
    )
    (root / "agents" / "openai.yaml").write_text(
        """interface:
  display_name: "Scope sample"
  short_description: "Validate active skill resources without scanning runtime outputs"
  default_prompt: "Use $scope-sample to validate this skill structure."
""",
        encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "scope-sample"
        write_minimal_skill(root)
        (root / "output" / "run" / "empty").mkdir(parents=True)
        (root / "artifacts" / "render" / "empty").mkdir(parents=True)
        errors = validate(root)
        if errors:
            raise AssertionError(
                "runtime output directories must stay outside structure validation: "
                + " | ".join(errors)
            )

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "scope-sample"
        write_minimal_skill(root)
        (root / "references" / "unused").mkdir(parents=True)
        errors = validate(root)
        expected = "empty directory: references\\unused"
        if expected not in errors and "empty directory: references/unused" not in errors:
            raise AssertionError(
                "empty active resource directory was not reported: " + " | ".join(errors)
            )

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "scope-sample"
        write_minimal_skill(root)
        nested = root / "examples" / "demo" / "SKILL.md"
        nested.parent.mkdir(parents=True)
        nested.write_text("# Demo\n", encoding="utf-8")
        errors = validate(root)
        if not any(error.startswith("nested discoverable SKILL.md:") for error in errors):
            raise AssertionError(
                "nested active SKILL.md was not reported: " + " | ".join(errors)
            )

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "scope-sample"
        write_minimal_skill(root)
        for relative in ("archive/legacy/SKILL.md", "output/run/SKILL.md"):
            ignored = root / relative
            ignored.parent.mkdir(parents=True, exist_ok=True)
            ignored.write_text("# Ignored\n", encoding="utf-8")
        errors = validate(root)
        if any(error.startswith("nested discoverable SKILL.md:") for error in errors):
            raise AssertionError(
                "inactive directories must stay outside nested entrypoint validation: "
                + " | ".join(errors)
            )

    print(
        "quick_validate 范围回归通过：活动目录中的嵌套入口会报错，归档和运行产物被忽略"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
