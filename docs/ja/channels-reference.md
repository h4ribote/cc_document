> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# チャネルリファレンス

> webhook、アラート、チャットメッセージを Claude Code セッションにプッシュする MCP サーバーを構築します。チャネルコントラクトのリファレンス：機能宣言、通知イベント、返信ツール、送信者ゲーティング、権限リレー。

<Note>
  チャネルは[リサーチプレビュー](/docs/ja/channels#research-preview)段階にあります。Team および Enterprise 組織は[明示的に有効化](/docs/ja/channels#enterprise-controls)する必要があります。
</Note>

チャネルは、Claude Code セッションにイベントをプッシュする MCP サーバーで、Claude がターミナルの外で発生していることに反応できるようにします。

一方向または双方向のチャネルを構築できます。一方向チャネルは、アラート、webhook、または監視イベントを転送して Claude が対応できるようにします。チャットブリッジのような双方向チャネルは、Claude がメッセージを返送できるように[返信ツールを公開](#expose-a-reply-tool)することもできます。信頼できる送信者パスを持つチャネルは、[権限プロンプトをリレー](#relay-permission-prompts)することを選択して、ツール使用をリモートで承認または拒否できます。

このページでは以下をカバーしています：

* [概要](#overview)：チャネルの仕組み
* [必要なもの](#what-you-need)：要件と一般的な手順
* [例：webhook レシーバーを構築](#example-build-a-webhook-receiver)：最小限の一方向ウォークスルー
* [サーバーオプション](#server-options)：コンストラクタフィールド
* [通知フォーマット](#notification-format)：イベントペイロードと配信動作
* [返信ツールを公開](#expose-a-reply-tool)：Claude がメッセージを返送できるようにする
* [インバウンドメッセージをゲート](#gate-inbound-messages)：プロンプトインジェクションを防ぐための送信者チェック
* [権限プロンプトをリレー](#relay-permission-prompts)：ツール承認プロンプトをリモートチャネルに転送

既存のチャネルを使用する場合は、[チャネル](/docs/ja/channels)を参照してください。Telegram、Discord、iMessage、および fakechat はリサーチプレビューに含まれています。

<h2 id="overview">
  概要
</h2>

チャネルは、Claude Code と同じマシン上で実行される[MCP](https://modelcontextprotocol.io) サーバーです。Claude Code はそれをサブプロセスとして生成し、stdio 経由で通信します。チャネルサーバーは、外部システムと Claude Code セッション間のブリッジです：

* **チャットプラットフォーム**（Telegram、Discord）：プラグインはローカルで実行され、プラットフォームの API をポーリングして新しいメッセージを取得します。誰かがボットに DM を送信すると、プラグインはメッセージを受け取り、Claude に転送します。公開する URL は不要です。
* **Webhook**（CI、監視）：サーバーはローカル HTTP ポートでリッスンします。外部システムがそのポートに POST し、サーバーはペイロードを Claude にプッシュします。

<img src="https://mintcdn.com/claude-code/9FG0ZKj9uKYiHmbi/images/channel-architecture.svg?fit=max&auto=format&n=9FG0ZKj9uKYiHmbi&q=85&s=9a037b7da80184ae49015c0256b21a1f" alt="外部システムがローカルチャネルサーバーに接続し、stdio 経由で Claude Code と通信するアーキテクチャ図" width="600" height="220" data-path="images/channel-architecture.svg" />

<h2 id="what-you-need">
  必要なもの
</h2>

唯一のハード要件は、[`@modelcontextprotocol/sdk`](https://www.npmjs.com/package/@modelcontextprotocol/sdk) パッケージと Node.js 互換ランタイムです。[Bun](https://bun.sh)、[Node](https://nodejs.org)、[Deno](https://deno.com) すべて動作します。リサーチプレビューの事前構築プラグインは Bun を使用していますが、チャネルはそうである必要はありません。

サーバーは以下を実行する必要があります：

1. `claude/channel` 機能を宣言して、Claude Code が通知リスナーを登録するようにする
2. 何かが発生したときに `notifications/claude/channel` イベントを発行する
3. [stdio トランスポート](https://modelcontextprotocol.io/docs/concepts/transports#standard-io)経由で接続する（Claude Code はサーバーをサブプロセスとして生成）

[サーバーオプション](#server-options)と[通知フォーマット](#notification-format)セクションでは、これらのそれぞれについて詳しく説明しています。完全なウォークスルーについては、[例：webhook レシーバーを構築](#example-build-a-webhook-receiver)を参照してください。

リサーチプレビュー中、カスタムチャネルは[承認許可リスト](/docs/ja/channels#supported-channels)にありません。ローカルでテストするには `--dangerously-load-development-channels` を使用してください。詳細については、[リサーチプレビュー中のテスト](#test-during-the-research-preview)を参照してください。

<h2 id="example-build-a-webhook-receiver">
  例：webhook レシーバーを構築
</h2>

このウォークスルーでは、HTTP リクエストをリッスンして Claude Code セッションに転送する単一ファイルサーバーを構築します。終了時には、CI パイプライン、監視アラート、または `curl` コマンドなど、HTTP POST を送信できるものはすべて、Claude にイベントをプッシュできます。

この例では、組み込み HTTP サーバーと TypeScript サポートのために [Bun](https://bun.sh) をランタイムとして使用しています。代わりに [Node](https://nodejs.org) または [Deno](https://deno.com) を使用できます。唯一の要件は [MCP SDK](https://www.npmjs.com/package/@modelcontextprotocol/sdk) です。

<Steps>
  <Step title="プロジェクトを作成">
    新しいディレクトリを作成して MCP SDK をインストールします：

    ```bash theme={null}
    mkdir webhook-channel && cd webhook-channel
    bun add @modelcontextprotocol/sdk
    ```
  </Step>

  <Step title="チャネルサーバーを記述">
    `webhook.ts` というファイルを作成します。これはチャネルサーバー全体です：stdio 経由で Claude Code に接続し、ポート 8788 で HTTP POST をリッスンします。リクエストが到着すると、本文をチャネルイベントとして Claude にプッシュします。

    ```ts title="webhook.ts" theme={null}
    #!/usr/bin/env bun
    import { Server } from '@modelcontextprotocol/sdk/server/index.js'
    import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'

    // MCP サーバーを作成してチャネルとして宣言
    const mcp = new Server(
      { name: 'webhook', version: '0.0.1' },
      {
        // このキーがチャネルにする — Claude Code はそれのリスナーを登録
        capabilities: { experimental: { 'claude/channel': {} } },
        // Claude のシステムプロンプトに追加されるため、これらのイベントの処理方法を知っている
        instructions: 'Events from the webhook channel arrive as <channel source="webhook" ...>. They are one-way: read them and act, no reply expected.',
      },
    )

    // stdio 経由で Claude Code に接続（Claude Code はこのプロセスを生成）
    await mcp.connect(new StdioServerTransport())

    // すべての POST を Claude に転送する HTTP サーバーを開始
    Bun.serve({
      port: 8788,  // 任意のオープンポートが機能
      // localhost のみ：このマシンの外からは何も POST できない
      hostname: '127.0.0.1',
      async fetch(req) {
        const body = await req.text()
        await mcp.notification({
          method: 'notifications/claude/channel',
          params: {
            content: body,  // <channel> タグの本文になる
            // 各キーはタグ属性になる、例：<channel path="/" method="POST">
            meta: { path: new URL(req.url).pathname, method: req.method },
          },
        })
        return new Response('ok')
      },
    })
    ```

    ファイルは順番に 3 つのことを実行します：

    * **サーバー設定**：`claude/channel` をその機能に含む MCP サーバーを作成します。これが Claude Code にこれがチャネルであることを伝えます。[`instructions`](#server-options) 文字列は Claude のシステムプロンプトに入ります：Claude に期待するイベント、返信するかどうか、返信する場合はどのように返信を処理するかを伝えます。
    * **Stdio 接続**：stdin/stdout 経由で Claude Code に接続します。これは任意の [MCP サーバー](https://modelcontextprotocol.io/docs/concepts/transports#standard-io) の標準です：Claude Code はそれをサブプロセスとして生成します。
    * **HTTP リスナー**：ポート 8788 でローカル Web サーバーを開始します。すべての POST 本文は `mcp.notification()` 経由でチャネルイベントとして Claude に転送されます。`content` はイベント本文になり、各 `meta` エントリは `<channel>` タグの属性になります。リスナーは `mcp` インスタンスへのアクセスが必要なため、同じプロセスで実行されます。より大きなプロジェクトの場合は、別のモジュールに分割できます。
  </Step>

  <Step title="Claude Code にサーバーを登録">
    Claude Code がそれを開始する方法を知るように、MCP 設定にサーバーを追加します。同じディレクトリのプロジェクトレベル `.mcp.json` の場合は、相対パスを使用します。`~/.claude.json` のユーザーレベル設定の場合は、サーバーが任意のプロジェクトから見つかるように完全な絶対パスを使用します：

    ```json title=".mcp.json" theme={null}
    {
      "mcpServers": {
        "webhook": { "command": "bun", "args": ["./webhook.ts"] }
      }
    }
    ```

    Claude Code は起動時に MCP 設定を読み込み、各サーバーをサブプロセスとして生成します。
  </Step>

  <Step title="テスト">
    リサーチプレビュー中、カスタムチャネルは許可リストにないため、開発フラグで Claude Code を開始します：

    ```bash theme={null}
    claude --dangerously-load-development-channels server:webhook
    ```

    このプロジェクトで初めてセッションを開始するとき、Claude Code は `.mcp.json` から新しいサーバーを使用する前に同意を求めます。ダイアログは'このプロジェクトで見つかった新しい MCP サーバー：webhook'と報告します。**このMCPサーバーを使用** を選択して続行します。

    Claude Code が起動すると、MCP 設定を読み込み、`webhook.ts` をサブプロセスとして生成し、HTTP リスナーは設定したポート（この例では 8788）で自動的に開始されます。サーバーを自分で実行する必要はありません。

    スタートアップバナーの下の薄い通知がチャネルが登録されたことを確認します：`Channels (experimental) messages from server:webhook inject directly in this session · restart without --dangerously-load-development-channels to stop`。

    '組織ポリシーによってブロックされています'が表示される場合は、組織管理者が最初に [チャネルを有効化](/docs/ja/channels#enterprise-controls) する必要があります。

    別のターミナルで、HTTP POST でメッセージを送信して webhook をシミュレートします。この例は、CI 失敗アラートをポート 8788（または設定したポート）に送信します：

    ```bash theme={null}
    curl -X POST localhost:8788 -d "build failed on main: https://ci.example.com/run/1234"
    ```

    ペイロードは Claude Code セッションに `<channel>` タグとして到着します：

    ```text theme={null}
    <channel source="webhook" path="/" method="POST">build failed on main: https://ci.example.com/run/1234</channel>
    ```

    Claude Code ターミナルでは、Claude がメッセージを受け取り、応答を開始するのが見えます：ファイルを読み込み、コマンドを実行、またはメッセージが要求するもの。これは一方向チャネルなので、Claude はセッションで動作しますが、webhook を通じて何も返送しません。返信を追加するには、[返信ツールを公開](#expose-a-reply-tool) を参照してください。

    イベントが到着しない場合、診断は `curl` が返したものに依存します：

    * **`curl` は成功するが Claude に何も到着しない**：セッションで `/mcp` を実行してサーバーのステータスを確認します。「接続に失敗」は通常、サーバーファイルの依存関係またはインポートエラーを意味します。`~/.claude/debug/<session-id>.txt` のデバッグログで stderr トレースを確認してください。
    * **`curl` が「接続が拒否されました」で失敗**：ポートはまだバインドされていないか、以前の実行からの古いプロセスがそれを保持しています。`lsof -i :<port>` は何がリッスンしているかを示します。セッションを再開する前に古いプロセスを `kill` してください。
  </Step>
</Steps>

[fakechat サーバー](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/fakechat) は、Web UI、ファイル添付、および双方向チャットの返信ツールでこのパターンを拡張します。

<h2 id="test-during-the-research-preview">
  リサーチプレビュー中のテスト
</h2>

リサーチプレビュー中、すべてのチャネルは登録するために[承認許可リスト](/docs/ja/channels#research-preview)にある必要があります。開発フラグは、確認プロンプトの後、特定のエントリの許可リストをバイパスします。この例は両方のエントリタイプを示しています：

```bash theme={null}
# 開発中のプラグインをテスト
claude --dangerously-load-development-channels plugin:yourplugin@yourmarketplace

# ベアな .mcp.json サーバーをテスト（プラグインラッパーはまだない）
claude --dangerously-load-development-channels server:webhook
```

バイパスはエントリごとです。このフラグを `--channels` と組み合わせても、バイパスは `--channels` エントリに拡張されません。リサーチプレビュー中、承認許可リストは Anthropic がキュレーションしているため、チャネルは構築とテスト中は開発フラグに留まります。

<Note>
  このフラグは許可リストのみをスキップします。`channelsEnabled` 組織ポリシーは引き続き適用されます。信頼できないソースからチャネルを実行するために使用しないでください。
</Note>

<h2 id="server-options">
  サーバーオプション
</h2>

チャネルは [`Server`](https://modelcontextprotocol.io/docs/concepts/servers) コンストラクタでこれらのオプションを設定します。`instructions` と `capabilities.tools` フィールドは[標準 MCP](https://modelcontextprotocol.io/docs/concepts/servers) です。`capabilities.experimental['claude/channel']` と `capabilities.experimental['claude/channel/permission']` はチャネル固有の追加です：

| フィールド                                                    | タイプ      | 説明                                                                                                                                                                   |
| :------------------------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `capabilities.experimental['claude/channel']`            | `object` | 必須。常に `{}`。存在は通知リスナーを登録します。                                                                                                                                          |
| `capabilities.experimental['claude/channel/permission']` | `object` | オプション。常に `{}`。このチャネルが権限リレーリクエストを受け取ることができることを宣言します。宣言されると、Claude Code はツール承認プロンプトをチャネルに転送して、リモートで承認または拒否できるようにします。[権限プロンプトをリレー](#relay-permission-prompts)を参照してください。 |
| `capabilities.tools`                                     | `object` | 双方向のみ。常に `{}`。標準 MCP ツール機能。[返信ツールを公開](#expose-a-reply-tool)を参照してください。                                                                                                |
| `instructions`                                           | `string` | 推奨。Claude のシステムプロンプトに追加されます。Claude に期待するイベント、`<channel>` タグ属性の意味、返信するかどうか、返信する場合はどのツールを使用するか、どの属性を返送するか（`chat_id` など）を伝えます。                                          |

一方向チャネルを作成するには、`capabilities.tools` を省略します。この例は、チャネル機能、ツール、および設定された命令を含む双方向セットアップを示しています：

```ts theme={null}
import { Server } from '@modelcontextprotocol/sdk/server/index.js'

const mcp = new Server(
  { name: 'your-channel', version: '0.0.1' },
  {
    capabilities: {
      experimental: { 'claude/channel': {} },  // チャネルリスナーを登録
      tools: {},  // 一方向チャネルの場合は省略
    },
    // Claude のシステムプロンプトに追加されるため、イベントの処理方法を知っている
    instructions: 'Messages arrive as <channel source="your-channel" ...>. Reply with the reply tool.',
  },
)
```

イベントをプッシュするには、メソッド `notifications/claude/channel` で `mcp.notification()` を呼び出します。パラメータは次のセクションにあります。

<h2 id="notification-format">
  通知フォーマット
</h2>

サーバーは `notifications/claude/channel` を 2 つのパラメータで発行します：

| フィールド     | タイプ                      | 説明                                                                                                                                               |
| :-------- | :----------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `content` | `string`                 | イベント本文。`<channel>` タグの本文として配信されます。                                                                                                               |
| `meta`    | `Record<string, string>` | オプション。各エントリは `<channel>` タグの属性になり、chat ID、送信者名、またはアラート重大度などのルーティングコンテキストを提供します。キーは識別子である必要があります：文字、数字、アンダースコアのみ。ハイフンまたは他の文字を含むキーはサイレントにドロップされます。 |

サーバーは `Server` インスタンスで `mcp.notification()` を呼び出してイベントをプッシュします。この例は、2 つのメタキーを持つ CI 失敗アラートをプッシュします：

```ts theme={null}
await mcp.notification({
  method: 'notifications/claude/channel',
  params: {
    content: 'build failed on main: https://ci.example.com/run/1234',
    meta: { severity: 'high', run_id: '1234' },
  },
})
```

イベントは Claude のコンテキストに `<channel>` タグでラップされて到着します。`source` 属性はサーバーの設定名から自動的に設定されます：

```text theme={null}
<channel source="your-channel" severity="high" run_id="1234">
build failed on main: https://ci.example.com/run/1234
</channel>
```

通知は確認されません。`mcp.notification()` の `await` は、メッセージがトランスポートに書き込まれるときに解決され、Claude が処理したときではありません。セッションがチャネルとしてサーバーを読み込んでいない場合、または組織ポリシーがそれをブロックしている場合、イベントはサーバーにエラーが返されることなくサイレントにドロップされます。

配信確認が必要な場合は、サーバーでイベント状態を追跡し、Claude が状態を報告するために呼び出せる[返信ツール](#expose-a-reply-tool)を公開します。

イベントはセッションにキューイングされ、順番に処理されます。Claude がビジーの間に複数の通知が到着した場合、次のターンで一緒に配信され、Claude はそれらをグループとして処理します。独立したイベントストリームを同時に処理するには、別のセッションを実行します。

<h2 id="expose-a-reply-tool">
  返信ツールを公開
</h2>

チャネルが双方向の場合、アラートフォワーダーではなくチャットブリッジのような場合、Claude がメッセージを返送するために呼び出せる標準 [MCP ツール](https://modelcontextprotocol.io/docs/concepts/tools)を公開します。ツール登録に関するチャネル固有のものはありません。返信ツールには 3 つのコンポーネントがあります：

1. `Server` コンストラクタ機能に `tools: {}` エントリがあり、Claude Code がツールを検出できるようにする
2. ツールのスキーマを定義し、送信ロジックを実装するツールハンドラー
3. Claude に何時どのようにツールを呼び出すかを伝える `Server` コンストラクタの `instructions` 文字列

これらを[上記の webhook レシーバー](#example-build-a-webhook-receiver)に追加するには：

<Steps>
  <Step title="ツール検出を有効化">
    `webhook.ts` の `Server` コンストラクタで、Claude Code がサーバーがツールを提供することを知るように、機能に `tools: {}` を追加します：

    ```ts theme={null}
    capabilities: {
      experimental: { 'claude/channel': {} },
      tools: {},  // ツール検出を有効化
    },
    ```
  </Step>

  <Step title="返信ツールを登録">
    以下を `webhook.ts` に追加します。`import` はファイルの上部の他のインポートと一緒に移動します。2 つのハンドラーは `Server` コンストラクタと `mcp.connect()` の間に移動します。これは、Claude が `chat_id` と `text` で呼び出せる `reply` ツールを登録します：

    ```ts theme={null}
    // webhook.ts の上部に追加
    import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js'

    // Claude は起動時にこれをクエリして、サーバーが提供するツールを検出
    mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [{
        name: 'reply',
        description: 'Send a message back over this channel',
        // inputSchema は Claude に渡すべき引数を伝える
        inputSchema: {
          type: 'object',
          properties: {
            chat_id: { type: 'string', description: 'The conversation to reply in' },
            text: { type: 'string', description: 'The message to send' },
          },
          required: ['chat_id', 'text'],
        },
      }],
    }))

    // Claude がツールを呼び出したいときにこれを呼び出す
    mcp.setRequestHandler(CallToolRequestSchema, async req => {
      if (req.params.name === 'reply') {
        const { chat_id, text } = req.params.arguments as { chat_id: string; text: string }
        // send() はアウトバウンド：チャットプラットフォームに POST、またはローカル
        // テストの場合は下の完全な例に示されている SSE ブロードキャスト。
        send(`Reply to ${chat_id}: ${text}`)
        return { content: [{ type: 'text', text: 'sent' }] }
      }
      throw new Error(`unknown tool: ${req.params.name}`)
    })
    ```
  </Step>

  <Step title="命令を更新">
    `Server` コンストラクタの `instructions` 文字列を更新して、Claude がツール経由で返信をルーティングすることを知るようにします。この例は、Claude にインバウンドタグから `chat_id` を渡すように伝えます：

    ```ts theme={null}
    instructions: 'Messages arrive as <channel source="webhook" chat_id="...">. Reply with the reply tool, passing the chat_id from the tag.'
    ```
  </Step>
</Steps>

以下は、双方向サポート付きの完全な `webhook.ts` です。アウトバウンド返信は [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)（SSE）を使用して `GET /events` でストリーミングされるため、`curl -N localhost:8788/events` はそれらをライブで見ることができます。インバウンドチャットは `POST /` に到着します：

```ts title="返信ツール付きの完全な webhook.ts' expandable theme={null}
#!/usr/bin/env bun
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js'

// --- アウトバウンド：/events の任意の curl -N リスナーに書き込み ---
// 実際のブリッジはチャットプラットフォームに POST します。
const listeners = new Set<(chunk: string) => void>()
function send(text: string) {
  const chunk = text.split('\n').map(l => `data: ${l}\n`).join('') + '\n'
  for (const emit of listeners) emit(chunk)
}

const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    capabilities: {
      experimental: { 'claude/channel': {} },
      tools: {},
    },
    instructions: 'Messages arrive as <channel source="webhook" chat_id="...">. Reply with the reply tool, passing the chat_id from the tag.',
  },
)

mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'reply',
    description: 'Send a message back over this channel',
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'The conversation to reply in' },
        text: { type: 'string', description: 'The message to send' },
      },
      required: ['chat_id', 'text'],
    },
  }],
}))

mcp.setRequestHandler(CallToolRequestSchema, async req => {
  if (req.params.name === 'reply') {
    const { chat_id, text } = req.params.arguments as { chat_id: string; text: string }
    send(`Reply to ${chat_id}: ${text}`)
    return { content: [{ type: 'text', text: 'sent' }] }
  }
  throw new Error(`unknown tool: ${req.params.name}`)
})

await mcp.connect(new StdioServerTransport())

let nextId = 1
Bun.serve({
  port: 8788,
  hostname: '127.0.0.1',
  idleTimeout: 0,  // アイドル SSE ストリームを閉じない
  async fetch(req) {
    const url = new URL(req.url)

    // GET /events：SSE ストリーム、curl -N が Claude の返信をライブで見ることができる
    if (req.method === 'GET' && url.pathname === '/events') {
      const stream = new ReadableStream({
        start(ctrl) {
          ctrl.enqueue(': connected\n\n')  // curl が何かをすぐに表示するように
          const emit = (chunk: string) => ctrl.enqueue(chunk)
          listeners.add(emit)
          req.signal.addEventListener('abort', () => listeners.delete(emit))
        },
      })
      return new Response(stream, {
        headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
      })
    }

    // POST：チャネルイベントとして Claude に転送
    const body = await req.text()
    const chat_id = String(nextId++)
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: {
        content: body,
        meta: { chat_id, path: url.pathname, method: req.method },
      },
    })
    return new Response('ok')
  },
})
```

[fakechat サーバー](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/fakechat)は、ファイル添付とメッセージ編集を含むより完全な例を示しています。

<h2 id="gate-inbound-messages">
  インバウンドメッセージをゲート
</h2>

ゲートなしチャネルはプロンプトインジェクションベクトルです。エンドポイントに到達できる誰もが Claude の前にテキストを置くことができます。チャットプラットフォームまたはパブリックエンドポイントをリッスンするチャネルは、何かを発行する前に実際の送信者チェックが必要です。

`mcp.notification()` を呼び出す前に、送信者を許可リストに対してチェックします。この例は、許可リストにない送信者からのメッセージをドロップします：

```ts theme={null}
const allowed = new Set(loadAllowlist())  // access.json またはそれに相当するもの

// メッセージハンドラー内、発行する前：
if (!allowed.has(message.from.id)) {  // 送信者、ルームではない
  return  // サイレントにドロップ
}
await mcp.notification({ ... })
```

チャットまたはルーム ID ではなく、送信者の ID でゲートします：例では `message.from.id`、`message.chat.id` ではありません。グループチャットでは、これらは異なり、ルームでゲートすると、許可リストに登録されたグループ内の誰もがセッションにメッセージを注入できます。

[Telegram](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram) と [Discord](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/discord) チャネルは同じ方法で送信者許可リストでゲートします。ペアリングでリストをブートストラップします：ユーザーがボットに DM を送信し、ボットはペアリングコードで返信し、ユーザーが Claude Code セッションで承認し、プラットフォーム ID が追加されます。完全なペアリングフローについては、いずれかの実装を参照してください。[iMessage](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage) チャネルは異なるアプローチを取ります：起動時にメッセージデータベースからユーザー自身のアドレスを検出し、それらを自動的に通します。他の送信者はハンドルで追加されます。

<h2 id="relay-permission-prompts">
  権限プロンプトをリレー
</h2>

Claude が承認が必要なツールを呼び出すと、ローカルターミナルダイアログが開き、セッションが待機します。双方向チャネルは、同じプロンプトを並行して受け取り、別のデバイスでそれをリレーすることを選択できます。両方がライブのままです：ターミナルまたは電話で答えることができ、Claude Code は最初に到着した答えを適用し、もう一方を閉じます。

リレーは `Bash`、`Write`、`Edit` などのツール使用承認をカバーします。プロジェクト信頼と MCP サーバー同意ダイアログはリレーされません。これらはローカルターミナルにのみ表示されます。

<h3 id="how-relay-works">
  リレーの仕組み
</h3>

権限プロンプトが開くと、リレーループには 4 つのステップがあります：

1. Claude Code は短いリクエスト ID を生成し、サーバーに通知
2. サーバーはプロンプトと ID をチャットアプリに転送
3. リモートユーザーは yes または no と ID で返信
4. インバウンドハンドラーは返信を判定に解析し、Claude Code は ID が開いているリクエストと一致する場合のみそれを適用

ローカルターミナルダイアログはこのすべてを通じて開いたままです。ターミナルの誰かがリモート判定が到着する前に答えた場合、その答えが代わりに適用され、保留中のリモートリクエストはドロップされます。

<img src="https://mintcdn.com/claude-code/9FG0ZKj9uKYiHmbi/images/channel-permission-relay.svg?fit=max&auto=format&n=9FG0ZKj9uKYiHmbi&q=85&s=97d57f128f0da55f105ab1e3a7e10240" alt="シーケンス図：Claude Code は権限リクエスト通知をチャネルサーバーに送信し、サーバーはプロンプトと ID をチャットアプリにフォーマットして送信し、人間は判定で返信し、サーバーはその返信を権限通知に解析して Claude Code に戻す" width="600" height="230" data-path="images/channel-permission-relay.svg" />

<h3 id="permission-request-fields">
  権限リクエストフィールド
</h3>

Claude Code からのアウトバウンド通知は `notifications/claude/channel/permission_request` です。[チャネル通知](#notification-format)のように、トランスポートは標準 MCP ですが、メソッドとスキーマは Claude Code 拡張です。`params` オブジェクトには、サーバーが発信プロンプトにフォーマットする 4 つの文字列フィールドがあります：

| フィールド           | 説明                                                                                                                                                                                             |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `request_id`    | `a`-`z` から `l` なしで描画された 5 つの小文字。電話で入力するときに `1` または `I` として読まれることはありません。発信プロンプトに含めて、返信で反映できるようにします。Claude Code は発行した ID を持つ判定のみを受け入れます。ローカルターミナルダイアログはこの ID を表示しないため、アウトバウンドハンドラーはそれを学ぶ唯一の方法です。 |
| `tool_name`     | Claude が使用したいツールの名前、例えば `Bash` または `Write`。                                                                                                                                                    |
| `description`   | この特定のツール呼び出しが何をするかの人間が読める要約。ローカルターミナルダイアログが表示するのと同じテキスト。Bash 呼び出しの場合、これは Claude のコマンドの説明、または何も与えられていない場合はコマンド自体です。                                                                             |
| `input_preview` | ツールの引数を JSON 文字列として、200 文字に切り詰めたもの。Bash の場合はコマンド。Write の場合はファイルパスとコンテンツのプレフィックス。1 行のメッセージの余地しかない場合はプロンプトから省略します。サーバーは何を表示するかを決定します。                                                            |

サーバーが返送する判定は `notifications/claude/channel/permission` で、2 つのフィールド：上記の ID を反映する `request_id` と、`'allow'` または `'deny'` に設定された `behavior`。Allow はツール呼び出しを続行させます。Deny はそれを拒否し、ローカルダイアログで No と答えるのと同じです。どちらの判定も将来の呼び出しに影響しません。

<h3 id="add-relay-to-a-chat-bridge">
  チャットブリッジにリレーを追加
</h3>

双方向チャネルに権限リレーを追加するには、3 つのコンポーネントが必要です：

1. `Server` コンストラクタの `experimental` 機能の下に `claude/channel/permission: {}` エントリがあり、Claude Code がプロンプトを転送することを知るようにする
2. `notifications/claude/channel/permission_request` の通知ハンドラーがプロンプトをフォーマットしてプラットフォーム API 経由で送信
3. インバウンドメッセージハンドラーの確認が `yes <id>` または `no <id>` を認識し、テキストを Claude に転送する代わりに `notifications/claude/channel/permission` 判定を発行

チャネルが[送信者を認証](#gate-inbound-messages)する場合のみ機能を宣言してください。チャネル経由で返信できる誰もがセッションのツール使用を承認または拒否できるためです。

これらを[返信ツールを公開](#expose-a-reply-tool)で組み立てられたような双方向チャットブリッジに追加するには：

<Steps>
  <Step title="権限機能を宣言">
    `Server` コンストラクタで、`experimental` の下に `claude/channel` と一緒に `claude/channel/permission: {}` を追加します：

    ```ts theme={null}
    capabilities: {
      experimental: {
        'claude/channel': {},
        'claude/channel/permission': {},  // 権限リレーにオプトイン
      },
      tools: {},
    },
    ```
  </Step>

  <Step title="受信リクエストを処理">
    `Server` コンストラクタと `mcp.connect()` の間に通知ハンドラーを登録します。権限ダイアログが開くと、Claude Code は[4 つのリクエストフィールド](#permission-request-fields)で呼び出します。ハンドラーはプロンプトをプラットフォーム用にフォーマットし、ID で返信するための命令を含めます：

    ```ts theme={null}
    import { z } from 'zod'

    // setNotificationHandler はメソッドフィールドで z.literal にルーティングするため、
    // このスキーマはバリデータとディスパッチキーの両方です
    const PermissionRequestSchema = z.object({
      method: z.literal('notifications/claude/channel/permission_request'),
      params: z.object({
        request_id: z.string(),     // 5 つの小文字、プロンプトに逐語的に含める
        tool_name: z.string(),      // 例：'Bash'、'Write'
        description: z.string(),    // この呼び出しが何をするかの人間が読める要約
        input_preview: z.string(),  // ツール引数を JSON として、約 200 文字に切り詰め
      }),
    })

    mcp.setNotificationHandler(PermissionRequestSchema, async ({ params }) => {
      // send() はアウトバウンド：チャットプラットフォームに POST、またはローカル
      // テストの場合は下の完全な例に示されている SSE ブロードキャスト。
      send(
        `Claude wants to run ${params.tool_name}: ${params.description}\n\n` +
        // 命令の ID はステップ 3 でインバウンドハンドラーが解析するもの
        `Reply "yes ${params.request_id}" or "no ${params.request_id}"`,
      )
    })
    ```
  </Step>

  <Step title="インバウンドハンドラーで判定をインターセプト">
    インバウンドハンドラーは、プラットフォームからメッセージを受け取るループまたはコールバック：[送信者でゲート](#gate-inbound-messages)し、`notifications/claude/channel` を発行してチャットを Claude に転送する同じ場所。判定フォーマットを認識し、チャット転送呼び出しの代わりに権限通知を発行するチェックを追加します。

    正規表現は Claude Code が生成する ID フォーマットと一致します：5 文字、`l` なし。`/i` フラグは電話オートコレクトが返信を大文字にすることを許容します。送信する前に取得した ID を小文字にします。

    ```ts theme={null}
    // 'y abcde'、'yes abcde'、'n abcde'、'no abcde'と一致
    // [a-km-z] は Claude Code が使用する ID アルファベット（小文字、'l'をスキップ）
    // /i はオートコレクト大文字を許容；送信する前に取得を小文字にする
    const PERMISSION_REPLY_RE = /^\s*(y|yes|n|no)\s+([a-km-z]{5})\s*$/i

    async function onInbound(message: PlatformMessage) {
      if (!allowed.has(message.from.id)) return  // 最初に送信者でゲート

      const m = PERMISSION_REPLY_RE.exec(message.text)
      if (m) {
        // m[1] は判定単語、m[2] はリクエスト ID
        // チャットの代わりに Claude Code に判定通知を発行
        await mcp.notification({
          method: 'notifications/claude/channel/permission',
          params: {
            request_id: m[2].toLowerCase(),  // オートコレクト大文字の場合は正規化
            behavior: m[1].toLowerCase().startsWith('y') ? 'allow' : 'deny',
          },
        })
        return  // 判定として処理、チャットとしても転送しない
      }

      // 判定フォーマットと一致しない：通常のチャットパスにフォールスルー
      await mcp.notification({
        method: 'notifications/claude/channel',
        params: { content: message.text, meta: { chat_id: String(message.chat.id) } },
      })
    }
    ```
  </Step>
</Steps>

Claude Code はローカルターミナルダイアログも開いたままにするため、どちらかの場所で答えることができ、最初に到着した答えが適用されます。期待されたフォーマットと正確に一致しないリモート返信は、2 つの方法のいずれかで失敗し、どちらの場合もダイアログは開いたままです：

* **異なるフォーマット**：インバウンドハンドラーの正規表現が一致しないため、'approve it'または ID なしの'yes'のようなテキストは通常のメッセージとして Claude にフォールスルーします。
* **正しいフォーマット、間違った ID**：サーバーは判定を発行しますが、Claude Code はその ID を持つ開いているリクエストを見つけず、サイレントにドロップします。

<h3 id="full-example">
  完全な例
</h3>

以下の組み立てられた `webhook.ts` は、このページからの 3 つの拡張をすべて組み合わせます：返信ツール、送信者ゲーティング、権限リレー。ここから始める場合は、初期ウォークスルーから[プロジェクト設定と `.mcp.json` エントリ](#example-build-a-webhook-receiver)も必要です。

curl から両方向をテスト可能にするために、HTTP リスナーは 2 つのパスを提供します：

* **`GET /events`**：SSE ストリームを開いたままにし、各アウトバウンドメッセージを `data:` 行としてプッシュするため、`curl -N` は Claude の返信と権限プロンプトがライブで到着するのを見ることができます。
* **`POST /`**：インバウンド側、以前と同じハンドラー、チャット転送ブランチの前に判定フォーマットチェックが挿入されました。

```ts title="権限リレー付きの完全な webhook.ts" expandable theme={null}
#!/usr/bin/env bun
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js'
import { z } from 'zod'

// --- アウトバウンド：/events の任意の curl -N リスナーに書き込み ---
// 実際のブリッジはチャットプラットフォームに POST します。
const listeners = new Set<(chunk: string) => void>()
function send(text: string) {
  const chunk = text.split('\n').map(l => `data: ${l}\n`).join('') + '\n'
  for (const emit of listeners) emit(chunk)
}

// 送信者許可リスト。ローカルウォークスルーの場合、単一の X-Sender
// ヘッダー値「dev」を信頼します。実際のブリッジはプラットフォームのユーザー ID をチェックします。
const allowed = new Set(['dev'])

const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    capabilities: {
      experimental: {
        'claude/channel': {},
        'claude/channel/permission': {},  // 権限リレーにオプトイン
      },
      tools: {},
    },
    instructions:
      'Messages arrive as <channel source="webhook" chat_id="...">. ' +
      'Reply with the reply tool, passing the chat_id from the tag.',
  },
)

// --- 返信ツール：Claude がメッセージを返送するために呼び出す ---
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'reply',
    description: 'Send a message back over this channel',
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'The conversation to reply in' },
        text: { type: 'string', description: 'The message to send' },
      },
      required: ['chat_id', 'text'],
    },
  }],
}))

mcp.setRequestHandler(CallToolRequestSchema, async req => {
  if (req.params.name === 'reply') {
    const { chat_id, text } = req.params.arguments as { chat_id: string; text: string }
    send(`Reply to ${chat_id}: ${text}`)
    return { content: [{ type: 'text', text: 'sent' }] }
  }
  throw new Error(`unknown tool: ${req.params.name}`)
})

// --- 権限リレー：ダイアログが開くと Claude Code（Claude ではない）がこれを呼び出す
const PermissionRequestSchema = z.object({
  method: z.literal('notifications/claude/channel/permission_request'),
  params: z.object({
    request_id: z.string(),
    tool_name: z.string(),
    description: z.string(),
    input_preview: z.string(),
  }),
})

mcp.setNotificationHandler(PermissionRequestSchema, async ({ params }) => {
  send(
    `Claude wants to run ${params.tool_name}: ${params.description}\n\n` +
    `Reply "yes ${params.request_id}" or "no ${params.request_id}"`,
  )
})

await mcp.connect(new StdioServerTransport())

// --- HTTP on :8788：GET /events はアウトバウンドをストリーム、POST はインバウンドをルート ---
const PERMISSION_REPLY_RE = /^\s*(y|yes|n|no)\s+([a-km-z]{5})\s*$/i
let nextId = 1

Bun.serve({
  port: 8788,
  hostname: '127.0.0.1',
  idleTimeout: 0,  // アイドル SSE ストリームを閉じない
  async fetch(req) {
    const url = new URL(req.url)

    // GET /events：SSE ストリーム、curl -N が返信とプロンプトをライブで見ることができる
    if (req.method === 'GET' && url.pathname === '/events') {
      const stream = new ReadableStream({
        start(ctrl) {
          ctrl.enqueue(': connected\n\n')  // curl がすぐに何かを表示するように
          const emit = (chunk: string) => ctrl.enqueue(chunk)
          listeners.add(emit)
          req.signal.addEventListener('abort', () => listeners.delete(emit))
        },
      })
      return new Response(stream, {
        headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
      })
    }

    // その他すべてはインバウンド：最初に送信者でゲート
    const body = await req.text()
    const sender = req.headers.get('X-Sender') ?? ''
    if (!allowed.has(sender)) return new Response('forbidden', { status: 403 })

    // チャットとして扱う前に判定フォーマットをチェック
    const m = PERMISSION_REPLY_RE.exec(body)
    if (m) {
      await mcp.notification({
        method: 'notifications/claude/channel/permission',
        params: {
          request_id: m[2].toLowerCase(),
          behavior: m[1].toLowerCase().startsWith('y') ? 'allow' : 'deny',
        },
      })
      return new Response('verdict recorded')
    }

    // 通常のチャット：チャネルイベントとして Claude に転送
    const chat_id = String(nextId++)
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: { content: body, meta: { chat_id, path: url.pathname } },
    })
    return new Response('ok')
  },
})
```

判定パスを 3 つのターミナルでテストします。最初は Claude Code セッションで、[開発フラグ](#test-during-the-research-preview)で開始されるため、`webhook.ts` を生成します：

```bash theme={null}
claude --dangerously-load-development-channels server:webhook
```

2 番目では、アウトバウンド側をストリーミングして、Claude の返信と権限プロンプトがライブで到着するのを見ることができます：

```bash theme={null}
curl -N localhost:8788/events
```

3 番目では、Claude がコマンドを実行しようとするメッセージを送信します：

```bash theme={null}
curl -d "list the files in this directory" -H "X-Sender: dev" localhost:8788
```

ファイルをリストすることは読み取り専用なので、Claude は承認なしでそれを実行します。権限ダイアログは Claude が `reply` ツールを呼び出して答えを返送するときに開きます。ローカルダイアログは Claude Code ターミナルで開き、少し後、`mcp__webhook__reply` のプロンプトが `/events` ストリームに表示され、5 文字の ID を含みます。リモート側から承認します：

```bash theme={null}
curl -d "yes <id>" -H "X-Sender: dev" localhost:8788
```

ローカルダイアログが閉じ、`reply` ツールが実行され、Claude の返信がストリームに到着します。

このファイルの 3 つのチャネル固有の部分：

* **`Server` コンストラクタの機能**：`claude/channel` は通知リスナーを登録し、`claude/channel/permission` は権限リレーにオプトイン、`tools` は Claude がツールを検出できるようにします。
* **アウトバウンドパス**：`reply` ツールハンドラーは Claude が会話応答のために呼び出すもの。`PermissionRequestSchema` 通知ハンドラーは権限ダイアログが開くと Claude Code が呼び出すもの。両方とも `/events` 経由でブロードキャストするために `send()` を呼び出しますが、システムの異なる部分によってトリガーされます。
* **HTTP ハンドラー**：`GET /events` は SSE ストリームを開いたままにするため、curl はアウトバウンドをライブで見ることができます。`POST` はインバウンド、`X-Sender` ヘッダーでゲート。`yes <id>` または `no <id>` 本文は Claude Code に判定通知として送信され、Claude に到達しません。その他はすべてチャネルイベントとして Claude に転送されます。

<h2 id="package-as-a-plugin">
  プラグインとしてパッケージ化
</h2>

チャネルをインストール可能で共有可能にするには、[プラグイン](/docs/ja/plugins)でラップして[マーケットプレイス](/docs/ja/plugin-marketplaces)に公開します。ユーザーは `/plugin install` でインストールし、`--channels plugin:<name>@<marketplace>` でセッションごとに有効化します。

独自のマーケットプレイスに公開されたチャネルは、[承認許可リスト](/docs/ja/channels#supported-channels)にないため、実行するには `--dangerously-load-development-channels` が必要です。デフォルトの許可リストは `claude-plugins-official` のチャネルプラグインで、Anthropic がその裁量で管理しています。[アプリ内送信フォーム](/docs/ja/plugins#submit-your-plugin-to-the-community-marketplace)はプラグインをコミュニティマーケットプレイスに追加しますが、これはチャネル許可リストにはありません。

Anthropic パートナー連絡先と協力している場合は、公式マーケットプレイスリストを調整するために彼らに連絡してください。Team および Enterprise プランでは、管理者は代わりにプラグインを組織の独自の [`allowedChannelPlugins`](/docs/ja/channels#restrict-which-channel-plugins-can-run) リストに含めることができます。これはデフォルトの Anthropic 許可リストを置き換えます。

<h2 id="see-also">
  関連項目
</h2>

* [チャネル](/docs/ja/channels)：Telegram、Discord、iMessage、または fakechat デモをインストールして使用し、Team または Enterprise 組織のチャネルを有効化
* [チャネル実装の動作](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins)：ペアリングフロー、返信ツール、ファイル添付を含む完全なサーバーコード
* [MCP](/docs/ja/mcp)：チャネルサーバーが実装する基礎となるプロトコル
* [プラグイン](/docs/ja/plugins)：チャネルをパッケージ化して、ユーザーが `/plugin install` でインストールできるようにする
