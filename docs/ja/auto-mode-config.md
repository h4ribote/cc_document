> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# オートモードの設定

> オートモード分類器に、組織が信頼するリポジトリ、バケット、ドメインを指定します。環境コンテキストを設定し、デフォルトのブロックおよび許可ルールをオーバーライドし、オートモード CLI サブコマンドで有効な設定を検査します。

[オートモード](/docs/ja/permission-modes#eliminate-prompts-with-auto-mode)を使用すると、Claude Code は、ツール呼び出しを分類器にルーティングして、不可逆的、破壊的、または環境外を対象とした操作をブロックすることで、定期的な権限プロンプトなしで実行できます。拒否および明示的な質問ルールは分類器の前に評価され、引き続きブロックまたはプロンプトを表示します。`autoMode` 設定ブロックを使用して、その分類器に組織が信頼するリポジトリ、バケット、ドメインを指定し、定期的な内部操作のブロックを停止させます。

<Note>
  オートモードは、Anthropic API、Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、およびサインイン済みの[Claude アプリゲートウェイ](/docs/ja/claude-apps-gateway)セッションを含む、すべてのプロバイダーのすべてのユーザーが利用できます。Claude Code がアカウントでオートモードが利用できないと報告する場合は、[完全な要件](/docs/ja/permission-modes#eliminate-prompts-with-auto-mode)を確認してください。これには、サポートされているモデルと Team および Enterprise プランでのオーナー有効化も含まれます。v2.1.158 から v2.1.206 では、Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、および Claude アプリゲートウェイセッション上のオートモードは `CLAUDE_CODE_ENABLE_AUTO_MODE=1` の設定が必要でしたが、v2.1.207 ではその要件が削除されました。
</Note>

デフォルトでは、分類器は作業ディレクトリと現在のリポジトリの設定されたリモートのみを信頼します。会社のソース管理組織へのプッシュやチームクラウドバケットへの書き込みなどのアクションは、`autoMode.environment` に追加するまでブロックされます。

オートモードを有効にする方法とデフォルトでブロックされるものについては、[権限モード](/docs/ja/permission-modes#eliminate-prompts-with-auto-mode)を参照してください。このページは設定リファレンスです。

このページでは、以下の方法について説明します。

* [`permissions.ask`](#common-boundaries)を使用してプッシュおよびプルリクエストの人間チェックポイントを追加する
* [CLAUDE.md、ユーザー設定、管理設定全体でルールを設定する場所を選択する](#where-the-classifier-reads-configuration)
* [`autoMode.environment`](#define-trusted-infrastructure)を使用して信頼できるインフラストラクチャを定義する
* [デフォルトがパイプラインに適さない場合、ブロックおよび許可ルールをオーバーライドする](#override-the-block-and-allow-rules)
* [`autoMode.classifyAllShell`](#route-all-shell-commands-through-the-classifier)を使用してすべてのシェルコマンドを分類器にルーティングする
* [`claude auto-mode`](#inspect-the-defaults-and-your-effective-config)サブコマンドで有効な設定を検査する
* [拒否を確認](#review-denials)して、次に何を追加するかを把握する

<h2 id="common-boundaries">
  一般的な境界
</h2>

オートモードでは、デフォルトでワーキングブランチへのプッシュ、リポジトリのデフォルトブランチへの定期的なプッシュ、およびプルリクエストの作成が許可されます。分類器は、フォースプッシュやセットアップしたレビューを回避するコンテンツなど、リスクを伴うプッシュのみをブロックします。すべてのプッシュまたはプルリクエストの前に人間によるチェックポイントが必要な場合は、権限ルールを追加してください。以下のレシピは、他のすべてのアクションに対してオートモードを有効に保ちます。

最も直接的なメカニズムは [`permissions.ask`](/docs/ja/permissions#permission-rule-syntax) です。以下のようなコンテンツスコープの ask ルールは、分類器の前に評価され、オートモードでも常に権限プロンプトを強制します。これは、明示的な ask ルールがそのアクションに対してプロンプトを表示する意図を示しているためです。[settings](/docs/ja/settings#settings-files) にルールを追加してください。

```json theme={null}
{
  "permissions": {
    "ask": [
      "Bash(git push *)",
      "Bash(gh pr create *)"
    ]
  }
}
```

境界がどの程度厳密である必要があるかに応じて、メカニズムを選択してください。

| 境界                | メカニズム                            | オートモードでの動作                                                                                                                                          |
| :---------------- | :------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| アクション前にプロンプト表示    | `permissions.ask`                | 上記のレシピのようなコンテンツスコープのルールに対して常にプロンプトを表示します。分類器は一致するアクションを自動承認することはできません。                                                                              |
| アクションを実行しない       | `permissions.deny`               | 分類器が参照される前にブロックします。分類器もユーザーの意図も、これをオーバーライドすることはできません。                                                                                               |
| このセッションの 1 回限りの境界 | 「レビューするまでプッシュしないでください」のように会話で述べる | 分類器は一致するアクションをブロックしますが、[コンテキストコンパクション](/docs/ja/costs#reduce-token-usage) がそれを述べたメッセージを削除した場合、境界が失われる可能性があります。耐久性のある保証のために ask ルールまたは deny ルールを使用してください。 |

<h2 id="where-the-classifier-reads-configuration">
  分類器が設定を読み込む場所
</h2>

分類器は Claude 自体が読み込む同じ [CLAUDE.md](/docs/ja/memory) コンテンツを読み込むため、プロジェクトの CLAUDE.md に「force push を絶対にしない」のような指示があれば、Claude と分類器の両方を同時に制御します。プロジェクト規約と動作ルールについては、ここから始めてください。

複数のプロジェクトに適用されるルール（信頼できるインフラストラクチャや組織全体の拒否ルールなど）については、`autoMode` 設定ブロックを使用してください。分類器は以下のスコープから `autoMode` を読み込みます。

| スコープ                          | ファイル                                   | 用途                           |
| :---------------------------- | :------------------------------------- | :--------------------------- |
| 1 人の開発者                       | `~/.claude/settings.json`              | 個人の信頼できるインフラストラクチャ           |
| 組織全体                          | [マネージド設定](/docs/ja/server-managed-settings) | すべての開発者に配布される信頼できるインフラストラクチャ |
| `--settings` フラグまたは Agent SDK | インライン JSON                             | 自動化のための呼び出しごとのオーバーライド        |

分類器は `.claude/settings.json` または `.claude/settings.local.json` のプロジェクト設定から `autoMode` を読み込みません。両方のファイルはリポジトリディレクトリに存在するため、チェックインされたリポジトリまたはビルドステップが独自の許可ルールを注入する可能性があります。v2.1.207 より前は、分類器は `.claude/settings.local.json` も読み込んでいました。そのファイルの `autoMode` ブロックを `~/.claude/settings.json` に移動してください。`.claude/settings.local.json` を除外することで、リポジトリがファイルをコミットしたり、ローカルツールまたはビルドステップが書き込んだりする場合も対応できます。

各スコープからのエントリは結合されます。開発者は個人的なエントリで `environment`、`allow`、`soft_deny`、`hard_deny` を拡張できますが、マネージド設定が提供するエントリを削除することはできません。許可ルールは分類器内のソフトブロックルールの例外として機能するため、開発者が追加した `allow` エントリは組織の `soft_deny` エントリをオーバーライドできます。組み合わせは加算的であり、ハードポリシー境界ではありません。

<Note>
  分類器は [権限システム](/docs/ja/permissions) の後に実行される 2 番目のゲートです。ユーザーの意図または分類器の設定に関係なく、絶対に実行してはいけないアクションについては、マネージド設定で `permissions.deny` を使用してください。これは分類器が参照される前にアクションをブロックし、オーバーライドできません。
</Note>

<h2 id="define-trusted-infrastructure">
  信頼できるインフラストラクチャを定義する
</h2>

ほとんどの組織では、`autoMode.environment` が設定する必要がある唯一のフィールドです。これは、分類器に、どのリポジトリ、バケット、ドメインが信頼できるかを指定します。分類器はこれを使用して「外部」が何を意味するかを決定するため、リストに記載されていない宛先は潜在的な流出ターゲットです。

Claude Code v2.1.198 以降、`claude auto-mode defaults` は 3 種類の環境エントリを出力します。v2.1.195 より前のバージョンは、最初の 5 つの信頼スロットのみを出力します。

* **コンテキストスロット**：分類器が他のルールをコンテキストで読み込むように、組織、スタック、セキュリティ体制を説明します。他の 2 種類と異なり、コンテキストスロットはそれらをターゲットにする独自のルールはありません。各スロットはデフォルトで `None configured` または次に記載されている保守的な仮定になります。
  * **Organization**
  * **Primary use of Claude Code**：デフォルトはソフトウェア開発
  * **Cloud provider(s)**
  * **Repository visibility**：リポジトリはリモートホストと名前が別途示さない限り、プライベートと見なされます。または、会話内で分類器が読み込む前のトランスクリプト内の可視性チェックがそれが公開されていることを示している場合。分類器はメッセージと Claude が実行するコマンドを読み込みますが、その出力は読み込みません。そのため、証拠はリポジトリを公開として指定するあなた自身のメッセージなど、読み込める何かである必要があります。`gh repo view` の出力だけではそこに到達しません。トランスクリプト証拠チェックには Claude Code v2.1.200 以降が必要です
  * **Internal sharing / snippet hosting**：パブリックペーストおよび gist サービスは、指定するまで信頼境界の外側として扱われます
  * **Org-specific CLIs**
  * **Secrets management**
  * **Default / protected branches**：`main` と `master` は、他を指定するまで保護されたものとして扱われます
  * **CI/CD deploy targets**
  * **Network posture**
  * **Protected deployment namespaces / environments**：指定するまで、機密リモートターゲットヒューリスティックにフォールバックします
  * **Data retention / declassification**
* **信頼スロット**：分類器が境界内として扱うものを指定します。スロットは「信頼できるリポジトリ」、「ソース管理」、「信頼できる内部ドメイン」、「信頼できるクラウドバケット」、「主要な内部サービス」、および「内部パッケージレジストリ」です。リポジトリとソース管理エントリはデフォルトで作業リポジトリとその設定されたリモートになります。他のすべての信頼スロットはデフォルトで `None configured` になるため、追加するまで他には何も信頼されません。リポジトリの可視性は機密情報のみをスコープします。プライベートリポジトリは機密情報の許容可能な宛先ですが、リポジトリをプライベートにしても、秘密、個人データ、または信頼されたデータをそこにクリアすることはなく、分類器は、作業リポジトリの外から移植、再ポイント、または最初に読み込まれたコンテンツを、そのリポジトリ自体の作業として扱いません。このスコープには Claude Code v2.1.203 以降が必要です。
* **感度スロット**：保護ルールが高リスクとして扱うものを指定します。スロットは「機密データの場所とオーディエンス」、「機密リモートターゲット」、および「保護された IaC スコープ」です。各スロットはデフォルトで広いヒューリスティックになります。例えば、名前に `prod` または `production` を含むホストまたはネームスペースを機密リモートターゲットとして扱うため、保護ルールは何も設定する前にアクティブになります。感度スロットで具体的なターゲットを指定すると、これらのルールはヒューリスティックではなく指定されたターゲットに適用されます。

デフォルトと一緒に独自のエントリを追加するには、配列にリテラル文字列 `"$defaults"` を含めます。デフォルトエントリはその位置に挿入されるため、カスタムエントリはそれらの前後に配置できます。

次の例は、デフォルトエントリを保持し、組織のリポジトリ、バケット、ドメイン、サービスを追加しています。

```json theme={null}
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.example.com/acme-corp and all repos under it",
      "Trusted cloud buckets: s3://acme-build-artifacts, gs://acme-ml-datasets",
      "Trusted internal domains: *.corp.example.com, api.internal.example.com",
      "Key internal services: Jenkins at ci.example.com, Artifactory at artifacts.example.com"
    ]
  }
}
```

エントリは散文であり、正規表現またはツールパターンではありません。分類器はそれらを自然言語ルールとして読み込みます。新しいエンジニアにインフラストラクチャを説明する方法で記述してください。十分な環境セクションは以下をカバーします。

* **組織**：会社名と Claude Code が主に使用される用途（ソフトウェア開発、インフラストラクチャ自動化、データエンジニアリングなど）
* **ソース管理**：開発者がプッシュするすべての GitHub、GitLab、または Bitbucket 組織
* **クラウドプロバイダーと信頼できるバケット**：Claude が読み取りおよび書き込みできるバケット名またはプレフィックス
* **信頼できる内部ドメイン**：ネットワーク内の API、ダッシュボード、サービスのホスト名（`*.internal.example.com` など）
* **主要な内部サービス**：CI、アーティファクトレジストリ、内部パッケージインデックス、インシデント対応ツール
* **内部パッケージレジストリ**：インストールがルーティングされるべき private npm、PyPI、またはその他のレジストリ。パブリックレジストリをバイパスするインストールはブロックされます
* **機密データの場所とオーディエンス**：個人データ、機密ビジネスデータ、認証情報、規制対象データ、または同様に機密性の高い情報を保持するバケット、データベース、またはパス。各場所のデータが共有される可能性があるオーディエンス。分類器がコンテンツから推測する代わりにこれらの場所を保護します。Claude Code v2.1.195 から v2.1.197 はこのエントリを PII / 規制対象データの場所として指定し、オーディエンスディメンションなしで個人データまたは規制対象データを保持する場所のみをカバーします
* **機密リモートターゲット**：本番環境としてカウントされるネームスペース、ホスト、またはコンテナ。リモートシェルとポートフォワードはこれらへの明示的な承認が必要です
* **保護された IaC スコープ**：apply または destroy が常にあなたが変更を指定する必要があるインフラストラクチャリソース
* **追加コンテキスト**：規制業界の制約、マルチテナントインフラストラクチャ、または分類器がリスクとして扱うべき内容に影響するコンプライアンス要件

内部パッケージレジストリ、機密データの場所とオーディエンス、機密リモートターゲット、および保護された IaC スコープエントリには Claude Code v2.1.195 以降が必要です。以前のバージョンはそれらをプレーンコンテキストとして読み込みますが、それらをターゲットにする組み込みルールはありません。

有用な開始テンプレート。括弧内のフィールドを入力し、適用されない行を削除します。

```json theme={null}
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Organization: {COMPANY_NAME}. Primary use: {PRIMARY_USE_CASE, e.g. software development, infrastructure automation}",
      "Source control: {SOURCE_CONTROL, e.g. GitHub org github.example.com/acme-corp}",
      "Cloud provider(s): {CLOUD_PROVIDERS, e.g. AWS, GCP, Azure}",
      "Trusted cloud buckets: {TRUSTED_BUCKETS, e.g. s3://acme-builds, gs://acme-datasets}",
      "Trusted internal domains: {TRUSTED_DOMAINS, e.g. *.internal.example.com, api.example.com}",
      "Key internal services: {SERVICES, e.g. Jenkins at ci.example.com, Artifactory at artifacts.example.com}",
      "Additional context: {EXTRA, e.g. regulated industry, multi-tenant infrastructure, compliance requirements}"
    ]
  }
}
```

より具体的なコンテキストを提供するほど、分類器はルーチンの内部操作と流出の試みをより良く区別できます。

すべてを一度に入力する必要はありません。合理的なロールアウト：デフォルトから始めて、ソース管理組織と主要な内部サービスを追加します。これにより、独自のリポジトリへのプッシュなど、最も一般的な誤検知が解決されます。次に信頼できるドメインとクラウドバケットを追加します。ブロックが発生したら残りを入力します。

<h2 id="override-the-block-and-allow-rules">
  ブロックルールと許可ルールをオーバーライドする
</h2>

3 つの追加フィールドを使用すると、分類器の組み込みルールリストを置き換えることができます。

* `autoMode.hard_deny`：無条件のセキュリティ境界
* `autoMode.soft_deny`：ユーザーの意図でクリアできる破壊的なアクション
* `autoMode.allow`：ソフトブロックルールの例外

各フィールドは散文説明の配列であり、自然言語ルールとして読み込まれます。分類器の前に実行されるツールパターンベースのハードブロックについては、[`permissions.deny`](/docs/ja/permissions) を使用します。

分類器内では、優先順位は 4 つのレベルで機能します。

* `hard_deny` ルールは無条件にブロックします。ユーザーの意図と `allow` 例外は適用されません。
* `soft_deny` ルールが次にブロックします。ユーザーの意図と `allow` 例外はこれらをオーバーライドできます。
* `allow` ルールは一致する `soft_deny` ルールを例外としてオーバーライドします。
* 明示的なユーザーの意図が残りのソフトブロックをオーバーライドします。ユーザーのメッセージが Claude が実行しようとしている正確なアクションを直接かつ具体的に説明する場合、`soft_deny` ルールが一致しても分類器はそれを許可します。

一般的なリクエストは明示的な意図としてカウントされません。Claude に「リポジトリをクリーンアップする」ように依頼することは force push を認可しませんが、「このブランチを force push する」ように依頼することは認可します。

緩和するには、分類器がデフォルトの例外がカバーしていないルーチンパターンを繰り返しフラグする場合、`allow` に追加します。厳しくするには、環境に固有で、デフォルトが見落としているリスクについて `soft_deny` に追加するか、絶対に越えてはいけないセキュリティ境界について `hard_deny` に追加します。

組み込みルールを保持しながら独自のルールを追加するには、配列にリテラル文字列 `"$defaults"` を含めます。デフォルトルールはその位置に挿入されるため、カスタムルールはそれらの前後に配置でき、リリース全体でビルトインリストが変更されるにつれて更新を継続して継承します。

次の例は、すべての 4 つのリストでデフォルトを保持し、各リストに組織固有のルールを追加しています。

```json theme={null}
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.example.com/acme-corp and all repos under it"
    ],
    "allow": [
      "$defaults",
      "Deploying to the staging namespace is allowed: staging is isolated from production and resets nightly",
      "Writing to s3://acme-scratch/ is allowed: ephemeral bucket with a 7-day lifecycle policy"
    ],
    "soft_deny": [
      "$defaults",
      "Never run database migrations outside the migrations CLI, even against dev databases",
      "Never modify files under infra/terraform/prod/: production infrastructure changes go through the review workflow"
    ],
    "hard_deny": [
      "$defaults",
      "Never send repository contents to third-party code-review APIs"
    ]
  }
}
```

<Danger>
  `environment`、`allow`、`soft_deny`、または `hard_deny` のいずれかを `"$defaults"` なしで設定すると、そのセクション全体のデフォルトリストが置き換わります。`"$defaults"` なしで配列を設定する場合、そのセクションの組み込みルールを破棄します。

  * `soft_deny`：force push、`curl | bash`、本番環境へのデプロイ、およびオートモードバイパスを含むすべての組み込みソフトブロックルール
  * `hard_deny`：組み込みのデータ流出ルール
</Danger>

各セクションは独立して評価されるため、`environment` のみを設定すると、デフォルトの `allow`、`soft_deny`、および `hard_deny` リストはそのままになります。

`"$defaults"` は、リストの完全な所有権を取得する意図がある場合のみ省略します。その場合、`claude auto-mode defaults` を実行して組み込みルールを出力し、それらを設定ファイルにコピーしてから、各ルールを独自のパイプラインとリスク許容度に対して確認します。

<h2 id="route-all-shell-commands-through-the-classifier">
  すべてのシェルコマンドを分類器にルーティングする
</h2>

デフォルトでは、`Bash(npm test)` などの狭い Bash および PowerShell 許可ルールはオートモードに引き継がれ、分類器が実行される前に解決されます。オートモードは、`Bash(*)` またはワイルドカード化されたインタープリターなど、任意のコード実行を許可する広いルールのみを一時停止します。これは、狭いルールが、ルールのプレフィックスが予想しなかったスクリプトパスまたはフラグなど、破壊的な引数を分類器に見られずに通す可能性があることを意味します。

`autoMode.classifyAllShell` を `true` に設定して、オートモードがアクティブな間、すべての Bash および PowerShell 許可ルールを一時停止し、許可リストに関係なく分類器がすべてのシェルコマンドを評価するようにします。

```json theme={null}
{
  "autoMode": {
    "classifyAllShell": true
  }
}
```

これはレイテンシーをカバレッジと交換します。許可ルールが即座に承認したコマンドは、分類器の決定を待つようになり、各シェルコマンドは分類器呼び出しとしてカウントされます。

この設定はオートモードがアクティブな間のみ適用され、他の権限モードでは許可ルールは通常通り動作します。

<Note>
  `autoMode.classifyAllShell` には Claude Code v2.1.193 以降が必要です。以前のバージョンはキーを無視し、狭いシェル許可ルールをオートモードに引き継ぎ続けます。
</Note>

<h2 id="inspect-the-defaults-and-your-effective-config">
  デフォルトと有効な設定を確認する
</h2>

3 つの CLI サブコマンドは、設定の検査と検証に役立ちます。

組み込みの `environment`、`allow`、`soft_deny`、および `hard_deny` ルールを JSON として出力します。

```bash theme={null}
claude auto-mode defaults
```

1 つのルールの完全な文言を `jq` にパイプすることなく読むには、`--label` をルールのラベルの開始部分（例えば `claude auto-mode defaults --label 'Git Destructive'`）と共に渡します。マッチングは各ルールのラベルに対する大文字と小文字を区別しないプレフィックスであり、マッチするセクションがない場合は空のリストとして出力されます。Claude Code v2.1.208 以降が必要です。

分類器が実際に使用する内容を JSON として出力します。設定が設定されている場合はそれを適用し、そうでない場合はデフォルトを適用します。

```bash theme={null}
claude auto-mode config
```

カスタム `allow`、`soft_deny`、および `hard_deny` ルールに関する AI フィードバックを取得します。

```bash theme={null}
claude auto-mode critique
```

設定を保存した後、`claude auto-mode config` を実行して、有効なルールが期待通りであることを確認します。`"$defaults"` が展開されて配置されます。カスタムルールを記述した場合、`claude auto-mode critique` はそれらを確認し、曖昧、冗長、または誤検知を引き起こす可能性があるエントリにフラグを付けます。

組み込みルールを削除または書き直す必要がある場合は、`claude auto-mode defaults` の出力をファイルに保存し、リストを編集して、結果を設定ファイルの `"$defaults"` の代わりに貼り付けます。

<h2 id="review-denials">
  拒否を確認する
</h2>

オートモードがツール呼び出しを拒否すると、拒否は `/permissions` の「最近拒否されたもの」タブに記録されます。拒否されたアクションで `r` を押してリトライ用にマークします。ダイアログを終了すると、Claude Code はモデルにそのツール呼び出しを再試行できることを伝えるメッセージを送信し、会話を再開します。

Claude Code v2.1.193 以降では、各拒否の分類器の理由がトランスクリプト内のブロックされたツール呼び出しの横、拒否通知内、および「最近拒否されたもの」タブの各エントリの下に表示されます。理由を使用して、修正が `environment` エントリ、`allow` 例外、または次のメッセージで明示的な意図で再試行することかを決定します。

同じ宛先への繰り返しの拒否は、通常、分類器がコンテキストを欠いていることを意味します。その宛先を `autoMode.environment` に追加し、`claude auto-mode config` を実行して、それが有効になったことを確認します。

プログラムで拒否に対応するには、[`PermissionDenied` フック](/docs/ja/hooks#permissiondenied)を使用します。

<h2 id="see-also">
  関連項目
</h2>

* [権限モード](/docs/ja/permission-modes#eliminate-prompts-with-auto-mode)：オートモードとは何か、デフォルトでブロックされる内容、有効にする方法
* [管理設定](/docs/ja/server-managed-settings)：組織全体に `autoMode` 設定をデプロイ
* [権限](/docs/ja/permissions)：分類器が実行される前に適用される許可、質問、拒否ルール
* [設定](/docs/ja/settings)：`autoMode` キーを含む完全な設定リファレンス
