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
REFERENCE_BACK_ROUTE_PATTERNS = (
    re.compile(
        r"(?:上层|主流程).{0,16}(?<!不)(?<!不能)(?<!不得)(?:重新选择|重选).{0,16}"
        r"(?:任务类型|成品类型|内容类型|模板|路线|流程)"
    ),
    re.compile(
        r"(?:改走|切换到|转入).{0,20}(?:其它|其他|另一|对应).{0,12}"
        r"(?:路线|流程|模板)"
    ),
)
CORE_START = "<!-- META_SKILLS_PROTECTED_CORE_START -->"
CORE_END = "<!-- META_SKILLS_PROTECTED_CORE_END -->"
PROTECTED_CORE_SHA256 = "5956101173b030e25889715829f145809c7c2966c8ee7e61f3375823b66aa4d7"
PROTECTED_CORE_TITLES = (
    "先按结果性质和失败代价选择方法",
    "用户本意和可观察结果优先",
    "有效能力按用户结果保全，不按实现细节增殖",
    "简单是默认，复杂度必须证明自己",
    "正面流程要在最早判断点解决问题",
    "验收服从结果性质和风险",
    "治理证据、创作参考和机器资源分开管理",
    "路由只保留真正改变做法的选择",
    "交付要让用户直接看见结果",
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
    if lock.get("version") != 10:
        errors.append("meta-skills core lock version is incorrect")
    if lock.get("change_policy") != "explicit-user-authorization-required":
        errors.append("meta-skills core lock change policy is incorrect")

    return errors


def validate_direct_reference_routes(root: Path, skill_text: str) -> list[str]:
    reference_root = root / "references"
    if not reference_root.exists():
        return []

    routed = {
        raw_reference.split()[0].replace("\\", "/")
        for raw_reference in REF_RE.findall(skill_text)
        if raw_reference.startswith("references/")
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
            errors.append(
                "reference is not directly routed by SKILL.md: "
                f"{relative}"
            )
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
            errors.append(f"cannot inspect reference routes in {relative_path.as_posix()}: {error}")
            continue

        nested_routes = sorted(
            {
                raw_reference.split()[0].replace("\\", "/")
                for raw_reference in REF_RE.findall(text)
                if raw_reference.startswith("references/")
            }
        )
        for nested_route in nested_routes:
            errors.append(
                "reference must not route another reference; route it from SKILL.md instead: "
                f"{relative_path.as_posix()} -> {nested_route}"
            )
        for pattern in REFERENCE_BACK_ROUTE_PATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(
                    "reference must report and stop instead of reselecting an upper route: "
                    f"{relative_path.as_posix()} -> {match.group(0)}"
                )
    return errors


def validate_meta_preservation_contract(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    required_skill_markers = (
        "### 1. 先判断结果性质和失败代价",
        "创作与开放判断",
        "确定性机器产物",
        "混合任务逐阶段选择方法",
        "### 2. 按用户结果建立改造前基线",
        "本轮处置：原位保留 / 迁移保留 / 用户明确退出",
        "创作案例与钩子只要来源清楚、能被检索并把全文交给写作上下文",
        "不要为自然语言成品建立执行记录或采用校验器",
        "reference、script 和 asset 执行已经选定的职责",
        "### 7. 按结果性质验证",
    )
    for marker in required_skill_markers:
        if marker not in skill_text:
            errors.append(f"meta-skills missing capability-preservation contract: {marker}")

    required_reference_markers = {
        "references/skill-design-playbook.md": (
            "### 改造现有 Skill 前先建立能力基线",
            "不能先断开消费者，再以资源孤立为理由移除",
            "创作时可以同时读取多个完整示范和钩子",
            "创作验证只需证明多个相关参考的全文确实一起进入上下文",
        ),
        "references/instruction-hygiene.md": (
            "约束清洗只处理同一能力内部怎样表达规则",
            "不能先删掉路由或消费者",
            "正面措辞不等于简单",
            "多个相关完整示范和钩子一起交给模型",
        ),
        "references/absorption-and-governance.md": (
            "吸收新价值不能覆盖现有价值",
            "创作与开放判断的经验",
            "为什么充分上下文、多个好例子或一条自然语言规则不足",
        ),
        "references/resource-design.md": (
            "管理边界与使用边界不同",
            "多个相关候选的全文一起放进同一写作上下文",
            "不要求逐项采用记录",
        ),
        "references/quality-gate.md": (
            "混合任务逐阶段检查",
            "多个相关完整案例、钩子或风格参考可以一起进入上下文",
            "没有固定候选数量、唯一参考、逐项采用记录、机器评分、执行记录或过程校验器",
        ),
    }
    for relative, markers in required_reference_markers.items():
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative} missing capability-preservation marker: {marker}")

    core, marker_errors = extract_protected_core(skill_text)
    errors.extend(marker_errors)
    if core is not None:
        for marker in (
            "事实、模板、案例、作者声音",
            "AI 起草的大纲或文章",
        ):
            if marker in core:
                errors.append(
                    "meta-skills protected core contains target-specific workflow wording: "
                    f"{marker}"
                )
    return errors


def validate_meta_write_confirmation_contract(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    required_skill_markers = (
        "### 5. 在写入前让用户确认实际行为",
        "是否允许写文件不在此处判断，统一由第 5 步决定",
        "凡本轮将创建、修改、移动、归档或删除任何 Skill 活动文件",
        "在首次写入前向用户一次性展示",
        "到此停止并等待用户明确确认",
        "最初的“创建”“修改”“修复”目标本身",
        "仅在第 5 步已经取得写入确认后进入本节",
    )
    for marker in required_skill_markers:
        if marker not in skill_text:
            errors.append(f"meta-skills missing write-confirmation contract: {marker}")

    forbidden_patterns = (
        re.compile(r"用户(?:已经)?说清[^\n]{0,30}直接(?:执行|修改|写入)"),
    )
    for pattern in forbidden_patterns:
        match = pattern.search(skill_text)
        if match:
            errors.append(
                "meta-skills contains a write-confirmation bypass: "
                f"{match.group(0)}"
            )

    required_reference_markers = {
        "references/skill-design-playbook.md": (
            "本节只规定确认材料的呈现形式，不判断写入权限",
            "展示后返回 `SKILL.md` 第 5 步并停止",
            "只有 `SKILL.md` 的写入确认步骤通过后才执行处置",
        ),
        "references/quality-gate.md": (
            "已经在首次写入前取得用户明确确认",
            "用户明确要求跳过确认",
        ),
    }
    for relative, markers in required_reference_markers.items():
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative} missing write-confirmation marker: {marker}")
    return errors


def validate_meta_self_evolution_contract(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    required_skill_markers = (
        "学习主体：目标 Skill / 当前项目 / 独立共享资源",
        "项目事实继续留在项目自身的真实来源",
        "不自动修改 Skill",
        "不另建项目经验区或共享经验库",
        "普通领域任务独立完成",
        "通用机制与重要特殊问题分别判断",
        "同一项经验和同一个用户结果可以同时进入两层",
        "一个结果可以同时叠加多个特殊维度",
        "不能让专项症状缩窄共同机制的适用范围",
        "没有特殊动作差异时不为形式完整虚构专项维度",
        "正在创建或改造自我进化型 Skill 时",
    )
    for marker in required_skill_markers:
        if marker not in skill_text:
            errors.append(f"meta-skills missing self-evolution contract: {marker}")

    required_file_markers = {
        "references/absorption-and-governance.md": (
            "自我进化不是把历史保存起来",
            "一段对话可以产生多项独立经验",
            "成功经验本身不是问题",
            "通用机制和重要特殊问题可以同时进入目标 Skill",
            "共同机制及其适用请求",
            "特殊条件改变的识别、观测、动作、产物、验收或停止位置",
            "两层共同消费顺序",
            "各自唯一真源和正式消费者",
            "同一个结果可以同时叠加多个特殊维度",
            "只有共同机制成立时是否没有虚构特殊维度",
            "普通领域任务与自我进化是独立结果",
        ),
        "references/skill-design-playbook.md": (
            "共同机制与特殊维度不是多个主路径",
            "由 `SKILL.md` 写清检测与共同消费顺序",
            "同一结果可以同时叠加多个维度",
        ),
        "references/instruction-hygiene.md": (
            "可叠加特殊维度",
            "不能把它们强制改成互斥分支",
            "只有共同机制成立时没有虚构特殊维度",
        ),
        "references/quality-gate.md": (
            "已确定学习主体、最终真源和正式消费者",
            "项目事实继续留在项目真源",
            "普通领域任务不会自动改写 Skill",
            "创作 Skill 的用户纠正优先变成更好的材料选择",
        ),
        "references/resource-design.md": (
            "本文件不根据内容看起来是否通用来选择学习落点",
            "资源目录不能反向把 Skill 自我进化改成项目沉淀或共享库建设",
        ),
        "references/skill-maintenance-and-evaluation.md": (
            "维护自我进化型 Skill 时",
            "普通领域任务和学习结果分开",
            "自我进化落点错误",
        ),
        "README.md": (
            "## 自我进化不是另建经验库",
            "完成当前项目任务和改变 Skill 未来行为是两个独立结果",
            "同一项经验可以同时产生共同机制和多个特殊维度",
            "共同路径不会被一个醒目的专项症状缩窄",
            "共同机制与可叠加特殊维度分别落位",
            "## 四个关键边界",
            "### 4. 学习主体决定经验落点",
        ),
    }
    for relative, markers in required_file_markers.items():
        path = root / relative
        if not path.exists():
            errors.append(f"meta-skills missing self-evolution contract file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative} missing self-evolution marker: {marker}")
    return errors


def validate_meta_diagnostic_resolution_contract(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    for marker in (
        "用户指出错误行为",
        "不能以归因或“我做错了”结束",
        "“需要修复”“无需持久修复”或“目前无法判断”",
        "正确行为、修法或不修改理由、唯一所有者、影响范围、验证方法和当前停止位置",
    ):
        if marker not in skill_text:
            errors.append(f"meta-skills missing diagnostic-resolution contract: {marker}")

    required_reference_markers = {
        "references/skill-maintenance-and-evaluation.md": (
            "### 2.1 将行为诊断收口为决定",
            "诊断不能停在责任归因",
            "规则缺失、彼此冲突、优先顺序错误",
            "问题是本次执行没有遵循规则",
            "现有证据不足以区分执行偏差和持久缺陷",
            "结论；证据与根因；正确行为；最终修法或不修改的理由；影响范围与唯一所有者；验证方式与当前停止位置",
            "不能被“我做错了”",
        ),
        "references/quality-gate.md": (
            "行为诊断已经明确落在“需要修复”“无需持久修复”或“目前无法判断”之一",
            "没有停在承认错误或责任解释",
        ),
    }
    for relative, markers in required_reference_markers.items():
        path = root / relative
        if not path.exists():
            errors.append(f"meta-skills missing diagnostic-resolution file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative} missing diagnostic-resolution marker: {marker}")
    return errors


def validate_meta_target_publication_contract(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    for marker in (
        "确认材料默认把本轮获准依赖闭包的精确提交、推送与远端核对列入完成链",
        "确认合同未选择只改本地",
        "核对远端 HEAD 后才完成",
    ):
        if marker not in skill_text:
            errors.append(f"meta-skills missing target-publication contract: {marker}")

    required_file_markers = {
        "references/skill-design-playbook.md": (
            "验证后的获准依赖闭包、精确提交、推送和远端核对",
            "提供只改本地选项",
        ),
        "references/skill-maintenance-and-evaluation.md": (
            "## 9. 完成目标 Skill 的仓库发布",
            "获准改动依赖闭包",
            "不创建远端、不改变可见性、不强制推送",
            "远端 HEAD 已核对",
        ),
        "references/quality-gate.md": (
            "提交只覆盖获准依赖闭包",
            "重新读取的远端 HEAD",
        ),
        "README.md": (
            "确认后的创建、改造或迭代默认继续完成",
            "精确提交、推送和远端 HEAD 核对",
        ),
    }
    for relative, markers in required_file_markers.items():
        path = root / relative
        if not path.exists():
            errors.append(f"meta-skills missing target-publication file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(
                    f"{relative} missing target-publication marker: {marker}"
                )
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
        errors.extend(validate_meta_preservation_contract(root, text))
        errors.extend(validate_meta_write_confirmation_contract(root, text))
        errors.extend(validate_meta_self_evolution_contract(root, text))
        errors.extend(validate_meta_diagnostic_resolution_contract(root, text))
        errors.extend(validate_meta_target_publication_contract(root, text))

    for raw_reference in sorted(set(REF_RE.findall(text))):
        relative = raw_reference.split()[0]
        target = root / relative
        if not target.exists():
            errors.append(f"referenced path does not exist: {relative}")

    for empty_dir in find_empty_dirs(root):
        errors.append(f"empty directory: {empty_dir.relative_to(root)}")

    errors.extend(validate_direct_reference_routes(root, text))
    errors.extend(validate_reference_leaf_nodes(root))

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
