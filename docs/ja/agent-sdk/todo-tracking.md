> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Todo リスト

> Claude Agent SDK を使用して todo を追跡・表示し、タスク管理を整理します

Todo 追跡は、タスクを管理し、ユーザーに進捗を表示するための構造化された方法を提供します。Claude Agent SDK には、複雑なワークフローを整理し、ユーザーにタスク進捗を知らせるのに役立つ組み込み todo 機能が含まれています。

<Note>
  TypeScript Agent SDK 0.3.142 および Claude Code v2.1.142 以降、セッションは `TodoWrite` の代わりに構造化された Task ツール `TaskCreate`、`TaskUpdate`、`TaskGet`、および `TaskList` を使用します。Python SDK は Python パッケージバージョンではなく、起動する Claude Code CLI からこの変更を取得します。スイッチは、その CLI（pip パッケージ内にバンドルされているコピー、または `cli_path` で指定するコピー）が v2.1.142 以降の場合に適用されます。監視コードの変更方法については、[Task ツールへの移行](#migrate-to-task-tools)を参照してください。このページの例では、まだ移行していないセッションの `TodoWrite` を引き続き表示するために `CLAUDE_CODE_ENABLE_TASKS=0` を設定しています。
</Note>

<h3 id="todo-lifecycle">
  Todo ライフサイクル
</h3>

Todo は予測可能なライフサイクルに従います：

1. **作成** - タスクが識別されたときに `pending` として作成される
2. **アクティベート** - 作業が開始されたときに `in_progress` に変更される
3. **完了** - タスクが正常に完了したときに完了する
4. **削除** - グループ内のすべてのタスクが完了したときに削除される

<h3 id="when-todos-are-used">
  Todo が使用される場合
</h3>

SDK は以下の場合に自動的に todo を作成します：

* **複雑なマルチステップタスク** - 3 つ以上の異なるアクションが必要な場合
* **ユーザー提供のタスクリスト** - 複数のアイテムが言及されている場合
* **非自明な操作** - 進捗追跡の恩恵を受ける場合
* **明示的なリクエスト** - ユーザーが todo 整理を要求した場合

<h2 id="examples">
  例
</h2>

これらの例を実行する前に、[クイックスタート](/docs/ja/agent-sdk/quickstart)に従って Claude Agent SDK をインストールしてください。

各例はエージェントが完了して最終結果メッセージを生成するまで実行されます。セッションがターン制限に最初に達した場合、その結果メッセージは `error_max_turns` サブタイプを持ちます。終了を検出するために `subtype` を確認してください。

これらの例は単一ショットの `query()` 呼び出しを使用します。`error_max_turns` 結果を生成した後、`query()` は `Reached maximum number of turns` を含むエラーを発生させます。各例はそれが発生したときにクリーンに終了するために、ループを try ブロックでラップします。

結果サブタイプについては、[結果を処理する](/docs/ja/agent-sdk/agent-loop#handle-the-result)を参照してください。

<h3 id="monitoring-todo-changes">
  Todo 変更の監視
</h3>

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  try {
    for await (const message of query({
      prompt: "Optimize my React app performance and track progress with todos",
      // Re-enable TodoWrite, which this example monitors. Without it, the SDK uses
      // Task tools instead and these tool_use blocks never appear.
      options: { maxTurns: 15, env: { ...process.env, CLAUDE_CODE_ENABLE_TASKS: "0" } }
    })) {
      // Todo updates are reflected in the message stream
      if (message.type === "assistant") {
        for (const block of message.message.content) {
          if (block.type === "tool_use" && block.name === "TodoWrite") {
            const todos = block.input.todos;

            console.log("Todo Status Update:");
            todos.forEach((todo, index) => {
              const status =
                todo.status === "completed" ? "✅" : todo.status === "in_progress" ? "🔧" : "❌";
              console.log(`${index + 1}. ${status} ${todo.content}`);
            });
          }
        }
      }
    }
  } catch (error) {
    // A single-shot query() throws after yielding an error result,
    // such as when the maxTurns limit is hit.
    console.log(`Session ended with an error: ${error}`);
  }
  ```

  ```python Python theme={null}
  import asyncio

  from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock


  async def main():
      try:
          async for message in query(
              prompt="Optimize my React app performance and track progress with todos",
              # Re-enable TodoWrite, which this example monitors. Without it, the SDK uses
              # Task tools instead and these tool_use blocks never appear.
              options=ClaudeAgentOptions(max_turns=15, env={"CLAUDE_CODE_ENABLE_TASKS": "0"}),
          ):
              # Todo updates are reflected in the message stream
              if isinstance(message, AssistantMessage):
                  for block in message.content:
                      if isinstance(block, ToolUseBlock) and block.name == "TodoWrite":
                          todos = block.input["todos"]

                          print("Todo Status Update:")
                          for i, todo in enumerate(todos):
                              status = (
   "✅"
   if todo["status"] == "completed"
   else "🔧"
   if todo["status"] == "in_progress"
   else "❌"
                              )
                              print(f"{i + 1}. {status} {todo['content']}")
      except Exception as error:
          # A single-shot query() raises after yielding an error result,
          # such as when the max_turns limit is hit.
          print(f"Session ended with an error: {error}")


  asyncio.run(main())
  ```
</CodeGroup>

<h3 id="real-time-progress-display">
  リアルタイム進捗表示
</h3>

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  class TodoTracker {
    private todos: any[] = [];

    displayProgress() {
      if (this.todos.length === 0) return;

      const completed = this.todos.filter((t) => t.status === "completed").length;
      const inProgress = this.todos.filter((t) => t.status === "in_progress").length;
      const total = this.todos.length;

      console.log(`\nProgress: ${completed}/${total} completed`);
      console.log(`Currently working on: ${inProgress} task(s)\n`);

      this.todos.forEach((todo, index) => {
        const icon =
          todo.status === "completed" ? "✅" : todo.status === "in_progress" ? "🔧" : "❌";
        const text = todo.status === "in_progress" ? todo.activeForm : todo.content;
        console.log(`${index + 1}. ${icon} ${text}`);
      });
    }

    async trackQuery(prompt: string) {
      try {
        for await (const message of query({
          prompt,
          // Re-enable TodoWrite, which this tracker watches for.
          options: { maxTurns: 20, env: { ...process.env, CLAUDE_CODE_ENABLE_TASKS: "0" } }
        })) {
          if (message.type === "assistant") {
            for (const block of message.message.content) {
              if (block.type === "tool_use" && block.name === "TodoWrite") {
                this.todos = block.input.todos;
                this.displayProgress();
              }
            }
          }
        }
      } catch (error) {
        // A single-shot query() throws after yielding an error result,
        // such as when the maxTurns limit is hit.
        console.log(`Session ended with an error: ${error}`);
      }
    }
  }

  // Usage
  const tracker = new TodoTracker();
  await tracker.trackQuery("Build a complete authentication system with todos");
  ```

  ```python Python theme={null}
  import asyncio

  from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock
  from typing import List, Dict


  class TodoTracker:
      def __init__(self):
          self.todos: List[Dict] = []

      def display_progress(self):
          if not self.todos:
              return

          completed = len([t for t in self.todos if t["status"] == "completed"])
          in_progress = len([t for t in self.todos if t["status"] == "in_progress"])
          total = len(self.todos)

          print(f"\nProgress: {completed}/{total} completed")
          print(f"Currently working on: {in_progress} task(s)\n")

          for i, todo in enumerate(self.todos):
              icon = (
                  "✅"
                  if todo["status"] == "completed"
                  else "🔧"
                  if todo["status"] == "in_progress"
                  else "❌"
              )
              text = (
                  todo["activeForm"]
                  if todo["status"] == "in_progress"
                  else todo["content"]
              )
              print(f"{i + 1}. {icon} {text}")

      async def track_query(self, prompt: str):
          try:
              async for message in query(
                  prompt=prompt,
                  # Re-enable TodoWrite, which this tracker watches for.
                  options=ClaudeAgentOptions(max_turns=20, env={"CLAUDE_CODE_ENABLE_TASKS": "0"}),
              ):
                  if isinstance(message, AssistantMessage):
                      for block in message.content:
                          if isinstance(block, ToolUseBlock) and block.name == "TodoWrite":
                              self.todos = block.input["todos"]
                              self.display_progress()
          except Exception as error:
              # A single-shot query() raises after yielding an error result,
              # such as when the max_turns limit is hit.
              print(f"Session ended with an error: {error}")


  # Usage
  async def main():
      tracker = TodoTracker()
      await tracker.track_query("Build a complete authentication system with todos")


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="migrate-to-task-tools">
  Task ツールへの移行
</h2>

Task ツールは、単一の `TodoWrite` 呼び出しを、各新規アイテムの `TaskCreate` と各ステータス変更の `TaskUpdate` に分割し、`TaskList` と `TaskGet` はモデルが現在のリストを読み戻すために利用可能です。監視コードは引き続きアシスタントストリーム内の `tool_use` ブロックを検査しますが、すべての呼び出しでリスト全体を置き換える代わりに、タスク ID でキー付けされたマップを保持します。Task ツールは TypeScript Agent SDK 0.3.142 および Claude Code v2.1.142 以降のデフォルトであるため、`options.env` の変更は不要です。

| `TodoWrite` を使用                          | Task ツールを使用                                                                                                                                                                                                                                                                         |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 つのツール呼び出しで完全な `todos` 配列を書き直す          | `TaskCreate` は 1 つのアイテムを追加し、`TaskUpdate` は `taskId` で 1 つのアイテムをパッチする                                                                                                                                                                                                                |
| `block.name === "TodoWrite"` に一致         | `block.name === "TaskCreate"` または `"TaskUpdate"` に一致                                                                                                                                                                                                                                |
| アイテム形状：`{ content, status, activeForm }` | `TaskCreate` 入力：`{ subject, description, activeForm?, metadata? }`。`TaskUpdate` 入力：`{ taskId, status?, subject?, description?, activeForm?, addBlocks?, addBlockedBy?, owner?, metadata? }`。`status` は `"pending"`、`"in_progress"`、または `"completed"`；削除するには `status: "deleted"` を設定 |
| `block.input.todos` を直接レンダリング            | 呼び出し全体でアイテムを蓄積するか、ストリームから `TaskList` ツール結果のスナップショットを読み取る                                                                                                                                                                                                                            |

割り当てられたタスク ID は `TaskCreate` 入力にはありません。マッチング `tool_result` で `{ task: { id, subject } }` として返されるため、マップをキー付けするために結果ブロックからそれをキャプチャします。次の例は、[Todo 変更の監視](#monitoring-todo-changes)ループへの最小限の変更を示しています。ストリーム内の `TaskList` ツール結果を監視するか、`TaskCreate` 結果と `TaskUpdate` 入力をマップに蓄積することで、完全なリストをレンダリングできます。

ストリーミングされた `tool_use` 入力は、モデルが発行した生の形状です。Claude Code は実行前にいくつかの近いが正確でないキー名を修復し、`id` または `task_id` を `taskId` にマッピングし、`active_form` を `activeForm` にマッピングしますが、その修復はストリームに反映されません。以下のサンプルのように、常に正規名が存在すると仮定するのではなく、`TaskUpdate` 入力フィールドを防御的に読み取ります。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  try {
    for await (const message of query({
      prompt: "Optimize my React app performance and track progress with todos",
      options: { maxTurns: 15 },
    })) {
      if (message.type !== "assistant") continue;
      for (const block of message.message.content) {
        if (block.type !== "tool_use") continue;
        if (block.name === "TaskCreate") {
          const input = block.input as { subject: string };
          console.log(`+ ${input.subject}`);
        } else if (block.name === "TaskUpdate") {
          const input = block.input as {
            taskId?: string;
            id?: string;
            task_id?: string;
            status?: string;
          };
          const taskId = input.taskId ?? input.id ?? input.task_id;
          if (taskId && input.status) console.log(`  ${taskId} -> ${input.status}`);
        }
      }
    }
  } catch (error) {
    // A single-shot query() throws after yielding an error result.
    console.log(`Session ended with an error: ${error}`);
  }
  ```

  ```python Python theme={null}
  import asyncio

  from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock

  async def main():
      try:
          async for message in query(
              prompt="Optimize my React app performance and track progress with todos",
              options=ClaudeAgentOptions(max_turns=15),
          ):
              if not isinstance(message, AssistantMessage):
                  continue
              for block in message.content:
                  if not isinstance(block, ToolUseBlock):
                      continue
                  if block.name == "TaskCreate":
                      print(f"+ {block.input['subject']}")
                  elif block.name == "TaskUpdate" and block.input.get("status"):
                      task_id = (
                          block.input.get("taskId")
                          or block.input.get("id")
                          or block.input.get("task_id")
                      )
                      if task_id:
                          print(f"  {task_id} -> {block.input['status']}")
      except Exception as error:
          # A single-shot query() raises after yielding an error result.
          print(f"Session ended with an error: {error}")


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="related-documentation">
  関連ドキュメント
</h2>

* [TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript)
* [Python SDK リファレンス](/docs/ja/agent-sdk/python)
* [ストリーミング vs シングルモード](/docs/ja/agent-sdk/streaming-vs-single-mode)
* [カスタムツール](/docs/ja/agent-sdk/custom-tools)
