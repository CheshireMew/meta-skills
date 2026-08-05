#!/usr/bin/env python3
"""Regression checks for quick_validate activity-directory scope."""

from __future__ import annotations

import shutil
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


def write_plain_public_readme(path: Path) -> None:
    path.write_text(
        """# Meta-skills

<!-- readme-header:start -->

<p align="center">
  <strong>中文</strong> · <a href="./README.en.md">English</a> · <a href="./README.ja.md">日本語</a> | <a href="./SKILL.md">文档</a> | <a href="./CONTRIBUTING.md">贡献</a>
</p>

<p align="center">
  <a href="https://x.com/0xCheshire">X</a>
  <a href="https://t.me/CheshireBTC">Telegram</a>
  <a href="https://blog.blacknico.com/">Blog</a>
  <a href="https://blacknico.com/">Homepage</a>
</p>

<p align="center">
  <a href="https://github.com/CheshireMew/meta-skills/stargazers">Stars</a>
  <a href="https://github.com/CheshireMew/meta-skills/forks">Forks</a>
  <a href="https://github.com/CheshireMew/meta-skills/blob/main/LICENSE">License</a>
</p>

<!-- readme-header:end -->

这是一个帮助普通人创建和改进 Codex Skill 的工具。安装后，直接告诉它你想创建、检查或改进哪个 Skill。

```bash
npx skills add CheshireMew/meta-skills
```

```text
Use $meta-skills 帮我检查这个 Skill 为什么不好用，先说明问题和修改方案。
```

## Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history-dark.svg">
  <img alt="Star History" src="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history.svg">
</picture>

## 许可证

参见 [LICENSE](LICENSE)。
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

    with tempfile.TemporaryDirectory() as temporary:
        source = Path(__file__).resolve().parents[1]
        root = Path(temporary) / "meta-skills"
        shutil.copytree(
            source,
            root,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                "output",
                "outputs",
                "artifacts",
                "dist",
                "build",
            ),
        )
        write_plain_public_readme(root / "README.md")
        plain_text = (root / "README.md").read_text(encoding="utf-8")
        internal_markers = (
            "沿正式调用点冻结实际提示词输入",
            "共同机制与可叠加特殊维度分别落位",
            "只有确实复用了 fork 的独有改动才另谢 fork",
            "先把检查范围限定在本次改动及其实际消费者",
            "一张图不能同时保证完整性与可读性",
            "精确提交、推送和远端 HEAD 核对",
        )
        if any(marker in plain_text for marker in internal_markers):
            raise AssertionError("plain public README fixture contains an internal rule marker")
        errors = validate(root)
        if errors:
            raise AssertionError(
                "a plain public README must not repeat internal governance rules: "
                + " | ".join(errors)
            )

    print(
        "quick_validate 范围回归通过：活动入口会检查，运行产物会忽略，公开 README 不必复述内部规则"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
