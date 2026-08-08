# Contributing to Meta-skills

感谢你改进 Meta-skills。这个仓库把“用户最终能得到什么”放在实现形式之前；提交应当保留真实的用户能力和必要材料，同时允许多余的分类、路径、步骤和检查退出，并提供与改动风险相称的验证证据。

Thank you for improving Meta-skills. Contributions should preserve every supported user result, keep one active source of truth for each decision, and include verification proportionate to the change.

## Before changing files

1. Read [`AGENTS.md`](AGENTS.md) and the relevant route in [`SKILL.md`](SKILL.md).
2. Run `python scripts/quick_validate.py .` from the repository root.
3. Inventory every active capability and runtime resource affected by the change. Record its trigger, input role, output contract, producer, consumer, stopping point, observable result, and whether it stays in place or migrates intact.
4. Do not read or use `archive/` unless the task explicitly names an archived item.
5. Do not modify the protected core, `core-principles.lock.json`, validator constants, or invariant tests unless the current task explicitly authorizes a core-principle change.

## Implementation rules

- `SKILL.md` selects the main result and mutually exclusive route. References remain leaf methods and must not reroute to siblings.
- Connect the final entry point and all consumers before retiring an old path. Once migration is complete, do not retain compatibility helpers, duplicate routes, or fallback architecture.
- Keep project facts in project sources of truth, reusable Skill behavior in the appropriate Skill file, and transient diagnostic evidence in the current task.
- Add scripts, schemas, indexes, or registered assets only when a deterministic consumer genuinely needs them.
- Do not delete files without explicit approval. If an inactive file must leave the active surface, propose an archive destination first.

## Verification

Run the narrowest check that proves the public claim:

```bash
python scripts/quick_validate.py .
```

If `quick_validate.py` or its scan boundary changed, also run:

```bash
python scripts/self-test-quick-validate.py
```

For deterministic artifacts, verify the real producer, transfer or storage boundary, consumer, and user-visible result with the same produced artifact. Do not replace the chain under test with hand-written consumer data or a mock of its core behavior. Documentation-only changes stop after the relevant documentation, link, render, and repository checks pass.

## Pull request checklist

- The change solves one clearly stated user result.
- Existing capabilities and runtime resources are accounted for.
- The protected core remains unchanged unless explicitly authorized.
- Active references are still selected directly from `SKILL.md`.
- Tests and checks are listed with their actual results.
- README, licensing, and third-party notices are updated only when their public contract changed.

By contributing, you agree that your contribution is licensed under the repository's [Mozilla Public License 2.0](LICENSE), subject to the scope described in [`LICENSING.md`](LICENSING.md).
