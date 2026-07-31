# Meta-skills

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Meta-skills 将文本、现有 Skill 与仓库材料蒸馏为判断、流程和资源，再接入目标 Skill">
</p>

Meta-skills 是一个专门为其它 Codex/Agent Skill 蒸馏、迁移和验证能力的元技能。它最突出的作用，是从文本、现有 Skill、规则、历史对话、仓库、压缩包、文档与示例项目中，找出真正产生价值的判断、流程和实现资源，再把它们接入目标 Skill 的正式运行链路。

它也负责从零创建、审计、重写、维护和评估 Skill，包括设计能够从对话中自我进化的 Skill。整个过程先确定用户真正要得到的结果、目标 Skill 已有的能力、运行资源与动作权限，再生成或迁移文件；完成后不只检查目录和 frontmatter，还会按任务风险验证到当前真实链路的可观察终点。当前没有真实下游时，它会明确说明只验证到了结构可达。

## 核心特色：把材料蒸馏成可运行能力

Meta-skills 所说的“蒸馏”不是给材料写摘要，也不是抽出几条放进任何 Skill 都差不多的通用原则。它先确定目标 Skill 缺少什么结果能力，再从来源材料中还原这项能力为什么有效、怎样执行、依赖什么资源，最后迁移能够独立产生结果的最小完整能力单元。

<p align="center">
  <img src="./assets/readme/distillation-workflow.svg" width="100%" alt="文本、现有 Skill、仓库和经验经过能力缺口判断，蒸馏为专业判断、操作流程、运行资源与验收边界，再接入目标 Skill 并通过正式生产者和消费者形成用户可见结果">
</p>

实际迁移内容会按价值因果链决定，可能包括触发条件、判断标准、步骤、输出合同、停止位置，以及生产需要的模板、完整示范、schema、脚本或资产。来源中的一次性人物、事实、数字、措辞、失败记录和纠偏过程不会被误升为长期默认；目标 Skill 原有的有效能力也会先进入台账并得到保全，蒸馏新能力不能覆盖旧能力。

这条链路分别由 [`references/absorption-and-governance.md`](references/absorption-and-governance.md)、[`references/evidence-distillation.md`](references/evidence-distillation.md) 和 [`references/resource-design.md`](references/resource-design.md) 负责识别可迁移价值、提炼完整能力单元并连接运行资源。

## 自我进化不是另建经验库

当用户要求一个 Skill 从对话中学习时，Meta-skills 会先确定“谁在学习、学完改变什么行为、最终写到哪里、以后由谁读取”。如果学习主体是目标 Skill，经过验证的经验会进入它自己的活动规则、方法、资源合同、脚本、元数据或确定性检查，使它下次处理同类请求时真正换一种判断或做法。当前项目的事实仍由项目自己的代码、测试和文档负责。

完成当前项目任务和改变 Skill 未来行为是两个独立结果。用户同时要求时，先验证项目结果，再迭代目标 Skill；只要求项目任务时不会自动修改 Skill。独立的项目经验区或共享经验库只有在用户明确把它列为结果，并且确实存在持续消费者时才会建立。

一段对话可以包含多项成功经验、失败、纠偏和稳定约束，它们会按性质分别处理，而不是被压成一条问题记录。每项经验分别说明表现或价值、成立机制或根因、采取的动作、验证结果、容易重复的坑和未来最早的预防点。高频、严重、容易误诊或只在特定条件下出现的问题会保留足以识别和治理它的细节，不会为了追求宽泛的通用规则而被抽空。

## 一分钟开始

Codex 的用户级 Skill 目录是 `$HOME/.agents/skills`。直接安装：

```bash
git clone https://github.com/CheshireMew/meta-skills.git "$HOME/.agents/skills/meta-skills"
```

Codex 通常会自动发现 Skill；列表中没有出现时，重启 Codex 后再检查。

把一组材料蒸馏给目标 Skill：

