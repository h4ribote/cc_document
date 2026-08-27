> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# SDK の Agent Skills

> Claude Agent SDK を使用して、Agent Skills で Claude を特殊な機能で拡張します

<h2 id="overview">
  概要
</h2>

Agent Skills は、Claude が関連する場合に自律的に呼び出す特殊な機能で Claude を拡張します。Skills は、指示、説明、およびオプションのサポートリソースを含む `SKILL.md` ファイルとしてパッケージ化されます。

Skills に関する包括的な情報（利点、アーキテクチャ、作成ガイドラインを含む）については、[Agent Skills の概要](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/overview)を参照してください。

<h2 id="how-skills-work-with-the-sdk">
  SDK での Skills の動作方法
</h2>

Claude Agent SDK を使用する場合、Skills は以下のように機能します。

1. **ファイルシステムアーティファクトとして定義される**：特定のディレクトリ（`.claude/skills/`）に `SKILL.md` ファイルとして作成されます
2. **ファイルシステムから読み込まれる**：Skills は `settingSources`（TypeScript）または `setting_sources`（Python）によって管理されるファイルシステムの場所から読み込まれます
3. **自動的に検出される**：ファイルシステム設定が読み込まれると、Skill メタデータはスタートアップ時にユーザーおよびプロジェクトディレクトリから検出されます。完全なコンテンツはトリガーされたときに読み込まれます
4. **モデルによって呼び出される**：Claude はコンテキストに基づいて自律的に使用するタイミングを選択します
5. **`skills` オプションでフィルタリングされる**：検出された Skills はデフォルトで有効になります。スキル名のリスト、`"all"`、または `[]` を渡して、セッションで利用可能なものを制御します

サブエージェント（プログラムで定義できる）とは異なり、Skills はファイルシステムアーティファクトとして作成する必要があります。SDK は Skills を登録するためのプログラマティック API を提供しません。

<Note>
  Skills はファイルシステム設定ソースを通じて検出されます。デフォルトの `query()` オプションでは、SDK はユーザーおよびプロジェクトソースを読み込むため、`~/.claude/skills/`、`<cwd>/.claude/skills/`、および `<cwd>` の親ディレクトリからリポジトリルートまでの `.claude/skills/` の skills が利用可能です。`settingSources` を明示的に設定する場合は、`'user'` または `'project'` を含めてスキル検出を維持するか、[`plugins` オプション](/docs/ja/agent-sdk/plugins)を使用して特定のパスから skills を読み込みます。
</Note>

<h2 id="using-skills-with-the-sdk">
  SDK での Skills の使用
</h2>

`query()` の `skills` オプションを設定して、セッションで利用可能な Skills を制御します。省略した場合、検出された Skills が有効になり、Skill ツールが利用可能になり、CLI の動作と一致します。`"all"` を渡してすべての検出された Skill を有効にするか、Skill 名のリストを渡してそれらのみを有効にするか、`[]` を渡してすべてを無効にします。`skills` を設定すると、SDK は Skill ツールを `allowedTools` に自動的に追加します。明示的な `tools` リストも渡す場合は、Claude が skills を呼び出せるようにそのリストに `"Skill"` を含めてください。

