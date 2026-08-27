> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# サーバー管理設定を構成する

> デバイス管理インフラストラクチャを必要とせずに、Claude.ai 上のウェブベースインターフェースを通じて、組織全体で Claude Code を一元的に構成します。

サーバー管理設定により、組織の所有者は claude.ai コンソールの [**Admin Settings > Claude Code > Managed settings**](https://claude.ai/admin-settings/claude-code) から Claude Code を一元的に構成できます。Claude Code クライアントは、ユーザーが組織の OAuth ログインまたは直接構成された API キーで認証すると、これらの設定を自動的に取得します。サーバー管理配信がサポートされているプラットフォームについては、[プラットフォームの可用性](#platform-availability)を参照してください。

このアプローチは、デバイス管理インフラストラクチャが導入されていない組織、または管理されていないデバイス上のユーザーの設定を管理する必要がある組織向けに設計されています。

<Note>
  サーバー管理設定は [Claude for Teams](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=server_settings_teams#team-&-enterprise) および [Claude for Enterprise](https://anthropic.com/contact-sales?utm_source=claude_code\&utm_medium=docs\&utm_content=server_settings_enterprise) カスタマー向けに利用可能です。
</Note>

<h2 id="requirements">
  要件
</h2>

サーバー管理設定を使用するには、以下が必要です。

* Claude for Teams または Claude for Enterprise プラン
* Claude 組織の Owner または Primary Owner ロール（設定を表示および編集するため）
* `api.anthropic.com` へのネットワークアクセス

<h2 id="choose-between-server-managed-and-endpoint-managed-settings">
  サーバー管理設定とエンドポイント管理設定の選択
</h2>

Claude Code は、一元的な構成のための 2 つのアプローチをサポートしています。サーバー管理設定は Anthropic のサーバーから構成を配信します。[エンドポイント管理設定](/docs/ja/settings#settings-files)は、ネイティブ OS ポリシー（macOS 管理設定、Windows レジストリ）または管理設定ファイルを通じてデバイスに直接配置されます。

| アプローチ                                          | 最適な用途                           | セキュリティモデル                                          |
| :--------------------------------------------- | :------------------------------ | :------------------------------------------------- |
| **サーバー管理設定**                                   | MDM がない組織、または管理されていないデバイス上のユーザー | 認証時に Anthropic のサーバーから配信される設定                      |
| **[エンドポイント管理設定](/docs/ja/settings#settings-files)** | MDM またはエンドポイント管理がある組織           | MDM 構成プロファイル、レジストリポリシー、または管理設定ファイルを通じてデバイスに配置される設定 |

デバイスが MDM またはエンドポイント管理ソリューションに登録されている場合、エンドポイント管理設定はより強力なセキュリティ保証を提供します。これは、設定ファイルが OS レベルでユーザーの変更から保護される可能性があるためです。エンドポイント管理設定は[クラウドセッション](/docs/ja/model-config#surface-coverage)に到達しないため、Web 上で Claude Code を使用する組織はサーバー管理設定も構成する必要があります。

<h2 id="configure-server-managed-settings">
  サーバー管理設定を構成する
</h2>

<Steps>
  <Step title="管理コンソールを開く">
    claude.ai コンソールで、[**Admin Settings > Claude Code > Managed settings**](https://claude.ai/admin-settings/claude-code) に移動します。

    リンクが Claude Code ページではなく別の Admin Settings ページにリダイレクトされる場合、アカウントに必要なロールがありません。Admin およびその他の Owner 以外のロールは管理設定を表示または編集できないため、組織内の Owner または Primary Owner に変更を依頼してください。[アクセス制御](#access-control)を参照してください。
  </Step>

  <Step title="設定を定義する">
    構成を JSON として追加します。`settings.json` で利用可能な[すべての設定](/docs/ja/settings#available-settings)がサポートされており、OS レベルのポリシー配信に制限されているものを除きます。[現在の制限事項](#current-limitations)でその短いリストを参照してください。これには[hooks](/docs/ja/hooks)、[環境変数](/docs/ja/env-vars)、および `allowManagedPermissionRulesOnly` などの[管理専用設定](/docs/ja/permissions#managed-only-settings)が含まれます。

    この例は、権限拒否リストを適用し、ユーザーが権限をバイパスするのを防ぎ、権限ルールを管理設定で定義されたものに制限します。

    ```json theme={null}
    {
      "permissions": {
        "deny": [
          "Bash(curl *)",
          "Read(./.env)",
          "Read(./.env.*)",
          "Read(./secrets/**)"
        ],
        "disableBypassPermissionsMode": "disable"
      },
      "allowManagedPermissionRulesOnly": true
    }
    ```

    hooks は `settings.json` と同じ形式を使用します。

    この例は、組織全体のすべてのファイル編集後に監査スクリプトを実行します。

    ```json theme={null}
    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Edit|Write",
            "hooks": [
              { "type": "command", "command": "/usr/local/bin/audit-edit.sh" }
            ]
          }
        ]
      }
    }
    ```

    [auto mode](/docs/ja/permission-modes#eliminate-prompts-with-auto-mode) 分類器を構成して、組織が信頼するリポジトリ、バケット、ドメインを認識させるには、以下のようにします。

    ```json theme={null}
    {
      "autoMode": {
        "environment": [
          "Source control: github.example.com/acme-corp and all repos under it",
          "Trusted cloud buckets: s3://acme-build-artifacts, gs://acme-ml-datasets",
          "Trusted internal domains: *.corp.example.com"
        ]
      }
    }
    ```

    hooks はシェルコマンドを実行するため、ユーザーは適用される前に[セキュリティ承認ダイアログ](#security-approval-dialogs)を表示します。`autoMode` エントリが分類器がブロックする内容にどのように影響するか、および `environment`、`allow`、`soft_deny`、および `hard_deny` フィールドに関する重要な警告については、[auto mode を構成する](/docs/ja/auto-mode-config)を参照してください。
  </Step>

  <Step title="保存してデプロイする">
    変更を保存します。Claude Code クライアントは、次回の起動時または 1 時間ごとのポーリングサイクルで更新された設定を受け取ります。
  </Step>
</Steps>

<h3 id="verify-settings-delivery">
  設定配信の確認
</h3>

設定が適用されていることを確認するには、ユーザーに Claude Code を再起動するよう依頼します。構成に[セキュリティ承認ダイアログ](#security-approval-dialogs)をトリガーする設定が含まれている場合、ユーザーは起動時に管理設定を説明するプロンプトを表示します。また、ユーザーに `/permissions` を実行して有効な権限ルールを表示させることで、管理権限ルールがアクティブであることを確認することもできます。

<h3 id="access-control">
  アクセス制御
</h3>

以下のロールがサーバー管理設定を管理できます。

* **Primary Owner**
* **Owner**

設定の変更は組織内のすべてのユーザーに適用されるため、信頼できる担当者へのアクセスを制限してください。

<h3 id="managed-only-settings">
  管理専用設定
</h3>

ほとんどの[設定キー](/docs/ja/settings#available-settings)は任意のスコープで機能します。いくつかのキーは管理設定からのみ読み込まれ、ユーザーまたはプロジェクト設定ファイルに配置された場合は効果がありません。完全なリストについては、[管理専用設定](/docs/ja/permissions#managed-only-settings)を参照してください。そのリストにない設定は、管理設定に配置することができ、最高の優先度を持ちます。

<h3 id="current-limitations">
  現在の制限事項
</h3>

サーバー管理設定には、以下の制限があります。

* 設定は組織内のすべてのユーザーに均一に適用されます。グループごとの構成はまだサポートされていません。
* [`managed-mcp.json`](/docs/ja/managed-mcp) ファイルはサーバー管理設定を通じて配布することはできません。代わりに `allowedMcpServers` および `deniedMcpServers` ポリシーキーをそこに配信してください。
* `policyHelper` および `wslInheritsWindowsSettings` など、OS レベルのポリシーソースに制限されている設定は、尊重されません。代わりに MDM またはシステム `managed-settings.json` ファイルを通じてデプロイしてください。

<h2 id="settings-delivery">
  設定配信
</h2>

<h3 id="settings-precedence">
  設定の優先順位
</h3>

サーバー管理設定と[エンドポイント管理設定](/docs/ja/settings#settings-files)は、Claude Code [設定階層](/docs/ja/settings#settings-precedence)の最上位を占めます。コマンドライン引数を含む他の設定レベルはこれらをオーバーライドできません。管理層内では、設定された [`policyHelper`](/docs/ja/settings#compute-managed-settings-with-a-policy-helper) は他のすべての管理ソース（サーバー管理設定を含む）に優先します。その出力は実行のための唯一の管理構成になります。それ以外の場合、Claude Code は空でない構成を配信する最初のソースを使用します。サーバー管理設定が最初にチェックされ、次にエンドポイント管理設定がチェックされます。ソースはマージされません。サーバー管理設定がキーを配信する場合、他のエンドポイント管理設定は無視されます。サーバー管理設定が何も配信しない場合、エンドポイント管理設定が適用されます。

1 つの例外が適用されます。[クロスソースロックキー](/docs/ja/settings#settings-precedence)（サンドボックスホワイトリストロックなど）の小さなセットは、管理者が管理する管理ソースがそれらを設定する場合に尊重されます。ユーザーが書き込み可能な HKCU レジストリ層は除外されます。

管理コンソールでサーバー管理構成をクリアして、エンドポイント管理 plist またはレジストリポリシーにフォールバックする意図がある場合、[キャッシュされた設定](#fetch-and-caching-behavior)はクライアントマシンに保持され、次の成功したフェッチまで続きます。`/status` を実行して、どの管理ソースがアクティブであるかを確認してください。

<h3 id="fetch-and-caching-behavior">
  フェッチとキャッシング動作
</h3>

Claude Code は起動時に Anthropic のサーバーから設定をフェッチし、アクティブなセッション中は 1 時間ごとに更新をポーリングします。

**キャッシュされた設定なしの初回起動：**

* Claude Code は非同期で設定をフェッチします
* フェッチが失敗した場合、Claude Code は管理設定なしで続行します
* 設定が読み込まれるまでの短い期間があり、その間は制限が適用されません

**キャッシュされた設定での後続の起動：**

* キャッシュされた設定は起動時に直ちに適用されます。ただし、以下で説明するトランスポート、ルーティング、認証環境変数は除きます
* Claude Code はバックグラウンドで新しい設定をフェッチします
* キャッシュされた設定はネットワーク障害を通じて保持されます。保留中の環境変数はフェッチが成功するまで保留されたままです

v2.1.198 以降、Claude Code はセッションのペイロードをサーバーが確認するまで、キャッシュされた `env` ブロック内の 3 つのカテゴリの変数を保留します。これにより、キャッシュされたプロキシ、認証局、エンドポイント、または認証情報の値がペイロードを確認する設定フェッチをリダイレクト、傍受、または再認証することを防ぎます。強化はサーバーがフェッチした設定キャッシュにのみ適用されます。MDM または `managed-settings.json` を通じてデプロイされた[エンドポイント管理設定](/docs/ja/settings#settings-files)は影響を受けません。保留中のカテゴリは以下の通りです。

* `HTTPS_PROXY`、`NODE_EXTRA_CA_CERTS`、mTLS クライアント証明書変数 `CLAUDE_CODE_CLIENT_CERT` および `CLAUDE_CODE_CLIENT_KEY` などのプロキシと TLS 構成
* `ANTHROPIC_BASE_URL`、`CLAUDE_CODE_USE_BEDROCK` および `CLAUDE_CODE_USE_VERTEX` などのプロバイダー選択変数、`ANTHROPIC_BEDROCK_BASE_URL` などのプロバイダーエンドポイント URL を含む API ルーティングとプロバイダー選択
* `ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`CLAUDE_CODE_OAUTH_TOKEN` などの認証認証情報

キャッシュされた `env` ブロック内の他のすべてのキー（テレメトリと OpenTelemetry 構成など）は、以前と同様に起動時に適用されます。フェッチが成功すると、保留中の変数はセッションの残りの期間に適用されます。

組織が `api.anthropic.com` に到達するためにプロキシが必要な場合、管理 `env` ブロックのみではなく、シェル環境または[ユーザー設定](/docs/ja/settings#settings-files)で設定してください。初回起動にはキャッシュがないため、これらのソースは既に初期フェッチに必要でした。

Claude Code は設定更新を自動的に適用します。ただし、OpenTelemetry 構成などの高度な設定は、有効にするために完全な再起動が必要です。

<h3 id="invalid-entries-in-delivered-settings">
  配信された設定の無効なエントリ
</h3>

配信されたペイロードは、他の管理ソースと同じルールで寛容にパースされます。ペイロードにスキーマ検証に失敗するエントリが含まれている場合、Claude Code はそのエントリを削除し、検証エラーを表示し、残りのすべての有効な設定を適用します。セキュリティ強制フィールドの処理方法を含むフィールドレベルの動作については、[管理設定の無効なエントリ](/docs/ja/settings#invalid-entries-in-managed-settings)を参照してください。Claude Code v2.1.169 以降が必要です。

サーバー管理配信は、これらの動作を追加します。

* `~/.claude/remote-settings.json` のキャッシュは、無効なエントリが削除された救済されたペイロードを保存します。生の無効なペイロードは永続化されません。
* ペイロード内のフィールドが救済できない場合、Claude Code は最後に受け入れられたキャッシュされた設定を保持し、致命的なエラーを記録します。
* [セキュリティ承認ダイアログ](#security-approval-dialogs)は救済されたペイロードを評価するため、削除された無効なエントリは承認のために提示されず、実行されません。

配信の問題をデバッグするには、`claude --debug-file <path>` を実行し、ログで `Remote settings` を検索してください。組織にロールアウトする前に、テストマシンで `claude doctor` を使用してペイロード変更を検証してください。

<h3 id="enforce-fail-closed-startup">
  強制的にクローズされた起動を適用する
</h3>

デフォルトでは、起動時にリモート設定フェッチが失敗した場合、CLI は管理設定なしで続行します。この短い未適用ウィンドウが許容できない環境では、管理設定で `forceRemoteSettingsRefresh: true` を設定します。

この設定がアクティブな場合、CLI は起動時にリモート設定が新しくフェッチされるまでブロックされます。フェッチが失敗した場合、CLI はポリシーなしで続行するのではなく、終了します。この設定は自己永続化します。サーバーから配信されると、ローカルにもキャッシュされるため、新しいセッションの最初の成功したフェッチの前でも、後続の起動は同じ動作を適用します。

これを有効にするには、管理設定構成にキーを追加します。

```json theme={null}
{
  "forceRemoteSettingsRefresh": true
}
```

[エンドポイント管理](/docs/ja/settings#settings-files)MDM プロファイルまたはシステム `managed-settings.json` ファイルでこのキーを設定して、最初の起動時にクローズされた失敗動作を適用することもできます。サーバーペイロードが配信される前です。v2.1.191 以降、このフラグは上記の[優先順位ルール](#settings-precedence)の例外です。キャッシュされたサーバー管理ペイロードも存在する場合でも、任意の管理ソースで設定されている場合は尊重されるため、MDM 配信値はサーバー管理設定が存在する場合は無視されません。設定フェッチは `Cache-Control: no-cache` ヘッダーも送信するため、中間 HTTP プロキシは古い応答を提供しません。

この設定を有効にする前に、ネットワークポリシーが `api.anthropic.com` への接続を許可していることを確認してください。そのエンドポイントに到達できない場合、CLI は起動時に終了し、ユーザーは Claude Code を開始できません。

v2.1.139 以降、`claude auth` サブコマンド（`claude auth login` など）はこのチェックから除外されるため、期限切れの認証情報が設定フェッチが失敗する理由である場合、ユーザーは再認証できます。

<h3 id="security-approval-dialogs">
  セキュリティ承認ダイアログ
</h3>

セキュリティリスクをもたらす可能性のある特定の設定には、適用される前に明示的なユーザー承認が必要です。

* **シェルコマンド設定**：シェルコマンドを実行する設定
* **カスタム環境変数**：既知の安全なホワイトリストにない変数
* **フック構成**：任意のフック定義
* **管理 CLAUDE.md コンテンツ**：管理設定を通じて配信される `claudeMd` 値

これらの設定が存在する場合、ユーザーは構成されている内容を説明するセキュリティダイアログを表示します。ユーザーは続行するために承認する必要があります。ユーザーが設定を拒否した場合、Claude Code は終了します。

<Note>
  `claude -p` または Agent SDK セッションなどの非対話実行では、ダイアログを表示できません。配信された設定が承認を必要とする場合、Claude Code はその実行のためだけにそれらを適用します。[ローカルキャッシュ](#fetch-and-caching-behavior)に承認済みとして記録したり、書き込んだりしません。次の対話セッションではダイアログが表示されます。ユーザーが対話セッションで承認するまで、各非対話実行は起動時に設定を再度フェッチします。v2.1.207 より前は、非対話実行は設定を承認済みとして保存したため、後続の対話セッションはそれらのダイアログを表示しませんでした。
</Note>

<h2 id="platform-availability">
  プラットフォームの可用性
</h2>

サーバー管理設定は `api.anthropic.com` への直接接続が必要であり、配信にはセッションが組織 OAuth ログインまたは直接設定された API キーで認証される必要があります。[`apiKeyHelper`](/docs/ja/settings#available-settings) スクリプトによって返されたキーは設定フェッチをトリガーしません。

サーバー管理設定は、サードパーティのモデルプロバイダーを使用する場合は利用できません。

* Amazon Bedrock
* Google Cloud の Agent Platform
* Microsoft Foundry
* [Claude Platform on AWS](/docs/ja/claude-platform-on-aws)
* `ANTHROPIC_BASE_URL` または [LLM ゲートウェイ](/docs/ja/llm-gateway)を通じたカスタム API エンドポイント

シェルで `CLAUDE_CODE_USE_*` プロバイダー変数または デフォルト以外の `ANTHROPIC_BASE_URL` をエクスポートする場合、Claude Code はセッションの設定フェッチをスキップします。エクスポートがフェッチを防ぐため、サーバー管理 `env` ブロックでエクスポートをクリアすることはできません。[エンドポイント管理設定](/docs/ja/settings#settings-files) `env` ブロックもフェッチを復元しません。Claude Code は管理 `env` ブロックを適用する前に適格性をチェックするため、オーバーライドはセッションのプロバイダー選択を変更しますが、フェッチはスキップされたままです。

サーバー管理配信を復元するには、シェルからエクスポートを削除するか、ユーザー設定 `env` ブロックで変数を `""` に設定します。これは適格性チェックの前に適用されます。ユーザーがシェルを変更することに依存せずにポリシーを適用するには、代わりにエンドポイント管理チャネルを通じて設定を配信してください。

Amazon Bedrock、Google Cloud の Agent Platform、および Microsoft Foundry デプロイメントの場合、自己ホスト型の [Claude apps ゲートウェイ](/docs/ja/claude-apps-gateway)は同等のリモート管理設定配信を提供します。ゲートウェイにサインインしたクライアントは、`api.anthropic.com` の代わりにゲートウェイから管理設定をフェッチします。起動時の失敗セマンティクスは異なります。ゲートウェイに到達できないゲートウェイクライアントはキャッシュされた設定にフォールバックする代わりにエラーで終了しますが、時間ごとのバックグラウンド更新は両方のチャネルで fail-open です。

<h2 id="audit-logging">
  監査ログ
</h2>

設定変更の監査ログイベントは、コンプライアンス API または監査ログエクスポートを通じて利用可能です。アクセスについては、Anthropic アカウントチームにお問い合わせください。

監査イベントには、実行されたアクションのタイプ、アクションを実行したアカウントとデバイス、および前の値と新しい値への参照が含まれます。

<h2 id="security-considerations">
  セキュリティに関する考慮事項
</h2>

サーバー管理設定は一元的なポリシー適用を提供しますが、クライアント側の制御として機能し、セキュリティ境界ではありません。管理されていないデバイスでは、ユーザーは管理者または sudo アクセス権を持つ必要なく、これらをバイパスできます。

| シナリオ                                                 | 動作                                                                                                                                                                                                                                                                                                                      |
| :--------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ユーザーがキャッシュされた設定ファイルを編集する                             | 改ざんされたファイルは起動時に適用されますが、次のサーバーフェッチで正しい設定が復元されます。v2.1.198 以降、`env` ブロック内のトランスポート、API ルーティング、および認証環境変数は、[サーバーがペイロードを確認するまで保留されます](#fetch-and-caching-behavior)                                                                                                                                                             |
| ユーザーがキャッシュされた設定ファイルを削除する                             | 初回起動動作が発生します。設定は非同期でフェッチされ、短い未適用ウィンドウがあります                                                                                                                                                                                                                                                                              |
| ユーザーが変更された Claude Code バイナリを実行する                     | 変更されたクライアントを実行できるユーザーは、クライアント側の制御をバイパスできます                                                                                                                                                                                                                                                                              |
| ユーザーが古い Claude Code バージョンを実行する                       | サーバー管理設定より前のバージョンは、これらをフェッチまたは適用しません                                                                                                                                                                                                                                                                                    |
| API が利用不可                                            | キャッシュされた設定が利用可能な場合は適用されます。そうでない場合、管理設定は次の成功したフェッチまで適用されません。v2.1.198 以降、キャッシュされた `env` ブロック内のトランスポート、API ルーティング、および認証環境変数は、[フェッチ失敗時に保留されます](#fetch-and-caching-behavior)。キャッシュの残りの部分は引き続き適用されます。`forceRemoteSettingsRefresh: true` の場合、CLI は続行するのではなく終了します。ただし、[`claude auth` サブコマンド](#enforce-fail-closed-startup)を除きます |
| ユーザーが別の組織で認証する                                       | 管理対象組織外のアカウントには設定が配信されません                                                                                                                                                                                                                                                                                               |
| ユーザーが[サードパーティモデルプロバイダー](#platform-availability)を構成する | サーバー管理設定はバイパスされます。これには `CLAUDE_CODE_USE_BEDROCK`、`CLAUDE_CODE_USE_MANTLE`、`CLAUDE_CODE_USE_VERTEX`、`CLAUDE_CODE_USE_FOUNDRY`、`CLAUDE_CODE_USE_ANTHROPIC_AWS`、またはデフォルト以外の `ANTHROPIC_BASE_URL` の設定が含まれます                                                                                                                 |
| ネットワークトラフィックが傍受またはリダイレクトされる                          | TLS 検証が無効化されたか、傍受されたトラフィックは、クライアントが受け取る設定を変更できます                                                                                                                                                                                                                                                                        |

ランタイム構成の変更を検出するには、[`ConfigChange` フック](/docs/ja/hooks#configchange)を使用して、変更をログに記録するか、変更が有効になる前に不正な変更をブロックしてください。

ユーザーがクライアントが提供する認証情報でアクセスできる組織を制限するには、Claude ヘルプセンターの[テナント制限を使用したネットワークレベルのアクセス制御の適用](https://support.claude.com/en/articles/13198485-enforce-network-level-access-control-with-tenant-restrictions)を参照してください。より強力な適用保証については、MDM ソリューションに登録されているデバイスで[エンドポイント管理設定](/docs/ja/settings#settings-files)を使用してください。

<h2 id="see-also">
  関連項目
</h2>

Claude Code 構成を管理するための関連ページ：

* [Settings](/docs/ja/settings)：すべての利用可能な設定を含む完全な構成リファレンス
* [Endpoint-managed settings](/docs/ja/settings#settings-files)：IT によってデバイスに配置される管理設定
* [Authentication](/docs/ja/authentication)：Claude Code へのユーザーアクセスのセットアップ
* [Security](/docs/ja/security)：セキュリティ保護とベストプラクティス
