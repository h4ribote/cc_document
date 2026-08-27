> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Amazon Bedrock、Claude Platform on AWS、Google Cloud、Microsoft Foundry 向け Claude アプリゲートウェイ

> SSO サインイン、グループごとのモデルアクセス、OTLP テレメトリを備えた自己ホスト型ゲートウェイを通じて、Amazon Bedrock、Claude Platform on AWS、Google Cloud、または Microsoft Foundry で Claude Code を実行します。

<Note>
  Claude アプリゲートウェイは、[データレジデンシー](/docs/ja/claude-apps-gateway-deploy#compliance-posture)要件を満たすなど、独自のクラウドプロバイダーを通じて推論をルーティングする必要がある、または希望する組織向けに設計されています。この要件がない場合、SCIM プロビジョニングや web・モバイル上の Claude Code などの他の機能へのアクセスを希望する場合は、Claude Enterprise の方がより適切である可能性があります。すべてのデプロイメント方法の完全な比較については、[機能可用性](/docs/ja/feature-availability)ページを参照してください。
</Note>

Claude アプリゲートウェイは、開発者の Claude Code クライアントとモデルプロバイダーの間に位置する自己ホスト型サービスです。開発者は API キーやクラウド認証情報を保持する代わりに、企業の ID プロバイダー（IdP）でサインインします。ゲートウェイはアップストリーム認証情報を保持し、IdP グループによるモデルアクセスと[管理設定](/docs/ja/permissions#managed-settings)を強制し、使用状況テレメトリを独自の可観測性スタックにリレーします。

これは `claude` バイナリに含まれているため、ラップトップで Claude Code を実行する同じ実行ファイルが `claude gateway --config gateway.yaml` でゲートウェイサーバーを実行します。

このページでは以下をカバーしています。

* [Claude アプリゲートウェイを使用する理由](#why-claude-apps-gateway)、独自に実行する場合に何が追加されるか、および他の何かがより適切な場合
* [前提条件](#prerequisites)を含む[クイックスタート](#quickstart)。ゲートウェイをゼロからサインイン済みの開発者まで進めます
* [開発者の接続](#connect-developers)。管理設定を通じてゲートウェイ URL を設定することを含みます
* [可用性と制限事項](#availability-and-limitations)。ゲートウェイを通じてどの Claude Code 機能が機能するか、およびサーバーが何をサポートするかをカバーしています

関連ページはさらに詳しく説明しています。[設定リファレンス](/docs/ja/claude-apps-gateway-config)はクイックスタートが書き込む YAML ファイルのすべてのオプションをカバーし、[デプロイメントガイド](/docs/ja/claude-apps-gateway-deploy)は IdP ごとのセットアップ、Kubernetes と Cloud Run デプロイメント、および運用をカバーしています。

<h2 id="why-claude-apps-gateway">
  Claude apps gateway を使用する理由
</h2>

[ゲートウェイの概要](/docs/ja/gateways)はゲートウェイが何をするか、なぜ実行するかをカバーしています。Claude apps gateway は Anthropic 独自のゲートウェイで、`claude` バイナリに組み込まれており、各 Claude Code リリースと一緒にテストされているため、Claude Code が送信するヘッダーとリクエストフィールドを、オペレーターが個別の許可リストを維持することなく転送します。デプロイされると、以下が得られます。

* **認証情報**：アップストリーム API キーまたはクラウド認証情報は、インフラストラクチャ内にのみ存在します。開発者は企業 SSO で認証し、短期間有効なベアラートークンを受け取るため、オフボーディングは IdP で発生します。ユーザーをプロビジョニング解除すると、ゲートウェイアクセスはセッション有効期間内に期限切れになります。デフォルトは 1 時間です。
* **アクセス制御**：IdP グループはモデル許可リストと[管理設定](/docs/ja/permissions#managed-settings)ポリシーにマップされます。ゲートウェイはモデルアクセスをサーバー側で強制し、許可されていないモデルのリクエストを拒否し、各グループの管理設定ポリシーを選択します。CLI は[管理設定層](/docs/ja/settings#settings-precedence)でこれを適用します。異なるチームは異なるモデル、ツール、および権限を取得し、開発者はポリシーがロックしているものをオーバーライドできません。
* **設定配信**：ゲートウェイは管理設定をサインイン済みクライアント自体に配信し、claude.ai 管理コンソールからの[サーバー管理設定](/docs/ja/server-managed-settings)の場所を取ります。
* **テレメトリ**：Datadog、Splunk、ClickHouse などの各設定先は、デフォルトではトークン数、モデル、ユーザーアイデンティティ、レイテンシを含む[OpenTelemetry Protocol（OTLP）メトリクス](/docs/ja/monitoring-usage)を受け取り、ログとトレースは宛先ごとのオプトインです。
* **アップストリームルーティング**：クライアントは Anthropic Messages API をゲートウェイに話しかけ、ゲートウェイは各アップストリーム（Amazon Bedrock、[Claude Platform on AWS](/docs/ja/claude-platform-on-aws)、Google Cloud の Agent Platform、Microsoft Foundry、または Anthropic API）に対して変換し、それらの間でフェイルオーバーします。開発者が気付いたり再設定したりすることなく、リージョン、プロバイダー、またはフェイルオーバー順序を変更できます。

<Frame>
  <img src="https://mintcdn.com/claude-code/VbyXug8hBU9UK6oT/images/claude-gateway-architecture.svg?fit=max&auto=format&n=VbyXug8hBU9UK6oT&q=85&s=9e4f1190fc56718144190a3db61c63af" alt="Claude Code クライアントがベアラートークンを使用して HTTPS 経由でインフラストラクチャ内の自己ホスト型 Claude apps ゲートウェイに接続し、IdP に対してユーザーにサインインし、PostgreSQL に認証状態を保存し、テレメトリを OTLP コレクターにリレーし、Amazon Bedrock、Claude Platform on AWS、Google Cloud、Microsoft Foundry、または Anthropic API に推論を転送する図" width="760" height="320" data-path="images/claude-gateway-architecture.svg" />
</Frame>

<Note>
  ゲートウェイ独自のデータプレーンは、Anthropic API が設定されたアップストリームでない限り、Anthropic インフラストラクチャに何も送信しません。テレメトリ、監査ログ、管理設定、および開発者の IdP アイデンティティがどこに行くかを制御し、ゲートウェイはそれらのいずれも Anthropic に送信しません。残りのトラフィック CLI プロセスが送信できる方法と、それを閉じる方法については、[コンプライアンスポスチャ](/docs/ja/claude-apps-gateway-deploy#compliance-posture)を参照してください。
</Note>

ゲートウェイを通じてどの Claude Code 機能が機能するか、およびサーバー自体が何をサポートするかについては、以下の[可用性と制限](#availability-and-limitations)を参照してください。コスト、バイパス、複数ゲートウェイの実行、サーバーレスプラットフォームなどの決定については、[デプロイメントガイド](/docs/ja/claude-apps-gateway-deploy#deployment)を参照してください。

<h3 id="other-gateway-implementations">
  その他のゲートウェイ実装
</h3>

既に要件を満たす LLM ゲートウェイまたは API ゲートウェイを実行している場合は、それを使い続けてください。[その他の LLM ゲートウェイ](/docs/ja/llm-gateway)は Claude Code をそれに対して設定することをカバーしています。

[ゲートウェイプロトコルリファレンス](/docs/ja/llm-gateway-protocol)は、Claude Code が任意のゲートウェイから期待する契約を文書化しています。呼び出すエンドポイント、転送するヘッダーとボディフィールド、およびそれらが削除されたときに何が機能しなくなるかです。実行中の Claude apps ゲートウェイは、SSO サインイン、管理設定配信、およびテレメトリ用の Claude apps ゲートウェイ固有のエンドポイントを追加して、その契約のスーパーセットを `GET /protocol` で提供します。`curl https://claude-gateway.internal.example.com/protocol` を使用して、[クイックスタート](#quickstart)以下が生成するようなデプロイされたゲートウェイから取得します。プロトコルへの破壊的な変更は事前に発表されますが、無期限の後方互換性は保証されません。

<h2 id="quickstart">
  クイックスタート
</h2>

このクイックスタートは最小限のパスを説明しています。IdP で OAuth クライアントを登録し、`gateway.yaml` を書き、Docker Compose で Postgres と一緒にゲートウェイを実行し、エンドツーエンドでサインインを確認します。Amazon Bedrock アップストリームを使用します。Claude Platform on AWS、Google Cloud の Agent Platform、Microsoft Foundry、および Anthropic API は、[設定リファレンス](/docs/ja/claude-apps-gateway-config#upstreams)に示されているように `upstreams` ブロックをスワップすることで同様にサポートされます。最後に、開発者が `/login` できるゲートウェイがあります。

<Note>
  **プライベートネットワークにデプロイします。** Claude Code は、アドレスがプライベートであるゲートウェイにのみ接続します。これはセキュリティガードです。信頼されたゲートウェイは開発者マシンでコマンドを実行する設定をプッシュできるためです。ゲートウェイを内部ロードバランサーまたは VPN の背後に配置し、プライベート IP にのみ解決するホスト名を付けます。

  Anthropic が運用するパブリックゲートウェイエンドポイントは例外です。`/login` は `https://` 経由でそれらを受け入れます。これらは Anthropic 自体が運用する小さな固定セットのゲートウェイです。これらは選択または設定できるデプロイメントオプションではありません。リストは Claude Code にコンパイルされているため、設定がホスト名をリストに追加することはできず、ホストするゲートウェイは免除の対象にはなりません。v2.1.206 より前では、`/login` はそれらのエンドポイントを他のパブリックアドレスと同様に拒否していました。
</Note>

<h3 id="prerequisites">
  前提条件
</h3>

開始する前に、以下を用意してください。

| 必要なもの                         | 詳細                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code v2.1.195 以降       | `claude gateway` サブコマンドとゲートウェイサインインフローは v2.1.195 で提供されます。以前のパブリックビルドには含まれていません。ゲートウェイサーバーを実行するマシンと各開発者のマシンの両方が v2.1.195 以降である必要があります。`claude update` を実行して最新リリースを取得します。 [Claude Platform on AWS アップストリーム](/docs/ja/claude-apps-gateway-config#claude-platform-on-aws)はゲートウェイサーバーで Claude Code v2.1.198 以降が必要です。                                                                                                                                                                                                                                                                             |
| OpenID Connect（OIDC）ID プロバイダー | Okta、Microsoft Entra ID、Google Workspace、Keycloak、Dex、または PingFederate などの OIDC 準拠の IdP。ゲートウェイは標準 OIDC ディスカバリーと認可コードフローを実行します。SAML と LDAP はサポートされていません。                                                                                                                                                                                                                                                                                                                                                                                                                                |
| PostgreSQL 14 以降              | デバイスサインインフロー（ブラウザコールバックが書き込み、ポーリング CLI が読み取る）とレート制限カウンターをサポートします。最小層を含む任意の管理 Postgres が機能します。支出制限が設定されていない場合、ゲートウェイは数 KB の短期間有効な認証状態を保存します。[支出制限](/docs/ja/claude-apps-gateway-spend-limits)を使用すると、バックアップする必要がある耐久的な支出、監査、およびアイデンティティテーブルも保持します。`?sslmode=require` 経由の TLS が推奨されます。                                                                                                                                                                                                                                                                                                         |
| モデルアップストリーム                   | Amazon Bedrock 認証情報、Claude Platform on AWS 認証情報、Google Cloud 認証情報、Microsoft Foundry リソース、または Anthropic API キー。複数のアップストリームがサポートされ、フェイルオーバーがあります。                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| HTTPS                         | ゲートウェイは開発者ラップトップとサインインに使用されるブラウザから `https://` 経由で到達可能である必要があります。ゲートウェイは同じリスナーでデバイス検証ページを提供します。`listen.tls` 経由で TLS 証明書を提供するか、TLS 終了イングレスの背後で実行し、`listen.public_url` を設定します。プレーン `http://` オリジンはローカル開発用のループバックでのみ受け入れられます。                                                                                                                                                                                                                                                                                                                                                              |
| プライベートネットワークアドレス              | `/login` では、Claude Code はゲートウェイのホスト名または IP アドレスがプライベートアドレスのみに解決されることを要求します。RFC 1918、CGNAT `100.64.0.0/10`、IPv6 ULA `fc00::/7`、またはローカル開発用のループバック。チェックは解決された各 IP で実行されるため、名前が解決するアドレスのいずれかがパブリックの場合、`/login` は URL を拒否します。開発者マシンが HTTPS を企業プロキシ経由でルーティングする場合、サインインはプロキシホストもプライベートアドレスに解決されることを要求します。そうでない場合は、ゲートウェイホストを `NO_PROXY` に追加して、CLI が直接接続するようにします。Anthropic が運用するパブリックゲートウェイエンドポイントはプライベートアドレスとプロキシチェックから除外されます。`/login` は正確なホスト名マッチにより `https://` 経由でそれらを受け入れるため、プライベートネットワーク要件はホストするゲートウェイにのみ適用されます。v2.1.206 より前では、`/login` は Anthropic が運用するエンドポイントを他のパブリックアドレスと同様に拒否していました。 |
| Linux ランタイム                   | ゲートウェイサーバーはネイティブ Linux バイナリでのみ実行されます。macOS はローカル開発用に機能します。Windows はサーバープラットフォームとしてサポートされていません。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |

ゲートウェイサーバーはネイティブ `claude` バイナリが必要です。[Claude Code のインストール](/docs/ja/setup)で説明されているようにピン留めされたリリースをダウンロードします。サーバーは Claude Code が Node の下で実行されるときに利用できないランタイム機能を使用します。起動時に `requires the native binary` が表示される場合は、スタンドアロンインストール方法の 1 つに切り替えます。

<h3 id="steps">
  ステップ
</h3>

<Steps>
  <Step title="IdP で OAuth クライアントを登録する">
    リダイレクト URI がそれと一致する必要があるため、まずゲートウェイのホスト名を決定します。新しい OIDC ウェブアプリケーションを作成し、リダイレクト URI を `https://claude-gateway.<your-domain>/oauth/callback` に設定します。ホストはステップ 3 で [`listen.public_url`](/docs/ja/claude-apps-gateway-config#listen) として設定する値と同じです。`client_id` と `client_secret` をメモします。IdP ごとの手順は[ID プロバイダーセットアップ](/docs/ja/claude-apps-gateway-deploy#identity-provider-setup)にあります。
  </Step>

  <Step title="PostgreSQL データベースをプロビジョニングする">
    最小管理層を含む任意の Postgres 14 以降が機能します。ゲートウェイは起動時に独自のスキーママイグレーションを実行するため、データベースユーザーは `CREATE TABLE` 権限が必要です。セキュリティポリシーがアプリケーションロールからの DDL を禁止する場合は、代わりにスキーマを事前作成します。[`store`](/docs/ja/claude-apps-gateway-config#store)を参照してください。
  </Step>

  <Step title="gateway.yaml を書く">
    シークレットは `${ENV_VAR}` 展開経由で読み取られるため、ファイル自体はバージョン管理に存在できます。`/login` がパブリックアドレスを拒否するため、プライベート IP に解決する `public_url` ホスト名を使用します。最小設定には 5 つのセクションがあり、他のすべてのフィールドにはデフォルトがあります。

    ```yaml gateway.yaml theme={null}
    listen:
      host: 0.0.0.0
      port: 8080
      # TLS 終了プロキシの背後で必須。IdP
      # redirect_uri とディスカバリードキュメントに使用されます。
      public_url: https://claude-gateway.internal.example.com

    oidc:
      issuer: https://login.example.com        # /.well-known/openid-configuration を提供する必要があります
      client_id: 0oa1example2
      client_secret: ${OIDC_CLIENT_SECRET}
      allowed_email_domains: [example.com]        # 組織外の id_tokens を拒否します
      userinfo_fallback: true                  # id_token が email/groups を省略する IdP の場合。それ以外の場合は無害です

    session:
      jwt_secret: ${GATEWAY_JWT_SECRET}        # openssl rand -base64 32
      ttl_hours: 1                             # IdP プロビジョニング解除時の失効レイテンシもバウンドします

    store:
      postgres_url: ${GATEWAY_POSTGRES_URL}    # 管理 Postgres の場合は ?sslmode=require を追加します

    upstreams:
      - provider: bedrock
        region: us-east-1
        auth: {} # 空：AWS デフォルト認証情報チェーン
    # （IRSA、EC2/ECS タスクロール、環境変数、~/.aws）

    # モデルはアップストリームごとに自動的に変換されます。組み込みカタログ
    # は claude-opus-4-8 を us.anthropic.claude-opus-4-8 にマップし、
    # Bedrock がサポートするすべての Claude モデルに対して同様にマップします。false に設定し、
    # `models:` リストを追加して、特定のモデルのみを公開します。
    auto_include_builtin_models: true
    ```

    この設定は、デフォルト Amazon Bedrock モデルカタログを使用した動作するサインインループに十分です。実行されたら、[`managed.policies`](/docs/ja/claude-apps-gateway-config#managed) 経由でグループごとの RBAC と管理設定を追加し、[`telemetry`](/docs/ja/claude-apps-gateway-config#telemetry) 経由でテレメトリファンアウトを追加し、[`models`](/docs/ja/claude-apps-gateway-config#models) 経由でマルチアップストリームフェイルオーバー、プロビジョニング済みスループット ARN、または非米国リージョンを追加します。

    <Note>
      Amazon Bedrock アップストリームは、`inference-profile/us.anthropic.*` ARN と基礎となる `foundation-model/anthropic.*` ARN の両方に対して `bedrock:InvokeModel` と `bedrock:InvokeModelWithResponseStream` を持つ AWS プリンシパルが必要であり、Bedrock コンソールで必要な Claude モデルのモデルアクセスが有効になっています。EKS の IRSA、ECS タスクロール、または EC2 インスタンスプロファイルではなく、静的キーを使用して認証情報を提供します。[`upstreams` リファレンス](/docs/ja/claude-apps-gateway-config#upstreams)には、完全な IAM 詳細、クロスクラウド認証情報マトリックス、および他のプロバイダーの `auth` ブロックがあります。
    </Note>
  </Step>

  <Step title="実行する">
    [イメージ要件](/docs/ja/claude-apps-gateway-deploy#container-image)を満たす `claude` バイナリの周りにコンテナイメージを構築し、Postgres と一緒に実行します。

    ```yaml docker-compose.yaml theme={null}
    services:
      gateway:
        image: <your-registry>/claude-gateway:<version>
        ports: ["8080:8080"]
        volumes: ["./gateway.yaml:/etc/claude/gateway.yaml:ro"]
        environment:
          OIDC_CLIENT_SECRET: ${OIDC_CLIENT_SECRET}
          GATEWAY_JWT_SECRET: ${GATEWAY_JWT_SECRET}
          GATEWAY_POSTGRES_URL: postgres://gw:pw@postgres/gateway
          # AWS 認証情報：本番環境では、これらを省略し、インスタンス
          # ロールを使用します。ローカル Compose テストの場合、独自のものを渡します。
          AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
          AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
          AWS_SESSION_TOKEN: ${AWS_SESSION_TOKEN}
        depends_on:
          postgres:
            condition: service_healthy
      postgres:
        image: postgres:16-alpine
        environment: { POSTGRES_USER: gw, POSTGRES_PASSWORD: pw, POSTGRES_DB: gateway }
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U gw"]
          interval: 5s
        volumes: ["pgdata:/var/lib/postgresql/data"]
    volumes: { pgdata: }
    ```

    ゲートウェイは、設定を読み取り、IdP に対して OIDC ディスカバリーを実行し、Postgres スキーママイグレーションを適用し、アップストリームクライアントを構築し、リッスンを開始する単一の Linux バイナリです。起動は設定、5 秒タイムアウト付き Postgres 接続、OIDC ディスカバリー、およびアップストリームクライアント構築に対して失敗時に閉じられます。これらのいずれかが到達不可能または設定が誤っている場合、ゲートウェイは低下した状態でトラフィックを提供するのではなく、エラーで終了します。

    成功した起動は推論パスを検証しません。Amazon Bedrock と Google Cloud の Agent Platform インスタンス認証情報は起動時ではなく最初のリクエストで解決されるためです。

    起動シーケンスについて stderr を監視します。ログ行は `[gateway] <timestamp> <level> <message>` 形式を使用し、監査イベントは `evt` フィールド付きの単一行 JSON であり、起動バナーは以下で省略され、マイグレーションとリッスン行の間に出力されます。順番に以下が表示されます。

    ```text theme={null}
    {"ts":"2026-06-10T17:03:21.114Z","evt":"config.load","path":"/etc/claude/gateway.yaml","sha256":"…"}
    [gateway] 2026-06-10T17:03:21.408Z info migration 1 applied
    [gateway] 2026-06-10T17:03:21.512Z info claude gateway listening on http://0.0.0.0:8080
    ```

    起動が `claude gateway listening on` 行の前に終了する場合、stderr の最後の行は問題を名前付けます。

    * 到達不可能な Postgres
    * DDL 権限のない Postgres ロール
    * 到達不可能または無効な OIDC ディスカバリードキュメント
    * 違反フィールドパスを含む設定スキーマ違反

    修正して再起動します。

    既に TLS 終了イングレスがある場合は、Compose をスキップし、`claude gateway --config gateway.yaml` でバイナリを直接実行します。`public_url` をイングレスオリジンに設定し、`listen` をループバックまたはクラスター内アドレスにバインドします。
  </Step>

  <Step title="認証サーフェスを確認する">
    3 つのチェックは、ゲートウェイが開発者に渡す前に実際のユーザーを認証できることを確認します。

    例はゲートウェイのパブリック URL を使用します。イングレスのないローカル Compose セットアップの場合、最初の 2 つのチェックで `http://localhost:8080` に置き換えます。3 番目のチェックは `verification_uri_complete` を開きます。これは `public_url` から構築されるため、ローカル Compose の場合は `gateway.yaml` で `public_url: http://localhost:8080` を設定し、ゲートウェイが `public_url` から IdP `redirect_uri` を構築するため、ステップ 1 の OAuth クライアントに 2 番目のリダイレクト URI として `http://localhost:8080/oauth/callback` を追加します。検証リンクはローカルブラウザで開きます。

    Windows PowerShell では、`curl.exe` を実行します。ベア `curl` は `Invoke-WebRequest` のエイリアスであり、これらのフラグを拒否します。

    まず、ディスカバリードキュメントを取得します。これはゲートウェイが起動し、設定が有効であり、すべての起動チェックが合格したことを確認します。

    ```bash theme={null}
    curl -s https://claude-gateway.internal.example.com/.well-known/oauth-authorization-server | jq
    ```

    ```json theme={null}
    {
      "issuer": "https://claude-gateway.internal.example.com",
      "device_authorization_endpoint": "…/oauth/device_authorization",
      "token_endpoint": "…/oauth/token",
      "grant_types_supported": ["urn:ietf:params:oauth:grant-type:device_code", "refresh_token"]
    }
    ```

    応答には `response_types_supported` や `scopes_supported` などの追加フィールドが含まれます。

    次に、デバイス認可をリクエストします。これはデバイスサインインフローが機能し、Postgres が到達可能で書き込み可能であることを確認します。

    ```bash theme={null}
    curl -s -X POST https://claude-gateway.internal.example.com/oauth/device_authorization | jq
    ```

    ```json theme={null}
    {
      "device_code": "…",
      "user_code": "WDJB-MJHT",
      "verification_uri": "https://claude-gateway.internal.example.com/device",
      "verification_uri_complete": "https://claude-gateway.internal.example.com/device?user_code=WDJB-MJHT",
      "expires_in": 600,
      "interval": 5
    }
    ```

    3 番目に、ブラウザで `verification_uri_complete` を開いてコードを確認することでブラウザレッグをテストします。IdP のサインインページにリダイレクトされ、サインイン後、ゲートウェイに戻ってサインイン確認に着地する必要があります。

    最初に失敗したチェックを使用して問題を特定します。

    * **最初のチェックが失敗**：起動が完了しませんでした。stderr を確認してください
    * **2 番目のチェックが失敗**：Postgres がゲートウェイから到達不可能であるか、ロールが書き込みできません。接続文字列と権限を確認してください
    * **3 番目のチェックが IdP に到達しない**：IdP のリダイレクト URI が `https://<gateway>/oauth/callback` と正確に一致することを確認してください
    * **3 番目のチェックが IdP に到達しますが、エラーで戻ります**：ゲートウェイの監査ログを読みます。これは `email domain not allowed` などの理由を含むすべての認証拒否を記録します
  </Step>

  <Step title="開発者をログインさせる">
    この最後のステップはサーバーではなく開発者マシンで発生します。そのマシンの[管理設定ファイル](/docs/ja/settings#settings-files)で `forceLoginMethod` を `"gateway"` に、`forceLoginGatewayUrl` をゲートウェイの `public_url` に設定し、`/login` を実行し、**Cloud gateway** 画面で Enter キーを押し、ブラウザサインインを完了します。[ゲートウェイ URL を設定](#set-the-gateway-url)以下は、スケール時に両方のキーを配布することをカバーしています。
  </Step>
</Steps>

<h2 id="connect-developers">
  開発者を接続する
</h2>

開発者は独自のラップトップから 1 つのブラウザサインインで接続し、企業の仕事用アカウントを使用します。claude.ai アカウント、API キー、またはサブスクリプションは必要ありません。モデルへのリクエストは組織のアップストリーム認証情報を使用してゲートウェイを通じて行くためです。接続は、MDM 経由でプッシュする[クライアント側管理設定](/docs/ja/claude-apps-gateway-config#client-side-managed-settings)によって駆動されるため、開発者側に手動セットアップはありません。このセクションは管理者が設定するものをカバーしています。

CLI はゲートウェイの TLS リーフ証明書を最初の接続時にフィンガープリントし、ホスト名ごとにピン留めします。期待されるフィンガープリント SHA-256 をゲートウェイ URL と一緒に公開して、開発者が比較するものを持つようにします。証明書ファイルから `openssl x509 -noout -fingerprint -sha256 -in cert.pem` でフィンガープリントを取得します。`/login` プロンプトはダイジェストの最初の 16 文字を小文字の 16 進数で区切り文字なしで表示します。

証明書がローテーションされると、すべての開発者は再度信頼プロンプトを見るため、ローテーションを計画されたイベントとして扱い、フィンガープリントを再公開します。

サインイン後、[モデルピッカー](/docs/ja/model-config)は開発者の `availableModels` 許可リストのモデルを表示し、管理設定は起動時に適用され、1 時間ごとに更新され、テレメトリはコレクターにルーティングされます。セッションは `ttl_hours` 有効期限の前にサイレントに更新され、IdP プロビジョニング解除後の失敗した更新は再ログインを促します。

<h3 id="set-the-gateway-url">
  ゲートウェイ URL を設定する
</h3>

MDM 経由またはディスク上で直接デプロイする OS ごとの[管理設定ファイル](/docs/ja/settings#settings-files)に両方のキーを設定し、`/login` は URL が入力された状態で **Cloud gateway** 画面で直接開きます。

```json theme={null}
{
  "forceLoginMethod": "gateway",
  "forceLoginGatewayUrl": "https://claude-gateway.internal.example.com"
}
```

開発者は Enter キーを押して接続します。最初の接続 TLS フィンガープリントプロンプトは引き続き表示されます。

開発者が手動で選択するためのログインピッカーにゲートウェイオプションはなく、`forceLoginGatewayUrl` は開発者独自の設定ファイルでは無視されます。URL なしの `forceLoginMethod` のみでは、開発者を「IT 管理者に連絡してください」メッセージのままにします。両方のキーは、マシンにプッシュするファイルに属し、ゲートウェイの `managed.policies[].cli` ブロックには属しません。これは既に接続されているクライアントにのみ到達します。

<h3 id="ci-pipelines-and-remote-machines">
  CI パイプラインとリモートマシン
</h3>

無人パイプラインのサービストークンフローはありません。ゲートウェイサインインは常にブラウザデバイスフローを実行するため、サインインを承認する開発者がない CI ジョブは認証できません。これらをプロバイダーに対して直接設定します。

開発者がサインインすると、そのマシンでのすべての Claude Code 呼び出しはゲートウェイセッションを使用します。非対話的な `claude -p` 実行と Agent SDK によって開始されたセッションを含み、[ゲートウェイポリシーはすべてに適用されます](/docs/ja/claude-apps-gateway-config#managed)。

デバイスフローはポーリング CLI を承認ブラウザから分離するため、ディスプレイのないリモート開発ボックスは引き続き機能します。開発者はリモートマシンで SSH 経由で `/login` を実行し、ラップトップのブラウザで検証リンクを開きます。

<h3 id="what’s-enforced-on-developers">
  開発者に何が強制されるか
</h3>

これらの保証はすべてのサインイン済みゲートウェイセッションに適用されます。

* **モデルアクセス**：ポリシーが許可しないモデルのリクエストは 400 を返し、`/model` ピッカーはポリシーの `availableModels` 許可リストにフィルタリングされます。ポリシーで [`enforceAvailableModels: true`](/docs/ja/model-config#default-model-behavior) を設定して、Default オプションが Claude Code の組み込みデフォルトではなく `availableModels` 内のモデルに解決されるようにします。なしでは、Default は選択可能なままであり、そのモデルが許可されていない場合、リクエスト時に拒否されます。
* **テレメトリ宛先**：[テレメトリ転送](/docs/ja/claude-apps-gateway-config#telemetry)が設定されている場合、OTLP エクスポートエンドポイントはゲートウェイにピン留めされ、ゲートウェイがプッシュした設定はローカルに設定された `OTEL_*` 変数をオーバーライドします。
* **認証情報**：ゲートウェイトークンはセッションの唯一の認証情報です。`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_API_KEY`、`apiKeyHelper`、および以前の claude.ai ログインはサインイン中は無視されるため、開発者は最初に claude.ai からログアウトする必要はありません。
* **管理設定**：ロックされたキーはローカルでオーバーライドできません。CLI はポリシーを起動時と毎時間のポーリングで適用します。
* **起動**：サインイン済みセッションは、ゲートウェイが到達不可能な場合、約 10 秒後に起動時にエラーで終了し、設定なしで起動するのではなく。
* **プロビジョニング解除**：ユーザーが IdP で無効化されたセッションは、次の更新が失敗したときに `ttl_hours` 内に期限切れになります。

<h3 id="what-the-organization-can-see">
  組織が見ることができるもの
</h3>

使用状況テレメトリは開発者のアイデンティティ、トークン数、モデル、およびレイテンシを組織のコレクターに伝えます。ゲートウェイはプロンプトまたは完了コンテンツをログまたは保存しません。ログやトレースなどのより豊富なテレメトリが収集されるかどうか。コマンドやファイルパスを含む可能性があるのは、組織の[宛先ごとの選択](/docs/ja/claude-apps-gateway-config#telemetry)です。

<h2 id="availability-and-limitations">
  可用性と制限
</h2>

表は、開発者がゲートウェイを通じて接続するときに機能する Claude Code 機能と、ゲートウェイサーバー自体がサポートするものをカバーしています。何かがサポートされていない場合、Notes 列は代替案を提供します。

ゲートウェイは、CLI がすべてのアップストリームに送信する [`anthropic-beta`](https://platform.claude.com/docs/ja/api/beta-headers) 値を配信するため、オペレーターはベータ許可リストを維持しません。Amazon Bedrock の場合、ヘッダーを無視し、ゲートウェイは値をリクエストボディの `anthropic_beta` フィールドに移動します。他のアップストリームは送信されたままヘッダーを受け取ります。CLI のゲートウェイセッションベータセットは、ファーストパーティのみのベータと拡張キャッシュ TTL ベータを省略します。これが以下の行がサポートされていないと表示される理由です。

| 機能                                                                                                    | ステータス      | 注記                                                                                                                                                                                                                                                                                                                                               |
| ----------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 推論転送（Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、Microsoft Foundry、Anthropic） | 利用可能       | アップストリームごとのモデル変換とフェイルオーバー付き。Amazon Bedrock アップストリームは `bedrock-runtime` エンドポイントと AWS デフォルト認証情報チェーンを使用します。Amazon Bedrock [Mantle エンドポイント](/docs/ja/amazon-bedrock#use-the-mantle-endpoint)はサポートされたアップストリームではありません。[Claude Platform on AWS アップストリーム](/docs/ja/claude-apps-gateway-config#claude-platform-on-aws)には、ゲートウェイサーバー上の Claude Code v2.1.198 以降が必要です。 |
| IdP グループによるモデルアクセスと管理設定                                                                               | 利用可能       | モデルアクセスはサーバー側で強制されます。管理設定は IdP グループごとに配信され、CLI によって[管理設定層](/docs/ja/settings#settings-precedence)で適用されます                                                                                                                                                                                                                                              |
| テレメトリファンアウト（OTLP/HTTP）                                                                                | 利用可能       | エクスポートごとにアイデンティティスタンプ付き。protobuf と JSON エンコーディングの両方                                                                                                                                                                                                                                                                                              |
| OIDC ID プロバイダー                                                                                        | 利用可能       | 任意の OIDC 準拠の IdP。ゲートウェイは標準 OIDC ディスカバリーと認可コードフローを実行します。[ID プロバイダーセットアップ](/docs/ja/claude-apps-gateway-deploy#identity-provider-setup)を参照して、IdP ごとの設定を確認してください                                                                                                                                                                                         |
| ユーザーごとおよびグループごとの支出制限                                                                                  | 利用可能       | [支出制限](/docs/ja/claude-apps-gateway-spend-limits)を参照してください                                                                                                                                                                                                                                                                                            |
| サーバー側ウェブ検索                                                                                            | 利用不可       | CLI はゲートウェイがルーティングするアップストリームプロバイダーを見ることができないため、ウェブ検索サポートを検証できず、ゲートウェイセッションで WebSearch を無効化します                                                                                                                                                                                                                                                    |
| 標準プロンプトキャッシング                                                                                         | 利用可能       | `cache_control` ブレークポイントはすべてのアップストリームに転送されます                                                                                                                                                                                                                                                                                                     |
| 1 時間キャッシュ TTL                                                                                         | 利用不可       | CLI はゲートウェイセッションで拡張キャッシュ TTL ベータを省略します。ゲートウェイがルーティングできるすべてのアップストリームが 1 時間 TTL をサポートしているわけではないため、ゲートウェイを通じたプロンプトキャッシングは 5 分 TTL を使用します。上記のベータヘッダーノートを参照してください                                                                                                                                                                                     |
| オートモード                                                                                                | 利用可能       | [サードパーティプロバイダールール](/docs/ja/permission-modes#enable-auto-mode-on-bedrock-agent-platform-or-foundry)に従います。サードパーティプロバイダーで適格なモデルのみがそれを使用できます。v2.1.207 より前では、ゲートウェイセッションのオートモードは `CLAUDE_CODE_ENABLE_AUTO_MODE=1` を設定する必要があり、管理ポリシー `env` ブロック経由で配信可能でした                                                                                                  |
| グローバルキャッシュスコープとトークン効率的なツールなどのファーストパーティのみの最適化                                                          | 利用不可       | CLI はゲートウェイセッションでそれらを有効化しません。上記のベータヘッダーノートを参照してください                                                                                                                                                                                                                                                                                              |
| OTLP/gRPC                                                                                             | サポートされていない | HTTP 経由の OTLP のみ                                                                                                                                                                                                                                                                                                                                 |
| SAML、LDAP、およびその他の非 OIDC 認証                                                                            | サポートされていない | OIDC のみ。必要に応じて OIDC ブリッジで前面に配置します                                                                                                                                                                                                                                                                                                                |
| マルチテナント（複数の OIDC 発行者）                                                                                 | サポートされていない | ゲートウェイごとに 1 つの発行者。個別インスタンスを実行します                                                                                                                                                                                                                                                                                                                 |
| Windows サーバー                                                                                          | サポートされていない | Linux にデプロイします。ローカル開発用の macOS のみ                                                                                                                                                                                                                                                                                                                 |
| Helm チャート                                                                                             | 利用不可       | ゲートウェイは標準ステートレス Deployment として実行されます。[デプロイメントガイド](/docs/ja/claude-apps-gateway-deploy#kubernetes)を参照してください                                                                                                                                                                                                                                            |
| 管理 UI                                                                                                 | 利用不可       | 設定は YAML ファイルです。変更するには再デプロイします                                                                                                                                                                                                                                                                                                                   |

<h2 id="next-steps">
  次のステップ
</h2>

クイックスタートは Docker Compose で実行されている最小設定を残します。さらに進めるには。

* グループごとの RBAC、マルチアップストリームフェイルオーバー、またはテレメトリ宛先を追加するなど、最小設定を超えて `gateway.yaml` を拡張します。[設定リファレンス](/docs/ja/claude-apps-gateway-config)はすべてのオプションをカバーしています。
* Compose から Kubernetes または Cloud Run での本番デプロイメントに移動し、IdP を適切に設定し、セキュリティモデルを確認します。[デプロイメントおよび運用ガイド](/docs/ja/claude-apps-gateway-deploy)は、IdP ごとのセットアップ、コンテナイメージ要件、ヘルスプローブ、およびトラブルシューティングをカバーしています。
* 個々の開発者またはグループに支出キャップを設定して、暴走ワークロードがコミットメント全体を消費できないようにします。[支出制限](/docs/ja/claude-apps-gateway-spend-limits)は管理 API と強制がどのように機能するかをカバーしています。
* Google Cloud での完全な実装例については、Cloud Run、Cloud SQL、Secret Manager を使用して、[Google Cloud にデプロイ](/docs/ja/claude-apps-gateway-on-gcp)を参照してください。
