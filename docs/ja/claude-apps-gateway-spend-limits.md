> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude apps gateway の支出制限

> Claude apps gateway を通じて各開発者の支出を日単位、週単位、または月単位で制限します。Admin API で制限を設定すると、gateway はすべてのリクエストでそれらを実行します。

支出制限は、各開発者が指定された日、週、または月の間に [Claude apps gateway](/docs/ja/claude-apps-gateway) を通じて支出できる金額の上限を設定します。開発者が上限に達すると、gateway は次のリクエストで `429` を返し、期間がリセットされるか管理者が上限を引き上げるまで、その開発者をブロックします。支出制限を使用して、各開発者、グループ、または組織全体に対して、全員が共有する認証情報の上限を設定できます。

Claude apps gateway は、すべての推論を 1 つの共有アップストリーム認証情報を通じて転送するため、プロバイダーの請求書はすべてをその認証情報に属するものとして記録し、個々の開発者には記録しません。開発者ごとの制限がない場合、1 つの暴走したエージェント フリートが組織全体のコミットメントを使い果たす可能性があります。支出制限は、その共有請求書の上に gateway の開発者ごとのビューとサーキット ブレーカーです。

<h2 id="set-a-cap">
  上限を設定する
</h2>

`gateway.yaml` で [`admin:`](/docs/ja/claude-apps-gateway-config#admin) ブロックが設定されている場合、gateway は `/v1/organizations/spend_limits` で管理 API を提供し、すべての推論リクエストで上限をリアルタイムに適用します。上限自体は `gateway.yaml` ではなく、その API を通じて設定されます。各 `POST /v1/organizations/spend_limits` リクエストは `{scope, amount, period}` から 1 つの上限を作成または置き換えます。API は Anthropic の公開 [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api) 支出制限エンドポイントのワイヤー形状をミラーリングするため、そのコントラクトに対して記述された HTTP クライアントは、ベース URL を変更することで gateway をターゲットにできます。

このリクエストは、すべての開発者に対して月額 500 ドルの組織全体のデフォルトを設定します。

```bash theme={null}
curl -sS https://claude-gateway.internal.example.com/v1/organizations/spend_limits \
  -H "x-api-key: $GATEWAY_ADMIN_WRITE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"scope": {"type": "organization"}, "amount": "50000", "period": "monthly"}'
```

このリクエストは、`contractors` グループの各メンバーに対して、より厳しい 1 日あたり 100 ドルの上限を追加します。

```bash theme={null}
curl -sS https://claude-gateway.internal.example.com/v1/organizations/spend_limits \
  -H "x-api-key: $GATEWAY_ADMIN_WRITE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"scope": {"type": "rbac_group", "rbac_group_id": "contractors"}, "amount": "10000", "period": "daily"}'
```

| フィールド        | 値                                  | 説明                                                                                                                                                                                                                                                                                                                    |
| ------------ | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scope.type` | `user`、`rbac_group`、`organization` | `user` は OpenID Connect（OIDC）`sub` で 1 人の開発者をターゲットにします。これは ID プロバイダーが割り当てる安定したユーザー ID です。`scope.user_id` として渡します。`rbac_group` は [IdP グループ](/docs/ja/claude-apps-gateway-config#managed) を名前でターゲットにします。`scope.rbac_group_id` として渡します。`organization` は組織全体のデフォルトです。gateway は 3 つすべてを受け入れます。Anthropic の公開 `POST` は現在ユーザーのみです。 |
| `amount`     | USD セントの整数文字列、または `null`           | `null` は無制限です。`"0"` はゼロ上限で、すべてのリクエストをブロックします。                                                                                                                                                                                                                                                                         |
| `period`     | `daily`、`weekly`、`monthly`         | スコープは期間ごとに 1 つの上限を保持でき、各々は独立して適用されます。開発者は、いずれかの上限を超えている場合、ブロックされます。                                                                                                                                                                                                                                                   |

グループまたは組織の上限は、各メンバーが継承する座席ごとのデフォルトであり、共有プールではありません。期間ごとに、開発者の有効な上限は次の順序で解決されます。ユーザーごとのオーバーライド、次に最も制限的なグループ上限、次に組織のデフォルト、次に無制限。[`admin.group_limit_mode: max`](/docs/ja/claude-apps-gateway-config#admin) は、複数グループのタイブレークを最も制限的ではないものに反転させます。

<h3 id="authenticate-to-the-admin-api">
  管理 API に認証する
</h3>

次のいずれかを送信します。

* [`admin.write_keys`](/docs/ja/claude-apps-gateway-config#admin) のキーと一致する `x-api-key` ヘッダー（フルアクセス）、または `admin.read_keys`（`GET` のみアクセス）。各キーは監査ログに `admin-key:<id>` として表示される `id` を持つため、Terraform、CI、および各自動化に独自のキーを付与します。
* `groups` クレームが [`admin.admin_groups`](/docs/ja/claude-apps-gateway-config#admin) のいずれかを含む gateway ベアラートークン。これはフルアクセスで、`oidc:<sub>` として監査されるため、人間の管理者には推奨されます。

<h2 id="how-enforcement-works">
  適用方法
</h2>

各 `/v1/messages` リクエストで、gateway は開発者の上限と期間から現在までの支出を 1 つの Postgres クエリで解決します。いずれかの上限を超えている場合、リクエストは `429` を返し、`error.type: billing_error` と `x-should-retry: false` ヘッダーが付きます。メッセージは `spend limit reached` で、その後に [`admin.blocked_message`](/docs/ja/claude-apps-gateway-config#admin) が設定されている場合はそれが続きます。

`/v1/messages/count_tokens` は除外されます。トークンカウントは無料なので、上限状態に関係なく実行されます。

各レスポンスの後、使用量メーターはレスポンスからトークンカウントを読み取り、クライアントにストリーミングされ、USD リスト価格で価格設定され、3 つの期間バケットすべての Postgres カウンターをインクリメントします。メーターはストリーム上の単一リーダーなので、クライアントのバイトは変更されず、メーリング障害はレスポンスを破壊しません。

支出制限は USD リスト価格のトークンカウントから支出を推定します。これはサーキットブレーカーであり、請求書ではありません。権限のある請求については、Anthropic Usage & Cost Admin API、Amazon Bedrock の呼び出しログ、または Google Cloud の Cloud Monitoring など、プロバイダー独自の使用状況レポートに対して調整してください。

価格設定は Claude Code CLI が独自のコスト表示に使用するのと同じテーブルを使用し、Anthropic、Amazon Bedrock（`us.anthropic.…-v1:0`）、Google Cloud の Agent Platform（`claude-…@date`）、および Microsoft Foundry ID フォーム全体で同じモデル ID 正規化を使用します。テーブルが配置できないモデル ID（Microsoft Foundry デプロイメント名または推論プロファイル ARN など）は、ゼロではなく、不明なモデルのデフォルトティアである 100 万入力/出力トークンあたり 5 ドル/25 ドルで価格設定されるため、認識されない ID は計測されないことで上限をバイパスできません。gateway はブート時と実行時に ID ごとに 1 回、フォールバックを通じて価格設定されるモデルについて警告します。

クライアント中止も請求されます。アップストリームはストリームの終端フレームでのみ出力トークンを報告するため、中止されたストリームはそれらを持ちません。メーターはストリーミングされたコンテンツサイズから保守的なフロア推定値（トークンあたり約 4 文字）を保持し、終端使用量フレームが欠落している場合にのみそれを請求します。完全なストリームは常にアップストリーム報告カウントを請求します。これがない場合、上限のある開発者は出力をストリーミングし、終了直前に各リクエストを中止して、カウントされることなく支出できます。

<h3 id="postgres-availability">
  Postgres の可用性
</h3>

事前チェッククエリは 2 秒のタイムアウトで Postgres にクエリします。ストアに到達できない場合またはタイムアウトする場合、デフォルトでは適用は開いた状態で失敗します。リクエストは進行し、gateway は警告をログに記録します。[`enforcement.fail_closed_on_error: true`](/docs/ja/claude-apps-gateway-config#enforcement) を設定して、代わりに閉じた状態で失敗させます。これは同じ `429 billing_error` を返し、メッセージは `spend limit unavailable` です。フェイルオープンはストア停止が推論停止になるのを防ぎます。フェイルクローズは計測されていない支出がないことを保証します。

<h2 id="admin-api-reference">
  管理 API リファレンス
</h2>

以下のエンドポイントは `/v1/organizations/spend_limits` の下で提供されます。

| メソッドとパス                                        | 説明                                                      |
| ---------------------------------------------- | ------------------------------------------------------- |
| `GET /v1/organizations/spend_limits`           | 設定された上限をリストします。クエリ：`?limit=&after_id=&before_id=`。      |
| `POST /v1/organizations/spend_limits`          | `{scope, period}` の上限を作成または置き換えます。                      |
| `GET /v1/organizations/spend_limits/{id}`      | `spl_` プレフィックス付き ID で 1 つの上限を取得します。                     |
| `DELETE /v1/organizations/spend_limits/{id}`   | 1 つの上限を削除します。`{type: "spend_limit_deleted", id}` を返します。 |
| `GET /v1/organizations/spend_limits/effective` | プリンシパルごと、期間ごとの解決された上限と期間から現在までの支出。                      |
| `GET /v1/organizations/spend_limits/audit`     | 管理者の変更トレイル、最新順。クエリ：`?limit=`。                           |

規約は Anthropic の Admin API をミラーリングします。

* すべてのオブジェクトの `type`
* `spl_` プレフィックス付き ID
* USD セントの整数文字列としての金額。`POST` は他の `currency` を `400` で拒否します
* `{type: "error", error: {type, message}, request_id}` エラーエンベロープ
* すべての管理レスポンス（成功またはエラー）の `request-id` レスポンスヘッダー、本文の `request_id` と一致

すべての変更は同じトランザクション内で `admin_audit` に前後の行を書き込み、`admin-key:<id>` または `oidc:<sub>` に属性付けされます。

ゲートウェイは支出制限エンドポイントのみを提供します。`spend_limit_increase_requests` キューなどの他の Admin API サーフェスは、ゲートウェイの管理 API の一部ではありません。

<h3 id="/effective">
  `/effective`
</h3>

`GET /v1/organizations/spend_limits/effective` は Anthropic の `SpendSummary` スキーマを返します。各行はプリンシパルの期間で、解決された上限、期間から現在までの支出、および `actor` オブジェクトを持ちます。ゲートウェイ固有の違い：

* `user_id` は OIDC `sub` です。
* `actor.name` と `actor.email_address` は、プリンシパルの最初の推論リクエストがゲートウェイを通じて実行されるまで `null` です。ゲートウェイにはユーザーディレクトリがなく、各ユーザー独自のセッション JWT から最後に見られた値を記録します。
* 各行は `groups` 配列も持ち、プリンシパルの最後に見られた IdP グループです。これはゲートウェイ拡張なので、管理者 UI は適用されるすべての上限ティアを表示できます。Anthropic 形状のクライアントはそれを無視します。
* `user_ids[]` フィルターがない場合、記録された支出を持つプリンシパルをリストします。ゲートウェイはすべての組織メンバーを列挙できないためです。

グループソースの上限は、適用が使用するのと同じ `group_limit_mode` タイブレークでそれらの最後に見られたグループに対して解決されるため、ビューアーは実際に適用される上限を表示します。

| クエリパラメーター        | 説明                                                              |
| ---------------- | --------------------------------------------------------------- |
| `user_ids[]`     | 繰り返し可能。OIDC `sub` で特定のプリンシパルにフィルターします。                          |
| `period[]`       | 繰り返し可能。`daily`、`weekly`、または `monthly` 行にフィルターします。               |
| `sort`           | `spend_desc` は最大支出者を最初にリストします。正確に 1 つの `period[]` が必要です。        |
| `q`              | OIDC `sub`、最後に見られたメール、および最後に見られた表示名に対する大文字と小文字を区別しない部分文字列フィルター。 |
| `limit` / `page` | ページサイズ（1～1000、デフォルト 20）および前のレスポンスの `next_page` からの不透明なカーソル。     |

<Warning>
  `q=` と `user_ids[]=` は GET クエリ文字列に乗るため、任意のフロントプロキシまたはロードバランサーはそれらをアクセスログでキャプチャします。PII ログポリシーが厳しい場合は、そこでこれらのパラメーターをスクラブしてください。
</Warning>

<h3 id="/audit">
  `/audit`
</h3>

支出制限の変更トレイルを返します。誰がどの上限を変更したか、前後のスナップショット、およびオプションの理由、最新順。`has_more` は正確です。このエンドポイントは最初のパーティワイヤー形状ではなく、ローカル Admin API 規約に従います。

<h3 id="pagination">
  ページネーション
</h3>

生のリストは `after_id` と `before_id` でページングされます。これらは相互に排他的な `spl_…` ID です。結果は作成順に並べられ、`has_more` はトラバーサル方向を反映します。`/effective` は、前のレスポンスの `next_page` トークンとして渡される不透明な `?page=` でページングされ、プリンシパルは昇順に並べられるため、支出が記録されている間もページは安定したままです。`limit` は両方で 1～1000、デフォルト 20 です。

<h2 id="data-lifecycle">
  データライフサイクル
</h2>

gateway は 4 つの支出関連テーブルを保持します。時間ごとのスイープが保持期間を適用します。

| テーブル               | 内容                                             | 保持期間                                                                                          |
| ------------------ | ---------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `spend`            | プリンシパルごとの期間から現在までのカウンター（セント）                   | [`admin.spend_retention_months`](/docs/ja/claude-apps-gateway-config#admin)、デフォルト 13               |
| `spend_limits`     | 設定された上限                                        | API 経由で削除されるまで                                                                                |
| `admin_audit`      | 変更トレイル                                         | [`admin.audit_retention_days`](/docs/ja/claude-apps-gateway-config#admin)、デフォルト 365                |
| `principal_emails` | 各プリンシパルの最後に見られたメール、表示名、および IdP グループ。PII を含みます。 | [`admin.identity_retention_days`](/docs/ja/claude-apps-gateway-config#admin) 最後のアクティビティ以降、デフォルト 90 |

`identity_retention_days` は意図的に `spend_retention_months` より短いです。プロビジョニング解除されたアイデンティティは更新を停止して期限切れになり、その匿名支出カウンターは年間比較レポート用に残ります。

開発者が去る場合、`DELETE /v1/organizations/spend_limits/{id}` 経由でユーザーごとの上限を削除します。その支出とアイデンティティ行は上記の保持期間で期限切れになります。1 人を即座に削除するには、オフボーディングまたはデータサブジェクトアクセスリクエスト（DSAR）の場合、gateway データベースに対して直接 `DELETE FROM principal_emails WHERE principal = '<sub>'` を実行します。これにより、メール、名前、およびグループを保持する唯一のテーブルが削除されます。`spend` と `admin_audit` 行は疑似匿名 OIDC `sub` のみを参照し、独自のウィンドウで期限切れになります。

<h2 id="related">
  関連
</h2>

* [`admin` と `enforcement` 設定](/docs/ja/claude-apps-gateway-config#admin)：管理 API の有効化と保持のチューニング
* [デプロイメントガイド](/docs/ja/claude-apps-gateway-deploy#postgres)：Postgres スキーマとバックアップガイダンス
