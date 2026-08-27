> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# advisor ツールで難しい判断をエスカレートする

> メインモデルをより強力な advisor モデルと組み合わせて、タスク中の重要な瞬間に Claude が相談できるようにします。

<Note>
  advisor ツールは実験的機能であり、Anthropic API が必要です。Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、Microsoft Foundry では利用できません。動作、価格設定、および利用可能性は変更される可能性があります。
</Note>

advisor ツールを使用すると、Claude はタスク中の重要な瞬間（アプローチをコミットする前、繰り返し発生するエラーで行き詰まった場合、またはタスク完了を宣言する前など）に、通常はより強力な 2 番目のモデルに相談できます。advisor は、すべてのツール呼び出しと結果を含む完全な会話を受け取り、Claude が続行する前に適用するガイダンスを返します。

advisor は Anthropic インフラストラクチャ上でサーバー側で実行され、[サーバーツール](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)として、サブスクリプションと API 課金の両方のアカウントで利用できます。どのモデルが advisor として機能するかを選択し、Claude がそれをいつ呼び出すかを決定します。

このページでは、advisor を有効にする方法、受け入れられるモデルペアリング、相談中に Claude が表示する内容、および advisor 使用量がどのように課金されるかについて説明します。

<h2 id="when-to-use-the-advisor">
  advisor を使用する場合
</h2>

advisor は、ほとんどのターンが定型的であるが、プラン品質が結果を決定する長い複数ステップのタスクに適しています。例としては、大規模なリファクタリング、エラーが繰り返し発生するデバッグセッション、および Claude が完了を宣言する前に独立して確認したいタスクが挙げられます。

