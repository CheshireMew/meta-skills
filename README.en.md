# Meta-skills

<p align="center">
  <img src="./assets/readme/hero.en.svg" width="100%" alt="Meta-skills distills text, existing Skills, and repository material into runnable, verifiable capabilities for a target Skill">
</p>

<!-- readme-header:start -->

<p align="center">
  <a href="./README.md">中文</a> · <strong>English</strong> · <a href="./README.ja.md">日本語</a> | <a href="./SKILL.md">文档</a> | <a href="./CONTRIBUTING.md">贡献</a> | <a href="https://github.com/CheshireMew/meta-skills/issues">反馈</a>
</p>

<p align="center">
  <a href="https://x.com/0xCheshire" title="X"><img src="https://img.shields.io/badge/X-%400xCheshire-000000?logo=x&amp;logoColor=white" alt="X：@0xCheshire"></a>
  <a href="https://t.me/CheshireBTC" title="Telegram"><img src="https://img.shields.io/badge/Telegram-CheshireBTC-26A5E4?logo=telegram&amp;logoColor=white" alt="Telegram：CheshireBTC"></a>
  <a href="https://blog.blacknico.com/" title="Blog"><img src="https://img.shields.io/badge/Blog-blog.blacknico.com-2E7D32?logo=rss&amp;logoColor=white" alt="博客：blog.blacknico.com"></a>
  <a href="https://blacknico.com/" title="Homepage"><img src="https://img.shields.io/badge/Home-blacknico.com-1F6FEB?logo=googlechrome&amp;logoColor=white" alt="个人主页：blacknico.com"></a>
</p>

<p align="center">
  <a href="https://github.com/CheshireMew/meta-skills/stargazers"><img src="https://img.shields.io/github/stars/CheshireMew/meta-skills?style=flat" alt="GitHub Stars"></a>
  <a href="https://github.com/CheshireMew/meta-skills/forks"><img src="https://img.shields.io/github/forks/CheshireMew/meta-skills?style=flat" alt="GitHub Forks"></a>
  <a href="https://github.com/CheshireMew/meta-skills/blob/main/LICENSE"><img src="https://img.shields.io/github/license/CheshireMew/meta-skills?style=flat" alt="Repository License"></a>
</p>

<!-- readme-header:end -->

Meta-skills is a Skill-engineering meta-skill for Codex and other agent runtimes. Give it a goal, source material, or an existing Skill: it first identifies the result you actually need, preserves working capabilities, designs the final behavior, migrates the required resources, and verifies the result as far as the current environment can genuinely observe.

Use it to create, audit, rewrite, migrate, and evaluate Skills; teach a target Skill to learn from conversations only when explicitly requested; or draw traceable diagrams of control flow, data flow, resource consumption, and verification.

Before any active Skill file changes, you receive the proposed behavior, preservation inventory, representative output, and affected files for approval.

## Complete one real task first

### 1. Install

Codex discovers user Skills from `$HOME/.agents/skills`:

```bash
git clone https://github.com/CheshireMew/meta-skills.git "$HOME/.agents/skills/meta-skills"
```

Codex normally discovers the Skill automatically. If it does not appear, restart Codex and check again.

### 2. Describe the result to migrate

This request asks Meta-skills to inspect the source and target, then propose the change before writing files:

```text
Use $meta-skills to read <materials> and <target-skill>, identify the result-producing capability the target lacks, and distill the source judgments, workflow, and necessary runtime resources into it. Show me the capability inventory, migration plan, output shape, and affected files first; wait for my approval before implementing and verifying.
```

You first receive:

- the target Skill's current results and the capabilities and resources that must survive;
- what should migrate from the source and what belongs only to the current task;
- the future default behavior, conditional branches, outputs, and stopping point;
- the exact files affected and the evidence needed to show that users can consume the result.

After approval, Meta-skills connects the new entry point, migrates every active consumer, and retires the replaced path.

Structural validation proves that files and routes are coherent. When scripts, templates, or registered resources are involved, verification continues through the official producer, transfer or storage boundary, consumer, and user-visible result.

## Choose an entry point by outcome

| Outcome | Example request |
| --- | --- |
| Create a Skill from scratch | `Use $meta-skills to create <skill-name> from <goal and materials>. Show the behavior contract, directory structure, and affected files first; implement and verify after I approve.` |
| Audit an existing Skill without edits | `Use $meta-skills to audit <skill-folder>. Explain its current capabilities, main problems, and recommendations without modifying files.` |
| Rewrite, simplify, or migrate a Skill | `Use $meta-skills to refactor <skill-folder>. Inventory every active capability and runtime resource, then mark each as keep in place, migrate and preserve, or exit with an explicit reason before proposing the final design.` |
| Let a Skill learn from conversations | `Use $meta-skills to update <target-skill> so it internalizes validated lessons only when I explicitly ask it to learn; keep project facts in the project's own source of truth.` |
| Draw the full operating chain | `Use $meta-skills to read <skill-folder> and draw detailed Mermaid diagrams covering routing, producers, sources of truth, boundaries, consumers, verification loops, user results, and any unconfirmed connection.` |
| Maintain, evaluate, or synchronize a Skill | `Use $meta-skills to inspect <skill-folder> for triggering, routing, output, default activation, or source synchronization problems and verify them at the appropriate risk level.` |

