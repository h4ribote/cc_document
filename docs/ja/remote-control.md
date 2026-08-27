> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 任意のデバイスからローカルセッションを続行する Remote Control

> Remote Control を使用して、電話、タブレット、または任意のブラウザから Claude Code のローカルセッションを続行します。claude.ai/code と Claude モバイルアプリで動作します。

<Note>
  Remote Control は研究プレビュー段階にあり、すべてのプランで利用可能です。Team および Enterprise では、管理者が [Claude Code 管理設定](https://claude.ai/admin-settings/claude-code) で Remote Control トグルを有効にするまで、デフォルトではオフになっています。
</Note>

Remote Control は [claude.ai/code](https://claude.ai/code) または Claude アプリ（[iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) および [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude)）をマシン上で実行されている Claude Code セッションに接続します。デスクでタスクを開始してから、ソファの電話またはコンピュータのブラウザで続行できます。

マシン上で Remote Control セッションを開始すると、Claude はローカルで実行され続けるため、コード実行とファイルシステムアクセスはマシン上に留まります。Remote Control を使用すると、以下のことができます。

* **ローカル環境全体をリモートで使用する**: ファイルシステム、[MCP サーバー](/docs/ja/mcp)、ツール、プロジェクト設定がすべて利用可能なままです。また、`@` を入力するとローカルプロジェクトのファイルパスが自動補完されます
* **両方のサーフェスから同時に作業する**: 会話と [subagents](/docs/ja/sub-agents) および [dynamic workflows](/docs/ja/workflows) の進捗がすべての接続されたデバイス間で同期されるため、ターミナル、ブラウザ、電話から相互に交換可能にメッセージを送信できます。v2.1.207 より前では、[Desktop app](/docs/ja/desktop) でホストされたセッションは接続されたデバイスに subagent またはワークフローの進捗を送信しませんでした。
* **電話またはブラウザから画像とファイルを送信する**: Claude アプリまたは claude.ai/code に添付ファイルを追加すると、Claude Code はそれをマシンにダウンロードし、キャプション付きまたはキャプションなしで `@` ファイル参照として Claude に渡します。v2.1.202 より前では、キャプションなしで送信された添付ファイルがセッションに到達する前に Claude Code がドロップする可能性がありました。
* **中断に対応する**: ラップトップがスリープ状態になったり、ネットワークが切断されたりした場合、マシンがオンラインに戻ると、セッションは自動的に再接続されます。Claude Code は再接続中に subagents およびワークフローからのステータス更新をキューに入れ、復旧後に配信します。v2.1.207 より前では、再接続または認証情報の更新中に送信された更新が失われる可能性があり、接続されたデバイスは完了したタスクが実行中として表示され続けていました。

クラウドインフラストラクチャで実行される [Web 上の Claude Code](/docs/ja/claude-code-on-the-web) とは異なり、Remote Control セッションはマシン上で直接実行され、ローカルファイルシステムと相互作用します。Web およびモバイルインターフェースは、そのローカルセッションへのウィンドウにすぎません。

このページでは、セットアップ、セッションの開始と接続方法、および Remote Control と Web 上の Claude Code の比較について説明します。

<h2 id="requirements">
  要件
</h2>

Remote Control を使用する前に、環境が以下の条件を満たしていることを確認してください。

* **サブスクリプション**: Pro、Max、Team、および Enterprise プランで利用可能です。API キーはサポートされていません。Team および Enterprise では、Owner が [Claude Code 管理設定](https://claude.ai/admin-settings/claude-code) で Remote Control トグルを最初に有効にする必要があります。
* **認証**: `claude` を実行し、まだサインインしていない場合は `/login` を使用して claude.ai 経由でサインインします。
* **API エンドポイント**: Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry では利用できません。v2.1.196 以降、[`ANTHROPIC_BASE_URL`](/docs/ja/env-vars) が `api.anthropic.com` 以外のホスト（[LLM gateway](/docs/ja/llm-gateway) やプロキシなど）を指している場合、Remote Control も無効になります。Remote Control を使用するには、この変数を設定解除してください。
* **ワークスペース信頼**: プロジェクトディレクトリで少なくとも 1 回 `claude` を実行して、ワークスペース信頼ダイアログを受け入れます。

<h2 id="start-a-remote-control-session">
  Remote Control セッションを開始する
</h2>

CLI または VS Code 拡張機能から Remote Control セッションを開始できます。CLI は 3 つの呼び出しモードを提供します。VS Code は `/remote-control` コマンドを使用します。

<Tabs>
  <Tab title="サーバーモード">
    プロジェクトディレクトリに移動して、以下を実行します。

    ```bash theme={null}
    claude remote-control
    ```

    プロセスはサーバーモードでターミナルで実行され続け、リモート接続を待機します。[別のデバイスから接続](#connect-from-another-device)するために使用できるセッション URL が表示され、スペースバーを押して電話からの高速アクセス用の QR コードを表示できます。リモートセッションがアクティブな間、ターミナルは接続ステータスとツールアクティビティを表示します。

    利用可能なフラグ:

    | フラグ                                             | 説明                                                                                                                                                                                                                                                                                                                                     |
    | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `--name "My Project"`                           | claude.ai/code のセッションリストに表示されるカスタムセッションタイトルを設定します。                                                                                                                                                                                                                                                                                     |
    | `--remote-control-session-name-prefix <prefix>` | 明示的な名前が設定されていない場合の自動生成セッション名のプレフィックス。デフォルトはマシンのホスト名で、`myhost-graceful-unicorn` のような名前が生成されます。同じ効果のために `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` を設定します。                                                                                                                                                                              |
    | `-c`, `--continue`                              | このディレクトリから開始された最新の Remote Control セッションを再開します。新しいセッションを作成する代わりに使用します。`--session-id`、`--spawn`、`--capacity`、または `--create-session-in-dir` と組み合わせることはできません。Claude Code v2.1.200 以降が必要です。それより前のバージョンはこのフラグを未知の引数として拒否します。                                                                                                                 |
    | `--session-id <id>`                             | 特定の Remote Control セッションをその ID で再開します。`--continue`、`--spawn`、`--capacity`、または `--create-session-in-dir` と組み合わせることはできません。Claude Code v2.1.200 以降が必要です。それより前のバージョンはこのフラグを未知の引数として拒否します。                                                                                                                                                  |
    | `--spawn <mode>`                                | サーバーがセッションを作成する方法。<br />• `same-dir`（デフォルト）: すべてのセッションが現在の作業ディレクトリを共有するため、同じファイルを編集している場合は競合する可能性があります。<br />• `worktree`: オンデマンドセッションごとに独自の [git worktree](/docs/ja/worktrees) を取得します。git リポジトリが必要です。<br />• `session`: シングルセッションモード。正確に 1 つのセッションを提供し、追加の接続を拒否します。スタートアップ時にのみ設定します。<br />実行時に `w` を押して `same-dir` と `worktree` の間でトグルします。 |
    | `--capacity <N>`                                | 同時セッションの最大数。デフォルトは 32 です。`--spawn=session` では使用できません。                                                                                                                                                                                                                                                                                  |
    | `--[no-]create-session-in-dir`                  | サーバーの起動時に現在のディレクトリに 1 つのセッションを事前作成し、すぐに入力できる場所を用意します。`worktree` モードでは、このセッションは現在のディレクトリに留まり、オンデマンドセッションは分離された worktree を取得します。デフォルトではオンです。`--no-create-session-in-dir` を渡して、何も作成しない状態で開始します。                                                                                                                                           |
    | `--verbose`                                     | 詳細な接続とセッションログを表示します。                                                                                                                                                                                                                                                                                                                   |
    | `--sandbox` / `--no-sandbox`                    | ファイルシステムとネットワーク分離のための [サンドボックス](/docs/ja/sandboxing)を有効または無効にします。デフォルトではオフです。                                                                                                                                                                                                                                                               |
  </Tab>

  <Tab title="対話型セッション">
    Remote Control を有効にした通常の対話型 Claude Code セッションを開始するには、`--remote-control` フラグ（または `--rc`）を使用します。

    ```bash theme={null}
    claude --remote-control
    ```

    オプションでセッションの名前を渡します。

    ```bash theme={null}
    claude --remote-control "My Project"
    ```

    これにより、ターミナルで完全な対話型セッションが得られ、claude.ai または Claude アプリからも制御できます。`claude remote-control`（サーバーモード）とは異なり、セッションがリモートで利用可能な間、ローカルでメッセージを入力できます。
  </Tab>

  <Tab title="既存のセッションから">
    既に Claude Code セッションにいて、それをリモートで続行したい場合は、`/remote-control`（または `/rc`）コマンドを使用します。

    ```text theme={null}
    /remote-control
    ```

    カスタムセッションタイトルを設定するために、引数として名前を渡します。

    ```text theme={null}
    /remote-control My Project
    ```

    これにより、現在の会話履歴を引き継ぎ、Remote Control セッションが開始されます。

    `--verbose`、`--sandbox`、および `--no-sandbox` フラグはこのコマンドでは利用できません。
  </Tab>

  <Tab title="VS Code">
    [Claude Code VS Code 拡張機能](/docs/ja/vs-code)で、プロンプトボックスに `/remote-control` または `/rc` を入力するか、`/` でコマンドメニューを開いて選択します。

    ```text theme={null}
    /remote-control
    ```

    プロンプトボックスの上にバナーが表示され、接続ステータスが示されます。接続されたら、バナーの **Open in browser** をクリックしてセッションに直接移動するか、[claude.ai/code](https://claude.ai/code)のセッションリストで見つけます。セッション URL は会話にも投稿されます。

    切断するには、バナーの閉じるアイコンをクリックするか、`/remote-control` を再度実行します。

    CLI とは異なり、VS Code コマンドは名前引数を受け入れず、QR コードを表示しません。セッションタイトルは会話履歴または最初のプロンプトから派生します。
  </Tab>
</Tabs>

<h3 id="check-connection-status">
  接続ステータスを確認する
</h3>

対話型ターミナルセッションでは、接続がアップしている間、入力ボックスの下のフッターに `/rc active` インジケーターが表示され、ターミナルが狭すぎる場合は非表示になります。インジケーターテキストは claude.ai のセッションへのリンクです。下矢印キーで選択して Enter キーを押すか、`/remote-control` を再度実行して、セッション URL と [別のデバイスから接続](#connect-from-another-device)するために使用できる QR コードを含むステータスパネルを開きます。

接続に失敗した場合、通知が失敗の理由とともに表示され、インジケーターはフッターから消えます。`/remote-control` を再度実行して再試行します。

<h3 id="connect-from-another-device">
  別のデバイスから接続する
</h3>

Remote Control セッションがアクティブになったら、別のデバイスから接続するいくつかの方法があります。

* **セッション URL を開く**: 任意のブラウザで [claude.ai/code](https://claude.ai/code)のセッションに直接移動します。
* **QR コードをスキャンする**: セッション URL の横に表示される QR コードをスキャンして、Claude アプリで直接開きます。`claude remote-control` を使用する場合は、スペースバーを押して QR コード表示をトグルします。
* **[claude.ai/code](https://claude.ai/code)または Claude アプリを開く**: セッションリストで名前でセッションを見つけます。Claude モバイルアプリでは、ナビゲーションの **Code** をタップしてセッションリストに到達します。Remote Control セッションはオンラインの場合、コンピュータアイコンと緑色のステータスドットを表示します。

接続すると、デバイスはセッションが既にバックグラウンドで実行しているサブエージェントとワークフローを表示します。v2.1.208 より前では、対話型ターミナルでホストされているセッションに接続するデバイスは、既に実行されていたサブエージェントとワークフローを、それらの 1 つが開始または停止されるまで表示しませんでした。

リモートセッションのタイトルは、この順序で選択されます。

1. `--name`、`--remote-control`、または `/remote-control` に渡した名前
2. `/rename` で設定したタイトル
3. 既存の会話履歴の最後の意味のあるメッセージ
4. `myhost-graceful-unicorn` のような自動生成名。ここで `myhost` はマシンのホスト名または `--remote-control-session-name-prefix` で設定したプレフィックスです

明示的な名前を設定しなかった場合、プロンプトを送信するとタイトルが更新されて反映されます。Claude Code v2.1.176 以降、自動生成されたタイトルは会話の言語、または設定されている場合は [`language`](/docs/ja/settings#available-settings) 設定に一致します。claude.ai または Claude アプリからセッションの名前を変更すると、`claude --resume` に表示されるローカルタイトルも更新されます。

環境に既にアクティブなセッションがある場合は、それを続行するか新しいセッションを開始するかを尋ねられます。

Claude アプリをまだ持っていない場合は、Claude Code 内で `/mobile` コマンドを使用して、[iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684)または [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude)のダウンロード QR コードを表示します。

<h3 id="enable-remote-control-for-all-sessions">
  すべてのセッションで Remote Control を有効にする
</h3>

Remote Control のみ、`claude remote-control`、`claude --remote-control`、または `/remote-control` を明示的に実行した場合、またはオートコネクトがオンになっている場合にアクティブになります。すべての対話型セッションで自動的に有効にするには、Claude Code 内で `/config` を実行し、**Enable Remote Control for all sessions** を `true` に設定します。無効にするには `false` に設定するか、組織のデフォルトに従うために設定しないままにします。Desktop アプリでは、**Settings → Claude Code → Enable remote control by default** からこれをトグルすることもできます。[VS Code 拡張機能](/docs/ja/vs-code#use-the-prompt-box)では、同じトグルがコマンドメニューの Settings セクションに **Enable Remote Control for all sessions** として表示されます。Claude Code v2.1.203 以降が必要です。

この設定がオンの場合、各対話型 Claude Code プロセスは 1 つのリモートセッションを登録します。複数のインスタンスを実行する場合、各インスタンスは独自の環境とセッションを取得します。単一のプロセスから複数の同時セッションを実行するには、[サーバーモード](#start-a-remote-control-session)を使用します。

<h2 id="connection-and-security">
  接続とセキュリティ
</h2>

ローカル Claude Code セッションは、アウトバウンド HTTPS リクエストのみを行い、マシン上のインバウンドポートを開くことはありません。Remote Control を開始すると、Anthropic API に登録され、作業をポーリングします。別のデバイスから接続すると、サーバーは Web またはモバイルクライアントとローカルセッション間のメッセージをストリーミング接続経由でルーティングします。

すべてのトラフィックは TLS 経由で Anthropic API を通じて移動し、Claude Code セッションと同じトランスポートセキュリティです。接続は複数の短命の認証情報を使用し、各認証情報は単一の目的にスコープされ、独立して有効期限が切れます。

Remote Control が接続されている間、セッショントランスクリプト（メッセージ、Claude の応答、ツールアクティビティを含む）は Anthropic サーバーに保存されます。保存されたトランスクリプトは、デバイス間で会話を同期させ、ネットワーク障害後にセッションが再接続できるようにします。実行とファイルシステムアクセスはマシン上に留まり、保存されたトランスクリプトは [データ使用](/docs/ja/data-usage) ポリシーに基づいて保持されます。

Remote Control を完全にオフにするには、[`disableRemoteControl`](/docs/ja/settings#available-settings) 設定を使用します。Zero Data Retention などのコンプライアンス要件を持つ組織は Remote Control を有効にすることはできません。

<h2 id="trusted-devices">
  信頼できるデバイス
</h2>

<Note>
  信頼できるデバイスは現在ベータ版です。エクスペリエンスが改善されるにつれて、機能と機能が進化する可能性があります。

  信頼できるデバイスは Team および Enterprise プランで利用可能です。デフォルトではオフになっており、管理者が有効にするまでオフのままです。
</Note>

信頼できるデバイスは、メンバーが claude.ai、Claude モバイルアプリ、または Claude Desktop から Remote Control セッションを表示または操作する前に、デバイスを確認する必要がある組織全体の設定です。これは、署名されたアカウントだけでなく、既知のデバイスと最近の認証に Remote Control アクセスを結び付けます。

設定がオンの場合、Remote Control セッションと相互作用するには、以下の両方が必要です。

* **登録されたデバイス**: メンバーが Remote Control に使用する各ブラウザ、電話、またはデスクトップアプリは、独自の認証情報を登録します。登録は完全なサインイン直後にのみ提供されるため、デバイスはバックグラウンドで静かに登録されるのではなく、実際の認証の一部として信頼できるリストに参加します。
* **最近のサインイン**: メンバーのサインインは 18 時間以内である必要があります。毎日サインインする代わりに、メンバーは Face ID、Touch ID、Windows Hello、またはパスキーで存在を確認します。このバイオメトリック段階的認証はセッションを即座にリフレッシュします。

バイオメトリック チェックはデバイス上でオペレーティングシステムまたはブラウザを通じて実行され、パスキーサインインと同じメカニズムです。Anthropic は指紋、顔データ、またはその他のバイオメトリック情報を受け取ったり保存したりすることはありません。デバイスの公開鍵と表示名、プラットフォーム、登録時刻などの基本的なメタデータのみが保存されます。

この設定は Remote Control にのみ適用されます。通常の Claude チャット、ターミナルの Claude Code、および API 使用は影響を受けません。

<h3 id="enable-trusted-devices-for-your-organization">
  組織で信頼できるデバイスを有効にする
</h3>

管理者は Claude Code 管理コンソールから設定を有効にします。

<Steps>
  <Step title="Claude Code 管理設定を開く">
    [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) に移動します。**Require trusted devices** トグルは Remote Control 設定の下に表示されます。
  </Step>

  <Step title="信頼できるデバイスを要求をオンにする">
    この設定は組織のすべてのメンバーと、トグルを有効にした後に開始された Remote Control セッションに適用されます。トグルがオンになる前に既に実行されていたセッションは遡及的に保護されず、終了するまでデバイス要件なしで続行されます。チームごとまたはプロジェクトごとのスコープは利用できません。
  </Step>

  <Step title="メンバーに何を期待するかを伝える">
    設定が有効になった後、メンバーがブラウザ、電話、またはデスクトップアプリから新しい Remote Control セッションを初めて表示または操作するときに、そのデバイスを登録するよう求められます。事前に知らせることで混乱を避けられます。
  </Step>
</Steps>

<h3 id="what-members-see">
  メンバーが見るもの
</h3>

登録はデバイスごとに 1 回限りのステップです。その後、唯一の目に見える変化は時折のバイオメトリック プロンプトです。

* **各デバイスでの初回使用**: メンバーは登録するよう求められます。サインインが最近でない場合は、SSO が設定されている場合を含む通常のフローを通じてサインインしてから、登録を確認します。
* **日々**: 登録されたデバイスと最近のサインインを持つメンバーはプロンプトを見ません。サインインが 18 時間を超えて経過すると、次の Remote Control インタラクションは単一の Face ID、Touch ID、Windows Hello、またはパスキー プロンプトを表示します。
* **登録されていないデバイス**: デバイスが登録されるまで、Remote Control セッションを表示または操作することはできません。そのデバイスでの通常の Claude チャットは影響を受けません。
* **プラットフォーム認証器がない**: Face ID、Touch ID、または Windows Hello がないマシン上のメンバーは、ハードウェアセキュリティキーを使用するか、段階的認証の代わりにサインインできます。
* **ターミナルで**: Claude Code を実行しているマシンは、開発者が CLI にサインインするときに独自の認証情報を自動的に受け取ります。ターミナルに別の登録ステップはありません。

<h3 id="manage-enrolled-devices">
  登録されたデバイスを管理する
</h3>

メンバーはアカウント設定から独自のデバイスを確認および取り消すことができます。

[claude.ai/settings/account](https://claude.ai/settings/account#trusted-devices) を開き、**Trusted devices** セクションを見つけて、名前、プラットフォーム、登録日を含むすべての登録されたデバイスを確認します。デバイスを削除すると、その認証情報は即座に取り消され、デバイスは後で新しいサインイン後に再登録できます。認証情報は更新されない場合は自動的に有効期限が切れるため、未使用のデバイスは信頼できるリストから自動的に削除されます。

紛失または盗難されたデバイスの場合、メンバーはこのページから削除します。メンバーがサインインできない場合、管理者は管理コンソールで **Sign out everywhere** を使用してそのメンバーのすべてのセッションと登録されたデバイスを取り消すことができます。その後、メンバーは保持しているデバイスを再登録します。

<h2 id="remote-control-vs-claude-code-on-the-web">
  Remote Control と Web 上の Claude Code
</h2>

Remote Control と [Web 上の Claude Code](/docs/ja/claude-code-on-the-web) の両方が claude.ai/code インターフェースを使用します。主な違いはセッションが実行される場所です。Remote Control はマシン上で実行されるため、ローカル MCP サーバー、ツール、プロジェクト設定が利用可能なままです。Web 上の Claude Code は Anthropic が管理するクラウドインフラストラクチャで実行されます。

ローカル作業の途中で別のデバイスから続行したい場合は Remote Control を使用します。ローカルセットアップなしでタスクを開始したい場合、クローンしていないリポジトリで作業したい場合、または複数のタスクを並列で実行したい場合は Web 上の Claude Code を使用します。

<h2 id="mobile-push-notifications">
  モバイルプッシュ通知
</h2>

Remote Control がアクティブな場合、Claude は電話にプッシュ通知を送信できます。

Claude がプッシュを送信するタイミングを決定します。通常は、長時間実行されるタスクが完了したときまたは続行するために決定が必要なときに送信されます。プロンプトでプッシュをリクエストすることもできます。たとえば、`notify me when the tests finish` のように指定します。以下のオン/オフトグル以外に、イベントごとの設定はありません。

モバイルプッシュ通知をセットアップするには:

<Steps>
  <Step title="Claude モバイルアプリをインストールする">
    Claude アプリを [iOS](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684) または [Android](https://play.google.com/store/apps/details?id=com.anthropic.claude) にダウンロードします。
  </Step>

  <Step title="Claude Code アカウントでサインインする">
    ターミナルで Claude Code に使用するのと同じアカウントと組織を使用します。
  </Step>

  <Step title="通知を許可する">
    オペレーティングシステムからの通知許可プロンプトを受け入れます。
  </Step>

  <Step title="Claude Code でプッシュを有効にする">
    ターミナルで `/config` を実行し、プロアクティブな通知の場合は **Push when Claude decides** を有効にし、許可プロンプトと質問の場合は **Push when actions required** を有効にするか、その両方を有効にします。
  </Step>
</Steps>

通知が到着しない場合:

* `/config` が **No mobile registered** を表示する場合は、Claude アプリを電話で開いてプッシュトークンをリフレッシュできるようにします。警告は Remote Control が次に接続するときにクリアされます。
* iOS では、フォーカスモードと通知サマリーがプッシュを抑制または遅延させることができます。Settings → Notifications → Claude を確認してください。
* Android では、積極的なバッテリー最適化が配信を遅延させることができます。システム設定で Claude アプリをバッテリー最適化から除外します。

Claude Code は、ターミナルに入力中またはターミナルにフォーカスしている間、モバイルプッシュ通知をスキップします。v2.1.181 以降では、[`CLAUDE_CLIENT_PRESENCE_FILE`](/docs/ja/env-vars) をマーカーファイルパスに設定して、別のウィンドウにいる場合でも、マシンにいるときはいつでもこれを拡張できます。ファイルが存在する間は通知がスキップされます。スクリーンロックリスナーまたは同様のツールを設定して、スクリーンがロック解除されたときにファイルを作成し、スクリーンがロックされたときにファイルを削除します。

<h2 id="limitations">
  制限事項
</h2>

* **対話型プロセスごとに 1 つのリモートセッション**: サーバーモード外では、各 Claude Code インスタンスは一度に 1 つのリモートセッションをサポートします。単一のプロセスから複数の同時セッションを実行するには、[サーバーモード](#start-a-remote-control-session)を使用します。
* **ローカルプロセスは実行し続ける必要があります**: Remote Control はローカルプロセスとして実行されます。ターミナルを閉じるか、VS Code を終了するか、または `claude` プロセスを停止すると、セッションは終了します。
* **長時間のネットワーク障害**: マシンが起動しているがおよそ 10 分以上ネットワークに到達できない場合、セッションはタイムアウトしてプロセスは終了します。新しいセッションを開始するには、`claude remote-control` を再度実行します。
* **Ultraplan は Remote Control を切断します**: [ultraplan](/docs/ja/ultraplan) セッションを開始すると、アクティブな Remote Control セッションが切断されます。両方の機能が claude.ai/code インターフェースを占有し、一度に 1 つだけ接続できるためです。
* **一部のコマンドはローカルのみです**: ターミナルインターフェースでのみ実行されるコマンド（`/plugin` や `/resume` など）は、引数を渡すかどうかに関わらず、ローカル CLI からのみ機能します。以下がモバイルと Web から機能します：
  * テキスト出力コマンド: `/compact`、`/clear`、`/context`、`/usage`、`/exit`、`/usage-credits`（CLI 内ダイアログを開く代わりにテキスト形式を実行します）、`/recap`、`/reload-plugins`
  * `/model`、`/effort`、`/fast`、`/color`、`/rename`: 値を引数として渡します。例えば `/model sonnet` または `/effort high` のようにします。モバイルと Web からは、`/model` と `/effort` は、ターミナルピッカーまたはスライダーの代わりに引数を受け取ります。
  * `/mcp`、v2.1.166 以降: モバイルアプリからは、ピッカーを開く代わりにサーバーステータスのテキスト概要を返します。Web では、`/mcp` 単独で概要を返す代わりに [claude.ai コネクタ](/docs/ja/mcp#use-mcp-servers-from-claude-ai)のディレクトリを開きます。`reconnect`、`enable`、`disable` [サブコマンド](/docs/ja/commands#all-commands)は両方から機能します。ローカル CLI と異なり、サーバー名なしで `/mcp reconnect` を実行すると、失敗したか認証が必要なすべてのサーバーを再接続します。
  * `/config`、v2.1.181 以降: モバイルアプリからは、`key=value` を渡して設定を行うか、引数なしで実行して設定できるキーのリストを表示します。Web では、`/config` は設定の Claude Code セクションを開く代わりに、コマンドの後のテキストを無視します。

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

<h3 id="remote-control-requires-a-claude-ai-subscription">
  「Remote Control には claude.ai サブスクリプションが必要です」
</h3>

claude.ai アカウントで認証されていません。`claude auth login` を実行して claude.ai オプションを選択してください。`ANTHROPIC_API_KEY` が環境に設定されている場合は、最初に設定を解除してください。

v2.1.206 より前では、サインアウト状態で `/remote-control` を実行すると、このメッセージの代わりに `Unknown command: /remote-control` が報告されていました。

<h3 id="remote-control-requires-a-full-scope-login-token">
  「Remote Control には完全スコープのログイントークンが必要です」
</h3>

`claude setup-token` または `CLAUDE_CODE_OAUTH_TOKEN` 環境変数からの長命トークンで認証されています。これらのトークンは推論のみに制限されており、Remote Control セッションを確立できません。代わりに `claude auth login` を実行して、完全スコープのセッショントークンで認証してください。

<h3 id="unable-to-determine-your-organization-for-remote-control-eligibility">
  「Remote Control 適格性のための組織を決定できません」
</h3>

キャッシュされたアカウント情報が古いまたは不完全です。`claude auth login` を実行して更新してください。

<h3 id="remote-control-is-not-yet-enabled-for-your-account">
  「Remote Control はまだアカウントで有効になっていません」
</h3>

Remote Control ロールアウトがアカウントに到達していないか、キャッシュされた権利が古い可能性があります。最近プランを変更した場合は、`claude auth logout` を実行してから `claude auth login` を実行して更新してください。`claude doctor` を実行して、どの個別の適格性チェックが失敗したかを確認してください。環境変数の競合、到達不可能なチェック、および組織ポリシーはそれぞれ独自のメッセージを生成するため、このエラーはロールアウトゲート自体を意味します。

<h3 id="couldn’t-verify-remote-control-eligibility">
  「Remote Control 適格性を確認できませんでした」
</h3>

Claude Code は Remote Control がアカウントで有効になっているかどうかを確認するためにフィーチャーフラグサービスに到達できませんでした。通常、オフラインであるか、プロキシがリクエストをブロックしているためです。ネットワークアクセスが可能になったら再度実行するか、詳細については `claude doctor` を実行してください。関連メッセージ「組織の Remote Control ポリシーを確認できませんでした」は同じ原因を持ち、同じ修正があります。両方のメッセージは v2.1.178 で追加されました。

<h3 id="remote-control-is-only-available-when-using-claude-via-api-anthropic-com">
  「Remote Control は Claude 経由で api.anthropic.com を使用している場合にのみ利用可能です」
</h3>

セッションが Anthropic API に直接通信していないため、ペアリングする claude.ai バックエンドがありません。これは Amazon Bedrock、Google Cloud の Agent Platform、および Microsoft Foundry で発生します。v2.1.196 以降、[`ANTHROPIC_BASE_URL`](/docs/ja/env-vars) が `api.anthropic.com` 以外のホスト（[LLM ゲートウェイ](/docs/ja/llm-gateway)やプロキシなど）を指している場合にも発生します。claude.ai でサインインしている場合でも同様です。`ANTHROPIC_BASE_URL` を設定解除してセッションを再開し、Remote Control を使用してください。

<h3 id="remote-control-is-disabled-by-your-organization’s-policy">
  「Remote Control は組織のポリシーで無効になっています」
</h3>

このエラーには 4 つの異なる原因があります。最初に `/status` を実行して、使用しているログイン方法とサブスクリプションを確認してください。

* **API キーまたは Console アカウントで認証されている**: Remote Control は claude.ai OAuth が必要です。`/login` を実行して claude.ai オプションを選択してください。`ANTHROPIC_API_KEY` が環境に設定されている場合は、設定を解除してください。
* **Team または Enterprise 管理者が有効にしていない**: Remote Control はこれらのプランではデフォルトでオフになっています。管理者は [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) で **Remote Control** トグルをオンにして有効にできます。このトグルはサーバー側の組織設定です。
* **管理者トグルがグレーアウトしている**: 組織には Remote Control と互換性のないデータ保持またはコンプライアンス設定があります。これは管理パネルから変更することはできません。オプションについて説明するために Anthropic サポートに連絡してください。
* **エラーに `disableRemoteControl` が記載されている**: IT 管理者が [管理設定](/docs/ja/settings#settings-files)を通じてこのデバイスで Remote Control を無効にしています。これは組織全体のトグルとは関係なく行われています。

<h3 id="remote-credentials-fetch-failed">
  「リモート認証情報の取得に失敗しました」
</h3>

Claude Code は Anthropic API から短命の認証情報を取得して接続を確立できませんでした。`--verbose` で再度実行して完全なエラーを確認してください。

```bash theme={null}
claude remote-control --verbose
```

一般的な原因:

* サインインしていない: `claude` を実行し、`/login` を使用して claude.ai アカウントで認証してください。API キー認証は Remote Control ではサポートされていません。
* ネットワークまたはプロキシの問題: ファイアウォールまたはプロキシがアウトバウンド HTTPS リクエストをブロックしている可能性があります。Remote Control はポート 443 で Anthropic API へのアクセスが必要です。
* セッション作成に失敗: `Session creation failed — see debug log` も表示される場合、失敗はセットアップの前の段階で発生しました。サブスクリプションがアクティブであることを確認してください。

<h3 id="couldn’t-reconnect-to-your-remote-control-session">
  「Remote Control セッションに再接続できませんでした」
</h3>

`claude --resume` または `claude --continue` で会話を再開すると、Claude Code はその会話に記録された Remote Control セッションに再接続します。このメッセージは、ネットワーク中断またはサーバーエラーなど、一時的な理由で再接続に失敗したことを意味します。そのため、Claude Code はリモートセッションがまだ存在するかどうかを確認できません。サーバーが前のセッションがもう存在しないことを確認すると、Claude Code はこのメッセージを表示せずに新しい Remote Control セッションを作成します。

ローカルセッションは Remote Control なしで実行を続けます。`/remote-control` を実行して接続を再試行するか、`--resume` なしで Claude Code を開始して新しい Remote Control セッションを作成してください。

v2.1.200 より前では、再接続の失敗により新しい Remote Control セッションが作成され、このメッセージが表示されず、claude.ai/code のセッションリストに余分なセッションが残されていました。

<h3 id="your-organization-requires-trusted-devices-for-remote-control-but-this-device-is-not-enrolled">
  「組織は Remote Control に信頼できるデバイスを要求していますが、このデバイスは登録されていません」
</h3>

組織は [信頼できるデバイス](#trusted-devices)を有効にしており、このマシンはまだ登録されていません。Claude Code で `/login` を実行します。登録はサインインの一部として行われ、別の登録コマンドはありません。

<h3 id="session-expired-for-trusted-device-check">
  「信頼できるデバイスチェックのセッションが期限切れです」
</h3>

サインインが 18 時間以上前です。Claude Code で `/login` を実行するか、claude.ai またはモバイルアプリが Face ID、Touch ID、Windows Hello、またはパスキーで確認するよう求めたときに確認します。[信頼できるデバイス](#trusted-devices)を参照してください。

<h2 id="choose-the-right-approach">
  適切なアプローチを選択する
</h2>

Claude Code offers several ways to work when you're not at your terminal. They differ in what triggers the work, where Claude runs, and how much you need to set up.

|                                                          | Trigger                                                                                        | Claude runs on                                                                               | Setup                                                                                                                                | Best for                                                      |
| :------------------------------------------------------- | :--------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------ |
| [Dispatch](/docs/en/desktop#sessions-from-dispatch)           | Message a task from the Claude mobile app                                                      | Your machine (Desktop)                                                                       | [Pair the mobile app with Desktop](https://support.claude.com/en/articles/13947068)                                                  | Delegating work while you're away, minimal setup              |
| [Remote Control](/docs/en/remote-control)                     | Drive a running session from [claude.ai/code](https://claude.ai/code) or the Claude mobile app | Your machine (CLI or VS Code)                                                                | Run `claude remote-control`                                                                                                          | Steering in-progress work from another device                 |
| [Channels](/docs/en/channels)                                 | Push events from a chat app like Telegram or Discord, or your own server                       | Your machine (CLI)                                                                           | [Install a channel plugin](/docs/en/channels#quickstart) or [build your own](/docs/en/channels-reference)                                      | Reacting to external events like CI failures or chat messages |
| [Slack](/docs/en/slack)                                       | Mention `@Claude` in a team channel                                                            | Anthropic cloud                                                                              | [Install the Slack app](/docs/en/slack#setting-up-claude-code-in-slack) with [Claude Code on the web](/docs/en/claude-code-on-the-web) enabled | PRs and reviews from team chat                                |
| [Self-hosted environments](/docs/en/self-hosted-environments) | Start a [cloud session](/docs/en/claude-code-on-the-web) and pick your organization's environment   | Your organization's infrastructure                                                           | [Deploy runners](/docs/en/self-hosted-environments-quickstart), on Team and Enterprise plans                                              | Cloud sessions that must run inside your network              |
| [Scheduled tasks](/docs/en/scheduled-tasks)                   | Set a schedule                                                                                 | [CLI](/docs/en/scheduled-tasks), [Desktop](/docs/en/desktop-scheduled-tasks), or [cloud](/docs/en/routines) | Pick a frequency                                                                                                                     | Recurring automation like daily reviews                       |

<h2 id="related-resources">
  関連リソース
</h2>

* [Web 上の Claude Code](/docs/ja/claude-code-on-the-web): マシン上ではなく Anthropic が管理するクラウド環境でセッションを実行します
* [Ultraplan](/docs/ja/ultraplan): ターミナルからクラウド計画セッションを起動し、ブラウザで計画を確認します
* [チャネル](/docs/ja/channels): Telegram、Discord、または iMessage をセッションに転送して、Claude が離席中にメッセージに反応するようにします
* [Dispatch](/docs/ja/desktop#sessions-from-dispatch): 電話からタスクをメッセージして、Desktop セッションを生成して処理できます
* [認証](/docs/ja/authentication): `/login` をセットアップし、claude.ai の認証情報を管理します
* [CLI リファレンス](/docs/ja/cli-reference): `claude remote-control` を含むフラグとコマンドの完全なリスト
* [セキュリティ](/docs/ja/security): Remote Control セッションが Claude Code セキュリティモデルにどのように適合するか
* [データ使用](/docs/ja/data-usage): ローカルおよびリモートセッション中に Anthropic API を通じてどのようなデータが流れるか
