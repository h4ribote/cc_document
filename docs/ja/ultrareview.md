> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# ultrareview でバグを見つける

> /code-review ultra でクラウド上で深い複数エージェント型のコードレビューを実行し、マージ前にバグを見つけて検証します。

<Note>
  Ultrareview はリサーチプレビュー機能です。機能、価格、および利用可能性はフィードバックに基づいて変更される可能性があります。コマンドは現在 `/code-review ultra` として呼び出され、`/ultrareview` はエイリアスとして残ります。
</Note>

Ultrareview は Claude Code のウェブインフラストラクチャ上で実行される深いコードレビューです。`/code-review ultra` を実行すると、Claude Code はリモートサンドボックスでレビュアーエージェントのフリートを起動し、ブランチまたはプルリクエストのバグを見つけます。

ローカルの `/code-review` または `/review` と比較して、ultrareview は以下を提供します。

* **より高いシグナル**: 報告されたすべての検出結果は独立して再現および検証されるため、結果はスタイル提案ではなく実際のバグに焦点を当てています
* **より広いカバレッジ**: より大規模なレビュアーエージェントのフリートが並行して変更を探索するため、ローカルレビューでは見落とされる可能性のある問題が浮かび上がります
* **ローカルリソースの使用なし**: レビューはリモートサンドボックスで完全に実行されるため、実行中はターミナルが他の作業に使用可能なままです

Ultrareview は Claude Code のウェブインフラストラクチャ上で実行されるため、Claude.ai アカウントでの認証が必要です。API キーのみで署名している場合は、`/login` を実行して Claude.ai で認証してください。Ultrareview は Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry で Claude Code を使用する場合は利用できず、Zero Data Retention を有効にしている組織でも利用できません。

<h2 id="run-ultrareview-from-the-cli">
  CLI から ultrareview を実行する
</h2>

任意の git リポジトリから Claude Code CLI でレビューを開始します。

```text theme={null}
/code-review ultra
```

引数なしの場合、ultrareview は現在のブランチとデフォルトブランチ間の差分をレビューします。これには、作業ツリー内のコミットされていない変更とステージされた変更が含まれます。Claude Code はリポジトリの状態をバンドルし、レビュー用にリモートサンドボックスにアップロードします。

代わりに GitHub プルリクエストをレビューするには、PR 番号を渡します。

```text theme={null}
/code-review ultra 1234
```

PR モードでは、リモートサンドボックスはローカルの作業ツリーをバンドルするのではなく、ホストから直接プルリクエストをクローンします。PR モードは `github.com` 上のリポジトリおよび Claude Code に接続されている Owner が設定した [GitHub Enterprise Server](/docs/ja/github-enterprise-server) インスタンスで機能します。

<Tip>
  リポジトリが大きすぎてバンドルできない場合、Claude Code は代わりに PR モードを使用するよう促します。ブランチをプッシュしてドラフト PR を開き、`/code-review ultra <PR-number>` を実行してください。

  プルリクエストの差分が大きすぎる場合、Claude Code はレビュー作業が実行される前にスコーピングヒントを含めて拒否します。
</Tip>

起動前に、Claude Code はレビュー範囲（ブランチをレビューする場合はファイルと行数を含む）、残りの無料実行回数、および推定コストを含む確認ダイアログを表示します。確認後、レビューはバックグラウンドで続行され、セッションを引き続き使用できます。コマンドは `/code-review ultra` で呼び出すときのみ実行されます。Claude は ultrareview を自動的に開始しません。

<h2 id="pricing-and-free-runs">
  価格と無料実行回数
</h2>

Ultrareview はプランに含まれる使用量ではなく、追加使用量に対して請求されるプレミアム機能です。

