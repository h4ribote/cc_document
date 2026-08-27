> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude apps gateway 設定

> gateway.yaml のすべてのオプションのリファレンス：リスナーと TLS、OIDC、セッション、Postgres ストア、Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、Microsoft Foundry アップストリーム、モデルルーティング、マネージドポリシー、テレメトリー。

Claude apps gateway デプロイメントは、慣例的に `gateway.yaml` という 1 つの YAML ファイルで設定されます。このファイルは、ゲートウェイが行うすべてのことを定義します：どこでリッスンするか、開発者がどのようにサインインするか、推論がどこに行くか、どのポリシーとテレメトリーが適用されるかです。このページは、そのファイル内のすべてのオプションのリファレンスです。最初のファイルを作成するには、[クイックスタート](/docs/ja/claude-apps-gateway#quickstart)から始めてください。これは最小限の動作設定を構築して実行します。設定に満足したら、[デプロイメントガイド](/docs/ja/claude-apps-gateway-deploy)で、Kubernetes、Cloud Run、または独自のプラットフォームでのコンテナ化とホスティングについて説明しています。

ゲートウェイは、`claude gateway --config /path/to/gateway.yaml` でスタートアップ時にファイルを 1 回読み込みます。すべてのオプションはブート時にスキーマに対して検証されるため、形式が正しくない設定は、最初の使用時ではなく、フィールドレベルのエラーで開始時に失敗します。

このページの最後にある[完全な例](#complete-example)は、すべてのセクションを実行します。

<h2 id="file-structure">
  ファイル構造
</h2>

5 つのセクションが[必須](#required-sections)です。他のすべてのセクションは[オプション](#optional-sections)であり、省略されたセクションはデフォルトを使用します。不明なキーはブートに失敗するため、タイプミスは無視された設定ではなく、名前付きエラーとして表示されます。

**必須セクション：**

* [`listen`](#listen)：バインドアドレス、パブリック URL、TLS 終了
* [`oidc`](#oidc)：ID プロバイダー（IdP）、発行者、クライアント、クレームマッピング、サインイン可能なユーザーを含む
* [`session`](#session)：ゲートウェイが発行するベアラートークン、シークレット、有効期間
* [`store`](#store)：デバイスグラント、レート制限カウンターの PostgreSQL
* [`upstreams`](#upstreams)：推論がどこに行くか、Anthropic、Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、または Microsoft Foundry かどうか

**オプションセクション：**

* [`admin`](#admin)：Admin API 認証、支出制限の保持
* [`enforcement`](#enforcement)：支出制限のフェイルオープンまたはフェイルクローズ動作
* [`models`](#models) と `auto_include_builtin_models`：管理者がキュレーションしたモデルリスト、アップストリームごとの ID
* [`managed`](#managed)：IdP グループ別のマネージド設定ポリシー
* [`telemetry`](#telemetry)：OTLP を観測可能性スタックに転送
* [`access_control`、`limits`、`timeouts`、`rate_limits`](#http-tuning)：IP 許可/拒否、リクエストサイズキャップ、アップストリーム初バイト時間、IP ごとのサインイン制限

<h2 id="secret-expansion">
  シークレット展開
</h2>

`client_secret`、`jwt_secret`、`postgres_url` などのシークレットを `gateway.yaml` に直接書き込まないでください。以下のいずれかの形式で参照すると、ゲートウェイはブート時に環境変数またはファイルから値を解決します：

| 形式              | 解決先                      | 用途                                           |
| --------------- | ------------------------ | -------------------------------------------- |
| `${VAR}`        | 環境変数 `VAR`。未定義の場合はブート失敗。 | コンテナ環境変数、env インジェクション経由の AWS Secrets Manager |
| `${file:/path}` | ファイルの内容、トリミング済み          | Kubernetes Secret ボリュームマウント、Vault Agent、SOPS |

<h2 id="required-sections">
  必須セクション
</h2>

<h3 id="listen">
  `listen`
</h3>

`listen` ブロックは、ゲートウェイがサービスを提供する場所を制御します：バインドアドレスとポート、外部から見えるオリジン、オプションの TLS 終了。

| フィールド                  | 必須      | 説明                                                                                                                                                                                                                                                                                                                           |
| ---------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `host`                 | いいえ     | バインドアドレス。デフォルト `0.0.0.0`。                                                                                                                                                                                                                                                                                                    |
| `port`                 | いいえ     | バインドポート。デフォルト `8080`。                                                                                                                                                                                                                                                                                                        |
| `public_url`           | プロキシの背後 | 外部から見える `https://` オリジン。IdP `redirect_uri` と検出メタデータを構築するために使用されます。ALB、Ingress、Cloud Run などの TLS 終了プロキシの背後では必須です。ゲートウェイは独自のオリジンを構築する際に `X-Forwarded-*` ヘッダーを信頼しないためです。これらはクライアントがスプーフ可能です。`trusted_proxies` 以下はクライアント IP 解決のみを管理します。また、[テレメトリ](#telemetry)を有効にするためにも必須です。ゲートウェイはこの URL からクライアントにプッシュする OTLP エンドポイントを構築するためです。 |
| `tls.cert` / `tls.key` | いいえ     | ゲートウェイが TLS 自体を終了する場合の PEM パス                                                                                                                                                                                                                                                                                                |
| `trusted_proxies`      | いいえ     | ゲートウェイの前にあるロードバランサーの CIDR または IP。設定すると、ゲートウェイはこれらのピアからのみ `X-Forwarded-For` を信頼し、IP ごとのレート制限と監査のための実際のクライアント IP を記録します。nginx `set_real_ip_from` と同等。                                                                                                                                                                          |

<h3 id="oidc">
  `oidc`
</h3>

`oidc` ブロックはゲートウェイを ID プロバイダーに接続し、サインイン可能なユーザーを決定します。発行者と OAuth クライアントに名前を付け、メールとグループを含むクレームをマップし、メールドメインまたはグループによるサインインを制限します。

OpenID Connect（OIDC）は、ゲートウェイが ID プロバイダーで使用する SSO プロトコルです。IdP 側で登録する内容については、[ID プロバイダー設定](/docs/ja/claude-apps-gateway-deploy#identity-provider-setup)を参照してください。

| フィールド                           | 必須  | 説明                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `issuer`                        | はい  | OIDC 検出ベース。`/.well-known/openid-configuration` で検出を提供する必要があります。本番環境では HTTPS を使用してください。ゲートウェイは `http://` 発行者を受け入れます。`http://localhost:8081` などのループバック発行者は、`CLAUDE_GATEWAY_ALLOW_LOOPBACK=1` がゲートウェイの環境に設定されていない限り、[SSRF ガード](/docs/ja/claude-apps-gateway-deploy#threat-model-summary)によって拒否されます。                                                                                                                                          |
| `client_id` / `client_secret`   | はい  | OAuth クライアント登録から                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `allowed_email_domains`         | いいえ | `email` クレームがこれらのドメインのいずれかにない id\_token を拒否します。大文字小文字を区別しません。マルチテナント IdP の設定ミスに対する多層防御。この設定とは無関係に、`email_verified` クレームが明示的に `false` である id\_token は常に拒否されます。                                                                                                                                                                                                                                                                        |
| `allowed_groups`                | いいえ | サインインを `groups_claim` に対してマッチしたこれらの IdP グループのメンバーに制限します。許可されたメールドメイン内にあるが、これらのグループのいずれにも属していないユーザーは拒否されます。IdP がグループクレームを発行する必要があります。                                                                                                                                                                                                                                                                                                 |
| `groups_claim`                  | いいえ | グループメンバーシップを含む id\_token クレーム。デフォルト `groups`。Microsoft Entra はアプリロールを `roles` の下に発行します。フラットキーまたは `/resource_access/gateway/roles` などのネストされたクレーム用の RFC 6901 JSON ポインタを受け入れます。                                                                                                                                                                                                                                                         |
| `google_groups`                 | いいえ | Google Workspace Admin SDK Directory API を通じてサインインしたユーザーのグループを検索します。Google の id\_token はグループクレームを含まないためです。`service_account_json_path` を `https://www.googleapis.com/auth/admin.directory.group.readonly` スコープでドメイン全体の委任を持つサービスアカウントキーファイルに設定し、`admin_email` をサービスアカウントが偽装する Workspace 管理者に設定します。Directory API は実際の管理者サブジェクトが必要です。各ユーザーのグループメールアドレスがグループクレームになるため、`allowed_groups` と `managed.policies.match.groups` はグループメールでマッチします。 |
| `email_claim`                   | いいえ | ユーザーのメールを含む id\_token クレーム。デフォルト `email`。ADFS や Entra B2C などの一部の IdP は、代わりに `upn` または `preferred_username` を発行します。フラットキー、JSON ポインタ、または最初に存在するキーが使用されるフォールバックキーのリストを受け入れます。                                                                                                                                                                                                                                                           |
| `scopes`                        | いいえ | ゲートウェイが要求する OIDC スコープの完全なオーバーライド。デフォルト `[openid, profile, email, offline_access]`。IdP が認識しないスコープを拒否する場合、またはグループまたはメールを発行するカスタムスコープが必要な場合に設定します。`openid` を含める必要があります。`offline_access` を削除するとリフレッシュトークンが無効になるため、開発者は `session.ttl_hours` ごとにブラウザログインを再実行します。Google のリフレッシュトークンフロー などの IdP ごとのスコープレシピについては、[ID プロバイダー設定](/docs/ja/claude-apps-gateway-deploy#identity-provider-setup)を参照してください。                                              |
| `extra_auth_params`             | いいえ | IdP 認可リクエストに逐語的に追加される追加クエリパラメータ。これは、Google リフレッシュトークンの `access_type: offline`、一部の Entra テナントの `domain_hint`、またはステップアップフローの `acr_values` など、IdP 固有の動作のオーバーライドメカニズムです。ゲートウェイが管理するプロトコルパラメータはオーバーライドできません：`state`、`nonce`、`redirect_uri`、PKCE、`scope`、`response_type`、`response_mode`、`client_id`。                                                                                                                                      |
| `userinfo_fallback`             | いいえ | id\_token がメールまたはグループを省略する場合、`/userinfo` から取得します。Keycloak 軽量アクセストークン、Okta org サーバー、ADFS 最小トークンに必要です。id\_token は権威的なままです。userinfo はギャップのみを埋めます。デフォルト `false`。                                                                                                                                                                                                                                                                         |
| `use_pkce`                      | いいえ | 認可リクエストで PKCE（S256）チャレンジを送信します。デフォルト `true`。IdP がこの機密クライアントの PKCE を拒否する場合のみ `false` に設定します。                                                                                                                                                                                                                                                                                                                                          |
| `clock_skew_seconds`            | いいえ | id\_token 時間クレームを検証する際にクロックドリフトを許容します。デフォルト `0`（厳密）。サインイン直後のホスト/IdP クロックスキューによる「トークン期限切れ/まだ有効でない」エラーが表示される場合は、増やします。                                                                                                                                                                                                                                                                                                                 |
| `token_endpoint_auth_method`    | いいえ | トークンエンドポイント認証方法をオーバーライドします。`client_secret_basic` または `client_secret_post` を受け入れます。デフォルトで自動ネゴシエーション。                                                                                                                                                                                                                                                                                                                                  |
| `id_token_signed_response_alg`  | いいえ | 予想される id\_token 署名アルゴリズム。デフォルト `RS256`。ES256、PS256、または EdDSA で署名する IdP に設定します。                                                                                                                                                                                                                                                                                                                                                       |
| `additional_authorized_parties` | いいえ | `client_id` を超えて受け入れる追加の `azp` 値。Keycloak ブローカーとトークン交換フロー用。                                                                                                                                                                                                                                                                                                                                                                          |
| `discovery_url`                 | いいえ | `issuer` から派生させるのではなく、この URL から検出ドキュメントを取得します。プロキシの背後にある IdP の場合、発行者ホストを書き直します。パスは `/.well-known/` を含む必要があります。                                                                                                                                                                                                                                                                                                                       |
| `form_action_origins`           | いいえ | `/device` ページの `Content-Security-Policy: form-action` ディレクティブの追加オリジン。ゲートウェイはすでに `'self'` と検出された `authorization_endpoint` オリジンを許可していますが、Chrome は全リダイレクトチェーンに対して `form-action` を強制します。IdP が Azure AD から ADFS へのフェデレーション、ハブスポーク Okta、または企業 SSO インターセプターなど、2 番目のホストを通じてリダイレクトする場合、認可リクエストがリダイレクトする可能性のあるすべてのオリジンをリストします。                                                                                                                 |
| `ca_cert_pem`                   | いいえ | IdP リクエストのみのシステムトラストストアを置き換える PEM CA 証明書。企業 PKI の背後にある Keycloak または Dex に使用します。                                                                                                                                                                                                                                                                                                                                                      |

<h3 id="session">
  `session`
</h3>

`session` ブロックは、サインイン後にゲートウェイが発行するベアラートークンの形状を決定します：それらに署名するシークレットと、どのくらい長く生きるか。

| フィールド        | 必須  | 説明                                                                                                                                                                                                                                                                |
| ------------ | --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `jwt_secret` | はい  | 少なくとも 32 バイトのエントロピー。例えば `openssl rand -base64 32` から。ゲートウェイの HS256 ベアラートークンに署名します。単一の文字列または回転用の配列を受け入れます：インデックス 0 が署名し、すべてのエントリが検証します。回転するには、新しいシークレットを先頭に追加し、`ttl_hours` 待機してから古いものを削除します。                                                                       |
| `ttl_hours`  | いいえ | ゲートウェイベアラートークンの有効期間。デフォルト `1`。CLI は IdP がリフレッシュトークンを発行する場合、有効期限前に無言でリフレッシュします。有効期間が短いほど、より速くプロビジョニング解除されます。長いほど、IdP ラウンドトリップが少なくなります。IdP が `offline_access` が利用できないため、リフレッシュトークンを発行できない場合、無言リフレッシュはないため、開発者が 1 時間ごとにブラウザログインに戻されるのを避けるために、これを `8` または `12` に上げます。 |

<h3 id="store">
  `store`
</h3>

`store` ブロックは、ゲートウェイを PostgreSQL データベースに指します。このデータベースは、デバイスグラントとレート制限カウンターを保持します。

| フィールド             | 必須  | 説明                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------------- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `postgres_url`    | はい  | `postgres://` または `postgresql://` URL。必須：デバイスグラント集合場所。ブラウザコールバックが書き込み、ポーリング CLI が読み込む場所。レプリカ間の状態が必要です。ゲートウェイはブート時に独自のスキーママイグレーションを実行するため、ロールはターゲットスキーマで `CREATE TABLE` が必要です。セキュリティポリシーがアプリケーションロールからの DDL を禁止する場合、マイグレーションを管理者ロールで実行し、最初と新しいリリースがマイグレーションを出荷するたびに、アプリロールに `SELECT, INSERT, UPDATE, DELETE` をゲートウェイのテーブルで付与します。[アップグレード](/docs/ja/claude-apps-gateway-deploy#upgrades)と [Postgres](/docs/ja/claude-apps-gateway-deploy#postgres) を参照してください。 |
| `username`        | いいえ | `postgres_url` のユーザーをオーバーライド                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `password`        | いいえ | データベース認証情報。`postgres_url` ではなくここに設定して、認証情報を URL から外します。任意の文字を受け入れ、URL 認証情報よりも優先されます。                                                                                                                                                                                                                                                                                                                                                              |
| `max_connections` | いいえ | レプリカごとの Postgres 接続プール サイズ。デフォルト `5`。共有データベースに対して保守的でフレンドリーです。[支出制限](#admin)が有効な場合、ホットパスは推論リクエストごとに数回の操作を実行するため、専用データベースの負荷の下で増やし、レプリカ × これをデータベースの `max_connections` 以下に保ちます。                                                                                                                                                                                                                                                                    |

ローカル開発の場合、`postgres_url` を使い捨て Postgres コンテナに指します。例えば `docker run --rm -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres`。

<h3 id="upstreams">
  `upstreams`
</h3>

`upstreams` は順序付きリストです。ゲートウェイは、要求されたモデルを解決する最初のアップストリームに推論を転送します。`5xx`、`429`、`401`、`403`、`404`、またはタイムアウト時に次にフェイルオーバーします。他の `4xx` はしません。これらのエラーはリクエストではなくアップストリームに起因するためです。`401` または `403` はゲートウェイ自身の認証情報がそのアップストリームに対して失敗したことを意味し、`404` はそのアップストリームが要求されたモデルを提供していないことを意味するため、リスト内の後のアップストリームはまだ提供できます。

`404` でのフェイルオーバーにはゲートウェイ v2.1.198 以降が必要です。以前のリリースは、リスト内の後のアップストリームがモデルを提供している場合でも、最初の `404` をクライアントに返しました。

同じプロバイダーの複数のアップストリームは、異なる `name:` を設定する必要があります。

Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、Microsoft Foundry クライアントはスタートアップ時に 1 回構築され、SDK は内部的に認証情報をリフレッシュするため、クラウド認証情報のローテーションは再起動を必要としません。静的 Anthropic API キーとベアラーはスタートアップ時に読み込まれます。[Anthropic API](#anthropic-api)を参照してください。

<h4 id="anthropic-api">
  Anthropic API
</h4>

最小限の Anthropic アップストリームは、[Claude Console](https://platform.claude.com) からの API キーです：

```yaml theme={null}
upstreams:
  - provider: anthropic
    auth:
      api_key: ${ANTHROPIC_API_KEY}
    # または OAuth ベアラー（例：Workload-Identity-Federation 交換トークン）：
    #   oauth_token: ${file:/var/run/secrets/anthropic-oauth-token}
    # base_url: https://api.anthropic.com   # デフォルト；フォワードプロキシの場合はオーバーライド
```

2 つの認証情報形式は、送信するヘッダーが異なります：

* **`api_key`**：`x-api-key` を送信します。Claude Console でローテーションし、env var を更新します。
* **`oauth_token`**：`Authorization: Bearer` を送信します。組織が長期 API キーではなく短期トークンを発行する場合、ベアラー形式を使用します。ベアラーはスタートアップ時に 1 回読み込まれるため、シークレットを再マウントして再起動することで更新します。

静的キーまたはベアラーの代わりに、Workload Identity Federation を使用できます。[Workload Identity Federation ガイド](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)に従って、フェデレーションルールを作成し、ワークロードの OIDC JWT をファイルとしてマウントします。例えば、Kubernetes プロジェクトサービスアカウントトークンまたは CI プラットフォームの id-token。ゲートウェイは JWT を短期ベアラーと交換し、自動的にリフレッシュします。トークンファイルはすべての交換で再読み込みされるため、ローテーションされたプロジェクトトークンは再起動なしで取得されます。

```yaml theme={null}
upstreams:
  - provider: anthropic
    auth:
      federation_rule_id: ${ANTHROPIC_FEDERATION_RULE_ID}
      organization_id: ${ANTHROPIC_ORGANIZATION_ID}
      identity_token_file: /var/run/secrets/anthropic/id-token
      # workspace_id: wrkspc_...       # ルールが 1 つ以上のワークスペースをカバーする場合は必須
      # service_account_id: svac_...   # オプションの予想ターゲットチェック
```

<h4 id="amazon-bedrock">
  Amazon Bedrock
</h4>

ゲートウェイが置き換えるまたはフロントする、クライアント側の Amazon Bedrock デプロイメントについては、[Amazon Bedrock の Claude Code](/docs/ja/amazon-bedrock)を参照してください。ゲートウェイ側のアップストリーム：

```yaml theme={null}
upstreams:
  - provider: bedrock
    region: us-east-1
    auth: {}                           # 推奨：AWS デフォルト認証情報チェーン
    # または明示的な認証情報：
    # auth:
    #   aws_access_key_id: ${AWS_AKID}
    #   aws_secret_access_key: ${AWS_SK}
    #   aws_session_token: ${AWS_ST}
    # または Bedrock API ベアラートークン：
    # auth:
    #   aws_bearer_token: ${AWS_BEARER_TOKEN}
    # FIPS または VPC エンドポイントデプロイメント用に bedrock-runtime エンドポイントをオーバーライド：
    # base_url: https://bedrock-runtime-fips.us-east-1.amazonaws.com
```

空の `auth` ブロックは AWS SDK のデフォルト認証情報チェーンを使用します：env vars、`~/.aws/credentials`、ECS タスクロール、EC2 インスタンスメタデータ、または EKS の IRSA。本番環境では、コンテナイメージに静的キーを埋め込むのではなく、ゲートウェイポッドに IAM ロールを付与します。

明示的な認証情報は完全である必要があります：`aws_access_key_id` と `aws_secret_access_key` が一緒に設定されていない場合、または `aws_session_token` が設定されていない場合、ゲートウェイはブート時に失敗します。v2.1.207 より前では、部分的な `auth:` ブロックは検証に合格しました。

| セットアップ    | 方法                                                                                                                                                                                                                                                                |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IAM 権限    | ゲートウェイのプリンシパルに `bedrock:InvokeModel` と `bedrock:InvokeModelWithResponseStream` を推論プロファイル ARN と基盤モデル ARN の両方に付与します。US リージョンの組み込みカタログの場合：`arn:aws:bedrock:<region>:<account>:inference-profile/us.anthropic.*` と `arn:aws:bedrock:*::foundation-model/anthropic.*`。 |
| モデルアクセス   | Bedrock コンソールで、リージョンごとに、必要な Claude モデルのモデルアクセスをリクエストして有効にします。クロスリージョン推論プロファイル（`us.anthropic.*`）は、プロファイルがスパンする各リージョンでモデルアクセスが必要です。                                                                                                                                 |
| EKS（IRSA） | 上記のポリシーと、クラスターの OIDC プロバイダーのトラストポリシーを持つ IAM ロールを作成します。ゲートウェイのサービスアカウントにスコープされます。サービスアカウントに `eks.amazonaws.com/role-arn: arn:aws:iam::<acct>:role/claude-gateway` でアノテーションを付けます。`auth: {}` がそれを取得します。                                                              |
| ECS / EC2 | IAM ロールをタスク定義またはインスタンスプロファイルにアタッチします。`auth: {}` がそれを取得します。                                                                                                                                                                                                        |
| その他の場所    | `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN` env vars を通じて認証情報を渡すか、`auth:` で `${VAR}` 展開を使用して明示的に設定します。                                                                                                                                        |
| リージョン     | `region:` は API エンドポイントリージョンです。クロスリージョン推論プロファイルは、どれを選択するかに関わらず、地域（US、EU、APAC）全体でルーティングします。US 以外のリージョンまたはプロビジョニングスループット ARN の場合、正しいアップストリームごとの ID を持つ [`models:`](#models) ブロックを追加します。                                                                             |

<h4 id="claude-platform-on-aws">
  Claude Platform on AWS
</h4>

Claude Platform on AWS は、`aws-external-anthropic.<region>.api.aws` で AWS インフラストラクチャ上の第一者 Anthropic API を提供します。第一者モデル ID を使用し、送信された `anthropic-beta` ヘッダーを尊重し、`count_tokens` を提供するため、Bedrock 固有の変換は適用されません。`anthropicAws` プロバイダーには Claude Code v2.1.198 以降が必要です。以前のゲートウェイリリースはブート時にそれを拒否します。

同じプラットフォームのクライアント側デプロイメントについては、[Claude Platform on AWS の Claude Code](/docs/ja/claude-platform-on-aws) を参照してください。ゲートウェイ側のアップストリーム：

```yaml theme={null}
upstreams:
  - provider: anthropicAws
    region: us-east-1
    workspace_id: wrkspc_...
    auth:
      api_key: ${ANTHROPIC_AWS_API_KEY}   # x-api-key として送信
    # または AWS デフォルト認証情報チェーン経由の SigV4：
    # auth: {}
    # または明示的な SigV4 認証情報：
    # auth:
    #   aws_access_key_id: ${AWS_ACCESS_KEY_ID}
    #   aws_secret_access_key: ${AWS_SECRET_ACCESS_KEY}
    # 派生エンドポイントをオーバーライド：
    # base_url: https://aws-external-anthropic.us-east-1.api.aws
```

プラットフォームは Amazon Bedrock とは別の AWS アカウントで実行され、独自のサービス名 `aws-external-anthropic` の SigV4 リクエストに署名するため、Bedrock スコープの IAM ロールはそれを認可しません。`auth.api_key` の API キーは、SigV4 認証情報も設定されている場合、優先されます。空の `auth` ブロックは AWS SDK のデフォルト認証情報チェーンを使用します。これは [Amazon Bedrock](#amazon-bedrock) アップストリームが使用するのと同じチェーンです。

| フィールド                                                   | 必須  | 説明                                                                                                 |
| ------------------------------------------------------- | --- | -------------------------------------------------------------------------------------------------- |
| `region`                                                | はい  | AWS リージョン。小文字、数字、ハイフン。ゲートウェイは `https://aws-external-anthropic.<region>.api.aws` としてエンドポイントを派生させます。 |
| `workspace_id`                                          | はい  | すべてのリクエストでヘッダーとして送信されます。プラットフォームはそれを必要とします。                                                        |
| `auth.api_key`                                          | いいえ | プラットフォームの API キー。`x-api-key` として送信されます。ベアラートークンではありません：2 つの認証モードは API キーまたは SigV4 です。              |
| `auth.aws_access_key_id` / `auth.aws_secret_access_key` | いいえ | 明示的な SigV4 認証情報。一方を他方なしで設定するとブート時に失敗します。`auth.aws_session_token` はそれらと一緒に受け入れられます。                 |
| `base_url`                                              | いいえ | 派生エンドポイントをオーバーライド                                                                                  |

プラットフォームは第一者モデル ID を解決するため、組み込みカタログは [`models:`](#models) ブロックなしでそれにルーティングします。`models:` リストをキュレートする場合、エントリを `anthropicAws:` でキーイングし、第一者 ID を使用します。

<h4 id="google-cloud-agent-platform">
  Google Cloud Agent Platform
</h4>

同等のクライアント側セットアップについては、[Google Cloud の Claude Code](/docs/ja/google-vertex-ai) を参照してください。ゲートウェイ側のアップストリーム：

```yaml theme={null}
upstreams:
  - provider: vertex
    region: us-east5
    project_id: example-prod
    auth: {}                           # 推奨：Application Default Credentials
    # またはサービスアカウントキーファイル：
    # auth: { service_account_json: /secrets/sa.json }
    # Private Service Connect 用に aiplatform エンドポイントをオーバーライド：
    # base_url: https://us-east5-aiplatform.p.googleapis.com
```

空の `auth` ブロックは Application Default Credentials を使用します：`GOOGLE_APPLICATION_CREDENTIALS`、GCE メタデータ、または GKE Workload Identity。サービスアカウント JSON キーファイルはサポートされていますが、推奨されません。Workload Identity を使用するか、GCE または Cloud Run インスタンスにサービスアカウントをアタッチします。

`region: global` を設定して、地域のエンドポイントの代わりに [Agent Platform のグローバルエンドポイント](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations)を使用します。Google は各リクエストを利用可能なリージョンにルーティングするため、リージョンごとのモデル可用性を追跡する必要はありません。特定のリージョンを設定すると、すべてのリクエストがそれにピンされます。

| セットアップ                 | 方法                                                                                                                                                                         |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IAM 権限                 | ゲートウェイのサービスアカウントに `roles/aiplatform.user` をプロジェクトに付与するか、`aiplatform.endpoints.predict` を持つカスタムロール。Agent Platform API（`aiplatform.googleapis.com`）を有効にします。                  |
| モデルアクセス                | Model Garden で、プロジェクトの Claude モデルを有効にします。特定のリージョンに公開されます。サポートされているリージョンについてはモデルカードを確認してください。                                                                               |
| GKE（Workload Identity） | GCP サービスアカウントをゲートウェイの Kubernetes サービスアカウントにバインドし、KSA に `iam.gke.io/gcp-service-account: claude-gateway@<proj>.iam.gserviceaccount.com` でアノテーションを付けます。`auth: {}` がそれを取得します。 |
| Cloud Run / GCE        | サービスのサービスアカウントを `roles/aiplatform.user` を持つものに設定します。`auth: {}` がそれを取得します。                                                                                                  |
| その他の場所                 | `auth: { service_account_json: /secrets/sa.json }`。JSON キーファイルへのパス。シークレットとしてマウントされます。フィールドはキーの内容ではなくファイルパスを取得するため、`${file:…}` 展開は関係ありません。                                  |

<h4 id="microsoft-foundry">
  Microsoft Foundry
</h4>

クライアント側の Foundry デプロイメントについては、[Microsoft Foundry の Claude Code](/docs/ja/microsoft-foundry)を参照してください。ゲートウェイ側のアップストリーム：

```yaml theme={null}
upstreams:
  - provider: foundry
    resource: example-foundry              # https://example-foundry.services.ai.azure.com
    auth: { use_azure_ad: true }        # 推奨：DefaultAzureCredential / Managed Identity
    # または API キー：
    # auth:
    #   api_key: ${FOUNDRY_API_KEY}
```

`use_azure_ad: true` は `DefaultAzureCredential` を通じて解決します：AKS、ACI、または App Service の Managed Identity、Azure CLI、または環境認証情報。API キーは機能しますが、プロジェクト全体であり、自動的にローテーションされません。Foundry のエンドポイントは `resource:` から派生します。Azure Government などのソブリンクラウドの場合、オプションの `base_url` を設定してオーバーライドします。

| セットアップ              | 方法                                                                                                                                                   |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| RBAC                | ゲートウェイのアイデンティティに `Azure AI User` または `Cognitive Services User` を Foundry リソースに付与                                                                     |
| デプロイメント             | Foundry は正規モデル ID ではなく、管理者が選択したデプロイメント名を使用します。各正規 ID をデプロイメント名にマップする [`models:`](#models)ブロックを追加します。                                                 |
| AKS（ワークロードアイデンティティ） | User-Assigned Managed Identity をクラスターの OIDC 発行者とフェデレーションし、ゲートウェイのサービスアカウントにバインドします。`use_azure_ad: true` は `WorkloadIdentityCredential` を通じてそれを取得します。 |
| ACI / App Service   | リソースでシステム割り当てまたはユーザー割り当てマネージドアイデンティティを有効にします。`use_azure_ad: true` がそれを取得します。                                                                         |
| その他の場所              | `auth: { api_key: "${FOUNDRY_API_KEY}" }`。`{ }` 内の `${…}` をクォートします。                                                                                  |

<h4 id="multiple-upstreams">
  複数のアップストリーム
</h4>

同じプロバイダーは、異なる `name:` で複数回表示できます。これは異なるリージョン、異なる認証情報チェーン経由の異なるアカウント、プロビジョニングスループット対オンデマンド、クロスプロバイダーフェイルオーバーをカバーします。

ゲートウェイはアップストリームを順番に試します。`5xx`、`429`、`401`、`403`、`404`、タイムアウト、および欠落エンドポイント（`501`）はフェイルオーバーします。他の `4xx` はしません。

`429` はアップストリーム容量ごとです。プロビジョニングスループット（PT）枯渇はオンデマンドにフェイルオーバーします。`404` はアップストリームモデル可用性ごとです。モデルを有効にしていないアップストリームは、後のアップストリームがそれを提供するのをブロックしません。要求されたモデルを解決できないアップストリームはネットワークラウンドトリップなしでスキップされます。

この例は、プロビジョニングスループット Amazon Bedrock 割り当てを最初にルーティングし、オンデマンドと 2 番目のアカウントにオーバーフロー、最後に Anthropic API にフォールバックします：

```yaml theme={null}
upstreams:
  # プライマリ：ホームリージョンのプロビジョニングスループット。
  - name: bedrock-pt
    provider: bedrock
    region: us-east-1
    auth: {}
  # オーバーフロー：オンデマンドクロスリージョン。
  - name: bedrock-od
    provider: bedrock
    region: us-west-2
    auth: {}
  # 異なるアカウント：想定ロール認証情報経由の別の Bedrock 割り当て。
  - name: bedrock-acct2
    provider: bedrock
    region: us-east-1
    auth:
      aws_access_key_id: ${ACCT2_AKID}
      aws_secret_access_key: ${ACCT2_SK}
  # 最後の手段：直接 Anthropic API。
  - name: anthropic-fallback
    provider: anthropic
    auth:
      api_key: ${ANTHROPIC_API_KEY}

# アップストリームごとのモデル ID はアップストリームの `name:` でキーイングされます。`name:` のないアップストリームはプロバイダー文字列（例：`bedrock`）にデフォルト設定されます。モデルにリストされていないアップストリームはスキップされます。これは、プロビジョニングスループットにモデルをルーティングしながら、他のすべてがオンデマンドのままである方法です。
models:
  - id: claude-opus-4-8
    label: Claude Opus 4.8
    upstream_model:
      bedrock-pt: arn:aws:bedrock:us-east-1:111111111111:provisioned-model/abcdef
      bedrock-od: us.anthropic.claude-opus-4-8
      bedrock-acct2: us.anthropic.claude-opus-4-8
      anthropic-fallback: claude-opus-4-8
```

| レバー                | 方法                                                                                                                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 異なるリージョン           | リージョンごとに 1 つの Amazon Bedrock アップストリーム。それぞれ独自の `region:` を持ちます。[`auto_include_builtin_models: true`](#models)を使用すると、クロスリージョン推論プロファイルは自動的にルーティングされます。リージョンピンデプロイメントの場合、`models:` ブロックを使用します。 |
| 異なるアカウント           | アカウントごとに 1 つの Amazon Bedrock アップストリーム。それぞれ `auth:` で独自の認証情報を持ちます。デフォルトチェーン（`auth: {}`）はポッドのアイデンティティを使用します。2 番目のアカウントの場合、明示的な認証情報またはベアラートークンを設定します。                                         |
| プロビジョニングスループット     | そのアップストリームの名前の `models:` でプロビジョニングスループット ARN にモデルをマップします。他のアップストリームはオンデマンド ID を保持するため、PT 容量はフェイルオーバー前に枯渇します。                                                                               |
| VPC / FIPS エンドポイント | アップストリームで `base_url:` を VPC エンドポイントまたは FIPS エンドポイント URL に設定します。                                                                                                                            |
| モデルスコープルーティング      | モデルの `upstream_model:` マップからアップストリームを省略し、そのアップストリームはそのモデルでスキップされます。例えば、Opus をプロビジョニングスループットにルーティングし、Sonnet と Haiku をオンデマンドにルーティングします。                                                      |

クラウドプロバイダー間、または直接 Anthropic API へのフェイルオーバーは、リクエストを管理する契約、地域、その他の条件を変更します。

CLI は、どのアップストリームが特定のリクエストを提供するかに関わらず、ゲートウェイに同じ機能ゲーティングを適用するため、フェイルオーバーはアップストリームが拒否するボディフィールドを送信しません。

<h2 id="optional-sections">
  オプションセクション
</h2>

<h3 id="admin">
  `admin`
</h3>

オプション。`/v1/organizations/spend_limits` を有効にします。これは Anthropic のパブリック Admin API をミラーリングし、`/v1/messages` で開発者ごとの支出強制を行います。[支出制限](/docs/ja/claude-apps-gateway-spend-limits)で、キャップがどのように設定および強制されるかを参照してください。このセクションは、機能をオンにしてチューニングする `gateway.yaml` キーをカバーします。

```yaml theme={null}
admin:
  # 管理エンドポイント用の名前付き静的 API キー。x-api-key として送信されます。
  # ID は監査ログに admin-key:<id> として表示されるため、各キーは
  # 属性可能です。回転用の配列：新しいキーを追加し、クライアントをロール、
  # 古いものを削除します。
  write_keys:
    - { id: terraform, key: "${GATEWAY_ADMIN_WRITE_KEY_TF}" }
    - { id: ci,        key: "${GATEWAY_ADMIN_WRITE_KEY_CI}" }
  read_keys:
    - { id: reporting, key: "${GATEWAY_ADMIN_READ_KEY}" }
  # 通常のゲートウェイ JWT（API キーなし）経由で完全な管理者を付与された IdP グループ。
  admin_groups: [platform-finops]
  blocked_message: request an increase at https://go.example.com/claude-limits
```

| フィールド                     | 必須  | 説明                                                                                                                                                                                                         |
| ------------------------- | --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write_keys`              | いいえ | `{id, key}` の配列。これらのいずれかと一致する `x-api-key` は、支出制限をリスト、設定、削除できます。キー値は少なくとも 32 文字である必要があります。`id` は `read_keys` と `write_keys` 全体で一意である必要があります。                                                                |
| `read_keys`               | いいえ | `{id, key}` の配列。読み取り専用：すべての `GET` エンドポイント。キャップのリスト、ID による 1 つの取得、[`/effective`](/docs/ja/claude-apps-gateway-spend-limits#%2Feffective) と [`/audit`](/docs/ja/claude-apps-gateway-spend-limits#%2Faudit) の読み取りを含みます。 |
| `admin_groups`            | いいえ | IdP グループ名。`groups` クレームがこれらのいずれかを含むゲートウェイ JWT は、完全な管理者アクセス、読み取りと書き込みを持ち、`oidc:<sub>` として監査されます。人間の管理者に使用します。マシンに API キーを使用します。                                                                             |
| `blocked_message`         | いいえ | ブロックされた開発者が見る `429 billing_error` に逐語的に追加されます。URL または Slack チャネルなど、完全な指示を書きます。未設定の場合、エラーは `spend limit reached` です。                                                                                        |
| `audit_retention_days`    | いいえ | デフォルト `365`。古い `admin_audit` 行はスイープされます。                                                                                                                                                                   |
| `spend_retention_months`  | いいえ | デフォルト `13`。この期間より古い `spend` カウンター行はスイープされます。デフォルトは、年間比較レポート用に完全な年と現在の部分月を保持します。                                                                                                                            |
| `identity_retention_days` | いいえ | デフォルト `90`。`principal_emails` 行の最後に見た TTL。各開発者のメール、表示名、グループ（PII）を保持します。意図的に支出保持より短いため、プロビジョニング解除されたアイデンティティは、その匿名支出カウンターが残っている間に期限切れになります。                                                                 |
| `group_limit_mode`        | いいえ | `min`（デフォルト）または `max`。開発者が複数のグループにキャップがある場合、`min` は最も制限的なものを強制し、`max` は最も制限的でないものを強制します。強制と `/effective` の両方で使用されます。                                                                                       |

<h3 id="enforcement">
  `enforcement`
</h3>

`enforcement` ブロックは、ストアが利用できない場合の支出制限チェックの動作を制御します。

| フィールド                  | 必須  | 説明                                                                                                                                                                |
| ---------------------- | --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fail_closed_on_error` | いいえ | デフォルト `false`。支出強制は Postgres 停止時にオープンで失敗するため、推論は稼働したままです。`true` に設定してクローズで失敗：上限を超えた開発者はブロックされますが、ストアに到達できない場合は他のすべてもブロックされます。[`admin:`](#admin) ブロックなしでは効果がありません。 |

<h3 id="models">
  `models`
</h3>

`models` ブロックはオプションの管理者がキュレーションしたモデルリストで、`/v1/models` で提供され、アップストリームごとのモデル ID を変換するために使用されます。US 以外の Amazon Bedrock リージョン、Amazon Bedrock プロビジョニングスループット ARN、Microsoft Foundry デプロイメント名に必須です。

```yaml theme={null}
auto_include_builtin_models: true   # false：以下のリストのみを公開
models:
  - id: claude-opus-4-8
    label: Claude Opus 4.8
    # description：オプションのテキスト。クライアントに表示される場合がある
    upstream_model:
      anthropic: claude-opus-4-8
      bedrock: us.anthropic.claude-opus-4-8   # または推論プロファイル ARN
      foundry: your-opus-deployment-name
```

<h3 id="managed">
  `managed`
</h3>

`managed` ブロックは、IdP グループまたはメールドメインでキーイングされた、ロールベースのアクセスポリシーを定義します。ポリシーは順番に評価されます。最初のマッチが選択され、以下で説明する `match: {}` キャッチオール基盤にマージされます。ユーザーごとに `GET /managed/settings` で ETag/304 キャッシング付きで提供されます。

```yaml theme={null}
managed:
  policies:
    # 特定のグループを最初に。
    - match: { groups: [eng-contractors] }
      cli:
        availableModels: [claude-sonnet-4-6]
        permissions: { deny: ["WebFetch", "WebSearch"] }
    # デフォルトキャッチオール最後：認証されたすべてのユーザーにマッチします。
    - match: {}
      cli:
        availableModels: [claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5]
```

`match: {}` キャッチオール。慣例的に最後にリストされます。基盤層として扱われます。他のすべてのポリシーは、設定しないキーについてキャッチオールから継承するため、ロール別エントリは組織デフォルトから異なるものだけをリストする必要があります。マージルールはキータイプに依存します：

* **許可リスト**：`availableModels` と `permissions.allow`。特定のポリシーのリストは基盤のリストを完全に置き換えます。
* **拒否リストとフックアレイ**：`permissions.deny`、`permissions.ask`、`disabledMcpjsonServers`、`deniedMcpServers`、`blockedMarketplaces`、およびすべての `hooks` イベントタイプアレイ。これらは基盤とポリシーの和集合を取得するため、組織全体の拒否または監査フックは、ロール別オーバーライドによって誤ってドロップされることはできません。
* **レコードタイプキー**：`env`、`modelOverrides`、`skillOverrides`。これらは浅くマージするため、ロール別 `env` ブロックは設定するキーをオーバーライドし、基盤から残りを継承します。

`availableModels` は `/v1/messages` でサーバー側でも強制されるため、拒否されたモデルはクライアントが送信するものに関わらず `400` を返します。

| マッチャー                                               | 動作                                                                                             |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `match: {}`                                         | 認証されたすべてのユーザーにマッチします。これで開始し、後で上にグループスコープポリシーを追加します。                                            |
| `match: { groups: [a, b] }`                         | JWT の `groups` クレームがリストされたグループのいずれかを含む場合にマッチします。大文字小文字を区別します：グループは IdP の正確な大文字小文字と一致する必要があります。 |
| `match: { email_domain: example.com }`              | JWT の `email` クレームの最後の `@` の後の部分にマッチします。大文字小文字を区別しません。ポリシーごとに 1 つのドメインを受け入れます。                 |
| `match: { groups: [a], email_domain: example.com }` | 両方の条件がマッチする必要があります。                                                                            |

ポリシーにマッチしない認証されたユーザーは、ゲートウェイのデフォルトを取得します。これは、カタログ内のすべてのモデルと管理設定なしを意味します。最後に `match: {}` キャッチオールを追加して、保証されたデフォルトポリシーが必要な場合。

<Note>
  ゲートウェイは独自のユーザーディレクトリを保持しません。ユーザーの IdP トークンから各リクエストを認可し、トークンの `groups` クレームからグループメンバーシップを読み込み、それに対してポリシーを評価します。列挙するロスターはなく、事前作成するアカウントもありません。したがって、SCIM エンドポイントはありません。SCIM が同期するものがないためです。

  ユーザーとグループのライフサイクル管理を、真実の源である IdP のネイティブ SCIM プロビジョニングまたは専用アイデンティティガバナンスプラットフォームで実行します。メンバーシップとプロビジョニング解除はそこで管理され、トークンを通じてゲートウェイに自動的に流れます。Claude アカウント自体の SCIM プロビジョニングが必要な場合、それは [Claude for Enterprise](/docs/ja/admin-setup) 機能です。

  2 つの伝播クロックが適用されます：

  * **ポリシーコンテンツ**：ポリシーを編集して再デプロイすると、接続されたクライアントの次のマネージド設定ポーリング時に到達します。1 時間以内。
  * **グループメンバーシップ**：ユーザーのグループメンバーシップを変更すると、どのポリシーが彼らにマッチするかが変わります。これは次のセッション再発行時に有効になります。つまり、次の無言リフレッシュ。`session.ttl_hours` で制限されます。
</Note>

<h4 id="what-goes-in-cli">
  `cli` に何が入るか
</h4>

各 `cli` 値は、完全な Claude Code `managed-settings.json` ドキュメントです。MDM または `/etc/claude-code/managed-settings.json` を通じてデプロイするのと同じスキーマ。ここでは YAML として表現されます。CLI は、マネージド層で配信されたドキュメントを適用します。ユーザーとプロジェクト設定の上。

ゲートウェイは、ブート時に CLI の設定スキーマに対して各ドキュメントを検証するため、認識されないトップレベルキーまたは認識されたキーで形式が正しくない値は、すべての違反キーに名前を付けるエラーでブートに失敗します。スキーマの意図的にオープンな部分は、新しいクライアントがゲートウェイのスキーマが認識しないエントリを認識する可能性があるため、任意の値を受け入れます。これらのオープンキーは `env`、`pluginConfigs`、`permissions` の下にネストされたキーです。

検証はゲートウェイのインストール済みバージョンにバンドルされたスキーマを使用するため、新しい Claude Code リリースで導入されたトップレベル設定キーをマネージド設定に入れるには、最初にゲートウェイをアップグレードする必要があります。新しいポリシーを 1 つのクライアントでスモークテストしてから、ロールアウトします。

完全なキーリファレンスは [Claude Code 設定](/docs/ja/settings#available-settings) にあります。オペレーターが最初に到達するキー：

```yaml theme={null}
managed:
  policies:
    - match: {}
      cli:
        # モデルアクセス（/v1/messages でサーバー側でも強制）
        availableModels: [claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5]

        # 権限ポリシー
        permissions:
          deny:
            - "WebFetch"
            - "Read(./.env)"
            - "Read(./secrets/**)"
          disableBypassPermissionsMode: disable   # --dangerously-skip-permissions をブロック
        allowManagedPermissionRulesOnly: true     # ユーザー/プロジェクト権限ルールを無視

        # CLI プロセスにプッシュされた環境。DISABLE_UPDATES はバックグラウンドと手動更新をブロック；DISABLE_AUTOUPDATER はバックグラウンド更新のみを停止。
        env:
          DISABLE_UPDATES: "1"                    # 独自の配布経由でバージョンをピン

        # 組織全体のフック。フックコマンドはゲートウェイではなく開発者マシンで実行されるため、パスはポリシー内のすべてのクライアント OS に存在する必要があります。
        hooks:
          PostToolUse:
            - matcher: "Edit|Write"
              hooks:
                - { type: command, command: /usr/local/bin/audit-edit.sh }
```

| キー                                         | 強制者          | 効果                                                                                                                                                                            |
| ------------------------------------------ | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `availableModels`                          | ゲートウェイ + CLI | モデル許可リスト。`/v1/messages` でもチェックされるため、パッチされたクライアントはバイパスできません。                                                                                                                   |
| `permissions.allow` / `.deny`              | CLI          | ツールとコマンドルール。[権限](/docs/ja/permissions)を参照してください。                                                                                                                                   |
| `permissions.disableBypassPermissionsMode` | CLI          | `disable` に設定して [`bypassPermissions`](/docs/ja/permission-modes#skip-all-checks-with-bypasspermissions-mode) をブロック。すべてのツール呼び出しを自動承認するモード、および `--dangerously-skip-permissions` フラグ。 |
| `allowManagedPermissionRulesOnly`          | CLI          | `true` の場合、ユーザーとプロジェクト権限ルールは無視されます。このドキュメントのルールのみが適用されます。                                                                                                                     |
| `env`                                      | CLI          | CLI プロセスにマージされた環境変数。テレメトリ、自動更新、モデル名オーバーライドに使用します。                                                                                                                             |
| `hooks`                                    | CLI          | 組織全体の [フック](/docs/ja/hooks)。                                                                                                                                                       |

これらの設定はネットワーク経由で到着するため、CLI は、シェルコマンドを実行したり、トラフィックがどこに行くかを変更したりできるものを適用する前に、各開発者に 1 回限りのセキュリティ承認ダイアログを表示します。ダイアログは以下をカバーします：

* `hooks`
* `env` 変数。CLI の組み込みセーフリストにない
* `apiKeyHelper` と `statusLine` などのシェル実行設定
* マネージド CLAUDE.md コンテンツ

セーフリストは、どの `env` 変数が承認なしで適用されるかを決定します：

* **セーフリスト上**：自動更新とモデル名変数
* **セーフリストにない**：プロキシ変数、ベース URL 変数、`OTEL_EXPORTER_OTLP_ENDPOINT`

ゲートウェイの [テレメトリ](#telemetry) 設定は `OTEL_EXPORTER_OTLP_ENDPOINT` をプッシュするため、`telemetry.forward_to` を設定すると、各インタラクティブクライアントで承認ダイアログがトリガーされます。ダイアログは、組織から開発者を保護するのではなく、開発者のマシンを侵害または敵対的なゲートウェイから保護します。

`-p` フラグを使用した非インタラクティブ実行はダイアログを表示できません。その実行のみのためにプッシュされた設定を適用し、それらを承認済みとして記録しないため、開発者の次のインタラクティブセッションはまだダイアログを表示します。v2.1.207 より前では、非インタラクティブ実行は設定を承認済みとして保存し、後のインタラクティブセッションはそれらのダイアログを表示しませんでした。

開発者が拒否した場合、Claude Code は設定を適用せずに終了します。新しいフックまたは非セーフ env var を広いポリシーにプッシュすることは、マッチする開発者の次の起動時に承認プロンプトを意味します。

`cli` キーは以前のリリースで `settings` という名前でした。その綴りはまだエイリアスとして受け入れられていますが、新しいデプロイメントは `cli` を使用する必要があります。

<h4 id="precedence-with-other-managed-sources">
  他のマネージドソースとの優先順位
</h4>

デバイスにローカル `managed-settings.json` または MDM 配信ポリシーもある場合、マネージドソースはマージされません。最優先ソースはすべてのポリシー設定を提供します。この順序でランク付けされます。最優先順位が最初：

1. [ポリシーヘルパー](/docs/ja/settings#compute-managed-settings-with-a-policy-helper)
2. ゲートウェイ配信設定
3. MDM。Windows の HKLM レジストリまたは macOS の plist 経由
4. `managed-settings.json` ファイル
5. HKCU レジストリ。Windows のみ

埋め込みホストは SDK `managedSettings` オプションを通じてポリシーを提供できます。デフォルトでは無視され、マネージドソースが [`parentSettingsBehavior: "merge"`](/docs/ja/settings#available-settings) でオプトインした場合のみ適用されます。ポリシーを厳しくできますが、緩くすることはできません。

例外は、管理者ソースが設定する場合に尊重される小さなキーセットです。ユーザー書き込み可能な HKCU 層は除外されます：

* `sandbox.network.allowManagedDomainsOnly` と `sandbox.filesystem.allowManagedReadPathsOnly`：ロックされている場合、対応する許可リストはソース全体で和集合されます。
* [`allowAllClaudeAiMcps`](/docs/ja/settings#available-settings)：claude.ai MCP サーバー許可リストの許可のみオーバーライド
* `sandbox.bwrapPath` と `sandbox.socatPath`：[サンドボックス](/docs/ja/sandboxing)ヘルパーバイナリへのファイルシステムパス
* [`forceRemoteSettingsRefresh`](/docs/ja/server-managed-settings)：スタートアップをブロックして、リモートマネージド設定を新しく取得するため、キーが不足しているキャッシュされたリモートペイロードが最優先ソースである場合でも、MDM またはファイルポリシーがそれを設定することが尊重されます。

`allowManagedPermissionRulesOnly` と `disableBypassPermissionsMode` を含むすべての他のキーは、最優先ソースのみから来ます。[設定の優先順位](/docs/ja/settings#settings-precedence)で、設定ページの同じルールを参照してください。

ゲートウェイポリシーはマシン上のすべての Claude Code 呼び出しに適用されます。非インタラクティブ `claude -p` 実行と Agent SDK によって生成されたセッションを含みます。ゲートウェイがスタートアップ時に到達不可能な場合、署名されたセッションはポリシーなしで実行するのではなく、エラーで終了します。

<Warning>
  ポリシーの `cli` ブロック内の `mcpServers` はゲートウェイブートで拒否されます。グループごとの MCP 配布は利用できません。各デバイスでファイルベースの `managed-mcp.json` を通じて MCP サーバーをデプロイするか、開発者がローカルで追加できるようにします。
</Warning>

<h3 id="telemetry">
  `telemetry`
</h3>

CLI は OpenTelemetry Protocol（OTLP）を HTTP メトリクス、ログ、有効な場合はトレースでゲートウェイに送信します。ゲートウェイはそれらを逐語的に各設定先にリレーします。[使用状況の監視](/docs/ja/monitoring-usage)で、CLI が発行するメトリクスとイベントを参照してください。

CLI は、ゲートウェイ発行 JWT から読み込まれた認証されたユーザーのアイデンティティで各エクスポートにスタンプを付けます：`user.id`、`user.email`、`user.groups` 属性。開発者ごとのコストと使用状況の属性は、開発者側の設定なしで機能します。

```yaml theme={null}
telemetry:
  forward_to:
    - url: https://otel-collector.internal.example.com
      headers:
        Authorization: ${OTLP_TOKEN}
      # シグナルごとのオプトイン。デフォルト：メトリクスのみ。
      metrics: true
      logs: false
      traces: false
    - url: https://api.datadoghq.com/api/v2/otlp
      headers:
        DD-API-KEY: ${DD_API_KEY}
```

<Warning>
  各宛先は `metrics`、`logs`、`traces` に独立してオプトインし、デフォルトはメトリクスのみです。シグナルは感度が異なります：

  * **メトリクス**：トークンカウント、リクエストカウント、レイテンシなどの集計カウンター
  * **ログとトレース**：完全な bash コマンド、ツール入力、ファイルパスを含むことができます。Claude Code が開発者のマシンで行うすべてをカバーします。

  ログとトレースは、アクセス制御と保持ポリシーがデータを保証する宛先でのみ有効にします。
</Warning>

テレメトリは CLI でデフォルトでオフです。`telemetry.forward_to` を `listen.public_url` と一緒に設定するとオンになります。ゲートウェイは 5 つの env var を `/managed/settings` を通じてすべての接続されたクライアントにプッシュします：

* `CLAUDE_CODE_ENABLE_TELEMETRY=1`
* `OTEL_METRICS_EXPORTER=otlp`
* `OTEL_LOGS_EXPORTER=otlp`
* `OTEL_TRACES_EXPORTER=otlp`
* `OTEL_EXPORTER_OTLP_ENDPOINT=<public_url>`

プッシュされたエンドポイントはパブリック URL から構築されるため、メトリクスとログは開発者またはポリシーからの OTEL 設定を必要としません。プッシュされた設定はマネージド層で適用され、開発者がローカルで設定する `OTEL_*` 変数をオーバーライドします。

[トレース](/docs/ja/monitoring-usage#traces-beta)はさらに各クライアントで `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` を必要とします。ゲートウェイはその変数をプッシュしないため、マネージドポリシーの `env` ブロックを通じて設定します。CLI のセーフリストにはないため、ポリシーを通じてそれを配信することは、プッシュされた OTLP エンドポイントがすでにトリガーする同じ [セキュリティ承認ダイアログ](#managed)でカバーされます。

protobuf と JSON OTLP エンコーディングの両方がリレーされ、OpenTelemetry 互換バックエンドは宛先として機能します。

<h3 id="http-tuning">
  HTTP チューニング
</h3>

4 つのオプションのトップレベルブロック、`access_control`、`limits`、`timeouts`、`rate_limits`。HTTP サーフェスをチューニングします。デフォルトはほとんどのデプロイメントに適しています。

| ブロック             | キー                                             | デフォルト    | 説明                                                                                                                                                                                                                                    |
| ---------------- | ---------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access_control` | `allow_cidrs` / `deny_cidrs`                   | 空        | `trusted_proxies` 解決後のクライアントアドレスによるインバウンド IP 許可/拒否。`deny_cidrs` が最初にチェックされます。クライアントがマッチする場合、`allow_cidrs` もマッチしても拒否されます。`allow_cidrs` が空でない場合、ゲートウェイはデフォルト拒否です。`/healthz` と `/readyz` は `allow_cidrs` から除外されます。                       |
| `limits`         | `max_request_bytes`                            | 32 MiB   | 最大インバウンドリクエストボディ。サイズを超えるリクエストはボディがバッファリングされる前に `413` を取得します。大きなファイルまたは画像リクエストの場合は増やします。                                                                                                                                               |
| `limits`         | `max_request_header_bytes`                     | 未設定      | 設定すると、サイズを超えるヘッダーは `431` を返します。                                                                                                                                                                                                       |
| `limits`         | `max_url_length`                               | 未設定      | 設定すると、長すぎる URL は `414` を返します。                                                                                                                                                                                                         |
| `timeouts`       | `upstream_ttfb_ms`                             | 120000   | アップストリームのレスポンスヘッダー（初バイト時間）を待つ最大時間。レスポンスボディはその後、ウォールクロックキャップなしでストリーミングされます。直接 Anthropic アップストリームパスに適用されます。他のすべてのプロバイダーはプロバイダー SDK 独自のタイムアウトで制限されます。                                                                                    |
| `rate_limits`    | `device_authorization.max` / `.window_seconds` | 30 / 600 | 認証されていないデバイス認可エンドポイントの IP ごとのレート制限。共有エグレス IP または NAT の背後にある大規模な組織の場合は増やします。これらの制限は、デバイスグラント サインインフローにのみ適用され、`/v1/messages` 推論には適用されません。[ユーザーコードブルートフォース耐性](/docs/ja/claude-apps-gateway-deploy#user-code-brute-force-resistance)を参照してください。 |
| `rate_limits`    | `device_verify.max` / `.window_seconds`        | 10 / 600 | `/device` での `user_code` 送信の IP ごとのレート制限。                                                                                                                                                                                             |

<h2 id="complete-example">
  完全な例
</h2>

この完全なリファレンス設定はすべてのコアセクションを実行します。[HTTP チューニングブロック](#http-tuning)はデフォルトを保持します。コピーして、不要なものを削除し、値を入力します。[クイックスタート](/docs/ja/claude-apps-gateway#quickstart)の設定はこれの最小バージョンです。

```yaml gateway.yaml theme={null}
# 実行：
#   claude gateway --config gateway.yaml
#
# 運用ログの詳細度は CLAUDE_GATEWAY_LOG_LEVEL
# 環境変数で制御されます（info | warn | error；デフォルト info）。監査イベントには影響しません。常に発行されます。

listen:
  host: 0.0.0.0
  port: 8080
  public_url: https://claude-gateway.internal.example.com
  # TLS 終了 ingress の背後で実行する場合は tls ブロックを省略します。
  # tls:
  #   cert: /certs/gateway.crt
  #   key: /certs/gateway.key
  # trusted_proxies:
  #   - 10.0.0.0/8

oidc:
  issuer: https://example.okta.com
  client_id: 0oa1example2
  client_secret: ${OIDC_CLIENT_SECRET}
  allowed_email_domains:
    - example.com
  # Okta org サーバーが発行者の場合は必須。id_token はメールとグループを省略できます。ゲートウェイは /userinfo から埋めます。
  userinfo_fallback: true
  # allowed_groups: [claude-code-users]
  # Okta はグループスコープがリクエストされ、アプリのグループクレームフィルターが許可する場合のみグループを発行します。以下のコントラクターポリシーはグループでマッチするため、スコープはここでリクエストされます。
  scopes: [openid, profile, email, offline_access, groups]
  # extra_auth_params: { access_type: offline, prompt: consent }  # Google
  # groups_claim: groups          # Entra アプリロール：`roles` を使用
  # email_claim: email

session:
  jwt_secret: ${GATEWAY_JWT_SECRET}   # openssl rand -base64 32
  # ttl_hours: 1

store:
  postgres_url: ${GATEWAY_POSTGRES_URL}
  # max_connections: 5

# /v1/organizations/spend_limits を有効にします（Anthropic Admin API をミラーリング）
# および /v1/messages での開発者ごとの支出強制。無効にするには省略します。
# キャップ自体は admin API 経由で設定されます。ここではありません。
# admin:
#   write_keys:
#     - { id: terraform, key: "${GATEWAY_ADMIN_WRITE_KEY_TF}" }
#   read_keys:
#     - { id: reporting, key: "${GATEWAY_ADMIN_READ_KEY}" }
#   admin_groups: [platform-finops]
#   blocked_message: request an increase at https://go.example.com/claude-limits
#   # audit_retention_days: 365
#   # spend_retention_months: 13
#   # identity_retention_days: 90
#   # group_limit_mode: min

# enforcement:
#   fail_closed_on_error: false

upstreams:
  - provider: anthropic
    auth:
      api_key: ${ANTHROPIC_API_KEY}

  # - provider: bedrock
  #   region: us-east-1
  #   auth: {}

  # - provider: anthropicAws
  #   region: us-east-1
  #   workspace_id: wrkspc_...
  #   auth:
  #     api_key: ${ANTHROPIC_AWS_API_KEY}

  # - provider: vertex
  #   region: us-east5
  #   project_id: example-prod
  #   auth: {}

  # - provider: foundry
  #   resource: example-foundry
  #   auth: { use_azure_ad: true }

auto_include_builtin_models: true
models:
  - id: claude-opus-4-8
    label: Claude Opus 4.8
    upstream_model:
      anthropic: claude-opus-4-8
      # bedrock: us.anthropic.claude-opus-4-8
      # anthropicAws: claude-opus-4-8
      # vertex: claude-opus-4-8
      # foundry: <your-opus-deployment-name>
  - id: claude-sonnet-4-6
    label: Claude Sonnet 4.6
    upstream_model:
      anthropic: claude-sonnet-4-6
  - id: claude-haiku-4-5
    label: Claude Haiku 4.5
    upstream_model:
      anthropic: claude-haiku-4-5

managed:
  policies:
    - match: { groups: [contractors] }
      cli:
        availableModels: [claude-haiku-4-5]
        # Default ピッカーオプションを availableModels に制限します。デフォルトの代わりに、コントラクターが default で 400 を取得しないようにします。
        enforceAvailableModels: true
        # allow はこれらのツールを自動承認します。残りをブロックしません。
        # ツールを制限するには deny ルールを追加します。
        permissions: { allow: [Read, Grep] }
    - match: {}
      cli:
        availableModels: [claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5]
        permissions:
          allow: [Read, Grep, Bash, Edit]
          deny: ["WebFetch"]
        env: { HTTP_PROXY: http://proxy.example.com:8080 }

telemetry:
  forward_to:
    - url: https://otel.internal.example.com:4318
      headers:
        Authorization: Bearer ${OTEL_TOKEN}
```

<h2 id="client-side-managed-settings">
  クライアント側マネージド設定
</h2>

上記のすべてはゲートウェイサーバーを設定します。開発者マシンをそれに指すことは、各デバイスで別々に設定されます。Claude Code の [マネージド設定](/docs/ja/settings#settings-files) を通じて。ゲートウェイはこれらのキーをプッシュできません。ゲートウェイがどこにあるかをクライアントに伝えるものだからです。

CLI の場合、OS ごとの `managed-settings.json` に両方のキーを設定します：

```json theme={null}
{
  "forceLoginMethod": "gateway",
  "forceLoginGatewayUrl": "https://claude-gateway.internal.example.com"
}
```

そのファイルを各デバイスにデプロイします。通常は MDM プラットフォーム経由。ファイルパスはプラットフォームによって異なります：

| プラットフォーム    | パス                                                                                                         |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| macOS       | `/Library/Application Support/ClaudeCode/managed-settings.json`、または `com.anthropic.claudecode` マネージド設定ドメイン |
| Linux と WSL | `/etc/claude-code/managed-settings.json`                                                                   |
| Windows     | `C:\Program Files\ClaudeCode\managed-settings.json`、または HKLM レジストリ経由のグループポリシー                              |

`forceLoginGatewayUrl` と `forceLoginMethod` の `"gateway"` 値は、管理者制御マネージド層からのみ尊重されます。開発者が独自の `~/.claude/settings.json` で設定しても効果がありません。

<h2 id="related">
  関連
</h2>

* [Claude apps gateway 概要](/docs/ja/claude-apps-gateway)：クイックスタートと開発者接続
* [デプロイメントガイド](/docs/ja/claude-apps-gateway-deploy)：IdP セットアップ、コンテナイメージ、Kubernetes と Cloud Run、運用
* [支出制限](/docs/ja/claude-apps-gateway-spend-limits)：開発者ごとのキャップと Admin API