```text
Use $meta-skills 读取 <materials> 和 <target-skill>，先找出目标 Skill 的能力缺口，再把材料中的判断、流程与必要运行资源蒸馏并迁移进去。先展示能力台账、迁移方案、输出骨架和将修改的文件，等我确认后实施。
```

让一个 Skill 获得或改进自我进化能力：

```text
Use $meta-skills 改造 <target-skill>，让它在我明确要求学习时，从当前对话的成功经验、失败、纠偏和项目结果中提炼多项经验，并内化到自身会被未来请求读取的行为；项目事实继续留在项目真源，不另建未经要求的经验库。先展示学习落点、行为合同和影响文件，等我确认后实施并验证。
```

创建一个新 Skill：

```text
Use $meta-skills 根据 <目标与材料> 创建 <skill-name>。先确定触发边界、默认流程、输出合同和必要运行资源，展示行为合同、目录结构与将创建的文件，等我确认后实施并验证。
```

改造或迁移一个现有 Skill：

```text
Use $meta-skills 改造 <skill-folder>，先盘点全部活动能力与运行资源，说明哪些原位保留、哪些迁移保留，以及新的行为合同、实施方案和将修改的文件，等我确认后实施并验证。
```

只读审计一个现有 Skill：

```text
Use $meta-skills 审计 <skill-folder>，说明现有能力、主要问题和建议，不修改文件。
```

Meta-skills 对 Skill 活动文件的创建、修改、移动、归档和删除都采用这个确认边界：先把实际行为方案讲清楚，再等待明确批准。纯分析、审计和答疑会直接交付结论，不为了输出报告额外写文件。

当请求与 [`SKILL.md`](SKILL.md) 中的 description 匹配，并且调用策略没有关闭隐式调用时，Codex 也可以自动选择 Meta-skills。

## 它怎样工作

```text
用户请求
   │
   ├─ 从材料或现有 Skill 蒸馏并迁移能力
   ├─ 创建或改进能从对话中自我进化的 Skill
   ├─ 新建、重写、更新或审计 Skill
   └─ 维护、评估、分发、默认启用或源码同步
                      ↓
        行为合同；修改现有 Skill 时同时建立
          活动能力与运行资源的改造前台账
                      ↓
        为每个独立结果选择唯一主路径
        再叠加来源、权限、强度与停止条件
                      ↓
       只读任务直接交付｜写入任务等待确认
                      ↓
          实现 → 结构检查 → 真实行为验收
                      ↓
                 用户可见结果
```

这里的“行为合同”不是额外文档，而是当前任务中的实施依据：什么请求触发、读取什么、允许做什么、默认怎样完成、何时进入按需分支、交付什么以及在哪里停止。任务结束后，它不会作为一次性过程材料写回 Skill。

## 能做什么

- **蒸馏并迁移完整能力**：从文本、现有 Skill、成功经验、纠偏、旧规则、历史对话、仓库或大量外部材料中，提炼目标 Skill 真正缺少的用户价值、操作结构与实现载体；输出是能够进入正式生产链的完整能力，不是材料摘要。
- **设计自我进化型 Skill**：先确定学习主体、最终真源和正式消费者，再把多项成功或失败经验转成目标 Skill 自身会执行的判断、动作和验收；普通项目任务不会自动触发 Skill 修改。
- **从零创建 Skill**：确定名称、触发边界、主流程和界面文案，初始化 `SKILL.md` 与 `agents/openai.yaml`，只在确有正式消费者时增加 references、scripts 或 assets。
- **审计、重写和迁移现有 Skill**：先盘点每项活动能力与运行资源，判断职责是否过窄、过宽或存在冲突入口，再逐项原位保留、迁移保留或按用户明确要求退出，避免重构后只剩一条新流程，旧能力却悄悄消失。
- **收敛路由与动作边界**：由顶层 `SKILL.md` 一次选择主路径和互斥子类型；下层 reference、script 与 asset 只执行已经选定的职责，不反向改路线。
- **把原则落实为目标行为**：区分哪些原则只约束当前设计与验收，哪些会改变目标 Skill 的长期行为；后者会被转换成具体判断、动作、产物和停止条件，而不是把原则名称原样复制过去。
- **设计运行资源**：为模板、完整示范、schema、脚本、资产和索引确定生产者、唯一真源、选择条件、正式消费者、注册状态与停止位置。
- **清洗提示词**：先建立能够独立完成正常请求的正向流程，再把限制性内容分成删除、正向改写、条件边界和少量真正必要的硬禁止。
- **维护与评估**：处理触发偏差、流程未执行、路由冲突、输出不稳定、默认启用、源码同步以及与系统 Skill 重叠等问题。
- **验证最终行为**：结构检查之外，按实际风险追踪生产者、文件或存储边界、消费者和最终可见结果；不会用消费端手写假数据冒充正在验证的正式产物。

