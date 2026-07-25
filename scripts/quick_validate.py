#!/usr/bin/env python3
"""Deterministic structure checks for Codex/Agent skills."""

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
REF_RE = re.compile(r"`((?:references|scripts|assets|evals)/[^`]+)`")
CORE_START = "<!-- META_SKILLS_PROTECTED_CORE_START -->"
CORE_END = "<!-- META_SKILLS_PROTECTED_CORE_END -->"
PROTECTED_CORE_SHA256 = "3c4a3c54bfddcbb927c1cd925881998c600d2e6162b9b3c33116957d7448d2dc"
PROTECTED_CORE_TITLES = (
    "正面流程必须独立成立",
    "预防大于治理",
    "先验收行为，再验收文件",
    "用户本意优先",
    "案例只作临时证据",
    "默认与按需分开",
    "边界是设计的一部分",
    "说人话要可验收",
    "唯一真源",
    "禁止案例衍生的默认方案",
    "验收强度与风险匹配",
    "案例与长期规则严格隔离",
)
FORBIDDEN_META_PATHS = (
    "references/regression-samples.md",
    "references/behavior-harness.md",
    "evals",
    "scripts/run_harness.py",
    "scripts/test_run_harness.py",
)
FORBIDDEN_META_ROUTES = (
    "regression-samples.md",
    "behavior-harness.md",
    "evals/cases.json",
    "run_harness.py",
    "test_run_harness.py",
)
ALLOWED_META_FILES = frozenset(
    {
        "SKILL.md",
        ".gitignore",
        "AGENTS.md",
        "README.md",
        "core-principles.lock.json",
        "agents/openai.yaml",
        "references/absorption-and-governance.md",
        "references/evidence-distillation.md",
        "references/instruction-hygiene.md",
        "references/openai-yaml.md",
        "references/quality-gate.md",
        "references/skill-design-playbook.md",
        "references/skill-maintenance-and-evaluation.md",
        "scripts/generate_openai_yaml.py",
        "scripts/init_skill.py",
        "scripts/quick_validate.py",
    }
)
REQUIRED_INSTRUCTION_HYGIENE_ROUTES = (
    "references/instruction-hygiene.md",
    "### 4. 清洗与分级约束",
    "删除是默认等级，候选规则承担保留依据的举证责任",
    "#### 硬禁止保留门槛",
    "确认正向合同仍能独立驱动正常请求完成并产出可观察结果",
)
REQUIRED_CAPABILITY_MIGRATION_ROUTES = (
    "逐项处置矩阵：迁移保留、明确退出、需要确认",
    "退出对象内部承载的独立能力、资源与消费者",
    "文件共置、同一模块或同一调用栈只说明实现位置相邻",
    "目标对象已经退出",
)
REQUIRED_AUDIENCE_LANGUAGE_ROUTES = (
    "### 4.1 分开证据语言、工作语言与用户语言",
    "来源中的术语、README 说法、字段名和实现动词先作为证据保存",
    "准确核实只证明信息可用，不自动赋予它正文篇幅",
    "内部字段名和过程标签到达最终消费者前要改写成用户能直接理解的内容",
)


def parse_frontmatter(text: str) -> tuple[dict, list[str]]:
    errors: list[str] = []
    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        return {}, ["SKILL.md missing frontmatter"]
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        return {}, [f"SKILL.md frontmatter is invalid YAML: {error}"]
    if not isinstance(data, dict):
        return {}, ["SKILL.md frontmatter must be a mapping"]

    unexpected = sorted(set(data) - {"name", "description"})
    if unexpected:
        errors.append(
            "SKILL.md frontmatter contains unsupported fields: " + ", ".join(unexpected)
        )
    return data, errors


def active_files(root: Path):
    for current, directories, files in os.walk(root):
        directories[:] = [
            name for name in directories if name not in {"archive", ".git", "__pycache__"}
        ]
        current_path = Path(current)
        for name in files:
            yield current_path / name


