# Meta-skills

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Meta-skills 将文本、现有 Skill 与仓库材料蒸馏为可运行、可验证的目标 Skill 能力">
</p>

<!-- readme-header:start -->

<p align="center">
  <strong>中文</strong> · <a href="./README.en.md">English</a> · <a href="./README.ja.md">日本語</a> | <a href="./SKILL.md">文档</a> | <a href="./CONTRIBUTING.md">贡献</a> | <a href="https://github.com/CheshireMew/meta-skills/issues">反馈</a>
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

Meta-skills 是给 Codex/Agent 使用的一套 Skill 工程元技能。把目标、材料或现有 Skill 交给它，它会先确认你真正要得到的结果，再保全已有能力、设计最终行为、迁移必要资源，并按风险验证到当前能够观察的终点。

它适合创建、审计、重写、迁移和评估 Skill，也能让目标 Skill 在你明确要求时从对话中学习，或把控制流、数据流、资源消费和验证闭环画成可追溯的流程图。写入前，你会先看到行为方案、保全台账、代表性输出和影响文件；确认后才会修改活动文件。

## 先完成一次真实任务

### 1. 安装

Codex 的用户级 Skill 目录是 `$HOME/.agents/skills`：

```bash
git clone https://github.com/CheshireMew/meta-skills.git "$HOME/.agents/skills/meta-skills"
```

Codex 通常会自动发现 Skill；如果列表中没有出现，重启 Codex 后再检查。

### 2. 直接描述要迁移的结果

下面这条请求会让 Meta-skills 读取材料和目标 Skill，先交付方案，不立即改文件：

```text
Use $meta-skills 读取 <materials> 和 <target-skill>，找出目标 Skill 缺少的结果能力，把材料中真正产生结果的判断、流程与必要运行资源蒸馏进去。先展示能力台账、迁移方案、输出骨架和影响文件，等我确认后实施并验证。
```

你会先看到：

- 目标 Skill 当前能完成什么，哪些能力和资源必须保留；
- 来源材料中哪些内容值得迁移，哪些只应留在当前任务；
- 未来默认行为、按需分支、输出与停止位置；
- 将修改哪些文件，以及怎样验证用户最终能用到结果。

确认方案后，Meta-skills 才会接通新入口、迁移调用点并退出被替代的旧路径。结构校验只证明文件和路由成立；涉及脚本、模板或注册资源时，它还会沿正式生产者、传输或存储边界、消费者和用户可见结果继续验证。

目标 Skill 位于已有 Git 远端仓库时，确认后的创建、改造或迭代默认继续完成本轮获准改动的验证、精确提交、推送和远端 HEAD 核对。你可以在确认方案时明确选择只改本地；这条默认也不会创建远端、改变可见性、强制推送或夹带其它工作区修改。

## 按你要的结果选择入口

| 你要完成什么 | 可以这样说 |
| --- | --- |
| 从零创建 Skill | `Use $meta-skills 根据 <目标与材料> 创建 <skill-name>，先给出行为合同、目录结构和影响文件，等我确认后实施并验证。` |
| 只读审计现有 Skill | `Use $meta-skills 审计 <skill-folder>，说明现有能力、主要问题和建议，不修改文件。` |
| 重写、精简或迁移 Skill | `Use $meta-skills 改造 <skill-folder>，先盘点全部活动能力与运行资源，逐项说明原位保留、迁移保留或退出依据，再给出最终方案。` |
| 让 Skill 从对话中学习 | `Use $meta-skills 改造 <target-skill>，让它只在我明确要求学习时，把经过验证的经验内化到未来会读取的活动行为；项目事实继续留在项目真源。` |
| 画出完整运行链路 | `Use $meta-skills 读取 <skill-folder>，画出路由、生产者、真源、边界、消费者、验证回路和用户结果的详细 Mermaid 图，并标出未确认连接。` |
| 维护、评估或同步 Skill | `Use $meta-skills 检查 <skill-folder> 的触发、路由、输出、默认启用或源码同步问题，并按当前风险给出验证结果。` |

这些入口可以组合，但每个独立结果只保留一条主路径。普通项目任务和“让 Skill 学会以后怎么做”是两个结果；只有你同时要求时，Meta-skills 才会先完成项目结果，再改造目标 Skill。

流程图可以表达当前状态、拟议状态或实施后状态。需要详细流程与链路图时，如果一张图不能同时保证完整性与可读性，Meta-skills 会拆成一张总览和必要的局部详图，并把关键节点映射回活动真源。

## 从材料到可运行能力

<p align="center">
  <img src="./assets/readme/distillation-workflow.svg" width="100%" alt="材料经过能力缺口判断，被蒸馏为判断、流程、运行资源和验收边界，再接入目标 Skill 并沿正式生产消费链验证">
</p>

“蒸馏”不是摘要材料，也不是复制几条看似通用的原则。Meta-skills 会先确定目标缺少的用户结果，再还原这项结果依赖的判断、步骤、资源与停止位置，最后迁移能够独立产生结果的最小完整能力单元。

## 自我进化不是另建经验库

完成当前项目任务和改变 Skill 未来行为是两个独立结果。学习主体是目标 Skill 时，经过验证的经验会进入它自己的活动规则、方法、资源合同、脚本、元数据或确定性检查；项目事实继续由项目代码、测试和文档负责。

