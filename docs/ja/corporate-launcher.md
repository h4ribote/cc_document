> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 企業ランチャーの背後で Claude Code を実行する

> CLAUDE_CODE_PROCESS_WRAPPER を使用して、Claude Code がそのバイナリから起動するプロセス（バックグラウンドサービスとすべてのエージェントビューセッションを含む）を必須ランチャーを通じてルーティングします。

一部の組織では、ワークステーション上のすべてのプロセスが必須ランチャーを通じて起動することを要求しています。ランチャーは、企業のセキュリティ体制が依存するサンドボックス、ネットワーク制御、または認証情報の注入を適用し、それなしで起動するバイナリはポリシー違反です。

`CLAUDE_CODE_PROCESS_WRAPPER` は、Claude Code がそのバイナリから起動するすべてのプロセスをランチャーを通じて実行します。バックグラウンドサービス、[エージェントビュー](/docs/ja/agent-view)でホストするすべてのセッション、および更新後の Claude Code の再起動が含まれます。ランチャーの絶対パスに設定すると、Claude Code はランチャーを実行し、Claude Code コマンドをその引数として渡します。

`PATH` 上の `claude` コマンドをラップするランチャーはこれらのプロセスに到達できません。これらのプロセスは `claude` を検索せずにバイナリの直接パスから起動するためです。

<Note>
  `CLAUDE_CODE_PROCESS_WRAPPER` には Claude Code v2.1.208 以降が必要です。以前のバージョンは変数を無視し、すべてのプロセスをラップなしで起動します。
</Note>

<h2 id="what-the-launcher-covers">
  ランチャーがカバーするもの
</h2>

`CLAUDE_CODE_PROCESS_WRAPPER` が設定されている場合、Claude Code は以下の各プロセスをランチャーを通じて起動します。

* `claude agents` とバックグラウンドセッションがオンデマンドで起動するバックグラウンドサービス。
* すべてのエージェントビュー行内の Claude Code セッションとターミナルホスト（サービスが準備しておく温かいスタンバイセッションを含む）。
* 更新またはクラッシュ後にサービスが再生成するセッション。
* 更新のインストールを完了するために Claude Code が自身を再起動するプロセス（エージェントビューの更新用再起動アクションを含む）。

Windows では、変数は無視されます。ランチャーコントラクトは `exec` に依存しており、Windows はこれをサポートしていません。変数が設定されている Windows マシンはすべてのプロセスをラップなしで実行し、正常に動作します。唯一の信号は[デバッグログ](/docs/ja/troubleshooting)の警告です。ランチャーポリシーが Windows をカバーしている場合、変数はそこでそれを満たしません。ロールアウトを計画する際に Windows マシンをラップなしとしてカウントしてください。

<h3 id="processes-that-start-outside-the-launcher">
  ランチャーの外で起動するプロセス
</h3>

3 つのプロセスはランチャーを通じて起動しません。

