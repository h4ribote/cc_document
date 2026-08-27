> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# セッションを外部ストレージに永続化する

> セッションのトランスクリプトを S3、Redis、または独自のバックエンドにミラーリングして、任意のホストからセッションを再開できるようにします。

デフォルトでは、SDK はセッションのトランスクリプトを `~/.claude/projects/` 下のローカルファイルシステムの JSONL ファイルに書き込みます。`SessionStore` アダプターを使用すると、これらのトランスクリプトを S3、Redis、データベースなど独自のバックエンドにミラーリングできるため、あるホストで作成されたセッションを別のホストで再開できます。

セッションストアを使用する一般的な理由：

* **マルチホスト展開。** サーバーレス関数、オートスケーリングワーカー、CI ランナーはファイルシステムを共有しません。共有ストアを使用すると、任意のレプリカが任意のセッションを再開できます。
* **耐久性。** ローカルコンテナは一時的です。S3 またはデータベースで支援されるストアは、再起動と再デプロイを乗り越えます。
* **コンプライアンスと監査。** 既に管理しているストレージにトランスクリプトを保持し、独自の保持ルール、暗号化、アクセス制御を適用できます。

<h2 id="the-sessionstore-interface">
  `SessionStore` インターフェース
</h2>

`SessionStore` は、2 つの必須メソッド `append` と `load`、および 3 つのオプションメソッドを持つオブジェクトです。SDK は `append` を呼び出してクエリ中にトランスクリプトエントリを書き込み、`load` を呼び出して再開用にそれらを読み戻します。

<CodeGroup>
  ```typescript TypeScript theme={null}
  // Exported from @anthropic-ai/claude-agent-sdk as
  // SessionStore, SessionKey, SessionStoreEntry.

  type SessionKey = {
    projectKey: string;
    sessionId: string;
    subpath?: string;
  };

  type SessionStore = {
    // Required
    append(key: SessionKey, entries: SessionStoreEntry[]): Promise<void>;
    load(key: SessionKey): Promise<SessionStoreEntry[] | null>;

    // Optional
    listSessions?(
      projectKey: string,
    ): Promise<Array<{ sessionId: string; mtime: number }>>;
    delete?(key: SessionKey): Promise<void>;
    listSubkeys?(key: {
      projectKey: string;
      sessionId: string;
    }): Promise<string[]>;
  };
  ```

  ```python Python theme={null}
  # Exported from claude_agent_sdk as
  # SessionStore, SessionKey, SessionStoreEntry.

  class SessionKey(TypedDict):
      project_key: str
      session_id: str
      subpath: NotRequired[str]

  class SessionStore(Protocol):
      # Required
      async def append(
          self, key: SessionKey, entries: list[SessionStoreEntry]
      ) -> None: ...
      async def load(self, key: SessionKey) -> list[SessionStoreEntry] | None: ...

      # Optional — omit or raise NotImplementedError
      async def list_sessions(
          self, project_key: str
      ) -> list[SessionStoreListEntry]: ...
      async def delete(self, key: SessionKey) -> None: ...
      async def list_subkeys(self, key: SessionListSubkeysKey) -> list[str]: ...
  ```
</CodeGroup>

`SessionKey` は 1 つのトランスクリプトをアドレス指定します。`projectKey` は作業ディレクトリの安定したファイルシステム安全なエンコーディング、`sessionId` はセッション UUID、`subpath` はエントリがサブエージェントトランスクリプトまたはサイドカーファイルではなくメイン会話に属する場合に設定されます。`subpath` を不透明なキーサフィックスとして扱います。これはオンディスクレイアウトに従います。例えば `subagents/agent-<id>` です。`subpath` が未定義の場合、キーはメイントランスクリプトを参照します。

