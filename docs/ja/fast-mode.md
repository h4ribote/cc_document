> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 高速モードでレスポンスを高速化

> Claude Code で高速モードを切り替えて、Opus のレスポンスを高速化します。

<Note>
  高速モードは[リサーチプレビュー](#research-preview)段階です。機能、価格設定、および利用可能性はフィードバックに基づいて変更される可能性があります。
</Note>

高速モードは Claude Opus の高速構成で、モデルを最大 2.5 倍高速化しますが、トークンあたりのコストは高くなります。迅速な反復やライブデバッグなどのインタラクティブな作業で速度が必要な場合は `/fast` でオンにし、コストがレイテンシーより重要な場合はオフにします。

高速モードは異なるモデルではありません。Claude Opus を使用していますが、コスト効率よりも速度を優先する異なる API 構成です。同じ品質と機能が得られ、レスポンスが高速化されるだけです。高速モードは Opus 4.8 および Opus 4.7 でサポートされています。Sonnet、Haiku、または他のモデルでは利用できません。

<Warning>
  Opus 4.7 の高速モードは 2026 年 6 月 25 日時点で非推奨となり、2026 年 7 月 24 日に削除される予定です。削除後、Opus 4.7 の高速モードリクエストはエラーを返し、標準 Opus 4.7 にフォールバックしません。高速化を維持するには Opus 4.8 に移行してください。
</Warning>

知っておくべきこと：

* Claude Code CLI で `/fast` を使用して高速モードをオンにします。VS Code Extension では高速モードはサポートされていません。
* 高速モード価格は Opus 4.8 で入力/出力あたり $10/$50 MTok、Opus 4.7 で $30/$150 MTok です。
* サブスクリプションプラン（Pro/Max/Team/Enterprise）の Claude Code ユーザーと Claude Console のすべてのユーザーが利用可能です。
* サブスクリプションプラン（Pro/Max/Team/Enterprise）の Claude Code ユーザーの場合、高速モードは使用量クレジットのみで利用可能であり、サブスクリプションレート制限に含まれていません。

<h2 id="toggle-fast-mode">
  高速モードの切り替え
</h2>

高速モードは次のいずれかの方法で切り替えます：

* `/fast` と入力して Tab キーを押してオンまたはオフに切り替える
* [ユーザー設定ファイル](/docs/ja/settings)で `"fastMode": true` を設定する

デフォルトでは、インタラクティブセッションで有効にした高速モードはセッション全体で保持されます。[非インタラクティブモード](/docs/ja/headless)では、`-p` フラグを使用して、`/fast` は [`--settings`](/docs/ja/cli-reference#cli-flags) 値で高速モードを使用して起動されたセッションでのみ機能します。例えば `claude -p --settings '{"fastMode": true}'` のように使用します。その場合、切り替えはそのセッションにのみ適用され、デフォルトとして保存されず、他の非インタラクティブセッションではコマンドが高速モードが利用できないことを報告します。高速モードを各セッションでリセットするように構成できます。詳細は[セッションごとのオプトインが必要](#require-per-session-opt-in)を参照してください。

最高のコスト効率を得るには、会話の途中で切り替えるのではなく、セッションの開始時に高速モードを有効にします。詳細は[コストのトレードオフを理解する](#understand-the-cost-tradeoff)を参照してください。

高速モードを有効にすると：

* 別のモデルを使用している場合、Claude Code は自動的に Opus に切り替わります
* 確認メッセージが表示されます：「Fast mode ON」
* 高速モードがアクティブな間、プロンプトの横に小さい `↯` アイコンが表示されます
* いつでも `/fast` を再度実行して、高速モードがオンかオフかを確認できます

`/fast` を再度実行して高速モードを無効にすると、Opus に留まります。モデルは以前のモデルに戻りません。別のモデルに切り替えるには、`/model` を使用します。

高速モードをサポートしていないモデルに切り替えると、高速モードがオフになります。サポートされている Opus モデルに戻すと、保存された高速モード設定がオンの場合、デフォルトで新しいセッションが開始される同じ設定から、高速モードが再度オンになります。[セッションごとのオプトイン](#require-per-session-opt-in)が構成されている場合、戻しても高速モードは再度オンになりません。`/fast` を実行して再度有効にしてください。保存された設定がオフのセッションでは、高速モードは決してオンになりません。また、`↯` アイコンと「Fast mode ON」確認メッセージは、アクティブになるたびに表示されます。v2.1.208 より前では、戻した後、再度 `/fast` を実行するまで高速モードはオフのままでした。

Opus 4.8 は Claude Code v2.1.154 以降の高速モードのデフォルトです。v2.1.142 から v2.1.153 では、高速モードは Opus 4.7 がデフォルトです。

<h2 id="understand-the-cost-tradeoff">
  コストのトレードオフを理解する
</h2>

高速モードは標準 Opus よりもトークンあたりの価格が高くなります。乗数はモデルによって異なります：

| モデル      | 入力（MTok） | 出力（MTok） |
| -------- | -------- | -------- |
| Opus 4.8 | \$10     | \$50     |
| Opus 4.7 | \$30     | \$150    |

高速モード価格は完全な 1M トークンコンテキストウィンドウ全体で一定です。比較対象となる標準 Opus レートについては、[Claude 価格リファレンス](https://platform.claude.com/docs/ja/about-claude/pricing)を参照してください。

会話で初めて高速モードを有効にすると、会話コンテキスト全体に対して完全な高速モードキャッシュなし入力トークン価格を支払います。会話が進むほど、このコストは高くなるため、最初から高速モードを有効にする方が安くなります。コストは会話ごとに 1 回適用されるため、後で高速モードをオフにしてからオンに切り替えても、再度請求されることはありません。メカニズムについては、[高速モードがプロンプトキャッシュとどのように相互作用するか](/docs/ja/prompt-caching#turning-on-fast-mode)を参照してください。

<h2 id="decide-when-to-use-fast-mode">
  高速モードの使用時期を判断する
</h2>

高速モードはレスポンスレイテンシーがコストより重要なインタラクティブな作業に最適です：

* コード変更の迅速な反復
* ライブデバッグセッション
* 厳しい期限を持つ時間に敏感な作業

標準モードは以下に適しています：

* 速度がそれほど重要でない長い自動タスク
* バッチ処理または CI/CD パイプライン
* コストに敏感なワークロード

<h3 id="fast-mode-vs-effort-level">
  高速モードと努力レベル
</h3>

高速モードと努力レベルはどちらもレスポンス速度に影響しますが、方法が異なります：

| 設定          | 効果                                  |
| ----------- | ----------------------------------- |
| **高速モード**   | 同じモデル品質、低レイテンシー、高コスト                |
| **低い努力レベル** | 思考時間が短い、レスポンスが高速、複雑なタスクでは品質が低下する可能性 |

両方を組み合わせることができます：単純なタスクで最大速度を得るために、低い[努力レベル](/docs/ja/model-config#adjust-effort-level)で高速モードを使用します。

<h2 id="requirements">
  要件
</h2>

高速モードには以下のすべてが必要です：

* **Anthropic API またはサブスクリプションのみ**：高速モードは Anthropic Console API および使用量クレジットを使用する Claude サブスクリプションプランで利用可能です。Amazon Bedrock、Google Cloud の Agent Platform、Microsoft Foundry、または AWS 上の Claude Platform では利用できません。
* **使用量クレジットが有効**：アカウントで使用量クレジットが有効になっている必要があります。これにより、プランに含まれる使用量を超えて請求できます。個人アカウントの場合、[Console 請求設定](https://platform.claude.com/settings/billing)で有効にします。Team および Enterprise の場合、管理者が組織の使用量クレジットを有効にする必要があります。

<Note>
  高速モード使用量は、プランに残りの使用量がある場合でも、使用量クレジットに直接請求されます。これは、高速モードトークンがプランに含まれる使用量にカウントされず、最初のトークンから高速モード料金で請求されることを意味します。
</Note>

* **Team および Enterprise の所有者による有効化**：高速モードは Team および Enterprise 組織ではデフォルトで無効になっています。ユーザーがアクセスできるようにするには、所有者が明示的に[高速モードを有効にする](#enable-fast-mode-for-your-organization)必要があります。

<Note>
  組織で高速モードが有効になっていない場合、`/fast` コマンドは「Fast mode has been disabled by your organization.」と表示されます。組織の [`availableModels`](/docs/ja/model-config#restrict-model-selection) 許可リストが高速モード Opus モデルを除外している場合、`/fast` は「is not in your organization's allowed models」で拒否されます。例外は、高速モードをサポートする許可された Opus モデルで既に実行中のセッションです：`/fast` はモデルを切り替える代わりに現在のモデルで高速モードを有効にします。
</Note>

<h3 id="enable-fast-mode-for-your-organization">
  組織の高速モードを有効にする
</h3>

組織で高速モードを有効にする場所は、組織が使用する製品によって異なります：

* **Console**（API カスタマー）：管理者が [Claude Code preferences](https://platform.claude.com/claude-code/preferences) で有効にします
* **Claude AI**（Team および Enterprise）：所有者が [Admin Settings > Claude Code](https://claude.ai/admin-settings/claude-code) で有効にします

高速モードを完全に無効にするもう 1 つのオプションは、`CLAUDE_CODE_DISABLE_FAST_MODE=1` を設定することです。[環境変数](/docs/ja/env-vars)を参照してください。

<h3 id="require-per-session-opt-in">
  セッションごとのオプトインが必要
</h3>

デフォルトでは、ユーザーがインタラクティブセッションで有効にした高速モードはセッション全体で保持されます：将来のセッションでもオンのままです。これを変更するには、任意の[設定ファイル](/docs/ja/settings#settings-files)で `fastModePerSessionOptIn` を `true` に設定します。これにより、各セッションは高速モードがオフで開始され、ユーザーが `/fast` で明示的に有効にする必要があります。[Team](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=fast_mode_teams#team-&-enterprise) または [Enterprise](https://anthropic.com/contact-sales?utm_source=claude_code\&utm_medium=docs\&utm_content=fast_mode_enterprise) プランの所有者は、[サーバー管理設定](/docs/ja/server-managed-settings)を通じて組織全体にこれをデプロイできます。

```json theme={null}
{
  "fastModePerSessionOptIn": true
}
```

これは、ユーザーが複数の同時セッションを実行する組織でコストを制御するのに役立ちます。ユーザーは速度が必要な場合でも `/fast` で高速モードを有効にできますが、新しいセッションの開始時にリセットされます。ユーザーの高速モード設定は保存されたままなので、この設定を削除するとデフォルトの永続的な動作が復元されます。

<h2 id="handle-rate-limits">
  レート制限の処理
</h2>

高速モードは標準 Opus とは別のレート制限があります。Opus 4.8 と Opus 4.7 の高速モードは同じレート制限プールを共有します：どちらかのモデルでの使用は同じ制限から引き出されます。高速モードレート制限に達するか、使用量クレジットが不足した場合：

1. 高速モードは自動的に標準速度にフォールバックします
2. `↯` アイコンがグレーに変わってクールダウンを示します
3. 標準速度と価格で作業を続けます
4. クールダウンが終了すると、高速モードは自動的に再度有効になります

クールダウンを待つ代わりに高速モードを手動で無効にするには、`/fast` を再度実行します。

<h2 id="research-preview">
  リサーチプレビュー
</h2>

高速モードはリサーチプレビュー機能です。これは以下を意味します：

* 機能はフィードバックに基づいて変更される可能性があります
* 利用可能性と価格設定は変更される可能性があります
* 基盤となる API 構成は進化する可能性があります

通常の Anthropic サポートチャネルを通じて問題またはフィードバックを報告してください。

<h2 id="see-also">
  関連項目
</h2>

* [モデル構成](/docs/ja/model-config)：モデルを切り替えて努力レベルを調整する
* [コストを効果的に管理する](/docs/ja/costs)：トークン使用量を追跡してコストを削減する
* [ステータスラインの構成](/docs/ja/statusline)：モデルとコンテキスト情報を表示する
