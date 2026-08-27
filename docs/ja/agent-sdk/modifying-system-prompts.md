> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# システムプロンプトの変更

> `claude_code` プリセットとカスタムシステムプロンプトの間で選択し、CLAUDE.md、出力スタイル、append、または完全にカスタムなプロンプトで動作をカスタマイズします。

システムプロンプトは Claude の動作、機能、応答スタイルを定義します。人間が作業を監視して操舵する CLI または IDE のようなコーディングツール向けに `claude_code` プリセットから始めます。異なるサーフェス、アイデンティティ、またはパーミッションモデルを持つエージェント向けに独自のプロンプトを作成します。

このページでは以下をカバーしています：

* [システムプロンプトの仕組み](#how-system-prompts-work)。プリセット、プリセットと `append` の組み合わせ、カスタムプロンプトの間で選択するための決定テーブル付き
* [エージェントの動作をカスタマイズ](#customize-agent-behavior)する方法。CLAUDE.md ファイル、出力スタイル、`append`、またはカスタム文字列を使用
* [4 つのアプローチを比較](#compare-the-four-approaches)する方法。永続性、スコープ、および保持される内容による比較
* [アプローチを組み合わせ](#combine-approaches)てカスタマイズ方法を重ねる方法

<h2 id="how-system-prompts-work">
  システムプロンプトの仕組み
</h2>

システムプロンプトは、会話全体を通じて Claude の動作方法を形作る初期命令セットです。Agent SDK には、これに対する 3 つの開始点があります：

* **最小限のデフォルト**：TypeScript で `systemPrompt` を設定しない、または Python で `system_prompt` を設定しない場合、SDK はツール呼び出しをカバーする最小限のプロンプトを使用しますが、Claude Code のコーディングガイドライン、応答スタイル、プロジェクトコンテキストは省略されています。これは、デフォルトで完全な Claude Code プロンプトを使用する `claude -p` とは異なります。CLI から移行していて、一致する動作を望む場合は、`claude_code` プリセットを設定してください。
* **`claude_code` プリセット**：Claude Code CLI が使用する完全なシステムプロンプト。ツール使用命令、コードスタイルとフォーマットガイドライン、応答トーンと詳細度ルール、セキュリティと安全性の命令、および作業ディレクトリと環境に関するコンテキストが含まれています。TypeScript で `systemPrompt: { type: "preset", preset: "claude_code" }` を設定するか、Python で `system_prompt={"type": "preset", "preset": "claude_code"}` を設定してください。オプションで `append` を使用して、最後に独自の命令を追加できます。
* **カスタム文字列**：自分で作成したプロンプト。SDK は提供したものだけを送信します。

<h3 id="decide-on-a-starting-point">
  開始点を決定する
</h3>

決定要因は、エージェントが Claude Code にどの程度似ているかです：リポジトリで動作するコーディングエージェント。人間がストリーミング出力を監視して作業を指導します。製品がそれから遠いほど、独自のプロンプトを作成する必要があります。

| 構築しているもの                                                       | 使用するもの                           | 得られるもの                                                        |
| :------------------------------------------------------------- | :------------------------------- | :------------------------------------------------------------ |
| 人間が監視して指導する CLI または IDE のようなコーディングツール。Claude Code のデフォルトが必要なもの | `claude_code` プリセット              | 完全な Claude Code プロンプト：ツールガイダンス、安全ルール、ターミナルフレンドリーな応答、リポジトリ規約認識 |
| 同じ種類のツール、プラス、コーディング標準、出力形式、またはドメインコンテキストなどの製品固有のルール            | `claude_code` プリセット（`append` 付き） | 上記のすべて。プリセットの後に命令が追加されます。何も削除されないため、これは最もリスクが低いカスタマイズです       |
| 異なるサーフェス、アイデンティティ、またはアクセス許可モデルを持つエージェント、またはコーディング以外のエージェント     | カスタムプロンプト文字列                     | 作成したもののみ。エージェントが必要とするツールガイダンスと安全命令を置き換える責任があります               |
| ツール呼び出しループが薄く、エージェントペルソナがなく、ユーザープロンプトですべての動作を提供する              | `systemPrompt` オプションなし           | 最小限のデフォルト：ツール呼び出しサポートのみ                                       |

「Claude Code と異なる」は通常、以下のいずれかを意味します：

* **異なるサーフェス**：出力は、それをトリガーした人によってターミナルで読まれません。チャット UI、構造化出力コンシューマー、およびコーディング以外の自動化は、それぞれ、出力がどのようにレンダリングおよびレビューされるかに一致するプロンプトが必要です。CI ジョブがリントエラーを修正したり、diff をレビューしたりするような無人コーディング自動化は、作業自体がプリセットが書かれているものであるため、プリセットに適合します。
* **異なるアイデンティティ**：エージェントは Claude Code として自分自身を提示すべきではありません。サポートボット、データ分析アシスタント、またはドメイン固有のエージェントは、独自の名前、スコープ、およびペルソナが必要です。
* **異なるアクセス許可モデル**：エージェントは人間が各ステップを承認することなく自律的に実行されるか、リソースの限定されたセットで動作します。Claude Code のプロンプトは、人間がループ内にいて、完全なツールセットにアクセスできることを前提としています。
* **コーディング以外のタスク**：Claude Code のプロンプトのほとんどはコーディングガイダンスです。研究、コンテンツ、または運用エージェントの場合、そのガイダンスは実際に必要な命令と競合します。

[比較表](#compare-the-four-approaches)は、各カスタマイズ方法が何を保持するかを示しています。

<h2 id="customize-agent-behavior">
  エージェントの動作をカスタマイズする
</h2>

出力スタイル、`append`、およびカスタムプロンプト文字列は、それぞれシステムプロンプトを直接変更します。CLAUDE.md は異なるパスを取ります。SDK がそれを読み込み、システムプロンプトではなくプロジェクトコンテキストとして会話に内容を注入するため、選択したシステムプロンプトに関係なく動作を形作ります。[Skills](/docs/ja/agent-sdk/skills)、[hooks](/docs/ja/agent-sdk/hooks)、および[permissions](/docs/ja/agent-sdk/permissions)もシステムプロンプト外で動作を形作り、独自のページで説明されています。

<h3 id="claude-md-files-for-project-level-instructions">
  プロジェクトレベルの命令用の CLAUDE.md ファイル
</h3>

CLAUDE.md ファイルは Claude に永続的なプロジェクトコンテキストと命令を提供します。SDK は会話に内容を注入し、システムプロンプトには注入しないため、任意のシステムプロンプト設定で機能します。CLAUDE.md に何を入れるか、どこに配置するか、効果的な命令を書く方法については、[Claude がプロジェクトを記憶する方法](/docs/ja/memory)を参照してください。このセクションでは SDK に固有のもの、つまり CLAUDE.md がどのように読み込まれるかについて説明します。

SDK は、対応する設定ソースが有効な場合に CLAUDE.md を読み込みます。`'project'` は作業ディレクトリから `CLAUDE.md` または `.claude/CLAUDE.md` を読み込み、`'user'` は `~/.claude/CLAUDE.md` を読み込みます。デフォルトの `query()` オプションは両方のソースを有効にするため、CLAUDE.md は自動的に読み込まれます。TypeScript で `settingSources` または Python で `setting_sources` を明示的に設定する場合は、必要なソースを含めてください。CLAUDE.md の読み込みは設定ソースによって制御され、`claude_code` プリセットによっては制御されません。

<h4 id="load-claude-md-with-the-sdk">
  SDK で CLAUDE.md を読み込む
</h4>

CLAUDE.md を読み込むには、`settingSources` を CLAUDE.md が存在するレベルを含むように設定します。以下の例は、プロジェクトレベルの CLAUDE.md を `claude_code` プリセットと共に読み込むため、Claude は完全なコーディングエージェントプロンプトとプロジェクトの規約の両方にアクセスできます。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const messages = [];

  for await (const message of query({
    prompt: "Add a new React component for user profiles",
    options: {
      systemPrompt: {
        type: "preset",
        preset: "claude_code" // Use Claude Code's system prompt
      },
      settingSources: ["project"] // Loads CLAUDE.md from project
    }
  })) {
    messages.push(message);
  }

  // Now Claude has access to your project guidelines from CLAUDE.md
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions

  messages = []

  async for message in query(
      prompt="Add a new React component for user profiles",
      options=ClaudeAgentOptions(
          system_prompt={
              "type": "preset",
              "preset": "claude_code",  # Use Claude Code's system prompt
          },
          setting_sources=["project"],  # Loads CLAUDE.md from project
      ),
  ):
      messages.append(message)

  # Now Claude has access to your project guidelines from CLAUDE.md
  ```
</CodeGroup>

CLAUDE.md はプロジェクト内のすべてのセッション全体で永続的であり、git を通じてチームと共有され、コード変更なしで自動的に検出されます。空の `settingSources` 配列を渡す場合は読み込まれません。

<h3 id="output-styles-for-persistent-configurations">
  永続的な設定のための出力スタイル
</h3>

出力スタイルは Claude のシステムプロンプトを変更する保存された設定です。マークダウンファイルとして保存され、セッションとプロジェクト全体で再利用できます。

<h4 id="create-an-output-style">
  出力スタイルを作成する
</h4>

出力スタイルは、[frontmatter](/docs/ja/output-styles#frontmatter)のメタデータを含むマークダウンファイルで、その後にプロンプトコンテンツが続きます。すべてのプロジェクトで利用可能なユーザーレベルのスタイルの場合は `~/.claude/output-styles/` に保存するか、チームと共有してコミットできるプロジェクトレベルのスタイルの場合はリポジトリの `.claude/output-styles/` に保存します。

デフォルトでは、カスタム出力スタイルは `claude_code` プリセットのソフトウェアエンジニアリング命令を独自のもので置き換えます。それらを保持し、命令を上に重ねるには、frontmatter で `keep-coding-instructions: true` を設定します。エージェントがまだソフトウェアエンジニアリング作業を行っている場合は、それらを保持してください。役割全体を置き換える場合は、それらを除外してください。

以下の例はコードレビュー担当者のペルソナを定義しています。コードレビューは依然として Claude Code のセキュリティとコード品質ガイダンスの恩恵を受けるため、コーディング命令を保持します。プロジェクト全体で利用可能にするために `~/.claude/output-styles/code-reviewer.md` として保存します。

```markdown ~/.claude/output-styles/code-reviewer.md theme={null}
---
name: Code Reviewer
description: Thorough code review assistant
keep-coding-instructions: true
---

You are an expert code reviewer.

For every code submission:
1. Check for bugs and security issues
2. Evaluate performance
3. Suggest improvements
4. Rate code quality (1-10)
```

<h4 id="activate-an-output-style">
  出力スタイルをアクティブ化する
</h4>

作成後、以下を通じて出力スタイルをアクティブ化します。

* **CLI**：`/config` を実行し、出力スタイルを選択
* **設定**：`.claude/settings.local.json` で `outputStyle` を設定
* **TypeScript SDK**：`query()` に渡されるインラインの `settings` オブジェクト内で `outputStyle` を設定するか、`settings` を `outputStyle` を設定する設定ファイルに指定します。`outputStyle` はトップレベルの `Options` フィールドではありません：

  ```typescript theme={null}
  const options = { settings: { outputStyle: "Explanatory" } };
  ```

Python SDK には、出力スタイルをプログラムで選択するオプションはありません。`.claude/settings.local.json` に書き込めないコードのみのデプロイメントの場合は、`append` またはカスタムプロンプト文字列を代わりに使用してください。

**SDK ユーザーへの注記：** 出力スタイルは、オプションに `settingSources: ['user']` または `settingSources: ['project']`（TypeScript）/ `setting_sources=["user"]` または `setting_sources=["project"]`（Python）を含める場合に読み込まれます。

<h3 id="append-to-the-claude_code-preset">
  `claude_code` プリセットに追加する
</h3>

Claude Code プリセットを `append` プロパティと共に使用して、カスタム命令を追加しながら、すべての組み込み機能を保持できます。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const messages = [];

  for await (const message of query({
    prompt: "Help me write a Python function to calculate fibonacci numbers",
    options: {
      systemPrompt: {
        type: "preset",
        preset: "claude_code",
        append: "Always include detailed docstrings and type hints in Python code."
      }
    }
  })) {
    messages.push(message);
    if (message.type === "assistant") {
      console.log(message.message.content);
    }
  }
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage

  messages = []

  async for message in query(
      prompt="Help me write a Python function to calculate fibonacci numbers",
      options=ClaudeAgentOptions(
          system_prompt={
              "type": "preset",
              "preset": "claude_code",
              "append": "Always include detailed docstrings and type hints in Python code.",
          }
      ),
  ):
      messages.append(message)
      if isinstance(message, AssistantMessage):
          print(message.content)
  ```
</CodeGroup>

<h4 id="improve-prompt-caching-across-users-and-machines">
  ユーザーとマシン全体でプロンプトキャッシングを改善する
</h4>

デフォルトでは、同じ `claude_code` プリセットと `append` テキストを使用する 2 つのセッションでも、異なる作業ディレクトリから実行される場合、プロンプトキャッシュエントリを共有することはできません。これは、プリセットが `append` テキストの前のシステムプロンプトにセッションごとのコンテキストを埋め込むためです。作業ディレクトリ、git リポジトリであるかどうか、プラットフォーム、アクティブなシェル、OS バージョン、および自動メモリパスです。そのコンテキストに違いがあると、異なるシステムプロンプトが生成され、キャッシュミスが発生します。CLAUDE.md コンテンツはシステムプロンプトに影響しません。SDK がそれを会話に注入し、システムプロンプトには注入しないためです。

セッション全体でシステムプロンプトを同じにするには、TypeScript で `excludeDynamicSections: true` を設定するか、Python で `"exclude_dynamic_sections": True` を設定してください。セッションごとのコンテキストは最初のユーザーメッセージに移動し、システムプロンプトには静的プリセットと `append` テキストのみが残るため、同じ設定がユーザーとマシン全体でキャッシュエントリを共有できます。

<Note>
  `excludeDynamicSections` には `@anthropic-ai/claude-agent-sdk` v0.2.98 以降、または Python の場合は `claude-agent-sdk` v0.1.58 以降が必要です。プリセットオブジェクト形式にのみ適用され、`systemPrompt` が文字列の場合は効果がありません。
</Note>

次の例は、共有 `append` ブロックを `excludeDynamicSections` と組み合わせているため、異なるディレクトリから実行されるエージェントのフリートが同じキャッシュされたシステムプロンプトを再利用できます。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Triage the open issues in this repo",
    options: {
      systemPrompt: {
        type: "preset",
        preset: "claude_code",
        append: "You operate Acme's internal triage workflow. Label issues by component and severity.",
        excludeDynamicSections: true
      }
    }
  })) {
    // ...
  }
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions

  async for message in query(
      prompt="Triage the open issues in this repo",
      options=ClaudeAgentOptions(
          system_prompt={
              "type": "preset",
              "preset": "claude_code",
              "append": "You operate Acme's internal triage workflow. Label issues by component and severity.",
              "exclude_dynamic_sections": True,
          },
      ),
  ):
      ...
  ```
</CodeGroup>

**トレードオフ：** 作業ディレクトリ、git リポジトリフラグ、プラットフォーム、アクティブなシェル、OS バージョン、および自動メモリパスは依然として Claude に到達しますが、システムプロンプトではなく最初のユーザーメッセージの一部として到達します。ユーザーメッセージの命令は、システムプロンプトの同じテキストよりもわずかに低い重みを持つため、Claude は現在のディレクトリまたは自動メモリパスについて推論する際にそれらに依存する可能性が低くなります。クロスセッションキャッシュの再利用が最大限に権威あるコンテキストよりも重要な場合は、このオプションを有効にしてください。

非対話型 CLI モードの同等のフラグについては、[`--exclude-dynamic-system-prompt-sections`](/docs/ja/cli-reference)を参照してください。

<h3 id="custom-system-prompts">
  カスタムシステムプロンプト
</h3>

カスタム文字列を `systemPrompt` として提供して、デフォルトを完全に独自の命令に置き換えることができます。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const customPrompt = `You are a Python coding specialist.
  Follow these guidelines:
  - Write clean, well-documented code
  - Use type hints for all functions
  - Include comprehensive docstrings
  - Prefer functional programming patterns when appropriate
  - Always explain your code choices`;

  const messages = [];

  for await (const message of query({
    prompt: "Create a data processing pipeline",
    options: {
      systemPrompt: customPrompt
    }
  })) {
    messages.push(message);
    if (message.type === "assistant") {
      console.log(message.message.content);
    }
  }
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage

  custom_prompt = """You are a Python coding specialist.
  Follow these guidelines:
  - Write clean, well-documented code
  - Use type hints for all functions
  - Include comprehensive docstrings
  - Prefer functional programming patterns when appropriate
  - Always explain your code choices"""

  messages = []

  async for message in query(
      prompt="Create a data processing pipeline",
      options=ClaudeAgentOptions(system_prompt=custom_prompt),
  ):
      messages.append(message)
      if isinstance(message, AssistantMessage):
          print(message.content)
  ```
</CodeGroup>

<h2 id="compare-the-four-approaches">
  4 つのアプローチすべての比較
</h2>

4 つのカスタマイズ方法は、どこに存在するか、どのように共有されるか、および `claude_code` プリセットから何を保持するかが異なります。

| 機能             | CLAUDE.md     | 出力スタイル        | `systemPrompt` を追加 | カスタム `systemPrompt` |
| -------------- | ------------- | ------------- | ------------------ | ------------------- |
| **永続性**        | プロジェクトごとのファイル | ファイルとして保存     | セッションのみ            | セッションのみ             |
| **再利用性**       | プロジェクトごと      | プロジェクト全体      | コード重複              | コード重複               |
| **管理**         | ファイルシステム上     | CLI + ファイル    | コード内               | コード内                |
| **デフォルトツール**   | 保持            | 保持            | 保持                 | 失われる（含まれない限り）       |
| **組み込みセキュリティ** | 維持            | 維持            | 維持                 | 追加する必要がある           |
| **環境コンテキスト**   | 自動            | 自動            | 自動                 | 提供する必要がある           |
| **カスタマイズレベル**  | 追加のみ          | デフォルトを置き換え    | 追加のみ               | 完全な制御               |
| **バージョン管理**    | プロジェクトと共に     | はい            | コードと共に             | コードと共に              |
| **スコープ**       | プロジェクト固有      | ユーザーまたはプロジェクト | コードセッション           | コードセッション            |

「追加を使用」は TypeScript で `systemPrompt: { type: "preset", preset: "claude_code", append: "..." }` を使用するか、Python で `system_prompt={"type": "preset", "preset": "claude_code", "append": "..."}` を使用することを意味します。CLAUDE.md はシステムプロンプト自体を変更しません。SDK はそのコンテンツをプロジェクトコンテキストとして会話に注入します。

<h2 id="use-cases-and-best-practices">
  ユースケースとベストプラクティス
</h2>

<h3 id="when-to-use-claude-md">
  CLAUDE.md を使用する場合
</h3>

CLAUDE.md は、セッションで使用されるシステムプロンプトに関係なく、プロジェクト内のすべてのセッションに適用すべき命令に使用します。コーディング標準、一般的なコマンド、アーキテクチャコンテキスト、チーム規約などです。CLAUDE.md はリポジトリにコミットされるため、それが説明するコードと同期を保ちます。詳細なガイダンスについては、[CLAUDE.md に追加する場合](/docs/ja/memory#when-to-add-to-claude-md)を参照してください。

CLAUDE.md ファイルは `project` 設定ソースが有効な場合に読み込まれます。これはデフォルトの `query()` オプションの場合です。TypeScript で `settingSources` または Python で `setting_sources` を明示的に設定する場合は、プロジェクトレベルの CLAUDE.md の読み込みを続けるために `'project'` を含めてください。

<h3 id="when-to-use-output-styles">
  出力スタイルを使用する場合
</h3>

出力スタイルは、アプリケーションコードを変更することなく CLI と SDK 全体で再利用したいペルソナ用です。`.claude/output-styles` 内のファイルとして存在するため、同じペルソナは CLI の `/config` から、および一致する設定ソースを読み込むすべての SDK セッションから利用できます。

**最適な用途：**

* セッション全体での永続的な動作変更
* チーム共有設定
* コードレビュアー、データサイエンティスト、DevOps アシスタントなどの特殊なアシスタント
* バージョン管理が必要な複雑なプロンプト変更

**例：**

* 専用 SQL 最適化アシスタントの作成
* セキュリティ重視のコードレビュアーの構築
* 特定の教育学を持つティーチングアシスタントの開発

<h3 id="when-to-use-systemprompt-with-append">
  `systemPrompt` を追加で使用する場合
</h3>

`claude_code` プリセットがすでに製品に適合しており、追加の命令をレイヤーするだけで済む場合は、`append` を使用します。プリセットのツールガイダンス、安全ルール、コーディング規約を再実装することなく保持します。

**最適な用途：**

* 特定のコーディング標準または設定の追加
* 出力フォーマットのカスタマイズ
* ドメイン固有の知識の追加
* 応答詳細度の変更
* ツール命令を失わずに Claude Code のデフォルト動作を強化する

<h3 id="when-to-use-custom-systemprompt">
  カスタム `systemPrompt` を使用する場合
</h3>

[開始点を決定する](#decide-on-a-starting-point)で説明されているように、エージェントのサーフェス、アイデンティティ、または権限モデルが Claude Code のものと異なる場合は、カスタムプロンプトを使用します。ツールガイダンスと安全ルールを含む、エージェントが必要とする完全な命令セットを定義します。

**最適な用途：**

* Claude の動作を完全に制御
* 特殊なシングルセッションタスク
* 新しいプロンプト戦略のテスト
* デフォルトツールが不要な状況
* ユニークな動作を持つ特殊なエージェントの構築

<h2 id="combine-approaches">
  アプローチの組み合わせ
</h2>

これらのメソッドは組み合わせることができます。永続的な出力スタイルまたは CLAUDE.md は長期的な動作を設定し、`append` はセッション固有の指示を保存された設定に触れることなく上に重ねます。

<h3 id="combine-an-output-style-with-session-specific-additions">
  出力スタイルとセッション固有の追加を組み合わせる
</h3>

以下の例は、Code Reviewer 出力スタイルがすでにアクティブであることを想定しています。`append` ブロックはセッション固有のフォーカス領域をペルソナの上に重ねるため、単一のレビュー セッションで保存された出力スタイルを変更することなく OAuth とトークン ストレージを優先することができます：

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // Assuming "Code Reviewer" output style is active (via /config or settings)
  // Add session-specific focus areas
  const messages = [];

  for await (const message of query({
    prompt: "Review this authentication module",
    options: {
      systemPrompt: {
        type: "preset",
        preset: "claude_code",
        append: `
          For this review, prioritize:
          - OAuth 2.0 compliance
          - Token storage security
          - Session management
        `
      }
    }
  })) {
    messages.push(message);
  }
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions

  # Assuming "Code Reviewer" output style is active (via /config or settings)
  # Add session-specific focus areas
  messages = []

  async for message in query(
      prompt="Review this authentication module",
      options=ClaudeAgentOptions(
          system_prompt={
              "type": "preset",
              "preset": "claude_code",
              "append": """
              For this review, prioritize:
              - OAuth 2.0 compliance
              - Token storage security
              - Session management
              """,
          }
      ),
  ):
      messages.append(message)
  ```
</CodeGroup>

<h2 id="see-also">
  関連項目
</h2>

* [出力スタイル](/docs/ja/output-styles)：CLI の出力スタイルを作成、管理、共有します。ファイル形式とストレージの場所を含みます
* [Claude がプロジェクトを記憶する方法](/docs/ja/memory)：CLAUDE.md に何を入れるか、どこに配置するか、効果的なプロジェクト指示の書き方
* [TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript)：`systemPrompt`、`settingSources`、`settings` を含む完全な `Options` 型
* [Python SDK リファレンス](/docs/ja/agent-sdk/python)：`system_prompt` と `setting_sources` を含む完全な `ClaudeAgentOptions` 型
* [設定](/docs/ja/settings)：出力スタイルおよび他の設定が保存される場所を含む `settings.json` リファレンス
