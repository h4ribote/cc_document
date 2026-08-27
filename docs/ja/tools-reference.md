> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# ツール リファレンス

> Claude Code が使用できるツールの完全なリファレンス（権限要件とツール別の動作を含む）

Claude Code は、コードベースを理解および変更するのに役立つ組み込みツールのセットにアクセスできます。ツール名は、[権限ルール](/docs/ja/permissions#tool-specific-permission-rules)、[subagent ツールリスト](/docs/ja/sub-agents)、および[フック マッチャー](/docs/ja/hooks)で使用する正確な文字列です。ツールを完全に無効にするには、[権限設定](/docs/ja/permissions#tool-specific-permission-rules)の `deny` 配列にその名前を追加します。

カスタム ツールを追加するには、[MCP サーバー](/docs/ja/mcp)を接続します。再利用可能なプロンプトベースのワークフローで Claude を拡張するには、[skill](/docs/ja/skills)を作成します。これは新しいツール エントリを追加するのではなく、既存の `Skill` ツールを通じて実行されます。

Permission required 列は、ツールが作業ディレクトリ内のパスに対してデフォルト権限モードでプロンプトを表示するかどうかを示します。`Read`、`Grep`、`Glob` を含むファイル アクセス ツールは No とマークされていますが、[作業ディレクトリと追加ディレクトリ](/docs/ja/permissions#working-directories)外のパスに対してはプロンプトを表示します。`Bash` は Yes とマークされていますが、プロンプトなしで組み込みの[読み取り専用コマンド](/docs/ja/permissions#read-only-commands)セットを実行します。

| ツール                    | 説明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 権限が必要 |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---- |
| `Agent`                | 独自のコンテキストウィンドウを持つ [subagent](/docs/ja/sub-agents)を生成してタスクを処理します。[Agent ツールの動作](#agent-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | いいえ   |
| `Artifact`             | HTML または Markdown ファイルを [artifact](/docs/ja/artifacts)として公開します：claude.ai 上の非公開でインタラクティブなページで、組織内で共有できます。Pro、Max、Team、または Enterprise プランが必要で、`/login` 認証が必要です。[可用性](/docs/ja/artifacts#availability)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | はい    |
| `AskUserQuestion`      | 要件を収集したり曖昧さを明確にするために複数選択肢の質問をします。質問は回答するまで開いたままです：デフォルトではアイドル タイムアウトはありません。アイドル ダイアログを自動的に続行させるには、ユーザー `settings.json` または `/config` の **Question auto-continue timeout** 行で [`askUserQuestionTimeout`](/docs/ja/settings#available-settings) 設定を `60s`、`5m`、または `10m` に設定します。選択したアイドル時間が経過してから入力がない場合、ダイアログは自動的に閉じます：既に選択したオプションを送信し、キーボードから離れている可能性があることを Claude に伝えるため、Claude は独自の判断で進行し、後で再度質問できます。最後の 20 秒間はカウントダウンが表示されます。キープレスはタイマーを再開し、フォーカスを報告するターミナルのフォーカスされたウィンドウも同様です。タイムアウトは `AskUserQuestion` の複数選択肢の質問にのみ適用されます。権限プロンプト（プラン承認を含む）は、アイドル時に自動解決されることはありません。v2.1.198 および v2.1.199 では、ダイアログはデフォルトで 60 秒のアイドル後に自動的に続行され、[`CLAUDE_AFK_TIMEOUT_MS`](/docs/ja/env-vars#variables)がそれを変更する唯一の方法でした | いいえ   |
| `Bash`                 | 環境でシェル コマンドを実行します。[Bash ツールの動作](#bash-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | はい    |
| `CronCreate`           | 現在のセッション内で定期的または 1 回限りのプロンプトをスケジュールします。タスクはセッションスコープであり、`--resume` または `--continue` で復元されます（有効期限が切れていない場合）。[スケジュール済みタスク](/docs/ja/scheduled-tasks)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | いいえ   |
| `CronDelete`           | ID でスケジュール済みタスクをキャンセルします                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | いいえ   |
| `CronList`             | セッション内のすべてのスケジュール済みタスクをリストします                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | いいえ   |
| `Edit`                 | 特定のファイルに対して対象を絞った編集を行います。[Edit ツールの動作](#edit-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | はい    |
| `EnterPlanMode`        | Plan Mode に切り替えてコーディング前にアプローチを設計します                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | いいえ   |
| `EnterWorktree`        | 分離された [git worktree](/docs/ja/worktrees)を作成してそこに切り替えます。現在のリポジトリの既存の worktree に切り替えるには、新しいものを作成する代わりに `path` を渡します。最初のエントリでは、ターゲットは現在のリポジトリの worktree、またはマルチリポジトリ ワークスペースでは、その中にネストされたリポジトリの worktree である可能性があります。v2.1.203 より前では、ネストされたリポジトリの worktree は拒否されました。`.claude/worktrees/` の外の `path` はセッションの作業ディレクトリと書き込みアクセスをその場所に移動するため、入る前に承認を求めるプロンプトが表示されます。新しい worktree の作成と `.claude/worktrees/` の下のパスはプロンプトを表示しません。v2.1.206 より前では、Claude は `.claude/worktrees/` の外のパスにプロンプトなしで入りました。worktree セッション内から、または [`isolation: worktree`](/docs/ja/sub-agents#supported-frontmatter-fields)などでピン留めされた作業ディレクトリを持つ subagent から、`path` フォームのみが利用可能で、ターゲットはセッションのリポジトリの `.claude/worktrees/` の下にある必要があります          | はい    |
| `ExitPlanMode`         | 承認用のプランを提示して Plan Mode を終了します                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | はい    |
| `ExitWorktree`         | worktree セッションを終了して元のディレクトリに戻ります。[`isolation: worktree`](/docs/ja/sub-agents#supported-frontmatter-fields)などで既に独自の作業ディレクトリで実行される subagent では利用できません                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | いいえ   |
| `Glob`                 | パターン マッチングに基づいてファイルを検索します。[Glob ツールの動作](#glob-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | いいえ   |
| `Grep`                 | ファイル コンテンツ内のパターンを検索します。[Grep ツールの動作](#grep-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | いいえ   |
| `ListMcpResourcesTool` | 接続された [MCP servers](/docs/ja/mcp)によって公開されたリソースをリストします                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | いいえ   |
| `LSP`                  | 言語サーバー経由のコード インテリジェンス：定義へのジャンプ、参照の検索、型エラーと警告の報告。[LSP ツールの動作](#lsp-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | いいえ   |
| `Monitor`              | コマンドをバックグラウンドで実行し、各出力行を Claude にフィードバックするため、会話の途中でログ エントリ、ファイル変更、またはポーリング ステータスに対応できます。WebSocket を開いて、各受信メッセージをイベントとして扱うこともできます。[Monitor ツール](#monitor-tool)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | はい    |
| `NotebookEdit`         | Jupyter ノートブック セルを変更します。[NotebookEdit ツールの動作](#notebookedit-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | はい    |
| `PowerShell`           | PowerShell コマンドをネイティブに実行します。[PowerShell ツール](#powershell-tool)の可用性を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | はい    |
| `PushNotification`     | デスクトップ通知を送信し、[Remote Control](/docs/ja/remote-control)が接続されている場合は電話プッシュ通知を送信するため、長時間実行タスクまたは[スケジュール済みタスク](/docs/ja/scheduled-tasks)が離席時に到達できます。プッシュ配信は Anthropic ホスト インフラストラクチャを通じて実行されます。これは Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry からはアクセスできません                                                                                                                                                                                                                                                                                                                                                                                                                            | いいえ   |
| `Read`                 | ファイルの内容を読み取ります。[Read ツールの動作](#read-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | いいえ   |
| `ReadMcpResourceTool`  | URI で特定の MCP リソースを読み取ります                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | いいえ   |
| `RemoteTrigger`        | claude.ai で[ルーチン](/docs/ja/routines)を作成、更新、実行、リストします。`/schedule` コマンドをサポートします。ルーチンは claude.ai に存在し、Pro、Max、Team、または Enterprise プランが必要なため、このツールは Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry からはアクセスできません                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | いいえ   |
| `ReportFindings`       | コード レビューの検出結果を構造化されたリストとして報告します。検出結果ごとにファイル、概要、失敗シナリオがあり、Claude Code はテキストとして出力するのではなく、それらをレンダリングできます。アクティブなコード レビュー指示が Claude にそれを呼び出すよう指示した場合、Claude はそれを呼び出します。Claude Code v2.1.196 以降が必要です。v2.1.199 以降、検出結果はオプションの `category` スラッグ（`correctness` や `test-coverage` など）を含めることもでき、レンダリングされたリストのファイル位置の横に表示されます                                                                                                                                                                                                                                                                                                                                                                               | いいえ   |
| `ScheduleWakeup`       | [self-paced `/loop`](/docs/ja/scheduled-tasks#let-claude-choose-the-interval)の次の反復をスケジュール変更します。Claude は各反復の終了時にこれを呼び出して、次の実行時刻を 1 分から 1 時間の間で選択します。直接呼び出すことはありません。ループを終了する代わりに、Claude は `stop: true` で呼び出します。これにより、保留中のウェイクアップがキャンセルされます。}`stop` フィールドには Claude Code v2.1.202 以降が必要です。保留中のウェイクアップは [Stop hook input](/docs/ja/hooks#stop-input)の `session_crons` に表示されます。Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、または Microsoft Foundry では利用できません。これらでは、間隔のない `/loop` プロンプトは固定スケジュールで実行されます                                                                                                                                                                                   | いいえ   |
| `SendMessage`          | [agent team](/docs/ja/agent-teams)メンバーにメッセージを送信するか、agent ID または名前で [subagent](/docs/ja/sub-agents#resume-subagents)を再開します。完了した subagent はバックグラウンドで自動的に再開されます。`/tasks` から停止した subagent は再開されず、呼び出しは拒否を返します。構造化されたチーム プロトコル メッセージには agent teams が必要です。受信者は別のエージェントからのメッセージを、あなたの同意または承認として扱うことはありません。v2.1.198 以降、subagent はそれを起動したエージェントからのメッセージをピア リクエストではなく通常のタスク指示として扱います。v2.1.199 以降、会話の早い段階で解決された名前とは異なるエージェントに現在解決される名前への送信は、配信される代わりに拒否されます。[subagent を再開](/docs/ja/sub-agents#resume-subagents)を参照してください                                                                                                                                                                                                | いいえ   |
| `SendUserFile`         | セッションからファイルをオプションのキャプション付きで送信するため、生成されたレポート、図、スクリーンショット、または構築されたアーティファクトがトランスクリプトでのみ言及されるのではなく、デバイスに到達します。v2.1.196 以降、オプションの `display` 入力がプレゼンテーションを制御します：`render` はファイルをクライアントにインラインで開き、`attach` はダウンロード カードのみを表示し、設定されていない場合はクライアントがファイル タイプで決定します。[Remote Control](/docs/ja/remote-control)クライアントが接続されている場合、またはセッションが [Claude Code on the web](/docs/ja/claude-code-on-the-web)などのマネージド クラウド環境で実行されている場合に利用可能です。配信は Anthropic ホスト インフラストラクチャを通じて実行されるため、このツールは Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry では利用できません                                                                                                                                                           | いいえ   |
| `ShareOnboardingGuide` | }`ONBOARDING.md` をアップロードし、チームメンバーが Claude Code で開くことができる共有リンクを返します。ガイドが作成された後、`/team-onboarding` から呼び出されます。claude.ai の Pro、Max、Team、および Enterprise プランのサブスクライバーが利用可能です                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | はい    |
| `Skill`                | メイン会話内で [skill](/docs/ja/skills#control-who-invokes-a-skill)を実行します                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | はい    |
| `TaskCreate`           | タスク リストに新しいタスクを作成します                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | いいえ   |
| `TaskGet`              | 特定のタスクの完全な詳細を取得します                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | いいえ   |
| `TaskList`             | すべてのタスクとその現在のステータスをリストします                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | いいえ   |
| `TaskOutput`           | バックグラウンド タスクから出力を取得します。タスクの出力ファイル パスで `Read` を使用することをお勧めします。タスク ID が一致しない場合、エラーは実行中のバックグラウンド エージェントを ID と説明でリストします。v2.1.203 より前では、エラーは不足している ID のみを名前付けていました                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | いいえ   |
| `TaskStop`             | ID で実行中のバックグラウンド タスクを終了します。また、[agent team メンバー](/docs/ja/agent-teams)または agent ID または名前で名前付きバックグラウンド エージェントも受け入れます。v2.1.198 より前では、バックグラウンド タスク ID のみを受け入れていました。タスク ID が一致しない場合、エラーは実行中のバックグラウンド エージェントを ID と説明でリストします。これには別のエージェントが生成したエージェントも含まれます。v2.1.203 より前では、エラーは実行中のチームメンバーと名前付きエージェントをリストしていましたが、別のエージェントが生成したバックグラウンド エージェントはリストしていなかったため、メイン会話から識別または停止できませんでした                                                                                                                                                                                                                                                                                                                           | いいえ   |
| `TaskUpdate`           | タスク ステータス、依存関係、詳細を更新するか、タスクを削除します                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | いいえ   |
| `TodoWrite`            | セッション タスク チェックリストを管理します。v2.1.142 以降、`TaskCreate`、`TaskGet`、`TaskList`、`TaskUpdate` を優先するため、デフォルトで無効になっています。`CLAUDE_CODE_ENABLE_TASKS=0` を設定して再度有効にします                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | いいえ   |
| `ToolSearch`           | [ツール検索](/docs/ja/mcp#scale-with-mcp-tool-search)が有効な場合、遅延ツールを検索してロードします                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | いいえ   |
| `WaitForMcpServers`    | バックグラウンドでまだ接続中の 1 つ以上の [MCP servers](/docs/ja/mcp)を待機するため、セッションを再開することなくそのツールをリクエストで使用できます。必要なサーバーがまだ接続されていない場合、Claude はそれを呼び出します。[ツール検索](/docs/ja/mcp#scale-with-mcp-tool-search)が無効な場合にのみ表示されます。有効な場合は `ToolSearch` が待機を処理するため                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | いいえ   |
| `WebFetch`             | 指定された URL からコンテンツを取得します。[WebFetch ツールの動作](#webfetch-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | はい    |
| `WebSearch`            | Web 検索を実行します。[WebSearch ツールの動作](#websearch-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | はい    |
| `Workflow`             | [動的ワークフロー](/docs/ja/workflows)を実行します：バックグラウンドで多くの subagent を調整し、1 つの統合結果を返すスクリプト                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | はい    |
| `Write`                | ファイルを作成または上書きします。[Write ツールの動作](#write-tool-behavior)を参照してください                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | はい    |

<h2 id="configure-tools-with-permission-rules-and-hooks">
  権限ルールとフックでツールを構成する
</h2>

ほとんどの場合、Claude はこれらのツールをいつ使用するかを決定し、Claude と対話するときにツール名を自分で指定する必要はありません。権限およびその他の構成を定義するときにツール名を直接参照します：

* 設定の [`permissions.allow` と `permissions.deny`](/docs/ja/settings#available-settings)および `/permissions` インターフェイス内
* [`allowedTools` と `disallowedTools`](/docs/ja/cli-reference)の CLI フラグ内
* Agent SDK の [`allowedTools` と `disallowedTools`](/docs/ja/agent-sdk/permissions#allow-and-deny-rules)オプション内
* [subagent の `tools` または `disallowedTools`](/docs/ja/sub-agents#supported-frontmatter-fields)frontmatter 内
* [skill の `allowed-tools`](/docs/ja/skills#frontmatter-reference)frontmatter 内
* フックの [`if` 条件](/docs/ja/hooks-guide#filter-by-tool-name-and-arguments-with-the-if-field)内

これらはすべて同じルール形式 `ToolName(specifier)` を受け入れます。指定子はツールによって異なり、複数のツールが形式を共有します：

| ルール形式                          | 適用対象                    | 詳細                                                                |
| :----------------------------- | :---------------------- | :---------------------------------------------------------------- |
| `Bash(npm run *)`              | Bash、Monitor            | [コマンド パターン マッチング](/docs/ja/permissions#bash)                           |
| `PowerShell(Get-ChildItem *)`  | PowerShell              | [コマンド パターン マッチング](/docs/ja/permissions#powershell)                     |
| `Read(~/secrets/**)`           | Read、Grep、Glob、LSP      | [パス パターン マッチング](/docs/ja/permissions#read-and-edit)                    |
| `Edit(/src/**)`                | Edit、Write、NotebookEdit | [パス パターン マッチング](/docs/ja/permissions#read-and-edit)                    |
| `Skill(deploy *)`              | Skill                   | [Skill 名マッチング](/docs/ja/skills#restrict-claude%E2%80%99s-skill-access) |
| `Agent(Explore)`               | Agent                   | [Subagent タイプ マッチング](/docs/ja/permissions#agent-subagents)             |
| `WebFetch(domain:example.com)` | WebFetch                | [ドメイン マッチング](/docs/ja/permissions#webfetch)                            |
| `WebSearch`                    | WebSearch               | 指定子なし。ツール全体を許可または拒否します                                            |

ここにリストされていないツール（`ExitPlanMode` や `ShareOnboardingGuide` など）は、指定子なしのベア ツール名のみを受け入れます。

`Edit(...)` 許可ルールは同じパスへの読み取りアクセスも付与するため、一致する `Read(...)` ルールは必要ありません。`Read(...)` 拒否ルールは同じパスの Edit ツールもブロックします。これには新しいファイルの作成も含まれます。編集には結果の読み取りが必要なためです。Edit での `Read` 拒否チェックには Claude Code v2.1.208 以降が必要です。

フック `matcher` フィールドは括弧で囲まれたルール形式ではなく、ベア ツール名を使用します。[マッチャー パターン](/docs/ja/hooks#matcher-patterns)のマッチング ルールを参照してください。各ツールがフック内の `tool_input` に渡すフィールド名については、[PreToolUse 入力リファレンス](/docs/ja/hooks#pretooluse-input)を参照してください。

<h2 id="agent-tool-behavior">
  Agent ツールの動作
</h2>

Agent ツールは、別のコンテキストウィンドウで subagent を生成します。Subagent はそのタスクを自律的に処理し、親会話に単一のテキスト結果を返します。親は subagent の中間ツール呼び出しまたは出力を見ず、その最終結果のみを見ます。

Subagent が実行するターン数を制限するには、[subagent 定義](/docs/ja/sub-agents#supported-frontmatter-fields)で `maxTurns` を設定します。

同じ Agent ツールは、フォーク モードが有効な場合に[フォーク subagent](/docs/ja/sub-agents#fork-the-current-conversation)も起動します。フォークは新規に開始する代わりに完全な親会話を継承し、常にバックグラウンドで実行され、ターミナルで権限プロンプトを表示します。このセクションの残りは名前付き subagent について説明します。

名前付き subagent が使用できるツールは、[subagent 定義](/docs/ja/sub-agents)の `tools` および `disallowedTools` フィールドに依存します：

* **どちらのフィールドも設定されていない**：subagent は親が利用可能なすべてのツールを継承します。
* **`tools` のみ**：subagent はリストされたツールのみを取得します。
* **`disallowedTools` のみ**：subagent は親のすべてのツール（リストされたもの除く）を取得します。
* **両方設定**：`disallowedTools` が優先されます。両方にリストされているツールは削除されます。

Subagent の `tools` リストがまったくツールに解決されない場合（例えば、すべてのエントリが誤字であるか、subagent で利用できないツールに名前を付けている場合）、Agent ツールは subagent を起動する代わりに、それらのエントリをリストするエラーを返します。v2.1.208 より前は、subagent はツールなしで起動し、空または混乱した結果を返す可能性がありました。

Subagent を起動しても、それ自体は権限を求めるプロンプトを表示しません。Claude Code は、実行時に subagent の独自のツール呼び出しを権限ルールに対してチェックします。

v2.1.198 以降、subagent はデフォルトでバックグラウンドで実行されます。Claude は結果が必要になる前に続行する必要がある場合、フォアグラウンドで実行します。

* **フォアグラウンド subagent** は、メイン会話で見られるのと同じ権限プロンプトを表示し、各ツール呼び出しが発生した時点で表示されます。
* **バックグラウンド subagent** は v2.1.186 以降、メイン セッションで権限プロンプトを表示します。プロンプトはどの subagent がリクエストしているかを示し、Esc キーを押すとその 1 つのツール呼び出しを拒否し、subagent を停止しません。v2.1.186 より前は、バックグラウンド subagent は、そうでなければプロンプトを表示するツール呼び出しを自動的に拒否し、そのツールなしで続行していました。

Subagent が最初に到達できるものを制限するには、その `tools` フィールドを絞り込み、Bash をリストから外すか、[Subagent 機能の制御](/docs/ja/sub-agents#control-subagent-capabilities)で説明されているように設定で拒否ルールを設定します。フォアグラウンドとバックグラウンドの選択の詳細については、[Subagent をフォアグラウンドまたはバックグラウンドで実行](/docs/ja/sub-agents#run-subagents-in-foreground-or-background)を参照してください。

<h2 id="bash-tool-behavior">
  Bash ツールの動作
</h2>

Bash ツールは、次の永続化動作で各コマンドを別々のプロセスで実行します：

* Claude がメイン セッションで `cd` を実行すると、新しい作業ディレクトリはプロジェクト ディレクトリ内に留まる限り、または `--add-dir`、`/add-dir`、または設定の `additionalDirectories` で追加した[追加の作業ディレクトリ](/docs/ja/permissions#working-directories)内に留まる限り、後の Bash コマンドに引き継がれます。Subagent セッションは作業ディレクトリの変更を引き継ぎません。
  * `cd` がこれらのディレクトリの外に出た場合、Claude Code はプロジェクト ディレクトリにリセットし、ツール結果に `Shell cwd was reset to <dir>` を追加します。
  * この引き継ぎを無効にして、すべての Bash コマンドがプロジェクト ディレクトリで開始されるようにするには、`CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1` を設定します。
* 環境変数は永続化されません。1 つのコマンドの `export` は次のコマンドでは利用できません。
* シェル スタートアップ ファイルで定義されたエイリアスとシェル関数は利用できます。セッション開始時に、Claude Code はシェルに応じて `~/.zshrc`、`~/.bashrc`、または `~/.profile` をソースし、結果のエイリアス、関数、およびシェル オプションをキャプチャして、すべての Bash コマンドに適用します。

Claude Code を起動する前に virtualenv または conda 環境をアクティブ化してください。Bash コマンド間で環境変数を永続化するには、Claude Code を起動する前に [`CLAUDE_ENV_FILE`](/docs/ja/env-vars) をシェル スクリプトに設定するか、[SessionStart フック](/docs/ja/hooks#persist-environment-variables)を使用して動的に設定します。

2 つの制限が各コマンドを制限します：

* **タイムアウト**：デフォルトでは 2 分です。Claude は `timeout` パラメーターで 1 コマンドあたり最大 10 分をリクエストできます。[`BASH_DEFAULT_TIMEOUT_MS` と `BASH_MAX_TIMEOUT_MS`](/docs/ja/env-vars)でデフォルトと上限をオーバーライドします。
* **出力長**：デフォルトでは 30,000 文字です。コマンドがそれ以上を生成する場合、Claude Code は完全な出力をセッション ディレクトリのファイルに保存し、Claude にファイル パスと開始からの短いプレビューを提供します。Claude は必要に応じてそのファイルを読み取るか検索します。[`BASH_MAX_OUTPUT_LENGTH`](/docs/ja/env-vars)で制限を上げます。上限は 150,000 文字です。

開発サーバーやウォッチ ビルドなどの長時間実行プロセスの場合、Claude は `run_in_background: true` を設定して、コマンドをバックグラウンド タスクとして開始し、実行中に作業を続けることができます。`/tasks` でバックグラウンド タスクをリストおよび停止します。非インタラクティブ モードで `-p` フラグを使用する場合、[バックグラウンド タスクは実行の最終結果の直後に終了します](/docs/ja/headless#background-tasks-at-exit)。

<h2 id="edit-tool-behavior">
  Edit ツールの動作
</h2>

Edit ツールは正確な文字列置換を実行します。`old_string` と `new_string` を取り、最初のものを 2 番目のものに置き換えます。正規表現またはあいまい一致は使用しません。

編集を適用するには、3 つのチェックが合格する必要があります。その前に、[`Read` 拒否ルール](/docs/ja/permissions#tool-specific-permission-rules)に一致するパスは拒否されます。これには新しいファイルをそこに作成することも含まれます。この拒否には Claude Code v2.1.208 以降が必要です。

* **編集前の読み取り**：Claude は現在の会話でファイルを読み取っている必要があり、[`PARTIAL ビュー` 通知](#read-tool-behavior)で短縮された読み取りはカウントされません。Claude Opus 4.6、Claude Haiku 4.5、およびそれ以前のモデルは常に読み取りが必要です。新しいモデルは、読み取りが権限プロンプトを必要とせず、Read ツールが利用可能な場合、未読ファイルを編集できます。
* **マッチ**：`old_string` はファイルに正確に記述されたとおりに表示される必要があります。空白またはインデントの 1 文字の違いでも不一致になります。
* **一意性**：`old_string` は正確に 1 回表示される必要があります。複数回表示される場合、Claude は 1 つの出現を特定するのに十分な周囲コンテキストを含む長い文字列を提供するか、`replace_all: true` を設定してすべてを置き換えます。

Claude が最後に読み取った後、ディスク上で変更されたファイルは、`old_string` が現在のコンテンツと正確かつ明確に一致し、Claude Code がプロンプトなしでファイルを読み取ることができる場合でも編集できます。ファイルの現在のコンテンツに対してマッチングすることでこれを安全に保ち、結果はファイルが他の変更を含むことを示すため、Claude は周囲のコンテンツに依存する編集の前に再度読み取ります。古い `old_string` や `replace_all` なしで複数回マッチするものなど、その他の場合は、Claude は編集する前にファイルを再度読み取ります。未読および変更されたファイルの緩和された処理には Claude Code v2.1.208 以降が必要です。それ以前は、Claude Code は会話で読み取っていないファイルまたは読み取り後にディスク上で変更されたファイルへの編集を拒否していました。

Bash でファイルを表示することは、コマンドが `cat`、`head`、`tail`、`sed -n 'X,Yp'`、`grep`、`egrep`、または `fgrep` である場合、パイプやリダイレクトのない単一ファイルに対して、編集前の読み取り要件を満たします。パイプ出力およびその他の Bash コマンドは編集前の読み取りチェックにはカウントされません。

これは編集の適格性にのみ影響し、権限には影響しません。[Read および Edit 拒否ルール](/docs/ja/permissions#tool-specific-permission-rules)は、Claude Code が `cat`、`head`、`tail`、`sed`、`grep` などの Bash で認識するファイルコマンドにも適用されますが、Python または Node スクリプトがファイルを自分で開くなど、ファイルを間接的に読み取るまたは書き込む任意のサブプロセスには適用されません。読み取り前編集リストの `egrep` と `fgrep` は読み取り前編集ではカウントされますが、Read 拒否ルールに対してはチェックされません。すべてのプロセスをカバーする OS レベルの強制については、[サンドボックスを有効にする](/docs/ja/sandboxing)を参照してください。

<h2 id="glob-tool-behavior">
  Glob ツールの動作
</h2>

Glob ツールはファイルを名前パターンで検索します。`**` を含む標準 glob 構文をサポートして、再帰的なディレクトリ マッチングを行います：

* `**/*.js` は任意の深さのすべての `.js` ファイルにマッチします
* `src/**/*.ts` は `src/` の下のすべての `.ts` ファイルにマッチします
* `*.{json,yaml}` は現在のディレクトリの `.json` および `.yaml` ファイルにマッチします

結果は変更時刻でソートされ、100 ファイルで制限されます。制限に達した場合、Claude は結果に切り詰めフラグを見て、パターンを絞り込むことができます。

Glob はデフォルトで `.gitignore` を尊重しないため、追跡されたファイルと並んで gitignore されたファイルを検出します。これは [Grep](#grep-tool-behavior) とは異なり、gitignore されたファイルをスキップします。Glob が `.gitignore` を尊重するようにするには、Claude Code を起動する前に `CLAUDE_CODE_GLOB_NO_IGNORE=false` を設定します。

`pattern` または `path` の値に null バイトが含まれている場合、Claude にそれを削除するよう求めるエラーが返されます。

<h2 id="grep-tool-behavior">
  Grep ツールの動作
</h2>

Grep ツールはファイル コンテンツ内のパターンを検索します。[Glob](#glob-tool-behavior)がファイルを名前で検索する場合、Grep はそれらの内部の行を検索します。

Grep は [ripgrep](https://github.com/BurntSushi/ripgrep)に基づいており、POSIX grep ではなく ripgrep の正規表現構文を使用します。正規表現メタ文字を含むパターンはエスケープが必要です。たとえば、Go コードで `interface{}` を検出するには、パターン `interface\{\}` が必要です。

ripgrep が拒否するパターン、glob、またはファイル タイプは、ripgrep の診断を含むエラーを返すため、Claude は入力を修正して再度検索できます。v2.1.208 より前では、Claude Code は拒否された入力を、検索対象のテキストが対象ファイルに存在する場合でも、エラーではなく `No files found` として報告していました。

3 つの出力モードは、戻ってくるものを制御します：

* `files_with_matches`：ファイル パスのみ、行コンテンツなし。これがデフォルトです。
* `content`：ファイルと行番号を含む一致する行。
* `count`：ファイルごとの一致数。その後、すべての一致ファイル全体の合計。合計は、ツールの `head_limit` または `offset` パラメーターがファイルごとのエントリをトリミングする場合でも、すべての一致をカバーします。v2.1.208 より前では、合計はリストされたエントリのみを合計していました。

Claude は `**/*.tsx` などの `glob` パラメーターでファイルごとに結果をスコープするか、`py` または `rust` などの `type` パラメーターで言語ごとにスコープできます。デフォルトでは、パターンは単一行内で一致します。Claude は `multiline: true` を設定して、行の境界を越えて一致させることができます。

Grep は `.gitignore` を尊重するため、gitignore されたファイルはスキップされます。gitignore されたファイルを検索するには、Claude はそのパスを直接渡します。

<h2 id="lsp-tool-behavior">
  LSP ツールの動作
</h2>

LSP ツールは、実行中の言語サーバーから Claude にコード インテリジェンスを提供します。ファイル編集後、型エラーと警告を自動的に報告するため、Claude は別のビルド ステップなしで問題を修正できます。Claude はナビゲーション操作のために直接呼び出すこともできます：

* シンボルの定義へのジャンプ
* シンボルへのすべての参照を検索
* 位置での型情報を取得
* ファイル内のシンボルをリスト
* ワークスペース全体でシンボルを名前で検索
* インターフェイスの実装を検索
* 呼び出し階層をトレース

ツールは、言語の[コード インテリジェンス プラグイン](/docs/ja/discover-plugins#code-intelligence)をインストールするまで非アクティブです。プラグインは言語サーバー構成をバンドルし、サーバー バイナリは別途インストールします。

<h2 id="monitor-tool">
  Monitor ツール
</h2>

Monitor ツールを使用すると、Claude は会話を一時停止することなく、バックグラウンドで何かを監視し、変更時に対応できます。Claude に以下を依頼します：

* ログ ファイルをテールして、エラーが表示されたらフラグを立てる
* PR または CI ジョブをポーリングして、ステータスが変更されたときに報告する
* ディレクトリのファイル変更を監視する
* 指定した長時間実行スクリプトからの出力を追跡する
* WebSocket フィードに接続し、到着した各メッセージを報告する

ほとんどの監視では、Claude は監視用の小さなスクリプトを作成し、バックグラウンドで実行し、到着した各出力行を受け取ります。イベントをプッシュするサーバーの場合、Claude はスクリプトを実行する代わりに、[WebSocket](#websocket-source) を開くことができます。

同じセッションで作業を続け、イベントが到着すると Claude が割り込みます。Claude にキャンセルするよう依頼するか、セッションを終了することで Monitor を停止します。

Monitor がコマンドを実行する場合、[Bash と同じ権限ルール](/docs/ja/permissions#tool-specific-permission-rules)を使用するため、Bash に設定した `allow` および `deny` パターンがここにも適用されます。[WebSocket ソース](#websocket-source)には独自の承認プロンプトがあります。

このツールは Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry では利用できません。`DISABLE_TELEMETRY` または `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` が設定されている場合も利用できません。

プラグインは、Claude に開始するよう依頼する代わりに、プラグインがアクティブな場合に自動的に開始される Monitor を宣言できます。[プラグイン Monitor](/docs/ja/plugins-reference#monitors)を参照してください。

<h3 id="websocket-source">
  WebSocket ソース
</h3>

<Note>
  WebSocket ソースには Claude Code v2.1.195 以降が必要です。
</Note>

サーバーが既に WebSocket 経由でイベントをプッシュしている場合、Claude はポーリング スクリプトを作成する代わりに、直接接続できます。各種のソケット アクティビティはイベントになるか、監視を終了します：

* **テキスト メッセージ**：各メッセージが 1 つのイベントになります。メッセージが複数行にまたがる場合でも同じです。
* **バイナリ メッセージ**：渡されません。Claude は `[binary frame, 512 bytes]` などのプレースホルダー行を受け取ります。
* **1 MiB より大きいメッセージ**：監視が終了するため、フィルタリングされたフィードが存在する場合はそれにサブスクライブしてください。
* **ソケット クローズ**：監視が終了し、Claude はクローズ コードを受け取ります。

WebSocket 監視は `command` の代わりに `ws` 入力を使用し、1 つの Monitor 呼び出しで両方を組み合わせることはできません。`ws` 入力には 2 つのフィールドがあります：

| フィールド       | 必須  | 説明                                                                                    |
| :---------- | :-- | :------------------------------------------------------------------------------------ |
| `url`       | はい  | 接続するエンドポイント。`ws://` または `wss://` URL である必要があり、埋め込まれた認証情報やホワイトスペースがなく、ASCII 文字のみを使用します |
| `protocols` | いいえ | ハンドシェイク中に提供する WebSocket サブプロトコル名。各エントリは有効なサブプロトコル トークンである必要があり、リストに重複を含めることはできません     |

`timeout_ms` および `persistent` 入力は、コマンドの場合と同じように動作します。`persistent` が設定されていない限り、監視は期限で終了し、`TaskStop` は早期にキャンセルします。

WebSocket を開くと承認を求めるプロンプトが表示され、プロンプトは同じホストの今後のプロンプトをスキップするオプションを提供しません。

Claude Code は、プライベート、リンク ローカル、またはクラウド メタデータ アドレスを指すホスト名を含む URL を拒否します。また、`sandbox.network.deniedDomains` 内のホストも拒否し、マネージド設定で [`allowManagedDomainsOnly`](/docs/ja/settings#sandbox-settings) が設定されている場合は、マネージド許可リスト外のホストを拒否します。

<h2 id="notebookedit-tool-behavior">
  NotebookEdit ツールの動作
</h2>

NotebookEdit は、Jupyter ノートブックを 1 回に 1 セル、`cell_id` でセルをターゲットにして変更します。[Edit](#edit-tool-behavior)がプレーン ファイルで行うようにノートブック全体で文字列置換を実行しません。

3 つの編集モードは、ターゲット セルに何が起こるかを制御します：

* `replace`：セルのソースを上書きします。これがデフォルトです。
* `insert`：ターゲットの後に新しいセルを追加します。`cell_id` がない場合、新しいセルはノートブックの開始に移動します。`cell_type` を `code` または `markdown` に設定する必要があります。
* `delete`：ターゲット セルを削除します。

権限ルールは `Edit(...)` パス形式を使用します。`Edit(notebooks**)` のようなルールは、そのディレクトリ内のファイルに対する NotebookEdit 呼び出しをカバーします。

<h2 id="powershell-tool">
  PowerShell ツール
</h2>

PowerShell ツールを使用すると、Claude は PowerShell コマンドをネイティブに実行できます。Windows では、これは Git Bash を経由するのではなく、PowerShell でコマンドが実行されることを意味します。ツールが利用可能になる方法はプラットフォームによって異なります：

* **Git Bash がない Windows**：ツールは自動的に有効になります。
* **Git Bash がインストールされている Windows**：ツールは段階的にロールアウトされています。
* **Linux、macOS、および WSL**：ツールはオプトインです。

<h3 id="enable-the-powershell-tool">
  PowerShell ツールを有効にする
</h3>

環境または `settings.json` で `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` を設定します：

```json theme={null}
{
  "env": {
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1"
  }
}
```

Windows では、変数を `0` に設定してロールアウトをオプトアウトします。Linux、macOS、および WSL では、ツールに PowerShell 7 以降が必要です：`pwsh` をインストールして、`PATH` に含まれていることを確認します。

Windows では、Claude Code は PowerShell 7 以降の `pwsh.exe` を自動検出し、PowerShell 5.1 の `powershell.exe` にフォールバックします。ツールが有効になっている場合、Claude は PowerShell をプライマリシェルとして扱います。Git Bash がインストールされている場合、Bash ツールは POSIX スクリプト用に利用可能なままです。

Claude Code は `-ExecutionPolicy Bypass` を使用して PowerShell をプロセススコープのみで生成するため、`.ps1` スクリプトとモジュールのインポートは、マシンのポリシーを変更することなく、デフォルトの Windows インストールで機能します。プロセススコープのバイパスは、グループ ポリシーの `MachinePolicy` または `UserPolicy` をオーバーライドしないため、エンタープライズポリシーは引き続き適用されます。マシンの有効な実行ポリシーを尊重する代わりに、`CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY=1` を設定します。

<h3 id="shell-selection-in-settings-hooks-and-skills">
  設定、フック、スキルでのシェル選択
</h3>

3 つの追加設定は PowerShell が使用される場所を制御します：

* [`settings.json`](/docs/ja/settings#available-settings)の `"defaultShell": "powershell"`：対話型 `!` コマンドを PowerShell 経由でルーティングします。PowerShell ツールが有効になっている必要があります。
* 個別の[コマンド フック](/docs/ja/hooks#command-hook-fields)の `"shell": "powershell"`：そのフックを PowerShell で実行します。フックは PowerShell を直接生成するため、`CLAUDE_CODE_USE_POWERSHELL_TOOL` に関係なく機能します。
* [skill frontmatter](/docs/ja/skills#frontmatter-reference)の `shell: powershell`：`` !`command` `` ブロックを PowerShell で実行します。PowerShell ツールが有効になっている必要があります。

Bash ツール セクションで説明されている同じメイン セッション作業ディレクトリ リセット動作が PowerShell コマンドに適用されます。これには `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` 環境変数が含まれます。

v2.1.196 以降、PowerShell ツールは Bash ツールの検索および diff 終了コードの処理と一致します。`grep`、`egrep`、`fgrep`、および `git grep` からの終了コード 1 は一致がないことを意味し、`git diff` からの終了コード 1 は差分が存在することを意味するため、これらの結果は Claude へのコマンド失敗として報告されません。

<h3 id="preview-limitations">
  プレビューの制限事項
</h3>

PowerShell ツールには、プレビュー中に次の既知の制限事項があります：

* PowerShell プロファイルはロードされません
* Windows では、サンドボックスはサポートされていません

<h2 id="read-tool-behavior">
  Read ツールの動作
</h2>

Read ツールはファイル パスを取得し、行番号付きでコンテンツを返します。Claude は常に絶対パスを渡すよう指示されます。

デフォルトでは、Read は開始からファイルを返します。全ファイル読み取りがトークン制限を超える場合、Read は最初のページを `PARTIAL view` 通知付きで返し、Claude がファイルのどの部分を受け取ったか、および `offset` と `limit` を使用してさらに読み取る方法を伝えます。明示的な `offset` または `limit` を渡す読み取りがトークン制限を超える場合でも、エラーを返します。

明示的な `limit` を指定した読み取りは、選択された行がトークン制限で収まる可能性のある量を超えるとすぐに停止し、残りの範囲を読み込まずにエラーを返します。エラーは Claude に、より小さい `limit` を使用するか、単一行が大きい場合は代わりに [Grep](#grep-tool-behavior) で特定のコンテンツを検索するよう指示します。v2.1.208 より前では、Claude Code は範囲全体をメモリに読み込んでから拒否していたため、非常に長い単一行を持つファイルはメモリを枯渇させる可能性がありました。

空のファイルを読み取ると、ファイルは存在するがコンテンツが空であることを示す通知が返され、最後の行を超えた `offset` は、ファイルの行数を示す通知を返します。v2.1.208 より前では、空のファイルを読み取ると、末尾を超えた通知が返されていました。

Read はプレーン テキストを超えるいくつかのファイル タイプを処理します：

* **画像**：PNG、JPG、およびその他の画像形式は、生バイトではなく Claude が見ることができるビジュアル コンテンツとして返されます。Claude Code は大きな画像をモデルの画像サイズ制限に合わせるようにサイズ変更および再圧縮するため、Claude は大きなスクリーンショットのダウンスケール版を見る場合があります。v2.1.196 以降、そのサイズ変更後も 500KB より大きい画像は、ピクセル寸法を変更せずに品質を低下させた JPEG として再エンコードされます。Claude が大きな画像で細かいピクセル レベルの詳細を見落とす場合は、ImageMagick を使用して Bash 経由で関心領域を最初にトリミングするよう依頼してください。
* **PDF**：Claude は短い `.pdf` ファイルを全体的に読み取ります。10 ページより長い PDF の場合、`pages` パラメーター（`"1-5"` など）で範囲で読み取り、一度に最大 20 ページまで読み取ります。
* **Jupyter ノートブック**：`.ipynb` ファイルは、コード、マークダウン、ビジュアライゼーションを含む、すべてのセルとその出力を返します。

Read はファイルのみを読み取り、ディレクトリは読み取りません。Claude は Bash ツール経由で `ls` を使用してディレクトリ コンテンツをリストします。

<h2 id="webfetch-tool-behavior">
  WebFetch ツールの動作
</h2>

WebFetch は URL と抽出する内容を説明するプロンプトを取得します。ページを取得し、サーバーが HTML を返す場合は応答を Markdown に変換し、小さく高速なモデルを使用してコンテンツに対してプロンプトを実行します。ほとんどのフェッチでは、Claude はそのモデルの回答を受け取り、生のページではなく受け取ります。変換ステップは構成不可です。

これにより WebFetch は設計上損失があります。抽出プロンプトは Claude に到達するものを決定するため、ページが何かについて言及していないという結果は、プロンプトがそれについて尋ねなかったことのみを意味する場合があります。Claude にもっと具体的なプロンプトで再度フェッチするよう依頼するか、Bash 経由で `curl` を使用して未処理のページを取得します。

いくつかの動作は Claude が受け取る応答を形成します：

* HTTP URL は自動的に HTTPS にアップグレードされます。
* 大きなページは処理前に固定文字制限に切り詰められます。
* 応答は 15 分間キャッシュされるため、同じ URL の繰り返しフェッチは迅速に返されます。
* URL が別のホストにリダイレクトされる場合、WebFetch はそれに従う代わりに、元の URL とリダイレクト ターゲットを名前付けするテキスト結果を返します。Claude は 2 番目の WebFetch 呼び出しで新しい URL をフェッチします。

デフォルトおよび `acceptEdits` 権限モードでは、WebFetch は新しいドメインに最初に到達するときにプロンプトを表示します。プロンプトなしで事前にドメインを許可するには、`WebFetch(domain:example.com)` のような権限ルールを追加します。`auto` および `bypassPermissions` [権限モード](/docs/ja/permissions#permission-modes)はプロンプトを完全にスキップします。

明示的な `WebFetch(domain:...)` ルールが `deny`、`ask`、または `allow` にある場合、事前承認されたセットよりも優先されるため、事前承認されたドメインをブロックするか、そのドメインに対してプロンプトを要求できます。

WebFetch は `Claude-User` で始まる `User-Agent` ヘッダーと、HTML よりも Markdown を優先する `Accept` ヘッダーを設定するため、コンテンツ ネゴシエーションをサポートするサーバーは Markdown を直接返すことができます。[sandbox](/docs/ja/sandboxing)ネットワーク ルールは別途構成されるため、サンドボックス化されたプロセスが到達したいドメインには、明示的なサンドボックス権限ルールが必要です。

<h2 id="websearch-tool-behavior">
  WebSearch ツールの動作
</h2>

WebSearch は Anthropic の [web search](https://platform.claude.com/docs/ja/agents-and-tools/tool-use/web-search-tool)バックエンドに対してクエリを実行し、結果のタイトルと URL を返します。結果ページをフェッチしません。Claude が検索結果で見つけたページを読むには、[WebFetch](#webfetch-tool-behavior)でフォローアップします。

ツールは 1 回の呼び出しあたり最大 8 つのバックエンド検索を発行し、結果を返す前に内部的に検索を絞り込む場合があります。Claude は `allowed_domains` で結果をスコープして特定のホストのみを含めるか、`blocked_domains` で除外できます。2 つのリストは 1 回の呼び出しで組み合わせることはできません。

検索バックエンドは構成不可です。別のプロバイダーで検索するには、検索ツールを公開する [MCP サーバー](/docs/ja/mcp)を追加します。

WebSearch 権限ルールは指定子を取りません。`allow` または `deny` の裸の `WebSearch` エントリのみが唯一の形式です。

<Note>
  WebSearch は Claude API、[Claude Platform on AWS](/docs/ja/claude-platform-on-aws)、および Microsoft Foundry で利用可能です。Google Cloud の Agent Platform では、Opus、Sonnet、Haiku を含む Claude 4 以降のモデルで機能します。Amazon Bedrock はサーバー側の Web 検索ツールを公開していません。
</Note>

<h2 id="write-tool-behavior">
  Write ツールの動作
</h2>

Write ツールは新しいファイルを作成するか、提供された完全なコンテンツで既存のファイルを上書きします。追加またはマージは行いません。

ターゲット パスが既に存在する場合、Claude は現在の会話でそのファイルを少なくとも 1 回読み取っている必要があります。読み取られていない既存ファイルへの Write はエラーで失敗します。この制約は新しいファイルには適用されません。

Bash でファイルを表示することは、[Edit ツールの動作](#edit-tool-behavior)で説明されているのと同じルールの下で、この要件を満たします。

既存ファイルへの部分的な変更の場合、Claude は Write ではなく Edit を使用します。

<h2 id="check-which-tools-are-available">
  利用可能なツールを確認する
</h2>

正確なツール セットは、プロバイダー、プラットフォーム、および設定によって異なります。実行中のセッションで読み込まれているものを確認するには、Claude に直接尋ねます：

```text theme={null}
What tools do you have access to?
```

Claude は会話形式の概要を提供します。正確な MCP ツール名については、`/mcp` を実行します。

<Note>
  [advisor tool](/docs/ja/advisor) は、Claude Code が実装するツールではなく、API が実行する [server tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) です。権限ルールやフック マッチャーで参照できる名前はありません。
</Note>

<h2 id="see-also">
  関連項目
</h2>

* [MCP servers](/docs/ja/mcp)：外部サーバーを接続してカスタム ツールを追加する
* [権限](/docs/ja/permissions)：権限システム、ルール構文、ツール固有のパターン
* [Subagents](/docs/ja/sub-agents)：subagent のツール アクセスを構成する
* [フック](/docs/ja/hooks-guide)：ツール実行の前後にカスタム コマンドを実行する