## 四个关键边界

### 1. 先保全能力，再谈精简

优化现有 Skill 前，Meta-skills 会为每项能力和资源记录触发请求、输入职责、输出合同、生产者、消费者、停止位置与可观察结果。只有这些方面全部等价，才能判定两项实现重复；新链路没有接通并验证前，旧入口不能提前退出。

### 2. 治理证据不等于运行资源

失败输出、纠偏故事、临时提示词和本次核对材料只用于当前任务。模板、完整示范、schema、脚本或资产只有在来源与使用条件明确、具有稳定标识和版本、进入活动索引，并由正式消费者持续读取后，才成为已注册运行资源。资源可以被显式选择，也不代表它自动成为默认。

### 3. 结构通过不等于行为完成

`quick_validate.py` 能证明目录、元数据、引用和确定性不变量成立，但不能证明用户结果真的产生。涉及脚本、模板、文件或注册资源时，Meta-skills 会在当前任务具备真实下游的范围内，继续检查正式产物是否被下一步读取和使用；如果只能证明结构可达，也会明确停在哪一层。

### 4. 学习主体决定经验落点

目标 Skill 自我进化、当前项目沉淀和独立共享资源是三种不同结果。Meta-skills 会在设计资源前先确定其中哪一种成立：目标 Skill 学习时直接改变它自身的活动行为；项目沉淀停在项目真源；共享资源需要用户明确要求和独立消费者。名称里出现“项目经验”或内容看起来可以通用，都不能替代这个判断。

## 自带工具

这些脚本都使用 Python 3 和 PyYAML。当前环境缺少 `yaml` 模块时，可在所使用的 Python 环境中安装 `PyYAML`。

| 工具 | 作用 |
| --- | --- |
| [`scripts/init_skill.py`](scripts/init_skill.py) | 把名称规范为小写连字符格式（kebab-case），创建新的 Skill 目录；目标已存在时停止，只生成 `SKILL.md` 与 `agents/openai.yaml` |
| [`scripts/generate_openai_yaml.py`](scripts/generate_openai_yaml.py) | 从最终 Skill 定位生成或更新界面元数据，同时保留已有 `dependencies` 与 `policy` |
| [`scripts/quick_validate.py`](scripts/quick_validate.py) | 检查 frontmatter、路径、顶层路由、reference 叶节点、空目录、UI 元数据、Meta-skills 受保护核心和自我进化学习落点合同 |

初始化新 Skill：

```bash
python scripts/init_skill.py my-skill --path <parent> --description "<trigger description>" --interface "display_name=My Skill" --interface "short_description=Create and maintain a reliable workflow" --interface 'default_prompt=Use $my-skill to complete this workflow.'
```

生成或更新 UI 元数据：

```bash
python scripts/generate_openai_yaml.py <skill-folder> --interface "display_name=My Skill" --interface "short_description=Create and maintain a reliable workflow" --interface 'default_prompt=Use $my-skill to complete this workflow.'
```

执行确定性结构检查：

```bash
python scripts/quick_validate.py <skill-folder>
```

## 方法与资料

