> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 用語集

> Claude Code の用語の定義。agentic loop、compaction、CLAUDE.md、hooks、subagents、MCP などのコア概念の意味を学びます。

この用語集は Claude Code の用語を定義しています。各エントリは、その概念について詳しく説明されているページにリンクしています。トークン、temperature、RAG などのモデルレベルの概念については、[プラットフォーム用語集](https://platform.claude.com/docs/ja/about-claude/glossary)を参照してください。

<h2 id="a">
  A
</h2>

<h3 id="agent-teams">
  Agent teams
</h3>

複数の独立した Claude Code セッションがチームリーダーによって調整され、共有タスクリストとピアツーピアメッセージングを備えています。単一のセッション内で実行され、親にのみレポートする [subagents](#subagent) とは異なり、チームメイトはそれぞれ独自のコンテキストウィンドウを持ち、任意のメンバーと直接対話できます。Agent teams は実験的機能であり、`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` を設定して有効にする必要があります。

詳細情報: [Run agent teams](/docs/ja/agent-teams)

<h3 id="agentic-coding">
  Agentic coding
</h3>

AI がファイルを読み取り、コマンドを実行し、自律的に変更を加えることができるワークフロー。あなたが見守ったり、リダイレクトしたり、立ち去ったりできます。これは、テキストのみで応答するチャットベースのアシスタントとは異なり、自分で適用する必要があります。Claude Code は agentic です。なぜなら、アドバイスするだけでなく、行動できる [tools](#tool) を持っているからです。

詳細情報: [How Claude Code works](/docs/ja/how-claude-code-works)

<h3 id="agentic-harness">
  Agentic harness
</h3>

言語モデルを有能なコーディングエージェントに変える、ツール、コンテキスト管理、実行環境。Claude Code はハーネスです。Claude はその中のモデルです。ハーネスはファイルアクセス、シェル実行、権限ゲーティング、メモリロード、およびアクションをチェーンするループを提供します。

詳細情報: [How Claude Code works](/docs/ja/how-claude-code-works)

<h3 id="agentic-loop">
  Agentic loop
</h3>

Claude がすべてのタスクで実行するサイクル: コンテキストを収集し、アクションを実行し、結果を検証し、完了するまで繰り返します。各ツール使用は次のステップに情報を提供します。ループはいつでも中断してリダイレクトできます。[hooks](#hook)、[skills](#skill)、[MCP](#mcp-model-context-protocol) を含むほとんどの拡張ポイントは、このループの特定のフェーズにプラグインします。

詳細情報: [How Claude Code works](/docs/ja/how-claude-code-works#the-agentic-loop)

<h3 id="artifact">
  Artifact
</h3>

Claude Code がセッションから claude.ai 上のプライベート URL に公開するライブでインタラクティブな Web ページ。出力を視覚的に確認したり、ターミナルテキストを読む代わりに共有したりできます。セッションが再公開されると、ページはその場で更新されます。Claude Code から作成した Artifact は、claude.ai の会話から作成した Artifact と同じギャラリーに表示されます。共有はプランに依存します: Pro と Max では、誰でも開くことができるパブリックリンク。Team と Enterprise では、組織内での共有、およびオーナーが有効にした後のパブリックリンク。

詳細情報: [Share session output as artifacts](/docs/ja/artifacts)

<h3 id="auto-memory">
  Auto memory
</h3>

Claude が自分自身のために書いたメモ。あなたの修正と設定に基づいて、git リポジトリごとに `~/.claude/projects/` に保存されます。同じリポジトリのすべてのワークツリーは 1 つの auto memory ディレクトリを共有します。`MEMORY.md` インデックスの最初の 200 行または 25 KB がすべてのセッションの開始時にロードされます。Auto memory は、あなたが書く [CLAUDE.md](#claude-md) に対する Claude が書いた対応物です。

詳細情報: [Auto memory](/docs/ja/memory#auto-memory)

<h3 id="auto-mode">
  Auto mode
</h3>

[permission mode](#permission-mode) の一種。承認プロンプトを表示する代わりに、別の分類器モデルがバックグラウンドで各アクションをレビューします。分類器はスコープエスカレーション、信頼されていないインフラストラクチャ、および [prompt injection](#prompt-injection) をブロックします。ツール結果を見ることはないため、注入された指示がその決定に影響を与えることはできません。

詳細情報: [Eliminate prompts with auto mode](/docs/ja/permission-modes#eliminate-prompts-with-auto-mode)

<h2 id="b">
  B
</h2>

<h3 id="bare-mode">
  Bare mode
</h3>

スタートアップフラグ `--bare`。hooks、skills、plugins、MCP servers、auto memory、CLAUDE.md の自動検出をスキップします。明示的に渡したフラグのみが有効になります。ローカル設定に関係なく、マシン間で同じ動作が必要な CI とスクリプト呼び出しに推奨されます。

詳細情報: [Start faster with bare mode](/docs/ja/headless#start-faster-with-bare-mode)

<h3 id="bundled-skills">
  Bundled skills
</h3>

Claude Code に含まれるプロンプトベースのプレイブック。`/batch`、`/code-review`、`/debug`、`/loop` など。固定ロジックを実行する組み込みコマンドとは異なり、bundled skills は Claude に詳細なプロンプトを与え、作業をオーケストレーションさせるため、エージェントを生成し、ファイルを読み取り、コードベースに適応できます。

詳細情報: [Bundled skills](/docs/ja/skills#bundled-skills)

<h2 id="c">
  C
</h2>

<h3 id="channel">
  Channel
</h3>

[MCP server](#mcp-model-context-protocol) の一種。実行中のセッションにイベントをプッシュして、Claude がターミナルから離れている間に発生することに反応できるようにします。チャネルは双方向にできます。Claude は受信イベントを読み取り、同じチャネルを通じて返信します。Telegram、Discord、iMessage は研究プレビューに含まれています。

詳細情報: [Channels](/docs/ja/channels)

<h3 id="checkpoint">
  Checkpoint
</h3>

各プロンプト送信時に作成されたリストアポイント。Claude Code はすべての編集の前にファイルをスナップショットするため、チェックポイントでそれらを復元できます。`Esc` を 2 回押すか `/rewind` を実行して、コード、会話、またはその両方を以前のポイントに復元するか、選択したメッセージから会話の一部を要約します。チェックポイントはセッションに対してローカルであり、git とは別であり、Bash ツールを通じて行われた変更は追跡しません。

詳細情報: [Checkpointing](/docs/ja/checkpointing)

<h3 id="claude-directory">
  `.claude` directory
</h3>

Claude Code がプロジェクトスコープの設定を読み取るディレクトリ: 設定、hooks、skills、subagents、rules、auto memory。プロジェクトはそのルートに `.claude/` を持ちます。ユーザーレベルのデフォルトは `~/.claude/` にあります。

詳細情報: [The `.claude` directory](/docs/ja/claude-directory)

<h3 id="claude-md">
  CLAUDE.md
</h3>

Claude のために書く永続的な指示のマークダウンファイル。システムプロンプトの後、ユーザーメッセージとしてすべてのセッションの開始時にロードされます。プロジェクト規約、アーキテクチャノート、「常に X を行う」ルールをここに配置します。プロジェクトルート CLAUDE.md は [compaction](#compaction) を生き残り、その後ディスクから新しく再読み込みされます。

CLAUDE.md は `./CLAUDE.md` または `./.claude/CLAUDE.md` のプロジェクトスコープに、`~/.claude/CLAUDE.md` のユーザースコープに、または組織の [managed policy](#managed-settings) として配置できます。検出されたすべてのファイルは、互いにオーバーライドするのではなく、最も広いスコープから最も具体的なスコープへの順序で、コンテキストに連結されます。

詳細情報: [CLAUDE.md files](/docs/ja/memory#claude-md-files)

<h3 id="command">
  Command
</h3>

プロンプトに `/name` と入力して呼び出す再利用可能な指示。`/clear`、`/model`、`/compact` などの組み込みコマンドはセッションを制御します。`.claude/commands/` のファイルとして独自のコマンドを定義するか、[plugin](#plugin) からインストールできます。[Skills](#skill) は複数ステップのコマンドをパッケージ化するための推奨される方法です。

詳細情報: [Commands](/docs/ja/commands) · [Skills](/docs/ja/skills)

<h3 id="compaction">
  Compaction
</h3>

[context window](#context-window) がその制限に近づくときの会話の自動要約。古いツール出力が最初にクリアされ、次に会話が要約されます。プロジェクトルート CLAUDE.md と auto memory は compaction を生き残り、ディスクから再ロードされます。会話でのみ与えられた指示は失われる可能性があります。`/compact` を手動でトリガーするか、オプションで `/compact focus on the API changes` のようなフォーカスを指定します。

詳細情報: [What survives compaction](/docs/ja/context-window#what-survives-compaction) · [When context fills up](/docs/ja/how-claude-code-works#when-context-fills-up)

<h3 id="context-window">
  Context window
</h3>

セッションの作業メモリ。会話履歴、ファイルコンテンツ、コマンド出力、CLAUDE.md、auto memory、ロードされたスキル、システム指示を保持します。作業を進めるにつれて、コンテキストが満杯になるまで [compaction](#compaction) がそれを要約します。`/context` を実行して、スペースを使用しているものを確認します。基礎となるモデル概念については、[プラットフォーム用語集](https://platform.claude.com/docs/ja/about-claude/glossary#context-window)を参照してください。

詳細情報: [Explore the context window](/docs/ja/context-window)

<h2 id="d">
  D
</h2>

<h3 id="dispatch">
  Dispatch
</h3>

電話で開始されたタスクルーター。Claude モバイルアプリからコーディングタスクを送信すると、Desktop アプリで Claude Code セッションを生成します。プロンプトは自動的に正しいツールにルーティングされます。Pro および Max プランで利用可能です。

詳細情報: [Sessions from Dispatch](/docs/ja/desktop#sessions-from-dispatch)

<h2 id="e">
  E
</h2>

<h3 id="effort-level">
  Effort level
</h3>

各ターンで Claude が適応的推論思考予算をどの程度使用するかを制御する設定です。より高い努力はより多くの思考トークンとより深い推論を意味し、より低い努力はより速く、より安価です。Effort は Fable 5、Opus 4.6 以降、および Sonnet 4.6 以降でサポートされています。

詳細情報: [Adjust effort level](/docs/ja/model-config#adjust-effort-level)

<h3 id="extended-thinking">
  Extended thinking
</h3>

モデルが応答する前に実行する可視的なステップバイステップの推論。[effort level](#effort-level) で調整するか、固定思考予算を持つモデルで `MAX_THINKING_TOKENS` で思考トークンをキャップできます。思考はターミナルのグレーイタリックテキストで表示されます。

詳細情報: [Use extended thinking](/docs/ja/model-config#extended-thinking)

<h2 id="h">
  H
</h2>

<h3 id="hook">
  Hook
</h3>

Claude Code のライフサイクルの特定のポイント（ツール実行前、ファイル編集後、セッション開始時など）で自動的に実行されるユーザー定義ハンドラー。ハンドラーはシェルコマンド、HTTP エンドポイント、MCP ツール、LLM プロンプト、または subagent にできます。Hooks は決定論的です。モデルの裁量ではなく、固定ライフサイクルポイントで発火します。

フック設定には 3 つのレベルがあります:

* **Hook event**: ライフサイクルポイント
* **Matcher**: どのイベントがそれを発火させるかをフィルタリング
* **Hook handler**: 実行内容

詳細情報: [Get started with hooks](/docs/ja/hooks-guide) · [Hooks reference](/docs/ja/hooks)

<h2 id="m">
  M
</h2>

<h3 id="managed-settings">
  Managed settings
</h3>

IT または DevOps によって組織全体で実施される設定。Anthropic のサーバーから管理コンソール経由で配信されるか、`~/.claude` の外の OS レベルパスにデバイスにデプロイされます。ユーザーおよびプロジェクト設定は managed settings をオーバーライドすることはできません。サーバー管理配信は[対象となる構成](/docs/ja/server-managed-settings#platform-availability)に適用されます。[セキュリティに関する考慮事項](/docs/ja/server-managed-settings#security-considerations)を参照してください。セキュリティポリシー、コンプライアンス要件、またはフロート全体の標準化されたツールに使用します。

詳細情報: [Server-managed settings](/docs/ja/server-managed-settings) · [Settings files](/docs/ja/settings#settings-files)

<h3 id="mcp-model-context-protocol">
  MCP (Model Context Protocol)
</h3>

AI ツールを外部データソースとサービスに接続するためのオープン標準。MCP servers は Claude に Slack、Jira、データベース、ブラウザ、および数百の他の統合用の新しいツールを提供します。`/mcp` を使用するか、`.mcp.json` に追加してサーバーを接続します。プロトコル自体については、[プラットフォーム用語集](https://platform.claude.com/docs/ja/about-claude/glossary#mcp-model-context-protocol)を参照してください。

詳細情報: [Model Context Protocol](/docs/ja/mcp)

<h3 id="mcp-tool-search">
  MCP Tool Search
</h3>

コンテキスト節約メカニズム。MCP ツールスキーマを必要になるまで遅延させます。スタートアップ時にはツール名のみがロードされます。Claude は特定のツールを使用することを決定したときにオンデマンドで完全なスキーマを取得します。これにより、アイドル MCP servers がコンテキストをあまり消費しないようにします。

詳細情報: [Scale with MCP Tool Search](/docs/ja/mcp#scale-with-mcp-tool-search)

<h2 id="n">
  N
</h2>

<h3 id="non-interactive-mode">
  Non-interactive mode
</h3>

単一のプロンプトを実行して会話セッションなしで終了するモード。`-p` または `--print` で呼び出されます。CI、スクリプト、パイピングに使用されます。`--no-session-persistence` を渡さない限り、実行は再開可能なセッションとして保存されます。[Agent SDK](/docs/ja/agent-sdk/overview) は Python および TypeScript の同等物です。以前は headless mode と呼ばれていました。

詳細情報: [Run Claude Code programmatically](/docs/ja/headless)

<h2 id="o">
  O
</h2>

<h3 id="output-style">
  Output style
</h3>

Claude のシステムプロンプトを変更して応答動作、トーン、または形式を変更する設定です。Output styles は、システムプロンプトの後にユーザーメッセージとして配信される [CLAUDE.md](#claude-md) とは異なり、デフォルトシステムプロンプトのソフトウェアエンジニアリング固有の部分をオフにします。組み込みスタイルには Default、Proactive、Explanatory、Learning が含まれます。

詳細情報: [Output styles](/docs/ja/output-styles)

<h2 id="p">
  P
</h2>

<h3 id="permission-mode">
  Permission mode
</h3>

セッションのベースライン承認動作。CLI で `Shift+Tab` でサイクルするか、VS Code、Desktop、claude.ai のモードセレクターを使用します。利用可能なモードは `default`、`acceptEdits`、`plan`、`auto`、`dontAsk`、`bypassPermissions` です。

`default` モードは CLI および VS Code と JetBrains 拡張機能では Manual とラベル付けされており、Claude Code は値の `manual` をエイリアスとして受け入れます。

詳細情報: [Permission mode を選択する](/docs/ja/permission-modes)

<h3 id="permission-rule">
  Permission rule
</h3>

ツール名と引数パターンに基づいてツール呼び出しを許可、質問、または拒否する設定エントリ。ルールは deny→ask→allow で評価され、最初にマッチしたものが優先されます。Permission rules は、より広い [permission mode](#permission-mode) の上に層状化された細粒度制御です。

詳細情報: [権限を設定する](/docs/ja/permissions)

<h3 id="plan-mode">
  Plan mode
</h3>

[permission mode](#permission-mode) の一種。Claude はソースファイルを編集せずに変更を研究および提案します。読み取り、検索、探索コマンドを実行でき、その後、何かに触れる前に承認用の計画を提示します。`/plan` を入力するか、`Shift+Tab` を押して plan mode に入ります。

詳細情報: [編集前に分析する（plan mode）](/docs/ja/permission-modes#analyze-before-you-edit-with-plan-mode)

<h3 id="plugin">
  Plugin
</h3>

skills、hooks、subagents、MCP servers のバンドル。単一のインストール可能なユニットとしてパッケージ化されます。Plugin skills は `plugin-name:skill-name` として名前空間化されるため、複数のプラグインが共存できます。[marketplace](/docs/ja/plugin-marketplaces) を通じてチーム全体にプラグインを配布します。

詳細情報: [Plugins](/docs/ja/plugins)

<h3 id="project-trust">
  Project trust
</h3>

Claude Code がその設定をロードする前に、ディレクトリを受け入れるダイアログ。受け入れはプロジェクトディレクトリごとに保存されます。ただし、ホームディレクトリの場合は、信頼は現在のセッションのみ保持され、起動するたびにプロンプトが再度表示されます。Trust は marketplace プラグインの自動インストールとプロジェクト定義フックの実行をゲートします。ディレクトリを信頼することは、その `.claude/settings.json`、`.mcp.json`、および他の設定ファイルが有効になることを意味します。

詳細情報: [`.claude` ディレクトリ](/docs/ja/claude-directory)

<h3 id="prompt-injection">
  Prompt injection
</h3>

ファイル、ウェブページ、またはツール結果に埋め込まれた敵対的な指示。Claude を、あなたが決して求めなかったアクションにリダイレクトしようとします。Claude Code の防御には、権限システム、コマンドインジェクション検出、信頼検証が含まれます。[Auto mode](#auto-mode) は、ツール結果の疑わしいコンテンツをスキャンするサーバー側プローブと、ツール結果を見ない分類器を追加します。そのため、注入されたテキストが承認決定に影響を与えることはできません。

詳細情報: [Prompt injection から保護する](/docs/ja/security#protect-against-prompt-injection)

<h2 id="r">
  R
</h2>

<h3 id="remote-control">
  Remote Control
</h3>

ローカル Claude Code セッションを電話またはブラウザから claude.ai 経由で続行する方法です。コード実行とファイルはマシンに留まります。インターフェースはリモートです。クラウドサンドボックスで実行される web 上の Claude Code とは異なります。

詳細情報: [Remote Control](/docs/ja/remote-control)

<h3 id="rules">
  Rules
</h3>

`.claude/rules/` のモジュール化された指示ファイル。CLAUDE.md と一緒にロードされます。ルールは YAML `paths:` frontmatter でパススコープできるため、Claude が一致するファイルを読み取るときのみロードされ、関連になるまでコンテキストを精力的に保ちます。

詳細情報: [Organize rules with `.claude/rules/`](/docs/ja/memory#organize-rules-with-claude/rules/)

<h2 id="s">
  S
</h2>

<h3 id="sandboxing">
  Sandboxing
</h3>

Bash ツールの OS レベルのファイルシステムおよびネットワーク分離。コマンドは事前に定義した境界内で実行されるため、Claude はコマンドごとの承認プロンプトなしで自由に作業できます。Sandboxing は [permission rules](#permission-rule) とは別のレイヤーです。

詳細情報: [Sandboxing](/docs/ja/sandboxing)

<h3 id="session">
  Session
</h3>

現在のディレクトリに関連付けられた会話。独自の独立した [context window](#context-window) を持ちます。セッションは `claude -c` で再開でき、`--fork-session` でフォークして履歴を新しいセッション ID の下に保存でき、またはターミナル全体で並列実行できます。`/clear` を実行すると新しいセッションが開始されます。前のセッションは保存されたままで、`/resume` を通じて利用可能です。各セッションのトランスクリプトは `~/.claude/projects/` に保存されます。

詳細情報: [Work with sessions](/docs/ja/how-claude-code-works#work-with-sessions)

<h3 id="settings-layers">
  Settings layers
</h3>

Claude Code が設定を読み取る階層。優先順位の高い順から低い順: [managed policy](#managed-settings)、コマンドライン引数、`.claude/settings.local.json` のローカル設定、`.claude/settings.json` のプロジェクト設定、`~/.claude/settings.json` のユーザー設定。配列はレイヤー全体でマージされます。スカラーは高いレイヤーで低いレイヤーをオーバーライドします。

詳細情報: [Settings files](/docs/ja/settings#settings-files)

<h3 id="skill">
  Skill
</h3>

指示、知識、またはワークフローを含む `SKILL.md` ファイル。Claude はそれをツールキットに追加します。Claude は関連する場合に自動的にスキルをロードするか、`/skill-name` で直接呼び出します。Skills は Agent Skills オープン標準に従います。Claude Code はそれを呼び出し制御と subagent 実行で拡張します。

Skills は custom commands の推奨される後継者です。`.claude/commands/deploy.md` のファイルと `.claude/skills/deploy/SKILL.md` のファイルの両方が `/deploy` を作成し、同じように機能します。既存のコマンドファイルは引き続き機能します。

詳細情報: [Extend Claude with skills](/docs/ja/skills)

<h3 id="subagent">
  Subagent
</h3>

独自のコンテキストウィンドウ、カスタムシステムプロンプト、特定のツールアクセス、独立した権限で実行される特化した AI アシスタント。委任されたタスクで機能し、メイン会話に要約を返します。大規模な探索をプライマリコンテキストから除外するか、並列研究を実行するために subagents を使用します。各エージェントが直接対話できる完全な独立したセッションである [agent teams](#agent-teams) とは異なります。

組み込み subagents には Explore、Plan、汎用があります。

詳細情報: [Create custom subagents](/docs/ja/sub-agents)

<h3 id="surface">
  Surface
</h3>

Claude Code にアクセスする任意の場所: CLI、VS Code、JetBrains、Desktop、または claude.ai。すべてのサーフェスは同じエンジンを共有するため、CLAUDE.md、設定、スキルはすべてのサーフェスで同じように機能します。Slack と Chrome 拡張機能は、サーフェス自体ではなくサーフェスに接続する統合です。

詳細情報: [Platforms and integrations](/docs/ja/platforms)

<h2 id="t">
  T
</h2>

<h3 id="teleport">
  Teleport
</h3>

コマンド `/teleport`。クラウド Claude Code セッションをローカルターミナルにプルします。Claude はブランチをフェッチし、会話履歴をロードし、web セッションの最後の状態から再開します。逆方向は `--cloud` です。ローカルタスクを web で実行するために送信します。

詳細情報: [From web to terminal](/docs/ja/claude-code-on-the-web#from-web-to-terminal)

<h3 id="tool">
  Tool
</h3>

Claude が実行できるアクション: ファイルを読み取る、コードを編集する、シェルコマンドを実行する、web を検索する、subagent を生成する。Tools は Claude Code を agentic にするものです。それらなしでは、Claude はテキストのみで応答できます。各ツール使用は、[agentic loop](#agentic-loop) での Claude の次の決定に情報を提供する結果を返します。

詳細情報: [Tools available to Claude](/docs/ja/tools-reference)

<h3 id="turn">
  Turn
</h3>

Claude が [session](#session) 内で行う 1 つの完全な応答です。Turn は、メッセージを送信するときに開始され、Claude が応答を終了するときに終了します。その間に任意の数の [tool](#tool) 呼び出しがあります。[Stop hooks](#hook) は各 turn の終了時に発火します。セッションは多くの turn で構成され、[agentic loop](#agentic-loop) は 1 つの内部で何が起こるかを説明します。

詳細情報: [How Claude Code works](/docs/ja/how-claude-code-works#the-agentic-loop)

<h2 id="v">
  V
</h2>

<h3 id="verification-loop">
  Verification loop
</h3>

セッションが作業が実際に完了したことを知る方法。テストスイート、ビルド、またはスクリーンショット比較など、Claude が実行できるチェックを提供します。Claude はチェックが成功するまで反復します。1 回の試行後に停止するのではなく。Verification loop は [`/goal`](/docs/ja/goal)、無人実行、および [dynamic workflows](/docs/ja/workflows) の前提条件です。それなしでは、エージェントが完了したことを決定する唯一のものはエージェント自体です。

詳細情報: [Claude に作業を検証する方法を提供する](/docs/ja/best-practices#give-claude-a-way-to-verify-its-work)

<h2 id="w">
  W
</h2>

<h3 id="worktree-isolation">
  Worktree isolation
</h3>

Claude を `.claude/worktrees/` の別の git worktree で実行する分離モード。`-w` フラグまたは subagent 設定の `isolation: worktree` で有効にされます。変更は別のブランチの別のディレクトリに留まるため、並列エージェントはお互いのファイルを上書きしません。

詳細情報: [git worktrees を使用した並列セッションの実行](/docs/ja/worktrees)

***

<h2 id="deprecated-and-renamed-terms">
  非推奨および名前変更された用語
</h2>

これらの用語は古いドキュメント、ブログ投稿、コミュニティコンテンツに表示されます。このサイトを検索するときは現在の名前を使用してください。

| 古い用語            | 現在の呼び方                                        | 注記                              |
| --------------- | --------------------------------------------- | ------------------------------- |
| Headless mode   | [Non-interactive mode](#non-interactive-mode) | 同じ `-p` フラグ、同じ動作                |
| Custom commands | [Skills](#skill)                              | `.claude/commands/` ファイルは引き続き機能 |
| Slash commands  | Commands                                      | 製品コピーから「Slash」を削除               |
