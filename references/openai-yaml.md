# `agents/openai.yaml` 生成规则

`agents/openai.yaml` 是产品界面和运行环境读取的元数据，不承载 Skill 行为。创建新 Skill 或修改名称、定位、图标、依赖和调用策略时读取本文件，然后使用 `scripts/generate_openai_yaml.py` 生成；不要手写另一套字段约定。

## 必需界面字段

`interface` 必须包含：

- `display_name`：用户在 Skill 列表中看到的名称。
- `short_description`：25–64 个字符的简述，说明用户能得到什么。
- `default_prompt`：一条简短的示范调用，必须明确包含 `$skill-name`。

根据最终 `SKILL.md` 生成这三个值。名称和简述面向用户，不能复制内部行为规则；默认提示只表达一个正常入口，不暗示联网、安装、写入、发送、发布或删除等未获授权动作。

## 可选界面字段

- `icon_small`、`icon_large`：相对于 Skill 根目录的文件路径。只在资产已经存在时填写，优先放在 `assets/`。
- `brand_color`：形如 `#3B82F6` 的六位十六进制颜色。

只有用户提供或现有 Skill 已经确认使用这些值时才保留。生成器会检查图标文件是否存在，不创建占位图标。

## 依赖与调用策略

已有文件中的 `dependencies` 和 `policy` 由生成器原样保留。需要声明 MCP 依赖时，使用 `dependencies.tools`，每项写明 `type`、`value`、`description`，并在适用时写 `transport` 和 `url`。`policy.allow_implicit_invocation` 为 `false` 时，Skill 只通过显式 `$skill-name` 调用；默认不添加该字段。

## 生成命令

新建目录时，把已经确认的 UI 文案传给初始化器：

```text
python scripts/init_skill.py <skill-name> --path <parent> --description <description> --interface display_name=<name> --interface short_description=<summary> --interface default_prompt=<prompt>
```

正文完成或既有 Skill 定位变化后重新生成：

```text
python scripts/generate_openai_yaml.py <skill-folder> --interface display_name=<name> --interface short_description=<summary> --interface default_prompt=<prompt>
```

生成器只更新 `interface`，保留已有 `dependencies` 和 `policy`。生成后重新读取文件，并运行 `scripts/quick_validate.py <skill-folder>`；脚本退出成功不能代替对最终文件内容的检查。
