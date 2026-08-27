> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# SDK で Claude Code 機能を使用する

> プロジェクト指示、スキル、フック、その他の Claude Code 機能を SDK エージェントに読み込みます。

Agent SDK は Claude Code と同じ基盤の上に構築されているため、SDK エージェントは同じファイルシステムベースの機能にアクセスできます。プロジェクト指示（`CLAUDE.md` とルール）、スキル、フック、その他の機能です。

`settingSources` を省略すると、`query()` は Claude Code CLI と同じファイルシステム設定を読み込みます。ユーザー、プロジェクト、ローカル設定、CLAUDE.md ファイル、`.claude/` スキル、エージェント、コマンドです。これらなしで実行するには、`settingSources: []` を渡します。これにより、エージェントはプログラムで設定したものに限定されます。マネージドポリシー設定とグローバル `~/.claude.json` 設定は、このオプションに関係なく読み込まれます。[settingSources が制御しないもの](#what-settingsources-does-not-control)を参照してください。

各機能の概念的な概要と使用時期については、[Claude Code を拡張する](/docs/ja/features-overview)を参照してください。

<h2 id="control-filesystem-settings-with-settingsources">
  settingSources でファイルシステム設定を制御する
</h2>

設定ソースオプション（Python では [`setting_sources`](/docs/ja/agent-sdk/python#claudeagentoptions)、TypeScript では [`settingSources`](/docs/ja/agent-sdk/typescript#settingsource)）は、SDK が読み込むファイルシステムベースの設定を制御します。特定のソースにオプトインするための明示的なリストを渡すか、ユーザー、プロジェクト、ローカル設定を無効にするための空の配列を渡します。

この例では、`settingSources` を `["user", "project"]` に設定して、ユーザーレベルとプロジェクトレベルの両方の設定を読み込みます。

<CodeGroup>
  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

  async for message in query(
      prompt="Help me refactor the auth module",
      options=ClaudeAgentOptions(
          # "user" loads from ~/.claude/, "project" loads from ./.claude/ in cwd.
          # Together they give the agent access to CLAUDE.md, skills, hooks, and
          # permissions from both locations.
          setting_sources=["user", "project"],
          allowed_tools=["Read", "Edit", "Bash"],
      ),
  ):
      if isinstance(message, AssistantMessage):
          for block in message.content:
              if hasattr(block, "text"):
                  print(block.text)
      if isinstance(message, ResultMessage) and message.subtype == "success":
          print(f"\nResult: {message.result}")
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Help me refactor the auth module",
    options: {
      // "user" loads from ~/.claude/, "project" loads from ./.claude/ in cwd.
      // Together they give the agent access to CLAUDE.md, skills, hooks, and
      // permissions from both locations.
      settingSources: ["user", "project"],
      allowedTools: ["Read", "Edit", "Bash"]
    }
  })) {
    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if (block.type === "text") console.log(block.text);
      }
    }
    if (message.type === "result" && message.subtype === "success") {
      console.log(`\nResult: ${message.result}`);
    }
  }
  ```
</CodeGroup>

各ソースは特定の場所から設定を読み込みます。`<cwd>` は `cwd` オプション経由で渡す作業ディレクトリです（設定されていない場合はプロセスの現在のディレクトリ）。完全な型定義については、[`SettingSource`](/docs/ja/agent-sdk/typescript#settingsource)（TypeScript）または [`SettingSource`](/docs/ja/agent-sdk/python#settingsource)（Python）を参照してください。

| ソース         | 読み込むもの                                                                           | 場所                                                                                                             |
| :---------- | :------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------- |
| `"project"` | プロジェクト CLAUDE.md、`.claude/rules/*.md`、プロジェクトスキル、プロジェクトフック、プロジェクト `settings.json` | `<cwd>/.claude/` （`settings.json` とフック用）；CLAUDE.md とルール用に `<cwd>` と全親ディレクトリ；スキル用に `<cwd>` とリポジトリルートまでの全親ディレクトリ |
| `"user"`    | ユーザー CLAUDE.md、`~/.claude/rules/*.md`、ユーザースキル、ユーザー設定                             | `~/.claude/`                                                                                                   |
| `"local"`   | CLAUDE.local.md、`.claude/settings.local.json`                                    | `<cwd>/.claude/` （`settings.local.json` 用）；CLAUDE.local.md 用に `<cwd>` と全親ディレクトリ                                |

`settingSources` を省略することは `["user", "project", "local"]` と同等です。

`cwd` オプションは、SDK がプロジェクトレベルの入力を探す場所を決定します。CLAUDE.md とルールは `<cwd>` と全親ディレクトリから読み込まれます。スキルは `<cwd>` とリポジトリルートまでの全親ディレクトリから読み込まれます。プロジェクト `settings.json` とフックは `<cwd>/.claude/` からのみ読み込まれ、親ディレクトリへのフォールバックはありません。

<h3 id="what-settingsources-does-not-control">
  settingSources が制御しないもの
</h3>

`settingSources` はユーザー、プロジェクト、ローカル設定をカバーします。その値に関係なく読み込まれるいくつかの入力があります。

| 入力                                                           | 動作                                                                                                                                                                                                                            | 無効にするには                                                                                                                                                                |
| :----------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| マネージドポリシー設定                                                  | エンドポイント管理ポリシー（MDM plist、レジストリポリシー、またはマネージド設定ファイル）はホストから読み込まれます。[サーバー管理設定](/docs/ja/server-managed-settings)は、組織 OAuth ログインまたは直接構成された API キーでセッションが認証されるときに取得されます（[対象となる構成](/docs/ja/server-managed-settings#platform-availability)の場合）。 | エンドポイントポリシー：ホストからマネージド設定ファイル、plist、またはレジストリポリシーを削除します。サーバー管理設定：組織管理者によって制御されます；SDK から無効にすることはできません。                                                                    |
| `~/.claude.json` グローバル設定                                     | 常に読み込まれます                                                                                                                                                                                                                     | `env` の `CLAUDE_CONFIG_DIR` で再配置します                                                                                                                                    |
| `~/.claude/projects/<project>/memory/` の自動メモリ                | セッション開始時にシステムプロンプトに読み込まれます。エージェントは専用のメモリツールではなく、標準の `Write` および `Edit` ツールを使用して新しいメモリをそこに書き込むため、エージェントがメモリを保存するにはこれらのツールを有効にする必要があります。                                                                                        | 設定で `autoMemoryEnabled: false` を設定するか、`env` で `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` を設定します                                                                               |
| [claude.ai MCP コネクタ](/docs/ja/mcp#use-mcp-servers-from-claude-ai) | アクティブな認証方法が claude.ai サブスクリプションの場合に読み込まれます。`mcpServers: {}` を渡しても抑制されません                                                                                                                                                      | `strictMcpConfig: true` を設定するか、設定で [`disableClaudeAiConnectors: true`](/docs/ja/mcp#disable-claude-ai-connectors) を設定するか、`env` で `ENABLE_CLAUDEAI_MCP_SERVERS=false` を設定します |

<Warning>
  マルチテナント分離のためにデフォルトの `query()` オプションに依存しないでください。上記の入力は `settingSources` に関係なく読み込まれるため、SDK プロセスはホストレベルの設定とディレクトリごとのメモリを取得できます。マルチテナント展開の場合は、各テナントを独自のファイルシステムで実行し、`settingSources: []` と `env` で `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` を設定します。[サーバー管理設定](/docs/ja/server-managed-settings)は、プロセスが組織認証情報で認証されるときに取得されます；ファイルシステム分離はそれらを削除しません。[セキュアな展開](/docs/ja/agent-sdk/secure-deployment)を参照してください。
</Warning>

<h2 id="project-instructions-claude-md-and-rules">
  プロジェクト指示（CLAUDE.md とルール）
</h2>

`CLAUDE.md` ファイルと `.claude/rules/*.md` ファイルは、エージェントにプロジェクトに関する永続的なコンテキストを提供します。コーディング規約、ビルドコマンド、アーキテクチャの決定、指示です。`settingSources` に `"project"` が含まれている場合（上記の例のように）、SDK はセッション開始時にこれらのファイルをコンテキストに読み込みます。その後、エージェントはプロジェクト規約に従い、すべてのプロンプトで繰り返す必要がありません。

<h3 id="claude-md-load-locations">
  CLAUDE.md 読み込み場所
</h3>

| レベル             | 場所                                                                         | 読み込まれるとき                                                                      |
| :-------------- | :------------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| プロジェクト（ルート）     | `<cwd>/CLAUDE.md` または `<cwd>/.claude/CLAUDE.md`                            | `settingSources` に `"project"` が含まれる                                          |
| プロジェクトルール       | `<cwd>/.claude/rules/*.md` および `cwd` より上のすべての親ディレクトリの `.claude/rules/*.md` | `settingSources` に `"project"` が含まれる                                          |
| プロジェクト（親ディレクトリ） | `cwd` より上のディレクトリの `CLAUDE.md` ファイル                                         | `settingSources` に `"project"` が含まれ、セッション開始時に読み込まれます                          |
| プロジェクト（子ディレクトリ） | `cwd` のサブディレクトリの `CLAUDE.md` ファイル                                          | `settingSources` に `"project"` が含まれ、エージェントがそのサブツリーのファイルを読み込むときにオンデマンドで読み込まれます |
| ローカル            | `<cwd>/CLAUDE.local.md` および `cwd` より上のすべての親ディレクトリの `CLAUDE.local.md`       | `settingSources` に `"local"` が含まれる                                            |
| ユーザー            | `~/.claude/CLAUDE.md`                                                      | `settingSources` に `"user"` が含まれる                                             |
| ユーザールール         | `~/.claude/rules/*.md`                                                     | `settingSources` に `"user"` が含まれる                                             |

すべてのレベルは加算的です。プロジェクトとユーザーの両方の CLAUDE.md ファイルが存在する場合、エージェントは両方を見ます。レベル間に厳密な優先順位ルールはありません。指示が競合する場合、結果は Claude がそれらをどのように解釈するかに依存します。競合しないルールを記述するか、より具体的なファイルで優先順位を明示的に述べます（「これらのプロジェクト指示は、競合するユーザーレベルのデフォルトをオーバーライドします」）。

<Tip>
  `systemPrompt` 経由でコンテキストを直接注入することもできます。CLAUDE.md ファイルを使用する必要はありません。[システムプロンプトを変更する](/docs/ja/agent-sdk/modifying-system-prompts)を参照してください。CLAUDE.md は、同じコンテキストをインタラクティブな Claude Code セッションと SDK エージェント間で共有したい場合に使用します。
</Tip>

CLAUDE.md コンテンツの構造と整理方法については、[Claude のメモリを管理する](/docs/ja/memory)を参照してください。

<h2 id="skills">
  スキル
</h2>

スキルは、エージェントに専門知識と呼び出し可能なワークフローを提供するマークダウンファイルです。`CLAUDE.md`（すべてのセッションで読み込まれる）とは異なり、スキルはオンデマンドで読み込まれます。エージェントはスタートアップ時にスキルの説明を受け取り、関連するときに完全なコンテンツを読み込みます。

スキルは `settingSources` を通じてファイルシステムから検出されます。`query()` の `skills` オプションが省略されている場合、検出されたユーザーとプロジェクトのスキルが有効になり、Skill ツールが利用可能になります。これは CLI の動作と一致します。どのスキルを有効にするかを制御するには、`skills` を `"all"`、スキル名のリスト、または `[]` を渡してすべてを無効にします。`skills` が設定されている場合、SDK は Skill ツールを `allowedTools` に自動的に追加します。明示的な `tools` リストも渡す場合は、Claude がスキルを呼び出せるようにそのリストに `"Skill"` を含めてください。

<CodeGroup>
  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

  # Skills in .claude/skills/ are discovered automatically
  # when settingSources includes "project"
  async for message in query(
      prompt="Review this PR using our code review checklist",
      options=ClaudeAgentOptions(
          setting_sources=["user", "project"],
          skills="all",
          allowed_tools=["Read", "Grep", "Glob"],
      ),
  ):
      if isinstance(message, ResultMessage) and message.subtype == "success":
          print(message.result)
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // Skills in .claude/skills/ are discovered automatically
  // when settingSources includes "project"
  for await (const message of query({
    prompt: "Review this PR using our code review checklist",
    options: {
      settingSources: ["user", "project"],
      skills: "all",
      allowedTools: ["Read", "Grep", "Glob"]
    }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```
</CodeGroup>

<Note>
  スキルはファイルシステムアーティファクト（`.claude/skills/<name>/SKILL.md`）として作成する必要があります。SDK にはスキルを登録するためのプログラマティック API がありません。詳細については、[SDK のエージェントスキル](/docs/ja/agent-sdk/skills)を参照してください。
</Note>

スキルの作成と使用の詳細については、[SDK のエージェントスキル](/docs/ja/agent-sdk/skills)を参照してください。

<h2 id="hooks">
  フック
</h2>

SDK は 2 つの方法でフックを定義することをサポートしており、それらは並行して実行されます。

* **ファイルシステムフック：** `settings.json` で定義されたシェルコマンド。`settingSources` に関連するソースが含まれている場合に読み込まれます。これらは[インタラクティブな Claude Code セッション](/docs/ja/hooks-guide)用に設定するのと同じフックです。
* **プログラマティックフック：** `query()` に直接渡されるコールバック関数。これらはアプリケーションプロセスで実行され、構造化された決定を返すことができます。[フックで実行を制御する](/docs/ja/agent-sdk/hooks)を参照してください。

両方のタイプは同じフックライフサイクル中に実行されます。プロジェクトの `.claude/settings.json` にフックが既にあり、`settingSources: ["project"]` を設定している場合、それらのフックは追加の設定なしで SDK で自動的に実行されます。

フックコールバックはツール入力を受け取り、決定辞書を返します。`{}` を返すことはツールの実行を許可することを意味します。実行をブロックするには、`permissionDecision: "deny"` と `permissionDecisionReason` を含む `hookSpecificOutput` オブジェクトを返します。理由は Claude にツール結果として送信されます。トップレベルの `decision` と `reason` フィールドは `PreToolUse` では非推奨です。完全なコールバック署名と戻り値の型については、[フックガイド](/docs/ja/agent-sdk/hooks)を参照してください。

<CodeGroup>
  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, ResultMessage


  # PreToolUse hook callback. Positional args:
  #   input_data: HookInput dict with tool_name, tool_input, hook_event_name
  #   tool_use_id: str | None, the ID of the tool call being intercepted
  #   context: HookContext, carries session metadata
  async def audit_bash(input_data, tool_use_id, context):
      command = input_data.get("tool_input", {}).get("command", "")
      if "rm -rf" in command:
          return {
              "hookSpecificOutput": {
                  "hookEventName": "PreToolUse",
                  "permissionDecision": "deny",
                  "permissionDecisionReason": "Destructive command blocked",
              }
          }
      return {}  # Empty dict: allow the tool to proceed


  # Filesystem hooks from .claude/settings.json run automatically
  # when settingSources loads them. You can also add programmatic hooks:
  async for message in query(
      prompt="Refactor the auth module",
      options=ClaudeAgentOptions(
          setting_sources=["project"],  # Loads hooks from .claude/settings.json
          hooks={
              "PreToolUse": [
                  HookMatcher(matcher="Bash", hooks=[audit_bash]),
              ]
          },
      ),
  ):
      if isinstance(message, ResultMessage) and message.subtype == "success":
          print(message.result)
  ```

  ```typescript TypeScript theme={null}
  import { query, type HookInput, type HookJSONOutput } from "@anthropic-ai/claude-agent-sdk";

  // PreToolUse hook callback. HookInput is a discriminated union on
  // hook_event_name, so narrowing on it gives TypeScript the right
  // tool_input shape for this event.
  const auditBash = async (input: HookInput): Promise<HookJSONOutput> => {
    if (input.hook_event_name !== "PreToolUse") return {};
    const toolInput = input.tool_input as { command?: string };
    if (toolInput.command?.includes("rm -rf")) {
      return {
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          permissionDecision: "deny",
          permissionDecisionReason: "Destructive command blocked",
        },
      };
    }
    return {}; // Empty object: allow the tool to proceed
  };

  // Filesystem hooks from .claude/settings.json run automatically
  // when settingSources loads them. You can also add programmatic hooks:
  for await (const message of query({
    prompt: "Refactor the auth module",
    options: {
      settingSources: ["project"], // Loads hooks from .claude/settings.json
      hooks: {
        PreToolUse: [{ matcher: "Bash", hooks: [auditBash] }]
      }
    }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```
</CodeGroup>

<h3 id="when-to-use-which-hook-type">
  どのフックタイプを使用するか
</h3>

| フックタイプ                            | 最適な用途                                                                                                                                                                                                              |
| :-------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ファイルシステム** （`settings.json`）    | CLI と SDK セッション間でフックを共有します。`"command"`（シェルスクリプト）、`"http"`（エンドポイントへの POST）、`"mcp_tool"`（接続された MCP サーバーのツールを呼び出す）、`"prompt"`（LLM がプロンプトを評価する）、`"agent"`（検証エージェントを生成する）をサポートします。これらはメインエージェントとそれが生成するサブエージェントで実行されます。 |
| **プログラマティック** （`query()` のコールバック） | アプリケーション固有のロジック、構造化された決定、およびプロセス内統合。これらはサブエージェント内でも実行されます。コールバックは `agent_id` と `agent_type` を受け取り、区別することができます。                                                                                                     |

<Note>
  TypeScript SDK は Python を超えた追加のフックイベントをサポートしており、`SessionStart`、`SessionEnd`、`TeammateIdle`、`TaskCompleted` が含まれます。完全なイベント互換性テーブルについては、[フックガイド](/docs/ja/agent-sdk/hooks)を参照してください。
</Note>

プログラマティックフックの詳細については、[フックで実行を制御する](/docs/ja/agent-sdk/hooks)を参照してください。ファイルシステムフック構文については、[フック](/docs/ja/hooks)を参照してください。

<h2 id="choose-the-right-feature">
  適切な機能を選択する
</h2>

Agent SDK は、エージェントの動作を拡張するいくつかの方法へのアクセスを提供します。どれを使用するか不確かな場合、このテーブルは一般的な目標を正しいアプローチにマップします。

| 実現したいこと                                                 | 使用                                            | SDK サーフェス                                                                            |
| :------------------------------------------------------ | :-------------------------------------------- | :----------------------------------------------------------------------------------- |
| エージェントが常に従うプロジェクト規約を設定する                                | [CLAUDE.md](/docs/ja/memory)                       | `settingSources: ["project"]` がそれを自動的に読み込みます                                         |
| エージェントが関連するときに読み込む参考資料を提供する                             | [Skills](/docs/ja/agent-sdk/skills)                | `settingSources` + `skills` オプション                                                    |
| 再利用可能なワークフロー（デプロイ、レビュー、リリース）を実行する                       | [User-invocable skills](/docs/ja/agent-sdk/skills) | `settingSources` + `skills` オプション                                                    |
| 分離されたサブタスク（研究、レビュー）を新しいコンテキストに委譲する                      | [Subagents](/docs/ja/agent-sdk/subagents)          | `agents` パラメータ + `allowedTools: ["Agent"]`                                           |
| 共有タスクリストと直接的なエージェント間メッセージングで複数の Claude Code インスタンスを調整する | [Agent teams](/docs/ja/agent-teams)                | SDK オプション経由で直接設定されません。エージェントチームは CLI 機能で、1 つのセッションがチームリードとして機能し、独立したチームメイト間で作業を調整します |
| ツール呼び出しで決定論的ロジックを実行する（監査、ブロック、変換）                       | [Hooks](/docs/ja/agent-sdk/hooks)                  | `hooks` パラメータとコールバック、または `settingSources` 経由で読み込まれたシェルスクリプト                          |
| Claude に外部サービスへの構造化ツールアクセスを提供する                         | [MCP](/docs/ja/agent-sdk/mcp)                      | `mcpServers` パラメータ                                                                   |

<Tip>
  **Subagents 対 agent teams：** Subagents は一時的で分離されています。新しい会話、1 つのタスク、親に返される要約。Agent teams は、タスクリストを共有し、直接メッセージを送り合う複数の独立した Claude Code インスタンスを調整します。Agent teams は CLI 機能です。詳細については、[What subagents inherit](/docs/ja/agent-sdk/subagents#what-subagents-inherit)と[agent teams comparison](/docs/ja/agent-teams#compare-with-subagents)を参照してください。
</Tip>

有効にする機能ごとに、エージェントのコンテキストウィンドウに追加されます。機能ごとのコストとこれらの機能がどのように層状に配置されるかについては、[Extend Claude Code](/docs/ja/features-overview#understand-context-costs)を参照してください。

<h2 id="related-resources">
  関連リソース
</h2>

* [Claude Code を拡張する](/docs/ja/features-overview)：すべての拡張機能の概念的な概要、比較テーブル、コンテキストコスト分析
* [SDK のスキル](/docs/ja/agent-sdk/skills)：スキルをプログラムで使用するための完全なガイド
* [サブエージェント](/docs/ja/agent-sdk/subagents)：分離されたサブタスク用のサブエージェントを定義して呼び出す
* [フック](/docs/ja/agent-sdk/hooks)：主要な実行ポイントでエージェントの動作をインターセプトして制御する
* [権限](/docs/ja/agent-sdk/permissions)：モード、ルール、コールバックでツールアクセスを制御する
* [システムプロンプト](/docs/ja/agent-sdk/modifying-system-prompts)：CLAUDE.md ファイルなしでコンテキストを注入する
