#!/usr/bin/env python3
"""Check deterministic file structure for a Codex/Agent Skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import yaml


NAME_RE = re.compile(r"^[a-z0-9-]+$")
PATH_RE = re.compile(r"`((?:references|scripts|assets|evals)/[^`]+)`")
BACKTICK_RE = re.compile(r"`([^`\r\n]+)`")
MAX_SKILL_LINES = 220
MAX_SKILL_CHARACTERS = 14_000
ACTIVE_RESOURCE_ROOTS = ("agents", "references", "scripts", "assets", "evals")
IGNORED_RESOURCE_DIR_NAMES = {"archive", ".git", "__pycache__"}
IGNORED_DISCOVERY_DIR_NAMES = IGNORED_RESOURCE_DIR_NAMES | {
    "node_modules",
    ".venv",
    "venv",
    "output",
    "outputs",
    "artifacts",
    "dist",
    "build",
}

CORE_START = "<!-- META_SKILLS_PROTECTED_CORE_START -->"
CORE_END = "<!-- META_SKILLS_PROTECTED_CORE_END -->"
PROTECTED_CORE_SHA256 = "785d4e26ac263595817a4a784ef0c26d3eb0a999ad51b0146d6b159a2ffb5c70"
PROTECTED_CORE_TITLES = (
    "所有文本先说人话，并忠实保留用户的意思",
    "用户本意和实际结果决定范围",
    "先用最简单但完整的方法，复杂度必须证明价值",
    "改造时完整保留已有的有用能力",
    "处理路径清楚，并只由主文件决定",
    "先写正常怎样成功，再在最早位置防止问题",
    "临时教训、可复用材料和项目事实分开",
    "蒸馏和迁移同时保留共同做法与必要差异",
    "方法和核对方式跟着结果与风险走",
    "直接交付用户需要的结果，完成后停止",
)
CORE_LOCK_VERSION = 12


def parse_frontmatter(text: str) -> tuple[dict, list[str]]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        return {}, ["SKILL.md missing frontmatter"]

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        return {}, [f"SKILL.md frontmatter is invalid YAML: {error}"]
    if not isinstance(data, dict):
        return {}, ["SKILL.md frontmatter must be a mapping"]

    errors: list[str] = []
    unexpected = sorted(set(data) - {"name", "description"})
    if unexpected:
        errors.append(
            "SKILL.md frontmatter contains unsupported fields: "
            + ", ".join(unexpected)
        )
    return data, errors


def validate_main_file_budget(text: str) -> list[str]:
    errors: list[str] = []
    line_count = len(text.splitlines())
    character_count = len(text)
    if line_count > MAX_SKILL_LINES:
        errors.append(
            f"SKILL.md exceeds the main-file line budget: {line_count} > {MAX_SKILL_LINES}"
        )
    if character_count > MAX_SKILL_CHARACTERS:
        errors.append(
            "SKILL.md exceeds the main-file character budget: "
            f"{character_count} > {MAX_SKILL_CHARACTERS}"
        )
    return errors


def find_empty_dirs(root: Path) -> list[Path]:
    empty: list[Path] = []
    for resource_name in ACTIVE_RESOURCE_ROOTS:
        resource_root = root / resource_name
        if not resource_root.is_dir():
            continue
        for current, directories, files in os.walk(resource_root):
            directories[:] = [
                name for name in directories if name not in IGNORED_RESOURCE_DIR_NAMES
            ]
            if not directories and not files:
                empty.append(Path(current))
    return empty


def find_nested_skill_entrypoints(root: Path) -> list[Path]:
    nested: list[Path] = []
    root_entrypoint = root / "SKILL.md"
    for current, directories, files in os.walk(root):
        directories[:] = [
            name for name in directories if name not in IGNORED_DISCOVERY_DIR_NAMES
        ]
        if "SKILL.md" not in files:
            continue
        candidate = Path(current) / "SKILL.md"
        if candidate != root_entrypoint:
            nested.append(candidate)
    return sorted(nested)


def extract_protected_core(text: str) -> tuple[str | None, list[str]]:
    normalized = text.replace("\r\n", "\n")
    if normalized.count(CORE_START) != 1 or normalized.count(CORE_END) != 1:
        return None, ["meta-skills protected core markers must each appear exactly once"]

    before, remainder = normalized.split(CORE_START, 1)
    core, after = remainder.split(CORE_END, 1)
    if not before or not after:
        return None, ["meta-skills protected core markers cannot wrap the entire file"]
    return core.strip("\n") + "\n", []


def validate_protected_core(root: Path, text: str) -> list[str]:
    core, errors = extract_protected_core(text)
    if core is None:
        return errors

    lock_path = root / "core-principles.lock.json"
    if not lock_path.is_file():
        return errors + ["meta-skills missing core-principles.lock.json"]

    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return errors + [f"meta-skills core lock is invalid: {error}"]

    digest = hashlib.sha256(core.encode("utf-8")).hexdigest()
    lock_digest = lock.get("sha256")
    if digest != PROTECTED_CORE_SHA256:
        errors.append(
            "meta-skills protected core changed without updating its fixed fingerprint"
        )
    if lock_digest != PROTECTED_CORE_SHA256:
        errors.append("meta-skills core lock does not match the fixed fingerprint")
    if digest != lock_digest:
        errors.append("meta-skills protected core does not match core-principles.lock.json")

    titles = tuple(re.findall(r"(?m)^\d+\.\s+\*\*(.+?)。\*\*", core))
    if titles != PROTECTED_CORE_TITLES:
        errors.append("meta-skills protected core titles or order changed")
    if lock.get("principle_count") != len(PROTECTED_CORE_TITLES):
        errors.append("meta-skills core lock principle_count is incorrect")
    if lock.get("version") != CORE_LOCK_VERSION:
        errors.append("meta-skills core lock version is incorrect")
    if lock.get("change_policy") != "explicit-user-authorization-required":
        errors.append("meta-skills core lock change policy is incorrect")
    return errors


def referenced_paths(text: str) -> set[str]:
    return {
        raw.split()[0].replace("\\", "/")
        for raw in PATH_RE.findall(text)
    }


def validate_referenced_paths(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    for relative in sorted(referenced_paths(skill_text)):
        if not (root / relative).exists():
            errors.append(f"referenced path does not exist: {relative}")
    return errors


def validate_direct_reference_routes(root: Path, skill_text: str) -> list[str]:
    reference_root = root / "references"
    if not reference_root.exists():
        return []

    routed = {
        relative
        for relative in referenced_paths(skill_text)
        if relative.startswith("references/")
    }
    errors: list[str] = []
    for path in reference_root.rglob("*"):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root)
        if any(part in {"archive", "__pycache__"} for part in relative_path.parts):
            continue
        relative = relative_path.as_posix()
        if relative not in routed:
            errors.append(f"reference is not directly routed by SKILL.md: {relative}")
    return errors


def validate_reference_leaf_nodes(root: Path) -> list[str]:
    reference_root = root / "references"
    if not reference_root.exists():
        return []

    errors: list[str] = []
    for path in reference_root.rglob("*"):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root)
        if any(part in {"archive", "__pycache__"} for part in relative_path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            errors.append(
                f"cannot inspect reference routes in {relative_path.as_posix()}: {error}"
            )
            continue
        nested_routes = referenced_paths(text)
        for raw in BACKTICK_RE.findall(text):
            shorthand = raw.split()[0].replace("\\", "/").split("#", 1)[0]
            if "/" in shorthand or not shorthand.endswith(".md"):
                continue
            candidate = path.parent / shorthand
            if candidate != path and candidate.is_file():
                nested_routes.add(candidate.relative_to(root).as_posix())
        for nested in sorted(nested_routes):
            if nested.startswith("references/"):
                errors.append(
                    "reference must not route another reference; route it from SKILL.md: "
                    f"{relative_path.as_posix()} -> {nested}"
                )
    return errors


def validate_metadata(root: Path, skill_name: str) -> list[str]:
    metadata = root / "agents" / "openai.yaml"
    if not metadata.is_file():
        return ["missing agents/openai.yaml"]

    try:
        data = yaml.safe_load(metadata.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return [f"agents/openai.yaml is invalid: {error}"]
    if not isinstance(data, dict):
        return ["agents/openai.yaml must contain a mapping"]

    interface = data.get("interface")
    if not isinstance(interface, dict):
        return ["agents/openai.yaml interface must be a mapping"]

    errors: list[str] = []
    allowed_interface = {
        "display_name",
        "short_description",
        "icon_small",
        "icon_large",
        "brand_color",
        "default_prompt",
    }
    unexpected = sorted(set(interface) - allowed_interface)
    if unexpected:
        errors.append(
            "agents/openai.yaml has unsupported interface fields: "
            + ", ".join(unexpected)
        )

    for key in ("display_name", "short_description", "default_prompt"):
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"agents/openai.yaml interface.{key} is required")

    short_description = interface.get("short_description")
    if isinstance(short_description, str) and not 25 <= len(short_description) <= 64:
        errors.append("agents/openai.yaml short_description must contain 25-64 characters")

    default_prompt = interface.get("default_prompt")
    if isinstance(default_prompt, str) and f"${skill_name}" not in default_prompt:
        errors.append(f"agents/openai.yaml default_prompt must mention ${skill_name}")

    brand_color = interface.get("brand_color")
    if brand_color is not None and (
        not isinstance(brand_color, str)
        or not re.fullmatch(r"#[0-9A-Fa-f]{6}", brand_color)
    ):
        errors.append("agents/openai.yaml brand_color must use #RRGGBB")

    for key in ("icon_small", "icon_large"):
        value = interface.get(key)
        if value is None:
            continue
        if not isinstance(value, str):
            errors.append(f"agents/openai.yaml {key} must be a string path")
            continue
        target = (root / value).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            errors.append(f"agents/openai.yaml {key} must stay inside the skill directory")
            continue
        if not target.is_file():
            errors.append(f"agents/openai.yaml {key} does not exist: {value}")

    dependencies = data.get("dependencies")
    if dependencies is not None:
        if not isinstance(dependencies, dict) or not isinstance(
            dependencies.get("tools"), list
        ):
            errors.append("agents/openai.yaml dependencies.tools must be a list")
        else:
            for index, tool in enumerate(dependencies["tools"]):
                if not isinstance(tool, dict):
                    errors.append(
                        f"agents/openai.yaml dependencies.tools[{index}] must be a mapping"
                    )
                    continue
                for key in ("type", "value", "description"):
                    if not isinstance(tool.get(key), str) or not tool[key].strip():
                        errors.append(
                            f"agents/openai.yaml dependencies.tools[{index}].{key} is required"
                        )
                if tool.get("type") != "mcp":
                    errors.append(
                        f"agents/openai.yaml dependencies.tools[{index}].type must be mcp"
                    )
                for key in ("transport", "url"):
                    if key in tool and (
                        not isinstance(tool[key], str) or not tool[key].strip()
                    ):
                        errors.append(
                            f"agents/openai.yaml dependencies.tools[{index}].{key} must be a non-empty string"
                        )

    policy = data.get("policy")
    if policy is not None:
        if not isinstance(policy, dict):
            errors.append("agents/openai.yaml policy must be a mapping")
        elif "allow_implicit_invocation" in policy and not isinstance(
            policy["allow_implicit_invocation"], bool
        ):
            errors.append(
                "agents/openai.yaml policy.allow_implicit_invocation must be boolean"
            )
    return errors


def validate(root: Path) -> list[str]:
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return [f"missing {skill_path}"]

    text = skill_path.read_text(encoding="utf-8")
    errors = validate_main_file_budget(text)
    frontmatter, frontmatter_errors = parse_frontmatter(text)
    errors.extend(frontmatter_errors)

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not isinstance(name, str) or not name.strip():
        errors.append("frontmatter missing name")
        name = ""
    elif not NAME_RE.fullmatch(name):
        errors.append(f"frontmatter name is not kebab-case: {name}")
    elif name.startswith("-") or name.endswith("-") or "--" in name:
        errors.append(
            "frontmatter name cannot start/end with a hyphen or contain consecutive hyphens"
        )
    elif len(name) > 64:
        errors.append("frontmatter name exceeds 64 characters")
    elif root.name != name:
        errors.append(
            f"directory name '{root.name}' does not match frontmatter name '{name}'"
        )

    if not isinstance(description, str) or not description.strip():
        errors.append("frontmatter missing description")
    elif len(description) > 1024:
        errors.append("frontmatter description exceeds 1024 characters")
    elif "<" in description or ">" in description:
        errors.append("frontmatter description cannot contain angle brackets")

    for marker in ("[待填写", "[TODO", "TODO:"):
        if marker in text:
            errors.append(f"SKILL.md contains unfinished placeholder: {marker}")

    for nested in find_nested_skill_entrypoints(root):
        errors.append(
            "nested discoverable SKILL.md: "
            f"{nested.relative_to(root)}; keep only the root SKILL.md"
        )

    if name == "meta-skills":
        errors.extend(validate_protected_core(root, text))

    errors.extend(validate_referenced_paths(root, text))
    errors.extend(validate_direct_reference_routes(root, text))
    errors.extend(validate_reference_leaf_nodes(root))

    for empty_dir in find_empty_dirs(root):
        errors.append(f"empty directory: {empty_dir.relative_to(root)}")

    if name:
        errors.extend(validate_metadata(root, name))
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_folder",
        nargs="?",
        default=".",
        help="Skill directory to check; defaults to the current directory",
    )
    args = parser.parse_args(argv[1:])
    root = Path(args.skill_folder).resolve()
    errors = validate(root)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
