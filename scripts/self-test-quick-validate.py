#!/usr/bin/env python3
"""Small regression checks for quick_validate structure scope."""

from __future__ import annotations

import tempfile
from pathlib import Path

from quick_validate import validate, validate_write_confirmation_invariant


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
    flexible_confirmation = """
Before
<!-- META_SKILLS_PROTECTED_WRITE_CONFIRMATION_START -->
这段可以按照需要改写，只要受保护的确认行为没有被整段删除。
<!-- META_SKILLS_PROTECTED_WRITE_CONFIRMATION_END -->
After
"""
    if validate_write_confirmation_invariant(flexible_confirmation):
        raise AssertionError("write-confirmation protection must not lock exact wording")
    if not validate_write_confirmation_invariant("No protected confirmation section here."):
        raise AssertionError("missing write-confirmation protection was not reported")

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

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "scope-sample"
        write_minimal_skill(root)
        reference_root = root / "references"
        reference_root.mkdir()
        first = reference_root / "first.md"
        second = reference_root / "second.md"
        first.write_text("Read `second.md`.\n", encoding="utf-8")
        second.write_text("Complete the selected work.\n", encoding="utf-8")
        with (root / "SKILL.md").open("a", encoding="utf-8") as skill:
            skill.write("\nUse `references/first.md` and `references/second.md`.\n")
        errors = validate(root)
        expected = "references/first.md -> references/second.md"
        if not any(expected in error for error in errors):
            raise AssertionError(
                "bare sibling reference routes must be reported: " + " | ".join(errors)
            )

    print("quick_validate 回归通过：确认规则保护、活动结构范围和参考说明路由检查正常")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