def find_empty_dirs(root: Path) -> list[Path]:
    empty: list[Path] = []
    for current, directories, files in os.walk(root):
        directories[:] = [
            name for name in directories if name not in {"archive", ".git", "__pycache__"}
        ]
        path = Path(current)
        if path != root and not directories and not files:
            empty.append(path)
    return empty


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
    errors: list[str] = []
    core, marker_errors = extract_protected_core(text)
    errors.extend(marker_errors)
    if core is None:
        return errors

    lock_path = root / "core-principles.lock.json"
    if not lock_path.exists():
        return ["meta-skills missing core-principles.lock.json"]

    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"meta-skills core lock is invalid: {error}"]

    digest = hashlib.sha256(core.encode("utf-8")).hexdigest()
    lock_digest = lock.get("sha256")
    if digest != PROTECTED_CORE_SHA256:
        errors.append("meta-skills protected core changed without updating its validator invariant")
    if lock_digest != PROTECTED_CORE_SHA256:
        errors.append("meta-skills core lock does not match the validator invariant")
    if digest != lock_digest:
        errors.append("meta-skills protected core fingerprint does not match core-principles.lock.json")

    titles = tuple(re.findall(r"(?m)^\d+\.\s+\*\*(.+?)。\*\*", core))
    if titles != PROTECTED_CORE_TITLES:
        errors.append("meta-skills protected core titles or order changed")
    if lock.get("principle_count") != len(PROTECTED_CORE_TITLES):
        errors.append("meta-skills core lock principle_count is incorrect")
    if lock.get("version") != 2:
        errors.append("meta-skills core lock version is incorrect")
    if lock.get("change_policy") != "explicit-user-authorization-required":
        errors.append("meta-skills core lock change policy is incorrect")

    return errors


def validate_case_isolation(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []

    for path in active_files(root):
        relative = path.relative_to(root)
        normalized_relative = relative.as_posix()
        if normalized_relative not in ALLOWED_META_FILES:
            errors.append(
                "meta-skills unreviewed active file is not allowed: "
                f"{normalized_relative}"
            )

    for relative in FORBIDDEN_META_PATHS:
        if (root / relative).exists():
            errors.append(f"meta-skills forbidden persistent case asset exists: {relative}")

    for sibling_name in ("harness-results", "harness-workspaces"):
        if (root.parent / sibling_name).exists():
            errors.append(
                f"meta-skills forbidden persistent case output exists: ../{sibling_name}"
            )

    routed_texts: list[tuple[str, str]] = [("SKILL.md", skill_text)]
    for folder in (root / "references", root / "agents"):
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".json"}:
                routed_texts.append(
                    (str(path.relative_to(root)), path.read_text(encoding="utf-8"))
                )

    for label, routed_text in routed_texts:
        normalized = routed_text.replace("\\", "/")
        for route in FORBIDDEN_META_ROUTES:
            if route in normalized:
                errors.append(
                    f"meta-skills forbidden persistent case route in {label}: {route}"
                )

    return errors


