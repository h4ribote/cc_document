> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 組織向けプラグインを推奨する

> マーケットプレイスプラグインエントリに関連性ブロックを追加して、ユーザーの作業が一致したときに Claude Code がそれらを提案するようにします。

組織向けプラグインマーケットプレイスを運営している場合、ユーザーが何に取り組んでいるかに基づいて、Claude Code が特定のプラグインをユーザーに提案するようにできます。`marketplace.json` のプラグインエントリに `relevance` ブロックを追加してから、マネージド設定でマーケットプレイスをホワイトリストに登録します。ユーザーのセッションが宣言されたシグナルのいずれかと一致すると、Claude Code はそのプラグインのインストール提案を表示します。

マーケットプレイスで宣言された提案は、[マネージド設定](/docs/ja/settings#settings-files)を通じてマーケットプレイスごとにオプトインです。管理者がそれを許可リストに追加するまで、マーケットプレイスの `relevance` 宣言は提案を生成しません。これには公式の Anthropic マーケットプレイスも含まれます。Claude Code には、この許可リストとは無関係の組み込み提案も 1 つ含まれています。その提案とすべてのマーケットプレイス宣言の提案は、[`spinnerTipsEnabled`](/docs/ja/settings#available-settings) が `false` に設定されている場合は無効になります。

この機能には Claude Code v2.1.152 以降が必要です。古いクライアントは `relevance` フィールドを無視します。

このページはマーケットプレイス運営者とエンタープライズ管理者向けです。プラグインのインストールを探している場合は、[プラグインの検出とインストール](/docs/ja/discover-plugins)を参照してください。

<h2 id="how-it-works">
  仕組み
</h2>

`marketplace.json` の各プラグインエントリは `relevance` オブジェクトを含むことができます。このオブジェクトはトピックと 1 つ以上のシグナルを指定します。シグナルは、作業ディレクトリや Claude が読んだファイルなど、現在のセッションに対して Claude Code がテストするパターンです。

シグナルマッチングはユーザーのマシン上でローカルに行われます。マッチングはネットワークトラフィックを追加せず、どのシグナルが一致したか、またはそれらの値を Anthropic またはマーケットプレイスオペレーターに報告しません。

シグナルが一致し、プラグインがまだインストールされていない場合、Claude Code はプラグインを 3 つの場所に表示します。

* **スピナーチップ**: Claude が応答している間、スピナーの下に「*topic* で作業していますか？*plugin* プラグインをインストール」というメッセージが `/plugin install` コマンドとともに表示されます。
* **セッション開始提案**: `cwd` シグナルが作業ディレクトリと一致する場合、最初のターンの前に「`plugin suggestion: <name>@<marketplace> · /plugin`」という 1 行の通知が表示されます。このサーフェスには Claude Code v2.1.153 以降が必要です。
* **`/plugin` Discover タブ**: プラグインは「このディレクトリで推奨」または「stripe コマンドで推奨」などの注釈とともに Discover リストの上部に固定されます。このサーフェスには Claude Code v2.1.154 以降が必要です。

スピナーチップとセッション開始通知はスピナーチップシステムの一部です。ユーザーまたはプロジェクトが `spinnerTipsEnabled` を `false` に設定した場合、または `excludeDefault` を使用してカスタム `spinnerTipsOverride` が設定されている場合、両方とも無効になります。Discover タブピンはチップ設定とは無関係です。

Claude Code はプラグインを自動的にインストールしません。ユーザーが常に確認します。

<h2 id="add-relevance-to-a-plugin-entry">
  プラグインエントリに関連性を追加
</h2>

プラグインの `marketplace.json` エントリに `relevance` オブジェクトを追加します。次の例は、Claude が `.tf` ファイルを読むか、Claude が `terraform` を実行するときに `terraform-helpers` プラグインが関連していることを宣言しています。

```json theme={null}
{
  "name": "acme-corp-plugins",
  "owner": { "name": "Acme Platform Team" },
  "plugins": [
    {
      "name": "terraform-helpers",
      "source": "./plugins/terraform-helpers",
      "description": "Acme conventions and helpers for Terraform",
      "relevance": {
        "topic": "Terraform",
        "signals": {
          "cli": ["terraform"],
          "filesRead": ["**/*.tf"]
        }
      }
    }
  ]
}
```

`relevance` ブロックを持つが一致するシグナルがないプラグインは、他のマーケットプレイスエントリのように動作します。Discover リストに通常の位置に表示され、スピナーチップとして表示されることはありません。

<h2 id="field-reference">
  フィールドリファレンス
</h2>

<h3 id="relevance">
  `relevance`
</h3>

| フィールド     | 型      | 説明                                                                                                                                                                             |
| :-------- | :----- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `topic`   | string | オプション。スピナーチップの「*topic* で作業していますか？」を埋める句。多くの場合、製品名（例：`Stripe`）。プラグイン名がトピックとして自然に読めない場合は、`design` などのドメインを使用します。デフォルトは、各ハイフンセグメントが大文字化されたプラグイン名です。セッション開始通知はこの値を使用しません。最大 64 文字。 |
| `signals` | object | プラグインが関連しているかを判断するマッチャー。プラグインが提案可能であるには、少なくとも 1 つのシグナルが必要です。以下の表を参照してください。                                                                                                     |

<h3 id="relevance-signals">
  `relevance.signals`
</h3>

| フィールド          | 型                | 説明                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| :------------- | :--------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cwd`          | array of strings | セッションの作業ディレクトリに対してマッチされるグロブパターン。絶対パスとしてマッチされ、git リポジトリ内にある場合はリポジトリルートに対する相対パスとしてマッチされます。フォワードスラッシュで正規化され、大文字と小文字を区別しません。すべてのパターンはディレクトリ自体とその下のすべてにマッチするため、`infra`、`infra/`、および `infra/**` は同じように動作します。これは、最初のターンの前のセッション開始時にマッチできる唯一のシグナルです。最大 10 パターン、各 256 文字。                                                                                                                                                                                                                                |
| `cli`          | array of strings | Claude がこのセッションで実行したシェルコマンドからのコマンド名（例：`["stripe"]`）。すべてのプラットフォームに適用されます。Windows 上で PowerShell または Git Bash を通じて実行されたコマンドは同じ方法で記録されます。Claude Code はシェルツール呼び出しごとに 1 つのコマンド名を記録します。先頭の環境変数割り当てと `sudo` の後の最初のトークン。複合コマンドは先頭のコマンドのみを提供するため、`cd infra && terraform plan` は `terraform` ではなく `cd` を記録します。完全一致。最大 10 エントリ、各 64 文字。                                                                                                                                                                     |
| `hosts`        | array of strings | このセッションの Bash コマンドの `http://` または `https://` URL に表示されるホスト名（例：`["api.stripe.com"]`）。スキーム、ポート、またはパスなしの裸のホスト名のみ。完全な大文字と小文字を区別しない一致。最大 20 エントリ、各 128 文字。                                                                                                                                                                                                                                                                                                                                           |
| `filesRead`    | array of strings | Claude がこのセッションで読んだファイルのパスに対してマッチされるグロブパターン（例：`["**/*.tf"]`）。フォワードスラッシュで正規化され、大文字と小文字を区別しません。最大 10 パターン、各 256 文字。                                                                                                                                                                                                                                                                                                                                                                               |
| `manifestDeps` | array of objects | Claude がこのセッションで読んだパッケージマニフェストで宣言された依存関係。各エントリは `{ "file": "...", "pattern": "..." }` です。ここで `file` はマニフェストファイルのパスに対してマッチされた正規表現で、通常は絶対パスとしてセッション状態に記録され、`pattern` はそのファイルの内容に対してマッチされた正規表現です。`file` を末尾にアンカーします（例：JSON エスケープ形式で `[/\\\\]package\\.json$`）。開始アンカー付きパターンは絶対パスと決してマッチしないためです。パスはこのシグナルに対して区切り文字で正規化されないため、Windows パスはバックスラッシュを使用します。512 KB を超えるマニフェストファイルはスキップされます。両方の値は最大 256 文字の JavaScript `RegExp` ソース文字列です。`file` は大文字と小文字を区別しないでマッチします。`pattern` は大文字と小文字を区別します。最大 10 エントリ。 |

`cli`、`hosts`、`filesRead`、および `manifestDeps` シグナルはセッション履歴が必要なため、スピナーチップと Discover タブでのみマッチできます。セッション開始時にマッチできるのは `cwd` のみです。`filesRead` および `manifestDeps` シグナルはセッションの記録されたファイル状態をテストします。これには、Claude が書き込みまたは編集したファイルと自動読み込みされた `CLAUDE.md` メモリファイルも含まれます。

次の例は `manifestDeps` を使用して、Claude が `stripe` に依存する `package.json` を読んだ後に Stripe プラグインを提案します。`file` パターンは `[/\\\\]` を使用するため、フォワードスラッシュとバックスラッシュの両方のパス区切り文字にマッチし、`\\.` はドットがリテラルであることを示します。JSON では、正規表現の各バックスラッシュは 2 回書き込まれます。

```json theme={null}
{
  "name": "stripe-helpers",
  "source": "./plugins/stripe-helpers",
  "relevance": {
    "topic": "Stripe",
    "signals": {
      "manifestDeps": [
        {
          "file": "[/\\\\]package\\.json$",
          "pattern": "\"stripe\"\\s*:"
        }
      ]
    }
  }
}
```

<Note>
  `relevance` および `relevance.signals` の下の未知のフィールドは読み込み時に無視されるため、古い Claude Code クライアントはマーケットプレイスを読み込み続けます。`claude plugin validate` を実行して、それらを警告として表示します。
</Note>

<h2 id="enable-suggestions-in-managed-settings">
  マネージドセッティングで提案を有効にする
</h2>

`marketplace.json` で `relevance` を宣言するだけでは十分ではありません。管理者は、提案がユーザーに表示される前に、[マネージドセッティング](/docs/ja/settings#settings-files)でマーケットプレイスをホワイトリストに登録する必要があります。

マーケットプレイス名を `pluginSuggestionMarketplaces` に追加します。公式 Anthropic マーケットプレイス以外のマーケットプレイスの場合は、同じマネージドセッティングでマーケットプレイスソースを宣言します。その名前の `extraKnownMarketplaces` のエントリとして、または `strictKnownMarketplaces` のエントリとして宣言します。ホワイトリストに登録された名前は、マーケットプレイスが別のソースから登録された場合は無視されます。これにより、関連のないソースが組織全体でプラグインを提案するためにホワイトリストに登録された名前で登録されるのを防ぎます。

次の `managed-settings.json` は GitHub リポジトリから組織マーケットプレイスを登録し、その提案を有効にします。

```json theme={null}
{
  "extraKnownMarketplaces": {
    "acme-corp-plugins": {
      "source": {
        "source": "github",
        "repo": "acme-corp/claude-plugins"
      }
    }
  },
  "pluginSuggestionMarketplaces": ["acme-corp-plugins"]
}
```

公式マーケットプレイスは、その名前が公式 Anthropic ソースからのみ登録できるため、ソース宣言要件から除外されます。名前のみをホワイトリストに登録するだけで十分です。

```json theme={null}
{
  "pluginSuggestionMarketplaces": ["claude-plugins-official"]
}
```

`pluginSuggestionMarketplaces` および [`extraKnownMarketplaces`](/docs/ja/settings#extraknownmarketplaces) の完全な設定詳細については、[セッティングリファレンス](/docs/ja/settings)を参照してください。

<h2 id="what-the-user-sees">
  ユーザーに表示される内容
</h2>

セッション中にシグナルが一致すると、スピナーチップは次のように読みます。

```text theme={null}
Working with Terraform? Install the terraform-helpers plugin:
/plugin install terraform-helpers@acme-corp-plugins
```

セッション開始時に、一致する `cwd` シグナルは 1 行の通知を表示します。

```text theme={null}
plugin suggestion: terraform-helpers@acme-corp-plugins · /plugin
```

特定のプラグインの提案は、スピナーチップとセッション開始通知を合わせて、最大 3 セッションごとに 1 回表示され、プラグインがインストールされると、どちらも繰り返されません。セッション開始通知は、提案が 2 回表示された後、さらに表示されなくなります。

`/plugin` Discover タブでは、プラグインは「このディレクトリで推奨」または「terraform コマンドで推奨」などの一致するシグナルを指定する注釈とともに、他の結果の上に固定されます。Discover タブは特定のプラグインを 1 回固定します。その後のアクセスは通常の順序でリストします。Discover タブピンには Claude Code v2.1.154 以降が必要です。v2.1.152 ではスピナーチップのみが表示されます。セッション開始通知は v2.1.153 で追加されます。

<h2 id="validate-your-marketplace">
  マーケットプレイスを検証する
</h2>

公開する前に、マーケットプレイスディレクトリに対して `claude plugin validate` を実行して、`relevance` ブロックを確認します。

```
claude plugin validate ./my-marketplace
```

バリデーターは `relevance` および `relevance.signals` の下の未知のキーを警告として報告し、`relevance` 値がオブジェクトではないことをフラグし、スキーム、ポート、またはパスを含む `signals.hosts` エントリを拒否します。

<h2 id="see-also">
  関連項目
</h2>

* [プラグインマーケットプレイスを作成および配布する](/docs/ja/plugin-marketplaces): プラグインをホストするマーケットプレイスを構築します
* [CLI からプラグインを推奨する](/docs/ja/plugin-hints): Claude Code のセッションシグナルではなく、独自の CLI からユーザーにプロンプトを表示します
* [セッティング](/docs/ja/settings): `pluginSuggestionMarketplaces` および `extraKnownMarketplaces` の完全なリファレンス
