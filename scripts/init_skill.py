#!/usr/bin/env python3
"""Initialize a behavior-first Codex/Agent Skill directory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from generate_openai_yaml import build_interface, parse_interface_overrides, write_openai_yaml


MAX_SKILL_NAME_LENGTH = 64


def normalize_skill_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return re.sub(r"-{2,}", "-", normalized).strip("-")


def title_from_name(skill_name: str) -> str:
    return " ".join(part.upper() if len(part) <= 3 else part.capitalize() for part in skill_name.split("-"))


def skill_template(skill_name: str, title: str, description: str) -> str:
    quoted_description = json.dumps(description, ensure_ascii=False)
    return f"""---
name: {skill_name}
description: {quoted_description}
---

# {title}

## 行为合同

[待填写：用户结果、默认信息真源、允许动作、按需动作和停止条件。]

## 工作流

[待填写：从第一判断到最终交付的正向步骤。]

## 资源路由

[待填写：只保留真实存在且按条件读取或运行的 references、scripts 和 assets；不需要时删除本节。]

## 交付

[待填写：第一段回答什么、后续内容顺序和用户可观察的通过标准。]
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_name", help="Skill name; normalized to kebab-case")
    parser.add_argument("--path", required=True, help="Parent directory for the new Skill")
    parser.add_argument(
        "--description",
        required=True,
        help="Final trigger description containing what the Skill does and when to use it",
    )
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="Interface field in key=value form; repeat for multiple fields",
    )
    args = parser.parse_args()

    skill_name = normalize_skill_name(args.skill_name)
    try:
        if not skill_name:
            raise ValueError("skill name must contain a letter or digit")
        if len(skill_name) > MAX_SKILL_NAME_LENGTH:
            raise ValueError(f"skill name exceeds {MAX_SKILL_NAME_LENGTH} characters")
        if not args.description.strip():
            raise ValueError("description cannot be empty")
        if len(args.description) > 1024:
            raise ValueError("description exceeds 1024 characters")
        if "<" in args.description or ">" in args.description:
            raise ValueError("description cannot contain angle brackets")
        interface_overrides = parse_interface_overrides(args.interface)
    except ValueError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    parent = Path(args.path).resolve()
    skill_dir = parent / skill_name
    if skill_dir.exists():
        print(f"FAIL: target already exists: {skill_dir}", file=sys.stderr)
        return 1

    try:
        build_interface(skill_dir, skill_name, {}, interface_overrides)
    except ValueError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        (skill_dir / "SKILL.md").write_text(
            skill_template(skill_name, title_from_name(skill_name), args.description.strip()),
            encoding="utf-8",
            newline="\n",
        )
        metadata_path = write_openai_yaml(skill_dir, skill_name, args.interface)
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"FAIL: initialization stopped at {skill_dir}: {error}", file=sys.stderr)
        return 1

    print(f"PASS {skill_dir}")
    print(f"CREATED {skill_dir / 'SKILL.md'}")
    print(f"CREATED {metadata_path}")
    print("NEXT replace every [待填写] block, add only resources with real content, then run quick_validate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
