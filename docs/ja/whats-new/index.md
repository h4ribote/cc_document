> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 新機能

> Claude Code の注目すべき機能を毎週紹介するダイジェスト。コードスニペット、デモ、およびそれらが重要である理由についての説明が含まれています。

週間開発ダイジェストは、あなたの仕事のやり方を変える可能性が最も高い機能をハイライトします。各エントリには実行可能なコード、短いデモ、および完全なドキュメントへのリンクが含まれています。すべてのバグ修正と軽微な改善については、[changelog](/docs/ja/changelog) を参照してください。

<Update label="Week 28" description="July 6–10, 2026" tags={["v2.1.202–v2.1.206"]}>
  **デスクトップ上のアプリ内ブラウザ**：Claude Code デスクトップはビルトインブラウザを取得し、Claude はドキュメント、デザイン、またはその他のサイトを表示して、ローカル開発サーバープレビューと同じ方法でページと対話できます。

  今週のその他の機能：**`/doctor`** は完全なセットアップチェックアップで、問題を診断して修正でき、`/checkup` がそのエイリアスです。**auto mode** はトランスクリプト改ざんをブロックし、未解決の変数で `rm -rf` の前に確認を求めます。**agent view rows** は色付きの状態単語と分類器が作成したヘッドラインを表示します。

  [Week 28 ダイジェストを読む →](/docs/ja/whats-new/2026-w28)
</Update>

<Update label="Week 27" description="June 29 – July 3, 2026" tags={["v2.1.195–v2.1.201"]}>
  **Claude Sonnet 5**：Pro、Team Standard、および Enterprise サブスクリプションシートの新しいデフォルトモデル。Sonnet 価格での最高レベルのコーディングとツール使用、ネイティブ 1M トークンコンテキストウィンドウ、およびデフォルトで有効な適応的思考を備えています。

  今週のその他の機能：**Chrome の Claude** はすべての直接 Anthropic プランで一般提供されています。**subagents はデフォルトでバックグラウンドで実行** されるため、Claude は実行中も動作し続けます。**Claude Desktop on Linux** は Ubuntu および Debian でベータ版として登場しました。**`/radio`** は Claude FM lo-fi ラジオにチューニングします。

  [Week 27 ダイジェストを読む →](/docs/ja/whats-new/2026-w27)
</Update>

<Update label="Week 26" description="June 22–26, 2026" tags={["v2.1.185–v2.1.193"]}>
  **`claude mcp login`**：インタラクティブな `/mcp` メニューの代わりに、シェルから設定済み MCP サーバーを認証し、後で `claude mcp logout` でその保存された認証情報をクリアします。

  今週のその他の機能：**シェルモードがコマンド出力に応答します**（`! npm test` は 2 番目のプロンプトなしで説明を取得します）。**`/rewind`** は `/clear` が実行される前の会話を再開できます。**バックグラウンドサブエージェント** は許可プロンプトをメインセッションに表示するようになり、自動的に拒否されなくなります。

  [Week 26 ダイジェストを読む →](/docs/ja/whats-new/2026-w26)
</Update>

<Update label="Week 25" description="June 15–19, 2026" tags={["v2.1.178–v2.1.183"]}>
  **Artifacts**：セッションの出力を claude.ai 上のライブで共有可能なページに変換し、セッションが動作するにつれてその場で更新されます。現在 Team および Enterprise プランでベータ版です。

  今週のその他の機能：**deny および ask ルール** は `Tool(param:value)` でツールパラメータにマッチします。例えば `Agent(model:opus)`。**`/config key=value`** は `-p` モードおよび Remote Control からプロンプトから任意の設定を設定します。**auto mode** は、ローカル作業を破棄するよう求めなかった場合、破壊的な git コマンドをブロックします。

  [Week 25 ダイジェストを読む →](/docs/ja/whats-new/2026-w25)
</Update>

<Update label="Week 24" description="June 8–12, 2026" tags={["v2.1.166–v2.1.176"]}>
  **`/cd`**：プロンプトキャッシュを再構築することなく、会話の途中で現在のセッションを新しい作業ディレクトリに移動します。

  今週のその他の機能：**サブエージェントは独自のサブエージェントを生成できます**（バックグラウンドチェーンは 5 レベルの深さでキャップされています）。**`--safe-mode`** はすべてのカスタマイズを無効にした状態で Claude Code を起動してトラブルシューティングを行います。**`fallbackModel`** は順番に試される最大 3 つのフォールバックモデルを設定します。

  [Week 24 ダイジェストを読む →](/docs/ja/whats-new/2026-w24)
