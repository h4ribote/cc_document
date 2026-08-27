> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# セッションの操作

> セッションがエージェント会話履歴をどのように保持するか、および以前の実行に戻るために continue、resume、fork をいつ使用するかについて説明します。

セッションは、エージェントが動作している間に SDK が蓄積する会話履歴です。プロンプト、エージェントが行ったすべてのツール呼び出し、すべてのツール結果、およびすべてのレスポンスが含まれます。SDK はそれを自動的にディスクに書き込むため、後で戻ることができます。

セッションに戻るということは、エージェントが以前のコンテキストを完全に持っているということです。既に読んだファイル、既に実行した分析、既に行った決定があります。フォローアップの質問をしたり、中断から回復したり、別のアプローチを試すために分岐したりできます。

<Note>
  セッションは**会話**を保持し、ファイルシステムは保持しません。エージェントが行ったファイル変更をスナップショットして戻すには、[ファイルチェックポイント](/docs/ja/agent-sdk/file-checkpointing)を使用します。
</Note>

このガイドでは、アプリケーションに適切なアプローチを選択する方法、セッションを自動的に追跡する SDK インターフェース、セッション ID をキャプチャして `resume` と `fork` を手動で使用する方法、およびホスト間でセッションを再開する際に知っておくべきことについて説明します。

<h2 id="choose-an-approach">
  アプローチを選択する
</h2>

必要なセッション処理の量は、アプリケーションの形状によって異なります。セッション管理は、コンテキストを共有する必要がある複数のプロンプトを送信する場合に関係します。単一の `query()` 呼び出し内では、エージェントは既に必要なだけのターンを実行し、権限プロンプトと `AskUserQuestion` は[ループ内で処理](/docs/ja/agent-sdk/user-input)されます（呼び出しを終了しません）。

