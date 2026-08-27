> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# プラットフォームと統合

> Claude Code を実行する場所を選択し、何に接続するかを決定します。CLI、Desktop、VS Code、JetBrains、Web、モバイル、および Chrome、Slack、CI/CD などの統合を比較します。

Claude Code は、どこでも同じ基盤となるエンジンを実行しますが、各サーフェスは異なる作業方法に合わせて調整されています。このページは、ワークフローに適したプラットフォームを選択し、既に使用しているツールを接続するのに役立ちます。

<h2 id="where-to-run-claude-code">
  Claude Code を実行する場所
</h2>

プロジェクトがどこにあるか、どのように作業したいかに基づいてプラットフォームを選択します。

| プラットフォーム                          | 最適な用途                                                | 提供される機能                                                                                                                                                          |
| :-------------------------------- | :--------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [CLI](/docs/ja/quickstart)             | ターミナルワークフロー、スクリプティング、リモートサーバー                        | 完全な機能セット、[Agent SDK](/docs/ja/headless)、[コンピューター使用](/docs/ja/computer-use)（macOS の Pro および Max）、サードパーティプロバイダー                                                              |
| [Desktop](/docs/ja/desktop)            | ビジュアルレビュー、並列セッション、管理されたセットアップ                        | Diff ビューアー、アプリプレビュー、Pro および Max での[コンピューター使用](/docs/ja/desktop#let-claude-use-your-computer)および[Dispatch](/docs/ja/desktop#sessions-from-dispatch)                         |
| [VS Code](/docs/ja/vs-code)            | ターミナルに切り替えずに VS Code 内で作業                            | インラインの Diff、統合ターミナル、ファイルコンテキスト                                                                                                                                   |
| [JetBrains](/docs/ja/jetbrains)        | IntelliJ、PyCharm、WebStorm、またはその他の JetBrains IDE 内で作業 | Diff ビューアー、選択共有、ターミナルセッション                                                                                                                                       |
| [Web](/docs/ja/claude-code-on-the-web) | あまり操作が必要ない長時間実行タスク、またはオフラインの場合も続行すべき作業               | Anthropic 管理クラウド、切断後も続行                                                                                                                                          |
| モバイル                              | コンピューターから離れている間にタスクを開始および監視                          | iOS および Android 用 Claude アプリからのクラウドセッション、ローカルセッション用の[Remote Control](/docs/ja/remote-control)、Pro および Max での Desktop への[Dispatch](/docs/ja/desktop#sessions-from-dispatch) |

CLI はターミナルネイティブな作業に最も完全なサーフェスです。スクリプティングと Agent SDK は CLI のみです。サードパーティプロバイダーは[VS Code](/docs/ja/vs-code#use-third-party-providers)でも機能します。Enterprise [Desktop](/docs/ja/desktop) デプロイメントは Google Cloud の Agent Platform をサポートしており、Desktop は[ゲートウェイプロバイダー](/docs/ja/llm-gateway-connect#desktop-app)をサポートしています。Amazon Bedrock または Microsoft Foundry の場合は、CLI または VS Code を使用するか、[Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview)を使用してください。これは、それらのプロバイダーで Code タブを実行します。Desktop と IDE 拡張機能は、CLI のみの機能の一部をビジュアルレビューとより緊密なエディター統合と引き換えにします。Web は Anthropic のクラウドで実行されるため、切断後もタスクが続行されます。モバイルは、これらの同じクラウドセッションへのシンクライアント、または Remote Control 経由のローカルセッションへのシンクライアントであり、Dispatch で Desktop にタスクを送信できます。

同じプロジェクトで複数のサーフェスを混在させることができます。設定、プロジェクトメモリ、MCP サーバーはローカルサーフェス全体で共有されます。

<h2 id="connect-your-tools">
  ツールを接続する
</h2>

統合により、Claude はコードベース外のサービスと連携できます。

| 統合                                   | 機能                          | 用途                                    |
| :----------------------------------- | :-------------------------- | :------------------------------------ |
| [Chrome](/docs/ja/chrome)                 | ログインしたセッションでブラウザを制御         | Web アプリのテスト、フォーム入力、API なしでサイトを自動化     |
| [GitHub Actions](/docs/ja/github-actions) | CI パイプラインで Claude を実行       | 自動 PR レビュー、Issue トリアージ、スケジュール済みメンテナンス |
| [GitLab CI/CD](/docs/ja/gitlab-ci-cd)     | GitLab の GitHub Actions と同じ | GitLab での CI 駆動自動化                    |
| [Code Review](/docs/ja/code-review)       | すべての PR を自動的にレビュー           | 人間によるレビュー前にバグをキャッチ                    |
| [Slack](/docs/ja/slack)                   | チャネルの `@Claude` メンションに応答    | バグレポートをチームチャットから PR に変換               |

ここにリストされていない統合については、[MCP サーバー](/docs/ja/mcp)と[コネクター](/docs/ja/desktop#connect-external-tools)により、ほぼすべてのものを接続できます。Linear、Notion、Google Drive、または独自の内部 API など。

<h2 id="work-when-you-are-away-from-your-terminal">
  ターミナルから離れているときに作業する
</h2>

Claude Code offers several ways to work when you're not at your terminal. They differ in what triggers the work, where Claude runs, and how much you need to set up.

|                                                          | Trigger                                                                                        | Claude runs on                                                                               | Setup                                                                                                                                | Best for                                                      |
| :------------------------------------------------------- | :--------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------ |
| [Dispatch](/docs/en/desktop#sessions-from-dispatch)           | Message a task from the Claude mobile app                                                      | Your machine (Desktop)                                                                       | [Pair the mobile app with Desktop](https://support.claude.com/en/articles/13947068)                                                  | Delegating work while you're away, minimal setup              |
| [Remote Control](/docs/en/remote-control)                     | Drive a running session from [claude.ai/code](https://claude.ai/code) or the Claude mobile app | Your machine (CLI or VS Code)                                                                | Run `claude remote-control`                                                                                                          | Steering in-progress work from another device                 |
| [Channels](/docs/en/channels)                                 | Push events from a chat app like Telegram or Discord, or your own server                       | Your machine (CLI)                                                                           | [Install a channel plugin](/docs/en/channels#quickstart) or [build your own](/docs/en/channels-reference)                                      | Reacting to external events like CI failures or chat messages |
| [Slack](/docs/en/slack)                                       | Mention `@Claude` in a team channel                                                            | Anthropic cloud                                                                              | [Install the Slack app](/docs/en/slack#setting-up-claude-code-in-slack) with [Claude Code on the web](/docs/en/claude-code-on-the-web) enabled | PRs and reviews from team chat                                |
| [Self-hosted environments](/docs/en/self-hosted-environments) | Start a [cloud session](/docs/en/claude-code-on-the-web) and pick your organization's environment   | Your organization's infrastructure                                                           | [Deploy runners](/docs/en/self-hosted-environments-quickstart), on Team and Enterprise plans                                              | Cloud sessions that must run inside your network              |
| [Scheduled tasks](/docs/en/scheduled-tasks)                   | Set a schedule                                                                                 | [CLI](/docs/en/scheduled-tasks), [Desktop](/docs/en/desktop-scheduled-tasks), or [cloud](/docs/en/routines) | Pick a frequency                                                                                                                     | Recurring automation like daily reviews                       |

どこから始めるべきか不確かな場合は、[CLI をインストール](/docs/ja/quickstart)してプロジェクトディレクトリで実行します。ターミナルを使用したくない場合は、[Desktop](/docs/ja/desktop-quickstart) がグラフィカルインターフェースで同じエンジンを提供します。

<h2 id="related-resources">
  関連リソース
</h2>

<h3 id="platforms">
  プラットフォーム
</h3>

* [CLI クイックスタート](/docs/ja/quickstart)：ターミナルでインストールして最初のコマンドを実行
* [Desktop](/docs/ja/desktop)：ビジュアル Diff レビュー、並列セッション、コンピューター使用、Dispatch
* [VS Code](/docs/ja/vs-code)：エディター内の Claude Code 拡張機能
* [JetBrains](/docs/ja/jetbrains)：IntelliJ、PyCharm、およびその他の JetBrains IDE の拡張機能
* [Claude Code on the web](/docs/ja/claude-code-on-the-web)：切断後も実行し続けるクラウドセッション
* モバイル：コンピューターから離れている間にタスクを開始および監視するための [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) および [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude) 用 Claude アプリ

<h3 id="integrations">
  統合
</h3>

* [Chrome](/docs/ja/chrome)：ログインしたセッションでブラウザタスクを自動化
* [Computer use](/docs/ja/computer-use)：Claude が macOS でアプリを開いてスクリーンを制御できるようにする
* [GitHub Actions](/docs/ja/github-actions)：CI パイプラインで Claude を実行
* [GitLab CI/CD](/docs/ja/gitlab-ci-cd)：GitLab の場合も同じ
* [Code Review](/docs/ja/code-review)：すべてのプルリクエストで自動レビュー
* [Slack](/docs/ja/slack)：チームチャットからタスクを送信、PR を取得

<h3 id="remote-access">
  リモートアクセス
</h3>

* [Dispatch](/docs/ja/desktop#sessions-from-dispatch)：携帯電話からタスクをメッセージして Desktop セッションを生成
* [Remote Control](/docs/ja/remote-control)：携帯電話またはブラウザから実行中のセッションを操作
* [Channels](/docs/ja/channels)：チャットアプリまたは独自のサーバーからセッションにイベントをプッシュ
* [Scheduled tasks](/docs/ja/scheduled-tasks)：定期的なスケジュールでプロンプトを実行
