# Meta-skills

用于完整创建、改造、审计、迁移和评估 Codex/Agent Skill 的元技能。

Meta-skills 不只检查目录和 frontmatter。它先确定用户真正需要的结果、Skill 的职责与动作边界，再完成文件生成、能力迁移、结构校验和可观察行为验收。

## 能做什么

- 从零设计并初始化 Skill。
- 生成和维护 `SKILL.md` 与 `agents/openai.yaml`。
- 审计触发范围、默认流程、信息来源、动作权限和停止条件。
- 改造现有 Skill 前建立能力与运行资源台账，逐项原位保留、迁移保留或按用户要求退出，防止精简和重构顺手丢掉仍有价值的能力。
- 由 `SKILL.md` 为每个独立用户结果选择一条主路径和一个互斥子类型，再按顺序组合专项模板、共享输入、动作权限、方法强度、输出和停止条件；下层资源只执行，不再互相分流。
- 把适用的核心原则转化为目标 Skill 的具体判断、动作和验收，而不是只让 Meta-skills 自己遵守或把原则原文复制进目标文件。
- 从现有规则、项目或方法中迁移可复用能力，把纠偏材料与正常生产链持续读取的模板、完整示范、脚本和资产分开治理。
- 检查 Skill 是否职能过窄、过宽或存在多个冲突入口。
- 清洗和分级限制性提示，把有效目标改写为正向合同，只保留会实质改变权限、安全、协议或用户结果的硬边界。
- 验证脚本、引用、资产、元数据和用户最终可观察结果。
- 将持续维护的源码目录作为唯一真源接入 Codex，并按路径禁用重叠的系统 Skill。

## 安装

Codex 的用户级 Skill 目录是 `$HOME/.agents/skills`。

直接安装：

```bash
git clone https://github.com/CheshireMew/meta-skills.git "$HOME/.agents/skills/meta-skills"
```

如果需要在其它目录持续开发，保留源码仓库作为唯一真源，再建立目录联接。

Windows PowerShell：

```powershell
New-Item -ItemType Junction -Path "$HOME/.agents/skills/meta-skills" -Target "<source-folder>"
```

POSIX：

```bash
ln -s "<source-folder>" "$HOME/.agents/skills/meta-skills"
```

Codex 通常会自动发现 Skill；没有显示时重启 Codex。替代重叠系统 Skill、处理旧入口和验证源码同步的完整流程见 [`references/skill-maintenance-and-evaluation.md`](references/skill-maintenance-and-evaluation.md#8-本地默认启用与源码同步)。

## 使用

显式调用：

```text
Use $meta-skills <说明要创建、改造、审计、迁移或验证的 Skill 工作>
```

当请求与 `SKILL.md` 中的 description 匹配时，Codex 也可以隐式调用 Meta-skills。

## 工具

初始化新 Skill：

```bash
python scripts/init_skill.py <skill-name> --path <parent> --description <description> --interface display_name=<name> --interface short_description=<summary> --interface default_prompt=<prompt>
```

生成或更新 UI 元数据：

```bash
python scripts/generate_openai_yaml.py <skill-folder> --interface key=value
```

执行确定性结构检查：

```bash
python scripts/quick_validate.py <skill-folder>
```

结构检查不能代替真实行为验收。完整设计流程见 [`references/skill-design-playbook.md`](references/skill-design-playbook.md)，最终检查见 [`references/quality-gate.md`](references/quality-gate.md)。

## 目录

```text
meta-skills/
├── SKILL.md
├── agents/openai.yaml
├── core-principles.lock.json
├── references/
└── scripts/
```

`SKILL.md` 中受 `META_SKILLS_PROTECTED_CORE_START` 与 `META_SKILLS_PROTECTED_CORE_END` 包围的核心原则默认只读。只有用户在当前任务中明确要求修改核心原则时，才能同步修改核心内容、锁文件和校验不变量。

## License

本仓库目前没有添加开源许可证。公开可见不代表自动授予复制、修改或分发权限。
