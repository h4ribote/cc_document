> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# エージェントから構造化された出力を取得する

> JSON Schema、Zod、または Pydantic を使用して、エージェントワークフローから検証済みの JSON を返します。マルチターンツール使用後に型安全で構造化されたデータを取得します。

構造化された出力を使用すると、エージェントから返してほしいデータの正確な形状を定義できます。エージェントはタスクを完了するために必要なツールを使用でき、最後にスキーマに一致する検証済み JSON を取得できます。必要な構造の [JSON Schema](https://json-schema.org/understanding-json-schema/about) を定義すると、SDK は出力をそれに対して検証し、不一致の場合は再プロンプトします。検証が再試行制限内に成功しない場合、結果は構造化データではなくエラーになります。[エラーハンドリング](#error-handling) を参照してください。

完全な型安全性のために、[Zod](#type-safe-schemas-with-zod-and-pydantic)（TypeScript）または [Pydantic](#type-safe-schemas-with-zod-and-pydantic)（Python）を使用してスキーマを定義し、強く型付けされたオブジェクトを取得します。

<h2 id="why-structured-outputs">
  構造化された出力が必要な理由
</h2>

エージェントはデフォルトでは自由形式のテキストを返します。これはチャットには機能しますが、出力をプログラムで使用する必要がある場合には機能しません。構造化された出力は、アプリケーションロジック、データベース、または UI コンポーネントに直接渡すことができる型付きデータを提供します。

エージェントがウェブを検索してレシピを取得するレシピアプリを考えてみてください。構造化された出力がない場合、自分で解析する必要がある自由形式のテキストが得られます。構造化された出力を使用すると、必要な形状を定義し、アプリで直接使用できる型付きデータを取得できます。

<AccordionGroup>
  <Accordion title="構造化された出力なし">
    ```text theme={null}
    これは古典的なチョコレートチップクッキーのレシピです！

    **チョコレートチップクッキー**
    準備時間：15 分 | 調理時間：10 分

    材料：
    - 2 1/4 カップ 薄力粉
    - 1 カップ バター、柔らかくしたもの
    ...
    ```

    これをアプリで使用するには、タイトルを解析し、'15 分'を数値に変換し、材料と手順を分離し、応答全体で一貫性のない形式を処理する必要があります。
  </Accordion>

  <Accordion title="構造化された出力あり">
    ```json theme={null}
    {
      "name": "Chocolate Chip Cookies",
      "prep_time_minutes": 15,
      "cook_time_minutes": 10,
      "ingredients": [
        { "item": "all-purpose flour", "amount": 2.25, "unit": "cups" },
        { "item": "butter, softened", "amount": 1, "unit": "cup" }
        // ...
      ],
      "steps": ["Preheat oven to 375°F", "Cream butter and sugar" /* ... */]
    }
    ```

    UI で直接使用できる型付きデータ。
  </Accordion>
</AccordionGroup>

<h2 id="quick-start">
  クイックスタート
</h2>

構造化された出力を使用するには、必要なデータの形状を説明する [JSON Schema](https://json-schema.org/understanding-json-schema/about) を定義し、`outputFormat` オプション（TypeScript）または `output_format` オプション（Python）を使用して `query()` に渡します。エージェントが完了すると、結果メッセージにはスキーマに一致する検証済みデータを含む `structured_output` フィールドが含まれます。

以下の例は、エージェントに Anthropic を調査し、会社名、設立年、本社を構造化された出力として返すよう求めています。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // 返してほしいデータの形状を定義
  const schema = {
    type: "object",
    properties: {
      company_name: { type: "string" },
      founded_year: { type: "number" },
      headquarters: { type: "string" }
    },
    required: ["company_name"]
  };

  for await (const message of query({
    prompt: "Research Anthropic and provide key company information",
    options: {
      outputFormat: {
        type: "json_schema",
        schema: schema
      }
    }
  })) {
    // 結果メッセージには検証済みデータを含む structured_output が含まれます
    if (message.type === "result" && message.subtype === "success" && message.structured_output) {
      console.log(message.structured_output);
      // { company_name: "Anthropic", founded_year: 2021, headquarters: "San Francisco, CA" }
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

  // 返してほしいデータの形状を定義
  schema = {
      "type": "object",
      "properties": {
          "company_name": {"type": "string"},
          "founded_year": {"type": "number"},
          "headquarters": {"type": "string"},
      },
      "required": ["company_name"],
  }


  async def main():
      async for message in query(
          prompt="Research Anthropic and provide key company information",
          options=ClaudeAgentOptions(
              output_format={"type": "json_schema", "schema": schema}
          ),
      ):
          // 結果メッセージには検証済みデータを含む structured_output が含まれます
          if isinstance(message, ResultMessage) and message.structured_output:
              print(message.structured_output)
              # {'company_name': 'Anthropic', 'founded_year': 2021, 'headquarters': 'San Francisco, CA'}


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="type-safe-schemas-with-zod-and-pydantic">
  Zod と Pydantic を使用した型安全なスキーマ
</h2>

JSON Schema を手書きする代わりに、[Zod](https://zod.dev/)（TypeScript）または [Pydantic](https://docs.pydantic.dev/latest/)（Python）を使用してスキーマを定義できます。これらのライブラリは JSON Schema を生成し、応答を完全に型付けされたオブジェクトに解析できるため、オートコンプリートと型チェックを使用してコードベース全体で使用できます。

以下の例は、概要、ステップのリスト（各ステップに複雑さレベルを含む）、および潜在的なリスクを含む機能実装計画のスキーマを定義しています。エージェントは機能を計画し、型付けされた `FeaturePlan` オブジェクトを返します。その後、`plan.summary` などのプロパティにアクセスし、完全な型安全性を備えて `plan.steps` を反復処理できます。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { z } from "zod";
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // Zod でスキーマを定義
  const FeaturePlan = z.object({
    feature_name: z.string(),
    summary: z.string(),
    steps: z.array(
      z.object({
        step_number: z.number(),
        description: z.string(),
        estimated_complexity: z.enum(["low", "medium", "high"])
      })
    ),
    risks: z.array(z.string())
  });

  type FeaturePlan = z.infer<typeof FeaturePlan>;

  // JSON Schema に変換
  const schema = z.toJSONSchema(FeaturePlan);

  // クエリで使用
  for await (const message of query({
    prompt:
      "Plan how to add dark mode support to a React app. Break it into implementation steps.",
    options: {
      outputFormat: {
        type: "json_schema",
        schema: schema
      }
    }
  })) {
    if (message.type === "result" && message.subtype === "success" && message.structured_output) {
      // 検証して完全に型付けされた結果を取得
      const parsed = FeaturePlan.safeParse(message.structured_output);
      if (parsed.success) {
        const plan: FeaturePlan = parsed.data;
        console.log(`Feature: ${plan.feature_name}`);
        console.log(`Summary: ${plan.summary}`);
        plan.steps.forEach((step) => {
          console.log(`${step.step_number}. [${step.estimated_complexity}] ${step.description}`);
        });
      }
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from pydantic import BaseModel
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


  class Step(BaseModel):
      step_number: int
      description: str
      estimated_complexity: str  # 'low', 'medium', 'high'


  class FeaturePlan(BaseModel):
      feature_name: str
      summary: str
      steps: list[Step]
      risks: list[str]


  async def main():
      async for message in query(
          prompt="Plan how to add dark mode support to a React app. Break it into implementation steps.",
          options=ClaudeAgentOptions(
              output_format={
                  "type": "json_schema",
                  "schema": FeaturePlan.model_json_schema(),
              }
          ),
      ):
          if isinstance(message, ResultMessage) and message.structured_output:
              # 検証して完全に型付けされた結果を取得
              plan = FeaturePlan.model_validate(message.structured_output)
              print(f"Feature: {plan.feature_name}")
              print(f"Summary: {plan.summary}")
              for step in plan.steps:
                  print(
                      f"{step.step_number}. [{step.estimated_complexity}] {step.description}"
                  )


  asyncio.run(main())
  ```
</CodeGroup>

**メリット：**

* 完全な型推論（TypeScript）と型ヒント（Python）
* `safeParse()` または `model_validate()` を使用したランタイム検証
* より良いエラーメッセージ
* 構成可能で再利用可能なスキーマ

<h2 id="output-format-configuration">
  出力形式の設定
</h2>

`outputFormat`（TypeScript）または `output_format`（Python）オプションは、以下を含むオブジェクトを受け入れます：

* `type`：構造化された出力の場合は `"json_schema"` に設定
* `schema`：出力構造を定義する [JSON Schema](https://json-schema.org/understanding-json-schema/about) オブジェクト。Zod スキーマから `z.toJSONSchema()` で、または Pydantic モデルから `.model_json_schema()` で生成できます。

SDK は、すべての基本型（object、array、string、number、boolean、null）、`enum`、`const`、`required`、ネストされたオブジェクト、および `$ref` 定義を含む標準 JSON Schema 機能をサポートしています。サポートされている機能と制限の完全なリストについては、[JSON Schema の制限](https://platform.claude.com/docs/ja/build-with-claude/structured-outputs#json-schema-limitations) を参照してください。

有効な JSON Schema ではないスキーマは、問題を示すエラーで起動時に実行に失敗します。v2.1.205 より前は、無効なスキーマは暗黙的に無視され、エージェントは非構造化テキストを返していました。

`"format": "email"` などの `format` キーワードは、注釈として受け入れられ、SDK のバリデーターによって強制されません。v2.1.205 より前は、`format` を含むスキーマは無効として扱われていました。

<h2 id="example-todo-tracking-agent">
  例：TODO トラッキングエージェント
</h2>

この例は、マルチステップツール使用で構造化された出力がどのように機能するかを示しています。エージェントはコードベース内の TODO コメントを見つけ、各コメントの git blame 情報を調べる必要があります。実行中に使用するツール（検索用の Grep、git コマンド実行用の Bash）を自律的に決定し、結果を単一の構造化応答に組み合わせます。

スキーマには、すべてのファイルで git blame 情報が利用できない可能性があるため、オプションフィールド（`author` と `date`）が含まれています。エージェントは見つけられるものを埋め、残りは省略します。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // TODO 抽出用の構造を定義
  const todoSchema = {
    type: "object",
    properties: {
      todos: {
        type: "array",
        items: {
          type: "object",
          properties: {
            text: { type: "string" },
            file: { type: "string" },
            line: { type: "number" },
            author: { type: "string" },
            date: { type: "string" }
          },
          required: ["text", "file", "line"]
        }
      },
      total_count: { type: "number" }
    },
    required: ["todos", "total_count"]
  };

  // エージェントは Grep を使用して TODO を見つけ、Bash を使用して git blame 情報を取得
  for await (const message of query({
    prompt: "Find all TODO comments in this codebase and identify who added them",
    options: {
      outputFormat: {
        type: "json_schema",
        schema: todoSchema
      }
    }
  })) {
    if (message.type === "result" && message.subtype === "success" && message.structured_output) {
      const data = message.structured_output as { total_count: number; todos: Array<{ file: string; line: number; text: string; author?: string; date?: string }> };
      console.log(`Found ${data.total_count} TODOs`);
      data.todos.forEach((todo) => {
        console.log(`${todo.file}:${todo.line} - ${todo.text}`);
        if (todo.author) {
          console.log(`  Added by ${todo.author} on ${todo.date}`);
        }
      });
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

  # TODO 抽出用の構造を定義
  todo_schema = {
      "type": "object",
      "properties": {
          "todos": {
              "type": "array",
              "items": {
                  "type": "object",
                  "properties": {
                      "text": {"type": "string"},
                      "file": {"type": "string"},
                      "line": {"type": "number"},
                      "author": {"type": "string"},
                      "date": {"type": "string"},
                  },
                  "required": ["text", "file", "line"],
              },
          },
          "total_count": {"type": "number"},
      },
      "required": ["todos", "total_count"],
  }


  async def main():
      # エージェントは Grep を使用して TODO を見つけ、Bash を使用して git blame 情報を取得
      async for message in query(
          prompt="Find all TODO comments in this codebase and identify who added them",
          options=ClaudeAgentOptions(
              output_format={"type": "json_schema", "schema": todo_schema}
          ),
      ):
          if isinstance(message, ResultMessage) and message.structured_output:
              data = message.structured_output
              print(f"Found {data['total_count']} TODOs")
              for todo in data["todos"]:
                  print(f"{todo['file']}:{todo['line']} - {todo['text']}")
                  if "author" in todo:
                      print(f"  Added by {todo['author']} on {todo['date']}")


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="error-handling">
  エラーハンドリング
</h2>

構造化された出力の生成は、エージェントがスキーマに一致する有効な JSON を生成できない場合に失敗する可能性があります。これは通常、スキーマがタスクに対して複雑すぎる場合、タスク自体が曖昧な場合、またはエージェントが検証エラーを修正しようとして再試行制限に達した場合に発生します。また、検証の失敗がなくても発生する可能性があります。[モデルフォールバック](/docs/ja/model-config#automatic-model-fallback)は既に完了した出力をストリーム中に取り消すことができ、再試行がそれを置き換えない場合、実行は同じエラーで終了します。デバッグの前に、結果メッセージの `errors` フィールドをチェックして、2 つの原因を区別してください。

エラーが発生すると、結果メッセージには何が問題かを示す `subtype` があります：

| Subtype                               | 意味                                                         |
| ------------------------------------- | ---------------------------------------------------------- |
| `success`                             | 出力が正常に生成および検証されました                                         |
| `error_max_structured_output_retries` | 複数の試行後に有効な出力が生き残りませんでした（検証の失敗、またはモデルフォールバックの取り消しで再試行がない場合） |

以下の例は、`subtype` フィールドをチェックして、出力が正常に生成されたか、失敗を処理する必要があるかを判断します：

<CodeGroup>
  ```typescript TypeScript theme={null}
  for await (const msg of query({
    prompt: "Extract contact info from the document",
    options: {
      outputFormat: {
        type: "json_schema",
        schema: contactSchema
      }
    }
  })) {
    if (msg.type === "result") {
      if (msg.subtype === "success" && msg.structured_output) {
        // 検証済み出力を使用
        console.log(msg.structured_output);
      } else if (msg.subtype === "error_max_structured_output_retries") {
        // 失敗を処理 - より単純なプロンプトで再試行、非構造化にフォールバック、など
        console.error("Could not produce valid output");
      }
    }
  }
  ```

  ```python Python theme={null}
  async for message in query(
      prompt="Extract contact info from the document",
      options=ClaudeAgentOptions(
          output_format={"type": "json_schema", "schema": contact_schema}
      ),
  ):
      if isinstance(message, ResultMessage):
          if message.subtype == "success" and message.structured_output:
              # 検証済み出力を使用
              print(message.structured_output)
          elif message.subtype == "error_max_structured_output_retries":
              # 失敗を処理
              print("Could not produce valid output")
  ```
</CodeGroup>

**エラーを回避するためのヒント：**

* **スキーマを焦点を絞ったものにしてください。** 多くの必須フィールドを持つ深くネストされたスキーマは満たすのが難しいです。シンプルに始めて、必要に応じて複雑さを追加してください。
* **スキーマをタスクに合わせてください。** タスクがスキーマが必要とするすべての情報を持たない可能性がある場合、それらのフィールドをオプションにしてください。
* **明確なプロンプトを使用してください。** 曖昧なプロンプトは、エージェントが何を出力するかを知るのを難しくします。

<h2 id="related-resources">
  関連リソース
</h2>

* [JSON Schema ドキュメント](https://json-schema.org/)：ネストされたオブジェクト、配列、列挙型、検証制約を含む複雑なスキーマを定義するための JSON Schema 構文を学習します
* [API 構造化出力](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)：ツール使用なしの単一ターンリクエストの場合、Claude API で直接構造化された出力を使用します
* [カスタムツール](/docs/ja/agent-sdk/custom-tools)：構造化された出力を返す前に実行中にエージェントが呼び出すカスタムツールを提供します
