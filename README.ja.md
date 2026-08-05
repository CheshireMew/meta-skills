# Meta-skills

<p align="center">
  <img src="./assets/readme/hero.ja.svg" width="100%" alt="Meta-skills は文章、既存 Skill、リポジトリ資料から、実行・検証可能な目標 Skill の能力を蒸留します">
</p>

<!-- readme-header:start -->

<p align="center">
  <a href="./README.md">中文</a> · <a href="./README.en.md">English</a> · <strong>日本語</strong> | <a href="./SKILL.md">文档</a> | <a href="./CONTRIBUTING.md">贡献</a> | <a href="https://github.com/CheshireMew/meta-skills/issues">反馈</a>
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

Meta-skills は、Codex/Agent 向けの Skill エンジニアリングを行うメタ Skill です。目的、資料、または既存の Skill を渡すと、まず本当に必要な結果を確定し、既存能力を保全したうえで最終的な振る舞いを設計し、必要な資源を移行し、現在の環境で観察できる終点まで検証します。

Skill の新規作成、監査、書き直し、移行、評価に加え、明示的に依頼した場合だけ対話から学習する Skill の設計や、制御フロー・データフロー・資源消費・検証ループの追跡可能な図示にも使えます。活動中の Skill ファイルを書き換える前に、振る舞いの案、能力保全台帳、代表的な出力、影響ファイルを提示し、承認を待ちます。

## まず一つの実タスクを完了する

### 1. インストール

Codex のユーザー Skill ディレクトリは `$HOME/.agents/skills` です。

```bash
git clone https://github.com/CheshireMew/meta-skills.git "$HOME/.agents/skills/meta-skills"
```

通常、Codex は Skill を自動検出します。表示されない場合は、Codex を再起動して確認してください。

### 2. 移行したい結果をそのまま伝える

次の依頼では、Meta-skills が資料と対象 Skill を読み、ファイルを書き換える前に案を提示します。

```text
Use $meta-skills で <materials> と <target-skill> を読み、対象 Skill に不足している「結果を生む能力」を特定し、資料中の判断・手順・必要な運用資源を蒸留して移行してください。まず能力台帳、移行案、出力の骨格、影響ファイルを示し、私の承認後に実装と検証を進めてください。
```

最初に確認できるもの：

- 対象 Skill が現在生み出せる結果と、保全すべき能力・資源；
- 資料から移行すべき内容と、今回の作業だけに留める内容；
- 将来の標準動作、条件分岐、出力、停止位置；
- 変更ファイルと、利用者が結果を使えることを示す検証方法。

承認後、Meta-skills は新しい入口を接続し、すべての活動中の消費側を移行し、置き換えられた旧経路を終了します。構造検査はファイルと経路が成立することを確認します。スクリプト、テンプレート、登録資源が関わる場合は、正式な生産者、転送または保存境界、消費者、利用者が見える結果まで検証します。

## 欲しい結果から入口を選ぶ

| 欲しい結果 | 依頼例 |
| --- | --- |
| Skill を新規作成する | `Use $meta-skills で <目的と資料> から <skill-name> を作成してください。まず振る舞い契約、ディレクトリ構成、影響ファイルを示し、承認後に実装・検証してください。` |
| 既存 Skill を読み取り専用で監査する | `Use $meta-skills で <skill-folder> を監査し、現在の能力、主要な問題、改善案を説明してください。ファイルは変更しないでください。` |
| Skill を書き直す、簡素化する、移行する | `Use $meta-skills で <skill-folder> を改造してください。全活動能力と運用資源を棚卸しし、原位置で保全、移行して保全、明示的な理由を伴う終了のいずれかを示してから最終案を提示してください。` |
| 対話から学ぶ Skill にする | `Use $meta-skills で <target-skill> を改造し、私が明示的に学習を依頼した場合だけ、検証済みの経験を将来参照される活動ルールへ内在化してください。プロジェクト固有の事実はプロジェクトの真源に残してください。` |
| 実行チェーン全体を図示する | `Use $meta-skills で <skill-folder> を読み、ルーティング、生産者、真源、境界、消費者、検証ループ、利用者の結果、未確認の接続を含む詳細な Mermaid 図を作成してください。` |
| Skill を保守・評価・同期する | `Use $meta-skills で <skill-folder> の発火、ルーティング、出力、既定有効化、ソース同期の問題を調べ、現在のリスクに合った深さで検証してください。` |

これらは組み合わせられますが、独立した一つの結果には一つの主経路だけを使います。現在のプロジェクト作業を完了することと、Skill の将来の振る舞いを変えることは別の結果です。両方を依頼した場合だけ、両方を実行します。

## 資料から実行可能な能力へ

<p align="center">
  <img src="./assets/readme/distillation-workflow.ja.svg" width="100%" alt="資料から判断、手順、運用資源、検収境界を蒸留し、対象 Skill へ接続して正式な生産・消費チェーンで検証します">
</p>

ここでいう「蒸留」は、要約や汎用原則の列挙ではありません。まず対象に不足している利用者の結果を特定し、その結果に必要な判断、手順、資源、停止位置を復元します。そのうえで、単独で結果を生み出せる最小の完全な能力単位を移行します。

