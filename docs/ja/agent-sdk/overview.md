> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Agent SDK の概要

> Claude Code をライブラリとして使用して、本番環境対応の AI エージェントを構築します

ファイルを自動的に読み取り、コマンドを実行し、ウェブを検索し、コードを編集するなど、さらに多くのことができる AI エージェントを構築します。Agent SDK は、Claude Code を強化する同じツール、エージェントループ、およびコンテキスト管理を提供し、Python と TypeScript でプログラム可能です。エージェントハーネス設計の背景については、ブログの「[A harness for every task: dynamic workflows in Claude Code](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)」を参照してください。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions


  async def main():
      async for message in query(
          prompt="Find and fix the bug in auth.py",
          options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
      ):
          print(message)  # Claude reads the file, finds the bug, edits it


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Find and fix the bug in auth.ts",
    options: { allowedTools: ["Read", "Edit", "Bash"] }
  })) {
    console.log(message); // Claude reads the file, finds the bug, edits it
  }
  ```
</CodeGroup>

Agent SDK には、ファイルの読み取り、コマンドの実行、コードの編集用の組み込みツールが含まれているため、ツール実行を実装することなく、エージェントはすぐに動作を開始できます。クイックスタートに進むか、SDK で構築された実際のエージェントを探索してください。

<CardGroup cols={2}>
  <Card title="クイックスタート" icon="play" href="/docs/ja/agent-sdk/quickstart">
    数分でバグ修正エージェントを構築します
  </Card>

  <Card title="エージェントの例" icon="star" href="https://github.com/anthropics/claude-agent-sdk-demos">
    メールアシスタント、リサーチエージェント、その他
  </Card>
</CardGroup>

<h2 id="get-started">
  はじめに
</h2>

<Steps>
  <Step title="SDK をインストールします">
    <Tabs>
      <Tab title="TypeScript">
        ```bash theme={null}
        npm install @anthropic-ai/claude-agent-sdk
        ```
      </Tab>

      <Tab title="Python (uv)">
        [uv](https://docs.astral.sh/uv/) は、仮想環境を自動的に処理する高速な Python パッケージマネージャーです。

        ```bash theme={null}
        uv init
        uv add claude-agent-sdk
        ```
      </Tab>

      <Tab title="Python (pip)">
        仮想環境を作成してアクティベートしてから、パッケージをインストールします。仮想環境にインストールすることで、最近の Debian、Ubuntu、Homebrew インストールのシステム Python が venv 外の `pip install` に対して返す `error: externally-managed-environment` エラーを回避できます。

        macOS または Linux の場合：

        ```bash theme={null}
        python3 -m venv .venv
        source .venv/bin/activate
        pip install claude-agent-sdk
        ```

        Windows の場合：

        ```powershell theme={null}
        py -m venv .venv
        .venv\Scripts\Activate.ps1
        pip install claude-agent-sdk
        ```

        PowerShell が実行ポリシーエラーで `Activate.ps1` をブロックする場合は、まず `Set-ExecutionPolicy -Scope Process RemoteSigned` を実行してください。

        Python パッケージには Python 3.10 以降が必要です。pip が `No matching distribution found for claude-agent-sdk` と報告する場合、インタープリターは 3.10 より古いバージョンです。macOS または Linux では `python3 --version` を実行するか、Windows では `py --version` を実行してバージョンを確認してください。
      </Tab>
    </Tabs>

    <Note>
      TypeScript SDK は、プラットフォーム用のネイティブ Claude Code バイナリをオプションの依存関係としてバンドルしているため、Claude Code を別途インストールする必要はありません。
    </Note>
  </Step>

  <Step title="API キーを設定します">
    [Console](https://platform.claude.com/) から API キーを取得し、環境変数として設定します。

    macOS または Linux の場合：

    ```bash theme={null}
    export ANTHROPIC_API_KEY=sk-ant-xxxxx
    ```

    Windows PowerShell の場合：

    ```powershell theme={null}
    $env:ANTHROPIC_API_KEY = "sk-ant-xxxxx"
    ```

    SDK はサードパーティ API プロバイダーを介した認証もサポートしています。

    * **Amazon Bedrock**: `CLAUDE_CODE_USE_BEDROCK=1` 環境変数を設定し、AWS 認証情報を構成します
    * **Claude Platform on AWS**: `CLAUDE_CODE_USE_ANTHROPIC_AWS=1` と `ANTHROPIC_AWS_WORKSPACE_ID` を設定し、AWS 認証情報を構成します
    * **Google Cloud の Agent Platform**: `CLAUDE_CODE_USE_VERTEX=1` 環境変数を設定し、Google Cloud 認証情報を構成します
    * **Microsoft Azure**: `CLAUDE_CODE_USE_FOUNDRY=1` 環境変数を設定し、Azure 認証情報を構成します

    詳細については、[Amazon Bedrock](/docs/ja/amazon-bedrock)、[Claude Platform on AWS](/docs/ja/claude-platform-on-aws)、[Google Cloud の Agent Platform](/docs/ja/google-vertex-ai)、または [Microsoft Foundry](/docs/ja/microsoft-foundry) のセットアップガイドを参照してください。

    <Note>
      事前に承認されていない限り、Anthropic は、Claude Agent SDK で構築されたエージェントを含む、サードパーティ開発者が claude.ai ログインまたはレート制限を提供することを許可していません。代わりに、このドキュメントで説明されている API キー認証方法を使用してください。
    </Note>
  </Step>

  <Step title="最初のエージェントを実行します">
    この例は、組み込みツールを使用して現在のディレクトリ内のファイルをリストするエージェントを作成します。

    <CodeGroup>
      ```python Python theme={null}
      import asyncio
      from claude_agent_sdk import query, ClaudeAgentOptions


      async def main():
          async for message in query(
              prompt="What files are in this directory?",
              options=ClaudeAgentOptions(allowed_tools=["Bash", "Glob"]),
          ):
              if hasattr(message, "result"):
                  print(message.result)


      asyncio.run(main())
      ```

      ```typescript TypeScript theme={null}
      import { query } from "@anthropic-ai/claude-agent-sdk";

      for await (const message of query({
        prompt: "What files are in this directory?",
        options: { allowedTools: ["Bash", "Glob"] }
      })) {
        if ("result" in message) console.log(message.result);
      }
      ```
    </CodeGroup>
  </Step>
</Steps>

**構築する準備はできていますか？** [クイックスタート](/docs/ja/agent-sdk/quickstart)に従って、数分でバグを見つけて修正するエージェントを作成します。

<h2 id="capabilities">
  機能
</h2>

Claude Code を強力にするすべてのものが SDK で利用可能です。

<Tabs>
  <Tab title="組み込みツール">
    エージェントは、ファイルの読み取り、コマンドの実行、コードベースの検索をすぐに実行できます。主要なツールは次のとおりです。

    | ツール                                                                         | 機能                                       |
    | --------------------------------------------------------------------------- | ---------------------------------------- |
    | **Read**                                                                    | 作業ディレクトリ内の任意のファイルを読み取ります                 |
    | **Write**                                                                   | 新しいファイルを作成します                            |
    | **Edit**                                                                    | 既存ファイルに正確な編集を加えます                        |
    | **Bash**                                                                    | ターミナルコマンド、スクリプト、git 操作を実行します             |
    | **Monitor**                                                                 | バックグラウンドスクリプトを監視し、各出力行をイベントとして反応します      |
    | **Glob**                                                                    | パターン（`**/*.ts`、`src/**/*.py`）でファイルを検索します |
    | **Grep**                                                                    | 正規表現でファイルコンテンツを検索します                     |
    | **WebSearch**                                                               | 現在の情報をウェブで検索します                          |
    | **WebFetch**                                                                | ウェブページコンテンツを取得して解析します                    |
    | **[AskUserQuestion](/docs/ja/agent-sdk/user-input#handle-clarifying-questions)** | 複数選択オプション付きで、ユーザーに明確化の質問をします             |

    この例は、コードベースで TODO コメントを検索するエージェントを作成します。

    <CodeGroup>
      ```python Python theme={null}
      import asyncio
      from claude_agent_sdk import query, ClaudeAgentOptions


      async def main():
          async for message in query(
              prompt="Find all TODO comments and create a summary",
              options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"]),
          ):
              if hasattr(message, "result"):
                  print(message.result)


      asyncio.run(main())
      ```

      ```typescript TypeScript theme={null}
      import { query } from "@anthropic-ai/claude-agent-sdk";

      for await (const message of query({
        prompt: "Find all TODO comments and create a summary",
        options: { allowedTools: ["Read", "Glob", "Grep"] }
      })) {
        if ("result" in message) console.log(message.result);
      }
      ```
    </CodeGroup>
  </Tab>

  <Tab title="Hooks">
    エージェントライフサイクルの重要なポイントでカスタムコードを実行します。SDK hooks はコールバック関数を使用して、エージェントの動作を検証、ログ、ブロック、または変換します。

    **利用可能な hooks:** `PreToolUse`、`PostToolUse`、`Stop`、`SessionStart`、`SessionEnd`、`UserPromptSubmit` など。

    この例は、すべてのファイル変更を監査ファイルにログします。

    <CodeGroup>
      ```python Python theme={null}
      import asyncio
      from datetime import datetime
      from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher


      async def log_file_change(input_data, tool_use_id, context):
          file_path = input_data.get("tool_input", {}).get("file_path", "unknown")
          with open("./audit.log", "a") as f:
              f.write(f"{datetime.now()}: modified {file_path}\n")
          return {}


      async def main():
          async for message in query(
              prompt="Refactor utils.py to improve readability",
              options=ClaudeAgentOptions(
                  permission_mode="acceptEdits",
                  hooks={
                      "PostToolUse": [
                          HookMatcher(matcher="Edit|Write", hooks=[log_file_change])
                      ]
                  },
              ),
          ):
              if hasattr(message, "result"):
                  print(message.result)


      asyncio.run(main())
      ```

      ```typescript TypeScript theme={null}
      import { query, HookCallback } from "@anthropic-ai/claude-agent-sdk";
      import { appendFile } from "fs/promises";

      const logFileChange: HookCallback = async (input) => {
        const filePath = (input as any).tool_input?.file_path ?? "unknown";
        await appendFile("./audit.log", `${new Date().toISOString()}: modified ${filePath}\n`);
        return {};
      };

      for await (const message of query({
        prompt: "Refactor utils.py to improve readability",
        options: {
          permissionMode: "acceptEdits",
          hooks: {
            PostToolUse: [{ matcher: "Edit|Write", hooks: [logFileChange] }]
          }
        }
      })) {
        if ("result" in message) console.log(message.result);
      }
      ```
    </CodeGroup>

    [hooks の詳細を学ぶ →](/docs/ja/agent-sdk/hooks)
  </Tab>

  <Tab title="サブエージェント">
    特定のサブタスクを処理するために特化したエージェントを生成します。メインエージェントが作業を委譲し、サブエージェントが結果を報告します。

    特化した指示を持つカスタムエージェントを定義します。サブエージェントは Agent ツール経由で呼び出されるため、`allowedTools` に `Agent` を含めて、それらの呼び出しを自動承認します。

    <CodeGroup>
      ```python Python theme={null}
      import asyncio
      from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


      async def main():
          async for message in query(
              prompt="Use the code-reviewer agent to review this codebase",
              options=ClaudeAgentOptions(
                  allowed_tools=["Read", "Glob", "Grep", "Agent"],
                  agents={
                      "code-reviewer": AgentDefinition(
                          description="Expert code reviewer for quality and security reviews.",
                          prompt="Analyze code quality and suggest improvements.",
                          tools=["Read", "Glob", "Grep"],
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
        prompt: "Use the code-reviewer agent to review this codebase",
        options: {
          allowedTools: ["Read", "Glob", "Grep", "Agent"],
          agents: {
            "code-reviewer": {
              description: "Expert code reviewer for quality and security reviews.",
              prompt: "Analyze code quality and suggest improvements.",
              tools: ["Read", "Glob", "Grep"]
            }
          }
        }
      })) {
        if ("result" in message) console.log(message.result);
      }
      ```
    </CodeGroup>

    サブエージェントのコンテキスト内からのメッセージには `parent_tool_use_id` フィールドが含まれており、どのメッセージがどのサブエージェント実行に属しているかを追跡できます。

    [サブエージェントの詳細を学ぶ →](/docs/ja/agent-sdk/subagents)
  </Tab>

  <Tab title="MCP">
    Model Context Protocol を介して外部システムに接続します。データベース、ブラウザ、API、および[数百以上](https://github.com/modelcontextprotocol/servers)。

    この例は、[Playwright MCP サーバー](https://github.com/microsoft/playwright-mcp)を接続して、エージェントにブラウザ自動化機能を提供します。

    <CodeGroup>
      ```python Python theme={null}
      import asyncio
      from claude_agent_sdk import query, ClaudeAgentOptions


      async def main():
          async for message in query(
              prompt="Open example.com and describe what you see",
              options=ClaudeAgentOptions(
                  mcp_servers={
                      "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}
                  }
              ),
          ):
              if hasattr(message, "result"):
                  print(message.result)


      asyncio.run(main())
      ```

      ```typescript TypeScript theme={null}
      import { query } from "@anthropic-ai/claude-agent-sdk";

      for await (const message of query({
        prompt: "Open example.com and describe what you see",
        options: {
          mcpServers: {
            playwright: { command: "npx", args: ["@playwright/mcp@latest"] }
          }
        }
      })) {
        if ("result" in message) console.log(message.result);
      }
      ```
    </CodeGroup>

    [MCP の詳細を学ぶ →](/docs/ja/agent-sdk/mcp)
  </Tab>

  <Tab title="権限">
    エージェントが使用できるツールを正確に制御します。安全な操作を許可し、危険な操作をブロックするか、機密アクションの承認を要求します。

    <Note>
      対話的な承認プロンプトと `AskUserQuestion` ツールについては、[承認とユーザー入力の処理](/docs/ja/agent-sdk/user-input)を参照してください。
    </Note>

    この例は、コードを分析できるが変更できない読み取り専用エージェントを作成します。`allowed_tools` は `Read`、`Glob`、および `Grep` を事前承認します。

    <CodeGroup>
      ```python Python theme={null}
      import asyncio
      from claude_agent_sdk import query, ClaudeAgentOptions


      async def main():
          async for message in query(
              prompt="Review this code for best practices",
              options=ClaudeAgentOptions(
                  allowed_tools=["Read", "Glob", "Grep"],
              ),
          ):
              if hasattr(message, "result"):
                  print(message.result)


      asyncio.run(main())
      ```

      ```typescript TypeScript theme={null}
      import { query } from "@anthropic-ai/claude-agent-sdk";

      for await (const message of query({
        prompt: "Review this code for best practices",
        options: {
          allowedTools: ["Read", "Glob", "Grep"]
        }
      })) {
        if ("result" in message) console.log(message.result);
      }
      ```
    </CodeGroup>

    [権限の詳細を学ぶ →](/docs/ja/agent-sdk/permissions)
  </Tab>

  <Tab title="セッション">
    複数の交換にわたってコンテキストを維持します。Claude は読み取ったファイル、実行した分析、および会話履歴を記憶します。後でセッションを再開するか、異なるアプローチを探索するためにフォークします。

    この例は、最初のクエリからセッション ID をキャプチャし、その後、完全なコンテキストで続行するために再開します。

    <CodeGroup>
      ```python Python theme={null}
      import asyncio
      from claude_agent_sdk import query, ClaudeAgentOptions, SystemMessage, ResultMessage


      async def main():
          session_id = None

          # First query: capture the session ID
          async for message in query(
              prompt="Read the authentication module",
              options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"]),
          ):
              if isinstance(message, SystemMessage) and message.subtype == "init":
                  session_id = message.data["session_id"]

          # Resume with full context from the first query
          async for message in query(
              prompt="Now find all places that call it",  # "it" = auth module
              options=ClaudeAgentOptions(resume=session_id),
          ):
              if isinstance(message, ResultMessage):
                  print(message.result)


      asyncio.run(main())
      ```

      ```typescript TypeScript theme={null}
      import { query } from "@anthropic-ai/claude-agent-sdk";

      let sessionId: string | undefined;

      // First query: capture the session ID
      for await (const message of query({
        prompt: "Read the authentication module",
        options: { allowedTools: ["Read", "Glob"] }
      })) {
        if (message.type === "system" && message.subtype === "init") {
          sessionId = message.session_id;
        }
      }

      // Resume with full context from the first query
      for await (const message of query({
        prompt: "Now find all places that call it", // "it" = auth module
        options: { resume: sessionId }
      })) {
        if ("result" in message) console.log(message.result);
      }
      ```
    </CodeGroup>

    [セッションの詳細を学ぶ →](/docs/ja/agent-sdk/sessions)
  </Tab>
</Tabs>

<h3 id="claude-code-features">
  Claude Code の機能
</h3>

SDK はまた Claude Code のファイルシステムベースの構成をサポートしています。デフォルトオプションでは、SDK は作業ディレクトリの `.claude/` と `~/.claude/` からこれらを読み込みます。どのソースを読み込むかを制限するには、オプションで `setting_sources`（Python）または `settingSources`（TypeScript）を設定します。

| 機能                                               | 説明                                             | 場所                                  |
| ------------------------------------------------ | ---------------------------------------------- | ----------------------------------- |
| [Skills](/docs/ja/agent-sdk/skills)                   | Claude が自動的に使用するか、`/name` で呼び出す特化した機能          | `.claude/skills/*/SKILL.md`         |
| [Commands](/docs/ja/agent-sdk/slash-commands)         | レガシー形式のカスタムコマンド。新しいカスタムコマンドには skills を使用してください | `.claude/commands/*.md`             |
| [Memory](/docs/ja/agent-sdk/modifying-system-prompts) | プロジェクトコンテキストと指示                                | `CLAUDE.md` または `.claude/CLAUDE.md` |
| [Plugins](/docs/ja/agent-sdk/plugins)                 | skills、エージェント、hooks、および MCP サーバーで拡張            | `plugins` オプション経由でプログラム的に           |

<h2 id="compare-the-agent-sdk-to-other-claude-tools">
  Agent SDK と他の Claude ツールを比較します
</h2>

Claude Platform は Claude で構築するための複数の方法を提供しています。Agent SDK がどのように適合するかは次のとおりです。

<Tabs>
  <Tab title="Agent SDK vs Client SDK">
    [Anthropic Client SDK](https://platform.claude.com/docs/ja/api/client-sdks) は直接 API アクセスを提供します。プロンプトを送信し、ツール実行を自分で実装します。**Agent SDK** は、組み込みツール実行を備えた Claude を提供します。

    Client SDK では、ツールループを実装します。Agent SDK では、Claude がそれを処理します。

    <CodeGroup>
      ```python Python theme={null}
      # Client SDK: You implement the tool loop
      response = client.messages.create(...)
      while response.stop_reason == "tool_use":
          result = your_tool_executor(response.tool_use)
          response = client.messages.create(tool_result=result, **params)

      # Agent SDK: Claude handles tools autonomously
      async for message in query(prompt="Fix the bug in auth.py"):
          print(message)
      ```

      ```typescript TypeScript theme={null}
      // Client SDK: You implement the tool loop
      let response = await client.messages.create({ ...params });
      while (response.stop_reason === "tool_use") {
        const result = yourToolExecutor(response.tool_use);
        response = await client.messages.create({ tool_result: result, ...params });
      }

      // Agent SDK: Claude handles tools autonomously
      for await (const message of query({ prompt: "Fix the bug in auth.ts" })) {
        console.log(message);
      }
      ```
    </CodeGroup>
  </Tab>

  <Tab title="Agent SDK vs Claude Code CLI">
    同じ機能、異なるインターフェース。

    | ユースケース       | 最適な選択 |
    | ------------ | ----- |
    | インタラクティブな開発  | CLI   |
    | CI/CD パイプライン | SDK   |
    | カスタムアプリケーション | SDK   |
    | 1 回限りのタスク    | CLI   |
    | 本番環境の自動化     | SDK   |

    多くのチームは両方を使用しています。日常的な開発には CLI、本番環境には SDK を使用します。ワークフローはそれらの間で直接変換されます。
  </Tab>

  <Tab title="Agent SDK vs Managed Agents">
    [Managed Agents](https://platform.claude.com/docs/ja/managed-agents/overview) はホストされた REST API です。Anthropic がエージェントとサンドボックスを実行し、アプリケーションがイベントを送信して結果をストリーミングで返します。**Agent SDK** は、独自のプロセス内でエージェントループを実行するライブラリです。

    |                   | Agent SDK                                    | Managed Agents                                                 |
    | ----------------- | -------------------------------------------- | -------------------------------------------------------------- |
    | **実行場所**          | ユーザーのプロセス、ユーザーのインフラストラクチャ                    | Anthropic 管理インフラストラクチャ                                         |
    | **インターフェース**      | Python または TypeScript ライブラリ                  | REST API                                                       |
    | **エージェントが動作する場所** | ユーザーのインフラストラクチャ上のファイル                        | セッションごとの管理サンドボックス                                              |
    | **セッション状態**       | ユーザーのファイルシステム上の JSONL                        | Anthropic ホスト型イベントログ                                           |
    | **カスタムツール**       | インプロセス Python または TypeScript 関数              | Claude がツールをトリガーします。ユーザーが実行して結果を返します                           |
    | **最適な用途**         | ローカルプロトタイピング、ユーザーのファイルシステムとサービスで直接動作するエージェント | サンドボックスまたはセッションインフラストラクチャを運用する必要のない本番環境エージェント、長時間実行および非同期セッション |

    一般的なパスは、Agent SDK でローカルにプロトタイプを作成してから、本番環境用に Managed Agents に移行することです。
  </Tab>
</Tabs>

<h2 id="changelog">
  変更ログ
</h2>

SDK の更新、バグ修正、および新機能の完全な変更ログを表示します。

* **TypeScript SDK**: [CHANGELOG.md を表示](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md)
* **Python SDK**: [CHANGELOG.md を表示](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md)

<h2 id="reporting-bugs">
  バグの報告
</h2>

Agent SDK でバグまたは問題が発生した場合：

* **TypeScript SDK**: [GitHub で問題を報告](https://github.com/anthropics/claude-agent-sdk-typescript/issues)
* **Python SDK**: [GitHub で問題を報告](https://github.com/anthropics/claude-agent-sdk-python/issues)

<h2 id="branding-guidelines">
  ブランドガイドライン
</h2>

Claude Agent SDK を統合するパートナーの場合、Claude ブランドの使用はオプションです。製品で Claude を参照する場合：

**許可されています：**

* 「Claude Agent」（ドロップダウンメニューに推奨）
* 「Claude」（既に「Agents」というラベルが付いたメニュー内の場合）
* 「{YourAgentName} Powered by Claude」（既存のエージェント名がある場合）

**許可されていません：**

* 「Claude Code」または「Claude Code Agent」
* Claude Code ブランドの ASCII アートまたは Claude Code を模倣する視覚要素

製品は独自のブランドを維持し、Claude Code または任意の Anthropic 製品のように見えるべきではありません。ブランドコンプライアンスに関する質問については、Anthropic [営業チーム](https://www.anthropic.com/contact-sales)に連絡してください。

<h2 id="license-and-terms">
  ライセンスと利用規約
</h2>

Claude Agent SDK の使用は、[Anthropic の商用利用規約](https://www.anthropic.com/legal/commercial-terms)によって管理されます。これは、Claude Agent SDK を使用して、独自のカスタマーおよびエンドユーザーに利用可能にする製品およびサービスを強化する場合を含みます。ただし、特定のコンポーネントまたは依存関係が、そのコンポーネントの LICENSE ファイルに示されているように異なるライセンスの対象である場合を除きます。

<h2 id="next-steps">
  次のステップ
</h2>

<CardGroup cols={2}>
  <Card title="クイックスタート" icon="play" href="/docs/ja/agent-sdk/quickstart">
    数分でバグを見つけて修正するエージェントを構築します
  </Card>

  <Card title="エージェントの例" icon="star" href="https://github.com/anthropics/claude-agent-sdk-demos">
    メールアシスタント、リサーチエージェント、その他
  </Card>

  <Card title="TypeScript SDK" icon="code" href="/docs/ja/agent-sdk/typescript">
    完全な TypeScript API リファレンスと例
  </Card>

  <Card title="Python SDK" icon="code" href="/docs/ja/agent-sdk/python">
    完全な Python API リファレンスと例
  </Card>
</CardGroup>
