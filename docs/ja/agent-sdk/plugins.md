> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# SDK のプラグイン

> Agent SDK を通じてカスタムプラグインを読み込み、スキル、エージェント、フック、MCP サーバーで Claude Code を拡張します

プラグインを使用すると、Claude Code をカスタム機能で拡張でき、プロジェクト全体で共有できます。Agent SDK を通じて、ローカルディレクトリからプログラムでプラグインを読み込み、スキル、エージェント、フック、MCP サーバーをエージェントセッションに追加できます。

<h2 id="what-are-plugins">
  プラグインとは何ですか？
</h2>

プラグインは Claude Code 拡張機能のパッケージであり、以下を含めることができます：

* **Skills**: Claude が自律的に使用するモデル呼び出し機能（`/skill-name` で呼び出すこともできます）
* **Agents**: 特定のタスク用の専門的なサブエージェント
* **Hooks**: ツール使用およびその他のイベントに応答するイベントハンドラー
* **MCP servers**: Model Context Protocol 経由の外部ツール統合

<Note>
  `commands/` ディレクトリはレガシー形式です。新しいプラグインには `skills/` を使用してください。Claude Code は後方互換性のために両方の形式をサポートし続けています。
</Note>

プラグイン構造とプラグインの作成方法に関する完全な情報については、[Plugins](/docs/ja/plugins) を参照してください。

<h2 id="loading-plugins">
  プラグインの読み込み
</h2>