</Update>

<Update label="Week 23" description="June 1–5, 2026" tags={["v2.1.158–v2.1.165"]}>
  **Amazon Bedrock、Google Cloud の Agent Platform、および Microsoft Foundry での Auto mode**：auto mode は Opus 4.7 および Opus 4.8 のサードパーティプロバイダーで利用可能になり、許可プロンプトをバックグラウンド安全チェックに置き換えます。

  今週のその他の機能：**より安全な自動編集** は `acceptEdits` モードでコードを実行できるファイルを書き込む前にプロンプトを表示します。**`/plugin list`** はインストール済みプラグインをインラインで出力します。**バージョン要件** により、マネージドデプロイメントは承認された Claude Code バージョン範囲を要求できます。

  [Week 23 ダイジェストを読む →](/docs/ja/whats-new/2026-w23)
</Update>

<Update label="Week 22" description="May 25–29, 2026" tags={["v2.1.150–v2.1.157"]}>
  **Claude Opus 4.8**：Max、Team Premium、Enterprise 従量課金制、および Anthropic API アカウント向けの新しいデフォルトモデル。デフォルトで高いエフォートレベルを備え、最も難しいタスク向けに `/effort xhigh` をサポートしています。

  今週のその他の機能：**dynamic workflows** は Claude が作成するスクリプトから数十から数百のサブエージェントを調整します。**security-guidance プラグイン** は Claude の変更を脆弱性についてレビューします。**fast mode** は Opus 4.8 で 1 MTok あたり $10/$50 で実行されます。

  [Week 22 ダイジェストを読む →](/docs/ja/whats-new/2026-w22)
</Update>

<Update label="Week 21" description="May 18–22, 2026" tags={["v2.1.143–v2.1.149"]}>
  **Pro プランの Auto mode**：auto mode は Pro アカウントで実行され、Opus と並行して Sonnet 4.6 をサポートし、許可プロンプトをバックグラウンド安全チェックに置き換えます。

  今週のその他の機能：**`/usage`** はスキル、サブエージェント、プラグイン、および MCP サーバーごとにプラン制限を駆動するものを分解します。新しい **`/code-review`** コマンドは正確性バグを報告します。**background sessions** は `/resume` に表示され、ピン留めされると生き続けます。

  [Week 21 ダイジェストを読む →](/docs/ja/whats-new/2026-w21)
</Update>

<Update label="Week 20" description="May 11–15, 2026" tags={["v2.1.139–v2.1.142"]}>
  **エージェントビュー**：`claude agents` は Claude Code セッションごとに 1 つの画面を開き、何が実行中か、何があなたをブロックしているか、何が完了したかを表示します。

  今週のその他の機能：**`/goal`** は完了条件が成立するまで Claude を複数ターンにわたって動作させ続けます。**fast mode** はデフォルトで Opus 4.7 で実行されるようになりました。**Rewind メニュー** は「ここまで要約」で以前のコンテキストを圧縮できます。

  [Week 20 ダイジェストを読む →](/docs/ja/whats-new/2026-w20)
</Update>

<Update label="Week 19" description="May 4–8, 2026" tags={["v2.1.128–v2.1.136"]}>
  **プラグインが `.zip` アーカイブと URL から読み込まれます**：`--plugin-dir` は `.zip` ファイルを受け入れるようになり、`--plugin-url` は現在のセッション用にプラグインアーカイブをフェッチします。

  今週のその他の機能：**`worktree.baseRef`** は新しい worktree がリモートデフォルトまたはローカル `HEAD` からブランチするかどうかを選択します。**auto mode hard deny ルール** は許可例外に関係なく無条件にアクションをブロックします。**hooks は有効なエフォートレベルを確認** できます（`effort.level` および `$CLAUDE_EFFORT` 経由）。

  [Week 19 ダイジェストを読む →](/docs/ja/whats-new/2026-w19)
</Update>