These entries can be combined, but each independent result gets one main path. Completing a project task and changing how a Skill behaves in the future are separate outcomes; Meta-skills performs both only when you request both.

## From material to a runnable capability

<p align="center">
  <img src="./assets/readme/distillation-workflow.en.svg" width="100%" alt="Source material is distilled into judgment, workflow, runtime resources, and acceptance boundaries, connected to a target Skill, then verified through the official production and consumption chain">
</p>

Distillation is not summarization and not a list of generic principles. Meta-skills first identifies the user result missing from the target, reconstructs the judgment, steps, resources, and stopping point that make it work, then migrates the smallest complete capability unit that can independently produce that result.

| Boundary | What Meta-skills does |
| --- | --- |
| Preserve before refactoring | Inventory triggers, input roles, outputs, producers, consumers, and observable results. Old paths stay until the new entry is connected; compatibility layers leave after migration. |
| Separate evidence from resources | Failures, corrections, and one-off cases remain governance evidence. A template, full example, schema, script, or asset becomes a runtime resource only when the normal production path consumes it. |
| Route once at the top | `SKILL.md` selects the main result and exclusive subtype. References, scripts, and assets execute that choice without rerouting the task. |
| Match verification to risk | Contracts verify routing, research verifies facts, deterministic artifacts verify the real production chain, and external actions verify permission and outcome. Structure never masquerades as completed behavior. |

When learning from another repository or Skill, Meta-skills also traces the original upstream. Directly copied or adapted code, templates, examples, data, and assets carry their license, reuse scope, and attribution into the target project. Learning a method and implementing it independently does not turn the source into a runtime dependency.

## When to use it

Use Meta-skills when:

- the target is a Codex/Agent Skill's identity, routing, capability, resource model, verification, or maintenance;
- complete capability must move from text, a conversation, a repository, an archive, an example, or another Skill;
- you need to decide whether a Skill is too broad or too narrow, or prove that an old architecture has fully exited;
- a script, template, schema, or asset must be shown to reach a real consumer and result.

You probably do not need Meta-skills when:

- you only want to complete an ordinary domain task without changing a Skill;
- project knowledge should remain in the project and you did not ask to change future Skill behavior;
- the deliverable is a one-off content artifact rather than a reusable Skill capability.

## Maintainer entry points

Active methods are grouped by responsibility; the README does not duplicate their full rules:

- Design and prompting: [`skill-design-playbook.md`](references/skill-design-playbook.md), [`instruction-hygiene.md`](references/instruction-hygiene.md), [`openai-yaml.md`](references/openai-yaml.md)
- Learning, distillation, and resources: [`absorption-and-governance.md`](references/absorption-and-governance.md), [`evidence-distillation.md`](references/evidence-distillation.md), [`resource-design.md`](references/resource-design.md)
- Flow diagrams, maintenance, and acceptance: [`skill-flow-diagram.md`](references/skill-flow-diagram.md), [`skill-maintenance-and-evaluation.md`](references/skill-maintenance-and-evaluation.md), [`quality-gate.md`](references/quality-gate.md)

Every active reference is selected directly by [`SKILL.md`](SKILL.md). The repository includes four deterministic tools:

| Tool | Purpose |
| --- | --- |
| [`scripts/init_skill.py`](scripts/init_skill.py) | Normalize a Skill name and initialize `SKILL.md` plus `agents/openai.yaml` |
| [`scripts/generate_openai_yaml.py`](scripts/generate_openai_yaml.py) | Generate or update Codex UI metadata from the final Skill identity |
| [`scripts/quick_validate.py`](scripts/quick_validate.py) | Check frontmatter, routing, active resources, UI metadata, and deterministic invariants |
| [`scripts/self-test-quick-validate.py`](scripts/self-test-quick-validate.py) | Regression-test the validator's own scanning boundary |

Run this before and after modifying the project:

```bash
python scripts/quick_validate.py .
```

See [`AGENTS.md`](AGENTS.md) for repository rules. The protected core in `SKILL.md` is read-only by default; README work does not modify it, its lock file, or validator invariants. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the contribution workflow.

When maintaining the source elsewhere, keep this repository as the single source of truth and link it into `$HOME/.agents/skills/meta-skills` instead of maintaining a second copy. See [source synchronization](references/skill-maintenance-and-evaluation.md#8-本地默认启用与源码同步).

## Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history.svg">
  <img alt="CheshireMew/meta-skills GitHub Star History" src="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history.svg">
</picture>

## License

Original source code, Agent/Codex Skill instructions, scripts, and reusable references in this repository are licensed under the [Mozilla Public License 2.0](LICENSE).

Skills inspected, migrated, or generated for users remain under their authors' terms; third-party components and imported material retain their own licensing boundaries. See [`LICENSING.md`](LICENSING.md) and [`NOTICE`](NOTICE) for the complete scope.
