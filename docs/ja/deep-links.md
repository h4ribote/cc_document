> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# リンクからセッションを起動する

> URL から Claude Code ターミナルセッションを開きます。ランブック、アラート、ダッシュボードに `claude-cli://` リンクを埋め込むと、クリックで Claude Code が正しいリポジトリで正しいプロンプトを使って開きます。

ディープリンクは `claude-cli://` URL で、Claude Code を新しいターミナルウィンドウで開きます。URL には作業ディレクトリとプリフィルするプロンプトを含めることができます。

これにより、タスクのワンクリック開始点を共有できます。Claude Code がインストールされている人がリンクをクリックすると、プロンプトが既に入力された状態でセッションが開きます。プロンプトは入力されていますが、Enter キーを押すまで送信されません。

ディープリンクは URL なので、リンクが使える場所ならどこにでも配置できます。

* インシデントランブックのステップで、影響を受けたサービスのリポジトリを診断プロンプト付きで開く
* モニタリングアラートやダッシュボードで、特定のメトリクスの調査プロンプトにリンクする
* README やウィキページでプロジェクトをオンボーディングプロンプト付きで開く
* CI 失敗通知で失敗したジョブの名前をプリフィルする

このページでは、[リンクの構築方法](#build-a-link)、[ランブックに埋め込む方法またはシェルからトリガーする方法](#examples)、および[各プラットフォームでハンドラー登録を管理または無効化する方法](#registration-and-supported-platforms)について説明します。

<h2 id="how-it-works">
  仕組み
</h2>

`claude-cli://` プレフィックスはカスタム URL スキームで、Claude Code がオペレーティングシステムに登録します。これは `mailto:` リンクがメールクライアントを開く方法と似ています。リンクは Web ページ、ウィキ、Slack メッセージ、またはリンクをレンダリングするアプリに配置できます。クリックすると以下のことが起こります。

1. ブラウザまたはアプリが URL をオペレーティングシステムに渡します。
2. オペレーティングシステムが `claude-cli://` プレフィックスを認識し、マシン上で Claude Code を起動します。
3. 新しいターミナルウィンドウが開き、Claude Code がリンクで指定されたディレクトリで実行され、リンクのプロンプトテキストが既に入力ボックスに入っています。
4. プロンプトを読み、必要に応じて編集し、Enter キーを押して送信します。

リンク自体はどこにでもホストできますが、セッションは常にクリックしたコンピューター上でローカルに開きます。各オペレーティングシステムで開くターミナルエミュレーターについては、[登録とサポートされているプラットフォーム](#registration-and-supported-platforms)を参照してください。

<Note>
  リンクを表示するプラットフォームはカスタム URL スキームを許可する必要があります。GitHub でレンダリングされた Markdown は `http` と `https` を許可しますが、README、issue、pull request、wiki で `claude-cli://` などのスキームを削除します。リンクテキストのみが表示され、リンクはなく、URL は非表示です。回避策については、[トラブルシューティング](#the-link-renders-as-plain-text-instead-of-being-clickable)を参照してください。
</Note>

<h3 id="what-a-launched-session-shows">
  起動されたセッションが表示するもの
</h3>

ディープリンクは単独では何も実行しません。リンクはディレクトリを選択し、プロンプトボックスを埋めるだけです。信頼していないページからリンクをクリックしても、プロンプトは依然として無害です。入力されたものを読んで Enter キーを押すまで、何もモデルに到達しません。

セッションが開くと、入力ボックスの下の警告行に `Prompt from an external link` と表示され、プロンプトを送信またはクリアするまで表示されたままになります。プロンプトが 1,000 文字を超える場合、警告には文字数が含まれ、長いプロンプトは指示を画面外に押し出す可能性があるため、Enter キーを押す前に全文をスクロールして確認するよう指示します。権限ルール、`CLAUDE.md`、および選択されたディレクトリの信頼プロンプトは、他のセッションと同じように適用されます。

<h2 id="build-a-link">
  リンクを構築する
</h2>

すべてのディープリンクは `claude-cli://open` で始まります。これはハンドラーが受け入れる唯一のパスで、その後にオプションのクエリパラメーターが続きます。最小形式は Claude Code をホームディレクトリで開き、空のプロンプトを表示します。

```text theme={null}
claude-cli://open
```

パラメーターを追加して、セッションが開始される場所とプロンプトボックスに含まれるテキストを制御します。

| パラメーター | 説明                                                                                                                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `q`    | プロンプトボックスにプリフィルするテキスト。[URL エンコード](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURIComponent)してください。複数行プロンプトの改行には `%0A` を使用します。最大 5,000 文字。 |
| `cwd`  | 作業ディレクトリとして使用する絶対パス。ネットワークおよび UNC パスは拒否されます。また、目に見えない制御文字または双方向制御文字を含むパスも拒否されます。                                                                                                     |
| `repo` | GitHub の `owner/name` スラッグ。Claude Code はそれを以前に見たローカルクローンに解決し、そこから開始します。一致するクローンがない場合、セッションはホームディレクトリで開きます。                                                                           |

`cwd` と `repo` は[作業ディレクトリを設定する 2 つの方法](#choose-between-cwd-and-repo)です。両方を渡す場合、`cwd` が優先され、`cwd` パスが存在しない場合でも `repo` は無視されます。

次のリンクは `acme/payments` というリポジトリを指し、2 行の診断プロンプトを含みます。独自のリンクを構築するときは、`acme/payments` をリポジトリの `owner/name` スラッグに置き換えてください。

```text theme={null}
claude-cli://open?repo=acme/payments&q=Investigate%20the%20failed%20deploy%20of%20payments-api.%0ACheck%20recent%20commits%20to%20main%20and%20the%20last%20successful%20build.
```

クリックすると新しいターミナルウィンドウが開き、Claude Code が `acme/payments` のローカルクローンで起動し、プロンプトボックスがデコードされたテキストで埋められます。

```text theme={null}
Investigate the failed deploy of payments-api.
Check recent commits to main and the last successful build.
```

Enter キーを押して送信する前にプロンプトを編集できます。リポジトリのローカルクローンがない場合、セッションはホームディレクトリで開きます。複数のクローンまたはワークツリーがある場合にローカルパスがどのように選択されるかについては、[`cwd` と `repo` の選択](#choose-between-cwd-and-repo)を参照してください。

<h3 id="choose-between-cwd-and-repo">
  `cwd` と `repo` の選択
</h3>

リンクをクリックするすべての人がプロジェクトを同じ絶対パスに持っている場合（標準化された devcontainer または VM イメージなど）は `cwd` を使用します。

リンクが共有され、各人がクローンを別の場所にクローンする場合は `repo` を使用します。Claude Code はスラッグをローカルパスに解決します。

* `claude` を Git リポジトリで実行するたびに、そのディレクトリのファイルシステムパスがリポジトリの GitHub `owner/name` スラッグに対して記録されます。
* ディープリンクが到着すると、`repo` は最近使用した一致するパスを開きます。複数のクローンとワークツリーは個別に追跡されるため、最後に作業したものを選択します。
* ルックアップは、少なくとも 1 回 Claude Code を実行したパスのみを検出します。
* リンクはどのブランチがチェックアウトされているかを変更しません。セッションはそのディレクトリが現在ある状態で開きます。

ウェルカムヘッダーは、選択したパスを表示するため、正しいクローンが開いたことを確認できます。

<h2 id="examples">
  例
</h2>

以下のセクションでは、ディープリンクを使用する 2 つの一般的な方法を示します。ドキュメント内の Markdown リンクとしてと、スクリプトまたはシェルエイリアスのコマンドとしてです。

<h3 id="embed-a-link-in-a-runbook">
  ランブックにリンクを埋め込む
</h3>

ランブック内のディープリンクは、トリアージを行う人に、正しいリポジトリで準備されたプロンプトを使って調査を開始するワンクリック方法を提供します。ランブックをレンダリングするプラットフォームはカスタム URL スキームを許可する必要があります。GitHub でレンダリングされた Markdown は `claude-cli://` を許可しないため、GitHub README、issue、wiki のディープリンクはラベルのみを表示し、クリック可能なリンクはありません。回避策については、[トラブルシューティングノート](#the-link-renders-as-plain-text-instead-of-being-clickable)を参照してください。

プロンプトは URL の一部であり、URL エンコードする必要があります。エンコードされた値を生成するには、ブラウザコンソールまたは任意の URL エンコーダーで `encodeURIComponent` を使用してプロンプトテキストを渡します。

以下の例は、`web-gateway` というサービスのインシデントランブックに調査エントリポイントを追加します。

```markdown theme={null}
## High 5xx rate on web-gateway

1. Acknowledge the page in PagerDuty.
2. [Open Claude Code in the gateway repo](claude-cli://open?repo=acme/web-gateway&q=5xx%20rate%20is%20elevated%20on%20web-gateway.%20Check%20recent%20deploys%2C%20error%20logs%20from%20the%20last%2030%20minutes%2C%20and%20open%20incidents%20in%20Linear.)
3. Post initial findings in #incident.
```

独自のランブックでこれを使用するには、`acme/web-gateway` をサービスのリポジトリスラッグに置き換えます。これにより、Claude Code がインストールされており、そのリポジトリのローカルクローンを持つエンジニアがステップ 2 をクリックして、プロンプトを送信する準備ができた状態で調査を開始できます。

<h3 id="open-a-link-from-the-shell">
  シェルからリンクを開く
</h3>

クリックする代わりに、シェルスクリプト、エイリアス、または自動化からディープリンクを開くこともできます。オペレーティングシステムの URL 開くコマンドをリンクを引数として呼び出します。

<Tabs>
  <Tab title="macOS">
    組み込みの `open` コマンドは URL を登録された `claude-cli://` ハンドラーに渡します。

    ```bash theme={null}
    open "claude-cli://open?repo=acme/payments&q=review%20open%20PRs"
    ```
  </Tab>

  <Tab title="Linux">
    ほとんどのデスクトップ環境は `xdg-open` を提供し、URL を登録されたハンドラーに渡します。

    ```bash theme={null}
    xdg-open "claude-cli://open?repo=acme/payments&q=review%20open%20PRs"
    ```
  </Tab>

  <Tab title="Windows">
    PowerShell では、`Start-Process` は URL を登録されたハンドラーに渡します。

    ```powershell theme={null}
    Start-Process "claude-cli://open?repo=acme/payments&q=review%20open%20PRs"
    ```

    `cmd.exe` では、`start` は最初の引用符付き引数をウィンドウタイトルとして扱うため、URL の前に空のタイトルを渡します。

    ```cmd theme={null}
    start "" "claude-cli://open?repo=acme/payments&q=review%20open%20PRs"
    ```
  </Tab>
</Tabs>

<h2 id="registration-and-supported-platforms">
  登録とサポートされているプラットフォーム
</h2>

Claude Code は、macOS、Linux、Windows で最初に対話的セッションを開始するときに、`claude-cli://` ハンドラーをオペレーティングシステムに登録します。別のインストールコマンドを実行する必要はありません。登録はユーザーレベルの場所にのみ書き込みます。

| プラットフォーム | ハンドラーの場所                                                                                                 |
| -------- | -------------------------------------------------------------------------------------------------------- |
| macOS    | `~/Applications/Claude Code URL Handler.app`                                                             |
| Linux    | `$XDG_DATA_HOME/applications` の下の `claude-code-url-handler.desktop`。デフォルトは `~/.local/share/applications` |
| Windows  | `HKEY_CURRENT_USER\Software\Classes\claude-cli`                                                          |

ハンドラーは検出されたターミナルエミュレーターで Claude Code を起動します。macOS では、Claude Code は最後の対話的セッションからターミナルを記憶し、再利用します。iTerm2、Ghostty、kitty、Alacritty、WezTerm、Terminal.app をサポートしています。Linux では `$TERMINAL` 環境変数を尊重し、次に `x-terminal-emulator`、次に一般的なエミュレーターのリストを使用します。Windows では Windows Terminal を優先し、次に PowerShell、次に `cmd.exe` を使用します。

登録を完全に防ぐには、`settings.json` で [`disableDeepLinkRegistration`](/docs/ja/settings) を `"disable"` に設定します。組織全体でこれを強制し、ユーザーが再度有効にできないようにするには、代わりに[マネージド設定](/docs/ja/server-managed-settings)で設定します。

<h2 id="open-a-vs-code-tab-instead-of-a-terminal">
  ターミナルの代わりに VS Code タブを開く
</h2>

VS Code 拡張機能は `vscode://anthropic.claude-code/open` で独自のハンドラーを登録し、ターミナルウィンドウではなく Claude Code エディタータブを開きます。その URL のパラメーターについては、[他のツールから VS Code タブを起動する](/docs/ja/vs-code#launch-a-vs-code-tab-from-other-tools)を参照してください。

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

<h3 id="clicking-the-link-does-nothing">
  リンクをクリックしても何も起こらない
</h3>

ハンドラーはまだ登録されていない可能性があります。そのマシンで対話的な `claude` セッションを 1 回開始し、終了してから、リンクを再度試してください。Linux でデスクトップ環境がない場合、`xdg-open` はディスパッチするものがない可能性があります。

<h3 id="the-link-renders-as-plain-text-instead-of-being-clickable">
  リンクがプレーンテキストとしてレンダリングされ、クリック可能ではない
</h3>

一部の Markdown レンダラーは `http` と `https` リンクのみを許可し、他の URL スキームを削除します。GitHub は README、issue、pull request、wiki でこれを行います。`[label](claude-cli://...)` は `label` のみとしてレンダリングされ、リンクはなく、URL は削除されます。これらのプラットフォームでは、ディープリンクをコードブロックに配置して、読者が URL を見てブラウザーのアドレスバーに貼り付けられるようにします。

<h3 id="the-session-opens-in-my-home-directory-instead-of-the-repo">
  セッションがリポジトリの代わりにホームディレクトリで開く
</h3>

`repo` パラメーターは、Claude Code が既に見たクローンのみに解決します。クローン内で `claude` を 1 回実行してパスを記録するか、リンクを `cwd` と絶対パスを使用するように切り替えます。

<h3 id="the-link-opens-the-wrong-terminal">
  リンクが間違ったターミナルを開く
</h3>

macOS では、好みのターミナルで `claude` を 1 回開始すると、次のディープリンクがそれを使用します。Linux では、`$TERMINAL` 環境変数を好みのエミュレーターのコマンド名に設定します。Windows では、順序は固定です。Windows Terminal をインストールして、リンクが PowerShell または `cmd.exe` ウィンドウの代わりにそこで開くようにします。

<h2 id="learn-more">
  詳細情報
</h2>

これらのページは、Claude Code セッションを起動または拡張する関連する方法をカバーしています。

* [Skills](/docs/ja/skills)：長いランブックプロンプトをリポジトリに `/skill` として保存し、ディープリンクの `q` パラメーターはそれを名前で指定するだけで済みます。
* [非対話モード](/docs/ja/headless)：スクリプトから Claude を実行し、ターミナルを開かずに出力をキャプチャします。
