> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# コストと使用状況の追跡

> Claude Agent SDK でトークン使用状況を追跡し、コストを見積もり、プロンプトキャッシングを設定する方法を学びます。

Claude Agent SDK は、Claude との各インタラクションの詳細なトークン使用情報を提供します。このガイドでは、使用状況を適切に追跡し、特に並列ツール使用とマルチステップ会話を扱う場合のコスト報告を理解する方法について説明します。

完全な API ドキュメントについては、[TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript)と[Python SDK リファレンス](/docs/ja/agent-sdk/python)を参照してください。

<Warning>
  `total_cost_usd` および `costUSD` フィールドはクライアント側の推定値であり、権限のある請求データではありません。SDK はビルド時にバンドルされた価格表からローカルで計算するため、以下の場合に実際の請求額から乖離する可能性があります。

  * 価格が変更された
  * インストールされている SDK バージョンがモデルを認識しない
  * クライアントがモデル化できない請求ルールが適用される

  これらのフィールドは開発の洞察と概算予算作成に使用してください。権限のある請求については、[Usage and Cost API](https://platform.claude.com/docs/en/build-with-claude/usage-cost-api)または[Claude Console](https://platform.claude.com/usage)の Usage ページを使用してください。これらのフィールドからエンドユーザーに請求したり、財務上の決定をトリガーしたりしないでください。
</Warning>

<h2 id="understand-token-usage">
  トークン使用状況を理解する
</h2>

TypeScript と Python SDK は、異なるフィールド名で同じ使用データを公開します。

* **TypeScript** は、各アシスタントメッセージ（`message.message.id`、`message.message.usage`）のステップごとのトークン分解、結果メッセージの `modelUsage` 経由のモデルごとのコスト、および結果メッセージの累積合計を提供します。
* **Python** は、各アシスタントメッセージ（`message.usage`、`message.message_id`）のステップごとのトークン分解、結果メッセージの `model_usage` 経由のモデルごとのコスト、および結果メッセージの累積合計（`total_cost_usd` および `usage` 辞書）を提供します。

両方の SDK は同じ基本的なコストモデルを使用し、同じ粒度を公開します。違いはフィールド命名とステップごとの使用がネストされている場所です。

コスト追跡は、SDK が使用データをどのようにスコープするかを理解することに依存します。

* **`query()` 呼び出し：** SDK の `query()` 関数の 1 つの呼び出し。単一の呼び出しは複数のステップを含むことができます（Claude が応答し、ツールを使用し、結果を取得し、再度応答します）。各呼び出しは最後に 1 つの[`result`](/docs/ja/agent-sdk/typescript#sdkresultmessage)メッセージを生成します。
* **ステップ：** `query()` 呼び出し内の単一のリクエスト/レスポンスサイクル。各ステップはトークン使用情報を含むアシスタントメッセージを生成します。
* **セッション：** セッション ID でリンクされた一連の `query()` 呼び出し（`resume` オプションを使用）。セッション内の各 `query()` 呼び出しは独立してコストを報告します。

次の図は、単一の `query()` 呼び出しからのメッセージストリームを示しており、各ステップでトークン使用が報告され、最後に累積推定値が表示されます。

<img src="https://mintcdn.com/claude-code/ikqp3_70mqIahteV/images/agent-sdk/message-usage-flow.svg?fit=max&auto=format&n=ikqp3_70mqIahteV&q=85&s=68497aee338e01cc745323af7aea378e" alt="クエリが 2 つのステップのメッセージを生成する図。ステップ 1 には同じ ID と使用状況を共有する 4 つのアシスタントメッセージがあり（1 回カウント）、ステップ 2 には新しい ID を持つ 1 つのアシスタントメッセージがあり、最終的な結果メッセージは推定 total_cost_usd を示します。" width="760" height="520" data-path="images/agent-sdk/message-usage-flow.svg" />

<Steps>
  <Step title="各ステップはアシスタントメッセージを生成します">
    Claude が応答すると、1 つ以上のアシスタントメッセージを送信します。TypeScript では、各アシスタントメッセージには、ネストされた `BetaMessage`（`message.message` 経由でアクセス）が含まれており、`id` とトークン数（`input_tokens`、`output_tokens`）を含む[`usage`](https://platform.claude.com/docs/en/api/messages)オブジェクトがあります。Python では、`AssistantMessage` データクラスは `message.usage` と `message.message_id` 経由で同じデータを直接公開します。Claude が 1 つのターンで複数のツールを使用する場合、そのターンのすべてのメッセージは同じ ID を共有するため、ID でデデュプリケートして二重カウントを避けてください。
  </Step>

  <Step title="結果メッセージは累積推定値を提供します">
    `query()` 呼び出しが完了すると、SDK は `total_cost_usd` と累積 `usage` を含む結果メッセージを発行します。これは TypeScript（[`SDKResultMessage`](/docs/ja/agent-sdk/typescript#sdkresultmessage)）と Python（[`ResultMessage`](/docs/ja/agent-sdk/python#resultmessage)）の両方で利用可能です。複数の `query()` 呼び出しを行う場合（たとえば、マルチターンセッション）、各結果はその個別の呼び出しのコストのみを反映します。推定合計のみが必要な場合は、ステップごとの使用を無視して、この単一の値を読むことができます。
  </Step>
</Steps>

<h2 id="get-the-total-cost-of-a-query">
  クエリの総コストを取得する
</h2>

結果メッセージ（[TypeScript](/docs/ja/agent-sdk/typescript#sdkresultmessage)、[Python](/docs/ja/agent-sdk/python#resultmessage)）は、`query()` 呼び出しのエージェントループの終了をマークします。これには `total_cost_usd` が含まれており、その呼び出し内のすべてのステップにわたる累積推定コストです。これは成功とエラー結果の両方で機能します。セッションを使用して複数の `query()` 呼び出しを行う場合、各結果はその個別の呼び出しのコストのみを反映します。

3 つの結果レベルのフィールドは、エージェントが[サブエージェント](/docs/ja/agent-sdk/subagents)を生成する場合に何をカウントするかが異なります。ツリー全体のトークンアカウンティングには `modelUsage` または Python の `model_usage` を使用してください。`usage` フィールドはネストが発生するとすぐに過小カウントされます。

| フィールド                        | サブエージェントアクティビティ                                            |
| ---------------------------- | ---------------------------------------------------------- |
| `usage`                      | 除外。トップレベルのエージェントループのみをカウントするため、サブエージェント内で消費されたトークンは追加されません |
| `total_cost_usd`             | 含まれます。トップレベルループと並行してサブエージェントリクエストをカウントします                  |
| `modelUsage` / `model_usage` | 含まれます。トップレベルループと並行してサブエージェントリクエストをカウントし、モデル別に分類されます        |

次の例は、`query()` 呼び出しからのメッセージストリームを反復処理し、`result` メッセージが到着したときに総コストを出力します。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  try {
    for await (const message of query({ prompt: "Summarize this project" })) {
      if (message.type === "result") {
        console.log(`Total cost: $${message.total_cost_usd}`);
      }
    }
  } catch (error) {
    // A single-shot query() throws after yielding an error result. If the
    // failure was an error result, it still carried total_cost_usd and the
    // branch above has already run; connection or process failures yield
    // no result message.
    console.error(`Session ended with an error: ${error}`);
  }
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ResultMessage
  import asyncio


  async def main():
      try:
          async for message in query(prompt="Summarize this project"):
              if isinstance(message, ResultMessage):
                  print(f"Total cost: ${message.total_cost_usd or 0}")
      except Exception as error:
          # A single-shot query() raises after yielding an error result. If the
          # failure was an error result, it still carried total_cost_usd and the
          # branch above has already run; connection or process failures yield
          # no result message.
          print(f"Session ended with an error: {error}")


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="track-per-step-and-per-model-usage">
  ステップごとおよびモデルごとの使用状況を追跡する
</h2>

このセクションの例は TypeScript フィールド名を使用します。Python では、同等のフィールドはステップごとの使用状況の[`AssistantMessage.usage`](/docs/ja/agent-sdk/python#assistantmessage)と `AssistantMessage.message_id`、およびモデルごとの分解の[`ResultMessage.model_usage`](/docs/ja/agent-sdk/python#resultmessage)です。

<h3 id="track-per-step-usage">
  ステップごとの使用状況を追跡する
</h3>

各アシスタントメッセージには、ネストされた `BetaMessage`（`message.message` 経由でアクセス）が含まれており、`id` とトークン数を含む `usage` オブジェクトがあります。Claude がツールを並列で使用する場合、複数のメッセージは同じ `id` と同一の使用データを共有します。既にカウントした ID を追跡し、重複をスキップして、インフレートされた合計を避けてください。

<Warning>
  並列ツール呼び出しは、ネストされた `BetaMessage` が同じ `id` と同一の使用データを共有する複数のアシスタントメッセージを生成します。正確なステップごとのトークン数を取得するには、常に ID でデデュプリケートしてください。
</Warning>

次の例は、各ユニークなメッセージ ID を 1 回だけカウントして、すべてのステップにわたって入力トークンと出力トークンを累積します。

```typescript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";

const seenIds = new Set<string>();
let totalInputTokens = 0;
let totalOutputTokens = 0;

try {
  for await (const message of query({ prompt: "Summarize this project" })) {
    if (message.type === "assistant") {
      const msgId = message.message.id;

      // Parallel tool calls share the same ID, only count once
      if (!seenIds.has(msgId)) {
        seenIds.add(msgId);
        totalInputTokens += message.message.usage.input_tokens;
        totalOutputTokens += message.message.usage.output_tokens;
      }
    }
  }
} catch (error) {
  // A single-shot query() throws after yielding an error result, so the
  // totals below still reflect the steps that ran before the failure.
  console.error(`Session ended with an error: ${error}`);
}

console.log(`Steps: ${seenIds.size}`);
console.log(`Input tokens: ${totalInputTokens}`);
console.log(`Output tokens: ${totalOutputTokens}`);
```

<h3 id="break-down-usage-per-model">
  モデルごとの使用状況を分解する
</h3>

結果メッセージには[`modelUsage`](/docs/ja/agent-sdk/typescript#modelusage)が含まれており、これはモデル名からモデルごとのトークン数とコストへのマップです。これは複数のモデルを実行する場合（たとえば、サブエージェント用の Haiku とメインエージェント用の Opus）に便利で、トークンがどこに行っているかを確認したい場合に役立ちます。

次の例はクエリを実行し、使用されたモデルごとのコストとトークン分解を出力します。

```typescript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";

try {
  for await (const message of query({ prompt: "Summarize this project" })) {
    if (message.type !== "result") continue;

    for (const [modelName, usage] of Object.entries(message.modelUsage)) {
      console.log(`${modelName}: $${usage.costUSD.toFixed(4)}`);
      console.log(`  Input tokens: ${usage.inputTokens}`);
      console.log(`  Output tokens: ${usage.outputTokens}`);
      console.log(`  Cache read: ${usage.cacheReadInputTokens}`);
      console.log(`  Cache creation: ${usage.cacheCreationInputTokens}`);
    }
  }
} catch (error) {
  // A single-shot query() throws after yielding an error result. If the
  // failure was an error result, the per-model breakdown above has already
  // printed; connection or process failures yield no result message.
  console.error(`Session ended with an error: ${error}`);
}
```

<h2 id="accumulate-costs-across-multiple-calls">
  複数の呼び出しにわたってコストを累積する
</h2>

各 `query()` 呼び出しは独自の `total_cost_usd` を返します。SDK はセッションレベルの合計を提供しないため、アプリケーションが複数の `query()` 呼び出しを行う場合（たとえば、マルチターンセッションまたは異なるユーザー間）、合計を自分で累積してください。

次の例は 2 つの `query()` 呼び出しを順序立てて実行し、各呼び出しの `total_cost_usd` を実行中の合計に追加し、呼び出しごとのコストと合計コストの両方を出力します。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // Track cumulative cost across multiple query() calls
  let totalSpend = 0;

  const prompts = [
    "Read the files in src/ and summarize the architecture",
    "List all exported functions in src/auth.ts"
  ];

  for (const prompt of prompts) {
    try {
      for await (const message of query({ prompt })) {
        if (message.type === "result") {
          totalSpend += message.total_cost_usd;
          console.log(`This call: $${message.total_cost_usd}`);
        }
      }
    } catch (error) {
      // A single-shot query() throws after yielding an error result. If the
      // failure was an error result, this call's cost was already counted;
      // connection or process failures yield no result message. Continue
      // with the next prompt.
      console.error(`Call failed: ${error}`);
    }
  }

  console.log(`Total spend: $${totalSpend.toFixed(4)}`);
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ResultMessage
  import asyncio


  async def main():
      # Track cumulative cost across multiple query() calls
      total_spend = 0.0

      prompts = [
          "Read the files in src/ and summarize the architecture",
          "List all exported functions in src/auth.ts",
      ]

      for prompt in prompts:
          try:
              async for message in query(prompt=prompt):
                  if isinstance(message, ResultMessage):
                      cost = message.total_cost_usd or 0
                      total_spend += cost
                      print(f"This call: ${cost}")
          except Exception as error:
              # A single-shot query() raises after yielding an error result. If
              # the failure was an error result, this call's cost was already
              # counted; connection or process failures yield no result message.
              # Continue with the next prompt.
              print(f"Call failed: {error}")

      print(f"Total spend: ${total_spend:.4f}")


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="handle-errors-caching-and-token-discrepancies">
  エラー、キャッシング、トークン不一致を処理する
</h2>

正確なコスト追跡のために、失敗した会話、キャッシュトークン価格、および時折の報告の不一致を考慮してください。

<h3 id="resolve-output-token-discrepancies">
  出力トークン不一致を解決する
</h3>

まれに、同じ ID を持つメッセージに対して異なる `output_tokens` 値が観察される場合があります。これが発生した場合：

1. **最高値を使用する：** グループ内の最終メッセージは通常、正確な合計を含みます。
2. **結果メッセージを優先する：** 結果メッセージの `total_cost_usd` は、すべてのステップにわたって SDK の累積推定値を反映するため、ステップごとの値を自分で合計するよりも信頼性が高くなります。これはまだ推定値であり、実際の請求額と異なる場合があります。
3. **不一致を報告する：** [Claude Code GitHub リポジトリ](https://github.com/anthropics/claude-code/issues)で問題をファイルしてください。

<h3 id="track-costs-on-failed-conversations">
  失敗した会話のコストを追跡する
</h3>

成功とエラーの両方の結果メッセージには `usage` と `total_cost_usd` が含まれます。会話が途中で失敗した場合、失敗の時点までトークンを消費しています。その `subtype` に関係なく、常に結果メッセージからコストデータを読んでください。

<h3 id="track-cache-tokens">
  キャッシュトークンを追跡する
</h3>

Agent SDK は [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) を自動的に使用して、繰り返されるコンテンツのコストを削減します。キャッシングを自分で設定する必要はありません。使用オブジェクトには、キャッシング追跡用の 2 つの追加フィールドが含まれます。

* `cache_creation_input_tokens`：新しいキャッシュエントリを作成するために使用されるトークン（標準入力トークンより高いレートで課金）。
* `cache_read_input_tokens`：既存のキャッシュエントリから読み取られるトークン（削減されたレートで課金）。

キャッシング節約を理解するために、これらを `input_tokens` とは別に追跡してください。TypeScript では、これらのフィールドは [`Usage`](/docs/ja/agent-sdk/typescript#usage) オブジェクトで型付けされます。Python では、[`ResultMessage.usage`](/docs/ja/agent-sdk/python#resultmessage) 辞書のキーとして表示されます（たとえば、`message.usage.get("cache_read_input_tokens", 0)`）。

<h3 id="extend-the-prompt-cache-ttl-to-one-hour">
  プロンプトキャッシュ TTL を 1 時間に延長する
</h3>

SDK によって書き込まれたキャッシュエントリは、API キーで認証するか、Amazon Bedrock、Google Cloud の Agent Platform、または Microsoft Foundry で実行する場合、デフォルトで 5 分の TTL を使用します。ワークロードが同じシステムプロンプトとコンテキストに対して多くの短いセッションを実行し、セッション間に 5 分以上のギャップがある場合、キャッシュはセッション間で期限切れになり、各新しいセッションは完全な入力価格を支払います。

キャッシュ書き込みで 1 時間の TTL をリクエストするには、[`ENABLE_PROMPT_CACHING_1H`](/docs/ja/env-vars) 環境変数を設定します。シェルまたはコンテナ環境でエクスポートするか、`options.env` 経由で渡すことができます。

次の例は、Amazon Bedrock で実行されているエージェントの 1 時間 TTL を有効にします。

<CodeGroup>
  ```python Python theme={null}
  from claude_agent_sdk import ClaudeAgentOptions, query
  import asyncio


  async def main():
      options = ClaudeAgentOptions(
          env={
              "CLAUDE_CODE_USE_BEDROCK": "1",
              "ENABLE_PROMPT_CACHING_1H": "1",
          },
      )

      async for message in query(prompt="Summarize this project", options=options):
          print(message)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const options = {
    env: {
      ...process.env,
      CLAUDE_CODE_USE_BEDROCK: "1",
      ENABLE_PROMPT_CACHING_1H: "1",
    },
  };

  for await (const message of query({ prompt: "Summarize this project", options })) {
    console.log(message);
  }
  ```
</CodeGroup>

1 時間の TTL を持つキャッシュ書き込みは、5 分の書き込みより高いレートで課金されるため、これを有効にすると、より高い書き込みコストとより多くのキャッシュ読み取りがトレードオフされます。詳細については、[prompt caching pricing](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) を参照してください。Claude サブスクリプションユーザーは既に 1 時間の TTL を自動的に受け取り、この変数を設定する必要はありません。

<h2 id="related-documentation">
  関連ドキュメント
</h2>

* [TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript) - 完全な API ドキュメント
* [SDK 概要](/docs/ja/agent-sdk/overview) - SDK の使用を開始する
* [SDK パーミッション](/docs/ja/agent-sdk/permissions) - ツールパーミッションの管理
