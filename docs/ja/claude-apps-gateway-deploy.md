> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude apps gateway のデプロイと運用

> IdP にゲートウェイを登録し、コンテナをビルドして Kubernetes または Cloud Run にデプロイし、ヘルスチェック、シークレットローテーション、アップグレード、セキュリティを運用します。

このページでは、[Claude apps gateway](/docs/ja/claude-apps-gateway) の運用側について説明します。ID プロバイダー（IdP）で OAuth クライアントを登録し、ゲートウェイをコンテナとしてデプロイし、日々運用します。ゲートウェイが起動時に読み込む `gateway.yaml` ファイルのすべてのオプションについては、[設定リファレンス](/docs/ja/claude-apps-gateway-config) を参照してください。

本番環境のデプロイメントは順序立てた 4 つのステップに従い、以下のセクションがそれに対応しています。最初の 2 つは選択を行う場所です。後の 2 つは、実行中に参照するリファレンス資料です。

1. [ID プロバイダーをセットアップする](#identity-provider-setup)：OAuth クライアントを登録し、Okta、Entra、Google の IdP 固有の注記を確認します
2. [ゲートウェイをデプロイする](#deployment)：ピン留めされたコンテナイメージをビルドし、Kubernetes、Cloud Run、または独自のプラットフォームで実行します。このセクションではコスト、バイパス、複数ゲートウェイ、サーバーレスの決定についても説明します
3. [運用をセットアップする](#operations)：ログ、ヘルスプローブ、障害時の動作、シークレットローテーション、アップグレード。監視とランブックを配線するときに参照するリファレンス
4. [セキュリティ体制を確認する](#security)：データがどこを流れるか、脅威モデル、コンプライアンスの回答。セキュリティレビュー用のリファレンス

サインインまたはブート中に失敗が発生した場合は、[トラブルシューティング](#troubleshooting) に直接進んでください。これは表示されるエラーに基づいてキー付けされています。

<Note>
  **プライベートネットワークにデプロイします。** Claude Code は、アドレスがプライベートであるゲートウェイにのみ接続します。これはセキュリティガードです。信頼されたゲートウェイは、開発者マシンでコマンドを実行する設定をプッシュできるためです。ゲートウェイを内部ロードバランサーまたは VPN の背後に配置し、プライベート IP にのみ解決するホスト名を付与します。

  Anthropic が運用する公開ゲートウェイエンドポイントは例外です。`/login` は `https://` 経由でそれらを受け入れます。これらは Anthropic 自体が運用する小さな固定セットのゲートウェイです。これらはデプロイオプションとして選択または設定できるデプロイメントオプションではありません。リストは Claude Code にコンパイルされているため、設定でホスト名をリストに追加することはできず、ホストするゲートウェイは免除の対象にはなりません。v2.1.206 より前では、`/login` はそれらのエンドポイントを他のパブリックアドレスと同様に拒否していました。
</Note>

<h2 id="identity-provider-setup">
  ID プロバイダーのセットアップ
</h2>

単一のリダイレクト URI `https://<gateway>/oauth/callback` を持つ機密 OAuth/OpenID Connect（OIDC）ウェブアプリケーションを ID プロバイダーに登録し、ゲートウェイアクセスを持つべきユーザーまたはグループに割り当てます。

任意の OIDC 準拠 IdP が機能します：Okta、Microsoft Entra ID、Google Workspace、Keycloak、Dex、PingFederate など。IdP は 3 つの要件を満たす必要があります：

* `/.well-known/openid-configuration` を提供します。本番環境では HTTPS 経由です。ゲートウェイは [`http://` issuer](/docs/ja/claude-apps-gateway-config#oidc) を受け入れ、ループバック issuer は追加で `CLAUDE_GATEWAY_ALLOW_LOOPBACK=1` が必要です
* 認可コードフローをサポートします。PKCE（Proof Key for Code Exchange）はデフォルトで有効です。サポートしない IdP の場合は `oidc.use_pkce: false` で無効にします
* id\_token で `email` と必要に応じて `groups` を返すか、`oidc.userinfo_fallback: true` で userinfo エンドポイントから提供します

プライベート PKI の場合は、`oidc.ca_cert_pem` を設定します。

いくつかのプロバイダーはメールとグループクレームを異なる方法で処理します：

* **Okta**：`https://example.okta.com` の org 認可サーバーは、`email` と `groups` を省略した薄い id\_token を返すため、issuer として使用する場合は常に `oidc.userinfo_fallback: true` を設定します。`https://example.okta.com/oauth2/default` などのカスタム認可サーバーは、id\_token に `email` と必要に応じて `groups` を含め、直接発行し、フォールバックは不要です。Okta は `oidc.scopes` で `groups` スコープがリクエストされ、アプリのグループクレームフィルターが許可する場合にのみ `groups` を発行します。`userinfo_fallback` は IdP がリクエストされなかったクレームを埋めることはできません。
* **Microsoft Entra ID**：`issuer` = `https://login.microsoftonline.com/<tenant-id>/v2.0`。Entra はグループ名ではなくグループオブジェクト ID を発行するため、`managed.policies.match.groups` で GUID を使用するか、人間が読める名前のためにアプリロールを使用します。テナントが `groups` の代わりに `roles` の下でロールを発行する場合は、`oidc.groups_claim: roles` を設定します。
* **Google Workspace**：`issuer` = `https://accounts.google.com`。Google の id\_token はグループを含みません。Google を IdP として、グループベースの `allowed_groups` または `managed.policies` を使用するには、[`oidc.google_groups`](/docs/ja/claude-apps-gateway-config#oidc) を設定します。これは、ドメイン全体の委任を持つサービスアカウントを使用して Admin SDK Directory API を通じて各ユーザーのグループを検索します。これなしで、メンバーシップゲーティングに `oidc.allowed_email_domains` を使用し、ポリシー割り当てに `managed.policies.match.email_domain` を使用します。Google は標準の `offline_access` スコープも無視します。リフレッシュトークンの場合は、`oidc.scopes: [openid, profile, email]` と `oidc.extra_auth_params: { access_type: offline, prompt: consent }` を設定します。

上記で説明されていない ID プロバイダーのサポートについては、[トラブルシューティング](#troubleshooting) を参照してください。

<Warning>
  リフレッシュトークンにより、ゲートウェイは開発者のセッションをサイレントに更新でき、開発者をブラウザに戻す必要がありません。また、IdP がユーザーを無効にすると、次のリフレッシュが失敗し、セッションは `ttl_hours` 内に終了するため、プロビジョニング解除を駆動します。ゲートウェイはデフォルトでリフレッシュトークンを取得するために `offline_access` をリクエストします。IdP がオフラインアクセスに明示的な同意を必要とする場合は、OAuth クライアントを設定してそれを許可します。

  IdP がリフレッシュトークンをまったく発行できない場合、ゲートウェイは引き続き機能しますが、サイレント更新がないため、開発者はセッションの有効期限が切れるとブラウザログインを再実行します。これが 1 時間ごとに発生するのを防ぐには、[`session.ttl_hours`](/docs/ja/claude-apps-gateway-config#session) を `8` または `12` に上げます。トレードオフはプロビジョニング解除の遅延です。リフレッシュトークンなしでは、無効にされたユーザーはより長い TTL が経過するまでアクセスを保持します。
</Warning>

<h2 id="deployment">
  デプロイ
</h2>

ゲートウェイは単一の Linux バイナリです。レプリカはステートレスで Postgres が共有調整層であるため、水平にスケーリングします。環境内でステートレスサービスを実行する方法で実行します。このセクションの残りは、イメージが必要とするもの、Kubernetes と Cloud Run の短い注記を述べています。

ゲートウェイは、上流の認証情報を保持し、推論の単一の出口ポイントとして機能するため、ネットワーク内で実行するように設計されています。開発者と IdP が HTTPS 経由で到達できる任意の場所で実行でき、本番認証情報を保持する他のサービスと同様に扱います。

デプロイメントを実行する場所を超えて形作るいくつかの決定があります：

* **コスト**：ゲートウェイの個別ライセンスまたはシートごとの料金はありません。これは `claude` バイナリの一部です。既存のクラウドまたは Anthropic コミットメントを通じて推論に対して支払い、コンテナのコンピュートとテレメトリコレクターを支払います。
* **バイパス**：ゲートウェイは、モデルへの唯一のルートがそれを通過することを強制しません。独自の認証情報を持つ開発者は引き続きプロバイダーを直接呼び出すことができるため、そのパスを閉じることはネットワークポリシーの決定です。例えば、`api.anthropic.com` へのエグレスをゲートウェイ以外からブロックします。そのエグレスをブロックすると、各開発者のマシンから `api.anthropic.com` を呼び出す [WebFetch ドメインセーフティチェック](/docs/ja/data-usage#webfetch-domain-safety-check) も破壊されます。管理ポリシーで `skipWebFetchPreflight: true` を設定して無効にします。
* **複数ゲートウェイ**：各ゲートウェイは独自の設定を持つ個別のデプロイメントです。CLI はゲートウェイホスト名ごとに信頼フィンガープリントと認証情報を保存するため、異なるチームは競合なしに異なるゲートウェイに接続できます。複数の OIDC issuer を提供するには、個別のインスタンスを実行します。
* **サーバーレス**：Cloud Run は機能します。`min-instances: 1` を設定して、コールド OIDC ディスカバリーを回避します。Lambda と Cloud Functions は機能しません。ゲートウェイは長時間実行 HTTP サーバーであるためです。

ここのすべての本番トポロジーは、L7 プロキシ（Ingress、Cloud Run のフロントエンド、ALB など）をプレーン HTTP レプリカの前に配置します。[`listen.trusted_proxies`](/docs/ja/claude-apps-gateway-config#listen) をプロキシのソース範囲に設定して、ゲートウェイが `X-Forwarded-For` からクライアント IP を読み込みます。ゲートウェイは TCP ピアが信頼されている場合にのみヘッダーを尊重します。[Google Cloud の実装例](/docs/ja/claude-apps-gateway-on-gcp) はトポロジーごとに具体的な値を持っています。信頼されたプロキシなしでは、すべてのリクエストはプロキシの IP から来ているように見え、IP ごとのレート制限を 1 つの共有バケットに折りたたみ、監査イベントにプロキシの IP を記録します。

<h3 id="container-image">
  コンテナイメージ
</h3>

標準 Claude Code リリースのネイティブ `claude` バイナリの周りに独自のイメージをビルドします：

1. ピン留めされたリリースからイメージアーキテクチャの Linux ビルドをダウンロードします。ダウンロード URL については、[特定のバージョンをインストールする](/docs/ja/setup#install-a-specific-version) を参照してください。
2. [バイナリの整合性とコード署名](/docs/ja/setup#binary-integrity-and-code-signing) で説明されているように、リリースの GPG 署名付き `manifest.json` に対して検証します。
3. ビルドコンテキストにコピーします。

ビルドがリリースホストに到達できない場合は、リリースを内部レジストリにミラーリングし、フロートが実行するバージョンをピン留めします。

バイナリを超えて、イメージは以下が必要です：

* **glibc ベースのイメージ**：glibc ビルドの唯一の動的依存関係は glibc ライブラリです。Musl ベースのイメージは `linux-x64-musl` または `linux-arm64-musl` ビルドと追加パッケージが必要です。[Alpine Linux セットアップ](/docs/ja/setup#alpine-linux-and-musl-based-distributions) を参照してください。
* **書き込み可能な状態ディレクトリ**：ゲートウェイは任意のユーザーとして実行されますが、最小限のイメージには書き込み可能なホームがありません。`CLAUDE_CONFIG_DIR` を `/tmp/.claude` などの書き込み可能なパスに設定します。
* **コンテナコマンド**：`claude gateway --config /etc/claude/gateway.yaml`。設定ファイルは読み取り専用でマウントされ、シークレットは環境変数として提供されます。ゲートウェイは `listen.port` でリッスンします。デフォルトは `8080` です。

<h3 id="kubernetes">
  Kubernetes
</h3>

ゲートウェイをデプロイメントとして実行します。他のステートレスサービスと同様です：

* ConfigMap から設定をマウントし、Secret からシークレットをマウントします。YAML で `${file:/path/to/secret}` または環境変数を通じてシークレットを参照します
* Ingress で TLS を終了し、`listen.public_url` を Ingress ホスト名に設定します
* readiness プローブを `GET /readyz` に、liveness プローブを `GET /healthz` に指定します

<Note>
  **ワークロードアイデンティティ**

  静的キーよりもプラットフォームのワークロードアイデンティティを優先します：EKS 上の Bedrock の場合は IRSA、GKE 上の Agent Platform の場合は Workload Identity、AKS 上の Foundry の場合はワークロードアイデンティティ。上流ブロックで `auth: {}` を設定するか、Foundry の場合は `use_azure_ad: true` を設定し、ゲートウェイはそのプロバイダーのデフォルト認証情報チェーンを通じてポッドのアイデンティティを取得します。GKE 上の Bedrock 上流など、クロスクラウドペアリングの場合は、上流の `auth` ブロックで明示的な認証情報を設定します。[`upstreams` リファレンス](/docs/ja/claude-apps-gateway-config#upstreams) にはプラットフォームごとのセットアップ詳細があります。
</Note>

<h3 id="cloud-run">
  Cloud Run
</h3>

サービスを以下のように設定します：

* `listen.port` をデフォルトの `8080` のままにします。これは Cloud Run のデフォルト `PORT` と一致するか、`port: ${PORT}` を設定します
* `public_url` を外部到達可能なオリジンに設定します。本番環境では、これは通常、内部ロードバランサーのホスト名です。`/login` は [パブリックアドレスを拒否](/docs/ja/claude-apps-gateway#prerequisites) し、`*.run.app` URL はそれに解決するため、Cloud Run URL だけは `curl` またはブラウザスモークテストにのみ機能します。例外は、`*.run.app` が Private Service Connect と Cloud DNS プライベートゾーンを通じてプライベートに解決するネットワークです。そのトポロジーでは、Cloud Run URL は有効な `public_url` です。[Google Cloud の実装例](/docs/ja/claude-apps-gateway-on-gcp#deploy-the-gateway) は両方をカバーしています。
* シークレットボリュームとして設定をマウントします
* `min-instances: 1` を設定して、最初のリクエストでコールド OIDC ディスカバリーを回避します

<Note>
  Google Cloud での完全な実装例（Cloud Run または GKE、Cloud SQL、Secret Manager をカバー）については、[Google Cloud にデプロイする](/docs/ja/claude-apps-gateway-on-gcp) を参照してください。
</Note>

<h3 id="push-the-gateway-url-to-developer-machines">
  ゲートウェイ URL を開発者マシンにプッシュする
</h3>

ゲートウェイがサービスを提供したら、MDM を通じて、または OS ごとの `managed-settings.json` を直接書き込むことで、管理設定を通じて各開発者のマシンに `forceLoginMethod` と `forceLoginGatewayUrl` をプッシュします。これなしでは、`/login` はゲートウェイオプションなしで標準アカウントピッカーを表示します。ファイルパスについては、[クライアント側の管理設定](/docs/ja/claude-apps-gateway-config#client-side-managed-settings) を参照してください。

<h2 id="operations">
  運用
</h2>

ゲートウェイがトラフィックを提供したら、日々の運用はそのログを読み込み、その健全性をプローブし、スケジュールに従ってシークレットをローテーションすることです。サブセクションは各々をカバーし、Postgres が保持するもの、アップグレードとロールバックがどのように動作するかをカバーします。

<h3 id="logs">
  ログ
</h3>

ゲートウェイは stderr に 2 つのストリームを書き込みます。両方とも JSON フレンドリーです：

* **監査イベント**：セキュリティ関連イベントごとの単一行 JSON。stderr をログアグリゲーターにパイプします。発行されるイベントには `config.load`、`session.mint`、`session.refresh`、`device.authorize`、`device.verify`、`auth.denied`、`access.denied`、`inference`、`managed.serve`、`spend.blocked`、`admin.denied` が含まれます。フィールドはイベントによって異なります：
  * 成功した mint と refresh イベントは `sub`、`email`、`client_ip`、結果を含みます
  * 拒否イベントは理由、パス、クライアント IP を含みます。拒否時にはアイデンティティが存在しないため
  * `inference` は、どの上流がリクエストを提供したか、応答ステータスを記録します
  * `admin.denied` は、拒否された admin-API 認証試行を理由（`invalid_key` または `no_credentials`）、クライアント IP、メソッド、パスで記録します。提示されたキーマテリアルなし
* **運用ログ**：ブート、警告、上流エラーの人間が読める `[gateway]` プレフィックス付きの行。`CLAUDE_GATEWAY_LOG_LEVEL` 環境変数は詳細度を制御し、`info`、`warn`、`error` を受け入れます。デフォルトは `info` です。監査イベントには影響しません。常に発行されます。

<h3 id="health">
  ヘルス
</h3>

ゲートウェイは `GET /healthz` を liveness プローブとして、`GET /readyz` を readiness プローブとして提供します。`/readyz` はストアが到達可能であることを検証します。両方とも `access_control.allow_cidrs` から除外されるため、プローブはロックダウンされたリスナーで機能し続けます。

`/.well-known/oauth-authorization-server` の OAuth ディスカバリードキュメントは、設定ロード、OIDC ディスカバリー、上流クライアント構築、Postgres マイグレーションがすべて成功した後にのみ `200` を返すため、エンドツーエンドのブートチェックとしても機能します。

実行中のゲートウェイは、実行しているバージョンに一致する `<public_url>/protocol` でそれが受け入れるパスとリクエスト形状の説明も提供します。内容はリリース間で安定していません。

<h3 id="outage-behavior">
  障害時の動作
</h3>

Postgres がダウンした場合、ゲートウェイ自体はサインイン済みの開発者にサービスを提供し続け、新しいサインインは失敗します。開発者が実際に機能し続けるかどうかは、オーケストレーターが readiness をどのように処理するかに依存します：

* **既存セッション**：ベアラートークンは JWT シークレットでローカルに検証され、セッション更新はストアに触れず、ゲートウェイプロセスは引き続き推論を提供できます
* **新しいサインイン**：Postgres が回復するまで失敗します。デバイスフローとそのレート制限カウンターは Postgres に存在するため
* **[支出制限の実装](/docs/ja/claude-apps-gateway-spend-limits#postgres-availability)**：デフォルトでは障害中に失敗してオープンになるため、推論は引き続き流れます。ブロックするのを好む場合は、失敗を閉じるようにフリップします
* **Readiness**：`/readyz` は障害中に not-ready を報告するため、readiness でトラフィックをゲートするオーケストレーターはすべてのレプリカを一度にローテーションから削除します。そのトポロジーでは、ゲートウェイが引き続き提供できる推論を含むすべてのトラフィックは、Postgres が回復するまでロードバランサーで失敗します。`/healthz` の liveness プローブは引き続き合格するため、レプリカは再起動されません。ストア障害を通じてサインイン済みの開発者が機能し続けるようにしたい場合は、readiness プローブを `/healthz` に指定します。コストは新しいサインインが引き続き ready を報告するレプリカに対して失敗することです。

IdP がダウンした場合、既存セッションは `ttl_hours` まで機能し、新しいログインと更新は失敗します。IdP が頻繁なメンテナンスウィンドウを持つ場合は、より長い `ttl_hours` を設定します。

<h3 id="jwt-secret-rotation">
  JWT シークレットローテーション
</h3>

既存セッションが有効なままになるように、3 つのステップで署名シークレットをローテーションします：

1. 新しいシークレットを生成します。`session.jwt_secret` 配列の前に付加します。
2. デプロイメントをロールします。新しいトークンは新しいシークレットで署名します。古いトークンは引き続き検証されます。
3. `ttl_hours` とマージンの後、古いシークレットを削除してもう一度ロールします。

ローテーションは、有効期限が切れる前にセッションを強制的に削除する唯一の方法でもあります。ベアラートークンは JWT シークレットに対してローカルに検証されるため、セッションごとの取り消しはありません。シークレットを完全に置き換え、配列に古いものを保持しないと、すべての未処理セッションが一度に無効になります。個別のオフボーディングの場合は、IdP でユーザーをプロビジョニング解除します。セッションは `ttl_hours` 内に終了します。

<h3 id="postgres">
  Postgres
</h3>

ゲートウェイは 5 つのテーブルを保持し、すべてはブート時マイグレーションで作成されます：

| テーブル               | 内容                                       | 保持期間                                                  |
| ------------------ | ---------------------------------------- | ----------------------------------------------------- |
| `kv`               | デバイスグラント（10 分 TTL）とレート制限カウンター            | 行ごとの TTL                                              |
| `spend`            | プリンシパルごとの期間から現在までの支出カウンター（セント単位）         | `admin.spend_retention_months`、デフォルト 13               |
| `spend_limits`     | 設定された支出キャップ                              | API 経由で削除されるまで                                        |
| `admin_audit`      | Admin API ミューテーショントレイル                   | `admin.audit_retention_days`、デフォルト 365                |
| `principal_emails` | 各プリンシパルの最後に見たメール、表示名、IdP グループ。PII を含みます。 | `admin.identity_retention_days` 最後のアクティビティ以来、デフォルト 90 |

30 秒ループは TTL を超えた `kv` 行を期限切れにし、1 時間のスイープは支出テーブルの保持ウィンドウを実装するため、何も無制限に成長しません。[支出制限](/docs/ja/claude-apps-gateway-spend-limits) が設定されていない場合、`kv` のみが書き込まれます。セキュリティポリシーがアプリケーションロールからの DDL を禁止する場合は、これらのテーブルと `_migrations` を管理ロールで事前作成し、各テーブルに `SELECT, INSERT, UPDATE, DELETE` をアプリロールに付与します。

支出制限が使用されている場合、失われたデータベースは失われた支出追跡とキャップを意味し、開発者の再ログインだけではないため、定期的なバックアップを実行します。保持を待つのではなく、出発した開発者を直ちに削除するには、`DELETE FROM principal_emails WHERE principal = '<sub>'` を直接実行します。これはメール、名前、グループを保持する唯一のテーブルを削除します。`spend` と `admin_audit` 行は疑似匿名 OIDC `sub` のみを参照します。

<h3 id="upgrades">
  アップグレード
</h3>

レプリカはステートレスであるため、ローリング再起動はいつでも安全です。ゲートウェイはブート時にスキーママイグレーションを実行します。つまり、新しいバイナリをデプロイするとデータベースが自動的にマイグレーションされます。データベースロールが DDL を実行できない場合は、スキーマを事前作成します。`_migrations` テーブルを現在のバージョンにシードします。そうしないと、`CREATE TABLE` を試みるブートが失敗します。

マイグレーションは追加のみであるため、より少ないマイグレーションを知っている以前のバイナリにロールバックするのは安全です。余分な行を無視します。ロールバックは YAML を古いバイナリのスキーマに対して再検証するため、新しいリリースで導入されたキーを採用した設定は古いバイナリでのブートに失敗します。ロールバックする前に新しいキーを削除します。

独自のイメージでゲートウェイのバージョンをピン留めするため、新しい Claude Code リリースのセキュリティ修正を含む修正は、ピンを更新して再デプロイするときにのみデプロイメントに到達します。ゲートウェイを、本番認証情報を保持する他のサービスに使用するのと同じパッチングケーデンスに含めます。

<h2 id="security">
  セキュリティ
</h2>

このセクションは、セキュリティレビューが尋ねる質問に答えます：ゲートウェイを通じてどのデータが流れ、どこに行くか、設計が防御する攻撃、コンプライアンスアンケートに属する回答。

<h3 id="data-flow">
  データフロー
</h3>

| データ                                                                             | パス                                                    | ゲートウェイによって Anthropic に送信    |
| ------------------------------------------------------------------------------- | ----------------------------------------------------- | --------------------------- |
| 推論（プロンプト、完了）                                                                    | CLI → ゲートウェイ → 上流                                     | Anthropic API が設定された上流の場合のみ |
| テレメトリ（OTLP メトリクス、プラス [オプトイン ログとトレース](/docs/ja/claude-apps-gateway-config#telemetry)） | CLI → ゲートウェイ → コレクター                                  | なし                          |
| アイデンティティ（メール、グループ、sub）                                                          | IdP → ゲートウェイ → JWT → CLI。CLI はそれを OTLP エクスポートにスタンプします | なし                          |
| 管理設定                                                                            | ゲートウェイ YAML → CLI                                     | なし                          |
| 監査ログ                                                                            | ゲートウェイ stderr → アグリゲーター                               | なし                          |

<h3 id="threat-model-summary">
  脅威モデルの概要
</h3>

ゲートウェイはネットワーク境界内に位置しますが、個々の開発者ラップトップは信頼されていないと見なされます。設計はこれを 3 つの方法で説明します：

* 開発者は生の上流キーの代わりに短命の JWT を保持します。CLI からゲートウェイへのレッグは RFC 8628 デバイスグラントを使用し、ゲートウェイの IdP との認可コード交換はデフォルト設定で PKCE を実行するため、インターセプトされた IdP 認可コードは無用です。
* デバイス検証ページは同一オリジン POST と RFC 8628 §5.1 ごとの IP ごとのレート制限を実装します。[ユーザーコードブルートフォース耐性](#user-code-brute-force-resistance) を参照してください。
* アウトバウンドリクエストはサーバー側リクエストフォージェリ（SSRF）ガードを通じて行われます。DNS を解決し、リンクローカルとクラウドメタデータアドレスをブロックし、デフォルトではループバックをブロックし、接続を解決された IP にピン留めします。IdP と OTLP 宛先などのオペレーター影響 URL はクラウドメタデータエンドポイントにリダイレクトできません。RFC 1918 プライベート範囲は意図的に許可されます。IdP と OTLP コレクターは一般的にプライベート IP に存在するため。ローカル開発でループバック IdP またはコレクターに対して、`CLAUDE_GATEWAY_ALLOW_LOOPBACK=1` をゲートウェイの環境に設定します。本番環境では設定しないままにします。

独自のエグレス制御を追加する場合、ゲートウェイはワークロードアイデンティティなどのインスタンスメタデータ認証情報を使用するときはいつでもメタデータサーバーに到達する必要があります。

2 つの脅威は、インフラストラクチャを保護するためのものであるため、スコープ外です：

* **侵害されたゲートウェイホスト**：ホストは上流認証情報を保持し、[管理設定](/docs/ja/claude-apps-gateway-config#managed) をすべての接続された開発者に配布するため、ゲートウェイの設定の制御は MDM の制御に匹敵します。CLI の 1 回限りの承認ダイアログはシェル対応設定のサイレント変更を制限しますが、ホストセキュリティに置き換わりません。
* **悪意のある OIDC プロバイダー**：プロバイダーはゲートウェイが信頼する id\_token に署名するため、任意のアイデンティティを主張できます。IdP の検証と保護はあなたの責任です。

<h3 id="user-code-brute-force-resistance">
  ユーザーコードブルートフォース耐性
</h3>

開発者が `/device` 検証ページに入力する `user_code` は、20 文字のアルファベットから引き出された 8 文字です。これは 20⁸ または約 2.56×10¹⁰ の組み合わせを生成し、10 分後に期限切れになります。

ゲートウェイは [`rate_limits`](/docs/ja/claude-apps-gateway-config#http-tuning) を通じて設定可能なデバイスグラントエンドポイントに IP ごとのレート制限を適用します。多くの開発者が単一の共有企業 NAT アドレスからサインインする場合は、制限を上げます。制限はサインインフローにのみ適用され、推論には適用されません。

<h3 id="compliance-posture">
  コンプライアンス体制
</h3>

* **データレジデンシー**：ゲートウェイ自体のデータプレーンは、Anthropic API が設定された上流の場合を除き、Anthropic に何も送信しません。その場合、既存のデータ処理契約が推論パスに適用されます。テレメトリ、監査、アイデンティティ、設定は設定した宛先にのみ行きます。
* **ホストプロセストラフィック**：ホストプロセスは Claude Code CLI です。スタートアップ分析と更新チェックを Anthropic に送信できます。厳密なエグレスデプロイメントの場合は、ゲートウェイのコンテナ環境で `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` を設定します。
* **クライアント分析**：CLI はゲートウェイにサインインしている間、独自の使用分析を無効にし、エラー報告はサードパーティ API サーフェスでデフォルトでオフです。
* **クライアントマシン**：開発者の CLI は、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` と `skipWebFetchPreflight: true` が設定されていない限り、WebFetch ホスト名チェックとバージョンチェックを Anthropic に送信し続けます。[データ使用](/docs/ja/data-usage) を参照してください。
* **サーベイ評価**：ゲートウェイ認証情報は Anthropic バウンド評価シンクを無効にするため、評価は Anthropic に送信されません。
* **トランスクリプト共有**：サーベイのトランスクリプト共有プロンプトで「はい」を選択すると、Anthropic にアップロードする代わりに `~/.claude/feedback-bundles/` の下にローカルファイルを書き込みます。
* **クライアント更新**：更新チェックはゲートウェイトラフィックとは別です。独自の配布を通じてバージョンをピン留めし、ラップトップがリリースをフェッチしてはいけない場合は `DISABLE_UPDATES` を設定します。`DISABLE_AUTOUPDATER` はバックグラウンド更新のみを停止し、`claude update` は引き続き機能します。
* **TLS**：本番環境で `public_url` を HTTPS 経由で提供します。ゲートウェイ自体のリスナー経由で `listen.tls` を使用するか、プレーン HTTP レプリカの前の TLS 終了 ingress から `listen.public_url` を設定します。ゲートウェイはプレーン HTTP を拒否しません。IdP は本番環境で HTTPS を提供する必要があり、Postgres は `?sslmode=require` をサポートします。ingress で `Strict-Transport-Security` を設定します。
* **脆弱性開示**：[セキュリティ問題の報告](/docs/ja/security#reporting-security-issues) に従います

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

質問とフィードバックについては、[Claude Code サポート](https://support.claude.com/en/collections/14445694-claude-code) を使用するか、[Claude Code GitHub リポジトリ](https://github.com/anthropics/claude-code/issues) で issue を開きます。問題を報告するときは、以下を含めます：

* **ゲートウェイの問題**：関連するウィンドウのゲートウェイの stderr、シークレットが削除された `gateway.yaml`、ゲートウェイバージョン（`/` のランディングページに表示、`/managed/settings` の `x-cc-gateway-version` レスポンスヘッダー）、最近変更されたもの
* **ログイン問題**：開発者は `claude --debug-file ./claude-debug.txt` を実行し、再現し、そのファイルとゲートウェイの同じウィンドウの監査ログを送信します
* **推論問題**：リクエストされたモデル、設定された上流、リクエストのゲートウェイ監査ログ。どの上流がそれを提供したか、応答ステータスを記録します

ゲートウェイの stderr には監査イベントストリームが含まれ、監査ログには開発者の ID が記録され、デバッグファイルには開発者のマシンからの hook と MCP サーバーの出力が記録されます。公開 issue に投稿する前に、これらを確認して秘密情報を削除してください。

| 症状                                                                                                                                                     | 原因                                                                                                                                                                                                                                                                                                                             | 修正                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 開発者の `/login` は標準アカウントピッカーを表示し、**Cloud gateway** 画面ではなく                                                                                                | 管理設定で `forceLoginMethod` または `forceLoginGatewayUrl` が設定されていない                                                                                                                                                                                                                                                                  | [管理設定ファイル](/docs/ja/claude-apps-gateway#set-the-gateway-url) をデバイスにデプロイします。`/login` はそこからゲートウェイ URL を読み込みます                                                                                                                                                                                              |
| スタートアップは `Gateway login is configured in managed settings, but this Claude Code build does not include Cloud gateway support.` を表示                     | インストールされた Claude Code ビルドはゲートウェイサポートより前                                                                                                                                                                                                                                                                                        | 開発者に Claude Code を Cloud gateway サポートを含むリリースに更新させます                                                                                                                                                                                                                                                 |
| CLI `/login`：`Gateway hosts must be on your organization's private network; <host> resolves to the public (or unrecognized) address <ip>`              | ゲートウェイホスト名は少なくとも 1 つのパブリック IP アドレスに解決されます。Claude Code は各解決されたアドレスをチェックし、すべてがプライベートであることを要求します。一般的な原因は、1 つのファミリーがパブリックアドレスに解決するデュアルスタック名です。AWS 内部デュアルスタックロードバランサーを含み、パブリック範囲 AAAA アドレスを返します。Anthropic が運用するパブリックゲートウェイエンドポイントはチェックから除外され、`/login` は `https://` 経由でそれらを受け入れます。v2.1.206 より前では、`/login` は他のパブリックアドレスと同様にそれらを拒否しました | ゲートウェイ名が開発者マシンでプライベートアドレスのみに解決されるようにします。デュアルスタック名の場合は、パブリック範囲レコードをドロップするか、個別の内部専用 DNS 名を提供します。[プライベートネットワーク前提条件](/docs/ja/claude-apps-gateway#prerequisites) を参照してください。                                                                                                                                  |
| CLI `/login`：`Gateway login requires a direct connection and does not support connecting through an HTTP proxy`                                        | `HTTPS_PROXY` または `HTTP_PROXY` がゲートウェイホストに適用され、プロキシのホスト名がパブリックアドレスに解決されます。ホスト名がプライベートアドレスのみに解決するプロキシは許可され、このエラーをトリガーしません                                                                                                                                                                                                       | ゲートウェイホストを開発者のマシンの `NO_PROXY` に追加して、接続が直接になるようにするか、ホスト名がプライベートアドレスに解決するプロキシを使用します                                                                                                                                                                                                                   |
| CLI `/login`：`Could not resolve gateway host <host>`                                                                                                   | マシンはゲートウェイの内部 DNS 名を解決できません。通常、企業ネットワークにないため                                                                                                                                                                                                                                                                                   | 開発者にネットワークまたは VPN に接続させ、`/login` を再試行します                                                                                                                                                                                                                                                            |
| ブートは `store.postgres_url` という名前の設定検証エラーで終了                                                                                                             | Postgres が設定されていません。ゲートウェイは Postgres が必要です                                                                                                                                                                                                                                                                                     | `store.postgres_url` を設定します。ローカル開発の場合は、使い捨てコンテナを使用します：`docker run --rm -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres`。                                                                                                                                                                   |
| ブートは終了：`requires the native binary`                                                                                                                    | Node の代わりにネイティブバイナリの下で実行                                                                                                                                                                                                                                                                                                       | [スタンドアロンインストール方法](/docs/ja/setup) の 1 つで Claude Code をインストールします                                                                                                                                                                                                                                          |
| ブートは `config.load` の後の OIDC ディスカバリーエラーで終了                                                                                                              | `oidc.issuer` に到達不可、または TLS チェーンが信頼されていない                                                                                                                                                                                                                                                                                      | issuer がポッドから到達可能で `/.well-known/openid-configuration` を提供することを確認します。プライベート PKI の場合は `ca_cert_pem` を設定します。                                                                                                                                                                                          |
| ブートは Postgres パーミッションエラーで終了                                                                                                                            | アプリロールに `CREATE TABLE` がない                                                                                                                                                                                                                                                                                                     | 管理ロールでスキーマを事前作成し、アプリロールに DML を付与するか、新しいマイグレーションを適用するブートのために DDL を一時的に付与します                                                                                                                                                                                                                          |
| `/oauth/callback` は「Sign-in could not be completed」を表示                                                                                                 | メールドメインが拒否されました。id\_token 検証が失敗しました。または `email_verified` が明示的に `false` です。ゲートウェイは常にオーバーライドなしで拒否します                                                                                                                                                                                                                             | `allowed_email_domains` を確認し、IdP が検証済み `email` クレームを返すことを確認します。`email_verified: false` の場合は、IdP 側の検証を修正します。IdP がメールを別のクレーム名の下で発行する場合は、`oidc.email_claim` を設定します。                                                                                                                                    |
| ログ：`token exchange failed: id_token missing email claim`                                                                                               | IdP はデフォルトで id\_token に `email` を含めていません。この拒否は `allowed_email_domains` が設定されている場合にのみ発火します。なしでは、欠落したメールはメールなしでセッションをミントします                                                                                                                                                                                                      | IdP を設定して id\_token で `email` を発行します。Okta：カスタム認可サーバーの ID トークンクレームに `email` を追加します。Entra：アプリ登録でオプションクレームとして `email` を追加します。PingFederate：`email` を発行する OpenID Connect ポリシーを有効にします。IdP が userinfo エンドポイントから `email` を提供するが、id\_token に含めない場合（Okta org 認可サーバーなど）、`oidc.userinfo_fallback: true` を設定します。 |
| すべての Amazon Bedrock リクエストは 502 を返します。ログは `Could not load credentials from any providers` を表示                                                           | EC2 では、IMDSv2 のデフォルトホップリミット 1 がコンテナ内からのインスタンスメタデータリクエストをブロックします。ブートと `/readyz` はクライアント構築時ではなく最初のリクエストで AWS SDK がインスタンス認証情報を解決するため、とにかく合格します                                                                                                                                                                                    | `aws ec2 modify-instance-metadata-options --instance-id <id> --http-put-response-hop-limit 2` でホップリミットを上げるか、起動テンプレートで設定します。変更はインスタンス上のすべてのコンテナに適用されます。利用可能な場合は ECS タスクロールを優先します。ECS コンテナ認証情報エンドポイントから認証情報を読み込み、変更を完全に回避するか、専用ゲートウェイインスタンスで変更を適用して露出を制限します。                                          |
| IdP エラー：unknown or unsupported scope                                                                                                                   | IdP は認識しないスコープを拒否します                                                                                                                                                                                                                                                                                                           | `oidc.scopes` を IdP が受け入れる正確なリストに設定します。`openid` を含める必要があります。デフォルトは `openid profile email offline_access` です。                                                                                                                                                                                        |
| `oidc.scopes` を設定した後、セッションはサイレントに更新されません                                                                                                               | `offline_access` がオーバーライドからドロップされました                                                                                                                                                                                                                                                                                           | IdP がサポートしている場合は `offline_access` を戻します。リフレッシュトークンなしでは、開発者は `session.ttl_hours` ごとにブラウザログインを再実行します。                                                                                                                                                                                                 |
| ブラウザは「This request came from another site and was blocked」を表示                                                                                          | クロスサイトフォーム POST。CSRF 保護としてブロックされました。埋め込みまたはプロキシされたページの場合は予想されます                                                                                                                                                                                                                                                                | 検証リンクを直接開きます                                                                                                                                                                                                                                                                                        |
| Chrome は「Refused to send form data … violates … Content Security Policy directive: form-action」で Approve ボタンをブロックしますが、同じページは Safari または Firefox で機能します | Chrome はリダイレクトチェーン全体に対して `form-action` を実装します。IdP はさらに、許可リストに登録されていない 2 番目のホストにリダイレクトします。                                                                                                                                                                                                                                      | リダイレクトチェーン内の各追加オリジンを `oidc.form_action_origins` に追加します。Approve ページで Chrome DevTools → Console を開いて、どのオリジンがブロックされたかを確認します。                                                                                                                                                                           |
| サインインは IdP で完了しますが、コールバックは失敗します。Chrome で CSP エラーまたは Safari で「this sign-in link has expired」                                                            | IdP は `response_mode=form_post` を通じてコードを返しました。これは `/oauth/callback` にクロスオリジン POST を通じて自動送信します。Chrome はそれを厳密な CSP の下でブロックします。Safari は送信を許可しますが、コールバックはクエリ文字列のみを読み込みます。                                                                                                                                                          | IdP が `response_mode=query` を尊重することを確認します。ゲートウェイは明示的にリクエストするため、コールバックはプレーンリダイレクトです                                                                                                                                                                                                                  |
| ログインはローカルで機能しますが、ALB の背後で失敗します                                                                                                                         | `public_url` が設定されていないため、IdP は内部 `http://` オリジンを `redirect_uri` として取得します                                                                                                                                                                                                                                                       | `listen.public_url` を外部 `https://` オリジンに設定します                                                                                                                                                                                                                                                       |
| 開発者は信頼プロンプトを繰り返し見ます                                                                                                                                    | TLS 証明書はレプリカごと、またはリクエストごとにローテーションしています                                                                                                                                                                                                                                                                                         | ingress で安定した証明書を使用するか、TLS を 1 回終了し、レプリカをプレーン HTTP で内部で実行します                                                                                                                                                                                                                                        |
| CLI `/login`：「Could not verify the gateway's TLS certificate」または `SELF_SIGNED_CERT_IN_CHAIN`                                                           | ゲートウェイの TLS チェーンは、CLI ホストの信頼ストアにないプライベート CA によって署名されています                                                                                                                                                                                                                                                                       | Claude Code はデフォルトでネイティブバイナリで OS 信頼ストアを読み込み、Node 22.15 以降で読み込みます。[`CLAUDE_CODE_CERT_STORE`](/docs/ja/network-config#ca-certificate-store) はこの動作を制御します。CA が OS 信頼ストアにインストールされている場合は、開発者が現在のランタイムにいることを確認します。そうでない場合は、起動する前に `NODE_EXTRA_CA_CERTS` を CA 証明書 PEM に設定します。最初の接続フィンガープリントプロンプトは引き続き適用されます。     |

<h2 id="related">
  関連
</h2>

* [Claude apps gateway の概要](/docs/ja/claude-apps-gateway)：クイックスタートと開発者接続
* [設定リファレンス](/docs/ja/claude-apps-gateway-config)：すべての `gateway.yaml` オプション