計画する必要がほとんどない短いタスク、またはすべてのターンで最強のモデルが必要な作業では、価値が低くなります。その場合は、[メインモデルを切り替える](/docs/ja/model-config#setting-your-model)か、[advisor が opusplan およびサブエージェントとどのように比較されるか](#compare-with-related-features)を参照して、2 番目の意見を得る他の方法を確認してください。

<h2 id="enable-the-advisor">
  advisor を有効にする
</h2>

advisor モデルは 3 つの方法で設定できます。

* **`/advisor` コマンド**：セッション中に advisor を設定または変更し、デフォルトとして保存します
* **`advisorModel` 設定**：[設定ファイル](/docs/ja/settings)で永続的なデフォルトを構成します
* **`--advisor` フラグ**：起動時に単一セッションの advisor を設定します

これらのいずれかが advisor モデルを設定する場合、advisor はメインモデルが[それをサポートしている](#choose-an-advisor-model)セッションで有効になります。使用を停止するには、[advisor をオフにする](#turn-the-advisor-off)を参照してください。

<Note>
  Fable 5 を advisor として使用するには、Claude Code v2.1.170 以降と、組織の [Fable 5 アクセス](/docs/ja/model-config#work-with-fable-5)が必要です。
</Note>

<h3 id="use-the-/advisor-command">
  `/advisor` コマンドを使用する
</h3>

引数なしで `/advisor` を実行して、利用可能な advisor モデルをリストするピッカーを開くか、モデルを直接渡します。

```
/advisor opus
```

選択は、ユーザー設定の `advisorModel` に保存され、セッション全体で保持されます。組織の [`availableModels`](/docs/ja/model-config#restrict-model-selection)許可リストが保存された advisor モデルを除外している場合、`/advisor` で許可されたモデルを選択するまで advisor は呼び出されません。現在のメインモデルが advisor をサポートしていない場合、選択は引き続き保存され、[`/model`](/docs/ja/model-config#setting-your-model)で[互換性のあるメインモデル](#choose-an-advisor-model)に切り替えるときにアクティブになります。

<h3 id="set-advisormodel-in-settings">
  設定で `advisorModel` を設定する
</h3>

セッションを開かずにデフォルトとして advisor を構成するには、設定ファイルで設定します。

```json theme={null}
{
  "advisorModel": "opus"
}
```

<h3 id="use-the-advisor-flag">
  `--advisor` フラグを使用する
</h3>

保存された設定を変更せずに単一セッションの advisor を設定するには、フラグを使用して起動します。

```bash theme={null}
claude --advisor opus
```

フラグはそのセッションの `advisorModel` 設定よりも優先されます。セッションのメインモデルが advisor をサポートしていない場合、またはリクエストされた advisor モデルが組織の [`availableModels`](/docs/ja/model-config#restrict-model-selection)許可リストで除外されている場合、エラーで終了します。

<h2 id="choose-an-advisor-model">
  advisor モデルを選択する
</h2>

advisor はメインモデル以上の機能を持つ必要があります。各メインモデルで受け入れられる advisor は次のとおりです。

| メインモデル              | 受け入れられる advisor         | 注記                                                                                                                    |
| ------------------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Haiku 4.5           | Fable、Opus、Sonnet       | Haiku は advisor を呼び出すことはできますが、advisor として機能することはできません                                                                 |
| Sonnet 4.6          | Fable、Opus、Sonnet       |                                                                                                                       |
| Sonnet 5            | Fable、Opus、Sonnet 5     | Sonnet 4.6 advisor は拒否されます                                                                                            |
| Opus 4.6            | Fable、Opus、Sonnet 5     | Sonnet 5 と Opus 4.6 は同等の機能として評価されるため、Opus 4.6 メインは Sonnet 5 advisor を受け入れます                                           |
| Opus 4.7 以降         | Fable、Opus 4.7、Opus 4.8 | Opus 4.7 と Opus 4.8 は同等の機能として評価されるため、どちらでも他方を advisor として受け入れます。Opus 4.6 または Sonnet 5 advisor を持つ Opus 4.7 メインは拒否されます |
| Fable 5 (v2.1.170+) | Fable                   | Opus または Sonnet advisor は拒否されます                                                                                       |

Fable 5 は、メインモデルとして機能するか advisor として機能するかに関わらず、Claude Code v2.1.170 以降と Fable 5 アクセスが必要です。

advisor を `opus`、`sonnet`、または `fable` として設定します。これらのエイリアスは各モデルの最新バージョンに解決されます。`claude-opus-4-8` などの完全なモデル ID を渡すこともできます。

Subagent は設定された advisor を継承し、独自のモデルに対して同じペアリングチェックを適用します。

Claude Code はリクエストを送信する前にペアリングを検証します。

* advisor がメインモデルより機能が低い場合、advisor はメインモデルのリクエストに接続されません。`/advisor` コマンド出力と通知がこれを表示します。独自のモデルがペアリングを満たす Subagent は引き続き advisor を使用できます。
* メインモデルまたは advisor が Claude Code が認識しないモデルである場合、advisor は接続されません。

<h3 id="common-model-pairings">
  一般的なモデルペアリング
</h3>

受け入れられるペアリングはすべて機能します。これらの組み合わせは、異なる方法でコストと機能のバランスを取ります。

| ペアリング                       | 使用する場合                                                                                                         |
| --------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Sonnet メイン + Opus advisor   | Sonnet は定型的な作業を処理し、計画、曖昧な失敗、および完了チェックを Opus にエスカレートします                                                         |
| Sonnet メイン + Fable advisor  | 決定ポイントで Fable 5 ガイダンスを取得し、Fable 5 全体を実行しません。v2.1.170 以降と Fable 5 アクセスが必要です                                     |
| Haiku メイン + Opus advisor    | 強力な計画を備えた最も低コストのメインモデル。Haiku のみよりもコストが高くなることが予想されますが、メインモデルを Sonnet または Opus に切り替えるよりは低くなります                   |
| Opus メイン + Opus advisor     | 2 番目の Opus が最初の Opus をレビューします。コストよりも独立したチェックが重要な高リスクタスクに役立ちます                                                  |
| Fable メイン + Fable advisor   | Fable 5 が利用可能な場合の最高機能ペアリング（v2.1.170+）。Fable は Opus および Sonnet より上位のティアであるため、Fable メインモデルの唯一の受け入れられた advisor です |
| Sonnet メイン + Sonnet advisor | 定型的な見落としをキャッチするための低コストの 2 番目の意見                                                                                |

<h2 id="when-claude-consults-the-advisor">
  Claude が advisor に相談する場合
</h2>

Claude は advisor をいつ呼び出すかを決定します。アプローチをコミットする前、エラーが繰り返し発生する場合、およびタスク完了を宣言する前に相談する傾向がありますが、タイミングはルールベースではなくモデル駆動です。

プロンプトで相談をリクエストするのと同じ方法で、プロンプトで相談をリクエストできます。例えば、`continue する前に advisor に相談してください`。advisor 呼び出しをキャップまたは強制する設定はありません。タスク中に Claude が advisor に相談する頻度を増やしたい場合は、指示で言及してください。

<h2 id="what-you-see-during-a-session">
  セッション中に表示される内容
</h2>

Claude が advisor を呼び出すと、トランスクリプトに呼び出しが進行中の advisor モデル名を含む `Advising` 行が表示されます。結果が返されると、行は advisor が会話をレビューしたことを確認します。`Ctrl+O` を押して展開し、advisor の完全なガイダンスを読みます。

Claude は一般的に advisor のガイダンスに従いますが、独自の証拠が特定の主張と矛盾する場合は適応します。推奨されたステップが試行時に失敗した場合、またはファイルの内容がアドバイスと矛盾する場合、Claude はガイダンスに無条件に従うのではなく、矛盾を表示します。

advisor は常に完全な会話を受け取り、Claude がタイミングを制御します。より多くの制御または異なる構成については、[advisor がサブエージェントおよび opusplan とどのように比較されるか](#compare-with-related-features)を参照してください。

<h2 id="cost">
  コスト
</h2>

各 advisor 呼び出しは会話を advisor モデルに送信するため、メインモデルの使用に加えて advisor モデルのレートでトークンを消費します。API 課金では、advisor トークンは advisor モデルの入力および出力レートで課金されます。サブスクリプションプランでは、advisor 使用量はプランの使用制限にカウントされます。

Claude は各ターンではなく決定ポイントで advisor を呼び出すため、より高速なメインモデルをより強力な advisor と組み合わせることは、通常、より強力なモデルを全体で実行するよりもコストが低くなります。advisor 使用量は [`/usage`](/docs/ja/costs#track-your-costs)で表示されるセッション合計にカウントされます。

advisor トークンが API レスポンスでどのように報告されるかについては、Claude API ドキュメントの [使用量と課金](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool#usage-and-billing)を参照してください。

<h2 id="impact-on-prompt-caching">
  プロンプトキャッシュへの影響
</h2>

セッション中に advisor を有効または無効にしても、メインモデルの[プロンプトキャッシュ](/docs/ja/prompt-caching)は無効になりません。[モデルまたは努力レベルを変更する](/docs/ja/prompt-caching#actions-that-invalidate-the-cache)とは異なり、`/advisor` を切り替えるとキャッシュされたプレフィックスはそのまま保持され、advisor が返したガイダンスは後のターンでトランスクリプトの一部としてキャッシュされます。

advisor モデル自体の会話の読み取りはキャッシュされません。各 advisor 呼び出しは完全なトランスクリプトを新たに処理し、呼び出し間での再利用はありません。

<h2 id="requirements">
  要件
</h2>

advisor ツールには、以下のすべてが必要です。

* **Anthropic API のみ**：advisor はサーバー実行ツールです。Amazon Bedrock、Claude Platform on AWS、Google Cloud の Agent Platform、または Microsoft Foundry では利用できません。[LLM ゲートウェイ](/docs/ja/llm-gateway)を通じて `ANTHROPIC_BASE_URL` で構成されている場合、利用可能性はゲートウェイがリクエストを Anthropic API に完全に転送するかどうかに依存します。
* **サポートされているメインモデル**：Opus 4.6 以降、Sonnet 4.6 以降、または Haiku 4.5。Fable 5 も Claude Code v2.1.170 以降で適格です。

<h2 id="turn-the-advisor-off">
  advisor をオフにする
</h2>

advisor の使用を停止し、保存された `advisorModel` をクリアするには、`/advisor off` を実行するか、`/advisor` ピッカーで **No advisor** を選択します。

```
/advisor off
```

advisor ツール全体を無効にするには、`CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` を設定します。`/advisor` コマンドは利用できなくなり、設定された `advisorModel` は無視されます。`--advisor` フラグは受け入れられますが、効果はありません。このフラグを渡す既存のスクリプトはエラーなしで動作し続けます。[環境変数](/docs/ja/env-vars)を参照してください。

<h2 id="compare-with-related-features">
  関連機能との比較
</h2>

advisor は、モデルの強みを組み合わせるいくつかの方法の 1 つです。2 番目のモデルをいつ関与させるかに基づいて選択します。

| アプローチ                                                 | より強力なモデルが実行される場合                                                                                          | 開始方法                          |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------- |
| Advisor ツール                                           | タスク中の決定ポイント                                                                                               | Claude がガイダンスが必要な場合に呼び出します    |
| [`opusplan`](/docs/ja/model-config#opusplan-model-setting) | プランモード中（[`availableModels`](/docs/ja/model-config#restrict-model-selection)で許可されている場合）、その後実行用に Sonnet に切り替わります | プランモードに入ります                   |
| [サブエージェント](/docs/ja/sub-agents#choose-a-model)（`model` 設定） | 委任されたサブタスク全体                                                                                              | Claude が委任するか、サブエージェントを呼び出します |
| [`/model`](/docs/ja/model-config#setting-your-model)       | 後続のすべてのターン                                                                                                | モデルを切り替えます                    |

<h2 id="see-also">
  関連項目
</h2>

* [モデル構成](/docs/ja/model-config)：モデルを切り替え、努力レベルを設定し、`opusplan` を使用します
* [コストを効果的に管理する](/docs/ja/costs)：モデル全体のトークン使用量を追跡します
* [Claude API の Advisor ツール](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)：基盤となるサーバーツールを理解するか、Messages API から直接使用します
* [advisor 戦略](https://claude.com/blog/the-advisor-strategy)：高速メインモデルをより強力な advisor と組み合わせる理由