<Update label="Week 18" description="April 27 – May 1, 2026" tags={["v2.1.120–v2.1.126"]}>
  **Git Bash なしの Windows**：Git for Windows は不要になり、Bash がない場合、Claude Code は PowerShell をシェルツールとして使用します。

  今週のその他の機能：**`claude ultrareview`** はクラウドコードレビューを CI とスクリプトにもたらします。**`claude project purge`** はプロジェクトのローカル状態をクリーンアップします。**PR URL を `/resume` に貼り付ける** とそれを作成したセッションを見つけます。

  [Week 18 ダイジェストを読む →](/docs/ja/whats-new/2026-w18)
</Update>

<Update label="Week 17" description="April 20–24, 2026" tags={["v2.1.114–v2.1.119"]}>
  **`/ultrareview`** がパブリックリサーチプレビューとしてオープンしました。バグ検出エージェントのフリートがクラウドで実行され、検出結果が自動的に CLI またはデスクトップに戻ります。

  今週のその他の機能：**セッションの概要** はターミナルがフォーカスされていない間に何が起こったかを表示します。**カスタムテーマ** では `/theme` またはプラグインから色パレットを構築して配布できます。**ウェブ上の Claude Code** は新しいセッションサイドバーとドラッグアンドドロップレイアウトでリデザインされました。

  [Week 17 ダイジェストを読む →](/docs/ja/whats-new/2026-w17)
</Update>

<Update label="Week 16" description="April 13–17, 2026" tags={["v2.1.105–v2.1.113"]}>
  **Claude Opus 4.7** が Max および Team Premium の新しいデフォルトとしてリリースされました。ほとんどのコーディング作業に推奨される新しい `xhigh` エフォートレベルと、インタラクティブな `/effort` スライダーで調整できます。

  今週のその他の機能：ウェブ上の Claude Code の **Routines** はスケジュール、GitHub イベント、または API 呼び出しからテンプレート化されたクラウドエージェントを実行します。**モバイルプッシュ通知** は長いタスクが終了したときまたは Claude があなたが必要なときに電話に通知を送ります。`/usage` はあなたの制限を何が駆動しているかを表示します。CLI はネイティブバイナリに移行しました。

  [Week 16 ダイジェストを読む →](/docs/ja/whats-new/2026-w16)
</Update>

<Update label="Week 15" description="April 6–10, 2026" tags={["v2.1.92–v2.1.101"]}>
  **Ultraplan** が早期プレビューに入りました。CLI からクラウドでプランを作成し、ウェブエディタで確認およびコメントしてから、リモートで実行するか、ローカルに戻します。最初の実行は自動的にクラウド環境を作成します。

  今週のその他の機能：**Monitor** ツールはバックグラウンドイベントをストリーミングして会話に流し込むため、Claude はログをテールして実時間で反応できます。`/loop` は間隔を省略すると自動ペースします。`/team-onboarding` はセットアップを再生可能なガイドにパッケージします。`/autofix-pr` はターミナルから PR 自動修正をオンにします。

  [Week 15 ダイジェストを読む →](/docs/ja/whats-new/2026-w15)
</Update>

<Update label="Week 14" description="March 30 – April 3, 2026" tags={["v2.1.86–v2.1.91"]}>
  **Computer use** がリサーチプレビューで CLI に登場しました。Claude はネイティブアプリを開き、UI をクリックして、ターミナルから変更を確認できます。GUI でのみ確認できるものを完了するのに最適です。

  今週のその他の機能：`/powerup` インタラクティブレッスン、ちらつきのない alt スクリーンレンダリング、ツールごとの MCP 結果サイズオーバーライド（最大 500K）、および Bash ツールの `PATH` 上のプラグイン実行ファイル。

  [Week 14 ダイジェストを読む →](/docs/ja/whats-new/2026-w14)
</Update>

<Update label="Week 13" description="March 23–27, 2026" tags={["v2.1.83–v2.1.85"]}>
  **Auto mode** がリサーチプレビューでリリースされました。分類器があなたの許可プロンプトを処理するため、安全なアクションは中断なく実行され、危険なアクションはブロックされます。すべてを承認することと `--dangerously-skip-permissions` の中間地点です。

  今週のその他の機能：デスクトップアプリでのコンピュータ使用、ウェブでの PR 自動修正、`/` でのトランスクリプト検索、Windows 用のネイティブ PowerShell ツール、および条件付き `if` フック。

  [Week 13 ダイジェストを読む →](/docs/ja/whats-new/2026-w13)
</Update>