| プラン                 | 含まれる無料実行回数 | 無料実行回数後                                                                                         |
| ------------------- | ---------- | ----------------------------------------------------------------------------------------------- |
| Pro                 | 3 回の無料実行   | [追加使用量](https://support.claude.com/ja/articles/12429409-extra-usage-for-paid-claude-plans)として請求 |
| Max                 | 3 回の無料実行   | [追加使用量](https://support.claude.com/ja/articles/12429409-extra-usage-for-paid-claude-plans)として請求 |
| Team および Enterprise | なし         | [追加使用量](https://support.claude.com/ja/articles/12429409-extra-usage-for-paid-claude-plans)として請求 |

Pro および Max サブスクライバーは、機能を試すために 3 回の無料 ultrareview 実行を受け取ります。これら 3 回の実行はアカウントごとの 1 回限りの割り当てであり、更新されません。3 回すべてを使用した後、または無料実行期間が終了した後、各レビューは追加使用量に請求され、通常は変更のサイズに応じて $5 から $20 の費用がかかります。クラウドセッションが開始されると実行がカウントされるため、早期に停止したレビューまたは完了に失敗したレビューでも、無料実行を使用します。有料レビューの場合、追加使用量は実行された部分に対してのみ請求されます。

Ultrareview は常に無料実行回数外の追加使用量として請求されるため、有料レビューを起動する前に、アカウントまたは組織で追加使用量を有効にする必要があります。追加使用量が有効になっていない場合、Claude Code は起動をブロックし、有効にできる請求設定にリンクします。`/usage-credits` を実行して、現在の設定を確認または変更することもできます。

<h2 id="track-a-running-review">
  実行中のレビューを追跡する
</h2>

レビューは通常 5 ～ 10 分かかります。レビューはバックグラウンドタスクとして実行されるため、セッションで作業を続けたり、他のコマンドを開始したり、ターミナルを完全に閉じたりできます。

`/tasks` を使用して、実行中および完了したレビューを表示し、レビューの詳細ビューを開くか、進行中のレビューを停止します。レビューを停止するとクラウドセッションがアーカイブされ、部分的な検出結果は返されません。レビューが完了すると、検証された検出結果がセッション内の通知として表示されます。各検出結果には、ファイルの場所と問題の説明が含まれているため、Claude に直接修正を依頼できます。

<h2 id="run-ultrareview-non-interactively">
  ultrareview を非対話的に実行する
</h2>

`claude ultrareview` サブコマンドを使用して、対話的なセッションなしに CI またはスクリプトから ultrareview を開始します。サブコマンドは `/code-review ultra` と同じレビューを起動し、リモートレビューが完了するまでブロックし、検出結果を stdout に出力し、成功時にコード 0 で終了するか、失敗時にコード 1 で終了します。

```bash theme={null}
claude ultrareview
claude ultrareview 1234
claude ultrareview origin/main
```

引数なしの場合、サブコマンドは現在のブランチとデフォルトブランチ間の差分をレビューします。PR 番号を渡して PR をレビューするか、ベースブランチを渡して代わりにそのブランチに対する差分をレビューします。サブコマンドを呼び出すことは、対話的なコマンドが表示する請求および利用規約プロンプトに対する同意として機能します。

進捗メッセージとライブセッション URL は stderr に送信されるため、stdout は解析可能なままです。出力とタイムアウトを制御するには、これらのフラグを使用します。

| フラグ                   | 説明                                            |
| --------------------- | --------------------------------------------- |
| `--json`              | フォーマットされた検出結果の代わりに、生の `bugs.json` ペイロードを出力します |
| `--timeout <minutes>` | レビューが完了するまで待機する最大分数。デフォルトは 30 です              |

`claude ultrareview` を実行するには、`/code-review ultra` と同じ認証と使用量クレジット設定が必要です。サブコマンドは、レビューが検出結果の有無にかかわらず完了したときにコード 0 で終了し、レビューの起動に失敗した場合、リモートセッションがエラーになった場合、またはタイムアウトが経過した場合にコード 1 で終了し、Ctrl-C で中断された場合にコード 130 で終了します。サブコマンドを中断した場合、リモートレビューは実行し続けます。stderr に出力されたセッション URL に従って、ブラウザで監視してください。

GitHub プルリクエストの自動レビューについては、[Code Review](/docs/ja/code-review) がリポジトリと直接統合され、CLI ステップなしでインラインの PR コメントとして検出結果を投稿します。

<h2 id="how-ultrareview-compares-to-/code-review-and-/review">
  ultrareview と /code-review および /review の比較
</h2>

3 つのコマンドはすべてコードをレビューしますが、ワークフローの異なるステージをターゲットにしています。

|       | `/code-review` | `/review <pr>`           | `/code-review ultra`          |
| ----- | -------------- | ------------------------ | ----------------------------- |
| ターゲット | 作業中の diff      | GitHub プルリクエスト           | 作業中の diff またはプルリクエスト          |
| 実行場所  | セッション内でローカルに実行 | セッション内でローカルに実行           | クラウドサンドボックスでリモートに実行           |
| 深さ    | effort 引数でスケール | セッションの effort での単一パスレビュー | 独立した検証を備えた複数エージェントフリート        |
| 期間    | 数秒から数分         | 数秒から数分                   | 約 5 ～ 10 分                    |
| コスト   | 通常の使用量にカウント    | 通常の使用量にカウント              | 無料実行回数、その後追加使用量として約 5 ～ 20 ドル |
| 最適な用途 | 反復中の迅速なフィードバック | マージ前にチームメイトの PR をレビュー    | 実質的な変更のマージ前の信頼度               |

作業中の迅速なフィードバックには `/code-review` を使用します。マージ前にチームメイトの PR をレビューする場合は `/review <pr>` を使用します。ローカルレビューで見落とされる可能性のある問題をキャッチするより深いパスが必要な場合は、実質的な変更をマージする前に `/code-review ultra` を使用します。

<h2 id="related-resources">
  関連リソース
</h2>

* [Claude Code on the web](/docs/ja/claude-code-on-the-web): クラウドセッションとクラウドサンドボックスの仕組みについて学習します
* [Plan complex changes with ultraplan](/docs/ja/ultraplan): 事前設計作業のための ultrareview のカウンターパート
* [Manage costs effectively](/docs/ja/costs): 使用量を追跡し、支出制限を設定します