設定されると、Claude はファイルシステムから Skills を自動的に検出し、ユーザーのリクエストに関連する場合に呼び出します。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions


  async def main():
      options = ClaudeAgentOptions(
          cwd="/path/to/project",  # Project with .claude/skills/
          setting_sources=["user", "project"],  # Load Skills from filesystem
          skills="all",  # Enable every discovered Skill
          allowed_tools=["Read", "Write", "Bash"],
      )

      async for message in query(
          prompt="Help me process this PDF document", options=options
      ):
          print(message)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Help me process this PDF document",
    options: {
      cwd: "/path/to/project", // Project with .claude/skills/
      settingSources: ["user", "project"], // Load Skills from filesystem
      skills: "all", // Enable every discovered Skill
      allowedTools: ["Read", "Write", "Bash"]
    }
  })) {
    console.log(message);
  }
  ```
</CodeGroup>

特定の Skills のみを有効にするには、それらの名前を渡します。名前は `SKILL.md` の `name` フィールドまたは Skill のディレクトリ名と一致します。プラグイン提供の Skills には `plugin:skill` を使用します。

<CodeGroup>
  ```python Python theme={null}
  options = ClaudeAgentOptions(skills=["pdf", "docx"])
  ```

  ```typescript TypeScript theme={null}
  const options = { skills: ["pdf", "docx"] };
  ```
</CodeGroup>

`skills` オプションはコンテキストフィルタであり、サンドボックスではありません。リストされていない Skills はモデルから非表示になり、Skill ツールによって拒否されますが、それらのファイルはディスク上に残り、Read および Bash を通じてアクセス可能です。

<h2 id="skill-locations">
  Skill の場所
</h2>

Skills は `settingSources`/`setting_sources` 設定に基づいてファイルシステムディレクトリから読み込まれます。

* **プロジェクト Skills**（`.claude/skills/`）：git を通じてチームと共有されます。`setting_sources` に `"project"` が含まれている場合に読み込まれます
* **ユーザー Skills**（`~/.claude/skills/`）：すべてのプロジェクト全体の個人用 Skills。`setting_sources` に `"user"` が含まれている場合に読み込まれます
* **プラグイン Skills**：インストールされた Claude Code プラグインにバンドルされています

<h2 id="creating-skills">
  Skills の作成
</h2>

Skills は、YAML フロントマターと Markdown コンテンツを含む `SKILL.md` ファイルを含むディレクトリとして定義されます。`description` フィールドは、Claude が Skill を呼び出すタイミングを決定します。

**ディレクトリ構造の例**：

```bash theme={null}
.claude/skills/processing-pdfs/
└── SKILL.md
```

Skills の作成に関する完全なガイダンス（SKILL.md 構造、複数ファイルの Skills、例を含む）については、以下を参照してください。

* [Claude Code の Agent Skills](/docs/ja/skills)：例を含む完全なガイド
* [Agent Skills のベストプラクティス](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/best-practices)：作成ガイドラインと命名規則

<h2 id="tool-restrictions">
  ツール制限
</h2>

<Note>
  SKILL.md の `allowed-tools` フロントマターフィールドは、Claude Code CLI を直接使用する場合にのみサポートされます。**SDK を通じて Skills を使用する場合には適用されません**。

  SDK を使用する場合、クエリ設定の主要な `allowedTools` オプションを通じてツールアクセスを制御します。
</Note>

SDK アプリケーションで Skills のツールアクセスを制御するには、`allowedTools` を使用して特定のツールを事前承認します。`canUseTool` コールバックがない場合、リストにないものはすべて拒否されます。

<Note>
  最初の例からのインポートステートメントは、以下のコードスニペットで想定されています。
</Note>

<CodeGroup>
  ```python Python theme={null}
  options = ClaudeAgentOptions(
      setting_sources=["user", "project"],  # Load Skills from filesystem
      skills="all",
      allowed_tools=["Read", "Grep", "Glob"],
  )

  async for message in query(prompt="Analyze the codebase structure", options=options):
      print(message)
  ```

  ```typescript TypeScript theme={null}
  for await (const message of query({
    prompt: "Analyze the codebase structure",
    options: {
      settingSources: ["user", "project"], // Load Skills from filesystem
      skills: "all",
      allowedTools: ["Read", "Grep", "Glob"],
      permissionMode: "dontAsk" // Deny anything not in allowedTools
    }
  })) {
    console.log(message);
  }
  ```
</CodeGroup>

<h2 id="discovering-available-skills">
  利用可能な Skills の検出
</h2>

SDK アプリケーションで利用可能な Skills を確認するには、Claude に尋ねるだけです。

<CodeGroup>
  ```python Python theme={null}
  options = ClaudeAgentOptions(
      setting_sources=["user", "project"],  # Load Skills from filesystem
      skills="all",
  )

  async for message in query(prompt="What Skills are available?", options=options):
      print(message)
  ```

  ```typescript TypeScript theme={null}
  for await (const message of query({
    prompt: "What Skills are available?",
    options: {
      settingSources: ["user", "project"], // Load Skills from filesystem
      skills: "all"
    }
  })) {
    console.log(message);
  }
  ```
</CodeGroup>

Claude は、現在の作業ディレクトリとインストールされたプラグインに基づいて、利用可能な Skills をリストします。

<h2 id="testing-skills">
  Skills のテスト
</h2>

説明と一致する質問をすることで Skills をテストします。

<CodeGroup>
  ```python Python theme={null}
  options = ClaudeAgentOptions(
      cwd="/path/to/project",
      setting_sources=["user", "project"],  # Load Skills from filesystem
      skills="all",
      allowed_tools=["Read", "Bash"],
  )

  async for message in query(prompt="Extract text from invoice.pdf", options=options):
      print(message)
  ```

  ```typescript TypeScript theme={null}
  for await (const message of query({
    prompt: "Extract text from invoice.pdf",
    options: {
      cwd: "/path/to/project",
      settingSources: ["user", "project"], // Load Skills from filesystem
      skills: "all",
      allowedTools: ["Read", "Bash"]
    }
  })) {
    console.log(message);
  }
  ```
</CodeGroup>

説明がリクエストと一致する場合、Claude は自動的に関連する Skill を呼び出します。

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

<h3 id="skills-not-found">
  Skills が見つからない
</h3>

**settingSources 設定を確認する**：Skills は `user` および `project` 設定ソースを通じて検出されます。`settingSources`/`setting_sources` を明示的に設定し、それらのソースを省略した場合、skills は読み込まれません。

<CodeGroup>
  ```python Python theme={null}
  # Skills not loaded: setting_sources excludes user and project
  options = ClaudeAgentOptions(setting_sources=[], skills="all")

  # Skills loaded: user and project sources included
  options = ClaudeAgentOptions(
      setting_sources=["user", "project"],
      skills="all",
  )
  ```

  ```typescript TypeScript theme={null}
  // Skills not loaded: settingSources excludes user and project
  const options = {
    settingSources: [],
    skills: "all"
  };

  // Skills loaded: user and project sources included
  const options = {
    settingSources: ["user", "project"],
    skills: "all"
  };
  ```
</CodeGroup>

`settingSources`/`setting_sources` の詳細については、[TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript#settingsource)または [Python SDK リファレンス](/docs/ja/agent-sdk/python#settingsource)を参照してください。

**作業ディレクトリを確認する**：SDK は `cwd` オプションの `.claude/skills/` およびリポジトリルートまでのすべての親ディレクトリから Skills を読み込みます。`cwd` が `.claude/skills/` を含むディレクトリ以下を指していることを確認してください。同じリポジトリ内である必要があります。

<CodeGroup>
  ```python Python theme={null}
  # Ensure your cwd points to the directory containing .claude/skills/
  options = ClaudeAgentOptions(
      cwd="/path/to/project",  # .claude/skills/ here or in a parent directory
      setting_sources=["user", "project"],  # Loads skills from these sources
      skills="all",
  )
  ```

  ```typescript TypeScript theme={null}
  // Ensure your cwd points to the directory containing .claude/skills/
  const options = {
    cwd: "/path/to/project", // .claude/skills/ here or in a parent directory
    settingSources: ["user", "project"], // Loads skills from these sources
    skills: "all"
  };
  ```
</CodeGroup>

上記の「SDK での Skills の使用」セクションで完全なパターンを参照してください。

**ファイルシステムの場所を確認する**：

```bash theme={null}
# Check project Skills
ls .claude/skills/*/SKILL.md

# Check personal Skills
ls ~/.claude/skills/*/SKILL.md
```

<h3 id="skill-not-being-used">
  Skill が使用されていない
</h3>

**`skills` オプションを確認する**：`skills` リストを渡した場合、skill の名前が含まれていることを確認します。`[]` を渡すとすべての skills が無効になります。

**説明を確認する**：具体的で関連するキーワードが含まれていることを確認します。効果的な説明の書き方に関するガイダンスについては、[Agent Skills のベストプラクティス](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions)を参照してください。

<h3 id="additional-troubleshooting">
  追加のトラブルシューティング
</h3>

一般的な Skills トラブルシューティング（YAML 構文、デバッグなど）については、[Claude Code Skills トラブルシューティングセクション](/docs/ja/skills#troubleshooting)を参照してください。

<h2 id="related-documentation">
  関連ドキュメント
</h2>

<h3 id="skills-guides">
  Skills ガイド
</h3>

* [Claude Code の Agent Skills](/docs/ja/skills)：作成、例、トラブルシューティングを含む完全な Skills ガイド
* [Agent Skills の概要](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/overview)：概念的な概要、利点、アーキテクチャ
* [Agent Skills のベストプラクティス](https://platform.claude.com/docs/ja/agents-and-tools/agent-skills/best-practices)：効果的な Skills のための作成ガイドライン
* [Agent Skills クックブック](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction)：例の Skills とテンプレート

<h3 id="sdk-resources">
  SDK リソース
</h3>

* [SDK のサブエージェント](/docs/ja/agent-sdk/subagents)：プログラマティックオプションを備えた同様のファイルシステムベースのエージェント
* [SDK のスラッシュコマンド](/docs/ja/agent-sdk/slash-commands)：ユーザーが呼び出すコマンド
* [SDK の概要](/docs/ja/agent-sdk/overview)：一般的な SDK の概念
* [TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript)：完全な API ドキュメント
* [Python SDK リファレンス](/docs/ja/agent-sdk/python)：完全な API ドキュメント
