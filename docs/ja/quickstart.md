> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# クイックスタート

> Claude Code へようこそ！

このクイックスタートガイドを使用すれば、数分で AI を活用したコーディング支援を利用できます。このガイドを終了する頃には、一般的な開発タスクに Claude Code を使用する方法を理解できるようになります。

<h2 id="before-you-begin">
  始める前に
</h2>

以下を確認してください：

* ターミナルまたはコマンドプロンプトが開いている
  * ターミナルを使用したことがない場合は、[ターミナルガイド](/docs/ja/terminal-guide)をご覧ください
* 作業するコードプロジェクトがある
* [Claude サブスクリプション](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=quickstart_prereq)（Pro、Max、Team、または Enterprise）、[Claude Console](https://console.anthropic.com/) アカウント、または[サポートされているクラウドプロバイダー](/docs/ja/third-party-integrations)経由のアクセスがある

<Note>
  このガイドはターミナル CLI について説明しています。Claude Code は[ウェブ](https://claude.ai/code)、[デスクトップアプリ](/docs/ja/desktop)、[VS Code](/docs/ja/vs-code) および [JetBrains IDE](/docs/ja/jetbrains)、[Slack](/docs/ja/slack)、および [GitHub Actions](/docs/ja/github-actions) と [GitLab](/docs/ja/gitlab-ci-cd) を使用した CI/CD でも利用できます。[すべてのインターフェース](/docs/ja/overview#use-claude-code-everywhere)を参照してください。
</Note>

<h2 id="step-1-install-claude-code">
  ステップ 1：Claude Code をインストールする
</h2>

To install Claude Code, use one of the following methods:

<Tabs>
  <Tab title="Native Install (Recommended)">
    **macOS, Linux, WSL:**

    ```bash theme={null}
    curl -fsSL https://claude.ai/install.sh | bash
    ```

    **Windows PowerShell:**

    ```powershell theme={null}
    irm https://claude.ai/install.ps1 | iex
    ```

    **Windows CMD:**

    ```batch theme={null}
    curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
    ```

    If you see `The token '&&' is not a valid statement separator`, you're in PowerShell, not CMD. If you see `'irm' is not recognized as an internal or external command`, you're in CMD, not PowerShell. Your prompt shows `PS C:\` when you're in PowerShell and `C:\` without the `PS` when you're in CMD.

    If the install command fails with `syntax error near unexpected token '<'`, a `403`, or another curl error, see [Troubleshoot installation](/docs/en/troubleshoot-install#find-your-error) to match the error to a fix and for alternative install methods.

    [Git for Windows](https://git-scm.com/downloads/win) is recommended on native Windows so Claude Code can use the Bash tool. If Git for Windows is not installed, Claude Code uses PowerShell as the shell tool instead. WSL setups do not need Git for Windows.

    <Info>
      Native installations automatically update in the background to keep you on the latest version.
    </Info>
  </Tab>

  <Tab title="Homebrew">
    ```bash theme={null}
    brew install --cask claude-code
    ```

    Homebrew offers two casks. `claude-code` tracks the stable release channel, which is typically about a week behind and skips releases with major regressions. `claude-code@latest` tracks the latest channel and receives new versions as soon as they ship.

    <Info>
      Homebrew installations do not auto-update. Run `brew upgrade claude-code` or `brew upgrade claude-code@latest`, depending on which cask you installed, to get the latest features and security fixes.
    </Info>
  </Tab>

  <Tab title="WinGet">
    ```powershell theme={null}
    winget install Anthropic.ClaudeCode
    ```

    <Info>
      WinGet installations do not auto-update. Run `winget upgrade Anthropic.ClaudeCode` periodically to get the latest features and security fixes.
    </Info>
  </Tab>
</Tabs>

You can also install with [apt, dnf, or apk](/docs/en/setup#install-with-linux-package-managers) on Debian, Fedora, RHEL, and Alpine.

<h2 id="step-2-log-in-to-your-account">
  ステップ 2：アカウントにログインする
</h2>

Claude Code を使用するにはアカウントが必要です。`claude` コマンドでインタラクティブセッションを開始すると、初回使用時にログインするよう求められます：

```bash theme={null}
claude
```

Claude サブスクリプションまたは Console アカウントの場合は、プロンプトに従ってブラウザで認証を完了してください。後でアカウントを切り替えるか再認証するには、実行中のセッション内で `/login` と入力します：

```text theme={null}
/login
```

以下のいずれかのアカウントタイプを使用してログインできます：

* [Claude Pro、Max、Team、または Enterprise](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=quickstart_login)（推奨）
* [Claude Console](https://console.anthropic.com/)（プリペイドクレジット付き API アクセス）。初回ログイン時に、コスト追跡を一元化するために「Claude Code」ワークスペースが Console に自動的に作成されます。
* [Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry](/docs/ja/third-party-integrations)（エンタープライズクラウドプロバイダー）
* 組織が実行している自己ホスト型の [Claude apps gateway](/docs/ja/claude-apps-gateway)：管理者がゲートウェイ URL を事前に設定し、`/login` で **Cloud gateway** 画面が直接開き、企業 SSO でサインインできます

ログイン後、認証情報が保存され、再度ログインする必要はありません。

<h2 id="step-3-start-your-first-session">
  ステップ 3：最初のセッションを開始する
</h2>

任意のプロジェクトディレクトリでターミナルを開き、Claude Code を開始します：

```bash theme={null}
cd /path/to/your/project
claude
```

Claude Code プロンプトが表示され、バージョン、現在のモデル、および作業ディレクトリが上に表示されます。利用可能なコマンドについては `/help` を入力するか、前の会話を続行するには `/resume` を入力します。

<Tip>
  ログイン後（ステップ 2）、認証情報がシステムに保存されます。詳細については、[認証情報管理](/docs/ja/authentication#credential-management)を参照してください。
</Tip>

<h2 id="step-4-ask-your-first-question">
  ステップ 4：最初の質問をする
</h2>

コードベースを理解することから始めましょう。以下のコマンドのいずれかを試してください：

```text theme={null}
what does this project do?
```

Claude はファイルを分析して概要を提供します。より具体的な質問をすることもできます：

```text theme={null}
what technologies does this project use?
```

```text theme={null}
where is the main entry point?
```

```text theme={null}
explain the folder structure
```

Claude 自体の機能について質問することもできます：

```text theme={null}
what can Claude Code do?
```

```text theme={null}
how do I create custom skills in Claude Code?
```

```text theme={null}
can Claude Code work with Docker?
```

<Note>
  Claude Code は必要に応じてプロジェクトファイルを読み込みます。コンテキストを手動で追加する必要はありません。
</Note>

<h2 id="step-5-make-your-first-code-change">
  ステップ 5：最初のコード変更を行う
</h2>

次に、Claude Code に実際のコーディングを行わせましょう。簡単なタスクを試してください：

```text theme={null}
メインファイルに hello world 関数を追加してください
```

Claude Code は以下を実行します：

1. 適切なファイルを見つける
2. 提案された変更を表示する
3. 承認を求める
4. 編集を行う

<Note>
  Claude Code はファイルを変更する前に常に許可を求めます。個別の変更を承認するか、セッション中に「すべて承認」モードを有効にすることができます。
</Note>

<h2 id="step-6-use-git-with-claude-code">
  ステップ 6：Claude Code で Git を使用する
</h2>

Claude Code は Git 操作を会話形式にします：

```text theme={null}
どのファイルを変更しましたか？
```

```text theme={null}
説明的なメッセージで変更をコミットしてください
```

より複雑な Git 操作を求めることもできます：

```text theme={null}
feature/quickstart という名前の新しいブランチを作成してください
```

```text theme={null}
最後の 5 つのコミットを表示してください
```

```text theme={null}
マージコンフリクトの解決を手伝ってください
```

<h2 id="step-7-fix-a-bug-or-add-a-feature">
  ステップ 7：バグを修正するか機能を追加する
</h2>

Claude はデバッグと機能実装に長けています。

自然言語で実現したいことを説明します：

```text theme={null}
ユーザー登録フォームに入力検証を追加してください
```

または既存の問題を修正します：

```text theme={null}
ユーザーが空のフォームを送信できるバグがあります。修正してください
```

Claude Code は以下を実行します：

* 関連するコードを見つける
* コンテキストを理解する
* ソリューションを実装する
* 利用可能な場合はテストを実行する

<h2 id="step-8-test-out-other-common-workflows">
  ステップ 8：他の一般的なワークフローを試す
</h2>

Claude と連携する方法は多数あります：

**コードをリファクタリングする**

```text theme={null}
認証モジュールをリファクタリングして、コールバックの代わりに async/await を使用するようにしてください
```

**テストを書く**

```text theme={null}
計算機関数のユニットテストを書いてください
```

**ドキュメントを更新する**

```text theme={null}
インストール手順で README を更新してください
```

**コードレビュー**

```text theme={null}
変更をレビューして改善を提案してください
```

<Tip>
  有能な同僚と話すように Claude と話してください。実現したいことを説明すれば、それを実現するのに役立ちます。
</Tip>

<h2 id="essential-commands">
  必須コマンド
</h2>

日常的に使用する最も重要なコマンドは以下の通りです。シェルコマンドはターミナルから実行して Claude Code を開始または再開します。セッションコマンドは Claude Code 起動後に実行します。

**シェルコマンド**

| コマンド                | 機能                   | 例                                   |
| ------------------- | -------------------- | ----------------------------------- |
| `claude`            | インタラクティブモードを開始する     | `claude`                            |
| `claude "task"`     | 1 回限りのタスクを実行する       | `claude "fix the build error"`      |
| `claude -p "query"` | 1 回限りのクエリを実行してから終了する | `claude -p "explain this function"` |
| `claude -c`         | 現在のディレクトリで最新の会話を続行する | `claude -c`                         |
| `claude -r`         | 前の会話を再開する            | `claude -r`                         |

**セッションコマンド**

| コマンド               | 機能                | 例        |
| ------------------ | ----------------- | -------- |
| `/clear`           | 会話履歴をクリアする        | `/clear` |
| `/help`            | 利用可能なコマンドを表示する    | `/help`  |
| `/exit` または Ctrl+D | Claude Code を終了する | `/exit`  |

シェルコマンドの完全なリストについては [CLI リファレンス](/docs/ja/cli-reference)を、セッションコマンドの完全なリストについては [コマンドリファレンス](/docs/ja/commands)を参照してください。

<h2 id="pro-tips-for-beginners">
  初心者向けのプロのヒント
</h2>

詳細については、[ベストプラクティス](/docs/ja/best-practices)と[一般的なワークフロー](/docs/ja/common-workflows)を参照してください。

<AccordionGroup>
  <Accordion title="リクエストを具体的にする">
    代わりに：'バグを修正してください'

    試してください：'ユーザーが間違った認証情報を入力した後に空白の画面が表示されるログインバグを修正してください'
  </Accordion>

  <Accordion title="段階的な指示を使用する">
    複雑なタスクをステップに分割します：

    ```text theme={null}
    1. ユーザープロファイル用の新しいデータベーステーブルを作成する
    2. ユーザープロファイルを取得および更新するための API エンドポイントを作成する
    3. ユーザーが自分の情報を表示および編集できるウェブページを構築する
    ```
  </Accordion>

  <Accordion title="Claude に最初に探索させる">
    変更を加える前に、Claude にコードを理解させます：

    ```text theme={null}
    データベーススキーマを分析する
    ```

    ```text theme={null}
    英国の顧客によって最も頻繁に返品される製品を表示するダッシュボードを構築する
    ```
  </Accordion>

  <Accordion title="ショートカットで時間を節約する">
    * `/` を入力してすべてのコマンドとスキルを表示する
    * Tab キーでコマンド補完を使用する
    * ↑ キーでコマンド履歴を表示する
    * `Shift+Tab` を押して権限モードをサイクルさせる
  </Accordion>
</AccordionGroup>

<h2 id="what’s-next">
  次のステップ
</h2>

基本を学習したので、より高度な機能を探索してください：

<CardGroup cols={2}>
  <Card title="Claude Code の仕組み" icon="microchip" href="/docs/ja/how-claude-code-works">
    agentic ループ、組み込みツール、および Claude Code がプロジェクトと相互作用する方法を理解する
  </Card>

  <Card title="ベストプラクティス" icon="star" href="/docs/ja/best-practices">
    効果的なプロンプティングとプロジェクト設定でより良い結果を得る
  </Card>

  <Card title="一般的なワークフロー" icon="graduation-cap" href="/docs/ja/common-workflows">
    一般的なタスクのステップバイステップガイド
  </Card>

  <Card title="Claude Code を拡張する" icon="puzzle-piece" href="/docs/ja/features-overview">
    CLAUDE.md、スキル、フック、MCP などでカスタマイズする
  </Card>
</CardGroup>

<h2 id="getting-help">
  ヘルプを取得する
</h2>

* **Claude Code 内**：`/help` を入力するか、「how do I...」と質問する
* **ドキュメント**：ここにいます！他のガイドを参照してください
* **コミュニティ**：[Discord](https://www.anthropic.com/discord) に参加してヒントとサポートを得る
