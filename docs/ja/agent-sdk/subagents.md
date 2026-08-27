> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# SDK のサブエージェント

> サブエージェントを定義して呼び出し、コンテキストを分離し、タスクを並列実行し、Claude Agent SDK アプリケーションで特殊な指示を適用します。

サブエージェントは、メインエージェントが生成できる個別のエージェントインスタンスで、焦点を絞ったサブタスクを処理します。
サブエージェントを使用して、コンテキストを分離し、複数の分析を並列実行し、メインエージェントのプロンプトを肥大化させずに特殊な指示を適用します。

このガイドでは、`agents` パラメータを使用して SDK でサブエージェントを定義および使用する方法について説明します。

<h2 id="overview">
  概要
</h2>

サブエージェントは 3 つの方法で作成できます。

* **プログラム的に**: `query()` オプションの `agents` パラメータを使用します。[TypeScript](/docs/ja/agent-sdk/typescript#agentdefinition) および [Python](/docs/ja/agent-sdk/python#agentdefinition) リファレンスを参照してください
* **ファイルシステムベース**: `.claude/agents/` ディレクトリ内のマークダウンファイルとしてエージェントを定義します。[ファイルとしてサブエージェントを定義する](/docs/ja/sub-agents)を参照してください
* **組み込みの汎用**: Claude は、何も定義することなく、Agent ツールを介して組み込みの `general-purpose` サブエージェントをいつでも呼び出すことができます

このガイドでは、SDK アプリケーションに推奨されるプログラム的なアプローチに焦点を当てています。

サブエージェントを定義する場合、Claude は各サブエージェントの `description` フィールドに基づいて、それらを呼び出すかどうかを判断します。サブエージェントをいつ使用すべきかを説明する明確な説明を書いてください。Claude は自動的に適切なタスクを委譲します。プロンプトでサブエージェントを名前で明示的にリクエストすることもできます。例えば「code-reviewer エージェントを使用して...」のようにです。

<h2 id="benefits-of-using-subagents">
  サブエージェントを使用する利点
</h2>

<h3 id="context-isolation">
  コンテキスト分離
</h3>

各サブエージェントは独自の新しい会話で実行されます。中間的なツール呼び出しと結果はサブエージェント内に留まり、最終メッセージだけが親に返されます。[サブエージェントが継承するもの](#what-subagents-inherit)を参照して、サブエージェントのコンテキストに正確に何が含まれているかを確認してください。

**例:** `research-assistant` サブエージェントは、そのコンテンツがメイン会話に蓄積されることなく、数十のファイルを探索できます。親は、サブエージェントが読んだすべてのファイルではなく、簡潔なサマリーを受け取ります。

<h3 id="parallelization">
  並列化
</h3>

複数のサブエージェントを同時に実行でき、独立したサブタスクはすべての合計ではなく、最も遅いものの時間で完了します。

**例:** コードレビュー中に、`style-checker`、`security-scanner`、`test-coverage` サブエージェントを順序立てて実行するのではなく、同時に実行できます。

<h3 id="specialized-instructions-and-knowledge">
  特殊な指示と知識
</h3>

各サブエージェントは、特定の専門知識、ベストプラクティス、制約を備えたカスタマイズされたシステムプロンプトを持つことができます。

**例:** `database-migration` サブエージェントは、SQL ベストプラクティス、ロールバック戦略、データ整合性チェックに関する詳細な知識を持つことができます。これらはメインエージェントの指示では不要なノイズになります。

<h3 id="tool-restrictions">
  ツール制限
</h3>

サブエージェントは特定のツールに制限でき、意図しないアクションのリスクを軽減します。

**例:** `doc-reviewer` サブエージェントは Read と Grep ツールのみにアクセスでき、ドキュメントファイルを分析できますが、誤って変更することはありません。

<h2 id="create-subagents">
  サブエージェントの作成
</h2>

<h3 id="programmatic-definition-recommended">
  プログラム的な定義（推奨）
</h3>

`agents` パラメータを使用してコード内でサブエージェントを直接定義します。Claude はサブエージェントを Agent ツール経由で呼び出すため、`allowedTools` に `Agent` を含めて、パーミッション プロンプトなしでサブエージェント呼び出しを自動承認する必要があります。

このページのほとんどの例は最終結果のみを出力します。Claude がサブエージェントに委譲したことを確認するには、[サブエージェント呼び出しの検出](#detect-subagent-invocation)を参照してください。

この例では、読み取り専用アクセスを持つコードレビュアーとコマンドを実行できるテストランナーの 2 つのサブエージェントを作成します。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


  async def main():
      async for message in query(
          prompt="Review the authentication module for security issues",
          options=ClaudeAgentOptions(
              # Auto-approve these tools, including Agent for subagent invocation
              allowed_tools=["Read", "Grep", "Glob", "Agent"],
              agents={
                  "code-reviewer": AgentDefinition(
                      # description tells Claude when to use this subagent
                      description="Expert code review specialist. Use for quality, security, and maintainability reviews.",
                      # prompt defines the subagent's behavior and expertise
                      prompt="""You are a code review specialist with expertise in security, performance, and best practices.

  When reviewing code:
  - Identify security vulnerabilities
  - Check for performance issues
  - Verify adherence to coding standards
  - Suggest specific improvements

  Be thorough but concise in your feedback.""",
                      # tools restricts what the subagent can do (read-only here)
                      tools=["Read", "Grep", "Glob"],
                      # model overrides the default model for this subagent
                      model="sonnet",
                  ),
                  "test-runner": AgentDefinition(
                      description="Runs and analyzes test suites. Use for test execution and coverage analysis.",
                      prompt="""You are a test execution specialist. Run tests and provide clear analysis of results.

  Focus on:
  - Running test commands
  - Analyzing test output
  - Identifying failing tests
  - Suggesting fixes for failures""",
                      # Bash access lets this subagent run test commands
                      tools=["Bash", "Read", "Grep"],
                  ),
              },
          ),
      ):
          if hasattr(message, "result"):
              print(message.result)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Review the authentication module for security issues",
    options: {
      // Auto-approve these tools, including Agent for subagent invocation
      allowedTools: ["Read", "Grep", "Glob", "Agent"],
      agents: {
        "code-reviewer": {
          // description tells Claude when to use this subagent
          description:
            "Expert code review specialist. Use for quality, security, and maintainability reviews.",
          // prompt defines the subagent's behavior and expertise
          prompt: `You are a code review specialist with expertise in security, performance, and best practices.

  When reviewing code:
  - Identify security vulnerabilities
  - Check for performance issues
  - Verify adherence to coding standards
  - Suggest specific improvements

  Be thorough but concise in your feedback.`,
          // tools restricts what the subagent can do (read-only here)
          tools: ["Read", "Grep", "Glob"],
          // model overrides the default model for this subagent
          model: "sonnet"
        },
        "test-runner": {
          description:
            "Runs and analyzes test suites. Use for test execution and coverage analysis.",
          prompt: `You are a test execution specialist. Run tests and provide clear analysis of results.

  Focus on:
  - Running test commands
  - Analyzing test output
  - Identifying failing tests
  - Suggesting fixes for failures`,
          // Bash access lets this subagent run test commands
          tools: ["Bash", "Read", "Grep"]
        }
      }
    }
  })) {
    if ("result" in message) console.log(message.result);
  }
  ```
</CodeGroup>

<h3 id="agentdefinition-configuration">
  AgentDefinition 設定
</h3>

| フィールド             | 型                                                           | 必須  | 説明                                                                                                                                                 |
| :---------------- | :---------------------------------------------------------- | :-- | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| `description`     | `string`                                                    | はい  | このエージェントをいつ使用するかについての自然言語説明                                                                                                                        |
| `prompt`          | `string`                                                    | はい  | エージェントの役割と動作を定義するシステムプロンプト                                                                                                                         |
| `tools`           | `string[]`                                                  | いいえ | 許可されたツール名の配列。省略した場合、すべてのツールを継承します                                                                                                                  |
| `disallowedTools` | `string[]`                                                  | いいえ | エージェントのツールセットから削除するツール名の配列。MCP サーバーレベルのパターンも受け入れられます。`mcp__server` または `mcp__server__*` はそのサーバーからすべてのツールを削除し、`mcp__*` は任意のサーバーからすべての MCP ツールを削除します |
| `model`           | `string`                                                    | いいえ | このエージェントのモデルオーバーライド。`'fable'`、`'opus'`、`'sonnet'`、`'haiku'`、`'inherit'` などのエイリアス、または完全なモデル ID を受け入れます。省略した場合、メインモデルがデフォルトになります                     |
| `skills`          | `string[]`                                                  | いいえ | スタートアップ時にエージェントのコンテキストにプリロードするスキル名のリスト。リストされていないスキルは Skill ツール経由で呼び出し可能なままです                                                                       |
| `memory`          | `'user' \| 'project' \| 'local'`                            | いいえ | このエージェントのメモリソース                                                                                                                                    |
| `mcpServers`      | `(string \| object)[]`                                      | いいえ | このエージェントが利用可能な MCP サーバー（名前またはインライン設定）                                                                                                              |
| `initialPrompt`   | `string`                                                    | いいえ | このエージェントがメインスレッドエージェントとして実行される場合、最初のユーザーターンとして自動送信されます。エージェントがサブエージェントとして呼び出される場合は無視されます                                                           |
| `maxTurns`        | `number`                                                    | いいえ | エージェントが停止する前の最大 agentic ターン数                                                                                                                       |
| `background`      | `boolean`                                                   | いいえ | 呼び出されたときにこのエージェントをノンブロッキングバックグラウンドタスクとして実行します                                                                                                      |
| `effort`          | `'low' \| 'medium' \| 'high' \| 'xhigh' \| 'max' \| number` | いいえ | このエージェントの推論努力レベル                                                                                                                                   |
| `permissionMode`  | `PermissionMode`                                            | いいえ | このエージェント内のツール実行のパーミッションモード                                                                                                                         |

Python SDK では、`disallowedTools` や `mcpServers` などの複数単語のフィールド名は、Python の snake\_case 規約に従うのではなく、wire フォーマットに一致するように camelCase を保持します。詳細については、[`AgentDefinition` リファレンス](/docs/ja/agent-sdk/python#agentdefinition)を参照してください。

Claude Code v2.1.198 でサブエージェントの動作が 2 つ変更されました。

* サブエージェントはデフォルトでバックグラウンドで実行されます。[`run_in_background`](/docs/ja/agent-sdk/typescript) 入力を省略する Agent ツール呼び出しはバックグラウンドサブエージェントを起動し、Claude が続行する前に結果が必要な場合は `run_in_background: false` を設定します。v2.1.198 より前は、`run_in_background` を省略するとサブエージェントが同期的に実行されていました。特定のエージェントに対してバックグラウンド実行を強制するには、`background` フィールドを `true` に設定してください。これは Claude が要求する内容に関わらず適用されます。
* サブエージェントはメインセッションの拡張思考設定を継承します。以前のバージョンでは、メインセッションの設定に関わらず、サブエージェント内で拡張思考が無効になっていました。

<Note>
  Claude Code v2.1.172 以降、サブエージェントは独自のサブエージェントを生成できます。メインエージェントの 5 レベル下のサブエージェントは、フォアグラウンドまたはバックグラウンドで実行されるかどうかに関わらず、それ以上のサブエージェントを生成できません。サブエージェントが他のサブエージェントを生成するのを防ぐには、その `tools` 配列から `Agent` を省略するか、`disallowedTools` に追加してください。完全な深さルールについては、[ネストされたサブエージェント](/docs/ja/sub-agents#spawn-nested-subagents)を参照してください。
</Note>

<h3 id="filesystem-based-definition-alternative">
  ファイルシステムベースの定義（代替）
</h3>

`.claude/agents/` ディレクトリ内のマークダウンファイルとしてサブエージェントを定義することもできます。このアプローチの詳細については、[Claude Code サブエージェントドキュメント](/docs/ja/sub-agents)を参照してください。プログラム的に定義されたエージェントは、同じ名前のファイルシステムベースのエージェントより優先されます。

<Note>
  カスタムサブエージェントを定義しなくても、Claude は組み込みの `general-purpose` サブエージェントを生成できます。これは、特殊なエージェントを作成せずに研究または探索タスクを委譲するのに便利です。`allowedTools` に `Agent` を含めて、これらの呼び出しがパーミッション プロンプトなしで自動承認されるようにしてください。
</Note>

<h2 id="what-subagents-inherit">
  サブエージェントが継承するもの
</h2>

サブエージェントのコンテキストウィンドウは新しく開始されます（親の会話なし）が、空ではありません。親からサブエージェントへの唯一のチャネルは Agent ツールのプロンプト文字列なので、サブエージェントが必要とするファイルパス、エラーメッセージ、または決定をそのプロンプトに直接含めてください。

[`SendMessage`](/docs/ja/tools-reference) ツールを持つサブエージェントは、セッションで実行されている他の名前付きエージェントのリストで開始されるため、メッセージを送信できる名前を認識しています。Claude Code はセッションの最初のターンでサブエージェントにリストを自動的に追加します。[フォーク](/docs/ja/sub-agents#fork-the-current-conversation)は親の会話を継承するため、リストを取得しません。このリストには Claude Code v2.1.206 以降が必要です。

| サブエージェントが受け取るもの                                                                                                                 | サブエージェントが受け取らないもの                                         |
| :------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------- |
| 独自のシステムプロンプト（`AgentDefinition.prompt`）と Agent ツールのプロンプト                                                                         | 親の会話履歴またはツール結果                                            |
| プロジェクト CLAUDE.md（[`settingSources`](/docs/ja/agent-sdk/claude-code-features#control-filesystem-settings-with-settingsources) 経由でロード） | プリロードされたスキルコンテンツ（`AgentDefinition.skills` にリストされている場合を除く） |
| ツール定義（親から継承、または `tools` のサブセット）                                                                                                 | 親のシステムプロンプト                                               |

<Note>
  親はサブエージェントの最終メッセージを Agent ツール結果として逐語的に受け取りますが、独自の応答で要約する場合があります。サブエージェント出力を逐語的にユーザー向けの応答で保持するには、メイン `query()` 呼び出しに渡すプロンプトまたは `systemPrompt` オプションに指示を含めてください。
</Note>

サブエージェントを早期に終了させるレート制限などの API エラーは、その結果として配信されることはありません。レート制限、オーバーロード、またはサーバーエラーがすでにテキスト出力を生成しているフォアグラウンドサブエージェントを遮断した場合、Agent ツールはサブエージェントが完了しなかったというメモ付きでその部分的な出力を返します。何も出力しなかったサブエージェント、またはテキストのないツール呼び出しのみが出力だったサブエージェントは、エラーメッセージ「Agent terminated early due to an API error」の後にエラーの詳細が続いて失敗します。フォアグラウンドおよびバックグラウンドの動作については、[サブエージェントの API エラー](/docs/ja/sub-agents#api-errors-in-subagents)を参照してください。

この部分的な出力処理には Claude Code v2.1.199 以降が必要です。v2.1.199 では、レート制限、オーバーロード、またはサーバーエラーは、ツール呼び出しのみの形状を遮断メモのみを含む空の部分的な結果のままにしました。

<h2 id="invoke-subagents">
  サブエージェントの呼び出し
</h2>

<h3 id="automatic-invocation">
  自動呼び出し
</h3>

Claude は、タスクと各サブエージェントの `description` に基づいて、サブエージェントをいつ呼び出すかを自動的に決定します。例えば、説明が「クエリチューニング用のパフォーマンス最適化スペシャリスト」である `performance-optimizer` サブエージェントを定義した場合、プロンプトでクエリの最適化について言及すると、Claude はそれを呼び出します。

Claude がタスクを正しいサブエージェントにマッチングできるように、明確で具体的な説明を書いてください。

<h3 id="explicit-invocation">
  明示的な呼び出し
</h3>

Claude が特定のサブエージェントを使用することを保証するには、プロンプトで名前を言及してください：

```text theme={null}
"Use the code-reviewer agent to check the authentication module"
```

これは自動マッチングをバイパスし、名前付きサブエージェントを直接呼び出します。

<h3 id="dynamic-agent-configuration">
  動的エージェント設定
</h3>

実行時の条件に基づいて、エージェント定義を動的に作成できます。この例では、異なる厳密性レベルを持つセキュリティレビュアーを作成し、厳密なレビューにはより強力なモデルを使用します。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


  # Factory function that returns an AgentDefinition
  # This pattern lets you customize agents based on runtime conditions
  def create_security_agent(security_level: str) -> AgentDefinition:
      is_strict = security_level == "strict"
      return AgentDefinition(
          description="Security code reviewer",
          # Customize the prompt based on strictness level
          prompt=f"You are a {'strict' if is_strict else 'balanced'} security reviewer...",
          tools=["Read", "Grep", "Glob"],
          # Key insight: use a more capable model for high-stakes reviews
          model="opus" if is_strict else "sonnet",
      )


  async def main():
      # The agent is created at query time, so each request can use different settings
      async for message in query(
          prompt="Review this PR for security issues",
          options=ClaudeAgentOptions(
              allowed_tools=["Read", "Grep", "Glob", "Agent"],
              agents={
                  # Call the factory with your desired configuration
                  "security-reviewer": create_security_agent("strict")
              },
          ),
      ):
          if hasattr(message, "result"):
              print(message.result)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query, type AgentDefinition } from "@anthropic-ai/claude-agent-sdk";

  // Factory function that returns an AgentDefinition
  // This pattern lets you customize agents based on runtime conditions
  function createSecurityAgent(securityLevel: "basic" | "strict"): AgentDefinition {
    const isStrict = securityLevel === "strict";
    return {
      description: "Security code reviewer",
      // Customize the prompt based on strictness level
      prompt: `You are a ${isStrict ? "strict" : "balanced"} security reviewer...`,
      tools: ["Read", "Grep", "Glob"],
      // Key insight: use a more capable model for high-stakes reviews
      model: isStrict ? "opus" : "sonnet"
    };
  }

  // The agent is created at query time, so each request can use different settings
  for await (const message of query({
    prompt: "Review this PR for security issues",
    options: {
      allowedTools: ["Read", "Grep", "Glob", "Agent"],
      agents: {
        // Call the factory with your desired configuration
        "security-reviewer": createSecurityAgent("strict")
      }
    }
  })) {
    if ("result" in message) console.log(message.result);
  }
  ```