同一项经验可以同时产生共同机制和多个特殊维度。共同机制覆盖性质不同但结果相同的请求；平台、版本、规模、顺序或生命周期确实改变动作时，再叠加特殊维度。共同路径不会被一个醒目的专项症状缩窄，共同机制与可叠加特殊维度分别落位，并由顶层路由共同消费。

## 四个关键边界

### 1. 先保全能力，再谈精简

优化现有 Skill 前，Meta-skills 会按用户结果盘点触发、输入职责、输出合同、生产者、消费者、停止位置和可观察结果。新入口未接通前不拆旧路径；迁移完成后，兼容层、旧 helper、双重路由和恢复分支退出。

### 2. 治理证据不等于运行资源

失败记录、纠偏和一次性案例只用于当前治理。模板、完整示范、schema、脚本或资产只有进入正式消费链后才成为运行资源。Meta-skills 还会沿正式调用点冻结实际提示词输入，生产模型只收到完成任务需要的事实、要求、参考与协议。

### 3. 结构通过不等于行为完成

`quick_validate.py` 只检查结构、元数据、引用和确定性不变量。验证会先把检查范围限定在本次改动及其实际消费者，再按结果性质选择证据深度；不会因为仓库提供全量入口就运行无关生产链，也不会用结构通过冒充用户已经拿到结果。

### 4. 学习主体决定经验落点

目标 Skill 学习时改变它自身的活动行为；项目沉淀停在项目真源；独立共享资源只有在用户明确要求且存在持续消费者时才建立。名称看起来通用，不能替代学习主体、唯一真源和正式消费者的判断。

学习其它 Skill 时，Meta-skills 会追溯真正产生被复用内容的原始上游。直接复制或改编代码、模板、示例、数据和资产时，目标项目保留许可证、复用范围与致谢；只学习方法并独立实现时，不把来源伪装成运行依赖。拿到 fork 时，只有确实复用了 fork 的独有改动才另谢 fork。

## 什么时候适合用

适合使用 Meta-skills：

- 目标是一个 Codex/Agent Skill 的身份、路由、能力、资源、验证或维护方式；
- 需要从文本、对话、仓库、压缩包、示例或另一个 Skill 中迁移完整能力；
- 需要判断一个 Skill 职能是否过宽、过窄，或者旧架构是否已经完整退出；
- 需要证明脚本、模板、schema 或资产确实被正式消费者读取并产生结果。

不需要使用 Meta-skills：

- 你只是要完成普通业务任务，而不是改变 Skill；
- 你只想让项目记住自身事实，没有要求改变 Skill 的未来行为；
- 你需要的是一次性内容成品，不需要建立可复用的 Skill 能力。

## 维护者入口

活动方法按职责分组，README 不复制它们的完整规则：

- 设计与提示词：[`skill-design-playbook.md`](references/skill-design-playbook.md)、[`instruction-hygiene.md`](references/instruction-hygiene.md)、[`openai-yaml.md`](references/openai-yaml.md)
- 学习、蒸馏与资源：[`absorption-and-governance.md`](references/absorption-and-governance.md)、[`evidence-distillation.md`](references/evidence-distillation.md)、[`resource-design.md`](references/resource-design.md)
- 链路图、维护与验收：[`skill-flow-diagram.md`](references/skill-flow-diagram.md)、[`skill-maintenance-and-evaluation.md`](references/skill-maintenance-and-evaluation.md)、[`quality-gate.md`](references/quality-gate.md)

所有活动 reference 都由 [`SKILL.md`](SKILL.md) 直接选择。项目自带四个确定性工具：

| 工具 | 作用 |
| --- | --- |
| [`scripts/init_skill.py`](scripts/init_skill.py) | 规范化 Skill 名称并初始化 `SKILL.md` 与 `agents/openai.yaml` |
| [`scripts/generate_openai_yaml.py`](scripts/generate_openai_yaml.py) | 从最终 Skill 定位生成或更新 Codex 界面元数据 |
| [`scripts/quick_validate.py`](scripts/quick_validate.py) | 检查 frontmatter、路由、活动资源、界面元数据和确定性不变量 |
| [`scripts/self-test-quick-validate.py`](scripts/self-test-quick-validate.py) | 回归验证结构校验器本身的扫描边界 |

修改本项目前后都运行：

```bash
python scripts/quick_validate.py .
```

详细仓库约束见 [`AGENTS.md`](AGENTS.md)。其中，`SKILL.md` 受保护核心默认只读；这类 README 优化不会改动它、锁文件或校验器不变量。贡献流程见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

如果你在其它目录持续维护源码，请把这个仓库保留为唯一真源，再从 `$HOME/.agents/skills/meta-skills` 建立目录联接；不要维护第二份副本。具体步骤见 [源码同步说明](references/skill-maintenance-and-evaluation.md#8-本地默认启用与源码同步)。

## Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history.svg">
  <img alt="CheshireMew/meta-skills GitHub Star History" src="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history.svg">
</picture>

## 许可证

本仓库原创的源代码、Agent/Codex Skill 指令、脚本和可复用 reference 文档采用 [Mozilla Public License 2.0](LICENSE)。Meta-skills 检查、迁移或生成的用户 Skill 继续受其作者自己的条款约束；第三方组件与引入内容也保留各自的授权边界。完整范围见 [`LICENSING.md`](LICENSING.md) 和 [`NOTICE`](NOTICE)。
