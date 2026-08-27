> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# インストールとログインのトラブルシューティング

> Claude Code のインストールまたはサインイン時に、コマンドが見つからない、PATH、権限、ネットワーク、認証エラーを修正します。

インストールが失敗した場合、またはサインインできない場合は、以下からエラーを見つけてください。Claude Code が動作している場合のランタイム問題については、[トラブルシューティング](/docs/ja/troubleshooting)を参照してください。設定が適用されない、またはフックが発火しないなどの設定の問題については、[設定をデバッグする](/docs/ja/debug-your-config)を参照してください。

<h2 id="find-your-error">
  エラーを見つける
</h2>

表示されているエラーメッセージまたは症状を修正方法と照合してください：

| 表示内容                                                                                           | 解決方法                                                                                                                                  |
| :--------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| `command not found: claude` または `'claude' is not recognized`                                   | [PATH を修正する](#command-not-found-claude-after-installation)                                                                            |
| `syntax error near unexpected token '<'`                                                       | [インストールスクリプトが HTML を返す](#install-script-returns-html-instead-of-a-shell-script)                                                       |
| `curl: (22) The requested URL returned error: 403`                                             | [インストールスクリプトが 403 を返す](#install-script-returns-html-instead-of-a-shell-script)                                                        |
| `curl: (23)` または `curl: (56) Failure writing output to destination`                            | [接続性を確認するか、別のインストーラーを使用する](#curl-56-failure-writing-output-to-destination)                                                            |
| Linux でのインストール中に `Killed` または `Installation was killed before it could finish (exit code 137)` | [メモリを解放するか、スワップスペースを追加する](#install-killed-on-low-memory-linux-servers)                                                                |
| `TLS connect error` または `SSL/TLS secure channel`                                               | [CA 証明書を更新する](#tls-or-ssl-connection-errors)                                                                                          |
| `Failed to fetch version` またはダウンロードサーバーに到達できない                                                 | [ネットワークとプロキシ設定を確認する](#check-network-connectivity)                                                                                     |
| `irm is not recognized` または `&& is not valid`                                                  | [シェルに適切なコマンドを使用する](#wrong-install-command-on-windows)                                                                                 |
| `Cask 'claude-code' is unavailable: No Cask with this name exists`                             | [Homebrew を更新する](#homebrew-cask-unavailable-or-outdated)                                                                              |
| `'bash' is not recognized as the name of a cmdlet`                                             | [Windows インストーラーコマンドを使用する](#wrong-install-command-on-windows)                                                                         |
| `A parameter cannot be found that matches parameter name 'fsSL'`                               | [Windows インストーラーコマンドを使用する](#wrong-install-command-on-windows)                                                                         |
| `Claude Code on Windows requires either Git for Windows (for bash) or PowerShell`              | [シェルをインストールする](#claude-code-on-windows-requires-either-git-for-windows-for-bash-or-powershell)                                        |
| `Claude Code does not support 32-bit Windows`                                                  | [Windows PowerShell を開く（x86 エントリではなく）](#claude-code-does-not-support-32-bit-windows)                                                  |
| `The process cannot access the file ... because it is being used by another process`           | [ダウンロードフォルダをクリアして再試行する](#the-process-cannot-access-the-file-during-windows-install)                                                   |
| `Error loading shared library`                                                                 | [システムに対応したバイナリバリアント](#linux-musl-or-glibc-binary-mismatch)                                                                            |
| `Illegal instruction`                                                                          | [アーキテクチャまたは CPU 命令セットの不一致](#illegal-instruction)                                                                                      |
| WSL での `cannot execute binary file: Exec format error`                                         | [WSL1 ネイティブバイナリ回帰](#exec-format-error-on-wsl1)                                                                                        |
| PowerShell インストーラーが完了しても `claude` が見つからないか古いバージョンが表示される                                        | [インストールディレクトリを PATH に追加する](#verify-your-path)、その後新しいターミナルを開く                                                                          |
| macOS での `dyld: cannot load`、`dyld: Symbol not found`、または `Abort trap`                         | [バイナリ互換性](#dyld-cannot-load-on-macos)                                                                                                 |
| `Invoke-Expression: Missing argument in parameter list`                                        | [インストールスクリプトが HTML を返す](#install-script-returns-html-instead-of-a-shell-script)                                                       |
| `App unavailable in region`                                                                    | Claude Code はお客様の国では利用できません。[サポートされている国](https://www.anthropic.com/supported-countries)を参照してください。                                     |
| `unable to get local issuer certificate`                                                       | [企業 CA 証明書を設定する](#tls-or-ssl-connection-errors)                                                                                       |
| `OAuth error` または `403 Forbidden`                                                              | [認証を修正する](#login-and-authentication)                                                                                                  |
| `Could not load the default credentials` または `Could not load credentials from any providers`   | [Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry 認証情報](#bedrock-agent-platform-or-foundry-credentials-not-loading) |
| `ChainedTokenCredential authentication failed` または `CredentialUnavailableError`                | [Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry 認証情報](#bedrock-agent-platform-or-foundry-credentials-not-loading) |
| `API Error: 500`、`529 Overloaded`、`429`、またはその他の 4xx および 5xx エラー（上記以外）                          | [エラーリファレンス](/docs/ja/errors)を参照してください                                                                                                      |

問題がリストに記載されていない場合は、以下の診断チェックを実行して、原因を特定してください。

<Tip>
  ターミナルをスキップしたい場合は、[Claude Code Desktop アプリ](/docs/ja/desktop-quickstart)を使用して、グラフィカルインターフェイスを通じて Claude Code をインストールして使用できます。[macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect?utm_source=claude_code\&utm_medium=docs)、[Windows](https://claude.com/download?utm_source=claude_code\&utm_medium=docs)、または [Linux](/docs/ja/desktop-linux)用にダウンロードして、コマンドラインセットアップなしでコーディングを開始してください。Linux では、[Linux インストール手順](/docs/ja/desktop-linux)に従って apt でアプリをインストールしてください。
</Tip>

<h2 id="run-diagnostic-checks">
  診断チェックを実行する
</h2>

<h3 id="check-network-connectivity">
  ネットワーク接続を確認する
</h3>

インストーラーは `downloads.claude.ai` からダウンロードします。到達可能であることを確認してください：

```bash theme={null}
curl -sI https://downloads.claude.ai/claude-code-releases/latest
```

PowerShell では、代わりに `curl.exe -sI` を実行してください。PowerShell は `curl` を `Invoke-WebRequest` にエイリアスしており、`-sI` フラグを拒否します。

`HTTP/2 200` という行はサーバーに到達したことを意味します。出力がない、`Could not resolve host`、または接続タイムアウトが表示される場合、ネットワークが接続をブロックしています。一般的な原因：

* `downloads.claude.ai` をブロックしている企業ファイアウォールまたはプロキシ
* 地域的なネットワーク制限：VPN または別のネットワークを試してください
* TLS/SSL の問題：システムの CA 証明書を更新するか、`HTTPS_PROXY` が設定されているかどうかを確認してください

企業プロキシの背後にいる場合は、インストール前に `HTTPS_PROXY` と `HTTP_PROXY` をプロキシのアドレスに設定してください。プロキシ URL がわからない場合は IT チームに問い合わせるか、ブラウザのプロキシ設定を確認してください。

この例は両方のプロキシ変数を設定してから、プロキシを通じてインストーラーを実行します：

<Tabs>
  <Tab title="macOS/Linux">
    ```bash theme={null}
    export HTTP_PROXY=http://proxy.example.com:8080
    export HTTPS_PROXY=http://proxy.example.com:8080
    curl -fsSL https://claude.ai/install.sh | bash
    ```
  </Tab>

  <Tab title="Windows PowerShell">
    ```powershell theme={null}
    $env:HTTP_PROXY = 'http://proxy.example.com:8080'
    $env:HTTPS_PROXY = 'http://proxy.example.com:8080'
    irm https://claude.ai/install.ps1 | iex
    ```
  </Tab>
</Tabs>

<h3 id="verify-your-path">
  PATH を確認する
</h3>

インストールが成功しても、`claude` を実行するときに `command not found` または `not recognized` エラーが表示される場合、インストールディレクトリが PATH に含まれていません。シェルは PATH にリストされているディレクトリ内のプログラムを検索し、インストーラーは macOS/Linux では `~/.local/bin/claude` に、Windows では `%USERPROFILE%\.local\bin\claude.exe` に `claude` を配置します。

<Note>
  [VS Code 拡張機能](/docs/ja/vs-code)は `claude` をこの場所に配置しません。拡張機能ディレクトリ内に CLI のプライベートコピーをバンドルし、独自のチャットパネル用に使用し、PATH に追加しません。拡張機能のみをインストールした場合、`~/.local/bin/claude` は存在しません。ターミナルから `claude` を使用するには[スタンドアロンインストール](/docs/ja/setup)を実行してから、以下を続行してください。
</Note>

インストールディレクトリが PATH に含まれているかどうかを確認するには、PATH エントリをリストして `local/bin` でフィルタリングしてください：

<Tabs>
  <Tab title="macOS/Linux">
    ```bash theme={null}
    echo $PATH | tr ':' '\n' | grep -Fx "$HOME/.local/bin"
    ```

    これが `/Users/you/.local/bin` または `/home/you/.local/bin` を出力する場合、ディレクトリは PATH に含まれており、[競合するインストールを確認する](#check-for-conflicting-installations)にスキップできます。出力がない場合は、シェル設定に追加してください。

    macOS のデフォルトである Zsh の場合：

    ```bash theme={null}
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

    ほとんどの Linux ディストリビューションのデフォルトである Bash の場合：

    ```bash theme={null}
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    ```

    または、ターミナルを閉じて再度開いてください。

    fish や Nushell などの他のシェルの場合は、シェル独自の設定構文を使用して `~/.local/bin` を PATH に追加してから、ターミナルを再起動してください。

    修正が機能したことを確認してください：

    ```bash theme={null}
    claude --version
    ```
  </Tab>

  <Tab title="Windows PowerShell">
    ```powershell theme={null}
    $env:PATH -split ';' | Select-String '\.local\\bin'
    ```

    出力がない場合は、インストールディレクトリをユーザー PATH に追加してください：

    ```powershell theme={null}
    $currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
    [Environment]::SetEnvironmentVariable('PATH', "$currentPath;$env:USERPROFILE\.local\bin", 'User')
    ```

    変更を有効にするためにターミナルを再起動してください。

    修正が機能したことを確認してください：

    ```powershell theme={null}
    claude --version
    ```
  </Tab>

  <Tab title="Windows CMD">
    ```batch theme={null}
    echo %PATH% | findstr /i "local\bin"
    ```

    出力がない場合は、システム設定を開き、環境変数に移動して、`%USERPROFILE%\.local\bin` をユーザー PATH 変数に追加してください。ターミナルを再起動してください。

    修正が機能したことを確認してください：

    ```batch theme={null}
    claude --version
    ```
  </Tab>
</Tabs>

<h3 id="check-for-conflicting-installations">
  競合するインストールを確認する
</h3>

複数の Claude Code インストールはバージョンの不一致または予期しない動作を引き起こす可能性があります。インストールされているものを確認してください：

<Tabs>
  <Tab title="macOS/Linux">
    PATH に見つかったすべての `claude` バイナリをリストします：

    ```bash theme={null}
    which -a claude
    ```

    これが何も出力しない場合、`claude` はまだ PATH にありません。[PATH を確認する](#verify-your-path)に戻ってください。

    `claude` バイナリが来ることができる 3 つの場所を確認してください。`~/.local/bin/claude` はネイティブインストーラー、`~/.claude/local/` は Claude Code の古いバージョンによって作成されたレガシーローカル npm インストール、npm グローバルリストは `-g` インストールを示します：

    ```bash theme={null}
    ls -la ~/.local/bin/claude
    ```

    ネイティブインストールは `~/.local/share/claude/versions/` へのシンボリックリンクを表示します。このパスで自分で作成したスクリプトまたはシンボリックリンクはカスタムランチャーであり、[自動更新はそのまま残します](/docs/ja/setup#auto-updates)。

    `ls` コマンドが `No such file or directory` を出力する場合、それはエラーではありません。その場所に何もインストールされていないことを意味するため、次のチェックに進んでください。

    ```bash theme={null}
    ls -la ~/.claude/local/
    ```

    ```bash theme={null}
    npm -g ls @anthropic-ai/claude-code 2>/dev/null
    ```
  </Tab>

  <Tab title="Windows PowerShell">
    PATH に見つかったすべての `claude` バイナリをリストします：

    ```powershell theme={null}
    where.exe claude
    ```

    ネイティブインストーラーがバイナリを配置したかどうかを確認してください：

    ```powershell theme={null}
    Test-Path "$env:USERPROFILE\.local\bin\claude.exe"
    ```
  </Tab>
</Tabs>

複数のインストールが見つかった場合は、1 つだけを保持してください。macOS/Linux の `~/.local/bin/claude` または Windows の `%USERPROFILE%\.local\bin\claude.exe` でのネイティブインストールが推奨されます。余分なものを削除してください：

npm グローバルインストールをアンインストールします：

```bash theme={null}
npm uninstall -g @anthropic-ai/claude-code
```

レガシーローカル npm インストールを削除します：

```bash theme={null}
rm -rf ~/.claude/local
```

Windows では PowerShell を使用してください：

```powershell theme={null}
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\local"
```

macOS で Homebrew インストールを削除します。`claude-code@latest` cask をインストールした場合は、その名前に置き換えてください：

```bash theme={null}
brew uninstall --cask claude-code
```

Windows で WinGet インストールを削除します：

```powershell theme={null}
winget uninstall Anthropic.ClaudeCode
```

<h3 id="check-directory-permissions">
  ディレクトリ権限を確認する
</h3>

インストーラーは macOS と Linux の `~/.local/bin/` と `~/.claude/` への書き込みアクセスが必要です。Windows ではインストール場所は `%USERPROFILE%` の下にあり、デフォルトではユーザーが書き込み可能なため、このセクションはそこではほとんど適用されません。

ディレクトリが書き込み可能かどうかを確認してください：

```bash theme={null}
test -w ~/.local/bin && echo "writable" || echo "not writable"
test -w ~/.claude && echo "writable" || echo "not writable"
```

いずれかのディレクトリが書き込み可能でない場合は、インストールディレクトリを作成し、ユーザーを所有者として設定してください：

```bash theme={null}
sudo mkdir -p ~/.local/bin
sudo chown -R $(whoami) ~/.local
```

<h3 id="verify-the-binary-works">
  バイナリが機能することを確認する
</h3>

`claude --version` がバージョンを出力しても `claude` がクラッシュまたはハングする場合は、これらのチェックを実行して原因を特定してください。`claude --version` がコマンドが見つからないと言う場合は、最初に [PATH を確認する](#verify-your-path)に移動してください。以下のコマンドは `claude` が PATH にあることを前提としています。

バイナリが存在し、実行可能であることを確認してください：

```bash theme={null}
ls -la "$(command -v claude)"
```

Windows では PowerShell を使用してください：

```powershell theme={null}
Get-Command claude | Select-Object Source
```

Linux では、不足している共有ライブラリを確認してください。`ldd` が不足しているライブラリを表示する場合は、システムパッケージをインストールする必要があるかもしれません。Alpine Linux およびその他の musl ベースのディストリビューションについては、[Alpine Linux セットアップ](/docs/ja/setup#alpine-linux-and-musl-based-distributions)を参照してください。

```bash theme={null}
ldd "$(command -v claude)" | grep "not found"
```

バイナリが実行できることを確認してください：

```bash theme={null}
claude --version
```

<h2 id="common-installation-issues">
  一般的なインストール問題
</h2>

これらは最も頻繁に遭遇するインストール問題とその解決策です。

<h3 id="install-script-returns-html-instead-of-a-shell-script">
  インストールスクリプトがシェルスクリプトではなく HTML を返す
</h3>

インストールコマンドを実行するときに、次のいずれかのエラーが表示される場合があります：

```text theme={null}
bash: line 1: syntax error near unexpected token `<'
bash: line 1: `<!DOCTYPE html>'
```

PowerShell では、同じ問題は次のように表示されます：

```text theme={null}
Invoke-Expression: Missing argument in parameter list.
```

リクエストのルーティング方法によっては、代わりに HTML ボディなしの 403 が表示される場合があります：

```text theme={null}
curl: (22) The requested URL returned error: 403
```

これらはすべて、インストール URL がインストールスクリプトではなく HTML ページまたはエラーステータスを返したことを意味します。HTML ページが「App unavailable in region」と表示される場合、Claude Code はお客様の国では利用できません。[サポートされている国](https://www.anthropic.com/supported-countries)を参照してください。

ボディなしの 403 は多くの場合同じ原因がありますが、企業プロキシまたはダウンロードをブロックしているファイアウォールからも発生する可能性があります。サポートされている国にいるのに 403 が表示される場合は、以下の代替インストーラーを試す前に[ネットワーク接続を確認する](#check-network-connectivity)を実行してください。これらは同じホストに到達するためです。

それ以外の場合、これはネットワークの問題、地域的なルーティング、または一時的なサービス中断が原因で発生する可能性があります。

**解決策：**

1. **別のインストール方法を使用してください**：

   macOS では、Homebrew 経由でインストールしてください：

   ```bash theme={null}
   brew install --cask claude-code
   ```

   Windows では、WinGet 経由でインストールしてください：

   ```powershell theme={null}
   winget install Anthropic.ClaudeCode
   ```

2. **数分後に再試行してください**：問題は一時的なことが多いです。待ってから元のコマンドを再度試してください。

<h3 id="command-not-found-claude-after-installation">
  インストール後に `command not found: claude`
</h3>

インストールが完了しましたが、`claude` が機能しません。正確なエラーはプラットフォームによって異なります：

| プラットフォーム    | エラーメッセージ                                                               |
| :---------- | :--------------------------------------------------------------------- |
| macOS       | `zsh: command not found: claude`                                       |
| Linux       | `bash: claude: command not found`                                      |
| Windows CMD | `'claude' is not recognized as an internal or external command`        |
| PowerShell  | `claude : The term 'claude' is not recognized as the name of a cmdlet` |

これは、インストールディレクトリがシェルの検索パスに含まれていないことを意味します。各プラットフォームの修正については、[PATH を確認する](#verify-your-path)を参照してください。

<h3 id="curl-56-failure-writing-output-to-destination">
  `curl: (56) Failure writing output to destination`
</h3>

`curl ... | bash` コマンドはスクリプトをダウンロードして Bash にパイプして実行します。このエラーと関連する `curl: (23) Failure writing output to destination` は、Bash がスクリプト全体を受け取らなかったことを意味します。終了コード 56 はダウンロード自体が中断されたことを示し、終了コード 23 は curl がパイプに受け取ったものを書き込めなかったことを示します。通常は Bash が早期に終了したためです。

**解決策：**

1. **ネットワークの安定性を確認してください**：Claude Code バイナリは `downloads.claude.ai` でホストされています。到達可能であることをテストしてください：
   ```bash theme={null}
   curl -sI https://downloads.claude.ai/claude-code-releases/latest
   ```
   `HTTP/2 200` という行はサーバーに到達したことを意味し、元の失敗は一時的なものである可能性があります。インストールコマンドを再試行してください。`Could not resolve host` または接続タイムアウトが表示される場合、ネットワークがダウンロードをブロックしています。

2. **別のインストール方法を試してください**：

   macOS では：

   ```bash theme={null}
   brew install --cask claude-code
   ```

   Windows では：

   ```powershell theme={null}
   winget install Anthropic.ClaudeCode
   ```

<h3 id="homebrew-cask-unavailable-or-outdated">
  Homebrew cask が利用できないか古い
</h3>

Homebrew が `Error: Cask 'claude-code' is unavailable: No Cask with this name exists` を報告する場合、Homebrew cask インデックスのローカルコピーが cask の公開より前のものです。インデックスを更新して再試行してください：

```bash theme={null}
brew update
brew install --cask claude-code
```

Homebrew が予想より古い Claude Code バージョンをインストールする場合、通常は同じ古いインデックスが原因です。`claude-code` cask は安定チャネルを追跡し、通常は最新リリースより約 1 週間遅れています。最新バージョンを実行するには、代わりに `brew install --cask claude-code@latest` を実行してください。2 つの cask の違いについては、[リリースチャネルを設定する](/docs/ja/setup#configure-release-channel)を参照してください。

<h3 id="tls-or-ssl-connection-errors">
  TLS または SSL 接続エラー
</h3>

`curl: (35) TLS connect error`、`schannel: next InitializeSecurityContext failed`、または PowerShell の `Could not establish trust relationship for the SSL/TLS secure channel` などのエラーは TLS ハンドシェイク失敗を示します。

**解決策：**

1. **システム CA 証明書を更新してください**：

   Ubuntu/Debian では：

   ```bash theme={null}
   sudo apt-get update && sudo apt-get install ca-certificates
   ```

   macOS では、システム curl は Keychain トラストストアを使用します。macOS 自体を更新するとルート証明書が更新されます。

2. **Windows では、インストーラーを実行する前に PowerShell で TLS 1.2 を有効にしてください**：
   ```powershell theme={null}
   [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
   irm https://claude.ai/install.ps1 | iex
   ```

3. **プロキシまたはファイアウォール干渉を確認してください**：TLS 検査を実行する企業プロキシは、`unable to get local issuer certificate` や `SELF_SIGNED_CERT_IN_CHAIN` を含むこれらのエラーを引き起こす可能性があります。インストール手順では、`--cacert` で curl を企業 CA バンドルに指定してください：
   ```bash theme={null}
   curl --cacert /path/to/corporate-ca.pem -fsSL https://claude.ai/install.sh | bash
   ```
   インストール後の Claude Code 自体については、`NODE_EXTRA_CA_CERTS` を設定して API リクエストが同じバンドルを信頼するようにしてください：
   ```bash theme={null}
   export NODE_EXTRA_CA_CERTS=/path/to/corporate-ca.pem
   ```
   証明書ファイルがない場合は IT チームに問い合わせてください。また、直接接続で試して、プロキシが原因であることを確認することもできます。

4. **Windows では、ネットワークが失効確認をブロックする場合はインストーラーを切り替えてください**。エラー `CRYPT_E_NO_REVOCATION_CHECK (0x80092012)` と `CRYPT_E_REVOCATION_OFFLINE (0x80092013)` は、curl がサーバーに到達したが、ネットワークが証明書失効ルックアップをブロックしていることを意味します。これは企業ファイアウォールの背後では一般的です。curl の `--ssl-revoke-best-effort` フラグを追加してもこれは修正されません。このフラグは `install.cmd` 自体のダウンロードにのみ適用され、スクリプト自体のダウンロードはこれなしで実行されるため、インストールは同じエラーで失敗します。ブロックされたルックアップを許容するインストール方法を使用してください。PowerShell を開き、PowerShell インストーラーを実行してください。これは .NET を通じてダウンロードし、失効サーバーに到達できない場合は失敗しません：
   ```powershell theme={null}
   irm https://claude.ai/install.ps1 | iex
   ```
   `winget install Anthropic.ClaudeCode` でインストールすることもできます。これは curl を完全に回避します。

<h3 id="failed-to-fetch-version-from-downloads-claude-ai">
  `Failed to fetch version from downloads.claude.ai`
</h3>

インストーラーがダウンロードサーバーに到達できませんでした。これは通常、`downloads.claude.ai` がネットワークでブロックされていることを意味します。

**解決策：**

1. **直接接続性をテストしてください**：
   ```bash theme={null}
   curl -sI https://downloads.claude.ai/claude-code-releases/latest
   ```

2. **プロキシの背後にいる場合**、インストーラーがプロキシを通じてルーティングできるように `HTTPS_PROXY` を設定してください。詳細については、[プロキシ設定](/docs/ja/network-config#proxy-configuration)を参照してください。
   ```bash theme={null}
   export HTTPS_PROXY=http://proxy.example.com:8080
   curl -fsSL https://claude.ai/install.sh | bash
   ```

3. **制限されたネットワーク上にいる場合**、別のネットワークまたは VPN を試すか、別のインストール方法を使用してください：

   macOS では：

   ```bash theme={null}
   brew install --cask claude-code
   ```

   Windows では：

   ```powershell theme={null}
   winget install Anthropic.ClaudeCode
   ```

<h3 id="wrong-install-command-on-windows">
  Windows での間違ったインストールコマンド
</h3>

`'irm' is not recognized`、`The token '&&' is not valid`、`A parameter cannot be found that matches parameter name 'fsSL'`、または `'bash' is not recognized as the name of a cmdlet` が表示される場合、別のシェルまたはオペレーティングシステムのインストールコマンドをコピーしました。

* **`irm` が認識されない**：CMD にいて、PowerShell ではありません。2 つのオプションがあります：

  スタートメニューで「PowerShell」を検索して PowerShell を開き、元のインストールコマンドを実行してください：

  ```powershell theme={null}
  irm https://claude.ai/install.ps1 | iex
  ```

  または CMD にとどまり、代わりに CMD インストーラーを使用してください：

  ```batch theme={null}
  curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
  ```

* **`&&` が有効ではない**：PowerShell にいますが、CMD インストーラーコマンドを実行しました。PowerShell インストーラーを使用してください：
  ```powershell theme={null}
  irm https://claude.ai/install.ps1 | iex
  ```

* **`A parameter cannot be found that matches parameter name 'fsSL'`**：Windows PowerShell で macOS/Linux `curl -fsSL ... | bash` インストーラーを実行しました。ここで `curl` は `Invoke-WebRequest` のエイリアスであり、`-fsSL` フラグを拒否します。代わりに PowerShell インストーラーを使用してください：
  ```powershell theme={null}
  irm https://claude.ai/install.ps1 | iex
  ```

* **`bash` が認識されない**：Windows で macOS/Linux インストーラーを実行しました。代わりに PowerShell インストーラーを使用してください：
  ```powershell theme={null}
  irm https://claude.ai/install.ps1 | iex
  ```

<h3 id="the-process-cannot-access-the-file-during-windows-install">
  Windows インストール中の `The process cannot access the file`
</h3>

PowerShell インストーラーが `Failed to download binary: The process cannot access the file ... because it is being used by another process` で失敗する場合、インストーラーは `%USERPROFILE%\.claude\downloads` に書き込むことができませんでした。これは通常、以前のインストール試行がまだ実行されているか、アンチウイルスソフトウェアがそのフォルダー内の部分的にダウンロードされたバイナリをスキャンしていることを意味します。

インストーラーを実行している他の PowerShell ウィンドウを閉じ、アンチウイルススキャンがファイルを解放するのを待ってください。その後、ダウンロードフォルダーを削除してインストーラーを再度実行してください：

```powershell theme={null}
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\downloads"
irm https://claude.ai/install.ps1 | iex
```

<h3 id="install-killed-on-low-memory-linux-servers">
  低メモリ Linux サーバーでインストール中に Killed
</h3>

インストール中に `Killed` メッセージが表示される場合、通常は Linux のメモリ不足（OOM）キラーがシステムがメモリ不足になったため `claude install` ステップを終了したことを意味します。これは小規模な VPS とクラウドインスタンスで一般的です。インストールスクリプトは原因を報告し、終了コード 137 で終了します：

```text theme={null}
Setting up Claude Code...
bash: line 142: 34803 Killed    "$binary_path" install ${TARGET:+"$TARGET"}
Installation was killed before it could finish (exit code 137). This usually means the system ran out of memory.
Claude Code needs roughly 512MB of free memory to install. Free up memory, then run this script again.
```

v2.1.200 より前では、スクリプトはシェルの単なる `Killed` 行と説明なしで終了しました。

インストールには約 512 MB の空きメモリが必要で、Claude Code を実行するにはさらに多くが必要です。[システム要件](/docs/ja/setup#system-requirements)を参照してください。

**解決策：**

1. **RAM が限られている場合はスワップスペースを追加してください**。スワップはディスク領域をオーバーフロー メモリとして使用し、物理 RAM が少ない場合でもインストールを完了できます。

   2 GB スワップファイルを作成して有効にしてください：

   ```bash theme={null}
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

   その後、インストールを再試行してください：

   ```bash theme={null}
   curl -fsSL https://claude.ai/install.sh | bash
   ```

2. **インストール前に他のプロセスを閉じて**メモリを解放してください。

3. **可能であれば、より大きなインスタンスを使用してください**。Claude Code には少なくとも 4 GB の RAM が必要です。

<h3 id="install-hangs-in-docker">
  Docker でのインストールハング
</h3>

Docker コンテナで Claude Code をインストールするときに、root として `/` にインストールするとハングが発生する可能性があります。

**解決策：**

1. **インストーラーを実行する前に作業ディレクトリを設定してください**。`/` から実行すると、インストーラーはファイルシステム全体をスキャンし、過度なメモリ使用を引き起こします。`WORKDIR` を設定すると、スキャンが小さなディレクトリに制限されます：
   ```dockerfile theme={null}
   WORKDIR /tmp
   RUN curl -fsSL https://claude.ai/install.sh | bash
   ```

2. **Docker メモリ制限を増やしてください**（Docker Desktop を使用している場合）：
   ```bash theme={null}
   docker build --memory=4g .
   ```

<h3 id="claude-desktop-overrides-the-claude-command-on-windows">
  Claude Desktop が Windows の `claude` コマンドをオーバーライドする
</h3>

Claude Desktop の古いバージョンをインストールした場合、`WindowsApps` ディレクトリに `Claude.exe` を登録して、Claude Code CLI よりも PATH の優先度を取得する可能性があります。`claude` を実行すると、CLI ではなく Desktop アプリが開きます。

Claude Desktop を最新バージョンに更新して、この問題を修正してください。

<h3 id="claude-code-on-windows-requires-either-git-for-windows-for-bash-or-powershell">
  Windows での Claude Code は Git for Windows（Bash 用）または PowerShell が必要です
</h3>

Git for Windows はオプションです。Claude Code は Git Bash がない場合、[PowerShell ツール](/docs/ja/tools-reference#powershell-tool)を使用するため、このエラーはどちらのシェルも見つからなかったことを意味します。

**PowerShell が PATH にない場合**、デフォルトの場所は `C:\Windows\System32\WindowsPowerShell\v1.0\` です。そのディレクトリを `PATH` に追加するか、`pwsh` を提供する [PowerShell 7](https://aka.ms/powershell) をインストールしてください。

**Git for Windows をインストールする代わりに**、[git-scm.com/downloads/win](https://git-scm.com/downloads/win) からダウンロードしてください。セットアップ中に「Add to PATH」を選択してください。インストール後、ターミナルを再起動してください。インストールすると Bash ツールが有効になり、Bash ベースのスクリプトとツーリングを操作するときに便利です。

**Git が既にインストールされている**が Claude Code が見つけられない場合は、[settings.json ファイル](/docs/ja/settings)でパスを設定してください：

```json theme={null}
{
  "env": {
    "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe"
  }
}
```

Git がどこか別の場所にインストールされている場合は、PowerShell で `where.exe git` を実行してパスを見つけ、そのディレクトリから `bin\bash.exe` パスを使用してください。

**パスが正しく、ファイルが存在する**が Claude Code がそれを見つけられないと報告する場合、AppLocker、グループポリシーソフトウェア制限ポリシー、または EDR エージェントなどのエンドポイントセキュリティソフトウェアが干渉している可能性があります。v2.1.116 より前のバージョンでは、Claude Code はパスを確認するために子プロセス（`cmd.exe`）を生成しました。これらのポリシーはこれをブロックできます。一般的な兆候は、`cmd.exe /c dir "C:\Program Files\Git\bin\bash.exe"` が PowerShell で直接実行するときは機能しますが、`claude.exe` によって起動されたときはサイレントに失敗することです。

Claude Code v2.1.116 以降はファイルシステムを直接チェックするため、最初に更新してください。現在のバージョンでエラーが続く場合は、IT チームに `claude.exe` と、`cmd.exe` や `bash.exe` を含むそれが生成するプロセスをエンドポイント保護ポリシーでホワイトリストに登録するよう依頼してください。

<h3 id="claude-code-does-not-support-32-bit-windows">
  Claude Code は 32 ビット Windows をサポートしていません
</h3>

Windows のスタートメニューには 2 つの PowerShell エントリが含まれています：`Windows PowerShell` と `Windows PowerShell (x86)`。x86 エントリは 32 ビットプロセスとして実行され、64 ビットマシンでもこのエラーをトリガーします。どちらの場合かを確認するには、エラーを生成したのと同じウィンドウで次を実行してください：

```powershell theme={null}
[Environment]::Is64BitOperatingSystem
```

これが `True` を出力する場合、オペレーティングシステムは問題ありません。ウィンドウを閉じて、x86 サフィックスなしで `Windows PowerShell` を開き、インストールコマンドを再度実行してください。

これが `False` を出力する場合、32 ビット版の Windows を使用しています。Claude Code には 64 ビットオペレーティングシステムが必要です。[システム要件](/docs/ja/setup#system-requirements)を参照してください。

<h3 id="linux-musl-or-glibc-binary-mismatch">
  Linux musl または glibc バイナリの不一致
</h3>

インストール後に `libstdc++.so.6` または `libgcc_s.so.1` などの不足している共有ライブラリに関するエラーが表示される場合、インストーラーはシステムに対応した間違ったバイナリバリアントをダウンロードした可能性があります。

```text theme={null}
Error loading shared library libstdc++.so.6: No such file or directory
```

これは、musl クロスコンパイルパッケージがインストールされている glibc ベースのシステムで発生する可能性があり、インストーラーがシステムを musl として誤検出します。

**解決策：**

1. **システムが使用している libc を確認してください**：
   ```bash theme={null}
   ldd --version 2>&1 | head -1
   ```
   `GNU libc` または `GLIBC` に言及している出力は glibc を意味します。`musl` に言及している出力は musl を意味します。

2. **glibc にいるが musl バイナリを取得した場合**、インストールを削除して再インストールしてください。`https://downloads.claude.ai/claude-code-releases/{VERSION}/manifest.json` のマニフェストを使用して正しいバイナリを手動でダウンロードすることもできます。`ldd --version` と `ls /lib/libc.musl*` の出力を含めて [GitHub issue](https://github.com/anthropics/claude-code/issues) をファイルしてください。

3. **実際に musl にいる場合**（Alpine Linux など）、必要なパッケージをインストールしてください：
   ```bash theme={null}
   apk add libgcc libstdc++ ripgrep
   ```

<h3 id="illegal-instruction">
  `Illegal instruction`
</h3>

`claude` またはインストーラーを実行すると `Illegal instruction` が出力される場合、ネイティブバイナリはプロセッサがサポートしていない CPU 命令を使用しています。2 つの異なる原因があります。

**アーキテクチャの不一致。** インストーラーは間違ったバイナリをダウンロードしました。たとえば、ARM サーバーで x86。macOS または Linux では `uname -m` で、PowerShell では `$env:PROCESSOR_ARCHITECTURE` で確認してください。結果が受け取ったバイナリと一致しない場合は、出力を含めて [GitHub issue](https://github.com/anthropics/claude-code/issues) をファイルしてください。

**古い CPU での不足している命令セット。** アーキテクチャは正しいが、それでも `Illegal instruction` が表示される場合、CPU は AVX またはバイナリが必要とする別の命令がない可能性があります。これは約 2013 年以前の Intel および AMD プロセッサに影響します。仮想マシンでは、ハイパーバイザーが AVX をゲストに渡さない場合があります。

VPS または VM では、`grep -m1 -ow avx /proc/cpuinfo` を実行してください。空の結果は AVX がゲストで利用できないことを意味します。

ネイティブバイナリの回避策はありません。[issue #50384](https://github.com/anthropics/claude-code/issues/50384) でステータスを追跡し、報告するときに Linux では `grep -m1 "model name" /proc/cpuinfo` から、macOS では `sysctl -n machdep.cpu.brand_string` から CPU モデルを含めてください。

別のインストール方法は同じネイティブバイナリをダウンロードし、どちらの原因も解決しません。

<h3 id="dyld-cannot-load-on-macos">
  macOS での `dyld: cannot load`
</h3>

インストール中に `dyld: cannot load`、`dyld: Symbol not found`、または `Abort trap: 6` が表示される場合、バイナリは macOS バージョンまたはハードウェアと互換性がありません。

```text theme={null}
dyld: cannot load 'claude-2.1.42-darwin-x64' (load command 0x80000034 is unknown)
Abort trap: 6
```

`libicucore` を参照する `Symbol not found` エラーは、macOS バージョンがバイナリがサポートするより古いことを示します：

```text theme={null}
dyld: Symbol not found: _ubrk_clone
  Referenced from: claude-darwin-x64 (which was built for Mac OS X 13.0)
  Expected in: /usr/lib/libicucore.A.dylib
```

**解決策：**

1. **macOS バージョンを確認してください**：Claude Code には macOS 13.0 以降が必要です。Apple メニューを開き、「このマックについて」を選択してバージョンを確認してください。

2. **古いバージョンを使用している場合は macOS を更新してください**。バイナリは古い macOS バージョンがサポートしていないロードコマンドとシステムライブラリを使用しています。Homebrew などの別のインストール方法は同じバイナリをダウンロードし、このエラーを解決しません。

<h3 id="exec-format-error-on-wsl1">
  WSL1 での `Exec format error`
</h3>

WSL で `claude` を実行すると `cannot execute binary file: Exec format error` が出力される場合、WSL1 にいて、[issue #38788](https://github.com/anthropics/claude-code/issues/38788) で追跡されている既知のネイティブバイナリ回帰に直面しています。バイナリのプログラムヘッダーが WSL1 のローダーが処理できない方法で変更されました。

最もクリーンな修正は、PowerShell からディストリビューションを WSL2 に変換することです：

```powershell theme={null}
wsl --set-version <DistroName> 2
```

WSL1 にとどまる必要がある場合は、動的リンカーを通じてバイナリを呼び出してください。ホームディレクトリが異なる場合はパスを置き換えて、WSL 内の `~/.bashrc` にこの関数を追加してください：

```bash theme={null}
claude() {
  /lib64/ld-linux-x86-64.so.2 "$(readlink -f "$HOME/.local/bin/claude")" "$@"
}
```

その後、`source ~/.bashrc` を実行して `claude` を再試行してください。

<h3 id="npm-install-errors-in-wsl">
  WSL での npm インストールエラー
</h3>

これらの問題は、WSL 内で `npm install -g` を使用して Claude Code をインストールした場合に適用されます。[ネイティブインストーラー](/docs/ja/setup)を使用した場合は、このセクションをスキップしてください。

**OS またはプラットフォーム検出の問題。** npm がインストール中にプラットフォームの不一致を報告する場合、WSL は Windows `npm` を取得している可能性があります。最初に `npm config set os linux` を実行してから、`npm install -g @anthropic-ai/claude-code --force` でインストールしてください。`sudo` を使用しないでください。

**`claude` を実行するときの `exec: node: not found`。** WSL 環境は Windows インストール Node.js を使用している可能性があります。`which npm` と `which node` で確認してください：`/mnt/c/` で始まるパスは Windows バイナリで、Linux パスは `/usr/` で始まります。これを修正するには、Linux ディストリビューションのパッケージマネージャーまたは [`nvm`](https://github.com/nvm-sh/nvm) 経由で Node をインストールしてください。

**nvm バージョンの競合。** WSL と Windows の両方に nvm がインストールされている場合、WSL でノードバージョンを切り替えると、WSL はデフォルトで Windows PATH をインポートし、Windows nvm が優先されるため、破損する可能性があります。最も一般的な原因は、nvm がシェルに読み込まれていないことです。nvm ローダーを `~/.bashrc` または `~/.zshrc` に追加してください：

```bash theme={null}
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

または現在のセッションで読み込んでください：

```bash theme={null}
source ~/.nvm/nvm.sh
```

nvm が読み込まれているが Windows パスがまだ優先される場合は、Linux Node パスを明示的に先頭に追加してください：

```bash theme={null}
export PATH="$HOME/.nvm/versions/node/$(node -v)/bin:$PATH"
```

<Warning>
  `appendWindowsPath = false` で Windows PATH インポートを無効にすることは避けてください。これは WSL から Windows 実行可能ファイルを呼び出す機能を破壊します。同様に、Windows 開発に使用する場合は Windows から Node.js をアンインストールすることは避けてください。
</Warning>

<h3 id="permission-errors-during-installation">
  インストール中の権限エラー
</h3>

ネイティブインストーラーが権限エラーで失敗する場合、ターゲットディレクトリが書き込み可能でない可能性があります。[ディレクトリ権限を確認する](#check-directory-permissions)を参照してください。

以前に npm でインストールしていて、npm 固有の権限エラーに直面している場合は、ネイティブインストーラーに切り替えてください：

```bash theme={null}
curl -fsSL https://claude.ai/install.sh | bash
```

<h3 id="native-binary-not-found-after-npm-install">
  npm インストール後にネイティブバイナリが見つからない
</h3>

`@anthropic-ai/claude-code` npm パッケージは、`@anthropic-ai/claude-code-darwin-arm64` などのプラットフォーム固有のオプション依存関係を通じてネイティブバイナリを取得します。インストール後に `claude` を実行すると `Could not find native binary package "@anthropic-ai/claude-code-<platform>"` が出力される場合は、次の原因を確認してください：

* **オプション依存関係が無効になっています。** npm インストールコマンドから `--omit=optional` を削除し、pnpm から `--no-optional` を削除し、yarn から `--ignore-optional` を削除し、`.npmrc` が `optional=false` を設定していないことを確認してから、再インストールしてください。ネイティブバイナリはオプション依存関係としてのみ配信されるため、スキップされた場合は JavaScript フォールバックはありません。
* **サポートされていないプラットフォーム。** プリビルドバイナリは `darwin-arm64`、`darwin-x64`、`linux-x64`、`linux-arm64`、`linux-x64-musl`、`linux-arm64-musl`、`win32-x64`、および `win32-arm64` 用に公開されています。Claude Code は他のプラットフォーム用のバイナリを出荷しません。[システム要件](/docs/ja/setup#system-requirements)を参照してください。FreeBSD では、インストーラーはプラットフォームをサポートされていないと報告します。v2.1.205 より前では、FreeBSD を Linux として扱い、実行できないバイナリをダウンロードしました。
* **企業 npm ミラーがプラットフォームパッケージを欠いています。** レジストリがメタパッケージに加えて 8 つすべての `@anthropic-ai/claude-code-*` プラットフォームパッケージをミラーしていることを確認してください。

`--ignore-scripts` でインストールしてもこのエラーはトリガーされません。バイナリを所定の位置にリンクする postinstall ステップはスキップされるため、Claude Code はプラットフォームバイナリを各起動時に検索して生成するラッパーにフォールバックします。これは機能しますが、より遅く開始します。スクリプトを有効にして再インストールして、直接実行してください。

<h2 id="login-and-authentication">
  ログインと認証
</h2>

これらのセクションはログイン失敗、OAuth エラー、およびトークンの問題に対処します。

<h3 id="reset-your-login">
  ログインをリセットする
</h3>

ログインが失敗し、原因が明らかでない場合、クリーンな再認証がほとんどの場合を解決します：

1. `/logout` を実行して完全にサインアウトしてください
2. Claude Code を閉じてください
3. `claude` で再起動して、認証プロセスを再度完了してください

ログイン中にブラウザが自動的に開かない場合は、`c` を押して OAuth URL をクリップボードにコピーしてから、手動でブラウザに貼り付けてください。これは、URL が狭いまたは SSH ターミナルで行をまたいでラップされ、直接クリックできない場合にも機能します。

<h3 id="oauth-error-invalid-code">
  OAuth エラー：無効なコード
</h3>

`OAuth error: Invalid code. Please make sure the full code was copied` が表示される場合、ログインコードが期限切れになったか、コピー貼り付け中に切り詰められました。

**解決策：**

* ブラウザが開いた後、Enter キーを押して迅速にログインを完了してください
* ブラウザが自動的に開かない場合は、`c` を入力して完全な URL をコピーしてください
* リモート/SSH セッションを使用している場合、ブラウザは間違ったマシンで開く可能性があります。ターミナルに表示されている URL をコピーして、代わりにローカルブラウザで開いてください。

<h3 id="403-forbidden-after-login">
  ログイン後の 403 Forbidden
</h3>

ログイン後に `API Error: 403 {"error":{"type":"forbidden","message":"Request not allowed"}}` が表示される場合：

* **Claude Pro/Max ユーザー**：[claude.ai/settings](https://claude.ai/settings) でサブスクリプションがアクティブであることを確認してください
* **Anthropic Console ユーザー**：アカウントに「Claude Code」または「Developer」ロールがあることを確認してください。管理者は Anthropic Console の設定 → メンバーで割り当てます。
* **プロキシの背後**：企業プロキシは API リクエストに干渉する可能性があります。[ネットワーク設定](/docs/ja/network-config) を参照してプロキシセットアップを確認してください。

<h3 id="this-organization-has-been-disabled-with-an-active-subscription">
  このオーガニゼーションはアクティブなサブスクリプションで無効になっています
</h3>

アクティブな Claude サブスクリプションがあるにもかかわらず `API Error: 400 ... "This organization has been disabled"` が表示される場合、`ANTHROPIC_API_KEY` 環境変数がサブスクリプションをオーバーライドしています。これは、前の雇用主またはプロジェクトからの古い API キーがシェルプロファイルに設定されている場合に一般的に発生します。

`ANTHROPIC_API_KEY` が存在し、承認されている場合、Claude Code はサブスクリプションの OAuth 認証情報の代わりにそのキーを使用します。`-p` フラグを使用した非対話モードでは、存在する場合、キーは常に使用されます。[認証の優先順位](/docs/ja/authentication#authentication-precedence) を参照して、完全な解決順序を確認してください。

代わりにサブスクリプションを使用するには、環境変数を設定解除し、シェルプロファイルから削除してください：

```bash theme={null}
unset ANTHROPIC_API_KEY
claude
```

`~/.zshrc`、`~/.bashrc`、または `~/.profile` で `export ANTHROPIC_API_KEY=...` 行を確認して削除し、変更を永続的にしてください。Windows では、`$PROFILE` の PowerShell プロファイルと `ANTHROPIC_API_KEY` のユーザー環境変数を確認してください。Claude Code 内で `/status` を実行して、どの認証方法がアクティブであるかを確認してください。

<h3 id="oauth-login-fails-in-wsl2-ssh-or-containers">
  WSL2、SSH、またはコンテナでの OAuth ログイン失敗
</h3>

Claude Code が WSL2 で実行されている場合、SSH 経由でリモートマシンで実行されている場合、またはコンテナ内で実行されている場合、ブラウザは通常、別のホストで開き、そのリダイレクトは Claude Code のローカルコールバックサーバーに到達できません。サインイン後、ブラウザは自動的にリダイレクトされるのではなく、ログインコードを表示します。ターミナルの `Paste code here if prompted` プロンプトにそのコードを貼り付けてログインを完了してください。

WSL2 からブラウザがまったく開かない場合は、`BROWSER` 環境変数を Windows ブラウザパスに設定してください：

```bash theme={null}
export BROWSER="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
claude
```

または、対話型ログインプロンプトで `c` を押して OAuth URL をコピーするか、`claude auth login` が出力する URL をコピーして、ローカルマシンのブラウザで開いてください。

対話型プロンプトにコードを貼り付けても何もしない場合、ターミナルの貼り付けバインディングはおそらく入力フィールドに到達していません。ターミナルの別の貼り付けショートカット（Windows Terminal では右クリックまたは Shift+Insert）を試すか、標準入力から貼り付けられたコードを読み取る `claude auth login` を使用してください：

```bash theme={null}
claude auth login
```

このフォールバックは、ネイティブ Windows またはコードを対話型プロンプトに貼り付けるのが失敗するその他のターミナルにも適用されます。

<h3 id="not-logged-in-or-token-expired">
  ログインしていないか、トークンが期限切れ
</h3>

Claude Code がセッション後に再度ログインするよう求める場合、OAuth トークンが期限切れになった可能性があります。

`/login` を実行して再認証してください。これが頻繁に発生する場合は、トークン検証が正しいタイムスタンプに依存するため、システムクロックが正確であることを確認してください。

macOS では、Keychain がロックされているか、パスワードがアカウントパスワードと同期していない場合、ログインが失敗する可能性があります。これにより、Claude Code が認証情報を保存できなくなります。`claude doctor` を実行して Keychain アクセスを確認してください。Keychain を手動でロック解除するには、`security unlock-keychain ~/Library/Keychains/login.keychain-db` を実行してください。ロック解除が役に立たない場合は、Keychain Access を開き、`login` キーチェーンを選択して、編集 > キーチェーン「login」のパスワードを変更を選択して、アカウントパスワードと再同期してください。

<h3 id="bedrock-agent-platform-or-foundry-credentials-not-loading">
  Bedrock、Agent Platform、または Foundry 認証情報が読み込まれない
</h3>

Claude Code をクラウドプロバイダーを使用するように設定し、Amazon Bedrock で `Could not load credentials from any providers`、Google Cloud の Agent Platform で `Could not load the default credentials`、または Microsoft Foundry で `ChainedTokenCredential authentication failed` が表示される場合、クラウドプロバイダー CLI は現在のシェルで認証されていない可能性があります。

Amazon Bedrock の場合、AWS 認証情報が有効であることを確認してください：

```bash theme={null}
aws sts get-caller-identity
```

Google Cloud の Agent Platform の場合、`ANTHROPIC_VERTEX_PROJECT_ID` と `CLOUD_ML_REGION` がシェルに設定されていることを確認してから、アプリケーションのデフォルト認証情報を設定してください：

```bash theme={null}
gcloud auth application-default login
```

Microsoft Foundry の場合、`ANTHROPIC_FOUNDRY_API_KEY` が設定されていることを確認するか、Azure CLI でサインインして、デフォルト認証情報チェーンがアカウントを見つけられるようにしてください：

```bash theme={null}
az login
```

認証情報がターミナルで機能するが VS Code または JetBrains 拡張機能では機能しない場合、IDE プロセスはおそらくシェル環境を継承していません。IDE 独自の設定でプロバイダー環境変数を設定するか、既にエクスポートされているターミナルから IDE を起動してください。

完全なプロバイダーセットアップについては、[Amazon Bedrock](/docs/ja/amazon-bedrock)、[Google Cloud の Agent Platform](/docs/ja/google-vertex-ai)、または [Microsoft Foundry](/docs/ja/microsoft-foundry) を参照してください。

<h2 id="still-stuck">
  まだ立ち往生している
</h2>

上記のいずれも問題を解決しない場合：

1. [GitHub リポジトリ](https://github.com/anthropics/claude-code/issues)で既知の問題を確認するか、オペレーティングシステム、実行したインストールコマンド、および完全なエラー出力を含めて新しい問題を開いてください
2. `claude --version` が機能するが他に何か問題がある場合は、`claude doctor` を実行して自動診断レポートを取得してください
3. セッションを開始できる場合は、Claude Code 内で `/feedback` を使用して問題を報告してください
