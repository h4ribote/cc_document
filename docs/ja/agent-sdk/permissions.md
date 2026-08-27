> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# パーミッションの設定

> パーミッションモード、フック、宣言的な許可/拒否ルールを使用して、エージェントがツールをどのように使用するかを制御します。

Claude Agent SDK は、Claude がツールをどのように使用するかを管理するためのパーミッション制御を提供します。パーミッションモードとルールを使用して、自動的に許可されるものを定義し、[`canUseTool` コールバック](/docs/ja/agent-sdk/user-input)を使用して、実行時にそれ以外のすべてを処理します。

<Note>
  このページはパーミッションモードとルールについて説明しています。ユーザーが実行時にツールリクエストを承認または拒否する対話的な承認フローを構築するには、[承認とユーザー入力の処理](/docs/ja/agent-sdk/user-input)を参照してください。
</Note>

<h2 id="how-permissions-are-evaluated">
  パーミッションの評価方法
</h2>

Claude がツールをリクエストすると、SDK は次の順序でパーミッションをチェックします。

<Steps>
  <Step title="フック">
    最初に[フック](/docs/ja/agent-sdk/hooks)を実行します。フックはコールを直接拒否するか、それを渡すことができます。`allow` を返すフックは、以下の拒否および質問ルールをスキップしません。これらはフックの結果に関係なく評価されます。
  </Step>

  <Step title="拒否ルール">
    `deny` ルール（`disallowed_tools` および[settings.json](/docs/ja/settings#permission-settings)から）をチェックします。拒否ルールが一致する場合、`bypassPermissions` モードでもツールはブロックされます。`Bash` のような裸名の拒否ルールはこの評価が開始される前に Claude のコンテキストからツールを削除するため、このステップでチェックされるのは `Bash(rm *)` のようなスコープ付きルールのみです。
  </Step>

  <Step title="質問ルール">
    [settings.json](/docs/ja/settings#permission-settings)から `ask` ルールをチェックします。質問ルールが一致する場合、`bypassPermissions` モードでも、コールは確認のために[`canUseTool` コールバック](/docs/ja/agent-sdk/user-input)にフォールスルーします。

    ユーザーインタラクションが必要なツールは同じように動作します。`AskUserQuestion` および MCP ツール（サーバーが[`_meta["anthropic/requiresUserInteraction"]`](/docs/ja/mcp#require-approval-for-a-specific-tool)を設定）は、許可ルールが一致する場合でも常にコールバックにフォールスルーします。`dontAsk` モードでは、このモードはプロンプトを表示しないため、両方のケースが代わりに拒否されます。MCP アノテーションには Claude Code v2.1.199 以降が必要です。

    [claude.ai コネクタ](/docs/ja/mcp#organization-controls-on-connector-tools)ツール（組織が `ask` に設定したもの）もこのステップでフローを離れます。すべてのコールはコールバックにフォールスルーします。`bypassPermissions` モードでも、許可ルールが一致する場合でもです。コールバックは理由 `Your organization requires approval for this tool` を受け取ります。`dontAsk` モードではコールが拒否される代わりに、このモードはプロンプトを表示しないためです。
  </Step>

  <Step title="権限モード">
    アクティブな[権限モード](#permission-modes)を適用します。`bypassPermissions` はこのステップに到達したすべてを承認します。`acceptEdits` はファイル操作を承認します。`plan` はファイル編集およびシェル書き込みツールを許可ルールに関係なく [`canUseTool` コールバック](/docs/ja/agent-sdk/user-input)にルーティングするため、計画中は書き込み操作を自動承認することはできません。その他のモードはフォールスルーします。
  </Step>

  <Step title="許可ルール">
    `allow` ルール（`allowed_tools` および settings.json から）をチェックします。ルールが一致する場合、ツールは承認されます。
  </Step>

  <Step title="canUseTool コールバック">
    上記のいずれでも解決されない場合、決定のために[`canUseTool` コールバック](/docs/ja/agent-sdk/user-input)を呼び出します。`dontAsk` モードでは、このステップはスキップされ、ツールは拒否されます。
  </Step>
</Steps>

<img src="https://mintcdn.com/claude-code/jYgs7qigNjO1Badj/images/agent-sdk/permissions-flow.svg?fit=max&auto=format&n=jYgs7qigNjO1Badj&q=85&s=c771ad9085b1277d3708027a49c744bc" alt="6 ステップのパーミッション評価フロー図。ツールリクエストはフック、拒否ルール、質問ルール、パーミッションモード、許可ルール、canUseTool を通過します。フック、拒否ルール、canUseTool はブロックにルーティングでき、パーミッションモードバイパス、許可ルール、canUseTool は実行にルーティングできます。質問ルールは canUseTool にルーティングします。" width="1180" height="260" data-path="images/agent-sdk/permissions-flow.svg" />

v2.1.198 以降、このパーミッション評価順序が到達できない `canUseTool` コールバックを渡す場合、TypeScript SDK はクエリが構築されるときに Node.js プロセス警告を 1 回発行します。警告のコードは `CLAUDE_SDK_CAN_USE_TOOL_SHADOWED` です。2 つの設定がこれをトリガーします。

* `permissionMode: 'bypassPermissions'`。これはパーミッションモードステップに到達するすべてのコールを自動承認します。
* `"Read"` などの各裸の `allowedTools` エントリ。これはコールバックが相談される前にそのツール全体を自動承認します。

`Bash(ls *)` などの指定子を持つエントリと `acceptEdits` モードはこれをトリガーしません。また、設定ファイルから来る許可ルールはチェックに表示されません。

`process.on('warning', ...)` でリッスンしてコードをマッチングしてログに記録するか、それを抑制します。モードとルールに関係なくすべてのツールコールをゲートするには、代わりに[`PreToolUse` フック](/docs/ja/agent-sdk/hooks)を使用します。

このページは**許可および拒否ルール**と**パーミッションモード**に焦点を当てています。その他のステップについては、以下を参照してください。

* **フック：** カスタムコードを実行して、ツールリクエストを許可、拒否、または変更します。[フックで実行を制御](/docs/ja/agent-sdk/hooks)を参照してください。
* **canUseTool コールバック：** 実行時にユーザーに承認を促します。[承認とユーザー入力の処理](/docs/ja/agent-sdk/user-input)を参照してください。

<h2 id="allow-and-deny-rules">
  許可および拒否ルール
</h2>

`allowed_tools` および `disallowed_tools`（TypeScript：`allowedTools` / `disallowedTools`）は、上記の評価フロー内の許可および拒否ルールリストにエントリを追加します。許可ルールは承認のみに影響します。`allowed_tools` にリストされていないツールは引き続き Claude に利用可能であり、パーミッションモードにフォールスルーします。拒否ルールは、ツール全体に名前を付けるか、ツール内のパターンをスコープするかによって異なる動作をします。

| オプション                             | 効果                                                                                                                       |
| :-------------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| `allowed_tools=["Read", "Grep"]`  | `Read` および `Grep` は自動承認されます。ここにリストされていないツールは引き続き存在し、パーミッションモードおよび `canUseTool` にフォールスルーします。                              |
| `disallowed_tools=["Bash"]`       | `Bash` ツール定義はリクエストから削除されます。Claude はツールを認識せず、それを試みることはできません。                                                              |
| `disallowed_tools=["Bash(rm *)"]` | `Bash` は利用可能なままです。`rm *` に一致する呼び出しは、`bypassPermissions` を含むすべてのパーミッションモードで拒否されます。その他の `Bash` 呼び出しはパーミッションモードにフォールスルーします。 |
| `disallowed_tools=["*"]`          | すべてのツール定義はリクエストから削除されます。拒否ルールではツール名グロブがサポートされています。`"*"` はすべてのツールに一致し、`"mcp__*"` はすべてのサーバー全体のすべての MCP ツールに一致します。          |

許可ルールは、リテラル `mcp__<server>__` プレフィックスの後にのみツール名グロブを受け入れます。サーバーセグメントはグロブフリーである必要があり、設定したサーバーに名前を付けます。`mcp__puppeteer__*` は `puppeteer` サーバーからのすべてのツールに一致し、`mcp__github__get_*` はその `get_` ツールに一致します。`allowed_tools=["*"]` または `allowed_tools=["mcp__*"]` のようなアンカーされていないエントリは、スタートアップ警告で無視され、何も自動承認しません。

`Read` および `Edit` のスコープ付きルールはパスパターンを取ります。`Edit(path)` ルールは、`Write` および `NotebookEdit` を含む、ファイルを書き込むすべての組み込みツールを管理します。`Write(path)` ルールはファイル権限チェックと一致することはありません。

絶対ファイルシステムパスには `//path` を使用します。`Edit(//secrets/**)` の拒否ルールは、ディスク上の `/secrets` の下のどこでも書き込みをブロックします。単一の先頭スラッシュを使用する場合、`Edit(/secrets/**)` はルールのソースでアンカーされます。`allowed_tools` または `disallowed_tools` を通じて渡されるルールの場合、これはセッションの作業ディレクトリを意味するため、ルールはディスク上の `/secrets` をブロックしません。4 つのアンカー形式と設定ファイルからのルール解決方法については、[Read および Edit ルール](/docs/ja/permissions#read-and-edit)を参照してください。

<Warning>
  **自動承認されたツールは `canUseTool` に到達しません。** 任意の前のステップで承認されたツール呼び出し（`acceptEdits` または `bypassPermissions` による、または許可ルールによる）は、`canUseTool` コールバックをスキップするため、そこに配置した権限チェックはそのツールに対して静かにバイパスされます。`AskUserQuestion`、MCP ツール（[`_meta["anthropic/requiresUserInteraction"]`](/docs/ja/mcp#require-approval-for-a-specific-tool) でマークされたもの）、およびコネクタツール（[組織が `ask` に設定したもの](/docs/ja/mcp#organization-controls-on-connector-tools)）は、許可ルールが一致する場合でもコールバックに到達します。

  カバレッジはエントリの形式に依存します。`Read` または `mcp__github__get_issue` のような単純な名前は、そのツールへのすべての呼び出しを自動承認しますが、`Bash(ls *)` のようなスコープ付きルールは一致する呼び出しのみを自動承認し、その他の `Bash` 呼び出しはコールバックにフォールスルーします。すべてのツール呼び出しで実行する必要があるチェックについては、[`PreToolUse` フック](/docs/ja/agent-sdk/hooks)を使用してください。フックはすべての他のステップの前に実行され、フック拒否は `bypassPermissions` モードでも適用されます。
</Warning>

ロックダウンされたエージェントの場合、`allowedTools` を `permissionMode: "dontAsk"` と組み合わせます。リストされたツールは承認されます。上記の警告の常にプロンプトが表示されるツールを除き、その他のものはプロンプトの代わりに直接拒否されます。

```typescript theme={null}
const options = {
  allowedTools: ["Read", "Glob", "Grep"],
  permissionMode: "dontAsk"
};
```

<Warning>
  **`allowed_tools` は `bypassPermissions` を制限しません。** `allowed_tools` はリストしたツールのみを事前承認します。リストされていないツールは許可ルールと一致せず、パーミッションモードにフォールスルーします。ここで `bypassPermissions` はそれらを承認します。`allowed_tools=["Read"]` を `permission_mode="bypassPermissions"` と一緒に設定すると、`Bash`、`Write`、`Edit` を含むすべてのツールが承認されます。`bypassPermissions` が必要だが特定のツールをブロックしたい場合は、`disallowed_tools` を使用してください。
</Warning>

`.claude/settings.json` で許可、拒否、および質問ルールを宣言的に設定することもできます。これらのルールは、`project` 設定ソースが有効な場合に読み込まれます。デフォルトの `query()` オプションではこれが有効です。`setting_sources`（TypeScript：`settingSources`）を明示的に設定する場合は、それらを適用するために `"project"` を含めてください。ルール構文については、[パーミッション設定](/docs/ja/settings#permission-settings)を参照してください。

<h2 id="permission-modes">
  パーミッションモード
</h2>

パーミッションモードは、Claude がツールをどのように使用するかについてのグローバル制御を提供します。`query()` を呼び出すときにパーミッションモードを設定するか、ストリーミングセッション中に動的に変更できます。

<h3 id="available-modes">
  利用可能なモード
</h3>

SDK は以下のパーミッションモードをサポートしています。

| モード                 | 説明               | ツール動作                                                                                                                                                                                                  |
| :------------------ | :--------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `default`           | 標準パーミッション動作      | 自動承認なし。一致しないツールは `canUseTool` コールバックをトリガーします                                                                                                                                                           |
| `dontAsk`           | プロンプトの代わりに拒否     | `allowed_tools` またはルールで事前承認されていないものはすべて拒否されます。コネクタツール[組織が `ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools)したもの、およびユーザーインタラクションが必要なツールは、事前承認していても拒否されます。`canUseTool` は呼び出されません              |
| `acceptEdits`       | ファイル編集を自動受け入れ    | ファイル編集および[ファイルシステム操作](#accept-edits-mode-acceptedits)（`mkdir`、`rm`、`mv` など）は自動的に承認されます                                                                                                                 |
| `bypassPermissions` | パーミッションチェックをバイパス | ツールは明示的な [`ask` ルール](#how-permissions-are-evaluated)が一致する場合、コネクタツール[組織が `ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools)した場合、およびユーザーインタラクションが必要なツール以外は、パーミッションプロンプトなしで実行されます（注意して使用してください） |
| `plan`              | 計画モード            | Claude はソースファイルを編集せずにコードベースを探索および計画します。ファイル編集は自動承認されず、`canUseTool` コールバックを通じてプロンプトが表示されます                                                                                                              |
| `auto`              | モデル分類承認          | モデル分類器が各ツール呼び出しを承認または拒否します。利用可能性については[自動モード](/docs/ja/permission-modes#eliminate-prompts-with-auto-mode)を参照してください                                                                                           |

<Warning>
  **サブエージェント継承：** 親が `bypassPermissions`、`acceptEdits`、または `auto` を使用する場合、すべてのサブエージェントはそのモードを継承し、サブエージェントごとにオーバーライドすることはできません。サブエージェントはシステムプロンプトが異なり、メインエージェントよりも制約が少ない動作をする可能性があるため、`bypassPermissions` を継承すると、完全な自律的なシステムアクセスが付与されます。明示的な [`ask` ルール](#how-permissions-are-evaluated)、コネクタツール[組織が `ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools)したもの、およびユーザーインタラクションが必要なツールは引き続きプロンプトを強制します。
</Warning>

<h3 id="set-permission-mode">
  パーミッションモードの設定
</h3>

クエリを開始するときにパーミッションモードを一度設定するか、セッションがアクティブな間に動的に変更できます。

<Tabs>
  <Tab title="クエリ時">
    クエリを作成するときに `permission_mode`（Python）または `permissionMode`（TypeScript）を渡します。このモードは、動的に変更されない限り、セッション全体に適用されます。

    <CodeGroup>
      ```python Python theme={null}
      import asyncio
      from claude_agent_sdk import query, ClaudeAgentOptions


      async def main():
          async for message in query(
              prompt="Help me refactor this code",
              options=ClaudeAgentOptions(
                  permission_mode="default",  # ここでモードを設定
              ),
          ):
              if hasattr(message, "result"):
                  print(message.result)


      asyncio.run(main())
      ```

      ```typescript TypeScript theme={null}
      import { query } from "@anthropic-ai/claude-agent-sdk";

      async function main() {
        for await (const message of query({
          prompt: "Help me refactor this code",
          options: {
            permissionMode: "default" // ここでモードを設定
          }
        })) {
          if ("result" in message) {
            console.log(message.result);
          }
        }
      }

      main();
      ```
    </CodeGroup>
  </Tab>

  <Tab title="ストリーミング中">
    `set_permission_mode()`（Python）または `setPermissionMode()`（TypeScript）を呼び出して、セッション中盤でモードを変更します。新しいモードは、その後のすべてのツールリクエストに対して直ちに有効になります。これにより、制限的に開始し、信頼が構築されるにつれてパーミッションを緩和できます。たとえば、Claude の初期アプローチをレビューした後に `acceptEdits` に切り替えます。

    <CodeGroup>
      ```python Python theme={null}
      import asyncio
      from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


      async def main():
          async with ClaudeSDKClient(
              options=ClaudeAgentOptions(
                  permission_mode="default",  # デフォルトモードで開始
              )
          ) as client:
              await client.query("Help me refactor this code")

              # セッション中盤でモードを動的に変更
              await client.set_permission_mode("acceptEdits")

              # 新しいパーミッションモードでメッセージを処理
              async for message in client.receive_response():
                  if hasattr(message, "result"):
                      print(message.result)


      asyncio.run(main())
      ```

      ```typescript TypeScript theme={null}
      import { query } from "@anthropic-ai/claude-agent-sdk";

      async function main() {
        const q = query({
          prompt: "Help me refactor this code",
          options: {
            permissionMode: "default" // デフォルトモードで開始
          }
        });

        // セッション中盤でモードを動的に変更
        await q.setPermissionMode("acceptEdits");

        // 新しいパーミッションモードでメッセージを処理
        for await (const message of q) {
          if ("result" in message) {
            console.log(message.result);
          }
        }
      }

      main();
      ```
    </CodeGroup>
  </Tab>
</Tabs>

<h3 id="mode-details">
  モードの詳細
</h3>

<h4 id="accept-edits-mode-acceptedits">
  ファイル編集モード（`acceptEdits`）
</h4>

ファイル操作を自動承認し、Claude がプロンプトなしでコードを編集できるようにします。その他のツール（ファイルシステム操作ではない Bash コマンドなど）は引き続き通常のパーミッションが必要です。

**自動承認される操作：**

* ファイル編集（Edit、Write ツール）
* ファイルシステムコマンド：`mkdir`、`touch`、`rm`、`rmdir`、`mv`、`cp`、`sed`

どちらも、作業ディレクトリまたは `additionalDirectories` 内のパスにのみ適用されます。そのスコープ外のパスおよび保護されたパスへの書き込みはプロンプトが表示されます。

**使用時期：** Claude の編集を信頼し、プロトタイピング中など、より高速な反復を望む場合、または分離されたディレクトリで作業する場合。

<h4 id="don’t-ask-mode-dontask">
  質問しないモード（`dontAsk`）
</h4>

パーミッションプロンプトを拒否に変換します。`allowed_tools`、`settings.json` 許可ルール、またはフックで事前承認されたツールは通常どおり実行されます。コネクタツール[組織が `ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools)したもの、およびユーザーインタラクションが必要なツールは、許可ルールが一致する場合でも拒否されます。その他のすべては `canUseTool` を呼び出さずに拒否されます。

**使用時期：** ヘッドレスエージェント用に固定された明示的なツール表面が必要で、`canUseTool` が存在しないことへの暗黙的な依存よりもハード拒否を優先する場合。

<h4 id="bypass-permissions-mode-bypasspermissions">
  パーミッションバイパスモード（`bypassPermissions`）
</h4>

プロンプトなしですべてのツール使用を自動承認します。フックは引き続き実行され、必要に応じて操作をブロックできます。

<Warning>
  極度の注意を持って使用してください。Claude はこのモードでフルシステムアクセスを持ちます。すべての可能な操作を信頼できる制御された環境でのみ使用してください。

  `allowed_tools` はこのモードを制限しません。リストしたツールだけでなく、すべてのツールが承認されます。拒否ルール（`disallowed_tools`）、明示的な `ask` ルール、およびフックはモードチェック前に評価され、ツールをブロックできます。コネクタツール[組織が `ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools)したもの、およびユーザーインタラクションが必要なツールは引き続き `canUseTool` コールバックにフォールスルーします。
</Warning>

<h4 id="plan-mode-plan">
  計画モード（`plan`）
</h4>

Claude はコードベースを探索および計画を作成し、ソースファイルを編集しません。読み取り専用ツールはデフォルトモードと同じように実行されます。ファイル編集は計画モードで自動承認されることはなく、許可ルールが一致する場合でも、代わりに `canUseTool` コールバックを通じてプロンプトが表示されます。Claude は計画を最終化する前に要件を明確にするために `AskUserQuestion` を使用する場合があります。これらのプロンプトの処理については、[承認とユーザー入力の処理](/docs/ja/agent-sdk/user-input#handle-clarifying-questions)を参照してください。

**使用時期：** Claude に変更を提案させたいが実行させたくない場合、たとえばコードレビュー中または変更を実行する前に承認が必要な場合。

<h2 id="related-resources">
  関連リソース
</h2>

パーミッション評価フロー内の他のステップについては、以下を参照してください。

* [承認とユーザー入力の処理](/docs/ja/agent-sdk/user-input)：対話的な承認プロンプトと明確化の質問
* [フックガイド](/docs/ja/agent-sdk/hooks)：エージェントライフサイクルの主要なポイントでカスタムコードを実行
* [パーミッションルール](/docs/ja/settings#permission-settings)：`settings.json` の宣言的な許可/拒否ルール
