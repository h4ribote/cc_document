> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Agent SDK リファレンス - TypeScript

> TypeScript Agent SDK の完全な API リファレンス。すべての関数、型、インターフェースを含みます。

<script src="/docs/components/typescript-sdk-type-links.js" defer />

<h2 id="installation">
  インストール
</h2>

```bash theme={null}
npm install @anthropic-ai/claude-agent-sdk
```

<Note>
  SDK は、`@anthropic-ai/claude-agent-sdk-darwin-arm64` などのオプション依存関係として、プラットフォーム用のネイティブ Claude Code バイナリをバンドルしています。Claude Code を別途インストールする必要はありません。パッケージマネージャーがオプション依存関係をスキップする場合、SDK は `Native CLI binary for <platform> not found` をスローします。代わりに、別途インストールされた `claude` バイナリに [`pathToClaudeCodeExecutable`](#options) を設定してください。
</Note>

<h3 id="compile-to-a-single-executable">
  単一の実行可能ファイルにコンパイルする
</h3>

`bun build --compile` を使用してアプリケーションを単一ファイルの実行可能ファイルにコンパイルする場合、SDK は実行時にバンドルされた CLI バイナリを解決できません。`require.resolve` はコンパイルされた実行可能ファイルの `$bunfs` 仮想ファイルシステム内では機能しないため、SDK は `Native CLI binary for <platform> not found` をスローします。

この問題を回避するには、プラットフォームバイナリをファイルアセットとして埋め込み、起動時に `extractFromBunfs()` を使用して実際のパスに抽出し、そのパスを [`pathToClaudeCodeExecutable`](#options) に渡します。

`extractFromBunfs()` ヘルパーには `@anthropic-ai/claude-agent-sdk` v0.3.144 以降が必要です。以下の例は macOS on Apple Silicon 向けにビルドします。

```typescript theme={null}
import binPath from "@anthropic-ai/claude-agent-sdk-darwin-arm64/claude" with { type: "file" };
import { extractFromBunfs } from "@anthropic-ai/claude-agent-sdk/extract";
import { query } from "@anthropic-ai/claude-agent-sdk";

const cliPath = extractFromBunfs(binPath);

for await (const message of query({
  prompt: "Hello",
  options: { pathToClaudeCodeExecutable: cliPath },
})) {
  console.log(message);
}
```

`extractFromBunfs()` は、コンパイルされた実行可能ファイルの仮想ファイルシステムから埋め込まれたバイナリをユーザーごとの一時ディレクトリにコピーし、実際のパスを返します。コンパイルされた実行可能ファイルの外では、入力パスを変更せずに返すため、同じコードは開発環境で変更なしに実行されます。

各コンパイルされた実行可能ファイルは、単一プラットフォームのバイナリを埋め込みます。インポート内のプラットフォームパッケージを `--target` と一致させます。

* クロスコンパイルするには、一致しないプラットフォームパッケージをインストールします。例えば `npm install @anthropic-ai/claude-agent-sdk-linux-x64 --force`。
* Windows では、バイナリサブパスは `claude.exe` です。例えば `@anthropic-ai/claude-agent-sdk-win32-x64/claude.exe`。

<h2 id="functions">
  関数
</h2>

<h3 id="query">
  `query()`
</h3>

Claude Code と対話するための主要な関数です。メッセージが到着するにつれてストリーミングする非同期ジェネレータを作成します。

```typescript theme={null}
function query({
  prompt,
  options
}: {
  prompt: string | AsyncIterable<SDKUserMessage>;
  options?: Options;
}): Query;
```

<h4 id="parameters">
  パラメータ
</h4>

| パラメータ     | 型                                                                | 説明                                         |
| :-------- | :--------------------------------------------------------------- | :----------------------------------------- |
| `prompt`  | `string \| AsyncIterable<`[`SDKUserMessage`](#sdkusermessage)`>` | 文字列またはストリーミングモード用の非同期反復可能オブジェクトとしての入力プロンプト |
| `options` | [`Options`](#options)                                            | オプションの設定オブジェクト（以下の Options 型を参照）           |

<h4 id="returns">
  戻り値
</h4>

[`Query`](#query-object) オブジェクトを返します。これは `AsyncGenerator<`[`SDKMessage`](#sdkmessage)`, void>` を拡張し、追加のメソッドを持ちます。

<h3 id="startup">
  `startup()`
</h3>

プロンプトが利用可能になる前に、CLI サブプロセスをスポーンして初期化ハンドシェイクを完了することで、プリウォーミングします。返された [`WarmQuery`](#warmquery) ハンドルは後でプロンプトを受け入れ、既に準備ができているプロセスに書き込むため、最初の `query()` 呼び出しはサブプロセスのスポーンと初期化コストをインラインで支払うことなく解決します。

```typescript theme={null}
function startup(params?: {
  options?: Options;
  initializeTimeoutMs?: number;
}): Promise<WarmQuery>;
```

<h4 id="parameters-2">
  パラメータ
</h4>

| パラメータ                 | 型                     | 説明                                                                            |
| :-------------------- | :-------------------- | :---------------------------------------------------------------------------- |
| `options`             | [`Options`](#options) | オプションの設定オブジェクト。`query()` の `options` パラメータと同じです                               |
| `initializeTimeoutMs` | `number`              | サブプロセス初期化を待つ最大時間（ミリ秒）。デフォルトは `60000` です。初期化が時間内に完了しない場合、プロミスはタイムアウトエラーで拒否されます |

<h4 id="returns-2">
  戻り値
</h4>

サブプロセスがスポーンされ、初期化ハンドシェイクを完了したら解決する `Promise<`[`WarmQuery`](#warmquery)`>` を返します。

<h4 id="example">
  例
</h4>

アプリケーションブート時など、早期に `startup()` を呼び出し、プロンプトが準備できたら返されたハンドルで `.query()` を呼び出します。これにより、サブプロセスのスポーンと初期化をクリティカルパスから移動させます。

```typescript theme={null}
import { startup } from "@anthropic-ai/claude-agent-sdk";

// スタートアップコストを事前に支払う
const warm = await startup({ options: { maxTurns: 3 } });

// 後で、プロンプトが準備できたら、これは即座です
for await (const message of warm.query("What files are here?")) {
  console.log(message);
}
```

<h3 id="tool">
  `tool()`
</h3>

SDK MCP サーバーで使用するためのタイプセーフな MCP ツール定義を作成します。

```typescript theme={null}
function tool<Schema extends AnyZodRawShape>(
  name: string,
  description: string,
  inputSchema: Schema,
  handler: (args: InferShape<Schema>, extra: unknown) => Promise<CallToolResult>,
  extras?: { annotations?: ToolAnnotations }
): SdkMcpToolDefinition<Schema>;
```

<h4 id="parameters-3">
  パラメータ
</h4>

| パラメータ         | 型                                                                 | 説明                                                |
| :------------ | :---------------------------------------------------------------- | :------------------------------------------------ |
| `name`        | `string`                                                          | ツールの名前                                            |
| `description` | `string`                                                          | ツールが何をするかの説明                                      |
| `inputSchema` | `Schema extends AnyZodRawShape`                                   | ツールの入力パラメータを定義する Zod スキーマ（Zod 3 と Zod 4 の両方をサポート） |
| `handler`     | `(args, extra) => Promise<`[`CallToolResult`](#calltoolresult)`>` | ツールロジックを実行する非同期関数                                 |
| `extras`      | `{ annotations?: `[`ToolAnnotations`](#toolannotations)` }`       | クライアントに動作ヒントを提供するオプションの MCP ツール注釈                 |

<h4 id="toolannotations">
  `ToolAnnotations`
</h4>

`@modelcontextprotocol/sdk/types.js` から再エクスポートされます。すべてのフィールドはオプションのヒントです。クライアントはセキュリティ決定のためにこれらに依存すべきではありません。

| フィールド             | 型         | デフォルト       | 説明                                                                           |
| :---------------- | :-------- | :---------- | :--------------------------------------------------------------------------- |
| `title`           | `string`  | `undefined` | ツールの人間が読める形式のタイトル                                                            |
| `readOnlyHint`    | `boolean` | `false`     | `true` の場合、ツールはその環境を変更しません                                                   |
| `destructiveHint` | `boolean` | `true`      | `true` の場合、ツールは破壊的な更新を実行する可能性があります（`readOnlyHint` が `false` の場合のみ意味があります）    |
| `idempotentHint`  | `boolean` | `false`     | `true` の場合、同じ引数での繰り返し呼び出しは追加の効果がありません（`readOnlyHint` が `false` の場合のみ意味があります） |
| `openWorldHint`   | `boolean` | `true`      | `true` の場合、ツールは外部エンティティと対話します（例：ウェブ検索）。`false` の場合、ツールのドメインは閉じています（例：メモリツール） |

```typescript theme={null}
import { tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const searchTool = tool(
  "search",
  "Search the web",
  { query: z.string() },
  async ({ query }) => {
    return { content: [{ type: "text", text: `Results for: ${query}` }] };
  },
  { annotations: { readOnlyHint: true, openWorldHint: true } }
);
```

<h3 id="createsdkmcpserver">
  `createSdkMcpServer()`
</h3>

アプリケーションと同じプロセスで実行される MCP サーバーインスタンスを作成します。

```typescript theme={null}
function createSdkMcpServer(options: {
  name: string;
  version?: string;
  tools?: Array<SdkMcpToolDefinition<any>>;
}): McpSdkServerConfigWithInstance;
```

<h4 id="parameters-4">
  パラメータ
</h4>

| パラメータ             | 型                             | 説明                               |
| :---------------- | :---------------------------- | :------------------------------- |
| `options.name`    | `string`                      | MCP サーバーの名前                      |
| `options.version` | `string`                      | オプションのバージョン文字列                   |
| `options.tools`   | `Array<SdkMcpToolDefinition>` | [`tool()`](#tool) で作成されたツール定義の配列 |

<h3 id="listsessions">
  `listSessions()`
</h3>

軽いメタデータを含む過去のセッションを検出してリストします。プロジェクトディレクトリでフィルタリングするか、すべてのプロジェクト全体でセッションをリストします。

```typescript theme={null}
function listSessions(options?: ListSessionsOptions): Promise<SDKSessionInfo[]>;
```

<h4 id="parameters-5">
  パラメータ
</h4>

| パラメータ                      | 型         | デフォルト       | 説明                                                   |
| :------------------------- | :-------- | :---------- | :--------------------------------------------------- |
| `options.dir`              | `string`  | `undefined` | セッションをリストするディレクトリ。省略すると、すべてのプロジェクト全体でセッションを返します      |
| `options.limit`            | `number`  | `undefined` | 返すセッションの最大数                                          |
| `options.includeWorktrees` | `boolean` | `true`      | `dir` が git リポジトリ内にある場合、すべての worktree パスからセッションを含めます |

<h4 id="return-type-sdksessioninfo">
  戻り値の型：`SDKSessionInfo`
</h4>

| プロパティ          | 型                     | 説明                                                  |
| :------------- | :-------------------- | :-------------------------------------------------- |
| `sessionId`    | `string`              | 一意のセッション識別子（UUID）                                   |
| `summary`      | `string`              | 表示タイトル：カスタムタイトル、自動生成されたサマリー、または最初のプロンプト             |
| `lastModified` | `number`              | エポック以降のミリ秒単位での最後の変更時刻                               |
| `fileSize`     | `number \| undefined` | セッションファイルサイズ（バイト）。ローカル JSONL ストレージの場合のみ入力されます       |
| `customTitle`  | `string \| undefined` | ユーザーが設定したセッションタイトル（`/rename` 経由）                    |
| `firstPrompt`  | `string \| undefined` | セッション内の最初の意味のあるユーザープロンプト                            |
| `gitBranch`    | `string \| undefined` | セッション終了時の Git ブランチ                                  |
| `cwd`          | `string \| undefined` | セッションの作業ディレクトリ                                      |
| `tag`          | `string \| undefined` | ユーザーが設定したセッションタグ（[`tagSession()`](#tagsession) を参照） |
| `createdAt`    | `number \| undefined` | 最初のエントリのタイムスタンプからのエポック以降のミリ秒単位での作成時刻                |

<h4 id="example-2">
  例
</h4>

プロジェクトの 10 個の最新セッションを出力します。結果は `lastModified` の降順でソートされるため、最初の項目が最新です。`dir` を省略してすべてのプロジェクト全体を検索します。

```typescript theme={null}
import { listSessions } from "@anthropic-ai/claude-agent-sdk";

const sessions = await listSessions({ dir: "/path/to/project", limit: 10 });

for (const session of sessions) {
  console.log(`${session.summary} (${session.sessionId})`);
}
```

<h3 id="getsessionmessages">
  `getSessionMessages()`
</h3>

過去のセッショントランスクリプトからユーザーおよびアシスタントメッセージを読み取ります。

```typescript theme={null}
function getSessionMessages(
  sessionId: string,
  options?: GetSessionMessagesOptions
): Promise<SessionMessage[]>;
```

<h4 id="parameters-6">
  パラメータ
</h4>

| パラメータ            | 型        | デフォルト       | 説明                                            |
| :--------------- | :------- | :---------- | :-------------------------------------------- |
| `sessionId`      | `string` | 必須          | 読み取るセッション UUID（`listSessions()` を参照）          |
| `options.dir`    | `string` | `undefined` | セッションを見つけるプロジェクトディレクトリ。省略すると、すべてのプロジェクトを検索します |
| `options.limit`  | `number` | `undefined` | 返すメッセージの最大数                                   |
| `options.offset` | `number` | `undefined` | 開始からスキップするメッセージ数                              |

<h4 id="return-type-sessionmessage">
  戻り値の型：`SessionMessage`
</h4>

| プロパティ                | 型                       | 説明                                                                                                                                                                                      |
| :------------------- | :---------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`               | `"user" \| "assistant"` | メッセージロール                                                                                                                                                                                |
| `uuid`               | `string`                | 一意のメッセージ識別子                                                                                                                                                                             |
| `session_id`         | `string`                | このメッセージが属するセッション                                                                                                                                                                        |
| `message`            | `unknown`               | トランスクリプトからの生のメッセージペイロード                                                                                                                                                                 |
| `parent_tool_use_id` | `string \| null`        | サブエージェントメッセージの場合、スポーニング `Agent` ツール呼び出しの `tool_use_id`。メインセッションメッセージおよび古いセッションの場合は `null`                                                                                               |
| `parent_agent_id`    | `string \| null`        | [ネストされたサブエージェント](/docs/ja/sub-agents#spawn-nested-subagents)からのメッセージの場合、それをスポーンしたサブエージェントの `agentId`。メインセッションメッセージ、トップレベルサブエージェントからのメッセージ、および古いセッションの場合は `null`。Claude Code v2.1.202 以降が必要です |

<h4 id="example-3">
  例
</h4>

```typescript theme={null}
import { listSessions, getSessionMessages } from "@anthropic-ai/claude-agent-sdk";

const [latest] = await listSessions({ dir: "/path/to/project", limit: 1 });

if (latest) {
  const messages = await getSessionMessages(latest.sessionId, {
    dir: "/path/to/project",
    limit: 20
  });

  for (const msg of messages) {
    console.log(`[${msg.type}] ${msg.uuid}`);
  }
}
```

<h3 id="getsessioninfo">
  `getSessionInfo()`
</h3>

プロジェクトディレクトリ全体をスキャンせずに、ID でセッションのメタデータを読み取ります。

```typescript theme={null}
function getSessionInfo(
  sessionId: string,
  options?: GetSessionInfoOptions
): Promise<SDKSessionInfo | undefined>;
```

<h4 id="parameters-7">
  パラメータ
</h4>

| パラメータ         | 型        | デフォルト       | 説明                                          |
| :------------ | :------- | :---------- | :------------------------------------------ |
| `sessionId`   | `string` | 必須          | ルックアップするセッションの UUID                         |
| `options.dir` | `string` | `undefined` | プロジェクトディレクトリパス。省略すると、すべてのプロジェクトディレクトリを検索します |

[`SDKSessionInfo`](#return-type-sdksessioninfo) を返すか、セッションが見つからない場合は `undefined` を返します。

<h3 id="renamesession">
  `renameSession()`
</h3>

カスタムタイトルエントリを追加することでセッションの名前を変更します。繰り返し呼び出しは安全です。最新のタイトルが優先されます。

```typescript theme={null}
function renameSession(
  sessionId: string,
  title: string,
  options?: SessionMutationOptions
): Promise<void>;
```

<h4 id="parameters-8">
  パラメータ
</h4>

| パラメータ         | 型        | デフォルト       | 説明                                          |
| :------------ | :------- | :---------- | :------------------------------------------ |
| `sessionId`   | `string` | 必須          | 名前を変更するセッションの UUID                          |
| `title`       | `string` | 必須          | 新しいタイトル。空白をトリミングした後、空でない必要があります             |
| `options.dir` | `string` | `undefined` | プロジェクトディレクトリパス。省略すると、すべてのプロジェクトディレクトリを検索します |

<h3 id="tagsession">
  `tagSession()`
</h3>

セッションにタグを付けます。`null` を渡してタグをクリアします。繰り返し呼び出しは安全です。最新のタグが優先されます。

```typescript theme={null}
function tagSession(
  sessionId: string,
  tag: string | null,
  options?: SessionMutationOptions
): Promise<void>;
```

<h4 id="parameters-9">
  パラメータ
</h4>

| パラメータ         | 型                | デフォルト       | 説明                                          |
| :------------ | :--------------- | :---------- | :------------------------------------------ |
| `sessionId`   | `string`         | 必須          | タグを付けるセッションの UUID                           |
| `tag`         | `string \| null` | 必須          | タグ文字列、またはクリアする場合は `null`                    |
| `options.dir` | `string`         | `undefined` | プロジェクトディレクトリパス。省略すると、すべてのプロジェクトディレクトリを検索します |

<h3 id="resolvesettings">
  `resolveSettings()`
</h3>

CLI と同じマージエンジンを使用して、指定されたディレクトリの有効な Claude Code 設定を解決します。Claude CLI をスポーンせずに実行します。`query()` 呼び出しを呼び出す前に、その呼び出しが何の設定を見るかを検査するために使用します。

<Note>
  この関数はアルファ版であり、安定化前に API が変更される可能性があります。CLI スタートアップとの同等性のために、macOS plist および Windows HKLM/HKCU を含む MDM ソースを読み取りますが、管理者が設定した `policyHelper` サブプロセスは実行しません。`permissions.defaultMode` フィールドは、プロジェクト設定を含むすべてのティアから現状のまま返されます。CLI が昇格するアクセス許可モードを尊重する前に適用する信頼フィルタは適用されません。
</Note>

```typescript theme={null}
function resolveSettings(
  options?: ResolveSettingsOptions
): Promise<ResolvedSettings>;
```

<h4 id="parameters-10">
  パラメータ
</h4>

`resolveSettings()` は単一のオプションオブジェクトを受け入れます。すべてのフィールドはオプションです。

| パラメータ                           | 型                                     | デフォルト           | 説明                                                                                                                                                                                                                             |
| :------------------------------ | :------------------------------------ | :-------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `options.cwd`                   | `string`                              | `process.cwd()` | プロジェクトおよびローカル設定を相対的に解決するディレクトリ                                                                                                                                                                                                 |
| `options.settingSources`        | [`SettingSource`](#settingsource)`[]` | すべてのソース         | 読み込むファイルシステムソース。ユーザー、プロジェクト、およびローカル設定をスキップするには `[]` を渡します。管理ポリシー設定はすべての場合に読み込まれます。サーバー管理設定はホストが `serverManagedSettings` を渡すときにそこから取得されるか、そうでない場合は CLI のオンディスクキャッシュから読み取られます。スナップショットはネットワークからそれらをフェッチしません                      |
| `options.managedSettings`       | `Settings`                            | `undefined`     | 埋め込みホストによって提供される制限的なポリシーティア設定。管理者がデプロイした管理ティアが存在する場合、ドロップされます。[`parentSettingsBehavior`](/docs/ja/settings#available-settings) が `"merge"` の場合、そのティアの下でマージされます。`model` などの非制限的なキーは静かにドロップされるため、このオプションは管理ポリシーを厳しくできますが、緩くすることはできません |
| `options.serverManagedSettings` | `Settings`                            | `undefined`     | `/api/claude_code/settings` からのサーバー管理設定ペイロード。非制限的なキーはフィルタリングなしで通過します                                                                                                                                                           |

<h4 id="return-type-resolvedsettings">
  戻り値の型：`ResolvedSettings`
</h4>

`resolveSettings()` は、マージされた設定と各キーに寄与したソースを説明するオブジェクトを返します。

| プロパティ        | 型                                                   | 説明                                     |
| :----------- | :-------------------------------------------------- | :------------------------------------- |
| `effective`  | `Settings`                                          | すべての有効なソースを優先度順に適用した後のマージされた設定         |
| `provenance` | `Partial<Record<keyof Settings, ProvenanceEntry>>`  | `effective` の各トップレベルキーについて、値を提供したソース   |
| `sources`    | `Array<{ source, settings, path?, policyOrigin? }>` | ソースごとの生の設定。最も低い優先度から最も高い優先度の順に並べられています |

<h4 id="example-4">
  例
</h4>

プロジェクトディレクトリの設定を解決し、クリーンアップ期間を制御するソースを出力します。

```typescript theme={null}
import { resolveSettings } from "@anthropic-ai/claude-agent-sdk";

const { effective, provenance } = await resolveSettings({
  cwd: "/path/to/project",
  settingSources: ["user", "project", "local"],
});

console.log(`Cleanup period: ${effective.cleanupPeriodDays} days`);
console.log(`Set by: ${provenance.cleanupPeriodDays?.source}`);
```

<h2 id="types">
  型
</h2>

<h3 id="options">
  `Options`
</h3>

`query()` 関数の設定オブジェクト。

| プロパティ                             | 型                                                                                                        | デフォルト                                  | 説明                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| :-------------------------------- | :------------------------------------------------------------------------------------------------------- | :------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `abortController`                 | `AbortController`                                                                                        | `new AbortController()`                | 操作をキャンセルするためのコントローラー                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `additionalDirectories`           | `string[]`                                                                                               | `[]`                                   | Claude がアクセスできる追加ディレクトリ                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `agent`                           | `string`                                                                                                 | `undefined`                            | メインスレッドのエージェント名。エージェントは `agents` オプションまたは設定で定義される必要があります                                                                                                                                                                                                                                                                                                                                                                                                                |
| `agents`                          | `Record<string, [`AgentDefinition`](#agentdefinition)>`                                                  | `undefined`                            | プログラムでサブエージェントを定義します                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `agentProgressSummaries`          | `boolean`                                                                                                | `false`                                | `true` の場合、サブエージェントの 1 行の進捗サマリーを生成し、`summary` フィールドを介して [`task_progress`](#sdktaskprogressmessage) イベントで転送します。フォアグラウンドおよびバックグラウンドサブエージェントに適用されます                                                                                                                                                                                                                                                                                                                        |
| `allowDangerouslySkipPermissions` | `boolean`                                                                                                | `false`                                | 権限のバイパスを有効にします。`permissionMode: 'bypassPermissions'` を使用する場合に必須です                                                                                                                                                                                                                                                                                                                                                                                                       |
| `allowedTools`                    | `string[]`                                                                                               | `[]`                                   | プロンプトなしで自動承認するツール。これは Claude をこれらのツールのみに制限しません。リストされていないツールは `permissionMode` と `canUseTool` にフォールスルーします。ツールをブロックするには `disallowedTools` を使用します。[権限](/docs/ja/agent-sdk/permissions#allow-and-deny-rules) を参照してください                                                                                                                                                                                                                                                           |
| `betas`                           | [`SdkBeta`](#sdkbeta)`[]`                                                                                | `[]`                                   | ベータ機能を有効にします                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `canUseTool`                      | [`CanUseTool`](#canusetool)                                                                              | `undefined`                            | カスタム権限関数。[権限フロー](/docs/ja/agent-sdk/permissions#how-permissions-are-evaluated) がプロンプトにフォールスルーする場合にのみ呼び出されます。`allowedTools`、許可ルール、または `permissionMode` によって自動承認されたツール呼び出しに対しては呼び出されません。`AskUserQuestion`、コネクタツール [組織が `ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools)、および [`requiresUserInteraction`](/docs/ja/mcp#require-approval-for-a-specific-tool) とマークされた MCP ツールは、許可ルールで許可されていても到達します。`dontAsk` モードではこれらは代わりに拒否されます。詳細は [`CanUseTool`](#canusetool) を参照してください |
| `continue`                        | `boolean`                                                                                                | `false`                                | 最新の会話を続けます                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `cwd`                             | `string`                                                                                                 | `process.cwd()`                        | 現在の作業ディレクトリ                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `debug`                           | `boolean`                                                                                                | `false`                                | Claude Code プロセスのデバッグモードを有効にします                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `debugFile`                       | `string`                                                                                                 | `undefined`                            | デバッグログを特定のファイルパスに書き込みます。暗黙的にデバッグモードを有効にします                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `disallowedTools`                 | `string[]`                                                                                               | `[]`                                   | 拒否するツール。`Bash` などの単純な名前はツールを Claude のコンテキストから削除します。`Bash(rm *)` などのスコープ付きルールはツールを利用可能なままにし、`bypassPermissions` を含むすべての権限モードで一致する呼び出しを拒否します。[権限](/docs/ja/agent-sdk/permissions#allow-and-deny-rules) を参照してください                                                                                                                                                                                                                                                               |
| `effort`                          | `'low' \| 'medium' \| 'high' \| 'xhigh' \| 'max'`                                                        | モデルのデフォルト                              | Claude がその応答にどれだけの努力を費やすかを制御します。適応的思考と連携して思考の深さをガイドします。[努力レベルを調整](/docs/ja/model-config#adjust-effort-level) を参照してください                                                                                                                                                                                                                                                                                                                                                       |
| `enableFileCheckpointing`         | `boolean`                                                                                                | `false`                                | ファイル変更追跡を有効にして巻き戻します。[ファイルチェックポイント](/docs/ja/agent-sdk/file-checkpointing) を参照してください                                                                                                                                                                                                                                                                                                                                                                                         |
| `env`                             | `Record<string, string \| undefined>`                                                                    | `process.env`                          | 環境変数。設定すると、このオプションは `process.env` とマージする代わりに、サブプロセス環境を置き換えるため、継承された `PATH` などの変数を保つには `{ ...process.env, YOUR_VAR: 'value' }` を渡します。[遅いまたは停止した API レスポンスを処理](#handle-slow-or-stalled-api-responses) でこのパターンの例を参照してください。また、[環境変数](/docs/ja/env-vars) で基になる CLI が読み取る変数を参照してください。User-Agent ヘッダーでアプリを識別するには `CLAUDE_AGENT_SDK_CLIENT_APP` を設定します                                                                                                                               |
| `executable`                      | `'bun' \| 'deno' \| 'node'`                                                                              | 自動検出                                   | 使用する JavaScript ランタイム                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `executableArgs`                  | `string[]`                                                                                               | `[]`                                   | 実行可能ファイルに渡す引数                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `extraArgs`                       | `Record<string, string \| null>`                                                                         | `{}`                                   | 追加の引数                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `fallbackModel`                   | `string`                                                                                                 | `undefined`                            | プライマリが失敗した場合に使用するモデル                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `forkSession`                     | `boolean`                                                                                                | `false`                                | `resume` で再開するときに、元のセッション ID を続行する代わりに新しいセッション ID にフォークします                                                                                                                                                                                                                                                                                                                                                                                                              |
| `forwardSubagentText`             | `boolean`                                                                                                | `false`                                | サブエージェントのテキストと思考ブロックを `parent_tool_use_id` が設定されたアシスタントおよびユーザーメッセージとして転送し、コンシューマーがネストされたトランスクリプトをレンダリングできるようにします。デフォルトでは、サブエージェントからの `tool_use` および `tool_result` ブロックのみが発行されます                                                                                                                                                                                                                                                                                         |
| `hooks`                           | `Partial<Record<`[`HookEvent`](#hookevent)`, `[`HookCallbackMatcher`](#hookcallbackmatcher)`[]>>`        | `{}`                                   | イベントのフックコールバック                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `includeHookEvents`               | `boolean`                                                                                                | `false`                                | フックライフサイクルイベントをメッセージストリームに [`SDKHookStartedMessage`](#sdkhookstartedmessage)、[`SDKHookProgressMessage`](#sdkhookprogressmessage)、[`SDKHookResponseMessage`](#sdkhookresponsemessage) として含めます。`SessionStart` および `Setup` フックのライフサイクルイベントは常に含まれており、このオプションは不要です                                                                                                                                                                                                           |
| `includePartialMessages`          | `boolean`                                                                                                | `false`                                | 部分的なメッセージイベントを含めます                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `loadTimeoutMs`                   | `number`                                                                                                 | `60000`                                | *アルファ版。* 再開の具体化中に各 `sessionStore.load()` および `sessionStore.listSubkeys()` 呼び出しのタイムアウト（ミリ秒単位）。アダプターがこのウィンドウ内で解決しない場合、クエリはハングする代わりに失敗します。`sessionStore` が設定されていない場合は無視されます                                                                                                                                                                                                                                                                                                |
| `managedSettings`                 | `Settings`                                                                                               | `undefined`                            | スポーニング親プロセスによって提供されるポリシーティア設定。マシンに IT 制御の管理設定ティアが既に存在する場合は削除されます。ただし、その管理者が `parentSettingsBehavior: 'merge'` でオプトインしない限り。関係なく制限的なキーのみにフィルタリングされます                                                                                                                                                                                                                                                                                                                      |
| `maxBudgetUsd`                    | `number`                                                                                                 | `undefined`                            | クライアント側のコスト推定がこの USD 値に達したときにクエリを停止します。`total_cost_usd` と同じ推定と比較されます。[コストと使用状況を追跡](/docs/ja/agent-sdk/cost-tracking) で精度の注意事項を参照してください                                                                                                                                                                                                                                                                                                                                       |
| `maxThinkingTokens`               | `number`                                                                                                 | `undefined`                            | *非推奨：* 代わりに `thinking` を使用してください。思考プロセスの最大トークン数                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `maxTurns`                        | `number`                                                                                                 | `undefined`                            | 最大 agentic ターン数（ツール使用ラウンドトリップ）                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `mcpServers`                      | `Record<string, [`McpServerConfig`](#mcpserverconfig)>`                                                  | `{}`                                   | MCP サーバー設定                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `model`                           | `string`                                                                                                 | CLI からのデフォルト                           | Claude モデルエイリアスまたは完全なモデル名。[受け入れられた値とプロバイダー固有の ID](/docs/ja/model-config#available-models) を参照してください                                                                                                                                                                                                                                                                                                                                                                          |
| `onElicitation`                   | `(request: ElicitationRequest, options: { signal: AbortSignal }) => Promise<ElicitationResult>`          | `undefined`                            | MCP エリシテーションリクエストを処理するためのコールバック。MCP サーバーがユーザー入力をリクエストし、フックがそれを最初に処理しない場合に呼び出されます。提供されない場合、未処理のエリシテーションリクエストは自動的に拒否されます                                                                                                                                                                                                                                                                                                                                                  |
| `outputFormat`                    | `{ type: 'json_schema', schema: JSONSchema }`                                                            | `undefined`                            | エージェント結果の出力形式を定義します。詳細は [構造化出力](/docs/ja/agent-sdk/structured-outputs) を参照してください                                                                                                                                                                                                                                                                                                                                                                                             |
| `outputStyle`                     | `string`                                                                                                 | `undefined`                            | `Options` フィールドではありません。インライン [`settings`](/docs/ja/settings) オブジェクトまたは設定ファイルで `outputStyle` を設定してください。[出力スタイルをアクティブにする](/docs/ja/agent-sdk/modifying-system-prompts#activate-an-output-style) を参照してください                                                                                                                                                                                                                                                                           |
| `pathToClaudeCodeExecutable`      | `string`                                                                                                 | バンドルされたネイティブバイナリから自動解決                 | Claude Code 実行可能ファイルへのパス。インストール中にオプション依存関係がスキップされた場合、またはプラットフォームがサポートされているセットにない場合にのみ必要です                                                                                                                                                                                                                                                                                                                                                                               |
| `permissionMode`                  | [`PermissionMode`](#permissionmode)                                                                      | `'default'`                            | セッションの権限モード                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `permissionPromptToolName`        | `string`                                                                                                 | `undefined`                            | 権限プロンプト用の MCP ツール名                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `persistSession`                  | `boolean`                                                                                                | `true`                                 | `false` の場合、セッション永続化をディスクに無効にします。セッションは後で再開できません                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `planModeInstructions`            | `string`                                                                                                 | `undefined`                            | プランモードのカスタムワークフロー指示。`permissionMode` が `'plan'` の場合、この文字列はデフォルトのプランモードワークフロー本体を置き換えます。CLI は引き続き読み取り専用強制プリアンブルと ExitPlanMode プロトコルフッターでラップします                                                                                                                                                                                                                                                                                                                            |
| `plugins`                         | [`SdkPluginConfig`](#sdkpluginconfig)`[]`                                                                | `[]`                                   | ローカルパスからカスタムプラグインをロードします。詳細は [プラグイン](/docs/ja/agent-sdk/plugins) を参照してください                                                                                                                                                                                                                                                                                                                                                                                                   |
| `promptSuggestions`               | `boolean`                                                                                                | `false`                                | プロンプト提案を有効にします。各ターン後に予測される次のユーザープロンプトを含む `prompt_suggestion` メッセージを発行します                                                                                                                                                                                                                                                                                                                                                                                                |
| `resume`                          | `string`                                                                                                 | `undefined`                            | 再開するセッション ID                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `resumeSessionAt`                 | `string`                                                                                                 | `undefined`                            | 特定のメッセージ UUID でセッションを再開します                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `sandbox`                         | [`SandboxSettings`](#sandboxsettings)                                                                    | `undefined`                            | サンドボックス動作をプログラムで設定します。詳細は [サンドボックス設定](#sandboxsettings) を参照してください                                                                                                                                                                                                                                                                                                                                                                                                       |
| `sessionId`                       | `string`                                                                                                 | 自動生成                                   | 自動生成する代わりに、セッションに特定の UUID を使用します                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `sessionStore`                    | [`SessionStore`](/docs/ja/agent-sdk/session-storage#the-sessionstore-interface)                               | `undefined`                            | セッショントランスクリプトを外部バックエンドにミラーリングして、任意のホストがそれらを再開できるようにします。[セッションを外部ストレージに永続化](/docs/ja/agent-sdk/session-storage) を参照してください                                                                                                                                                                                                                                                                                                                                                     |
| `sessionStoreFlush`               | `'batched' \| 'eager'`                                                                                   | `'batched'`                            | *アルファ版。* `sessionStore` のフラッシュモード。`sessionStore` が設定されていない場合は無視されます                                                                                                                                                                                                                                                                                                                                                                                                     |
| `settings`                        | `string \| Settings`                                                                                     | `undefined`                            | インライン [設定](/docs/ja/settings) オブジェクトまたは設定ファイルへのパス。[優先順位](/docs/ja/settings#settings-precedence) のフラグ設定レイヤーを入力します。[`applyFlagSettings()`](#applyflagsettings) でランタイムに変更します                                                                                                                                                                                                                                                                                                         |
| `settingSources`                  | [`SettingSource`](#settingsource)`[]`                                                                    | CLI デフォルト（すべてのソース）                     | ロードするファイルシステム設定を制御します。ユーザー、プロジェクト、ローカル設定を無効にするには `[]` を渡します。[エンドポイント管理ポリシー](/docs/ja/settings#settings-files) は関係なくロードされます。サーバー管理設定は、[適格な設定](/docs/ja/server-managed-settings#platform-availability) で組織認証情報を使用してセッションが認証されるときにフェッチされます。[Claude Code 機能を使用](/docs/ja/agent-sdk/claude-code-features#what-settingsources-does-not-control) を参照してください                                                                                                                                    |
| `skills`                          | `string[] \| 'all'`                                                                                      | `undefined`                            | セッションで利用可能なスキル。すべての検出されたスキルを有効にするには `'all'` を渡すか、スキル名のリストを渡します。設定すると、SDK は `allowedTools` に `'Skill'` を含めていなくても Skill ツールを自動的に追加します。`tools` も渡す場合は、そのリストに `'Skill'` を含めます。[スキル](/docs/ja/agent-sdk/skills) を参照してください                                                                                                                                                                                                                                                         |
| `spawnClaudeCodeProcess`          | `(options: SpawnOptions) => SpawnedProcess`                                                              | `undefined`                            | Claude Code プロセスをスポーンするカスタム関数。VM、コンテナ、またはリモート環境で Claude Code を実行するために使用します                                                                                                                                                                                                                                                                                                                                                                                              |
| `stderr`                          | `(data: string) => void`                                                                                 | `undefined`                            | stderr 出力のコールバック                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `strictMcpConfig`                 | `boolean`                                                                                                | `false`                                | `mcpServers` で渡されたサーバーのみを使用し、プロジェクト `.mcp.json`、ユーザー設定、プラグイン提供の MCP サーバー、および [claude.ai コネクタ](/docs/ja/mcp#use-mcp-servers-from-claude-ai) を無視します                                                                                                                                                                                                                                                                                                                            |
| `systemPrompt`                    | `string \| { type: 'preset'; preset: 'claude_code'; append?: string; excludeDynamicSections?: boolean }` | `undefined`（最小限のプロンプト）                 | システムプロンプト設定。カスタムプロンプト用の文字列を渡すか、Claude Code のシステムプロンプトを使用するには `{ type: 'preset', preset: 'claude_code' }` を渡します。プリセットオブジェクト形式を使用する場合、追加の指示で拡張するには `append` を追加し、[マシン全体でプロンプトキャッシュの再利用を改善](/docs/ja/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines) するためにセッションごとのコンテキストを最初のユーザーメッセージに移動するには `excludeDynamicSections: true` を設定します                                                                                                         |
| `taskBudget`                      | `{ total: number }`                                                                                      | `undefined`                            | *アルファ版。* API サイドのタスク予算（トークン単位）。設定すると、モデルは残りのトークン予算を知らされるため、ツール使用のペースを調整し、制限前にラップアップできます                                                                                                                                                                                                                                                                                                                                                                                 |
| `thinking`                        | [`ThinkingConfig`](#thinkingconfig)                                                                      | サポートされているモデルの場合 `{ type: 'adaptive' }` | Claude の思考/推論動作を制御します。オプションについては [`ThinkingConfig`](#thinkingconfig) を参照してください                                                                                                                                                                                                                                                                                                                                                                                          |
| `title`                           | `string`                                                                                                 | `undefined`                            | セッションの表示タイトル。`resume` または `continue` を介して再開する場合、再開されたセッションの永続化されたタイトルが優先されます。既存のセッションを再タイトルするには [`renameSession()`](#renamesession) を使用してください                                                                                                                                                                                                                                                                                                                           |
| `toolAliases`                     | `Record<string, string>`                                                                                 | `undefined`                            | 組み込みツール名を MCP ツール名にマップして、Claude が組み込みの代わりに MCP 実装を呼び出すようにします。例えば、`{ Bash: 'mcp__workspace__bash' }`                                                                                                                                                                                                                                                                                                                                                                     |
| `toolConfig`                      | [`ToolConfig`](#toolconfig)                                                                              | `undefined`                            | 組み込みツール動作の設定。詳細は [`ToolConfig`](#toolconfig) を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `tools`                           | `string[] \| { type: 'preset'; preset: 'claude_code' }`                                                  | `undefined`                            | ツール設定。ツール名の配列を渡すか、Claude Code のデフォルトツールを取得するにはプリセットを使用します                                                                                                                                                                                                                                                                                                                                                                                                               |

<h4 id="handle-slow-or-stalled-api-responses">
  遅いまたは停止した API レスポンスを処理
</h4>

CLI サブプロセスは、API タイムアウトと停止検出を制御するいくつかの環境変数を読み取ります。`env` オプションを通じてそれらを渡します：

```typescript theme={null}
const result = query({
  prompt: "Analyze this code",
  options: {
    env: {
      ...process.env,
      API_TIMEOUT_MS: "120000",
      CLAUDE_CODE_MAX_RETRIES: "2",
      CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS: "120000",
    },
  },
});
```

* `API_TIMEOUT_MS`：Anthropic クライアントのリクエストごとのタイムアウト（ミリ秒単位）。デフォルト `600000`。メインループとすべてのサブエージェントに適用されます。
* `CLAUDE_CODE_MAX_RETRIES`：最大 API リトライ数。デフォルト `10`、上限 `15`。各リトライは独自の `API_TIMEOUT_MS` ウィンドウを取得するため、最悪の場合の経過時間は約 `API_TIMEOUT_MS × (CLAUDE_CODE_MAX_RETRIES + 1)` にバックオフを加えたものです。無人実行で長い停止を待つ必要がある場合は、`CLAUDE_CODE_RETRY_WATCHDOG=1` を設定して容量エラーを無限に再試行します。Claude Code v2.1.199 以降では、他の一時的なエラーのデフォルトを `300` に引き上げ、この変数の上限を削除します。
* `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`：`run_in_background` で起動されたサブエージェントの停止ウォッチドッグ。デフォルト `600000`。各ストリームイベントでリセットされます。停止時にサブエージェントを中止し、タスクを失敗とマークし、部分的な結果を含むエラーを親に表示します。同期サブエージェントには適用されません。
* `CLAUDE_ENABLE_STREAM_WATCHDOG` と `CLAUDE_STREAM_IDLE_TIMEOUT_MS`：ヘッダーが到着したがレスポンスボディがストリーミングを停止したときにリクエストを中止します。ウォッチドッグはすべてのプロバイダーでデフォルトでオンになっています。`CLAUDE_ENABLE_STREAM_WATCHDOG=0` で無効にします。`CLAUDE_STREAM_IDLE_TIMEOUT_MS` はデフォルトで `300000` で、その最小値にクランプされます。中止されたリクエストは通常のリトライパスを通ります。

<h3 id="query-object">
  `Query` オブジェクト
</h3>

`query()` 関数によって返されるインターフェース。

```typescript theme={null}
interface Query extends AsyncGenerator<SDKMessage, void> {
  interrupt(): Promise<SDKControlInterruptResponse | undefined>;
  rewindFiles(
    userMessageId: string,
    options?: { dryRun?: boolean }
  ): Promise<RewindFilesResult>;
  setPermissionMode(mode: PermissionMode): Promise<void>;
  setModel(model?: string): Promise<void>;
  setMaxThinkingTokens(maxThinkingTokens: number | null): Promise<void>;
  applyFlagSettings(settings: { [K in keyof Settings]?: Settings[K] | null }): Promise<void>;
  initializationResult(): Promise<SDKControlInitializeResponse>;
  reinitialize(): Promise<SDKControlInitializeResponse>;
  supportedCommands(): Promise<SlashCommand[]>;
  supportedModels(): Promise<ModelInfo[]>;
  supportedAgents(): Promise<AgentInfo[]>;
  mcpServerStatus(): Promise<McpServerStatus[]>;
  accountInfo(): Promise<AccountInfo>;
  reconnectMcpServer(serverName: string): Promise<void>;
  toggleMcpServer(serverName: string, enabled: boolean): Promise<void>;
  setMcpServers(servers: Record<string, McpServerConfig>): Promise<McpSetServersResult>;
  streamInput(stream: AsyncIterable<SDKUserMessage>): Promise<void>;
  stopTask(taskId: string): Promise<void>;
  close(): void;
}
```

<h4 id="methods">
  メソッド
</h4>

| メソッド                                   | 説明                                                                                                                                                                                                                                                                         |
| :------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `interrupt()`                          | クエリを中断します。ストリーミング入力モードでのみ利用可能です。CLI が [`SDKSystemMessage.capabilities`](#sdksystemmessage) で `interrupt_receipt_v1` 機能をアドバタイズする場合、中断を生き残るキューに入れられたメッセージをリストする [`SDKControlInterruptResponse`](#sdkcontrolinterruptresponse) で解決します。v2.1.205 より前の CLI では `undefined` で解決します |
| `rewindFiles(userMessageId, options?)` | ファイルを指定されたユーザーメッセージの状態に復元します。`{ dryRun: true }` を渡して変更をプレビューします。`enableFileCheckpointing: true` が必須です。[ファイルチェックポイント](/docs/ja/agent-sdk/file-checkpointing) を参照してください                                                                                                           |
| `setPermissionMode()`                  | 権限モードを変更します（ストリーミング入力モードでのみ利用可能）                                                                                                                                                                                                                                           |
| `setModel()`                           | モデルを変更します（ストリーミング入力モードでのみ利用可能）                                                                                                                                                                                                                                             |
| `setMaxThinkingTokens()`               | *非推奨：* 代わりに `thinking` オプションを使用してください。最大思考トークン数を変更します。`null` を渡すと、思考をセッションのデフォルトにリセットします。ミッドセッションオーバーライドはクリアされ、思考が無効になっているセッションでは思考は無効のままです                                                                                                                                |
| `applyFlagSettings(settings)`          | ランタイムにセッションのフラグ設定レイヤーに設定をマージします（ストリーミング入力モードでのみ利用可能）。[`applyFlagSettings()`](#applyflagsettings) を参照してください                                                                                                                                                                 |
| `initializationResult()`               | サポートされているコマンド、モデル、アカウント情報、出力スタイル設定を含む完全な初期化結果を返します                                                                                                                                                                                                                         |
| `reinitialize()`                       | 実行中の CLI に `initialize` コントロールリクエストを再送信し、キャッシュされた最初の接続結果の代わりに新しい結果を返します。トランスポートギャップ後（切断後のセッションへの再接続など）に使用して、保留中の権限リクエストが `canUseTool` コールバックに再度到達するようにします。リクエスト ID ごとにコールバックをべき等にしてください。応答が失われたリクエストは再度ディスパッチされるためです。Claude Code v2.1.195 以降が必要です                          |
| `supportedCommands()`                  | 利用可能なスラッシュコマンドを返します                                                                                                                                                                                                                                                        |
| `supportedModels()`                    | 表示情報を含む利用可能なモデルを返します                                                                                                                                                                                                                                                       |
| `supportedAgents()`                    | 利用可能なサブエージェントを [`AgentInfo`](#agentinfo)`[]` として返します                                                                                                                                                                                                                       |
| `mcpServerStatus()`                    | 接続された MCP サーバーのステータスを返します                                                                                                                                                                                                                                                  |
| `accountInfo()`                        | アカウント情報を返します                                                                                                                                                                                                                                                               |
| `reconnectMcpServer(serverName)`       | 名前で MCP サーバーを再接続します                                                                                                                                                                                                                                                        |
| `toggleMcpServer(serverName, enabled)` | 名前で MCP サーバーを有効または無効にします                                                                                                                                                                                                                                                   |
| `setMcpServers(servers)`               | このセッションの MCP サーバーセットを動的に置き換えます。追加、削除、エラーが発生したサーバーに関する情報を返します                                                                                                                                                                                                               |
| `streamInput(stream)`                  | マルチターン会話のためにクエリに入力メッセージをストリーミングします                                                                                                                                                                                                                                         |
| `stopTask(taskId)`                     | ID で実行中のバックグラウンドタスクを停止します                                                                                                                                                                                                                                                  |
| `close()`                              | クエリを閉じて、基になるプロセスを終了します。クエリを強制的に終了し、すべてのリソースをクリーンアップします                                                                                                                                                                                                                     |

<h4 id="applyflagsettings">
  `applyFlagSettings()`
</h4>

実行中のセッションで任意の [設定](/docs/ja/settings) を変更します。クエリを再開せずに変更します。エージェントが信頼できない入力を読み取った後に `permissions` を厳しくするなど、専用セッターがない設定を変更する必要がある場合に使用します。`setModel()` と `setPermissionMode()` はこれら 2 つのキーの専用セッターです。`applyFlagSettings()` は、設定キーの任意のサブセットを受け入れる一般的な形式であり、ここで `model` を渡すことは `setModel()` と同じように動作します。

ミッドセッションで効果を発揮するキーのみ：

* **次のターンで適用される**：`model`、`effortLevel`、`ultracode`、`permissions`、`hooks`、`skillOverrides`、`fastMode`、`agent`。`agent` を切り替えると、そのエージェントのモデルオーバーライド、フック、システムプロンプトも次のターンで適用されます。
* **ミッドセッションで効果なし**：システムプロンプトオプション。これらはスタートアップ時に 1 回解決されるため、実行中のセッションは呼び出しが成功しても元の値を保持します。それらを変更するには、新しいセッションを開始してください。

`effortLevel` は [努力レベル](/docs/ja/model-config#adjust-effort-level) 名を受け入れます。また、`"ultracode"` も受け入れます。これはセッションを `xhigh` 努力で実行し、[ultracode](/docs/ja/workflows#let-claude-decide-with-ultracode) をオンにします。`Settings` 型はその値なしで `effortLevel` を宣言しているため、TypeScript では同等の `{ ultracode: true }` を渡します。`ultracode` 値には Claude Code v2.1.203 以降が必要であり、設定ファイルの `effortLevel` キーではなく、`applyFlagSettings()` によってのみ受け入れられます。

値はフラグ設定レイヤーに書き込まれます。これは、`query()` のインライン `settings` オプションがスタートアップ時に入力するのと同じレイヤーです。フラグ設定は [設定優先順位](/docs/ja/settings#settings-precedence) の上部付近に位置します。ユーザー、プロジェクト、ローカル設定をオーバーライドし、管理ポリシー設定のみがそれらをオーバーライドできます。これは、[優先順位セクション](#settings-precedence) がプログラム的なオプションと呼ぶのと同じティアです。

連続した呼び出しは、トップレベルキーを浅くマージします。`{ permissions: {...} }` を含む 2 番目の呼び出しは、前の呼び出しから `permissions` オブジェクト全体を置き換えます。深くマージするのではなく。フラグレイヤーからキーをクリアして、より低い優先度のソースにフォールバックするには、そのキーに `null` を渡します。`undefined` を渡すと、JSON シリアル化がそれをドロップするため、効果がありません。

ストリーミング入力モードでのみ利用可能です。これは `setModel()` と `setPermissionMode()` と同じ制約です。

以下の例は、セッション中にアクティブなモデルを切り替えてから、オーバーライドをクリアして、ユーザーまたはプロジェクト設定が指定するモデルにフォールバックします。

```typescript theme={null}
const q = query({ prompt: messageStream });

// セッションの残りの部分のモデルをオーバーライド
await q.applyFlagSettings({ model: "claude-opus-4-6" });

// 後で：オーバーライドをクリアして、より低い優先度の設定にフォールバック
await q.applyFlagSettings({ model: null });
```

<Note>
  `applyFlagSettings()` は TypeScript のみです。Python SDK は同等のメソッドを公開していません。
</Note>

<h3 id="warmquery">
  `WarmQuery`
</h3>

[`startup()`](#startup) によって返されるハンドル。サブプロセスは既にスポーンされ、初期化されているため、このハンドルで `query()` を呼び出すと、スタートアップレイテンシーなしで準備ができているプロセスにプロンプトを直接書き込みます。

```typescript theme={null}
interface WarmQuery extends AsyncDisposable {
  query(prompt: string | AsyncIterable<SDKUserMessage>): Query;
  close(): void;
}
```

<h4 id="methods-2">
  メソッド
</h4>

| メソッド            | 説明                                                                                          |
| :-------------- | :------------------------------------------------------------------------------------------ |
| `query(prompt)` | プリウォーミングされたサブプロセスにプロンプトを送信し、[`Query`](#query-object) を返します。`WarmQuery` ごとに 1 回だけ呼び出すことができます |
| `close()`       | プロンプトを送信せずにサブプロセスを閉じます。不要になったウォームクエリを破棄するために使用します                                           |

`WarmQuery` は `AsyncDisposable` を実装しているため、自動クリーンアップのために `await using` で使用できます。

<h3 id="sdkcontrolinitializeresponse">
  `SDKControlInitializeResponse`
</h3>

`initializationResult()` の戻り値の型。セッション初期化データを含みます。

```typescript theme={null}
type SDKControlInitializeResponse = {
  commands: SlashCommand[];
  agents: AgentInfo[];
  output_style: string;
  available_output_styles: string[];
  models: ModelInfo[];
  account: AccountInfo;
  fast_mode_state?: "off" | "cooldown" | "on";
};
```

クライアントが既に実行中のセッションに `initialize` を送信する場合、コントロールレスポンスラッパーは、オプションの `pending_permission_requests` 配列も含みます。フィールドはレスポンスラッパー自体にあり、上記の `SDKControlInitializeResponse` ペイロードにはありません。各エントリは、セッションが実行中にストリーミングする権限リクエストと同じ `{ type: "control_request", request_id, request }` 形状を持つ完全な `control_request` メッセージです。

これらは、クライアントが接続する前に発行され、まだ返信を待っているリクエストです。SDK はこの配列を読み取り、各エントリを [`canUseTool`](#canusetool) コールバックにディスパッチします。これは、トランスポートギャップ後に [`reinitialize()`](#query-object) がトリガーする再配信と同じです。繰り返されたリクエスト ID をべき等に処理してください。接続が切断される前にコールバックが既に受け取ったリクエストを繰り返すエントリが存在する可能性があるためです。

<h3 id="sdkcontrolinterruptresponse">
  `SDKControlInterruptResponse`
</h3>

中断レシート：[`interrupt()`](#query-object) が [`SDKSystemMessage.capabilities`](#sdksystemmessage) で `interrupt_receipt_v1` 機能をアドバタイズする CLI で解決する値。Claude Code v2.1.205 以降が必要です。以前の CLI は中断に空の成功ペイロードで応答するため、`interrupt()` は `undefined` で解決します。

```typescript theme={null}
type SDKControlInterruptResponse = {
  still_queued: string[];
};
```

`still_queued` は中断を生き残るユーザーメッセージの UUID をリストします：キューに残っているメッセージ、および次のターンのためにすでにデキューされたが、まだ中止によって到達できないバッチ。各メッセージは、中断後に独自のターンとして実行されます。最初にキャンセルしない限り。レシートを使用して、何かを再送信するかどうかを決定します。既にリストされているメッセージを再送信すると、重複したターンが生成されます。

これらの注意事項でリストを解釈します：

* UUID が付いてエンキューされたメッセージのみが表示されます。空の配列は、他に何も実行されないことを意味しません。
* メインスレッドメッセージのみがリストされます。サブエージェントにアドレス指定されたメッセージはスコープ外です。
* リストには、クライアントが送信しなかった UUID（[スケジュール済みタスク](/docs/ja/scheduled-tasks) トリガーなど）が含まれる場合があります。認識しない UUID は、エラーとして扱う代わりに無視してください。

レシートは中断が処理される瞬間に取得されたスナップショットであり、クリーンな中断では、中断されたターンの [`SDKResultMessage`](#sdkresultmessage) の前に到着します。その結果の後にキューを検査するのではなく、レシートを読んでください。ループは次のキューに入れられたターンをすぐに開始するため、結果の後に検査するキューは既に変更されています。

<h3 id="agentdefinition">
  `AgentDefinition`
</h3>

プログラムで定義されたサブエージェントの設定。

```typescript theme={null}
type AgentDefinition = {
  description: string;
  tools?: string[];
  disallowedTools?: string[];
  prompt: string;
  model?: string;
  mcpServers?: AgentMcpServerSpec[];
  skills?: string[];
  initialPrompt?: string;
  maxTurns?: number;
  background?: boolean;
  memory?: "user" | "project" | "local";
  effort?: "low" | "medium" | "high" | "xhigh" | "max" | number;
  permissionMode?: PermissionMode;
  criticalSystemReminder_EXPERIMENTAL?: string;
};
```

| フィールド                                 | 必須  | 説明                                                                                                                                                    |
| :------------------------------------ | :-- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `description`                         | はい  | このエージェントをいつ使用するかの自然言語説明                                                                                                                               |
| `tools`                               | いいえ | 許可されたツール名の配列。省略すると、親からすべてのツールを継承します。スキルをエージェントのコンテキストにプリロードするには、`tools` にリストするのではなく `skills` フィールドを使用します                                              |
| `disallowedTools`                     | いいえ | このエージェントに対して明示的に許可しないツール名の配列。MCP サーバーレベルのパターンも受け入れられます：`mcp__server` または `mcp__server__*` はそのサーバーからすべてのツールを削除し、`mcp__*` はすべての MCP ツールをすべてのサーバーから削除します |
| `prompt`                              | はい  | エージェントのシステムプロンプト                                                                                                                                      |
| `model`                               | いいえ | このエージェントのモデルオーバーライド。`'fable'`、`'opus'`、`'sonnet'`、`'haiku'`、`'inherit'` などのエイリアス、または完全なモデル ID を受け入れます。省略または `'inherit'` の場合、メインモデルを使用します              |
| `mcpServers`                          | いいえ | このエージェントの MCP サーバー仕様                                                                                                                                  |
| `skills`                              | いいえ | エージェントコンテキストにプリロードするスキル名の配列                                                                                                                           |
| `initialPrompt`                       | いいえ | このエージェントがメインスレッドエージェントとして実行される場合、最初のユーザーターンとして自動送信されます                                                                                                |
| `maxTurns`                            | いいえ | 停止する前の最大 agentic ターン数（API ラウンドトリップ）                                                                                                                   |
| `background`                          | いいえ | 呼び出されたときにこのエージェントをノンブロッキングバックグラウンドタスクとして実行します                                                                                                         |
| `memory`                              | いいえ | このエージェントのメモリソース：`'user'`、`'project'`、または `'local'`                                                                                                    |
| `effort`                              | いいえ | このエージェントの推論努力レベル。名前付きレベルまたは整数を受け入れます                                                                                                                  |
| `permissionMode`                      | いいえ | このエージェント内のツール実行の権限モード。[`PermissionMode`](#permissionmode) を参照してください                                                                                   |
| `criticalSystemReminder_EXPERIMENTAL` | いいえ | 実験的：システムプロンプトに追加される重要なリマインダー                                                                                                                          |

<h3 id="agentmcpserverspec">
  `AgentMcpServerSpec`
</h3>

サブエージェントで利用可能な MCP サーバーを指定します。サーバー名（親の `mcpServers` 設定からサーバーを参照する文字列）またはインラインサーバー設定レコード（サーバー名を設定にマッピング）です。

```typescript theme={null}
type AgentMcpServerSpec = string | Record<string, McpServerConfigForProcessTransport>;
```

ここで `McpServerConfigForProcessTransport` は `McpStdioServerConfig | McpSSEServerConfig | McpHttpServerConfig | McpSdkServerConfig` です。

<h3 id="settingsource">
  `SettingSource`
</h3>

SDK がどのファイルシステムベースの設定ソースから設定をロードするかを制御します。

```typescript theme={null}
type SettingSource = "user" | "project" | "local";
```

| 値           | 説明                       | 場所                            |
| :---------- | :----------------------- | :---------------------------- |
| `'user'`    | グローバルユーザー設定              | `~/.claude/settings.json`     |
| `'project'` | 共有プロジェクト設定（バージョン管理）      | `.claude/settings.json`       |
| `'local'`   | ローカルプロジェクト設定（gitignored） | `.claude/settings.local.json` |

<h4 id="default-behavior">
  デフォルト動作
</h4>

`settingSources` が省略または `undefined` の場合、`query()` は Claude Code CLI と同じファイルシステム設定をロードします：ユーザー、プロジェクト、ローカル。[エンドポイント管理ポリシー](/docs/ja/settings#settings-files) はすべての場合にロードされます。サーバー管理設定は、[適格な設定](/docs/ja/server-managed-settings#platform-availability) で組織認証情報を使用してセッションが認証されるときにフェッチされます。このオプションに関係なく読み取られる入力については [Claude Code 機能を使用](/docs/ja/agent-sdk/claude-code-features#what-settingsources-does-not-control) を参照してください。

<h4 id="why-use-settingsources">
  settingSources を使用する理由
</h4>

**ファイルシステム設定を無効にする：**

```typescript theme={null}
// ディスクからユーザー、プロジェクト、またはローカル設定をロードしません
const result = query({
  prompt: "Analyze this code",
  options: { settingSources: [] }
});
```

**すべてのファイルシステム設定を明示的にロードする：**

```typescript theme={null}
const result = query({
  prompt: "Analyze this code",
  options: {
    settingSources: ["user", "project", "local"] // すべての設定をロード
  }
});
```

**特定の設定ソースのみをロードする：**

```typescript theme={null}
// プロジェクト設定のみをロードし、ユーザーとローカルを無視します
const result = query({
  prompt: "Run CI checks",
  options: {
    settingSources: ["project"] // .claude/settings.json のみ
  }
});
```

**テストと CI 環境：**

```typescript theme={null}
// ローカル設定を除外することで、CI で一貫した動作を確保します
const result = query({
  prompt: "Run tests",
  options: {
    settingSources: ["project"], // チーム共有設定のみ
    permissionMode: "bypassPermissions"
  }
});
```

**SDK のみのアプリケーション：**

```typescript theme={null}
// すべてをプログラムで定義します。
// ファイルシステム設定ソースをオプトアウトするには [] を渡します。
const result = query({
  prompt: "Review this PR",
  options: {
    settingSources: [],
    agents: {
      /* ... */
    },
    mcpServers: {
      /* ... */
    },
    allowedTools: ["Read", "Grep", "Glob"]
  }
});
```

**CLAUDE.md プロジェクト指示をロードする：**

```typescript theme={null}
// プロジェクト設定をロードして CLAUDE.md ファイルを含めます
const result = query({
  prompt: "Add a new feature following project conventions",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code" // Claude Code のシステムプロンプトを使用
    },
    settingSources: ["project"], // プロジェクトディレクトリから CLAUDE.md をロード
    allowedTools: ["Read", "Write", "Edit"]
  }
});
```

<h4 id="settings-precedence">
  設定の優先順位
</h4>

複数のソースがロードされる場合、設定はこの優先順位（高から低）でマージされます：

1. ローカル設定（`.claude/settings.local.json`）
2. プロジェクト設定（`.claude/settings.json`）
3. ユーザー設定（`~/.claude/settings.json`）

`agents` と `allowedTools` などのプログラム的なオプションは、ユーザー、プロジェクト、ローカルのファイルシステム設定をオーバーライドします。管理ポリシー設定はプログラム的なオプションより優先されます。

<h3 id="permissionmode">
  `PermissionMode`
</h3>

```typescript theme={null}
type PermissionMode =
  | "default" // 標準的な権限動作
  | "acceptEdits" // ファイル編集を自動承認
  | "bypassPermissions" // 権限チェックをバイパス；明示的な質問ルールはまだプロンプトします
  | "plan" // 計画モード - 編集なしで探索
  | "dontAsk" // 権限をプロンプトしない、事前承認されていない場合は拒否
  | "auto"; // モデル分類器を使用して各ツール呼び出しを承認または拒否
```

<h3 id="canusetool">
  `CanUseTool`
</h3>

ツール使用を制御するためのカスタム権限関数型。

関数は、インタラクティブな権限プロンプトの SDK 置き換えです。[権限評価フロー](/docs/ja/agent-sdk/permissions#how-permissions-are-evaluated) がプロンプトに解決される場合にのみ呼び出されます。`allowedTools` エントリ、設定許可ルール、または `acceptEdits` や `bypassPermissions` などの権限モードによって既に承認されたツール呼び出しは、それを呼び出しません。`AskUserQuestion`、[`requiresUserInteraction`](/docs/ja/mcp#require-approval-for-a-specific-tool) とマークされた MCP ツール、および [組織が `ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools) したコネクタツールは、許可ルールが一致する場合でも関数に到達します。`dontAsk` モードではこれらの呼び出しは代わりに拒否されます。すべてのツール呼び出しをゲートするには、代わりに [`PreToolUse` フック](/docs/ja/agent-sdk/hooks) を使用します。

```typescript theme={null}
type CanUseTool = (
  toolName: string,
  input: Record<string, unknown>,
  options: {
    signal: AbortSignal;
    suggestions?: PermissionUpdate[];
    blockedPath?: string;
    decisionReason?: string;
    toolUseID: string;
    agentID?: string;
    requestId: string;
  }
) => Promise<PermissionResult | null>;
```

| オプション            | 型                                           | 説明                                                                                                                                                                                                               |
| :--------------- | :------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `signal`         | `AbortSignal`                               | 操作を中止する必要がある場合にシグナルされます                                                                                                                                                                                          |
| `suggestions`    | [`PermissionUpdate`](#permissionupdate)`[]` | 提案されたパーミッション更新。ユーザーがこのツールに対して再度プロンプトされないようにします。Bash プロンプトには `localSettings` [宛先](#permissionupdatedestination) を含む提案が含まれているため、`updatedPermissions` で返すと、ルールを `.claude/settings.local.json` に書き込み、セッション全体で永続化します。 |
| `blockedPath`    | `string`                                    | 権限リクエストをトリガーしたファイルパス（該当する場合）                                                                                                                                                                                     |
| `decisionReason` | `string`                                    | この権限リクエストがトリガーされた理由を説明します                                                                                                                                                                                        |
| `toolUseID`      | `string`                                    | アシスタントメッセージ内のこの特定のツール呼び出しの一意の識別子                                                                                                                                                                                 |
| `agentID`        | `string`                                    | サブエージェント内で実行している場合、サブエージェントの ID                                                                                                                                                                                  |
| `requestId`      | `string`                                    | `control_request` エンベロープの `request_id`。アプリケーションが送信する `control_response`（署名付き HTTP POST など）は、Claude Code プロセスが返信をリクエストと照合できるようにこの値をエコーする必要があります                                                                   |

コールバックは通常、[`PermissionResult`](#permissionresult) を返すことでリクエストを解決します。これは SDK がそのトランスポートを介して `control_response` として書き込みます。アプリケーションが既にこのリクエストの `control_response` を独自のチャネルを介して送信した場合にのみ `null` を返します。`requestId` をエコーします。その場合、SDK はそのトランスポートへの応答の書き込みをスキップします。他の場合に `null` を返すと、`control_response` が送信されず、権限プロンプトがタイムアウトしないため、ツール呼び出しは無期限にブロックされたままになります。

`requestId` オプションと `null` 戻り値には Claude Code v2.1.199 以降が必要です。

<h3 id="permissionresult">
  `PermissionResult`
</h3>

権限チェックの結果。

```typescript theme={null}
type PermissionResult =
  | {
      behavior: "allow";
      updatedInput?: Record<string, unknown>;
      updatedPermissions?: PermissionUpdate[];
      toolUseID?: string;
    }
  | {
      behavior: "deny";
      message: string;
      interrupt?: boolean;
      toolUseID?: string;
    };
```

<h3 id="toolconfig">
  `ToolConfig`
</h3>

組み込みツール動作の設定。

```typescript theme={null}
type ToolConfig = {
  askUserQuestion?: {
    previewFormat?: "markdown" | "html";
  };
};
```

| フィールド                           | 型                      | 説明                                                                                                                                          |
| :------------------------------ | :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| `askUserQuestion.previewFormat` | `'markdown' \| 'html'` | [`AskUserQuestion`](/docs/ja/agent-sdk/user-input#question-format) オプションの `preview` フィールドにオプトインし、そのコンテンツ形式を設定します。設定されていない場合、Claude はプレビューを発行しません |

<h3 id="mcpserverconfig">
  `McpServerConfig`
</h3>

MCP サーバーの設定。

```typescript theme={null}
type McpServerConfig =
  | McpStdioServerConfig
  | McpSSEServerConfig
  | McpHttpServerConfig
  | McpSdkServerConfigWithInstance;
```

<h4 id="mcpstdioserverconfig">
  `McpStdioServerConfig`
</h4>

```typescript theme={null}
type McpStdioServerConfig = {
  type?: "stdio";
  command: string;
  args?: string[];
  env?: Record<string, string>;
};
```

<h4 id="mcpsseserverconfig">
  `McpSSEServerConfig`
</h4>

```typescript theme={null}
type McpSSEServerConfig = {
  type: "sse";
  url: string;
  headers?: Record<string, string>;
};
```

<h4 id="mcphttpserverconfig">
  `McpHttpServerConfig`
</h4>

```typescript theme={null}
type McpHttpServerConfig = {
  type: "http";
  url: string;
  headers?: Record<string, string>;
};
```

<h4 id="mcpsdkserverconfigwithinstance">
  `McpSdkServerConfigWithInstance`
</h4>

```typescript theme={null}
type McpSdkServerConfigWithInstance = {
  type: "sdk";
  name: string;
  instance: McpServer;
};
```

<h4 id="mcpclaudeaiproxyserverconfig">
  `McpClaudeAIProxyServerConfig`
</h4>

```typescript theme={null}
type McpClaudeAIProxyServerConfig = {
  type: "claudeai-proxy";
  url: string;
  id: string;
};
```

<h3 id="sdkpluginconfig">
  `SdkPluginConfig`
</h3>

SDK でプラグインをロードするための設定。

```typescript theme={null}
type SdkPluginConfig = {
  type: "local";
  path: string;
  skipMcpDiscovery?: boolean;
};
```

| フィールド              | 型         | 説明                                                                                                                                         |
| :----------------- | :-------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `type`             | `'local'` | `'local'` である必要があります（現在ローカルプラグインのみサポート）                                                                                                    |
| `path`             | `string`  | プラグインディレクトリへの絶対パスまたは相対パス                                                                                                                   |
| `skipMcpDiscovery` | `boolean` | `true` の場合、SDK はこのプラグインからスキル、フック、エージェント、コマンドをロードしますが、その `.mcp.json` またはマニフェスト `mcpServers` は読み取りません。アプリケーションがプラグインの MCP 接続を所有している場合に設定します。 |

**例：**

```typescript theme={null}
plugins: [
  { type: "local", path: "./my-plugin" },
  { type: "local", path: "/absolute/path/to/plugin" }
];
```

プラグインの作成と使用に関する完全な情報については、[プラグイン](/docs/ja/agent-sdk/plugins) を参照してください。

<h2 id="message-types">
  メッセージ型
</h2>

<h3 id="sdkmessage">
  `SDKMessage`
</h3>

クエリによって返されるすべての可能なメッセージの共用体型。

```typescript theme={null}
type SDKMessage =
  | SDKAssistantMessage
  | SDKUserMessage
  | SDKUserMessageReplay
  | SDKResultMessage
  | SDKSystemMessage
  | SDKPartialAssistantMessage
  | SDKCompactBoundaryMessage
  | SDKStatusMessage
  | SDKLocalCommandOutputMessage
  | SDKHookStartedMessage
  | SDKHookProgressMessage
  | SDKHookResponseMessage
  | SDKPluginInstallMessage
  | SDKToolProgressMessage
  | SDKAuthStatusMessage
  | SDKTaskNotificationMessage
  | SDKTaskStartedMessage
  | SDKTaskProgressMessage
  | SDKTaskUpdatedMessage
  | SDKBackgroundTasksChangedMessage
  | SDKThinkingTokensMessage
  | SDKSessionStateChangedMessage
  | SDKWorkerShuttingDownMessage
  | SDKCommandsChangedMessage
  | SDKNotificationMessage
  | SDKFilesPersistedEvent
  | SDKToolUseSummaryMessage
  | SDKMemoryRecallMessage
  | SDKRateLimitEvent
  | SDKElicitationCompleteMessage
  | SDKPermissionDeniedMessage
  | SDKPromptSuggestionMessage
  | SDKAPIRetryMessage
  | SDKMirrorErrorMessage
  | SDKInformationalMessage
  | SDKConversationResetMessage;
```

<h3 id="sdkassistantmessage">
  `SDKAssistantMessage`
</h3>

アシスタント応答メッセージ。

```typescript theme={null}
type SDKAssistantMessage = {
  type: "assistant";
  uuid: UUID;
  session_id: string;
  message: BetaMessage; // Anthropic SDK から
  parent_tool_use_id: string | null;
  error?: SDKAssistantMessageError;
};
```

`message` フィールドは Anthropic SDK の [`BetaMessage`](https://platform.claude.com/docs/ja/api/messages/create) です。`id`、`content`、`model`、`stop_reason`、`usage` などのフィールドを含みます。

`SDKAssistantMessageError` は以下のいずれかです：`'authentication_failed'`、`'oauth_org_not_allowed'`、`'billing_error'`、`'rate_limit'`、`'overloaded'`、`'invalid_request'`、`'model_not_found'`、`'server_error'`、`'max_output_tokens'`、または `'unknown'`。`'model_not_found'` は、選択されたモデルが存在しないか、アカウントまたはデプロイメントで利用できないことを意味します。`'overloaded'` は、API がサーバーが容量に達しているため 529 を返したことを意味し、`'rate_limit'` はクォータに対する 429 とは異なります。

<h3 id="sdkusermessage">
  `SDKUserMessage`
</h3>

ユーザー入力メッセージ。

```typescript theme={null}
type SDKUserMessage = {
  type: "user";
  uuid?: UUID;
  session_id?: string;
  message: MessageParam; // Anthropic SDK から
  parent_tool_use_id: string | null;
  isSynthetic?: boolean;
  shouldQuery?: boolean;
  tool_use_result?: unknown;
  origin?: SDKMessageOrigin;
};
```

`shouldQuery` を `false` に設定して、アシスタントターンをトリガーせずにメッセージをトランスクリプトに追加します。メッセージは保持され、ターンをトリガーする次のユーザーメッセージにマージされます。これを使用して、バンド外で実行したコマンドの出力など、モデル呼び出しを費やさずにコンテキストを注入します。

`tool_result` ブロックを持つメッセージでは、`tool_use_result` はモデルに送信されたテキストではなく、ツールの構造化出力オブジェクトです。その形状は、対応する `tool_use` ブロックで指定されたツールに依存するため、フィールドは `unknown` として型付けされます。組み込みの形状は [ツール出力型](#tool-output-types) の下にリストされています。

`Agent` ツールの場合、`tool_use_result` は [`AgentOutput`](#agent-2) です。`completed` 結果では、`content` はサブエージェントのレポートを保持し、Claude Code が `tool_result` テキストに追加するエージェント ID と使用状況トレーラーは含まれません。そのため、そのテキストを解析する代わりに `tool_use_result` からレンダリングします。

<h3 id="sdkusermessagereplay">
  `SDKUserMessageReplay`
</h3>

必須 UUID を含む再生されたユーザーメッセージ。

```typescript theme={null}
type SDKUserMessageReplay = {
  type: "user";
  uuid: UUID;
  session_id: string;
  message: MessageParam;
  parent_tool_use_id: string | null;
  isSynthetic?: boolean;
  tool_use_result?: unknown;
  origin?: SDKMessageOrigin;
  isReplay: true;
};
```

セッション外から注入されたユーザーターン（[`origin`](#sdkmessageorigin) の種類が `peer` または `channel` であるもの）は、アクティブなターン中に配信されたか、セッションがアイドル状態の間に新しいターンを開始したかに関わらず、ストリームに再生として到達します。v2.1.207 より前では、セッションがアイドル状態の間に配信された注入されたターンはストリーム上にメッセージを生成せず、トランスクリプトを再読み込みするときにのみ表示されました。

<h3 id="sdkresultmessage">
  `SDKResultMessage`
</h3>

最終結果メッセージ。

```typescript theme={null}
type SDKResultMessage =
  | {
      type: "result";
      subtype: "success";
      uuid: UUID;
      session_id: string;
      duration_ms: number;
      duration_api_ms: number;
      is_error: boolean;
      api_error_status?: number | null;
      num_turns: number;
      result: string;
      stop_reason: string | null;
      ttft_ms?: number;
      ttft_stream_ms?: number;
      total_cost_usd: number;
      usage: NonNullableUsage;
      modelUsage: { [modelName: string]: ModelUsage };
      permission_denials: SDKPermissionDenial[];
      structured_output?: unknown;
      deferred_tool_use?: { id: string; name: string; input: Record<string, unknown> };
      terminal_reason?: TerminalReason;
      fast_mode_state?: FastModeState;
      origin?: SDKMessageOrigin;
    }
  | {
      type: "result";
      subtype:
        | "error_max_turns"
        | "error_during_execution"
        | "error_max_budget_usd"
        | "error_max_structured_output_retries";
      uuid: UUID;
      session_id: string;
      duration_ms: number;
      duration_api_ms: number;
      is_error: boolean;
      num_turns: number;
      stop_reason: string | null;
      total_cost_usd: number;
      usage: NonNullableUsage;
      modelUsage: { [modelName: string]: ModelUsage };
      permission_denials: SDKPermissionDenial[];
      errors: string[];
      terminal_reason?: TerminalReason;
      fast_mode_state?: FastModeState;
      origin?: SDKMessageOrigin;
    };
```

結果の複数のフィールドは、`subtype` を超えた診断詳細を提供します：

* `api_error_status`：会話を終了させた API エラーの HTTP ステータスコード。ターンが API エラーなしで終了した場合、存在しないか `null` です。
* `ttft_ms`：最初のトークンまでの時間（ミリ秒）。最初の完全なアシスタントメッセージが到着したときに測定されます。成功の場合のみ存在します。
* `ttft_stream_ms`：最初の `message_start` ストリームイベントまでの時間（ミリ秒）。レスポンスストリームが開くときです。`ttft_ms` より低く、2 つの間のギャップは最初のメッセージをストリーミングするのに費やされた時間です。成功の場合のみ存在します。
* `terminal_reason`：ループが終了した理由。`"completed"`、`"max_turns"`、`"tool_deferred"`、`"aborted_streaming"`、`"aborted_tools"`、`"hook_stopped"`、`"stop_hook_prevented"`、`"background_requested"`、`"blocking_limit"`、`"rapid_refill_breaker"`、`"prompt_too_long"`、`"image_error"`、`"model_error"`、`"api_error"`、`"malformed_tool_use_exhausted"`、`"budget_exhausted"`、`"structured_output_retry_exhausted"`、`"tool_deferred_unavailable"`、または `"turn_setup_failed"` のいずれかです。
* `fast_mode_state`：`"on"`、`"off"`、または `"cooldown"` のいずれかです。

`origin` フィールドは、この結果をトリガーしたユーザーメッセージの [`SDKMessageOrigin`](#sdkmessageorigin) を転送します。バックグラウンドタスクが完了し、SDK が合成フォローアップターンを注入する場合、結果の `SDKResultMessage` は `origin: { kind: "task-notification" }` を持ちます。このフィールドをチェックして、プロンプトに答える結果とバックグラウンドタスクのフォローアップで発行される結果を区別し、後者をルーティングまたは抑制できます。このフィールドは、スタートアップエラーなど、ユーザーターンの前に発行される結果には存在しません。

`PreToolUse` フックが `permissionDecision: "defer"` を返すと、結果は `stop_reason: "tool_deferred"` を持ち、`deferred_tool_use` は保留中のツールの `id`、`name`、`input` を保持します。このフィールドを読んで、独自の UI でリクエストをサーフェスし、同じ `session_id` で再開して続行します。完全なラウンドトリップについては、[ツール呼び出しを後で延期する](/docs/ja/hooks#defer-a-tool-call-for-later)を参照してください。

<h3 id="sdksystemmessage">
  `SDKSystemMessage`
</h3>

システム初期化メッセージ。

```typescript theme={null}
type SDKSystemMessage = {
  type: "system";
  subtype: "init";
  uuid: UUID;
  session_id: string;
  agents?: string[];
  apiKeySource: ApiKeySource;
  betas?: string[];
  claude_code_version: string;
  cwd: string;
  tools: string[];
  mcp_servers: {
    name: string;
    status: string;
  }[];
  model: string;
  permissionMode: PermissionMode;
  slash_commands: string[];
  output_style: string;
  skills: string[];
  plugins: { name: string; path: string }[];
  capabilities?: string[];
};
```

`capabilities` 配列は、この CLI が実装するプロトコル動作に名前を付けるため、`claude_code_version` 文字列を比較する代わりに機能検出を行うことができます。これはオープンセットです：認識しない値は無視し、依存する特定の動作の機能をチェックしてください。このフィールドには Claude Code v2.1.205 以降が必要で、以前の CLI では存在しません。

| 機能                     | 意味                                                                                                                                       |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `interrupt_receipt_v1` | [`interrupt()`](#query-object) は、割り込みを生き残るキューに入れられたメッセージに名前を付ける [`SDKControlInterruptResponse`](#sdkcontrolinterruptresponse) レシートで解決します |

<h3 id="sdkpartialassistantmessage">
  `SDKPartialAssistantMessage`
</h3>

ストリーミング部分メッセージ（`includePartialMessages` が true の場合のみ）。`parent_tool_use_id` フィールドは常に `null` です：ストリームイベントはメインセッションのみに対して発行されます。サブエージェント属性については、`parent_tool_use_id` を持つ完全なメッセージを使用するか、[`forwardSubagentText`](#options) を有効にして、サブエージェントテキストと思考を完全なメッセージとして受け取ります。

```typescript theme={null}
type SDKPartialAssistantMessage = {
  type: "stream_event";
  event: BetaRawMessageStreamEvent; // Anthropic SDK から
  parent_tool_use_id: string | null;
  uuid: UUID;
  session_id: string;
  ttft_ms?: number; // 最初のトークンまでの時間（ミリ秒）。message_start イベントにのみ存在
};
```

<h3 id="sdkcompactboundarymessage">
  `SDKCompactBoundaryMessage`
</h3>

会話圧縮境界を示すメッセージ。

```typescript theme={null}
type SDKCompactBoundaryMessage = {
  type: "system";
  subtype: "compact_boundary";
  uuid: UUID;
  session_id: string;
  compact_metadata: {
    trigger: "manual" | "auto";
    pre_tokens: number;
  };
};
```

<h3 id="sdkinformationalmessage">
  `SDKInformationalMessage`
</h3>

ループによって発行される汎用テキストバナー。エラーではないステータス行、`UserPromptSubmit` フックのブロック理由などのフックフィードバック、およびコマンド出力を含みます。`content` を指定された `level` でプレーンテキストとしてレンダリングします。

```typescript theme={null}
type SDKInformationalMessage = {
  type: "system";
  subtype: "informational";
  content: string;
  level: "info" | "notice" | "suggestion" | "warning";
  tool_use_id?: string;
  prevent_continuation?: boolean;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkworkershuttingdownmessage">
  `SDKWorkerShuttingDownMessage`
</h3>

グレースフルワーカーティアダウン時に発行されるため、リモートクライアントはハートビートタイムアウトを待つ代わりにワーカーが消えた理由を表示できます。`reason` はホスト CLI によって設定される短い snake\_case 文字列です（`"host_exit"` や `"remote_control_disabled"` など）。ライブストリーミング時にのみこれに対応します。再開されたセッションはこのメッセージの過去のインスタンスを再生するため、その場合は無視してください。

```typescript theme={null}
type SDKWorkerShuttingDownMessage = {
  type: "system";
  subtype: "worker_shutting_down";
  reason: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkplugininstallmessage">
  `SDKPluginInstallMessage`
</h3>

プラグインインストール進捗イベント。[`CLAUDE_CODE_SYNC_PLUGIN_INSTALL`](/docs/ja/env-vars) が設定されている場合に発行されるため、Agent SDK アプリケーションは最初のターンの前にマーケットプレイスプラグインのインストールを追跡できます。`started` と `completed` ステータスは全体的なインストールをブラケットします。`installed` と `failed` ステータスは個別のマーケットプレイスをレポートし、`name` を含みます。

```typescript theme={null}
type SDKPluginInstallMessage = {
  type: "system";
  subtype: "plugin_install";
  status: "started" | "installed" | "failed" | "completed";
  name?: string;
  error?: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkpermissiondeniedmessage">
  `SDKPermissionDeniedMessage`
</h3>

権限システムがインタラクティブプロンプトなしでツール呼び出しを自動的に拒否するときに発行されるストリームイベント。これを使用して、その後に続く `is_error` ツール結果のみを観察するのではなく、拒否を UI にリアルタイムでレンダリングします。インタラクティブな質問パスは、[`canUseTool`](#canusetool) コールバックを通じてアプリケーションに別途到達します。`PreToolUse` フックによって発行された拒否は、このイベントを通じてレポートされません。

このイベントには Claude Code v2.1.136 以降が必要です。

```typescript theme={null}
type SDKPermissionDeniedMessage = {
  type: "system";
  subtype: "permission_denied";
  tool_name: string;
  tool_use_id: string;
  agent_id?: string;
  decision_reason_type?: string;
  decision_reason?: string;
  message: string;
  uuid: UUID;
  session_id: string;
};
```

| フィールド                  | 型        | 説明                                                                                  |
| ---------------------- | -------- | ----------------------------------------------------------------------------------- |
| `tool_name`            | `string` | 拒否されたツールの名前                                                                         |
| `tool_use_id`          | `string` | この拒否が答える `tool_use` ブロックの ID                                                        |
| `agent_id`             | `string` | 拒否された呼び出しがサブエージェント内で発生した場合のサブエージェント ID。ホスト側ルーティング用に `can_use_tool` のフィールドをミラーリングします |
| `decision_reason_type` | `string` | 決定したコンポーネントの判別式（`"rule"`、`"mode"`、`"classifier"`、`"asyncAgent"` など）                 |
| `decision_reason`      | `string` | 利用可能な場合、決定したコンポーネントからの人間が読める理由                                                      |
| `message`              | `string` | `tool_result` でモデルに返される拒否メッセージ                                                      |

<h3 id="sdkpermissiondenial">
  `SDKPermissionDenial`
</h3>

拒否されたツール使用に関する情報。

```typescript theme={null}
type SDKPermissionDenial = {
  tool_name: string;
  tool_use_id: string;
  tool_input: Record<string, unknown>;
};
```

<h3 id="sdkmessageorigin">
  `SDKMessageOrigin`
</h3>

ユーザーロールメッセージの出所。これは [`SDKUserMessage`](#sdkusermessage) の `origin` として表示され、対応する [`SDKResultMessage`](#sdkresultmessage) に転送されるため、特定のターンをトリガーしたものを判断できます。

```typescript theme={null}
type SDKMessageOrigin =
  | { kind: "human" }
  | { kind: "channel"; server: string }
  | {
      kind: "peer";
      from: string;
      name?: string;
      senderTaskId?: string;
      body?: string;
    }
  | { kind: "task-notification" }
  | { kind: "coordinator" }
  | { kind: "auto-continuation" };
```

| `kind`              | 意味                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `human`             | エンドユーザーからの直接入力。ユーザーメッセージでは、`origin` が存在しないこともヒューマン入力を意味します。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `channel`           | [チャネル](/docs/ja/channels)に到着するメッセージ。`server` はソース MCP サーバー名です。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `peer`              | 別のエージェントからのメッセージ。プロセス内の [teammate](/docs/ja/agent-teams) が `SendMessage` 経由で `main` に送信する場合、`from` は teammate の名前で、`senderTaskId` はそのタスク ID です。別のローカル Claude Code プロセスなどのクロスセッションピアの場合、`from` は送信者アドレスで、`senderTaskId` は存在しません。`name` と `body` には Claude Code v2.1.205 以降が必要です。`name` は送信者の表示名で、Claude Code によって正規化されます：Unicode 制御、形式、サロゲート、および行または段落区切り文字コードポイントを削除し、結果をトリミングして 64 コードポイントで上限に達し、省略記号を付けます。`body` はピアエンベロープを削除したデコードされたメッセージ本体で、モデルが見るものとバイト単位で正確です。teammate メッセージの場合、`body` は常に存在します。クロスセッションピアの場合、ターンが Claude Code によって形成された正確に 1 つのピアエンベロープである場合にのみ存在します。メッセージテキストを再解析する代わりに、`name` と `body` をレンダリングします。 |
| `task-notification` | バックグラウンドタスク完了後に注入される合成ターン。[`SDKTaskNotificationMessage`](#sdktasknotificationmessage) を参照してください。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `coordinator`       | [エージェントチーム](/docs/ja/agent-teams)のチームコーディネーターからのメッセージ。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `auto-continuation` | セッションが新しいユーザー入力なしで続行するときに注入される合成ターン（コマンド結果がフォローアッププロンプトをトリガーするなど）。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

<h2 id="hook-types">
  フック型
</h2>

フックの使用に関する包括的なガイド、例、一般的なパターンについては、[フックガイド](/docs/ja/agent-sdk/hooks) を参照してください。

<h3 id="hookevent">
  `HookEvent`
</h3>

利用可能なフックイベント。

```typescript theme={null}
type HookEvent =
  | "PreToolUse"
  | "PostToolUse"
  | "PostToolUseFailure"
  | "PostToolBatch"
  | "Notification"
  | "UserPromptSubmit"
  | "SessionStart"
  | "SessionEnd"
  | "Stop"
  | "SubagentStart"
  | "SubagentStop"
  | "PreCompact"
  | "PermissionRequest"
  | "Setup"
  | "TeammateIdle"
  | "TaskCompleted"
  | "ConfigChange"
  | "WorktreeCreate"
  | "WorktreeRemove"
  | "MessageDisplay";
```

<h3 id="hookcallback">
  `HookCallback`
</h3>

フックコールバック関数型。

```typescript theme={null}
type HookCallback = (
  input: HookInput, // すべてのフック入力型の共用体
  toolUseID: string | undefined,
  options: { signal: AbortSignal }
) => Promise<HookJSONOutput>;
```

<h3 id="hookcallbackmatcher">
  `HookCallbackMatcher`
</h3>

オプションのマッチャーを含むフック設定。

```typescript theme={null}
interface HookCallbackMatcher {
  matcher?: string;
  hooks: HookCallback[];
  timeout?: number; // このマッチャーのすべてのフックのタイムアウト（秒）
}
```

<h3 id="hookinput">
  `HookInput`
</h3>

すべてのフック入力型の共用体型。

```typescript theme={null}
type HookInput =
  | PreToolUseHookInput
  | PostToolUseHookInput
  | PostToolUseFailureHookInput
  | PostToolBatchHookInput
  | NotificationHookInput
  | UserPromptSubmitHookInput
  | SessionStartHookInput
  | SessionEndHookInput
  | StopHookInput
  | SubagentStartHookInput
  | SubagentStopHookInput
  | PreCompactHookInput
  | PermissionRequestHookInput
  | SetupHookInput
  | TeammateIdleHookInput
  | TaskCompletedHookInput
  | ConfigChangeHookInput
  | WorktreeCreateHookInput
  | WorktreeRemoveHookInput
  | MessageDisplayHookInput;
```

<h3 id="basehookinput">
  `BaseHookInput`
</h3>

すべてのフック入力型が拡張する基本インターフェース。

```typescript theme={null}
type BaseHookInput = {
  session_id: string;
  transcript_path: string;
  cwd: string;
  prompt_id?: string;
  permission_mode?: string;
  effort?: { level: string };
  agent_id?: string;
  agent_type?: string;
};
```

`prompt_id` フィールドは、現在処理中のユーザープロンプトを識別する UUID です。[OpenTelemetry イベントの `prompt.id` 属性](/docs/ja/monitoring-usage#event-correlation-attributes) と一致し、最初のユーザー入力まで存在しません。Claude Code v2.1.196 以降が必要です。

<h4 id="pretoolusehookinput">
  `PreToolUseHookInput`
</h4>

```typescript theme={null}
type PreToolUseHookInput = BaseHookInput & {
  hook_event_name: "PreToolUse";
  tool_name: string;
  tool_input: unknown;
  tool_use_id: string;
};
```

<h4 id="posttoolusehookinput">
  `PostToolUseHookInput`
</h4>

```typescript theme={null}
type PostToolUseHookInput = BaseHookInput & {
  hook_event_name: "PostToolUse";
  tool_name: string;
  tool_input: unknown;
  tool_response: unknown;
  tool_use_id: string;
  duration_ms?: number;
};
```

<h4 id="posttoolusefailurehookinput">
  `PostToolUseFailureHookInput`
</h4>

```typescript theme={null}
type PostToolUseFailureHookInput = BaseHookInput & {
  hook_event_name: "PostToolUseFailure";
  tool_name: string;
  tool_input: unknown;
  tool_use_id: string;
  error: string;
  is_interrupt?: boolean;
  duration_ms?: number;
};
```

<h4 id="posttoolbatchhookinput">
  `PostToolBatchHookInput`
</h4>

バッチ内のすべてのツール呼び出しが解決された後、次のモデルリクエストの前に 1 回発火します。`tool_response` はモデルが見るシリアル化された `tool_result` コンテンツを保持します。形状は `PostToolUseHookInput` の構造化された `Output` オブジェクトとは異なります。

```typescript theme={null}
type PostToolBatchHookInput = BaseHookInput & {
  hook_event_name: "PostToolBatch";
  tool_calls: PostToolBatchToolCall[];
};

type PostToolBatchToolCall = {
  tool_name: string;
  tool_input: unknown;
  tool_use_id: string;
  tool_response?: unknown;
};
```

<h4 id="notificationhookinput">
  `NotificationHookInput`
</h4>

```typescript theme={null}
type NotificationHookInput = BaseHookInput & {
  hook_event_name: "Notification";
  message: string;
  title?: string;
  notification_type: string;
};
```

<h4 id="userpromptsubmithookinput">
  `UserPromptSubmitHookInput`
</h4>

```typescript theme={null}
type UserPromptSubmitHookInput = BaseHookInput & {
  hook_event_name: "UserPromptSubmit";
  prompt: string;
};
```

<h4 id="sessionstarthookinput">
  `SessionStartHookInput`
</h4>

```typescript theme={null}
type SessionStartHookInput = BaseHookInput & {
  hook_event_name: "SessionStart";
  source: "startup" | "resume" | "clear" | "compact";
  agent_type?: string;
  model?: string;
};
```

<h4 id="sessionendhookinput">
  `SessionEndHookInput`
</h4>

```typescript theme={null}
type SessionEndHookInput = BaseHookInput & {
  hook_event_name: "SessionEnd";
  reason: ExitReason; // EXIT_REASONS 配列からの文字列
};
```

<h4 id="stophookinput">
  `StopHookInput`
</h4>

```typescript theme={null}
type StopHookInput = BaseHookInput & {
  hook_event_name: "Stop";
  stop_hook_active: boolean;
  last_assistant_message?: string;
  background_tasks?: BackgroundTaskSummary[];
  session_crons?: SessionCronSummary[];
};
```

<h4 id="subagentstarthookinput">
  `SubagentStartHookInput`
</h4>

```typescript theme={null}
type SubagentStartHookInput = BaseHookInput & {
  hook_event_name: "SubagentStart";
  agent_id: string;
  agent_type: string;
};
```

<h4 id="subagentstophookinput">
  `SubagentStopHookInput`
</h4>

```typescript theme={null}
type SubagentStopHookInput = BaseHookInput & {
  hook_event_name: "SubagentStop";
  stop_hook_active: boolean;
  agent_id: string;
  agent_transcript_path: string;
  agent_type: string;
  last_assistant_message?: string;
  background_tasks?: BackgroundTaskSummary[];
  session_crons?: SessionCronSummary[];
};

type BackgroundTaskSummary = {
  id: string;
  type: string;
  status: string;
  description: string;
  command?: string;
  agent_type?: string;
  server?: string;
  tool?: string;
  name?: string;
};

type SessionCronSummary = {
  id: string;
  schedule: string;
  recurring: boolean;
  prompt: string;
};
```

<h4 id="precompacthookinput">
  `PreCompactHookInput`
</h4>

```typescript theme={null}
type PreCompactHookInput = BaseHookInput & {
  hook_event_name: "PreCompact";
  trigger: "manual" | "auto";
  custom_instructions: string | null;
};
```

<h4 id="permissionrequesthookinput">
  `PermissionRequestHookInput`
</h4>

```typescript theme={null}
type PermissionRequestHookInput = BaseHookInput & {
  hook_event_name: "PermissionRequest";
  tool_name: string;
  tool_input: unknown;
  permission_suggestions?: PermissionUpdate[];
};
```

<h4 id="setuphookinput">
  `SetupHookInput`
</h4>

```typescript theme={null}
type SetupHookInput = BaseHookInput & {
  hook_event_name: "Setup";
  trigger: "init" | "maintenance";
};
```

<h4 id="teammateidlehookinput">
  `TeammateIdleHookInput`
</h4>

```typescript theme={null}
type TeammateIdleHookInput = BaseHookInput & {
  hook_event_name: "TeammateIdle";
  teammate_name: string;
  /** @deprecated v2.1.178 以降は非推奨。セッション派生のチーム名を保持します。削除予定です。 */
  team_name: string;
};
```

<h4 id="taskcompletedhookinput">
  `TaskCompletedHookInput`
</h4>

```typescript theme={null}
type TaskCompletedHookInput = BaseHookInput & {
  hook_event_name: "TaskCompleted";
  task_id: string;
  task_subject: string;
  task_description?: string;
  teammate_name?: string;
  /** @deprecated v2.1.178 以降は非推奨。セッション派生のチーム名を保持します。削除予定です。 */
  team_name?: string;
};
```

<h4 id="configchangehookinput">
  `ConfigChangeHookInput`
</h4>

```typescript theme={null}
type ConfigChangeHookInput = BaseHookInput & {
  hook_event_name: "ConfigChange";
  source:
    | "user_settings"
    | "project_settings"
    | "local_settings"
    | "policy_settings"
    | "skills";
  file_path?: string;
};
```

<h4 id="worktreecreatehookinput">
  `WorktreeCreateHookInput`
</h4>

```typescript theme={null}
type WorktreeCreateHookInput = BaseHookInput & {
  hook_event_name: "WorktreeCreate";
  name: string;
};
```

<h4 id="worktreeremovehookinput">
  `WorktreeRemoveHookInput`
</h4>

```typescript theme={null}
type WorktreeRemoveHookInput = BaseHookInput & {
  hook_event_name: "WorktreeRemove";
  worktree_path: string;
};
```

<h4 id="messagedisplayhookinput">
  `MessageDisplayHookInput`
</h4>

```typescript theme={null}
type MessageDisplayHookInput = BaseHookInput & {
  hook_event_name: "MessageDisplay";
  turn_id: string;
  message_id: string;
  index: number;
  final: boolean;
  delta: string;
};
```

<h3 id="hookjsonoutput">
  `HookJSONOutput`
</h3>

フック戻り値。

```typescript theme={null}
type HookJSONOutput = AsyncHookJSONOutput | SyncHookJSONOutput;
```

<h4 id="asynchookjsonoutput">
  `AsyncHookJSONOutput`
</h4>

```typescript theme={null}
type AsyncHookJSONOutput = {
  async: true;
  asyncTimeout?: number;
};
```

<h4 id="synchookjsonoutput">
  `SyncHookJSONOutput`
</h4>

```typescript theme={null}
type SyncHookJSONOutput = {
  continue?: boolean;
  suppressOutput?: boolean;
  stopReason?: string;
  decision?: "approve" | "block";
  systemMessage?: string;
  reason?: string;
  hookSpecificOutput?:
    | {
        hookEventName: "PreToolUse";
        permissionDecision?: "allow" | "deny" | "ask" | "defer";
        permissionDecisionReason?: string;
        updatedInput?: Record<string, unknown>;
        additionalContext?: string;
      }
    | {
        hookEventName: "UserPromptSubmit";
        additionalContext?: string;
      }
    | {
        hookEventName: "SessionStart";
        additionalContext?: string;
      }
    | {
        hookEventName: "Setup";
        additionalContext?: string;
      }
    | {
        hookEventName: "SubagentStart";
        additionalContext?: string;
      }
    | {
        hookEventName: "PostToolUse";
        additionalContext?: string;
        updatedToolOutput?: unknown;
        /** @deprecated `updatedToolOutput` を使用してください。これはすべてのツールで機能します。 */
        updatedMCPToolOutput?: unknown;
      }
    | {
        hookEventName: "PostToolUseFailure";
        additionalContext?: string;
      }
    | {
        hookEventName: "PostToolBatch";
        additionalContext?: string;
      }
    | {
        hookEventName: "Notification";
        additionalContext?: string;
      }
    | {
        hookEventName: "PermissionRequest";
        decision:
          | {
              behavior: "allow";
              updatedInput?: Record<string, unknown>;
              updatedPermissions?: PermissionUpdate[];
            }
          | {
              behavior: "deny";
              message?: string;
              interrupt?: boolean;
            };
      };
};
```

<h2 id="tool-input-types">
  ツール入力型
</h2>

すべての組み込み Claude Code ツールの入力スキーマのドキュメント。これらの型は `@anthropic-ai/claude-agent-sdk` からエクスポートされ、タイプセーフなツール相互作用に使用できます。

<h3 id="toolinputschemas">
  `ToolInputSchemas`
</h3>

すべてのツール入力型の共用体。`@anthropic-ai/claude-agent-sdk` からエクスポートされます。

```typescript theme={null}
type ToolInputSchemas =
  | AgentInput
  | AskUserQuestionInput
  | BashInput
  | TaskOutputInput
  | EnterWorktreeInput
  | ExitPlanModeInput
  | FileEditInput
  | FileReadInput
  | FileWriteInput
  | GlobInput
  | GrepInput
  | ListMcpResourcesInput
  | McpInput
  | MonitorInput
  | NotebookEditInput
  | ReadMcpResourceInput
  | SubscribeMcpResourceInput
  | SubscribePollingInput
  | TaskCreateInput
  | TaskGetInput
  | TaskListInput
  | TaskStopInput
  | TaskUpdateInput
  | TodoWriteInput
  | UnsubscribeMcpResourceInput
  | UnsubscribePollingInput
  | WebFetchInput
  | WebSearchInput
  | WorkflowInput;
```

<h3 id="agent">
  Agent
</h3>

**ツール名：** `Agent`（以前は `Task`。これはまだエイリアスとして受け入れられます）

```typescript theme={null}
type AgentInput = {
  description: string;
  prompt: string;
  subagent_type?: string;
  model?: "sonnet" | "opus" | "haiku" | "fable";
  run_in_background?: boolean;
  name?: string;
  mode?: "acceptEdits" | "auto" | "bypassPermissions" | "default" | "dontAsk" | "plan";
  isolation?: "worktree";
};
```

複雑なマルチステップタスクを自律的に処理する新しいエージェントを起動します。

<h3 id="askuserquestion">
  AskUserQuestion
</h3>

**ツール名：** `AskUserQuestion`

```typescript theme={null}
type AskUserQuestionInput = {
  questions: Array<{
    question: string;
    header: string;
    options: Array<{ label: string; description: string; preview?: string }>;
    multiSelect: boolean;
  }>;
};
```

実行中にユーザーに明確化の質問をします。使用方法の詳細については、[承認とユーザー入力を処理](/docs/ja/agent-sdk/user-input#handle-clarifying-questions) を参照してください。

<h3 id="bash">
  Bash
</h3>

**ツール名：** `Bash`

```typescript theme={null}
type BashInput = {
  command: string;
  timeout?: number; // milliseconds, max 600000; higher values are clamped to the max
  description?: string;
  run_in_background?: boolean;
  dangerouslyDisableSandbox?: boolean;
};
```

オプションのタイムアウトとバックグラウンド実行を備えた永続的なシェルセッションで bash コマンドを実行します。

<h3 id="monitor">
  Monitor
</h3>

**ツール名：** `Monitor`

```typescript theme={null}
type MonitorInput = {
  command?: string;
  ws?: {
    url: string;
    protocols?: string[];
  };
  description: string;
  timeout_ms?: number;
  persistent?: boolean;
};
```

バックグラウンドソースを実行し、各イベントを Claude に配信するため、ポーリングなしで反応できます。`command` はスクリプトを実行し、stdout 行ごとに 1 つのイベントを発行し、`ws` は WebSocket を開き、テキストフレームごとに 1 つのイベントを発行します。`command` または `ws` のいずれか正確に 1 つを指定してください。`ws` ソースには Claude Code v2.1.195 以降が必要です。

セッション長のウォッチ（ログテールなど）の場合は `persistent: true` を設定します。Monitor がコマンドを実行する場合、Bash と同じパーミッションルールに従います。WebSocket ウォッチは別途承認を求めます。動作とプロバイダーの可用性については、[Monitor ツールリファレンス](/docs/ja/tools-reference#monitor-tool) を参照してください。

<h3 id="taskoutput">
  TaskOutput
</h3>

**ツール名：** `TaskOutput`

```typescript theme={null}
type TaskOutputInput = {
  task_id: string;
  block: boolean;
  timeout: number;
};
```

実行中または完了したバックグラウンドタスクから出力を取得します。

<h3 id="edit">
  Edit
</h3>

**ツール名：** `Edit`

```typescript theme={null}
type FileEditInput = {
  file_path: string;
  old_string: string;
  new_string: string;
  replace_all?: boolean;
};
```

ファイル内で正確な文字列置換を実行します。

<h3 id="read">
  Read
</h3>

**ツール名：** `Read`

```typescript theme={null}
type FileReadInput = {
  file_path: string;
  offset?: number;
  limit?: number;
  pages?: string;
};
```

テキスト、画像、PDF、Jupyter ノートブックを含むローカルファイルシステムからファイルを読み取ります。PDF ページ範囲には `pages` を使用します（例：`"1-5"`）。

<h3 id="write">
  Write
</h3>

**ツール名：** `Write`

```typescript theme={null}
type FileWriteInput = {
  file_path: string;
  content: string;
};
```

ローカルファイルシステムにファイルを書き込み、存在する場合は上書きします。

<h3 id="glob">
  Glob
</h3>

**ツール名：** `Glob`

```typescript theme={null}
type GlobInput = {
  pattern: string;
  path?: string;
};
```

任意のコードベースサイズで機能する高速ファイルパターンマッチング。

<h3 id="grep">
  Grep
</h3>

**ツール名：** `Grep`

```typescript theme={null}
type GrepInput = {
  pattern: string;
  path?: string;
  glob?: string;
  type?: string;
  output_mode?: "content" | "files_with_matches" | "count";
  "-i"?: boolean;
  "-n"?: boolean;
  "-B"?: number;
  "-A"?: number;
  "-C"?: number;
  context?: number;
  head_limit?: number;
  offset?: number;
  multiline?: boolean;
};
```

ripgrep に基づいた正規表現サポート付きの強力な検索ツール。

<h3 id="taskstop">
  TaskStop
</h3>

**ツール名：** `TaskStop`

```typescript theme={null}
type TaskStopInput = {
  task_id?: string;
  shell_id?: string; // 非推奨：task_id を使用
};
```

ID でバックグラウンドタスクまたはシェルを停止します。v2.1.198 以降、`task_id` はエージェントチームのチームメイト、またはエージェント ID または名前で名前付きバックグラウンドエージェントも受け入れます。

<h3 id="notebookedit">
  NotebookEdit
</h3>

**ツール名：** `NotebookEdit`

```typescript theme={null}
type NotebookEditInput = {
  notebook_path: string;
  cell_id?: string;
  new_source: string;
  cell_type?: "code" | "markdown";
  edit_mode?: "replace" | "insert" | "delete";
};
```

Jupyter ノートブックファイルのセルを編集します。

<h3 id="webfetch">
  WebFetch
</h3>

**ツール名：** `WebFetch`

```typescript theme={null}
type WebFetchInput = {
  url: string;
  prompt: string;
};
```

URL からコンテンツを取得し、AI モデルで処理します。

<h3 id="websearch">
  WebSearch
</h3>

**ツール名：** `WebSearch`

```typescript theme={null}
type WebSearchInput = {
  query: string;
  allowed_domains?: string[];
  blocked_domains?: string[];
};
```

ウェブを検索し、フォーマットされた結果を返します。

<h3 id="workflow">
  Workflow
</h3>

**ツール名：** `Workflow`

```typescript theme={null}
type WorkflowInput = {
  script?: string;
  name?: string;
  scriptPath?: string;
  args?: unknown;
  resumeFromRunId?: string;
};
```

[動的ワークフロー](/docs/ja/workflows) を実行します。これは多くのサブエージェントをバックグラウンドで調整し、1 つの統合結果を返すスクリプトです。`Workflow` ツールは Agent SDK v0.3.149 以降で利用可能です。`script`、`name`、または `scriptPath` の少なくとも 1 つが必要です。

| フィールド             | 型         | 説明                                                                                                                                                                                                                    |
| ----------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `script`          | `string`  | インラインワークフロースクリプト。リテラルとして `export const meta = { name, description }` で始まり、その後に `agent()`、`parallel()`、`pipeline()`、および `phase()` を使用するスクリプト本体が続く必要があります。`meta` 内のオプションの `phases` 配列は、進捗ビューで名前付きステージの下にエージェントをグループ化します |
| `name`            | `string`  | 組み込みワークフローまたは `.claude/workflows/` に保存されたワークフローの名前。スクリプトに解決されます                                                                                                                                                       |
| `scriptPath`      | `string`  | ディスク上のワークフロースクリプトファイルへのパス。`script` と `name` より優先されます。すべての呼び出しはそのスクリプトを永続化し、結果でパスを返すため、そのファイルを編集して同じ `scriptPath` で再度呼び出して反復処理できます                                                                                     |
| `args`            | `unknown` | スクリプトにグローバル `args` として公開される入力値。研究質問またはファイルパスのリストなど、パラメータ化された名前付きワークフロー用です。配列とオブジェクトを JSON エンコード文字列ではなく実際の JSON 値として渡します                                                                                               |
| `resumeFromRunId` | `string`  | 再開する前の `Workflow` 呼び出しの実行 ID。変更されていない入力を持つ完了した `agent()` 呼び出しはキャッシュされた結果を返します。変更または新しい呼び出しのみがライブで実行されます。同じセッションのみ                                                                                                     |

<h3 id="todowrite">
  TodoWrite
</h3>

**ツール名：** `TodoWrite`

```typescript theme={null}
type TodoWriteInput = {
  todos: Array<{
    content: string;
    status: "pending" | "in_progress" | "completed";
    activeForm: string;
  }>;
};
```

進捗を追跡するための構造化タスクリストを作成および管理します。

<Note>
  TypeScript Agent SDK 0.3.142 以降、`TodoWrite` はデフォルトで無効になっています。代わりに `TaskCreate`、`TaskGet`、`TaskUpdate`、および `TaskList` を使用してください。監視コードを更新するには、[Task ツールへの移行](/docs/ja/agent-sdk/todo-tracking#migrate-to-task-tools) を参照するか、`CLAUDE_CODE_ENABLE_TASKS=0` を設定して `TodoWrite` に戻してください。
</Note>

<h3 id="taskcreate">
  TaskCreate
</h3>

**ツール名：** `TaskCreate`

```typescript theme={null}
type TaskCreateInput = {
  subject: string;
  description: string;
  activeForm?: string;
  metadata?: Record<string, unknown>;
};
```

単一のタスクを作成し、割り当てられた ID を返します。

<h3 id="taskupdate">
  TaskUpdate
</h3>

**ツール名：** `TaskUpdate`

```typescript theme={null}
type TaskUpdateInput = {
  taskId: string;
  status?: "pending" | "in_progress" | "completed" | "deleted";
  subject?: string;
  description?: string;
  activeForm?: string;
  addBlocks?: string[];
  addBlockedBy?: string[];
  owner?: string;
  metadata?: Record<string, unknown>;
};
```

ID でタスクを 1 つパッチします。`status` を `"deleted"` に設定して削除します。

<h3 id="taskget">
  TaskGet
</h3>

**ツール名：** `TaskGet`

```typescript theme={null}
type TaskGetInput = {
  taskId: string;
};
```

1 つのタスクの完全な詳細を返すか、ID が見つからない場合は `null` を返します。

<h3 id="tasklist">
  TaskList
</h3>

**ツール名：** `TaskList`

```typescript theme={null}
type TaskListInput = {};
```

現在のリストのすべてのタスクのスナップショットを返します。

<h3 id="exitplanmode">
  ExitPlanMode
</h3>

**ツール名：** `ExitPlanMode`

```typescript theme={null}
type ExitPlanModeInput = {
  /** 非推奨：使用されなくなりました。 */
  allowedPrompts?: Array<{
    tool: "Bash";
    prompt: string;
  }>;
};
```

計画モードを終了します。`allowedPrompts` フィールドは非推奨で無視されます。Claude Code は既存の呼び出し元とトランスクリプトが検証されるようにそれでも受け入れます。v2.1.205 より前は、計画を実装するためのプロンプトベースの Bash パーミッションをリクエストしていました。

<h3 id="listmcpresources">
  ListMcpResources
</h3>

**ツール名：** `ListMcpResourcesTool`

```typescript theme={null}
type ListMcpResourcesInput = {
  server?: string;
};
```

接続されたサーバーから利用可能な MCP リソースをリストします。

<h3 id="readmcpresource">
  ReadMcpResource
</h3>

**ツール名：** `ReadMcpResourceTool`

```typescript theme={null}
type ReadMcpResourceInput = {
  server: string;
  uri: string;
};
```

サーバーから特定の MCP リソースを読み取ります。

<h3 id="enterworktree">
  EnterWorktree
</h3>

**ツール名：** `EnterWorktree`

```typescript theme={null}
type EnterWorktreeInput = {
  name?: string;
  path?: string;
};
```

分離された作業用の一時的な git worktree を作成して入力します。新しい worktree を作成する代わりに、現在のリポジトリの既存の worktree に切り替えるには `path` を渡します。最初の入力時、ターゲットは現在のリポジトリの登録済み worktree、またはマルチリポジトリワークスペースの場合はその中にネストされたリポジトリの worktree である必要があります。worktree セッション内からは、セッションのリポジトリの `.claude/worktrees/` の下にある必要があります。`name` と `path` は相互に排他的です。

<h2 id="tool-output-types">
  ツール出力型
</h2>

すべての組み込み Claude Code ツールの出力スキーマのドキュメント。これらの型は `@anthropic-ai/claude-agent-sdk` からエクスポートされ、各ツールによって返される実際の応答データを表します。

<h3 id="tooloutputschemas">
  `ToolOutputSchemas`
</h3>

すべてのツール出力型の共用体。

```typescript theme={null}
type ToolOutputSchemas =
  | AgentOutput
  | AskUserQuestionOutput
  | BashOutput
  | EnterWorktreeOutput
  | ExitPlanModeOutput
  | FileEditOutput
  | FileReadOutput
  | FileWriteOutput
  | GlobOutput
  | GrepOutput
  | ListMcpResourcesOutput
  | MonitorOutput
  | NotebookEditOutput
  | ReadMcpResourceOutput
  | TaskCreateOutput
  | TaskGetOutput
  | TaskListOutput
  | TaskStopOutput
  | TaskUpdateOutput
  | TodoWriteOutput
  | WebFetchOutput
  | WebSearchOutput
  | WorkflowOutput;
```

<h3 id="agent-2">
  Agent
</h3>

**ツール名：** `Agent`（以前は `Task`。これはまだエイリアスとして受け入れられます）

```typescript theme={null}
type AgentOutput =
  | {
      status: "completed";
      agentId: string;
      agentType?: string;
      content: Array<{ type: "text"; text: string; citations?: unknown[] | null }>;
      resolvedModel?: string;
      totalToolUseCount: number;
      totalDurationMs: number;
      totalTokens: number;
      usage: {
        input_tokens: number;
        output_tokens: number;
        cache_creation_input_tokens: number | null;
        cache_read_input_tokens: number | null;
        server_tool_use: {
          web_search_requests: number;
          web_fetch_requests: number;
        } | null;
        service_tier: string | null;
        cache_creation: {
          ephemeral_1h_input_tokens: number;
          ephemeral_5m_input_tokens: number;
        } | null;
        inference_geo?: string | null;
        speed?: string | null;
        iterations?: unknown;
      };
      toolStats?: {
        readCount: number;
        searchCount: number;
        bashCount: number;
        editFileCount: number;
        linesAdded: number;
        linesRemoved: number;
        otherToolCount: number;
        frameCount?: number;
      };
      prompt: string;
      worktreePath?: string;
      worktreeBranch?: string;
    }
  | {
      status: "async_launched";
      isAsync?: true;
      agentId: string;
      description: string;
      resolvedModel?: string;
      prompt: string;
      outputFile: string;
      canReadOutputFile?: boolean;
    }
  | {
      status: "remote_launched";
      taskId: string;
      sessionUrl: string;
      description: string;
      prompt: string;
      outputFile: string;
    };
```

サブエージェントからの結果を返します。`status` フィールドで判別されます：完了したタスクの場合は `"completed"`、バックグラウンドタスクの場合は `"async_launched"`、Claude Code がリモートクラウドセッションにディスパッチしたタスクの場合は `"remote_launched"`。`sessionUrl` はそのセッションにリンクし、`taskId` はそれを識別します。

`completed` および `async_launched` バリアントの `resolvedModel` フィールドは、サブエージェントが実際に実行されたモデルに名前を付けます。これは、[`availableModels`](/docs/ja/model-config#restrict-model-selection) または別のオーバーライドが適用される場合、要求された `model` 入力と異なる場合があります。このフィールドには Claude Code v2.1.174 以降が必要です。

`completed` バリアントでは、サブエージェントが分離された git worktree で実行された場合に `worktreePath` が設定され、Claude Code がそれを作成した場合に `worktreeBranch` はその worktree のブランチに名前を付けます。`usage.service_tier` は、API がサブエージェントのリクエストに対して報告したサービスティア文字列を保持します。

v2.1.207 より前では、公開された型はより狭いものでした。`worktreePath`、`worktreeBranch`、`citations`、`toolStats.frameCount`、および `inference_geo`、`speed`、`iterations` 使用フィールドを省略し、`service_tier` を `"standard" | "priority" | "batch"` として型付けしていました。型がオプションとしてマークするフィールドは、以前のバージョンで記録された結果に存在しない場合があります。

<h3 id="askuserquestion-2">
  AskUserQuestion
</h3>

**ツール名：** `AskUserQuestion`

```typescript theme={null}
type AskUserQuestionOutput = {
  questions: Array<{
    question: string;
    header: string;
    options: Array<{ label: string; description: string; preview?: string }>;
    multiSelect: boolean;
  }>;
  answers: Record<string, string>;
  response?: string;
};
```

質問とユーザーの回答を返します。`response` はユーザーが構造化された質問に答える代わりに自由形式の返信を入力した場合に設定されます。存在する場合、Claude は質問ごとの回答リストの代わりに「ユーザーが応答しました：…」を受け取ります。

<h3 id="bash-2">
  Bash
</h3>

**ツール名：** `Bash`

```typescript theme={null}
type BashOutput = {
  stdout: string;
  stderr: string;
  rawOutputPath?: string;
  interrupted: boolean;
  isImage?: boolean;
  backgroundTaskId?: string;
  backgroundedByUser?: boolean;
  dangerouslyDisableSandbox?: boolean;
  returnCodeInterpretation?: string;
  structuredContent?: unknown[];
  persistedOutputPath?: string;
  persistedOutputSize?: number;
};
```

stdout/stderr が分割されたコマンド出力を返します。バックグラウンドコマンドには `backgroundTaskId` が含まれます。

<h3 id="monitor-2">
  Monitor
</h3>

**ツール名：** `Monitor`

```typescript theme={null}
type MonitorOutput = {
  taskId: string;
  timeoutMs: number;
  persistent?: boolean;
};
```

実行中のモニターのバックグラウンドタスク ID を返します。この ID を `TaskStop` で使用して、ウォッチを早期にキャンセルします。

<h3 id="edit-2">
  Edit
</h3>

**ツール名：** `Edit`

```typescript theme={null}
type FileEditOutput = {
  filePath: string;
  oldString: string;
  newString: string;
  originalFile: string;
  structuredPatch: Array<{
    oldStart: number;
    oldLines: number;
    newStart: number;
    newLines: number;
    lines: string[];
  }>;
  userModified: boolean;
  replaceAll: boolean;
  gitDiff?: {
    filename: string;
    status: "modified" | "added";
    additions: number;
    deletions: number;
    changes: number;
    patch: string;
  };
};
```

編集操作の構造化された diff を返します。

<h3 id="read-2">
  Read
</h3>

**ツール名：** `Read`

```typescript theme={null}
type FileReadOutput =
  | {
      type: "text";
      file: {
        filePath: string;
        content: string;
        numLines: number;
        startLine: number;
        totalLines: number;
      };
    }
  | {
      type: "image";
      file: {
        base64: string;
        type: "image/jpeg" | "image/png" | "image/gif" | "image/webp";
        originalSize: number;
        dimensions?: {
          originalWidth?: number;
          originalHeight?: number;
          displayWidth?: number;
          displayHeight?: number;
        };
      };
    }
  | {
      type: "notebook";
      file: {
        filePath: string;
        cells: unknown[];
      };
    }
  | {
      type: "pdf";
      file: {
        filePath: string;
        base64: string;
        originalSize: number;
      };
    }
  | {
      type: "parts";
      file: {
        filePath: string;
        originalSize: number;
        count: number;
        outputDir: string;
      };
    };
```

ファイルタイプに適切な形式でファイルコンテンツを返します。`type` フィールドで判別されます。

<h3 id="write-2">
  Write
</h3>

**ツール名：** `Write`

```typescript theme={null}
type FileWriteOutput = {
  type: "create" | "update";
  filePath: string;
  content: string;
  structuredPatch: Array<{
    oldStart: number;
    oldLines: number;
    newStart: number;
    newLines: number;
    lines: string[];
  }>;
  originalFile: string | null;
  gitDiff?: {
    filename: string;
    status: "modified" | "added";
    additions: number;
    deletions: number;
    changes: number;
    patch: string;
  };
};
```

構造化された diff 情報を含む書き込み結果を返します。

<h3 id="glob-2">
  Glob
</h3>

**ツール名：** `Glob`

```typescript theme={null}
type GlobOutput = {
  durationMs: number;
  numFiles: number;
  filenames: string[];
  truncated: boolean;
};
```

glob パターンに一致するファイルパスを返します。変更時刻でソートされます。

<h3 id="grep-2">
  Grep
</h3>

**ツール名：** `Grep`

```typescript theme={null}
type GrepOutput = {
  mode?: "content" | "files_with_matches" | "count";
  numFiles: number;
  filenames: string[];
  content?: string;
  numLines?: number;
  numMatches?: number;
  appliedLimit?: number;
  appliedOffset?: number;
};
```

検索結果を返します。形状は `mode` によって異なります：ファイルリスト、マッチを含むコンテンツ、またはマッチ数。

<h3 id="taskstop-2">
  TaskStop
</h3>

**ツール名：** `TaskStop`

```typescript theme={null}
type TaskStopOutput = {
  message: string;
  task_id: string;
  task_type: string;
  command?: string;
};
```

バックグラウンドタスクを停止した後の確認を返します。

<h3 id="notebookedit-2">
  NotebookEdit
</h3>

**ツール名：** `NotebookEdit`

```typescript theme={null}
type NotebookEditOutput = {
  new_source: string;
  cell_id?: string;
  cell_type: "code" | "markdown";
  language: string;
  edit_mode: string;
  error?: string;
  notebook_path: string;
  original_file: string;
  updated_file: string;
};
```

元のファイルと更新されたファイルコンテンツを含むノートブック編集の結果を返します。

<h3 id="webfetch-2">
  WebFetch
</h3>

**ツール名：** `WebFetch`

```typescript theme={null}
type WebFetchOutput = {
  bytes: number;
  code: number;
  codeText: string;
  result: string;
  durationMs: number;
  url: string;
};
```

HTTP ステータスとメタデータを含む取得されたコンテンツを返します。

<h3 id="websearch-2">
  WebSearch
</h3>

**ツール名：** `WebSearch`

```typescript theme={null}
type WebSearchOutput = {
  query: string;
  results: Array<
    | {
        tool_use_id: string;
        content: Array<{ title: string; url: string }>;
      }
    | string
  >;
  durationSeconds: number;
};
```

ウェブからの検索結果を返します。

<h3 id="workflow-2">
  Workflow
</h3>

**ツール名：** `Workflow`

```typescript theme={null}
type WorkflowOutput = {
  status: "async_launched";
  taskId: string;
  runId?: string;
  summary?: string;
  transcriptDir?: string;
  scriptPath?: string;
  error?: string;
};
```

ツールが呼び出しを受け入れた直後に返します。最終的な結果は後でタスク完了として到着します。実行が開始されたと見なす前に `error` を確認してください：構文チェックに失敗したスクリプトは `status: "async_launched"` と `error` セットで返され、実行されません。

| フィールド           | 型                  | 説明                                                                           |
| --------------- | ------------------ | ---------------------------------------------------------------------------- |
| `status`        | `"async_launched"` | ツールが呼び出しを受け入れました。これはフィールドが取る唯一の値です                                           |
| `taskId`        | `string`           | 実行のバックグラウンドタスク識別子                                                            |
| `runId`         | `string`           | 後の呼び出しで `resumeFromRunId` として渡すワークフロー実行識別子                                   |
| `summary`       | `string`           | ワークフローが何をするかの 1 行の説明                                                         |
| `transcriptDir` | `string`           | 実行中にサブエージェントトランスクリプトが書き込まれるディレクトリ                                            |
| `scriptPath`    | `string`           | この実行のために永続化されたワークフロースクリプトへのパス。編集して `scriptPath` として戻すことで、スクリプトを再送信せずに再実行できます |
| `error`         | `string`           | スクリプトが構文チェックに失敗した場合に設定されます。存在する場合、`async_launched` ステータスにもかかわらず実行は開始されませんでした |

<h3 id="todowrite-2">
  TodoWrite
</h3>

**ツール名：** `TodoWrite`

```typescript theme={null}
type TodoWriteOutput = {
  oldTodos: Array<{
    content: string;
    status: "pending" | "in_progress" | "completed";
    activeForm: string;
  }>;
  newTodos: Array<{
    content: string;
    status: "pending" | "in_progress" | "completed";
    activeForm: string;
  }>;
};
```

前のタスクリストと更新されたタスクリストを返します。

<Note>
  TypeScript Agent SDK 0.3.142 以降、`TodoWrite` はデフォルトで無効になっています。代わりに `TaskCreate`、`TaskGet`、`TaskUpdate`、および `TaskList` を使用してください。[タスクツールへの移行](/docs/ja/agent-sdk/todo-tracking#migrate-to-task-tools)を参照して、監視コードを更新するか、`CLAUDE_CODE_ENABLE_TASKS=0` を設定して `TodoWrite` に戻してください。
</Note>

<h3 id="taskcreate-2">
  TaskCreate
</h3>

**ツール名：** `TaskCreate`

```typescript theme={null}
type TaskCreateOutput = {
  task: {
    id: string;
    subject: string;
  };
};
```

割り当てられた ID を持つ作成されたタスクを返します。

<h3 id="taskupdate-2">
  TaskUpdate
</h3>

**ツール名：** `TaskUpdate`

```typescript theme={null}
type TaskUpdateOutput = {
  success: boolean;
  taskId: string;
  updatedFields: string[];
  error?: string;
  statusChange?: {
    from: string;
    to: string;
  };
};
```

更新結果を返します。どのフィールドが変更されたかを含みます。

<h3 id="taskget-2">
  TaskGet
</h3>

**ツール名：** `TaskGet`

```typescript theme={null}
type TaskGetOutput = {
  task: {
    id: string;
    subject: string;
    description: string;
    status: "pending" | "in_progress" | "completed";
    blocks: string[];
    blockedBy: string[];
  } | null;
};
```

完全なタスクレコードを返します。ID が見つからない場合は `null` を返します。

<h3 id="tasklist-2">
  TaskList
</h3>

**ツール名：** `TaskList`

```typescript theme={null}
type TaskListOutput = {
  tasks: Array<{
    id: string;
    subject: string;
    status: "pending" | "in_progress" | "completed";
    owner?: string;
    blockedBy: string[];
  }>;
};
```

現在のリスト内のすべてのタスクのスナップショットを返します。

<h3 id="exitplanmode-2">
  ExitPlanMode
</h3>

**ツール名：** `ExitPlanMode`

```typescript theme={null}
type ExitPlanModeOutput = {
  plan: string | null;
  isAgent: boolean;
  filePath?: string;
  hasTaskTool?: boolean;
  awaitingLeaderApproval?: boolean;
  requestId?: string;
};
```

計画モード終了後の計画状態を返します。

<h3 id="listmcpresources-2">
  ListMcpResources
</h3>

**ツール名：** `ListMcpResourcesTool`

```typescript theme={null}
type ListMcpResourcesOutput = Array<{
  uri: string;
  name: string;
  mimeType?: string;
  description?: string;
  server: string;
}>;
```

利用可能な MCP リソースの配列を返します。

<h3 id="readmcpresource-2">
  ReadMcpResource
</h3>

**ツール名：** `ReadMcpResourceTool`

```typescript theme={null}
type ReadMcpResourceOutput = {
  contents: Array<{
    uri: string;
    mimeType?: string;
    text?: string;
  }>;
};
```

要求された MCP リソースのコンテンツを返します。

<h3 id="enterworktree-2">
  EnterWorktree
</h3>

**ツール名：** `EnterWorktree`

```typescript theme={null}
type EnterWorktreeOutput = {
  worktreePath: string;
  worktreeBranch?: string;
  message: string;
};
```

git worktree に関する情報を返します。

<h2 id="permission-types">
  パーミッション型
</h2>

<h3 id="permissionupdate">
  `PermissionUpdate`
</h3>

パーミッション更新の操作。

```typescript theme={null}
type PermissionUpdate =
  | {
      type: "addRules";
      rules: PermissionRuleValue[];
      behavior: PermissionBehavior;
      destination: PermissionUpdateDestination;
    }
  | {
      type: "replaceRules";
      rules: PermissionRuleValue[];
      behavior: PermissionBehavior;
      destination: PermissionUpdateDestination;
    }
  | {
      type: "removeRules";
      rules: PermissionRuleValue[];
      behavior: PermissionBehavior;
      destination: PermissionUpdateDestination;
    }
  | {
      type: "setMode";
      mode: PermissionMode;
      destination: PermissionUpdateDestination;
    }
  | {
      type: "addDirectories";
      directories: string[];
      destination: PermissionUpdateDestination;
    }
  | {
      type: "removeDirectories";
      directories: string[];
      destination: PermissionUpdateDestination;
    };
```

<h3 id="permissionbehavior">
  `PermissionBehavior`
</h3>

```typescript theme={null}
type PermissionBehavior = "allow" | "deny" | "ask";
```

<h3 id="permissionupdatedestination">
  `PermissionUpdateDestination`
</h3>

```typescript theme={null}
type PermissionUpdateDestination =
  | "userSettings" // グローバルユーザー設定
  | "projectSettings" // ディレクトリごとのプロジェクト設定
  | "localSettings" // ローカルプロジェクト設定
  | "session" // 現在のセッションのみ
  | "cliArg"; // CLI 引数
```

<h3 id="permissionrulevalue">
  `PermissionRuleValue`
</h3>

```typescript theme={null}
type PermissionRuleValue = {
  toolName: string;
  ruleContent?: string;
};
```

<h2 id="other-types">
  その他の型
</h2>

<h3 id="apikeysource">
  `ApiKeySource`
</h3>

```typescript theme={null}
type ApiKeySource = "user" | "project" | "org" | "temporary" | "oauth";
```

<h3 id="sdkbeta">
  `SdkBeta`
</h3>

`betas` オプション経由で有効にできる利用可能なベータ機能。詳細は [ベータヘッダー](https://platform.claude.com/docs/ja/api/beta-headers) を参照してください。

```typescript theme={null}
type SdkBeta = "context-1m-2025-08-07";
```

<Warning>
  `context-1m-2025-08-07` ベータは 2026 年 4 月 30 日時点で廃止されました。Claude Sonnet 4.5 または Sonnet 4 でこの値を渡すと効果がなく、標準 200k トークンコンテキストウィンドウを超えるリクエストはエラーを返します。1M トークンコンテキストウィンドウを使用するには、[Claude Sonnet 5、Claude Sonnet 4.6、Claude Opus 4.6、Claude Opus 4.7、または Claude Opus 4.8](https://platform.claude.com/docs/ja/about-claude/models/overview) に移行してください。これらには、ベータヘッダーなしで標準価格で 1M コンテキストが含まれます。
</Warning>

<h3 id="slashcommand">
  `SlashCommand`
</h3>

利用可能なスラッシュコマンドに関する情報。

```typescript theme={null}
type SlashCommand = {
  name: string;
  description: string;
  argumentHint: string;
  aliases?: string[];
};
```

<h3 id="modelinfo">
  `ModelInfo`
</h3>

利用可能なモデルに関する情報。

```typescript theme={null}
type ModelInfo = {
  value: string;
  resolvedModel?: string;
  displayName: string;
  description: string;
  supportsEffort?: boolean;
  supportedEffortLevels?: ("low" | "medium" | "high" | "xhigh" | "max")[];
  supportsAdaptiveThinking?: boolean;
  supportsFastMode?: boolean;
  supportsAutoMode?: boolean;
};
```

| フィールド                      | 型                                                                  | 説明                                                                                                                                                                             |
| :------------------------- | :----------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `value`                    | `string`                                                           | API 呼び出しで渡すモデル識別子                                                                                                                                                              |
| `resolvedModel`            | `string \| undefined`                                              | このエントリの `value` が解決される正規のワイヤモデル ID。`sonnet` などのエイリアスエントリは `claude-sonnet-5` などの明示的なモデル ID に解決されるため、ホストは保存された明示的なモデル ID をそれをカバーするエイリアスエントリと照合できます。Claude Code v2.1.197 以降が必要です。 |
| `displayName`              | `string`                                                           | 人間が読める表示名                                                                                                                                                                      |
| `description`              | `string`                                                           | モデルの機能の説明                                                                                                                                                                      |
| `supportsEffort`           | `boolean \| undefined`                                             | このモデルが努力レベルをサポートするかどうか                                                                                                                                                         |
| `supportedEffortLevels`    | `("low" \| "medium" \| "high" \| "xhigh" \| "max")[] \| undefined` | このモデルが受け入れる努力レベル                                                                                                                                                               |
| `supportsAdaptiveThinking` | `boolean \| undefined`                                             | このモデルが適応的思考をサポートするかどうか。Claude が何をいつ考えるかを決定します                                                                                                                                  |
| `supportsFastMode`         | `boolean \| undefined`                                             | このモデルが高速モードをサポートするかどうか                                                                                                                                                         |
| `supportsAutoMode`         | `boolean \| undefined`                                             | このモデルが自動モードをサポートするかどうか                                                                                                                                                         |

<h3 id="agentinfo">
  `AgentInfo`
</h3>

Agent ツール経由で呼び出すことができる利用可能なサブエージェントに関する情報。

```typescript theme={null}
type AgentInfo = {
  name: string;
  description: string;
  model?: string;
};
```

| フィールド         | 型                     | 説明                                            |
| :------------ | :-------------------- | :-------------------------------------------- |
| `name`        | `string`              | エージェント型識別子（例：`"Explore"`、`"general-purpose"`） |
| `description` | `string`              | このエージェントをいつ使用するかの説明                           |
| `model`       | `string \| undefined` | このエージェントが使用するモデルエイリアス。省略すると、親のモデルを継承します       |

<h3 id="mcpserverstatus">
  `McpServerStatus`
</h3>

接続された MCP サーバーのステータス。

```typescript theme={null}
type McpServerStatus = {
  name: string;
  status: "connected" | "failed" | "needs-auth" | "pending" | "disabled";
  serverInfo?: {
    name: string;
    version: string;
  };
  error?: string;
  config?: McpServerStatusConfig;
  scope?: string;
  tools?: {
    name: string;
    description?: string;
    annotations?: {
      readOnly?: boolean;
      destructive?: boolean;
      openWorld?: boolean;
    };
  }[];
};
```

<h3 id="mcpserverstatusconfig">
  `McpServerStatusConfig`
</h3>

`mcpServerStatus()` によってレポートされた MCP サーバーの設定。これはすべての MCP サーバートランスポートタイプの共用体です。

```typescript theme={null}
type McpServerStatusConfig =
  | McpStdioServerConfig
  | McpSSEServerConfig
  | McpHttpServerConfig
  | McpSdkServerConfig
  | McpClaudeAIProxyServerConfig;
```

各トランスポートタイプの詳細については、[`McpServerConfig`](#mcpserverconfig) を参照してください。

<h3 id="accountinfo">
  `AccountInfo`
</h3>

認証されたユーザーのアカウント情報。

```typescript theme={null}
type AccountInfo = {
  email?: string;
  organization?: string;
  subscriptionType?: string;
  tokenSource?: string;
  apiKeySource?: string;
};
```

<h3 id="modelusage">
  `ModelUsage`
</h3>

結果メッセージで返されるモデルごとの使用統計。`costUSD` 値はクライアント側の推定です。請求に関する注意事項については、[コストと使用状況を追跡](/docs/ja/agent-sdk/cost-tracking) を参照してください。

```typescript theme={null}
type ModelUsage = {
  inputTokens: number;
  outputTokens: number;
  cacheReadInputTokens: number;
  cacheCreationInputTokens: number;
  webSearchRequests: number;
  costUSD: number;
  contextWindow: number;
  maxOutputTokens: number;
};
```

<h3 id="configscope">
  `ConfigScope`
</h3>

```typescript theme={null}
type ConfigScope = "local" | "user" | "project";
```

<h3 id="nonnullableusage">
  `NonNullableUsage`
</h3>

すべての nullable フィールドが non-nullable になった [`Usage`](#usage) のバージョン。

```typescript theme={null}
type NonNullableUsage = {
  [K in keyof Usage]: NonNullable<Usage[K]>;
};
```

<h3 id="usage">
  `Usage`
</h3>

トークン使用統計。これは `@anthropic-ai/sdk` の `BetaUsage` 型です。

```typescript theme={null}
type Usage = {
  input_tokens: number;
  output_tokens: number;
  cache_creation_input_tokens: number | null;
  cache_read_input_tokens: number | null;
  cache_creation: {
    ephemeral_5m_input_tokens: number;
    ephemeral_1h_input_tokens: number;
  } | null;
  server_tool_use: BetaServerToolUsage | null;
  service_tier: "standard" | "priority" | "batch" | null;
  speed: "standard" | "fast" | null;
  inference_geo: string | null;
  iterations: BetaIterationsUsage | null;
};
```

`BetaServerToolUsage` と `BetaIterationsUsage` は `@anthropic-ai/sdk` で定義されています。

<h3 id="calltoolresult">
  `CallToolResult`
</h3>

MCP ツール結果型（`@modelcontextprotocol/sdk/types.js` から）。`structuredContent` は `content` と一緒に返すことができる JSON オブジェクトで、画像ブロックを含みます。詳細は [構造化データを返す](/docs/ja/agent-sdk/custom-tools#return-structured-data) を参照してください。

```typescript theme={null}
type CallToolResult = {
  content: Array<{
    type: "text" | "image" | "audio" | "resource" | "resource_link";
    // 追加フィールドはタイプによって異なります
  }>;
  structuredContent?: Record<string, unknown>;
  isError?: boolean;
};
```

<h3 id="thinkingconfig">
  `ThinkingConfig`
</h3>

Claude の思考/推論動作を制御します。非推奨の `maxThinkingTokens` より優先されます。

```typescript theme={null}
type ThinkingDisplay = "summarized" | "omitted";

type ThinkingConfig =
  | { type: "adaptive"; display?: ThinkingDisplay } // モデルが推論のタイミングと量を決定します（Opus 4.6 以降）
  | { type: "enabled"; budgetTokens?: number; display?: ThinkingDisplay } // 固定思考トークン予算
  | { type: "disabled" }; // 拡張思考なし
```

オプションの `display` フィールドは、思考テキストが `"summarized"` または `"omitted"` で返されるかどうかを制御します。Claude Opus 4.7 以降では、API のデフォルトは `"omitted"` であるため、`"summarized"` を設定して `thinking` ブロックで思考コンテンツを受け取ります。

<h3 id="spawnedprocess">
  `SpawnedProcess`
</h3>

カスタムプロセススポーニング用のインターフェース（`spawnClaudeCodeProcess` オプションで使用）。`ChildProcess` は既にこのインターフェースを満たしています。

```typescript theme={null}
interface SpawnedProcess {
  stdin: Writable;
  stdout: Readable;
  readonly killed: boolean;
  readonly exitCode: number | null;
  kill(signal: NodeJS.Signals): boolean;
  on(
    event: "exit",
    listener: (code: number | null, signal: NodeJS.Signals | null) => void
  ): void;
  on(event: "error", listener: (error: Error) => void): void;
  once(
    event: "exit",
    listener: (code: number | null, signal: NodeJS.Signals | null) => void
  ): void;
  once(event: "error", listener: (error: Error) => void): void;
  off(
    event: "exit",
    listener: (code: number | null, signal: NodeJS.Signals | null) => void
  ): void;
  off(event: "error", listener: (error: Error) => void): void;
}
```

<h3 id="spawnoptions">
  `SpawnOptions`
</h3>

カスタムスポーン関数に渡されるオプション。

```typescript theme={null}
interface SpawnOptions {
  command: string;
  args: string[];
  cwd?: string;
  env: Record<string, string | undefined>;
  signal: AbortSignal;
}
```

<Note>
  `signal` フィールドは、スポーン関数にプロセスをティアダウンするタイミングを通知します。Node の `spawn()` に `signal` オプションとして渡すか、VM またはコンテナティアダウンハンドラーに渡してください。

  このシグナルは、[`Options.abortController`](#options) が中止した瞬間には発火しません。SDK は最初にプロセスの stdin を閉じて約 2 秒待機し、CLI がクリーンにシャットダウンできるようにしてから、このシグナルを中止します。呼び出し元が中止した瞬間に反応するには、スポーン関数がそのエンクロージングスコープから参照できる独自の `Options.abortController.signal` をリッスンしてください。
</Note>

<h3 id="mcpsetserversresult">
  `McpSetServersResult`
</h3>

`setMcpServers()` 操作の結果。

```typescript theme={null}
type McpSetServersResult = {
  added: string[];
  removed: string[];
  errors: Record<string, string>;
};
```

<h3 id="rewindfilesresult">
  `RewindFilesResult`
</h3>

`rewindFiles()` 操作の結果。

```typescript theme={null}
type RewindFilesResult = {
  canRewind: boolean;
  error?: string;
  filesChanged?: string[];
  insertions?: number;
  deletions?: number;
};
```

<h3 id="sdkstatusmessage">
  `SDKStatusMessage`
</h3>

ステータス更新メッセージ（例：圧縮）。

```typescript theme={null}
type SDKStatusMessage = {
  type: "system";
  subtype: "status";
  status: "compacting" | null;
  permissionMode?: PermissionMode;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdktasknotificationmessage">
  `SDKTaskNotificationMessage`
</h3>

バックグラウンドタスクが完了、失敗、または停止したときの通知。バックグラウンドタスクには、`run_in_background` Bash コマンド、[Monitor](#monitor) ウォッチ、バックグラウンドサブエージェントが含まれます。

```typescript theme={null}
type SDKTaskNotificationMessage = {
  type: "system";
  subtype: "task_notification";
  task_id: string;
  tool_use_id?: string;
  status: "completed" | "failed" | "stopped";
  output_file: string;
  summary: string;
  usage?: {
    total_tokens: number;
    tool_uses: number;
    duration_ms: number;
  };
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdktoolusesummarymessage">
  `SDKToolUseSummaryMessage`
</h3>

会話でのツール使用のサマリー。

```typescript theme={null}
type SDKToolUseSummaryMessage = {
  type: "tool_use_summary";
  summary: string;
  preceding_tool_use_ids: string[];
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkhookstartedmessage">
  `SDKHookStartedMessage`
</h3>

フックが実行を開始したときに発行されます。

Claude Code は、このメッセージ、[`SDKHookProgressMessage`](#sdkhookprogressmessage)、および [`SDKHookResponseMessage`](#sdkhookresponsemessage) をメッセージストリームに直ちに配信します。これは、セッション起動中に `SessionStart` または `Setup` フックがまだ実行中であっても含まれます。Claude Code v2.1.169 から v2.1.203 は、`SessionStart` または `Setup` フックが完了した後、これらのメッセージを 1 つのバッチで配信していました。v2.1.204 はライブ配信を復元しました。

```typescript theme={null}
type SDKHookStartedMessage = {
  type: "system";
  subtype: "hook_started";
  hook_id: string;
  hook_name: string;
  hook_event: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkhookprogressmessage">
  `SDKHookProgressMessage`
</h3>

フックが実行中に stdout/stderr 出力で発行されます。

```typescript theme={null}
type SDKHookProgressMessage = {
  type: "system";
  subtype: "hook_progress";
  hook_id: string;
  hook_name: string;
  hook_event: string;
  stdout: string;
  stderr: string;
  output: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkhookresponsemessage">
  `SDKHookResponseMessage`
</h3>

フックが実行を終了したときに発行されます。

```typescript theme={null}
type SDKHookResponseMessage = {
  type: "system";
  subtype: "hook_response";
  hook_id: string;
  hook_name: string;
  hook_event: string;
  output: string;
  stdout: string;
  stderr: string;
  exit_code?: number;
  outcome: "success" | "error" | "cancelled";
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdktoolprogressmessage">
  `SDKToolProgressMessage`
</h3>

ツール実行中に定期的に発行され、進捗を示します。

```typescript theme={null}
type SDKToolProgressMessage = {
  type: "tool_progress";
  tool_use_id: string;
  tool_name: string;
  parent_tool_use_id: string | null;
  elapsed_time_seconds: number;
  task_id?: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkauthstatusmessage">
  `SDKAuthStatusMessage`
</h3>

認証フロー中に発行されます。

```typescript theme={null}
type SDKAuthStatusMessage = {
  type: "auth_status";
  isAuthenticating: boolean;
  output: string[];
  error?: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdktaskstartedmessage">
  `SDKTaskStartedMessage`
</h3>

バックグラウンドタスクが開始したときに発行されます。`task_type` フィールドは、バックグラウンド Bash コマンドと [Monitor](#monitor) ウォッチの場合は `"local_bash"`、サブエージェントの場合は `"local_agent"`、またはリモートエージェントの場合は `"remote_agent"` です。

```typescript theme={null}
type SDKTaskStartedMessage = {
  type: "system";
  subtype: "task_started";
  task_id: string;
  tool_use_id?: string;
  description: string;
  task_type?: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdktaskprogressmessage">
  `SDKTaskProgressMessage`
</h3>

サブエージェントまたはバックグラウンドタスクが実行中に定期的に発行されます。`summary` フィールドは、[`agentProgressSummaries`](#options) が有効な場合にのみ入力されます。

```typescript theme={null}
type SDKTaskProgressMessage = {
  type: "system";
  subtype: "task_progress";
  task_id: string;
  tool_use_id?: string;
  description: string;
  subagent_type?: string;
  usage: {
    total_tokens: number;
    tool_uses: number;
    duration_ms: number;
  };
  last_tool_name?: string;
  summary?: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdktaskupdatedmessage">
  `SDKTaskUpdatedMessage`
</h3>

バックグラウンドタスクの状態が変更されたときに発行されます。例えば、`running` から `completed` に遷移するときなど。`patch` をローカルタスクマップ（`task_id` でキー付け）にマージしてください。`end_time` フィールドは Unix エポックタイムスタンプ（ミリ秒単位）で、`Date.now()` と比較可能です。

```typescript theme={null}
type SDKTaskUpdatedMessage = {
  type: "system";
  subtype: "task_updated";
  task_id: string;
  patch: {
    status?: "pending" | "running" | "completed" | "failed" | "killed";
    description?: string;
    end_time?: number;
    total_paused_ms?: number;
    error?: string;
    is_backgrounded?: boolean;
  };
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkbackgroundtaskschangedmessage">
  `SDKBackgroundTasksChangedMessage`
</h3>

ライブバックグラウンドタスクのセットが変更されるたびに発行されます。タスクが開始、完了、キル、またはフォアグラウンドエージェントがバックグラウンド化されるときです。`tasks` 配列はライブセット全体です。`task_started` および `task_notification` イベントをペアリングするのではなく、各ペイロードでキャッシュされたセットを置き換えてください。そのため、次のメンバーシップ変更は、逃したイベントを修正します。

これらのタスク単位のイベントに対する順序付けは指定されていないため、2 つのストリームを相関させないでください。

起動時には何も発行されません。セッションの CLI プロセスが開始または再開されるたびに空のセットにリセットし、次のメンバーシップ変更でそれを再入力させてください。

Claude Code v2.1.203 以降が必要です。

```typescript theme={null}
type SDKBackgroundTasksChangedMessage = {
  type: "system";
  subtype: "background_tasks_changed";
  tasks: {
    task_id: string;
    task_type: string;
    description: string;
  }[];
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkthinkingtokensmessage">
  `SDKThinkingTokensMessage`
</h3>

Claude が思考ブロック（編集されたものを含む）を生成している間に発行され、これまでに生成された思考トークンの実行中の推定値を含みます。`estimated_tokens` は現在の思考ブロックの実行合計で、`estimated_tokens_delta` はこのフレームで実行された増分です。進捗表示に使用してください。トップレベルエージェントループの最終カウントは結果メッセージの `usage.output_tokens` です。これは [サブエージェントトークンを含みません](/docs/ja/agent-sdk/cost-tracking#get-the-total-cost-of-a-query)。全体のツリーアカウンティングには [`modelUsage`](#modelusage) を使用してください。

Claude Code v2.1.153 以降が必要です。

```typescript theme={null}
type SDKThinkingTokensMessage = {
  type: "system";
  subtype: "thinking_tokens";
  estimated_tokens: number;
  estimated_tokens_delta: number;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkfilespersistedevent">
  `SDKFilesPersistedEvent`
</h3>

ファイルチェックポイントがディスクに永続化されたときに発行されます。

```typescript theme={null}
type SDKFilesPersistedEvent = {
  type: "system";
  subtype: "files_persisted";
  files: { filename: string; file_id: string }[];
  failed: { filename: string; error: string }[];
  processed_at: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkratelimitevent">
  `SDKRateLimitEvent`
</h3>

セッションがレート制限に遭遇したときに発行されます。

```typescript theme={null}
type SDKRateLimitEvent = {
  type: "rate_limit_event";
  rate_limit_info: {
    status: "allowed" | "allowed_warning" | "rejected";
    resetsAt?: number;
    utilization?: number;
    errorCode?: "credits_required";
    canUserPurchaseCredits?: boolean;
    hasChargeableSavedPaymentMethod?: boolean;
  };
  uuid: UUID;
  session_id: string;
};
```

`errorCode` が `"credits_required"` の場合、拒否は含まれた使用量が枯渇した claude.ai サブスクリプションからのもので、ユーザーが使用クレジットを購入するまでセッションは続行できません。`canUserPurchaseCredits` は認証されたユーザーがアカウントのクレジットを購入できるかどうかを示し、`hasChargeableSavedPaymentMethod` は保存された支払い方法がファイルにあるかどうかを示します。3 つのフィールドすべてはクレジット必須の拒否ではないレート制限イベントには存在しません。Claude Code v2.1.181 以降が必要です。

<h3 id="sdklocalcommandoutputmessage">
  `SDKLocalCommandOutputMessage`
</h3>

ローカルスラッシュコマンド（例：`/voice` または `/usage`）からの出力。トランスクリプトでアシスタント形式のテキストとして表示されます。

```typescript theme={null}
type SDKLocalCommandOutputMessage = {
  type: "system";
  subtype: "local_command_output";
  content: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkcommandschangedmessage">
  `SDKCommandsChangedMessage`
</h3>

利用可能なコマンドのセットがセッション中に変更されたときに発行されます。例えば、エージェントがサブディレクトリに入るときにスキルが検出されるなど。`commands` 配列は完全に更新されたリストであるため、キャッシュされたコマンドリストをこのペイロードで置き換えてください。`supportedCommands()` を再度呼び出すことは同等ではありません。そのメソッドは初期化時にキャプチャされたスナップショットを返し、セッション中の変更を反映しません。

```typescript theme={null}
type SDKCommandsChangedMessage = {
  type: "system";
  subtype: "commands_changed";
  commands: SlashCommand[];
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkpromptsuggestionmessage">
  `SDKPromptSuggestionMessage`
</h3>

`promptSuggestions` が有効な場合、各ターン後に発行されます。予測される次のユーザープロンプトを含みます。

```typescript theme={null}
type SDKPromptSuggestionMessage = {
  type: "prompt_suggestion";
  suggestion: string;
  uuid: UUID;
  session_id: string;
};
```

<h3 id="sdkconversationresetmessage">
  `SDKConversationResetMessage`
</h3>

セッションの会話がセッションを終了せずに置き換えられたときに発行されます。例えば、`/clear` の後、プランモード終了時、または新しい会話が開始されるときなど。`new_conversation_id` の下に空のトランスクリプトをマウントし、キャッシュされたセッションタイトルを破棄してください。

```typescript theme={null}
type SDKConversationResetMessage = {
  type: "conversation_reset";
  new_conversation_id: UUID;
  uuid: UUID;
  session_id: string;
};
```

SDK の公開された型定義は Claude Code v2.1.203 以降で `SDKConversationResetMessage` を宣言しています。v2.1.203 より前では、`SDKMessage` は型を宣言せずに参照していたため、`skipLibCheck` が無効な場合、`type === "conversation_reset"` での絞り込みは型チェックに失敗しました。

<h3 id="aborterror">
  `AbortError`
</h3>

中止操作のカスタムエラークラス。

```typescript theme={null}
class AbortError extends Error {}
```

<h2 id="sandbox-configuration">
  サンドボックス設定
</h2>

<h3 id="sandboxsettings">
  `SandboxSettings`
</h3>

サンドボックス動作の設定。これを使用して、コマンドサンドボックスを有効にし、ネットワーク制限をプログラムで設定します。

```typescript theme={null}
type SandboxSettings = {
  enabled?: boolean;
  failIfUnavailable?: boolean;
  autoAllowBashIfSandboxed?: boolean;
  excludedCommands?: string[];
  allowUnsandboxedCommands?: boolean;
  network?: SandboxNetworkConfig;
  filesystem?: SandboxFilesystemConfig;
  ignoreViolations?: Record<string, string[]>;
  enableWeakerNestedSandbox?: boolean;
  ripgrep?: { command: string; args?: string[] };
};
```

| プロパティ                       | 型                                                     | デフォルト       | 説明                                                                                                                                                                         |
| :-------------------------- | :---------------------------------------------------- | :---------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `enabled`                   | `boolean`                                             | `false`     | コマンド実行のサンドボックスモードを有効にします                                                                                                                                                   |
| `failIfUnavailable`         | `boolean`                                             | `true`      | `enabled` が `true` でもサンドボックスが起動できない場合、起動時に停止します。`false` に設定すると、stderr に警告を表示してサンドボックス外実行にフォールバックします                                                                        |
| `autoAllowBashIfSandboxed`  | `boolean`                                             | `true`      | サンドボックスが有効な場合、bash コマンドを自動承認します                                                                                                                                            |
| `excludedCommands`          | `string[]`                                            | `[]`        | 常にサンドボックス制限をバイパスするコマンド（例：`['docker']`）。これらはモデルの関与なしに自動的にサンドボックス外で実行されます                                                                                                    |
| `allowUnsandboxedCommands`  | `boolean`                                             | `true`      | モデルがサンドボックス外でコマンドを実行するようにリクエストすることを許可します。`true` の場合、モデルはツール入力で `dangerouslyDisableSandbox` を設定でき、[パーミッションシステム](#permissions-fallback-for-unsandboxed-commands) にフォールバックします |
| `network`                   | [`SandboxNetworkConfig`](#sandboxnetworkconfig)       | `undefined` | ネットワーク固有のサンドボックス設定                                                                                                                                                         |
| `filesystem`                | [`SandboxFilesystemConfig`](#sandboxfilesystemconfig) | `undefined` | 読み取り/書き込み制限のためのファイルシステム固有のサンドボックス設定                                                                                                                                        |
| `ignoreViolations`          | `Record<string, string[]>`                            | `undefined` | 違反カテゴリを無視するパターンのマップ（例：`{ file: ['/tmp/*'], network: ['localhost'] }`）                                                                                                      |
| `enableWeakerNestedSandbox` | `boolean`                                             | `false`     | 互換性のための弱いネストされたサンドボックスを有効にします                                                                                                                                              |
| `ripgrep`                   | `{ command: string; args?: string[] }`                | `undefined` | サンドボックス環境のカスタム ripgrep バイナリ設定                                                                                                                                              |

<Note>
  サンドボックスはプラットフォームサポートに依存し、Linux では `bubblewrap` や `socat` などのツールが必要です。`enabled` が `true` でサンドボックスが起動できない場合、`query()` は `subtype: "error_during_execution"` の `result` メッセージを報告し、理由を `errors` に含めます。単一メッセージの `query()` 呼び出しの場合、SDK はそのエラー結果を生成した後にスローするため、ループを try ブロックでラップして、それを超えて続行してください。エラーコントラクトについては [結果を処理する](/docs/ja/agent-sdk/agent-loop#handle-the-result) を参照してください。

  代わりにサンドボックス外で実行するには、`failIfUnavailable: false` を設定してください。
</Note>

<h4 id="example-usage">
  使用例
</h4>

```typescript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";

try {
  for await (const message of query({
    prompt: "Build and test my project",
    options: {
      sandbox: {
        enabled: true,
        autoAllowBashIfSandboxed: true,
        network: {
          allowLocalBinding: true
        }
      }
    }
  })) {
    if ("result" in message) console.log(message.result);
  }
} catch (error) {
  // A single-shot query() throws after yielding an error result,
  // such as when the sandbox can't start (failIfUnavailable defaults to true).
  console.log(`Session ended with an error: ${error}`);
}
```

<Warning>
  **Unix ソケットセキュリティ：** `allowUnixSockets` オプションは強力なシステムサービスへのアクセスを許可できます。例えば、`/var/run/docker.sock` を許可すると、Docker API 経由でホストシステムへの完全なアクセスが効果的に許可され、サンドボックス分離がバイパスされます。厳密に必要な Unix ソケットのみを許可し、各ソケットのセキュリティへの影響を理解してください。
</Warning>

<h3 id="sandboxnetworkconfig">
  `SandboxNetworkConfig`
</h3>

サンドボックスモードのネットワーク固有の設定。これらの設定は、親の [`SandboxSettings`](#sandboxsettings) で `enabled` が `true` の場合、サンドボックス化された Bash コマンドに適用されます。WebFetch ツールには適用されず、代わりに [パーミッションルール](/docs/ja/permissions#webfetch) を使用します。

```typescript theme={null}
type SandboxNetworkConfig = {
  allowedDomains?: string[];
  deniedDomains?: string[];
  allowManagedDomainsOnly?: boolean;
  allowLocalBinding?: boolean;
  allowUnixSockets?: string[];
  allowAllUnixSockets?: boolean;
  httpProxyPort?: number;
  socksProxyPort?: number;
};
```

| プロパティ                     | 型          | デフォルト       | 説明                                                                                                                                                             |
| :------------------------ | :--------- | :---------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `allowedDomains`          | `string[]` | `[]`        | サンドボックス化されたプロセスがアクセスできるドメイン名                                                                                                                                   |
| `deniedDomains`           | `string[]` | `[]`        | サンドボックス化されたプロセスがアクセスできないドメイン名。`allowedDomains` より優先されます                                                                                                        |
| `allowManagedDomainsOnly` | `boolean`  | `false`     | 管理設定のみ。[管理設定](/docs/ja/permissions#managed-settings) で設定された場合、管理設定からの `allowedDomains` エントリのみが尊重され、ユーザー、プロジェクト、またはローカル設定からのエントリは無視されます。SDK オプション経由で設定された場合は効果がありません |
| `allowLocalBinding`       | `boolean`  | `false`     | プロセスがローカルポートにバインドすることを許可します（例：開発サーバー）                                                                                                                          |
| `allowUnixSockets`        | `string[]` | `[]`        | プロセスがアクセスできる Unix ソケットパス（例：Docker ソケット）                                                                                                                        |
| `allowAllUnixSockets`     | `boolean`  | `false`     | すべての Unix ソケットへのアクセスを許可します                                                                                                                                     |
| `httpProxyPort`           | `number`   | `undefined` | ネットワークリクエスト用の HTTP プロキシポート                                                                                                                                     |
| `socksProxyPort`          | `number`   | `undefined` | ネットワークリクエスト用の SOCKS プロキシポート                                                                                                                                    |

<Note>
  組み込みサンドボックスプロキシは、リクエストされたホスト名に基づいて `allowedDomains` を強制し、TLS トラフィックを終了または検査しないため、[ドメインフロンティング](https://en.wikipedia.org/wiki/Domain_fronting) などの技術がそれをバイパスする可能性があります。詳細は [サンドボックスセキュリティの制限](/docs/ja/sandboxing#security-limitations) を参照し、TLS 終了プロキシの設定については [セキュアなデプロイ](/docs/ja/agent-sdk/secure-deployment#traffic-forwarding) を参照してください。
</Note>

<h3 id="sandboxfilesystemconfig">
  `SandboxFilesystemConfig`
</h3>

サンドボックスモードのファイルシステム固有の設定。

```typescript theme={null}
type SandboxFilesystemConfig = {
  allowWrite?: string[];
  denyWrite?: string[];
  denyRead?: string[];
};
```

| プロパティ        | 型          | デフォルト | 説明                    |
| :----------- | :--------- | :---- | :-------------------- |
| `allowWrite` | `string[]` | `[]`  | 書き込みアクセスを許可するファイルパターン |
| `denyWrite`  | `string[]` | `[]`  | 書き込みアクセスを拒否するファイルパターン |
| `denyRead`   | `string[]` | `[]`  | 読み取りアクセスを拒否するファイルパターン |

<h3 id="permissions-fallback-for-unsandboxed-commands">
  サンドボックス外コマンドのパーミッションフォールバック
</h3>

`allowUnsandboxedCommands` が有効な場合、モデルはツール入力で `dangerouslyDisableSandbox: true` を設定することで、サンドボックス外でコマンドを実行するようにリクエストできます。これらのリクエストは既存のパーミッションシステムにフォールバックします。つまり、`canUseTool` ハンドラーが呼び出され、カスタム認可ロジックを実装できます。下の例では、`isCommandAuthorized` は定義する認可チェックの代わりです。

<Note>
  **`excludedCommands` vs `allowUnsandboxedCommands`：**

  * `excludedCommands`：常にサンドボックスを自動的にバイパスするコマンドの静的リスト（例：`['docker']`）。モデルはこれを制御できません。
  * `allowUnsandboxedCommands`：モデルがツール入力で `dangerouslyDisableSandbox: true` を設定することで、実行時にサンドボックス外実行をリクエストすることを許可します。
</Note>

```typescript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Deploy my application",
  options: {
    sandbox: {
      enabled: true,
      allowUnsandboxedCommands: true // モデルはサンドボックス外実行をリクエストできます
    },
    permissionMode: "default",
    canUseTool: async (tool, input) => {
      // モデルがサンドボックスをバイパスするようにリクエストしているかチェック
      if (tool === "Bash" && input.dangerouslyDisableSandbox) {
        // モデルはこのコマンドをサンドボックス外で実行するようにリクエストしています
        console.log(`Unsandboxed command requested: ${input.command}`);

        if (isCommandAuthorized(input.command)) {
          return { behavior: "allow" as const, updatedInput: input };
        }
        return {
          behavior: "deny" as const,
          message: "Command not authorized for unsandboxed execution"
        };
      }
      return { behavior: "allow" as const, updatedInput: input };
    }
  }
})) {
  if ("result" in message) console.log(message.result);
}
```

このパターンにより、以下が可能になります：

* **モデルリクエストを監査：** モデルがサンドボックス外実行をリクエストしたときにログします
* **許可リストを実装：** 特定のコマンドのみがサンドボックス外で実行されることを許可します
* **承認ワークフローを追加：** 特権操作に明示的な認可を要求します

<Warning>
  `dangerouslyDisableSandbox: true` で実行されるコマンドはシステムへの完全なアクセスを持ちます。`canUseTool` ハンドラーがこれらのリクエストを慎重に検証することを確認してください。

  `permissionMode` が `bypassPermissions` に設定され、`allowUnsandboxedCommands` が有効な場合、モデルは承認プロンプトなしにサンドボックス外でコマンドを自律的に実行できます（明示的な [`ask` ルール](/docs/ja/agent-sdk/permissions#how-permissions-are-evaluated) はそれでも強制します）。この組み合わせにより、モデルはサンドボックス分離を静かにエスケープできます。
</Warning>

<h2 id="see-also">
  関連項目
</h2>

* [SDK 概要](/docs/ja/agent-sdk/overview) - 一般的な SDK 概念
* [Python SDK リファレンス](/docs/ja/agent-sdk/python) - Python SDK ドキュメント
* [CLI リファレンス](/docs/ja/cli-reference) - コマンドラインインターフェース
* [一般的なワークフロー](/docs/ja/common-workflows) - ステップバイステップガイド