| メソッド           | 必須  | 呼び出されるタイミング                                                                                                                                    |
| :------------- | :-- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| `append`       | はい  | トランスクリプトエントリの各バッチがローカルに書き込まれた後。エントリは JSON セーフなオブジェクトで、ローカル JSONL では 1 行に 1 つです。                                                                |
| `load`         | はい  | サブプロセスが生成される前に 1 回、`resume` が設定されている場合。セッションが不明な場合は `null` を返します。                                                                              |
| `listSessions` | いいえ | `listSessions({ sessionStore })` および `continue: true` を指定した `query()`/`startup()` によって。未定義の場合、これらの呼び出しはスローされます。                                |
| `delete`       | いいえ | `deleteSession({ sessionStore })` によって。メインキー（`subpath` なし）を削除する場合、そのセッションのすべてのサブキーにカスケードする必要があります。未定義の場合、削除は no-op です。これはアペンドのみのバックエンドに適しています。 |
| `listSubkeys`  | いいえ | 再開中に、サブエージェントトランスクリプトを検出するため。未定義の場合、メイントランスクリプトのみが復元されます。                                                                                      |

<h2 id="quick-start">
  クイックスタート
</h2>

SDK は開発とテスト用に `InMemorySessionStore` を提供しています。以下の例は、ストアを接続してクエリを実行し、結果メッセージからセッション ID をキャプチャしてから、2 番目の `query()` 呼び出しでストアから再開します。2 番目の呼び出しは同じストアインスタンスと `resume` を渡すため、SDK はローカルファイルシステムではなくストアからトランスクリプトを読み込みます：

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query, InMemorySessionStore } from "@anthropic-ai/claude-agent-sdk";

  const store = new InMemorySessionStore();

  let sessionId: string | undefined;
  for await (const message of query({
    prompt: "List the TypeScript files under src/",
    options: { sessionStore: store },
  })) {
    if (message.type === "result") {
      sessionId = message.session_id;
    }
  }

  // Resume from the store. The agent has full context from the first call.
  for await (const message of query({
    prompt: "Summarize what those files do",
    options: { sessionStore: store, resume: sessionId },
  })) {
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import (
      ClaudeAgentOptions,
      InMemorySessionStore,
      ResultMessage,
      query,
  )

  store = InMemorySessionStore()


  async def main():
      session_id = None
      async for message in query(
          prompt="List the Python files under src/",
          options=ClaudeAgentOptions(session_store=store),
      ):
          if isinstance(message, ResultMessage):
              session_id = message.session_id

      # Resume from the store. The agent has full context from the first call.
      async for message in query(
          prompt="Summarize what those files do",
          options=ClaudeAgentOptions(session_store=store, resume=session_id),
      ):
          if isinstance(message, ResultMessage) and message.subtype == "success":
              print(message.result)


  asyncio.run(main())
  ```
</CodeGroup>

2 番目のクエリは最初のクエリのファイルの概要を出力し、エージェントがストアから完全なコンテキストで再開されたことを示しています。

<h2 id="write-your-own-adapter">
  独自のアダプターを作成する
</h2>

バックエンドに対して `append` と `load` を実装します。ストアに対して `listSessions()`、`deleteSession()`、およびサブエージェント再開を機能させたい場合は、`listSessions`、`delete`、および `listSubkeys` を追加します。

`append` に渡されるエントリは `SessionStoreEntry` として型付けされます（`{ type: string; ... }` オブジェクト）。これらを不透明な JSON セーフ値として扱います。順序を保持して永続化し、`load` から同じ順序で返します。`load` は追加されたものと深く等しいエントリを返す必要があります。バイト等しいシリアル化は必須ではないため、Postgres `jsonb` のようなオブジェクトキーを並べ替えるバックエンドは問題ありません。

<h2 id="reference-implementations">
  リファレンス実装
</h2>

TypeScript SDK リポジトリには、[`examples/session-stores/`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores) の下に S3、Redis、Postgres 用の実行可能なリファレンスアダプターが含まれています。これらは npm に公開されていません。必要な `src/` ファイルをプロジェクトにコピーし、対応するバックエンドクライアントをインストールしてください。

| アダプター                                                                                                                          | バックエンドクライアント         | ストレージモデル                                                   |
| :----------------------------------------------------------------------------------------------------------------------------- | :------------------- | :--------------------------------------------------------- |
| [`S3SessionStore`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores/s3)             | `@aws-sdk/client-s3` | `append()` ごとに 1 つの JSONL パートファイル。`load()` はリスト、ソート、連結します。 |
| [`RedisSessionStore`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores/redis)       | `ioredis`            | トランスクリプトごとの `RPUSH`/`LRANGE` リスト、およびソート済みセットセッションインデックス。   |
| [`PostgresSessionStore`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores/postgres) | `pg`                 | `jsonb` テーブルのエントリごとに 1 行、`BIGSERIAL` で順序付け。                |

各アダプターは事前に設定されたクライアントインスタンスを取得するため、認証情報、TLS、リージョン、プーリングを制御できます。例えば、S3 の場合：

```typescript TypeScript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";
import { S3Client } from "@aws-sdk/client-s3";
import { S3SessionStore } from "./S3SessionStore"; // copied from examples/session-stores/s3

const store = new S3SessionStore({
  bucket: "my-claude-sessions",
  prefix: "transcripts",
  client: new S3Client({ region: "us-east-1" }),
});

for await (const message of query({
  prompt: "Hello!",
  options: { sessionStore: store },
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}

// Later, possibly on a different host:
for await (const message of query({
  prompt: "Continue where we left off",
  options: { sessionStore: store, resume: "previous-session-id" },
})) {
  // ...
}
```

<h3 id="validate-your-adapter">
  アダプターを検証する
</h3>

両方の SDK は、`append`、`load`、およびオプションメソッドが満たす必要がある動作契約をアサートする適合スイートを提供しています。オプションメソッドのテストは、これらのメソッドが実装されていない場合、自動的にスキップされます。

TypeScript では、例ディレクトリから [`shared/conformance.ts`](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/examples/session-stores/shared/conformance.ts) をテストスイートにコピーしてください。Python では、スイートはパッケージに含まれています：

```python Python theme={null}
import pytest
from claude_agent_sdk.testing import run_session_store_conformance


@pytest.mark.asyncio
async def test_my_store_conformance():
    await run_session_store_conformance(MyRedisStore)
```

<h2 id="behavior-notes">
  動作に関する注記
</h2>

<h3 id="dual-write-architecture">
  デュアルライトアーキテクチャ
</h3>

ストアはミラーであり、置き換えではありません。Claude Code サブプロセスは常にローカルディスクに最初に書き込みます。SDK はその後、各バッチを `append()` に転送します。ローカルコピーを一時的にしたい場合は、`options.env` の一時ディレクトリに `CLAUDE_CONFIG_DIR` をポイントします。ミラーはローカル書き込みに依存するため、`sessionStore` を `persistSession: false` と組み合わせることはできません。両方を設定するとスローされます。また、`enableFileCheckpointing` と組み合わせることもできません。ファイル履歴バックアップブロブはローカルディスクに直接書き込まれ、ストアにはミラーリングされないためです。

<h3 id="mirror-writes-are-best-effort">
  ミラー書き込みはベストエフォート
</h3>

`append()` が拒否した場合、SDK は短いバックオフで最大 2 回まで再試行し、合計で最大 3 回の試行を行います。タイムアウトした呼び出しは再試行されません。元の呼び出しがまだ到達する可能性があるためです。バッチがまだ失敗した場合、エラーはログに記録され、`{ type: "system", subtype: "mirror_error" }` メッセージがイテレータに発行され、バッチは削除され、クエリは続行されます。ローカルトランスクリプトは既にディスク上で耐久性があるため、ストア障害はエージェントを中断したり、ローカルでデータを失ったりしません。ストアデータ損失を検出する必要がある場合は `mirror_error` を監視してください。再試行されたバッチは既に到達したエントリを再配信できるため、`append()` 実装で `entry.uuid` によって重複排除してください。

<h3 id="getsessionmessages-returns-the-post-compaction-chain">
  `getSessionMessages` は圧縮後のチェーンを返す
</h3>

`getSessionMessages({ sessionStore })` は、エージェントが再開時に見るリンクされたメッセージチェーンを返します。自動圧縮後、以前のターンは概要に置き換えられるため、ストアが 503 個の生エントリを保持するセッションは `getSessionMessages` から 18 個のメッセージを返す場合があります。圧縮前のターンとメタデータエントリを含む完全な生履歴については、`store.load(key)` を直接呼び出します。

<h3 id="forksession-is-not-a-byte-copy">
  `forkSession` はバイトコピーではない
</h3>

`forkSession({ sessionStore })` はソースエントリを読み込み、すべての `sessionId` フィールドを書き直し、メッセージ UUID を再マップしてから、変換されたエントリを新しいキーの下に追加します。アダプターレベルのコピーまたは `CopyObject` ショートカットは、古いセッション ID を参照するトランスクリプトを生成するため、SDK はそれを使用しません。

<h3 id="subagent-transcripts">
  サブエージェントトランスクリプト
</h3>

サブエージェントトランスクリプトは `subpath: "subagents/agent-<id>"` の下にミラーリングされます。`listSubagents({ sessionStore })` はアダプターが `listSubkeys` を実装する必要があります。`getSubagentMessages({ sessionStore })` は利用可能な場合はそれを使用しますが、未定義の場合は直接サブパスにフォールバックします。再開も `listSubkeys` を呼び出してサブエージェントファイルを復元します。これがない場合、メイントランスクリプトのみが具体化されます。

<h3 id="retention">
  保持
</h3>

SDK は独自の判断でストアから削除することはありません。保持はアダプターの責任です。コンプライアンス要件に従って TTL、S3 ライフサイクルポリシー、またはスケジュール済みクリーンアップを実装します。`CLAUDE_CONFIG_DIR` の下のローカルトランスクリプトは `cleanupPeriodDays` 設定によって独立して掃除されます。

<h2 id="supported-on">
  サポート対象
</h2>

以下の SDK 関数は `sessionStore` オプションを受け入れ、提供されている場合、ローカルファイルシステムではなくストアに対して動作します：

* [`query()`](/docs/ja/agent-sdk/typescript#query)
* [`startup()`](/docs/ja/agent-sdk/typescript#startup)
* [`listSessions()`](/docs/ja/agent-sdk/typescript#listsessions)
* [`getSessionInfo()`](/docs/ja/agent-sdk/typescript#getsessioninfo)
* [`getSessionMessages()`](/docs/ja/agent-sdk/typescript#getsessionmessages)
* [`renameSession()`](/docs/ja/agent-sdk/typescript#renamesession)
* [`tagSession()`](/docs/ja/agent-sdk/typescript#tagsession)
* [`deleteSession()`](/docs/ja/agent-sdk/typescript)
* [`forkSession()`](/docs/ja/agent-sdk/typescript)
* [`listSubagents()`](/docs/ja/agent-sdk/typescript)
* [`getSubagentMessages()`](/docs/ja/agent-sdk/typescript)

<h2 id="related-resources">
  関連リソース
</h2>

* [セッションを操作する](/docs/ja/agent-sdk/sessions)：カスタムストアなしで続行、再開、フォーク
* [SDK をホストする](/docs/ja/agent-sdk/hosting)：マルチホスト環境のデプロイメントパターン
* [TypeScript `Options`](/docs/ja/agent-sdk/typescript#options)：完全なオプションリファレンス
* [`examples/session-stores/`](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores)：実行可能な S3、Redis、Postgres リファレンスアダプター
