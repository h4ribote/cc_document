> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# スクリーンリーダーで Claude Code を使用する

> VoiceOver や NVDA などのスクリーンリーダー、スクリーン拡大鏡、モーション削減、色覚異常対応テーマの設定で Claude Code をセットアップします。

Claude Code には、ビジュアルターミナルインターフェースをプレーンな線形テキストに置き換えるスクリーンリーダーモードがあります。ボックス、プログレスアニメーション、インプレース再描画の代わりに、このモードはラベル付きの行を出力し、VoiceOver や NVDA などのスクリーンリーダーが順番に読み上げるため、完全な会話を保持し、ツール権限を承認し、出力を最後まで確認できます。

スクリーンリーダーモードはオプトインです。スクリーン拡大鏡、モーション削減、またはスクリーンリーダーの代わりにカラーブラインド対応テーマを使用する場合は、[スクリーンリーダーモード以外のアクセシビリティ設定](#accessibility-settings-beyond-screen-reader-mode)を参照してください。

<Note>
  スクリーンリーダーモードには Claude Code v2.1.181 以降が必要です。以前のバージョンは `--ax-screen-reader` フラグを `error: unknown option '--ax-screen-reader'` で拒否します。
</Note>

<h2 id="turn-on-screen-reader-mode">
  スクリーンリーダーモードをオンにする
</h2>

スクリーンリーダーを使用する頻度に合わせて方法を選択してください。

* 1 つのセッション用：`claude --ax-screen-reader` を実行します。
* 1 つのシェルから開始されたセッション用：`CLAUDE_AX_SCREEN_READER` 環境変数を `1` に設定します。Bash または Zsh では `export CLAUDE_AX_SCREEN_READER=1` を実行し、PowerShell では `$env:CLAUDE_AX_SCREEN_READER = "1"` を実行します。すべてのシェルをカバーするために、シェルプロファイルに行を追加します。
* マシン上のすべてのセッション用：ユーザー[設定ファイル](/docs/ja/settings)に `"axScreenReader": true` を追加します。これは VS Code 統合ターミナルを含むすべてのターミナルをカバーします。

<Note>
  メソッドは優先順位順にリストされています。[`--ax-screen-reader`](/docs/ja/cli-reference#cli-flags) フラグは [`CLAUDE_AX_SCREEN_READER`](/docs/ja/env-vars) 環境変数をオーバーライドし、これは [`axScreenReader`](/docs/ja/settings#available-settings) 設定をオーバーライドします。
</Note>

SSH 経由で Claude Code を使用する場合は、Claude Code が実行されるリモートマシンで環境変数または設定を設定します。

モードがオンの場合、Claude Code が最初に出力するのは、それをオンにした方法を名前付けする確認行です。`[Screen Reader Mode: on via flag]`、`[Screen Reader Mode: on via env]`、または `[Screen Reader Mode: on via settings]` です。このメソッド命名形式には Claude Code v2.1.206 以降が必要です。Claude Code が自身を再起動する場合（例えば、アップデートのインストールを完了するため）、新しいプロセスは `CLAUDE_AX_SCREEN_READER` 環境変数を通じてモードを継承するため、使用した方法に関係なく、その確認行は `[Screen Reader Mode: on via env]` と表示されます。
以前のバージョンは `[Accessible screen reader mode: on]` を出力します。

<h2 id="turn-off-screen-reader-mode">
  スクリーンリーダーモードをオフにする
</h2>

モードをオンにした方法を逆にします。フラグなしで開始するか、環境変数を設定解除するか、`axScreenReader` を `false` に設定します。`CLAUDE_AX_SCREEN_READER=0` を設定すると、設定が `true` の場合でもモードはオフのままです。

<h2 id="what-your-screen-reader-hears">
  スクリーンリーダーが聞くもの
</h2>

スクリーンリーダーモードでは、Claude Code はフラットテキストを書き込みます。

* インターフェースクロムのボックス描画文字なし
* 色のみのキューなし
* 変更されていないコンテンツの再描画なし。プログレススピナーは静的テキストとしてレンダリングされます
* Claude の返信のテーブルは、ボックス文字グリッドの代わりに `Header: value` 文として読み上げられます。Claude Code v2.1.198 以降が必要です。以前のバージョンはスクリーンリーダーモードでもテーブルをグリッドとして描画します。

出力はターミナルのスクロールバックに蓄積されるため、スクリーンリーダーのレビューコマンドまたはターミナルの検索を使用して以前のターンを再度読むことができます。

スクリーンリーダーモードは、[フルスクリーンレンダリング](/docs/ja/fullscreen)を [`tui` 設定](/docs/ja/settings#available-settings)でオンにしている場合でも、プレーンなスクロールテキストとしてレンダリングされます。モードがアクティブな間、設定は効果がありません。アタッチされたバックグラウンドセッションは引き続きフルスクリーンでレンダリングされます。[既知の制限事項](#known-limitations)を参照してください。

トランスクリプト内の各メッセージは、スクリーンリーダーが発表するラベルで始まり、それが何であるかを名前付けします。あなたのメッセージ、Claude の返信、ツールアクティビティ、エラー、プロンプトです。ラベルは検索可能でもあるため、ターミナルのスクロールバックを検索してトランスクリプトのセクション間をジャンプできます。

| ラベル                    | 意味                                                              |
| :--------------------- | :-------------------------------------------------------------- |
| `you:`                 | あなたのメッセージ                                                       |
| `claude:`              | Claude の返信                                                      |
| `tool:`                | ファイル編集やコマンド実行などのツールアクティビティ                                      |
| `tool error:`          | 失敗したツール                                                         |
| `error:`               | 失敗した API リクエストなどの会話内のエラー                                        |
| `Permission Required:` | あなたの回答を待っている権限プロンプト                                             |
| `Cost:`                | Claude Code が終了するときのセッションコスト概要（アカウントが[コストを表示](/docs/ja/costs)している場合） |

ターミナルカーソルは入力キャレットに従うため、スクリーンリーダーの現在の行を読むコマンドは「どこにいるのか」に編集しているプロンプトで答えます。

<h3 id="jump-between-turns">
  ターン間をジャンプする
</h3>

Claude Code はターン境界で OSC 133 シェル統合マーカーを出力するため、ターミナルの前のプロンプトにジャンプするキーはトランスクリプト全体を読まずにターン間を移動します。

* iTerm2：Cmd+Shift+Up
* VS Code ターミナル：Windows では Ctrl+Up、macOS では Cmd+Up
* Windows Terminal：デフォルトではキーなし。設定で `scrollToMark` アクションをバインドします
* Kitty と Ghostty：ターミナルのドキュメントでプロンプトにジャンプするキーを確認してください

macOS Terminal はマーカーに作用せず、Claude Code は WezTerm では出力しません。これらのターミナルでは、代わりにスクロールバックで `you:` ラベルを検索してください。

<h2 id="answer-menus-and-prompts">
  メニューとプロンプトに答える
</h2>

スクリーンリーダーモードでは、通常は矢印キーで移動するメニュー（権限プロンプトを含む）は番号付きリストになります。各オプションは番号付きの行として発表され、その後に有効な範囲を名前付けする `Enter selection` プロンプトが続きます。希望するオプションの番号を入力して Enter キーを押します。

* 却下可能なメニューをキャンセルするには：Escape キーを押します。そのプロンプトは `or Escape to cancel` で終わります。
* リストにない番号を入力した場合：Claude Code は有効な範囲を発表し、もう一度試すことができます。

はい/いいえプロンプトは、2 オプションメニューの代わりに入力された回答を求めます。`y` または `n` で答えて Enter キーを押します。`yes` と `no` も機能します。

<h2 id="hear-when-claude-code-needs-you">
  Claude Code があなたを必要とするときに聞く
</h2>

スクリーンリーダーモードでは、Claude Code はあなたの注意が必要なときにターミナルベルを鳴らすため、トランスクリプトを常にチェックする必要はありません。ベルは以下の場合に鳴ります。

* Claude が返信を完了した
* 権限プロンプトが表示される
* 5 秒以上実行されたツールが完了する

ベルはターミナルの標準アラートです。それをサイレントにするには、ターミナルアプリケーションのベル設定を変更します。ベルはスクリーンリーダーモードを必要としません。モード外では、[`preferredNotifChannel`](/docs/ja/settings#available-settings) を `"terminal_bell"` に設定して、Claude があなたを待っているときに同様のアラートを取得します。[ターミナルベルまたは通知を取得する](/docs/ja/terminal-config#get-a-terminal-bell-or-notification)を参照してください。

<h2 id="accessibility-settings-beyond-screen-reader-mode">
  スクリーンリーダーモード以外のアクセシビリティ設定
</h2>

これらのオプションはスクリーンリーダーモード外のアクセシビリティニーズに対応しています。すべてそれと一緒に機能します。

* `CLAUDE_CODE_ACCESSIBILITY` [環境変数](/docs/ja/env-vars)はスクリーン拡大鏡用です。`CLAUDE_CODE_ACCESSIBILITY=1` を設定して、ネイティブターミナルカーソルを表示したままにして、macOS Zoom などの拡大鏡がカーソル位置を追跡できるようにします。
* `prefersReducedMotion` [設定](/docs/ja/settings#available-settings)は、インターフェースの残りを変更せずにスピナー、シマー、その他のアニメーションを削減または無効にします。
* `theme` [設定](/docs/ja/settings#available-settings)はインターフェースの色を選択します。カラーブラインド対応の `dark-daltonized` および `light-daltonized` テーマを含みます。

<h2 id="known-limitations">
  既知の制限事項
</h2>

一部の動作はスクリーンリーダーモード用に適応していません。

* スクリーンリーダーモードは、スクリーンリーダーが実行されているときに自動的にオンになりません。
* [プランモード](/docs/ja/permission-modes#analyze-before-you-edit-with-plan-mode)に入るなどのモード変更はまだ発表されていません。
* `claude attach` または agent view から[バックグラウンドセッション](/docs/ja/agent-view)にアタッチすると、ターミナルの代替画面に入ります。これはネイティブスクロールバックがありません。これは[他のアタッチされたセッションと同じ動作](/docs/ja/fullscreen)です。抜け出すには、空のプロンプトで左矢印を押すか、ダイアログにフォーカスがある場合は Ctrl+Z を押します。
* Claude Code はコストを終了時に出力するサマリーで発表し、ターンごとではありません。
* スクリーンリーダーモードは `-p` フラグで[非対話型モード](/docs/ja/headless)を変更しません。非対話型モードは既にプレーンテキストを書き込み、スクリプト作成の代替案のままです。

<h2 id="report-an-issue">
  問題を報告する
</h2>

スクリーンリーダー、拡大鏡、またはターミナルで何かが機能しない場合は、[Claude Code issue tracker](https://github.com/anthropics/claude-code/issues) で問題を開き、タイトルに支援技術を記載してください。レポートにオペレーティングシステム、ターミナルアプリケーション、支援技術の名前とバージョンを含めます。

<h2 id="related-resources">
  関連リソース
</h2>

これらのページには、このページがカバーする内容の完全なリファレンスエントリと関連セットアップが含まれています。

* [設定](/docs/ja/settings#available-settings)：`axScreenReader`、`prefersReducedMotion`、`theme`、および `preferredNotifChannel` エントリ
* [環境変数](/docs/ja/env-vars)：`CLAUDE_AX_SCREEN_READER` および `CLAUDE_CODE_ACCESSIBILITY` エントリ
* [CLI リファレンス](/docs/ja/cli-reference#cli-flags)：`--ax-screen-reader` フラグ
* [ターミナル設定](/docs/ja/terminal-config)：スクリーンリーダーモード外のベル、通知、テーマ
* [非対話型モード](/docs/ja/headless)：スクリプト化された `claude -p` 実行。スクリーンリーダーモードなしでプレーンテキストを書き込みます