</CodeGroup>

<h2 id="detect-subagent-invocation">
  サブエージェント呼び出しの検出
</h2>

Claude はサブエージェントを Agent ツール経由で呼び出します。サブエージェントが呼び出されたときを検出するには、`name` が `"Agent"` である `tool_use` ブロックをチェックしてください。サブエージェントのコンテキスト内からのメッセージには `parent_tool_use_id` フィールドが含まれます。

<Note>
  ツール名は Claude Code v2.1.63 で `"Task"` から `"Agent"` に変更されました。現在の SDK リリースは `tool_use` ブロックで `"Agent"` を出力しますが、`system:init` ツールリストと `result.permission_denials[].tool_name` では引き続き `"Task"` を使用します。SDK バージョン全体での互換性を確保するために、`block.name` で両方の値をチェックしてください。
</Note>

メッセージ構造は SDK 間で異なります。Python では、コンテンツブロックは `message.content` 経由で直接アクセスされます。TypeScript では、`SDKAssistantMessage` が Claude API メッセージをラップするため、コンテンツは `message.message.content` 経由でアクセスされます。

この例は、ストリーミングされたメッセージを反復処理し、サブエージェントが呼び出されたときと、その後のメッセージがそのサブエージェントの実行コンテキスト内から発信されたときをログに記録します。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ToolUseBlock


  async def main():
      async for message in query(
          prompt="Use the code-reviewer agent to review this codebase",
          options=ClaudeAgentOptions(
              allowed_tools=["Read", "Glob", "Grep", "Agent"],
              agents={
                  "code-reviewer": AgentDefinition(
                      description="Expert code reviewer.",
                      prompt="Analyze code quality and suggest improvements.",
                      tools=["Read", "Glob", "Grep"],
                  )
              },
          ),
      ):
          # Check for subagent invocation. Match both names: older SDK
          # versions emitted "Task", current versions emit "Agent".
          if hasattr(message, "content") and message.content:
              for block in message.content:
                  if isinstance(block, ToolUseBlock) and block.name in (
                      "Task",
                      "Agent",
                  ):
                      print(f"Subagent invoked: {block.input.get('subagent_type')}")

          # Check if this message is from within a subagent's context
          if hasattr(message, "parent_tool_use_id") and message.parent_tool_use_id:
              print("  (running inside subagent)")

          if hasattr(message, "result"):
              print(message.result)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Use the code-reviewer agent to review this codebase",
    options: {
      allowedTools: ["Read", "Glob", "Grep", "Agent"],
      agents: {
        "code-reviewer": {
          description: "Expert code reviewer.",
          prompt: "Analyze code quality and suggest improvements.",
          tools: ["Read", "Glob", "Grep"]
        }
      }
    }
  })) {
    const msg = message as any;

    // Check for subagent invocation. Match both names: older SDK versions
    // emitted "Task", current versions emit "Agent".
    for (const block of msg.message?.content ?? []) {
      if (block.type === "tool_use" && (block.name === "Task" || block.name === "Agent")) {
        console.log(`Subagent invoked: ${block.input.subagent_type}`);
      }
    }

    // Check if this message is from within a subagent's context
    if (msg.parent_tool_use_id) {
      console.log("  (running inside subagent)");
    }

    if ("result" in message) {
      console.log(message.result);
    }
  }
  ```
</CodeGroup>

<h2 id="resume-subagents">
  サブエージェントの再開
</h2>

サブエージェントを再開して、中断したところから続行できます。再開されたサブエージェントは、以前のすべてのツール呼び出し、結果、推論を含む完全な会話履歴を保持します。

サブエージェントが完了すると、Agent ツール結果には `agentId: <id>` を含むテキストブロックが含まれます。組み込みの [`Explore` および `Plan` エージェント](/docs/ja/sub-agents#built-in-subagents) はワンショットであり、`agentId` を返さないため、再開が必要な場合はカスタムエージェントまたは `general-purpose` を使用してください。サブエージェントをプログラム的に再開するには：

1. **セッション ID をキャプチャする**: 最初のクエリ中にメッセージから `session_id` を抽出します
2. **エージェント ID を抽出する**: Agent ツール結果テキストから `agentId` を解析します
3. **セッションを再開する**: 2 番目のクエリのオプションで `resume: sessionId` を渡し、プロンプトにエージェント ID を含めます

<Note>
  サブエージェントのトランスクリプトにアクセスするには、同じセッションを再開する必要があります。各 `query()` 呼び出しはデフォルトで新しいセッションを開始するため、同じセッションで続行するには `resume: sessionId` を渡してください。

  カスタムエージェントを使用する場合は、両方のクエリの `agents` パラメータで同じエージェント定義を渡してください。
</Note>

以下の例は、カスタム `endpoint-finder` エージェントを定義しています。最初のクエリはそれを実行し、Agent ツール結果からセッション ID とエージェント ID をキャプチャします。その後、2 番目のクエリはセッションを再開して、最初の分析からのコンテキストが必要なフォローアップ質問をします。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  import re
  from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ToolResultBlock

  AGENTS = {
      "endpoint-finder": AgentDefinition(
          description="Locates and catalogs API endpoints in a codebase.",
          prompt="You find and document API endpoints. Report each endpoint's path, method, and handler.",
          tools=["Read", "Grep", "Glob"],
      )
  }


  def extract_agent_id(block: ToolResultBlock) -> str | None:
      """Extract agentId from an Agent tool result's text content."""
      parts = block.content if isinstance(block.content, list) else [{"text": block.content}]
      for part in parts:
          if match := re.search(r"agentId:\s*([\w-]+)", part.get("text") or ""):
              return match.group(1)
      return None


  async def main():
      agent_id = None
      session_id = None

      # First invocation - run the endpoint-finder subagent
      try:
          async for message in query(
              prompt="Use the endpoint-finder agent to find all API endpoints in this codebase",
              options=ClaudeAgentOptions(allowed_tools=["Read", "Grep", "Glob", "Agent"], agents=AGENTS),
          ):
              # Capture session_id from ResultMessage (needed to resume this session)
              if hasattr(message, "session_id"):
                  session_id = message.session_id
              # Search tool results for the agentId trailer
              for block in getattr(message, "content", None) or []:
                  if isinstance(block, ToolResultBlock):
                      agent_id = extract_agent_id(block) or agent_id
              # Print the final result
              if hasattr(message, "result"):
                  print(message.result)
      except Exception as error:
          # A single-shot query() raises after yielding an error result,
          # so session_id and agent_id have already been captured by the loop above.
          print(f"Session ended with an error: {error}")

      # Second invocation - resume and ask follow-up
      if agent_id and session_id:
          async for message in query(
              prompt=f"Resume agent {agent_id} and list the top 3 most complex endpoints",
              options=ClaudeAgentOptions(
                  allowed_tools=["Read", "Grep", "Glob", "Agent"], agents=AGENTS, resume=session_id
              ),
          ):
              if hasattr(message, "result"):
                  print(message.result)
      else:
          print("No agentId found in the first query, so there is no subagent to resume.")


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query, type SDKMessage } from "@anthropic-ai/claude-agent-sdk";

  const agents = {
    "endpoint-finder": {
      description: "Locates and catalogs API endpoints in a codebase.",
      prompt: "You find and document API endpoints. Report each endpoint's path, method, and handler.",
      tools: ["Read", "Grep", "Glob"]
    }
  };

  // Stringify content to search for agentId without traversing nested block types
  function extractAgentId(message: SDKMessage): string | undefined {
    if (message.type !== "assistant" && message.type !== "user") return undefined;
    const content = JSON.stringify(message.message.content);
    const match = content.match(/agentId:\s*([\w-]+)/);
    return match?.[1];
  }

  let agentId: string | undefined;
  let sessionId: string | undefined;

  // First invocation - run the endpoint-finder subagent
  try {
    for await (const message of query({
      prompt: "Use the endpoint-finder agent to find all API endpoints in this codebase",
      options: { allowedTools: ["Read", "Grep", "Glob", "Agent"], agents }
    })) {
      // Capture session_id from ResultMessage (needed to resume this session)
      if ("session_id" in message) sessionId = message.session_id;
      // Search message content for the agentId (appears in Agent tool results)
      const extractedId = extractAgentId(message);
      if (extractedId) agentId = extractedId;
      // Print the final result
      if ("result" in message) console.log(message.result);
    }
  } catch (error) {
    // A single-shot query() throws after yielding an error result,
    // so sessionId and agentId have already been captured by the loop above.
    console.error(`Session ended with an error: ${error}`);
  }

  // Second invocation - resume and ask follow-up
  if (agentId && sessionId) {
    for await (const message of query({
      prompt: `Resume agent ${agentId} and list the top 3 most complex endpoints`,
      options: { allowedTools: ["Read", "Grep", "Glob", "Agent"], agents, resume: sessionId }
    })) {
      if ("result" in message) console.log(message.result);
    }
  } else {
    console.log("No agentId found in the first query, so there is no subagent to resume.");
  }
  ```
