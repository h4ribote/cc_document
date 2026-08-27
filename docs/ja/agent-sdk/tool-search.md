> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 多くのツールにスケーリングするツール検索

> 必要なものだけをオンデマンドで検出して読み込むことで、エージェントを数千のツールにスケーリングします。

ツール検索により、エージェントは数百または数千のツールを動的に検出し、オンデマンドで読み込むことで、それらと連携できます。すべてのツール定義をコンテキストウィンドウに事前に読み込む代わりに、エージェントはツールカタログを検索し、必要なツールのみを読み込みます。

このアプローチは、ツールライブラリがスケーリングするにつれて、2 つの課題を解決します。

* **コンテキスト効率：** ツール定義はコンテキストウィンドウの大部分を消費する可能性があります（50 個のツールは 10～20K トークンを使用できます）。実際の作業用のスペースが減少します。
* **ツール選択精度：** 30～50 個以上のツールが一度に読み込まれると、ツール選択精度が低下します。

ツール検索はデフォルトで有効になっています。

<h2 id="how-tool-search-works">
  ツール検索の仕組み
</h2>

ツール検索がアクティブな場合、ツール定義はコンテキストウィンドウから保留されます。エージェントは利用可能なツールの概要を受け取り、タスクが既に読み込まれていない機能を必要とする場合、関連するツールを検索します。最も関連性の高い 5 個までのツールがデフォルトでコンテキストに読み込まれ、その後のターンで利用可能なままになります。会話が十分に長く、SDK が以前のメッセージをコンパクト化してスペースを解放する場合、以前に検出されたツールが削除される可能性があり、エージェントは必要に応じて再度検索します。

ツール検索は、Claude が初めてツールを検出するときに 1 つの追加ラウンドトリップを追加します（検索ステップ）。ただし、大規模なツールセットの場合、これはすべてのターンでより小さいコンテキストによってオフセットされます。ツールが約 10 個未満の場合、すべてを事前に読み込む方が通常は高速です。

