> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude Code を LLM ゲートウェイに接続する

> Claude Code を組織の LLM ゲートウェイに指定します。管理者がすでに設定しているかどうかを確認するか、基本 URL と認証情報を自分で設定してから、接続を確認し、ゲートウェイエラーを修正します。

[LLM ゲートウェイ](/docs/ja/llm-gateway)は、Claude Code とモデルプロバイダーの間に組織が実行するプロキシです。組織がゲートウェイを使用する場合、Claude Code は個人の claude.ai ログインではなく、組織が発行する認証情報を使用してゲートウェイに認証します。

このページは、組織が運用するゲートウェイを通じて Claude Code を実行している開発者向けです。2 つのパスをカバーしています。[管理者がすでに設定しているかどうかを確認する](#check-for-an-existing-configuration)場合と、[設定していない場合に自分で設定する](#configure-claude-code-yourself)場合です。

<Note>
  * 組織用のゲートウェイをデプロイするには、[LLM ゲートウェイをロールアウトする](/docs/ja/llm-gateway-rollout)を参照してください
  * Claude Code がゲートウェイに送信する内容については、[ゲートウェイプロトコルリファレンス](/docs/ja/llm-gateway-protocol)を参照してください
</Note>

<h2 id="check-for-an-existing-configuration">
  既存の設定を確認する
</h2>

管理者は、[管理設定](/docs/ja/settings#settings-files)、デバイス管理、または [`apiKeyHelper`](#rotate-credentials-with-apikeyhelper) を通じてゲートウェイアドレスと認証情報を配布できるため、Claude Code は起動時にそれらを取得し、設定する必要がありません。組織がすでにこれを行ったかどうかを確認するには：

<Steps>
  <Step title="Claude Code を起動する">
    `claude` を実行します。ログイン画面ではなくセッションが開く場合、ゲートウェイ認証情報は配布されていません。以下の[自分で設定](#configure-claude-code-yourself)を参照してください。
  </Step>

  <Step title="Status タブを確認する">
    Claude Code がログイン画面を表示せずにセッションを開始した場合、`/status` を実行し、**Status** タブを開いて、2 つの行を確認します：

    * `Anthropic base URL`：この行はゲートウェイアドレスが設定されている場合にのみ表示されます。ない場合、Claude Code はゲートウェイを指していません。以下の[自分で設定](#configure-claude-code-yourself)を参照してください。
    * `Auth token` または `API key`：`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_API_KEY`、または `apiKeyHelper` という名前の行は、ゲートウェイ認証情報がアクティブであることを確認します。代わりに claude.ai アカウントという名前の `Login method` 行は、認証情報が配布されていないことを意味します。[自分で設定](#set-the-credential-variable)してください。
  </Step>

  <Step title="テストメッセージを送信する">
    `/status` メニューを閉じて、Claude Code で任意のプロンプトを送信します。Claude からの通常の応答でエラーがない場合、ゲートウェイ接続が機能していることを確認します。
  </Step>
</Steps>

`/status` メニューの両方の行が正しく見えるが、Claude へのメッセージが失敗する場合は、[トラブルシューティングテーブル](#troubleshoot-gateway-errors)を参照してください。

<h2 id="configure-claude-code-yourself">
  Claude Code を自分で設定する
</h2>

Claude Code をゲートウェイ用に自分で設定するには、ゲートウェイチームから以下が必要です：

* ゲートウェイの基本 URL
* 認証情報：キーまたはトークン文字列、またはそれを取得するコマンド
  * ゲートウェイチームが認証情報の種類を指定しなかった場合、以下の[認証情報変数セクション](#set-the-credential-variable)で試すべきことをカバーしています

以下のセクションは設定を順番にカバーしています：

* [認証情報変数を設定する](#set-the-credential-variable)と[基本 URL を設定する](#set-the-base-url-and-credential)：すべてのゲートウェイ接続に必要な 2 つの変数
* [接続を確認する](#verify-the-connection)：何かを永続化する前に機能することを確認します
* [各サーフェスを設定する](#configure-each-surface)：Claude Code CLI 以外のサーフェス（VS Code など）を使用している場合、ゲートウェイ認証情報で設定する方法を参照してください
* [追加設定](#additional-configuration)：基本 URL と認証情報を超えて一部のゲートウェイが必要とする変数（カスタムヘッダー、認証情報ヘルパー、モデル検出、プロバイダー形式の基本 URL、またはゲートウェイパス外のトラフィックをオフにするなど）。管理者が名前を付けた場合のみこれらを設定するか、ネットワークが出力を制限します

<h3 id="set-the-credential-variable">
  認証情報変数を設定する
</h3>

Claude Code をゲートウェイに認証するには、環境変数に認証情報を設定します。どの変数を使用するかは、ゲートウェイチームが何を言ったかによって異なります：

| 認証情報を設定する場所                                             | 使用する場合                                                  |
| :------------------------------------------------------ | :------------------------------------------------------ |
| `ANTHROPIC_AUTH_TOKEN`                                  | ゲートウェイチームが'bearer token'または'Authorization header'と言った場合 |
| `ANTHROPIC_API_KEY`                                     | ゲートウェイチームが'API key'または'x-api-key'と言った場合                 |
| [`apiKeyHelper`](#rotate-credentials-with-apikeyhelper) | 認証情報がローテーションするか、ボルトから来る場合                               |

どの種類かを指定されなかった場合は、`ANTHROPIC_AUTH_TOKEN` を使用します。以下の[検証リクエスト](#verify-the-connection)は、切り替える必要があるかどうかを判断する方法を示しています。

<h3 id="set-the-base-url-and-credential">
  基本 URL と認証情報を設定する
</h3>

ゲートウェイの基本 URL と、上記で選択した認証情報変数を環境変数として設定します。例は `ANTHROPIC_AUTH_TOKEN` を使用しています。[選択した変数](#set-the-credential-variable)が `ANTHROPIC_API_KEY` の場合は、それに置き換えてください。[シェルで](#set-as-shell-environment-variables)設定できます（1 つのターミナルセッション用）、または [Claude Code 設定ファイルで](#set-in-a-settings-file)設定できます（Claude Code が実行されるすべての場所で永続化）。

最初の接続の場合、シェルエクスポートから始めて、値を設定ファイルに移動する前に[検証リクエスト](#verify-the-connection)を実行してください。

<h4 id="set-as-shell-environment-variables">
  シェル環境変数として設定する
</h4>

ゲートウェイチームが提供した値に置き換えます：

<Tabs>
  <Tab title="Bash または Zsh">
    ```bash theme={null}
    export ANTHROPIC_BASE_URL=https://llm-gateway.example.com
    export ANTHROPIC_AUTH_TOKEN=sk-gateway-key
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    $env:ANTHROPIC_BASE_URL = "https://llm-gateway.example.com"
    $env:ANTHROPIC_AUTH_TOKEN = "sk-gateway-key"
    ```
  </Tab>
</Tabs>

シェルエクスポートはそのターミナルセッションと、そこから開始されたプログラムにのみ適用されます。ドックまたはスタートメニューから起動されたエディターはそれらを見ません。新しいターミナル全体で永続化するには、同じ行をシェルプロファイル（`~/.zshrc`、`~/.bashrc`、PowerShell `$PROFILE` など）に追加するか、代わりに設定ファイルを使用してください。

<h4 id="set-in-a-settings-file">
  設定ファイルで設定する
</h4>

Claude Code が実行されるすべての場所で設定を適用し、シェルに依存しないようにするには、[設定ファイル](/docs/ja/settings)の `env` ブロックで変数を設定します。設定ファイルはスコープが異なります：

* `~/.claude/settings.json` はすべてのプロジェクトに適用されます。Windows ではパスは `%USERPROFILE%\.claude\settings.json` です
* `.claude/settings.local.json` は 1 つのプロジェクトに適用されます。Claude Code はファイルを作成するときに gitignore に追加します。自分で作成する場合は、認証情報を誤ってコミットしないように、最初に gitignore に手動で追加してください

<Warning>
  プロジェクトの `.claude/settings.json` に認証情報を入れないでください。このファイルはコミットされ、リポジトリをクローンするすべての人と共有されます。
</Warning>

`env` ブロックはどちらのファイルでも同じように見えます：

```json theme={null}
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
    "ANTHROPIC_AUTH_TOKEN": "sk-gateway-key"
  }
}
```

シェルエクスポートと設定ファイルの `env` ブロックの両方が同じ変数を設定する場合、設定ファイルの値が適用されます。`/status` を実行して、Claude Code が使用している基本 URL と認証情報ソースを確認してください。

<h3 id="verify-the-connection">
  接続を確認する
</h3>

シェルで変数をエクスポートした状態で、ゲートウェイに 1 トークンのリクエストを直接送信します。これは Claude Code を開く前に URL と認証情報が機能することを確認するため、失敗はゲートウェイを指し、設定ではなく。以下のコマンドはシェル変数を読み取るため、設定ファイルに値を入れた場合でも[シェルエクスポート](#set-as-shell-environment-variables)が必要です。

<Tabs>
  <Tab title="Bash または Zsh">
    ```bash theme={null}
    curl -X POST "$ANTHROPIC_BASE_URL/v1/messages" \
      -H "Authorization: Bearer $ANTHROPIC_AUTH_TOKEN" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    Invoke-RestMethod -Method Post -Uri "$env:ANTHROPIC_BASE_URL/v1/messages" `
      -Headers @{ "Authorization" = "Bearer $env:ANTHROPIC_AUTH_TOKEN"; "anthropic-version" = "2023-06-01" } `
      -ContentType "application/json" `
      -Body '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
    ```
  </Tab>
</Tabs>

ゲートウェイが `x-api-key` ヘッダーのキーを期待する場合、Bash コマンドの `Authorization` ヘッダーを `x-api-key: $ANTHROPIC_API_KEY` に置き換えるか、PowerShell コマンドの `"Authorization"` ハッシュテーブルエントリを `"x-api-key" = "$env:ANTHROPIC_API_KEY"` に置き換えてください。

`{"id":"msg_` で始まり、`"content":[...]` フィールドを含む JSON レスポンスは、ゲートウェイに到達可能で、認証情報が機能していることを意味します。不明なモデルという名前のエラーでも、ゲートウェイがリクエストを認証してからモデル名を拒否したため、URL と認証情報が機能していることを証明します。このテストのためにゲートウェイが提供するモデルを見つける必要はありません。`401` は認証情報が拒否されたことを意味します。変数を推測した場合は、もう一方に切り替えて再度エクスポートしてください。

<h4 id="confirm-in-claude-code">
  Claude Code で確認する
</h4>

同じシェルから `claude` を起動して、エクスポートを継承し、メッセージを送信して、`/status` を実行します。

**Status** タブで、`Anthropic base URL` 行はゲートウェイアドレスを表示する必要があり、リクエストがそこにルーティングされていることを確認します。行がない場合、変数がセッションに到達しませんでした。`Auth token` または `API key` 行が設定した変数という名前は、保存された claude.ai ログインではなく、ゲートウェイ認証情報がアクティブであることを確認します。

メッセージが失敗するか、`/status` がゲートウェイ URL を表示しない場合は、以下の[トラブルシューティングテーブル](#troubleshoot-gateway-errors)を参照してください。

<h3 id="how-the-credential-variable-maps-to-a-header">
  認証情報変数がヘッダーにマップされる方法
</h3>

各変数は認証情報を異なる HTTP ヘッダーで送信します：`ANTHROPIC_AUTH_TOKEN` は `Authorization: Bearer` で、`ANTHROPIC_API_KEY` は `x-api-key` で、`apiKeyHelper` は両方で。間違った変数の認証情報はゲートウェイが読まないヘッダーに到達し、リクエストは `401` で失敗します。検証リクエストが `401` を返した場合、もう一方の変数に切り替えて再度試してください。

<h3 id="conflicts-with-an-existing-login">
  既存のログインとの競合
</h3>

ゲートウェイ認証情報変数は、保存された claude.ai ログインまたは Console キーより優先されます。claude.ai ログインは保存されたままで、変数が設定されている間は使用されません。変数を設定解除すると、Claude Code はそれに戻ります。`ANTHROPIC_AUTH_TOKEN` では、変数は直ちに優先されます。`ANTHROPIC_API_KEY` では、キーが引き継ぐ前に、インタラクティブモードで 1 回承認するよう求められます。

`/status` を実行して、どの認証情報ソースがアクティブかを確認します。起動が 2 つのソースという名前の認証競合警告を表示する場合は、[トラブルシューティングテーブル](#troubleshoot-gateway-errors)の最初の行を参照して、どちらを削除するかを確認してください。保存されたログインをクリアしてゲートウェイ認証情報のみを残すには、`/logout` を実行してください。

<h2 id="configure-each-surface">
  各サーフェスを設定する
</h2>

CLI は上記の環境変数と設定ファイルを読み取ります。他のサーフェスは VS Code 拡張機能、デスクトップアプリ、GitHub Actions、Agent SDK、Slack やウェブなどのクラウドサーフェスです。以下のセクションは、これらの設定が各サーフェスに到達するかどうかをカバーしています。

<h3 id="vs-code-extension">
  VS Code 拡張機能
</h3>

[VS Code 拡張機能](/docs/ja/vs-code)のゲートウェイ変数を VS Code 独自のユーザー設定で `claudeCode.environmentVariables` に設定します。**Preferences: Open User Settings (JSON)** コマンドで開きます。拡張機能は起動前にこの設定から認証情報をチェックするため、ゲートウェイ認証情報の信頼できる場所です。`~/.claude/settings.json` の値は生成されたプロセスに到達しますが、拡張機能独自のログインチェックには到達しません。

```json theme={null}
{
  "claudeCode.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL", "value": "https://llm-gateway.example.com" },
    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "sk-gateway-key" }
  ]
}
```

<h3 id="desktop-app">
  デスクトップアプリ
</h3>

デスクトップアプリは、`ANTHROPIC_BASE_URL` または `settings.json` ではなく、[サードパーティ推論設定](https://claude.com/docs/third-party/claude-desktop/gateway)からゲートウェイルーティングを読み取ります。その設定は組織から、またはアプリ自体のフォームから来ることができます：

* **管理者によって配布される**：組織が[設定を配布](/docs/ja/llm-gateway-rollout#distribute-through-managed-settings)している場合、デスクトップアプリはゲートウェイを通じてルーティングされ、設定は不要です
* **ローカルで設定される**：管理者配布設定がないデバイスの場合、Help → Troubleshooting → 開発者モードを有効化を開きます。これはアプリを再起動して開発者メニューを表示します。その後、Developer → Configure Third-Party Inference を開き、ゲートウェイベース URL を入力します。管理者配布設定が優先され、このフォームを読み取り専用にします

ゲートウェイ設定がアクティブな場合、デスクトップアプリはローカルマシンのみでセッションを実行します。環境ピッカーは SSH セッションまたは Anthropic ホスト型クラウド環境を提供せず、[Remote Control](/docs/ja/remote-control)は利用できません。ゲートウェイを通じてリモートホストで Claude Code を使用するには、そのホストで CLI を実行し、[`ANTHROPIC_BASE_URL` とゲートウェイ認証情報](#set-the-base-url-and-credential)を設定します。

デスクトップアプリが `Gateway was unreachable` を表示する場合、アプリは起動時に設定されたベース URL に到達できませんでした。URL とネットワークパスを上記の [curl テスト](#verify-the-connection)で確認してください。

<h3 id="github-actions">
  GitHub Actions
</h3>

[Claude Code GitHub Actions](/docs/ja/github-actions) はワークフローの `env` ブロックから `ANTHROPIC_BASE_URL` と `ANTHROPIC_CUSTOM_HEADERS` を読み取ります。認証情報をアクションの `anthropic_api_key` 入力として渡します。アクションはそれを `ANTHROPIC_API_KEY` として設定するため、`x-api-key` ヘッダーでゲートウェイに到達します。

`x-api-key` ゲートウェイの場合、`env` でベース URL を設定し、ゲートウェイキーを入力として渡します：

```yaml theme={null}
env:
  ANTHROPIC_BASE_URL: https://llm-gateway.example.com

steps:
  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.GATEWAY_API_KEY }}
```

bearer token ゲートウェイの場合、同じシークレットをアクションの `anthropic_api_key` 入力とワークフロー `env` ブロックの `ANTHROPIC_AUTH_TOKEN` の両方として渡します。アクションは Claude Code を起動する前に `anthropic_api_key`、`CLAUDE_CODE_OAUTH_TOKEN`、またはワークロード ID フェデレーションが必要で、`ANTHROPIC_AUTH_TOKEN` を読み取らないため、入力はその起動チェックを満たすためだけのものです。env 変数はゲートウェイが読む `Authorization` ヘッダーにキーを入れます。`x-api-key` のコピーは無視されます：

```yaml theme={null}
env:
  ANTHROPIC_BASE_URL: https://llm-gateway.example.com
  ANTHROPIC_AUTH_TOKEN: ${{ secrets.GATEWAY_API_KEY }}

steps:
  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.GATEWAY_API_KEY }}
```

アクションの他の認証オプション（`CLAUDE_CODE_OAUTH_TOKEN` やワークロード ID フェデレーションを含む）については、[Claude Code GitHub Actions](/docs/ja/github-actions) とアクションの [README](https://github.com/anthropics/claude-code-action#readme) を参照してください。

<h3 id="agent-sdk">
  Agent SDK
</h3>

[Agent SDK](/docs/ja/agent-sdk/overview) にはゲートウェイ固有のオプションはありません。生成する Claude Code プロセスに環境変数を渡します。各 SDK は生成されたプロセスの環境を設定する `env` オプションを受け入れ、TypeScript と Python SDK はそれを異なる方法で処理します：

* TypeScript：生成されたプロセスはデフォルトで親環境を継承しますが、`options.env` を設定すると環境全体が置き換わります。ゲートウェイ変数を保つために `process.env` をそこに広げます。
* Python：`ClaudeAgentOptions(env=...)` は継承された環境の上にマージされるため、親プロセスで設定されたゲートウェイ変数は広げずに通ります。

<CodeGroup>
  ```ts TypeScript theme={null}
  const result = query({
    prompt: "...",
    options: {
      env: {
        ...process.env,
        ANTHROPIC_BASE_URL: "https://llm-gateway.example.com",
        ANTHROPIC_AUTH_TOKEN: process.env.GATEWAY_KEY,
      },
    },
  })
  ```

  ```python Python theme={null}
  options = ClaudeAgentOptions(
      env={
          "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
          "ANTHROPIC_AUTH_TOKEN": os.environ["GATEWAY_KEY"],
      }
  )
  ```
</CodeGroup>

<h3 id="slack-web-and-remote-control">
  Slack、ウェブ、Remote Control
</h3>

[Slack の Claude Code](/docs/ja/slack) と [ウェブの Claude Code](/docs/ja/claude-code-on-the-web) は、Anthropic がホストする製品で、常に Anthropic の API を使用します。ゲートウェイデプロイメントの一部ではありません。クラウドセッションの環境設定で設定されたゲートウェイ変数は適用されません。トラフィックがゲートウェイに留まる必要がある場合、これらのユーザーに対してこれらのサーフェスを有効にしないでください。

[Remote Control](/docs/ja/remote-control) と[音声ディクテーション](/docs/ja/voice-dictation)は両方とも claude.ai ID に依存します。Remote Control はライブセッションをアカウントとペアリングし、音声ディクテーションは claude.ai トランスクリプションエンドポイントに到達します。`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、または `apiKeyHelper` がアクティブな間は利用できません。v2.1.196 以降では、`ANTHROPIC_BASE_URL` が Anthropic 以外のホストを指している場合、Remote Control も無効になるため、claude.ai でサインインするだけでは十分ではありません。

どちらかの機能を復元するには、claude.ai でログインし、チェックするゲートウェイ変数を設定解除してください。`claude doctor` の Remote Control セクションは設定解除する認証情報変数の名前を表示します。

* 音声ディクテーション：ゲートウェイ認証情報を設定解除する
* Remote Control：ゲートウェイ認証情報と `ANTHROPIC_BASE_URL` を設定解除する

<h2 id="additional-configuration">
  追加設定
</h2>

これらの設定は基本 URL と認証情報を超えるケースをカバーしています。管理者の指示、ネットワークの出力ルール、または[トラブルシューティングテーブル](#troubleshoot-gateway-errors)が 1 つを呼び出す場合のみこれらを設定します。

<h3 id="send-additional-headers">
  追加ヘッダーを送信する
</h3>

一部のゲートウェイは、テナント識別子またはルーティングキーなど、認証情報に加えてカスタムヘッダーを使用してリクエストをルーティングまたはタグ付けします。1 つを送信するには、[`ANTHROPIC_CUSTOM_HEADERS`](/docs/ja/env-vars) を 1 行あたり 1 つの `Name: Value` ペアで設定します。以下の例は `X-Org-Route` という名前のルーティングヘッダーを追加します：

<Tabs>
  <Tab title="Bash または Zsh">
    ```bash theme={null}
    export ANTHROPIC_CUSTOM_HEADERS="X-Org-Route: prod"
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    $env:ANTHROPIC_CUSTOM_HEADERS = "X-Org-Route: prod"
    ```
  </Tab>
</Tabs>

設定ファイルの `env` ブロックで `ANTHROPIC_CUSTOM_HEADERS` を設定することもできます。JSON 文字列は複数行にまたがることができないため、ペア間で `\n` を使用します：

```json theme={null}
{
  "env": {
    "ANTHROPIC_CUSTOM_HEADERS": "X-Org-Route: prod\nX-Tenant: example"
  }
}
```

<h3 id="add-gateway-models-to-the-model-picker">
  ゲートウェイモデルをモデルピッカーに追加する
</h3>

モデル検出は起動時にゲートウェイにモデルリストをクエリし、それらの名前を組み込みエントリと一緒に `/model` ピッカーに追加します。

ゲートウェイが Claude Code の組み込みリストにないモデル名を提供し、ピッカーから選択したい場合は、それを有効にします。組み込みモデルが使用するものである場合、検出は不要です。管理者は管理設定を通じてすでに有効にしている可能性があります。

有効にするには、シェルまたは `~/.claude/settings.json` の `env` ブロックで `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` を設定します。検出には Claude Code v2.1.129 以降が必要です。

検出されたモデルは `From gateway` というラベルの追加 `/model` エントリとして表示されます。検出が実行されたことを確認するには、`claude --debug` を起動して `[gatewayDiscovery]` 行を探します。成功はキャッシュされたモデル数をログに記録し、`404`、タイムアウト、またはリダイレクトもそこに記録されます。検出が実行される場合、フィルタリング内容、ゲートウェイが提供するレスポンス形式については、[モデル検出リファレンス](/docs/ja/llm-gateway-protocol#model-discovery)を参照してください。

<h3 id="rotate-credentials-with-apikeyhelper">
  apiKeyHelper で認証情報をローテーションする
</h3>

`apiKeyHelper` は、静的環境変数から読み取る代わりに、ゲートウェイ認証情報を取得するために Claude Code が実行するコマンドです。

認証情報がスケジュールで期限切れになる場合、ボルトまたは SSO コマンドから来る場合、または管理者が 1 つを設定するよう指示した場合、ヘルパーを使用します。認証情報が 1 回設定する固定文字列である場合、[認証情報変数](#set-the-credential-variable)がすべて必要で、このセクションをスキップできます。

ヘルパーは現在の認証情報を stdout に出力するシェルコマンドです。Claude Code はシステムシェルを通じて実行するため、Windows ではそれは実行可能ファイルまたは PowerShell 呼び出しです。スクリプトを書き、実行可能にして、[設定ファイル](/docs/ja/settings)の `apiKeyHelper` から参照します：

<Tabs>
  <Tab title="Bash または Zsh">
    たとえば、ボルトから読み取るスクリプト：

    ```bash theme={null}
    #!/bin/bash
    vault kv get -field=api_key secret/llm-gateway/claude-code
    ```

    `~/.claude/settings.json` でそのパスを参照します：

    ```json theme={null}
    {
      "apiKeyHelper": "~/bin/get-gateway-key.sh"
    }
    ```
  </Tab>

  <Tab title="PowerShell">
    たとえば、ボルトから読み取るスクリプト：

    ```powershell theme={null}
    vault kv get -field=api_key secret/llm-gateway/claude-code
    ```

    `%USERPROFILE%\.claude\settings.json` で PowerShell 呼び出しを参照し、JSON 文字列のバックスラッシュをエスケープします：

    ```json theme={null}
    {
      "apiKeyHelper": "powershell -NoProfile -File C:\\scripts\\get-gateway-key.ps1"
    }
    ```
  </Tab>
</Tabs>

Claude Code はデフォルトでヘルパーの出力を 5 分間キャッシュし、リクエストが HTTP 401 を返すときに再度実行します。キャッシュ有効期間を変更するには、`CLAUDE_CODE_API_KEY_HELPER_TTL_MS` をミリ秒で設定します。たとえば、15 分の場合は `CLAUDE_CODE_API_KEY_HELPER_TTL_MS=900000` です。

ヘルパーの値は `Authorization` と `x-api-key` ヘッダーの両方で送信されるため、ゲートウェイがどちらのヘッダーを読むかに関わらず機能します。

<h3 id="turn-off-traffic-outside-the-gateway-path">
  ゲートウェイパス外のトラフィックをオフにする
</h3>

ゲートウェイはモデルリクエストを処理しますが、Claude Code はゲートウェイパス外の非必須バックグラウンドトラフィックも Anthropic および GitHub などのサードパーティサービスに送信します。バージョンチェック、テレメトリ、エラーレポート、リリースノート、および同様のリクエストです。ゲートウェイへの出力のみを許可するネットワークでは、これらのリクエストは失敗し、出力監視でブロックされた接続として表示される可能性があります。

そのトラフィックをオフにするには、ゲートウェイ変数と同じシェルエクスポートまたは設定ファイルの `env` ブロックで `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` を設定します：

<Tabs>
  <Tab title="Bash または Zsh">
    ```bash theme={null}
    export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    $env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
    ```
  </Tab>
</Tabs>

変数を設定すると、これらの効果と制限があります：

* 自動更新を無効にするため、パッケージマネージャーまたは管理配布などの別の更新パスを計画します。
* [高速モード](/docs/ja/fast-mode)の可用性チェックを抑制します。前のチェックがすでにマシンで高速モードを有効にしていない限り、`/fast` は高速モードが利用できないことを報告します。
* [ゲートウェイモデル検出](#add-gateway-models-to-the-model-picker)をオフにします。ただし、検出はゲートウェイ自体をクエリします。以前に検出されたモデルはローカルキャッシュから利用可能なままですが、リストは更新されません。
* WebFetch ツールの[ドメイン安全チェック](/docs/ja/data-usage#webfetch-domain-safety-check)は影響を受けず、引き続き `api.anthropic.com` を呼び出します。ネットワークがそのホストをブロックする場合、[設定](/docs/ja/settings)で `skipWebFetchPreflight: true` を使用して個別にオフにします。
* 各テレメトリストリームおよびそれを制御する変数については、[テレメトリサービス](/docs/ja/data-usage#telemetry-services)を参照してください。

<h3 id="route-to-a-cloud-provider-through-a-gateway">
  クラウドプロバイダーをゲートウェイ経由でルーティングする
</h3>

これらの設定は Claude Code を `ANTHROPIC_BASE_URL` の代わりにプロバイダー固有の基本 URL 変数を通じてゲートウェイに指定します。Amazon Bedrock と Google Cloud の Agent Platform ゲートウェイはそれらのプロバイダーのネイティブリクエスト形式を受け入れます。Microsoft Foundry と AWS 上の Claude Platform ゲートウェイは Anthropic Messages 形式を受け入れ、どの基本 URL 変数がそれらに到達するかでのみ異なります。

ゲートウェイチームが Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、または AWS 上の Claude Platform という名前を付けた場合のみ 1 つを使用します。上記の[検証リクエスト](#verify-the-connection)が JSON を返した場合、このセクションをスキップできます。

ゲートウェイチームが名前を付けたプロバイダーのブロックを設定します。skip-auth 変数は Claude Code にプロバイダー認証情報でリクエストに署名しないよう指示します。ゲートウェイがそれらを保持しているため。ゲートウェイが独自のトークンが必要な場合、Foundry を除いて、ブロックの後に `ANTHROPIC_AUTH_TOKEN` を追加します。Microsoft Foundry は示されているように `ANTHROPIC_FOUNDRY_API_KEY` を使用します。Bearer トークンを期待する Microsoft Foundry ゲートウェイは、代わりに [`ANTHROPIC_FOUNDRY_AUTH_TOKEN`](/docs/ja/env-vars) を使用できます。これは両方が設定されている場合、`ANTHROPIC_FOUNDRY_API_KEY` より優先されます。`ANTHROPIC_FOUNDRY_AUTH_TOKEN` には Claude Code v2.1.203 以降が必要です。

<h4 id="amazon-bedrock">
  Amazon Bedrock
</h4>

<Tabs>
  <Tab title="Bash または Zsh">
    ```bash theme={null}
    export ANTHROPIC_BEDROCK_BASE_URL=https://llm-gateway.example.com/bedrock
    export CLAUDE_CODE_SKIP_BEDROCK_AUTH=1
    export CLAUDE_CODE_USE_BEDROCK=1
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    $env:ANTHROPIC_BEDROCK_BASE_URL = "https://llm-gateway.example.com/bedrock"
    $env:CLAUDE_CODE_SKIP_BEDROCK_AUTH = "1"
    $env:CLAUDE_CODE_USE_BEDROCK = "1"
    ```
  </Tab>
</Tabs>

<h4 id="google-cloud’s-agent-platform">
  Google Cloud の Agent Platform
</h4>

<Tabs>
  <Tab title="Bash または Zsh">
    ```bash theme={null}
    export ANTHROPIC_VERTEX_BASE_URL=https://llm-gateway.example.com/vertex
    export ANTHROPIC_VERTEX_PROJECT_ID=your-gcp-project-id
    export CLAUDE_CODE_SKIP_VERTEX_AUTH=1
    export CLAUDE_CODE_USE_VERTEX=1
    export CLOUD_ML_REGION=us-east5
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    $env:ANTHROPIC_VERTEX_BASE_URL = "https://llm-gateway.example.com/vertex"
    $env:ANTHROPIC_VERTEX_PROJECT_ID = "your-gcp-project-id"
    $env:CLAUDE_CODE_SKIP_VERTEX_AUTH = "1"
    $env:CLAUDE_CODE_USE_VERTEX = "1"
    $env:CLOUD_ML_REGION = "us-east5"
    ```
  </Tab>
</Tabs>

<h4 id="microsoft-foundry">
  Microsoft Foundry
</h4>

ゲートウェイの認証情報を `ANTHROPIC_FOUNDRY_API_KEY` に入れます。`x-api-key` ヘッダーとしてゲートウェイに送信されます。Bearer トークンを期待するゲートウェイは、代わりに [`ANTHROPIC_FOUNDRY_AUTH_TOKEN`](/docs/ja/env-vars) を使用できます。Claude Code はその値を `Authorization: Bearer` ヘッダーとして送信し、両方が設定されている場合、`ANTHROPIC_FOUNDRY_API_KEY` より優先されます。Claude Code v2.1.203 以降が必要です。

独自の `Authorization` ヘッダーを挿入するゲートウェイの場合、`CLAUDE_CODE_SKIP_FOUNDRY_AUTH=1` を設定し、両方の認証情報変数を設定しないままにします。Claude Code はその後、Azure 認証情報なしでリクエストを送信し、たとえば `ANTHROPIC_CUSTOM_HEADERS` を通じて提供する `Authorization` ヘッダーを保持します。v2.1.203 より前では、API キーなしの `CLAUDE_CODE_SKIP_FOUNDRY_AUTH` は Microsoft Foundry クライアントがリクエストを送信できないままにしました。

<Tabs>
  <Tab title="Bash または Zsh">
    ```bash theme={null}
    export ANTHROPIC_FOUNDRY_BASE_URL=https://llm-gateway.example.com/foundry
    export ANTHROPIC_FOUNDRY_API_KEY=sk-gateway-key
    export CLAUDE_CODE_USE_FOUNDRY=1
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    $env:ANTHROPIC_FOUNDRY_BASE_URL = "https://llm-gateway.example.com/foundry"
    $env:ANTHROPIC_FOUNDRY_API_KEY = "sk-gateway-key"
    $env:CLAUDE_CODE_USE_FOUNDRY = "1"
    ```
  </Tab>
</Tabs>

<h4 id="claude-platform-on-aws">
  AWS 上の Claude Platform
</h4>

ワークスペース ID については、[AWS 上の Claude Platform](/docs/ja/claude-platform-on-aws) を参照してください。

<Tabs>
  <Tab title="Bash または Zsh">
    ```bash theme={null}
    export ANTHROPIC_AWS_BASE_URL=https://llm-gateway.example.com/anthropic-aws
    export ANTHROPIC_AWS_WORKSPACE_ID=wrkspc_01ABCDEFGHIJKLMN
    export CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH=1
    export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    $env:ANTHROPIC_AWS_BASE_URL = "https://llm-gateway.example.com/anthropic-aws"
    $env:ANTHROPIC_AWS_WORKSPACE_ID = "wrkspc_01ABCDEFGHIJKLMN"
    $env:CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH = "1"
    $env:CLAUDE_CODE_USE_ANTHROPIC_AWS = "1"
    ```
  </Tab>
</Tabs>

<h2 id="troubleshoot-gateway-errors">
  ゲートウェイエラーのトラブルシューティング
</h2>

これらはゲートウェイを通じて Claude Code を実行する場合の最も一般的なエラーで、ゲートウェイ側の原因と修正方法です：

| エラー                                                                                                                                                           | 原因                                                                                                                                                                                 | 修正                                                                                                                                                                                                                                                               |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2 つの認証情報ソースという名前の起動警告で、`auth may not work as expected` で終わります。古いバージョンは代わりに `Auth conflict: Both a token (SOURCE) and an API key (SOURCE) are set` を表示します。     | ゲートウェイ認証情報と保存されたログインの両方がアクティブです。変数はリクエストに使用されますが、古いログインは予期しない認証動作を引き起こす可能性があります                                                                                                    | 変数を設定解除して保存されたログインを使用するか、`/logout` を実行してゲートウェイ認証情報を使用します                                                                                                                                                                                                         |
| 無効または認識されないトークンという名前の `401` エラー                                                                                                                               | 認証情報はゲートウェイが発行したものではないか、ゲートウェイが読むヘッダーにあります                                                                                                                                         | [認証情報テーブル](#set-the-credential-variable)で変数が認証情報の種類と一致することを確認し、ゲートウェイで失効した場合はキーを再生成します                                                                                                                                                                           |
| `Your apiKeyHelper script is failing`                                                                                                                         | [`apiKeyHelper`](/docs/ja/settings#available-settings) 設定のコマンドがエラーで終了したか、タイムアウトしたか、何も出力しなかったため、リクエストはプレースホルダーキーを含みます                                                                    | コマンドを直接実行して失敗の理由を確認し、期限切れセッションを報告する場合は認証情報プロバイダーで再認証します。[エラーリファレンス](/docs/ja/errors#your-apikeyhelper-script-is-failing)を参照してください                                                                                                                                     |
| `Unable to connect to API (ConnectionRefused)`、または npm インストールからの `(ECONNREFUSED)`。多くの場合、Claude Code が[バックオフで再試行](/docs/ja/errors#automatic-retries)している間の静かな一時停止の後 | 基本 URL で何も応答しません。アドレスが間違っているか、VPN またはファイアウォールがゲートウェイへのパスをブロックしています                                                                                                                 | 上記の [curl テスト](#verify-the-connection)を実行します。これは同じ原因で直ちに失敗し、URL とネットワークパスをゲートウェイチームで確認します                                                                                                                                                                        |
| `API returned an empty or malformed response (HTTP 200)`                                                                                                      | ゲートウェイまたは中間プロキシが非 API レスポンス（多くの場合 HTML エラーまたはログインページ）を返しました                                                                                                                        | 上記の [curl リクエスト](#verify-the-connection)でテストします。非 JSON を返すゲートウェイルートを修正します                                                                                                                                                                                        |
| `context_management`、`Extra inputs are not permitted`、または他の認識されないフィールドという名前の `400` エラー                                                                        | ゲートウェイは Anthropic 形式エンドポイントに Claude Code が送信するフィールドを拒否する上流にリクエストを転送します                                                                                                             | `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` を設定します。これはほとんどのプレリリースフィールドを抑制します。[機能パススルー](/docs/ja/llm-gateway-protocol#feature-pass-through)を参照してください。一部のベータはこのフラグでゲートされていません。それらについては、一致する `CLAUDE_CODE_USE_*` プロバイダー変数を設定して、Claude Code がそのプロバイダーが受け入れるもののみを送信するようにします |
| `thinking` または `adaptive` という名前の `400` エラー（`Input tag 'adaptive' found` など）                                                                                   | 上流モデルビルドは Claude Code が Claude 4.6 以降のモデルに要求する適応推論を受け入れません                                                                                                                         | ゲートウェイの上流をアップグレードします。Opus 4.6 と Sonnet 4.6 では、代わりに `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` が機能します。[モデル設定](/docs/ja/model-config)機能変数は、`CLAUDE_CODE_USE_BEDROCK` や `CLAUDE_CODE_USE_VERTEX` などのプロバイダー設定にのみ適用され、`ANTHROPIC_BASE_URL` ゲートウェイの背後には適用されません               |
| ゲートウェイ独自の言葉でコンテキストまたはトークン制限を述べる `400` エラー（`ContextWindowExceededError` または `prompt token count of N exceeds the limit of M` など）                               | ゲートウェイはモデルのネイティブウィンドウより小さいコンテキストを強制し、上流エラーを書き直すため、Anthropic の `prompt is too long` 表現と一致する自動コンパクト再試行は発火しません                                                                        | `/compact` を実行してセッションを復旧します。防ぐには、`CLAUDE_CODE_AUTO_COMPACT_WINDOW` をゲートウェイの制限に設定します。値は少なくとも 100,000 トークン、最大でもモデルのコンテキストウィンドウにクランプされるため、100,000 未満のゲートウェイ制限は一致できず、`/compact` はそこでの復旧のままです。また、`CLAUDE_CODE_MAX_OUTPUT_TOKENS` をゲートウェイモデルの出力制限より下に設定します             |
| `/model` ピッカーから欠落しているモデル                                                                                                                                      | ゲートウェイモデル名は Claude Code の組み込みリストにありません                                                                                                                                             | [ゲートウェイモデル検出](#add-gateway-models-to-the-model-picker)を有効にするか、[モデル設定](/docs/ja/model-config)変数で名前を追加します                                                                                                                                                               |
| Claude Code は [curl テスト](#verify-the-connection)が成功しても、ログインするよう求めます                                                                                           | CLI には独自の認証情報がありません。到達可能な基本 URL は 1 つではなく、プロジェクトの `.claude/settings.json` または `.claude/settings.local.json` の `env` ブロックは最初の実行ウィザードと信頼プロンプトの後にのみ適用されます                             | `ANTHROPIC_AUTH_TOKEN` をどこかに設定します。Claude Code は最初の実行セットアップの前に読み取ります。シェルエクスポート、`~/.claude/settings.json` の `env` ブロック、または管理設定                                                                                                                                     |
| `ANTHROPIC_API_KEY` が設定されていますが、プロンプトなしで無視されます                                                                                                                 | キーはインタラクティブセッションで 1 回の承認が必要で、以前に拒否されたキーは再度尋ねられずに無視されます                                                                                                                             | `/config` で `Use custom API key` オプションで有効にします                                                                                                                                                                                                                    |
| `This machine's managed settings require a first-party login`                                                                                                 | 管理設定に `forceLoginMethod` または `forceLoginOrgUUID` が含まれています。Claude Code v2.1.146 以降では、`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、または `apiKeyHelper` と共存できません                         | 管理者は管理設定から `forceLoginMethod` と `forceLoginOrgUUID` を削除してゲートウェイ認証情報を使用するか、ゲートウェイ認証情報を削除してファーストパーティログインを使用する必要があります。2 つは組み合わせることはできません                                                                                                                            |
| `403` と HTML 本体（`403 Forbidden` など）。ゲートウェイ独自のログに受信したリクエストがない場合                                                                                                | ゲートウェイの前の Web アプリケーションファイアウォールまたはリバースプロキシがゲートウェイに到達する前にリクエスト本体をブロックしました。Claude Code プロンプトには XML スタイルタグとソースコードが含まれており、クロスサイトスクリプティング本体ルールと一致するため、短い curl テストは成功しますが、実際のセッションは成功しません | ゲートウェイの `/v1/messages` パスをリクエスト本体検査から除外します。AWS WAF ではこれは `CrossSiteScripting_Body` マネージドルールです。nginx と ModSecurity では、同等の OWASP CRS 本体ルールです                                                                                                                       |
| 証明書または TLS エラー（`SSL certificate verification failed` または `Self-signed certificate detected` など）。[curl テスト](#verify-the-connection)が成功する場合                     | Claude Code のランタイムは `curl` が使用するのと同じ認証局を信頼していません。一般的に企業 TLS 検査プロキシの背後                                                                                                              | `NODE_EXTRA_CA_CERTS` を CA バンドルパスに設定します。[CA 証明書ストア](/docs/ja/network-config#ca-certificate-store)を参照してください                                                                                                                                                            |

ゲートウェイ設定を削除した後、Claude Code が繰り返しログインするよう求める場合、原因は通常、ゲートウェイではなく認証情報ストレージです。[認証エラー](/docs/ja/errors#authentication-errors)を参照してください。

<h2 id="related-resources">
  関連リソース
</h2>

* [LLM ゲートウェイの概要](/docs/ja/llm-gateway)：ゲートウェイとは何か、および claude.ai サブスクリプションとどのように相互作用するか
* [組織用の LLM ゲートウェイをロールアウトする](/docs/ja/llm-gateway-rollout)：ゲートウェイをデプロイして配布するための管理者向けチェックリスト
* [ゲートウェイプロトコルリファレンス](/docs/ja/llm-gateway-protocol)：Claude Code がゲートウェイに送信するもの。ゲートウェイが転送する必要があるヘッダーとフィールドを含む
* [設定](/docs/ja/settings)：設定ファイルが存在する場所と `env` ブロックがどのように読み取られるか
* [認証](/docs/ja/authentication)：認証情報変数、`apiKeyHelper`、OAuth ログインがどのように相互作用するか
