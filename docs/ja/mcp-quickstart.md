> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# MCP サーバーに接続する

> MCP サーバーを Claude Code に追加し、接続を確認し、ディスク上の設定を見つけます。

[Model Context Protocol（MCP）](https://modelcontextprotocol.io/introduction)により、Claude Code は問題トラッカーの検索、データベースのクエリ、Web ブラウザの制御など、組み込みセット以外のツールを使用できます。これらのツールは MCP サーバーから提供され、マシン上で実行されるか、ホストされたサービスとして実行されます。

このガイドでは、Claude Code CLI を使用して 1 つの MCP サーバーをエンドツーエンドで接続する手順を説明します。最後には、サーバーが接続され応答している状態になり、その設定がディスク上のどこにあるかを知り、最も一般的な接続エラーを修正する方法を知ることができます。

<Note>
  MCP サーバーは、デスクトップアプリ、VS Code、Web など、他のサーフェスからも追加できます。[他のサーフェスから接続する](#connect-from-other-surfaces)を参照してください。
</Note>

Claude Code で MCP サーバーを接続および設定するすべての方法については、[MCP リファレンス](/docs/ja/mcp)を参照してください。

<h2 id="before-you-begin">
  開始する前に
</h2>

以下があることを確認してください。

* [Claude Code がインストール](/docs/ja/quickstart)され、認証されている
* プロジェクトディレクトリで開いているターミナル。空のディレクトリを含む、任意のディレクトリが機能します。

<h2 id="add-and-verify-a-server">
  サーバーを追加して確認する
</h2>

以下の例は、[Claude Code ドキュメンテーション MCP サーバー](https://code.claude.com/docs/mcp)に接続します。これは Claude Code ドキュメント全体にフルテキスト検索を備えたホストされたサーバーです。認証や特別な設定は必要ないため、セットアップフローをテストするための最初のサーバーとして適しています。

手順はすべてのサーバーで同じです。追加し、接続ステータスを確認し、セッションで使用し、最後にオプションのクリーンアップステップを実行します。[追加の MCP サーバーの例](#additional-mcp-server-examples)に示されているブラウザサインインなど、一部のサーバーはステップを追加します。接続するサーバーの詳細については、[Anthropic Directory](/docs/ja/mcp#find-and-build-mcp-servers)を参照してください。

<Steps>
  <Step title="MCP サーバーを追加する">
    Claude Code にサーバーを登録します。`claude` セッション内ではなく、ターミナルで実行します。会話を開始する前にサーバーを設定しています。

    ```bash theme={null}
    claude mcp add --transport http claude-code-docs https://code.claude.com/docs/mcp
    ```

    コマンドの部分：

    * `claude mcp add`：Claude Code にサーバーを登録します。
    * `--transport http`：サーバーはローカルプロセスとして実行されるのではなく、URL でホストされています。
    * `claude-code-docs`：自分で作成する名前。同じサーバーを `docs` と呼ぶことも同じように機能します。Claude Code は選択した名前を使用して、Claude の出力でサーバーのツールにラベルを付け、`claude mcp remove` などのコマンドでサーバーを参照します。
    * `https://code.claude.com/docs/mcp`：サーバーがホストされている URL。

    コマンドは `Added HTTP MCP server claude-code-docs with URL: https://code.claude.com/docs/mcp to local config` のような確認を出力します。`local config` の部分は、サーバーがあなたに登録されていることを意味します。このプロジェクトでは、別のプロジェクトで Claude Code を開始した場合、このサーバーはそこでアクティブではありません。すべてのプロジェクトに対して一度サーバーを登録するには、ユーザースコープで追加します。これは[サーバースコープを変更する](#change-server-scope)で説明されています。
  </Step>

  <Step title="接続ステータスを確認する">
    サーバーがサーバーリストに表示されることを確認し、そのステータスを確認します。

    ```bash theme={null}
    claude mcp list
    ```

    サーバーはステータスインジケーター付きで表示されます。

    | ステータス                              | 意味                                                                                                                               |
    | :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
    | `✓ Connected`                      | 使用可能です。これは `claude-code-docs` で表示されるはずです                                                                                         |
    | `! Connected · tools fetch failed` | サーバーは接続されましたが、ツールをリストできませんでした。エラーの詳細については `claude mcp get <name>` を実行してください                                                      |
    | `! Needs authentication`           | サーバーに到達可能ですが、ブラウザサインインが必要です。または `--header` で渡されたトークンが必要です。[サインインが必要なサーバーに接続する](#connect-a-server-that-requires-sign-in)を参照してください |
    | `✗ Failed to connect`              | サーバーが応答しませんでした。[トラブルシューティング](#troubleshooting)を参照してください                                                                          |
    | `✗ Connection error`               | 接続試行がエラーをスローしました。[トラブルシューティング](#troubleshooting)を参照してください                                                                        |
    | `⏸ Pending approval`               | まだ承認していないプロジェクトスコープのサーバー。[.mcp.json を直接編集する](#edit-mcp-json-directly)を参照してください                                                   |
  </Step>

  <Step title="サーバーを使用する">
    セッションを開始し、Claude に名前で新しいサーバーを使用するよう依頼します。

    ```bash theme={null}
    claude
    ```

    ```text theme={null}
    Use the claude-code-docs server to look up what MCP_TIMEOUT does
    ```

    <Info>
      Claude は関連するツールを自動的に選択するため、通常はプロンプトでサーバーに名前を付ける必要はありません。ここで名前を付けることで、Web フェッチなど同じ質問に答えることができる別のツールではなく、新しいサーバーを通じてデモンストレーションが進むことを保証します。
    </Info>

    Claude が初めてサーバーを呼び出すとき、新しいツールを使用する許可を求めます。続行するには承認してください。Claude の出力のツール呼び出しはサーバー名でラベル付けされており、これにより答えが Claude の組み込み知識ではなく MCP サーバーから来たことを確認できます。
  </Step>

  <Step title="サーバーを削除する">
    このステップはオプションです。実験が終わったら、サーバーを削除できます。

    ```bash theme={null}
    claude mcp remove claude-code-docs
    ```

    <Note>
      接続されたサーバーはそれぞれ、ツール名とサーバー命令がすべてのセッションに読み込まれるため、[Claude のコンテキストウィンドウ](/docs/ja/how-claude-code-works#the-context-window)にスペースを取ります。使用しなくなったサーバーを削除すると、そのスペースが解放されます。
    </Note>
  </Step>
</Steps>

<h2 id="where-servers-are-saved">
  サーバーが保存される場所
</h2>

`claude mcp add` コマンドは、サーバーの詳細を設定ファイルに書き込みます。デフォルトでは、`local` スコープでサーバーを登録します。これはあなたのみが使用でき、現在のプロジェクトでのみアクティブです。`--scope user` を渡してすべてのプロジェクトに対して一度登録するか、`--scope project` を渡してチームメイトと共有します。[サーバースコープを変更する](#change-server-scope)では両方を説明しています。

<Note>
  `claude mcp add` は PowerShell やコマンドプロンプトを含むすべてのシェルで同じように機能します。`claude` セッション内では、`/mcp` コマンドを使用して、既に追加したサーバーを確認および管理します。
</Note>

サーバーを追加する他の方法があり、それぞれこのページの後半で説明されています。

* [ローカルサーバーを追加する](#add-a-local-server)：URL に接続する代わりに、マシン上でプログラムを実行します。
* [.mcp.json を直接編集する](#edit-mcp-json-directly)：コマンドを使用する代わりに、JSON エントリを自分で書き込みます。
* [サインインが必要なサーバーに接続する](#connect-a-server-that-requires-sign-in)：ツールが機能する前にブラウザサインインが必要なホストされたサーバーを追加します。

<h3 id="find-your-configuration-on-disk">
  ディスク上の設定を見つける
</h3>

`claude mcp add` コマンドは、`--scope` フラグに応じて、2 つのファイルに分散された 3 つのスコープのいずれかにサーバーを書き込みます。これらのファイルを直接編集する必要はありませんが、どこにあるかを知ることはデバッグとバージョン管理に役立ちます。

| スコープ      | ファイル                                       | 利用可能な対象                |
| :-------- | :----------------------------------------- | :--------------------- |
| `local`   | `~/.claude.json`、このプロジェクトのエントリの下           | あなたのみ、このプロジェクトのみ。デフォルト |
| `project` | プロジェクトルートの `.mcp.json`                     | プロジェクトをクローンした全員        |
| `user`    | `~/.claude.json`、トップレベルの `mcpServers` キーの下 | あなたのみ、すべてのプロジェクト       |

Windows では、`~/.claude.json` は `%USERPROFILE%\.claude.json`（通常は `C:\Users\YourName\.claude.json`）に解決されます。[`CLAUDE_CONFIG_DIR`](/docs/ja/env-vars)を設定している場合、Claude Code はそのディレクトリ内から `.claude.json` を読み込みます。

`claude mcp get claude-code-docs` を実行して、どのスコープがサーバーの定義を保持しているかを確認します。同じサーバーが複数で定義されている場合のスコープの相互作用については、[MCP インストールスコープ](/docs/ja/mcp#mcp-installation-scopes)を参照してください。

<h2 id="change-server-scope">
  サーバースコープを変更する
</h2>

サーバーのスコープは追加時に固定されるため、スコープを変更するには、エントリを削除して新しいスコープで再度追加することを意味します。以下の両方のケースは、最初のウォークスルーからローカルエントリを削除することから始まるため、サーバーは定義が 1 つだけです。そのウォークスルーの最後で既に削除している場合は、このコマンドをスキップしてください。

```bash theme={null}
claude mcp remove claude-code-docs --scope local
```

<h3 id="use-a-server-in-all-your-projects">
  すべてのプロジェクトでサーバーを使用する
</h3>

サーバーを `user` スコープで再度追加して、開くすべてのプロジェクトでアクティブにします。これはあなたのみが使用できます。

```bash theme={null}
claude mcp add --scope user --transport http claude-code-docs https://code.claude.com/docs/mcp
```

<h3 id="share-a-server-with-your-team">
  チームとサーバーを共有する
</h3>

サーバーを `project` スコープで再度追加します。これはプロジェクトルートの `.mcp.json` に書き込みます。

```bash theme={null}
claude mcp add --scope project --transport http claude-code-docs https://code.claude.com/docs/mcp
```

`.mcp.json` をバージョン管理にコミットします。リポジトリをクローンして Claude Code を開始するチームメイトは、サーバーを承認するプロンプトを表示し、その後、彼らのためにも接続します。

<h2 id="additional-mcp-server-examples">
  追加の MCP サーバーの例
</h2>

最初のウォークスルーは、サインインなしで接続するホストされたサーバーを使用しました。以下の例は、他の 2 つの一般的な形状をカバーしており、同じ追加、確認、使用フローを使用しています。

<h3 id="add-a-local-server">
  ローカルサーバーを追加する
</h3>

ローカル stdio サーバーは、Claude Code が URL 経由で到達するサービスではなく、マシン上でサブプロセスとして開始するプログラムです。ブラウザ、ファイルシステム、データベースソケットなどのローカルリソースへのアクセスが必要なツールに使用します。

[Playwright MCP サーバー](https://github.com/microsoft/playwright-mcp)は試すのに適しています。Claude にブラウザを提供し、ナビゲート、クリック、読み取りができます。アカウントは必要ありません。`npx` を通じて実行されるため、[Node.js](https://nodejs.org/en/download) 18 以降が必要です。

<Steps>
  <Step title="Playwright サーバーを追加する">
    Claude Code が実行して開始するコマンドでサーバーを登録します。

    ```bash theme={null}
    claude mcp add playwright -- npx -y @playwright/mcp@latest
    ```

    このコマンドはホストされた例と 3 つの方法で異なります。

    * ローカルサーバーはデフォルトの `stdio` トランスポートを使用するため、`--transport` フラグはありません。
    * `--` セパレーターの後のすべてはサーバーを開始するために Claude Code が実行するコマンドです。
    * `-y` は、`npx` にプロンプトなしでパッケージをインストールするよう指示します。

    Playwright はマシンに既にインストールされている Chrome を駆動します。別のブラウザを使用するには、`@playwright/mcp@latest` の後に `--browser` を追加します。例えば `--browser firefox`。
  </Step>

  <Step title="接続を確認する">
    `Added` 確認はエントリが保存されたことを意味し、コマンドが実行されることではありません。接続を確認します。

    ```bash theme={null}
    claude mcp list
    ```

    最初のチェックは `npx` がパッケージをダウンロードしている間に `✗ Failed to connect` を表示できるため、少し待ってから再度実行してください。
  </Step>

  <Step title="ブラウザを使用する">
    Claude にブラウザが必要なタスクを与えます。

    ```text theme={null}
    Use playwright to open https://example.com and tell me the page title
    ```

    ブラウザウィンドウが開き、動作を確認でき、Claude の出力のツール呼び出しは `playwright` サーバー名とアクション（`browser_navigate` など）でラベル付けされます。

    ローカル開発サーバーを指すことで、変更後もページが引き続きレンダリングされることを確認するか、バグレポートを段階的に実行させてみてください。
  </Step>
</Steps>

<h3 id="connect-a-server-that-requires-sign-in">
  サインインが必要なサーバーに接続する
</h3>

Sentry、Linear、Notion などのホストされたサービスは、MCP サーバーを OAuth の背後で実行します。サーバーの URL を追加し、ブラウザを通じてサインインします。

以下の手順は Sentry を例として使用しています。別のサービスに接続するには、その URL を置き換えます。これは [Anthropic Directory](/docs/ja/mcp#find-and-build-mcp-servers) またはサービスのドキュメントで見つけることができます。

<Steps>
  <Step title="サーバーを追加する">
    `add` コマンドはドキュメントサーバーと同じですが、Sentry の URL を使用します。

    ```bash theme={null}
    claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
    ```

    追加後、`claude mcp list` はサーバーを `! Needs authentication` で表示します。これは予想されています。次のステップでサインインが完了します。
  </Step>

  <Step title="ブラウザで認証する">
    Claude Code セッションを開始し、MCP パネルを開きます。

    ```text theme={null}
    /mcp
    ```

    リストから `sentry` を選択し、Enter キーを押して、`Authenticate` を選択します。ブラウザが Sentry のサインインページに開きます。そこで接続を承認します。

    Claude Code に戻ると、サーバーのステータスが接続に変わります。サインインが失敗するか、ブラウザが開かない場合は、[トラブルシューティング](#troubleshooting)を参照してください。
  </Step>

  <Step title="サーバーを使用する">
    Claude に `What Sentry projects do I have access to?` のようなサービスが必要な何かを尋ね、出力で `sentry` サーバー名でラベル付けされたツール呼び出しを探します。
  </Step>
</Steps>

OAuth の代わりに静的トークンで認証するサーバーは、`--header "Authorization: Bearer <token>"` で追加時にトークンを取得します。[GitHub の例](/docs/ja/mcp#example-connect-to-github-for-code-reviews)で実装されたバージョンを参照してください。

<h2 id="edit-mcp-json-directly">
  .mcp.json を直接編集する
</h2>

[スコープテーブル](#find-your-configuration-on-disk)のすべてのファイルは、サーバーエントリに同じ JSON 形式を使用します。このセクションは `.mcp.json`（プロジェクトスコープファイル）を編集します。これはリポジトリにチェックインされるため、手で書く価値があり、チームの設定コードとしても機能します。

プロジェクトルートに `.mcp.json` を作成します。以下の例は、このガイドの両方のサーバーを定義しています。HTTP 経由で到達するホストされたドキュメントサーバーと、ローカル `stdio` プロセスとしての Playwright サーバー。

```json theme={null}
{
  "mcpServers": {
    "claude-code-docs": {
      "type": "http",
      "url": "https://code.claude.com/docs/mcp"
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

フィールドはサーバータイプによって異なります。

* HTTP サーバーの場合、`url` は Claude Code が接続するエンドポイントです。
* stdio サーバーの場合、`command` と `args` は実行するプログラムです。

ファイルを保存した後、プロジェクトで新しい Claude Code セッションを開始します。Claude Code はスタートアップ時に `.mcp.json` を読み込みます。

Claude Code がプロジェクトスコープのサーバーを初めて見るとき、それを承認するよう求めます。プロンプトが存在するため、クローンしたリポジトリは同意なしにマシン上でプロセスを起動できません。プロンプトを承認するか、見逃した場合は後で承認するために `/mcp` を実行します。

承認したら、`/mcp` を実行し、サーバーが接続として表示されることを確認します。代わりにエラーが表示される場合は、[トラブルシューティング](#troubleshooting)を参照してください。

<h2 id="connect-from-other-surfaces">
  他のサーフェスから接続する
</h2>

このガイドは `claude mcp` CLI コマンドを使用しますが、すべての Claude Code サーフェスは MCP サーバーに接続できます。

* **Claude Code デスクトップアプリ**：[Connectors UI](/docs/ja/desktop#connect-external-tools)を通じてサーバーを追加します。
* **Claude Desktop チャットアプリ**：Claude Code とは別のアプリです。`claude_desktop_config.json` からサーバーを CLI にコピーするには、macOS または WSL で `claude mcp add-from-claude-desktop` を実行します。
* **VS Code**：[MCP で外部ツールに接続する](/docs/ja/vs-code#connect-to-external-tools-with-mcp)を参照してください。
* **Web 上の Claude Code**：リポジトリから `.mcp.json` を読み込みます。[.mcp.json を直接編集する](#edit-mcp-json-directly)を参照してください。
* **Claude.ai**：[claude.ai/customize/connectors](https://claude.ai/customize/connectors) で追加したコネクタは、そのアカウントでサインインするとき CLI に自動的に読み込まれます。[Claude.ai から MCP サーバーを使用する](/docs/ja/mcp#use-mcp-servers-from-claude-ai)を参照してください。

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

サーバーが接続しない場合は、セッション内の `/mcp` またはシェルから `claude mcp list` でそのステータスを確認し、以下の症状と照合してください。`/mcp` パネルでは、セッションを離れずに再接続または認証することもできます。

<AccordionGroup>
  <Accordion title="/mcp は'No MCP servers configured'を表示します">
    Claude Code は現在のディレクトリのサーバーを見つけませんでした。最も一般的な原因：

    * 別のプロジェクトから `claude mcp add` を実行しました。ローカルスコープのサーバーは追加したプロジェクトに関連付けられています。リポジトリルート、または git リポジトリにいなかった場合は正確なディレクトリ。現在いるプロジェクトからサーバーを再度追加するか、`--scope user` で追加してプロジェクトに関連付けられないようにします。
    * 設定ファイルを間違ったパスで編集しました。正しいファイルは `~/.claude.json` と `<project>/.mcp.json` です。Claude Code は `~/.claude/.mcp.json`、`~/.claude/config/mcp.json`、`~/.claude/mcp.json`、`%APPDATA%\Claude\mcp.json` などのパスを読み込みません。ユーザースコープのサーバーの場合は、`claude mcp add --scope user` を実行します。これは `~/.claude.json` の `mcpServers` キーに書き込みます。プロジェクトスコープのサーバーの場合は、プロジェクトルートの `.mcp.json` を編集します。
  </Accordion>

  <Accordion title="ステータスは「Failed to connect」または「Connection error」を表示します">
    両方のステータスはサーバーが開始しなかったか、URL が応答しなかったことを意味します。[サインインが必要なサーバーに接続する](#connect-a-server-that-requires-sign-in)で説明されているブラウザサインインではなく、トークンを期待する HTTP サーバーにも表示される可能性があります。

    v2.1.191 以降、HTTP サーバーが `404 Not Found` を返す場合、`/mcp` でサーバーを選択すると、Claude Code が試した URL を含む `MCP endpoint not found at <url>. Check the URL in your MCP config.` が表示されます。以前のバージョンでは、URL なしで汎用的な `Error POSTing to endpoint` メッセージが表示されます。URL をサーバーのドキュメント化された MCP エンドポイントパスと比較してから、`claude mcp remove <name>` を実行し、正しい URL で再度追加します。

    HTTP サーバーの場合、URL がマシンから到達可能であることを確認します。

    ```bash theme={null}
    curl -I https://mcp.sentry.dev/mcp
    ```

    PowerShell では、`curl` の代わりに `curl.exe` を使用して、リクエストが `Invoke-WebRequest` エイリアスではなく実際の curl バイナリに送信されるようにします。

    応答は、どの種類の問題があるかを示します。

    * `404` または `405`：サーバーは稼働しています。多くの MCP エンドポイントは POST リクエストのみに応答するため、これでも URL がマシンから到達可能であることが確認されます。
    * `401` または `403`：サーバーは稼働しており、認証が必要です。[サインインが必要なサーバーに接続する](#connect-a-server-that-requires-sign-in)でブラウザサインインを使用するか、GitHub のようなトークンを取得するサーバーの場合は、`claude mcp add` コマンドで `--header "Authorization: Bearer <token>"` で渡します。
    * 応答がない：URL とネットワークを確認します。

    stdio サーバーの場合、設定されたコマンドをターミナルで直接実行して、基になるエラーを確認します。このガイドの Playwright サーバーの場合、実行します。

    ```bash theme={null}
    npx -y @playwright/mcp@latest
    ```

    次に起こることは、問題がどこにあるかを示します。

    * コマンドが開始され、入力を待ちます。サーバー自体は機能しています。`claude mcp get <name>` を実行し、そこに表示されるコマンドが実行したばかりのコマンドと一致することを確認します。表示されるコマンドが入力したものと異なる場合、サーバーコマンドの前に `--` セパレーターを省略した可能性があります。サーバーを削除し、`--` を配置して再度追加します。`.mcp.json` を手で書いた場合は、その構文と場所を確認します。
    * コマンドエラー：メッセージは Node.js やブラウザなど、不足しているものに名前を付けます。
  </Accordion>

  <Accordion title="接続がスタートアップでタイムアウトしました">
    サーバーはデフォルトの 30 秒スタートアップタイムアウトより長くかかりました。stdio サーバーの最初の実行は、`npx` がパッケージをダウンロードしている間に遅くなる可能性があります。[`MCP_TIMEOUT`](/docs/ja/env-vars)環境変数でミリ秒単位で制限を増やします。

    ```bash theme={null}
    MCP_TIMEOUT=60000 claude
    ```

    PowerShell では、同じ行のコマンドの前に変数を設定します。

    ```powershell theme={null}
    $env:MCP_TIMEOUT = "60000"; claude
    ```
  </Accordion>

  <Accordion title="サーバーは既に存在します">
    同じスコープで同じ名前のサーバーを既に追加しています。既存のエントリを削除するか、別の名前を選択します。

    ```bash theme={null}
    claude mcp remove claude-code-docs
    ```

    名前が複数のスコープに存在する場合、`remove` は `exists in multiple scopes` を報告します。削除するコピーを選択するために `--scope` を渡します。例えば `claude mcp remove claude-code-docs --scope local`。
  </Accordion>

  <Accordion title="サーバーは接続しますが、ツールが表示されません">
    セッション内で `/mcp` を実行し、サーバーを選択してそのツールリストを確認します。リストが空の場合、サーバーは開始しましたが、ツールを登録しませんでした。これは通常、API キーなどの必要な環境変数が不足していることを意味します。

    `claude mcp add` で `--env KEY=value` を使用して変数を渡すか、サーバーの `.mcp.json` エントリの `env` フィールドで渡します。サーバーのドキュメントは必要な変数をリストします。
  </Accordion>

  <Accordion title=".mcp.json への変更が有効になりません">
    Claude Code はセッション開始時に `.mcp.json` を読み込みます。ファイルを編集した後、セッションを終了して再開します。

    サーバーがまだ表示されない場合は、`/mcp` を実行し、解析警告を探します。Claude Code は不正な形式のエントリをスキップし、そこに問題のあるフィールドを表示します。

    以前にプロンプトを拒否した場合は、プロジェクト承認をリセットします。

    ```bash theme={null}
    claude mcp reset-project-choices
    ```
  </Accordion>

  <Accordion title="OAuth サインインが失敗するか、ブラウザが開きません">
    `/mcp` を実行し、サーバーを選択して、再度 `Authenticate` を選択します。ブラウザが自動的に開かない場合は、ターミナルに表示される URL をコピーして手動で開きます。固定コールバックポートと事前設定された認証情報については、[リモート MCP サーバーで認証する](/docs/ja/mcp#authenticate-with-remote-mcp-servers)を参照してください。
  </Accordion>
</AccordionGroup>

<h2 id="next-steps">
  次のステップ
</h2>

1 つのサーバーが接続されたら、MCP が有効にする残りを探索します。

* [Anthropic Directory](/docs/ja/mcp#find-and-build-mcp-servers) で[より多くの MCP サーバーを見つける](/docs/ja/mcp#find-and-build-mcp-servers)
* インストールスコープを使用して[チームとサーバーを共有する](/docs/ja/mcp#mcp-installation-scopes)
* [組織の MCP アクセスを管理する](/docs/ja/managed-mcp)（管理設定とポリシーコントロール）
* [プロンプトで MCP リソースを参照する](/docs/ja/mcp#use-mcp-resources)（@ メンション付き）
* [`/` メニューから MCP プロンプトをコマンドとして実行する](/docs/ja/mcp#use-mcp-prompts-as-commands)
* [MCP SDK を使用して独自のサーバーを構築する](https://modelcontextprotocol.io/quickstart/server)
