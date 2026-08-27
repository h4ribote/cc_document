> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# デスクトップアプリを始める

> Claude Code をデスクトップにインストールして、最初のコーディングセッションを開始します

デスクトップアプリは、複数のセッションを並行して実行するために構築されたグラフィカルインターフェース付きの Claude Code を提供します。並列作業を管理するためのサイドバー、統合ターミナルとファイルエディター付きのドラッグアンドドロップレイアウト、ビジュアル diff レビュー、ライブアプリプレビュー、自動マージ機能付きの GitHub PR 監視、スケジュール済みタスクがあります。ターミナルは不要です。

<CardGroup cols={3}>
  <Card title="Download for macOS" icon="apple" href="https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code&utm_medium=docs">
    Universal build for Intel and Apple Silicon
  </Card>

  <Card title="Download for Windows" icon="windows" href="https://claude.ai/api/desktop/win32/x64/setup/latest/redirect?utm_source=claude_code&utm_medium=docs">
    For x64 processors
  </Card>

  <Card title="Get Claude for Linux (beta)" icon="linux" href="/docs/en/desktop-linux">
    apt or .deb for Ubuntu and Debian
  </Card>
</CardGroup>

For Windows ARM64, download the [ARM64 installer](https://claude.ai/api/desktop/win32/arm64/setup/latest/redirect?utm_source=claude_code\&utm_medium=docs). On Linux, install with apt; see [Claude Desktop on Linux](/docs/en/desktop-linux).

<Note>
  Claude Code には [Pro、Max、Team、または Enterprise サブスクリプション](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=desktop_quickstart_pricing)が必要です。
</Note>

このページでは、アプリのインストールと最初のセッションの開始について説明します。既にセットアップが完了している場合は、[Claude Code Desktop を使用する](/docs/ja/desktop)で完全なリファレンスを参照してください。

デスクトップアプリには 3 つのタブがあります。

* **Chat**: ファイルアクセスなしの一般的な会話。claude.ai と同様です。
* **Cowork**: サンドボックス化された仮想マシン内で独自の環境を持つ自律型バックグラウンドエージェント。あなたが他の作業をしている間も独立して実行できます。オンデバイス Cowork セッションはコンピューター上で VM を実行します。リモート Cowork セッションは代わりに Anthropic 管理の VM 上で実行されます。
* **Code**: ローカルファイルへの直接アクセスを備えたインタラクティブなコーディングアシスタント。各変更をリアルタイムでレビューして承認します。

Chat と Cowork は [Claude ヘルプセンター](https://support.claude.com/)で説明されています。デスクトップアプリのインストールとデプロイは [Claude Desktop サポート記事](https://support.claude.com/en/collections/16163169-claude-desktop)で説明されています。このページは **Code** タブに焦点を当てています。

<h2 id="install">
  インストール
</h2>

<Steps>
  <Step title="インストールしてサインインする">
    macOS と Windows では、上記のリンクからインストーラーをダウンロードして実行します。Linux では、[Claude Desktop on Linux](/docs/ja/desktop-linux) のインストール手順に従ってください。macOS の Applications フォルダ、Windows の Start メニュー、または Linux のアプリケーションランチャーから Claude を起動し、Anthropic アカウントでサインインします。
  </Step>

  <Step title="Code タブを開く">
    上部中央の **Code** タブをクリックします。Code をクリックするとアップグレードを促すメッセージが表示される場合は、最初に[有料プランにサブスクライブ](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=desktop_quickstart_upgrade)する必要があります。オンラインでサインインするよう促すメッセージが表示される場合は、サインインを完了してアプリを再起動してください。403 エラーが表示される場合は、[認証のトラブルシューティング](/docs/ja/desktop#403-or-authentication-errors-in-the-code-tab)を参照してください。
  </Step>
</Steps>

デスクトップアプリには Claude Code が含まれています。Node.js または CLI を別途インストールする必要はありません。ターミナルから `claude` を使用するには、CLI を別途インストールしてください。[CLI を始める](/docs/ja/quickstart)を参照してください。

<h2 id="start-your-first-session">
  最初のセッションを開始する
</h2>

Code タブを開いた状態で、プロジェクトを選択して Claude に何かをさせます。

<Steps>
  <Step title="環境とフォルダを選択する">
    **Local** を選択して、Claude をマシン上で実行し、ファイルを直接使用します。**Select folder** をクリックして、プロジェクトディレクトリを選択します。

    <Tip>
      よく知っている小さなプロジェクトから始めてください。Claude Code が何ができるかを見るための最速の方法です。Windows では、ローカルセッションが機能するために [Git](https://git-scm.com/downloads/win) がインストールされている必要があります。ほとんどの Mac にはデフォルトで Git が含まれています。
    </Tip>

    以下も選択できます。

    * **Remote**: Anthropic のクラウドインフラストラクチャでセッションを実行します。アプリを閉じても続行します。リモートセッションは [Claude Code on the web](/docs/ja/claude-code-on-the-web) と同じインフラストラクチャを使用します。
    * **SSH**: SSH 経由でリモートマシンに接続します（独自のサーバー、クラウド VM、または dev コンテナー）。Desktop は初回接続時にリモートマシンに Claude Code を自動的にインストールします。
    * **WSL**（Windows）: [WSL 2 ディストリビューション](/docs/ja/desktop-wsl) 内でセッションを実行します。Claude Code、ツール、および git はネイティブパスで Linux 側で実行されます。
  </Step>

  <Step title="モデルを選択する">
    送信ボタンの横のドロップダウンからモデルを選択します。利用可能なモデルの比較については、[モデル](/docs/ja/model-config#available-models) を参照してください。後でこのドロップダウンから同じモデルを変更できます。
  </Step>

  <Step title="Claude に何をするかを伝える">
    Claude にしてほしいことを入力します。

    * `TODO コメントを見つけて修正する`
    * `メイン関数のテストを追加する`
    * `このコードベースの指示を含む CLAUDE.md を作成する`

    [セッション](/docs/ja/desktop#work-in-parallel-with-sessions) は、コードについて Claude との会話です。各セッションは独自のコンテキストと変更を追跡するため、複数のタスクに取り組む際に相互に干渉することなく作業できます。
  </Step>

  <Step title="変更をレビューして受け入れる">
    デフォルトでは、Code タブは [Manual mode](/docs/ja/desktop#choose-a-permission-mode) で開始されます。このモードでは、Claude が変更を提案し、適用する前にあなたの承認を待ちます。以下が表示されます。

    1. 各ファイルで何が変わるかを正確に示す [diff ビュー](/docs/ja/desktop#review-changes-with-diff-view)
    2. 各変更を承認または拒否する Accept/Reject ボタン
    3. Claude があなたのリクエストを処理する際のリアルタイム更新

    変更を拒否すると、Claude は別の方法で進めたいかを尋ねます。あなたが受け入れるまで、ファイルは変更されません。
  </Step>
</Steps>

<h2 id="now-what">
  次は何をしますか？
</h2>

最初の編集が完了しました。Desktop ができることすべての完全なリファレンスについては、[Claude Code Desktop を使用する](/docs/ja/desktop)を参照してください。次に試すべきことをいくつか紹介します。

**割り込みと操舵。** Claude をいつでも割り込むことができます。停止ボタンをクリックして直ちに割り込むか、修正を入力して **Enter** を押して実行中のアクションを停止せずに送信します。どちらの方法でも、完了を待つか最初からやり直す必要はありません。

**Claude により多くのコンテキストを提供する。** プロンプトボックスに `@filename` と入力して特定のファイルを会話に取り込み、添付ボタンを使用して画像と PDF を添付するか、ファイルをプロンプトに直接ドラッグアンドドロップします。Claude が持つコンテキストが多いほど、結果は良くなります。[ファイルとコンテキストを追加する](/docs/ja/desktop#add-files-and-context-to-prompts)を参照してください。

**繰り返し可能なタスクにスキルを使用する。** `/` を入力するか、**+** → **Slash commands** をクリックして、[組み込みコマンド](/docs/ja/commands)、[カスタムスキル](/docs/ja/skills)、およびプラグインスキルを参照します。スキルは、コードレビューチェックリストやデプロイメント手順など、必要なときに呼び出すことができる再利用可能なプロンプトです。

**コミット前に変更をレビューする。** Claude がファイルを編集した後、`+12 -1` インジケーターが表示されます。それをクリックして [diff ビュー](/docs/ja/desktop#review-changes-with-diff-view)を開き、ファイルごとに変更をレビューし、特定の行にコメントします。Claude はあなたのコメントを読んで修正します。**Review code** をクリックして、Claude に diff を評価させ、インライン提案を残させます。

**コントロール量を調整する。** [権限モード](/docs/ja/desktop#choose-a-permission-mode)は、Claude が承認を求めずにどの程度実行できるかを設定します。

* **Manual**: デフォルトです。Claude はファイルを編集またはコマンドを実行する前に確認を求めます。
* **Accept edits**: Claude はファイル編集を自動的に受け入れて、より高速な反復を実現します。
* **Plan**: Claude はファイルを編集せずにアプローチを提案します。これは大規模なリファクタリング前に便利です。

**プラグインを追加してさらに多くの機能を追加する。** プロンプトボックスの横の **+** ボタンをクリックして **Plugins** を選択し、スキル、エージェント、MCP servers などを追加する [プラグイン](/docs/ja/desktop#install-plugins)を参照してインストールします。

**ワークスペースを配置する。** チャット、diff、ターミナル、ファイル、ブラウザペインを好きなレイアウトにドラッグします。**Ctrl+\`** でターミナルを開いてセッションと一緒にコマンドを実行するか、ファイルパスをクリックしてファイルペインで開きます。[ワークスペースを配置する](/docs/ja/desktop#arrange-your-workspace)を参照してください。

**アプリをプレビューする。** デスクトップで開発サーバーを実行すると、アプリはブラウザペインで開きます。ブラウザペインは [外部サイトを開く](/docs/ja/desktop#browse-external-sites)こともできます。Claude は実行中のアプリを表示し、エンドポイントをテストし、ログを検査し、見たものに対して反復できます。[アプリをプレビューする](/docs/ja/desktop#preview-your-app)を参照してください。

**プルリクエストを追跡する。** PR を開いた後、Claude Code は CI チェック結果を監視し、失敗を自動的に修正するか、すべてのチェックが成功したら PR をマージできます。[プルリクエストステータスを監視する](/docs/ja/desktop#monitor-pull-request-status)を参照してください。

**Claude をスケジュールに配置する。** [スケジュール済みタスク](/docs/ja/desktop-scheduled-tasks)を設定して、Claude を定期的に自動実行します。毎朝のコードレビュー、週次の依存関係監査、または接続されたツールから取得する概要です。

**準備ができたらスケールアップする。** サイドバーから [並列セッション](/docs/ja/desktop#work-in-parallel-with-sessions)を開いて、複数のタスクに同時に取り組みます。各タスクは独自の Git worktree にあります。[タスクペイン](/docs/ja/desktop#watch-background-tasks)を開いて、セッションが実行しているサブエージェントとバックグラウンドコマンドを監視します。[サイドチャット](/docs/ja/desktop#ask-a-side-question-without-derailing-the-session)を開いて、メインスレッドを脱線させずに質問をします。[長時間実行される作業をクラウドに送信](/docs/ja/desktop#run-long-running-tasks-remotely)して、アプリを閉じても続行するか、タスクが予想より長くかかる場合は [web またはあなたの IDE でセッションを続行](/docs/ja/desktop#continue-in-another-surface)します。[GitHub、Slack、Linear などの外部ツールを接続](/docs/ja/desktop#extend-claude-code)して、ワークフローをまとめます。

<h2 id="coming-from-the-cli">
  CLI から来ましたか？
</h2>

Desktop は、グラフィカルインターフェース付きの CLI と同じエンジンを実行します。同じプロジェクトで両方を同時に実行でき、設定（CLAUDE.md ファイル、MCP servers、hooks、skills、設定）を共有します。機能、フラグの同等物、Desktop で利用できないものの完全な比較については、[CLI 比較](/docs/ja/desktop#coming-from-the-cli)を参照してください。

<h2 id="what’s-next">
  次のステップ
</h2>

* [Claude Code Desktop を使用する](/docs/ja/desktop): 権限モード、並列セッション、diff ビュー、コネクター、エンタープライズ設定
* [トラブルシューティング](/docs/ja/desktop#troubleshooting): 一般的なエラーとセットアップの問題の解決策
* [ベストプラクティス](/docs/ja/best-practices): 効果的なプロンプトを書き、Claude Code を最大限に活用するためのヒント
* [一般的なワークフロー](/docs/ja/common-workflows): デバッグ、リファクタリング、テストなどのチュートリアル
