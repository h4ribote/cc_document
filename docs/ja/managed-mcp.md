> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 組織の MCP サーバーアクセスを制御する

> 管理対象設定ファイル、許可リスト、ブロックリストを使用して、ユーザーが追加または接続できる MCP サーバーを制限します。

デフォルトでは、Claude Code を実行している誰もが、選択した任意の [MCP サーバー](/docs/ja/mcp) に接続できます。Anthropic は、[Anthropic Directory](https://claude.ai/directory) に追加する前に、[リスティング基準](https://claude.com/docs/connectors/building/review-criteria) に対してコネクターをレビューしていますが、MCP サーバーのセキュリティ監査や管理は行いません。管理者として、組織内で実行されるサーバーを制限できます。固定の承認済みセットをデプロイすることから、MCP 全体を無効にすることまで可能です。

このページでは、以下の方法について説明します。

* [パターンを選択する](#choose-a-pattern)。必要な制御レベルに合わせたパターンを選択します
* [`managed-mcp.json` で固定サーバーセットをデプロイする](#exclusive-control-with-managed-mcp-json)。[MCP 全体を無効にする](#disable-mcp-entirely)方法も含まれます
* [許可リストとブロックリストでサーバーを制御する](#policy-based-control-with-allowlists-and-denylists)
* [制限がサーバーをブロックするときにユーザーに何が起こるかを伝える](#how-restrictions-appear-to-users)
* [組織が実際に使用するサーバーを監視する](#monitor-mcp-usage)

<Note>
  [セキュリティ](/docs/ja/security)ページでは、MCP の脅威モデルと、サーバーを承認する前に評価する方法について説明しています。[実施する内容を決定する](/docs/ja/admin-setup#decide-what-to-enforce)では、MCP 制限と他の管理制御について説明しています。
</Note>

<h2 id="choose-a-pattern">
  パターンを選択する
</h2>

Claude Code は、さまざまな制限レベルをサポートしています。各パターンは、以下で説明する 1 つまたは両方のメカニズムを使用します。固定セットをデプロイするための `managed-mcp.json` と、ユーザーが設定できる内容をフィルタリングするための `allowedMcpServers`/`deniedMcpServers` です。

| パターン            | 機能                                              | 設定                                                                                              |
| :-------------- | :---------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| **MCP を無効にする**  | サーバーはどこにも読み込まれません                               | 空のサーバーマップを含む `managed-mcp.json`                                                                 |
| **固定デプロイ**      | すべてのユーザーが同じサーバーを取得し、他のサーバーを追加できません              | 必要なサーバーを含む `managed-mcp.json`                                                                   |
| **承認済みカタログ**    | 承認済みサーバーのリストを公開します。ユーザーは必要なものを追加し、他のものはブロックされます | `allowedMcpServers` + `allowManagedMcpServersOnly: true`                                        |
| **プラグインサーバーのみ** | サーバーはプラグインからのみ取得できます。ユーザーは独自のサーバーを追加できません       | [`strictPluginOnlyCustomization`](/docs/ja/settings#strictpluginonlycustomization) とリストに `mcp` を含めます |
| **ソフト許可リスト**    | ユーザーが独自の設定で拡張できる許可リストを実施します                     | `allowManagedMcpServersOnly` なしの `allowedMcpServers`                                            |
| **ブロックリストのみ**   | 既知の悪いサーバーをブロックし、他のすべてを許可します                     | `deniedMcpServers`                                                                              |
| **制限なし**        | ユーザーは何でも追加できます                                  | 管理対象 MCP 設定をデプロイしません                                                                            |

<Note>
  Claude Code には、ユーザーが参照してインストールできる組み込み MCP サーバーレジストリはありません。承認済みカタログパターンの場合、承認済みリストとその `claude mcp add` コマンドをユーザーが見つけられる場所（内部 wiki など）で共有するか、[管理対象プラグインマーケットプレイス](/docs/ja/plugin-marketplaces#managed-marketplace-restrictions)を通じてサーバーをプラグインとして配布して、ユーザーが `/plugin` から参照してインストールできるようにします。
</Note>

<h2 id="exclusive-control-with-managed-mcp-json">
  managed-mcp.json による排他的制御
</h2>

`managed-mcp.json` ファイルをデプロイすると、Claude Code はそのファイルで定義されたサーバーのみを読み込みます。ユーザーは、プラグイン提供のサーバーを含む他の MCP サーバーを追加、変更、または使用することはできません。また、このファイルは [管理対象セットと共に許可する](#allow-claude-ai-connectors-alongside-the-managed-set)場合を除き、claude.ai コネクターも抑制します。

2 つの他の設定は、管理対象セットをさらにフィルタリングできます。

* `allowedMcpServers` と `deniedMcpServers` は管理対象サーバーにも適用されるため、管理対象サーバーがそれらを通過しない場合は読み込まれません。
* ユーザー独自の `deniedMcpServers` は設定からマージされるため、ユーザーは管理対象サーバーを自分自身でブロックできます。

チェックの完全な順序については、[サーバーの評価方法](#how-a-server-is-evaluated)を参照してください。

`managed-mcp.json` はスタンドアロンファイルであるため、[サーバー管理設定](/docs/ja/server-managed-settings)を通じて配信することはできません。管理者権限を持つシステムパスに書き込むことができるプロセスは、それをデプロイできます。大規模では、通常は Jamf などのデバイス管理ツール、macOS 上の設定プロファイル、Windows 上のグループポリシーまたは Intune、または Linux 上の選択したフリート管理を通じて行われます。Claude Code は、以下のパスのいずれかでファイルを探します。

| プラットフォーム    | パス                                                         |
| :---------- | :--------------------------------------------------------- |
| macOS       | `/Library/Application Support/ClaudeCode/managed-mcp.json` |
| Linux と WSL | `/etc/claude-code/managed-mcp.json`                        |
| Windows     | `C:\Program Files\ClaudeCode\managed-mcp.json`             |

ファイルは、プロジェクト [`.mcp.json`](/docs/ja/mcp#project-scope) ファイルと同じ形式を使用します。

```json theme={null}
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "sentry": {
      "type": "http",
      "url": "https://mcp.sentry.dev/mcp"
    },
    "company-internal": {
      "type": "stdio",
      "command": "/usr/local/bin/company-mcp-server",
      "args": ["--config", "/etc/company/mcp-config.json"],
      "env": {
        "COMPANY_API_URL": "https://internal.example.com"
      }
    }
  }
}
```

<h3 id="authenticate-with-per-user-credentials">
  ユーザーごとの認証情報で認証する
</h3>

マシン上の任意のユーザーがこのファイルを読むことができるため、`env` ブロックに API キーまたは他の認証情報を保存しないでください。代わりに、以下のいずれかを使用してユーザーごとの認証情報を渡します。

* [`${VAR}` 展開](/docs/ja/mcp#environment-variable-expansion-in-mcp-json)。各ユーザーの環境からシークレットを読み取ります。
* [OAuth またはユーザーごとのヘッダー](/docs/ja/mcp#authenticate-with-remote-mcp-servers)。各ユーザーが自分として認証します。
* [`headersHelper`](/docs/ja/mcp#use-dynamic-headers-for-custom-authentication)。接続時に認証情報を生成します。

<h3 id="validate-the-configuration">
  設定を検証する
</h3>

ファイルが有効であることを確認するには、管理対象マシンで 2 つのチェックを実行します。

1. `claude mcp list` は `managed-mcp.json` 内のサーバーのみを表示します。ユーザー独自のサーバーがまだ表示される場合、ファイルが読み込まれていません。パスと権限を確認してください。
2. `claude mcp add --transport http test https://example.com/mcp` は `Cannot add MCP server: enterprise MCP configuration is active and has exclusive control over MCP servers` で失敗します。URL は実際のサーバーである必要はありません。ポリシーチェックが何かに接続される前にコマンドを拒否するためです。

<h3 id="disable-mcp-entirely">
  MCP 全体を無効にする
</h3>

空のサーバーマップを含む `managed-mcp.json` をデプロイして、すべての MCP サーバーをブロックします。

```json theme={null}
{
  "mcpServers": {}
}
```

ユーザーは `/mcp` に MCP サーバーを表示しません。`claude mcp add` は上記のエンタープライズポリシーエラーで失敗します。ユーザーが以前に設定したサーバーは、次回セッションを開始するときに読み込みを停止します。ポリシーが理由であることについて警告はありません。

<h3 id="allow-claude-ai-connectors-alongside-the-managed-set">
  管理対象セットと共に claude.ai コネクターを許可する
</h3>

`managed-mcp.json` をデプロイすると、デフォルトでは [claude.ai コネクター](/docs/ja/mcp#use-mcp-servers-from-claude-ai)が抑制されます。これには、管理者が claude.ai 管理コンソールで組織向けに設定したコネクターも含まれます。これらのコネクターを `managed-mcp.json` 内のサーバーと共に読み込むには、[管理設定ソース](/docs/ja/admin-setup#decide-how-settings-reach-devices)で `"allowAllClaudeAiMcps": true` を設定します。Claude Code v2.1.149 以降が必要です。

この設定が有効になると、Claude Code は `managed-mcp.json` がデプロイされていない場合に読み込むのと同じ claude.ai コネクターを読み込みます。[許可リストと拒否リスト](#policy-based-control-with-allowlists-and-denylists)は引き続きこれらのコネクターに適用されるため、`deniedMcpServers` で特定のコネクターをブロックできます。この設定は claude.ai コネクターのみに影響します。プラグイン提供のサーバーは抑制されたままです。

Claude Code は、この設定を管理者制御のポリシー層からのみ読み取ります。サーバー管理設定、MDM デプロイされた plist または HKLM レジストリキー、またはシステム `managed-settings.json` ファイルです。これをユーザーまたはプロジェクト設定に配置しても効果がないため、ユーザーは排他的制御が抑制したコネクターを再度有効にすることはできません。

<h2 id="policy-based-control-with-allowlists-and-denylists">
  許可リストとブロックリストによるポリシーベースの制御
</h2>

許可リストとブロックリストは、設定されたサーバーのどれが読み込まれることを許可するかをフィルタリングします。これらはレジストリではありません。サーバーは、ユーザー、プラグイン、または `managed-mcp.json` によって追加される前に、許可リストまたはブロックリストが適用されます。ユーザーにサーバーをデプロイするには、[`managed-mcp.json`](#exclusive-control-with-managed-mcp-json) を使用します。両方のリストは、[`--mcp-config` CLI フラグ](/docs/ja/cli-reference#cli-flags)で渡されるサーバーもフィルタリングします。`--strict-mcp-config` は、どの設定ファイルが読み込まれるかを制限し、どちらのリストもバイパスしません。

許可リストを権限あるものにするには、[管理設定ソース](/docs/ja/admin-setup#decide-how-settings-reach-devices)（サーバー管理設定またはデプロイされた `managed-settings.json` ファイルなど）で `allowedMcpServers` と `allowManagedMcpServersOnly: true` を一緒に設定します。[許可リストを管理設定のみに制限する](#restrict-the-allowlist-to-managed-settings-only)は設定を示しています。`allowManagedMcpServersOnly` がない場合、すべての設定ソース（ユーザー独自の `~/.claude/settings.json` を含む）からの許可リストがマージされるため、ユーザーは許可リストが許可する内容を拡張できます。ブロックリストは関係なくすべてのソースからマージされます。

<Note>
  `allowManagedMcpServersOnly` は `allowManagedPermissionRulesOnly` とは別です。後者は [権限ルール](/docs/ja/permissions#managed-settings)のみをロックダウンします。そのフラグを設定しても、MCP 許可リストは実施されません。
</Note>

<h3 id="match-servers-by-url-command-or-name">
  URL、コマンド、または名前でサーバーを一致させる
</h3>

`allowedMcpServers` と `deniedMcpServers` はエントリのリストです。各エントリは、URL、コマンド、または名前でサーバーを識別する単一のキーを持つオブジェクトです。

| キー              | 一致                                   | 用途                         |
| :-------------- | :----------------------------------- | :------------------------- |
| `serverUrl`     | リモートサーバー URL。正確またはワイルドカード `*` を使用    | HTTP および SSE サーバー          |
| `serverCommand` | stdio サーバーを開始する正確なコマンドと引数            | Stdio サーバー                 |
| `serverName`    | ユーザーが割り当てたラベル。完全一致のみ。ワイルドカードは展開されません | どちらのタイプでも、ただし下の警告を参照してください |

`allowedMcpServers` を設定しないことは、空の配列に設定することとは異なります。

| 設定                  | 設定なし（デフォルト）     | 空の配列 `[]`      | 入力済み              |
| :------------------ | :-------------- | :------------- | :---------------- |
| `allowedMcpServers` | すべてのサーバーが許可されます | サーバーは許可されません   | 一致するサーバーのみが許可されます |
| `deniedMcpServers`  | サーバーはブロックされません  | サーバーはブロックされません | 一致するサーバーがブロックされます |

[管理設定での無効なエントリ](/docs/ja/settings#invalid-entries-in-managed-settings)を参照して、エントリがスキーマ検証に失敗した場合に何が起こるかを確認してください。

<Warning>
  `serverName` エントリは、どちらのリストでも、セキュリティ制御ではありません。名前は、`claude mcp add` を実行するか設定ファイルを編集するときにユーザーが割り当てるラベルであり、基になるサーバーではないため、ユーザーは任意のサーバーを `github` と呼ぶことができます。claude.ai コネクタの場合、名前は claude.ai によって返される表示名であり、変更される可能性があります。実際に実行されるサーバーを実施するには、`serverCommand` または `serverUrl` エントリを追加します。
</Warning>

`serverName` の検証は 2 つのリスト間で異なります。

* `deniedMcpServers` では、`serverName` は任意の空でない文字列を受け入れるため、[claude.ai コネクタ](/docs/ja/mcp#use-mcp-servers-from-claude-ai)をその表示名でブロックできます。たとえば、`{ "serverName": "claude.ai Slack" }` は Slack コネクタをブロックします。ブロックが名前変更に対して堅牢である必要がある場合、またはコネクタ名が衝突して ` (N)` サフィックスを取得する場合は、`serverUrl` エントリを優先します。
* `allowedMcpServers` では、`serverName` は文字、数字、ハイフン、アンダースコアに限定されます。claude.ai コネクタをホワイトリストに登録するには `serverUrl` を使用します。

すべての claude.ai コネクタをオフにするには、[`disableClaudeAiConnectors`](/docs/ja/mcp#disable-claude-ai-connectors) を参照してください。

<h3 id="how-a-server-is-evaluated">
  サーバーの評価方法
</h3>

`managed-mcp.json` からのサーバーを含む、サーバーを読み込む前に、Claude Code は順序に 3 つのチェックを実行します。

1. **リストをマージします。** すべての設定ソースからの許可リストとブロックリストエントリが 1 つの許可リストと 1 つのブロックリストに結合されます。`allowManagedMcpServersOnly` が `true` の場合、管理対象許可リストのみが保持されます。ブロックリストは常にすべてのソースからマージされます。
2. **ブロックリストをチェックします。** URL、コマンド、または名前でブロックリストエントリと一致するサーバーはブロックされます。ブロックリスト一致をオーバーライドするものはありません。
3. **許可リストをチェックします。** `allowedMcpServers` がどこにも設定されていない場合、ブロックリストを通過したすべてのサーバーが読み込まれます。設定されている場合、サーバーが一致する必要があるものは、その種類に依存し、以下の表に示されています。

| サーバータイプ            | 一致するときに許可されます                                                                          |
| :----------------- | :------------------------------------------------------------------------------------- |
| リモート（HTTP または SSE） | `serverUrl` エントリ。`serverName` 一致は、許可リストに `serverUrl` エントリが含まれていない場合にのみカウントされます         |
| Stdio              | `serverCommand` エントリ。`serverName` 一致は、許可リストに `serverCommand` エントリが含まれていない場合にのみカウントされます |

これらのチェック内で 3 つの一致ルールが適用されます。

* **コマンドは正確に一致します。** すべての引数、順序通り。`["npx", "-y", "server"]` は `["npx", "server"]` または `["npx", "-y", "server", "--flag"]` と一致しません。
* **`serverCommand` と `serverUrl` の値は一致する前に展開されます。** ポリシーエントリとサーバーの設定値の両方が、`.mcp.json` と同じ [`${VAR}` と `${VAR:-default}` 展開](/docs/ja/mcp#environment-variable-expansion-in-mcp-json)を通過するため、`["${HOME}/bin/server"]` として記述されたエントリは、同じ参照または展開されたパスのいずれかを使用するサーバー設定と一致します。Windows では、`${HOME}` の代わりに `${USERPROFILE}` など、そこで設定されている環境変数を参照してください。`serverName` の値は文字通りに一致し、展開されることはありません。
* **URL は `*` ワイルドカード** をパターン内の任意の場所（スキームを含む）でサポートします。ホスト名の一致は大文字と小文字を区別しません。末尾の FQDN ドットを無視します。したがって、`https://Mcp.Example.com/*` は `https://mcp.example.com/api` と一致します。パスは大文字と小文字を区別したままです。

| パターン                        | 許可                                    |
| :-------------------------- | :------------------------------------ |
| `https://mcp.example.com/*` | 特定のドメイン上のすべてのパス                       |
| `https://mcp.example.com`   | そのドメイン上のすべてのパスも。パスのないパターンは任意のパスと一致します |
| `https://*.example.com/*`   | `example.com` の任意のサブドメイン              |
| `http://localhost:*/*`      | localhost 上の任意のポート                    |
| `*://mcp.example.com/*`     | 特定のドメインへの任意のスキーム                      |

`${VAR}` 展開は Claude Code 独自のプロセス環境を読み取るため、変数を参照する `serverCommand` または `serverUrl` ポリシーエントリは、ユーザーが設定する値に展開されます。実施に依存するエントリには、リテラル URL とコマンドを使用してください。

<h3 id="example-configuration">
  設定例
</h3>

以下の設定は、ブロックリストを含むハード許可リストを設定します。強調表示された行は、リストの残りの部分がどのように評価されるかを変更し、ブロック後のコールアウトは各行を説明しています。

```json {3,5,11} theme={null}
{
  "allowedMcpServers": [
    { "serverUrl": "https://api.githubcopilot.com/*" },
    { "serverUrl": "https://mcp.sentry.dev/*" },
    { "serverCommand": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."] },
    { "serverCommand": ["python", "/usr/local/bin/approved-server.py"] },
    { "serverUrl": "https://mcp.example.com/*" },
    { "serverUrl": "https://*.internal.example.com/*" }
  ],
  "deniedMcpServers": [
    { "serverName": "dangerous-server" },
    { "serverCommand": ["npx", "-y", "unapproved-package"] },
    { "serverUrl": "https://*.untrusted.example.com/*" }
  ]
}
```

* **3 行目**：最初の `serverUrl` エントリ。1 つが存在すると、すべてのリモートサーバーが URL パターンと一致する必要があるため、ユーザーは許可された名前を付けることで許可されていないリモートサーバーを取得することはできません。
* **5 行目**：最初の `serverCommand` エントリ。stdio サーバーでも同じ効果があるため、すべてのローカルサーバーが正確にリストされたコマンドと一致する必要があります。
* **11 行目**：ブロックリスト内の `serverName` エントリ。ブロックリストエントリは常に適用されるため、`dangerous-server` という名前のサーバーは URL またはコマンドに関係なくブロックされます。

この許可リスト内の `serverName` エントリは、両方のトランスポートタイプが既に厳密なエントリを持っているため、何とも一致しません。

以下のアコーディオンは、他の許可リストとブロックリストの組み合わせに対してサーバーがどのように評価されるかについて説明しています。

<Accordion title="URL のみの許可リスト">
  ```json theme={null}
  {
    "allowedMcpServers": [
      { "serverUrl": "https://mcp.example.com/*" },
      { "serverUrl": "https://*.internal.example.com/*" }
    ]
  }
  ```

  | サーバー                                               | 結果                           |
  | :------------------------------------------------- | :--------------------------- |
  | `https://mcp.example.com/api` の HTTP サーバー          | 許可：URL パターンと一致               |
  | `https://api.internal.example.com/mcp` の HTTP サーバー | 許可：ワイルドカードサブドメインと一致          |
  | `https://external.example.com/mcp` の HTTP サーバー     | ブロック：URL パターンと一致しません         |
  | 任意のコマンドを持つ Stdio サーバー                              | ブロック：一致する名前またはコマンドエントリがありません |
</Accordion>

<Accordion title="コマンドのみの許可リスト">
  ```json theme={null}
  {
    "allowedMcpServers": [
      { "serverCommand": ["npx", "-y", "approved-package"] }
    ]
  }
  ```

  | サーバー                                               | 結果                    |
  | :------------------------------------------------- | :-------------------- |
  | `["npx", "-y", "approved-package"]` を持つ Stdio サーバー | 許可：コマンドと一致            |
  | `["node", "server.js"]` を持つ Stdio サーバー             | ブロック：コマンドと一致しません      |
  | `my-api` という名前の HTTP サーバー                          | ブロック：一致する名前エントリがありません |
</Accordion>

<Accordion title="混合名とコマンド許可リスト">
  ```json theme={null}
  {
    "allowedMcpServers": [
      { "serverName": "github" },
      { "serverCommand": ["npx", "-y", "approved-package"] }
    ]
  }
  ```

  | サーバー                                                                   | 結果                                               |
  | :--------------------------------------------------------------------- | :----------------------------------------------- |
  | `local-tool` という名前で `["npx", "-y", "approved-package"]` を持つ Stdio サーバー | 許可：コマンドと一致                                       |
  | `local-tool` という名前で `["node", "server.js"]` を持つ Stdio サーバー             | ブロック：コマンドエントリが存在しますが一致しません                       |
  | `github` という名前で `["node", "server.js"]` を持つ Stdio サーバー                 | ブロック：stdio サーバーはコマンドエントリが存在する場合、コマンドと一致する必要があります |
  | `github` という名前の HTTP サーバー                                              | 許可：名前と一致                                         |
  | `other-api` という名前の HTTP サーバー                                           | ブロック：名前が一致しません                                   |
</Accordion>

<Accordion title="名前のみの許可リスト">
  ```json theme={null}
  {
    "allowedMcpServers": [
      { "serverName": "github" },
      { "serverName": "internal-tool" }
    ]
  }
  ```

  | サーバー                                         | 結果             |
  | :------------------------------------------- | :------------- |
  | 任意のコマンドを持つ `github` という名前の Stdio サーバー        | 許可：コマンド制限なし    |
  | 任意のコマンドを持つ `internal-tool` という名前の Stdio サーバー | 許可：コマンド制限なし    |
  | `github` という名前の HTTP サーバー                    | 許可：名前と一致       |
  | `other` という名前の任意のサーバー                        | ブロック：名前が一致しません |
</Accordion>

<Accordion title="ブロックリストオーバーライド付き許可リスト">
  ```json theme={null}
  {
    "allowedMcpServers": [
      { "serverUrl": "https://*.example.com/*" }
    ],
    "deniedMcpServers": [
      { "serverUrl": "https://staging.example.com/*" }
    ]
  }
  ```

  | サーバー                                          | 結果                               |
  | :-------------------------------------------- | :------------------------------- |
  | `https://mcp.example.com/api` の HTTP サーバー     | 許可：許可リスト URL パターンと一致、ブロックリスト一致なし |
  | `https://staging.example.com/api` の HTTP サーバー | ブロック：両方と一致しますが、ブロックリストが優先されます    |
  | `https://other.com/mcp` の HTTP サーバー           | ブロック：許可リストと一致しません                |
</Accordion>

<h3 id="restrict-the-allowlist-to-managed-settings-only">
  許可リストを管理設定のみに制限する
</h3>

管理対象許可リストが適用される唯一のものにするには、管理設定ファイルで `allowManagedMcpServersOnly` を設定します。

```json theme={null}
{
  "allowManagedMcpServersOnly": true,
  "allowedMcpServers": [
    { "serverUrl": "https://api.githubcopilot.com/*" },
    { "serverUrl": "https://*.internal.example.com/*" }
  ]
}
```

`allowManagedMcpServersOnly` が `true` の場合、ユーザー、プロジェクト、ローカル設定からの許可リストは無視されます。ブロックリストはすべてのソースからマージされるため、ユーザーは常に自分自身のサーバーをブロックできます。

<h2 id="how-restrictions-appear-to-users">
  制限がユーザーにどのように表示されるか
</h2>

制限がサーバーをブロックすると、ユーザーは `claude mcp add` からエラーを表示するか、サーバーが静かに読み込みを停止します。このテーブルを使用して、これらのレポートを認識し、変更をロールアウトする前にユーザーに何が起こるかを伝えます。

| 制限                                                   | ユーザーが表示するもの                                                                                                |
| :--------------------------------------------------- | :--------------------------------------------------------------------------------------------------------- |
| `managed-mcp.json` が存在し、ユーザーが `claude mcp add` を実行する | `Cannot add MCP server: enterprise MCP configuration is active and has exclusive control over MCP servers` |
| サーバーがブロックリスト上にあり、ユーザーが `claude mcp add` を実行する        | `Cannot add MCP server "<name>": server is explicitly blocked by enterprise policy`                        |
| サーバーが許可リスト上にはなく、ユーザーが `claude mcp add` を実行する         | `Cannot add MCP server "<name>": not allowed by enterprise policy`                                         |
| 以前に設定されたサーバーがポリシーによってブロックされるようになった                   | サーバーは `/mcp` と `claude mcp list` から警告なく静かに消えます                                                             |

最後のケースでは、ユーザーはポリシーがサーバーが消えた理由であることについてシグナルを取得しません。新しい制限をロールアウトするときに、影響を受けるユーザーにどのサーバーがブロックされているかを伝えます。

<h2 id="monitor-mcp-usage">
  MCP 使用状況を監視する
</h2>

[OpenTelemetry エクスポート](/docs/ja/monitoring-usage)が設定されている場合、Claude Code はユーザーが呼び出す MCP サーバーとツールを記録できます。`OTEL_LOG_TOOL_DETAILS=1` を設定して、ツールイベントに MCP サーバーとツール名を含めます。その後、コレクターで集計して、ユーザーが実際に接続するサーバーを確認します。エクスポーターを設定し、完全なイベントスキーマについては、[監視](/docs/ja/monitoring-usage)を参照してください。

<h2 id="configuration-summary">
  設定の概要
</h2>

このページで説明するすべてのファイルと設定、それが制御するもの、および配信方法：

| サーフェス                        | 制御するもの                                                     | 場所                                                                                                        | 配信方法                                                                                                                    |
| :--------------------------- | :--------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| `managed-mcp.json`           | 固定サーバーセット、排他的制御                                            | システムパス：`/Library/Application Support/ClaudeCode/`、`/etc/claude-code/`、または `C:\Program Files\ClaudeCode\`  | MDM、GPO、フリート管理、または管理者権限を持つプロセス。サーバー管理設定を通じて設定することはできません                                                                 |
| `allowedMcpServers`          | 許可されたサーバーの許可リスト                                            | 任意の [設定ファイル](/docs/ja/settings#settings-files)。`allowManagedMcpServersOnly` が設定されていない限り、すべてのソースからのエントリがマージされます | 実施のため、[管理設定ソース](/docs/ja/admin-setup#decide-how-settings-reach-devices)：サーバー管理設定、`managed-settings.json`、MDM プロファイル、またはレジストリ |
| `deniedMcpServers`           | ブロックされたサーバーのブロックリスト                                        | 任意の設定ファイル。すべてのソースからのエントリがマージされます                                                                          | `allowedMcpServers` と同じ                                                                                                 |
| `allowManagedMcpServersOnly` | 許可リストを管理ソースのみにロックします                                       | 管理設定ソースのみ。設定は他の場所では効果がありません                                                                               | `allowedMcpServers` と同じ                                                                                                 |
| `allowAllClaudeAiMcps`       | `managed-mcp.json` と一緒に claude.ai コネクタを読み込みます。これらを抑制する代わりに | 管理設定ソースのみ。設定は他の場所では効果がありません                                                                               | `allowedMcpServers` と同じ                                                                                                 |

<h2 id="related-resources">
  関連リソース
</h2>

* [実施する内容を決定する](/docs/ja/admin-setup#decide-what-to-enforce)：MCP 制限と権限ルール、サンドボックス化、および他の管理制御
* [MCP 経由で Claude Code をツールに接続する](/docs/ja/mcp)：トランスポート、スコープ、認証を含む完全な MCP リファレンス
* [設定](/docs/ja/settings)：設定階層と管理設定がどのように優先されるか
* [サーバー管理設定](/docs/ja/server-managed-settings)：Claude.ai 管理コンソールから `allowedMcpServers` と `deniedMcpServers` を配信します
* [セキュリティ](/docs/ja/security)：これらの制御が防御する脅威モデル
* [Claude Enterprise Administrator Guide](https://claude.com/resources/tutorials/claude-enterprise-administrator-guide)：SSO、SCIM、シート管理、およびロールアウトプレイブック
