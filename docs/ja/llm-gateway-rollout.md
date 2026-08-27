> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 組織向けの LLM ゲートウェイをロールアウトする

> Claude Code 用のゲートウェイ製品をデプロイします。Claude Code が送信する内容を転送するように設定し、開発者認証情報を発行し、マネージド設定を通じて設定を配布し、ロールアウトを検証します。

このページでは、管理者が Claude Code 用の LLM ゲートウェイをロールアウトする手順を説明します。[ゲートウェイ要件](#gateway-requirements)を満たすゲートウェイ製品がデプロイされていることを前提としています。特定の製品のデプロイまたは運用はここでは説明しません。ベンダーのドキュメントに従って、お客様のゲートウェイをデプロイしてください。

<Note>
  * 自分のマシン上の Claude Code を既存のゲートウェイに接続するには、[Claude Code を LLM ゲートウェイに接続する](/docs/ja/llm-gateway-connect)を参照してください
  * Claude Code がゲートウェイに送信する内容と転送する内容については、[ゲートウェイプロトコルリファレンス](/docs/ja/llm-gateway-protocol)を参照してください
</Note>

<h2 id="prerequisites">
  前提条件
</h2>

ロールアウトを完了するには、以下が必要です。

* インフラストラクチャにデプロイされたゲートウェイ。HTTPS で開発者に配布する正確なアドレスで提供され、リダイレクト先のアドレスではなく、Claude モデル名をプロバイダーにルーティングするように設定されている
* ゲートウェイが転送するプロバイダー認証情報。以下のいずれか。
  * Anthropic API の場合：[Claude Console](https://platform.claude.com/settings/keys)から取得した API キー
  * クラウドプロバイダーの場合：モデルアクセス権を持つクラウド認証情報。[Amazon Bedrock](/docs/ja/amazon-bedrock#prerequisites)、[Google Cloud の Agent Platform](/docs/ja/google-vertex-ai#prerequisites)、または [Microsoft Foundry](/docs/ja/microsoft-foundry#prerequisites)ページの前提条件を参照してください
* 開発者マシンに設定ファイルを配信する方法。MDM または設定管理など
  * まだない場合は、[設定がデバイスに到達する方法](/docs/ja/admin-setup#decide-how-settings-reach-devices)でオプションを比較してください

<h3 id="gateway-requirements">
  ゲートウェイ要件
</h3>

ゲートウェイを提供する製品がどれであれ、以下を満たす必要があります。

* **サポートされている API 形式を受け入れる**：[API 形式テーブル](/docs/ja/llm-gateway-protocol#api-formats)の形式のいずれか。以下のロールアウト手順は、ほとんどのゲートウェイが提供する `POST /v1/messages` の Anthropic Messages API を想定しています
* **レスポンスをストリーミングする**：サーバー送信イベントをバッファリングせずに到着時に通す
* **Claude モデル名をルーティングする**：開発者が使用する各名前をアップストリームモデルにマップする。Claude Code は各リクエストで `claude-sonnet-4-6` などのモデル名を送信します。ほとんどのゲートウェイ製品では、マッピングはゲートウェイ自体の設定内のモデルリストまたはルーティングテーブルです
* **ヘッダーと本文を変更せずに転送する**：`anthropic-beta`、`anthropic-version`、およびリクエスト本文を両方向で通す。[機能パススルーテーブル](/docs/ja/llm-gateway-protocol#feature-pass-through)は各機能をそれなしで破損するものにマップします
* **アップストリームエラーを変更せずに返す**：Claude Code の自動復旧はエラーの文言に一致するため、ゲートウェイ独自のエンベロープでエラーをラップすると破損します
* **リクエスト本文 WAF 検査からパスを除外する**：Claude Code プロンプトはソースコードと XML スタイルのタグを含み、クロスサイトスクリプティング本文ルールに一致します。ゲートウェイの前の WAF は実際のセッションで `403` を返しますが、短いテストリクエストは通ります

オプションで、`GET /v1/models` を提供して、Claude Code が [モデル検出](/docs/ja/llm-gateway-protocol#model-discovery)でゲートウェイからモデルピッカーを入力できるようにします。

<h2 id="rollout-steps">
  ロールアウト手順
</h2>

ロールアウトは 5 つのステップで構成され、各ステップにはチェックポイントがあります。

1. [ゲートウェイがモデルをルーティングすることを確認する](#confirm-the-gateway-routes-your-models)
2. [各開発者に認証情報を発行する](#issue-developer-credentials)
3. [ゲートウェイに対して Claude Code をテストする](#test-claude-code-against-the-gateway)
4. [ベース URL と認証情報を配布する](#distribute-the-configuration)
5. [開発者マシンから検証する](#verify-the-rollout)

ステップには 3 つの異なる認証情報が関係し、チェックポイントはプレースホルダーで名前を付けるため、何か失敗したときにどれが原因かを判断できます。

| 認証情報         | 保有者                                                         | チェックポイント内のプレースホルダー            |
| :----------- | :---------------------------------------------------------- | :---------------------------- |
| プロバイダー認証情報   | ゲートウェイ。アップストリームプロバイダーに転送します                                 | ゲートウェイで設定。クライアントコマンドには表示されません |
| ゲートウェイ管理認証情報 | お客様。ゲートウェイ製品が管理またはテストインターフェース用に発行する場合                       | `<gateway-key>`               |
| 開発者キー        | 各開発者。[開発者認証情報を発行する](#issue-developer-credentials)でゲートウェイが発行 | `<developer-key>`             |

<h3 id="confirm-the-gateway-routes-your-models">
  ゲートウェイがモデルをルーティングすることを確認する
</h3>

ゲートウェイはすでにプロバイダー認証情報で設定され、ベース URL でリッスンし、プロバイダーの API にリクエストを転送している必要があります。デプロイから 2 つの値を置き換えて、最小限のリクエストでパスが端から端まで機能することをテストします。

* `<gateway-key>` は、現在ゲートウェイを呼び出すことができる認証情報です。管理キー、テストキー、またはすでに発行した独自の開発者キー。すべてのゲートウェイ製品に個別の管理認証情報があるわけではありません。ない場合は、まず [開発者認証情報を発行する](#issue-developer-credentials)で自分用の開発者キーを発行してください
* `model` はゲートウェイがルーティングするように設定されている Claude モデル名です。例では `claude-sonnet-4-6` を使用しています。設定した名前に置き換えてください

<Tabs>
  <Tab title="Bash or Zsh">
    ```bash theme={null}
    curl -X POST "https://llm-gateway.example.com/v1/messages" \
      -H "Authorization: Bearer <gateway-key>" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    Invoke-RestMethod -Method Post -Uri "https://llm-gateway.example.com/v1/messages" `
      -Headers @{ "Authorization" = "Bearer <gateway-key>"; "anthropic-version" = "2023-06-01" } `
      -ContentType "application/json" `
      -Body '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
    ```
  </Tab>
</Tabs>

**チェックポイント**：`content` フィールドを持つ `200` は、ゲートウェイがそのモデル名でプロバイダーに到達したことを意味します。`404` はその名前がゲートウェイでルーティングされていないことを意味します。プロバイダーからの `401` はゲートウェイのプロバイダー認証情報が間違っていることを意味します。

ゲートウェイのルーティング設定内の Claude モデル名ごとに 1 回リクエストを繰り返します。ゲートウェイがルーティングしない名前は、それを選択した開発者に `404` を返すため、ロールアウト前にすべての名前をテストしてください。

<Note>
  ゲートウェイをリダイレクトの背後で提供することは避けてください。リダイレクトはリクエスト本文をドロップするか、推論リクエストで認証情報ヘッダーをストリップでき、[モデル検出](/docs/ja/llm-gateway-protocol#model-discovery)はリダイレクトを失敗として扱うため、認証情報がリダイレクト先にリークする可能性があります。
</Note>

<h3 id="issue-developer-credentials">
  開発者認証情報を発行する
</h3>

各開発者はゲートウェイで認証するために独自のゲートウェイキーが必要です。製品の認証情報管理ドキュメントに従って、ゲートウェイで開発者ごとに認証情報を作成します。

新しく発行されたキーが [ゲートウェイがモデルをルーティングすることを確認する](#confirm-the-gateway-routes-your-models)と同じリクエストでゲートウェイに対して機能することを確認し、`<gateway-key>` を新しい `<developer-key>` に置き換えます。

<Tabs>
  <Tab title="Bash or Zsh">
    ```bash theme={null}
    curl -X POST "https://llm-gateway.example.com/v1/messages" \
      -H "Authorization: Bearer <developer-key>" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    Invoke-RestMethod -Method Post -Uri "https://llm-gateway.example.com/v1/messages" `
      -Headers @{ "Authorization" = "Bearer <developer-key>"; "anthropic-version" = "2023-06-01" } `
      -ContentType "application/json" `
      -Body '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
    ```
  </Tab>
</Tabs>

**チェックポイント**：`content` フィールドを持つ `200` は、開発者キーがゲートウェイに到達し、ゲートウェイが転送することを意味します。[前のステップ](#confirm-the-gateway-routes-your-models)が成功したときにここで `401` が表示される場合は、開発者キーが間違っているか、ゲートウェイでまだ有効になっていないことを意味します。

開発者ごとに 1 つのキーを発行することは、共有キーではなく、開発者ごとの使用状況の属性化と個別のオフボーディングを機能させるものです。キーを保持する環境変数は、ゲートウェイがどのヘッダーを読むかによって異なります。`Authorization: Bearer` ヘッダーで認証情報をチェックするゲートウェイの場合、開発者は `ANTHROPIC_AUTH_TOKEN` でキーを設定します。`x-api-key` ヘッダーからキーを読むゲートウェイの場合、開発者は代わりに `ANTHROPIC_API_KEY` を設定します。[認証情報テーブル](/docs/ja/llm-gateway-connect#set-the-credential-variable)はマッピングをカバーしています。

<h3 id="test-claude-code-against-the-gateway">
  ゲートウェイに対して Claude Code をテストする
</h3>

ロールアウトが配布する前に、同じ設定を使用してゲートウェイを通じて Claude Code を自分で実行します。これらを `.env` または設定ファイルではなく、ターミナルに直接入力します。これらはこのターミナルセッションのみ続くため、閉じるとマシンは通常の設定に戻ります。ゲートウェイが `x-api-key` ヘッダーを読む場合は、`ANTHROPIC_AUTH_TOKEN` の代わりに `ANTHROPIC_API_KEY` を使用します。

<Tabs>
  <Tab title="Bash or Zsh">
    ```bash theme={null}
    export ANTHROPIC_BASE_URL=https://llm-gateway.example.com
    export ANTHROPIC_AUTH_TOKEN="<developer-key>"
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    $env:ANTHROPIC_BASE_URL = "https://llm-gateway.example.com"
    $env:ANTHROPIC_AUTH_TOKEN = "<developer-key>"
    ```
  </Tab>
</Tabs>

次に、ゲートウェイを通じてワンショットプロンプトを送信します。

```bash theme={null}
claude -p "Reply with one word: connected"
```

**チェックポイント**：プロンプトはレスポンスを返し、リクエストはゲートウェイのログに `/v1/messages` パスへの `POST` として状態 `200` で表示されます。Claude Code は `?beta=true` などのクエリ文字列を追加するため、完全な URL ではなくパスで一致させます。2 つの失敗メッセージは異なる方向を指します。

* `Not logged in`：ゲートウェイログをチェックして 2 つの原因を区別します。空の場合、認証情報がセッションに到達せず、リクエストがマシンを離れません。テストしているシェルでエクスポートを再実行してください。`401` 本文に `x-api-key` を示す拒否されたリクエストが表示される場合、ゲートウェイはそのヘッダーでキーを期待しています。`ANTHROPIC_API_KEY` に切り替えてください
* `Failed to authenticate. API Error: 401` は認証情報が送信され、拒否されたことを意味し、ゲートウェイログはどこかを示します。`api.anthropic.com` またはプロバイダーのエンドポイントに名前を付ける `401` は、ゲートウェイがアップストリームに到達したが、保持するプロバイダー認証情報が拒否されたことを意味するため、開発者キーは機能し、ゲートウェイが保持するプロバイダー認証情報が間違っているか、プレースホルダーです

間違っているか到達不可能なベース URL は異なる症状を生成します。Claude Code は [バックオフで接続を再試行](/docs/ja/errors#automatic-retries)し、エラーを報告する前に数分間出力なしで待機できます。コマンドがハングしているように見える場合は、待つ代わりにゲートウェイログをチェックしてください。到着するリクエストがないことは、`ANTHROPIC_BASE_URL` がゲートウェイを指していないことを意味します。

<h3 id="distribute-the-configuration">
  設定を配布する
</h3>

すべての開発者マシンにはゲートウェイアドレスと認証情報が必要です。[マネージド設定](/docs/ja/settings#settings-files)を通じて中央から配布できるため、開発者は何も設定しないか、開発者に値を手動で設定させます。

<h4 id="what-to-distribute">
  配布する内容
</h4>

どのパスを選択するかに関わらず、同じ変数セットが適用されます。ほとんどのロールアウトは `ANTHROPIC_BASE_URL` と認証情報のみが必要です。ゲートウェイセットアップが必要とする場合は、条件付き行を含めます。

| 変数または設定                                                                                                                                                                                                 | 機能                                                                                                                             | 含める場合                                                                                                                                                                                                                                                                                                |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ANTHROPIC_BASE_URL`                                                                                                                                                                                    | Claude Code の API リクエストを `api.anthropic.com` の代わりにゲートウェイに送信します                                                                 | 常に                                                                                                                                                                                                                                                                                                   |
| `apiKeyHelper`、または `ANTHROPIC_AUTH_TOKEN` または `ANTHROPIC_API_KEY` の認証情報                                                                                                                                 | ゲートウェイへの各リクエストを認証します。ヘルパーはキーを取得するコマンドを実行します。変数は静的キーを保持し、`Authorization: Bearer` および `x-api-key` としてそれぞれ送信されます                  | 常に。3 つのうち 1 つ                                                                                                                                                                                                                                                                                        |
| `ANTHROPIC_CUSTOM_HEADERS`                                                                                                                                                                              | すべての API リクエストに追加の HTTP ヘッダーを追加します                                                                                             | ゲートウェイがすべてのリクエストでテナントまたはルーティングヘッダーを必要とする場合                                                                                                                                                                                                                                                           |
| `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY`                                                                                                                                                            | 起動時にゲートウェイの `/v1/models` をクエリし、返された名前を `/model` ピッカーに追加します                                                                     | ゲートウェイが `/v1/models` を提供し、開発者のピッカーをそこから入力したい場合                                                                                                                                                                                                                                                       |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`                                                                                                                                                                | Claude Code がプリリリース機能ヘッダーと本文フィールドを送信するのを停止します                                                                                  | ゲートウェイが Amazon Bedrock または Google Cloud の Agent Platform アップストリームに転送し、ベータフィールドを拒否する場合。[ゲートウェイ要件](#gateway-requirements)を参照してください                                                                                                                                                                     |
| `ANTHROPIC_MODEL` または [`ANTHROPIC_DEFAULT_HAIKU_MODEL`](/docs/ja/model-config)                                                                                                                               | Claude Code がメインセッションとバックグラウンドトラフィックに要求するモデル名を設定します                                                                            | ゲートウェイが Claude Code のデフォルトと一致しないモデル名をルーティングするか、[バックグラウンド機能](/docs/ja/costs#background-token-usage)を別のモデルにルーティングする場合。オーバーライド名と Claude Code がオーバーライドが設定されていないときにリクエストする組み込みモデル ID の両方をゲートウェイでルーティングします。一部のバックグラウンドサブコールはオーバーライドに関わらず組み込み ID をリクエストできるため。[モデル設定](/docs/ja/model-config)は各セッション部分が使用するモデルをカバーしています |
| `ANTHROPIC_BEDROCK_BASE_URL`、`ANTHROPIC_VERTEX_BASE_URL`、`ANTHROPIC_FOUNDRY_BASE_URL`、または `ANTHROPIC_AWS_BASE_URL` と [そのプロバイダーの変数](/docs/ja/llm-gateway-connect#route-to-a-cloud-provider-through-a-gateway) | Claude Code をプロバイダー固有のベース URL を通じてゲートウェイに指します。Amazon Bedrock と Google Cloud の Agent Platform はそれらのプロバイダーのネイティブリクエスト形式にも切り替わります | ゲートウェイが Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、または AWS 上の Claude Platform の前にある場合。[API 形式](/docs/ja/llm-gateway-protocol#api-formats)を参照してください                                                                                                                                    |

<h4 id="distribute-through-managed-settings">
  マネージド設定を通じて配布する
</h4>

[マネージド設定ファイル](/docs/ja/settings#settings-files)の `env` ブロックを通じて変数を配信し、MDM、レジストリポリシー、または設定管理によってプッシュします。

```json theme={null}
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com"
  },
  "apiKeyHelper": "/usr/local/bin/get-gateway-key"
}
```

テーブルから条件付き変数を同じ `env` ブロックに追加します。マネージド `ANTHROPIC_BASE_URL` は強制され、Claude Code がプロセス環境と低優先度の設定の上に適用するため、開発者のシェルエクスポートでオーバーライドできません。

マネージド設定にゲートウェイ認証情報と一緒に `forceLoginMethod` または `forceLoginOrgUUID` を含めないでください。Claude Code v2.1.146 以降では、どちらのキーも起動時に `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、および `apiKeyHelper` をブロックするため、開発者は `This machine's managed settings require a first-party login` を見て進むことができません。

[サーバー管理設定](/docs/ja/server-managed-settings#platform-availability)配信には `api.anthropic.com` への直接接続が必要なため、ゲートウェイルーティングセッションに到達しません。ゲートウェイデプロイメントはこのファイルベースのマネージド設定パスを使用し、同じキーを強制します。

認証情報については、上記のように、マネージド設定ファイルで 1 つの [`apiKeyHelper`](/docs/ja/llm-gateway-connect#rotate-credentials-with-apikeyhelper) コマンドを配布します。コマンドはローカル開発者としてシークレットストアに認証するため、各マシンは独自のキーを受け取ります。または、既存のシークレットプロセスを通じて各開発者にキーを配信し、`ANTHROPIC_AUTH_TOKEN` を自分で設定させます。

一部の環境には個別の配信が必要です。

* デスクトップアプリはゲートウェイルーティングをマネージド設定ではなく、サードパーティ推論設定から読み取ります。デスクトップセッションもゲートウェイを通じてルーティングするように、マネージド設定と一緒にそのファイルを MDM 経由でデプロイします。[デスクトップサードパーティ設定ドキュメント](https://claude.com/docs/third-party/claude-desktop/configuration)と [デスクトップゲートウェイドキュメント](https://claude.com/docs/third-party/claude-desktop/gateway)を参照してください
* CI ランナーは [ランナーの環境](/docs/ja/llm-gateway-connect#configure-each-surface)で `ANTHROPIC_BASE_URL` と認証情報を設定する必要があります
* マネージド Windows マシン上の WSL は、[`wslInheritsWindowsSettings`](/docs/ja/settings#available-settings) が `true` の場合にのみ Windows マネージド設定を読み取ります

<h4 id="hand-developers-the-values-to-set-themselves">
  開発者に値を自分で設定させる
</h4>

マネージド設定配布が設定されていない場合は、各開発者に [接続ページ](/docs/ja/llm-gateway-connect#configure-claude-code-yourself)に従うために必要なものを送信します。

* ゲートウェイ URL
* 個人認証情報
* **認証情報を入れる変数**：ベアラートークンゲートウェイの場合は `ANTHROPIC_AUTH_TOKEN`、`x-api-key` ゲートウェイの場合は `ANTHROPIC_API_KEY`。開発者にどちらかを伝えることで、[接続ページ](/docs/ja/llm-gateway-connect#set-the-credential-variable)で説明されている試行錯誤を節約できます
* [配布する内容テーブル](#what-to-distribute)からの条件付き変数。その値を含む

[接続ページ](/docs/ja/llm-gateway-connect#configure-claude-code-yourself)は開発者に各変数の設定を説明します。

**チェックポイント**：開発者マシンで、`claude` はログイン画面を表示せずにセッションを開始します。配布された認証情報が認証を満たすため。次に `/status` を実行し、**Status** タブを開きます。`Anthropic base URL` 行はゲートウェイアドレスを表示し、マネージド配布の場合、`Setting sources` 行にはマネージド設定が含まれます。ログイン画面、または欠落している `Anthropic base URL` 行は、設定がマシンに到達しなかったことを意味します。

<h3 id="verify-the-rollout">
  ロールアウトを検証する
</h3>

ゲートウェイホストではなく開発者マシンからすべてが機能することを確認し、テストが開発者が使用するネットワークパスをカバーするようにします。ストリーミングリクエストを送信します。これはエンドポイント、ストリーミングパススルー、およびモデルルーティングを一度にチェックします。

<Tabs>
  <Tab title="Bash or Zsh">
    ```bash theme={null}
    curl -N -X POST "https://llm-gateway.example.com/v1/messages" \
      -H "Authorization: Bearer <developer-key>" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d '{"model": "claude-sonnet-4-6", "max_tokens": 16, "stream": true, "messages": [{"role": "user", "content": "count to 3"}]}'
    ```
  </Tab>

  <Tab title="PowerShell">
    ```powershell theme={null}
    $body = '{"model": "claude-sonnet-4-6", "max_tokens": 16, "stream": true, "messages": [{"role": "user", "content": "count to 3"}]}'
    $body | curl.exe -N -X POST "https://llm-gateway.example.com/v1/messages" `
      -H "Authorization: Bearer <developer-key>" `
      -H "anthropic-version: 2023-06-01" `
      -H "content-type: application/json" `
      --data-binary '@-'
    ```
  </Tab>
</Tabs>

`data:` 行が段階的に到着するのが見えるはずです。一時停止後に全レスポンスが一度に到着することは、ゲートウェイがバッファリングしていることを意味し、Claude Code をスタールさせます。`404` はモデル名がルーティングされていないことを意味します。モデル名ごとに繰り返します。

次に `claude` を開始し、メッセージを送信します。このステップでの各症状には 1 つの原因があります。

* ログインプロンプトは認証情報ギャップを意味します。`/status` を実行し、**Status** タブを開きます。`Setting sources` 行にマネージド設定が含まれていない場合、配布がマシンに到達しませんでした。含まれている場合、開発者認証情報が配布されなかったため、`ANTHROPIC_AUTH_TOKEN` または `apiKeyHelper` を設定します
* `Failed to authenticate` エラーはゲートウェイがリクエストを拒否していることを意味します。そのログは、どの認証情報が失敗したかを示します。ゲートウェイ自体がログする拒否は開発者キーに名前を付けますが、`api.anthropic.com` またはプロバイダーのエンドポイントからの `401` は、ゲートウェイが保持するプロバイダー認証情報が拒否されたことを意味します
* ゲートウェイが `x-api-key` ヘッダーでキーを期待する場合、`ANTHROPIC_API_KEY` として設定されたときの 1 回限りの承認プロンプトは予想されます。`ANTHROPIC_AUTH_TOKEN` では、プロンプトは表示されず、変数は静かに引き継ぎます。以前に保存された claude.ai ログインはそのセッションでは非アクティブです

最後に、送信したメッセージのゲートウェイログをチェックします。認証情報は開発者を識別し、[`x-claude-code-session-id` ヘッダー](/docs/ja/llm-gateway-protocol#request-headers)はセッション別にリクエストをグループ化します。機能が [トラブルシューティング症状](/docs/ja/llm-gateway-connect#troubleshoot-gateway-errors)で失敗する場合、ゲートウェイはヘッダーをストリップするか、エラーを書き直しています。上記の [ゲートウェイ要件](#gateway-requirements)を参照してください。

<h2 id="maintain-the-gateway">
  ゲートウェイを維持する
</h2>

ロールアウト後、3 種類の変更が時間とともにゲートウェイに到達します。各変更には、監視する症状と実行するアクションがあります。

| 変更                                                          | ゲートウェイが追いついていない場合の症状                                                                                                      | アクション                                                                                                                                                                    |
| :---------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 新しい Claude Code リリースは `anthropic-beta` 値とリクエスト本文フィールドを追加します | 開発者は Claude Code を更新した後、新しいフィールドに名前を付ける `400` エラーを報告します。[機能パススルー](/docs/ja/llm-gateway-protocol#feature-pass-through)を参照してください | `anthropic-*` ヘッダーとリクエスト本文を許可リストではなく逐語的に転送します。新しい Claude Code リリースを開発者に到達する前にゲートウェイに対してテストします                                                                            |
| 新しい Claude モデルが利用可能になります                                    | 開発者が新しいモデル名を選択すると `404` が表示されます。`/model` ピッカーはそれをリストしません                                                                  | モデル名をゲートウェイのルーティング設定に追加し、[ルーティングチェック](#confirm-the-gateway-routes-your-models)を再実行します。`ANTHROPIC_MODEL` またはデフォルトモデル変数を配布する場合は、マネージド設定を更新します                              |
| 認証情報の有効期限が切れるか、ローテーションが必要です                                 | すべての開発者リクエストがアップストリームからの `401` で失敗し始めます                                                                                   | ゲートウェイのプロバイダー認証情報を独自のスケジュールでローテーションします。開発者キーはゲートウェイでローテーションし、[`apiKeyHelper`](/docs/ja/llm-gateway-connect#rotate-credentials-with-apikeyhelper)は設定を再配布せずに開発者ごとのローテーションを処理します |

キーごとのレート制限をサイズ設定するときは、クライアント [一時的な障害を再試行](/docs/ja/errors#automatic-retries)することを考慮に入れます。`429` レスポンスを含め、バックオフで最大 10 回、`Retry-After` を尊重します。[プロトコルリファレンス](/docs/ja/llm-gateway-protocol)を各 Claude Code リリースが送信する内容の契約として保持します。

<h2 id="related-resources">
  関連リソース
</h2>

* [Claude Code を LLM ゲートウェイに接続する](/docs/ja/llm-gateway-connect)：開発者向けのセットアップ手順。サーフェスごとの設定とトラブルシューティングテーブル。開発者に配布できます
* [ゲートウェイプロトコルリファレンス](/docs/ja/llm-gateway-protocol)：ゲートウェイオペレーター向けのワイヤコントラクト。エンドポイント、転送するヘッダー、および機能パススルーテーブルをカバーしています
* [設定ファイルと優先度](/docs/ja/settings#settings-files)：マネージド、プロジェクト、およびユーザー設定がどのように組み合わさるか、および各プラットフォームでマネージドファイルがどこに行くか
* [組織向けに Claude Code をセットアップする](/docs/ja/admin-setup)：このゲートウェイが一部である広いロールアウト。ポリシー強制、使用状況の可視性、およびデータ処理を含みます
