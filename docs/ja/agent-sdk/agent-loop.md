> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# エージェントループの仕組み

> メッセージライフサイクル、ツール実行、コンテキストウィンドウ、および SDK エージェントを支えるアーキテクチャを理解します。

Agent SDK を使用すると、Claude Code の自律型エージェントループを独自のアプリケーションに組み込むことができます。SDK はスタンドアロンパッケージで、ツール、権限、コスト制限、および出力をプログラムで制御できます。これを使用するために Claude Code CLI をインストールする必要はありません。

エージェントを開始すると、SDK は Claude Code を支える[実行ループ](/docs/ja/how-claude-code-works#the-agentic-loop)と同じものを実行します。Claude はプロンプトを評価し、ツールを呼び出してアクションを実行し、結果を受け取り、タスクが完了するまで繰り返します。このページでは、そのループ内で何が起こるかを説明し、エージェントを効果的に構築、デバッグ、最適化できるようにします。

<h2 id="the-loop-at-a-glance">
  ループの概要
</h2>

すべてのエージェントセッションは同じサイクルに従います。

<img src="https://mintcdn.com/claude-code/ikqp3_70mqIahteV/images/agent-loop-diagram.svg?fit=max&auto=format&n=ikqp3_70mqIahteV&q=85&s=1c6e8f28d80dba14a7287419656f1237" alt="エージェントループの図：プロンプトが agentic ループに入り、Claude が評価して、ツール呼び出しをリクエストするか最終回答を返すか、またはツール呼び出しの結果が別の評価にフィードバックされます" width="720" height="212" data-path="images/agent-loop-diagram.svg" />

1. **プロンプトを受け取る。** Claude はプロンプト、システムプロンプト、ツール定義、および会話履歴とともにプロンプトを受け取ります。SDK はセッションメタデータを含むサブタイプ `"init"` の[`SystemMessage`](#message-types)を生成します。
2. **評価して応答する。** Claude は現在の状態を評価し、どのように進めるかを決定します。テキストで応答したり、1 つ以上のツール呼び出しをリクエストしたり、その両方を行ったりできます。SDK はテキストとツール呼び出しリクエストを含む[`AssistantMessage`](#message-types)を生成します。
3. **ツールを実行する。** SDK は要求された各ツールを実行し、結果を収集します。ツール結果の各セットは次の決定のために Claude にフィードバックされます。[hooks](/docs/ja/agent-sdk/hooks)を使用して、ツール呼び出しを実行前に傍受、変更、またはブロックできます。
4. **繰り返す。** ステップ 2 と 3 がサイクルとして繰り返されます。各完全なサイクルは 1 ターンです。Claude はツール呼び出しと結果の処理を続け、ツール呼び出しのない応答を生成するまで続きます。
5. **結果を返す。** SDK は最終的な[`AssistantMessage`](#message-types)（テキスト応答、ツール呼び出しなし）を生成し、その後に最終テキスト、トークン使用量、コスト、およびセッション ID を含む[`ResultMessage`](#message-types)を生成します。

簡単な質問（「ここにはどのようなファイルがありますか？」）は、`Glob` を呼び出して結果で応答する 1 ～ 2 ターンで済む場合があります。複雑なタスク（「認証モジュールをリファクタリングしてテストを更新する」）は、多くのターンにわたって数十のツール呼び出しをチェーンでき、ファイルを読み取り、コードを編集し、テストを実行し、Claude が各結果に基づいてアプローチを調整します。

<h2 id="turns-and-messages">
  ターンとメッセージ
</h2>

ターンはループ内の 1 往復です。Claude はツール呼び出しを含む出力を生成し、SDK はそれらのツールを実行し、結果は自動的に Claude にフィードバックされます。これはコードに制御を戻さずに発生します。Claude がツール呼び出しのない出力を生成するまでターンが続き、その時点でループが終了し、最終結果が配信されます。

プロンプト「Fix the failing tests in auth.ts」の完全なセッションがどのようなものかを考えてみましょう。

まず、SDK はプロンプトを Claude に送信し、セッションメタデータを含む[`SystemMessage`](#message-types)を生成します。その後、ループが開始されます。

1. **ターン 1：** Claude は `Bash` を呼び出して `npm test` を実行します。SDK は[`AssistantMessage`](#message-types)とツール呼び出しを生成し、コマンドを実行し、出力（3 つの失敗）を含む[`UserMessage`](#message-types)を生成します。
2. **ターン 2：** Claude は `Read` を呼び出して `auth.ts` と `auth.test.ts` を読み取ります。SDK はファイルの内容を返し、`AssistantMessage` を生成します。
3. **ターン 3：** Claude は `Edit` を呼び出して `auth.ts` を修正し、`Bash` を呼び出して `npm test` を再実行します。3 つのテストすべてが成功します。SDK は `AssistantMessage` を生成します。
4. **最終ターン：** Claude はツール呼び出しのないテキストのみの応答を生成します。「認証バグを修正し、3 つのテストすべてが成功しました。」SDK はこのテキストを含む最終 `AssistantMessage` を生成し、その後、同じテキストとコストおよび使用量を含む[`ResultMessage`](#message-types)を生成します。

これは 4 ターンでした。3 つはツール呼び出し、1 つは最終テキストのみの応答です。

`max_turns` / `maxTurns` でループをキャップできます。これはツール使用ターンのみをカウントします。たとえば、上記のループで `max_turns=2` は編集ステップの前に停止していたでしょう。`max_budget_usd` / `maxBudgetUsd` を使用して、支出しきい値に基づいてターンをキャップすることもできます。

制限がない場合、ループは Claude が独自に終了するまで実行されます。これは適切にスコープされたタスクには問題ありませんが、オープンエンドのプロンプト（「このコードベースを改善する」）では長時間実行される可能性があります。予算を設定することは、本番エージェントの良いデフォルトです。以下の[ターンと予算](#turns-and-budget)でオプションリファレンスを参照してください。

<h2 id="message-types">
  メッセージタイプ
</h2>

ループが実行されると、SDK はメッセージのストリームを生成します。各メッセージは、ループのどのステージから来たかを示すタイプを持ちます。5 つのコアタイプは次のとおりです。

* **`SystemMessage`：** セッションライフサイクルイベント。`subtype` フィールドはそれらを区別します。

  * `"init"`：実行のセッションメタデータ。セッション起動中に `SessionStart` または `Setup` フックが実行される場合、その[フックライフサイクルメッセージ](/docs/ja/agent-sdk/typescript#sdkhookstartedmessage)は `init` メッセージの前に到着します
  * `"compact_boundary"`：[圧縮](#automatic-compaction)後に発火します
  * `"informational"`：ループからのプレーンテキストステータスバナー
  * `"worker_shutting_down"`：ホストが終了しているか Remote Control が切断されたため、現在のターン後にループが終了します

  TypeScript では、`"init"` 以外の各サブタイプは `SDKSystemMessage` のサブタイプではなく、[`SDKMessage` ユニオン](/docs/ja/agent-sdk/typescript#sdkmessage)内の独自のタイプです。
* **`AssistantMessage`：** 最終テキストのみの応答を含む、各 Claude 応答の後に生成されます。そのターンからのテキストコンテンツブロックとツール呼び出しブロックを含みます。
* **`UserMessage`：** 各ツール実行後、Claude に送り返されるツール結果コンテンツとともに生成されます。ループ中盤でストリーミングするユーザー入力に対しても生成されます。
* **`StreamEvent`：** 部分メッセージが有効な場合のみ生成されます。生の API ストリーミングイベント（テキストデルタ、ツール入力チャンク）を含みます。[ストリーム応答](/docs/ja/agent-sdk/streaming-output)を参照してください。
* **`ResultMessage`：** エージェントループの終了をマークします。最終テキスト結果、トークン使用量、コスト、およびセッション ID を含みます。`subtype` フィールドをチェックして、タスクが成功したか制限に達したかを判断します。`prompt_suggestion` などの少数の末尾システムイベントはその後に到着する可能性があるため、結果で中断するのではなく、ストリームを完了まで反復処理します。[結果を処理する](#handle-the-result)を参照してください。

これら 5 つのタイプは、両方の SDK でエージェントループライフサイクル全体をカバーしています。TypeScript SDK は、追加の観測可能性イベント（フックイベント、ツール進捗、レート制限、タスク通知）も生成し、追加の詳細を提供しますが、ループを駆動するために必須ではありません。完全なリストについては、[Python メッセージタイプリファレンス](/docs/ja/agent-sdk/python#message-types)と [TypeScript メッセージタイプリファレンス](/docs/ja/agent-sdk/typescript#message-types)を参照してください。

<h3 id="handle-messages">
  メッセージを処理する
</h3>

処理するメッセージは、構築しているものによって異なります。

* **最終結果のみ：** `ResultMessage` を処理して、出力、コスト、およびタスクが成功したか制限に達したかを取得します。
* **進捗更新：** `AssistantMessage` を処理して、Claude が各ターンで何をしているか、どのツールを呼び出したかを確認します。
* **ライブストリーミング：** 部分メッセージを有効にする（Python では `include_partial_messages`、TypeScript では `includePartialMessages`）して、リアルタイムで `StreamEvent` メッセージを取得します。[リアルタイムでストリーム応答](/docs/ja/agent-sdk/streaming-output)を参照してください。

メッセージタイプをチェックする方法は SDK によって異なります。

* **Python：** `claude_agent_sdk` からインポートされたクラスに対して `isinstance()` でメッセージタイプをチェックします（たとえば、`isinstance(message, ResultMessage)`）。
* **TypeScript：** `type` 文字列フィールドをチェックします（たとえば、`message.type === "result"`）。`AssistantMessage` と `UserMessage` は生の API メッセージを `.message` フィールドでラップするため、コンテンツブロックは `message.content` ではなく `message.message.content` にあります。

<Accordion title="例：メッセージタイプをチェックして結果を処理する">
  <CodeGroup>
    ```python Python theme={null}
    import asyncio
    from claude_agent_sdk import query, AssistantMessage, ResultMessage


    async def main():
        try:
            async for message in query(prompt="Summarize this project"):
                if isinstance(message, AssistantMessage):
                    print(f"Turn completed: {len(message.content)} content blocks")
                if isinstance(message, ResultMessage):
                    if message.subtype == "success":
                        print(message.result)
                    else:
                        print(f"Stopped: {message.subtype}")
        except Exception as error:
            # A single-shot query() raises after yielding an error result. If the
            # failure was an error result, the error subtype branches above have
            # already run; connection or process failures yield no result message.
            print(f"Session ended with an error: {error}")


    asyncio.run(main())
    ```

    ```typescript TypeScript theme={null}
    import { query } from "@anthropic-ai/claude-agent-sdk";

    try {
      for await (const message of query({ prompt: "Summarize this project" })) {
        if (message.type === "assistant") {
          console.log(`Turn completed: ${message.message.content.length} content blocks`);
        }
        if (message.type === "result") {
          if (message.subtype === "success") {
            console.log(message.result);
          } else {
            console.log(`Stopped: ${message.subtype}`);
          }
        }
      }
    } catch (error) {
      // A single-shot query() throws after yielding an error result. If the
      // failure was an error result, the error subtype branches above have
      // already run; connection or process failures yield no result message.
      console.log(`Session ended with an error: ${error}`);
    }
    ```
  </CodeGroup>
</Accordion>

<h2 id="tool-execution">
  ツール実行
</h2>

ツールはエージェントにアクションを実行する機能を提供します。ツールがなければ、Claude はテキストでのみ応答できます。ツールを使用すると、Claude はファイルを読み取り、コマンドを実行し、コードを検索し、外部サービスと相互作用できます。

<h3 id="built-in-tools">
  組み込みツール
</h3>

SDK には Claude Code を支えるのと同じツールが含まれています。

| カテゴリ           | ツール                                                         | 機能                                    |
| :------------- | :---------------------------------------------------------- | :------------------------------------ |
| **ファイル操作**     | `Read`、`Edit`、`Write`                                       | ファイルを読み取り、変更、作成                       |
| **検索**         | `Glob`、`Grep`                                               | パターンでファイルを検索、正規表現でコンテンツを検索            |
| **実行**         | `Bash`                                                      | シェルコマンド、スクリプト、git 操作を実行               |
| **Web**        | `WebSearch`、`WebFetch`                                      | Web を検索、ページを取得して解析                    |
| **検出**         | `ToolSearch`                                                | すべてをプリロードする代わりに、オンデマンドでツールを動的に検索してロード |
| **オーケストレーション** | `Agent`、`Skill`、`AskUserQuestion`、`TaskCreate`、`TaskUpdate` | サブエージェントを生成、スキルを呼び出し、ユーザーに質問、タスクを追跡   |

組み込みツール以外に、以下を実行できます。

* **外部サービスを接続する** [MCP サーバー](/docs/ja/agent-sdk/mcp)（データベース、ブラウザ、API）
* **カスタムツールを定義する** [カスタムツールハンドラー](/docs/ja/agent-sdk/custom-tools)
* **プロジェクトスキルをロードする** [設定ソース](/docs/ja/agent-sdk/claude-code-features)経由で再利用可能なワークフロー

<h3 id="tool-permissions">
  ツール権限
</h3>

Claude はタスクに基づいてどのツールを呼び出すかを決定しますが、それらの呼び出しの実行を許可するかどうかを制御します。特定のツールを自動承認したり、他のツールを完全にブロックしたり、すべてに対して承認を要求したりできます。3 つのオプションが連携して、何が実行されるかを決定します。

* **`allowed_tools` / `allowedTools`** リストされたツールを自動承認します。許可されたツールリストに `["Read", "Glob", "Grep"]` がある読み取り専用エージェントは、プロンプトなしでそれらのツールを実行します。リストされていないツールは引き続き利用可能ですが、権限が必要です。
* **`disallowed_tools` / `disallowedTools`** リストされたツールをブロックします。他の設定に関係なく。ツールが実行される前にルールがチェックされる順序については、[権限](/docs/ja/agent-sdk/permissions)を参照してください。
* **`permission_mode` / `permissionMode`** 許可または拒否ルールでカバーされていないツールに何が起こるかを制御します。利用可能なモードについては、[権限モード](#permission-mode)を参照してください。

`"Bash(npm *)"` のようなルールで個別のツールをスコープすることもできます。これにより、特定のコマンドのみを許可できます。完全なルール構文については、[権限](/docs/ja/agent-sdk/permissions)を参照してください。

ツールが拒否されると、Claude はツール結果として拒否メッセージを受け取り、通常は別のアプローチを試みるか、進めなかったことを報告します。

<h3 id="parallel-tool-execution">
  並列ツール実行
</h3>

Claude が単一のターンで複数のツール呼び出しをリクエストすると、両方の SDK はツールに応じて同時または順序に実行できます。読み取り専用ツール（`Read`、`Glob`、`Grep`、読み取り専用としてマークされた MCP ツール）は同時に実行できます。状態を変更するツール（`Edit`、`Write`、`Bash`）は競合を避けるために順序に実行されます。

カスタムツールはデフォルトで順序実行されます。カスタムツールの並列実行を有効にするには、その注釈で `readOnlyHint` を設定します。[TypeScript](/docs/ja/agent-sdk/typescript#tool)と[Python](/docs/ja/agent-sdk/python#tool)SDK の両方は MCP SDK からこのフィールド名を使用します。

<h2 id="control-how-the-loop-runs">
  ループの実行方法を制御する
</h2>

ループが実行するターン数、コスト、Claude がどの程度推論するか、ツールが実行前に承認を必要とするかどうかを制限できます。これらはすべて[`ClaudeAgentOptions`](/docs/ja/agent-sdk/python#claudeagentoptions)（Python）/ [`Options`](/docs/ja/agent-sdk/typescript#options)（TypeScript）のフィールドです。

<h3 id="turns-and-budget">
  ターンと予算
</h3>

| オプション                                   | 制御内容       | デフォルト |
| :-------------------------------------- | :--------- | :---- |
| 最大ターン（`max_turns` / `maxTurns`）         | 最大ツール使用往復数 | 制限なし  |
| 最大予算（`max_budget_usd` / `maxBudgetUsd`） | 停止前の最大コスト  | 制限なし  |

どちらかの制限に達すると、SDK は対応するエラーサブタイプ（`error_max_turns` または `error_max_budget_usd`）を含む `ResultMessage` を返します。これらのサブタイプをチェックする方法については[結果を処理する](#handle-the-result)を、構文については[`ClaudeAgentOptions`](/docs/ja/agent-sdk/python#claudeagentoptions) / [`Options`](/docs/ja/agent-sdk/typescript#options)を参照してください。

[ストリーミング入力](/docs/ja/agent-sdk/streaming-vs-single-mode)を使用する場合、ターンがまだ実行中に送信したメッセージは、そのターンが最大ターン制限で終了するときにキューに入ったままになり、独自の最大ターン制限を持つ独自のターンを開始します。v2.1.205 より前では、ターンの最終イテレーションに到着したメッセージは終了ターンに消費され、モデルに到達することなく失われる可能性がありました。

<h3 id="effort-level">
  努力レベル
</h3>

`effort` オプションは Claude が適用する推論の量を制御します。低い努力レベルはターンあたりのトークンが少なく、コストが削減されます。すべてのモデルが努力パラメータをサポートしているわけではありません。どのモデルがサポートしているかについては、[努力](https://platform.claude.com/docs/ja/build-with-claude/effort)を参照してください。

| レベル        | 動作          | 適している用途                                                     |
| :--------- | :---------- | :---------------------------------------------------------- |
| `"low"`    | 最小限の推論、高速応答 | ファイル検索、ディレクトリのリスト                                           |
| `"medium"` | バランスの取れた推論  | ルーチン編集、標準タスク                                                |
| `"high"`   | 徹底的な分析      | リファクタリング、デバッグ                                               |
| `"xhigh"`  | 拡張推論深度      | コーディングと agentic coding タスク。Fable 5、Opus 4.7 以上、Sonnet 5 で推奨 |
| `"max"`    | 最大推論深度      | 深い分析が必要な複数ステップの問題                                           |

`effort` を設定しない場合、両方の SDK はパラメータを設定したままにして、モデルのデフォルト動作に委譲します。

<Note>
  `effort` は各応答内の推論深度のレイテンシとトークンコストをトレードオフします。[拡張思考](https://platform.claude.com/docs/ja/build-with-claude/extended-thinking)は、出力に表示される思考の連鎖ブロックを生成する別の機能です。これらは独立しています。`effort: "low"` を拡張思考有効で設定することも、`effort: "max"` を有効にしないで設定することもできます。
</Note>

単純でスコープが明確なタスク（ファイルのリストや単一の grep の実行など）を実行するエージェントの場合は、低い努力を使用してコストとレイテンシを削減します。トップレベルの `query()` オプションでセッション全体に `effort` を設定するか、[`AgentDefinition`](/docs/ja/agent-sdk/subagents#agentdefinition-configuration)の `effort` フィールドでサブエージェントごとにセッションレベルをオーバーライドします。

<h3 id="permission-mode">
  権限モード
</h3>

権限モードオプション（Python では `permission_mode`、TypeScript では `permissionMode`）は、エージェントがツールを使用する前に承認を求めるかどうかを制御します。

| モード                   | 動作                                                                                                                                                                                                                                                                                                                                                          |
| :-------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `"default"`           | 許可ルールでカバーされていないツールは承認コールバックをトリガーします。コールバックがない場合は拒否                                                                                                                                                                                                                                                                                                          |
| `"acceptEdits"`       | ファイル編集と一般的なファイルシステムコマンド（`mkdir`、`touch`、`mv`、`cp` など）を自動承認します。他の Bash コマンドはデフォルトルールに従います                                                                                                                                                                                                                                                                    |
| `"plan"`              | Claude はソースファイルを編集せずに探索して計画を作成します。ファイル編集は自動承認されず、`canUseTool` コールバックを通じてプロンプトされます                                                                                                                                                                                                                                                                           |
| `"dontAsk"`           | プロンプトしません。[権限ルール](/docs/ja/settings#permission-settings)によって事前承認されたツールが実行され、その他はすべて拒否されます。`AskUserQuestion`、組織が[`ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools)したコネクタツール、および[`requiresUserInteraction`](/docs/ja/mcp#require-approval-for-a-specific-tool)とマークされた MCP ツールは、許可していても拒否されます                                                                 |
| `"auto"`              | モデル分類器を使用して各ツール呼び出しを承認または拒否します。利用可能性と動作については、[自動モード](/docs/ja/permission-modes#eliminate-prompts-with-auto-mode)を参照してください                                                                                                                                                                                                                                        |
| `"bypassPermissions"` | 明示的な[`ask` ルール](/docs/ja/settings#permission-settings)に一致するツール、組織が[`ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools)したコネクタツール、およびユーザーインタラクションが必要なツールを除き、尋ねずにすべての許可されたツールを実行します。権限がどのように評価されるかについては、[権限の評価方法](/docs/ja/agent-sdk/permissions#how-permissions-are-evaluated)を参照してください。Unix でルートとして実行する場合は使用できません。エージェントのアクションが気にするシステムに影響を与えられない隔離環境でのみ使用します |

インタラクティブアプリケーションの場合は、ツール承認コールバックで `"default"` を使用して承認プロンプトを表示します。開発マシン上の自律型エージェントの場合は、`"acceptEdits"` を使用してファイル編集と一般的なファイルシステムコマンド（`mkdir`、`touch`、`mv`、`cp` など）を自動承認しながら、他の `Bash` コマンドを許可ルールの背後にゲートします。CI、コンテナ、またはその他の隔離環境に対して `"bypassPermissions"` を予約します。詳細については、[権限](/docs/ja/agent-sdk/permissions)を参照してください。

<h3 id="model">
  モデル
</h3>

`model` を設定しない場合、SDK は Claude Code のデフォルトを使用します。これは認証方法とサブスクリプションによって異なります。特定のモデルをピン留めするか、より高速で安価なエージェント用に小さいモデルを使用するために明示的に設定します（たとえば、`model="claude-sonnet-5"`）。利用可能な ID については、[モデル](https://platform.claude.com/docs/ja/about-claude/models)を参照してください。

<h2 id="the-context-window">
  コンテキストウィンドウ
</h2>

コンテキストウィンドウは、セッション中に Claude が利用できる情報の総量です。セッション内のターン間でリセットされません。すべてが蓄積されます。システムプロンプト、ツール定義、会話履歴、ツール入力、およびツール出力です。ターン間で同じままのコンテンツ（システムプロンプト、ツール定義、CLAUDE.md）は自動的に[プロンプトキャッシュ](https://platform.claude.com/docs/ja/build-with-claude/prompt-caching)され、繰り返されるプリフィックスのコストとレイテンシが削減されます。

<h3 id="what-consumes-context">
  コンテキストを消費するもの
</h3>

SDK でのコンテキストへの各コンポーネントの影響は次のとおりです。

| ソース                | ロード時期                                                             | 影響                                                                                                                                                                                                                                                                             |
| :----------------- | :---------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **システムプロンプト**      | すべてのリクエスト                                                         | 小さい固定コスト、常に存在                                                                                                                                                                                                                                                                  |
| **CLAUDE.md ファイル** | セッション開始時、[`settingSources`](/docs/ja/agent-sdk/claude-code-features)経由 | すべてのリクエストで完全なコンテンツ（ただしプロンプトキャッシュされるため、最初のリクエストのみが完全なコストを支払う）                                                                                                                                                                                                                   |
| **ツール定義**          | すべてのリクエスト。MCP スキーマはデフォルトで遅延                                       | 組み込みツールスキーマはすべてのリクエストをロードします。[ツール検索](/docs/ja/agent-sdk/mcp#mcp-tool-search)は、デフォルトで MCP ツールスキーマを遅延させ、Google Cloud の Agent Platform または非ファーストパーティの `ANTHROPIC_BASE_URL` でのアップフロントロードにフォールバックします。完全なマトリックスについては、[ツール検索を構成](/docs/ja/agent-sdk/tool-search#configure-tool-search)を参照してください |
| **会話履歴**           | ターン間で蓄積                                                           | 各ターンで増加。プロンプト、応答、ツール入力、ツール出力                                                                                                                                                                                                                                                   |
| **スキル説明**          | セッション開始時、設定ソース経由                                                  | 短い要約。完全なコンテンツは呼び出し時のみロード                                                                                                                                                                                                                                                       |

大きなツール出力は大量のコンテキストを消費します。大きなファイルを読み取るか、詳細な出力を含むコマンドを実行すると、単一のターンで数千のトークンを使用できます。コンテキストはターン間で蓄積されるため、多くのツール呼び出しを含む長いセッションは、短いセッションよりもはるかに多くのコンテキストを構築します。

<h3 id="automatic-compaction">
  自動圧縮
</h3>

コンテキストウィンドウが制限に近づくと、SDK は会話を自動的に圧縮します。古い履歴を要約してスペースを解放し、最新の交換と重要な決定を保持します。SDK はこれが発生したときにストリームで `type: "system"` と `subtype: "compact_boundary"` を含むメッセージを生成します（Python では `SystemMessage`。TypeScript では別の `SDKCompactBoundaryMessage` タイプです）。

圧縮は古いメッセージを要約に置き換えるため、会話の早い段階からの特定の指示は保持されない可能性があります。永続的なルールは初期プロンプトではなく CLAUDE.md に属します（[`settingSources`](/docs/ja/agent-sdk/claude-code-features)経由でロード）。CLAUDE.md コンテンツはすべてのリクエストで再注入されるためです。

圧縮動作をいくつかの方法でカスタマイズできます。

* **CLAUDE.md の要約指示：** 圧縮機は他のコンテキストと同様に CLAUDE.md を読むため、要約時に保持する内容を指示するセクションを含めることができます。セクションヘッダーは自由形式です（マジック文字列ではありません）。圧縮機は意図に基づいて一致します。
* **`PreCompact` フック：** 圧縮が発生する前にカスタムロジックを実行します。たとえば、完全なトランスクリプトをアーカイブします。フックは `trigger` フィールド（`manual` または `auto`）を受け取ります。[hooks](/docs/ja/agent-sdk/hooks)を参照してください。
* **手動圧縮：** `/compact` をプロンプト文字列として送信して、オンデマンドで圧縮をトリガーします。この方法で送信されるコマンドは SDK 入力であり、CLI のみのショートカットではありません。[SDK のコマンド](/docs/ja/agent-sdk/slash-commands)を参照してください。

<Accordion title="例：CLAUDE.md の要約指示">
  プロジェクトの CLAUDE.md にセクションを追加して、圧縮機に保持する内容を指示します。ヘッダー名は特別ではありません。明確なラベルを使用してください。

  ```markdown CLAUDE.md theme={null}
  # Summary instructions

  When summarizing this conversation, always preserve:
  - The current task objective and acceptance criteria
  - File paths that have been read or modified
  - Test results and error messages
  - Decisions made and the reasoning behind them
  ```
</Accordion>

<h3 id="keep-context-efficient">
  コンテキストを効率的に保つ
</h3>

長時間実行されるエージェントのいくつかの戦略。

* **サブタスク用にサブエージェントを使用します。** 各サブエージェントは新しい会話で開始されます（以前のメッセージ履歴はありませんが、独自のシステムプロンプトとプロジェクトレベルのコンテキスト（CLAUDE.md など）をロードします）。親のターンは表示されず、最終応答のみが親にツール結果として返されます。メインエージェントのコンテキストは完全なサブタスクトランスクリプトではなく、その要約で増加します。詳細については、[サブエージェントが継承するもの](/docs/ja/agent-sdk/subagents#what-subagents-inherit)を参照してください。
* **ツールを選別します。** すべてのツール定義はコンテキストスペースを取ります。[`AgentDefinition`](/docs/ja/agent-sdk/subagents#agentdefinition-configuration)の `tools` フィールドを使用してサブエージェントを必要な最小セットにスコープします。
* **MCP サーバーコストを監視します。** [MCP ツール検索](/docs/ja/agent-sdk/mcp#mcp-tool-search)はデフォルトで MCP ツールスキーマを遅延させ、オンデマンドでロードします。ツール検索がオフの場合、Google Cloud の Agent Platform 上の場合、または非ファーストパーティの `ANTHROPIC_BASE_URL` の背後にある場合、各 MCP サーバーはすべてのツールスキーマをすべてのリクエストに追加するため、多くのツールを持つ少数のサーバーは、エージェントが何か作業を行う前に大量のコンテキストを消費できます。
* **ルーチンタスクに低い努力を使用します。** ファイルを読み取るか、ディレクトリをリストするだけで済むエージェント用に[努力](#effort-level)を `"low"` に設定します。これはトークン使用量とコストを削減します。

機能ごとのコンテキストコストの詳細な内訳については、[コンテキストコストを理解する](/docs/ja/features-overview#understand-context-costs)を参照してください。

<h2 id="sessions-and-continuity">
  セッションと継続性
</h2>

SDK との各インタラクションはセッションを作成または継続します。`ResultMessage.session_id` からセッション ID をキャプチャして（両方の SDK で利用可能）、後で再開します。TypeScript SDK は init `SystemMessage` の直接フィールドとしても公開します。Python では、`SystemMessage.data` にネストされています。

再開すると、以前のターンからの完全なコンテキストが復元されます。読み取られたファイル、実行された分析、および実行されたアクション。セッションをフォークして、元のセッションを変更せずに別のアプローチに分岐することもできます。

セッション再開、継続、フォークパターンの完全なガイドについては、[セッション管理](/docs/ja/agent-sdk/sessions)を参照してください。

<Note>
  Python では、`ClaudeSDKClient` は複数の呼び出し間でセッション ID を自動的に処理します。詳細については、[Python SDK リファレンス](/docs/ja/agent-sdk/python#choosing-between-query-and-claudesdkclient)を参照してください。
</Note>

<h2 id="handle-the-result">
  結果を処理する
</h2>

ループが終了すると、`ResultMessage` は何が起こったかを示し、出力を提供します。`subtype` フィールド（両方の SDK で利用可能）は、終了状態をチェックする主な方法です。

| 結果サブタイプ                               | 何が起こったか                                                                             | `result` フィールドは利用可能か？ |
| :------------------------------------ | :---------------------------------------------------------------------------------- | :-------------------: |
| `success`                             | Claude は通常、タスクを完了しました                                                               |           はい          |
| `error_max_turns`                     | 完了前に `maxTurns` 制限に達しました                                                            |          いいえ          |
| `error_max_budget_usd`                | 完了前に `maxBudgetUsd` 制限に達しました                                                        |          いいえ          |
| `error_during_execution`              | エラーがループを中断しました（たとえば、API 障害またはキャンセルされたリクエスト）                                         |          いいえ          |
| `error_max_structured_output_retries` | 設定された再試行制限内で有効な構造化出力が生成されませんでした。すべての試行が検証に失敗したか、モデルフォールバックが成功した再試行なしで完了した出力を取り消しました |          いいえ          |

`result` フィールド（最終テキスト出力）は `success` バリアントにのみ存在するため、読み取る前に常にサブタイプをチェックしてください。すべての結果サブタイプは `total_cost_usd`、`usage`、`num_turns`、および `session_id` を持つため、コストを追跡し、エラー後でも再開できます。Python では、`total_cost_usd` と `usage` はオプションとして型付けされ、一部のエラーパスで `None` である可能性があるため、フォーマットする前にガードしてください。[コストと使用量の追跡](/docs/ja/agent-sdk/cost-tracking)を参照して、`usage` フィールドの解釈の詳細を確認してください。

<Note>
  クエリがエラー結果で終了する場合：

  * 単一ショットの `query()` 呼び出しは最終結果メッセージを生成し、その後 `Reached maximum number of turns` などの失敗テキストを含むエラーを発生させます。発生は意図的です。コードがそれを超えて続行する必要がある場合は、ループを try ブロックでラップしてください。基盤となる Claude Code プロセスも 0 以外のコードで終了します。
  * ストリーミング入力セッションは生きたままで、メッセージを送信し続けることができます。
</Note>

結果には、モデルが最終ターンで生成を停止した理由を示す `stop_reason` フィールド（TypeScript では `string | null`、Python では `str | None`）も含まれます。一般的な値は `end_turn`（モデルが通常終了）、`max_tokens`（出力トークン制限に達した）、および `refusal`（モデルがリクエストを拒否）です。エラー結果サブタイプでは、`stop_reason` はループが終了する前の最後のアシスタント応答からの値を持ちます。拒否を検出するには、`stop_reason === "refusal"`（TypeScript）または `stop_reason == "refusal"`（Python）をチェックしてください。完全なタイプについては、[`SDKResultMessage`](/docs/ja/agent-sdk/typescript#sdkresultmessage)（TypeScript）または [`ResultMessage`](/docs/ja/agent-sdk/python#resultmessage)（Python）を参照してください。

<h2 id="hooks">
  Hooks
</h2>

[Hooks](/docs/ja/agent-sdk/hooks)は、ループの特定のポイントで発火するコールバックです。ツールが実行される前、戻った後、エージェントが終了したときなど。一般的に使用されるフックは次のとおりです。

| フック                              | 発火時期           | 一般的な用途                |
| :------------------------------- | :------------- | :-------------------- |
| `PreToolUse`                     | ツール実行前         | 入力を検証、危険なコマンドをブロック    |
| `PostToolUse`                    | ツール戻り後         | 出力を監査、副作用をトリガー        |
| `UserPromptSubmit`               | プロンプト送信時       | プロンプトに追加コンテキストを注入     |
| `Stop`                           | エージェント終了時      | 結果を検証、セッション状態を保存      |
| `SubagentStart` / `SubagentStop` | サブエージェント生成/完了時 | 並列タスク結果を追跡して集約        |
| `PreCompact`                     | コンテキスト圧縮前      | 要約前に完全なトランスクリプトをアーカイブ |

フックはエージェントのコンテキストウィンドウ内ではなく、アプリケーションプロセスで実行されるため、コンテキストを消費しません。フックはループをショートサーキットすることもできます。ツール呼び出しを拒否する `PreToolUse` フックはそれが実行されるのを防ぎ、Claude は代わりに拒否メッセージを受け取ります。

両方の SDK はすべての上記のイベントをサポートしています。TypeScript SDK には、Python がまだサポートしていない追加のイベントが含まれています。完全なイベントリスト、SDK ごとの利用可能性、および完全なコールバック API については、[フックで実行を制御する](/docs/ja/agent-sdk/hooks)を参照してください。

<h2 id="put-it-all-together">
  すべてをまとめる
</h2>

この例は、このページの主要な概念を、失敗するテストを修正する単一のエージェントに組み合わせています。許可されたツール（自動承認されるため、エージェントが自律的に実行される）、プロジェクト設定、およびターンと推論努力の安全制限でエージェントを構成します。ループが実行されると、潜在的な再開のためにセッション ID をキャプチャし、最終結果を処理し、総コストを出力します。

単一の `query()` 呼び出しはエラー結果を生成した後に発生するため、ループは try ブロックでラップされており、制限に達したときにスクリプトがクリーンに終了します。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


  async def run_agent():
      session_id = None

      try:
          async for message in query(
              prompt="Find and fix the bug causing test failures in the auth module",
              options=ClaudeAgentOptions(
                  allowed_tools=[
                      "Read",
                      "Edit",
                      "Bash",
                      "Glob",
                      "Grep",
                  ],  # Listing tools here auto-approves them (no prompting)
                  setting_sources=[
                      "project"
                  ],  # Load CLAUDE.md, skills, hooks from current directory
                  max_turns=30,  # Prevent runaway sessions
                  effort="high",  # Thorough reasoning for complex debugging
              ),
          ):
              # Handle the final result
              if isinstance(message, ResultMessage):
                  session_id = message.session_id  # Save for potential resumption

                  if message.subtype == "success":
                      print(f"Done: {message.result}")
                  elif message.subtype == "error_max_turns":
                      # Agent ran out of turns. Resume with a higher limit.
                      print(f"Hit turn limit. Resume session {session_id} to continue.")
                  elif message.subtype == "error_max_budget_usd":
                      print("Hit budget limit.")
                  else:
                      print(f"Stopped: {message.subtype}")
                  if message.total_cost_usd is not None:
                      print(f"Cost: ${message.total_cost_usd:.4f}")
      except Exception as error:
          # A single-shot query() raises after yielding an error result. If the
          # failure was an error result, the error subtype branches above have
          # already run; connection or process failures yield no result message.
          print(f"Session ended with an error: {error}")


  asyncio.run(run_agent())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  let sessionId: string | undefined;

  try {
    for await (const message of query({
      prompt: "Find and fix the bug causing test failures in the auth module",
      options: {
        allowedTools: ["Read", "Edit", "Bash", "Glob", "Grep"], // Listing tools here auto-approves them (no prompting)
        settingSources: ["project"], // Load CLAUDE.md, skills, hooks from current directory
        maxTurns: 30, // Prevent runaway sessions
        effort: "high" // Thorough reasoning for complex debugging
      }
    })) {
      // Save the session ID to resume later if needed
      if (message.type === "system" && message.subtype === "init") {
        sessionId = message.session_id;
      }

      // Handle the final result
      if (message.type === "result") {
        if (message.subtype === "success") {
          console.log(`Done: ${message.result}`);
        } else if (message.subtype === "error_max_turns") {
          // Agent ran out of turns. Resume with a higher limit.
          console.log(`Hit turn limit. Resume session ${sessionId} to continue.`);
        } else if (message.subtype === "error_max_budget_usd") {
          console.log("Hit budget limit.");
        } else {
          console.log(`Stopped: ${message.subtype}`);
        }
        console.log(`Cost: $${message.total_cost_usd.toFixed(4)}`);
      }
    }
  } catch (error) {
    // A single-shot query() throws after yielding an error result. If the
    // failure was an error result, the error subtype branches above have
    // already run; connection or process failures yield no result message.
    console.log(`Session ended with an error: ${error}`);
  }
  ```
</CodeGroup>

<h2 id="next-steps">
  次のステップ
</h2>

ループを理解したので、構築しているものに応じて、ここに行くべき場所があります。

* **まだエージェントを実行していませんか？** [クイックスタート](/docs/ja/agent-sdk/quickstart)から始めて、SDK をインストールし、完全な例をエンドツーエンドで実行してください。
* **プロジェクトにフックする準備ができていますか？** [CLAUDE.md、スキル、ファイルシステムフックをロード](/docs/ja/agent-sdk/claude-code-features)して、エージェントがプロジェクト規約に自動的に従うようにします。
* **インタラクティブ UI を構築していますか？** [ストリーミング](/docs/ja/agent-sdk/streaming-output)を有効にして、ループが実行されるときにライブテキストとツール呼び出しを表示します。
* **エージェントが何をできるかについてより厳密な制御が必要ですか？** [権限](/docs/ja/agent-sdk/permissions)でツールアクセスをロックダウンし、[フック](/docs/ja/agent-sdk/hooks)を使用して、実行前にツール呼び出しを監査、ブロック、または変換します。
* **長時間または高コストのタスクを実行していますか？** 隔離された作業を[サブエージェント](/docs/ja/agent-sdk/subagents)にオフロードして、メインコンテキストをリーンに保ちます。

agentic ループのより広い概念的な図（SDK 固有ではない）については、[Claude Code の仕組み](/docs/ja/how-claude-code-works)を参照してください。Claude Code でループを設計するための実践的なガイド（ターンベースループからゴールベースループおよびプロアクティブループまで）については、ブログの[ループエンジニアリング：ループの開始](/docs/ja/blog/getting-started-with-loops)を参照してください。
