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

    print(
        "quick_validate 范围回归通过：运行产物目录被忽略，活动资源空目录仍会报错"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
