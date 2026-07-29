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

## 目标

[待填写：这个 Skill 为谁解决什么问题，默认交付什么结果。]

## 路由与流程

[待填写：只在这里完成路由。先按用户结果选择一条主路径和一个条件互斥的子类型，再写该类型依次读取什么、做什么、何时进入按需步骤、做到哪里停止。下层只报告不满足条件的事实并停止；只有用户改变结果或权限，或这里预先排定下一阶段时，才开启新路线。]

## 资源

[待填写：只列上面已经选定的流程会直接读取的 reference、script 或 asset，说明选择条件、使用顺序、消费者和返回位置。reference 不调用其它 reference。不需要资源时删除本节。]

## 输出与完成

[待填写：普通结果怎样直接回复，文件任务写到哪里，用户怎样看出已经完成。]
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