基盤となる API メカニズムの詳細については、[API のツール検索](https://platform.claude.com/docs/ja/agents-and-tools/tool-use/tool-search-tool)を参照してください。

<Note>
  ツール検索は Claude Sonnet 4.5、Claude Haiku 4.5、Claude Opus 4.5、およびそれ以降のモデルでサポートされています。現在のリストについては、[API ドキュメントのモデル互換性](https://platform.claude.com/docs/ja/agents-and-tools/tool-use/tool-search-tool#model-compatibility)を参照してください。Google Cloud の Agent Platform では、サポートされている最小モデルは Claude Sonnet 4.5 と Claude Opus 4.5 です。
</Note>

<h2 id="configure-tool-search">
  ツール検索を設定する
</h2>

ツール検索はデフォルトでオンです。Google Cloud の Agent Platform ではデフォルトで無効になっており、Claude Sonnet 4.5 以降および Claude Opus 4.5 以降でサポートされています。また、`ANTHROPIC_BASE_URL` が非ファーストパーティホストを指す場合も無効になります。ほとんどのプロキシは `tool_reference` ブロックを転送しないためです。`ENABLE_TOOL_SEARCH` 環境変数でいずれかのデフォルトをオーバーライドできます。

| 値        | 動作                                                                                                                                                                                            |
| :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| （未設定）    | ツール検索はオンです。ツール定義は遅延され、オンデマンドで検出されます。Google Cloud の Agent Platform または非ファーストパーティ `ANTHROPIC_BASE_URL` では事前読み込みにフォールバックします。                                                                     |
| `true`   | ツール検索は常にオンです。SDK は Google Cloud の Agent Platform およびプロキシ経由でもベータヘッダーを送信します。Sonnet 4.5 または Opus 4.5 より前の Google Cloud の Agent Platform モデル、または `tool_reference` ブロックをサポートしないプロキシでは、リクエストが失敗します。 |
| `auto`   | すべてのツール定義の合計トークン数をモデルのコンテキストウィンドウと照合します。コンテキストウィンドウの 10% を超える場合、ツール検索がアクティブになります。10% 未満の場合、すべてのツールが通常どおりコンテキストに読み込まれます。                                                                       |
| `auto:N` | カスタム割合を使用した `auto` と同じです。`auto:5` はツール定義がコンテキストウィンドウの 5% を超える場合にアクティブになります。値が低いほど、より早くアクティブになります。                                                                                             |
| `false`  | ツール検索はオフです。すべてのツール定義がすべてのターンでコンテキストに読み込まれます。                                                                                                                                                  |

[`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`](/docs/ja/env-vars) を設定するとツール検索がオフになり、`ENABLE_TOOL_SEARCH` はそれをオーバーライドできません。この変数は、`defer_loading` ツール定義と `tool_reference` コンテンツブロックが必要とするベータヘッダーを削除します。

ツール検索は、リモート MCP サーバーから来るか、[カスタム SDK MCP サーバー](/docs/ja/agent-sdk/custom-tools)から来るかに関わらず、すべての登録ツールに適用されます。`auto` を使用する場合、閾値はすべてのサーバー全体のすべてのツール定義の合計サイズに基づいています。

`query()` の `env` オプションで値を設定します。TypeScript では、`env` はサブプロセス環境を置き換えるため、継承された変数を保持するために `...process.env` を展開します。Python では、`env` は継承された環境の上にマージされます。この例は、多くのツールを公開するリモート MCP サーバーに接続し、ワイルドカードですべてのツールを事前承認し、`auto:5` を使用して、ツール定義がコンテキストウィンドウの 5% を超える場合にツール検索をアクティブにします。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  try {
    for await (const message of query({
      prompt: "Find and run the appropriate database query",
      options: {
        mcpServers: {
          "enterprise-tools": {
            // Connect to a remote MCP server
            type: "http",
            url: "https://tools.example.com/mcp"
          }
        },
        allowedTools: ["mcp__enterprise-tools__*"], // Wildcard pre-approves all tools from this server
        env: {
          ...process.env, // env replaces the subprocess environment, so keep inherited variables
          ENABLE_TOOL_SEARCH: "auto:5" // Activate tool search when tools exceed 5% of context
        }
      }
    })) {
      if (message.type === "result" && message.subtype === "success") {
        console.log(message.result);
      }
    }
  } catch (error) {
    // A single-shot query() throws after yielding an error result
    console.log(`Session ended with an error: ${error}`);
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


  async def main():
      options = ClaudeAgentOptions(
          mcp_servers={
              "enterprise-tools": {
                  "type": "http",
                  "url": "https://tools.example.com/mcp",
              }
          },
          allowed_tools=[
              "mcp__enterprise-tools__*"
          ],  # Wildcard pre-approves all tools from this server
          env={
              "ENABLE_TOOL_SEARCH": "auto:5"  # Activate tool search when tools exceed 5% of context
          },
      )

      try:
          async for message in query(
              prompt="Find and run the appropriate database query",
              options=options,
          ):
              if isinstance(message, ResultMessage) and message.subtype == "success":
                  print(message.result)
      except Exception as error:
          # A single-shot query() raises after yielding an error result
          print(f"Session ended with an error: {error}")


  asyncio.run(main())
  ```
</CodeGroup>

この例を実行するには、`https://tools.example.com/mcp` を独自の MCP サーバーの URL に置き換えてください。成功時に、結果テキストがコンソールに出力されます。

これは単一ショットの `query()` 呼び出しであるため、SDK はエラー結果を生成した後に発生するため、この例はループを try ブロックでラップします。実行が失敗した理由を確認するには、ループ内の結果メッセージの `subtype`（`error_during_execution` など）を確認してください。結果メッセージの詳細については、[結果を処理する](/docs/ja/agent-sdk/agent-loop#handle-the-result)を参照してください。

`ENABLE_TOOL_SEARCH` を `"false"` に設定すると、ツール検索が無効になり、すべてのツール定義がすべてのターンでコンテキストに読み込まれます。これにより検索ラウンドトリップが削除されます。ツールセットが小さい（約 10 個未満のツール）場合、定義がコンテキストウィンドウに快適に収まる場合は、より高速になる可能性があります。

<h2 id="optimize-tool-discovery">
  ツール検出を最適化する
</h2>

検索メカニズムは、ツール名と説明に対してクエリを照合します。`search_slack_messages` のような名前は、`query_slack` よりも広い範囲のリクエストに対して表示されます。「キーワード、チャネル、または日付範囲で Slack メッセージを検索」などの具体的なキーワードを含む説明は、「Slack をクエリ」などの一般的な説明よりも多くのクエリに一致します。

利用可能なツールカテゴリをリストするシステムプロンプトセクションを追加することもできます。これにより、エージェントは検索対象のツールの種類に関するコンテキストを取得します。TypeScript では `systemPrompt` オプション、Python では `system_prompt` を使用してテキストを渡します。`claude_code` プリセットで `append` を使用すると、プリセットのプロンプトを置き換えるのではなく、テキストを追加します。

<CodeGroup>
  ```typescript TypeScript theme={null}
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "You can search for tools to interact with Slack, GitHub, and Jira."
    }
  }
  ```

  ```python Python theme={null}
  options = ClaudeAgentOptions(
      system_prompt={
          "type": "preset",
          "preset": "claude_code",
          "append": "You can search for tools to interact with Slack, GitHub, and Jira.",
      }
  )
  ```
</CodeGroup>

システムプロンプトオプションの完全なセットについては、[システムプロンプトの変更](/docs/ja/agent-sdk/modifying-system-prompts)を参照してください。

<h2 id="limits">
  制限
</h2>

* **最大ツール数：** カタログ内の 10,000 個のツール
* **検索結果：** デフォルトでは検索ごとに最も関連性の高い 5 つのツールを返します
* **モデルサポート：** Claude Sonnet 4.5、Claude Haiku 4.5、Claude Opus 4.5、およびそれ以降のモデル。現在のリストについては、[API ドキュメントのモデル互換性](https://platform.claude.com/docs/ja/agents-and-tools/tool-use/tool-search-tool#model-compatibility)を参照してください。Google Cloud の Agent Platform では、Claude Sonnet 4.5 以降および Claude Opus 4.5 以降。

<h2 id="related-documentation">
  関連ドキュメント
</h2>

* [API のツール検索](https://platform.claude.com/docs/ja/agents-and-tools/tool-use/tool-search-tool)：カスタム実装を含むツール検索の完全な API ドキュメント
* [MCP サーバーを接続する](/docs/ja/agent-sdk/mcp)：MCP サーバー経由で外部ツールに接続する
* [カスタムツール](/docs/ja/agent-sdk/custom-tools)：SDK MCP サーバーで独自のツールを構築する
* [TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript)：完全な API リファレンス
* [Python SDK リファレンス](/docs/ja/agent-sdk/python)：完全な API リファレンス
