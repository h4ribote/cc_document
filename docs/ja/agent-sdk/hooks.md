> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# フックを使用してエージェントの動作をインターセプトして制御する

> フックを使用して、エージェント実行の重要なポイントでエージェントの動作をインターセプトしてカスタマイズします

フックはエージェントイベントに応答してコードを実行するコールバック関数です。ツールが呼び出されたり、セッションが開始したり、実行が停止したりするなどのイベントに対応します。フックを使用すると、以下のことができます。

* **危険な操作をブロック**する：破壊的なシェルコマンドや不正なファイルアクセスなど、実行前に危険な操作をブロックします
* **ログと監査**：コンプライアンス、デバッグ、分析のためにすべてのツール呼び出しをログして監査します
* **入力と出力を変換**する：データをサニタイズしたり、認証情報を注入したり、ファイルパスをリダイレクトしたりします
* **人間の承認を要求**する：データベース書き込みや API 呼び出しなどの機密アクションに対して
* **セッションライフサイクルを追跡**する：状態を管理したり、リソースをクリーンアップしたり、通知を送信したりします

このガイドでは、フックの仕組み、フックの設定方法、およびツールのブロック、入力の変更、通知の転送などの一般的なパターンの例を説明します。

<h2 id="how-hooks-work">
  フックの仕組み
</h2>

