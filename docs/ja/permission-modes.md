> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 権限モードを選択する

> Claude がファイルを編集またはコマンドを実行する前に確認するかどうかを制御します。CLI で Shift+Tab でモードをサイクルするか、VS Code、Desktop、claude.ai のモードセレクターを使用します。

Claude がファイルを編集、シェルコマンドを実行、またはネットワークリクエストを行いたい場合、一時停止してアクションを承認するよう求めます。権限モードは、その一時停止がどのくらいの頻度で発生するかを制御します。選択するモードはセッションのフローを形作ります。Manual モードではアクションが来るたびにレビューし、より緩いモードでは Claude が長い中断のない作業を行い、完了時に報告できます。機密作業には監視を強化し、信頼できる方向性には中断を減らしてください。

<h2 id="available-modes">
  利用可能なモード
</h2>

各モードは利便性と監視のバランスが異なります。以下の表は、各モードで権限プロンプトなしで Claude が実行できることを示しています。

| モード                                                                 | 確認なしで実行されるもの                                               | 最適な用途             |
| :------------------------------------------------------------------ | :--------------------------------------------------------- | :---------------- |
| `default`                                                           | 読み取りのみ                                                     | 開始、機密作業           |
| [`acceptEdits`](#auto-approve-file-edits-with-acceptedits-mode)     | 読み取り、ファイル編集、一般的なファイルシステムコマンド（`mkdir`、`touch`、`mv`、`cp` など） | レビュー中のコードの反復処理    |
| [`plan`](#analyze-before-you-edit-with-plan-mode)                   | 読み取りのみ                                                     | コードベースの探索、変更前     |
| [`auto`](#eliminate-prompts-with-auto-mode)                         | すべて、バックグラウンド安全チェック付き                                       | 長時間タスク、プロンプト疲労の軽減 |
| [`dontAsk`](#allow-only-pre-approved-tools-with-dontask-mode)       | 事前承認済みツールのみ                                                | ロックダウン CI とスクリプト  |
| [`bypassPermissions`](#skip-all-checks-with-bypasspermissions-mode) | すべて                                                        | 隔離されたコンテナと VM のみ  |

すべてのアクションをレビューするモードは、CLI、`claude --help`、VS Code と JetBrains 拡張機能、およびデスクトップアプリでは **Manual** という名前です。その設定値は `default` で、これは hooks と SDK 統合が使用するものです。CLI は値を入力する場所ならどこでも `manual` をエイリアスとして受け入れます。例えば `claude --permission-mode manual` または `"defaultMode": "manual"` です。Manual ラベルと `manual` エイリアスには Claude Code v2.1.200 以降が必要です。デスクトップアプリのラベルは CLI バージョンに依存しません。

`bypassPermissions` を除くすべてのモードで、[保護されたパス](#protected-paths)への書き込みは自動承認されることはなく、リポジトリ状態と Claude 独自の設定を偶発的な破損から保護します。

モードはベースラインを設定します。[権限ルール](/docs/ja/permissions#manage-permissions)を上に層状にして、特定のツールを事前承認またはブロックします。拒否ルール、明示的な確認ルール、[コネクタツールの組織 `ask` 設定](/docs/ja/mcp#organization-controls-on-connector-tools)、および [`requiresUserInteraction`](/docs/ja/mcp#require-approval-for-a-specific-tool) マーカーは `bypassPermissions` を含むすべてのモードで適用されます。許可ルールはそのモードでは効果がありません。他のすべてが既に承認されているためです。

<h2 id="switch-permission-modes">
  権限モードを切り替える
</h2>

セッション中、起動時、または永続的なデフォルトとしてモードを切り替えることができます。モードは Claude にチャットで尋ねるのではなく、これらのコントロールを通じて設定されます。以下からインターフェースを選択して、変更方法を確認してください。

<Tabs>
  <Tab title="CLI">
    **セッション中**：`Shift+Tab` を押して `default` → `acceptEdits` → `plan` をサイクルします。現在のモードはステータスバーに表示されます。Manual モード（そのサイクルのデフォルト）は、グレーの `⏸ manual mode on` バッジを表示します。v2.1.203 より前では、ステータスバーは Manual モードでバッジを表示していませんでした。

    すべてのモードがデフォルトサイクルに含まれるわけではありません。

    * `auto`：アカウントが [auto モード要件](#eliminate-prompts-with-auto-mode)を満たす場合に表示されます。auto へのサイクルは確認プロンプトなしでモードを切り替えます
    * `bypassPermissions`：`--permission-mode bypassPermissions`、`--dangerously-skip-permissions`、または `--allow-dangerously-skip-permissions` で開始した後に表示されます。`--allow-` バリアントはモードをサイクルに追加しますが、アクティブ化しません
    * `dontAsk`：サイクルに表示されることはありません。`--permission-mode dontAsk` で設定します

    有効なオプションモードは `plan` の後にスロットインし、`bypassPermissions` が最初で `auto` が最後です。両方が有効な場合、`bypassPermissions` から `auto` へのサイクルを通過します。

    **起動時**：モードをフラグとして渡します。

    ```bash theme={null}
    claude --permission-mode plan
    ```

    **デフォルトとして**：[設定](/docs/ja/settings#settings-files)で `defaultMode` を設定します。

    ```json theme={null}
    {
      "permissions": {
        "defaultMode": "acceptEdits"
      }
    }
    ```

    同じ `--permission-mode` フラグは [非対話的実行](/docs/ja/headless)用に `-p` で機能します。
  </Tab>

  <Tab title="VS Code">
    **セッション中**：プロンプトボックスの下部にあるモード指示器をクリックします。

    **デフォルトとして**：VS Code 設定で `claudeCode.initialPermissionMode` を設定するか、Claude Code 拡張機能設定パネルを使用します。

    モード指示器は以下のラベルを表示し、各ラベルが適用するモードにマップされます。

    | UI ラベル  | モード                 |
    | :------ | :------------------ |
    | 手動      | `default`           |
    | 自動編集    | `acceptEdits`       |
    | 計画モード   | `plan`              |
    | 自動モード   | `auto`              |
    | 権限をバイパス | `bypassPermissions` |

    v2.1.205 より前では、拡張機能は `plan` を Plan mode、`auto` を Auto mode とラベル付けしていました。

    自動モードは、アカウントが [auto モードセクション](#eliminate-prompts-with-auto-mode)にリストされているすべての要件を満たす場合、モード指示器に表示されます。`claudeCode.initialPermissionMode` 設定は `auto` を受け入れません。デフォルトで自動モードで開始するには、代わりに [ユーザー設定](/docs/ja/settings#settings-files)で `defaultMode` を設定します。Claude Code はプロジェクトおよびローカル設定の `defaultMode: "auto"` を無視します。

    権限をバイパスするには、拡張機能設定で **Allow dangerously skip permissions** トグルが必要です。その後、モード指示器に表示されます。

    拡張機能固有の詳細については、[VS Code ガイド](/docs/ja/vs-code)を参照してください。
  </Tab>

  <Tab title="JetBrains">
    JetBrains プラグインは IDE ターミナルで Claude Code を実行するため、モードの切り替えは CLI と同じように機能します。`Shift+Tab` を押してサイクルするか、起動時に `--permission-mode` を渡します。
  </Tab>

  <Tab title="Desktop">
    **セッション中**：送信ボタンの横にあるモードセレクターを使用します。すべてのモードがセレクターに表示されるわけではありません。

    * **自動**：アカウントが [auto モード要件](#eliminate-prompts-with-auto-mode)を満たす場合に表示されます
    * **権限をバイパス**：Pro および Max プランの Desktop 設定で **Allow bypass permissions mode** トグルが必要です。Team および Enterprise プランでは、組織ポリシーがそれを制御します

    Desktop 固有の詳細については、Desktop ガイドの [権限モードを選択する](/docs/ja/desktop#choose-a-permission-mode)を参照してください。

    **デフォルトとして**：[設定](/docs/ja/settings#settings-files)で `defaultMode` を設定します。Desktop アプリは CLI と同じ設定ファイルを読み取り、新しいローカルセッションにモードを適用します。

    モードセレクターで選択したモードはフォルダごとに記憶され、そのフォルダの `defaultMode` より優先されます。Plan は例外です。それを選択すると現在のセッションのみに適用されます。

    この例は、新しいローカルセッションのデフォルトとして Plan モードを設定します。

    ```json theme={null}
    {
      "permissions": {
        "defaultMode": "plan"
      }
    }
    ```
  </Tab>

  <Tab title="Web and mobile">
    [claude.ai/code](https://claude.ai/code) のプロンプトボックスの横またはモバイルアプリのモードドロップダウンを使用します。権限プロンプトは承認のために claude.ai に表示されます。どのモードが表示されるかはセッションが実行される場所によります。

    * **[Claude Code on the web](/docs/ja/claude-code-on-the-web) のクラウドセッション**：編集を受け入れる、計画モード、および自動モード。編集を受け入れるは `default` モードに対応します。クラウド環境はモードに関係なくファイル編集を事前承認するため、ドロップダウンは手動の代わりに編集を受け入れるを表示します。設定からの `defaultMode: "acceptEdits"` は依然として尊重されます。自動モードは組織がそれを許可し、選択されたモデルがそれをサポートする場合にのみ表示されます。権限をバイパスは利用できません。
    * **ローカルマシンの [Remote Control](/docs/ja/remote-control) セッション**：手動、編集を受け入れる、および計画モード。アプリから自動と権限をバイパスを選択することはできません。ドロップダウンはローカルセッションが実行されているモードを表示します。これにはターミナルから設定されたモードが含まれ、アプリまたはターミナルでモードが変更されると更新されます。唯一の例外は権限をバイパスです。セッションはそのモードを claude.ai に報告することはないため、ターミナルからそれに切り替えてもドロップダウンに表示される内容は変わりません。v2.1.202 より前では、`/remote-control` または `claude --remote-control` で接続されたセッションはモードをまったく報告しなかったため、claude.ai とモバイルアプリはセッションが実行されていないモードを表示する可能性がありました。不一致はラベルのみに影響しました。Claude Code は権限プロンプトをセッションの実際のモードから生成し、それらは依然としてアプリに表示されて承認されました。

    Remote Control の場合、ホストを起動するときに開始モードを設定することもできます。

    ```bash theme={null}
    claude remote-control --permission-mode acceptEdits
    ```
  </Tab>
</Tabs>

<h2 id="auto-approve-file-edits-with-acceptedits-mode">
  acceptEdits モードでファイル編集を自動承認する
</h2>

`acceptEdits` モードでは Claude はプロンプトなしに作業ディレクトリ内のファイルを作成および編集できます。このモードがアクティブな間、ステータスバーは `⏵⏵ accept edits on` を表示します。

ファイル編集に加えて、`acceptEdits` モードは一般的なファイルシステム Bash コマンドを自動承認します。`mkdir`、`touch`、`rm`、`rmdir`、`mv`、`cp`、`sed`。これらのコマンドは `LANG=C` または `NO_COLOR=1` のような安全な環境変数、または `timeout`、`nice`、`nohup` のようなプロセスラッパーでプレフィックスされた場合にも自動承認されます。ファイル編集と同様に、自動承認は作業ディレクトリまたは `additionalDirectories` 内のパスにのみ適用されます。そのスコープ外のパス、[保護されたパス](#protected-paths)への書き込み、その他すべての Bash コマンド（[読み取り専用コマンド](/docs/ja/permissions#read-only-commands)の組み込みセットを除く）はまだプロンプトが表示されます。

[PowerShell ツール](/docs/ja/tools-reference#powershell-tool)が有効な場合、`acceptEdits` モードはスコープ内のパスに対して `Set-Content`、`Add-Content`、`Clear-Content`、`Remove-Item` も自動承認し、それらの一般的なエイリアスも承認します。同じスコープと保護されたパスのルールが適用されます。

事実後にエディターまたは `git diff` 経由で変更をレビューしたい場合、各編集をインラインで承認するのではなく `acceptEdits` を使用します。Manual モードから `Shift+Tab` を 1 回押して入るか、直接開始します。

```bash theme={null}
claude --permission-mode acceptEdits
```

<h2 id="analyze-before-you-edit-with-plan-mode">
  計画モードで編集前に分析する
</h2>

計画モードは Claude に変更を加えずに調査と提案を行うよう指示します。Claude はファイルを読み、シェルコマンドを実行して探索し、計画を書きますが、ソースを編集しません。権限プロンプトはマニュアルモードと同じように適用されます。ただし、[自動モード](/docs/ja/auto-mode-config)が利用可能で `useAutoModeDuringPlan` がオンになっている場合（デフォルト）は除きます。自動モードがアクティブな場合、分類器は検索やファイル読み取りなどの読み取り専用コマンドをプロンプトなしで承認します。どちらの場合でも、編集は計画を承認するまでブロックされたままです。

`Shift+Tab` を押すか、単一のプロンプトに `/plan` をプレフィックスして計画モードに入ります。CLI から計画モードで開始することもできます。

```bash theme={null}
claude --permission-mode plan
```

計画モードを終了するには `Shift+Tab` を再度押し、計画を承認しません。

<h3 id="review-and-approve-a-plan">
  計画をレビューして承認する
</h3>

計画の準備ができたら、Claude はそれを提示し、どのように進めるかを尋ねます。そのプロンプトから以下を実行できます。

* 承認して自動モードで開始
* 承認して編集を受け入れる
* 承認して各編集を手動でレビュー
* フィードバック付きで計画を続ける
* [Ultraplan](/docs/ja/ultraplan) でブラウザベースのレビュー用に改善

計画を承認すると、計画モードを終了し、セッションを各承認オプションが説明する権限モードに切り替えるため、Claude は編集を開始します。再度計画するには、`Shift+Tab` で計画モードに戻るか、次のプロンプトに `/plan` をプレフィックスしてください。

`Ctrl+G` を押して、提案された計画をデフォルトのテキストエディタで開き、Claude が進める前に直接編集できます。[`showClearContextOnPlanAccept`](/docs/ja/settings#available-settings) が有効な場合、各承認オプションは計画コンテキストを最初にクリアするオプションも提供します。

計画を受け入れると、`--name` または `/rename` で既に名前を設定していない限り、計画コンテンツからセッションに自動的に名前が付けられます。

<h3 id="set-plan-mode-as-the-default">
  計画モードをデフォルトとして設定する
</h3>

プロジェクトのデフォルトとして計画モードを設定するには、`.claude/settings.json` で `defaultMode` を設定します。

```json theme={null}
{
  "permissions": {
    "defaultMode": "plan"
  }
}
```

<h2 id="eliminate-prompts-with-auto-mode">
  自動モードで権限プロンプトをなくす
</h2>

自動モードでは Claude はルーチンの権限プロンプトなしで実行できます。別の分類器モデルはアクション実行前にアクションをレビューし、リクエストを超えてエスカレートするもの、認識されないインフラストラクチャをターゲットにするもの、または Claude が読んだ敵対的なコンテンツによって駆動されているように見えるものをブロックします。明示的な [ask ルール](/docs/ja/permissions#manage-permissions) は依然としてプロンプトを強制します。

ファイルシステムルートまたはホームディレクトリをターゲットにした削除（`rm -rf /` や `rm -rf ~` など）は、分類器に送られるのではなく、承認を求めるプロンプトを表示します。このプロンプトはまた、コマンドが `$(...)` または バッククォートを使用したコマンド置換、または `<(...)` を使用したプロセス置換を含む場合にも発火します。削除が `echo "$(rm -rf ~)"` のように置換内にある場合でも、コマンド内の他の場所にある場合でも同様です。v2.1.208 より前では、これらの形式を含むコマンドは分類器に送られていました。

自動モードはまた Claude に明確化の質問を停止せずに作業を続けるよう促します。ただし、Claude はプロンプトまたはスキルが明示的にそれに依存する場合は依然として質問します。権限プロンプトを保持しながらより強い自律的な動作を取得するには、代わりに [プロアクティブ出力スタイル](/docs/ja/output-styles) を設定してください。

<Warning>
  自動モードは権限プロンプトを減らしますが、安全性を保証しません。一般的な方向を信頼するタスクに使用し、機密操作のレビューの代わりとしては使用しないでください。
</Warning>

自動モードはアカウントがこれらすべての要件を満たす場合にのみ利用可能です。

* **プラン**：すべてのプラン。
* **所有者**：Team と Enterprise では、所有者がユーザーがオンにできるようにする前に [Claude Code 管理設定](https://claude.ai/admin-settings/claude-code) で有効にする必要があります。管理者は [管理設定](/docs/ja/permissions#managed-settings) で `permissions.disableAutoMode` を `"disable"` に設定することでロックオフすることもできます。デスクトップアプリの Code タブの場合、`disableAutoMode` は組織レベルの制御であり、管理設定トグルは適用されません。
* **モデル**：Anthropic API では Claude Opus 4.6 以降、または Sonnet 4.6 以降。Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、および署名済み [Claude apps gateway](/docs/ja/claude-apps-gateway) セッションでは、Claude Sonnet 5、Opus 4.7、および Opus 4.8 のみ。Sonnet 4.5、Opus 4.5、Haiku、claude-3 モデルを含む古いモデルはどのプロバイダーでもサポートされていません。
* **プロバイダー**：Anthropic API ではデフォルトで利用可能です。Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、および署名済み Claude apps gateway セッションでは、デフォルトで利用可能です。v2.1.158 から v2.1.206 では、自動モードは Anthropic API を除くこれらすべてのプロバイダーでオフでした。`CLAUDE_CODE_ENABLE_AUTO_MODE=1` を設定するまで。v2.1.207 は要件を削除しました。

Claude Code が自動モードを利用不可と報告する場合、これらの要件のいずれかが満たされていません。これは一時的な停止ではありません。モデルに名前を付けて自動モードが「アクションの安全性を判断できない」と言う別のメッセージは一時的な分類器停止です。[エラーリファレンス](/docs/ja/errors#auto-mode-cannot-determine-the-safety-of-an-action) を参照してください。

[設定](/docs/ja/settings#available-settings) で `defaultMode: "auto"` を設定し、セッションがエラーなしで `default` モードで開始する場合、設定は `.claude/settings.json` または `.claude/settings.local.json` にある可能性があります。Claude Code v2.1.142 以降はこれらのファイルから `auto` を無視するため、リポジトリは自動モードを自身に付与することはできません。`~/.claude/settings.json` に移動してください。

<h3 id="enable-auto-mode-on-bedrock-agent-platform-or-foundry">
  Bedrock、Agent Platform、または Foundry で自動モードを有効にする
</h3>

[Amazon Bedrock](/docs/ja/amazon-bedrock)、[Google Cloud の Agent Platform](/docs/ja/google-vertex-ai)、[Microsoft Foundry](/docs/ja/microsoft-foundry)、および署名済み [Claude apps gateway](/docs/ja/claude-apps-gateway) セッションでは、自動モードはデフォルトで `Shift+Tab` サイクルに表示されます。サイクルに表示されることはセッションが開始するモードを変更しません。セッションは依然として [`defaultMode`](/docs/ja/settings#available-settings) で開始します。これは変更しない限り Manual です。これらのプロバイダーでは Claude Sonnet 5、Opus 4.7、および Opus 4.8 のみがサポートされています。

自動モードをデフォルトの開始モードにするには、ユーザーまたは管理設定で `"permissions": {"defaultMode": "auto"}` を設定します。

開発者が自動モードを使用するのを防ぐには、[管理設定](/docs/ja/permissions#managed-settings) で `disableAutoMode` を `"disable"` に設定します。これは `auto` を `Shift+Tab` サイクルから削除し、起動時に `--permission-mode auto` を拒否します。

v2.1.158 から v2.1.206 では、自動モードはこれらのプロバイダーでオフでした。`CLAUDE_CODE_ENABLE_AUTO_MODE=1` を設定するまで。Claude Code はこれらのプロバイダーで `defaultMode: "auto"` を無視していました。変数も設定されていない限り。変数は互換性のために依然として受け入れられ、v2.1.207 以降は効果がありません。

<h3 id="what-the-classifier-blocks-by-default">
  分類器がデフォルトでブロックするもの
</h3>

分類器は作業ディレクトリとセッション開始時に設定されたリモートを信頼します。セッション中に `git remote add` または `git remote set-url` で追加またはリポイントされたリモートは信頼されず、[信頼できるインフラストラクチャを設定](/docs/ja/auto-mode-config) するまで他のすべては外部として扱われます。v2.1.200 より前では、セッション中に追加されたリモートも信頼されていました。

**デフォルトでブロック**：

* `curl | bash` のようなコードのダウンロードと実行
* 機密データを外部エンドポイントに送信
* 本番環境へのデプロイとマイグレーション
* クラウドストレージでの大量削除
* IAM またはリポジトリ権限の付与
* 共有インフラストラクチャの変更
* セッション前に存在していたファイルを不可逆的に破壊
* フォースプッシュ
* リポジトリのデフォルトブランチへのプッシュ。プッシュがシークレットや個人情報または信頼されたデータなどの機密コンテンツを含む場合、変更があなたが求めたものに対して隠蔽または誤表示されている場合、コンテンツがリポジトリ外からポートインまたは最初に読み込まれた場合、またはあなたが求めたプルリクエスト、レビュー、またはチェックの周りをルーティングする場合。デフォルトブランチへのプレーンプッシュはそれ自体ではブロックされず、フラグが立てられたプッシュをクリアするにはプッシュだけではなく、フラグが立てられたコンテンツまたはバイパスされたレビューに名前を付ける必要があります。分類器は 1 つのレイヤーです。[`permissions.deny` ルール](/docs/ja/permissions#manage-permissions) はすべてのモードで適用され、デフォルトブランチへのプッシュを完全にブロックでき、リモート独自のブランチ保護は依然として適用されます。v2.1.203 より前では、デフォルトブランチへの直接プッシュはすべてブロックされていました
* `git reset --hard`、`git checkout -- .`、`git restore .`、`git clean -fd`、`git stash drop`、または `git stash clear`。分類器はこれらがコミットされていない変更を破棄すると推定します
* `git commit --amend`。HEAD のコミットがこのセッションで作成されていない場合
* v2.1.198 から、`git commit --amend`。HEAD のコミットが既にプッシュされている場合。メッセージのみの言い換えはブロックされません。`--amend -m` で新たにステージされたものがなく、Claude がこのセッション中に作成したコミット上
* `terraform destroy`、`pulumi destroy`、`cdk destroy`、または `terragrunt destroy`。リソースを破壊するプランを適用する場合

Claude Code v2.1.195 以降はデフォルトでより多くのカテゴリをブロックします。いくつかは [環境](/docs/ja/auto-mode-config#define-trusted-infrastructure) エントリに依存します。例えば、機密リモートターゲットと保護された IaC スコープなど。これらを具体的な名前に絞ることができます。

* シークレットマネージャーへの書き込み、または DNS レコードまたは TLS 証明書の変更
* 人間が承認していないプルリクエストのマージ、Claude 独自のプルリクエストの承認、または CI チェックの無効化
* それ自体がオートメーションへのコマンドであるコメントの投稿。例えば `atlantis apply` またはボットの `/deploy` または `/merge`
* 本番環境機能フラグの切り替え、ランプアップ、または削除
* 保護された IaC スコープへのインフラストラクチャ変更の適用、またはクラスタノードのドレインと削除
* ラベルセレクターまたは `--all` のような、他のユーザーのジョブをキャッチする共有コンピュートクラスタへの書き込み
* すべてのノードで実行されるか、クラスタトラフィックをインターセプトする Kubernetes リソースの作成。例えば DaemonSets と admission webhooks
* 機密リモートターゲットへのインタラクティブシェルまたはポートフォワード
* ローカルサービスをパブリックインターネットから到達可能にするトンネルまたはリバースシェルの開設
* トランスクリプトまたはファイルへのライブ認証情報またはトークンの印刷
* [環境](/docs/ja/auto-mode-config#define-trusted-infrastructure) で機密データロケーションとしてリストされている場所へのアクセス、またはそこからのデータのコピー。v2.1.198 以降、これはエントリが除外する対象者にそこからデータを送信することもブロックします
* パッケージインストールを内部パッケージレジストリの周りからパブリックレジストリにルーティング。v2.1.198 以降、これは会話で Claude に内部レジストリまたはミラーが存在することを伝えた場合にも適用されます。環境にリストされている場合だけではなく
* `--insecure` のようなセーフティガードを解除するフラグを使用したコマンドの実行
* `--dangerously-skip-permissions` または `--no-sandbox` で開始されたものなど、人間の承認またはサンドボックスなしで実行される自律エージェントループの起動。v2.1.198 以降、これは `--yes-always` で開始されたランナーなど、分離とアクションごとの承認を無効にして実行される第三者エージェントまたは eval ハーネスもカバーします
* [Claude in Chrome](/docs/ja/chrome) ブラウザアクション。ページコンテンツ、クッキー、または認証情報をオリジン外に送信する可能性があります

Claude Code v2.1.198 以降はこれらもデフォルトでブロックします。

* `/tmp`、`$TMPDIR`、または別の共有スクラッチまたはキャッシュディレクトリ内のファイルを、特定の名前付きパスではなく、ワイルドカード、glob、または年齢フィルターで削除
* 自身のメッセージがその受信者にそれらの詳細を認可しなかった場合、送信、アップロード、公開、または他の人または共有システムに書き込まれるコンテンツに機密詳細を含める。PR およびイシュー本文、コミットメッセージ、およびコメントは、リポジトリが信頼境界外またはパブリックである場合、この種の送信コンテンツとしてカウントされます。組織独自のパブリックリポジトリを含む。内部ファイルパス、コード名、メールやアカウント識別子などのライブ API レスポンスデータ、およびインフラストラクチャ識別子は機密詳細としてカウントされます。PR、イシュー、およびコミットメッセージのスコープには Claude Code v2.1.200 以降が必要です。PR またはイシュー本文内のメールアドレス、アカウントまたは組織識別子、または使用メトリックなどのライブ個人データは、リポジトリの可視性または信頼境界に関係なく、それらの詳細と受信者に名前を付ける必要があります。そのチェックには Claude Code v2.1.203 以降が必要です
* Claude Code 独自の tmux ペインにキーストロークを送信して独自のインターフェースを駆動。分類器はこれを Claude が独自の権限または監視を変更することとして扱います

Claude Code v2.1.200 以降はこれらもデフォルトでブロックします。

* セキュリティ動作を保護するテストまたはアサーションをコメントアウト、削除、または強制パス。例えば認証、アクセス制御、入力検証、またはサンドボックス
* Claude がセッションで作成しなかった状態リソースの削除またはティアダウン。より具体的な削除ルールが適用されず、リソースに名前を付けなかった場合
* API ベース URL、プロキシエンドポイント、webhook レシーバー、またはレジストリミラーを、タスクに適さない第三者ホストにリポイント。`.env.example` のようなサンプルファイルを含む
* `git remote set-url` または `git remote add` でプッシュ先を変更。新しいリモートに名前を付けた場合を除く
* パブリックであることが知られているリポジトリにシークレットをプッシュ、またはそのリポジトリ独自の作業の一部ではない他の機密または機密材料をプッシュ。ドットファイルリポジトリ独自の主題は個人情報または信頼されたデータの唯一の例外であり、プライベートリポジトリからのコンテンツがパブリックサーフェスに到達することは同じ方法でブロックされます。両方の改善には Claude Code v2.1.203 以降が必要です。v2.1.203 より前では、個人データは機密材料とグループ化され、そのリポジトリ独自の作業の一部ではない場合にのみブロックされていました。リポジトリの可視性が確立されていない場合、分類器はそれだけではブロックしません。代わりに他のルールに対してコンテンツを判断します
* 異なるリポジトリまたは組織に対するプルリクエストを開く、`gh repo fork` でフォーク、または第三者リポジトリにプッシュ。外部ターゲットに名前を付けた場合を除く

Claude Code v2.1.203 以降はこれらもデフォルトでブロックします。

* 機密ローカルストアからのコンテンツ、またはファイル名、パス、またはタイプが機密としてマークしているファイルからのコンテンツ。コミット、プッシュ、PR またはイシューテキスト、gist またはペースト、またはパッケージ公開に入る。ソースと宛先の両方に名前を付けない限り。セッショントランスクリプトと会話ログ、SSH キー、クラウド認証情報、ブラウザプロファイル、シェル履歴などの認証情報と設定ドットフォルダ、およびユーザーデータエクスポートはすべてカウントされ、リポジトリがプライベートであることはそれをクリアしません

Claude Code v2.1.205 以降はこれらもデフォルトでブロックします。

* Claude Code セッショントランスクリプト、`~/.claude/projects/` の `.jsonl` 履歴ファイル、または設定ディレクトリへの書き込み。直接またはシェルコマンドを通じて。ルールはまた Claude Code が独自のチェック用に各トランスクリプトエントリに追加するメタデータ行もカバーします。トランスクリプトは Claude Code が書き込むセッション状態であり、作業ファイルではなく、改ざんされたエントリはセッションを再開すると後のすべてのチェックに到達するため、自動モードは防御の深さとしてこれらの書き込みをブロックします。トランスクリプトの読み取りはブロックされません
* `rm -rf "$VAR"` または `Remove-Item -Recurse -Force $dir` のような再帰的な強制削除。ターゲットがシェル変数である場合、または分類器が見る会話のどこにも割り当てられていない変数に根ざしている glob。値は以前のコマンド出力からのみ来ており、分類器は決してコマンド出力を受け取らないため、分類器は削除ターゲットを他の削除ルールに対して検証できません。分類器は設計上、コマンド出力ではなく会話を読むため、推測する代わりにコールをブロックします。ブロックは削除されている正確なパスに名前を付けるか、Claude が削除をコマンドに書き込まれた解決済みリテラルパスで再実行するときにクリアされます。分類器が解決できるターゲットを持つ削除は影響を受けません

**デフォルトで許可**：

* 作業ディレクトリ内のローカルファイル操作
* ロックファイルまたはマニフェストで宣言されている依存関係のインストール
* `.env` を読み取り、認証情報を一致する API に送信
* 読み取り専用 HTTP リクエスト
* 開始したブランチまたは Claude が作成したブランチへのプッシュ
* リポジトリデフォルトブランチへのルーチンプッシュ。v2.1.203 より前では、デフォルトブランチへの直接プッシュはすべてブロックされていました

Claude Code v2.1.195 以降はデフォルトでこれらも許可します。

* Claude が同じセッション内で以前に作成した正確なジョブの削除
* タスクの一部として、セキュリティ関連のコード、設定、脅威モデルの読み取り、レビュー、または書き込み
* 同じマルチエージェントセッションで連携しているエージェント間のメッセージ
* [`environment`](/docs/ja/auto-mode-config#define-trusted-infrastructure) にリストされている信頼できるドメイン、バケット、サービスへのデータ送信。これはデータフローのみをカバーし、同じインフラストラクチャ上の破壊的または認証情報操作ではありません
* [Claude in Chrome](/docs/ja/chrome) の信頼できる内部ドメイン、localhost、または名前を付けた URL へのナビゲーション

サンドボックスネットワークアクセスリクエストはデフォルトで許可されるのではなく、分類器を通じてルーティングされます。v2.1.198 以降、分類器はネットワークホストとポートの判定を再利用し、接続のたびに再実行するのではなく。

* 許可は新しいコンテンツが会話に入るまで再利用され、その時点でそのホストが再度チェックされます
* インタラクティブ CLI では、拒否はターンが終了するときにドロップされます
* [非対話的モード](/docs/ja/headless) と Agent SDK セッションではターン境界がないため、拒否はランの残りの間再利用されます
* 権限モードまたはルールを変更すると、すべてのキャッシュされた判定がドロップされます

`claude auto-mode defaults` を実行して完全なルールリストを確認してください。日常的なアクションがブロックされている場合、管理者は `autoMode.environment` 設定を通じて信頼できるリポジトリ、バケット、サービスを追加できます。[自動モードを設定](/docs/ja/auto-mode-config) を参照してください。

作業ブランチへのプッシュ、リポジトリデフォルトブランチへのルーチンプッシュ、およびリクエストに一致するプルリクエストの作成はすべてプロンプトなしで実行されます。分類器はフォースプッシュやあなたが設定したレビューの周りをルーティングするコンテンツなど、リスクを伴うプッシュのみをブロックします。自動モードにとどまりながらこれらのアクション前に人間のチェックポイントを要求するには、`permissions.ask` ルールを追加します。[一般的な境界](/docs/ja/auto-mode-config#common-boundaries) を参照してください。

<h3 id="boundaries-you-state-in-conversation">
  会話で述べる境界
</h3>

分類器は会話で述べる境界をブロック信号として扱います。Claude に「プッシュしないで」または「デプロイ前にレビューを待って」と言う場合、分類器はデフォルトルールが許可する場合でも一致するアクションをブロックします。境界は後のメッセージで解除するまで有効です。Claude 独自の判断が条件が満たされたことは解除しません。

境界はルールとして保存されません。分類器はチェックのたびにトランスクリプトから再読み込みするため、[コンテキストコンパクション](/docs/ja/costs#reduce-token-usage) が述べたメッセージを削除する場合、境界は失われる可能性があります。ハード保証の場合、代わりに [deny ルール](/docs/ja/permissions#permission-rule-syntax) を追加します。

<h3 id="when-auto-mode-falls-back">
  自動モードがフォールバックする場合
</h3>

拒否されたアクションはそれぞれ通知を表示し、`/permissions` の Recently denied タブに表示されます。そこで `r` を押して手動承認で再試行できます。

分類器がアクション 3 回連続でブロックするか、合計 20 回ブロックする場合、自動モードは一時停止し、Claude Code はプロンプトを再開します。プロンプトされたアクションを承認すると自動モードが再開されます。これらのしきい値は設定不可です。許可されたアクションは連続カウンターをリセットし、合計カウンターはセッション中に保持され、独自の制限がフォールバックをトリガーする場合にのみリセットされます。

[非対話的モード](/docs/ja/headless) で `-p` フラグを使用する場合、プロンプトするユーザーがいないため、繰り返されるブロックはセッションを中止します。

繰り返されるブロックは通常、分類器がインフラストラクチャについてのコンテキストが不足していることを意味します。`/feedback` を使用して誤検知を報告するか、管理者に [信頼できるインフラストラクチャを設定](/docs/ja/auto-mode-config) するよう依頼してください。

<AccordionGroup>
  <Accordion title="分類器がアクションを評価する方法">
    各アクションは固定の決定順序を通過します。最初に一致するステップが勝ちます。

    1. [allow、ask、または deny ルール](/docs/ja/permissions#manage-permissions) に一致するアクションは即座に解決されます。ただし、[保護されたパス](#protected-paths) への書き込みは、allow ルールが一致する場合でも分類器にルーティングされます。[組織が `ask` に設定した](/docs/ja/mcp#organization-controls-on-connector-tools) コネクターツールと [`requiresUserInteraction`](/docs/ja/mcp#require-approval-for-a-specific-tool) でマークされた MCP ツールは、allow ルールが一致する場合でも直接プロンプトを表示します。コンテンツスコープの ask ルールは権限プロンプトにフォールバックします
    2. 読み取り専用アクションと作業ディレクトリ内のファイル編集は自動承認されます。[保護されたパス](#protected-paths) への書き込みを除く
    3. その他すべては分類器に送られます。コネクターツール [組織が `ask` に設定した](/docs/ja/mcp#organization-controls-on-connector-tools) は分類器をスキップし、直接プロンプトを表示するため、組織が必要とする承認は決して自動承認されません。v2.1.199 以降、[`_meta["anthropic/requiresUserInteraction"]`](/docs/ja/mcp#require-approval-for-a-specific-tool) でマークされた MCP ツールも分類器をスキップし、直接プロンプトを表示するため、同意ステップはツール作成者の代わりに自動承認されることはありません
    4. 分類器がブロックする場合、Claude は理由を受け取り、別のアプローチを試みます

    自動モードに入ると、任意のコード実行を許可する広いルールが削除されます。

    * ブランケット `Bash(*)` または `PowerShell(*)`
    * `Bash(python*)` のようなワイルドカードインタープリター
    * パッケージマネージャー実行コマンド
    * `Agent` allow ルール

    `Bash(npm test)` のような狭いルールは引き継がれます。削除されたルールは自動モードを終了するときに復元されます。

    分類器はユーザーメッセージ、ツール呼び出し、CLAUDE.md コンテンツを見ます。ツール結果は削除されるため、ファイルまたは Web ページの敵対的なコンテンツはそれを直接操作することはできません。サーバー側プローブは受信ツール結果をスキャンし、Claude がそれを読む前に疑わしいコンテンツにフラグを立てます。これらのレイヤーがどのように連携するかについての詳細については、[自動モードのお知らせ](https://claude.com/blog/auto-mode) および [エンジニアリング深掘り](https://www.anthropic.com/engineering/claude-code-auto-mode) を参照してください。
  </Accordion>

  <Accordion title="自動モードがサブエージェントを処理する方法">
    分類器は [サブエージェント](/docs/ja/sub-agents) の作業を 3 つのポイントでチェックします。

    1. サブエージェント開始前に、委譲されたタスク説明が評価されるため、危険に見えるタスクは生成時にブロックされます。
    2. サブエージェント実行中、その各アクションは親セッションと同じルールで分類器を通過し、サブエージェントのフロントマターの任意の `permissionMode` は無視されます。
    3. サブエージェント完了時、分類器はその完全なアクション履歴をレビューします。リターンチェックが懸念事項にフラグを立てた場合、セキュリティ警告がサブエージェントの結果の前に付加されます。

    ステップ 1 には Claude Code v2.1.178 以降が必要です。以前のバージョンはステップ 2 と 3 で分類器を適用しましたが、サブエージェント開始前にタスク説明を評価しませんでした。
  </Accordion>

  <Accordion title="コストとレイテンシ">
    分類器は `/model` 選択から独立したサーバー設定モデルで実行されるため、モデルの切り替えは分類器の可用性を変更しません。分類器呼び出しはトークン使用量にカウントされます。各チェックはトランスクリプトの一部と保留中のアクションを送信し、実行前にラウンドトリップを追加します。保護されたパス外の読み取りと作業ディレクトリ編集は分類器をスキップするため、オーバーヘッドは主にシェルコマンドとネットワーク操作から発生します。v2.1.198 以降、サンドボックスネットワーク判定はホストとポートに対して再利用され、接続のたびに再分類されるのではなく、繰り返される接続は同じホストへのチェックを追加しません。[分類器がデフォルトでブロックするもの](#what-the-classifier-blocks-by-default) は許可と拒否がどのくらい続くかを説明しています。
  </Accordion>
</AccordionGroup>

<h2 id="allow-only-pre-approved-tools-with-dontask-mode">
  dontAsk モードで事前承認済みツールのみを許可する
</h2>

`dontAsk` モードを設定すると、Claude Code はプロンプトが表示されるすべてのツール呼び出しを自動的に拒否します。Claude は `permissions.allow` ルール、[読み取り専用 Bash コマンド](/docs/ja/permissions#read-only-commands)、および [PreToolUse フック](/docs/ja/permissions#extend-permissions-with-hooks)によって承認された呼び出しに一致するアクションのみを実行します。このモードは CI パイプラインまたは Claude が実行を許可されているものを事前に定義する制限環境で使用します。セッションは入力を待つことはありません。このモードがアクティブな間、ステータスバーに `⏵⏵ don't ask on` が表示されます。

Claude Code は明示的な [`ask` ルール](/docs/ja/permissions#manage-permissions)に一致するプロンプトするのではなく呼び出しを拒否します。また、組み込みの `AskUserQuestion` ツールと [組織が `ask` に設定したコネクタツール](/docs/ja/mcp#organization-controls-on-connector-tools)も拒否します。これは allow ルールが一致する場合でも同じです。[`_meta["anthropic/requiresUserInteraction"]`](/docs/ja/mcp#require-approval-for-a-specific-tool)でマークされた MCP ツールも同じ方法で拒否されます。これは、その承認カードがこのモードが収集することのない回答を必要とするためです。これには Claude Code v2.1.199 以降が必要です。

[Claude Code on the web](/docs/ja/claude-code-on-the-web)上のクラウドセッションは `defaultMode: "dontAsk"` を無視します。詳細は [bypassPermissions](#skip-all-checks-with-bypasspermissions-mode)を参照してください。

フラグで起動時に設定します。

```bash theme={null}
claude --permission-mode dontAsk
```

<h2 id="skip-all-checks-with-bypasspermissions-mode">
  bypassPermissions モードですべてのチェックをスキップする
</h2>

`bypassPermissions` モードは権限プロンプトと安全チェックを無効にするため、ツール呼び出しは即座に実行されます。これには[保護されたパス](#protected-paths)への書き込みが含まれます。v2.1.126 より前のバージョンでは、保護されたパスへの書き込みはこのモードでもプロンプトが表示されていました。

明示的な[ask ルール](/docs/ja/permissions#manage-permissions)と、コネクタツール[組織が `ask` に設定したもの](/docs/ja/mcp#organization-controls-on-connector-tools)はこのモードでもプロンプトを強制します。[`_meta["anthropic/requiresUserInteraction"]`](/docs/ja/mcp#require-approval-for-a-specific-tool)でマークされた MCP ツールもプロンプトが表示されます。これには Claude Code v2.1.199 以降が必要です。

ファイルシステムのルートまたはホームディレクトリを対象とした削除（`rm -rf /` や `rm -rf ~` など）は、モデルエラーに対する回路遮断器として機能するため、引き続きプロンプトが表示されます。回路遮断器は、コマンドに `$(...)` またはバッククォートを含むコマンド置換、または `<(...)` を含むプロセス置換が含まれている場合にも発動します。削除が置換内にある場合（`echo "$(rm -rf ~)"` など）でも、同じコマンド内の他の場所にある場合でも発動します。プレーンな形式（独立したコマンドとして入力された場合）は、回路遮断器が導入されて以来このモードでプロンプトが表示されていました。v2.1.208 より前のバージョンでは、これらの形式を含むコマンドはプロンプトが表示されていませんでした。

<Warning>
  このモードは、Claude Code がホストシステムに損害を与えることができないコンテナ、VM、またはインターネットアクセスのない dev container のような隔離環境でのみ使用してください。
</Warning>

有効にするフラグの 1 つで開始したセッションから `bypassPermissions` に入ることはできません。有効にするために再起動してください。

```bash theme={null}
claude --permission-mode bypassPermissions
```

`--dangerously-skip-permissions` フラグは同等です。

Linux と macOS では、Claude Code はこのモードで root として実行されている場合、または `sudo` の下で実行されている場合、起動を拒否します。

```text theme={null}
--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons
```

チェックは認識されたサンドボックス内で自動的にスキップされます。コンテナで自律的に実行するには、[dev container](/docs/ja/devcontainer) 設定を使用してください。これは Claude Code を非 root ユーザーとして実行します。

[Web 上の Claude Code](/docs/ja/claude-code-on-the-web) は設定ファイルの `defaultMode: "bypassPermissions"` または `"dontAsk"` を尊重しないため、リポジトリのチェックイン済み設定はクラウドセッションを bypass-permissions モードで開始することはできません。この設定は無視され、セッションはモードドロップダウンに表示されるモードで開始されます。クラウドセッションが提供するモードについては、[権限モードを切り替える](#switch-permission-modes)を参照してください。

<Warning>
  `bypassPermissions` はプロンプトインジェクションまたは意図しないアクションに対する保護を提供しません。権限プロンプトが大幅に少ないバックグラウンド安全チェックの場合は、代わりに[自動モード](#eliminate-prompts-with-auto-mode)を使用してください。管理者は[管理設定](/docs/ja/permissions#managed-settings)で `permissions.disableBypassPermissionsMode` を `"disable"` に設定することでこのモードをブロックできます。
</Warning>

<h2 id="protected-paths">
  保護されたパス
</h2>

パスの小さなセットへの書き込みは、`bypassPermissions` を除くすべてのモードで自動承認されることはありません。これはリポジトリ状態と Claude 独自の設定の偶発的な破損を防ぎます。

| モード                            | 保護されたパスへの書き込み |
| :----------------------------- | :------------ |
| `default`、`acceptEdits`、`plan` | プロンプト表示       |
| `auto`                         | 分類器にルーティング    |
| `dontAsk`                      | 拒否            |
| `bypassPermissions`            | 許可            |

[`permissions.allow`](/docs/ja/permissions#manage-permissions) 設定ファイルのルールは、保護されたパスへの書き込みを事前承認しません。安全性チェックは Claude Code が設定から allow ルールを評価する前に実行されるため、`~/.claude/settings.json` または `.claude/settings.json` の `Edit(.claude/**)` などのエントリは、上記の表のモード別の結果を変更しません。プロンプトを表示するモードでは、`.claude/` への書き込みのプロンプトに **Yes, and allow Claude to edit its own settings for this session** というオプションが表示され、そのセッション内の後続の `.claude/` への書き込みを再度プロンプトなしで承認します。

保護されたディレクトリ：

* `.git`
* `.config/git`
* `.vscode`
* `.idea`
* `.husky`
* `.cargo`
* `.devcontainer`
* `.yarn`
* `.mvn`
* `.claude`。ただし `.claude/worktrees` は除く。Claude はここに独自の git worktrees を保存します

保護されたファイル：

* `.gitconfig`、`.gitmodules`
* `.bashrc`、`.bash_profile`、`.bash_login`、`.bash_aliases`、`.bash_logout`、`.zshrc`、`.zprofile`、`.zshenv`、`.zlogin`、`.zlogout`、`.profile`、`.envrc`
* `.npmrc`、`.yarnrc`、`.yarnrc.yml`、`.pnp.cjs`、`.pnp.loader.mjs`、`.pnpmfile.cjs`、`bunfig.toml`、`.bunfig.toml`
* `.bazelrc`、`.bazelversion`、`.bazeliskrc`
* `.pre-commit-config.yaml`、`lefthook.yml`、`lefthook.yaml`、`.lefthook.yml`、`.lefthook.yaml`
* `gradle-wrapper.properties`、`maven-wrapper.properties`
* `.devcontainer.json`
* `.ripgreprc`、`pyrightconfig.json`
* `.mcp.json`、`.claude.json`

<h2 id="see-also">
  関連項目
</h2>

* [Permissions](/docs/ja/permissions)：allow、ask、deny ルール。管理ポリシー
* [Configure auto mode](/docs/ja/auto-mode-config)：分類器に組織が信頼するインフラストラクチャを伝える
* [Hooks](/docs/ja/hooks)：`PreToolUse` および `PermissionRequest` フック経由のカスタム権限ロジック
* [Ultraplan](/docs/ja/ultraplan)：ブラウザベースのレビュー付き Claude Code on the web セッションで計画モードを実行
* [Security](/docs/ja/security)：セキュリティ保護とベストプラクティス
* [Sandboxing](/docs/ja/sandboxing)：Bash コマンドのファイルシステムとネットワーク隔離
* [Non-interactive mode](/docs/ja/headless)：`-p` フラグで Claude Code を実行
