> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 一般的なワークフロー

> Claude Code を使用してコードベースの探索、バグ修正、リファクタリング、テスト、その他の日常的なタスクを実行するためのステップバイステップガイド。

このページでは、日常的な開発のための短いレシピを集めています。プロンプティングとコンテキスト管理に関する高度なガイダンスについては、[ベストプラクティス](/docs/ja/best-practices)を参照してください。

このページでは以下をカバーしています：

* [プロンプトレシピ](#prompt-recipes)：コード探索、バグ修正、リファクタリング、テスト、PR、ドキュメント用
* [以前の会話を再開する](#resume-previous-conversations)：タスクを複数回に分けて実行できるようにする
* [worktree を使用して並列セッションを実行する](#run-parallel-sessions-with-worktrees)：同時編集が衝突しないようにする
* [編集前に計画する](#plan-before-editing)：ディスクに変更を加える前に確認する
* [研究を subagent に委譲する](#delegate-research-to-subagents)：メインコンテキストをクリーンに保つ
* [Claude をスクリプトにパイプする](#pipe-claude-into-scripts)：CI とバッチ処理用

<h2 id="prompt-recipes">
  プロンプトレシピ
</h2>

これらは、未知のコード探索、デバッグ、リファクタリング、テスト作成、PR 作成などの日常的なタスク用のプロンプトパターンです。各パターンは任意の Claude Code サーフェスで機能します。プロジェクトに合わせて表現を調整してください。

<h3 id="understand-new-codebases">
  新しいコードベースを理解する
</h3>

モノレポまたは大規模なコードベースで Claude Code を設定する場合は、[モノレポと大規模リポジトリ](/docs/ja/large-codebases)を参照してください。

<h4 id="get-a-quick-codebase-overview">
  コードベースの概要を素早く把握する
</h4>

新しいプロジェクトに参加したばかりで、その構造を素早く理解する必要があるとします。

<Steps>
  <Step title="プロジェクトルートディレクトリに移動する">
    ```bash theme={null}
    cd /path/to/project 
    ```
  </Step>

  <Step title="Claude Code を起動する">
    ```bash theme={null}
    claude 
    ```
  </Step>

  <Step title="高レベルの概要をリクエストする">
    ```text theme={null}
    give me an overview of this codebase
    ```
  </Step>

  <Step title="特定のコンポーネントについてさらに詳しく調べる">
    ```text theme={null}
    explain the main architecture patterns used here
    ```

    ```text theme={null}
    what are the key data models?
    ```

    ```text theme={null}
    how is authentication handled?
    ```
  </Step>
</Steps>

<Tip>
  ヒント：

  * 広い質問から始めて、特定の領域に絞り込んでいく
  * プロジェクトで使用されているコーディング規約とパターンについて質問する
  * プロジェクト固有の用語の用語集をリクエストする
</Tip>

<h4 id="find-relevant-code">
  関連するコードを見つける
</h4>

特定の機能または機能に関連するコードを見つける必要があるとします。

<Steps>
  <Step title="Claude に関連ファイルを見つけるよう依頼する">
    ```text theme={null}
    find the files that handle user authentication
    ```
  </Step>

  <Step title="コンポーネントがどのように相互作用するかについてのコンテキストを取得する">
    ```text theme={null}
    how do these authentication files work together?
    ```
  </Step>

  <Step title="実行フローを理解する">
    ```text theme={null}
    trace the login process from front-end to database
    ```
  </Step>
</Steps>

<Tip>
  ヒント：

  * 探しているものについて具体的に説明する
  * プロジェクトのドメイン言語を使用する
  * 言語の[コード インテリジェンス プラグイン](/docs/ja/discover-plugins#code-intelligence)をインストールして、Claude に正確な'定義に移動'と'参照を検索'のナビゲーションを提供する
</Tip>

***

<h3 id="fix-bugs-efficiently">
  バグを効率的に修正する
</h3>

エラーメッセージが表示され、そのソースを見つけて修正する必要があるとします。

<Steps>
  <Step title="Claude とエラーを共有する">
    ```text theme={null}
    I'm seeing an error when I run npm test
    ```
  </Step>

  <Step title="修正の推奨事項をリクエストする">
    ```text theme={null}
    suggest a few ways to fix the @ts-ignore in user.ts
    ```
  </Step>

  <Step title="修正を適用する">
    ```text theme={null}
    update user.ts to add the null check you suggested
    ```
  </Step>
</Steps>

<Tip>
  ヒント：

  * Claude に問題を再現するコマンドとスタックトレースを伝える
  * エラーを再現するための手順を記載する
  * エラーが断続的か一貫しているかを Claude に知らせる
</Tip>

***

<h3 id="refactor-code">
  コードをリファクタリングする
</h3>

古いコードを最新のパターンとプラクティスを使用するように更新する必要があるとします。

<Steps>
  <Step title="リファクタリング対象のレガシーコードを特定する">
    ```text theme={null}
    find deprecated API usage in our codebase
    ```
  </Step>

  <Step title="リファクタリングの推奨事項を取得する">
    ```text theme={null}
    suggest how to refactor utils.js to use modern JavaScript features
    ```
  </Step>

  <Step title="変更を安全に適用する">
    ```text theme={null}
    refactor utils.js to use ES2024 features while maintaining the same behavior
    ```
  </Step>

  <Step title="リファクタリングを検証する">
    ```text theme={null}
    run tests for the refactored code
    ```
  </Step>
</Steps>

<Tip>
  ヒント：

  * Claude に最新のアプローチの利点を説明するよう依頼する
  * 必要に応じて変更が後方互換性を維持することをリクエストする
  * リファクタリングを小さくテスト可能な増分で実行する
</Tip>

***

<h3 id="work-with-tests">
  テストを使用する
</h3>

カバーされていないコードのテストを追加する必要があるとします。

<Steps>
  <Step title="テストされていないコードを特定する">
    ```text theme={null}
    find functions in NotificationsService.swift that are not covered by tests
    ```
  </Step>

  <Step title="テストスキャフォルディングを生成する">
    ```text theme={null}
    add tests for the notification service
    ```
  </Step>

  <Step title="意味のあるテストケースを追加する">
    ```text theme={null}
    add test cases for edge conditions in the notification service
    ```
  </Step>

  <Step title="テストを実行して検証する">
    ```text theme={null}
    run the new tests and fix any failures
    ```
  </Step>
</Steps>

Claude は、プロジェクトの既存のパターンと規約に従うテストを生成できます。テストをリクエストするときは、検証したい動作について具体的に説明してください。Claude は既存のテストファイルを調べて、既に使用されているスタイル、フレームワーク、アサーションパターンに一致させます。

包括的なカバレッジのために、Claude に見落とした可能性のあるエッジケースを特定するよう依頼してください。Claude はコードパスを分析し、エラー条件、境界値、見落としやすい予期しない入力のテストを提案できます。

***

<h3 id="create-pull-requests">
  プルリクエストを作成する
</h3>

Claude に直接プルリクエストを作成するよう依頼するか（「create a pr for my changes」）、ステップバイステップで Claude をガイドできます：

<Steps>
  <Step title="変更内容を要約する">
    ```text theme={null}
    summarize the changes I've made to the authentication module
    ```
  </Step>

  <Step title="プルリクエストを生成する">
    ```text theme={null}
    create a pr
    ```
  </Step>

  <Step title="レビューと改善">
    ```text theme={null}
    enhance the PR description with more context about the security improvements
    ```
  </Step>
</Steps>

`gh pr create` を使用して PR を作成すると、セッションはその PR に自動的にリンクされます。後で `claude --from-pr 123` で再開するか（123 を PR 番号に置き換えます）、[`/resume` ピッカー](/docs/ja/sessions#use-the-session-picker)の検索に PR URL を貼り付けることで再開できます。

<Tip>
  Claude が生成した PR を送信する前にレビューし、Claude に潜在的なリスクや考慮事項を強調するよう依頼してください。
</Tip>

<h3 id="handle-documentation">
  ドキュメントを処理する
</h3>

コードのドキュメントを追加または更新する必要があるとします。

<Steps>
  <Step title="ドキュメント化されていないコードを特定する">
    ```text theme={null}
    find functions without proper JSDoc comments in the auth module
    ```
  </Step>

  <Step title="ドキュメントを生成する">
    ```text theme={null}
    add JSDoc comments to the undocumented functions in auth.js
    ```
  </Step>

  <Step title="レビューと改善">
    ```text theme={null}
    improve the generated documentation with more context and examples
    ```
  </Step>

  <Step title="ドキュメントを検証する">
    ```text theme={null}
    check if the documentation follows our project standards
    ```
  </Step>
</Steps>

<Tip>
  ヒント：

  * 必要なドキュメントスタイル（JSDoc、docstring など）を指定する
  * ドキュメント内の例をリクエストする
  * パブリック API、インターフェース、複雑なロジックのドキュメントをリクエストする
</Tip>

***

<h3 id="work-in-notes-and-non-code-folders">
  ノートと非コードフォルダで作業する
</h3>

Claude Code はどのディレクトリでも機能します。ノートボルト、ドキュメントフォルダ、またはマークダウンファイルの任意のコレクション内で実行して、コードと同じ方法でコンテンツを検索、編集、再編成します。

`.claude/` ディレクトリと `CLAUDE.md` は他のツールの設定ディレクトリと並んで競合なく存在します。Claude は各ツール呼び出しで新しくファイルを読み込むため、別のアプリケーションで行った編集は次回そのファイルを読み込むときに表示されます。

***

<h3 id="work-with-images">
  画像を使用する
</h3>

コードベース内の画像を使用する必要があり、Claude の画像コンテンツ分析を支援したいとします。

<Steps>
  <Step title="会話に画像を追加する">
    次のいずれかの方法を使用できます：

    1. Claude Code ウィンドウに画像をドラッグアンドドロップする
    2. 画像をコピーして、CLI に Ctrl+V で貼り付ける。macOS では、iTerm2 でも Cmd+V が機能します。
    3. Claude に画像パスを提供する。例：「Analyze this image: /path/to/your/image.png」
  </Step>

  <Step title="Claude に画像を分析するよう依頼する">
    ```text theme={null}
    What does this image show?
    ```

    ```text theme={null}
    Describe the UI elements in this screenshot
    ```

    ```text theme={null}
    Are there any problematic elements in this diagram?
    ```
  </Step>

  <Step title="コンテキストに画像を使用する">
    ```text theme={null}
    Here's a screenshot of the error. What's causing it?
    ```

    ```text theme={null}
    This is our current database schema. How should we modify it for the new feature?
    ```
  </Step>

  <Step title="ビジュアルコンテンツからコード提案を取得する">
    ```text theme={null}
    Generate CSS to match this design mockup
    ```

    ```text theme={null}
    What HTML structure would recreate this component?
    ```
  </Step>
</Steps>

<Tip>
  ヒント：

  * テキスト説明が不明確または面倒な場合は画像を使用する
  * より良いコンテキストのために、エラー、UI デザイン、図のスクリーンショットを含める
  * 会話で複数の画像を使用できます
  * 画像分析は図、スクリーンショット、モックアップなどで機能します
  * Claude が画像を参照する場合（例：`[Image #1]`）、`Cmd+Click`（Mac）または `Ctrl+Click`（Windows/Linux）リンクをクリックして、デフォルトビューアで画像を開きます
</Tip>

***

<h3 id="reference-files-and-directories">
  ファイルとディレクトリを参照する
</h3>

@ を使用して、Claude に読み込まれるのを待たずにファイルまたはディレクトリをすばやく含めます。

<Steps>
  <Step title="単一ファイルを参照する">
    ```text theme={null}
    Explain the logic in @src/utils/auth.js
    ```

    これにより、ファイルの完全な内容が会話に含まれます。
  </Step>

  <Step title="ディレクトリを参照する">
    ```text theme={null}
    What's the structure of @src/components?
    ```

    これにより、ファイル情報を含むディレクトリリストが提供されます。
  </Step>

  <Step title="MCP リソースを参照する">
    ```text theme={null}
    Show me the data from @github:repos/owner/repo/issues
    ```

    これにより、@server:resource 形式を使用して接続された MCP サーバーからデータを取得します。詳細については、[MCP リソース](/docs/ja/mcp#use-mcp-resources)を参照してください。
  </Step>
</Steps>

<Tip>
  ヒント：

  * ファイルパスは相対パスまたは絶対パスにできます
  * @ ファイル参照は、ファイルのディレクトリと親ディレクトリに `CLAUDE.md` を追加してコンテキストに含めます
  * ディレクトリ参照はコンテンツではなくファイルリストを表示します
  * 単一のメッセージで複数のファイルを参照できます（例：「@file1.js and @file2.js」）
</Tip>

***

<h3 id="run-claude-on-a-schedule">
  スケジュールで Claude を実行する
</h3>

Claude に長時間実行されるタスクを自動的に定期的に処理させたいとします。例えば、毎朝オープン PR をレビューしたり、毎週依存関係を監査したり、夜間に CI の失敗をチェックしたりします。

実行場所に基づいてスケジューリングオプションを選択します：

| オプション                                            | 実行場所                   | 最適な用途                                                                                                                                        |
| :----------------------------------------------- | :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| [ルーチン](/docs/ja/routines)                             | Anthropic 管理インフラストラクチャ | コンピュータがオフの場合でも実行する必要があるタスク。[claude.ai/code/routines](https://claude.ai/code/routines)で設定します。API 呼び出しまたは GitHub イベントに加えてスケジュールでトリガーすることもできます。 |
| [デスクトップスケジュール済みタスク](/docs/ja/desktop-scheduled-tasks) | デスクトップアプリ経由のマシン        | ローカルファイル、ツール、またはコミットされていない変更への直接アクセスが必要なタスク。                                                                                                 |
| [GitHub Actions](/docs/ja/github-actions)             | CI パイプライン              | オープン PR などのリポジトリイベント、またはワークフロー設定と一緒に存在する必要がある cron スケジュールに関連するタスク。                                                                           |
| [`/loop`](/docs/ja/scheduled-tasks)                   | 現在の CLI セッション          | セッションが開いている間のクイックポーリング。タスクは新しい会話を開始すると停止します。`--resume` と `--continue` は期限切れでないものを復元します。                                                      |

<Tip>
  スケジュール済みタスク用のプロンプトを作成するときは、成功がどのように見えるか、および結果をどうするかについて明示的に説明してください。タスクは自律的に実行されるため、質問を明確にすることはできません。例えば：「`needs-review` ラベルが付いたオープン PR をレビューし、問題に関するインラインコメントを残し、`#eng-reviews` Slack チャネルに要約を投稿します。」
</Tip>

***

<h3 id="ask-claude-about-its-capabilities">
  Claude にその機能について質問する
</h3>

Claude は自分のドキュメントへの組み込みアクセスを持っており、自分の機能と制限について質問に答えることができます。

<h4 id="example-questions">
  質問例
</h4>

```text theme={null}
can Claude Code create pull requests?
```

```text theme={null}
how does Claude Code handle permissions?
```

```text theme={null}
what skills are available?
```

```text theme={null}
how do I use MCP with Claude Code?
```

```text theme={null}
how do I configure Claude Code for Amazon Bedrock?
```

```text theme={null}
what are the limitations of Claude Code?
```

<Note>
  Claude はこれらの質問に対してドキュメントベースの回答を提供します。実行可能な例と実践的なデモンストレーションについては、`/powerup` を実行してアニメーション化されたデモを含むインタラクティブレッスンを受けるか、上記の特定のワークフローセクションを参照してください。
</Note>

<Tip>
  ヒント：

  * Claude は使用しているバージョンに関係なく、常に最新の Claude Code ドキュメントにアクセスできます
  * 詳細な回答を得るために具体的な質問をする
  * Claude は MCP 統合、エンタープライズ設定、高度なワークフローなどの複雑な機能を説明できます
</Tip>

***

<h2 id="resume-previous-conversations">
  以前の会話を再開する
</h2>

タスクが複数回に分けて実行される場合は、コンテキストを再度説明するのではなく、中断したところから再開してください。Claude Code はすべての会話をローカルに保存します。

```bash theme={null}
claude --continue
```

これにより、現在のディレクトリで最新のセッションが再開されます。まだセッションがない場合は、`No conversation found to continue` と出力して終了します。`claude --resume` を使用してリストから選択するか、実行中のセッション内から `/resume` を使用してください。[セッションを管理する](/docs/ja/sessions)を参照して、名前付け、ブランチ、および完全なピッカーリファレンスを確認してください。

<h2 id="run-parallel-sessions-with-worktrees">
  worktree を使用して並列セッションを実行する
</h2>

1 つのターミナルで機能に取り組みながら、別のターミナルで Claude がバグを修正するようにします。編集が衝突しないようにしてください。各 worktree は独自のブランチ上の個別のチェックアウトです。

```bash theme={null}
claude --worktree feature-auth
```

別の名前で 2 番目のターミナルで同じコマンドを実行して、分離された並列セッションを開始します。[Worktrees](/docs/ja/worktrees)を参照して、クリーンアップ、`.worktreeinclude`、および非 git VCS サポートを確認してください。1 つの画面から並列セッションを監視するには、[バックグラウンドエージェント](/docs/ja/agent-view)を参照してください。

<h2 id="plan-before-editing">
  編集前に計画する
</h2>

ディスクに変更を加える前に確認したい変更については、計画モードに切り替えてください。Claude はファイルを読み込んで計画を提案しますが、承認されるまで編集は行いません。

```bash theme={null}
claude --permission-mode plan
```

セッション中に `Shift+Tab` を押して計画モードに切り替えることもできます。[計画モード](/docs/ja/permission-modes#analyze-before-you-edit-with-plan-mode)を参照して、承認フローとテキストエディタで計画を編集することを確認してください。

<h2 id="delegate-research-to-subagents">
  研究を subagent に委譲する
</h2>

大規模なコードベースの探索はコンテキストをファイル読み込みで満たします。探索を委譲して、結果のみが戻るようにしてください。

```text theme={null}
use a subagent to investigate how our auth system handles token refresh
```

subagent は独自のコンテキストウィンドウでファイルを読み込み、要約を報告します。[Subagents](/docs/ja/sub-agents)を参照して、独自のツールとプロンプトを持つカスタムエージェントを定義することを確認してください。

<h2 id="pipe-claude-into-scripts">
  Claude をスクリプトにパイプする
</h2>

CI、プリコミットフック、またはバッチ処理用に Claude を非対話的に実行します。stdin と stdout は任意の Unix ツールのように機能します。

```bash theme={null}
git log --oneline -20 | claude -p "summarize these recent commits"
```

[非対話モード](/docs/ja/headless)を参照して、出力形式、許可フラグ、およびファンアウトパターンを確認してください。

<h2 id="next-steps">
  次のステップ
</h2>

<CardGroup cols={2}>
  <Card title="ベストプラクティス" icon="lightbulb" href="/docs/ja/best-practices">
    Claude Code から最大限の価値を得るためのパターン
  </Card>

  <Card title="セッションを管理する" icon="rotate-left" href="/docs/ja/sessions">
    会話を再開、名前付け、ブランチする
  </Card>

  <Card title="Worktrees" icon="code-branch" href="/docs/ja/worktrees">
    分離された並列セッションを実行する
  </Card>

  <Card title="Claude Code を拡張する" icon="puzzle-piece" href="/docs/ja/features-overview">
    skill、フック、MCP、subagent、プラグインを追加する
  </Card>
</CardGroup>