<Steps>
  <Step title="イベントが発火する">
    エージェント実行中に何かが起こり、SDK がイベントを発火します。ツールが呼び出されようとしている（`PreToolUse`）、ツールが結果を返した（`PostToolUse`）、サブエージェントが開始または停止した、エージェントがアイドル状態である、または実行が完了したなどです。[イベントの完全なリスト](#available-hooks)を参照してください。
  </Step>

  <Step title="SDK が登録されたフックを収集する">
    SDK は、そのイベントタイプに登録されたフックをチェックします。これには、`options.hooks` に渡すコールバックフックと、対応する [`settingSources`](/docs/ja/agent-sdk/typescript#settingsource) または [`setting_sources`](/docs/ja/agent-sdk/python#settingsource) エントリが有効になっているときの設定ファイルからのシェルコマンドフックが含まれます。これはデフォルトの `query()` オプションで有効になっています。
  </Step>

  <Step title="マッチャーがどのフックを実行するかをフィルタリングする">
    フックに [`matcher`](#matchers) パターン（`"Write|Edit"` など）がある場合、SDK はそれをイベントのターゲット（たとえば、ツール名）に対してテストします。マッチャーのないフックは、そのタイプのすべてのイベントに対して実行されます。
  </Step>

  <Step title="コールバック関数が実行される">
    各マッチングフックの[コールバック関数](#callback-functions)は、何が起こっているかについての入力を受け取ります。ツール名、その引数、セッション ID、およびその他のイベント固有の詳細です。
  </Step>

  <Step title="コールバックが決定を返す">
    任意の操作（ログ、API 呼び出し、検証）を実行した後、コールバックは[出力オブジェクト](#outputs)を返します。これはエージェントに何をするかを指示します。操作を許可する、ブロックする、入力を変更する、または会話にコンテキストを注入するなどです。
  </Step>
</Steps>

次の例は、これらのステップをまとめたものです。`PreToolUse` フック（ステップ 1）を `"Write|Edit"` マッチャー（ステップ 3）で登録して、コールバックがファイル書き込みツールに対してのみ発火するようにします。トリガーされると、コールバックはツールの入力（ステップ 4）を受け取り、ファイルパスが `.env` ファイルをターゲットにしているかどうかをチェックし、`permissionDecision: "deny"` を返して操作をブロックします（ステップ 5）。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import (
      AssistantMessage,
      ClaudeSDKClient,
      ClaudeAgentOptions,
      HookMatcher,
      ResultMessage,
  )


  # ツール呼び出しの詳細を受け取るフックコールバックを定義する
  async def protect_env_files(input_data, tool_use_id, context):
      # ツールの入力引数からファイルパスを抽出する
      file_path = input_data["tool_input"].get("file_path", "")
      file_name = file_path.split("/")[-1]

      # .env ファイルをターゲットにしている場合は操作をブロックする
      if file_name == ".env":
          return {
              "hookSpecificOutput": {
                  "hookEventName": input_data["hook_event_name"],
                  "permissionDecision": "deny",
                  "permissionDecisionReason": "Cannot modify .env files",
              }
          }

      # 空のオブジェクトを返して操作を許可する
      return {}


  async def main():
      options = ClaudeAgentOptions(
          hooks={
              # PreToolUse イベントのフックを登録する
              # マッチャーは Write と Edit ツール呼び出しのみにフィルタリングする
              "PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])]
          }
      )

      async with ClaudeSDKClient(options=options) as client:
          await client.query("Update the database configuration")
          async for message in client.receive_response():
              # アシスタントとリザルトメッセージをフィルタリングする
              if isinstance(message, (AssistantMessage, ResultMessage)):
                  print(message)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query, HookCallback, PreToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

  // HookCallback 型でフックコールバックを定義する
  const protectEnvFiles: HookCallback = async (input, toolUseID, { signal }) => {
    // 型安全性のために入力を特定のフック型にキャストする
    const preInput = input as PreToolUseHookInput;

    // tool_input をキャストしてそのプロパティにアクセスする（SDK では unknown として型付けされている）
    const toolInput = preInput.tool_input as Record<string, unknown>;
    const filePath = toolInput?.file_path as string;
    const fileName = filePath?.split("/").pop();

    // .env ファイルをターゲットにしている場合は操作をブロックする
    if (fileName === ".env") {
      return {
        hookSpecificOutput: {
          hookEventName: preInput.hook_event_name,
          permissionDecision: "deny",
          permissionDecisionReason: "Cannot modify .env files"
        }
      };
    }

    // 空のオブジェクトを返して操作を許可する
    return {};
  };

  for await (const message of query({
    prompt: "Update the database configuration",
    options: {
      hooks: {
        // PreToolUse イベントのフックを登録する
        // マッチャーは Write と Edit ツール呼び出しのみにフィルタリングする
        PreToolUse: [{ matcher: "Write|Edit", hooks: [protectEnvFiles] }]
      }
    }
  })) {
    // アシスタントとリザルトメッセージをフィルタリングする
    if (message.type === "assistant" || message.type === "result") {
      console.log(message);
    }
  }
  ```
</CodeGroup>

<h2 id="available-hooks">
  利用可能なフック
</h2>

SDK はエージェント実行のさまざまなステージのフックを提供します。一部のフックは両方の SDK で利用可能ですが、その他は TypeScript のみです。

| フックイベント                                                | Python SDK | TypeScript SDK | トリガーされる条件                                           | 使用例                                         |
| ------------------------------------------------------ | ---------- | -------------- | --------------------------------------------------- | ------------------------------------------- |
| `PreToolUse`                                           | はい         | はい             | ツール呼び出しリクエスト（ブロックまたは変更可能）                           | 危険なシェルコマンドをブロックする                           |
| `PostToolUse`                                          | はい         | はい             | ツール実行結果                                             | すべてのファイル変更を監査証跡にログする                        |
| `PostToolUseFailure`                                   | はい         | はい             | ツール実行失敗                                             | ツールエラーを処理またはログする                            |
| `PostToolBatch`                                        | いいえ        | はい             | ツール呼び出しの完全なバッチが解決される。次のモデル呼び出しの前に 1 回               | バッチ全体に対して規約を 1 回注入する                        |
| `UserPromptSubmit`                                     | はい         | はい             | ユーザープロンプト送信                                         | プロンプトに追加のコンテキストを注入する                        |
| [`UserPromptExpansion`](/docs/ja/hooks#userpromptexpansion) | いいえ        | はい             | ユーザーが入力したコマンドが Claude に到達する前にプロンプトに展開される            | コマンドの直接呼び出しをブロックするか、スキルが入力されたときにコンテキストを追加する |
| `MessageDisplay`                                       | いいえ        | はい             | テキスト付きのアシスタントメッセージが完了する。メッセージごとに 1 回、完全なメッセージテキスト付き | 表示されたテキストを編集または再フォーマットする（トランスクリプトは変更しない）    |
| `Stop`                                                 | はい         | はい             | エージェント実行停止                                          | 終了前にセッション状態を保存する                            |
| `SubagentStart`                                        | はい         | はい             | サブエージェント初期化                                         | 並列タスク生成を追跡する                                |
| `SubagentStop`                                         | はい         | はい             | サブエージェント完了                                          | 並列タスクから結果を集約する                              |
| `PreCompact`                                           | はい         | はい             | 会話圧縮リクエスト                                           | 要約する前に完全なトランスクリプトをアーカイブする                   |
| `PermissionRequest`                                    | はい         | はい             | パーミッションダイアログが表示される                                  | カスタムパーミッション処理                               |
| `SessionStart`                                         | いいえ        | はい             | セッション初期化                                            | ログとテレメトリを初期化する                              |
| `SessionEnd`                                           | いいえ        | はい             | セッション終了                                             | 一時的なリソースをクリーンアップする                          |
| `Notification`                                         | はい         | はい             | エージェントステータスメッセージ                                    | エージェントステータス更新を Slack または PagerDuty に送信する    |
| `Setup`                                                | いいえ        | はい             | セッション設定/メンテナンス                                      | 初期化タスクを実行する                                 |
| `TeammateIdle`                                         | いいえ        | はい             | チームメイトがアイドル状態になる                                    | 作業を再割り当てするか通知する                             |
| `TaskCompleted`                                        | いいえ        | はい             | バックグラウンドタスク完了                                       | 並列タスクから結果を集約する                              |
| `ConfigChange`                                         | いいえ        | はい             | 設定ファイル変更                                            | 設定を動的に再ロードする                                |
| `WorktreeCreate`                                       | いいえ        | はい             | Git ワークツリー作成                                        | 分離されたワークスペースを追跡する                           |
| `WorktreeRemove`                                       | いいえ        | はい             | Git ワークツリー削除                                        | ワークスペースリソースをクリーンアップする                       |

<h2 id="configure-hooks">
  フックを設定する
</h2>

フックを設定するには、エージェントオプション（Python では `ClaudeAgentOptions`、TypeScript では `options` オブジェクト）の `hooks` フィールドに渡します。

<CodeGroup>
  ```python Python theme={null}
  options = ClaudeAgentOptions(
      hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[my_callback])]}
  )

  async with ClaudeSDKClient(options=options) as client:
      await client.query("Your prompt")
      async for message in client.receive_response():
          print(message)
  ```

  ```typescript TypeScript theme={null}
  for await (const message of query({
    prompt: "Your prompt",
    options: {
      hooks: {
        PreToolUse: [{ matcher: "Bash", hooks: [myCallback] }]
      }
    }
  })) {
    console.log(message);
  }
  ```
</CodeGroup>

`hooks` オプションは辞書（Python）またはオブジェクト（TypeScript）です。ここで：

* **キー**は[フックイベント名](#available-hooks)です（例：`'PreToolUse'`、`'PostToolUse'`、`'Stop'`）
* **値**は[マッチャー](#matchers)の配列です。各マッチャーには、オプションのフィルタパターンと[コールバック関数](#callback-functions)が含まれます

<h3 id="matchers">
  マッチャー
</h3>

マッチャーを使用して、コールバックがいつ発火するかをフィルタリングします。`matcher` フィールドは、フックイベントタイプに応じて異なる値に対してマッチングされます。たとえば、ツールベースのフックはツール名に対してマッチングされ、`Notification` フックは通知タイプに対してマッチングされます。各イベントタイプのマッチャー値の完全なリストについては、[Claude Code フックリファレンス](/docs/ja/hooks#matcher-patterns)を参照してください。

SDK マッチャーは[設定ファイルのマッチャー](/docs/ja/hooks#matcher-patterns)と同じルールに従います。文字、数字、`_`、`-`、スペース、`,`、および `|` のみを含むマッチャーは正確な文字列として比較され、`|` または `,` で区切られた代替案とオプションの周囲の空白があるため、`Write|Edit` と `Write, Edit` はそれぞれこれら 2 つのツールと正確にマッチし、`code-reviewer` はそのエージェント型のみにマッチします。`*` のマッチャー、空の文字列、またはマッチャーを完全に省略すると、イベントのすべての発生にマッチします。

他の文字を含むマッチャーはアンカーなしの正規表現として評価されるため、`^mcp__` はすべての MCP ツールにマッチし、`Edit.*` は `Edit` と `NotebookEdit` の両方にマッチします。全文字列マッチが必要な場合は、正規表現を `^` と `$` でラップします。

`mcp__memory` または `mcp__brave-search` のようなマッチャーは正確マッチ文字のみを含むため、正確な文字列として比較され、ツールにマッチしません。そのサーバーからすべてのツールにマッチするには、`mcp__memory__.*` を使用します。

ハイフンを正確マッチセットに含めるには、Claude Code ランタイム v2.1.195 以降が必要です。以前のバージョンでは、`code-reviewer` のようなハイフン付き名前はアンカーなしの正規表現として評価され、正確にマッチするには `^code-reviewer$` としてアンカーする必要があります。

| オプション     | 型                | デフォルト       | 説明                                                                                                                                                                                                                                                                  |
| --------- | ---------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `matcher` | `string`         | `undefined` | イベントのフィルタフィールドに対してマッチングされるパターン。上記の比較ルールに従います。ツールフックの場合、これはツール名です。組み込みツールには `Bash`、`Read`、`Write`、`Edit`、`Glob`、`Grep`、`WebFetch`、`Agent` などが含まれます（完全なリストについては[ツール入力型](/docs/ja/agent-sdk/typescript#tool-input-types)を参照）。MCP ツールはパターン `mcp__<server>__<action>` を使用します。 |
| `hooks`   | `HookCallback[]` | -           | 必須。パターンがマッチしたときに実行するコールバック関数の配列                                                                                                                                                                                                                                     |
| `timeout` | `number`         | `60`        | タイムアウト（秒単位）                                                                                                                                                                                                                                                         |

可能な限り `matcher` パターンを使用して特定のツールをターゲットにします。`'Bash'` のマッチャーは Bash コマンドに対してのみ実行されますが、パターンを省略するとコールバックはそのイベントのすべての発生に対して実行されます。

ツールベースのフックの場合、マッチャーはツール名でのみフィルタリングされ、ファイルパスやその他の引数ではフィルタリングされません。ファイルパスでフィルタリングするには、コールバック内で `tool_input.file_path` をチェックします。

<Tip>
  **ツール名の発見：** 組み込みツール名の完全なリストについては[ツール入力型](/docs/ja/agent-sdk/typescript#tool-input-types)を参照するか、マッチャーなしでフックを追加して、セッションが行うすべてのツール呼び出しをログします。

  **MCP ツール命名：** MCP ツールは常に `mcp__` で始まり、その後にサーバー名とアクション `mcp__<server>__<action>` が続きます。たとえば、`playwright` という名前のサーバーを設定した場合、そのツールは `mcp__playwright__browser_screenshot`、`mcp__playwright__browser_click` などという名前になります。サーバー名は `mcpServers` 設定で使用するキーから取得されます。
</Tip>

<h3 id="callback-functions">
  コールバック関数
</h3>

<h4 id="inputs">
  入力
</h4>

すべてのフックコールバックは 3 つの引数を受け取ります。

* **入力データ：** イベント詳細を含む型付きオブジェクト。各フック型には独自の入力形状があります。たとえば、`PreToolUseHookInput` には `tool_name` と `tool_input` が含まれ、`NotificationHookInput` には `message` が含まれます。[TypeScript](/docs/ja/agent-sdk/typescript#hookinput) および [Python](/docs/ja/agent-sdk/python#hookinput) SDK リファレンスで完全な型定義を参照してください。
  * すべてのフック入力は `session_id`、`cwd`、および `hook_event_name` を共有します。
  * `agent_id` と `agent_type` は、フックがサブエージェント内で発火するときに入力されます。TypeScript では、これらはベースフック入力にあり、すべてのフック型で利用可能です。Python では、これらは `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、および `PermissionRequest` のオプションフィールドであり、`SubagentStart` および `SubagentStop` の必須フィールドです。
* **ツール使用 ID**（`str | None` / `string | undefined`）：同じツール呼び出しの `PreToolUse` と `PostToolUse` イベントを相関させます。
* **コンテキスト：** TypeScript では、キャンセル用の `signal` プロパティ（`AbortSignal`）を含みます。Python では、この引数は将来の使用のために予約されています。

<h4 id="outputs">
  出力
</h4>

コールバックは 2 つのカテゴリのフィールドを持つオブジェクトを返します。

* **トップレベルフィールド**はすべてのイベントで同じように機能します。`systemMessage` はユーザーにメッセージを表示し、`continue`（Python では `continue_`）はこのフック後にエージェントが実行を続けるかどうかを決定します。
* **`hookSpecificOutput`** は現在の操作を制御します。内部のフィールドはフックイベントタイプに依存します。`PreToolUse` フックの場合、ここで `permissionDecision`（`"allow"`、`"deny"`、`"ask"`、または `"defer"`）、`permissionDecisionReason`、および `updatedInput` を設定します。`"defer"` を返すとクエリが終了し、[後で再開](/docs/ja/hooks#defer-a-tool-call-for-later)できます。`PostToolUse` フックの場合、`additionalContext` を設定してツール結果に情報を追加できます。Claude がそれを見る前にツールの出力を置き換えるには、`updatedToolOutput` を設定します。これは両方の SDK のすべてのツールで機能します。古い `updatedMCPToolOutput` フィールドは MCP ツール出力のみを置き換え、非推奨です。

変更なしで操作を許可するには `{}` を返します。SDK コールバックフックは、[Claude Code シェルコマンドフック](/docs/ja/hooks#json-output)と同じ JSON 出力形式を使用します。これはすべてのフィールドとイベント固有のオプションを文書化しています。SDK 型定義については、[TypeScript](/docs/ja/agent-sdk/typescript#synchookjsonoutput) および [Python](/docs/ja/agent-sdk/python#synchookjsonoutput) SDK リファレンスを参照してください。

<Note>
  複数のフックまたはパーミッションルールが適用される場合、`deny` は `defer` より優先され、`defer` は `ask` より優先され、`ask` は `allow` より優先されます。いずれかのフックが `deny` を返す場合、他のフックに関係なく操作はブロックされます。
</Note>

<h4 id="asynchronous-output">
  非同期出力
</h4>

デフォルトでは、エージェントはコールバックが返されるのを待ってから続行します。フックが副作用（ログ、ウェブフック送信）を実行し、エージェントの動作に影響を与える必要がない場合、代わりに非同期出力を返すことができます。これはエージェントに、フックが完了するのを待たずに即座に続行するよう指示します。

<CodeGroup>
  ```python Python theme={null}
  async def async_hook(input_data, tool_use_id, context):
      # バックグラウンドタスクを開始してから即座に返す
      asyncio.create_task(send_to_logging_service(input_data))
      return {"async_": True, "asyncTimeout": 30000}
  ```

  ```typescript TypeScript theme={null}
  const asyncHook: HookCallback = async (input, toolUseID, { signal }) => {
    // バックグラウンドタスクを開始してから即座に返す
    sendToLoggingService(input).catch(console.error);
    return { async: true, asyncTimeout: 30000 };
  };
  ```
</CodeGroup>

| フィールド          | 型        | 説明                                                                      |
| -------------- | -------- | ----------------------------------------------------------------------- |
| `async`        | `true`   | 非同期モードを通知します。エージェントは待たずに続行します。Python では、予約キーワードを避けるために `async_` を使用します。 |
| `asyncTimeout` | `number` | バックグラウンド操作のオプションのタイムアウト（ミリ秒単位）                                          |

<Note>
  非同期出力はエージェントが既に先に進んでいるため、ブロック、変更、またはコンテキストを注入することはできません。ログ、メトリクス、または通知などの副作用にのみ使用します。
</Note>

<h2 id="examples">
  例
</h2>

<h3 id="modify-tool-input">
  ツール入力を変更する
</h3>

この例は Write ツール呼び出しをインターセプトし、`file_path` 引数を書き直して `/sandbox` を先頭に追加し、すべてのファイル書き込みをサンドボックスディレクトリにリダイレクトします。コールバックは変更されたパスで `updatedInput` を返し、`permissionDecision: 'allow'` を返して書き直された操作を自動承認します。

<CodeGroup>
  ```python Python theme={null}
  async def redirect_to_sandbox(input_data, tool_use_id, context):
      if input_data["hook_event_name"] != "PreToolUse":
          return {}

      if input_data["tool_name"] == "Write":
          original_path = input_data["tool_input"].get("file_path", "")
          return {
              "hookSpecificOutput": {
                  "hookEventName": input_data["hook_event_name"],
                  "permissionDecision": "allow",
                  "updatedInput": {
                      **input_data["tool_input"],
                      "file_path": f"/sandbox{original_path}",
                  },
              }
          }
      return {}
  ```

  ```typescript TypeScript theme={null}
  const redirectToSandbox: HookCallback = async (input, toolUseID, { signal }) => {
    if (input.hook_event_name !== "PreToolUse") return {};

    const preInput = input as PreToolUseHookInput;
    const toolInput = preInput.tool_input as Record<string, unknown>;
    if (preInput.tool_name === "Write") {
      const originalPath = toolInput.file_path as string;
      return {
        hookSpecificOutput: {
          hookEventName: preInput.hook_event_name,
          permissionDecision: "allow",
          updatedInput: {
            ...toolInput,
            file_path: `/sandbox${originalPath}`
          }
        }
      };
    }
    return {};
  };
  ```
</CodeGroup>

<Note>
  `updatedInput` を使用する場合、`permissionDecision: 'allow'` を含めて変更された入力を自動承認するか、`permissionDecision: 'ask'` を含めてユーザーに表示する必要があります。`'defer'` の場合、`updatedInput` は無視されます。常に元の `tool_input` を変更するのではなく、新しいオブジェクトを返します。
</Note>

<h3 id="add-context-and-block-a-tool">
  コンテキストを追加してツールをブロックする
</h3>

この例は `/etc` ディレクトリへの書き込みをブロックし、モデルとユーザーの両方に理由を説明します。

* `permissionDecision: 'deny'` はツール呼び出しを停止します。
* `permissionDecisionReason` はモデルに理由を伝えるため、再試行を避けます。
* `systemMessage` はユーザーに何が起こったかを表示します。

<CodeGroup>
  ```python Python theme={null}
  async def block_etc_writes(input_data, tool_use_id, context):
      file_path = input_data["tool_input"].get("file_path", "")

      if file_path.startswith("/etc"):
          return {
              # トップレベルフィールド：ユーザーに表示されるメッセージ
              "systemMessage": "Remember: system directories like /etc are protected.",
              # hookSpecificOutput：操作をブロックする
              "hookSpecificOutput": {
                  "hookEventName": input_data["hook_event_name"],
                  "permissionDecision": "deny",
                  "permissionDecisionReason": "Writing to /etc is not allowed",
              },
          }
      return {}
  ```

  ```typescript TypeScript theme={null}
  const blockEtcWrites: HookCallback = async (input, toolUseID, { signal }) => {
    const preInput = input as PreToolUseHookInput;
    const toolInput = preInput.tool_input as Record<string, unknown>;
    const filePath = toolInput?.file_path as string;

    if (filePath?.startsWith("/etc")) {
      return {
        // トップレベルフィールド：ユーザーに表示されるメッセージ
        systemMessage: "Remember: system directories like /etc are protected.",
        // hookSpecificOutput：操作をブロックする
        hookSpecificOutput: {
          hookEventName: preInput.hook_event_name,
          permissionDecision: "deny",
          permissionDecisionReason: "Writing to /etc is not allowed"
        }
      };
    }
    return {};
  };
  ```
</CodeGroup>

<h3 id="auto-approve-specific-tools">
  特定のツールを自動承認する
</h3>

デフォルトでは、エージェントは特定のツールを使用する前にパーミッションを求めるプロンプトを表示する場合があります。この例は、`permissionDecision: 'allow'` を返すことで読み取り専用ファイルシステムツール（Read、Glob、Grep）を自動承認し、ユーザー確認なしで実行できるようにしながら、他のすべてのツールは通常のパーミッションチェックの対象のままにします。

<CodeGroup>
  ```python Python theme={null}
  async def auto_approve_read_only(input_data, tool_use_id, context):
      if input_data["hook_event_name"] != "PreToolUse":
          return {}

      read_only_tools = ["Read", "Glob", "Grep"]
      if input_data["tool_name"] in read_only_tools:
          return {
              "hookSpecificOutput": {
                  "hookEventName": input_data["hook_event_name"],
                  "permissionDecision": "allow",
                  "permissionDecisionReason": "Read-only tool auto-approved",
              }
          }
      return {}
  ```

  ```typescript TypeScript theme={null}
  const autoApproveReadOnly: HookCallback = async (input, toolUseID, { signal }) => {
    if (input.hook_event_name !== "PreToolUse") return {};

    const preInput = input as PreToolUseHookInput;
    const readOnlyTools = ["Read", "Glob", "Grep"];
    if (readOnlyTools.includes(preInput.tool_name)) {
      return {
        hookSpecificOutput: {
          hookEventName: preInput.hook_event_name,
          permissionDecision: "allow",
          permissionDecisionReason: "Read-only tool auto-approved"
        }
      };
    }
    return {};
  };
  ```
</CodeGroup>

<h3 id="register-multiple-hooks">
  複数のフックを登録する
</h3>

イベントが発火すると、すべてのマッチするフックが並列で実行されます。パーミッション決定の場合、最も制限的な結果が優先されます。単一の `deny` は、他のフックが何を返すかに関係なく、ツール呼び出しをブロックします。完了順序は非決定的であるため、別のフックが最初に実行されたことに依存するのではなく、各フックが独立して動作するように記述します。

以下の例は、すべてのツール呼び出しに対して 3 つの独立したチェックを登録します。

<CodeGroup>
  ```python Python theme={null}
  options = ClaudeAgentOptions(
      hooks={
          "PreToolUse": [
              HookMatcher(hooks=[authorization_check]),
              HookMatcher(hooks=[input_validator]),
              HookMatcher(hooks=[audit_logger]),
          ]
      }
  )
  ```

  ```typescript TypeScript theme={null}
  const options = {
    hooks: {
      PreToolUse: [
        { hooks: [authorizationCheck] },
        { hooks: [inputValidator] },
        { hooks: [auditLogger] }
      ]
    }
  };
  ```
</CodeGroup>

<h3 id="filter-with-multi-tool-matchers">
  マルチツールマッチャーでフィルタリングする
</h3>

マルチツールマッチャーを使用して、関連するツール間で 1 つのコールバックを共有します。この例は、異なるスコープを持つ 3 つのマッチャーを登録します。

* パイプで区切られた正確なリスト（`Write|Edit|Delete`）は、ファイル変更ツールに対してのみ `file_security_hook` をトリガーします。
* 正規表現（`^mcp__`）は、名前が `mcp__` で始まる任意の MCP ツールに対して `mcp_audit_hook` をトリガーします。
* 省略されたマッチャーは、名前に関係なくすべてのツール呼び出しに対して `global_logger` をトリガーします。

<CodeGroup>
  ```python Python theme={null}
  options = ClaudeAgentOptions(
      hooks={
          "PreToolUse": [
              # ファイル変更ツールをマッチングする
              HookMatcher(matcher="Write|Edit|Delete", hooks=[file_security_hook]),
              # すべての MCP ツールをマッチングする
              HookMatcher(matcher="^mcp__", hooks=[mcp_audit_hook]),
              # すべてをマッチングする（マッチャーなし）
              HookMatcher(hooks=[global_logger]),
          ]
      }
  )
  ```

  ```typescript TypeScript theme={null}
  const options = {
    hooks: {
      PreToolUse: [
        // ファイル変更ツールをマッチングする
        { matcher: "Write|Edit|Delete", hooks: [fileSecurityHook] },

        // すべての MCP ツールをマッチングする
        { matcher: "^mcp__", hooks: [mcpAuditHook] },

        // すべてをマッチングする（マッチャーなし）
        { hooks: [globalLogger] }
      ]
    }
  };
  ```
</CodeGroup>

<h3 id="track-subagent-activity">
  サブエージェントアクティビティを追跡する
</h3>

`SubagentStop` フックを使用して、サブエージェントが作業を完了するときを監視します。[TypeScript](/docs/ja/agent-sdk/typescript#hookinput) および [Python](/docs/ja/agent-sdk/python#hookinput) SDK リファレンスで完全な入力型を参照してください。この例は、サブエージェントが完了するたびに概要をログします。

<CodeGroup>
  ```python Python theme={null}
  async def subagent_tracker(input_data, tool_use_id, context):
      # サブエージェントが完了したときにサブエージェント詳細をログする
      print(f"[SUBAGENT] Completed: {input_data['agent_id']}")
      print(f"  Transcript: {input_data['agent_transcript_path']}")
      print(f"  Tool use ID: {tool_use_id}")
      print(f"  Stop hook active: {input_data.get('stop_hook_active')}")
      return {}


  options = ClaudeAgentOptions(
      hooks={"SubagentStop": [HookMatcher(hooks=[subagent_tracker])]}
  )
  ```

  ```typescript TypeScript theme={null}
  import { HookCallback, SubagentStopHookInput } from "@anthropic-ai/claude-agent-sdk";

  const subagentTracker: HookCallback = async (input, toolUseID, { signal }) => {
    // SubagentStopHookInput にキャストしてサブエージェント固有のフィールドにアクセスする
    const subInput = input as SubagentStopHookInput;

    // サブエージェントが完了したときにサブエージェント詳細をログする
    console.log(`[SUBAGENT] Completed: ${subInput.agent_id}`);
    console.log(`  Transcript: ${subInput.agent_transcript_path}`);
    console.log(`  Tool use ID: ${toolUseID}`);
    console.log(`  Stop hook active: ${subInput.stop_hook_active}`);
    return {};
  };

  const options = {
    hooks: {
      SubagentStop: [{ hooks: [subagentTracker] }]
    }
  };
  ```
</CodeGroup>

<h3 id="make-http-requests-from-hooks">
  フックから HTTP リクエストを行う
</h3>

フックは HTTP リクエストなどの非同期操作を実行できます。フック内でエラーをキャッチして、処理されない例外がエージェントを中断しないようにします。

この例は、各ツールが完了した後にウェブフックを送信し、どのツールが実行されたかと実行時刻をログします。フックはエラーをキャッチして、失敗したウェブフックがエージェントを中断しないようにします。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  import json
  import urllib.request
  from datetime import datetime


  def _send_webhook(tool_name):
      """外部ウェブフックにツール使用データを POST する同期ヘルパー。"""
      data = json.dumps(
          {
              "tool": tool_name,
              "timestamp": datetime.now().isoformat(),
          }
      ).encode()
      req = urllib.request.Request(
          "https://api.example.com/webhook",
          data=data,
          headers={"Content-Type": "application/json"},
          method="POST",
      )
      urllib.request.urlopen(req)


  async def webhook_notifier(input_data, tool_use_id, context):
      # ツールが完了した後（PostToolUse）に発火し、前ではない
      if input_data["hook_event_name"] != "PostToolUse":
          return {}

      try:
          # イベントループをブロックしないようにスレッドでブロッキング HTTP 呼び出しを実行する
          await asyncio.to_thread(_send_webhook, input_data["tool_name"])
      except Exception as e:
          # エラーをログするが、発生させない。失敗したウェブフックはエージェントを停止すべきではない
          print(f"Webhook request failed: {e}")

      return {}
  ```

  ```typescript TypeScript theme={null}
  import { query, HookCallback, PostToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

  const webhookNotifier: HookCallback = async (input, toolUseID, { signal }) => {
    // ツールが完了した後（PostToolUse）に発火し、前ではない
    if (input.hook_event_name !== "PostToolUse") return {};

    try {
      await fetch("https://api.example.com/webhook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: (input as PostToolUseHookInput).tool_name,
          timestamp: new Date().toISOString()
        }),
        // フックがタイムアウトした場合、リクエストがキャンセルされるように signal を渡す
        signal
      });
    } catch (error) {
      // キャンセルを他のエラーから分けて処理する
      if (error instanceof Error && error.name === "AbortError") {
        console.log("Webhook request cancelled");
      }
      // 再スローしない。失敗したウェブフックはエージェントを停止すべきではない
    }

    return {};
  };

  // PostToolUse フックとして登録する
  for await (const message of query({
    prompt: "Refactor the auth module",
    options: {
      hooks: {
        PostToolUse: [{ hooks: [webhookNotifier] }]
      }
    }
  })) {
    console.log(message);
  }
  ```
</CodeGroup>

<h3 id="forward-notifications-to-slack">
  通知を Slack に転送する
</h3>

`Notification` フックを使用して、エージェントからのシステム通知を受け取り、外部サービスに転送します。通知は以下のようなイベントタイプに対して発火します。

* `permission_prompt`（Claude がパーミッションを必要とする）
* `idle_prompt`（Claude が入力を待機している）
* `auth_success`（認証が完了した）
* `elicitation_dialog`、`elicitation_complete`、および `elicitation_response`（ユーザープロンプト引き出しフロー用）

各通知には、人間が読める説明を含む `message` フィールドと、オプションで `title` が含まれます。

この例は、すべての通知を Slack チャネルに転送します。[Slack 受信ウェブフック URL](https://api.slack.com/messaging/webhooks) が必要です。これは、Slack ワークスペースにアプリを追加し、受信ウェブフックを有効にすることで作成します。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  import json
  import urllib.request

  from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher


  def _send_slack_notification(message):
      """受信ウェブフック経由で Slack にメッセージを送信する同期ヘルパー。"""
      data = json.dumps({"text": f"Agent status: {message}"}).encode()
      req = urllib.request.Request(
          "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
          data=data,
          headers={"Content-Type": "application/json"},
          method="POST",
      )
      urllib.request.urlopen(req)


  async def notification_handler(input_data, tool_use_id, context):
      try:
          # イベントループをブロックしないようにスレッドでブロッキング HTTP 呼び出しを実行する
          await asyncio.to_thread(_send_slack_notification, input_data.get("message", ""))
      except Exception as e:
          print(f"Failed to send notification: {e}")

      # 空のオブジェクトを返す。通知フックはエージェント動作を変更しない
      return {}


  async def main():
      options = ClaudeAgentOptions(
          hooks={
              # 通知イベントのフックを登録する（マッチャーは不要）
              "Notification": [HookMatcher(hooks=[notification_handler])],
          },
      )

      async with ClaudeSDKClient(options=options) as client:
          await client.query("Analyze this codebase")
          async for message in client.receive_response():
              print(message)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query, HookCallback, NotificationHookInput } from "@anthropic-ai/claude-agent-sdk";

  // 通知を Slack に送信するフックコールバックを定義する
  const notificationHandler: HookCallback = async (input, toolUseID, { signal }) => {
    // NotificationHookInput にキャストして message フィールドにアクセスする
    const notification = input as NotificationHookInput;

    try {
      // 通知メッセージを Slack 受信ウェブフックに POST する
      await fetch("https://hooks.slack.com/services/YOUR/WEBHOOK/URL", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: `Agent status: ${notification.message}`
        }),
        // フックがタイムアウトした場合、リクエストがキャンセルされるように signal を渡す
        signal
      });
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        console.log("Notification cancelled");
      } else {
        console.error("Failed to send notification:", error);
      }
    }

    // 空のオブジェクトを返す。通知フックはエージェント動作を変更しない
    return {};
  };

  // 通知イベントのフックを登録する（マッチャーは不要）
  for await (const message of query({
    prompt: "Analyze this codebase",
    options: {
      hooks: {
        Notification: [{ hooks: [notificationHandler] }]
      }
    }
  })) {
    console.log(message);
  }
  ```
</CodeGroup>

<h2 id="fix-common-issues">
  一般的な問題を修正する
</h2>

<h3 id="hook-not-firing">
  フックが発火しない
</h3>

* フックイベント名が正しく、大文字と小文字が区別されていることを確認します（`preToolUse` ではなく `PreToolUse`）
* マッチャーパターンがツール名と正確にマッチしていることを確認します
* フックが `options.hooks` の正しいイベントタイプの下にあることを確認します
* `Notification` や `SubagentStop` などの非ツールフックでマッチャーをサポートする場合、マッチャーは異なるフィールドに対してマッチングされ、`Stop` はマッチャーを完全に無視します（[マッチャーパターン](/docs/ja/hooks#matcher-patterns)を参照）
* エージェントが [`max_turns`](/docs/ja/agent-sdk/python#claudeagentoptions) 制限に達するとセッションが終了する前にフックが実行される可能性があるため、フックが発火しない場合があります

<h3 id="matcher-not-filtering-as-expected">
  マッチャーが期待どおりにフィルタリングしない
</h3>

マッチャーはツール名のみをマッチングし、ファイルパスやその他の引数はマッチングしません。ファイルパスでフィルタリングするには、フック内で `tool_input.file_path` をチェックします：

```typescript theme={null}
const myHook: HookCallback = async (input, toolUseID, { signal }) => {
  const preInput = input as PreToolUseHookInput;
  const toolInput = preInput.tool_input as Record<string, unknown>;
  const filePath = toolInput?.file_path as string;
  if (!filePath?.endsWith(".md")) return {}; // マークダウンファイル以外をスキップ
  // マークダウンファイルを処理...
  return {};
};
```

<h3 id="hook-timeout">
  フックタイムアウト
</h3>

* `HookMatcher` 設定で `timeout` 値を増やします
* TypeScript で 3 番目のコールバック引数から `AbortSignal` を使用して、キャンセルを適切に処理します

`UserPromptSubmit` または [`UserPromptExpansion`](/docs/ja/hooks#userpromptexpansion) コールバックがタイムアウトを超過した場合、そのプロンプトはタイムアウトメッセージでブロックされ、セッションは続行されます。クエリを中断すると、保留中のツール呼び出しがキャンセルされます。v2.1.208 より前では、これらのイベントのコールバックタイムアウトはクエリを `error_during_execution` で終了し、保留中の `PreToolUse` コールバック中の中断はツール呼び出しを続行させる可能性がありました。

<h3 id="tool-blocked-unexpectedly">
  ツールが予期せずブロックされた
</h3>

* すべての `PreToolUse` フックで `permissionDecision: 'deny'` を返していないかチェックします
* フックにログを追加して、返している `permissionDecisionReason` を確認します
* マッチャーパターンが広すぎないことを確認します（空のマッチャーはすべてのツールにマッチングします）

<h3 id="modified-input-not-applied">
  変更された入力が適用されない
</h3>

* `updatedInput` が `hookSpecificOutput` の内部にあり、トップレベルにないことを確認します：

  ```typescript theme={null}
  return {
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow",
      updatedInput: { command: "new command" }
    }
  };
  ```

* 変更された入力を自動承認するには `permissionDecision: 'allow'` を返すか、ユーザーに承認を求めるには `'ask'` を返します

* `hookSpecificOutput` に `hookEventName` を含めて、出力がどのフック型用かを識別します

<h3 id="session-hooks-not-available-in-python">
  Python でセッションフックが利用できない
</h3>

`SessionStart` と `SessionEnd` は TypeScript で SDK コールバックフックとして登録できますが、Python SDK では利用できません（`HookEvent` は除外されています）。Python では、設定ファイルで定義された[シェルコマンドフック](/docs/ja/hooks#hook-events)としてのみ利用可能です（たとえば、`.claude/settings.json`）。SDK アプリケーションからシェルコマンドフックをロードするには、[`setting_sources`](/docs/ja/agent-sdk/python#settingsource) または [`settingSources`](/docs/ja/agent-sdk/typescript#settingsource) で適切な設定ソースを含めます：

<CodeGroup>
  ```python Python theme={null}
  options = ClaudeAgentOptions(
      setting_sources=["project"],  # フックを含む .claude/settings.json をロード
  )
  ```

  ```typescript TypeScript theme={null}
  const options = {
    settingSources: ["project"] // フックを含む .claude/settings.json をロード
  };
  ```
</CodeGroup>

Python SDK コールバックとして初期化ロジックを実行するには、`client.receive_response()` からの最初のメッセージをトリガーとして使用します。

<h3 id="subagent-permission-prompts-multiplying">
  サブエージェントパーミッションプロンプトが増加する
</h3>

複数のサブエージェントを生成する場合、各サブエージェントは個別にパーミッションをリクエストする可能性があります。サブエージェントは親エージェントのパーミッションを自動的に継承しません。繰り返されるプロンプトを避けるには、`PreToolUse` フックを使用して特定のツールを自動承認するか、サブエージェントセッションに適用されるパーミッションルールを設定します。

<h3 id="recursive-hook-loops-with-subagents">
  サブエージェントを使用した再帰的フックループ
</h3>

サブエージェントを生成する `UserPromptSubmit` フックは、それらのサブエージェントが同じフックをトリガーする場合、無限ループを作成できます。これを防ぐには：

* サブエージェント指標をチェックしてからサブエージェントを生成する前にフック入力をチェックします
* 共有変数またはセッション状態を使用して、既にサブエージェント内にいるかどうかを追跡します
* フックをトップレベルエージェントセッションのみに実行するようにスコープします

<h3 id="systemmessage-not-appearing-in-output">
  systemMessage が出力に表示されない
</h3>

`systemMessage` フィールドはユーザーにメッセージを表示します。デフォルトでは SDK はメッセージストリームにフック出力を表示しないため、`includeHookEvents`（Python では `include_hook_events`）を設定しない限り、メッセージが表示されない場合があります。代わりにモデルにコンテキストを渡すには、[`additionalContext`](/docs/ja/hooks#add-context-for-claude)を返します。

フック決定をアプリケーションに確実に表示する必要がある場合は、別途ログするか、専用の出力チャネルを使用します。

<h2 id="related-resources">
  関連リソース
</h2>

* [Claude Code フックリファレンス](/docs/ja/hooks)：完全な JSON 入力/出力スキーマ、イベント文書、およびマッチャーパターン
* [Claude Code フックガイド](/docs/ja/hooks-guide)：シェルコマンドフックの例とウォークスルー
* [TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript)：フック型、入力/出力定義、および設定オプション
* [Python SDK リファレンス](/docs/ja/agent-sdk/python)：フック型、入力/出力定義、および設定オプション
* [パーミッション](/docs/ja/agent-sdk/permissions)：エージェントが何をできるかを制御します
* [カスタムツール](/docs/ja/agent-sdk/custom-tools)：エージェント機能を拡張するツールを構築します
