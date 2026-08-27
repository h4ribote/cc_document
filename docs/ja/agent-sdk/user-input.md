> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# 承認とユーザー入力を処理する

> Claude の承認リクエストと確認質問をユーザーに表示し、その決定を SDK に返します。

タスクに取り組んでいる間、Claude はユーザーに確認を取る必要がある場合があります。ファイルを削除する前に許可が必要な場合もあれば、新しいプロジェクト用にどのデータベースを使用するかを尋ねる必要がある場合もあります。アプリケーションはこれらのリクエストをユーザーに表示して、Claude がユーザーの入力で続行できるようにする必要があります。

Claude がユーザー入力をリクエストするのは 2 つの状況です。ツールを使用する**許可が必要な場合**（ファイルの削除やコマンドの実行など）と、**確認質問がある場合**（`AskUserQuestion` ツール経由）です。どちらも `canUseTool` コールバックをトリガーし、応答を返すまで実行を一時停止します。これは Claude が終了して次のメッセージを待つ通常の会話ターンとは異なります。

確認質問については、Claude が質問とオプションを生成します。あなたの役割は、それらをユーザーに提示して、ユーザーの選択を返すことです。このフローに独自の質問を追加することはできません。ユーザーに何か尋ねる必要がある場合は、アプリケーションロジックで別途実行してください。