| 構築しているもの                                 | 使用するもの                                                                                                                    |
| :--------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| ワンショットタスク：単一プロンプト、フォローアップなし              | 追加は不要です。1 つの `query()` 呼び出しで処理されます。                                                                                       |
| 1 つのプロセス内のマルチターンチャット                     | [`ClaudeSDKClient`（Python）または `continue: true`（TypeScript）](#automatic-session-management)。SDK はセッションを自動的に追跡し、ID 処理は不要です。 |
| プロセス再起動後に中断したところから再開                     | `continue_conversation=True`（Python）/ `continue: true`（TypeScript）。ディレクトリ内の最新セッションを再開し、ID は不要です。                          |
| 特定の過去のセッション（最新ではない）を再開                   | セッション ID をキャプチャして `resume` に渡します。                                                                                         |
| 元のセッションを失わずに別のアプローチを試す                   | セッションをフォークします。                                                                                                            |
| ステートレスタスク、ディスクに何も書き込みたくない（TypeScript のみ） | [`persistSession: false`](/docs/ja/agent-sdk/typescript#options)を設定します。セッションは呼び出しの期間中メモリにのみ存在します。Python は常にディスクに保持します。         |

<h3 id="continue-resume-and-fork">
  Continue、resume、および fork
</h3>

Continue、resume、および fork は `query()` に設定するオプションフィールドです（Python では [`ClaudeAgentOptions`](/docs/ja/agent-sdk/python#claudeagentoptions)、TypeScript では [`Options`](/docs/ja/agent-sdk/typescript#options)）。

**Continue** と **resume** はどちらも既存のセッションを取得して追加します。違いはそのセッションを見つける方法です：

* **Continue** は現在のディレクトリ内の最新セッションを見つけます。何も追跡する必要はありません。アプリケーションが一度に 1 つの会話を実行する場合に適しています。
* **Resume** は特定のセッション ID を取得します。ID を追跡します。複数のセッション（たとえば、マルチユーザーアプリケーションのユーザーごとに 1 つ）がある場合、または最新ではないセッションに戻りたい場合に必要です。

**Fork** は異なります。元の履歴のコピーで開始する新しいセッションを作成します。元のセッションは変更されません。別の方向を試しながら戻るオプションを保持するために fork を使用します。

<h2 id="automatic-session-management">
  自動セッション管理
</h2>

両方の SDK は、呼び出し間でセッション状態を追跡するインターフェースを提供するため、ID を手動で渡す必要はありません。単一プロセス内のマルチターン会話にこれらを使用します。

<h3 id="python-claudesdkclient">
  Python：`ClaudeSDKClient`
</h3>

[`ClaudeSDKClient`](/docs/ja/agent-sdk/python#claudesdkclient) はセッション ID を内部的に処理します。`client.query()` への各呼び出しは自動的に同じセッションを続行します。[`client.receive_response()`](/docs/ja/agent-sdk/python#claudesdkclient) を呼び出して、現在のクエリのメッセージを反復処理します。クライアントを非同期コンテキストマネージャーとして使用すると、接続のセットアップとティアダウンが自動的に処理されます。または、`connect()` と `disconnect()` を手動で呼び出すこともできます。

この例は、同じ `client` に対して 2 つのクエリを実行します。最初はエージェントにモジュールを分析するよう求め、2 番目はそのモジュールをリファクタリングするよう求めます。両方の呼び出しが同じクライアントインスタンスを通過するため、2 番目のクエリは明示的な `resume` またはセッション ID なしで最初のクエリから完全なコンテキストを持ちます：

```python Python theme={null}
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)


def print_response(message):
    """Print only the human-readable parts of a message."""
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
    elif isinstance(message, ResultMessage):
        cost = (
            f"${message.total_cost_usd:.4f}"
            if message.total_cost_usd is not None
            else "N/A"
        )
        print(f"[done: {message.subtype}, cost: {cost}]")


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Glob", "Grep"],
    )

    async with ClaudeSDKClient(options=options) as client:
        # First query: client captures the session ID internally
        await client.query("Analyze the auth module")
        async for message in client.receive_response():
            print_response(message)

        # Second query: automatically continues the same session
        await client.query("Now refactor it to use JWT")
        async for message in client.receive_response():
            print_response(message)


asyncio.run(main())
```

Python SDK リファレンスの [ClaudeSDKClient とスタンドアロン `query()` 関数のどちらを使用するかについて](/docs/ja/agent-sdk/python#choosing-between-query-and-claudesdkclient)の詳細を参照してください。

<h3 id="typescript-continue-true">
  TypeScript：`continue: true`
</h3>

TypeScript SDK には、Python の `ClaudeSDKClient` のようなセッション保持クライアントオブジェクトがありません。代わりに、後続の各 `query()` 呼び出しで `continue: true` を渡すと、SDK は現在のディレクトリ内の最新セッションを見つけて再開します。ID 追跡は不要です。

この例は 2 つの別々の `query()` 呼び出しを行います。最初は新しいセッションを作成し、2 番目は `continue: true` を設定します。これは SDK にディスク上の最新セッションを見つけて再開するよう指示します。エージェントは最初の呼び出しから完全なコンテキストを持ちます：

```typescript TypeScript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";

// First query: creates a new session
for await (const message of query({
  prompt: "Analyze the auth module",
  options: { allowedTools: ["Read", "Glob", "Grep"] }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}

// Second query: continue: true resumes the most recent session
for await (const message of query({
  prompt: "Now refactor it to use JWT",
  options: {
    continue: true,
    allowedTools: ["Read", "Edit", "Write", "Glob", "Grep"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

<Note>
  実験的な [V2 セッション API](/docs/ja/agent-sdk/typescript-v2-preview)（`createSession()` と `send` / `stream` パターンを提供していた）は TypeScript Agent SDK 0.3.142 で削除されました。このページで説明されている `query()` 関数とセッションオプションを使用してください。
</Note>

<h2 id="use-session-options-with-query">
  `query()` でセッションオプションを使用する
</h2>

<h3 id="capture-the-session-id">
  セッション ID をキャプチャする
</h3>

Resume と fork にはセッション ID が必要です。結果メッセージ（Python では [`ResultMessage`](/docs/ja/agent-sdk/python#resultmessage)、TypeScript では [`SDKResultMessage`](/docs/ja/agent-sdk/typescript#sdkresultmessage)）の `session_id` フィールドから読み取ります。これは成功またはエラーに関係なく、すべての結果に存在します。TypeScript では、ID は初期 `SystemMessage` の直接フィールドとしても利用可能です。Python では、`SystemMessage.data` 内にネストされています。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


  async def main():
      session_id = None

      async for message in query(
          prompt="Analyze the auth module and suggest improvements",
          options=ClaudeAgentOptions(
              allowed_tools=["Read", "Glob", "Grep"],
          ),
      ):
          if isinstance(message, ResultMessage):
              session_id = message.session_id
              if message.subtype == "success":
                  print(message.result)

      print(f"Session ID: {session_id}")
      return session_id


  session_id = asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  let sessionId: string | undefined;

  for await (const message of query({
    prompt: "Analyze the auth module and suggest improvements",
    options: { allowedTools: ["Read", "Glob", "Grep"] }
  })) {
    if (message.type === "result") {
      sessionId = message.session_id;
      if (message.subtype === "success") {
        console.log(message.result);
      }
    }
  }

  console.log(`Session ID: ${sessionId}`);
  ```
</CodeGroup>

<h3 id="resume-by-id">
  ID で再開する
</h3>

セッション ID を `resume` に渡して、その特定のセッションに戻ります。エージェントはセッションが終了した場所から完全なコンテキストで再開します。再開の一般的な理由：

* **完了したタスクをフォローアップします。** エージェントは既に何かを分析しました。今、ファイルを再度読み込まずにその分析に基づいて行動してほしいです。
* **制限から回復します。** 最初の実行は `error_max_turns` または `error_max_budget_usd` で終了しました（[結果を処理する](/docs/ja/agent-sdk/agent-loop#handle-the-result)を参照）。より高い制限で再開します。
* **プロセスを再起動します。** シャットダウン前に ID をキャプチャし、会話を復元したいです。

この例は、[セッション ID をキャプチャする](#capture-the-session-id)からのセッションをフォローアッププロンプトで再開します。再開しているため、エージェントは既に以前の分析をコンテキストに持っています：

<CodeGroup>
  ```python Python theme={null}
  # Earlier session analyzed the code; now build on that analysis
  async for message in query(
      prompt="Now implement the refactoring you suggested",
      options=ClaudeAgentOptions(
          resume=session_id,
          allowed_tools=["Read", "Edit", "Write", "Glob", "Grep"],
      ),
  ):
      if isinstance(message, ResultMessage) and message.subtype == "success":
          print(message.result)
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const sessionId = "..."; // The ID you captured in the previous example

  // Earlier session analyzed the code; now build on that analysis
  for await (const message of query({
    prompt: "Now implement the refactoring you suggested",
    options: {
      resume: sessionId,
      allowedTools: ["Read", "Edit", "Write", "Glob", "Grep"]
    }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```
</CodeGroup>

以前の分析に基づいて構築された応答が表示されるはずです。これにより、エージェントが以前のコンテキストを保持したままセッションを再開したことが確認されます。

<Tip>
  `resume` 呼び出しが予期された履歴ではなく新しいセッションを返す場合、最も一般的な原因は `cwd` の不一致です。セッションは `~/.claude/projects/<encoded-cwd>/*.jsonl` に保存されます。または、`CLAUDE_CONFIG_DIR` 環境変数を設定した場合は `$CLAUDE_CONFIG_DIR/projects/<encoded-cwd>/*.jsonl` に保存されます。ここで `<encoded-cwd>` は、すべての英数字以外の文字が `-` に置き換えられた絶対作業ディレクトリです（したがって `/Users/me/proj` は `-Users-me-proj` になります）。resume 呼び出しが別のディレクトリから実行される場合、SDK は間違った場所を探します。セッションファイルも現在のマシンに存在する必要があります。
</Tip>

マシン間またはサーバーレス環境でセッションを再開するには、[`SessionStore` アダプター](/docs/ja/agent-sdk/session-storage)を使用して共有ストレージにトランスクリプトをミラーリングします。

<h3 id="fork-to-explore-alternatives">
  フォークして代替案を探索する
</h3>

フォークは、元の履歴のコピーで開始する新しいセッションを作成しますが、その時点から分岐します。フォークは独自のセッション ID を取得します。元の ID と履歴は変更されません。2 つの独立したセッションが終わり、それぞれ別々に再開できます。

<Note>
  フォークは会話履歴を分岐させ、ファイルシステムは分岐させません。フォークされたエージェントがファイルを編集する場合、それらの変更は実際であり、同じディレクトリで動作しているすべてのセッションに表示されます。ファイル変更を分岐して戻すには、[ファイルチェックポイント](/docs/ja/agent-sdk/file-checkpointing)を使用します。
</Note>

この例は、[セッション ID をキャプチャする](#capture-the-session-id)に基づいています。`session_id` で認証モジュールを既に分析し、JWT に焦点を当てたスレッドを失わずに OAuth2 を探索したいです。最初のブロックはセッションをフォークし、フォークの ID（`forked_id`）をキャプチャします。2 番目のブロックは元の `session_id` を再開して、JWT パスを続行します。これで、2 つの別々の履歴を指す 2 つのセッション ID があります：

<CodeGroup>
  ```python Python theme={null}
  # Fork: branch from session_id into a new session
  forked_id = None
  async for message in query(
      prompt="Instead of JWT, outline how OAuth2 would work for the auth module",
      options=ClaudeAgentOptions(
          resume=session_id,
          fork_session=True,
          max_turns=5,
      ),
  ):
      if isinstance(message, ResultMessage):
          forked_id = message.session_id  # The fork's ID, distinct from session_id
          if message.subtype == "success":
              print(message.result)

  print(f"Forked session: {forked_id}")

  # Original session is untouched; resuming it continues the JWT thread
  async for message in query(
      prompt="Continue with the JWT approach",
      options=ClaudeAgentOptions(resume=session_id),
  ):
      if isinstance(message, ResultMessage) and message.subtype == "success":
          print(message.result)
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const sessionId = "..."; // The ID you captured in the previous example

  // Fork: branch from sessionId into a new session
  let forkedId: string | undefined;

  for await (const message of query({
    prompt: "Instead of JWT, outline how OAuth2 would work for the auth module",
    options: {
      resume: sessionId,
      forkSession: true,
      maxTurns: 5
    }
  })) {
    if (message.type === "system" && message.subtype === "init") {
      forkedId = message.session_id; // The fork's ID, distinct from sessionId
    }
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }

  console.log(`Forked session: ${forkedId}`);

  // Original session is untouched; resuming it continues the JWT thread
  for await (const message of query({
    prompt: "Continue with the JWT approach",
    options: { resume: sessionId }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```
</CodeGroup>

`forkedId` が元のセッション ID と異なることが表示されるはずです。元のセッションを再開すると、JWT スレッドが続行されます。これにより、フォークが元の履歴を変更しなかったことが確認されます。

<h2 id="resume-across-hosts">
  ホスト間で再開する
</h2>

セッションファイルは、それを作成したマシンに対してローカルです。別のホスト（CI ワーカー、一時的なコンテナ、サーバーレス）でセッションを再開するには、2 つのオプションがあります：

* **セッションファイルを移動します。** 最初の実行から `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl` を保持し、`resume` を呼び出す前に新しいホスト上の同じパスに復元します。`cwd` は一致する必要があります。
* **セッション再開に依存しないでください。** 必要な結果（分析出力、決定、ファイル差分）をアプリケーション状態としてキャプチャし、新しいセッションのプロンプトに渡します。これは多くの場合、トランスクリプトファイルを周りに配送するよりも堅牢です。

両方の SDK は、ディスク上のセッションを列挙し、メッセージを読み取るための関数を公開します。TypeScript では [`listSessions()`](/docs/ja/agent-sdk/typescript#listsessions) と [`getSessionMessages()`](/docs/ja/agent-sdk/typescript#getsessionmessages)、Python では [`list_sessions()`](/docs/ja/agent-sdk/python#list_sessions) と [`get_session_messages()`](/docs/ja/agent-sdk/python#get_session_messages)。これらを使用して、カスタムセッションピッカー、クリーンアップロジック、またはトランスクリプトビューアーを構築します。

両方の SDK は、個別のセッションを検索および変更するための関数も公開します。Python では [`get_session_info()`](/docs/ja/agent-sdk/python#get_session_info)、[`rename_session()`](/docs/ja/agent-sdk/python#rename_session)、および [`tag_session()`](/docs/ja/agent-sdk/python#tag_session)。TypeScript では [`getSessionInfo()`](/docs/ja/agent-sdk/typescript#getsessioninfo)、[`renameSession()`](/docs/ja/agent-sdk/typescript#renamesession)、および [`tagSession()`](/docs/ja/agent-sdk/typescript#tagsession)。これらを使用して、セッションをタグで整理するか、人間が読める形のタイトルを付けます。

<h2 id="related-resources">
  関連リソース
</h2>

* [エージェントループの仕組み](/docs/ja/agent-sdk/agent-loop)：セッション内のターン、メッセージ、およびコンテキスト蓄積を理解する
* [ファイルチェックポイント](/docs/ja/agent-sdk/file-checkpointing)：セッション内でエージェントが行ったファイル変更をスナップショット化して戻す
* [Python `ClaudeAgentOptions`](/docs/ja/agent-sdk/python#claudeagentoptions)：Python のセッションオプション参照全体
* [TypeScript `Options`](/docs/ja/agent-sdk/typescript#options)：TypeScript のセッションオプション参照全体
