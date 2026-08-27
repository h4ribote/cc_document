> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# checkpointing でファイル変更を巻き戻す

> エージェントセッション中のファイル変更を追跡し、ファイルを以前の任意の状態に復元します

ファイル checkpointing は、エージェントセッション中に Write、Edit、NotebookEdit ツールを通じて行われたファイル修正を追跡し、ファイルを以前の任意の状態に巻き戻すことができます。試してみたいですか？[インタラクティブな例](#try-it-out)にジャンプしてください。

checkpointing を使用すると、以下のことができます：

* **不要な変更を元に戻す** - ファイルを既知の良好な状態に復元することで、不要な変更を元に戻します
* **代替案を探索する** - checkpoint に復元して、別のアプローチを試します
* **エラーから回復する** - エージェントが不正な修正を行った場合に回復します

<Warning>
  Write、Edit、NotebookEdit ツールを通じて行われた変更のみが追跡されます。Bash コマンド（`echo > file.txt` や `sed -i` など）を通じて行われた変更は、checkpoint システムでキャプチャされません。
</Warning>

<h2 id="how-checkpointing-works">
  checkpointing の仕組み
</h2>

ファイル checkpointing を有効にすると、SDK は Write、Edit、または NotebookEdit ツールを通じてファイルを修正する前に、ファイルのバックアップを作成します。レスポンスストリーム内のユーザーメッセージには、復元ポイントとして使用できる checkpoint UUID が含まれます。

Checkpoint は、エージェントがファイルを修正するために使用するこれらの組み込みツールで機能します：

| ツール          | 説明                                     |
| ------------ | -------------------------------------- |
| Write        | 新しいファイルを作成するか、既存のファイルを新しいコンテンツで上書きします  |
| Edit         | 既存ファイルの特定の部分に対して、対象を絞った編集を行います         |
| NotebookEdit | Jupyter ノートブック（`.ipynb` ファイル）のセルを修正します |

<Note>
  ファイル巻き戻しは、ディスク上のファイルを以前の状態に復元します。会話自体を巻き戻すわけではありません。`rewindFiles()`（TypeScript）または `rewind_files()`（Python）を呼び出した後も、会話履歴とコンテキストはそのまま保持されます。
</Note>

checkpoint システムは以下を追跡します：

* セッション中に作成されたファイル
* セッション中に修正されたファイル
* 修正されたファイルの元のコンテンツ

checkpoint に巻き戻すと、作成されたファイルは削除され、修正されたファイルはその時点でのコンテンツに復元されます。

<h2 id="implement-checkpointing">
  checkpointing を実装する
</h2>

ファイル checkpointing を使用するには、オプションで有効にし、レスポンスストリームから checkpoint UUID をキャプチャしてから、復元が必要な場合に `rewindFiles()`（TypeScript）または `rewind_files()`（Python）を呼び出します。

次の例は、完全なフロー（checkpointing を有効にし、レスポンスストリームから checkpoint UUID とセッション ID をキャプチャしてから、後でセッションを再開してファイルを巻き戻す）を示しています。各ステップについては、以下で詳しく説明します。このセクションの例では、プロンプト「Refactor the authentication module」を使用しています。認証モジュールを含むプロジェクトで実行するか、プロンプトを変更してプロジェクトに存在するファイルを指定してください。ファイルの変更を確認し、巻き戻しがそれらを復元するのを見ることができます。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import (
      ClaudeSDKClient,
      ClaudeAgentOptions,
      UserMessage,
      ResultMessage,
  )


  async def main():
      # Step 1: checkpointing を有効にする
      options = ClaudeAgentOptions(
          enable_file_checkpointing=True,
          permission_mode="acceptEdits",  # プロンプトなしでファイル編集を自動承認
          extra_args={
              "replay-user-messages": None
          },  # レスポンスストリームで checkpoint UUID を受け取るために必須
      )

      checkpoint_id = None
      session_id = None

      # クエリを実行し、checkpoint UUID とセッション ID をキャプチャ
      async with ClaudeSDKClient(options) as client:
          await client.query("Refactor the authentication module")

          # Step 2: 最初のユーザーメッセージから checkpoint UUID をキャプチャ
          async for message in client.receive_response():
              if isinstance(message, UserMessage) and message.uuid and not checkpoint_id:
                  checkpoint_id = message.uuid
              if isinstance(message, ResultMessage) and not session_id:
                  session_id = message.session_id

      # Step 3: 後で、空のプロンプトでセッションを再開して巻き戻す
      if checkpoint_id and session_id:
          async with ClaudeSDKClient(
              ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
          ) as client:
              await client.query("")  # 接続を開くための空のプロンプト
              async for message in client.receive_response():
                  await client.rewind_files(checkpoint_id)
                  break
          print(f"Rewound to checkpoint: {checkpoint_id}")


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  async function main() {
    // Step 1: checkpointing を有効にする
    const opts = {
      enableFileCheckpointing: true,
      permissionMode: "acceptEdits" as const, // プロンプトなしでファイル編集を自動承認
      extraArgs: { "replay-user-messages": null } // レスポンスストリームで checkpoint UUID を受け取るために必須
    };

    const response = query({
      prompt: "Refactor the authentication module",
      options: opts
    });

    let checkpointId: string | undefined;
    let sessionId: string | undefined;

    // Step 2: 最初のユーザーメッセージから checkpoint UUID をキャプチャ
    for await (const message of response) {
      if (message.type === "user" && message.uuid && !checkpointId) {
        checkpointId = message.uuid;
      }
      if ("session_id" in message && !sessionId) {
        sessionId = message.session_id;
      }
    }

    // Step 3: 後で、空のプロンプトでセッションを再開して巻き戻す
    if (checkpointId && sessionId) {
      const rewindQuery = query({
        prompt: "", // 接続を開くための空のプロンプト
        options: { ...opts, resume: sessionId }
      });

      for await (const msg of rewindQuery) {
        await rewindQuery.rewindFiles(checkpointId);
        break;
      }
      console.log(`Rewound to checkpoint: ${checkpointId}`);
    }
  }

  main();
  ```
</CodeGroup>

<Steps>
  <Step title="checkpointing を有効にする">
    checkpointing を有効にして checkpoint UUID を受け取るように SDK オプションを設定します：

    | オプション                 | Python                                      | TypeScript                                    | 説明                               |
    | --------------------- | ------------------------------------------- | --------------------------------------------- | -------------------------------- |
    | checkpointing を有効にする  | `enable_file_checkpointing=True`            | `enableFileCheckpointing: true`               | 巻き戻しのためのファイル変更を追跡します             |
    | checkpoint UUID を受け取る | `extra_args={"replay-user-messages": None}` | `extraArgs: { 'replay-user-messages': null }` | ストリーム内でユーザーメッセージ UUID を取得するために必須 |

    <CodeGroup>
      ```python Python theme={null}
      options = ClaudeAgentOptions(
          enable_file_checkpointing=True,
          permission_mode="acceptEdits",
          extra_args={"replay-user-messages": None},
      )

      async with ClaudeSDKClient(options) as client:
          await client.query("Refactor the authentication module")
      ```

      ```typescript TypeScript theme={null}
      const response = query({
        prompt: "Refactor the authentication module",
        options: {
          enableFileCheckpointing: true,
          permissionMode: "acceptEdits" as const,
          extraArgs: { "replay-user-messages": null }
        }
      });
      ```
    </CodeGroup>
  </Step>

  <Step title="checkpoint UUID とセッション ID をキャプチャする">
    `replay-user-messages` オプションが設定されている場合（上記を参照）、レスポンスストリーム内の各ユーザーメッセージには、checkpoint として機能する UUID があります。

    ほとんどのユースケースでは、最初のユーザーメッセージ UUID（`message.uuid`）をキャプチャします。これに巻き戻すと、すべてのファイルが元の状態に復元されます。複数の checkpoint を保存して中間状態に巻き戻すには、[複数の復元ポイント](#multiple-restore-points)を参照してください。

    セッション ID（`message.session_id`）をキャプチャするのはオプションです。ストリームが完了した後に巻き戻したい場合にのみ必要です。[Checkpoint before risky operations](#checkpoint-before-risky-operations) の例のように、メッセージの処理中に `rewindFiles()` をすぐに呼び出す場合は、セッション ID のキャプチャをスキップできます。

    <CodeGroup>
      ```python Python theme={null}
      checkpoint_id = None
      session_id = None

      async for message in client.receive_response():
          # 最初のユーザーメッセージ UUID を checkpoint としてキャプチャ
          if isinstance(message, UserMessage) and message.uuid and checkpoint_id is None:
              checkpoint_id = message.uuid
          # 結果メッセージからセッション ID をキャプチャ
          if isinstance(message, ResultMessage):
              session_id = message.session_id
      ```

      ```typescript TypeScript theme={null}
      let checkpointId: string | undefined;
      let sessionId: string | undefined;

      for await (const message of response) {
        // 最初のユーザーメッセージ UUID を checkpoint としてキャプチャ
        if (message.type === "user" && message.uuid && !checkpointId) {
          checkpointId = message.uuid;
        }
        // セッション ID を持つメッセージからキャプチャ
        if ("session_id" in message) {
          sessionId = message.session_id;
        }
      }
      ```
    </CodeGroup>
  </Step>

  <Step title="ファイルを巻き戻す">
    ストリームが完了した後に巻き戻すには、空のプロンプトでセッションを再開し、checkpoint UUID を使用して `rewind_files()`（Python）または `rewindFiles()`（TypeScript）を呼び出します。ストリーム中に巻き戻すこともできます。そのパターンについては、[Checkpoint before risky operations](#checkpoint-before-risky-operations) を参照してください。

    <CodeGroup>
      ```python Python theme={null}
      async with ClaudeSDKClient(
          ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
      ) as client:
          await client.query("")  # 接続を開くための空のプロンプト
          async for message in client.receive_response():
              await client.rewind_files(checkpoint_id)
              break
      ```

      ```typescript TypeScript theme={null}
      const rewindQuery = query({
        prompt: "", // 接続を開くための空のプロンプト
        options: { ...opts, resume: sessionId }
      });

      for await (const msg of rewindQuery) {
        await rewindQuery.rewindFiles(checkpointId);
        break;
      }
      ```
    </CodeGroup>

    セッション ID と checkpoint ID をキャプチャした場合、CLI からも巻き戻すことができます。このコマンドには、[Claude Code をインストール](/docs/ja/setup)することで取得できる `claude` 実行ファイルが必要です。これは SDK パッケージではインストールされません。SDK は checkpointing を有効にしますが、`claude -p` を直接実行する場合は、`CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING` 環境変数を設定する必要があります：

    ```bash theme={null}
    CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING=true claude -p --resume <session-id> --rewind-files <checkpoint-uuid>
    ```

    `--rewind-files` フラグは `claude --help` 出力には表示されませんが、CLI は上記のように受け入れます。
  </Step>
</Steps>

<h2 id="common-patterns">
  一般的なパターン
</h2>

これらのパターンは、ユースケースに応じて checkpoint UUID をキャプチャして使用するさまざまな方法を示しています。

<h3 id="checkpoint-before-risky-operations">
  リスクのある操作の前に checkpoint を作成する
</h3>

このパターンは、最新の checkpoint UUID のみを保持し、各エージェントターンの前に更新します。処理中に問題が発生した場合、最後の安全な状態にすぐに巻き戻して、ループから抜け出すことができます。

このサンプルを実行する前に、`your_revert_condition`（Python）または `yourRevertCondition`（TypeScript）を独自のチェック（エラー検出や検証失敗など）に置き換えてください。プレースホルダーはサンプルでは定義されていません。

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, UserMessage


  async def main():
      options = ClaudeAgentOptions(
          enable_file_checkpointing=True,
          permission_mode="acceptEdits",
          extra_args={"replay-user-messages": None},
      )

      safe_checkpoint = None

      async with ClaudeSDKClient(options) as client:
          await client.query("Refactor the authentication module")

          async for message in client.receive_response():
              # 各エージェントターンが開始する前に checkpoint を更新
              # これは前の checkpoint を上書きします。最新のみを保持
              if isinstance(message, UserMessage) and message.uuid:
                  safe_checkpoint = message.uuid

              # 独自のロジックに基づいて復帰するかどうかを決定
              # 例：エラー検出、検証失敗、またはユーザー入力
              if your_revert_condition and safe_checkpoint:
                  await client.rewind_files(safe_checkpoint)
                  # 巻き戻し後、ループを終了します。ファイルは復元されます
                  break


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  async function main() {
    const response = query({
      prompt: "Refactor the authentication module",
      options: {
        enableFileCheckpointing: true,
        permissionMode: "acceptEdits" as const,
        extraArgs: { "replay-user-messages": null }
      }
    });

    let safeCheckpoint: string | undefined;

    for await (const message of response) {
      // 各エージェントターンが開始する前に checkpoint を更新
      // これは前の checkpoint を上書きします。最新のみを保持
      if (message.type === "user" && message.uuid) {
        safeCheckpoint = message.uuid;
      }

      // 独自のロジックに基づいて復帰するかどうかを決定
      // 例：エラー検出、検証失敗、またはユーザー入力
      if (yourRevertCondition && safeCheckpoint) {
        await response.rewindFiles(safeCheckpoint);
        // 巻き戻し後、ループを終了します。ファイルは復元されます
        break;
      }
    }
  }

  main();
  ```
</CodeGroup>

<h3 id="multiple-restore-points">
  複数の復元ポイント
</h3>

Claude が複数のターンにわたって変更を加える場合、すべての方法で巻き戻すのではなく、特定のポイントに巻き戻したい場合があります。例えば、Claude がターン 1 でファイルをリファクタリングし、ターン 2 でテストを追加した場合、リファクタリングは保持したいが、テストは元に戻したい場合があります。

このパターンは、すべての checkpoint UUID をメタデータ付きの配列に保存します。セッションが完了した後、以前の任意の checkpoint に巻き戻すことができます：

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from dataclasses import dataclass
  from datetime import datetime
  from claude_agent_sdk import (
      ClaudeSDKClient,
      ClaudeAgentOptions,
      UserMessage,
      ResultMessage,
  )


  # より良い追跡のために checkpoint メタデータを保存
  @dataclass
  class Checkpoint:
      id: str
      description: str
      timestamp: datetime


  async def main():
      options = ClaudeAgentOptions(
          enable_file_checkpointing=True,
          permission_mode="acceptEdits",
          extra_args={"replay-user-messages": None},
      )

      checkpoints = []
      session_id = None

      async with ClaudeSDKClient(options) as client:
          await client.query("Refactor the authentication module")

          async for message in client.receive_response():
              if isinstance(message, UserMessage) and message.uuid:
                  checkpoints.append(
                      Checkpoint(
                          id=message.uuid,
                          description=f"After turn {len(checkpoints) + 1}",
                          timestamp=datetime.now(),
                      )
                  )
              if isinstance(message, ResultMessage) and not session_id:
                  session_id = message.session_id

      # 後で：セッションを再開して任意の checkpoint に巻き戻す
      if checkpoints and session_id:
          target = checkpoints[0]  # 任意の checkpoint を選択
          async with ClaudeSDKClient(
              ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
          ) as client:
              await client.query("")  # 接続を開くための空のプロンプト
              async for message in client.receive_response():
                  await client.rewind_files(target.id)
                  break
          print(f"Rewound to: {target.description}")


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // より良い追跡のために checkpoint メタデータを保存
  interface Checkpoint {
    id: string;
    description: string;
    timestamp: Date;
  }

  async function main() {
    const opts = {
      enableFileCheckpointing: true,
      permissionMode: "acceptEdits" as const,
      extraArgs: { "replay-user-messages": null }
    };

    const response = query({
      prompt: "Refactor the authentication module",
      options: opts
    });

    const checkpoints: Checkpoint[] = [];
    let sessionId: string | undefined;

    for await (const message of response) {
      if (message.type === "user" && message.uuid) {
        checkpoints.push({
          id: message.uuid,
          description: `After turn ${checkpoints.length + 1}`,
          timestamp: new Date()
        });
      }
      if ("session_id" in message && !sessionId) {
        sessionId = message.session_id;
      }
    }

    // 後で：セッションを再開して任意の checkpoint に巻き戻す
    if (checkpoints.length > 0 && sessionId) {
      const target = checkpoints[0]; // 任意の checkpoint を選択
      const rewindQuery = query({
        prompt: "", // 接続を開くための空のプロンプト
        options: { ...opts, resume: sessionId }
      });

      for await (const msg of rewindQuery) {
        await rewindQuery.rewindFiles(target.id);
        break;
      }
      console.log(`Rewound to: ${target.description}`);
    }
  }

  main();
  ```
</CodeGroup>

<h2 id="try-it-out">
  試してみる
</h2>

この完全な例は、小さなユーティリティファイルを作成し、エージェントにドキュメンテーションコメントを追加させ、変更を表示してから、巻き戻したいかどうかを尋ねます。

開始する前に、[Claude Agent SDK がインストール](/docs/ja/agent-sdk/quickstart)されていることを確認してください。

<Steps>
  <Step title="テストファイルを作成する">
    `utils.py`（Python）または `utils.ts`（TypeScript）という新しいファイルを作成し、次のコードを貼り付けます：

    <CodeGroup>
      ```python utils.py theme={null}
      def add(a, b):
          return a + b


      def subtract(a, b):
          return a - b


      def multiply(a, b):
          return a * b


      def divide(a, b):
          if b == 0:
              raise ValueError("Cannot divide by zero")
          return a / b
      ```

      ```typescript utils.ts theme={null}
      export function add(a: number, b: number): number {
        return a + b;
      }

      export function subtract(a: number, b: number): number {
        return a - b;
      }

      export function multiply(a: number, b: number): number {
        return a * b;
      }

      export function divide(a: number, b: number): number {
        if (b === 0) {
          throw new Error("Cannot divide by zero");
        }
        return a / b;
      }
      ```
    </CodeGroup>
  </Step>

  <Step title="インタラクティブな例を実行する">
    ユーティリティファイルと同じディレクトリに `try_checkpointing.py`（Python）または `try_checkpointing.ts`（TypeScript）という新しいファイルを作成し、次のコードを貼り付けます。

    このスクリプトは Claude にユーティリティファイルにドキュメンテーションコメントを追加するよう要求し、その後、元の状態に巻き戻すオプションを提供します。

    <CodeGroup>
      ```python try_checkpointing.py theme={null}
      import asyncio
      from claude_agent_sdk import (
          ClaudeSDKClient,
          ClaudeAgentOptions,
          UserMessage,
          ResultMessage,
      )


      async def main():
          # checkpointing を有効にして SDK を設定
          # - enable_file_checkpointing: 巻き戻しのためのファイル変更を追跡
          # - permission_mode: プロンプトなしでファイル編集を自動承認
          # - extra_args: ストリーム内でユーザーメッセージ UUID を受け取るために必須
          options = ClaudeAgentOptions(
              enable_file_checkpointing=True,
              permission_mode="acceptEdits",
              extra_args={"replay-user-messages": None},
          )

          checkpoint_id = None  # 巻き戻しのためのユーザーメッセージ UUID を保存
          session_id = None  # 後で再開するためのセッション ID を保存

          print("Running agent to add doc comments to utils.py...\n")

          # エージェントを実行し、レスポンスストリームから checkpoint データをキャプチャ
          async with ClaudeSDKClient(options) as client:
              await client.query("Add doc comments to utils.py")

              async for message in client.receive_response():
                  # 最初のユーザーメッセージ UUID をキャプチャ - これが復元ポイント
                  if isinstance(message, UserMessage) and message.uuid and not checkpoint_id:
                      checkpoint_id = message.uuid
                  # 後で再開できるようにセッション ID をキャプチャ
                  if isinstance(message, ResultMessage):
                      session_id = message.session_id

          print("Done! Open utils.py to see the added doc comments.\n")

          # ユーザーに変更を巻き戻したいかどうかを尋ねる
          if checkpoint_id and session_id:
              response = input("Rewind to remove the doc comments? (y/n): ")

              if response.lower() == "y":
                  # セッションを再開して空のプロンプトで巻き戻す
                  async with ClaudeSDKClient(
                      ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
                  ) as client:
                      await client.query("")  # 空のプロンプトで接続を開く
                      async for message in client.receive_response():
                          await client.rewind_files(checkpoint_id)  # ファイルを復元
                          break

                  print(
                      "\n✓ File restored! Open utils.py to verify the doc comments are gone."
                  )
              else:
                  print("\nKept the modified file.")


      asyncio.run(main())
      ```

      ```typescript try_checkpointing.ts theme={null}
      import { query } from "@anthropic-ai/claude-agent-sdk";
      import * as readline from "readline";

      async function main() {
        // checkpointing を有効にして SDK を設定
        // - enableFileCheckpointing: 巻き戻しのためのファイル変更を追跡
        // - permissionMode: プロンプトなしでファイル編集を自動承認
        // - extraArgs: ストリーム内でユーザーメッセージ UUID を受け取るために必須
        const opts = {
          enableFileCheckpointing: true,
          permissionMode: "acceptEdits" as const,
          extraArgs: { "replay-user-messages": null }
        };

        let sessionId: string | undefined; // 後で再開するためのセッション ID を保存
        let checkpointId: string | undefined; // 巻き戻しのためのユーザーメッセージ UUID を保存

        console.log("Running agent to add doc comments to utils.ts...\n");

        // エージェントを実行し、レスポンスストリームから checkpoint データをキャプチャ
        const response = query({
          prompt: "Add doc comments to utils.ts",
          options: opts
        });

        for await (const message of response) {
          // 最初のユーザーメッセージ UUID をキャプチャ - これが復元ポイント
          if (message.type === "user" && message.uuid && !checkpointId) {
            checkpointId = message.uuid;
          }
          // 後で再開できるようにセッション ID をキャプチャ
          if ("session_id" in message) {
            sessionId = message.session_id;
          }
        }

        console.log("Done! Open utils.ts to see the added doc comments.\n");

        // ユーザーに変更を巻き戻したいかどうかを尋ねる
        if (checkpointId && sessionId) {
          const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
          });

          const answer = await new Promise<string>((resolve) => {
            rl.question("Rewind to remove the doc comments? (y/n): ", resolve);
          });
          rl.close();

          if (answer.toLowerCase() === "y") {
            // セッションを再開して空のプロンプトで巻き戻す
            const rewindQuery = query({
              prompt: "", // 空のプロンプトで接続を開く
              options: { ...opts, resume: sessionId }
            });

            for await (const msg of rewindQuery) {
              await rewindQuery.rewindFiles(checkpointId); // ファイルを復元
              break;
            }

            console.log("\n✓ File restored! Open utils.ts to verify the doc comments are gone.");
          } else {
            console.log("\nKept the modified file.");
          }
        }
      }

      main();
      ```
    </CodeGroup>

    この例は、完全な checkpointing ワークフローを示しています：

    1. **checkpointing を有効にする**：`enable_file_checkpointing=True` と `permission_mode="acceptEdits"` で SDK を設定して、ファイル編集を自動承認します
    2. **checkpoint データをキャプチャする**：エージェントが実行されるときに、最初のユーザーメッセージ UUID（復元ポイント）とセッション ID を保存します
    3. **巻き戻しを促す**：エージェントが完了した後、ユーティリティファイルをチェックしてドキュメンテーションコメントを確認し、変更を元に戻したいかどうかを決定します
    4. **再開して巻き戻す**：はいの場合、空のプロンプトでセッションを再開し、`rewind_files()` を呼び出して元のファイルを復元します
  </Step>

  <Step title="例を実行する">
    ユーティリティファイルと同じディレクトリからスクリプトを実行します。

    <Tip>
      スクリプトを実行する前に、ユーティリティファイル（`utils.py` または `utils.ts`）を IDE またはエディタで開きます。エージェントがドキュメンテーションコメントを追加するときにファイルがリアルタイムで更新され、巻き戻しを選択すると元の状態に戻ります。
    </Tip>

    <Tabs>
      <Tab title="Python">
        ```bash theme={null}
        python try_checkpointing.py
        ```
      </Tab>

      <Tab title="TypeScript">
        ```bash theme={null}
        npx tsx try_checkpointing.ts
        ```
      </Tab>
    </Tabs>

    エージェントがドキュメンテーションコメントを追加し、巻き戻したいかどうかを尋ねるプロンプトが表示されます。はいを選択すると、ファイルは元の状態に復元されます。
  </Step>
</Steps>

<h2 id="limitations">
  制限事項
</h2>

ファイル checkpointing には、次の制限事項があります：

| 制限事項                          | 説明                                   |
| ----------------------------- | ------------------------------------ |
| Write/Edit/NotebookEdit ツールのみ | Bash コマンドを通じて行われた変更は追跡されません          |
| 同じセッション                       | Checkpoint は、それを作成したセッションに関連付けられています |
| ファイルコンテンツのみ                   | ディレクトリの作成、移動、または削除は、巻き戻しによって元に戻されません |
| ローカルファイル                      | リモートまたはネットワークファイルは追跡されません            |

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

<h3 id="checkpointing-options-not-recognized">
  Checkpointing オプションが認識されない
</h3>

`enableFileCheckpointing` または `rewindFiles()` が利用できない場合、古い SDK バージョンを使用している可能性があります。

**解決策**：最新の SDK バージョンに更新します：

* **Python**：`pip install --upgrade claude-agent-sdk`
* **TypeScript**：`npm install @anthropic-ai/claude-agent-sdk@latest`

<h3 id="user-messages-don’t-have-uuids">
  ユーザーメッセージに UUID がない
</h3>

`message.uuid` が `undefined` または欠落している場合、checkpoint UUID を受け取っていません。

**原因**：`replay-user-messages` オプションが設定されていません。

**解決策**：オプションに `extra_args={"replay-user-messages": None}`（Python）または `extraArgs: { 'replay-user-messages': null }`（TypeScript）を追加します。

<h3 id="no-file-checkpoint-found-for-message-error">
  「No file checkpoint found for message」エラー
</h3>

このエラーは、指定されたユーザーメッセージ UUID の checkpoint データが存在しない場合に発生します。

**一般的な原因**：

* ファイル checkpointing が元のセッションで有効になっていない（`enable_file_checkpointing` または `enableFileCheckpointing` が `true` に設定されていない）
* セッションが再開して巻き戻しを試みる前に適切に完了していない

**解決策**：元のセッションで `enable_file_checkpointing=True`（Python）または `enableFileCheckpointing: true`（TypeScript）が設定されていることを確認してから、例に示されているパターンを使用します：最初のユーザーメッセージ UUID をキャプチャし、セッションを完全に完了してから、空のプロンプトで再開し、`rewindFiles()` を 1 回呼び出します。

<h3 id="file-rewinding-is-not-enabled-error">
  「File rewinding is not enabled」エラー
</h3>

このエラーは、checkpointing が有効になっていない非対話的な巻き戻しを試みた場合に発生します：`--rewind-files` を使用して bare `claude -p` を実行するか、checkpointing を有効にしないオプションを持つ SDK セッション（再開されたセッションを含む）を実行します。SDK は、`enable_file_checkpointing`（Python）または `enableFileCheckpointing`（TypeScript）が巻き戻しを実行するセッションで有効になっている場合にのみ、`CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING` 環境変数を内部的に設定します。bare CLI はこれを設定しません。

**解決策**：bare CLI の場合、コマンドを実行するときに環境変数を設定します：

```bash theme={null}
CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING=true claude -p --resume <session-id> --rewind-files <checkpoint-uuid>
```

SDK の場合、このページの例で行うように、再開されたセッションで `enable_file_checkpointing=True`（Python）または `enableFileCheckpointing: true`（TypeScript）を設定します。

<h3 id="processtransport-is-not-ready-for-writing-error">
  「ProcessTransport is not ready for writing」エラー
</h3>

このエラーは、レスポンスを反復処理した後に `rewindFiles()` または `rewind_files()` を呼び出した場合に発生します。ループが完了すると、CLI プロセスへの接続が閉じられます。

**解決策**：空のプロンプトでセッションを再開してから、新しいクエリで巻き戻します：

<CodeGroup>
  ```python Python theme={null}
  # セッションを空のプロンプトで再開してから巻き戻す
  async with ClaudeSDKClient(
      ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
  ) as client:
      await client.query("")
      async for message in client.receive_response():
          await client.rewind_files(checkpoint_id)
          break
  ```

  ```typescript TypeScript theme={null}
  // セッションを空のプロンプトで再開してから巻き戻す
  const rewindQuery = query({
    prompt: "",
    options: { ...opts, resume: sessionId }
  });

  for await (const msg of rewindQuery) {
    await rewindQuery.rewindFiles(checkpointId);
    break;
  }
  ```
</CodeGroup>

<h2 id="next-steps">
  次のステップ
</h2>

* **[Sessions](/docs/ja/agent-sdk/sessions)**：セッションを再開する方法を学びます。これはストリームが完了した後に巻き戻すために必須です。セッション ID、会話の再開、セッションフォーク化について説明します。
* **[Permissions](/docs/ja/agent-sdk/permissions)**：Claude が使用できるツールとファイル修正の承認方法を設定します。編集がいつ発生するかについてより多くの制御が必要な場合に便利です。
* **[TypeScript SDK reference](/docs/ja/agent-sdk/typescript)**：`query()` のすべてのオプションと `rewindFiles()` メソッドを含む完全な API リファレンス。
* **[Python SDK reference](/docs/ja/agent-sdk/python)**：`ClaudeAgentOptions` のすべてのオプションと `rewind_files()` メソッドを含む完全な API リファレンス。