コールバックは無期限に保留中のままにすることができます。実行はコールバックが返されるまで一時停止したままであり、SDK はクエリ自体がキャンセルされた場合にのみ待機をキャンセルします。ユーザーがプロセスが合理的に実行し続けることができるより長く応答するのに時間がかかる可能性がある場合、[`defer` フック決定](/docs/ja/hooks#defer-a-tool-call-for-later)を返します。これにより、プロセスを終了して、後で永続化されたセッションから再開できます。

このガイドでは、各タイプのリクエストを検出し、適切に応答する方法を示します。

<h2 id="detect-when-claude-needs-input">
  Claude が入力を必要とする場合を検出する
</h2>

クエリオプションで `canUseTool` コールバックを渡します。Claude がユーザー入力を必要とするたびにコールバックが発火し、ツール名と入力を引数として受け取ります。

<CodeGroup>
  ```python Python theme={null}
  async def handle_tool_request(tool_name, input_data, context):
      # ユーザーにプロンプトを表示して、許可または拒否を返す
      ...


  options = ClaudeAgentOptions(can_use_tool=handle_tool_request)
  ```

  ```typescript TypeScript theme={null}
  async function handleToolRequest(toolName, input, options) {
    // options には { signal: AbortSignal, suggestions?: PermissionUpdate[] } が含まれます
    // ユーザーにプロンプトを表示して、許可または拒否を返す
  }

  const options = { canUseTool: handleToolRequest };
  ```
</CodeGroup>

コールバックは 2 つのケースで発火します。

1. **ツールが承認を必要とする場合**：Claude が [許可ルール](/docs/ja/agent-sdk/permissions)またはモードによって自動承認されていないツールを使用したい場合。`tool_name` でツール（例：`"Bash"`、`"Write"`）を確認します。
2. **Claude が質問をする場合**：Claude が `AskUserQuestion` ツールを呼び出します。`tool_name == "AskUserQuestion"` をチェックして、異なる方法で処理します。`tools` 配列を指定する場合は、これが機能するように `AskUserQuestion` を含めます。詳細は [確認質問を処理する](#handle-clarifying-questions)を参照してください。

<Warning>
  **コールバックは自動承認されたツールに対しては発火しません。** [許可評価フロー](/docs/ja/agent-sdk/permissions#how-permissions-are-evaluated)の前の段階での承認、許可ルール、または `acceptEdits` や `bypassPermissions` のようなモードは、`canUseTool` が参照される前に呼び出しを解決します。`allowed_tools` にツールをそのまま列挙する場合、そのツールに対する `canUseTool` チェックは、ask ルールまたは `plan` モードが呼び出しをプロンプトに戻さない限り実行されません。すべてのツール呼び出しに適用する必要があるロジックについては、[`PreToolUse` フック](/docs/ja/agent-sdk/hooks)を使用してください。このフックはフローの残りの部分の前に実行され、リクエストを許可、拒否、または変更できます。

  `AskUserQuestion`、[`requiresUserInteraction`](/docs/ja/mcp#require-approval-for-a-specific-tool)とマークされた MCP ツール、および [組織が `ask` に設定したコネクタツール](/docs/ja/mcp#organization-controls-on-connector-tools)は、許可ルールが一致する場合でもコールバックに到達します。`dontAsk` モードではこれらの呼び出しは代わりに拒否され、コールバックは呼び出されません。
</Warning>

また、[`PermissionRequest` フック](/docs/ja/agent-sdk/hooks#available-hooks)を使用して、Claude が承認を待っているときに外部通知（Slack、メール、プッシュ）を送信することもできます。

<h2 id="handle-tool-approval-requests">
  ツール承認リクエストを処理する
</h2>

クエリオプションで `canUseTool` コールバックを渡すと、Claude が自動承認されていないツールを使用したい場合に発火します。コールバックは 3 つの引数を受け取ります。

| 引数                               | 説明                                                                                                                                                                                                                                                                 |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `toolName`                       | Claude が使用したいツールの名前（例：`"Bash"`、`"Write"`、`"Edit"`）                                                                                                                                                                                                                 |
| `input`                          | Claude がツールに渡しているパラメーター。内容はツールによって異なります。                                                                                                                                                                                                                           |
| `options`（TS）/ `context`（Python） | 再度プロンプトを表示しないための提案された `PermissionUpdate` エントリを含むオプション `suggestions` とキャンセル信号を含む追加コンテキスト。TypeScript では、`signal` は `AbortSignal` です。Python では、信号フィールドは将来の使用のために予約されています。Python については [`ToolPermissionContext`](/docs/ja/agent-sdk/python#toolpermissioncontext)を参照してください。 |

`input` オブジェクトにはツール固有のパラメーターが含まれます。一般的な例：

| ツール     | 入力フィールド                               |
| ------- | ------------------------------------- |
| `Bash`  | `command`、`description`、`timeout`     |
| `Write` | `file_path`、`content`                 |
| `Edit`  | `file_path`、`old_string`、`new_string` |
| `Read`  | `file_path`、`offset`、`limit`          |

完全な入力スキーマについては SDK リファレンスを参照してください。[Python](/docs/ja/agent-sdk/python#tool-input%2Foutput-types) | [TypeScript](/docs/ja/agent-sdk/typescript#tool-input-types)。

この情報をユーザーに表示して、アクションを許可するか拒否するかを決定してから、適切な応答を返すことができます。

次の例では、Claude にテストファイルを作成して削除するよう要求します。Claude が各操作を試みるたびに、コールバックはツールリクエストをターミナルに出力し、y/n 承認を求めます。

<CodeGroup>
  ```python Python theme={null}
  import asyncio

  from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
  from claude_agent_sdk.types import (
      HookMatcher,
      PermissionResultAllow,
      PermissionResultDeny,
      ToolPermissionContext,
  )


  async def can_use_tool(
      tool_name: str, input_data: dict, context: ToolPermissionContext
  ) -> PermissionResultAllow | PermissionResultDeny:
      # ツールリクエストを表示する
      print(f"\nTool: {tool_name}")
      if tool_name == "Bash":
          print(f"Command: {input_data.get('command')}")
          if input_data.get("description"):
              print(f"Description: {input_data.get('description')}")
      else:
          print(f"Input: {input_data}")

      # ユーザーの承認を取得する
      response = input("Allow this action? (y/n): ")

      # ユーザーの応答に基づいて許可または拒否を返す
      if response.lower() == "y":
          # 許可：ツールは元の（または変更された）入力で実行される
          return PermissionResultAllow(updated_input=input_data)
      else:
          # 拒否：ツールは実行されず、Claude はメッセージを見る
          return PermissionResultDeny(message="User denied this action")


  # 必須の回避策：ダミーフックはストリームを canUseTool 用に開いたままにします
  async def dummy_hook(input_data, tool_use_id, context):
      return {"continue_": True}


  async def prompt_stream():
      yield {
          "type": "user",
          "message": {
              "role": "user",
              "content": "Create a test file in /tmp and then delete it",
          },
      }


  async def main():
      async for message in query(
          prompt=prompt_stream(),
          options=ClaudeAgentOptions(
              can_use_tool=can_use_tool,
              hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[dummy_hook])]},
          ),
      ):
          if isinstance(message, ResultMessage) and message.subtype == "success":
              print(message.result)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";
  import * as readline from "readline";

  // ターミナルでユーザー入力を求めるヘルパー
  function prompt(question: string): Promise<string> {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    return new Promise((resolve) =>
      rl.question(question, (answer) => {
        rl.close();
        resolve(answer);
      })
    );
  }

  for await (const message of query({
    prompt: "Create a test file in /tmp and then delete it",
    options: {
      canUseTool: async (toolName, input) => {
        // ツールリクエストを表示する
        console.log(`\nTool: ${toolName}`);
        if (toolName === "Bash") {
          console.log(`Command: ${input.command}`);
          if (input.description) console.log(`Description: ${input.description}`);
        } else {
          console.log(`Input: ${JSON.stringify(input, null, 2)}`);
        }

        // ユーザーの承認を取得する
        const response = await prompt("Allow this action? (y/n): ");

        // ユーザーの応答に基づいて許可または拒否を返す
        if (response.toLowerCase() === "y") {
          // 許可：ツールは元の（または変更された）入力で実行される
          return { behavior: "allow", updatedInput: input };
        } else {
          // 拒否：ツールは実行されず、Claude はメッセージを見る
          return { behavior: "deny", message: "User denied this action" };
        }
      }
    }
  })) {
    if ("result" in message) console.log(message.result);
  }
  ```
</CodeGroup>

<Note>
  Python では、`can_use_tool` は [ストリーミングモード](/docs/ja/agent-sdk/streaming-vs-single-mode)が必要です。有限のメッセージストリームを `query(prompt=generator)` または `ClaudeSDKClient.connect(prompt=async_iterable)` を通じて渡すと、登録されたフックまたはプロセス内 MCP サーバーがストリームを開いたままにしていない限り、SDK は最後のメッセージの後、許可コールバックが呼び出される前にストリームを閉じます。上記の例は、`{"continue_": True}` を返す `PreToolUse` フックでストリームを開いたままにします。プロンプトなしで接続し、`ClaudeSDKClient.query()` を通じてメッセージを送信すると、ストリームは自動的に開いたままになり、フックは不要です。
</Note>

この例では y/n フローを使用しており、`y` 以外の入力は拒否として扱われます。実際には、ユーザーがリクエストを変更したり、フィードバックを提供したり、Claude を完全にリダイレクトしたりできるより豊富な UI を構築する可能性があります。すべての応答方法については [ツールリクエストに応答する](#respond-to-tool-requests)を参照してください。

<h3 id="respond-to-tool-requests">
  ツールリクエストに応答する
</h3>

コールバックは 2 つの応答タイプのいずれかを返します。

| 応答     | Python                                     | TypeScript                            |
| ------ | ------------------------------------------ | ------------------------------------- |
| **許可** | `PermissionResultAllow(updated_input=...)` | `{ behavior: "allow", updatedInput }` |
| **拒否** | `PermissionResultDeny(message=...)`        | `{ behavior: "deny", message }`       |

許可する場合、Claude がリクエストした入力でツールが実行されます。ただし、変更された入力を返す場合は、TypeScript では `updatedInput`、Python では `updated_input` を返すことができます。v2.1.207 より前では、Claude Code は `updatedInput` を省略した許可結果を拒否し、検証エラーでツール呼び出しを拒否していました。

拒否する場合、理由を説明するメッセージを提供します。Claude はこのメッセージを見て、アプローチを調整する可能性があります。

<CodeGroup>
  ```python Python theme={null}
  from claude_agent_sdk.types import PermissionResultAllow, PermissionResultDeny

  # ツールの実行を許可する
  return PermissionResultAllow(updated_input=input_data)

  # ツールをブロックする
  return PermissionResultDeny(message="User rejected this action")
  ```

  ```typescript TypeScript theme={null}
  // ツールの実行を許可する
  return { behavior: "allow", updatedInput: input };

  // ツールをブロックする
  return { behavior: "deny", message: "User rejected this action" };
  ```
</CodeGroup>

許可または拒否を超えて、ツールの入力を変更したり、Claude がアプローチを調整するのに役立つコンテキストを提供したりできます。

* **承認**：ツールを Claude がリクエストしたとおりに実行させる
* **変更を加えて承認**：実行前に入力を変更する（例：パスをサニタイズ、制約を追加）
* **承認して記憶**：提案された許可ルールをエコーバックして、一致する呼び出しが次回プロンプトをスキップするようにする
* **拒否**：ツールをブロックして Claude に理由を伝える
* **代替案を提案**：ブロックするが、ユーザーが望むものに向かって Claude をガイドする
* **完全にリダイレクト**：[ストリーミング入力](/docs/ja/agent-sdk/streaming-vs-single-mode)を使用して Claude に完全に新しい指示を送信する

<Tabs>
  <Tab title="承認">
    ユーザーはアクションをそのまま承認します。コールバックから `input` をそのまま渡し、ツールは Claude がリクエストしたとおりに実行されます。

    <CodeGroup>
      ```python Python theme={null}
      async def can_use_tool(tool_name, input_data, context):
          print(f"Claude wants to use {tool_name}")
          approved = await ask_user("Allow this action?")

          if approved:
              return PermissionResultAllow(updated_input=input_data)
          return PermissionResultDeny(message="User declined")
      ```

      ```typescript TypeScript theme={null}
      canUseTool: async (toolName, input) => {
        console.log(`Claude wants to use ${toolName}`);
        const approved = await askUser("Allow this action?");

        if (approved) {
          return { behavior: "allow", updatedInput: input };
        }
        return { behavior: "deny", message: "User declined" };
      };
      ```
    </CodeGroup>
  </Tab>

  <Tab title="変更を加えて承認">
    ユーザーは承認しますが、最初にリクエストを変更したいと考えています。ツールが実行される前に入力を変更できます。Claude は結果を見ますが、何かを変更したことは伝えられません。パラメーターをサニタイズ、制約を追加、またはアクセスをスコープするのに役立ちます。

    <CodeGroup>
      ```python Python theme={null}
      async def can_use_tool(tool_name, input_data, context):
          if tool_name == "Bash":
              # ユーザーが承認しましたが、すべてのコマンドをサンドボックスにスコープします
              sandboxed_input = {**input_data}
              sandboxed_input["command"] = input_data["command"].replace(
                  "/tmp", "/tmp/sandbox"
              )
              return PermissionResultAllow(updated_input=sandboxed_input)
          return PermissionResultAllow(updated_input=input_data)
      ```

      ```typescript TypeScript theme={null}
      canUseTool: async (toolName, input) => {
        if (toolName === "Bash") {
          // ユーザーが承認しましたが、すべてのコマンドをサンドボックスにスコープします
          const sandboxedInput = {
            ...input,
            command: input.command.replace("/tmp", "/tmp/sandbox")
          };
          return { behavior: "allow", updatedInput: sandboxedInput };
        }
        return { behavior: "allow", updatedInput: input };
      };
      ```
    </CodeGroup>
  </Tab>

  <Tab title="承認して記憶">
    ユーザーが承認し、この種の呼び出しについて再度尋ねられたくない場合。3 番目のコールバック引数は `suggestions` を含み、これは準備完了した [`PermissionUpdate`](/docs/ja/agent-sdk/typescript#permissionupdate) エントリの配列です。`updatedPermissions` で 1 つをエコーバックして適用します。`localSettings` 宛先を持つ提案は、ルールを `.claude/settings.local.json` に書き込むため、将来のセッションは一致する呼び出しのプロンプトをスキップします。

    Python の例には `claude-agent-sdk` 0.1.80 以降が必要です。

    <CodeGroup>
      ```python Python theme={null}
      async def can_use_tool(tool_name, input_data, context):
          choice = await ask_user(f"Allow {tool_name}?", ["once", "always", "no"])

          if choice == "always":
              persist = [
                  s for s in context.suggestions if s.destination == "localSettings"
              ]
              return PermissionResultAllow(
                  updated_input=input_data, updated_permissions=persist
              )
          if choice == "once":
              return PermissionResultAllow(updated_input=input_data)
          return PermissionResultDeny(message="User declined")
      ```

      ```typescript TypeScript theme={null}
      canUseTool: async (toolName, input, { suggestions = [] }) => {
        const choice = await askUser(`Allow ${toolName}?`, ["once", "always", "no"]);

        if (choice === "always") {
          const persist = suggestions.filter(
            (s) => s.destination === "localSettings"
          );
          return {
            behavior: "allow",
            updatedInput: input,
            updatedPermissions: persist
          };
        }
        if (choice === "once") {
          return { behavior: "allow", updatedInput: input };
        }
        return { behavior: "deny", message: "User declined" };
      };
      ```
    </CodeGroup>
  </Tab>

  <Tab title="拒否">
    ユーザーはこのアクションが実行されることを望んでいません。ツールをブロックして、理由を説明するメッセージを提供します。Claude はこのメッセージを見て、別のアプローチを試す可能性があります。

    <CodeGroup>
      ```python Python theme={null}
      async def can_use_tool(tool_name, input_data, context):
          approved = await ask_user(f"Allow {tool_name}?")

          if not approved:
              return PermissionResultDeny(message="User rejected this action")
          return PermissionResultAllow(updated_input=input_data)
      ```

      ```typescript TypeScript theme={null}
      canUseTool: async (toolName, input) => {
        const approved = await askUser(`Allow ${toolName}?`);

        if (!approved) {
          return {
            behavior: "deny",
            message: "User rejected this action"
          };
        }
        return { behavior: "allow", updatedInput: input };
      };
      ```
    </CodeGroup>
  </Tab>

  <Tab title="代替案を提案">
    ユーザーはこの特定のアクションを望んでいませんが、別のアイデアがあります。ツールをブロックして、メッセージにガイダンスを含めます。Claude はこれを読んで、フィードバックに基づいて進行方法を決定します。

    <CodeGroup>
      ```python Python theme={null}
      async def can_use_tool(tool_name, input_data, context):
          if tool_name == "Bash" and "rm" in input_data.get("command", ""):
              # ユーザーは削除を望んでいません。代わりにアーカイブに圧縮することを提案します
              return PermissionResultDeny(
                  message="User doesn't want to delete files. They asked if you could compress them into an archive instead."
              )
          return PermissionResultAllow(updated_input=input_data)
      ```

      ```typescript TypeScript theme={null}
      canUseTool: async (toolName, input) => {
        if (toolName === "Bash" && input.command.includes("rm")) {
          // ユーザーは削除を望んでいません。代わりにアーカイブに圧縮することを提案します
          return {
            behavior: "deny",
            message:
              "User doesn't want to delete files. They asked if you could compress them into an archive instead."
          };
        }
        return { behavior: "allow", updatedInput: input };
      };
      ```
    </CodeGroup>
  </Tab>

  <Tab title="完全にリダイレクト">
    方向の完全な変更（単なるナッジではなく）の場合は、[ストリーミング入力](/docs/ja/agent-sdk/streaming-vs-single-mode)を使用して Claude に新しい指示を直接送信します。これは現在のツールリクエストをバイパスし、Claude に完全に新しい指示に従うように指示します。
  </Tab>
</Tabs>

<h2 id="handle-clarifying-questions">
  確認質問を処理する
</h2>

Claude が複数の有効なアプローチを持つタスクについてさらに方向性が必要な場合、`AskUserQuestion` ツールを呼び出します。これは `toolName` が `AskUserQuestion` に設定された `canUseTool` コールバックをトリガーします。入力には Claude の質問が複数選択肢として含まれており、これらをユーザーに表示して、ユーザーの選択を返します。

<Tip>
  確認質問は特に [`plan` モード](/docs/ja/agent-sdk/permissions#plan-mode-plan)で一般的です。Claude はコードベースを探索し、計画を提案する前に質問をします。これにより、プラン モードは Claude が変更を加える前に要件を収集したい対話的なワークフローに最適です。
</Tip>

次のステップは、確認質問を処理する方法を示しています。

<Steps>
  <Step title="canUseTool コールバックを渡す">
    クエリオプションで `canUseTool` コールバックを渡します。デフォルトでは、`AskUserQuestion` が利用可能です。Claude の機能を制限するために `tools` 配列を指定する場合（例：`Read`、`Glob`、`Grep` のみを持つ読み取り専用エージェント）、その配列に `AskUserQuestion` を含めます。そうしないと、Claude は確認質問をすることができません。

    <CodeGroup>
      ```python Python theme={null}
      async for message in query(
          prompt="Analyze this codebase",
          options=ClaudeAgentOptions(
              # ツールリストに AskUserQuestion を含める
              tools=["Read", "Glob", "Grep", "AskUserQuestion"],
              can_use_tool=can_use_tool,
          ),
      ):
          print(message)
      ```

      ```typescript TypeScript theme={null}
      for await (const message of query({
        prompt: "Analyze this codebase",
        options: {
          // ツールリストに AskUserQuestion を含める
          tools: ["Read", "Glob", "Grep", "AskUserQuestion"],
          canUseTool: async (toolName, input) => {
            // ここで確認質問を処理する
          }
        }
      })) {
        console.log(message);
      }
      ```
    </CodeGroup>
  </Step>

  <Step title="AskUserQuestion を検出する">
    コールバックで、`toolName` が `AskUserQuestion` と等しいかどうかをチェックして、他のツールとは異なる方法で処理します。

    <CodeGroup>
      ```python Python theme={null}
      async def can_use_tool(tool_name: str, input_data: dict, context):
          if tool_name == "AskUserQuestion":
              # ユーザーから回答を収集するための実装
              return await handle_clarifying_questions(input_data)
          # 他のツールを通常どおり処理する
          return await prompt_for_approval(tool_name, input_data)
      ```

      ```typescript TypeScript theme={null}
      canUseTool: async (toolName, input) => {
        if (toolName === "AskUserQuestion") {
          // ユーザーから回答を収集するための実装
          return handleClarifyingQuestions(input);
        }
        // 他のツールを通常どおり処理する
        return promptForApproval(toolName, input);
      };
      ```
    </CodeGroup>
  </Step>

  <Step title="質問入力を解析する">
    入力には Claude の質問が `questions` 配列に含まれています。各質問には `question`（表示するテキスト）、`options`（選択肢）、`multiSelect`（複数選択が許可されているかどうか）があります。

    ```json theme={null}
    {
      "questions": [
        {
          "question": "How should I format the output?",
          "header": "Format",
          "options": [
            { "label": "Summary", "description": "Brief overview" },
            { "label": "Detailed", "description": "Full explanation" }
          ],
          "multiSelect": false
        },
        {
          "question": "Which sections should I include?",
          "header": "Sections",
          "options": [
            { "label": "Introduction", "description": "Opening context" },
            { "label": "Conclusion", "description": "Final summary" }
          ],
          "multiSelect": true
        }
      ]
    }
    ```

    完全なフィールド説明については [質問形式](#question-format)を参照してください。
  </Step>

  <Step title="ユーザーから回答を収集する">
    質問をユーザーに提示して、ユーザーの選択を収集します。これをどのように行うかは、アプリケーションによって異なります。ターミナルプロンプト、Web フォーム、モバイルダイアログなど。
  </Step>

  <Step title="Claude に回答を返す">
    `answers` オブジェクトをレコードとして構築します。各キーは `question` テキストで、各値は選択されたオプションの `label` です。

    | 質問オブジェクトから                                              | 使用方法 |
    | ------------------------------------------------------- | ---- |
    | `question` フィールド（例：`"How should I format the output?"`） | キー   |
    | 選択されたオプションの `label` フィールド（例：`"Summary"`）                | 値    |

    複数選択質問の場合、ラベルの配列を渡すか、`", "` で結合します。[自由テキスト入力をサポート](#support-free-text-input)する場合は、ユーザーのカスタムテキストを値として使用します。

    <CodeGroup>
      ```python Python theme={null}
      return PermissionResultAllow(
          updated_input={
              "questions": input_data.get("questions", []),
              "answers": {
                  "How should I format the output?": "Summary",
                  "Which sections should I include?": ["Introduction", "Conclusion"],
              },
          }
      )
      ```

      ```typescript TypeScript theme={null}
      return {
        behavior: "allow",
        updatedInput: {
          questions: input.questions,
          answers: {
            "How should I format the output?": "Summary",
            "Which sections should I include?": "Introduction, Conclusion"
          }
        }
      };
      ```
    </CodeGroup>
  </Step>
</Steps>

<h3 id="question-format">
  質問形式
</h3>

入力には Claude が生成した質問が `questions` 配列に含まれています。各質問には以下のフィールドがあります。

| フィールド         | 説明                                                                                                                              |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `question`    | 表示する完全な質問テキスト                                                                                                                   |
| `header`      | 質問の短いラベル（最大 12 文字）                                                                                                              |
| `options`     | 2～4 個の選択肢の配列。各選択肢には `label` と `description` があります。TypeScript：オプションで `preview`（下記の [オプションプレビュー](#option-previews-typescript)を参照） |
| `multiSelect` | `true` の場合、ユーザーは複数のオプションを選択できます                                                                                                 |

コールバックが受け取る構造：

```json theme={null}
{
  "questions": [
    {
      "question": "How should I format the output?",
      "header": "Format",
      "options": [
        { "label": "Summary", "description": "Brief overview of key points" },
        { "label": "Detailed", "description": "Full explanation with examples" }
      ],
      "multiSelect": false
    }
  ]
}
```

<h4 id="option-previews-typescript">
  オプションプレビュー（TypeScript）
</h4>

`toolConfig.askUserQuestion.previewFormat` は各オプションに `preview` フィールドを追加して、アプリがラベルと一緒に視覚的なモックアップを表示できるようにします。この設定がない場合、Claude はプレビューを生成せず、フィールドは存在しません。

| `previewFormat` | `preview` に含まれるもの                                                                   |
| :-------------- | :---------------------------------------------------------------------------------- |
| 未設定（デフォルト）      | フィールドは存在しません。Claude はプレビューを生成しません。                                                  |
| `"markdown"`    | ASCII アートとフェンスコードブロック                                                               |
| `"html"`        | スタイル付き `<div>` フラグメント（SDK はコールバックが実行される前に `<script>`、`<style>`、`<!DOCTYPE>` を拒否します） |

形式はセッション内のすべての質問に適用されます。Claude は視覚的な比較が役立つオプション（レイアウト選択、配色）に `preview` を含め、役立たないオプション（はい/いいえの確認、テキストのみの選択）では省略します。レンダリング前に `undefined` をチェックしてください。

```typescript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Help me choose a card layout",
  options: {
    toolConfig: {
      askUserQuestion: { previewFormat: "html" }
    },
    canUseTool: async (toolName, input) => {
      // input.questions[].options[].preview は HTML 文字列または undefined です
      return { behavior: "allow", updatedInput: input };
    }
  }
})) {
  // ...
}
```

HTML プレビュー付きのオプション：

```json theme={null}
{
  "label": "Compact",
  "description": "Title and metric value only",
  "preview": "<div style=\"padding:12px;border:1px solid #ddd;border-radius:8px\"><div style=\"font-size:12px;color:#666\">Active users</div><div style=\"font-size:28px;font-weight:600\">1,284</div></div>"
}
```

<h3 id="response-format">
  応答形式
</h3>

各質問の `question` フィールドを選択されたオプションの `label` にマップする `answers` オブジェクトを返します。

| フィールド       | 説明                                      |
| ----------- | --------------------------------------- |
| `questions` | 元の質問配列をパススルーする（ツール処理に必須）                |
| `answers`   | キーが質問テキストで、値が選択されたラベルであるオブジェクト          |
| `response`  | ユーザーが構造化された質問に答える代わりに入力した、オプションの自由形式の返信 |

複数選択質問の場合、ラベルの配列を渡すか、`", "` で結合します。[自由テキスト入力をサポート](#support-free-text-input)に示されているような質問ごとの自由テキスト（例：「その他」オプション）の場合は、ユーザーのテキストを `answers[question]` に入力します。`response` は、ユーザーが質問カードを閉じて、特定の質問への回答ではない一般的な返信を入力できる UI の場合にのみ設定します。`response` が設定されている場合、Claude は質問ごとの回答リストではなく「ユーザーが応答しました：…」を受け取ります。

```json theme={null}
{
  "questions": [
    // ...
  ],
  "answers": {
    "How should I format the output?": "Summary",
    "Which sections should I include?": ["Introduction", "Conclusion"]
  }
}
```

<h4 id="support-free-text-input">
  自由テキスト入力をサポートする
</h4>

Claude の定義済みオプションがユーザーが望むものをカバーしていない場合があります。ユーザーが独自の回答を入力できるようにするには：

* Claude のオプションの後に追加の「その他」選択肢を表示して、テキスト入力を受け入れます
* ユーザーのカスタムテキストを回答値として使用します（「その他」という単語ではなく）

完全な実装については、下記の [完全な例](#complete-example)を参照してください。

<h3 id="complete-example">
  完全な例
</h3>

Claude は、タスクを進めるためにユーザー入力が必要な場合に確認質問をします。たとえば、モバイルアプリのテックスタックを決定するのに役立つよう求められた場合、Claude はクロスプラットフォーム対応 vs ネイティブ、バックエンド設定、またはターゲットプラットフォームについて質問する可能性があります。これらの質問は、Claude がユーザーの設定に合致する決定を下すのに役立ちます。推測ではなく。

この例は、ターミナルアプリケーションでこれらの質問を処理します。各ステップで何が起こるかは以下の通りです。

1. **リクエストをルーティングする**：`canUseTool` コールバックはツール名が `"AskUserQuestion"` であるかどうかをチェックし、専用ハンドラーにルーティングします
2. **質問を表示する**：ハンドラーは `questions` 配列をループして、各質問を番号付きオプションで出力します
3. **入力を収集する**：ユーザーはオプションを選択する番号を入力するか、自由テキストを直接入力できます（例：「jquery」、「i don't know」）
4. **回答をマップする**：コードは入力が数値（オプションのラベルを使用）か自由テキスト（テキストを直接使用）かをチェックします
5. **Claude に返す**：応答には元の `questions` 配列と `answers` マッピングの両方が含まれます

TypeScript バージョンを `ask.ts` として保存して `npx tsx ask.ts` で実行するか、Python バージョンを `ask.py` として保存して `python ask.py` で実行してください。

<CodeGroup>
  ```python Python theme={null}
  import asyncio

  from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
  from claude_agent_sdk.types import HookMatcher, PermissionResultAllow


  def parse_response(response: str, options: list) -> str:
      """ユーザー入力をオプション番号または自由テキストとして解析します。"""
      try:
          indices = [int(s.strip()) - 1 for s in response.split(",")]
          labels = [options[i]["label"] for i in indices if 0 <= i < len(options)]
          return ", ".join(labels) if labels else response
      except ValueError:
          return response


  async def handle_ask_user_question(input_data: dict) -> PermissionResultAllow:
      """Claude の質問を表示してユーザーの回答を収集します。"""
      answers = {}

      for q in input_data.get("questions", []):
          print(f"\n{q['header']}: {q['question']}")

          options = q["options"]
          for i, opt in enumerate(options):
              print(f"  {i + 1}. {opt['label']} - {opt['description']}")
          if q.get("multiSelect"):
              print("  (Enter numbers separated by commas, or type your own answer)")
          else:
              print("  (Enter a number, or type your own answer)")

          response = input("Your choice: ").strip()
          answers[q["question"]] = parse_response(response, options)

      return PermissionResultAllow(
          updated_input={
              "questions": input_data.get("questions", []),
              "answers": answers,
          }
      )


  async def can_use_tool(
      tool_name: str, input_data: dict, context
  ) -> PermissionResultAllow:
      # AskUserQuestion を質問ハンドラーにルーティングする
      if tool_name == "AskUserQuestion":
          return await handle_ask_user_question(input_data)
      # この例では他のツールを自動承認する
      return PermissionResultAllow(updated_input=input_data)


  async def prompt_stream():
      yield {
          "type": "user",
          "message": {
              "role": "user",
              "content": "Help me decide on the tech stack for a new mobile app",
          },
      }


  # 必須の回避策：ダミーフックはストリームを canUseTool 用に開いたままにします
  async def dummy_hook(input_data, tool_use_id, context):
      return {"continue_": True}


  async def main():
      async for message in query(
          prompt=prompt_stream(),
          options=ClaudeAgentOptions(
              can_use_tool=can_use_tool,
              hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[dummy_hook])]},
          ),
      ):
          if isinstance(message, ResultMessage) and message.subtype == "success":
              print(message.result)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";
  import * as readline from "readline/promises";

  // ターミナルでユーザー入力を求めるヘルパー
  async function prompt(question: string): Promise<string> {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const answer = await rl.question(question);
    rl.close();
    return answer;
  }

  // ユーザー入力をオプション番号または自由テキストとして解析する
  function parseResponse(response: string, options: any[]): string {
    const indices = response.split(",").map((s) => parseInt(s.trim()) - 1);
    const labels = indices
      .filter((i) => !isNaN(i) && i >= 0 && i < options.length)
      .map((i) => options[i].label);
    return labels.length > 0 ? labels.join(", ") : response;
  }

  // Claude の質問を表示してユーザーの回答を収集する
  async function handleAskUserQuestion(input: any) {
    const answers: Record<string, string> = {};

    for (const q of input.questions) {
      console.log(`\n${q.header}: ${q.question}`);

      const options = q.options;
      options.forEach((opt: any, i: number) => {
        console.log(`  ${i + 1}. ${opt.label} - ${opt.description}`);
      });
      if (q.multiSelect) {
        console.log("  (Enter numbers separated by commas, or type your own answer)");
      } else {
        console.log("  (Enter a number, or type your own answer)");
      }

      const response = (await prompt("Your choice: ")).trim();
      answers[q.question] = parseResponse(response, options);
    }

    // Claude に回答を返す（ツール処理に元の質問を含める必須）
    return {
      behavior: "allow",
      updatedInput: { questions: input.questions, answers }
    };
  }

  async function main() {
    for await (const message of query({
      prompt: "Help me decide on the tech stack for a new mobile app",
      options: {
        canUseTool: async (toolName, input) => {
          // AskUserQuestion を質問ハンドラーにルーティングする
          if (toolName === "AskUserQuestion") {
            return handleAskUserQuestion(input);
          }
          // この例では他のツールを自動承認する
          return { behavior: "allow", updatedInput: input };
        }
      }
    })) {
      if ("result" in message) console.log(message.result);
    }
  }

  main();
  ```
</CodeGroup>

<h2 id="limitations">
  制限事項
</h2>

* **サブエージェント**：`AskUserQuestion` は現在、Agent ツール経由で生成されたサブエージェントでは利用できません
* **質問の制限**：各 `AskUserQuestion` 呼び出しは 1～4 個の質問と 2～4 個のオプションをサポートします

<h2 id="other-ways-to-get-user-input">
  ユーザー入力を取得する他の方法
</h2>

`canUseTool` コールバックと `AskUserQuestion` ツールはほとんどの承認と明確化のシナリオをカバーしていますが、SDK はユーザーから入力を取得する他の方法を提供しています。

<h3 id="streaming-input">
  ストリーミング入力
</h3>

以下が必要な場合は [ストリーミング入力](/docs/ja/agent-sdk/streaming-vs-single-mode)を使用します。

* **エージェントをタスク途中で中断する**：Claude が作業中にキャンセル信号を送信するか、方向を変更する
* **追加コンテキストを提供する**：Claude が尋ねるのを待たずに、Claude が必要とする情報を追加する
* **チャットインターフェースを構築する**：長時間実行される操作中にユーザーがエージェントと対話できるようにする

ストリーミング入力は、承認チェックポイントだけでなく、実行全体を通じてユーザーがエージェントと対話する会話型 UI に最適です。

<h3 id="custom-tools">
  カスタムツール
</h3>

以下が必要な場合は [カスタムツール](/docs/ja/agent-sdk/custom-tools)を使用します。

* **構造化入力を収集する**：`AskUserQuestion` の複数選択形式を超えたフォーム、ウィザード、または複数ステップのワークフローを構築する
* **外部承認システムを統合する**：既存のチケット、ワークフロー、または承認プラットフォームに接続する
* **ドメイン固有の対話を実装する**：コードレビューインターフェースやデプロイメントチェックリストなど、アプリケーションのニーズに合わせたツールを作成する

カスタムツールは対話を完全に制御できますが、組み込みの `canUseTool` コールバックを使用するよりも実装作業が必要です。

<h2 id="related-resources">
  関連リソース
</h2>

* [権限を設定する](/docs/ja/agent-sdk/permissions)：権限モードとルールを設定する
* [フックで実行を制御する](/docs/ja/agent-sdk/hooks)：エージェントライフサイクルの重要なポイントでカスタムコードを実行する
* [TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript#canusetool)：完全な canUseTool API ドキュメント
