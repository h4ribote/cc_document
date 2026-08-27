> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# TypeScript SDK V2 セッション API（削除済み）

> マルチターン会話向けのセッションベースの send/stream パターンを備えた、削除済みの V2 TypeScript Agent SDK セッション API のリファレンス。

<Warning>
  V2 セッション API はサポートされなくなりました。TypeScript Agent SDK 0.3.142 では `unstable_v2_createSession`、`unstable_v2_resumeSession`、`unstable_v2_prompt`、および `SDKSession` と `SDKSessionOptions` 型が削除されます。

  移行するには、[`query()` API](/docs/ja/agent-sdk/typescript) と、それが受け入れる [セッションオプション](/docs/ja/agent-sdk/sessions) を使用してください。マルチターン会話の場合は `AsyncIterable<SDKUserMessage>` を渡すか、保存されたセッションを続行するには `options.resume` を使用してください。このページは、Agent SDK 0.2.x 以前のコードを保守している場合の参照用に保持されています。
</Warning>

V2 は、非同期ジェネレータと yield 調整の必要性を排除した実験的なセッション API でした。ターン間でジェネレータの状態を管理する代わりに、各ターンは個別の `send()`/`stream()` サイクルになります。API サーフェスは 3 つの概念に縮小されました。

* `createSession()` / `resumeSession()`：会話を開始または継続する
* `session.send()`：メッセージを送信する
* `session.stream()`：レスポンスを取得する

<h2 id="installation">
  インストール
</h2>

Agent SDK 0.2.x は V2 インターフェースを含む最後のバージョンです。パッケージバージョンは 0.2.x から直接 0.3.142 にジャンプしたため、上記の削除バージョンと下記のインストールピンは同じ境界を説明しています。最後の V2 互換リリースをインストールするには、メジャーバージョンとマイナーバージョンをピンしてください。

```bash theme={null}
npm install @anthropic-ai/claude-agent-sdk@0.2
```

<Note>
  SDK はオプションの依存関係として、プラットフォーム用のネイティブ Claude Code バイナリをバンドルしているため、Claude Code を別途インストールする必要はありません。
</Note>

<h2 id="quick-start">
  クイックスタート
</h2>

<h3 id="one-shot-prompt">
  ワンショットプロンプト
</h3>

セッションを維持する必要がない単純なシングルターンクエリの場合は、`unstable_v2_prompt()` を使用します。この例は数学の質問を送信し、答えをログに出力します。

```typescript theme={null}
import { unstable_v2_prompt } from "@anthropic-ai/claude-agent-sdk";

const result = await unstable_v2_prompt("What is 2 + 2?", {
  model: "claude-opus-4-7"
});
if (result.subtype === "success") {
  console.log(result.result);
}
```

<details>
  <summary>V1 での同じ操作を参照</summary>

  ```typescript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const q = query({
    prompt: "What is 2 + 2?",
    options: { model: "claude-opus-4-7" }
  });

  for await (const msg of q) {
    if (msg.type === "result" && msg.subtype === "success") {
      console.log(msg.result);
    }
  }
  ```
</details>

<h3 id="basic-session">
  基本的なセッション
</h3>

単一のプロンプトを超えるインタラクションの場合は、セッションを作成します。V2 は送信とストリーミングを個別のステップに分離します。

* `send()` はメッセージをディスパッチします
* `stream()` はレスポンスをストリーミングします

この明示的な分離により、ターン間にロジックを追加しやすくなります（レスポンスを処理してからフォローアップを送信するなど）。