* [インストール済みバックグラウンドサービス](/docs/ja/agent-view#the-supervisor-process)：`launchd` または `systemd` がそのプロセスをユニットファイルから起動します。これが適用される場合、`/status` と `claude daemon status` が警告を表示し、サービスが変数をその設定で再起動すると、サービスが生成するセッションはランチャーを通じて起動します。
* ターミナルで自分で起動するセッション。これは呼び出し方法に関係なく実行されます。これらのセッションをカバーするには、`PATH` の前のディレクトリに `claude` という名前のスクリプトを配置し、ランチャーを実際のバイナリで実行します。管理されたシンボリックリンクを置き換えないでください。自己生成は `PATH` を参照しないため、2 つのランチャーはスタックしません。
* `claude-cli://` ディープリンクの最初のプロセス。オペレーティングシステムのプロトコルハンドラーが直接起動します。そのセッションがバックグラウンドで起動するすべてのものはランチャーを通じて実行されます。このパスを完全に閉じるには、`disableDeepLinkRegistration` 設定で[ハンドラー登録を防止](/docs/ja/deep-links#registration-and-supported-platforms)してください。

<h3 id="helper-process-names-in-process-monitors">
  プロセスモニターのヘルパープロセス名
</h3>

ランチャーが設定されている場合、`ps` と Activity Monitor は Claude Code の `claude bg-pty-host` と `claude bg-spare` ラベルの代わりに、バックグラウンドヘルパープロセスのバージョン付きバイナリ名を表示します。これはランチャーの `exec` が引数リストを再構築するためです。名前変更は隠蔽ではなく副作用です。プロセスはそれ以外は変更されず、Claude Code は表示名ではなくバイナリパスで独自のプロセスを識別します。

<h2 id="set-up-the-launcher">
  ランチャーをセットアップする
</h2>

<Steps>
  <Step title="ランチャースクリプトを作成する">
    `/opt/corp/launcher` などの絶対パスに実行可能スクリプトを作成します。Claude Code はそれを完全な Claude Code コマンドをその引数として実行し、スクリプトは `exec "$@"` を呼び出して終了し、自身を Claude Code に置き換える必要があります。

    ```bash theme={null}
    #!/bin/sh
    # Your organization's setup: enter the sandbox, apply
    # network controls, or inject credentials.
    exec "$@"
    ```

    `chmod +x` で実行可能にします。セットアップ部分は、Claude Code を実行する前にランチャーが実行する必要があることです。[下記のランチャーコントラクト](#the-launcher-contract)はスクリプトが従う必要があるルールをリストしています。

    <Note>
      以前に `~/.local/bin/claude` シンボリックリンクをランチャーで置き換えた場合は、同じ変更で元のシンボリックリンクを復元してください。置き換えられたシンボリックリンクにより、最初のラップされたセッションがバックグラウンドサービスを両方のランチャーを通じて同時に起動し、インストールを外部管理状態に置きます。`/doctor` がそれを報告し、自動更新はファイルをそのままにし、古いバージョンのクリーンアップはインストーラーが再びそのパスを管理するまで無効のままです。
    </Note>
  </Step>

  <Step title="設定で CLAUDE_CODE_PROCESS_WRAPPER を設定する">
    デタッチされたバックグラウンドサービスがそれを継承するように、設定ファイルの `env` ブロックで変数を設定します。シェル `export` では不十分です。バックグラウンドサービスはオンデマンドで起動し、シェルより長く存続し、シェルプロファイルを再読み込みしません。

    1 台のマシンの場合は、`~/.claude/settings.json` に追加します。組織内のすべてのマシンにデプロイするには、同じブロックを[管理設定](/docs/ja/permissions#managed-settings)に配置します。

    ```json theme={null}
    {
      "env": {
        "CLAUDE_CODE_PROCESS_WRAPPER": "/opt/corp/launcher"
      }
    }
    ```

    複数のソースが変数を設定する場合、管理設定値は `~/.claude/settings.json` とシェルでエクスポートされた値の両方をオーバーライドするため、ユーザーは自己生成を別のランチャーにポイントできません。

    プロジェクトおよびローカル設定はこの変数を設定できません。リポジトリにコミットされたファイルは、マシン上のすべての Claude Code プロセスの前にバイナリを配置できないため、`.claude/settings.json` または `.claude/settings.local.json` の `CLAUDE_CODE_PROCESS_WRAPPER` は無視され、[デバッグログ](/docs/ja/troubleshooting)に警告が表示されます。
  </Step>

  <Step title="バックグラウンドサービスとセッションを再起動する">
    実行中のバックグラウンドサービスと開いている `claude` セッションは起動時に変数を 1 回読み込むため、再起動されるまでラップなしでプロセスを起動し続けます。`claude daemon stop --any` を実行してオンデマンドサービスを停止します。`claude agents` などそれを必要とする次のコマンドがラップされたものを起動します。[インストール済みサービス](/docs/ja/agent-view#the-supervisor-process)は `--any` なしで `claude daemon stop` を実行します。その後、開いている `claude` セッションを再起動します。

    手動で再起動できないマシンでは、設定プッシュ後に起動された最初のセッションが残されたラップなしのオンデマンドサービスを自動的に廃止します。新しいセッションが起動しないマシンは、セッションが起動するまでラップなしのサービスを保持し、インストール済みサービスは常にこのステップで再起動が必要です。
  </Step>

  <Step title="検証する">
    セッションで `/status` を実行します。Self-exec エントリは解決された起動コマンドを表示し、実行中のバックグラウンドサービスがそれと一致しない場合に警告します。`claude daemon status` はシェルから同じ情報を出力します。変数を設定解除した後も含めて、`/status` はエントリを表示しなくなります。
  </Step>
</Steps>

<h2 id="the-launcher-contract">
  ランチャーコントラクト
</h2>

ランチャーが実行できない場合、Claude Code はプロセスをラップなしで起動する代わりに起動を拒否します。Windows では、[変数は無視され](#what-the-launcher-covers)、プロセスはラップなしで起動します。Claude Code はスクリプトをこれらのルールに保持します。

* **`exec "$@"` で終了する。** フォークして終了するランチャーは、バックグラウンドサービスが追跡できない孤立した Claude Code プロセスを残します。エージェントビューはそのようなセッションを失敗とマークし、ランチャーを名前で示すメッセージを表示し、サービスはランチャーが残したものを回収します。
* **引数を並べ替え、吸収、または前置しない。** 最初の引数は Claude Code バイナリで、その後のすべてはその argv です。
* **継承されたすべての環境変数を `exec` に渡す。** 注入された認証情報などの変数を追加することは問題ありませんが、継承されたものをドロップすることはできません。
  * セッションごとの認証トークン、モデルとプロバイダーの選択、および `CLAUDE_CODE_PROCESS_WRAPPER` 自体はすべて継承された環境で移動するため、許可リストから再構築するランチャーは起動するセッションを破壊し、`/status` はランチャーの不一致を報告します。
  * ランチャーが環境をリセットするネームスペースまたはサンドボックスに入る必要がある場合は、その内部で継承された環境を逐語的に再エクスポートします。
* **ランチャーが実行されるたびに約 3 秒以内に `exec` に到達する。** コールドバックグラウンドディスパッチは最初の出力バイトの前にランチャーを 2 回連続で実行するため、シングルサインオン交換などの遅い作業を遅延または キャッシュから実行します。
  * 予算をはるかに超えて実行するランチャーは停止した起動として扱われ、再起動されます。
* **自身の内部から呼び出されることに耐える。** Claude Code はすべてのネストされた自己生成にランチャーを適用するため、排他的リソースを取得するランチャーはそれが既に保持していることを検出する必要があります。
* **Claude Code が起動する前にターミナルに書き込まない。** `exec` の前に出力されたものはすべて、セッションが初期化前に終了した場合のクラッシュ原因として報告されます。

<h3 id="format-of-the-claude_code_process_wrapper-value">
  `CLAUDE_CODE_PROCESS_WRAPPER` 値の形式
</h3>

ほとんどのランチャーでは、値はスクリプトの絶対パスです（`/opt/corp/launcher` など）。

ランチャーに独自の引数を渡すには、パスの後に記述します。Claude Code は値をシェルコマンドではなく引数リストとして解析します。

* 空白はトークンを区切り、二重引用符はスペースを含むトークンをグループ化します。
* `[` で始まる値は JSON 文字列配列として読み込まれます（`["/opt/corp/launcher", "--profile", "cc"]` など）。
* シェル構文は機能しません。変数展開またはグロビングはなく、`;`、`|`、`&`、`$(` などの引用符なしの演算子は再解釈ではなく設定エラーとして拒否されます。

値を使用できない場合、Claude Code は影響を受けるプロセスの起動を拒否し、[理由を報告](/docs/ja/errors#claude_code_process_wrapper-launcher-errors)します。

<h2 id="relationship-to-claude_code_shell_prefix">
  `CLAUDE_CODE_SHELL_PREFIX` との関係
</h2>

`CLAUDE_CODE_PROCESS_WRAPPER` は Claude Code 独自のプロセスをラップし、コマンドを分離された argv トークンとしてランチャーに渡して `exec` します。[`CLAUDE_CODE_SHELL_PREFIX`](/docs/ja/env-vars) は Claude Code が代わりに実行するシェルコマンド（Bash ツール呼び出し、hooks、stdio MCP サーバーを起動するコマンドなど）をラップし、各コマンドを `$1` の単一のシェル引用文字列として渡して、ラッパーが再評価します。一方用に書かれたランチャーはもう一方として機能しません。

<h2 id="related-resources">
  関連リソース
</h2>

* [エージェントビュー](/docs/ja/agent-view)：ランチャーがカバーするバックグラウンドセッションとスーパーバイザープロセス
* [環境変数](/docs/ja/env-vars)：`CLAUDE_CODE_PROCESS_WRAPPER` リファレンスエントリ
* [管理設定](/docs/ja/permissions#managed-settings)：`env` ブロックをフリート全体に配信
* [ランチャーエラーリファレンス](/docs/ja/errors#claude_code_process_wrapper-launcher-errors)：拒否メッセージと復旧方法