def validate_instruction_hygiene_route(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    for marker in REQUIRED_INSTRUCTION_HYGIENE_ROUTES:
        if marker not in skill_text:
            errors.append(f"meta-skills missing instruction hygiene route: {marker}")

    reference = root / "references" / "instruction-hygiene.md"
    if reference.exists():
        text = reference.read_text(encoding="utf-8")
        for heading in ("## 一、先写正向合同", "## 三、四级处理", "## 五、验收"):
            if heading not in text:
                errors.append(f"instruction hygiene reference missing section: {heading}")
    return errors


def validate_capability_migration_route(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    for marker in REQUIRED_CAPABILITY_MIGRATION_ROUTES:
        if marker not in skill_text:
            errors.append(f"meta-skills missing capability migration route: {marker}")

    absorption = root / "references" / "absorption-and-governance.md"
    if absorption.exists():
        text = absorption.read_text(encoding="utf-8")
        for marker in (
            "### 4.1 退出载体时的处置矩阵",
            "正式生产者：",
            "正式消费者：",
            "明确退出项不进入新的生产链路",
        ):
            if marker not in text:
                errors.append(f"capability migration reference missing marker: {marker}")
    return errors


def validate_audience_language_route(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    for marker in REQUIRED_AUDIENCE_LANGUAGE_ROUTES:
        if marker not in skill_text:
            errors.append(f"meta-skills missing audience language route: {marker}")

    references = {
        "references/skill-design-playbook.md": (
            "来源语言：",
            "内部工作语言：",
            "最终用户语言：",
            "不建立禁词表，也不触发自动返修",
        ),
        "references/instruction-hygiene.md": (
            "来源语言、内部工作语言还是最终用户语言",
            "不会直接替代用户成品语言",
            "案例库可以继续提供完整案例以及结构、节奏和表达机制",
        ),
        "references/quality-gate.md": (
            "来源语言、内部工作语言和最终用户语言已经分开",
            "没有只做表面同义词替换",
        ),
    }
    for relative, markers in references.items():
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative} missing audience language marker: {marker}")
    return errors


def validate_metadata(root: Path, skill_name: str) -> list[str]:
    errors: list[str] = []
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
        errors.append("agents/openai.yaml has unsupported interface fields: " + ", ".join(unexpected))

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
        if not isinstance(dependencies, dict) or not isinstance(dependencies.get("tools"), list):
            errors.append("agents/openai.yaml dependencies.tools must be a list")
        else:
            for index, tool in enumerate(dependencies["tools"]):
                if not isinstance(tool, dict):
                    errors.append(f"agents/openai.yaml dependencies.tools[{index}] must be a mapping")
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
            errors.append("agents/openai.yaml policy.allow_implicit_invocation must be boolean")

    metadata_text = metadata.read_text(encoding="utf-8")
    behavior_markers = ("## 工作流", "## 核心原则", "references/", "scripts/", "assets/")
    for marker in behavior_markers:
        if marker in metadata_text:
            errors.append(f"agents/openai.yaml appears to contain behavior rule marker: {marker}")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        return [f"missing {skill_path}"]

    text = skill_path.read_text(encoding="utf-8")
    fm, fm_errors = parse_frontmatter(text)
    errors.extend(fm_errors)

    name = fm.get("name", "")
    description = fm.get("description", "")
    if not isinstance(name, str) or not name.strip():
        errors.append("frontmatter missing name")
        name = ""
    elif not NAME_RE.fullmatch(name):
        errors.append(f"frontmatter name is not kebab-case: {name}")
    elif name.startswith("-") or name.endswith("-") or "--" in name:
        errors.append("frontmatter name cannot start/end with a hyphen or contain consecutive hyphens")
    elif len(name) > 64:
        errors.append("frontmatter name exceeds 64 characters")
    elif root.name != name:
        errors.append(f"directory name '{root.name}' does not match frontmatter name '{name}'")

    if not isinstance(description, str) or not description.strip():
        errors.append("frontmatter missing description")
    elif len(description) > 1024:
        errors.append("frontmatter description exceeds 1024 characters")
    elif "<" in description or ">" in description:
        errors.append("frontmatter description cannot contain angle brackets")

    for marker in ("[待填写", "[TODO", "TODO:"):
        if marker in text:
            errors.append(f"SKILL.md contains unfinished placeholder: {marker}")

    if name == "meta-skills":
        errors.extend(validate_protected_core(root, text))
        errors.extend(validate_case_isolation(root, text))
        errors.extend(validate_instruction_hygiene_route(root, text))
        errors.extend(validate_capability_migration_route(root, text))
        errors.extend(validate_audience_language_route(root, text))

    for raw_reference in sorted(set(REF_RE.findall(text))):
        relative = raw_reference.split()[0]
        target = root / relative
        if not target.exists():
            errors.append(f"referenced path does not exist: {relative}")

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
        help="Skill directory to validate; defaults to the current directory",
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
