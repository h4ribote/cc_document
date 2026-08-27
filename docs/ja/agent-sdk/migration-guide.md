> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude Agent SDK への移行

> Claude Code TypeScript および Python SDK を Claude Agent SDK に移行するためのガイド

<h2 id="overview">
  概要
</h2>

Claude Code SDK は **Claude Agent SDK** に名前が変更され、ドキュメントが再編成されました。この変更は、コーディングタスクだけでなく、AI エージェント構築のための SDK のより広い機能を反映しています。

<h2 id="what’s-changed">
  変更内容
</h2>

| 項目                | 旧版                          | 新版                               |
| :---------------- | :-------------------------- | :------------------------------- |
| **パッケージ名（TS/JS）** | `@anthropic-ai/claude-code` | `@anthropic-ai/claude-agent-sdk` |
| **Python パッケージ**  | `claude-code-sdk`           | `claude-agent-sdk`               |
| **ドキュメント場所**      | Claude Code ドキュメント          | API ガイド → Agent SDK セクション        |

<Note>
  **ドキュメント変更：** Agent SDK ドキュメントは Claude Code ドキュメントから API ガイドの専用 [Agent SDK](/docs/ja/agent-sdk/overview) セクションに移動しました。Claude Code ドキュメントは現在、CLI ツールと自動化機能に焦点を当てています。
</Note>

<h2 id="migration-steps">
  移行手順
</h2>

<h3 id="for-typescript/javascript-projects">
  TypeScript/JavaScript プロジェクト向け
</h3>

**1. 古いパッケージをアンインストールします：**

```bash theme={null}
npm uninstall @anthropic-ai/claude-code
```

**2. 新しいパッケージをインストールします：**

```bash theme={null}
npm install @anthropic-ai/claude-agent-sdk
```

**3. インポートを更新します：**

`@anthropic-ai/claude-code` からのすべてのインポートを `@anthropic-ai/claude-agent-sdk` に変更します：

```typescript theme={null}
// 変更前
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-code";

// 変更後
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
```

**4. package.json の依存関係を更新します：**

`package.json` にパッケージがリストされている場合は、更新します：

変更前：

```json theme={null}
{
  "dependencies": {
    "@anthropic-ai/claude-code": "^0.0.42"
  }
}
```

変更後：

```json theme={null}
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.2.0"
  }
}
```