| 境界 | Meta-skills の動作 |
| --- | --- |
| 保全してから再構成する | 発火条件、入力の役割、出力、生産者、消費者、観察可能な結果を棚卸しします。新しい入口が接続されるまで旧経路を残し、移行後は互換層を残しません。 |
| 証拠と資源を分ける | 失敗、修正、一度限りの事例はガバナンス証拠に留めます。テンプレート、完全な例、schema、スクリプト、アセットは、通常の生産経路が消費する場合だけ運用資源になります。 |
| 最上位で一度だけ経路を選ぶ | `SKILL.md` が主結果と排他的な分岐を選びます。reference、script、asset は選ばれた責務だけを実行し、下位から経路を変えません。 |
| 結果とリスクに合わせて検証する | 文字契約は経路、研究は事実、決定的な成果物は実際の生産チェーン、外部操作は権限と結果を確認します。構造合格を動作完了とは呼びません。 |

別のリポジトリや Skill から学ぶときは、元の upstream も追跡します。コード、テンプレート、例、データ、アセットを直接複製・改変する場合は、ライセンス、再利用範囲、謝辞を対象プロジェクトへ引き継ぎます。方法だけを学び独自に実装した場合、出典を実行時依存関係として扱いません。

## 使うべき場面

Meta-skills が適している場面：

- 対象が Codex/Agent Skill の役割、経路、能力、資源、検証、保守方法である；
- 文章、対話、リポジトリ、アーカイブ、例、別の Skill から完全な能力を移したい；
- Skill の職能が広すぎるか狭すぎるか、旧アーキテクチャが完全に終了したかを判断したい；
- スクリプト、テンプレート、schema、アセットが正式な消費者と結果に到達することを証明したい。

Meta-skills が不要な場面：

- Skill を変更せず、通常の業務タスクだけを完了したい；
- プロジェクト固有の知識をプロジェクト内に残すだけで、Skill の将来動作を変えない；
- 一度限りのコンテンツ成果物が欲しく、再利用可能な Skill 能力を作らない。

## メンテナー向け入口

活動中の方法は責務ごとに分かれ、README は詳細規則を重複させません。

- 設計とプロンプト：[`skill-design-playbook.md`](references/skill-design-playbook.md)、[`instruction-hygiene.md`](references/instruction-hygiene.md)、[`openai-yaml.md`](references/openai-yaml.md)
- 学習、蒸留、資源：[`absorption-and-governance.md`](references/absorption-and-governance.md)、[`evidence-distillation.md`](references/evidence-distillation.md)、[`resource-design.md`](references/resource-design.md)
- フロー図、保守、検収：[`skill-flow-diagram.md`](references/skill-flow-diagram.md)、[`skill-maintenance-and-evaluation.md`](references/skill-maintenance-and-evaluation.md)、[`quality-gate.md`](references/quality-gate.md)

すべての活動中の reference は [`SKILL.md`](SKILL.md) から直接選択されます。リポジトリには四つの決定的ツールがあります。

| ツール | 役割 |
| --- | --- |
| [`scripts/init_skill.py`](scripts/init_skill.py) | Skill 名を正規化し、`SKILL.md` と `agents/openai.yaml` を初期化する |
| [`scripts/generate_openai_yaml.py`](scripts/generate_openai_yaml.py) | 最終的な Skill の役割から Codex UI メタデータを生成・更新する |
| [`scripts/quick_validate.py`](scripts/quick_validate.py) | frontmatter、経路、活動資源、UI メタデータ、決定的不変条件を検査する |
| [`scripts/self-test-quick-validate.py`](scripts/self-test-quick-validate.py) | 構造検査器自身の走査境界を回帰検証する |

プロジェクトを変更する前後に実行します。

```bash
python scripts/quick_validate.py .
```

リポジトリ規則は [`AGENTS.md`](AGENTS.md) を参照してください。`SKILL.md` の保護コアは既定で読み取り専用です。README の作業では、保護コア、ロックファイル、検証器の不変条件を変更しません。貢献手順は [`CONTRIBUTING.md`](CONTRIBUTING.md) にあります。

別の場所で継続的に保守する場合は、このリポジトリを唯一の真源にし、第二のコピーを作らず `$HOME/.agents/skills/meta-skills` からリンクしてください。詳しい手順は [ソース同期](references/skill-maintenance-and-evaluation.md#8-本地默认启用与源码同步) を参照してください。

## Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history.svg">
  <img alt="CheshireMew/meta-skills GitHub Star History" src="https://raw.githubusercontent.com/CheshireMew/meta-skills/star-history/star-history.svg">
</picture>

## ライセンス

このリポジトリのオリジナルなソースコード、Agent/Codex Skill 指示、スクリプト、再利用可能な reference 文書は [Mozilla Public License 2.0](LICENSE) で提供されます。Meta-skills が監査、移行、生成した利用者の Skill は各作者の条件に従い、第三者コンポーネントと導入資料もそれぞれのライセンス境界を保ちます。完全な範囲は [`LICENSING.md`](LICENSING.md) と [`NOTICE`](NOTICE) を参照してください。
