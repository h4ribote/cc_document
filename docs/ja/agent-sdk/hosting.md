> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Agent SDK のホスティング

> Agent SDK を本番環境にデプロイする：サブプロセスアーキテクチャ、セッション永続化、スケーリング、可観測性、Docker、Kubernetes、サンドボックスプロバイダー向けのマルチテナント分離。

Agent SDK は `claude` CLI サブプロセスをスポーンして監視します。このサブプロセスはシェル、作業ディレクトリ、ディスク上のセッションファイルを所有しています。ホスティングはステートレス API ラッパーのホスティングとは異なります。実行中のすべてのエージェントはローカル状態に結びついた長寿命プロセスであり、これはリソースの割り当て方法、セッションの永続化方法、テナント間のスケーリング方法に影響を与えます。

このページでは、独自のインフラストラクチャでのセルフホスティングについて説明します：[サブプロセスモデル](#the-subprocess-model)を理解し、[セッションパターンを選択](#choose-a-session-pattern)し、[コンテナをプロビジョニング](#provision-the-container)し、永続化、可観測性、認証、マルチテナント分離などの[本番環境の懸念事項](#handle-production-concerns)に対処します。デプロイ可能な Dockerfile と Kubernetes マニフェストについては、[ホスティングクックブック](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk/hosting)を参照してください。

インフラストラクチャ制御、カスタム分離、または独自のデータプレーンが不要な場合は、代わりに[Managed Agents](https://platform.claude.com/docs/ja/managed-agents/overview)の使用を検討してください：Anthropic がエージェントとサンドボックスを実行するホスト型 REST API であり、アプリケーションはイベントを送信し、ホスティングインフラストラクチャを操作することなく結果をストリーミングバックします。

<Info>
  ネットワーク制御、認証情報管理、分離オプションを含む基本的なサンドボックス化を超えたセキュリティ強化については、[セキュアデプロイメント](/docs/ja/agent-sdk/secure-deployment)を参照してください。
</Info>

<h2 id="the-subprocess-model">
  サブプロセスモデル
</h2>

このページのすべてのホスティング決定は、SDK がエージェントを実行する方法に基づいています。コードが `query()` を呼び出すと、SDK は別の `claude` CLI プロセスを生成し、stdio 経由で通信します。そのサブプロセスはシェル、作業ディレクトリ、およびローカルディスク上の JSONL セッショントランスクリプトを所有しています。

<img src="https://mintcdn.com/claude-code/ikqp3_70mqIahteV/images/agent-sdk/hosting-subprocess.svg?fit=max&auto=format&n=ikqp3_70mqIahteV&q=85&s=9dac857ca9d3b1410c3734900c386004" alt="リクエストフロー：クライアントからアプリへ、コンテナ内の stdio 経由で claude CLI サブプロセスを生成し、サブプロセスはローカルディスクに書き込み、HTTPS 経由で api.anthropic.com を呼び出します" width="920" height="220" data-path="images/agent-sdk/hosting-subprocess.svg" />

1 つのエージェントセッションは 1 つのサブプロセスにマップされます。N 個の同時セッションを実行することは、N 個のサブプロセスを実行することを意味し、各サブプロセスは独自のプロセスツリーとトランスクリプトファイルを持ちます。デフォルトでは、すべてがアプリケーションの作業ディレクトリを継承するため、セッションが別のファイルシステムを必要とする場合は、各 `query()` 呼び出しで `cwd` を渡してください：

<CodeGroup>
  ```typescript TypeScript theme={null}
  query({ prompt, options: { cwd: "/work/session-a" } })
  ```

  ```python Python theme={null}
  query(prompt=prompt, options=ClaudeAgentOptions(cwd="/work/session-a"))
  ```
</CodeGroup>

<h3 id="state-that-lives-on-local-disk">
  ローカルディスク上に存在する状態
</h3>

3 種類のエージェント状態がデフォルトでコンテナのファイルシステム上に存在します。これらのいずれもコンテナの再起動、スケールダウン、または別のノードへの移動を生き残りません。

| 状態                  | デフォルトの場所                                                                       |
| ------------------- | ------------------------------------------------------------------------------ |
| セッショントランスクリプト       | `~/.claude/projects/`、または設定されている場合は `CLAUDE_CONFIG_DIR` の下の `projects/` ディレクトリ |
| `CLAUDE.md` メモリファイル | ユーザーティアの場合は `~/.claude/CLAUDE.md`、プロジェクトティアの場合はセッションの作業ディレクトリ                  |
| 作業ディレクトリアーティファクト    | セッションの作業ディレクトリ                                                                 |

ホスト間でトランスクリプトを永続化するには、[`SessionStore` アダプター](/docs/ja/agent-sdk/session-storage)を設定してください。メモリファイルおよび他の作業ディレクトリアーティファクトには、マウントされたボリュームまたはオブジェクトストア同期などの独自のストレージ戦略が必要です。

セッション、再開、およびフォークが API レベルでどのように機能するかについては、[セッション](/docs/ja/agent-sdk/sessions)を参照してください。

<h2 id="choose-a-session-pattern">
  セッションパターンを選択する
</h2>

これら 4 つのパターンはセッションライフサイクルをカバーしています。コンテナがそれが提供するセッションに対してどのくらいの期間存在するかです。コンテナが実行される場所については、[ホスティングクックブック](https://github.com/anthropics/claude-cookbooks/blob/main/claude_agent_sdk/07_Hosting_the_agent.ipynb)に、ローカル Docker、Modal、Kubernetes 用の[デプロイ可能なコード](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk/hosting)があります。ここでセッションパターンを選択し、クックブックからデプロイメントターゲットを選択してください。

<h3 id="ephemeral-sessions">
  エフェメラルセッション
</h3>

各ユーザータスク用にコンテナを作成し、タスクが完了したときに破棄します。ワンオフタスクに最適です。ユーザーはタスクが完了している間も AI と相互作用できますが、完了するとコンテナは破棄されます。

例のワークロードには、バグ調査と修正、請求書と領収書の抽出、ドキュメント翻訳、メディア変換が含まれます。

コンテナは SDK を呼び出して終了する 1 回限りのエントリポイントを実行します。以下の例は最小限の TypeScript バージョンを示しています。`entrypoint.mts` として保存するか、`package.json` で `"type": "module"` を設定して、トップレベルの `await` が利用可能になるようにしてください。

```typescript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";

const prompt = process.env.TASK_PROMPT!;
for await (const message of query({ prompt, options: { maxTurns: 20 } })) {
  console.log(message);
}
```

<h3 id="long-running-sessions">
  長時間実行セッション
</h3>

永続的なコンテナインスタンスを実行し、多くの場合、コンテナごとに複数の SDK プロセスをホストして、継続的な作業に対応します。自律的なアクションを実行するエージェント、コンテンツを提供するエージェント、または高ボリュームのメッセージストリームを処理するエージェントに最適です。

例のワークロードには、受信メールをトリアージして応答するメールエージェント、コンテナポートを通じてユーザーごとの編集可能なサイトをホストするサイトビルダー、Slack などのプラットフォームからの継続的なトラフィックを処理するチャットボットが含まれます。

コンテナは HTTP または WebSocket エンドポイントを公開し、各アクティブセッションを長時間実行されるクエリとその背後にあるサブプロセスにマップします。TypeScript では、[`streamInput()`](/docs/ja/agent-sdk/typescript#query-object) を使用してアクティブセッションにターンを追加し、[`startup()`](/docs/ja/agent-sdk/typescript#startup) を使用して受信トラフィックの前にサブプロセスをプリウォームします。Python では、[`ClaudeSDKClient`](/docs/ja/agent-sdk/python#claudesdkclient) を使用してセッションをターン全体で開いたままにします。コンテナのサイズを、メモリに保持できる最大数の同時セッションに対応できるようにしてください。

<h3 id="hybrid-sessions">
  ハイブリッドセッション
</h3>

スタートアップ時に [`SessionStore`](/docs/ja/agent-sdk/session-storage) から水和し、更新を戻す一時的なコンテナです。多くの相互作用にまたがるが、その間アイドル状態になるセッションに最適です。コンテナはアイドル期間中にスピンダウンし、ユーザーが戻ってきたときにスピンバックアップします。

例のワークロードには、断続的なチェックインを伴う個人プロジェクトマネージャー、数時間にわたって一時停止および再開する深い研究、相互作用全体でチケット履歴を読み込むカスタマーサポートエージェントが含まれます。

プロバイダーのアイドルタイムアウトをユーザーが戻ってくることを期待する頻度に合わせて調整します。`SessionStore` が設定されていない状態でコンテナをシャットダウンするとトランスクリプトが失われるため、ストアはこのパターンでは必須であり、オプションではありません。

パターンは ID でセッションを再開し、共有ストアを接続することに基づいています：

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query, type SessionStore } from "@anthropic-ai/claude-agent-sdk";

  declare const userInput: string;
  declare const sessionId: string;          // looked up from your database by user
  declare const sessionStore: SessionStore; // S3, Redis, Postgres, or your own adapter

  for await (const message of query({
    prompt: userInput,
    options: { resume: sessionId, sessionStore },
  })) {
    // ...
  }
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions

  async for message in query(
      prompt=user_input,
      options=ClaudeAgentOptions(
          resume=session_id,            # looked up from your database by user
          session_store=session_store,  # S3, Redis, Postgres, or your own adapter
      ),
  ):
      ...
  ```
</CodeGroup>

[セッションストレージ](/docs/ja/agent-sdk/session-storage)で完全な `SessionStore` インターフェースと参照アダプターを参照してください。

<h3 id="multi-agent-container">
  マルチエージェントコンテナ
</h3>

1 つのコンテナ内で複数の SDK サブプロセスを実行します。エージェントが密接に協力する必要があるエージェント、たとえば、エージェントが共有環境で相互に相互作用するマルチエージェントシミュレーションに最適です。

各エージェントに独自の作業ディレクトリを与えて、相互にファイルを上書きしないようにし、設定読み込みを分離して、エージェントごとの `CLAUDE.md` ファイルがエージェント間でリークしないようにします。具体的なオプションについては、[マルチテナント分離](#multi-tenant-isolation)を参照してください。

<h2 id="provision-the-container">
  コンテナのプロビジョニング
</h2>

<h3 id="container-based-sandboxing">
  コンテナベースのサンドボックス
</h3>

プロセス分離、リソース制限、ネットワーク制御、および一時的なファイルシステムのために、サンドボックス化されたコンテナ内で SDK を実行します。複数のプロバイダーが Agent SDK のモデルに適合するサンドボックス化されたコンテナ環境を専門としています。

プロバイダーを選択する際に回答すべき質問：

* **サンドボックスを実行するのは誰か**：sandbox-as-a-service プロバイダーはインフラストラクチャを運用しますが、自己ホスト型オプションは自分のシステムで実行するソフトウェアを提供します。
* **コールドスタートレイテンシ**：「サンドボックスを作成」から「最初のリクエストを受け入れる準備ができた」までの時間。一時的なパターンは 1 秒未満の起動が必要です。長時間実行パターンはより長い時間を許容します。
* **永続的なストレージ**：プロバイダーが耐久性のあるボリュームを提供するか、一時的なディスクのみを提供するか。ハイブリッドパターンは、サンドボックス内またはその横のいずれかで、どこかに耐久性のあるストレージが必要です。
* **価格モデル**：秒単位、リクエスト単位、または時間単位の定額請求。秒単位の価格設定は、バースト的な一時的なワークロードに適しています。時間単位は長時間実行セッションに適しています。
* **ネットワーク**：カスタム出力ルール、アウトバウンドプロキシ、および規制環境向けのプライベート VPC ピアリングのサポート。

評価するプロバイダー：

* [Modal Sandbox](https://modal.com/docs/guide/sandbox)（[デモ実装](https://modal.com/docs/examples/claude-slack-gif-creator)付き）
* [Cloudflare Sandboxes](https://github.com/cloudflare/sandbox-sdk)
* [Daytona](https://www.daytona.io/)
* [E2B](https://e2b.dev/)
* [Fly Machines](https://fly.io/docs/machines/)
* [Vercel Sandbox](https://vercel.com/docs/functions/sandbox)

Docker、gVisor、Firecracker などの自己ホスト型オプション、および詳細な分離設定については、[分離テクノロジー](/docs/ja/agent-sdk/secure-deployment#isolation-technologies)を参照してください。

<h3 id="runtime-dependencies">
  ランタイム依存関係
</h3>

コンテナには SDK の言語ランタイムのみが必要です：

* Python SDK の場合は Python 3.10 以上、または TypeScript SDK の場合は Node.js 18 以上
* 両方の SDK パッケージはホストプラットフォーム用のネイティブ Claude Code バイナリをバンドルしているため、生成された CLI に対して個別の Claude Code または Node.js インストールは不要です

バンドルされたバイナリは SDK パッケージバージョンに固定されているため、SDK を更新することが CLI を更新する方法です。SDK は semver に従います：パッチリリースは継続的に取得し、マイナーを取得する前に [TypeScript](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md) または [Python](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md) チェンジログを確認してください。

<h3 id="resources">
  リソース
</h3>

新しく起動されたインスタンスの場合、エージェントあたり 1 GiB RAM、5 GiB ディスク、および 1 CPU が合理的な開始点です。メモリ使用量はセッション長とツールアクティビティとともに増加するため、アイドル状態のベースラインではなく、実際に必要なセッション長と同時実行性に合わせてサイズを設定してください。ホストあたりのエージェント数を計算する方法については、[スケーリングと同時実行](#scaling-and-concurrency)を参照してください。

<h3 id="network">
  ネットワーク
</h3>

SDK は `api.anthropic.com` へのアウトバウンド HTTPS、または Amazon Bedrock または Google Cloud の Agent Platform で実行する場合はプロバイダーのリージョナルエンドポイントへのアウトバウンド HTTPS が必要です。エージェントが [MCP サーバー](/docs/ja/agent-sdk/mcp)または外部ツールを使用する場合、それらのエンドポイントへのアウトバウンドアクセスも必要です。本番環境では、ドメイン許可リストを適用し、認証情報を挿入し、リクエストをログに記録する出力プロキシを通じてアウトバウンドトラフィックをルーティングしてください。完全なパターンについては、[セキュアデプロイメント](/docs/ja/agent-sdk/secure-deployment)を参照してください。

インバウンドトラフィックの場合、コンテナ上の HTTP または WebSocket ポートを公開します。アプリケーションはそのポート上のクライアントリクエストを処理し、SDK を内部的に呼び出します。サブプロセス自体はネットワーク上でリッスンしません。

<h2 id="handle-production-concerns">
  本番環境の懸念事項に対応する
</h2>

自己ホスト型エージェントをリリースする前に、これらの決定を検討してください。

<h3 id="session-and-state-persistence">
  セッションと状態の永続性
</h3>

デフォルトのローカルディスクは、再起動、スケールダウン、または別のノードへの移動時に失われます。ユーザーが再開することを期待するセッションについては、トランスクリプトを [`SessionStore` アダプター](/docs/ja/agent-sdk/session-storage) を使用して耐久性のあるストレージにミラーリングしてください。S3、Redis、Postgres アダプターと独自のアダプター用の適合スイートについては、[リファレンス実装](/docs/ja/agent-sdk/session-storage#reference-implementations) を参照してください。

`SessionStore` の動作について知っておくべき 3 つのことがあります。

* **トランスクリプトのみ**：`SessionStore` はトランスクリプトをミラーリングし、`CLAUDE.md` メモリファイルまたは他の作業ディレクトリアーティファクトはミラーリングしません。共有ボリュームをマウントするか、それらを別途同期してください。
* **ミラーリング、置き換えではない**：サブプロセスはまずローカルディスクに書き込み、ストアは各バッチのコピーを受け取ります。ローカル書き込みは権限を持ったままです。
* **`mirror_error` メッセージ**：ストアが拒否したバッチは合計最大 3 回送信され、各再試行の前に短いバックオフがあります。タイムアウトした呼び出しは再試行されません。バッチがまだ失敗する場合、SDK はそれをドロップし、`{ type: "system", subtype: "mirror_error" }` メッセージを発行し、クエリを続行します。ストアの耐久性が重要な場合は、これらについてアラートを設定してください。

<h3 id="observability">
  可観測性
</h3>

Agent SDK エージェントは、多くの API ラウンドトリップにわたってツール呼び出しを生成する長時間実行プロセスです。テレメトリがなければ、どのツールが実行されたか、どのくらい時間がかかったか、またはセッションがどこで停止したかを確認することはできません。

SDK は環境から OpenTelemetry 設定を継承します。コンテナまたはオーケストレーターレベルで OTEL 環境変数を設定して、すべての `query()` 呼び出しがスパン、メトリクス、およびログイベントをコレクターにエクスポートするようにしてください。以下の例は、3 つのシグナルすべてに対して OTLP エクスポートを有効にします。`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA` はトレースにのみ必要です。メトリクスとログのみをエクスポートする場合は省略してください。

```bash title=".env' theme={null}
CLAUDE_CODE_ENABLE_TELEMETRY=1
CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1
OTEL_TRACES_EXPORTER=otlp
OTEL_METRICS_EXPORTER=otlp
OTEL_LOGS_EXPORTER=otlp
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector.example.com:4318
```

プロンプトテキストとツール入力はデフォルトではエクスポートに含まれません。オプトインフラグについては [エクスポートで機密データを制御する](/docs/ja/agent-sdk/observability#control-sensitive-data-in-exports) を参照し、完全なシグナルカタログについては [可観測性](/docs/ja/agent-sdk/observability) を参照してください。

<h3 id="auth-and-secrets">
  認証とシークレット
</h3>

ホスティング時に重要な 3 つの認証上の懸念があります。

* **Anthropic API**：サブプロセスは環境から `ANTHROPIC_API_KEY` を読み取ります。シークレットマネージャーから提供するか、`ANTHROPIC_BASE_URL` を設定して、モデル呼び出しをコンテナ外でキーを注入するプロキシを通じてルーティングしてください。プロキシパターンについては [認証情報管理](/docs/ja/agent-sdk/secure-deployment#credential-management) を参照し、サポートされている認証方法については [SDK 概要](/docs/ja/agent-sdk/overview#get-started) を参照してください。
* **インバウンド**：エージェントコンテナの前のゲートウェイに認証を配置してください。エージェントは事前認証されたリクエストを受け取る必要があり、ユーザートークンを検証するコンポーネントであってはいけません。
* **アウトバウンドツール**：ツール認証情報をエージェント環境から除外してください。アウトバウンド呼び出しをプロキシを通じてルーティングし、リクエストがコンテナを離れた後に API キーを注入してください。エージェントが呼び出しを行い、プロキシが認証情報を追加します。

<h3 id="scaling-and-concurrency">
  スケーリングと並行処理
</h3>

各セッションは独自のサブプロセスで実行されるため、ホスト上の並行処理はそのホストの RAM が保持できるサブプロセスの数によって制限されます。

この式を使用してホストのサイズを設定してください。

```text theme={null}
agents per host = (host RAM - overhead) / (per-session RAM ceiling)
```

セッションごとの上限を測定するには、代表的なセッションをターゲット長まで実行し、予想されるツール負荷の下で実行し、ピーク RSS を記録してください。[リソース](#resources) の 1 GiB の開始点は下限であり、上限ではありません。

水平スケーリングルーティングはパターンに依存します。長時間実行セッションの場合、コンテナが多くのセッションを保持する場合、ロードバランサーの背後にコンテナプールを実行し、`sessionId` での一貫性ハッシュを使用して各セッションを 1 つのコンテナにピン留めしてください。ピン留めされたセッションは、削除されるか、コンテナが再起動されるまで、同じコンテナ、したがって同じ実行中のサブプロセスに継続的にヒットします。

単一セッションからの [サブエージェント](/docs/ja/agent-sdk/subagents) の大規模なファンアウトは、API レート制限に達する可能性があります。1 つの広いディスパッチを発行するのではなく、作業をより小さなバッチに分割してください。

<h3 id="cost">
  コスト
</h3>

Anthropic トークンコストは通常、コンテナインフラストラクチャコストを 1 桁以上上回ります。最小限にプロビジョニングされたコンテナは 1 時間あたり約 \$0.05 で実行されますが、単一の長いエージェントセッションはトークンで数ドルを費やす可能性があります。セッションごとのトークンアカウンティングについては [コスト追跡](/docs/ja/agent-sdk/cost-tracking) を参照してください。

<h3 id="multi-tenant-isolation">
  マルチテナント分離
</h3>

デフォルト SDK の動作は、ファイルシステムから設定と `CLAUDE.md` メモリファイルを読み取ります。複数のテナントにサービスを提供する共有コンテナでは、これらのファイルは 1 つのテナントのコンテキストを別のテナントのセッションにリークする可能性があります。

共有コンテナ内でテナントを分離するには：

* TypeScript で `settingSources: []` を渡すか、Python で `setting_sources=[]` を渡して、ファイルシステム設定が読み込まれないようにしてください。
* `env` で `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` を設定してください。[自動メモリ](/docs/ja/memory#auto-memory) は `~/.claude/projects/<project>/memory/` で `settingSources` に関係なくシステムプロンプトに読み込まれます。[settingSources が制御しないもの](/docs/ja/agent-sdk/claude-code-features#what-settingsources-does-not-control) を参照して、無条件に読み込まれる他の入力を確認してください。
* `CLAUDE_CONFIG_DIR` をテナントごとのディレクトリにポイントして、テナントが `~/.claude.json` グローバル設定を共有しないようにしてください。
* テナントごとの作業ディレクトリを使用してください。すべての `query()` 呼び出しで `cwd` を明示的に渡してください。
* プロキシで異なるアウトバウンド IP、認証情報、またはドメイン許可リストなど、テナントごとのエグレスルールを適用して、侵害されたテナントが別のテナントのアウトバウンドポリシーを介してデータを流出させることができないようにしてください。

以下の例は、4 つの SDK レベルのオプションを一緒に適用します。`tenantDir` と `configDir` を構築して、各テナントが他のテナントが読み取ることができないパスを取得するようにしてください。TypeScript では、`env` はサブプロセス環境を置き換えるため、`PATH` や `ANTHROPIC_API_KEY` などの継承された変数を保持するために `...process.env` を展開してください。Python では、`env` は継承された環境の上にマージされます。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  declare const prompt: string;
  declare const tenantDir: string;
  declare const configDir: string;

  for await (const message of query({
    prompt,
    options: {
      cwd: tenantDir,
      settingSources: [],
      env: {
        ...process.env,
        CLAUDE_CONFIG_DIR: configDir,
        CLAUDE_CODE_DISABLE_AUTO_MEMORY: "1",
      },
    },
  })) {
    // ...
  }
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions

  async for message in query(
      prompt=prompt,
      options=ClaudeAgentOptions(
          cwd=tenant_dir,
          setting_sources=[],
          env={
              "CLAUDE_CONFIG_DIR": config_dir,
              "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
          },
      ),
  ):
      ...
  ```
</CodeGroup>

テナントごとのネットワーク制御については、[セキュアデプロイメント](/docs/ja/agent-sdk/secure-deployment) を参照してください。

<h2 id="known-limitations">
  既知の制限事項
</h2>

デプロイメント設計でこれらを考慮してください。

| 制限事項                                  | 対応方法                                                                                                                                                                                                                             |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| トップレベルのセッションタイムアウトがない                 | セッションは自動的にタイムアウトしません。`Options` で `maxTurns` を設定して、エージェントがツール使用ラウンドトリップを実行する回数を制限し、停止する前に制限してください。                                                                                                                                |
| 長いセッションでのメモリ増加                        | セッション長を制限するか、サブプロセスを定期的にリサイクルしてください。[スケーリングと並行処理](#scaling-and-concurrency)を参照してください。                                                                                                                                            |
| 大規模な並列サブエージェントのファンアウトがレート制限に達する可能性がある | 1 つの広いディスパッチを発行するのではなく、作業をより小さなバッチに分割してください。                                                                                                                                                                                     |
| サブエージェントごとのウォールクロック期限がない              | 各[サブエージェント](/docs/ja/agent-sdk/subagents)を `AgentDefinition` の `maxTurns` で制限してください。バックグラウンドサブエージェントのみの場合、`CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS` は、`run_in_background` サブエージェントが出力の生成を停止したときに発火するスタールウォッチドッグを設定します。これは総実行時間の期限ではありません。 |

<h2 id="next-steps">
  次のステップ
</h2>

* [ホスティングクックブック](https://github.com/anthropics/claude-cookbooks/blob/main/claude_agent_sdk/07_Hosting_the_agent.ipynb)：Docker、Modal、および Kubernetes 用の[デプロイ可能なコード](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk/hosting)を含むノートブックのウォークスルー。
* [セッションストレージ](/docs/ja/agent-sdk/session-storage)：`SessionStore` アダプターを使用してホスト間でトランスクリプトを永続化します。
* [可観測性](/docs/ja/agent-sdk/observability)：OTEL トレース、メトリクス、およびログをコレクターにエクスポートします。
* [セキュアデプロイメント](/docs/ja/agent-sdk/secure-deployment)：ネットワーク制御、認証情報管理、および分離強化。
* [コスト追跡](/docs/ja/agent-sdk/cost-tracking)：セッションごとのトークンおよびコスト会計。
