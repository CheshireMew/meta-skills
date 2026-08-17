# Meta-skills repository guard

These rules apply to every task in this repository.

1. The protected core and write-confirmation blocks in `SKILL.md` hold stable user control rights. Ordinary work preserves them. A user-authorized change updates the block, `core-principles.lock.json`, the matching constants in `scripts/quick_validate.py`, and their invariant tests as one change.
2. Run `python meta-skills/scripts/quick_validate.py meta-skills` before and after modifying Meta-skills. The validated core, routes and active resources form the working baseline.
3. Before changing an existing Skill, build a temporary inventory of user results, necessary materials, tools, permissions and approved decisions. Map every active implementation to preserve, replace while preserving its result, or exit when it has no independent user result.
4. Write runtime guidance as the positive behavior that produces the user result, at the single place that performs it. Failure outputs and correction history remain temporary evidence. A persistent example, template, schema, script or asset has an explicit producer, selection condition, consumer, role and stopping point.
5. `archive/` is inert storage and becomes input only when the user explicitly requests a named archived item. Active references remain leaf resources selected directly by `SKILL.md`; the main entrypoint owns result selection, shared inputs, execution order and output contracts.