以下の例はセッションを作成し、「Hello!」を Claude に送信し、テキストレスポンスを出力します。[`await using`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-2.html#using-declarations-and-explicit-resource-management)（TypeScript 5.2 以降）を使用して、ブロックが終了するときにセッションを自動的に閉じます。`session.close()` を手動で呼び出すこともできます。

```typescript theme={null}
import { unstable_v2_createSession } from "@anthropic-ai/claude-agent-sdk";

await using session = unstable_v2_createSession({
  model: "claude-opus-4-7"
});

await session.send("Hello!");
for await (const msg of session.stream()) {
  // Filter for assistant messages to get human-readable output
  if (msg.type === "assistant") {
    const text = msg.message.content
      .filter((block) => block.type === "text")
      .map((block) => block.text)
      .join("");
    console.log(text);
  }
}
```

<details>
  <summary>V1 での同じ操作を参照</summary>

  V1 では、入力と出力の両方が単一の非同期ジェネレータを通じてフローします。基本的なプロンプトの場合は同様に見えますが、マルチターンロジックを追加するには、入力ジェネレータを使用するように再構築する必要があります。

  ```typescript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const q = query({
    prompt: "Hello!",
    options: { model: "claude-opus-4-7" }
  });

  for await (const msg of q) {
    if (msg.type === "assistant") {
      const text = msg.message.content
        .filter((block) => block.type === "text")
        .map((block) => block.text)
        .join("");
      console.log(text);
    }
  }
  ```
</details>

<h3 id="multi-turn-conversation">
  マルチターン会話
</h3>

セッションは複数の交換全体でコンテキストを保持します。会話を続けるには、同じセッションで `send()` を再度呼び出します。Claude は前のターンを記憶しています。

この例は数学の質問を尋ねてから、前の答えを参照するフォローアップを尋ねます。

```typescript theme={null}
import { unstable_v2_createSession } from "@anthropic-ai/claude-agent-sdk";

await using session = unstable_v2_createSession({
  model: "claude-opus-4-7"
});

// Turn 1
await session.send("What is 5 + 3?");
for await (const msg of session.stream()) {
  // Filter for assistant messages to get human-readable output
  if (msg.type === "assistant") {
    const text = msg.message.content
      .filter((block) => block.type === "text")
      .map((block) => block.text)
      .join("");
    console.log(text);
  }
}

// Turn 2
await session.send("Multiply that by 2");
for await (const msg of session.stream()) {
  if (msg.type === "assistant") {
    const text = msg.message.content
      .filter((block) => block.type === "text")
      .map((block) => block.text)
      .join("");
    console.log(text);
  }
}
```

<details>
  <summary>V1 での同じ操作を参照</summary>

  ```typescript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // Must create an async iterable to feed messages
  async function* createInputStream() {
    yield {
      type: "user",
      session_id: "",
      message: { role: "user", content: [{ type: "text", text: "What is 5 + 3?" }] },
      parent_tool_use_id: null
    };
    // Must coordinate when to yield next message
    yield {
      type: "user",
      session_id: "",
      message: { role: "user", content: [{ type: "text", text: "Multiply by 2" }] },
      parent_tool_use_id: null
    };
  }

  const q = query({
    prompt: createInputStream(),
    options: { model: "claude-opus-4-7" }
  });

  for await (const msg of q) {
    if (msg.type === "assistant") {
      const text = msg.message.content
        .filter((block) => block.type === "text")
        .map((block) => block.text)
        .join("");
      console.log(text);
    }
  }
  ```
</details>

<h3 id="session-resume">
  セッションの再開
</h3>

前のインタラクションからセッション ID がある場合は、後でそれを再開できます。これは長時間実行されるワークフローや、アプリケーションの再起動全体で会話を永続化する必要がある場合に便利です。

この例はセッションを作成し、その ID を保存し、それを閉じてから会話を再開します。

```typescript theme={null}
import {
  unstable_v2_createSession,
  unstable_v2_resumeSession,
  type SDKMessage
} from "@anthropic-ai/claude-agent-sdk";

// Helper to extract text from assistant messages
function getAssistantText(msg: SDKMessage): string | null {
  if (msg.type !== "assistant") return null;
  return msg.message.content
    .filter((block) => block.type === "text")
    .map((block) => block.text)
    .join("");
}

// Create initial session and have a conversation
const session = unstable_v2_createSession({
  model: "claude-opus-4-7"
});

await session.send("Remember this number: 42");

// Get the session ID from any received message
let sessionId: string | undefined;
for await (const msg of session.stream()) {
  sessionId = msg.session_id;
  const text = getAssistantText(msg);
  if (text) console.log("Initial response:", text);
}

console.log("Session ID:", sessionId);
session.close();

// Later: resume the session using the stored ID
await using resumedSession = unstable_v2_resumeSession(sessionId!, {
  model: "claude-opus-4-7"
});

await resumedSession.send("What number did I ask you to remember?");
for await (const msg of resumedSession.stream()) {
  const text = getAssistantText(msg);
  if (text) console.log("Resumed response:", text);
}
```

<details>
  <summary>V1 での同じ操作を参照</summary>

  ```typescript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // Create initial session
  const initialQuery = query({
    prompt: "Remember this number: 42",
    options: { model: "claude-opus-4-7" }
  });

  // Get session ID from any message
  let sessionId: string | undefined;
  for await (const msg of initialQuery) {
    sessionId = msg.session_id;
    if (msg.type === "assistant") {
      const text = msg.message.content
        .filter((block) => block.type === "text")
        .map((block) => block.text)
        .join("");
      console.log("Initial response:", text);
    }
  }

  console.log("Session ID:", sessionId);

  // Later: resume the session
  const resumedQuery = query({
    prompt: "What number did I ask you to remember?",
    options: {
      model: "claude-opus-4-7",
      resume: sessionId
    }
  });

  for await (const msg of resumedQuery) {
    if (msg.type === "assistant") {
      const text = msg.message.content
        .filter((block) => block.type === "text")
        .map((block) => block.text)
        .join("");
      console.log("Resumed response:", text);
    }
  }
  ```
</details>

<h3 id="cleanup">
  クリーンアップ
</h3>

セッションは手動で閉じるか、[`await using`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-2.html#using-declarations-and-explicit-resource-management)（自動リソースクリーンアップ用の TypeScript 5.2 以降の機能）を使用して自動的に閉じることができます。古い TypeScript バージョンを使用している場合や互換性の問題が発生した場合は、代わりに手動クリーンアップを使用してください。

**自動クリーンアップ（TypeScript 5.2 以降）：**

```typescript theme={null}
import { unstable_v2_createSession } from "@anthropic-ai/claude-agent-sdk";

await using session = unstable_v2_createSession({
  model: "claude-opus-4-7"
});
// Session closes automatically when the block exits
```

**手動クリーンアップ：**

```typescript theme={null}
import { unstable_v2_createSession } from "@anthropic-ai/claude-agent-sdk";

const session = unstable_v2_createSession({
  model: "claude-opus-4-7"
});
// ... use the session ...
session.close();
```

<h2 id="api-reference">
  API リファレンス
</h2>

<h3 id="unstable_v2_createsession">
  `unstable_v2_createSession()`
</h3>

マルチターン会話用の新しいセッションを作成します。

```typescript theme={null}
function unstable_v2_createSession(options: {
  model: string;
  // Additional options supported
}): SDKSession;
```

<h3 id="unstable_v2_resumesession">
  `unstable_v2_resumeSession()`
</h3>

ID で既存のセッションを再開します。

```typescript theme={null}
function unstable_v2_resumeSession(
  sessionId: string,
  options: {
    model: string;
    // Additional options supported
  }
): SDKSession;
```

<h3 id="unstable_v2_prompt">
  `unstable_v2_prompt()`
</h3>

シングルターンクエリ用のワンショット便利関数。

```typescript theme={null}
function unstable_v2_prompt(
  prompt: string,
  options: {
    model: string;
    // Additional options supported
  }
): Promise<SDKResultMessage>;
```

<h3 id="sdksession-interface">
  SDKSession インターフェース
</h3>

```typescript theme={null}
interface SDKSession {
  readonly sessionId: string;
  send(message: string | SDKUserMessage): Promise<void>;
  stream(): AsyncGenerator<SDKMessage, void>;
  close(): void;
}
```

<h2 id="feature-availability">
  機能の可用性
</h2>

V2 セッション API は、すべての V1 機能をサポートしていません。以下は [V1 SDK](/docs/ja/agent-sdk/typescript) を使用する必要があります。

* セッションフォーキング（`forkSession` オプション）
* 一部の高度なストリーミング入力パターン

<h2 id="see-also">
  関連項目
</h2>

* [TypeScript SDK リファレンス（V1）](/docs/ja/agent-sdk/typescript) - 完全な V1 SDK ドキュメント
* [SDK 概要](/docs/ja/agent-sdk/overview) - 一般的な SDK の概念
* [GitHub 上の V2 例](https://github.com/anthropics/claude-agent-sdk-demos/tree/main/hello-world-v2) - 動作するコード例
