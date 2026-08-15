#!/usr/bin/env python3
"""Small regression checks for quick_validate structure scope."""

from __future__ import annotations

import tempfile
from pathlib import Path

from file_budget import MAX_OUTER_TOOL_TOKENS, validate_file_budgets
from quick_validate import (
    validate,
    validate_protected_core,
    validate_protected_write_confirmation,
    validate_write_confirmation_section,
)


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
    valid_confirmation = f"""
Before
<!-- META_SKILLS_PROTECTED_WRITE_CONFIRMATION_START -->
Explain the concrete change and wait for confirmation.
<!-- META_SKILLS_PROTECTED_WRITE_CONFIRMATION_END -->
After
"""
    if validate_write_confirmation_section(valid_confirmation):
        raise AssertionError("one non-empty write-confirmation section must pass")
    if not validate_write_confirmation_section("No protected confirmation section here."):
        raise AssertionError("missing write-confirmation protection was not reported")
    empty_confirmation = """
Before
<!-- META_SKILLS_PROTECTED_WRITE_CONFIRMATION_START -->
<!-- META_SKILLS_PROTECTED_WRITE_CONFIRMATION_END -->
After
"""
    if not validate_write_confirmation_section(empty_confirmation):
        raise AssertionError("empty write-confirmation protection was not reported")

    source_root = Path(__file__).resolve().parent.parent
    source_text = (source_root / "SKILL.md").read_text(encoding="utf-8")
    if validate_protected_core(source_root, source_text):
        raise AssertionError("current protected core must match its lock")
    mutated_core = source_text.replace(
        "实际交接只能有一份",
        "实际交接可以有多份",
        1,
    )
    if mutated_core == source_text:
        raise AssertionError("protected-core mutation fixture did not change the text")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "meta-skills"
        root.mkdir()
        (root / "core-principles.lock.json").write_text(
            (source_root / "core-principles.lock.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        errors = validate_protected_core(root, mutated_core)
        if not errors:
            raise AssertionError("modified AI handoff principle was not reported")

    mutated_heavy_work = source_text.replace(
        "必须在真正执行前展示具体目标",
        "可以在执行之后再展示具体目标",
        1,
    )
    if mutated_heavy_work == source_text:
        raise AssertionError("heavy-work mutation fixture did not change the text")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "meta-skills"
        root.mkdir()
        (root / "core-principles.lock.json").write_text(
            (source_root / "core-principles.lock.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        errors = validate_protected_core(root, mutated_heavy_work)
        if not errors:
            raise AssertionError("modified heavy-work principle was not reported")

    if validate_protected_write_confirmation(source_root, source_text):
        raise AssertionError("current protected write confirmation must match its lock")
    mutated_confirmation = source_text.replace(
        "任一项改变都停止写入",
        "任一项改变都可以继续写入",
        1,
    )
    if mutated_confirmation == source_text:
        raise AssertionError("write-confirmation mutation fixture did not change the text")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "meta-skills"
        root.mkdir()
        (root / "core-principles.lock.json").write_text(
            (source_root / "core-principles.lock.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        errors = validate_protected_write_confirmation(root, mutated_confirmation)
        if not errors:
            raise AssertionError("modified protected write confirmation was not reported")

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
        starter = root / "assets" / "react-starter"
        (starter / "node_modules" / ".vite-temp").mkdir(parents=True)
        (starter / "package.json").write_text("{}\n", encoding="utf-8")
        errors = validate(root)
        if errors:
            raise AssertionError(
                "ignored dependency directories must stay outside structure validation: "
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

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "scope-sample"
        write_minimal_skill(root)
        scripts = root / "scripts"
        scripts.mkdir()
        oversized = scripts / "oversized.py"
        oversized.write_text("x" * (MAX_OUTER_TOOL_TOKENS * 4 + 1), encoding="utf-8")
        errors = validate_file_budgets(root)
        if not any("scripts/oversized.py" in error for error in errors):
            raise AssertionError("oversized active text file was not reported")

        oversized.unlink()
        (scripts / "within-budget.py").write_text(
            "x" * (MAX_OUTER_TOOL_TOKENS * 4),
            encoding="utf-8",
        )
        ignored = root / "archive" / "legacy.md"
        ignored.parent.mkdir()
        ignored.write_text("x" * (MAX_OUTER_TOOL_TOKENS * 8), encoding="utf-8")
        promo = root / "assets" / "promo" / "runtime.js"
        promo.parent.mkdir(parents=True)
        promo.write_text("x" * (MAX_OUTER_TOOL_TOKENS * 8), encoding="utf-8")
        if validate_file_budgets(root):
            raise AssertionError("budget boundary or inactive resources were misclassified")

        structured_asset = root / "assets" / "catalog.json"
        structured_asset.write_text(
            "x" * (MAX_OUTER_TOOL_TOKENS * 4 + 1),
            encoding="utf-8",
        )
        errors = validate_file_budgets(root)
        if not any("assets/catalog.json" in error for error in errors):
            raise AssertionError("oversized model-readable asset was not reported")

    print("quick_validate 回归通过：确认区、活动资源、引用和文件预算检查正常")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
