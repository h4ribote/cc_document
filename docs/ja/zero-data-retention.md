> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# ゼロデータ保持

> Claude for Enterprise での Claude Code のゼロデータ保持（ZDR）について、スコープ、無効化される機能、有効化のリクエスト方法を学びます。

ゼロデータ保持（ZDR）は、Claude for Enterprise を通じて使用される Claude Code で利用可能です。ZDR が有効になると、Claude Code セッション中に生成されたプロンプトとモデル応答はリアルタイムで処理され、法令遵守またはミスユース対策が必要な場合を除き、応答が返された後は Anthropic によって保存されません。

<Note>
  ZDR は標準的な Claude for Enterprise プランに含まれておらず、管理者設定から有効化することはできません。適格なアカウントで利用可能であり、Anthropic による個別の有効化が必要です。組織が ZDR を必要とする場合は、[営業に連絡](https://www.anthropic.com/contact-sales?utm_source=claude_code\&utm_medium=docs\&utm_content=zero_data_retention_request)するか、Anthropic アカウントチームに連絡して適格性を確認してください。
</Note>

Claude for Enterprise 上の ZDR により、エンタープライズカスタマーは Claude Code をゼロデータ保持で使用し、管理機能にアクセスできます：

* ユーザーごとのコスト管理
* [Analytics](/docs/ja/analytics) ダッシュボード
* [Server-managed settings](/docs/ja/server-managed-settings)
* 監査ログ

Claude for Enterprise 上の Claude Code の ZDR は、Anthropic の直接プラットフォームにのみ適用されます。Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry 上の Claude デプロイメントについては、これらのプラットフォームのデータ保持ポリシーを参照してください。

<h2 id="zdr-scope">
  ZDR スコープ
</h2>

ZDR は Claude for Enterprise 上の Claude Code 推論をカバーします。

<Warning>
  ZDR は組織ごとに有効化されます。新しい各組織では、Anthropic アカウントチームによって ZDR を個別に有効化する必要があります。ZDR は同じアカウントの下に作成された新しい組織に自動的に適用されません。新しい組織に対して ZDR を有効化するには、アカウントチームに連絡してください。
</Warning>

<h3 id="what-zdr-covers">
  ZDR がカバーする内容
</h3>

ZDR は Claude for Enterprise 上の Claude Code を通じて行われたモデル推論呼び出しをカバーします。ターミナルで Claude Code を使用する場合、送信するプロンプトと Claude が生成する応答は Anthropic によって保持されません。これは、ZDR 組織で利用可能なすべてのモデルに適用されます。一部のモデルはデータ保持を必要とし、ZDR では利用できません。[ZDR でのモデル利用可能性](#model-availability-under-zdr)を参照してください。

<h3 id="what-zdr-does-not-cover">
  ZDR がカバーしない内容
</h3>

ZDR は、ZDR が有効化されている組織であっても、以下には適用されません。これらの機能は[標準データ保持ポリシー](/docs/ja/data-usage#data-retention)に従います：

| 機能                    | 詳細                                                                                                                                |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| claude.ai 上のチャット      | Claude for Enterprise ウェブインターフェース経由のチャット会話は ZDR でカバーされません。                                                                        |
| Cowork                | Cowork セッションは ZDR でカバーされません。                                                                                                      |
| Claude Code Analytics | プロンプトまたはモデル応答を保存しませんが、アカウントメールや使用統計などの生産性メタデータを収集します。貢献メトリクスは ZDR 組織では利用できません。[analytics ダッシュボード](/docs/ja/analytics)は使用メトリクスのみを表示します。 |
| ユーザーとシート管理            | アカウントメールやシート割り当てなどの管理データは標準ポリシーの下で保持されます。                                                                                         |
| サードパーティ統合             | サードパーティツール、MCP servers、またはその他の外部統合によって処理されたデータは ZDR でカバーされません。これらのサービスのデータ処理慣行を独立して確認してください。                                      |

<h2 id="features-disabled-under-zdr">
  ZDR の下で無効化される機能
</h2>

Claude for Enterprise 上の Claude Code 組織に対して ZDR が有効化されると、プロンプトまたは完了を保存する必要がある特定の機能はバックエンドレベルで自動的に無効化されます：

| 機能                                                    | 理由                                                   |
| ----------------------------------------------------- | ---------------------------------------------------- |
| [Web 上の Claude Code](/docs/ja/claude-code-on-the-web)      | 会話履歴のサーバー側ストレージが必要です。                                |
| Desktop アプリからの[クラウドセッション](/docs/ja/desktop#cloud-sessions) | プロンプトと完了を含む永続的なセッションデータが必要です。                        |
| [Artifacts](/docs/ja/artifacts)                            | Anthropic が運用するインフラストラクチャに公開されたページコンテンツを保存する必要があります。 |
| フィードバック送信（`/feedback`）                                | フィードバックを送信すると、会話データが Anthropic に送信されます。              |
| [Remote Control](/docs/ja/remote-control)                  | Anthropic サーバーにセッショントランスクリプトを保存して、デバイス間で会話を同期します。    |

これらの機能はクライアント側の表示に関係なく、バックエンドでブロックされます。Claude Code ターミナルの起動中に無効化された機能が表示される場合、それを使用しようとするとエラーが返され、組織のポリシーがそのアクションを許可していないことが示されます。

プロンプトまたは完了を保存する必要がある場合、将来の機能も無効化される可能性があります。

<h3 id="model-availability-under-zdr">
  ZDR の下でのモデルの利用可能性
</h3>

Claude Fable 5 は、ゼロデータ保持が有効化されている組織では利用できません。このモデルクラスは[データ保持が必要](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#model-specific-data-retention-requirements)であるため、ZDR 組織からのリクエストはそれによって処理することができません。モデルは ZDR 組織の `/model` ピッカーに表示されないか、ZDR を無効化する必要があることを示す通知付きで無効化として表示され、クライアント設定に関係なくサーバーはそれに対するリクエストを拒否します。

その他のモデルは ZDR の下で利用可能なままです。Fable 5 はデフォルトモデルではなく、利用可能な場所では Fable 5 に解決される `best` エイリアスは、ZDR 組織を含む利用できない場所では Opus に解決されます。

<h2 id="data-retention-for-policy-violations">
  ポリシー違反のためのデータ保持
</h2>

ZDR が有効化されている場合でも、法律で必要な場合または Usage Policy 違反に対処するために、Anthropic はデータを保持する場合があります。セッションがポリシー違反でフラグが立てられた場合、Anthropic は関連する入力と出力を最大 2 年間保持する場合があり、これは Anthropic の標準 ZDR ポリシーと一致しています。

<h2 id="request-zdr">
  ZDR をリクエストする
</h2>

Claude for Enterprise 上の Claude Code に対して ZDR をリクエストするには、[営業に連絡](https://www.anthropic.com/contact-sales?utm_source=claude_code\&utm_medium=docs\&utm_content=zero_data_retention_request)するか、Anthropic アカウントチームに連絡してください。アカウントチームが内部でリクエストを送信し、Anthropic は適格性を確認した後、組織に対して ZDR を確認して有効化します。すべての有効化アクションは監査ログに記録されます。

現在、従量課金制 API キーを介して Claude Code に対して ZDR を使用している場合、Claude for Enterprise に移行して、Claude Code の ZDR を維持しながら管理機能にアクセスできます。移行を調整するには、アカウントチームに連絡してください。
