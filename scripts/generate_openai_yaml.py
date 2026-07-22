#!/usr/bin/env python3
"""Generate or update the UI metadata for a Codex/Agent Skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml


INTERFACE_ORDER = (
    "display_name",
    "short_description",
    "icon_small",
    "icon_large",
    "brand_color",
    "default_prompt",
)
ALLOWED_INTERFACE_KEYS = frozenset(INTERFACE_ORDER)
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def format_display_name(skill_name: str) -> str:
    return " ".join(part.upper() if len(part) <= 3 else part.capitalize() for part in skill_name.split("-"))


def default_short_description(display_name: str) -> str:
    value = f"Create and maintain {display_name} workflows"
    if len(value) > 64:
        value = f"Create and maintain {display_name}"
    if len(value) > 64:
        value = f"{display_name[:52].rstrip()} skill helper"
    if len(value) < 25:
        value = f"{value} with reliable guidance"
    return value[:64].rstrip()


def validate_skill_name(skill_name: str) -> None:
    if not SKILL_NAME_RE.fullmatch(skill_name):
        raise ValueError("skill name must use lowercase letters, digits, and single hyphens")
    if len(skill_name) > 64:
        raise ValueError("skill name exceeds 64 characters")


def read_skill_name(skill_dir: Path) -> str:
    skill_path = skill_dir / "SKILL.md"
    if not skill_path.is_file():
        raise ValueError(f"SKILL.md not found in {skill_dir}")
    text = skill_path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md frontmatter is invalid")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict) or not isinstance(data.get("name"), str):
        raise ValueError("SKILL.md frontmatter name is missing or invalid")
    return data["name"].strip()


def parse_interface_overrides(items: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"invalid interface override '{item}'; use key=value")
        key, value = (part.strip() for part in item.split("=", 1))
        if key not in ALLOWED_INTERFACE_KEYS:
            allowed = ", ".join(INTERFACE_ORDER)
            raise ValueError(f"unknown interface field '{key}'; allowed: {allowed}")
        if not value:
            raise ValueError(f"interface field '{key}' cannot be empty")
        values[key] = value
    return values


def load_existing(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("agents/openai.yaml must contain a mapping")
    return data


def build_interface(
    skill_dir: Path,
    skill_name: str,
    existing: dict,
    overrides: dict[str, str],
) -> dict[str, str]:
    current = existing.get("interface", {})
    if current is None:
        current = {}
    if not isinstance(current, dict):
        raise ValueError("agents/openai.yaml interface must be a mapping")

    merged = {key: value for key, value in current.items() if key in ALLOWED_INTERFACE_KEYS}
    merged.update(overrides)
    for key, value in merged.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"interface field '{key}' must be a non-empty string")
    display_name = merged.get("display_name") or format_display_name(skill_name)
    short_description = merged.get("short_description") or default_short_description(display_name)
    default_prompt = merged.get("default_prompt") or f"Use ${skill_name} to complete this workflow."

    if not 25 <= len(short_description) <= 64:
        raise ValueError("short_description must contain 25-64 characters")
    if f"${skill_name}" not in default_prompt:
        raise ValueError(f"default_prompt must explicitly mention ${skill_name}")
    if "brand_color" in merged and not HEX_COLOR_RE.fullmatch(merged["brand_color"]):
        raise ValueError("brand_color must use #RRGGBB")
    for key in ("icon_small", "icon_large"):
        if key not in merged:
            continue
        target = (skill_dir / merged[key]).resolve()
        try:
            target.relative_to(skill_dir.resolve())
        except ValueError as error:
            raise ValueError(f"{key} must stay inside the skill directory") from error
        if not target.is_file():
            raise ValueError(f"{key} does not exist: {merged[key]}")

    merged.update(
        display_name=display_name,
        short_description=short_description,
        default_prompt=default_prompt,
    )
    return {key: merged[key] for key in INTERFACE_ORDER if key in merged}


def scalar(value: object) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    raise ValueError(f"unsupported YAML value: {type(value).__name__}")


def render_yaml(value: object, level: int = 0) -> list[str]:
    indent = "  " * level
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key):
                raise ValueError(f"unsupported YAML key: {key!r}")
            if isinstance(child, (dict, list)) and child:
                lines.append(f"{indent}{key}:")
                lines.extend(render_yaml(child, level + 1))
            elif isinstance(child, dict):
                lines.append(f"{indent}{key}: {{}}")
            elif isinstance(child, list):
                lines.append(f"{indent}{key}: []")
            else:
                lines.append(f"{indent}{key}: {scalar(child)}")
        return lines
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict) and item:
                first = True
                for key, child in item.items():
                    prefix = f"{indent}- " if first else f"{indent}  "
                    first = False
                    if isinstance(child, (dict, list)) and child:
                        lines.append(f"{prefix}{key}:")
                        lines.extend(render_yaml(child, level + 2))
                    elif isinstance(child, dict):
                        lines.append(f"{prefix}{key}: {{}}")
                    elif isinstance(child, list):
                        lines.append(f"{prefix}{key}: []")
                    else:
                        lines.append(f"{prefix}{key}: {scalar(child)}")
            elif isinstance(item, (dict, list)):
                lines.append(f"{indent}- {'{}' if isinstance(item, dict) else '[]'}")
            else:
                lines.append(f"{indent}- {scalar(item)}")
        return lines
    return [f"{indent}{scalar(value)}"]


def write_openai_yaml(skill_dir: Path, skill_name: str, raw_overrides: list[str]) -> Path:
    validate_skill_name(skill_name)
    output_path = skill_dir / "agents" / "openai.yaml"
    existing = load_existing(output_path)
    overrides = parse_interface_overrides(raw_overrides)
    interface = build_interface(skill_dir, skill_name, existing, overrides)

    document = {"interface": interface}
    for key, value in existing.items():
        if key != "interface":
            document[key] = value
    content = "\n".join(render_yaml(document)) + "\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", dir=output_path.parent, delete=False
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(output_path)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="Skill directory containing SKILL.md")
    parser.add_argument("--name", help="Override the name read from SKILL.md")
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="Interface field in key=value form; repeat for multiple fields",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    try:
        if not skill_dir.is_dir():
            raise ValueError(f"skill directory not found: {skill_dir}")
        skill_name = args.name or read_skill_name(skill_dir)
        output_path = write_openai_yaml(skill_dir, skill_name, args.interface)
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"PASS {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
