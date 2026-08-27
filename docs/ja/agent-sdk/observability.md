> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# OpenTelemetry を使用した可観測性

> Agent SDK からトレース、メトリクス、イベントを OpenTelemetry を使用して可観測性バックエンドにエクスポートします。

本番環境でエージェントを実行する場合、エージェントが何をしたかについての可視性が必要です。

* どのツールを呼び出したか
* 各モデルリクエストにかかった時間
* 使用されたトークン数
* 障害が発生した場所

Agent SDK は、このデータを OpenTelemetry トレース、メトリクス、ログイベントとして、OpenTelemetry Protocol（OTLP）を受け入れるバックエンド（Honeycomb、Datadog、Grafana、Langfuse、自己ホスト型コレクターなど）にエクスポートできます。

このガイドでは、SDK がテレメトリをどのように発行するか、エクスポートを設定する方法、およびデータがバックエンドに到達した後にタグ付けしてフィルタリングする方法について説明します。バックエンドにエクスポートする代わりに SDK レスポンスストリームからトークン使用量とコストを直接読み取るには、[コストと使用量の追跡](/docs/ja/agent-sdk/cost-tracking)を参照してください。

<h2 id="how-telemetry-flows-from-the-sdk">
  SDK からのテレメトリフロー
</h2>

Agent SDK は Claude Code CLI を子プロセスとして実行し、ローカルパイプを介して通信します。CLI には OpenTelemetry インストルメンテーションが組み込まれています。各モデルリクエストとツール実行の周囲にスパンを記録し、トークンとコストカウンターのメトリクスを発行し、プロンプトとツール結果の構造化ログイベントを発行します。SDK は独自のテレメトリを生成しません。代わりに、設定を CLI プロセスに渡し、CLI がコレクターに直接エクスポートします。

設定は環境変数として渡されます。デフォルトでは、子プロセスはアプリケーションの環境を継承するため、テレメトリは次の 2 つの場所のいずれかで設定できます。

* **プロセス環境：** アプリケーションが開始される前に、シェル、コンテナ、またはオーケストレーターで変数を設定します。すべての `query()` 呼び出しはコード変更なしで自動的にそれらを取得します。これは本番環境デプロイメントの推奨アプローチです。
* **呼び出しごとのオプション：** `ClaudeAgentOptions.env`（Python）または `options.env`（TypeScript）で変数を設定します。同じプロセス内の異なるエージェントが異なるテレメトリ設定を必要とする場合に使用します。Python では、`env` は継承された環境の上にマージされます。TypeScript では、`env` は継承された環境を完全に置き換えるため、渡すオブジェクトに `...process.env` を含めます。

CLI は 3 つの独立した OpenTelemetry シグナルをエクスポートします。各シグナルには独自の有効化スイッチと独自のエクスポーターがあるため、必要なものだけをオンにできます。

| シグナル   | 含まれるもの                                   | 有効化方法                                                            |
| ------ | ---------------------------------------- | ---------------------------------------------------------------- |
| メトリクス  | トークン、コスト、セッション、コード行数、ツール決定のカウンター         | `OTEL_METRICS_EXPORTER`                                          |
| ログイベント | 各プロンプト、API リクエスト、API エラー、ツール結果の構造化レコード   | `OTEL_LOGS_EXPORTER`                                             |
| トレース   | 各インタラクション、モデルリクエスト、ツール呼び出し、フック（ベータ版）のスパン | `OTEL_TRACES_EXPORTER` と `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` |

