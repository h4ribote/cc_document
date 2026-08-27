> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Google Cloud に Claude apps gateway をデプロイする

> Google Cloud で Claude apps gateway を実行する実装例：Cloud Run または GKE、Cloud SQL for PostgreSQL、Secret Manager、および Agent Platform への service account 認証。

<Note>
  このページでは、Google Cloud で Claude apps gateway を実行する 1 つの方法を説明します。この設定は、サポートされている本番環境デプロイメントではなく、カスタマー管理インフラストラクチャの実装例です。各部分がどのように組み合わさるかを確認してから、自分の環境に適応させてください。プラットフォーム非依存の要件については、[デプロイメントガイド](/docs/ja/claude-apps-gateway-deploy)を参照してください。
</Note>

この例では、Google Cloud の Agent Platform をモデルアップストリームとして使用し、Cloud Run または GKE をコンピュートに使用して、Google Cloud に Claude apps gateway をプロビジョニングします。Google Workspace は例の ID プロバイダー（IdP）ですが、OpenID Connect（OIDC）準拠の任意の IdP が機能します。`oidc` ブロックのみが変わります。IdP ごとの詳細については、[ID プロバイダーのセットアップ](/docs/ja/claude-apps-gateway-deploy#identity-provider-setup)を参照してください。

<h2 id="what-you’ll-build">
  構築内容
</h2>

<Frame>
  <img src="https://mintcdn.com/claude-code/-uq-4JE0W_JO5Er5/images/claude-gateway-gcp-architecture.svg?fit=max&auto=format&n=-uq-4JE0W_JO5Er5&q=85&s=cb705151c69128ac0da235852d5600ab" alt="Google Cloud 上の Claude apps gateway の図：Claude Code クライアントは HTTPS 経由でゲートウェイ（Cloud Run または GKE）に接続し、ゲートウェイは VPC 内でプライベート IP Cloud SQL データベースと並行して実行され、セッション状態を保存します。ゲートウェイは OIDC 経由で Google Workspace に対してユーザーをサインインさせ、Secret Manager から設定とシークレットを読み取り、モデルリクエストを Agent Platform に転送し、デプロイ時に Artifact Registry からイメージをプルします。" width="760" height="400" data-path="images/claude-gateway-gcp-architecture.svg" />
</Frame>

リファレンス設定は以下をプロビジョニングします：

* ゲートウェイコンテナを実行する **Cloud Run** サービスまたは **GKE** Deployment
* ゲートウェイイメージ用の **Artifact Registry** リポジトリ
* ゲートウェイの[ストア](/docs/ja/claude-apps-gateway-config#store)用のプライベート IP のみの **Cloud SQL for PostgreSQL** インスタンス
* `gateway.yaml`、JWT 署名キー、OIDC クライアントシークレット、および Postgres URL 用の **Secret Manager** シークレット
* `roles/aiplatform.user` を持つ **Service account**、Cloud Run に直接アタッチされるか、GKE 上で Workload Identity 経由でバインドされます
* Cloud Run 上の **Internal Application Load Balancer**、または GKE 上のクラス `gce-internal` の内部 **GKE Ingress**（HTTPS 用）

<h2 id="prerequisites">
  前提条件
</h2>

* 課金が有効になっている GCP プロジェクトと、上記のリソースを作成する権限
* `gcloud auth login` で認証された `gcloud` CLI、およびローカルにインストールされた Docker
* GKE トラック用：`kubectl`、および以下のウォークスルーで作成された VPC 上の GKE クラスタ
* Model Garden で必要な Claude モデルへのアクセス、それらを公開している地域内
* リダイレクト URI が `https://<gateway-host>/oauth/callback` の Google Workspace OAuth 2.0 ウェブアプリケーションクライアント。[ID プロバイダーのセットアップ](/docs/ja/claude-apps-gateway-deploy#identity-provider-setup)を参照してください
* ゲートウェイ用の TLS ホスト名。通常はロードバランサーを指すプライベート DNS 名

プロジェクトと地域を一度設定します：

```bash theme={null}
export PROJECT_ID=<your-project>
export REGION=us-east5   # a region where the Claude models you need are published in Model Garden
gcloud config set project "$PROJECT_ID"
```

<h2 id="deploy-the-gateway">
  ゲートウェイをデプロイする
</h2>

以下のステップは、`gcloud` コマンドで完全なデプロイメントをプロビジョニングします。

<Steps>
  <Step title="API を有効にする">
    ウォークスルーで使用するサービス API を有効にします：

    ```bash theme={null}
    gcloud services enable \
      aiplatform.googleapis.com \
      artifactregistry.googleapis.com \
      sqladmin.googleapis.com \
      secretmanager.googleapis.com \
      iamcredentials.googleapis.com \
      iam.googleapis.com \
      compute.googleapis.com \
      servicenetworking.googleapis.com \
      run.googleapis.com \
      container.googleapis.com
    ```

    必要な API はデプロイメントパスによって異なります：

    * `compute` および `servicenetworking`：プライベート IP Cloud SQL パス用
    * `run`：Cloud Run のみ
    * `container`：GKE のみ
  </Step>

  <Step title="Service account を作成して IAM を付与する">
    ゲートウェイは Agent Platform を呼び出す権限を持つ専用 service account として実行されます。VPC 経由で Cloud SQL に到達するパスワードユーザーなので、Cloud SQL IAM ロールは不要です：

    ```bash theme={null}
    gcloud iam service-accounts create claude-gateway --display-name="Claude apps gateway"
    SA="claude-gateway@${PROJECT_ID}.iam.gserviceaccount.com"

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:${SA}" --role="roles/aiplatform.user" --condition=None
    ```

    次に、Model Garden でプロジェクト用に Claude モデルを有効にします。モデルは特定の地域に公開されるため、各モデルカードを確認してください。
  </Step>

  <Step title="イメージをビルドして Artifact Registry にプッシュする">
    [コンテナイメージ要件](/docs/ja/claude-apps-gateway-deploy#container-image)に従ってイメージをビルドし、`linux-x64` glibc バイナリを使用してプッシュします：

    ```bash theme={null}
    gcloud artifacts repositories create claude-gateway \
      --repository-format=docker --location="$REGION"
    gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

    # Cloud Run requires linux/amd64. --provenance=false avoids a buildx OCI
    # image index that Cloud Run rejects.
    docker build --platform=linux/amd64 --provenance=false \
      -t "${REGION}-docker.pkg.dev/${PROJECT_ID}/claude-gateway/gateway:<version>" .
    docker push "${REGION}-docker.pkg.dev/${PROJECT_ID}/claude-gateway/gateway:<version>"
    ```
  </Step>

  <Step title="Cloud SQL for PostgreSQL をプロビジョニングする">
    Private Services Access 経由で VPC 上にインスタンスを作成し、パブリック IP がないようにします。これは `constraints/sql.restrictPublicIp` が適用されているプロジェクトも満たします：

    ```bash theme={null}
    VPC=cc-gateway-vpc
    gcloud compute networks create "$VPC" --subnet-mode=custom
    gcloud compute networks subnets create cc-gateway-subnet \
      --network="$VPC" --region="$REGION" --range=10.0.0.0/24

    # Private Services Access: one-time per VPC
    gcloud compute addresses create "google-managed-services-${VPC}" \
      --global --purpose=VPC_PEERING --prefix-length=16 --network="$VPC"
    gcloud services vpc-peerings connect \
      --service=servicenetworking.googleapis.com \
      --ranges="google-managed-services-${VPC}" --network="$VPC"

    gcloud sql instances create claude-gateway-db \
      --database-version=POSTGRES_16 --tier=db-g1-small --region="$REGION" \
      --network="projects/${PROJECT_ID}/global/networks/${VPC}" --no-assign-ip
    gcloud sql databases create claude_gateway --instance=claude-gateway-db
    PGPASS="$(openssl rand -hex 24)"
    gcloud sql users create gateway --instance=claude-gateway-db --password="$PGPASS"

    PRIVATE_IP="$(gcloud sql instances describe claude-gateway-db \
      --format='value(ipAddresses[0].ipAddress)')"
    GATEWAY_POSTGRES_URL="postgres://gateway:${PGPASS}@${PRIVATE_IP}:5432/claude_gateway?sslmode=require"
    ```

    Cloud Run または GKE ランタイムは、この VPC 上にあるか、この VPC にルーティングされている必要があります。
  </Step>

  <Step title="gateway.yaml を書き込む">
    `upstreams` ブロックは `auth: {}` で Agent Platform を指すため、ゲートウェイはランタイム service account からの Application Default Credentials 経由で認証します。すべてのフィールドについては、[設定リファレンス](/docs/ja/claude-apps-gateway-config)を参照してください。

    2 つの `listen` フィールドはゲートウェイの前にあるものに依存します：

    * `public_url`：Cloud Run または GKE Ingress の背後で必須。ゲートウェイは IdP `redirect_uri` と検出ドキュメントをこの値からのみビルドし、`X-Forwarded-*` ヘッダーからは決してビルドしません。
    * `trusted_proxies`：フロントエンドのソース範囲。ゲートウェイは TCP ピアがこのリストにある場合にのみ `X-Forwarded-For` を尊重し、信頼できるホップを超えてチェーンを歩くため、IP ごとのサインイン レート制限と監査イベントはロードバランサーの IP ではなく開発者 IP を記録します。

    フロントエンドに合わせて `trusted_proxies` を設定します。クラス `gce` の外部 GKE Ingress はリストされていません。パブリック転送ルールアドレスをプロビジョニングし、`/login` [プライベートネットワークチェック](/docs/ja/claude-apps-gateway#prerequisites)がこれを拒否します。

    | フロントエンド                                          | `trusted_proxies`                     |
    | ------------------------------------------------ | ------------------------------------- |
    | ロードバランサーなしで直接到達する Cloud Run                      | `[169.254.0.0/16]`                    |
    | Cloud Run の前の Internal Application Load Balancer | `169.254.0.0/16` プラスプロキシのみサブネットの CIDR |
    | GKE 内部 Ingress、クラス `gce-internal`                | プロキシのみサブネットの CIDR                     |

    以下の例は、Cloud Run の前の内部ロードバランサー値を使用します。

    ```yaml gateway.yaml theme={null}
    listen:
      host: 0.0.0.0
      port: 8080
      public_url: https://claude-gateway.internal.example.com
      trusted_proxies: [169.254.0.0/16, <your-proxy-only-subnet-cidr>]

    oidc:
      issuer: https://accounts.google.com
      client_id: <your-oauth-client-id>
      client_secret: ${OIDC_CLIENT_SECRET}           # GKE: ${file:/secrets/oidc-client-secret}
      allowed_email_domains: [example.com]
      # Google ignores offline_access; these yield refresh tokens:
      scopes: [openid, profile, email]
      extra_auth_params: { access_type: offline, prompt: consent }

    session:
      jwt_secret: ${GATEWAY_JWT_SECRET}              # GKE: ${file:/secrets/jwt-secret}

    store:
      postgres_url: ${GATEWAY_POSTGRES_URL}          # GKE: ${file:/secrets/postgres-url}

    upstreams:
      - provider: vertex
        region: <your-region>                        # must match $REGION
        project_id: <your-project>
        auth: {} # ADC via the runtime service account
    ```

    <Note>
      Google id\_tokens は `groups` クレームを含みません。Google Workspace を IdP として [`managed.policies`](/docs/ja/claude-apps-gateway-config#managed) でグループベースのポリシーを使用するには、[`oidc.google_groups`](/docs/ja/claude-apps-gateway-config#oidc) を設定します。これは Admin SDK Directory API を使用してドメイン全体の委任を持つ service account を使用して各ユーザーのグループを検索します。これなしで、代わりに `email_domain` で一致させます。
    </Note>
  </Step>

  <Step title="Secret Manager にシークレットを保存する">
    4 つのシークレットを作成し、`claude-gateway` service account に `roles/secretmanager.secretAccessor` を付与します：

    | シークレット                       | ソース                                       |
    | ---------------------------- | ----------------------------------------- |
    | `gateway-jwt-secret`         | `openssl rand -base64 32`                 |
    | `gateway-oidc-client-secret` | Google Cloud Console → OAuth クライアント       |
    | `gateway-postgres-url`       | Cloud SQL ステップからの `$GATEWAY_POSTGRES_URL` |
    | `gateway-config`             | 前のステップからの完全な `gateway.yaml`               |

    シークレットがコンテナに到達する方法はトラックによって異なります：

    * GKE では Secret Manager CSI ドライバー経由で `/secrets` にマウントされ、`gateway.yaml` は `${file:/secrets/...}` を参照します。
    * Cloud Run では複数のシークレットを 1 つのディレクトリにマウントできないため、`gateway.yaml` はファイルとしてマウントされ、他の 3 つは環境変数として注入されるため、`gateway.yaml` は代わりに `${GATEWAY_JWT_SECRET}`、`${OIDC_CLIENT_SECRET}`、および `${GATEWAY_POSTGRES_URL}` を参照します。
  </Step>

  <Step title="デプロイする">
    <Tabs>
      <Tab title="Cloud Run">
        以下のコマンドは内部ロードバランサーの背後で本番環境用にデプロイします。

        ```bash theme={null}
        gcloud run deploy claude-gateway \
          --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/claude-gateway/gateway:<version>" \
          --region="$REGION" \
          --service-account="claude-gateway@${PROJECT_ID}.iam.gserviceaccount.com" \
          --min-instances=1 \
          --timeout=3600 \
          --ingress=internal-and-cloud-load-balancing \
          --network="$VPC" --subnet=cc-gateway-subnet --vpc-egress=private-ranges-only \
          --set-secrets=/etc/claude/gateway.yaml=gateway-config:latest,GATEWAY_JWT_SECRET=gateway-jwt-secret:latest,OIDC_CLIENT_SECRET=gateway-oidc-client-secret:latest,GATEWAY_POSTGRES_URL=gateway-postgres-url:latest \
          --no-invoker-iam-check
        ```

        Direct VPC egress（`--network`、`--subnet`、および `--vpc-egress=private-ranges-only` 経由）により、サービスは Cloud SQL プライベート IP に直接到達できます。Agent Platform エンドポイントおよび `accounts.google.com` への公開エグレスは VPC を通さずにインターネットに直接移動するため、Cloud NAT は不要です。

        invoker IAM チェックはオープンまたは無効にする必要があります。ゲートウェイは独自の OIDC を実行し、そのクライアントは GCP トークンを持たないため、Cloud Run の invoker チェックは認証されていないリクエストを許可する必要があります。ゲートウェイの OIDC サインインは、コンテナに到達すると `allowed_email_domains` でゲートウェイがどのドメインがサインインできるかを制御して、リクエストを認証します。

        2 つのフラグが認証されていないリクエストを許可します：

        * `--no-invoker-iam-check`：管理する `allUsers` バインディングなしでチェックを無効にし、Domain Restricted Sharing の下で機能します
        * `--allow-unauthenticated`：`allUsers` に `run.invoker` ロールを付与します。組織が `--no-invoker-iam-check` を許可しない場合はこれを使用します

        `--ingress` 経由のイングレス制限は invoker チェックから独立した別のレイヤーです。サービスを企業ネットワークに制限するために設定したままにしておきます。

        デフォルトでは、Cloud Run `*.run.app` URL はパブリックアドレスに解決され、`/login` [プライベートネットワークチェック](/docs/ja/claude-apps-gateway#prerequisites)がこれを拒否します。2 つのトポロジーは開発者にプライベートに解決可能なホスト名を提供し、Cloud Run はどちらもプロビジョニングしません：

        * **Internal Application Load Balancer**、上記のデプロイコマンドが想定するトポロジー：`--ingress=internal-and-cloud-load-balancing` でデプロイし、サービスの前に内部 Application Load Balancer をプロビジョニングして内部 DNS 名と証明書を使用し、`listen.public_url` をそのホスト名に設定します。
        * **ロードバランサーなしの内部のみイングレス**：`--ingress=internal` でデプロイし、`listen.public_url` を `*.run.app` URL（以下の[リファレンスアセット](#terraform-reference)のデフォルト）のままにします。`*.run.app` がプライベートに解決するには、ネットワークチームが既に Google API 用の Private Service Connect エンドポイント、`*.run.app` をそれに解決する Cloud DNS プライベートゾーン、およびそのエンドポイントへのオンプレミスルーティングを運用している必要があります。

        Google の [Cloud Run のプライベートネットワークガイド](https://cloud.google.com/run/docs/securing/private-networking)は、両方のオプションが必要とするインフラストラクチャをカバーしています。ゲートウェイがプライベートホスト名で提供されたら、サインインを確認します。それまで、Cloud Run のログからコンテナがブートしたことを確認します。

        最初のサインイン前に OAuth クライアントの認可リダイレクト URI を `<public_url>/oauth/callback` に更新します。`public_url` を変更した後に再デプロイします。ゲートウェイはその設定からのみパブリックオリジンをビルドし、`X-Forwarded-Host` および `X-Forwarded-Proto` を無視するためです。`X-Forwarded-For` は `listen.trusted_proxies` が設定されている場合にのみクライアント IP に対して尊重されます。
      </Tab>

      <Tab title="GKE">
        クラスタは Cloud SQL ステップで作成された `$VPC` 上にある必要があります。ポッドがデータベースのプライベート IP に到達できるようにするためです。VPC ピアリングだけでは機能しません。Cloud SQL プライベート IP 自体がピアリングされたネットワークであり、ピアリングは非推移的だからです。その VPC 上に新しいクラスタを作成するには、`gcloud container clusters create` に `--network="$VPC" --subnetwork=cc-gateway-subnet` を渡します。

        クラスタとそのノードプールで Workload Identity を有効にし、Google service account を Kubernetes service account にバインドして、ポッドがその認証情報を継承するようにします：

        ```bash theme={null}
        gcloud container clusters update <cluster> --region="$REGION" \
          --workload-pool="${PROJECT_ID}.svc.id.goog"
        # On a Standard cluster, existing node pools also need GKE_METADATA;
        # Autopilot enables this by default.
        gcloud container node-pools update <pool> --cluster=<cluster> \
          --region="$REGION" --workload-metadata=GKE_METADATA

        kubectl create namespace claude-gateway
        kubectl create serviceaccount gateway -n claude-gateway

        gcloud iam service-accounts add-iam-policy-binding \
          "claude-gateway@${PROJECT_ID}.iam.gserviceaccount.com" \
          --role roles/iam.workloadIdentityUser \
          --member "serviceAccount:${PROJECT_ID}.svc.id.goog[claude-gateway/gateway]"

        kubectl annotate serviceaccount gateway -n claude-gateway \
          iam.gke.io/gcp-service-account="claude-gateway@${PROJECT_ID}.iam.gserviceaccount.com"
        ```

        [Kubernetes デプロイメント](/docs/ja/claude-apps-gateway-deploy#kubernetes)で説明されているように、ゲートウェイを標準 Deployment、Service、および内部 Ingress（クラス `gce-internal`）としてデプロイします。以下を使用します：

        * `serviceAccountName: gateway`
        * Secret Manager CSI ドライバーが `/secrets` にシークレットをマウント
        * readiness probe が `GET /readyz` を指す

        ゲートウェイ Service に BackendConfig をアタッチして、`timeoutSec` を上げます。GKE Ingress の背後のロードバランサーバックエンドサービスはデフォルトで 30 秒のタイムアウトで、長いストリーミング応答を切断します。

        Workload Identity クラスタで `169.254.169.254` をブロックするエグレス NetworkPolicy を適用しないでください。ポッドは認証情報のためにメタデータサーバーに到達する必要があります。ゲートウェイの組み込み [SSRF ガード](/docs/ja/claude-apps-gateway-deploy#threat-model-summary)がそこでの防御です。

        ゲートウェイはメタデータエンドポイントに到達可能であることを示すブート警告をログに記録し、エグレス NetworkPolicy を適用することを提案します。Workload Identity の下では、ポッドがエンドポイントを必要とするため、その警告は予想されます。
      </Tab>
    </Tabs>
  </Step>

  <Step title="ゲートウェイ URL を開発者マシンにプッシュする">
    ゲートウェイは実行されていますが、開発者は `/login` からゲートウェイ URL がマシンに配置されるまでそれに到達できません。MDM 経由で各デバイスにデプロイする[管理設定ファイル](/docs/ja/claude-apps-gateway#set-the-gateway-url)で `forceLoginMethod` および `forceLoginGatewayUrl` を設定します。開発者が手動で選択できるログインピッカーのゲートウェイオプションはありません。
  </Step>
</Steps>

<h2 id="terraform-reference">
  Terraform リファレンス
</h2>

[リファレンスデプロイメントアセット](https://github.com/anthropics/claude-code/tree/main/examples/gateway/gcp)はこのページの Cloud Run トラックを自動化します。設定とイメージアセットは両方のトラックに適用されます：

* `setup.sh`：API の有効化から最初のデプロイまで、完全な Cloud Run パスを歩く冪等な `gcloud` プロビジョナー
* `terraform/`：インフラストラクチャアズコードとしての同じデプロイメント。greenfield デプロイ用：Artifact Registry リポジトリを作成するための対象適用、次にイメージをビルドしてプッシュ、次に完全適用
* `gateway.yaml.example` および distroless ランタイムイメージ用の `Dockerfile`

アーティファクトは Cloud Run イングレスをデフォルトで `internal` にするため、ロードバランサーは不要です。このページの本番環境の背後の ALB デプロイメントに一致させるには、`INGRESS=internal-and-cloud-load-balancing` で `setup.sh` を実行するか、Terraform 変数 `ingress` を `INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER` に設定します。アーティファクトは invoker レイヤーもデフォルトで `allUsers` `run.invoker` 付与にするため、このページのウォークスルーの `--no-invoker-iam-check` ではなく逆です。どちらでも機能し、選択は組織のポリシー制約に依存します。

アセットは実装例として提供されており、サポートされている本番環境アーティファクトではありません。環境に合わせてレビューして適応させてください。

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

ゲートウェイブートとログインエラーについては、プラットフォーム非依存の[トラブルシューティングテーブル](/docs/ja/claude-apps-gateway-deploy#troubleshooting)を参照してください。以下のエントリは Google Cloud に固有です。

| 症状                                                                                  | 原因                                                                                     | 修正                                                                                                                                                                                          |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cloud Run がコンテナに到達する前に `403 Forbidden` を返す                                          | invoker IAM チェックがまだ有効                                                                  | `--no-invoker-iam-check` でデプロイするか、`--allow-unauthenticated` で `allUsers` に `run.invoker` ロールを付与します                                                                                          |
| `--no-invoker-iam-check` が `invoker_iam_disabled is not currently available` で拒否される | `constraints/run.managed.requireInvokerIam` でブロック                                      | `--allow-unauthenticated` を使用します。`constraints/iam.allowedPolicyMemberDomains` 経由の Domain Restricted Sharing もそれをブロックする場合は、GKE トラックを使用します。これはネットワークレイヤーでゲートウェイを公開し、`allUsers` バインディングはありません。 |
| デプロイ時に `Container manifest type … must support amd64/linux`                         | イメージが非 amd64 ホストでビルドされたか、buildx が OCI イメージインデックスを発行した                                  | `--platform=linux/amd64 --provenance=false` でビルドします                                                                                                                                         |
| ゲートウェイブートが Cloud Run で Postgres 接続タイムアウトエラーで終了                                      | Service が VPC にアタッチされていないか、Cloud SQL がその VPC にプライベート IP がない。ストアは 5 秒後に待機を停止します         | Direct VPC egress 用に `--network` および `--subnet` でデプロイし、Cloud SQL インスタンスを `--no-assign-ip` および `--network` で同じ VPC を指すように作成します                                                               |
| Agent Platform リクエストが `403 PERMISSION_DENIED` を返す                                   | ランタイムが `claude-gateway` service account を使用していないか、モデルが Model Garden でプロジェクト用に有効になっていない | Cloud Run で `--service-account` を設定するか、GKE で Workload Identity をバインドし、各 Claude モデルを Model Garden でターゲット地域用に有効にします                                                                           |
| ストリーミング応答が固定期間後に切断される                                                               | フロントエンドリクエストタイムアウト：GKE Ingress の背後のロードバランサーバックエンドサービスはデフォルトで 30 秒、Cloud Run は 300 秒    | GKE で `timeoutSec` を上げた BackendConfig をアタッチするか、Cloud Run で `--timeout=3600` でデプロイします                                                                                                        |

<h2 id="next-steps">
  次のステップ
</h2>

* [設定リファレンス](/docs/ja/claude-apps-gateway-config)：すべての `gateway.yaml` オプション（`managed.policies` および `telemetry` を含む）
* [デプロイメントと運用](/docs/ja/claude-apps-gateway-deploy)：IdP セットアップ、ヘルスチェック、JWT シークレットローテーション、アップグレード、およびセキュリティモデル
* [Claude apps gateway 概要](/docs/ja/claude-apps-gateway)：クイックスタートと開発者の接続