オプション設定でローカルファイルシステムパスを指定してプラグインを読み込みます。`type` フィールドは `"local"` である必要があります。これは SDK が受け入れる唯一の値です。[マーケットプレイス](/docs/ja/plugin-marketplaces)またはリモートリポジトリを通じて配布されているプラグインを使用するには、まずダウンロードしてローカルディレクトリパスを指定してください。SDK は複数の場所から複数のプラグインを読み込むことをサポートしています。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Hello",
    options: {
      plugins: [
        { type: "local", path: "./my-plugin" },
        { type: "local", path: "/absolute/path/to/another-plugin" }
      ]
    }
  })) {
    // Plugin commands, agents, and other features are now available
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions


  async def main():
      async for message in query(
          prompt="Hello",
          options=ClaudeAgentOptions(
              plugins=[
                  {"type": "local", "path": "./my-plugin"},
                  {"type": "local", "path": "/absolute/path/to/another-plugin"},
              ]
          ),
      ):
          # Plugin commands, agents, and other features are now available
          pass


  asyncio.run(main())
  ```
</CodeGroup>

<h3 id="path-specifications">
  パス指定
</h3>

プラグインパスは以下のいずれかです：

* **相対パス**: 現在の作業ディレクトリを基準に解決されます（例：`"./plugins/my-plugin"`）
* **絶対パス**: 完全なファイルシステムパス（例：`"/home/user/plugins/my-plugin"`）

<Note>
  パスはプラグインのルートディレクトリ（`skills/`、`agents/`、`hooks/`、`commands/`（レガシー）、または `.claude-plugin/` の親ディレクトリ）を指す必要があります。サブディレクトリではありません。
</Note>

<h2 id="verifying-plugin-installation">
  プラグインインストールの確認
</h2>

プラグインが正常に読み込まれると、システム初期化メッセージに表示されます。プラグインが利用可能であることを確認できます：

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  for await (const message of query({
    prompt: "Hello",
    options: {
      plugins: [{ type: "local", path: "./my-plugin" }]
    }
  })) {
    if (message.type === "system" && message.subtype === "init") {
      // 読み込まれたプラグインを確認
      console.log("Plugins:", message.plugins);
      // 例：[{ name: "my-plugin", path: "./my-plugin" }]

      // プラグインスキルはプラグイン名をプレフィックスとして表示されます
      console.log("Skills:", message.skills);
      // 例：["my-plugin:greet"]

      // プラグインコマンドは同じプレフィックスを使用し、スキルもここに表示されます
      console.log("Commands:", message.slash_commands);
      // 例：["compact", "context", "my-plugin:custom-command", "my-plugin:greet"]
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, SystemMessage


  async def main():
      async for message in query(
          prompt="Hello",
          options=ClaudeAgentOptions(
              plugins=[{"type": "local", "path": "./my-plugin"}]
          ),
      ):
          if isinstance(message, SystemMessage) and message.subtype == "init":
              # 読み込まれたプラグインを確認
              print("Plugins:", message.data.get("plugins"))
              # 例：[{"name": "my-plugin", "path": "./my-plugin"}]

              # プラグインスキルはプラグイン名をプレフィックスとして表示されます
              print("Skills:", message.data.get("skills"))
              # 例：["my-plugin:greet"]

              # プラグインコマンドは同じプレフィックスを使用し、スキルもここに表示されます
              print("Commands:", message.data.get("slash_commands"))
              # 例：["compact", "context", "my-plugin:custom-command", "my-plugin:greet"]


  asyncio.run(main())
  ```
</CodeGroup>

<h2 id="using-plugin-skills">
  プラグインスキルの使用
</h2>

プラグインのスキルは競合を避けるためにプラグイン名で自動的に名前空間化されます。直接呼び出すには、プロンプトとして `/plugin-name:skill-name` を送信してください。

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";

  // Load a plugin with a custom /greet skill
  for await (const message of query({
    prompt: "/my-plugin:greet", // Use plugin skill with namespace
    options: {
      plugins: [{ type: "local", path: "./my-plugin" }]
    }
  })) {
    // Claude executes the custom greeting skill from the plugin
    if (message.type === "assistant") {
      console.log(message.message.content);
    }
  }
  ```

  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock


  async def main():
      # Load a plugin with a custom /greet skill
      async for message in query(
          prompt="/demo-plugin:greet",  # Use plugin skill with namespace
          options=ClaudeAgentOptions(
              plugins=[{"type": "local", "path": "./plugins/demo-plugin"}]
          ),
      ):
          # Claude executes the custom greeting skill from the plugin
          if isinstance(message, AssistantMessage):
              for block in message.content:
                  if isinstance(block, TextBlock):
                      print(f"Claude: {block.text}")


  asyncio.run(main())
  ```
</CodeGroup>

<Note>
  CLI 経由でプラグインをインストールした場合（例：`/plugin install my-plugin@marketplace`）、SDK でそのインストールパスを指定することで引き続き使用できます。CLI でインストールされたプラグインについては `~/.claude/plugins/` を確認してください。
</Note>

<h2 id="complete-example">
  完全な例
</h2>

プラグインの読み込みと使用を示す完全な例を以下に示します：

<CodeGroup>
  ```typescript TypeScript theme={null}
  import { query } from "@anthropic-ai/claude-agent-sdk";
  import * as path from "path";

  async function runWithPlugin() {
    const pluginPath = path.join(__dirname, "plugins", "my-plugin");

    console.log("Loading plugin from:", pluginPath);

    for await (const message of query({
      prompt: "What custom commands do you have available?",
      options: {
        plugins: [{ type: "local", path: pluginPath }],
        maxTurns: 3
      }
    })) {
      if (message.type === "system" && message.subtype === "init") {
        console.log("Loaded plugins:", message.plugins);
        console.log("Available skills:", message.skills);
        console.log("Available commands:", message.slash_commands);
      }

      if (message.type === "assistant") {
        console.log("Assistant:", message.message.content);
      }
    }
  }

  runWithPlugin().catch(console.error);
  ```

  ```python Python theme={null}
  #!/usr/bin/env python3
  """Example demonstrating how to use plugins with the Agent SDK."""

  from pathlib import Path
  import anyio
  from claude_agent_sdk import (
      AssistantMessage,
      ClaudeAgentOptions,
      SystemMessage,
      TextBlock,
      query,
  )


  async def run_with_plugin():
      """Example using a custom plugin."""
      plugin_path = Path(__file__).parent / "plugins" / "demo-plugin"

      print(f"Loading plugin from: {plugin_path}")

      options = ClaudeAgentOptions(
          plugins=[{"type": "local", "path": str(plugin_path)}],
          max_turns=3,
      )

      async for message in query(
          prompt="What custom commands do you have available?", options=options
      ):
          if isinstance(message, SystemMessage) and message.subtype == "init":
              print(f"Loaded plugins: {message.data.get('plugins')}")
              print(f"Available skills: {message.data.get('skills')}")
              print(f"Available commands: {message.data.get('slash_commands')}")

          if isinstance(message, AssistantMessage):
              for block in message.content:
                  if isinstance(block, TextBlock):
                      print(f"Assistant: {block.text}")


  if __name__ == "__main__":
      anyio.run(run_with_plugin)
  ```
</CodeGroup>

<h2 id="plugin-structure-reference">
  プラグイン構造リファレンス
</h2>

プラグインディレクトリには通常、`.claude-plugin/plugin.json` マニフェストファイルが含まれています。マニフェストはオプションです。省略した場合、Claude Code はディレクトリレイアウトからコンポーネントを自動検出します。ディレクトリには以下を含めることができます：

```text theme={null}
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # プラグインマニフェスト（オプション、これなしでもコンポーネントは自動検出されます）
├── skills/                   # Agent Skills（自律的に呼び出されるか /skill-name 経由で呼び出されます）
│   └── my-skill/
│       └── SKILL.md
├── commands/                 # レガシー：代わりに skills/ を使用してください
│   └── custom-cmd.md
├── agents/                   # カスタムエージェント
│   └── specialist.md
├── hooks/                    # イベントハンドラー
│   └── hooks.json
└── .mcp.json                # MCP サーバー定義
```

プラグイン作成の詳細については、以下を参照してください：

* [Plugins](/docs/ja/plugins) - プラグイン開発の完全ガイド
* [Plugins reference](/docs/ja/plugins-reference) - 技術仕様とスキーマ

<h2 id="common-use-cases">
  一般的なユースケース
</h2>

<h3 id="development-and-testing">
  開発とテスト
</h3>

グローバルにインストールせずに開発中にプラグインを読み込みます：

```typescript theme={null}
plugins: [{ type: "local", path: "./dev-plugins/my-plugin" }];
```

<h3 id="project-specific-extensions">
  プロジェクト固有の拡張機能
</h3>

チーム全体の一貫性のためにプラグインをプロジェクトリポジトリに含めます：

```typescript theme={null}
plugins: [{ type: "local", path: "./project-plugins/team-workflows" }];
```

<h3 id="multiple-plugin-sources">
  複数のプラグインソース
</h3>

異なる場所からプラグインを組み合わせます：

```typescript theme={null}
plugins: [
  { type: "local", path: "./local-plugin" },
  { type: "local", path: "~/.claude/custom-plugins/shared-plugin" }
];
```

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

<h3 id="plugin-not-loading">
  プラグインが読み込まれない
</h3>

プラグインが初期化メッセージに表示されない場合：

1. **パスを確認する**: パスがプラグインルートディレクトリ（`skills/`、`agents/`、`hooks/`、`commands/`（レガシー）、または `.claude-plugin/` の親）を指していることを確認してください
2. **plugin.json を検証する**: プラグインにマニフェストが含まれている場合、有効な JSON 構文を持っていることを確認してください
3. **ファイルパーミッションを確認する**: プラグインディレクトリが読み取り可能であることを確認してください

<h3 id="skills-not-appearing">
  スキルが表示されない
</h3>

プラグインスキルが機能しない場合：

1. **名前空間を使用する**: `/plugin-name:skill-name` としてプラグインスキルを呼び出してください
2. **初期化メッセージを確認する**: スキルが正しい名前空間で `skills` リストに表示されることを確認してください
3. **スキルファイルを検証する**: 各スキルが `skills/` の下の独自のサブディレクトリに `SKILL.md` ファイルを持っていることを確認してください（例：`skills/my-skill/SKILL.md`）

<h3 id="path-resolution-issues">
  パス解決の問題
</h3>

相対パスが機能しない場合：

1. **作業ディレクトリを確認する**: 相対パスは現在の作業ディレクトリから解決されます
2. **絶対パスを使用する**: 信頼性のために、絶対パスの使用を検討してください
3. **パスを正規化する**: パスユーティリティを使用してパスを正しく構築してください

<h2 id="see-also">
  関連項目
</h2>

* [Plugins](/docs/ja/plugins) - プラグイン開発の完全ガイド
* [Plugins reference](/docs/ja/plugins-reference) - 技術仕様
* [Commands](/docs/ja/agent-sdk/slash-commands) - SDK でのコマンドの使用
* [Subagents](/docs/ja/agent-sdk/subagents) - 専門的なエージェントの操作
* [Skills](/docs/ja/agent-sdk/skills) - Agent Skills の使用