メトリクス名、イベント名、属性の完全なリストについては、Claude Code [Monitoring](/docs/ja/monitoring-usage) リファレンスを参照してください。Agent SDK は同じ CLI を実行するため、同じデータを発行します。スパン名は以下の [エージェントトレースの読み取り](#read-agent-traces)に記載されています。

<h2 id="enable-telemetry-export">
  テレメトリエクスポートを有効化
</h2>

テレメトリは `CLAUDE_CODE_ENABLE_TELEMETRY=1` を設定し、少なくとも 1 つのエクスポーターを選択するまでオフです。最も一般的な設定は、3 つのシグナルすべてを OTLP HTTP 経由でコレクターに送信します。

次の例では、変数を辞書に設定し、`options.env` を通じて渡します。エージェントは単一のタスクを実行し、CLI は `collector.example.com` のコレクターにスパン、メトリクス、イベントをエクスポートしながら、ループはレスポンスストリームを消費します。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions

  OTEL_ENV = {
      "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
      # トレースに必須（ベータ版）。メトリクスとログイベントは不要です。
      "CLAUDE_CODE_ENHANCED_TELEMETRY_BETA": "1",
      # シグナルごとにエクスポーターを選択します。SDK には otlp を使用します。以下の注記を参照してください。
      "OTEL_TRACES_EXPORTER": "otlp",
      "OTEL_METRICS_EXPORTER": "otlp",
      "OTEL_LOGS_EXPORTER": "otlp",
      # 標準 OTLP トランスポート設定。
      "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
      "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.example.com:4318",
      "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer your-token",
  }


  async def main():
      options = ClaudeAgentOptions(env=OTEL_ENV)
      async for message in query(
          prompt="List the files in this directory", options=options
      ):
          print(message)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const otelEnv = {
    CLAUDE_CODE_ENABLE_TELEMETRY: "1",
    // トレースに必須（ベータ版）。メトリクスとログイベントは不要です。
    CLAUDE_CODE_ENHANCED_TELEMETRY_BETA: "1",
    // シグナルごとにエクスポーターを選択します。SDK には otlp を使用します。以下の注記を参照してください。
    OTEL_TRACES_EXPORTER: "otlp",
    OTEL_METRICS_EXPORTER: "otlp",
    OTEL_LOGS_EXPORTER: "otlp",
    // 標準 OTLP トランスポート設定。
    OTEL_EXPORTER_OTLP_PROTOCOL: "http/protobuf",
    OTEL_EXPORTER_OTLP_ENDPOINT: "http://collector.example.com:4318",
    OTEL_EXPORTER_OTLP_HEADERS: "Authorization=Bearer your-token",
  };

  for await (const message of query({
    prompt: "List the files in this directory",
    // TypeScript では env は継承された環境を置き換えるため、最初に
    // process.env をスプレッドして PATH、ANTHROPIC_API_KEY、その他の変数を保持します。
    options: { env: { ...process.env, ...otelEnv } },
  })) {
    console.log(message);
  }
  ```
</CodeGroup>

子プロセスはデフォルトでアプリケーションの環境を継承するため、これらの変数を Dockerfile、Kubernetes マニフェスト、またはシェルプロファイルでエクスポートし、`options.env` を完全に省略することで同じ結果を達成できます。

<Note>
  `console` エクスポーターはテレメトリを標準出力に書き込みます。これは SDK がメッセージチャネルとして使用するものです。SDK を通じて実行する場合、エクスポーター値として `console` を設定しないでください。テレメトリをローカルで検査するには、`OTEL_EXPORTER_OTLP_ENDPOINT` をローカルコレクターまたはオールインワン Jaeger コンテナに指定してください。
</Note>

<h3 id="flush-telemetry-from-short-lived-calls">
  短時間の呼び出しからテレメトリをフラッシュ
</h3>

CLI はテレメトリをバッチ処理し、間隔でエクスポートします。クリーンなプロセス終了時に、保留中のデータをフラッシュしようとしますが、フラッシュはタイムアウトで制限されるため、コレクターの応答が遅い場合はスパンが削除される可能性があります。プロセスが CLI のシャットダウン前に強制終了された場合、バッチバッファ内のすべてが失われます。エクスポート間隔を短縮すると、両方のウィンドウが削減されます。

デフォルトでは、メトリクスは 60 秒ごとにエクスポートされ、トレースとログは 5 秒ごとにエクスポートされます。次の例では、短いタスクがまだ実行されている間にデータがコレクターに到達するように、3 つの間隔すべてを短縮します。

<CodeGroup>
  ```python Python theme={null}
  OTEL_ENV = {
      # ... 前の例のエクスポーター設定 ...
      "OTEL_METRIC_EXPORT_INTERVAL": "1000",
      "OTEL_LOGS_EXPORT_INTERVAL": "1000",
      "OTEL_TRACES_EXPORT_INTERVAL": "1000",
  }
  ```

  ```typescript TypeScript theme={null}
  const otelEnv = {
    // ... 前の例のエクスポーター設定 ...
    OTEL_METRIC_EXPORT_INTERVAL: "1000",
    OTEL_LOGS_EXPORT_INTERVAL: "1000",
    OTEL_TRACES_EXPORT_INTERVAL: "1000",
  };
  ```
</CodeGroup>

<h2 id="read-agent-traces">
  エージェントトレースの読み取り
</h2>

トレースはエージェント実行の最も詳細なビューを提供します。`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` を設定すると、エージェントループの各ステップがトレーシングバックエンドで検査できるスパンになります。

* **`claude_code.interaction`：** エージェントループの単一ターンをラップします。プロンプトの受信からレスポンスの生成まで。
* **`claude_code.llm_request`：** Claude API への各呼び出しをラップします。モデル名、レイテンシ、トークンカウントが属性として含まれます。
* **`claude_code.tool`：** 各ツール呼び出しをラップします。権限待機（`claude_code.tool.blocked_on_user`）と実行自体（`claude_code.tool.execution`）の子スパンがあります。
* **`claude_code.hook`：** 各 [フック](/docs/ja/agent-sdk/hooks)実行をラップします。上記の変数に加えて、詳細なベータトレース（`ENABLE_BETA_TRACING_DETAILED=1` と `BETA_TRACING_ENDPOINT`）が必要です。

`llm_request`、`tool`、`hook` スパンは、囲む `claude_code.interaction` スパンの子です。エージェントが Task ツールを通じてサブエージェントを生成する場合、サブエージェントの `llm_request` と `tool` スパンは親エージェントの `claude_code.tool` スパンの下にネストするため、完全な委譲チェーンが 1 つのトレースとして表示されます。

スパンはデフォルトで `session.id` 属性を持ちます。同じ [セッション](/docs/ja/agent-sdk/sessions)に対して複数の `query()` 呼び出しを行う場合、バックエンドで `session.id` をフィルタリングして、それらを 1 つのタイムラインとして表示します。`OTEL_METRICS_INCLUDE_SESSION_ID` が偽の値に設定されている場合、属性は省略されます。

<Note>
  トレースはベータ版です。スパン名と属性はリリース間で変更される可能性があります。Monitoring リファレンスの [トレース（ベータ版）](/docs/ja/monitoring-usage#traces-beta)を参照して、トレースエクスポーター設定変数を確認してください。
</Note>

<h2 id="link-traces-to-your-application">
  トレースをアプリケーションにリンク
</h2>

SDK は W3C トレースコンテキストを CLI サブプロセスに自動的に伝播します。アプリケーションで OpenTelemetry スパンがアクティブな状態で `query()` を呼び出すと、SDK は `TRACEPARENT` と `TRACESTATE` を子プロセス環境に注入し、CLI はそれらを読み取るため、その `claude_code.interaction` スパンはスパンの子になります。エージェント実行は、切断されたルートではなく、アプリケーションのトレース内に表示されます。

トレースコンテキスト伝播が有効な場合、CLI は `TRACEPARENT` を実行するすべての Bash および PowerShell コマンドに転送します。Bash ツールを通じて起動されたコマンドが独自の OpenTelemetry スパンを発行する場合、それらのスパンはコマンドをラップする `claude_code.tool.execution` スパンの下にネストします。

`options.env` で `TRACEPARENT` を明示的に設定すると、自動注入がスキップされるため、必要に応じて特定の親コンテキストをピン留めできます。インタラクティブ CLI セッションは受信 `TRACEPARENT` を完全に無視します。Agent SDK と `claude -p` 実行のみがそれを尊重します。Monitoring リファレンスの [トレース（ベータ版）](/docs/ja/monitoring-usage#traces-beta)を参照して、完全なスパンと属性リファレンスを確認してください。

<h2 id="tag-telemetry-from-your-agent">
  エージェントからのテレメトリにタグを付ける
</h2>

デフォルトでは、CLI は `service.name` を `claude-code` として報告します。複数のエージェントを実行する場合、または SDK を同じコレクターにエクスポートする他のサービスと一緒に実行する場合、サービス名をオーバーライドしてリソース属性を追加し、バックエンドでエージェントでフィルタリングできるようにします。

次の例では、サービスの名前を変更し、デプロイメントメタデータを添付します。これらの値は、エージェントが発行するすべてのスパン、メトリクス、イベントに OpenTelemetry リソース属性として適用されます。

<CodeGroup>
  ```python Python theme={null}
  options = ClaudeAgentOptions(
      env={
          # ... エクスポーター設定 ...
          "OTEL_SERVICE_NAME": "support-triage-agent",
          "OTEL_RESOURCE_ATTRIBUTES": "service.version=1.4.0,deployment.environment=production",
      },
  )
  ```

  ```typescript TypeScript theme={null}
  const options = {
    env: {
      ...process.env,
      // ... エクスポーター設定 ...
      OTEL_SERVICE_NAME: "support-triage-agent",
      OTEL_RESOURCE_ATTRIBUTES":
        "service.version=1.4.0,deployment.environment=production",
    },
  };
  ```
</CodeGroup>

<h2 id="attribute-actions-to-your-end-users">
  アクションをエンドユーザーに属性付ける
</h2>

CLI は、Anthropic を呼び出すために使用する認証情報に基づいて、すべてのイベントに [ID 属性](/docs/ja/monitoring-usage#standard-attributes)を添付します。1 つのデプロイメントから多くのエンドユーザーにサービスを提供するアプリケーションを構築する場合、これらの属性はサービスの認証情報を識別し、エージェントが代わりに機能したエンドユーザーを識別しません。

ツール呼び出しと MCP アクティビティをアプリケーションのエンドユーザーに属性付けるには、各 `query()` 呼び出しでエンドユーザー ID をリソース属性として注入します。`OTEL_RESOURCE_ATTRIBUTES` は [コンマ、スペース、等号記号を予約](/docs/ja/monitoring-usage#multi-team-organization-support)しているため、値を補間する前にパーセントエンコードします。次の例では、要求するユーザーとテナントを 1 つのリクエストからのすべてのスパンとイベントに添付します。ここでは、ユーザー ID とテナント ID を含む web フレームワークからの `request` オブジェクトを想定しています。

<CodeGroup>
  ```python Python theme={null}
  from urllib.parse import quote

  options = ClaudeAgentOptions(
      env={
          # ... エクスポーター設定 ...
          "OTEL_RESOURCE_ATTRIBUTES": f"enduser.id={quote(request.user_id)},tenant.id={quote(request.tenant_id)}",
      },
  )
  ```

  ```typescript TypeScript theme={null}
  const options = {
    env: {
      ...process.env,
      // ... エクスポーター設定 ...
      OTEL_RESOURCE_ATTRIBUTES: `enduser.id=${encodeURIComponent(request.userId)},tenant.id=${encodeURIComponent(request.tenantId)}`,
    },
  };
  ```
</CodeGroup>

エンドユーザー ID が添付されると、`tool_decision`、`tool_result`、`mcp_server_connection`、`permission_mode_changed` イベント（`claude_code.` プレフィックス付きのログレコードとしてエクスポートされる）はユーザーごとの監査証跡になり、Security Information and Event Management（SIEM）プラットフォームに転送できます。Monitoring リファレンスの [セキュリティイベントの監査](/docs/ja/monitoring-usage#audit-security-events)を参照して、セキュリティ関連イベントの完全なリストと各イベントが持つ属性を確認してください。

<h2 id="control-sensitive-data-in-exports">
  エクスポートの機密データを制御
</h2>

テレメトリはデフォルトで構造化されています。期間、モデル名、ツール名はすべてのスパンに記録されます。トークンカウントは基になる API リクエストが使用データを返すときに記録されるため、失敗または中止されたリクエストのスパンはそれらを省略する可能性があります。エージェントが読み取り、書き込むコンテンツはデフォルトでは記録されません。これらのオプトイン変数は、エクスポートされたデータにコンテンツを追加します。

| 変数                        | 追加内容                                                                                                                                                                                                                                                                                                             |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `OTEL_LOG_USER_PROMPTS=1` | `claude_code.user_prompt` イベントと `claude_code.interaction` スパンのプロンプトテキスト                                                                                                                                                                                                                                          |
| `OTEL_LOG_TOOL_DETAILS=1` | `claude_code.tool_result` イベントのツール入力引数（ファイルパス、シェルコマンド、検索パターン）                                                                                                                                                                                                                                                    |
| `OTEL_LOG_TOOL_CONTENT=1` | `claude_code.tool` のスパンイベントとしての完全なツール入力および出力本体。60 KB で切り詰められます。[トレース](#read-agent-traces)が有効になっている必要があります                                                                                                                                                                                                        |
| `OTEL_LOG_RAW_API_BODIES` | Anthropic Messages API リクエストおよびレスポンス JSON 全体を `claude_code.api_request_body` および `claude_code.api_response_body` ログイベントとして。`1` に設定して 60 KB で切り詰められたインラインボディを取得するか、`file:<dir>` に設定してディスク上の切り詰められていないボディをイベント内の `body_ref` パスで取得します。ボディには会話履歴全体が含まれ、拡張思考コンテンツが編集されます。これを有効にすると、上記の 3 つの変数が明かすすべてのコンテンツへの同意が暗示されます |

エージェントが処理するデータを保存することが可観測性パイプラインで承認されていない限り、これらを設定しないままにしてください。Monitoring リファレンスの [セキュリティとプライバシー](/docs/ja/monitoring-usage#security-and-privacy)を参照して、すべての属性と編集動作の完全なリストを確認してください。

<h2 id="related-documentation">
  関連ドキュメント
</h2>

これらのガイドは、エージェントの監視とデプロイメントの隣接トピックをカバーしています。

* [コストと使用量の追跡](/docs/ja/agent-sdk/cost-tracking)：外部バックエンドなしでメッセージストリームからトークンとコストデータを読み取ります。
* [Agent SDK のホスティング](/docs/ja/agent-sdk/hosting)：環境レベルで OpenTelemetry 変数を設定できるコンテナにエージェントをデプロイします。
* [Monitoring](/docs/ja/monitoring-usage)：CLI が発行するすべての環境変数、メトリクス、イベントの完全なリファレンス。
