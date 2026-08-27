> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 機能の利用可能性

> Anthropic のサブスクリプションプラン、Anthropic Console、Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、Microsoft Foundry 全体で利用可能な Claude Code 機能を比較します。

Claude Code CLI とローカルで実行されるすべてのものは、すべてのプロバイダーで同じように動作します。プロバイダーごとのセットアップ手順については、[エンタープライズデプロイメント概要](/docs/ja/third-party-integrations)を参照してください。プロバイダーで不足している機能に直接進みたい場合は、[プロバイダー別サマリー](#summary-by-provider)タブを参照してください。

以下の表では、✓ は利用可能、✗ は利用不可、「注記を参照」は部分的なサポートについての脚注にリンクしています。✓ の後の修飾子は、その部分集合への利用可能性を絞り込み、「Admin-enabled」は、組織管理者がそれをオンにするまで機能がオフであることを意味します。

<h2 id="availability-by-model-provider">
  モデルプロバイダー別の利用可能性
</h2>

認証方法によって、Claude Code がアクセスできる機能が決まります。プロバイダーで不足している機能の単一リストについては、[プロバイダー別サマリー](#summary-by-provider)タブを参照してください。表内の列を見つけるには：

* **Claude サブスクリプション**：Pro、Max、Team、または Enterprise プランで claude.ai アカウントでサインインします
* **Anthropic Console**：Anthropic API キーで認証します
* **Amazon Bedrock**：Amazon Bedrock モデルカタログから Claude モデルを使用し、`CLAUDE_CODE_USE_BEDROCK` を設定します。[Mantle エンドポイント](/docs/ja/amazon-bedrock#use-the-mantle-endpoint)（`CLAUDE_CODE_USE_MANTLE`）はこの列でカバーされています
* **Claude Platform on AWS**：AWS Marketplace を通じて Claude を購入しましたが、Anthropic API を呼び出し、`CLAUDE_CODE_USE_ANTHROPIC_AWS` を設定します
* **Google Cloud の Agent Platform**：Google が運営しており、`CLAUDE_CODE_USE_VERTEX` を設定します
* **Microsoft Foundry**：Azure 上で Anthropic が運営しており、`CLAUDE_CODE_USE_FOUNDRY` を設定します

<h3 id="features-available-on-every-provider">
  すべてのプロバイダーで利用可能な機能
</h3>

これらはすべてのプロバイダーで動作します：

* [CLI](/docs/ja/quickstart) と [Agent SDK](/docs/ja/agent-sdk/overview)
* [VS Code](/docs/ja/vs-code) と [JetBrains](/docs/ja/jetbrains) 拡張機能
* [Subagents](/docs/ja/sub-agents)、[hooks](/docs/ja/hooks-guide)、[commands](/docs/ja/commands)、および [skills](/docs/ja/skills)
* [CLAUDE.md メモリ](/docs/ja/memory)、[plugins](/docs/ja/plugins)、および [MCP サーバー](/docs/ja/mcp)
* [Checkpoints](/docs/ja/checkpointing)、[sandboxing](/docs/ja/sandboxing)、および [Workflows](/docs/ja/workflows)
* [OpenTelemetry メトリクス](/docs/ja/monitoring-usage) と [管理設定ファイル](/docs/ja/settings#settings-files)

これらの 3 つには、プロバイダー固有の違いがあります：

* **MCP サーバー**：[claude.ai からのコネクタ](/docs/ja/mcp#use-mcp-servers-from-claude-ai)は、claude.ai サブスクリプションがアクティブな認証方法である場合にのみロードされ、[ツール検索](/docs/ja/mcp#configure-tool-search)は Google Cloud の Agent Platform でデフォルトでオフになっており、`ANTHROPIC_BASE_URL` がファーストパーティ以外のホストを指している場合もオフになります
* **Subagents**：組み込みの [Explore subagent](/docs/ja/sub-agents#built-in-subagents)は、Claude API で継承されたモデルを Opus に制限し、他のプロバイダー（Claude Platform on AWS を含む）では直接メイン会話のモデルを継承します
* **[Commands](/docs/ja/commands#all-commands)**：`/design-sync` と `/radio` は Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、および Claude Platform on AWS では利用不可であり、`/voice` には claude.ai アカウントが必要です

<h3 id="features-that-require-a-claude-subscription">
  Claude サブスクリプションが必要な機能
</h3>

これらは claude.ai アカウントでサインインする必要があり、Anthropic Console API キーまたはサードパーティプロバイダーからはアクセスできません：

* [Web 上の Claude Code](/docs/ja/claude-code-on-the-web)、モバイル上の Claude Code、および [Slack の Claude Code](/docs/ja/slack)
* [Claude Code Desktop](/docs/ja/desktop)
* [Routines](/docs/ja/routines)（`/schedule`）
* [Ultraplan](/docs/ja/ultraplan) と [Ultrareview](/docs/ja/ultrareview)
* [Code Review](/docs/ja/code-review)：Team および Enterprise プラン
* [Remote Control](/docs/ja/remote-control)
* [Chrome 拡張機能](/docs/ja/chrome)
* [Computer use](/docs/ja/computer-use)：Pro および Max プラン
* [Artifacts](/docs/ja/artifacts)：Pro、Max、Team、および Enterprise プラン
* [Voice dictation](/docs/ja/voice-dictation)

Desktop は部分的な例外です：[ゲートウェイルーティングはアプリで設定するか、管理者が設定できます](/docs/ja/llm-gateway-connect#desktop-app)。Enterprise デプロイメントは、[管理設定](https://claude.com/docs/third-party/claude-desktop/configuration)を介して Desktop を Google Cloud の Agent Platform またはゲートウェイプロバイダーにルーティングでき、[Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview) は Code タブを Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、または自己ホスト型 LLM ゲートウェイで実行します。これらの機能のプラン別利用可能性については、[サブスクリプションプラン別の利用可能性](#availability-by-subscription-plan)を参照してください。

<h3 id="cli-capabilities-that-vary-by-provider">
  プロバイダーによって異なる CLI 機能
</h3>

これらの機能はローカル CLI で動作しますが、すべてのプロバイダーが公開していないサーバー側の機能に依存しています。

<table>
  <thead>
    <tr>
      <th>機能</th>
      <th>Claude サブスクリプション</th>
      <th>Anthropic Console</th>
      <th>Amazon Bedrock</th>
      <th>Claude Platform on AWS</th>
      <th>Google Cloud の Agent Platform</th>
      <th>Microsoft Foundry</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td>[Web 検索](/docs/ja/tools-reference#websearch-tool-behavior)</td>
      <td>✓</td>
      <td>✓</td>
      <td>✗</td>
      <td>✓</td>
      <td>注記を参照 <sup><a href="#fn1">1</a></sup></td>
      <td>✓</td>
    </tr>

    <tr>
      <td>[Fast mode](/docs/ja/fast-mode)</td>
      <td>✓</td>
      <td>✓</td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
    </tr>

    <tr>
      <td>[Auto mode](/docs/ja/auto-mode-config)</td>
      <td>✓</td>
      <td>✓</td>
      <td>注記を参照 <sup><a href="#fn2">2</a></sup></td>
      <td>✓</td>
      <td>注記を参照 <sup><a href="#fn2">2</a></sup></td>
      <td>注記を参照 <sup><a href="#fn2">2</a></sup></td>
    </tr>

    <tr>
      <td>[Advisor](/docs/ja/advisor)</td>
      <td>✓</td>
      <td>✓</td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
    </tr>

    <tr>
      <td>[Channels](/docs/ja/channels)</td>
      <td>✓</td>
      <td>✓</td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
    </tr>

    <tr>
      <td>[`/loop` スケジュール済みタスク](/docs/ja/scheduled-tasks)</td>
      <td>✓</td>
      <td>✓</td>
      <td>注記を参照 <sup><a href="#fn3">3</a></sup></td>
      <td>注記を参照 <sup><a href="#fn3">3</a></sup></td>
      <td>注記を参照 <sup><a href="#fn3">3</a></sup></td>
      <td>注記を参照 <sup><a href="#fn3">3</a></sup></td>
    </tr>

    <tr>
      <td>[GitHub Actions](/docs/ja/github-actions) と [GitLab CI/CD](/docs/ja/gitlab-ci-cd)</td>
      <td>✓</td>
      <td>✓</td>
      <td>✓</td>
      <td>✓</td>
      <td>✓</td>
      <td>✗</td>
    </tr>
  </tbody>
</table>

<h3 id="admin-and-analytics">
  管理とアナリティクス
</h3>

組織レベルのコントロールと使用状況の可視化。

<table>
  <thead>
    <tr>
      <th>機能</th>
      <th>Claude サブスクリプション</th>
      <th>Anthropic Console</th>
      <th>Amazon Bedrock</th>
      <th>Claude Platform on AWS</th>
      <th>Google Cloud の Agent Platform</th>
      <th>Microsoft Foundry</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td>[アナリティクスダッシュボードと API](/docs/ja/analytics)</td>
      <td>✓（ダッシュボード：Team および Enterprise、API：Enterprise）</td>
      <td>✓ <sup><a href="#fn5">5</a></sup></td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
    </tr>

    <tr>
      <td>[サーバー管理設定](/docs/ja/server-managed-settings)</td>
      <td>✓（Team および Enterprise）</td>
      <td>✓（Team および Enterprise）</td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
      <td>✗</td>
    </tr>

    <tr>
      <td>[Zero Data Retention](/docs/ja/zero-data-retention)</td>
      <td>✓（適格な Enterprise アカウント）</td>
      <td>✓（適格なアカウント）</td>
      <td>注記を参照 <sup><a href="#fn4">4</a></sup></td>
      <td>✓（適格なアカウント）</td>
      <td>注記を参照 <sup><a href="#fn4">4</a></sup></td>
      <td>注記を参照 <sup><a href="#fn4">4</a></sup></td>
    </tr>
  </tbody>
</table>

<span id="fn1" style={{display: 'block', position: 'relative', top: '-120px'}} /><sup>1</sup> Google Cloud の Agent Platform では、Claude 4 モデル以降で Web 検索が利用可能です。<br />
<span id="fn2" style={{display: 'block', position: 'relative', top: '-120px'}} /><sup>2</sup> これらのプロバイダーでは、Auto mode は Claude Sonnet 5、Opus 4.7、および Opus 4.8 のみをサポートしています。[Auto mode 設定](/docs/ja/auto-mode-config)を参照してください。v2.1.158 から v2.1.206 では、これらのプロバイダーの Auto mode は `CLAUDE_CODE_ENABLE_AUTO_MODE=1` の設定も必要でしたが、v2.1.207 でその要件が削除されました。<br />
<span id="fn3" style={{display: 'block', position: 'relative', top: '-120px'}} /><sup>3</sup> `/loop every 2 hours` などの明示的な間隔はすべてのプロバイダーで動作します。Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、および Microsoft Foundry では、`/loop` は独自の間隔を選択したり、デフォルトのメンテナンスプロンプトを提供したりできないため、間隔のないプロンプトは 10 分ごとに実行され、引数のない `/loop` は使用メッセージを表示します。[スケジュール済みタスク](/docs/ja/scheduled-tasks)を参照してください。<br />
<span id="fn4" style={{display: 'block', position: 'relative', top: '-120px'}} /><sup>4</sup> クラウドプロバイダーとの契約に従います。<br />
<span id="fn5" style={{display: 'block', position: 'relative', top: '-120px'}} /><sup>5</sup> ダッシュボードと API のみ。[貢献メトリクス](/docs/ja/analytics#enable-contribution-metrics)には claude.ai Team または Enterprise 組織が必要です。

<Note>
  [LLM ゲートウェイ](/docs/ja/llm-gateway)を通じて認証する場合、機能の利用可能性はゲートウェイが転送する基盤となるプロバイダーと一致します。[Advisor](/docs/ja/advisor) などの一部の Anthropic 専用機能は、ゲートウェイが要求を Anthropic API に完全に転送する場合にのみ機能します。
</Note>

<h3 id="summary-by-provider">
  プロバイダー別サマリー
</h3>

各タブには、そのプロバイダーで利用不可または部分的にサポートされている機能と、存在する場合は代替案が記載されています。記載されていないすべてのものは Claude サブスクリプションと同じように動作します。ただし、上記で説明した[プロバイダー固有の違い](#features-available-on-every-provider)は除きます。Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、および Claude Platform on AWS では、Anthropic へのエラー報告とテレメトリはデフォルトでオフです。[API プロバイダー別のデフォルト動作](/docs/ja/data-usage#default-behaviors-by-api-provider)を参照して、どのトラフィックが Anthropic に到達し、オプトアウトする方法を確認してください。

<Tabs>
  <Tab title="Amazon Bedrock">
    **利用不可：** すべての [Claude サブスクリプションが必要な機能](#features-that-require-a-claude-subscription)、および [Web 検索](/docs/ja/tools-reference#websearch-tool-behavior)、[Fast mode](/docs/ja/fast-mode)、[Advisor](/docs/ja/advisor)、[Channels](/docs/ja/channels)、[アナリティクスダッシュボード](/docs/ja/analytics)、[サーバー管理設定](/docs/ja/server-managed-settings)、および [`/design-sync` と `/radio` コマンド](/docs/ja/commands#all-commands)。

    **部分的なサポート：**

    * [Desktop](/docs/ja/desktop)：[Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview) 経由のみ
    * [Auto mode](/docs/ja/auto-mode-config)：Sonnet 5、Opus 4.7、および Opus 4.8 のみ
    * [`/loop`](/docs/ja/scheduled-tasks)：明示的な間隔のみ
    * [Zero Data Retention](/docs/ja/zero-data-retention)：AWS 契約に従う

    **代替案：** スケジューリングの場合、`/schedule` の代わりに明示的な間隔で [`/loop`](/docs/ja/scheduled-tasks) を使用してください。クラウドセッションの場合、[GitHub Actions](/docs/ja/github-actions) または [GitLab CI/CD](/docs/ja/gitlab-ci-cd) を使用してください。Web ルックアップの場合、特定の URL で [WebFetch ツール](/docs/ja/tools-reference#webfetch-tool-behavior)を使用してください。
  </Tab>

  <Tab title="Claude Platform on AWS">
    **利用不可：** すべての [Claude サブスクリプションが必要な機能](#features-that-require-a-claude-subscription)、[Fast mode](/docs/ja/fast-mode)、[Advisor](/docs/ja/advisor)、[Channels](/docs/ja/channels)、[アナリティクスダッシュボード](/docs/ja/analytics)、[サーバー管理設定](/docs/ja/server-managed-settings)、および [`/design-sync` と `/radio` コマンド](/docs/ja/commands#all-commands)。

    **Amazon Bedrock では利用不可の場合に利用可能：** [Web 検索](/docs/ja/tools-reference#websearch-tool-behavior)。

    **部分的なサポート：**

    * [`/loop`](/docs/ja/scheduled-tasks)：明示的な間隔のみ

    **代替案：** スケジューリングの場合、`/schedule` の代わりに明示的な間隔で [`/loop`](/docs/ja/scheduled-tasks) を使用してください。クラウドセッションの場合、[GitHub Actions](/docs/ja/github-actions) または [GitLab CI/CD](/docs/ja/gitlab-ci-cd) を使用してください。
  </Tab>

  <Tab title="Google Cloud の Agent Platform">
    **利用不可：** すべての [Claude サブスクリプションが必要な機能](#features-that-require-a-claude-subscription)、[Fast mode](/docs/ja/fast-mode)、[Advisor](/docs/ja/advisor)、[Channels](/docs/ja/channels)、[アナリティクスダッシュボード](/docs/ja/analytics)、[サーバー管理設定](/docs/ja/server-managed-settings)、および [`/design-sync` と `/radio` コマンド](/docs/ja/commands#all-commands)。

    **部分的なサポート：**

    * [Desktop](/docs/ja/desktop)：[管理設定](https://claude.com/docs/third-party/claude-desktop/configuration)または [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview) 経由
    * [Web 検索](/docs/ja/tools-reference#websearch-tool-behavior)：Claude 4 モデル以降
    * [Auto mode](/docs/ja/auto-mode-config)：Sonnet 5、Opus 4.7、および Opus 4.8 のみ
    * [`/loop`](/docs/ja/scheduled-tasks)：明示的な間隔のみ
    * [Zero Data Retention](/docs/ja/zero-data-retention)：Google Cloud 契約に従う

    **代替案：** スケジューリングの場合、`/schedule` の代わりに明示的な間隔で [`/loop`](/docs/ja/scheduled-tasks) を使用してください。クラウドセッションの場合、[GitHub Actions](/docs/ja/github-actions) または [GitLab CI/CD](/docs/ja/gitlab-ci-cd) を使用してください。
  </Tab>

  <Tab title="Microsoft Foundry">
    **利用不可：** すべての [Claude サブスクリプションが必要な機能](#features-that-require-a-claude-subscription)、[Fast mode](/docs/ja/fast-mode)、[Advisor](/docs/ja/advisor)、[Channels](/docs/ja/channels)、[GitHub Actions](/docs/ja/github-actions) と [GitLab CI/CD](/docs/ja/gitlab-ci-cd)、[アナリティクスダッシュボード](/docs/ja/analytics)、[サーバー管理設定](/docs/ja/server-managed-settings)、および [`/design-sync` と `/radio` コマンド](/docs/ja/commands#all-commands)。

    **部分的なサポート：**

    * [Desktop](/docs/ja/desktop)：[Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview) 経由のみ
    * [Auto mode](/docs/ja/auto-mode-config)：Sonnet 5、Opus 4.7、および Opus 4.8 のみ
    * [`/loop`](/docs/ja/scheduled-tasks)：明示的な間隔のみ
    * [Zero Data Retention](/docs/ja/zero-data-retention)：Azure 契約に従う

    **代替案：** スケジューリングの場合、明示的な間隔で [`/loop`](/docs/ja/scheduled-tasks) を使用してください。`/schedule` の代わりに。
  </Tab>

  <Tab title="Anthropic Console">
    **利用不可：** すべての [Claude サブスクリプションが必要な機能](#features-that-require-a-claude-subscription)。

    [プロバイダーによって異なる CLI 機能](#cli-capabilities-that-vary-by-provider)のすべてが利用可能であり、API キーが Team または Enterprise 組織に属する場合は [サーバー管理設定](/docs/ja/server-managed-settings)も利用可能です。
  </Tab>
</Tabs>

<h2 id="availability-by-subscription-plan">
  サブスクリプションプラン別の利用可能性
</h2>

Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、または Anthropic Console API キーを通じて認証する場合、このセクションは適用されません。claude.ai アカウントでサインインすると、プランによって以下の機能の利用可能性が決まります。

| 機能                                                                          | Pro | Max | Team          | Enterprise                        |
| :-------------------------------------------------------------------------- | :-- | :-- | :------------ | :-------------------------------- |
| [Web 上の Claude Code](/docs/ja/claude-code-on-the-web)                            | ✓   | ✓   | ✓             | ✓ <sup><a href="#fn6">6</a></sup> |
| [Routines](/docs/ja/routines)                                                    | ✓   | ✓   | ✓             | ✓                                 |
| [Remote Control](/docs/ja/remote-control)                                        | ✓   | ✓   | Admin-enabled | Admin-enabled                     |
| [Channels](/docs/ja/channels)                                                    | ✓   | ✓   | Admin-enabled | Admin-enabled                     |
| [Computer use](/docs/ja/computer-use)                                            | ✓   | ✓   | ✗             | ✗                                 |
| Dispatch（[Desktop](/docs/ja/desktop#sessions-from-dispatch)）                     | ✓   | ✓   | ✗             | ✗                                 |
| [Code Review](/docs/ja/code-review)                                              | ✗   | ✗   | ✓             | ✓                                 |
| [Artifacts](/docs/ja/artifacts)                                                  | ✓   | ✓   | ✓             | Admin-enabled                     |
| [アナリティクスダッシュボードと貢献メトリクス](/docs/ja/analytics)                                     | ✗   | ✗   | ✓             | ✓                                 |
| [Enterprise Analytics API](/docs/ja/analytics#access-data-programmatically)      | ✗   | ✗   | ✗             | ✓                                 |
| [サーバー管理設定](/docs/ja/server-managed-settings)                                     | ✗   | ✗   | ✓             | ✓                                 |
| [SSO](https://support.claude.com/en/articles/9266767-what-is-the-team-plan) | ✗   | ✗   | ✓             | ✓                                 |
| SCIM                                                                        | ✗   | ✗   | ✗             | ✓                                 |
| [Compliance API](https://platform.claude.com/docs/en/api/compliance)        | ✗   | ✗   | ✗             | ✓                                 |
| [Zero Data Retention](/docs/ja/zero-data-retention)                              | ✗   | ✗   | ✗             | ✓ <sup><a href="#fn7">7</a></sup> |

<span id="fn6" style={{display: 'block', position: 'relative', top: '-120px'}} /><sup>6</sup> Enterprise では、プレミアムシートまたは Chat + Claude Code シートが必要です。[Web 上の Claude Code](/docs/ja/claude-code-on-the-web)を参照してください。<br />
<span id="fn7" style={{display: 'block', position: 'relative', top: '-120px'}} /><sup>7</sup> 標準 Enterprise プランに含まれていません。適格なアカウントについては Anthropic による個別の有効化が必要です。[Zero Data Retention](/docs/ja/zero-data-retention)を参照してください。

価格設定と完全なプラン比較については、[Team プラン](https://support.claude.com/en/articles/9266767-what-is-the-team-plan)と [Enterprise プラン](https://support.claude.com/en/articles/9797531-what-is-the-enterprise-plan)を参照してください。

<h2 id="model-availability">
  モデルの利用可能性
</h2>

プロバイダーとリージョンごとに利用可能な Claude モデルとコンテキストウィンドウサイズについては、[モデル設定](/docs/ja/model-config)と [モデル概要](https://platform.claude.com/docs/en/about-claude/models/overview)を参照してください。Vision、PDF 入力、および拡張思考はモデル機能であり Claude Code 機能ではなく、モデルを提供するすべてのプロバイダーで動作します。[Prompt caching](/docs/ja/prompt-caching) はほとんどのプロバイダーで同じように動作します。Amazon Bedrock では、サポートはモデルによって異なります。

<h2 id="related-resources">
  関連リソース
</h2>

* [エンタープライズデプロイメント概要](/docs/ja/third-party-integrations)：プロバイダー全体で認証、請求、およびリージョンを比較
* プロバイダーセットアップガイド：[Amazon Bedrock](/docs/ja/amazon-bedrock)、[Claude Platform on AWS](/docs/ja/claude-platform-on-aws)、[Google Cloud の Agent Platform](/docs/ja/google-vertex-ai)、[Microsoft Foundry](/docs/ja/microsoft-foundry)
* [プラットフォームと統合](/docs/ja/platforms)：CLI、Desktop、IDE 拡張機能、Web、モバイル、CI/CD を含む Claude Code が実行される場所
