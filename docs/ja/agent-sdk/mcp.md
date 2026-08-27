> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# MCP を使用して外部ツールに接続する

> MCP サーバーを設定してエージェントを外部ツールで拡張します。トランスポートタイプ、大規模なツールセット向けのツール検索、認証、エラーハンドリングについて説明します。

[Model Context Protocol（MCP）](https://modelcontextprotocol.io/docs/getting-started/intro)は、AI エージェントを外部ツールおよびデータソースに接続するためのオープンスタンダードです。MCP を使用すると、エージェントはデータベースをクエリし、Slack や GitHub などの API と統合し、カスタムツール実装を記述することなく他のサービスに接続できます。

MCP サーバーはローカルプロセスとして実行したり、HTTP 経由で接続したり、SDK アプリケーション内で直接実行したりできます。

<Note>
  このページは Agent SDK の MCP 設定について説明しています。Claude Code CLI に MCP サーバーを追加してすべてのプロジェクトで読み込むには、[MCP インストールスコープ](/docs/ja/mcp#mcp-installation-scopes)を参照してください。
</Note>

<h2 id="quickstart">
  クイックスタート
</h2>

この例は、[HTTP トランスポート](#http%2Fsse-servers)を使用して [Claude Code ドキュメンテーション](https://code.claude.com/docs)MCP サーバーに接続し、[`allowedTools`](#allow-mcp-tools)とワイルドカードを使用してサーバーからすべてのツールを許可します。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Use the docs MCP server to explain what hooks are in Claude Code",
    options: {
      mcpServers: {
        "claude-code-docs": {
          type: "http",
          url: "https://code.claude.com/docs/mcp"
        }
      },
      allowedTools: ["mcp__claude-code-docs__*"]
    }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


  async def main():
      options = ClaudeAgentOptions(
          mcp_servers={
              "claude-code-docs": {
                  "type": "http",
                  "url": "https://code.claude.com/docs/mcp",
              }
          },
          allowed_tools=["mcp__claude-code-docs__*"],
      )

      async for message in query(
          prompt="Use the docs MCP server to explain what hooks are in Claude Code",
          options=options,
      ):
          if isinstance(message, ResultMessage) and message.subtype == "success":
              print(message.result)


  asyncio.run(main())
  ```
</CodeGroup>

エージェントはドキュメンテーションサーバーに接続し、hooks に関する情報を検索して、結果を返します。

<h2 id="add-an-mcp-server">
  MCP サーバーを追加する
</h2>

`query()` を呼び出すときにコード内で MCP サーバーを設定するか、[`settingSources`](#from-a-config-file)経由で読み込まれる `.mcp.json` ファイルで設定できます。

<h3 id="in-code">
  コード内で
</h3>

`mcpServers` オプションで MCP サーバーを直接渡します：

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "List files in my project",
    options: {
      mcpServers: {
        filesystem: {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
        }
      },
      allowedTools: ["mcp__filesystem__*"]
    }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


  async def main():
      options = ClaudeAgentOptions(
          mcp_servers={
              "filesystem": {
                  "command": "npx",
                  "args": [
                      "-y",
                      "@modelcontextprotocol/server-filesystem",
                      "/Users/me/projects",
                  ],
              }
          },
          allowed_tools=["mcp__filesystem__*"],
      )

      async for message in query(prompt="List files in my project", options=options):
          if isinstance(message, ResultMessage) and message.subtype == "success":
              print(message.result)


  asyncio.run(main())
  ```
</CodeGroup>

<h3 id="from-a-config-file">
  設定ファイルから
</h3>

プロジェクトルートに `.mcp.json` ファイルを作成します。`project` 設定ソースが有効な場合、ファイルが取得されます。これはデフォルトの `query()` オプションの場合です。`settingSources` を明示的に設定する場合は、このファイルを読み込むために `"project"` を含めます：

```json theme={null}
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
    }
  }
}
```

<h2 id="allow-mcp-tools">
  MCP ツールを許可する
</h2>

MCP ツールは Claude が使用する前に明示的な許可が必要です。許可がない場合、Claude はツールが利用可能であることを認識しますが、呼び出すことはできません。

<h3 id="tool-naming-convention">
  ツール命名規則
</h3>

MCP ツールは `mcp__<server-name>__<tool-name>` という命名パターンに従います。たとえば、`"github"` という名前の GitHub サーバーに `list_issues` ツールがある場合、`mcp__github__list_issues` になります。

<h3 id="auto-approve-with-allowedtools">
  allowedTools でアクセスを許可する
</h3>

`allowedTools` を使用して、Claude が使用できる MCP ツールを指定します：

```typescript hidelines={1,-1} theme={null}
const _ = {
  options: {
    mcpServers: {
      // your servers
    },
    allowedTools: [
      "mcp__github__*", // All tools from the github server
      "mcp__db__query", // Only the query tool from db server
      "mcp__slack__send_message" // Only send_message from slack server
    ]
  }
};
```

ワイルドカード（`*`）を使用すると、各ツールを個別にリストアップすることなく、サーバーからすべてのツールを許可できます。

<Note>
  **MCP アクセスには `allowedTools` をパーミッションモードより優先してください。** `permissionMode: "acceptEdits"` は MCP ツールを自動承認しません（ファイル編集とファイルシステム Bash コマンドのみ）。`permissionMode: "bypassPermissions"` は MCP ツールを自動承認しますが、他のすべてのセーフティプロンプトも無効にするため、必要以上に広範です。`allowedTools` のワイルドカードは、必要な MCP サーバーのみを許可し、それ以上は許可しません。完全な比較については、[パーミッションモード](/docs/ja/agent-sdk/permissions#permission-modes)を参照してください。
</Note>

<h3 id="discover-available-tools">
  利用可能なツールを検出する
</h3>

MCP サーバーが提供するツールを確認するには、サーバーのドキュメンテーションを確認するか、サーバーに接続して `system` init メッセージを検査します：

<CodeGroup>
  ```typescript TypeScript theme={null}
  for await (const message of query({ prompt: "...", options })) {
    if (message.type === "system" && message.subtype === "init") {
      console.log("Available MCP tools:", message.mcp_servers);
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, SystemMessage


  async def main():
      async for message in query(prompt="...", options=options):
          if isinstance(message, SystemMessage) and message.subtype == "init":
              print("Available MCP tools:", message.data["mcp_servers"])


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="transport-types">
  トランスポートタイプ
</h2>

MCP サーバーはさまざまなトランスポートプロトコルを使用してエージェントと通信します。サーバーのドキュメンテーションを確認して、どのトランスポートをサポートしているかを確認してください：

* ドキュメンテーションに**実行するコマンド**（`npx @modelcontextprotocol/server-github` など）が記載されている場合は、stdio を使用します
* ドキュメンテーションに**URL** が記載されている場合は、HTTP または SSE を使用します
* コード内で独自のツールを構築している場合は、SDK MCP サーバーを使用します

<h3 id="stdio-servers">
  stdio サーバー
</h3>

stdin/stdout 経由で通信するローカルプロセス。同じマシンで実行する MCP サーバーに使用します：

<Tabs>
  <Tab title="In code">
    <CodeGroup>
      ```typescript TypeScript hidelines={1,-1} theme={null}
      const _ = {
        options: {
          mcpServers: {
            github: {
              command: "npx",
              args: ["-y", "@modelcontextprotocol/server-github"],
              env: {
                GITHUB_TOKEN: process.env.GITHUB_TOKEN
              }
            }
          },
          allowedTools: ["mcp__github__list_issues", "mcp__github__search_issues"]
        }
      };
      ```

      ```python Python theme={null}
      options = ClaudeAgentOptions(
          mcp_servers={
              "github": {
                  "command": "npx",
                  "args": ["-y", "@modelcontextprotocol/server-github"],
                  "env": {"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
              }
          },
          allowed_tools=["mcp__github__list_issues", "mcp__github__search_issues"],
      )
      ```
    </CodeGroup>
  </Tab>

  <Tab title=".mcp.json">
    ```json theme={null}
    {
      "mcpServers": {
        "github": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-github"],
          "env": {
            "GITHUB_TOKEN": "${GITHUB_TOKEN}"
          }
        }
      }
    }
    ```
  </Tab>
</Tabs>

<h3 id="http/sse-servers">
  HTTP/SSE サーバー
</h3>

クラウドホストされた MCP サーバーとリモート API に HTTP または SSE を使用します：

<Tabs>
  <Tab title="In code">
    <CodeGroup>
      ```typescript TypeScript hidelines={1,-1} theme={null}
      const _ = {
        options: {
          mcpServers: {
            "remote-api": {
              type: "sse",
              url: "https://api.example.com/mcp/sse",
              headers: {
                Authorization: `Bearer ${process.env.API_TOKEN}`
              }
            }
          },
          allowedTools: ["mcp__remote-api__*"]
        }
      };
      ```

      ```python Python theme={null}
      options = ClaudeAgentOptions(
          mcp_servers={
              "remote-api": {
                  "type": "sse",
                  "url": "https://api.example.com/mcp/sse",
                  "headers": {"Authorization": f"Bearer {os.environ['API_TOKEN']}"},
              }
          },
          allowed_tools=["mcp__remote-api__*"],
      )
      ```
    </CodeGroup>
  </Tab>

  <Tab title=".mcp.json">
    ```json theme={null}
    {
      "mcpServers": {
        "remote-api": {
          "type": "sse",
          "url": "https://api.example.com/mcp/sse",
          "headers": {
            "Authorization": "Bearer ${API_TOKEN}"
          }
        }
      }
    }
    ```
  </Tab>
</Tabs>

ストリーミング可能な HTTP トランスポートの場合は、代わりに `"type": "http"` を使用します。`.mcp.json` およびその他の JSON 設定ファイルでは、`"streamable-http"` は `"http"` のエイリアスとして受け入れられます。プログラマティック `mcpServers` オプションは `"http"` のみを受け入れます。

<h3 id="sdk-mcp-servers">
  SDK MCP サーバー
</h3>

別のサーバープロセスを実行する代わりに、アプリケーションコード内でカスタムツールを直接定義します。実装の詳細については、[カスタムツールガイド](/docs/ja/agent-sdk/custom-tools)を参照してください。

<h2 id="mcp-tool-search">
  MCP ツール検索
</h2>

多くの MCP ツールを設定している場合、ツール定義はコンテキストウィンドウの大部分を消費する可能性があります。ツール検索は、コンテキストからツール定義を保留し、各ターンで Claude が必要とするツールのみを読み込むことでこれを解決します。

ツール検索はデフォルトで有効になっています。設定オプションと詳細については、[ツール検索](/docs/ja/agent-sdk/tool-search)を参照してください。

カスタム SDK ツールでのベストプラクティスとツール検索の使用を含む詳細については、[ツール検索ガイド](/docs/ja/agent-sdk/tool-search)を参照してください。

<h2 id="authentication">
  認証
</h2>

ほとんどの MCP サーバーは外部サービスにアクセスするために認証が必要です。サーバー設定の環境変数を通じて認証情報を渡します。

<h3 id="pass-credentials-via-environment-variables">
  環境変数を通じて認証情報を渡す
</h3>

`env` フィールドを使用して、API キー、トークン、およびその他の認証情報を MCP サーバーに渡します：

<Tabs>
  <Tab title="In code">
    <CodeGroup>
      ```typescript TypeScript hidelines={1,-1} theme={null}
      const _ = {
        options: {
          mcpServers: {
            github: {
              command: "npx",
              args: ["-y", "@modelcontextprotocol/server-github"],
              env: {
                GITHUB_TOKEN: process.env.GITHUB_TOKEN
              }
            }
          },
          allowedTools: ["mcp__github__list_issues"]
        }
      };
      ```

      ```python Python theme={null}
      options = ClaudeAgentOptions(
          mcp_servers={
              "github": {
                  "command": "npx",
                  "args": ["-y", "@modelcontextprotocol/server-github"],
                  "env": {"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
              }
          },
          allowed_tools=["mcp__github__list_issues"],
      )
      ```
    </CodeGroup>
  </Tab>

  <Tab title=".mcp.json">
    ```json theme={null}
    {
      "mcpServers": {
        "github": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-github"],
          "env": {
            "GITHUB_TOKEN": "${GITHUB_TOKEN}"
          }
        }
      }
    }
    ```

    `${GITHUB_TOKEN}` 構文は実行時に環境変数を展開します。
  </Tab>
</Tabs>

デバッグログを含む完全な動作例については、[リポジトリからの問題のリスト](#list-issues-from-a-repository)を参照してください。

<h3 id="http-headers-for-remote-servers">
  リモートサーバーの HTTP ヘッダー
</h3>

HTTP および SSE サーバーの場合、サーバー設定で認証ヘッダーを直接渡します：

<Tabs>
  <Tab title="In code">
    <CodeGroup>
      ```typescript TypeScript hidelines={1,-1} theme={null}
      const _ = {
        options: {
          mcpServers: {
            "secure-api": {
              type: "http",
              url: "https://api.example.com/mcp",
              headers: {
                Authorization: `Bearer ${process.env.API_TOKEN}`
              }
            }
          },
          allowedTools: ["mcp__secure-api__*"]
        }
      };
      ```

      ```python Python theme={null}
      options = ClaudeAgentOptions(
          mcp_servers={
              "secure-api": {
                  "type": "http",
                  "url": "https://api.example.com/mcp",
                  "headers": {"Authorization": f"Bearer {os.environ['API_TOKEN']}"},
              }
          },
          allowed_tools=["mcp__secure-api__*"],
      )
      ```
    </CodeGroup>
  </Tab>

  <Tab title=".mcp.json">
    ```json theme={null}
    {
      "mcpServers": {
        "secure-api": {
          "type": "http",
          "url": "https://api.example.com/mcp",
          "headers": {
            "Authorization": "Bearer ${API_TOKEN}"
          }
        }
      }
    }
    ```

    `${API_TOKEN}` 構文は実行時に環境変数を展開します。
  </Tab>
</Tabs>

<h3 id="oauth2-authentication">
  OAuth2 認証
</h3>

[MCP 仕様は OAuth 2.1 をサポートしています](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization)。SDK はブラウザを開いたり、対話的な OAuth フローを実行したりしません。設定されたサーバーが認可チャレンジを返し、保存されたトークンが利用できない場合、エージェント実行はそのサーバーのツールなしで続行され、サーバーは [システム初期化メッセージ](/docs/ja/agent-sdk/typescript#sdksystemmessage)の `mcp_servers` 配列で `needs-auth` ステータスで報告されます。エージェントが特定のサーバーの接続に依存している場合は、起動時にその配列を確認してください。

認証情報を提供するには、アプリケーションで OAuth フローを完了し、結果のアクセストークンをサーバーの `headers` に渡します：

<CodeGroup>
  ```typescript TypeScript theme={null}
  // After completing OAuth flow in your app
  const accessToken = await getAccessTokenFromOAuthFlow();

  const options = {
    mcpServers: {
      "oauth-api": {
        type: "http",
        url: "https://api.example.com/mcp",
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      }
    },
    allowedTools: ["mcp__oauth-api__*"]
  };
  ```

  ```python Python theme={null}
  # After completing OAuth flow in your app
  access_token = await get_access_token_from_oauth_flow()

  options = ClaudeAgentOptions(
      mcp_servers={
          "oauth-api": {
              "type": "http",
              "url": "https://api.example.com/mcp",
              "headers": {"Authorization": f"Bearer {access_token}"},
          }
      },
      allowed_tools=["mcp__oauth-api__*"],
  )
  ```
</CodeGroup>

<h2 id="examples">
  例
</h2>

<h3 id="list-issues-from-a-repository">
  リポジトリから問題をリストする
</h3>

この例は、[GitHub MCP サーバー](https://github.com/modelcontextprotocol/servers/tree/main/src/github)に接続して最近の問題をリストします。この例には、MCP 接続とツール呼び出しを検証するためのデバッグログが含まれています。

実行する前に、`repo` スコープを持つ [GitHub 個人用アクセストークン](https://github.com/settings/tokens)を作成し、環境変数として設定します：

```bash theme={null}
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "List the 3 most recent issues in anthropics/claude-code",
    options: {
      mcpServers: {
        github: {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-github"],
          env: {
            GITHUB_TOKEN: process.env.GITHUB_TOKEN
          }
        }
      },
      allowedTools: ["mcp__github__list_issues"]
    }
  })) {
    // Verify MCP server connected successfully
    if (message.type === "system" && message.subtype === "init") {
      console.log("MCP servers:", message.mcp_servers);
    }

    // Log when Claude calls an MCP tool
    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if (block.type === "tool_use" && block.name.startsWith("mcp__")) {
          console.log("MCP tool called:", block.name);
        }
      }
    }

    // Print the final result
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  import os
  from claude_agent_sdk import (
      query,
      ClaudeAgentOptions,
      ResultMessage,
      SystemMessage,
      AssistantMessage,
  )


  async def main():
      options = ClaudeAgentOptions(
          mcp_servers={
              "github": {
                  "command": "npx",
                  "args": ["-y", "@modelcontextprotocol/server-github"],
                  "env": {"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
              }
          },
          allowed_tools=["mcp__github__list_issues"],
      )

      async for message in query(
          prompt="List the 3 most recent issues in anthropics/claude-code",
          options=options,
      ):
          # Verify MCP server connected successfully
          if isinstance(message, SystemMessage) and message.subtype == "init":
              print("MCP servers:", message.data.get("mcp_servers"))

          # Log when Claude calls an MCP tool
          if isinstance(message, AssistantMessage):
              for block in message.content:
                  if hasattr(block, "name") and block.name.startswith("mcp__"):
                      print("MCP tool called:", block.name)

          # Print the final result
          if isinstance(message, ResultMessage) and message.subtype == "success":
              print(message.result)


  asyncio.run(main())
  ```
</CodeGroup>

<h3 id="query-a-database">
  データベースをクエリする
</h3>

この例は、[Postgres MCP サーバー](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres)を使用してデータベースをクエリします。接続文字列はサーバーへの引数として渡されます。エージェントは自動的にデータベーススキーマを検出し、SQL クエリを記述して、結果を返します：

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // Connection string from environment variable
  const connectionString = process.env.DATABASE_URL;

  for await (const message of query({
    // Natural language query - Claude writes the SQL
    prompt: "How many users signed up last week? Break it down by day.",
    options: {
      mcpServers: {
        postgres: {
          command: "npx",
          // Pass connection string as argument to the server
          args: ["-y", "@modelcontextprotocol/server-postgres", connectionString]
        }
      },
      // Allow only read queries, not writes
      allowedTools: ["mcp__postgres__query"]
    }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  import os
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


  async def main():
      # Connection string from environment variable
      connection_string = os.environ["DATABASE_URL"]

      options = ClaudeAgentOptions(
          mcp_servers={
              "postgres": {
                  "command": "npx",
                  # Pass connection string as argument to the server
                  "args": [
                      "-y",
                      "@modelcontextprotocol/server-postgres",
                      connection_string,
                  ],
              }
          },
          # Allow only read queries, not writes
          allowed_tools=["mcp__postgres__query"],
      )

      # Natural language query - Claude writes the SQL
      async for message in query(
          prompt="How many users signed up last week? Break it down by day.",
          options=options,
      ):
          if isinstance(message, ResultMessage) and message.subtype == "success":
              print(message.result)


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="error-handling">
  エラーハンドリング
</h2>

MCP サーバーはさまざまな理由で接続に失敗する可能性があります。サーバープロセスがインストールされていない、認証情報が無効である、またはリモートサーバーに到達できない可能性があります。

SDK は各クエリの開始時に、サブタイプ `init` の `system` メッセージを発行します。このメッセージには、各 MCP サーバーの接続ステータスが含まれます。`status` フィールドをチェックして、エージェントが作業を開始する前に接続失敗を検出します：

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Process data",
    options: {
      mcpServers: {
        "data-processor": dataServer
      }
    }
  })) {
    if (message.type === "system" && message.subtype === "init") {
      const failedServers = message.mcp_servers.filter((s) => s.status !== "connected");

      if (failedServers.length > 0) {
        console.warn("Failed to connect:", failedServers);
      }
    }

    if (message.type === "result" && message.subtype === "error_during_execution") {
      console.error("Execution failed");
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, SystemMessage, ResultMessage


  async def main():
      options = ClaudeAgentOptions(mcp_servers={"data-processor": data_server})

      async for message in query(prompt="Process data", options=options):
          if isinstance(message, SystemMessage) and message.subtype == "init":
              failed_servers = [
                  s
                  for s in message.data.get("mcp_servers", [])
                  if s.get("status") != "connected"
              ]

              if failed_servers:
                  print(f"Failed to connect: {failed_servers}")

          if (
              isinstance(message, ResultMessage)
              and message.subtype == "error_during_execution"
          ):
              print("Execution failed")


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

<h3 id="server-shows-failed-status">
  サーバーが「失敗」ステータスを表示する
</h3>

`init` メッセージをチェックして、どのサーバーが接続に失敗したかを確認します：

```typescript theme={null}
if (message.type === "system" && message.subtype === "init") {
  for (const server of message.mcp_servers) {
    if (server.status === "failed") {
      console.error(`Server ${server.name} failed to connect`);
    }
  }
}
```

一般的な原因：

* **環境変数の欠落**：必要なトークンと認証情報が設定されていることを確認します。stdio サーバーの場合、`env` フィールドがサーバーが期待するものと一致することを確認します。
* **サーバーがインストールされていない**：`npx` コマンドの場合、パッケージが存在し、Node.js が PATH にあることを確認します。
* **無効な接続文字列**：データベースサーバーの場合、接続文字列の形式を確認し、データベースにアクセス可能であることを確認します。
* **ネットワークの問題**：リモート HTTP/SSE サーバーの場合、URL に到達可能であり、ファイアウォールが接続を許可していることを確認します。

<h3 id="tools-not-being-called">
  ツールが呼び出されていない
</h3>

Claude がツールを認識しているが使用していない場合は、`allowedTools` で許可を付与していることを確認します：

```typescript hidelines={1,-1} theme={null}
const _ = {
  options: {
    mcpServers: {
      // your servers
    },
    allowedTools: ["mcp__servername__*"] // Auto-approve calls from this server
  }
};
```

<h3 id="connection-timeouts">
  接続タイムアウト
</h3>

MCP サーバー接続のデフォルトタイムアウトは 30 秒です。サーバーの起動に時間がかかる場合、接続は失敗します。[`MCP_TIMEOUT`](/docs/ja/env-vars) 環境変数でリミットを上げてください（ミリ秒単位）。より多くの起動時間が必要なサーバーの場合は、以下も検討してください：

* 利用可能な場合は、より軽量なサーバーを使用する
* エージェントを開始する前にサーバーをプリウォーミングする
* 遅い初期化の原因についてサーバーログを確認する

<h3 id="tool-output-exceeds-maximum-allowed-tokens">
  ツール出力が許可される最大トークン数を超える
</h3>

SDK は Claude Code と同じ MCP 出力制限を適用します。ツール結果が 25,000 トークンより大きい場合、完全な出力はファイルに保存され、ツール結果はファイルパスを名前に含むエラーメッセージに置き換えられるため、エージェントは出力を部分的に読み戻すことができます。[`MAX_MCP_OUTPUT_TOKENS`](/docs/ja/env-vars) 環境変数でリミットを上げてください。サーバーがツールごとにより高いリミットを宣言する方法を含む完全な動作については、[MCP 出力制限と警告](/docs/ja/mcp#mcp-output-limits-and-warnings)を参照してください。

<h2 id="related-resources">
  関連リソース
</h2>

* **[カスタムツールガイド](/docs/ja/agent-sdk/custom-tools)**：SDK アプリケーションと同じプロセスで実行される独自の MCP サーバーを構築します
* **[パーミッション](/docs/ja/agent-sdk/permissions)**：`allowedTools` と `disallowedTools` を使用してエージェントが使用できる MCP ツールを制御します
* **[MCP 出力制限と警告](/docs/ja/mcp#mcp-output-limits-and-warnings)**：`MAX_MCP_OUTPUT_TOKENS` を超えるツール結果を SDK が処理する方法。ディスクへの永続化フォールバックと、ツールごとの `anthropic/maxResultSizeChars` アノテーションを含みます
* **[TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript)**：MCP 設定オプションを含む完全な API リファレンス
* **[Python SDK リファレンス](/docs/ja/agent-sdk/python)**：MCP 設定オプションを含む完全な API リファレンス
* **[MCP サーバーディレクトリ](https://github.com/modelcontextprotocol/servers)**：データベース、API など、利用可能な MCP サーバーを参照します
