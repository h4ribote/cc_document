> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# チャネルを使用して実行中のセッションにイベントをプッシュする

> チャネルを使用して、MCP サーバーから実行中の Claude Code セッションにメッセージ、アラート、ウェブフックをプッシュします。CI 結果、チャットメッセージ、監視イベントを転送して、あなたが不在の間に Claude が対応できるようにします。

<Note>
  チャネルは[リサーチプレビュー](#research-preview)段階にあります。Anthropic 認証が claude.ai または Console API キーを通じて必要で、Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry では利用できません。Team および Enterprise 組織は[明示的に有効にする](#enterprise-controls)必要があります。
</Note>

チャネルは MCP サーバーで、実行中の Claude Code セッションにイベントをプッシュするため、あなたがターミナルにいない間に起こることに Claude が対応できます。チャネルは双方向にすることができます。Claude がイベントを読み取り、同じチャネルを通じて返信します。チャットブリッジのようなものです。イベントはセッションが開いている間だけ到着するため、常時稼働セットアップの場合は、Claude をバックグラウンドプロセスまたは永続的なターミナルで実行します。

新しいクラウドセッションを生成するか、ポーリングされるのを待つ統合とは異なり、イベントはすでに開いているセッションに到着します。[チャネルの比較方法](#how-channels-compare)を参照してください。

チャネルをプラグインとしてインストールし、独自の認証情報で設定します。Telegram、Discord、iMessage はリサーチプレビューに含まれています。

Claude がチャネルを通じて返信する場合、ターミナルに受信メッセージが表示されますが、返信テキストは表示されません。ターミナルはツール呼び出しと確認（「送信済み」など）を表示し、実際の返信は他のプラットフォームに表示されます。

Team、Enterprise、または Console 組織を管理している場合は、[組織のチャネルを有効にする](#enterprise-controls)を参照してください。独自のチャネルを構築するには、[チャネルリファレンス](/docs/ja/channels-reference)を参照してください。

<h2 id="supported-channels">
  サポートされているチャネル
</h2>

サポートされている各チャネルはプラグインで、[Bun](https://bun.sh) が必要です。実際のプラットフォームを接続する前にプラグインフローの実践的なデモを試すには、[fakechat クイックスタート](#quickstart)を試してください。

<Tabs>
  <Tab title="Telegram">
    完全な[Telegram プラグインソース](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram)を表示します。

    <Steps>
      <Step title="Telegram ボットを作成する">
        Telegram で [BotFather](https://t.me/BotFather) を開き、`/newbot` を送信します。表示名と `bot` で終わる一意のユーザー名を指定します。BotFather が返すトークンをコピーします。
      </Step>

      <Step title="プラグインをインストールする">
        Claude Code で以下を実行します。

        ```
        /plugin install telegram@claude-plugins-official
        ```

        Claude Code がプラグインがどのマーケットプレイスにも見つからないと報告する場合、マーケットプレイスが見つからないか古い可能性があります。`/plugin marketplace update claude-plugins-official` を実行して更新するか、まだ追加していない場合は `/plugin marketplace add anthropics/claude-plugins-official` を実行します。その後、インストールを再試行します。

        インストール後、`/reload-plugins` を実行してプラグインの設定コマンドをアクティブにします。
      </Step>

      <Step title="トークンを設定する">
        BotFather からのトークンで設定コマンドを実行します。

        ```
        /telegram:configure <token>
        ```

        これは `~/.claude/channels/telegram/.env` に保存されます。Claude Code を起動する前に、シェル環境で `TELEGRAM_BOT_TOKEN` を設定することもできます。
      </Step>

      <Step title="チャネルを有効にして再起動する">
        Claude Code を終了し、チャネルフラグで再起動します。これにより Telegram プラグインが起動し、ボットからのメッセージのポーリングが開始されます。

        ```bash theme={null}
        claude --channels plugin:telegram@claude-plugins-official
        ```
      </Step>

      <Step title="アカウントをペアリングする">
        Telegram を開き、ボットに任意のメッセージを送信します。ボットはペアリングコードで返信します。

        <Note>ボットが応答しない場合は、前のステップから `--channels` で Claude Code が実行されていることを確認してください。ボットはチャネルがアクティブな間だけ返信できます。</Note>

        Claude Code に戻り、以下を実行します。

        ```
        /telegram:access pair <code>
        ```

        その後、アクセスをロックダウンして、アカウントだけがメッセージを送信できるようにします。

        ```
        /telegram:access policy allowlist
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="Discord">
    完全な[Discord プラグインソース](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/discord)を表示します。

    <Steps>
      <Step title="Discord ボットを作成する">
        [Discord Developer Portal](https://discord.com/developers/applications) に移動し、**New Application** をクリックして名前を付けます。**Bot** セクションでユーザー名を作成し、**Reset Token** をクリックしてトークンをコピーします。
      </Step>

      <Step title="Message Content Intent を有効にする">
        ボットの設定で、**Privileged Gateway Intents** までスクロールし、**Message Content Intent** を有効にします。
      </Step>

      <Step title="ボットをサーバーに招待する">
        **OAuth2 > URL Generator** に移動します。`bot` スコープを選択し、以下の権限を有効にします。

        * View Channels
        * Send Messages
        * Send Messages in Threads
        * Read Message History
        * Attach Files
        * Add Reactions

        生成された URL を開いてボットをサーバーに追加します。
      </Step>

      <Step title="プラグインをインストールする">
        Claude Code で以下を実行します。

        ```
        /plugin install discord@claude-plugins-official
        ```

        Claude Code がプラグインがどのマーケットプレイスにも見つからないと報告する場合、マーケットプレイスが見つからないか古い可能性があります。`/plugin marketplace update claude-plugins-official` を実行して更新するか、まだ追加していない場合は `/plugin marketplace add anthropics/claude-plugins-official` を実行します。その後、インストールを再試行します。

        インストール後、`/reload-plugins` を実行してプラグインの設定コマンドをアクティブにします。
      </Step>

      <Step title="トークンを設定する">
        コピーしたボットトークンで設定コマンドを実行します。

        ```
        /discord:configure <token>
        ```

        これは `~/.claude/channels/discord/.env` に保存されます。Claude Code を起動する前に、シェル環境で `DISCORD_BOT_TOKEN` を設定することもできます。
      </Step>

      <Step title="チャネルを有効にして再起動する">
        Claude Code を終了し、チャネルフラグで再起動します。これにより Discord プラグインが接続され、ボットがメッセージを受信して応答できるようになります。

        ```bash theme={null}
        claude --channels plugin:discord@claude-plugins-official
        ```
      </Step>

      <Step title="アカウントをペアリングする">
        Discord でボットに DM を送信します。ボットはペアリングコードで返信します。

        <Note>ボットが応答しない場合は、前のステップから `--channels` で Claude Code が実行されていることを確認してください。ボットはチャネルがアクティブな間だけ返信できます。</Note>

        Claude Code に戻り、以下を実行します。

        ```
        /discord:access pair <code>
        ```

        その後、アクセスをロックダウンして、アカウントだけがメッセージを送信できるようにします。

        ```
        /discord:access policy allowlist
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="iMessage">
    完全な[iMessage プラグインソース](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage)を表示します。

    iMessage チャネルは Messages データベースを直接読み取り、AppleScript を通じて返信を送信します。macOS が必要で、ボットトークンや外部サービスは不要です。

    <Steps>
      <Step title="フルディスクアクセスを許可する">
        `~/Library/Messages/chat.db` にある Messages データベースは macOS によって保護されています。サーバーが初めてそれを読み取るとき、macOS はアクセスを求めるプロンプトを表示します。**Allow** をクリックします。プロンプトは Bun を起動したアプリ（Terminal、iTerm、IDE など）の名前を表示します。

        プロンプトが表示されない場合、または Don't Allow をクリックした場合は、**System Settings > Privacy & Security > Full Disk Access** でアクセスを手動で許可し、ターミナルを追加します。これがないと、サーバーは `authorization denied` で直ちに終了します。
      </Step>

      <Step title="プラグインをインストールする">
        Claude Code で以下を実行します。

        ```
        /plugin install imessage@claude-plugins-official
        ```

        Claude Code がプラグインがどのマーケットプレイスにも見つからないと報告する場合、マーケットプレイスが見つからないか古い可能性があります。`/plugin marketplace update claude-plugins-official` を実行して更新するか、まだ追加していない場合は `/plugin marketplace add anthropics/claude-plugins-official` を実行します。その後、インストールを再試行します。
      </Step>

      <Step title="チャネルを有効にして再起動する">
        Claude Code を終了し、チャネルフラグで再起動します。

        ```bash theme={null}
        claude --channels plugin:imessage@claude-plugins-official
        ```
      </Step>

      <Step title="自分自身にテキストを送信する">
        Apple ID にサインインしているデバイスで Messages を開き、自分自身にメッセージを送信します。それは Claude に直ちに到着します。セルフチャットはセットアップなしでアクセス制御をバイパスします。

        <Note>Claude が送信する最初の返信は、ターミナルが Messages を制御できるかどうかを尋ねる macOS Automation プロンプトをトリガーします。**OK** をクリックします。</Note>
      </Step>

      <Step title="他の送信者を許可する">
        デフォルトでは、独自のメッセージだけが通過します。別の連絡先が Claude に到達できるようにするには、ハンドルを追加します。

        ```
        /imessage:access allow +15551234567
        ```

        ハンドルは `+country` 形式の電話番号または `user@example.com` のような Apple ID メールです。
      </Step>
    </Steps>
  </Tab>
</Tabs>

また、[独自のチャネルを構築](/docs/ja/channels-reference)して、まだプラグインがないシステムに対応することもできます。

<h2 id="quickstart">
  クイックスタート
</h2>

Fakechat は公式にサポートされているデモチャネルで、localhost でチャット UI を実行し、認証は不要で、設定する外部サービスもありません。

Fakechat をインストールして有効にすると、ブラウザで入力でき、メッセージが Claude Code セッションに到着します。Claude が返信し、返信がブラウザに戻ります。Fakechat インターフェイスをテストした後、[Telegram](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram)、[Discord](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/discord)、または [iMessage](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage) を試してください。

Fakechat デモを試すには、以下が必要です。

* Claude Code が[インストールされ、認証されている](/docs/ja/quickstart#step-1-install-claude-code)（claude.ai アカウントまたは Claude Console API キー）
* [Bun](https://bun.sh) がインストールされている。事前構築されたチャネルプラグインは Bun スクリプトです。`bun --version` で確認します。失敗する場合は、[Bun をインストール](https://bun.sh/docs/installation)します。
* **Team、Enterprise、または管理 Console 組織**：管理者が[チャネルを有効にする](#enterprise-controls)必要があります。

<Steps>
  <Step title="Fakechat チャネルプラグインをインストールする">
    Claude Code セッションを開始し、インストールコマンドを実行します。

    ```text theme={null}
    /plugin install fakechat@claude-plugins-official
    ```

    Claude Code がプラグインがどのマーケットプレイスにも見つからないと報告する場合、マーケットプレイスが見つからないか古い可能性があります。`/plugin marketplace update claude-plugins-official` を実行して更新するか、まだ追加していない場合は `/plugin marketplace add anthropics/claude-plugins-official` を実行します。その後、インストールを再試行します。
  </Step>

  <Step title="チャネルを有効にして再起動する">
    Claude Code を終了し、`--channels` で再起動してインストールした Fakechat プラグインを渡します。

    ```bash theme={null}
    claude --channels plugin:fakechat@claude-plugins-official
    ```

    Fakechat サーバーが自動的に起動します。

    <Tip>
      複数のプラグインを `--channels` に渡すことができます（スペース区切り）。
    </Tip>
  </Step>

  <Step title="メッセージをプッシュする">
    [http://localhost:8787](http://localhost:8787) で Fakechat UI を開き、メッセージを入力します。

    ```text theme={null}
    hey, what's in my working directory?
    ```

    メッセージは Claude Code セッションに `<channel source="fakechat">` イベントとして到着します。Claude がそれを読み取り、作業を行い、Fakechat の `reply` ツールを呼び出します。答えがチャット UI に表示されます。
  </Step>
</Steps>

Claude がターミナルから離れている間に権限プロンプトにヒットした場合、セッションは応答するまで一時停止します。[権限リレー機能](/docs/ja/channels-reference#relay-permission-prompts)を宣言するチャネルサーバーは、これらのプロンプトをあなたに転送して、リモートで承認または拒否できるようにします。無人使用の場合、[`--dangerously-skip-permissions`](/docs/ja/permission-modes#skip-all-checks-with-bypasspermissions-mode) はほとんどのプロンプトをバイパスしますが、信頼できる環境でのみ使用してください。明示的な ask ルール、コネクタツール[組織が `ask` に設定したもの](/docs/ja/mcp#organization-controls-on-connector-tools)、および MCP ツール[`requiresUserInteraction`](/docs/ja/mcp#require-approval-for-a-specific-tool)でマークされたものは、引き続きプロンプトが表示されます。

非対話型モードで `-p` でチャネルを実行する場合、複数選択質問や Plan Mode 承認など、ターミナル入力が必要なツールは無効になるため、セッションは入力を待つことで停止することはありません。

<h2 id="security">
  セキュリティ
</h2>

承認されたすべてのチャネルプラグインは送信者許可リストを保持します。追加した ID だけがメッセージをプッシュでき、他のすべては静かにドロップされます。

Telegram と Discord はペアリングでリストをブートストラップします。

1. Telegram または Discord でボットを見つけ、任意のメッセージを送信します。
2. ボットはペアリングコードで返信します。
3. Claude Code セッションで、プロンプトが表示されたときにコードを承認します。
4. 送信者 ID が許可リストに追加されます。

iMessage は異なります。自分自身にテキストを送信するとゲートを自動的にバイパスし、`/imessage:access allow` でハンドルを使用して他の連絡先を追加します。

その上に、`--channels` で各セッションで有効なサーバーを制御し、組織は claude.ai Team および Enterprise プランと、管理設定をデプロイする Console 組織で [`channelsEnabled`](#enterprise-controls) で可用性を制御します。

`.mcp.json` にあるだけではメッセージをプッシュするのに十分ではありません。サーバーも `--channels` で名前を付ける必要があります。

許可リストは、チャネルが宣言する場合、[パーミッションリレー](/docs/ja/channels-reference#relay-permission-prompts)もゲートします。チャネルを通じて返信できるすべてのユーザーは、セッションでのツール使用を承認または拒否できるため、その権限を信頼できる許可リスト送信者だけを追加してください。

<h2 id="enterprise-controls">
  Enterprise コントロール
</h2>

管理者は 2 つの[管理設定](/docs/ja/settings)を通じて可用性を制御します。ユーザーはこれらをオーバーライドできません。デフォルトは認証方法によって異なります。

* **claude.ai Team および Enterprise**：チャネルは Owner が有効にするまでブロックされます。
* **Anthropic Console と API キー認証**：チャネルはデフォルトで許可されます。組織が管理設定をデプロイする場合のみこの設定が必要です。

すべての場合において、ユーザーが `--channels` でセッションにオプトインするまで、チャネルは実行されません。

| 設定                      | 目的                                                                                                                                                                      | 設定されていない場合                                                                                                       |
| :---------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- |
| `channelsEnabled`       | マスタースイッチ。チャネルがメッセージを配信するには `true` である必要があります。[claude.ai Admin console](https://claude.ai/admin-settings/claude-code) トグルまたは管理設定で直接設定します。オフの場合、開発フラグを含むすべてのチャネルをブロックします。 | claude.ai Team および Enterprise：チャネルがブロックされます。Console：組織が管理設定をデプロイしない限りチャネルが許可されます。その場合、このキーが設定されるまでチャネルがブロックされます。 |
| `allowedChannelPlugins` | チャネルが有効になったら、どのプラグインが登録できるか。設定されている場合、Anthropic が管理するリストを置き換えます。`channelsEnabled` が `true` の場合のみ適用されます。                                                                 | Anthropic デフォルトリストが適用されます。                                                                                       |

組織のない Pro および Max ユーザーはこれらのチェックを完全にスキップします。チャネルが利用可能で、ユーザーは `--channels` でセッションごとにオプトインします。

<h3 id="enable-channels-for-your-organization">
  組織のチャネルを有効にする
</h3>

[**claude.ai → Admin settings → Claude Code → Channels**](https://claude.ai/admin-settings/claude-code) から組織のチャネルを有効にします。これには Owner ロールが必要です。または、管理設定で `channelsEnabled` を `true` に設定します。

有効にすると、組織内のユーザーは `--channels` を使用して個別のセッションにチャネルサーバーをオプトインできます。設定が無効または未設定の場合、MCP サーバーは接続され、そのツールは機能しますが、チャネルメッセージは到着しません。スタートアップ警告は、ユーザーに管理者が設定を有効にするよう指示します。

<h3 id="restrict-which-channel-plugins-can-run">
  チャネルプラグインが実行できるものを制限する
</h3>

デフォルトでは、Anthropic が管理する許可リスト上のプラグインはチャネルとして登録できます。Team および Enterprise プランの管理者は、管理設定で `allowedChannelPlugins` を設定することで、その許可リストを独自のものに置き換えることができます。これを使用して、許可されている公式プラグインを制限したり、独自の内部マーケットプレイスからチャネルを承認したり、その両方を行ったりします。各エントリは、プラグインとそれが由来するマーケットプレイスに名前を付けます。

```json theme={null}
{
  "channelsEnabled": true,
  "allowedChannelPlugins": [
    { "marketplace": "claude-plugins-official", "plugin": "telegram" },
    { "marketplace": "claude-plugins-official", "plugin": "discord" },
    { "marketplace": "acme-corp-plugins", "plugin": "internal-alerts" }
  ]
}
```

`allowedChannelPlugins` が設定されている場合、Anthropic 許可リスト全体を置き換えます。リストされたプラグインだけが登録できます。デフォルト Anthropic 許可リストにフォールバックするには、設定されていないままにします。空の配列はすべてのチャネルプラグインを許可リストからブロックしますが、`--dangerously-load-development-channels` はローカルテストのためにそれをバイパスできます。開発フラグを含むチャネルを完全にブロックするには、代わりに `channelsEnabled` を設定されていないままにします。

この設定には `channelsEnabled: true` が必要です。ユーザーが `--channels` にリストにないプラグインを渡す場合、Claude Code は通常起動しますが、チャネルは登録されず、スタートアップ通知はプラグインが組織の承認リストにないことを説明します。

<h2 id="research-preview">
  リサーチプレビュー
</h2>

チャネルはリサーチプレビュー機能です。可用性は段階的にロールアウトされており、`--channels` フラグの構文とプロトコルコントラクトはフィードバックに基づいて変更される可能性があります。

プレビュー中、`--channels` は Anthropic が管理する許可リストからのプラグイン、または管理者が [`allowedChannelPlugins`](#restrict-which-channel-plugins-can-run) を設定している場合は組織の許可リストからのプラグインのみを受け入れます。[claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins) のチャネルプラグインはデフォルトで承認されたセットです。有効な許可リストにないものを渡す場合、Claude Code は通常起動しますが、チャネルは登録されず、スタートアップ通知は理由を伝えます。

構築しているチャネルをテストするには、`--dangerously-load-development-channels` を使用します。構築するカスタムチャネルのテストについては、[リサーチプレビュー中のテスト](/docs/ja/channels-reference#test-during-the-research-preview)を参照してください。

[Claude Code GitHub リポジトリ](https://github.com/anthropics/claude-code/issues)で問題またはフィードバックを報告してください。

<h2 id="how-channels-compare">
  チャネルの比較方法
</h2>

Claude Code のいくつかの機能はターミナルの外のシステムに接続し、それぞれ異なる種類の作業に適しています。

| 機能                                              | 何をするか                                      | 適している用途                                  |
| ----------------------------------------------- | ------------------------------------------ | ---------------------------------------- |
| [ウェブ上の Claude Code](/docs/ja/claude-code-on-the-web) | GitHub からクローンされた新しいクラウドサンドボックスでタスクを実行      | 後で確認する自己完結型の非同期作業を委任する                   |
| [Slack の Claude](/docs/ja/slack)                     | チャネルまたはスレッドの `@Claude` メンションからウェブセッションを生成  | チームの会話コンテキストから直接タスクを開始する                 |
| 標準 [MCP サーバー](/docs/ja/mcp)                          | Claude はタスク中にそれをクエリします。セッションには何もプッシュされません  | Claude にシステムを読み取るまたはクエリするオンデマンドアクセスを提供する |
| [リモートコントロール](/docs/ja/remote-control)                | claude.ai または Claude モバイルアプリからローカルセッションを駆動 | デスクから離れている間に進行中のセッションを操舵する               |

チャネルは、Claude 以外のソースからのイベントをすでに実行中のローカルセッションにプッシュすることで、そのリストのギャップを埋めます。

* **チャットブリッジ**：Telegram、Discord、または iMessage を通じて電話から Claude に何かを尋ね、答えが同じチャットに戻ってきます。作業はマシンで実際のファイルに対して実行されます。
* **[ウェブフックレシーバー](/docs/ja/channels-reference#example-build-a-webhook-receiver)**：CI、エラートラッカー、デプロイパイプライン、または他の外部サービスからのウェブフックが、Claude がファイルをすでに開いており、デバッグしていたことを覚えている場所に到着します。

<h2 id="next-steps">
  次のステップ
</h2>

チャネルが実行されたら、これらの関連機能を探索してください。

* [独自のチャネルを構築](/docs/ja/channels-reference)して、まだプラグインがないシステムに対応する
* [リモートコントロール](/docs/ja/remote-control)を使用して、イベントをそれに転送する代わりに電話からローカルセッションを駆動する
* [スケジュール済みタスク](/docs/ja/scheduled-tasks)を使用して、プッシュされたイベントに対応する代わりにタイマーでポーリングする