- [`SKILL.md`](SKILL.md) 是唯一的顶层路由、动作权限、默认输出和停止条件真源。
- [`references/skill-design-playbook.md`](references/skill-design-playbook.md) 负责新建、重写、更新和审计时的行为合同、职能边界与实施方法。
- [`references/instruction-hygiene.md`](references/instruction-hygiene.md) 负责建立正向流程并清洗限制性提示。
- [`references/absorption-and-governance.md`](references/absorption-and-governance.md) 负责确定学习主体与经验落点，并从多项成功经验、失败、纠偏、旧规则和外部方法中吸收可迁移能力。
- [`references/evidence-distillation.md`](references/evidence-distillation.md) 负责从仓库、压缩包和大量资料中提炼完整能力单元。
- [`references/resource-design.md`](references/resource-design.md) 负责模板、完整示范、schema、脚本、资产与索引的身份、生命周期和消费链。
- [`references/skill-maintenance-and-evaluation.md`](references/skill-maintenance-and-evaluation.md) 负责维护、评估、分发、默认启用和源码同步。
- [`references/openai-yaml.md`](references/openai-yaml.md) 定义 `agents/openai.yaml` 的界面字段、依赖和调用策略。
- [`references/quality-gate.md`](references/quality-gate.md) 是交付前的行为、资源、结构和用户结果检查清单。

所有正在使用的 reference 都由 `SKILL.md` 直接选择。reference 之间不互相调用，也不重新选择任务类型或覆盖顶层输出合同。

## 目录

```text
meta-skills/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── readme/
│       ├── hero.svg
│       └── distillation-workflow.svg
├── references/
│   ├── skill-design-playbook.md
│   ├── instruction-hygiene.md
│   ├── absorption-and-governance.md
│   ├── evidence-distillation.md
│   ├── resource-design.md
│   ├── skill-maintenance-and-evaluation.md
│   ├── openai-yaml.md
│   └── quality-gate.md
├── scripts/
│   ├── init_skill.py
│   ├── generate_openai_yaml.py
│   └── quick_validate.py
├── core-principles.lock.json
├── AGENTS.md
├── LICENSING.md
├── NOTICE
└── LICENSE
```

## 持续开发与源码同步

如果你在其它目录持续维护 Meta-skills，应当把源码仓库保留为唯一真源，再从 Codex 的用户级 Skill 目录建立联接，不要维护第二份副本。

Windows PowerShell：

```powershell
New-Item -ItemType Junction -Path "$HOME/.agents/skills/meta-skills" -Target "<source-folder>"
```

POSIX：

```bash
ln -s "<source-folder>" "$HOME/.agents/skills/meta-skills"
```

建立联接前先确认目标位置没有同名目录或错误联接；需要移走或删除旧入口时，先取得相应许可。替代重叠系统 Skill、按真实路径禁用旧入口以及验证源码同步的完整流程见 [`references/skill-maintenance-and-evaluation.md`](references/skill-maintenance-and-evaluation.md#8-本地默认启用与源码同步)。

## 修改本项目

修改 Meta-skills 前后都运行：

```bash
python scripts/quick_validate.py .
```

还需要遵守 [`AGENTS.md`](AGENTS.md) 中的仓库规则：

- `SKILL.md` 中 `META_SKILLS_PROTECTED_CORE_START` 与 `META_SKILLS_PROTECTED_CORE_END` 之间的核心原则默认只读。只有用户在当前任务中明确要求修改核心原则，才同步修改核心内容、`core-principles.lock.json` 和校验器不变量。
- 优化、精简、重构、迁移或审计前，先盘点全部活动能力与运行资源，并为每项确定原位保留、迁移保留或用户明确退出。
- 所有分流都留在 `SKILL.md`；正在使用的 reference 保持为叶节点。
- 结构检查和真实行为验收分别记录，不能用其中一个代替另一个。

## 许可证

本仓库原创的源代码、Agent/Codex Skill 指令、脚本和可复用 reference 文档采用 [Mozilla Public License 2.0](LICENSE)。Meta-skills 检查、迁移或生成的用户 Skill 继续受其作者自己的条款约束；第三方组件与引入内容也保留各自的授权边界。完整范围见 [`LICENSING.md`](LICENSING.md) 和 [`NOTICE`](NOTICE)。
