> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# ゲートウェイを通じて Claude Code を実行する

> Claude Code を自社ホスト型ゲートウェイ経由でルーティングして、認証情報の一元管理、使用状況の追跡、コスト管理を実現します。アーキテクチャ、Anthropic の Claude apps ゲートウェイ、および他のゲートウェイ製品の使用方法について説明します。

ゲートウェイは、Claude Code とモデルプロバイダーの間に組織が配置するプロキシです。Claude Code は API トラフィックをプロバイダーに直接送信するのではなく、ゲートウェイに送信し、ゲートウェイが組織が保有する認証情報を使用してそれを転送します。開発者はプロバイダーの認証情報を保有する代わりにゲートウェイに認証するため、認証、使用状況の追跡、予算、監査ログが、あなたが管理する 1 つの場所で行われます。

Claude Code には自社ホスト型ゲートウェイである [Claude apps ゲートウェイ](/docs/ja/claude-apps-gateway) が `claude` バイナリに含まれているため、ゲートウェイを実行するために別のゲートウェイ製品を採用する必要はありません。組織が既に [LLM ゲートウェイ](/docs/ja/llm-gateway) を実行している場合、Claude Code はそれでも機能します。

このページでは、以下について説明します。

* [ゲートウェイが Claude Code とプロバイダーの間にどのように位置するか](#how-a-gateway-works)
* [Claude apps ゲートウェイと既に実行しているゲートウェイの選択](#choose-a-gateway)
* [ゲートウェイが claude.ai サブスクリプションとどのように相互作用するか](#subscriptions-and-gateways)
* [ゲートウェイとは別に設定されるもの](#configure-separately-from-the-gateway)

<h2 id="how-a-gateway-works">
  ゲートウェイの仕組み
</h2>

各開発者の Claude Code はゲートウェイのアドレスを指すように設定され、ゲートウェイが発行した認証情報で認証します。

ゲートウェイは開発者を認証し、設定したアクセスおよび予算ルールを適用し、組織の認証情報を使用してリクエストをプロバイダーに転送します。プロバイダーは Anthropic の API または Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry などの [クラウドプロバイダー](/docs/ja/third-party-integrations) である可能性があります。ゲートウェイの設定によって決定されます。Claude apps ゲートウェイ、または単一の Anthropic 形式エンドポイントを公開する別のゲートウェイを使用する場合、プロバイダーを変更しても開発者マシンに触れる必要はありません。

<Frame>
  <img src="https://mintcdn.com/claude-code/-uq-4JE0W_JO5Er5/images/llm-gateway-flow.svg?fit=max&auto=format&n=-uq-4JE0W_JO5Er5&q=85&s=1c1a8dcc0cfcc3a58652cc8e28cd3e20" alt="Claude Code がゲートウェイを通じてルーティングされることを示す図。開発者マシンゾーンでは、Claude Code CLI と VS Code 拡張機能が、開発者ごとの認証情報を使用してゲートウェイアドレスにリクエストを送信します。あなたのインフラストラクチャというラベルのゾーンでは、ゲートウェイが認証、使用状況の追跡、予算、ルーティングを処理し、組織の認証情報を使用してリクエストを転送します。モデルプロバイダーゾーンでは、実線矢印が設定したプロバイダー（Anthropic API として表示）に向かい、破線矢印が他のプロバイダーオプション（Amazon Bedrock、Google Cloud、Microsoft Foundry の例として示されている）に向かいます。" width="780" height="322" data-path="images/llm-gateway-flow.svg" />
</Frame>

2 種類の認証情報が関係しています。

* **開発者認証情報**: 各開発者が保有し、ゲートウェイによって発行されます。ゲートウェイに対して認証し、使用状況の追跡で開発者を識別します
* **プロバイダー認証情報**: ゲートウェイが保有し、プロバイダーアカウント用の 1 つの認証情報で、すべての転送されたトラフィックで共有されます

<h2 id="choose-a-gateway">
  ゲートウェイの選択
</h2>

Claude Code は Anthropic 独自のゲートウェイ、または組織が既に実行しているゲートウェイで機能します。

<h3 id="claude-apps-gateway">
  Claude apps ゲートウェイ
</h3>

Claude apps ゲートウェイは Anthropic の自社ホスト型ゲートウェイで、`claude` バイナリに含まれています。Amazon Bedrock、Claude Platform on AWS、Google Cloud、Microsoft Foundry、または Anthropic API にアップストリームとしてルーティングします。開発者は `/login` を通じて企業の ID プロバイダーでサインインし、ゲートウェイは IdP グループによってモデルアクセスと [管理設定](/docs/ja/permissions#managed-settings) を強制し、[OpenTelemetry Protocol（OTLP）](/docs/ja/monitoring-usage) 使用状況メトリクスを独自の可観測性スタックに出力します。

これは各 Claude Code リリースと共にビルドおよびテストされるため、Claude Code が送信するヘッダーとリクエストフィールドを転送します。別途保守されるゲートウェイは、各リリースでそれらのヘッダーとフィールドが変更されるため、[転送ルールを更新](/docs/ja/llm-gateway-protocol#forward-as-open-lists) する必要があります。Claude apps ゲートウェイは CLI と共にリリースされるため、最新の状態を保つリストはありません。[可用性と制限事項](/docs/ja/claude-apps-gateway#availability-and-limitations) を参照して、ゲートウェイセッションで異なる動作をする機能の小さなセットを確認してください。

ゲートウェイサインインはブラウザ SSO ステップであり、サービストークンフローはないため、サインインを承認する開発者がない CI パイプラインはそれを通じて認証できません。それらをプロバイダーに直接設定してください。Agent SDK セッションと、開発者がサインインしたマシンで実行される `claude -p` は、そのマシンのゲートウェイセッションを使用し、そのポリシーによって管理されます。[CI パイプラインとリモートマシン](/docs/ja/claude-apps-gateway#ci-pipelines-and-remote-machines) を参照してください。

[Claude apps ゲートウェイ](/docs/ja/claude-apps-gateway) を参照してデプロイしてください。

<h3 id="other-gateways">
  他のゲートウェイ
</h3>

組織が既に LLM ゲートウェイまたは API ゲートウェイを実行している場合、代わりにそれを使用できます。Anthropic は他のゲートウェイ製品を推奨、保守、または監査せず、任意のゲートウェイを通じて Claude Code を非 Claude モデルにルーティングすることをサポートしていません。[他の LLM ゲートウェイ](/docs/ja/llm-gateway) を参照して、管理者ロールアウトチェックリスト、ゲートウェイが実装する必要があるもの、および Claude Code をそれに指すようにする方法を確認してください。

<h2 id="subscriptions-and-gateways">
  サブスクリプションとゲートウェイ
</h2>

開発者がゲートウェイ認証情報を使用してゲートウェイ経由で接続する場合、使用状況は API レートで組織のプロバイダーアカウントに請求され、claude.ai サブスクリプションは使用または請求されません。実行するゲートウェイの [`ANTHROPIC_AUTH_TOKEN`](/docs/ja/env-vars) を設定するか、`/login` で Claude apps ゲートウェイにサインインすると、そのセッションのサブスクリプションログインがオフになります。その認証情報の下で転送されるすべてのリクエストは、ゲートウェイのプロバイダー認証情報の背後にあるアカウントに請求されます。

例外は、ゲートウェイ認証情報なしで `ANTHROPIC_BASE_URL` のみを設定することです。リクエストはまだゲートウェイを通じてルーティングされますが、保存された claude.ai ログインはアクティブな認証情報のままなので、サブスクリプションの使用制限と請求が適用されます。[他の LLM ゲートウェイ](/docs/ja/llm-gateway#subscriptions-and-gateways) はその設定とゲートウェイが機能するために転送する必要があるものについて説明しています。

<h2 id="configure-separately-from-the-gateway">
  ゲートウェイとは別に設定する
</h2>

ゲートウェイはモデル API リクエストをルーティングします。ゲートウェイが処理することを期待するかもしれないいくつかのことは、別の場所で設定されます。

* **どのモデルが応答するか**: `/model` コマンドまたは [モデル環境変数](/docs/ja/model-config#setting-your-model) でモデルを選択します。ゲートウェイはリクエストがどこに行くかを決定し、開発者が選択するモデルではありません。Claude apps ゲートウェイはグループごとの `availableModels` 許可リストで選択を制限できますが、開発者はそれ以内で選択します。
* **その他のネットワークトラフィック**: Claude Code 自体はバージョンチェックをダウンロードし、ゲートウェイパスとは別に Anthropic に直接ダウンロードします。オプションのクライアントテレメトリストリームも含まれるかどうかはプロバイダーによって異なります。[テレメトリデフォルトテーブル](/docs/ja/data-usage#telemetry-services) は各ケースについて説明しています。サインインした Claude apps ゲートウェイセッションでは、ゲートウェイ認証情報は Anthropic バウンド分析を無効にし、[テレメトリ転送](/docs/ja/claude-apps-gateway-config#telemetry) が設定されている場合、OTLP エクスポートをゲートウェイにピン留めします。ネットワークはまだ [必要なドメイン](/docs/ja/network-config) へのエグレスが必要です。または [`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`](/docs/ja/env-vars) を設定してオプションストリームをオフにします。
* **企業 HTTP プロキシ**: `HTTPS_PROXY` は Claude Code とそれが通信するすべてのサーバー（ゲートウェイを含む）の間に位置します。ネットワークが必要な場合、ゲートウェイに加えて [プロキシを設定](/docs/ja/network-config) してください。Claude apps ゲートウェイの場合、[サインインはプロキシホストもプライベートネットワーク上にあることを確認します](/docs/ja/claude-apps-gateway#prerequisites)。そうでない場合、ゲートウェイホストを `NO_PROXY` に追加して、CLI がそれに直接接続するようにします。

<h2 id="next-steps">
  次のステップ
</h2>

次のページはゲートウェイを実行する人によって異なります。Anthropic のゲートウェイは `claude` バイナリから実行され、独自のセットアップガイドがあります。組織が既に実行しているゲートウェイには、実装するプロトコルと管理者ロールアウトチェックリストがあります。

* [Claude apps ゲートウェイ](/docs/ja/claude-apps-gateway) - SSO サインインと OTLP テレメトリを使用して Anthropic の自社ホスト型ゲートウェイをデプロイする
* [他の LLM ゲートウェイ](/docs/ja/llm-gateway) - 組織が既に実行しているゲートウェイが実装する必要があるもの、および Claude Code をそれに指すようにする方法
* [組織向けに Claude Code をセットアップする](/docs/ja/admin-setup) - ゲートウェイが 1 つの部分である、より広いロールアウト決定
