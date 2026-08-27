> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude に CLI からコンピュータを使用させる

> Claude Code CLI でコンピュータ使用を有効にして、Claude がアプリを開いたり、クリックしたり、入力したり、macOS でスクリーンを表示したりできるようにします。ネイティブアプリをテストし、ビジュアルの問題をデバッグし、ターミナルを離れることなく GUI のみのツールを自動化します。

<Note>
  コンピュータ使用は macOS 上の研究プレビューであり、Pro または Max プランが必要です。Team または Enterprise プランでは利用できません。インタラクティブセッションが必要なため、`-p` フラグを使用した非インタラクティブモードでは利用できません。
</Note>

コンピュータ使用により、Claude はアプリを開き、スクリーンを制御し、あなたが行うのと同じ方法でマシンで作業できます。CLI から、Claude は Swift アプリをコンパイルし、起動し、すべてのボタンをクリックして、結果をスクリーンショットできます。これらはすべて、コードを書いた同じ会話内で行われます。

このページでは、CLI でコンピュータ使用がどのように機能するかについて説明します。Desktop アプリについては、[Desktop でのコンピュータ使用](/docs/ja/desktop#let-claude-use-your-computer)を参照してください。

<h2 id="what-you-can-do-with-computer-use">
  コンピュータ使用でできること
</h2>

コンピュータ使用は GUI が必要なタスクを処理します。通常、ターミナルを離れて手動で行う必要があるすべてのことです。

* **ネイティブアプリの構築と検証**: Claude に macOS メニューバーアプリを構築するよう依頼します。Claude は Swift を書き、コンパイルし、起動し、すべてのコントロールをクリックして、開く前に動作することを確認します。
* **エンドツーエンド UI テスト**: Claude をローカル Electron アプリに指し、「オンボーディングフローをテストして」と言います。Claude はアプリを開き、サインアップをクリックして、各ステップをスクリーンショットします。Playwright 設定なし、テストハーネスなし。
* **ビジュアルとレイアウトの問題をデバッグ**: Claude に「モーダルが小さいウィンドウでクリップしている」と伝えます。Claude はウィンドウをリサイズし、バグを再現し、スクリーンショットを撮り、CSS にパッチを当て、修正を検証します。Claude はあなたが見るものを見ます。
* **GUI のみのツールを駆動**: デザインツール、ハードウェアコントロールパネル、iOS Simulator、または CLI や API がない独自のアプリと対話します。

<h2 id="when-computer-use-applies">
  コンピュータ使用が適用される場合
</h2>

Claude はアプリやサービスと対話するいくつかの方法があります。コンピュータ使用は最も広く、最も遅いため、Claude は最初に最も正確なツールを試します。

* サービスの [MCP サーバー](/docs/ja/mcp)がある場合、Claude はそれを使用します。
* タスクがシェルコマンドの場合、Claude は Bash を使用します。
* タスクがブラウザ作業で、[Chrome の Claude](/docs/ja/chrome)がセットアップされている場合、Claude はそれを使用します。
* これらのいずれも適用されない場合、Claude はコンピュータ使用を使用します。

スクリーン制御は、他に何も到達できないもの（ネイティブアプリ、シミュレータ、API のないツール）のために予約されています。

<h2 id="enable-computer-use">
  コンピュータ使用を有効にする
</h2>

コンピュータ使用は `computer-use` という組み込み MCP サーバーとして利用可能です。有効にするまでデフォルトではオフです。

<Steps>
  <Step title="MCP メニューを開く">
    インタラクティブな Claude Code セッションで、以下を実行します。

    ```text theme={null}
    /mcp
    ```

    サーバーリストで `computer-use` を見つけます。無効として表示されます。
  </Step>

  <Step title="サーバーを有効にする">
    `computer-use` を選択し、**Enable** を選択します。設定はプロジェクトごとに保持されるため、コンピュータ使用が必要な各プロジェクトに対してこれを 1 回だけ行います。
  </Step>

  <Step title="macOS のアクセス許可を付与する">
    Claude がコンピュータを使用しようとする最初の時点で、2 つの macOS アクセス許可を付与するプロンプトが表示されます。

    * **Accessibility**: Claude がクリック、入力、スクロールできるようにします
    * **Screen Recording**: Claude がスクリーンに表示されているものを見ることができるようにします

    プロンプトには、関連するシステム設定ペインを開くためのリンクが含まれています。両方を付与し、プロンプトで **Try again** を選択します。macOS は Screen Recording を付与した後、Claude Code を再起動する必要がある場合があります。
  </Step>
</Steps>

セットアップ後、Claude に GUI が必要なことを実行するよう依頼します。

```text theme={null}
Build the app target, launch it, and click through each tab to make
sure nothing crashes. Screenshot any error states you find.
```

<h2 id="approve-apps-per-session">
  セッションごとにアプリを承認する
</h2>

`computer-use` サーバーを有効にしても、Claude にマシン上のすべてのアプリへのアクセスが許可されるわけではありません。Claude がセッション内で特定のアプリを初めて必要とする場合、ターミナルにプロンプトが表示され、以下が示されます。

* Claude が制御したいアプリ
* クリップボードアクセスなどのリクエストされた追加のアクセス許可
* Claude が作業している間に非表示になる他のアプリの数

**Allow for this session** または **Deny** を選択します。承認は現在のセッションに対して有効です。Claude が一度にそれらをリクエストする場合、複数のアプリを一度に承認できます。

広い範囲を持つアプリは、プロンプトに追加の警告を表示して、承認が何を許可するかを知ることができます。

| 警告                      | 適用対象                                          |
| :---------------------- | :-------------------------------------------- |
| シェルアクセスと同等              | Terminal、iTerm、VS Code、Warp、およびその他のターミナルと IDE |
| 任意のファイルを読み取りまたは書き込みできます | Finder                                        |
| システム設定を変更できます           | System Settings                               |

これらのアプリはブロックされていません。警告により、タスクがそのレベルのアクセスを必要とするかどうかを決定できます。

Claude の制御レベルはアプリカテゴリによっても異なります。ブラウザと取引プラットフォームはビューのみ、ターミナルと IDE はクリックのみ、その他すべてはフルコントロールを取得します。完全なティア分類については、[Desktop でのアプリのアクセス許可](/docs/ja/desktop#app-permissions)を参照してください。

<h2 id="how-claude-works-on-your-screen">
  Claude がスクリーンでどのように機能するか
</h2>

フローを理解することで、Claude が何をするかを予測し、どのように介入するかを理解するのに役立ちます。

<h3 id="one-session-at-a-time">
  一度に 1 つのセッション
</h3>

コンピュータ使用は、最初のコンピュータ使用アクションからそれを取得したセッションが終了するまで、マシン全体のロックを保持します。v2.1.195 以降、タスクを完了してもロックは解放されません。セッションを終了するだけです。別の Claude Code セッションが既にコンピュータを使用している場合、新しい試みはロックを保持しているセッションを示すメッセージで失敗します。最初にそのセッションを終了してください。

<h3 id="apps-are-hidden-while-claude-works">
  Claude が作業している間、アプリは非表示になります
</h3>

Claude がスクリーンの制御を開始すると、他の表示されているアプリは非表示になり、Claude は承認されたアプリのみと対話します。ターミナルウィンドウは表示されたままで、スクリーンショットから除外されるため、セッションを監視でき、Claude は独自の出力を見ることはありません。

Claude がターンを終了すると、非表示のアプリは自動的に復元されます。

<h3 id="screenshots-are-downscaled-automatically">
  スクリーンショットは自動的にダウンスケールされます
</h3>

Claude Code はモデルに送信する前に、すべてのスクリーンショットをダウンスケールします。Retina またはその他の高解像度ディスプレイでディスプレイ解像度を下げたり、ウィンドウをリサイズしたりする必要はありません。16 インチ MacBook Pro をネイティブ Retina 解像度でキャプチャすると 3456×2234 でキャプチャされ、約 1372×887 にダウンスケールされ、アスペクト比が保持されます。

ターゲットサイズを変更する設定はありません。ダウンスケール後、オンスクリーンテキストまたはコントロールが Claude が読むには小さすぎる場合は、ディスプレイ解像度を変更するのではなく、アプリでそれらのサイズを増やします。

<h3 id="stop-at-any-time">
  いつでも停止
</h3>

Claude がロックを取得すると、macOS 通知が表示されます。「Claude is using your computer · press Esc to stop」。どこからでも `Esc` を押して現在のアクションを直ちに中止するか、ターミナルで `Ctrl+C` を押します。どちらの方法でも、Claude は停止し、アプリを表示し、制御をあなたに返します。セッションは、[コンピュータ使用ロック](#one-session-at-a-time)を終了するまで保持します。

Claude が完了したときに 2 番目の通知が表示されます。

<h2 id="safety-and-the-trust-boundary">
  セーフティと信頼の境界
</h2>

<Warning>
  [サンドボックス化された Bash ツール](/docs/ja/sandboxing)とは異なり、コンピュータ使用は実際のデスクトップで実行され、承認したアプリへのアクセスがあります。Claude は各アクションをチェックし、オンスクリーンコンテンツからの潜在的なプロンプトインジェクションにフラグを立てますが、信頼の境界は異なります。ベストプラクティスについては、[コンピュータ使用セーフティガイド](https://support.claude.com/en/articles/14128542)を参照してください。
</Warning>

組み込みのガードレールは、設定を必要とせずにリスクを軽減します。

* **アプリごとの承認**: Claude は現在のセッションで承認したアプリのみを制御できます。
* **センチネル警告**: シェル、ファイルシステム、またはシステム設定アクセスを許可するアプリは、承認する前にフラグが立てられます。
* **スクリーンショットから除外されたターミナル**: Claude はターミナルウィンドウを見ることはないため、セッション内のオンスクリーンプロンプトはモデルにフィードバックできません。
* **グローバルエスケープ**: `Esc` キーはどこからでもコンピュータ使用を中止し、キープレスは消費されるため、プロンプトインジェクションはそれを使用してダイアログを閉じることはできません。
* **ロックファイル**: 一度に 1 つのセッションのみがマシンを制御できます。

<h2 id="example-workflows">
  ワークフロー例
</h2>

これらの例は、コンピュータ使用とコーディングタスクを組み合わせる一般的な方法を示しています。

<h3 id="validate-a-native-build">
  ネイティブビルドを検証する
</h3>

macOS または iOS アプリに変更を加えた後、Claude にコンパイルして 1 回のパスで検証させます。

```text theme={null}
Build the MenuBarStats target, launch it, open the preferences window,
and verify the interval slider updates the label. Screenshot the
preferences window when you're done.
```

Claude は `xcodebuild` を実行し、アプリを起動し、UI と対話し、見つけたものを報告します。

<h3 id="reproduce-a-layout-bug">
  レイアウトバグを再現する
</h3>

ビジュアルバグが特定のウィンドウサイズでのみ表示される場合、Claude に見つけさせます。

```text theme={null}
The settings modal clips its footer on narrow windows. Resize the app
window down until you can reproduce it, screenshot the clipped state,
then check the CSS for the modal container.
```

Claude はウィンドウをリサイズし、壊れた状態をキャプチャし、関連するスタイルシートを読みます。

<h3 id="test-a-simulator-flow">
  シミュレータフローをテストする
</h3>

XCTest を書かずに iOS Simulator を駆動します。

```text theme={null}
Open the iOS Simulator, launch the app, tap through the onboarding
screens, and tell me if any screen takes more than a second to load.
```

Claude はマウスを使用するのと同じ方法でシミュレータを制御します。

<h2 id="differences-from-the-desktop-app">
  Desktop アプリとの違い
</h2>

CLI と Desktop サーフェスは同じコンピュータ使用エンジンを共有します。いくつかの違いがあります。

| 機能          | Desktop                                         | CLI                          |
| :---------- | :---------------------------------------------- | :--------------------------- |
| プラットフォーム    | macOS と Windows                                 | macOS のみ                     |
| 有効化         | **Settings > General** のトグル（**Desktop app** の下） | `/mcp` で `computer-use` を有効化 |
| 拒否されたアプリリスト | 設定で設定可能                                         | まだ利用できません                    |
| 自動非表示トグル    | オプション                                           | 常にオン                         |
| Dispatch 統合 | Dispatch で生成されたセッションはコンピュータ使用を使用できます            | 適用されません                      |

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

<h3 id="computer-use-is-in-use-by-another-claude-session">
  「Computer use is in use by another Claude session」
</h3>

別の Claude Code セッションがロックを保持しており、そのセッションが終了するまでロックを保持し続けます。そのセッションを終了してください。他のセッションがクラッシュした場合、Claude がプロセスがもう実行されていないことを検出すると、ロックは自動的に解放されます。

<h3 id="macos-permissions-prompt-keeps-reappearing">
  macOS のアクセス許可プロンプトが繰り返し表示される
</h3>

macOS は、Screen Recording を付与した後、リクエストプロセスの再起動が必要な場合があります。Claude Code を完全に終了し、新しいセッションを開始します。プロンプトが続く場合は、**System Settings > Privacy & Security > Screen Recording** を開き、ターミナルアプリがリストされ、有効になっていることを確認します。

<h3 id="computer-use-doesn’t-appear-in-/mcp">
  `computer-use` が `/mcp` に表示されない
</h3>

サーバーは適格なセットアップにのみ表示されます。以下を確認してください。

* macOS を使用しています。コンピュータ使用は Linux または Windows では利用できません。Windows では、代わりに [Desktop でのコンピュータ使用](/docs/ja/desktop#let-claude-use-your-computer)を使用してください。
* Pro または Max プランを使用しています。`/status` を実行してサブスクリプションを確認します。
* claude.ai を通じて認証されています。コンピュータ使用は Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry などのサードパーティプロバイダーでは利用できません。サードパーティプロバイダーのみを通じて Claude にアクセスする場合、この機能を使用するには別の claude.ai アカウントが必要です。
* インタラクティブセッションを使用しています。コンピュータ使用は `-p` フラグを使用した非インタラクティブモードでは利用できません。

<h2 id="see-also">
  関連項目
</h2>

* [Desktop でのコンピュータ使用](/docs/ja/desktop#let-claude-use-your-computer): グラフィカル設定ページを備えた同じ機能
* [Chrome の Claude](/docs/ja/chrome): Web ベースのタスク用のブラウザ自動化
* [MCP](/docs/ja/mcp): Claude を構造化ツールと API に接続する
* [サンドボックス化](/docs/ja/sandboxing): Claude の Bash ツールがファイルシステムとネットワークアクセスを分離する方法
* [コンピュータ使用セーフティガイド](https://support.claude.com/en/articles/14128542): 安全なコンピュータ使用のためのベストプラクティス
