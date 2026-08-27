> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude にカスタムツールを提供する

> Claude Agent SDK のインプロセス MCP サーバーでカスタムツールを定義し、Claude が関数を呼び出し、API にアクセスし、ドメイン固有の操作を実行できるようにします。

カスタムツールは Agent SDK を拡張し、Claude が会話中に呼び出せる独自の関数を定義できるようにします。SDK のインプロセス MCP サーバーを使用すると、Claude にデータベース、外部 API、ドメイン固有のロジック、またはアプリケーションが必要とするその他の機能へのアクセスを提供できます。

このガイドでは、入力スキーマとハンドラーを使用してツールを定義し、それらを MCP サーバーにバンドルし、`query` に渡し、Claude がアクセスできるツールを制御する方法について説明します。また、エラーハンドリング、ツール注釈、および画像などの非テキストコンテンツを返す方法についても説明します。

<h2 id="quick-reference">
  クイックリファレンス
</h2>

| 実行したい操作                      | 方法                                                                                                                                                                                  |
| :--------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ツールを定義する                     | Python では [`@tool`](/docs/ja/agent-sdk/python#tool)、TypeScript では [`tool()`](/docs/ja/agent-sdk/typescript#tool) を使用して、名前、説明、スキーマ、ハンドラーを指定します。[カスタムツールを作成する](#create-a-custom-tool)を参照してください。 |
| Claude にツールを登録する             | `create_sdk_mcp_server` / `createSdkMcpServer` でラップし、`query()` の `mcpServers` に渡します。[カスタムツールを呼び出す](#call-a-custom-tool)を参照してください。                                                   |
| ツールを事前承認する                   | 許可されたツールに追加します。[許可されたツールを設定する](#configure-allowed-tools)を参照してください。                                                                                                                  |
| Claude のコンテキストから組み込みツールを削除する | 必要な組み込みのみをリストする `tools` 配列を渡します。[許可されたツールを設定する](#configure-allowed-tools)を参照してください。                                                                                                 |
| Claude がツールを並列で呼び出せるようにする    | 副作用のないツールに `readOnlyHint: true` を設定します。[ツール注釈を追加する](#add-tool-annotations)を参照してください。                                                                                                |
| Claude が読むエラーメッセージを制御する      | `isError: true` を返して、生の例外をサーフェスする代わりにメッセージを作成します。[エラーを処理する](#handle-errors)を参照してください。                                                                                               |
| 画像またはファイルを返す                 | コンテンツ配列で `image` または `resource` ブロックを使用します。[画像とリソースを返す](#return-images-and-resources)を参照してください。                                                                                     |
| マシン可読 JSON 結果を返す             | 結果に `structuredContent` を設定します。[構造化データを返す](#return-structured-data)を参照してください。                                                                                                       |
| 多くのツールにスケーリングする              | [ツール検索](/docs/ja/agent-sdk/tool-search)を使用して、オンデマンドでツールを読み込みます。                                                                                                                          |

<h2 id="create-a-custom-tool">
  カスタムツールを作成する
</h2>

ツールは 4 つの部分で定義され、TypeScript の [`tool()`](/docs/ja/agent-sdk/typescript#tool) ヘルパーまたは Python の [`@tool`](/docs/ja/agent-sdk/python#tool) デコレーターに引数として渡されます。

* **名前：** Claude がツールを呼び出すために使用する一意の識別子。
* **説明：** ツールが何をするかを説明します。Claude はこれを読んで、ツールをいつ呼び出すかを決定します。
* **入力スキーマ：** Claude が提供する必要がある引数。TypeScript では常に [Zod スキーマ](https://zod.dev/)であり、ハンドラーの `args` は自動的に型付けされます。Python では `{"latitude": float}` のような名前から型へのマッピングであり、SDK が JSON Schema に変換します。Python デコレーターは、列挙型、範囲、オプションフィールド、またはネストされたオブジェクトが必要な場合、完全な [JSON Schema](https://json-schema.org/understanding-json-schema/about) 辞書も受け入れます。
* **ハンドラー：** Claude がツールを呼び出すときに実行される非同期関数。検証された引数を受け取り、以下を含むオブジェクトを返す必要があります。
  * `content`（必須）：結果ブロックの配列。各ブロックは `"text"`、`"image"`、`"audio"`、`"resource"`、または `"resource_link"` の `type` を持ちます。非テキストブロックについては、[画像とリソースを返す](#return-images-and-resources)を参照してください。
  * `structuredContent`（オプション）：結果をマシン可読データとして保持する JSON オブジェクト。`content` と共に返されます。[構造化データを返す](#return-structured-data)を参照してください。
  * `isError`（オプション）：ツール障害を通知するために `true` に設定し、Claude が対応できるようにします。[エラーを処理する](#handle-errors)を参照してください。

ツールを定義した後、[`createSdkMcpServer`](/docs/ja/agent-sdk/typescript#createsdkmcpserver)（TypeScript）または [`create_sdk_mcp_server`](/docs/ja/agent-sdk/python#create_sdk_mcp_server)（Python）でサーバーにラップします。サーバーはアプリケーション内でインプロセスで実行され、別のプロセスとしては実行されません。

<h3 id="weather-tool-example">
  天気ツールの例
</h3>

この例は `get_temperature` ツールを定義し、MCP サーバーにラップします。ツールのセットアップのみを行います。`query` に渡して実行するには、以下の [カスタムツールを呼び出す](#call-a-custom-tool)を参照してください。

<CodeGroup>
  ```python Python theme={null}
  from typing import Any
  import httpx
  from claude_agent_sdk import tool, create_sdk_mcp_server


  # ツールを定義：名前、説明、入力スキーマ、ハンドラー
  @tool(
      "get_temperature",
      "Get the current temperature at a location",
      {"latitude": float, "longitude": float},
  )
  async def get_temperature(args: dict[str, Any]) -> dict[str, Any]:
      async with httpx.AsyncClient() as client:
          response = await client.get(
              "https://api.open-meteo.com/v1/forecast",
              params={
                  "latitude": args["latitude"],
                  "longitude": args["longitude"],
                  "current": "temperature_2m",
                  "temperature_unit": "fahrenheit",
              },
          )
          data = response.json()

      # コンテンツ配列を返す - Claude はこれをツール結果として見ます
      return {
          "content": [
              {
                  "type": "text",
                  "text": f"Temperature: {data['current']['temperature_2m']}°F",
              }
          ]
      }


  # ツールをインプロセス MCP サーバーにラップします
  weather_server = create_sdk_mcp_server(
      name="weather",
      version="1.0.0",
      tools=[get_temperature],
  )
  ```

  ```typescript TypeScript theme={null}
  import { tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
  import { z } from "zod";

  // ツールを定義：名前、説明、入力スキーマ、ハンドラー
  const getTemperature = tool(
    "get_temperature",
    "Get the current temperature at a location",
    {
      latitude: z.number().describe("Latitude coordinate"), // .describe() は Claude が見るフィールド説明を追加します
      longitude: z.number().describe("Longitude coordinate")
    },
    async (args) => {
      // args はスキーマから型付けされます：{ latitude: number; longitude: number }
      const response = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${args.latitude}&longitude=${args.longitude}&current=temperature_2m&temperature_unit=fahrenheit`
      );
      const data: any = await response.json();

      // コンテンツ配列を返す - Claude はこれをツール結果として見ます
      return {
        content: [{ type: "text", text: `Temperature: ${data.current.temperature_2m}°F` }]
      };
    }
  );

  // ツールをインプロセス MCP サーバーにラップします
  const weatherServer = createSdkMcpServer({
    name: "weather",
    version: "1.0.0",
    tools: [getTemperature]
  });
  ```
</CodeGroup>

完全なパラメーター詳細については、[`tool()`](/docs/ja/agent-sdk/typescript#tool) TypeScript リファレンスまたは [`@tool`](/docs/ja/agent-sdk/python#tool) Python リファレンスを参照してください。JSON Schema 入力形式と戻り値の構造を含みます。

<Tip>
  パラメーターをオプションにするには：TypeScript では、Zod フィールドに `.default()` を追加します。Python では、辞書スキーマはすべてのキーを必須として扱うため、パラメーターをスキーマから除外し、説明文字列で言及し、ハンドラーで `args.get()` で読み取ります。以下の [`get_precipitation_chance` ツール](#add-more-tools)は両方のパターンを示しています。
</Tip>

<h3 id="call-a-custom-tool">
  カスタムツールを呼び出す
</h3>

作成した MCP サーバーを `mcpServers` オプション経由で `query` に渡します。`mcpServers` のキーは各ツールの完全修飾名の `{server_name}` セグメントになります：`mcp__{server_name}__{tool_name}`。その名前を `allowedTools` にリストして、ツールが許可プロンプトなしで実行されるようにします。

これらのスニペットは、[上記の例](#weather-tool-example)の `weatherServer` を再利用して、特定の場所の天気について Claude に尋ねます。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


  async def main():
      options = ClaudeAgentOptions(
          mcp_servers={"weather": weather_server},
          allowed_tools=["mcp__weather__get_temperature"],
      )

      async for message in query(
          prompt="What's the temperature in San Francisco?",
          options=options,
      ):
          # ResultMessage はすべてのツール呼び出しが完了した後の最終メッセージです
          if isinstance(message, ResultMessage) and message.subtype == "success":
              print(message.result)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "What's the temperature in San Francisco?",
    options: {
      mcpServers: { weather: weatherServer },
      allowedTools: ["mcp__weather__get_temperature"]
    }
  })) {
    // "result" はすべてのツール呼び出しが完了した後の最終メッセージです
    if (message.type === "result" && message.subtype === "success") {
      console.log(message.result);
    }
  }
  ```
</CodeGroup>

<h3 id="add-more-tools">
  さらにツールを追加する
</h3>

サーバーは `tools` 配列にリストされた数だけのツールを保持します。複数のツールがサーバーにある場合、`allowedTools` で各ツールを個別にリストするか、ワイルドカード `mcp__weather__*` を使用してサーバーが公開するすべてのツールをカバーできます。

以下の例は、[天気ツールの例](#weather-tool-example)の `weatherServer` に 2 番目のツール `get_precipitation_chance` を追加し、両方のツールを配列で再構築します。

<CodeGroup>
  ```python Python theme={null}
  # 同じサーバーの 2 番目のツールを定義します
  @tool(
      "get_precipitation_chance",
      "Get the hourly precipitation probability for a location. "
      "Optionally pass 'hours' (1-24) to control how many hours to return.",
      {"latitude": float, "longitude": float},
  )
  async def get_precipitation_chance(args: dict[str, Any]) -> dict[str, Any]:
      # 'hours' はスキーマにありません - .get() で読み取ってオプションにします
      hours = args.get("hours", 12)
      async with httpx.AsyncClient() as client:
          response = await client.get(
              "https://api.open-meteo.com/v1/forecast",
              params={
                  "latitude": args["latitude"],
                  "longitude": args["longitude"],
                  "hourly": "precipitation_probability",
                  "forecast_days": 1,
              },
          )
          data = response.json()
      chances = data["hourly"]["precipitation_probability"][:hours]

      return {
          "content": [
              {
                  "type": "text",
                  "text": f"Next {hours} hours: {'%, '.join(map(str, chances))}%",
              }
          ]
      }


  # 両方のツールを配列で再構築します
  weather_server = create_sdk_mcp_server(
      name="weather",
      version="1.0.0",
      tools=[get_temperature, get_precipitation_chance],
  )
  ```

  ```typescript TypeScript theme={null}
  // 同じサーバーの 2 番目のツールを定義します
  const getPrecipitationChance = tool(
    "get_precipitation_chance",
    "Get the hourly precipitation probability for a location",
    {
      latitude: z.number(),
      longitude: z.number(),
      hours: z
        .number()
        .int()
        .min(1)
        .max(24)
        .default(12) // .default() はパラメーターをオプションにします
        .describe("How many hours of forecast to return")
    },
    async (args) => {
      const response = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${args.latitude}&longitude=${args.longitude}&hourly=precipitation_probability&forecast_days=1`
      );
      const data: any = await response.json();
      const chances = data.hourly.precipitation_probability.slice(0, args.hours);

      return {
        content: [{ type: "text", text: `Next ${args.hours} hours: ${chances.join("%, ")}%` }]
      };
    }
  );

  // 両方のツールを配列で再構築します
  const weatherServer = createSdkMcpServer({
    name: "weather",
    version: "1.0.0",
    tools: [getTemperature, getPrecipitationChance]
  });
  ```
</CodeGroup>

この配列内のすべてのツールは、毎ターン、コンテキストウィンドウスペースを消費します。数十のツールを定義している場合は、[ツール検索](/docs/ja/agent-sdk/tool-search)を参照して、代わりにオンデマンドで読み込みます。

<h3 id="add-tool-annotations">
  ツール注釈を追加する
</h3>

[ツール注釈](https://modelcontextprotocol.io/docs/concepts/tools#tool-annotations)は、ツールの動作を説明するオプションのメタデータです。TypeScript の `tool()` ヘルパーの 5 番目の引数として、または Python の `@tool` デコレーターの `annotations` キーワード引数として渡します。すべてのヒントフィールドはブール値です。

| フィールド             | デフォルト   | 意味                                                |
| :---------------- | :------ | :------------------------------------------------ |
| `readOnlyHint`    | `false` | ツールは環境を変更しません。ツールが他の読み取り専用ツールと並列で呼び出せるかどうかを制御します。 |
| `destructiveHint` | `true`  | ツールは破壊的な更新を実行する可能性があります。情報提供のみです。                 |
| `idempotentHint`  | `false` | 同じ引数での繰り返し呼び出しは追加の効果がありません。情報提供のみです。              |
| `openWorldHint`   | `true`  | ツールはプロセス外のシステムに到達します。情報提供のみです。                    |

注釈はメタデータであり、強制ではありません。`readOnlyHint: true` でマークされたツールは、ハンドラーがそれを行う場合、ディスクに書き込むことができます。注釈をハンドラーに正確に保ちます。

この例は、[天気ツールの例](#weather-tool-example)の `get_temperature` ツールに `readOnlyHint` を追加します。

<CodeGroup>
  ```python Python theme={null}
  from claude_agent_sdk import tool, ToolAnnotations


  @tool(
      "get_temperature",
      "Get the current temperature at a location",
      {"latitude": float, "longitude": float},
      annotations=ToolAnnotations(
          readOnlyHint=True
      ),  # Claude がこれを他の読み取り専用呼び出しとバッチ処理できるようにします
  )
  async def get_temperature(args):
      return {"content": [{"type": "text", "text": "..."}]}
  ```

  ```typescript TypeScript theme={null}
  tool(
    "get_temperature",
    "Get the current temperature at a location",
    { latitude: z.number(), longitude: z.number() },
    async (args) => ({ content: [{ type: "text", text: `...` }] }),
    { annotations: { readOnlyHint: true } } // Claude がこれを他の読み取り専用呼び出しとバッチ処理できるようにします
  );
  ```
</CodeGroup>

[TypeScript](/docs/ja/agent-sdk/typescript#toolannotations) または [Python](/docs/ja/agent-sdk/python#toolannotations) リファレンスで `ToolAnnotations` を参照してください。

<h2 id="control-tool-access">
  ツールアクセスを制御する
</h2>

[天気ツールの例](#weather-tool-example)はサーバーを登録し、`allowedTools` にツールをリストしました。このセクションでは、ツール名がどのように構成されるか、および複数のツールがある場合や組み込みを制限したい場合にアクセスをスコープする方法について説明します。

<h3 id="tool-name-format">
  ツール名形式
</h3>

MCP ツールが Claude に公開されるとき、それらの名前は特定の形式に従います。

* パターン：`mcp__{server_name}__{tool_name}`
* 例：`weather` サーバーの `get_temperature` という名前のツールは `mcp__weather__get_temperature` になります

<h3 id="configure-allowed-tools">
  許可されたツールを設定する
</h3>

`tools` オプションと許可/禁止リストは 2 つのレイヤーに影響します。可用性はツールが Claude のコンテキストに表示されるかどうかを制御し、許可は Claude がそれを試みた後に呼び出しが承認されるかどうかを制御します。`tools` と裸の名前の `disallowedTools` エントリは可用性を変更します。`allowedTools` とスコープされた `disallowedTools` ルールは許可のみを変更します。

| オプション                     | レイヤー | 効果                                                                                                                                  |
| :------------------------ | :--- | :---------------------------------------------------------------------------------------------------------------------------------- |
| `tools: ["Read", "Grep"]` | 可用性  | リストされた組み込みのみが Claude のコンテキストにあります。リストされていない組み込みは削除されます。MCP ツールは影響を受けません。                                                            |
| `tools: []`               | 可用性  | すべての組み込みが削除されます。Claude は MCP ツールのみを使用できます。                                                                                          |
| 許可されたツール                  | 許可   | リストされたツールは許可プロンプトなしで実行されます。リストされていないツールは利用可能なままです。呼び出しは[許可フロー](/docs/ja/agent-sdk/permissions)を通ります。                                     |
| 禁止されたツール                  | 両方   | `"Bash"` などの裸のツール名はツールを Claude のコンテキストから削除します。これは `tools` から省略するのと同じです。`"Bash(rm *)"` などのスコープされたルールはツールをコンテキストに残し、一致する呼び出しのみを拒否します。 |

組み込みを完全に削除するには、`tools` から省略するか、`disallowedTools`（Python：`disallowed_tools`）に裸の名前をリストします。どちらもツールをコンテキストから外すため、Claude はそれを試みることはありません。スコープされた `disallowedTools` ルールは一致する呼び出しをブロックしますが、ツールを表示したままにするため、Claude はそれを試みるターンを無駄にする可能性があります。完全な評価順序については、[許可を設定する](/docs/ja/agent-sdk/permissions)を参照してください。

<h2 id="handle-errors">
  エラーを処理する
</h2>

ハンドラーエラーはエージェントループを停止しません。SDK のインプロセス MCP サーバーはキャッチされない例外をキャッチし、エラー結果として返すため、エラーをどのように報告するかによって Claude が読む内容が決まります。クエリが失敗するかどうかではなく：

| 何が起こるか                                                              | 結果                                                                            |
| :------------------------------------------------------------------ | :---------------------------------------------------------------------------- |
| ハンドラーがキャッチされない例外をスロー                                                | MCP サーバーはそれをエラー結果に変換し、生の例外メッセージを含みます。Claude はそのメッセージを見て、エージェントループが続行します。      |
| ハンドラーがエラーをキャッチして `isError: true`（TS）/ `"is_error": True`（Python）を返す | Claude はあなたが作成したメッセージを見ます。生の例外が欠けているコンテキスト（どのリクエストが失敗したか、代わりに何を試すかなど）を追加できます。 |

どちらの場合も Claude は再試行したり、別のツールを試したり、失敗を説明したりできます。生の例外メッセージが Claude が対応するのに十分でない場合は、自分でエラーをキャッチしてください。

以下の例は、ハンドラー内で 2 種類の障害をキャッチし、Claude が読むエラーメッセージを作成します。200 以外の HTTP ステータスは応答からキャッチされ、エラー結果として返されます。ネットワークエラーまたは無効な JSON は、周囲の `try/except`（Python）または `try/catch`（TypeScript）でキャッチされ、エラー結果としても返されます。どちらの場合も Claude は、生の例外文字列ではなく、失敗を説明するメッセージを受け取ります。

<CodeGroup>
  ```python Python theme={null}
  import json
  import httpx
  from typing import Any


  @tool(
      "fetch_data",
      "Fetch data from an API",
      {"endpoint": str},  # Simple schema
  )
  async def fetch_data(args: dict[str, Any]) -> dict[str, Any]:
      try:
          async with httpx.AsyncClient() as client:
              response = await client.get(args["endpoint"])
              if response.status_code != 200:
                  # Claude が対応できるようにツール結果として失敗を返します。
                  # is_error はこれを失敗した呼び出しとしてマークし、奇妙に見えるデータではなく。
                  return {
                      "content": [
                          {
                              "type": "text",
                              "text": f"API error: {response.status_code} {response.reason_phrase}",
                          }
                      ],
                      "is_error": True,
                  }

              data = response.json()
              return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}
      except Exception as e:
          # Claude が読むメッセージを作成します。キャッチされない例外は
          # コンテキストなしで生の str(e) として Claude に到達します。
          return {
              "content": [{"type": "text", "text": f"Failed to fetch data: {str(e)}"}],
              "is_error": True,
          }
  ```

  ```typescript TypeScript theme={null}
  tool(
    "fetch_data",
    "Fetch data from an API",
    {
      endpoint: z.string().url().describe("API endpoint URL")
    },
    async (args) => {
      try {
        const response = await fetch(args.endpoint);

        if (!response.ok) {
          // Claude が対応できるようにツール結果として失敗を返します。
          // isError はこれを失敗した呼び出しとしてマークし、奇妙に見えるデータではなく。
          return {
            content: [
              {
                type: "text",
                text: `API error: ${response.status} ${response.statusText}`
              }
            ],
            isError: true
          };
        }

        const data = await response.json();
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(data, null, 2)
            }
          ]
        };
      } catch (error) {
        // Claude が読むメッセージを作成します。キャッチされない throw は
        // コンテキストなしで生のエラーメッセージとして Claude に到達します。
        return {
          content: [
            {
              type: "text",
              text: `Failed to fetch data: ${error instanceof Error ? error.message : String(error)}`
            }
          ],
          isError: true
        };
      }
    }
  );
  ```
</CodeGroup>

<h2 id="return-images-and-resources">
  画像とリソースを返す
</h2>

ツール結果の `content` 配列は `text`、`image`、`audio`、`resource`、および `resource_link` ブロックを受け入れます。同じ応答でそれらを混ぜることができます。TypeScript では、オーディオブロックはディスクに保存され、Claude は保存されたファイルパスを含むテキストブロックを受け取ります。Python では、SDK はツール結果からオーディオブロックを削除し、警告をログに記録します。リソースリンクブロックはリンクの名前、URI、および説明を含むテキストブロックに変換されます。

<h3 id="images">
  画像
</h3>

画像ブロックは画像バイトをインラインで、base64 としてエンコードされた状態で運びます。URL フィールドはありません。URL に存在する画像を返すには、ハンドラーで取得し、応答バイトを読み取り、返す前に base64 エンコードします。結果は視覚入力として処理されます。

| フィールド      | 型         | 注釈                                                                 |
| :--------- | :-------- | :----------------------------------------------------------------- |
| `type`     | `"image"` |                                                                    |
| `data`     | `string`  | Base64 エンコードされたバイト。`data:image/...;base64,` プレフィックスなしの生の base64 のみ |
| `mimeType` | `string`  | 必須。例えば `image/png`、`image/jpeg`、`image/webp`、`image/gif`           |

<CodeGroup>
  ```python Python theme={null}
  import base64
  import httpx


  # URL から画像を取得して Claude に返すツールを定義します
  @tool("fetch_image", "Fetch an image from a URL and return it to Claude", {"url": str})
  async def fetch_image(args):
      async with httpx.AsyncClient() as client:  # 画像バイトを取得します
          response = await client.get(args["url"])

      return {
          "content": [
              {
                  "type": "image",
                  "data": base64.b64encode(response.content).decode(
                      "ascii"
                  ),  # 生のバイトを base64 エンコードします
                  "mimeType": response.headers.get(
                      "content-type", "image/png"
                  ),  # 応答から MIME タイプを読み取ります
              }
          ]
      }
  ```

  ```typescript TypeScript theme={null}
  tool(
    "fetch_image",
    "Fetch an image from a URL and return it to Claude",
    {
      url: z.string().url()
    },
    async (args) => {
      const response = await fetch(args.url); // 画像バイトを取得します
      const buffer = Buffer.from(await response.arrayBuffer()); // base64 エンコーディング用にバッファに読み込みます
      const mimeType = response.headers.get("content-type") ?? "image/png";

      return {
        content: [
          {
            type: "image",
            data: buffer.toString("base64"), // 生のバイトを base64 エンコードします
            mimeType
          }
        ]
      };
    }
  );
  ```
</CodeGroup>

<h3 id="resources">
  リソース
</h3>

リソースブロックは URI で識別されるコンテンツを埋め込みます。URI は Claude が参照するためのラベルです。実際のコンテンツはブロックの `text` または `blob` フィールドに含まれます。これは、生成されたファイルや外部システムのレコードなど、後で名前で対処することが理にかなっているツールが生成するものを使用します。

| フィールド               | 型            | 注釈                                                                                     |
| :------------------ | :----------- | :------------------------------------------------------------------------------------- |
| `type`              | `"resource"` |                                                                                        |
| `resource.uri`      | `string`     | コンテンツの識別子。任意の URI スキーム                                                                 |
| `resource.text`     | `string`     | テキストの場合のコンテンツ。`blob` ではなく、これを提供します                                                     |
| `resource.blob`     | `string`     | バイナリの場合、base64 エンコードされたコンテンツ。TypeScript のみ：Python SDK はツール結果からバイナリリソースを削除し、警告をログに記録します |
| `resource.mimeType` | `string`     | オプション                                                                                  |

この例は、ツールハンドラー内から返されるリソースブロックを示しています。URI `file:///tmp/report.md` は Claude が後で参照できるラベルです。SDK はそのパスから読み取りません。

<CodeGroup>
  ```typescript TypeScript theme={null}
  return {
    content: [
      {
        type: "resource",
        resource: {
          uri: "file:///tmp/report.md", // Claude が参照するためのラベル。SDK が読み取るパスではありません
          mimeType: "text/markdown",
          text: "# Report\n..." // 実際のコンテンツ、インライン
        }
      }
    ]
  };
  ```

  ```python Python theme={null}
  return {
      "content": [
          {
              "type": "resource",
              "resource": {
                  "uri": "file:///tmp/report.md",  # Claude が参照するためのラベル。SDK が読み取るパスではありません
                  "mimeType": "text/markdown",
                  "text": "# Report\n...",  # 実際のコンテンツ、インライン
              },
          }
      ]
  }
  ```
</CodeGroup>

これらのブロック形状は MCP `CallToolResult` 型から来ています。完全な定義については、[MCP 仕様](https://modelcontextprotocol.io/specification/2025-06-18/server/tools#tool-result)を参照してください。

<h2 id="return-structured-data">
  構造化データを返す
</h2>

`structuredContent` は結果のオプションの JSON オブジェクトで、`content` 配列とは別です。テキスト文字列または画像から解析する代わりに、Claude が正確なフィールドとして読み取ることができる生の値を返すために使用します。

`structuredContent` が設定されると、Claude は JSON と `content` からの任意の画像またはリソースブロックを受け取ります。`content` のテキストブロックは転送されません。構造化データを複製すると想定されるためです。以下の例は、チャートを画像ブロックとしてレンダリングし、同じハンドラーから `structuredContent` でそれの背後にあるデータポイントを返します。

```typescript TypeScript theme={null}
return {
  content: [
    {
      type: "image",
      data: chartPngBuffer.toString("base64"),
      mimeType: "image/png"
    }
  ],
  structuredContent: {
    series: "temperature_2m",
    unit: "fahrenheit",
    points: [62.1, 63.4, 65.0, 64.2]
  }
};
```

<Note>
  Python `@tool` デコレーターはハンドラーの戻り辞書から `content` と `is_error` のみを転送します。Python から `structuredContent` を返すには、インプロセス SDK サーバーの代わりに [スタンドアロン MCP サーバー](/docs/ja/agent-sdk/mcp)を実行します。
</Note>

<h2 id="example-unit-converter">
  例：単位変換ツール
</h2>

このツールは長さ、温度、重量の単位間で値を変換します。ユーザーは「100 キロメートルをマイルに変換」または「72°F は摂氏何度か」と尋ねることができ、Claude はリクエストから正しい単位タイプと単位を選択します。

2 つのパターンを示しています。

* **列挙型スキーマ：** `unit_type` は固定値のセットに制限されます。TypeScript では `z.enum()` を使用します。Python では、辞書スキーマは列挙型をサポートしないため、完全な JSON Schema 辞書が必要です。
* **サポートされていない入力処理：** 変換ペアが見つからない場合、ハンドラーは `isError: true` を返すため、Claude はユーザーに何が間違っていたかを伝えることができ、失敗を通常の結果として扱いません。

<CodeGroup>
  ```python Python theme={null}
  from typing import Any
  from claude_agent_sdk import tool, create_sdk_mcp_server


  # TypeScript の z.enum() は JSON Schema の "enum" 制約になります。
  # 辞書スキーマに同等のものはないため、完全な JSON Schema が必要です。
  @tool(
      "convert_units",
      "Convert a value from one unit to another",
      {
          "type": "object",
          "properties": {
              "unit_type": {
                  "type": "string",
                  "enum": ["length", "temperature", "weight"],
                  "description": "Category of unit",
              },
              "from_unit": {
                  "type": "string",
                  "description": "Unit to convert from, e.g. kilometers, fahrenheit, pounds",
              },
              "to_unit": {"type": "string", "description": "Unit to convert to"},
              "value": {"type": "number", "description": "Value to convert"},
          },
          "required": ["unit_type", "from_unit", "to_unit", "value"],
      },
  )
  async def convert_units(args: dict[str, Any]) -> dict[str, Any]:
      conversions = {
          "length": {
              "kilometers_to_miles": lambda v: v * 0.621371,
              "miles_to_kilometers": lambda v: v * 1.60934,
              "meters_to_feet": lambda v: v * 3.28084,
              "feet_to_meters": lambda v: v * 0.3048,
          },
          "temperature": {
              "celsius_to_fahrenheit": lambda v: (v * 9) / 5 + 32,
              "fahrenheit_to_celsius": lambda v: (v - 32) * 5 / 9,
              "celsius_to_kelvin": lambda v: v + 273.15,
              "kelvin_to_celsius": lambda v: v - 273.15,
          },
          "weight": {
              "kilograms_to_pounds": lambda v: v * 2.20462,
              "pounds_to_kilograms": lambda v: v * 0.453592,
              "grams_to_ounces": lambda v: v * 0.035274,
              "ounces_to_grams": lambda v: v * 28.3495,
          },
      }

      key = f"{args['from_unit']}_to_{args['to_unit']}"
      fn = conversions.get(args["unit_type"], {}).get(key)

      if not fn:
          return {
              "content": [
                  {
                      "type": "text",
                      "text": f"Unsupported conversion: {args['from_unit']} to {args['to_unit']}",
                  }
              ],
              "is_error": True,
          }

      result = fn(args["value"])
      return {
          "content": [
              {
                  "type": "text",
                  "text": f"{args['value']} {args['from_unit']} = {result:.4f} {args['to_unit']}",
              }
          ]
      }


  converter_server = create_sdk_mcp_server(
      name="converter",
      version="1.0.0",
      tools=[convert_units],
  )
  ```

  ```typescript TypeScript theme={null}
  import { tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
  import { z } from "zod";

  const convert = tool(
    "convert_units",
    "Convert a value from one unit to another",
    {
      unit_type: z.enum(["length", "temperature", "weight"]).describe("Category of unit"),
      from_unit: z
        .string()
        .describe("Unit to convert from, e.g. kilometers, fahrenheit, pounds"),
      to_unit: z.string().describe("Unit to convert to"),
      value: z.number().describe("Value to convert")
    },
    async (args) => {
      type Conversions = Record<string, Record<string, (v: number) => number>>;

      const conversions: Conversions = {
        length: {
          kilometers_to_miles: (v) => v * 0.621371,
          miles_to_kilometers: (v) => v * 1.60934,
          meters_to_feet: (v) => v * 3.28084,
          feet_to_meters: (v) => v * 0.3048
        },
        temperature: {
          celsius_to_fahrenheit: (v) => (v * 9) / 5 + 32,
          fahrenheit_to_celsius: (v) => ((v - 32) * 5) / 9,
          celsius_to_kelvin: (v) => v + 273.15,
          kelvin_to_celsius: (v) => v - 273.15
        },
        weight: {
          kilograms_to_pounds: (v) => v * 2.20462,
          pounds_to_kilograms: (v) => v * 0.453592,
          grams_to_ounces: (v) => v * 0.035274,
          ounces_to_grams: (v) => v * 28.3495
        }
      };

      const key = `${args.from_unit}_to_${args.to_unit}`;
      const fn = conversions[args.unit_type]?.[key];

      if (!fn) {
        return {
          content: [
            {
              type: "text",
              text: `Unsupported conversion: ${args.from_unit} to ${args.to_unit}`
            }
          ],
          isError: true
        };
      }

      const result = fn(args.value);
      return {
        content: [
          {
            type: "text",
            text: `${args.value} ${args.from_unit} = ${result.toFixed(4)} ${args.to_unit}`
          }
        ]
      };
    }
  );

  const converterServer = createSdkMcpServer({
    name: "converter",
    version: "1.0.0",
    tools: [convert]
  });
  ```
</CodeGroup>

サーバーが定義されたら、天気の例と同じ方法で `query` に渡します。この例は、同じツールが異なる単位タイプを処理することを示すために、ループで 3 つの異なるプロンプトを送信します。各応答について、`AssistantMessage` オブジェクト（Claude がそのターン中に行ったツール呼び出しを含む）を検査し、最終的な `ResultMessage` テキストを出力する前に各 `ToolUseBlock` を出力します。これにより、Claude がツールを使用しているのか、独自の知識から答えているのかを確認できます。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import (
      query,
      ClaudeAgentOptions,
      ResultMessage,
      AssistantMessage,
      ToolUseBlock,
  )


  async def main():
      options = ClaudeAgentOptions(
          mcp_servers={"converter": converter_server},
          allowed_tools=["mcp__converter__convert_units"],
      )

      prompts = [
          "Convert 100 kilometers to miles.",
          "What is 72°F in Celsius?",
          "How many pounds is 5 kilograms?",
      ]

      for prompt in prompts:
          async for message in query(prompt=prompt, options=options):
              if isinstance(message, AssistantMessage):
                  for block in message.content:
                      if isinstance(block, ToolUseBlock):
                          print(f"[tool call] {block.name}({block.input})")
              elif isinstance(message, ResultMessage) and message.subtype == "success":
                  print(f"Q: {prompt}\nA: {message.result}\n")


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const prompts = [
    "Convert 100 kilometers to miles.",
    "What is 72°F in Celsius?",
    "How many pounds is 5 kilograms?"
  ];

  for (const prompt of prompts) {
    for await (const message of query({
      prompt,
      options: {
        mcpServers: { converter: converterServer },
        allowedTools: ["mcp__converter__convert_units"]
      }
    })) {
      if (message.type === "assistant") {
        for (const block of message.message.content) {
          if (block.type === "tool_use") {
            console.log(`[tool call] ${block.name}`, block.input);
          }
        }
      } else if (message.type === "result" && message.subtype === "success") {
        console.log(`Q: ${prompt}\nA: ${message.result}\n`);
      }
    }
  }
  ```
</CodeGroup>

<h2 id="next-steps">
  次のステップ
</h2>

カスタムツールは非同期関数を標準インターフェースにラップします。このページのパターンを同じサーバーで混ぜることができます。単一のサーバーは、データベースツール、API ゲートウェイツール、および画像レンダラーを並べて保持できます。

ここから：

* サーバーが数十のツールに成長する場合は、[ツール検索](/docs/ja/agent-sdk/tool-search)を参照して、Claude がそれらを必要とするまで読み込みを遅延させます。
* 独自のツールを構築する代わりに、外部 MCP サーバー（ファイルシステム、GitHub、Slack）に接続するには、[MCP サーバーを接続する](/docs/ja/agent-sdk/mcp)を参照してください。
* どのツールが自動的に実行されるか、承認が必要かを制御するには、[許可を設定する](/docs/ja/agent-sdk/permissions)を参照してください。

<h2 id="related-documentation">
  関連ドキュメント
</h2>

* [TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript)
* [Python SDK リファレンス](/docs/ja/agent-sdk/python)
* [MCP ドキュメント](https://modelcontextprotocol.io)
* [SDK 概要](/docs/ja/agent-sdk/overview)