**5. [破壊的変更](#breaking-changes) を確認します**

移行を完了するために必要なコード変更を行います。

<h3 id="for-python-projects">
  Python プロジェクト向け
</h3>

**1. 古いパッケージをアンインストールします：**

```bash theme={null}
pip uninstall claude-code-sdk
```

**2. 新しいパッケージをインストールします：**

```bash theme={null}
pip install claude-agent-sdk
```

**3. インポートを更新します：**

`claude_code_sdk` からのすべてのインポートを `claude_agent_sdk` に変更します：

```python theme={null}
# 変更前
from claude_code_sdk import query, ClaudeCodeOptions

# 変更後
from claude_agent_sdk import query, ClaudeAgentOptions
```

**4. 型名を更新します：**

`ClaudeCodeOptions` を `ClaudeAgentOptions` に変更します：

```python theme={null}
# 変更前
from claude_code_sdk import query, ClaudeCodeOptions

options = ClaudeCodeOptions(model="claude-opus-4-7")

# 変更後
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(model="claude-opus-4-7")
```

**5. [破壊的変更](#breaking-changes) を確認します**

移行を完了するために必要なコード変更を行います。

<h2 id="breaking-changes">
  破壊的変更
</h2>

<Warning>
  分離と明示的な設定を改善するため、Claude Agent SDK v0.1.0 は Claude Code SDK から移行するユーザーに対して破壊的変更を導入しています。移行前にこのセクションを注意深く確認してください。
</Warning>

<h3 id="python-claudecodeoptions-renamed-to-claudeagentoptions">
  Python：ClaudeCodeOptions が ClaudeAgentOptions に名前変更
</h3>

**変更内容：** Python SDK の型 `ClaudeCodeOptions` が `ClaudeAgentOptions` に名前変更されました。

**移行：**

```python theme={null}
# 変更前（claude-code-sdk）
from claude_code_sdk import query, ClaudeCodeOptions

options = ClaudeCodeOptions(model="claude-opus-4-7", permission_mode="acceptEdits")

# 変更後（claude-agent-sdk）
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(model="claude-opus-4-7", permission_mode="acceptEdits")
```

**変更理由：** 型名は「Claude Agent SDK」ブランディングと一致し、SDK の命名規則全体で一貫性を提供します。

<h3 id="system-prompt-no-longer-default">
  システムプロンプトがデフォルトではなくなりました
</h3>

**変更内容：** SDK はデフォルトで Claude Code のシステムプロンプトを使用しなくなりました。

**移行：**

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // 変更前（v0.0.x）- デフォルトで Claude Code のシステムプロンプトを使用
  const before = query({ prompt: "Hello" });

  // 変更後（v0.1.0）- デフォルトで最小限のシステムプロンプトを使用
  // 古い動作を取得するには、Claude Code のプリセットを明示的にリクエストします：
  const presetResult = query({
    prompt: "Hello",
    options: {
      systemPrompt: { type: "preset", preset: "claude_code" }
    }
  });

  // またはカスタムシステムプロンプトを使用します：
  const customResult = query({
    prompt: "Hello",
    options: {
      systemPrompt: "You are a helpful coding assistant"
    }
  });
  ```

  ```python Python theme={null}
  # 変更前（v0.0.x）- デフォルトで Claude Code のシステムプロンプトを使用
  async for message in query(prompt="Hello"):
      print(message)

  # 変更後（v0.1.0）- デフォルトで最小限のシステムプロンプトを使用
  # 古い動作を取得するには、Claude Code のプリセットを明示的にリクエストします：
  from claude_agent_sdk import query, ClaudeAgentOptions

  async for message in query(
      prompt="Hello",
      options=ClaudeAgentOptions(
          system_prompt={"type": "preset", "preset": "claude_code"}  # プリセットを使用
      ),
  ):
      print(message)

  # またはカスタムシステムプロンプトを使用します：
  async for message in query(
      prompt="Hello",
      options=ClaudeAgentOptions(system_prompt="You are a helpful coding assistant"),
  ):
      print(message)
  ```
</CodeGroup>

**変更理由：** SDK アプリケーションのより良い制御と分離を提供します。Claude Code の CLI 中心の指示を継承することなく、カスタム動作を持つエージェントを構築できるようになりました。

<h3 id="settings-sources-default">
  設定ソースのデフォルト
</h3>

このデフォルトは v0.1.0 で一度変更されてから元に戻されたため、移行アクションは必要ありません。

**現在の動作：** `query()` で `settingSources` を省略すると、ユーザー、プロジェクト、ローカルファイルシステムの設定が読み込まれ、CLI と一致します。これには `~/.claude/settings.json`、`.claude/settings.json`、`.claude/settings.local.json`、CLAUDE.md ファイル、およびカスタムコマンドが含まれます。

ファイルシステム設定から分離して実行するには、空の配列を渡します：

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  const isolatedResult = query({
    prompt: "Hello",
    options: {
      settingSources: [] // ファイルシステム設定は読み込まれません
    }
  });

  // または特定のソースのみを読み込みます：
  const projectOnlyResult = query({
    prompt: "Hello",
    options: {
      settingSources: ["project"] // プロジェクト設定のみ
    }
  });
  ```

  ```python Python theme={null}
  from claude_agent_sdk import query, ClaudeAgentOptions

  async for message in query(
      prompt="Hello",
      options=ClaudeAgentOptions(setting_sources=[]),  # ファイルシステム設定は読み込まれません
  ):
      print(message)

  # または特定のソースのみを読み込みます：
  async for message in query(
      prompt="Hello",
      options=ClaudeAgentOptions(
          setting_sources=["project"]  # プロジェクト設定のみ
      ),
  ):
      print(message)
  ```
</CodeGroup>

分離は、ローカルのカスタマイズがリークしてはいけない CI/CD パイプライン、デプロイされたアプリケーション、テスト環境、マルチテナントシステムで特に重要です。

<Note>
  SDK v0.1.0 は一度設定が読み込まれないようにデフォルト設定されましたが、その後のリリースで元に戻されました。Python SDK 0.1.59 以前は空のリストをオプションを省略するのと同じように扱ったため、`setting_sources=[]` に依存する前にアップグレードしてください。`settingSources` が `[]` の場合でも読み込まれる入力については、[What settingSources does not control](/docs/ja/agent-sdk/claude-code-features#what-settingsources-does-not-control) を参照してください。
</Note>

<h2 id="why-the-rename">
  名前変更の理由
</h2>

Claude Code SDK はもともとコーディングタスク用に設計されていましたが、あらゆるタイプの AI エージェント構築のための強力なフレームワークに進化しました。新しい名前「Claude Agent SDK」はその機能をより良く反映しています：

* ビジネスエージェントの構築（法務アシスタント、ファイナンスアドバイザー、カスタマーサポート）
* 特化したコーディングエージェントの作成（SRE ボット、セキュリティレビュアー、コードレビューエージェント）
* ツール使用、MCP 統合など、あらゆるドメイン向けのカスタムエージェント開発

<h2 id="getting-help">
  ヘルプを得る
</h2>

移行中に問題が発生した場合：

**TypeScript/JavaScript の場合：**

1. すべてのインポートが `@anthropic-ai/claude-agent-sdk` を使用するように更新されていることを確認します
2. package.json に新しいパッケージ名があることを確認します
3. `npm install` を実行して、依存関係が更新されていることを確認します

**Python の場合：**

1. すべてのインポートが `claude_agent_sdk` を使用するように更新されていることを確認します
2. requirements.txt または pyproject.toml に新しいパッケージ名があることを確認します
3. `pip install claude-agent-sdk` を実行して、パッケージがインストールされていることを確認します

<h2 id="next-steps">
  次のステップ
</h2>

* [Agent SDK Overview](/docs/ja/agent-sdk/overview) を探索して、利用可能な機能について学びます
* [TypeScript SDK Reference](/docs/ja/agent-sdk/typescript) をチェックして、詳細な API ドキュメントを確認します
* [Python SDK Reference](/docs/ja/agent-sdk/python) を確認して、Python 固有のドキュメントを確認します
* [Custom Tools](/docs/ja/agent-sdk/custom-tools) と [MCP Integration](/docs/ja/agent-sdk/mcp) について学びます
