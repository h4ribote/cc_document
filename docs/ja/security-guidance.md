> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude がコードを書く際のセキュリティ問題をキャッチする

> security-guidance プラグインをインストールして、Claude が自身のコード変更の脆弱性をレビューし、同じセッション内で修正するようにします。

security guidance プラグインは、Claude が作業中に自身のコード変更を一般的な脆弱性についてレビューし、同じセッション内で見つかった問題を修正します。このプラグインは、インジェクション、安全でないデシリアライゼーション、安全でない DOM API などの問題をコードがプルリクエストに到達する前にキャッチし、下流の人間レビュアーが行うセキュリティレビューの量を削減します。

インストール後、プラグインは自動的に実行されます。呼び出すものはなく、覚えておく必要のある個別のコマンドもありません。

このプラグインは、プルリクエストで実行される [Code Review](/docs/ja/code-review) のセッション内コンパニオンです。このプラグインは PR に到達するものを削減します。Code Review はそれをキャッチします。プラグインがオンデマンドレビューと CI スキャンとどのように層状になるかについては、[これが他のセキュリティツールとどのように適合するか](#how-this-fits-with-other-security-tools) を参照してください。

<h2 id="prerequisites">
  前提条件
</h2>

* Claude Code CLI バージョン 2.1.144 以降
* `PATH` 上の Python 3.8 以降。プラグインは `python3`、`python`、`py -3` をこの順序で試します
* 作業するディレクトリ用の git リポジトリ。ターン終了とコミットレビューは git 状態に対して diff を行い、リポジトリ外では無音でスキップします。編集ごとのパターンチェックはどこでも機能します

初回実行時、プラグインは `~/.claude/security/` の下に仮想環境を作成し、Claude Agent SDK をインストールします。これには `pip` とネットワークアクセスが必要です。そのインストールが失敗した場合、コミットレビューは agentic なものではなく、単一ショットレビューにフォールバックします。Windows では仮想環境ステップはスキップされるため、agentic コミットレビューは `claude-agent-sdk` が既にインポート可能な場合にのみ実行され、そうでない場合は同じようにフォールバックします。

<h2 id="install-the-plugin">
  プラグインをインストールする
</h2>

Claude Code セッションで、[公式 Anthropic マーケットプレイス](/docs/ja/discover-plugins#official-anthropic-marketplace) からインストールします：

```text theme={null}
/plugin install security-guidance@claude-plugins-official
```

インストールはスコープを求めます。ユーザースコープを選択して、プラグインをユーザー設定に書き込み、このマシンで開始するすべての新しいローカルセッションで読み込まれるようにします。Claude Code がマーケットプレイスが見つからないと報告した場合、まず `/plugin marketplace add anthropics/claude-plugins-official` を実行してから、インストールを再試行してください。

次に、現在のセッションで `/reload-plugins` を使用して有効化します。これはプラグインの変更を再起動なしで適用します：

```text theme={null}
/reload-plugins
```

<h3 id="enable-in-cloud-sessions-and-shared-repositories">
  クラウドセッションと共有リポジトリで有効化する
</h3>

ユーザースコープのプラグインは、Anthropic インフラストラクチャで実行されるため、[ウェブ上の Claude Code](/docs/ja/claude-code-on-the-web) には引き継がれません。そこで有効化するか、リポジトリをクローンするすべてのユーザーに対して有効化するには、プロジェクトのチェックイン設定で宣言します：

```json .claude/settings.json theme={null}
{
  "enabledPlugins": {
    "security-guidance@claude-plugins-official": true
  }
}
```

管理者は、[管理設定](/docs/ja/admin-setup) で [`enabledPlugins`](/docs/ja/settings#plugin-settings) を設定することで、組織全体でプラグインを有効化できます。

<h2 id="what-the-plugin-checks">
  プラグインがチェックする内容
</h2>

プラグインは 3 つのポイントで Claude の作業をレビューし、それぞれ異なる深さです：

* [各ファイル編集時](#on-each-file-edit)：リスキーな呼び出しの高速パターンマッチ、モデル呼び出しなし
* [各ターンの終了時](#at-the-end-of-each-turn)：そのターンが変更したすべてのバックグラウンドモデルレビュー
* [Claude が行う各コミットまたはプッシュ時](#on-each-commit-or-push-claude-makes)：周囲のコードを読む深い agentic レビュー

各レイヤーは [独自のルールを追加](#add-your-own-rules) することで拡張できます。組み込みチェックは個別に削除することはできませんが、各レイヤーは [独立して無効化](#disable-or-uninstall) できます。

<h3 id="on-each-file-edit">
  各ファイル編集時
</h3>

Claude がファイルに書き込むと、プラグインは新しいコンテンツをスキャンして既知のリスキーなパターンを探します。これはモデル呼び出しのないパターンマッチなので、使用コストは追加されません。

パターンカテゴリの例：

* 動的コード実行：`eval(`、`new Function`、`os.system`、`child_process.exec`
* 安全でないデシリアライゼーション：`pickle`
* DOM インジェクション：`dangerouslySetInnerHTML`、`.innerHTML =`、`document.write`
* ワークフローファイル：`.github/workflows/` 下の編集。リポジトリレベルの権限を付与できます

チェックは編集が完了した後に実行され、警告を Claude の次のステップのコンテキストに追加します。各警告はセッションごとにパターンごとにファイルごとに 1 回発火するため、同じファイル内の繰り返しマッチは会話をあふれさせません。

`security-patterns.yaml` ファイルを使用して、このレイヤーに [独自のパターンを追加](#add-custom-per-edit-patterns) できます。

<h3 id="at-the-end-of-each-turn">
  各ターンの終了時
</h3>

ターンは Claude が応答する 1 ラウンドです：メッセージを送信し、Claude が作業して返信し、ターンが終了します。各ターンの後、プラグインはターン中に作業ツリーで変更されたすべてのもの（Claude の編集ツール、Bash コマンド、サブエージェントからの変更を含む）の git diff を計算し、セキュリティに焦点を当てた別の Claude レビューに送信します。レビューはバックグラウンドで実行されるため、Claude の返信は遅延しません。レビューが問題を見つけた場合、Claude は結果を使用して再度プロンプトされ、フォローアップとして対処します。

これは文字列マッチでは捕捉できない問題をキャッチします。例えば：

* 認可バイパス
* 安全でない直接オブジェクト参照
* インジェクション
* サーバー側リクエストフォージェリ
* 弱い暗号化

セッションで直接、結果と Claude の解決策の両方が表示されます。レビューはターンごとに最大 30 個の変更されたファイルをカバーし、最大 3 回連続で発火してからあなたに戻ります。

<h3 id="on-each-commit-or-push-claude-makes">
  Claude が行う各コミットまたはプッシュ時
</h3>

Claude が Bash ツールを通じて `git commit` または `git push` を実行すると、プラグインはバックグラウンドで変更の深い agentic レビューを実行します。このレビューは、呼び出し元、サニタイザー、関連ファイルを含む周囲のコードを読んで、結果が実際のものであるかどうかを判断してから報告します。追加のコンテキストは、分離されたときは危険に見えるが、コードベースでは安全なパターンの偽陽性を低く保ちます。

このレイヤーは、Claude が Bash ツールを通じて行うコミットとプッシュでのみ発火します。独自のシェルから実行するコミット（セッション内の `!` シェルエスケープを含む）はレビューされません。コミットとプッシュレビューはローリング 1 時間あたり 20 に制限されています。コミットレビューの結果がターン終了レビューが既に報告したものと重複する場合、Claude は再度プロンプトされないため、クリーンなコミットはこのレイヤーから目に見える出力を生成しません。

<h3 id="review-independence-and-limits">
  レビューの独立性と制限
</h3>

プラグインは、コードを書いた同じ Claude インスタンスに自分自身を採点するよう求めません。編集ごとのチェックは、モデルが関与しない決定論的な文字列マッチです。ターン終了とコミットレビューは、新しいコンテキストとセキュリティに焦点を当てたプロンプトを持つ別の Claude 呼び出しとして実行されます：レビュアーは diff から開始し、元のアプローチに投資がなく、問題を見つけるだけの指示を受けます。

どのレイヤーも書き込みやコミットをブロックしません。結果は書き込み Claude に指示として到達し、Claude は会話で対処し、レビューモデルは問題を見落とす可能性があります。プラグインを完全なセキュリティソリューションではなく、多層防御の 1 つのレイヤーとして扱ってください。[これが他のセキュリティツールとどのように適合するか](#how-this-fits-with-other-security-tools) を参照してください。

<h2 id="add-your-own-rules">
  独自のルールを追加する
</h2>

プラグインには 2 つの拡張ポイントがあります：モデルバックアップレビュー用の Markdown ガイダンスファイルと、編集ごとの文字列マッチ用の YAML または JSON パターンファイルです。どちらも加算的です。チェックを追加できますが、これらのファイルから組み込みのものを無効化することはできません。

<h3 id="add-guidance-for-the-model-backed-reviews">
  モデルバックアップレビュー用のガイダンスを追加する
</h3>

プロジェクトに `.claude/claude-security-guidance.md` を作成し、脅威モデルとレビューチェックリストを平文で説明します。モデルバックアップレビューは、組み込みの脆弱性チェックリストと一緒に追加のコンテキストとして読み込みます。

以下の例は、ロールゲートされた管理ルートとカスタマーデータロギングポリシーを持つウェブサービス用です：

```markdown .claude/claude-security-guidance.md theme={null}
# このリポジトリのセキュリティガイダンス

- INFO レベル以上で `customer_id` または `account_number` をログに記録しないでください。
- `/admin` 下のすべてのルートは、データベース読み取り前に `require_role("admin")` を呼び出す必要があります。
- `===` の代わりに `crypto.timingSafeEqual` をトークン比較に使用してください。
```

これらのルールはレビュアーのガイダンスであり、決定論的なガードレールではありません。プラグインは違反を Claude が修正するための結果として表示しますが、書き込みをブロックしたり、すべての違反がキャッチされることを保証しません。ガイダンスは加算的のみです：脆弱性クラスを無視するように言うルールはそれらの結果を抑制しません。ハード実装の場合、プラグインを [編集をブロックするフック](/docs/ja/hooks-guide#block-edits-to-protected-files) または CI チェックと組み合わせてください。

<h3 id="add-custom-per-edit-patterns">
  カスタム編集ごとのパターンを追加する
</h3>

`.claude/security-patterns.yaml` を作成して、[編集ごとのパターンチェック](#on-each-file-edit) に正規表現またはサブストリングルールを追加します。これらは組み込みパターンと一緒に決定論的な文字列マッチとして実行されます：

```yaml .claude/security-patterns.yaml theme={null}
patterns:
  - rule_name: internal_api_key
    substrings: ["sk_live_", "AKIA"]
    reminder: "ハードコードされた API キープレフィックス。シークレットマネージャーから認証情報を読み込んでください。"
  - rule_name: tenant_unfiltered_query
    regex: "\\.objects\\.all\\(\\)"
    paths: ["**/src/tenants/**"]
    reminder: "マルチテナントコードは org_id でフィルタリングする必要があります。"
```

| フィールド           | タイプ    | 説明                                                                                          |
| :-------------- | :----- | :------------------------------------------------------------------------------------------ |
| `rule_name`     | string | 警告に表示される識別子                                                                                 |
| `reminder`      | string | Claude のコンテキストに追加される警告テキスト、1 KB でキャップ                                                       |
| `regex`         | string | 編集されたコンテンツに対してマッチされる Python 正規表現                                                            |
| `substrings`    | list   | リテラルサブストリング；これまたは `regex` を提供してください                                                         |
| `paths`         | list   | オプションのグロブパターン；ルールはマッチするファイルにのみ適用されます。グロブはフルファイルパスに対してマッチするため、プロジェクト相対パターンの前に `**/` を付けてください |
| `exclude_paths` | list   | スキップするオプションのグロブパターン；`paths` と同じマッチング                                                        |

プラグインは、同じスキーマで `.claude/security-patterns.yml` と `.claude/security-patterns.json` も読み込みます。JSON はすべての Python インストールで機能します。YAML フォームは PyYAML をインポート可能にする必要があり、プラグインはそれをインストールしません。プラグインは最大 50 個のカスタムルールを読み込み、壊滅的なバックトラッキングの傾向がある正規表現をスキップします。

<h3 id="rule-file-lookup-locations">
  ルールファイルの検索場所
</h3>

プラグインは、プラグインがどのように有効化されたかに関係なく、同じ場所で `claude-security-guidance.md` と `security-patterns.yaml` を探します：

| スコープ       | パス                                          | 注記                      |
| :--------- | :------------------------------------------ | :---------------------- |
| ユーザー       | `~/.claude/claude-security-guidance.md`     | マシン上のすべてのプロジェクトに適用されます  |
| プロジェクト     | `.claude/claude-security-guidance.md`       | リポジトリでチェックインされます        |
| プロジェクトローカル | `.claude/claude-security-guidance.local.md` | Gitignored、個人的なオーバーライド用 |

プラグインは存在するすべての場所を読み込み、ガイダンスファイルの合計キャップ 8 KB で連結します。管理者は、デバイス管理を通じて `~/.claude/` にユーザースコープファイルをプッシュすることで、組織全体のルールを配布できます。同じパスが `security-patterns.yaml` に適用されます。

<h2 id="usage-cost">
  使用コスト
</h2>

[編集ごとのパターンチェック](#on-each-file-edit) はモデル呼び出しを行わず、コストを追加しません。[ターン終了](#at-the-end-of-each-turn) と [コミット](#on-each-commit-or-push-claude-makes) レビューはそれぞれ、他の Claude リクエストと同様に [使用](/docs/ja/costs) にカウントされる追加のモデル使用を費やします。コミットレビューは agentic であり、コミットごとに複数のモデルターンを取る可能性があり、ローリング 1 時間あたり 20 レビューに制限されています。ターンごとにファイルを変更する 1 つのレビュー呼び出しと、コミットごとに 1 つの深いレビューを期待してください。どちらも上記のキャップの対象です。

両方のモデルバックアップレビューはデフォルトで Claude Opus 4.7 を使用します。`SECURITY_REVIEW_MODEL` を設定して、ターン終了レビュー用に別のモデルを選択し、`SG_AGENTIC_MODEL` をコミットレビュー用に設定します。

プラグインはすべてのプランで利用可能です。

<h2 id="disable-or-uninstall">
  無効化またはアンインストール
</h2>

残りを保持しながら個別のレイヤーをオフにするには、マッチング環境変数を設定します：

| 変数                              | 効果                                                         |
| :------------------------------ | :--------------------------------------------------------- |
| `ENABLE_PATTERN_RULES=0`        | [編集ごとのパターンチェック](#on-each-file-edit) を無効化                   |
| `ENABLE_STOP_REVIEW=0`          | [ターン終了 diff レビュー](#at-the-end-of-each-turn) を無効化           |
| `ENABLE_COMMIT_REVIEW=0`        | [コミットとプッシュレビュー](#on-each-commit-or-push-claude-makes) を無効化 |
| `ENABLE_CODE_SECURITY_REVIEW=0` | すべてのモデルバックアップレビューを一度に無効化                                   |
| `SECURITY_GUIDANCE_DISABLE=1`   | アンインストールせずにプラグイン全体を無効化                                     |

ユーザースコープでプラグインを一時停止するには：

```text theme={null}
/plugin disable security-guidance@claude-plugins-official
```

ユーザースコープから削除するには：

```text theme={null}
/plugin uninstall security-guidance@claude-plugins-official
```

プラグインがプロジェクトの `.claude/settings.json` を通じて有効化された場合、`/plugin` から無効化すると、チェックインファイルを編集するのではなく、`.claude/settings.local.json` にオーバーライドを書き込むため、プラグインはあなたにとってオフのままで、チームメイトは影響を受けません。同じダイアログでは、共有 `.claude/settings.json` から削除することでプラグインをすべてのユーザーに対してアンインストールするオプションも提供されます。そのオプションには Claude Code v2.1.203 以降が必要です。[管理設定](/docs/ja/admin-setup) を通じて有効化された場合、管理者のみがそれを無効化できます。

<h2 id="how-the-plugin-integrates-with-claude-code">
  プラグインが Claude Code とどのように統合されるか
</h2>

プラグインは完全に [hooks](/docs/ja/hooks) 上に構築されています。これは Claude のループの特定のポイントで独自のコードを実行するメカニズムです。登録されます：

| フックイベント                                                    | 目的                                   |
| :--------------------------------------------------------- | :----------------------------------- |
| `SessionStart`                                             | プラグインの Python 環境をブートストラップ            |
| `UserPromptSubmit`                                         | ターン終了レビューが diff を行う作業ツリーベースラインをキャプチャ |
| `PostToolUse` on `Edit`、`Write`、`NotebookEdit`             | 編集ごとのパターンマッチ                         |
| `Stop`                                                     | ターン終了 diff レビュー、バックグラウンドで実行          |
| `PostToolUse` on `Bash`、`git commit` と `git push` にフィルタリング | コミットとプッシュレビュー、バックグラウンドで実行            |

独自のフックを構築する場合、[プラグインのソース](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance) はフックから別のモデル呼び出しを実行し、結果をセッションにフィードバックする実装例です。

<h2 id="how-this-fits-with-other-security-tools">
  これが他のセキュリティツールとどのように適合するか
</h2>

プラグインは多層防御アプローチの 1 つのレイヤーです。コードがまだエディタにある間に最も早く問題をキャッチしますが、保証ではなく、後の確認を置き換えません。典型的なスタック：

| ステージ    | ツール                                                    | カバーするもの                                   |
| :------ | :----------------------------------------------------- | :---------------------------------------- |
| セッション内  | Security guidance プラグイン                                | Claude が書くコードの一般的な脆弱性。同じセッション内で修正         |
| オンデマンド  | [`/security-review`](/docs/ja/commands#all-commands)        | 現在のブランチでの 1 回限りのセキュリティパス。要求時に実行           |
| プルリクエスト | [Code Review](/docs/ja/code-review)、Team および Enterprise プラン | 完全なコードベースコンテキストを持つマルチエージェント正確性とセキュリティレビュー |
| CI      | 既存の静的分析と依存関係スキャナー                                      | 言語固有のルール、サプライチェーンチェック、プラグインが試みないポリシー実装    |

各後のステージは、前のものが見落とすものをキャッチします。プラグインの価値は、それらに到達するボリュームを削減することであり、それらの必要性を排除することではありません。

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

プラグインはランタイム診断を `~/.claude/security/log.txt` に書き込みます。レビューが表示されない場合は、まずそこを確認してください。

レビューレイヤーが会話にメッセージなしでスキップする一般的な理由：

* ディレクトリが git リポジトリではない：ターン終了とコミットレビューは git 状態を必要とし、リポジトリ外ではスキップします
* セッションに Anthropic 認証がない：モデルバックアップレビューはスキップされ、編集ごとのパターンチェックのみが実行されます
* `security-patterns.yaml` ファイルが存在するが PyYAML がインポート可能ではない：ファイルは無視されます。代わりに `security-patterns.json` を使用してください

<h2 id="related-resources">
  関連リソース
</h2>

このページが触れるピースについてさらに深く掘り下げるには：

* [Code Review](/docs/ja/code-review)：PR 時のマルチエージェントレビューをセットアップ
* [フックでワークフローを自動化](/docs/ja/hooks-guide)：同じライフサイクルポイントで独自のチェックを構築
* [プラグインを発見してインストール](/docs/ja/discover-plugins#official-anthropic-marketplace)：他の公式プラグインを参照