</CodeGroup>

サブエージェントのトランスクリプトはメイン会話とは独立して永続化されます：

* **メイン会話の圧縮**: メイン会話が圧縮されると、サブエージェントのトランスクリプトは影響を受けません。これらは別のファイルに保存されます。
* **セッション永続化**: サブエージェントのトランスクリプトはセッション内で永続化されます。同じセッションを再開することで、Claude Code を再起動した後にサブエージェントを再開できます。
* **自動クリーンアップ**: トランスクリプトは `cleanupPeriodDays` 設定に基づいてクリーンアップされます（デフォルト：30 日）。

<h2 id="tool-restrictions-2">
  ツール制限
</h2>

サブエージェントは `tools` フィールド経由で制限されたツールアクセスを持つことができます。

* **フィールドを省略**: エージェントは利用可能なすべてのツールを継承します（デフォルト）
* **ツールを指定**: エージェントはリストされたツールのみを使用できます

この例では、コードを検査できるが、ファイルを変更したりコマンドを実行したりできない読み取り専用分析エージェントを作成します。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


  async def main():
      async for message in query(
          prompt="Analyze the architecture of this codebase",
          options=ClaudeAgentOptions(
              allowed_tools=["Read", "Grep", "Glob", "Agent"],
              agents={
                  "code-analyzer": AgentDefinition(
                      description="Static code analysis and architecture review",
                      prompt="""You are a code architecture analyst. Analyze code structure,
  identify patterns, and suggest improvements without making changes.""",
                      # Read-only tools: no Edit, Write, or Bash access
                      tools=["Read", "Grep", "Glob"],
                  )
              },
          ),
      ):
          if hasattr(message, "result"):
              print(message.result)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Analyze the architecture of this codebase",
    options: {
      allowedTools: ["Read", "Grep", "Glob", "Agent"],
      agents: {
        "code-analyzer": {
          description: "Static code analysis and architecture review",
          prompt: `You are a code architecture analyst. Analyze code structure,
  identify patterns, and suggest improvements without making changes.`,
          // Read-only tools: no Edit, Write, or Bash access
          tools: ["Read", "Grep", "Glob"]
        }
      }
    }
  })) {
    if ("result" in message) console.log(message.result);
  }
  ```
</CodeGroup>

<h3 id="common-tool-combinations">
  一般的なツール組み合わせ
</h3>

| ユースケース   | ツール                                 | 説明                                 |
| :------- | :---------------------------------- | :--------------------------------- |
| 読み取り専用分析 | `Read`、`Grep`、`Glob`                | コードを検査できますが、変更または実行はできません          |
| テスト実行    | `Bash`、`Read`、`Grep`                | コマンドを実行し、出力を分析できます                 |
| コード変更    | `Read`、`Edit`、`Write`、`Grep`、`Glob` | コマンド実行なしで完全な読み取り/書き込みアクセス          |
| 完全アクセス   | すべてのツール                             | 親からすべてのツールを継承します（`tools` フィールドを省略） |

<h2 id="scale-up-with-dynamic-workflows">
  動的ワークフローでスケールアップ
</h2>

サブエージェントは、ターンごとに数個の委譲されたタスクに適しています。数十から数百のエージェントを調整する実行の場合は、`Workflow` ツールを使用してください。これにより、オーケストレーションを会話コンテキストの外で実行時が実行するスクリプトに移動します。[動的ワークフロー](/docs/ja/workflows)を参照して、ワークフローがターンごとのサブエージェント委譲とどのように異なるかを確認してください。

`Workflow` ツールは TypeScript Agent SDK v0.3.149 以降で利用可能です。`allowedTools` に `Workflow` を含めてワークフロー実行を自動承認します。ツール入力および出力スキーマは [TypeScript リファレンス](/docs/ja/agent-sdk/typescript#workflow)に記載されています。

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

<h3 id="claude-not-delegating-to-subagents">
  Claude がサブエージェントに委譲していない
</h3>

Claude がサブエージェントに委譲する代わりにタスクを直接完了する場合：

* **Agent ツールの呼び出しが承認されていることを確認する**: `allowedTools` に `Agent` を含めて、サブエージェント呼び出しを自動承認します。これがない場合、Agent 呼び出しは `canUseTool` コールバックにフォールスルーするか、`dontAsk` モードでは拒否されます
* **明示的なプロンプトを使用する**: プロンプトでサブエージェントを名前で言及します。例えば「code-reviewer エージェントを使用して...」のように
* **明確な説明を書く**: サブエージェントをいつ使用すべきかを正確に説明し、Claude がタスクを適切にマッチングできるようにします

<h3 id="filesystem-based-agents-not-loading">
  ファイルシステムベースのエージェントが読み込まれていない
</h3>

Claude Code は `~/.claude/agents/` と `.claude/agents/` を監視し、数秒以内に新しいまたは編集されたエージェントファイルを検出します。再起動は不要です。定義が表示されない場合は、以下の原因を確認してください：

* **新しい `agents` ディレクトリ**: ウォッチャーはセッション開始時に存在していたディレクトリのみをカバーするため、新しいディレクトリ内の最初のファイルはセッション再起動が必要です。これが最も一般的な原因です。
* **無効なフロントマターまたは重複した `name`**: ファイルの YAML を確認し、既存のエージェントが同じ `name` を使用していないか確認してください。
* **`--disable-slash-commands`**: このフラグで開始されたセッションはこれらのディレクトリを監視せず、新しいファイルを読み込むには常に再起動が必要です。
* **同じ名前のプログラマティックエージェント**: `query()` に渡される `agents` は、同じ名前のファイルシステムエージェントをオーバーライドします。

ファイル形式については、[サブエージェントファイルの書き方](/docs/ja/sub-agents#write-subagent-files)を参照してください。

<h3 id="long-prompt-failures-on-windows">
  Windows での長いプロンプトの失敗
</h3>

Windows では、非常に長いプロンプトを持つサブエージェントは、コマンドラインの長さ制限である 8191 文字により失敗する場合があります。プロンプトを簡潔に保つか、複雑な指示にはファイルシステムベースのエージェントを使用してください。

<h2 id="related-documentation">
  関連ドキュメント
</h2>

* [Claude Code サブエージェント](/docs/ja/sub-agents)：ファイルシステムベースの定義を含む包括的なサブエージェントドキュメント
* [動的ワークフロー](/docs/ja/workflows)：スクリプトから多くのサブエージェントをオーケストレートして、1 つの会話には大きすぎるジョブを実行します
* [SDK 概要](/docs/ja/agent-sdk/overview)：Claude Agent SDK の開始方法
