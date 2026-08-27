> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Agent SDK リファレンス - Python

> Python Agent SDK の完全な API リファレンス。すべての関数、型、クラスを含みます。

<h2 id="installation">
  インストール
</h2>

仮想環境にパッケージをインストールしてください。最近の Debian、Ubuntu、Homebrew Python インストールでは、システム Python に対して `pip install` を実行すると `error: externally-managed-environment` で失敗します。

```bash theme={null}
python3 -m venv .venv
source .venv/bin/activate
pip install claude-agent-sdk
```

uv、Windows PowerShell、API キーのセットアップについては、[Agent SDK 概要の「Get started」セクション](/docs/ja/agent-sdk/overview#get-started)を参照してください。

<h2 id="choosing-between-query-and-claudesdkclient">
  `query()` と `ClaudeSDKClient` の選択
</h2>

Python SDK は Claude Code と対話するための 2 つの方法を提供します。

<h3 id="quick-comparison">
  クイック比較
</h3>

| 機能            | `query()`                                  | `ClaudeSDKClient` |
| :------------ | :----------------------------------------- | :---------------- |
| **セッション**     | デフォルトで新しいセッションを作成                          | 同じセッションを再利用       |
| **会話**        | 単一の交換                                      | 同じコンテキスト内の複数の交換   |
| **接続**        | 自動的に管理                                     | 手動制御              |
| **ストリーミング入力** | ✅ サポート                                     | ✅ サポート            |
| **割り込み**      | ❌ サポートなし                                   | ✅ サポート            |
| **Hooks**     | ✅ サポート                                     | ✅ サポート            |
| **カスタムツール**   | ✅ サポート                                     | ✅ サポート            |
| **会話を続ける**    | `continue_conversation` または `resume` で手動実行 | ✅ 自動              |
| **ユースケース**    | 1 回限りのタスク                                  | 継続的な会話            |

<h3 id="when-to-use-query-one-off-tasks">
  `query()` を使用する場合（1 回限りのタスク）
</h3>

**最適な用途：**

* 会話履歴が不要な 1 回限りの質問
* 前の交換からのコンテキストが不要な独立したタスク
* シンプルな自動化スクリプト
* 毎回新しく開始したい場合

<h3 id="when-to-use-claudesdkclient-continuous-conversation">
  `ClaudeSDKClient` を使用する場合（継続的な会話）
</h3>

**最適な用途：**

* **会話を続ける** - Claude がコンテキストを記憶する必要がある場合
* **フォローアップ質問** - 前の回答に基づいて構築する
* **インタラクティブなアプリケーション** - チャットインターフェース、REPL
* **応答駆動ロジック** - 次のアクションが Claude の応答に依存する場合
* **セッション制御** - 会話ライフサイクルを明示的に管理する

<h2 id="functions">
  関数
</h2>

<h3 id="query">
  `query()`
</h3>

Claude Code との各インタラクションのために新しいセッションを作成します。デフォルトでは、メッセージが到着するにつれて生成される非同期イテレータを返します。`query()` への各呼び出しは、`continue_conversation=True` または [`ClaudeAgentOptions`](#claudeagentoptions) の `resume` を渡さない限り、前のインタラクションのメモリなしで新しく開始します。[セッション](/docs/ja/agent-sdk/sessions) を参照してください。

```python theme={null}
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None
) -> AsyncIterator[Message]
```

<h4 id="parameters">
  パラメータ
</h4>

| パラメータ       | 型                            | 説明                                                      |
| :---------- | :--------------------------- | :------------------------------------------------------ |
| `prompt`    | `str \| AsyncIterable[dict]` | 入力プロンプト（文字列またはストリーミングモード用の非同期イテレータ）                     |
| `options`   | `ClaudeAgentOptions \| None` | オプションの設定オブジェクト（None の場合は `ClaudeAgentOptions()` がデフォルト） |
| `transport` | `Transport \| None`          | CLI プロセスとの通信用のオプションのカスタムトランスポート                         |

<h4 id="returns">
  戻り値
</h4>

会話からのメッセージを生成する `AsyncIterator[Message]` を返します。

<h4 id="example-with-options">
  例 - オプション付き
</h4>

```python theme={null}
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer",
        permission_mode="acceptEdits",
        cwd="/home/user/project",
    )

    async for message in query(prompt="Create a Python web server", options=options):
        print(message)


asyncio.run(main())
```

<h3 id="tool">
  `tool()`
</h3>

型安全性を備えた MCP ツールを定義するためのデコレータ。

```python theme={null}
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any],
    annotations: ToolAnnotations | None = None
) -> Callable[[Callable[[Any], Awaitable[dict[str, Any]]]], SdkMcpTool[Any]]
```

<h4 id="parameters-2">
  パラメータ
</h4>

| パラメータ          | 型                                               | 説明                                     |
| :------------- | :---------------------------------------------- | :------------------------------------- |
| `name`         | `str`                                           | ツールの一意の識別子                             |
| `description`  | `str`                                           | ツールが何をするかの人間が読める説明                     |
| `input_schema` | `type \| dict[str, Any]`                        | ツールの入力パラメータを定義するスキーマ（以下を参照）            |
| `annotations`  | [`ToolAnnotations`](#toolannotations)` \| None` | クライアントに動作ヒントを提供するオプションの MCP ツールアノテーション |

<h4 id="input-schema-options">
  入力スキーマオプション
</h4>

1. **シンプルな型マッピング**（推奨）：

   ```python theme={null}
   {"text": str, "count": int, "enabled": bool}
   ```

2. **JSON Schema 形式**（複雑な検証用）：
   ```python theme={null}
   {
       "type": "object",
       "properties": {
           "text": {"type": "string"},
           "count": {"type": "integer", "minimum": 0},
       },
       "required": ["text"],
   }
   ```

<h4 id="returns-2">
  戻り値
</h4>

ツール実装をラップし、`SdkMcpTool` インスタンスを返すデコレータ関数。

<h4 id="example">
  例
</h4>

```python theme={null}
from claude_agent_sdk import tool
from typing import Any


@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}
```

<h4 id="toolannotations">
  `ToolAnnotations`
</h4>

`mcp.types` から再エクスポート（`from claude_agent_sdk import ToolAnnotations` としても利用可能）。すべてのフィールドはオプションのヒントです。クライアントはセキュリティ決定のためにこれらに依存すべきではありません。

| フィールド             | 型              | デフォルト   | 説明                                                                            |
| :---------------- | :------------- | :------ | :---------------------------------------------------------------------------- |
| `title`           | `str \| None`  | `None`  | ツールの人間が読める題名                                                                  |
| `readOnlyHint`    | `bool \| None` | `False` | `True` の場合、ツールはその環境を変更しません                                                    |
| `destructiveHint` | `bool \| None` | `True`  | `True` の場合、ツールは破壊的な更新を実行する可能性があります（`readOnlyHint` が `False` の場合のみ意味があります）     |
| `idempotentHint`  | `bool \| None` | `False` | `True` の場合、同じ引数での繰り返し呼び出しは追加の効果がありません（`readOnlyHint` が `False` の場合のみ意味があります）  |
| `openWorldHint`   | `bool \| None` | `True`  | `True` の場合、ツールは外部エンティティと対話します（例：Web 検索）。`False` の場合、ツールのドメインは閉じています（例：メモリツール） |

```python theme={null}
from claude_agent_sdk import tool, ToolAnnotations
from typing import Any


@tool(
    "search",
    "Search the web",
    {"query": str},
    annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
)
async def search(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Results for: {args['query']}"}]}
```

<h3 id="create_sdk_mcp_server">
  `create_sdk_mcp_server()`
</h3>

Python アプリケーション内で実行されるインプロセス MCP サーバーを作成します。

```python theme={null}
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig
```

<h4 id="parameters-3">
  パラメータ
</h4>

| パラメータ     | 型                               | デフォルト     | 説明                           |
| :-------- | :------------------------------ | :-------- | :--------------------------- |
| `name`    | `str`                           | -         | サーバーの一意の識別子                  |
| `version` | `str`                           | `"1.0.0"` | サーバーバージョン文字列                 |
| `tools`   | `list[SdkMcpTool[Any]] \| None` | `None`    | `@tool` デコレータで作成されたツール関数のリスト |

<h4 id="returns-3">
  戻り値
</h4>

`ClaudeAgentOptions.mcp_servers` に渡すことができる `McpSdkServerConfig` オブジェクトを返します。

<h4 id="example-2">
  例
</h4>

```python theme={null}
from claude_agent_sdk import tool, create_sdk_mcp_server


@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": f"Sum: {args['a'] + args['b']}"}]}


@tool("multiply", "Multiply two numbers", {"a": float, "b": float})
async def multiply(args):
    return {"content": [{"type": "text", "text": f"Product: {args['a'] * args['b']}"}]}


calculator = create_sdk_mcp_server(
    name="calculator",
    version="2.0.0",
    tools=[add, multiply],  # Pass decorated functions
)

# Use with Claude
options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add", "mcp__calc__multiply"],
)
```

<h3 id="list_sessions">
  `list_sessions()`
</h3>

メタデータを含む過去のセッションをリストします。プロジェクトディレクトリでフィルタするか、すべてのプロジェクト全体のセッションをリストします。同期的です。すぐに返します。

```python theme={null}
def list_sessions(
    directory: str | None = None,
    limit: int | None = None,
    offset: int = 0,
    include_worktrees: bool = True
) -> list[SDKSessionInfo]
```

<h4 id="parameters-4">
  パラメータ
</h4>

| パラメータ               | 型             | デフォルト  | 説明                                                          |
| :------------------ | :------------ | :----- | :---------------------------------------------------------- |
| `directory`         | `str \| None` | `None` | セッションをリストするディレクトリ。省略した場合、すべてのプロジェクト全体のセッションを返します            |
| `limit`             | `int \| None` | `None` | 返すセッションの最大数                                                 |
| `offset`            | `int`         | `0`    | ソート結果の開始からスキップするセッション数。`limit` と一緒に使用してページネーションを行います        |
| `include_worktrees` | `bool`        | `True` | `directory` が git リポジトリ内にある場合、すべての worktree パスからのセッションを含めます |

<h4 id="return-type-sdksessioninfo">
  戻り値の型：`SDKSessionInfo`
</h4>

| プロパティ           | 型             | 説明                                                    |
| :-------------- | :------------ | :---------------------------------------------------- |
| `session_id`    | `str`         | 一意のセッション識別子                                           |
| `summary`       | `str`         | 表示タイトル：カスタムタイトル、自動生成されたサマリー、または最初のプロンプト               |
| `last_modified` | `int`         | エポック以降のミリ秒単位での最後の変更時刻                                 |
| `file_size`     | `int \| None` | セッションファイルサイズ（バイト）（リモートストレージバックエンドの場合は `None`）         |
| `custom_title`  | `str \| None` | ユーザーが設定したセッションタイトル                                    |
| `first_prompt`  | `str \| None` | セッション内の最初の意味のあるユーザープロンプト                              |
| `git_branch`    | `str \| None` | セッション終了時の Git ブランチ                                    |
| `cwd`           | `str \| None` | セッションの作業ディレクトリ                                        |
| `tag`           | `str \| None` | ユーザーが設定したセッションタグ（[`tag_session()`](#tag_session) を参照） |
| `created_at`    | `int \| None` | エポック以降のミリ秒単位でのセッション作成時刻                               |

<h4 id="example-3">
  例
</h4>

プロジェクトの 10 個の最新セッションを出力します。結果は `last_modified` の降順でソートされるため、最初の項目が最新です。`directory` を省略するとすべてのプロジェクト全体を検索します。

```python theme={null}
from claude_agent_sdk import list_sessions

for session in list_sessions(directory="/path/to/project", limit=10):
    print(f"{session.summary} ({session.session_id})")
```

<h3 id="get_session_messages">
  `get_session_messages()`
</h3>

過去のセッションからメッセージを取得します。同期的です。すぐに返します。

```python theme={null}
def get_session_messages(
    session_id: str,
    directory: str | None = None,
    limit: int | None = None,
    offset: int = 0
) -> list[SessionMessage]
```

<h4 id="parameters-5">
  パラメータ
</h4>

| パラメータ        | 型             | デフォルト  | 説明                                       |
| :----------- | :------------ | :----- | :--------------------------------------- |
| `session_id` | `str`         | 必須     | メッセージを取得するセッション ID                       |
| `directory`  | `str \| None` | `None` | 検索するプロジェクトディレクトリ。省略した場合、すべてのプロジェクトを検索します |
| `limit`      | `int \| None` | `None` | 返すメッセージの最大数                              |
| `offset`     | `int`         | `0`    | 開始からスキップするメッセージ数                         |

<h4 id="return-type-sessionmessage">
  戻り値の型：`SessionMessage`
</h4>

| プロパティ                | 型                              | 説明            |
| :------------------- | :----------------------------- | :------------ |
| `type`               | `Literal["user", "assistant"]` | メッセージロール      |
| `uuid`               | `str`                          | 一意のメッセージ識別子   |
| `session_id`         | `str`                          | セッション識別子      |
| `message`            | `Any`                          | 生のメッセージコンテンツ  |
| `parent_tool_use_id` | `None`                         | 将来の使用のために予約済み |

<h4 id="example-4">
  例
</h4>

```python theme={null}
from claude_agent_sdk import list_sessions, get_session_messages

sessions = list_sessions(limit=1)
if sessions:
    messages = get_session_messages(sessions[0].session_id)
    for msg in messages:
        print(f"[{msg.type}] {msg.uuid}")
```

<h3 id="get_session_info">
  `get_session_info()`
</h3>

プロジェクトディレクトリ全体をスキャンせずに、ID でシングルセッションのメタデータを読み取ります。同期的です。すぐに返します。

```python theme={null}
def get_session_info(
    session_id: str,
    directory: str | None = None,
) -> SDKSessionInfo | None
```

<h4 id="parameters-6">
  パラメータ
</h4>

| パラメータ        | 型             | デフォルト  | 説明                                           |
| :----------- | :------------ | :----- | :------------------------------------------- |
| `session_id` | `str`         | 必須     | 検索するセッションの UUID                              |
| `directory`  | `str \| None` | `None` | プロジェクトディレクトリパス。省略した場合、すべてのプロジェクトディレクトリを検索します |

[`SDKSessionInfo`](#return-type-sdksessioninfo) を返すか、セッションが見つからない場合は `None`。

<h4 id="example-5">
  例
</h4>

プロジェクトディレクトリをスキャンせずに、シングルセッションのメタデータを検索します。前の実行からセッション ID を既に持っている場合に便利です。

```python theme={null}
from claude_agent_sdk import get_session_info

info = get_session_info("550e8400-e29b-41d4-a716-446655440000")
if info:
    print(f"{info.summary} (branch: {info.git_branch}, tag: {info.tag})")
```

<h3 id="rename_session">
  `rename_session()`
</h3>

カスタムタイトルエントリを追加することでセッションの名前を変更します。繰り返し呼び出しは安全です。最新のタイトルが優先されます。同期的です。

```python theme={null}
def rename_session(
    session_id: str,
    title: str,
    directory: str | None = None,
) -> None
```

<h4 id="parameters-7">
  パラメータ
</h4>

| パラメータ        | 型             | デフォルト  | 説明                                           |
| :----------- | :------------ | :----- | :------------------------------------------- |
| `session_id` | `str`         | 必須     | 名前を変更するセッションの UUID                           |
| `title`      | `str`         | 必須     | 新しいタイトル。空白をストリップした後、空でない必要があります              |
| `directory`  | `str \| None` | `None` | プロジェクトディレクトリパス。省略した場合、すべてのプロジェクトディレクトリを検索します |

`session_id` が有効な UUID でない場合、または `title` が空の場合は `ValueError` を発生させます。セッションが見つからない場合は `FileNotFoundError`。

<h4 id="example-6">
  例
</h4>

最新のセッションの名前を変更して、後で見つけやすくします。新しいタイトルは、その後の読み取りで [`SDKSessionInfo.custom_title`](#return-type-sdksessioninfo) に表示されます。

```python theme={null}
from claude_agent_sdk import list_sessions, rename_session

sessions = list_sessions(directory="/path/to/project", limit=1)
if sessions:
    rename_session(sessions[0].session_id, "Refactor auth module")
```

<h3 id="tag_session">
  `tag_session()`
</h3>

セッションにタグを付けます。`None` を渡してタグをクリアします。繰り返し呼び出しは安全です。最新のタグが優先されます。同期的です。

```python theme={null}
def tag_session(
    session_id: str,
    tag: str | None,
    directory: str | None = None,
) -> None
```

<h4 id="parameters-8">
  パラメータ
</h4>

| パラメータ        | 型             | デフォルト  | 説明                                              |
| :----------- | :------------ | :----- | :---------------------------------------------- |
| `session_id` | `str`         | 必須     | タグを付けるセッションの UUID                               |
| `tag`        | `str \| None` | 必須     | タグ文字列、またはクリアする場合は `None`。保存前に Unicode サニタイズされます |
| `directory`  | `str \| None` | `None` | プロジェクトディレクトリパス。省略した場合、すべてのプロジェクトディレクトリを検索します    |

`session_id` が有効な UUID でない場合、またはサニタイズ後に `tag` が空の場合は `ValueError` を発生させます。セッションが見つからない場合は `FileNotFoundError`。

<h4 id="example-7">
  例
</h4>

セッションにタグを付けてから、後の読み取りでそのタグでフィルタします。既存のタグをクリアするには `None` を渡します。

```python theme={null}
from claude_agent_sdk import list_sessions, tag_session

# Tag a session
tag_session("550e8400-e29b-41d4-a716-446655440000", "needs-review")

# Later: find all sessions with that tag
for session in list_sessions(directory="/path/to/project"):
    if session.tag == "needs-review":
        print(session.summary)
```

<h2 id="classes">
  クラス
</h2>

<h3 id="claudesdkclient">
  `ClaudeSDKClient`
</h3>

**複数の交換にわたってセッションを維持します。** これは TypeScript SDK の `query()` 関数が内部的にどのように機能するかの Python 同等物です。会話を続けることができるクライアントオブジェクトを作成します。

<h4 id="key-features">
  主な機能
</h4>

* **セッション継続性**：複数の `query()` 呼び出しにわたって会話コンテキストを維持します
* **同じ会話**：セッションは前のメッセージを保持します
* **割り込みサポート**：タスク途中で実行を停止できます
* **明示的なライフサイクル**：セッションの開始と終了を制御します
* **応答駆動フロー**：応答に反応してフォローアップを送信できます
* **カスタムツールと hooks**：カスタムツール（`@tool` デコレータで作成）と hooks をサポートします

```python theme={null}
class ClaudeSDKClient:
    def __init__(self, options: ClaudeAgentOptions | None = None, transport: Transport | None = None)
    async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
    async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
    async def receive_messages(self) -> AsyncIterator[Message]
    async def receive_response(self) -> AsyncIterator[Message]
    async def interrupt(self) -> None
    async def set_permission_mode(self, mode: str) -> None
    async def set_model(self, model: str | None = None) -> None
    async def rewind_files(self, user_message_id: str) -> None
    async def get_mcp_status(self) -> McpStatusResponse
    async def reconnect_mcp_server(self, server_name: str) -> None
    async def toggle_mcp_server(self, server_name: str, enabled: bool) -> None
    async def stop_task(self, task_id: str) -> None
    async def get_server_info(self) -> dict[str, Any] | None
    async def disconnect(self) -> None
```

<h4 id="methods">
  メソッド
</h4>

| メソッド                                      | 説明                                                                                                                       |
| :---------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| `__init__(options)`                       | オプションの設定でクライアントを初期化します                                                                                                   |
| `connect(prompt)`                         | オプションの初期プロンプトまたはメッセージストリームで Claude に接続します                                                                                |
| `query(prompt, session_id)`               | ストリーミングモードで新しいリクエストを送信します                                                                                                |
| `receive_messages()`                      | Claude からのすべてのメッセージを非同期イテレータとして受け取ります                                                                                    |
| `receive_response()`                      | ResultMessage を含むまでのメッセージを受け取ります                                                                                         |
| `interrupt()`                             | 割り込み信号を送信します（ストリーミングモードでのみ機能）                                                                                            |
| `set_permission_mode(mode)`               | 現在のセッションのパーミッションモードを変更します                                                                                                |
| `set_model(model)`                        | 現在のセッションのモデルを変更します。デフォルトにリセットするには `None` を渡します                                                                           |
| `rewind_files(user_message_id)`           | ファイルを指定されたユーザーメッセージの状態に復元します。`enable_file_checkpointing=True` が必要です。[ファイルチェックポイント](/docs/ja/agent-sdk/file-checkpointing) を参照 |
| `get_mcp_status()`                        | すべての設定済み MCP サーバーのステータスを取得します。[`McpStatusResponse`](#mcpstatusresponse) を返します                                            |
| `reconnect_mcp_server(server_name)`       | 失敗したか切断された MCP サーバーへの再接続を試みます                                                                                            |
| `toggle_mcp_server(server_name, enabled)` | セッション中に MCP サーバーを有効または無効にします。無効にするとそのツールが削除されます                                                                          |
| `stop_task(task_id)`                      | 実行中のバックグラウンドタスクを停止します。ステータス `"stopped"` の [`TaskNotificationMessage`](#tasknotificationmessage) がメッセージストリームに続きます         |
| `get_server_info()`                       | セッション ID と機能を含むサーバー情報を取得します                                                                                              |
| `disconnect()`                            | Claude から切断します                                                                                                           |

<h4 id="context-manager-support">
  コンテキストマネージャーサポート
</h4>

クライアントは自動接続管理のための非同期コンテキストマネージャーとして使用できます：

```python theme={null}
async with ClaudeSDKClient() as client:
    await client.query("Hello Claude")
    async for message in client.receive_response():
        print(message)
```

> **重要：** メッセージを反復処理する場合、早期に終了するために `break` を使用することは避けてください。これは asyncio クリーンアップの問題を引き起こす可能性があります。代わりに、反復を自然に完了させるか、フラグを使用して必要なものを見つけたときを追跡してください。

<h4 id="example-continuing-a-conversation">
  例 - 会話を続ける
</h4>

```python theme={null}
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock, ResultMessage


async def main():
    async with ClaudeSDKClient() as client:
        # First question
        await client.query("What's the capital of France?")

        # Process response
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up question - the session retains the previous context
        await client.query("What's the population of that city?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Another follow-up - still in the same conversation
        await client.query("What are some famous landmarks there?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")


asyncio.run(main())
```

<h4 id="example-streaming-input-with-claudesdkclient">
  例 - ClaudeSDKClient でのストリーミング入力
</h4>

```python theme={null}
import asyncio
from claude_agent_sdk import ClaudeSDKClient


async def message_stream():
    """Generate messages dynamically."""
    yield {
        "type": "user",
        "message": {"role": "user", "content": "Analyze the following data:"},
    }
    await asyncio.sleep(0.5)
    yield {
        "type": "user",
        "message": {"role": "user", "content": "Temperature: 25°C, Humidity: 60%"},
    }
    await asyncio.sleep(0.5)
    yield {
        "type": "user",
        "message": {"role": "user", "content": "What patterns do you see?"},
    }


async def main():
    async with ClaudeSDKClient() as client:
        # Stream input to Claude
        await client.query(message_stream())

        # Process response
        async for message in client.receive_response():
            print(message)

        # Follow-up in same session
        await client.query("Should we be concerned about these readings?")

        async for message in client.receive_response():
            print(message)


asyncio.run(main())
```

<h4 id="example-using-interrupts">
  例 - 割り込みの使用
</h4>

```python theme={null}
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, ResultMessage


async def interruptible_task():
    options = ClaudeAgentOptions(allowed_tools=["Bash"], permission_mode="acceptEdits")

    async with ClaudeSDKClient(options=options) as client:
        # Start a long-running task
        await client.query("Count from 1 to 100 slowly, using the bash sleep command")

        # Let it run for a bit
        await asyncio.sleep(2)

        # Interrupt the task
        await client.interrupt()
        print("Task interrupted!")

        # Drain the interrupted task's messages (including its ResultMessage)
        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                print(f"Interrupted task finished with subtype={message.subtype!r}")
                # subtype is "error_during_execution" for interrupted tasks

        # Send a new command
        await client.query("Just say hello instead")

        # Now receive the new response
        async for message in client.receive_response():
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(f"New result: {message.result}")


asyncio.run(interruptible_task())
```

<Note>
  **割り込み後のバッファ動作：** `interrupt()` は停止信号を送信しますが、メッセージバッファをクリアしません。割り込まれたタスクによって既に生成されたメッセージ（`subtype="error_during_execution"` の `ResultMessage` を含む）はストリームに残ります。新しいクエリの応答を読む前に、`receive_response()` でそれらをドレインする必要があります。`interrupt()` の直後に新しいクエリを送信し、`receive_response()` を 1 回だけ呼び出すと、割り込まれたタスクのメッセージが受け取られ、新しいクエリの応答ではありません。
</Note>

<h4 id="example-advanced-permission-control">
  例 - 高度なパーミッション制御
</h4>

```python theme={null}
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import (
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)


async def custom_permission_handler(
    tool_name: str, input_data: dict, context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    """Custom logic for tool permissions."""

    # Block writes to system directories
    if tool_name == "Write" and input_data.get("file_path", "").startswith("/system/"):
        return PermissionResultDeny(
            message="System directory write not allowed", interrupt=True
        )

    # Redirect sensitive file operations
    if tool_name in ["Write", "Edit"] and "config" in input_data.get("file_path", ""):
        safe_path = f"./sandbox/{input_data['file_path']}"
        return PermissionResultAllow(
            updated_input={**input_data, "file_path": safe_path}
        )

    # Allow everything else
    return PermissionResultAllow(updated_input=input_data)


async def main():
    # ゲートされたツールを allowed_tools にも列挙しないでください：許可ルールは can_use_tool が実行される前に呼び出しを承認します
    options = ClaudeAgentOptions(can_use_tool=custom_permission_handler)

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Update the system config file")

        async for message in client.receive_response():
            # Will use sandbox path instead
            print(message)


asyncio.run(main())
```

<h2 id="types">
  型
</h2>

<Note>
  **`@dataclass` vs `TypedDict`：** この SDK は 2 種類の型を使用します。`@dataclass` で装飾されたクラス（`ResultMessage`、`AgentDefinition`、`TextBlock` など）は実行時にオブジェクトインスタンスであり、属性アクセスをサポートします：`msg.result`。`TypedDict` で定義されたクラス（`ThinkingConfigEnabled`、`McpStdioServerConfig`、`SyncHookJSONOutput` など）は**実行時にプレーンな dict** であり、キーアクセスが必要です：`config["budget_tokens"]`、`config.budget_tokens` ではなく。`ClassName(field=value)` 呼び出し構文は両方で機能しますが、dataclass のみが属性を持つオブジェクトを生成します。
</Note>

<h3 id="sdkmcptool">
  `SdkMcpTool`
</h3>

`@tool` デコレータで作成された SDK MCP ツールの定義。

```python theme={null}
@dataclass
class SdkMcpTool(Generic[T]):
    name: str
    description: str
    input_schema: type[T] | dict[str, Any]
    handler: Callable[[T], Awaitable[dict[str, Any]]]
    annotations: ToolAnnotations | None = None
```

| プロパティ          | 型                                          | 説明                                                                                       |
| :------------- | :----------------------------------------- | :--------------------------------------------------------------------------------------- |
| `name`         | `str`                                      | ツールの一意の識別子                                                                               |
| `description`  | `str`                                      | 人間が読める説明                                                                                 |
| `input_schema` | `type[T] \| dict[str, Any]`                | 入力検証用のスキーマ                                                                               |
| `handler`      | `Callable[[T], Awaitable[dict[str, Any]]]` | ツール実行を処理する非同期関数                                                                          |
| `annotations`  | `ToolAnnotations \| None`                  | オプションの MCP ツールアノテーション（例：`readOnlyHint`、`destructiveHint`、`openWorldHint`）。`mcp.types` から |

<h3 id="transport">
  `Transport`
</h3>

カスタムトランスポート実装の抽象基本クラス。これを使用して、カスタムチャネル（例：ローカルサブプロセスの代わりにリモート接続）を介して Claude プロセスと通信します。

<Warning>
  これは低レベルの内部 API です。インターフェースは将来のリリースで変更される可能性があります。カスタム実装は、インターフェースの変更に合わせて更新する必要があります。
</Warning>

```python theme={null}
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any


class Transport(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def write(self, data: str) -> None: ...

    @abstractmethod
    def read_messages(self) -> AsyncIterator[dict[str, Any]]: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    def is_ready(self) -> bool: ...

    @abstractmethod
    async def end_input(self) -> None: ...
```

| メソッド              | 説明                                        |
| :---------------- | :---------------------------------------- |
| `connect()`       | トランスポートを接続し、通信の準備をします                     |
| `write(data)`     | 生データ（JSON + 改行）をトランスポートに書き込みます            |
| `read_messages()` | 解析された JSON メッセージを生成する非同期イテレータ             |
| `close()`         | 接続を閉じてリソースをクリーンアップします                     |
| `is_ready()`      | トランスポートが送受信できる場合は `True` を返します            |
| `end_input()`     | 入力ストリームを閉じます（例：サブプロセストランスポートの stdin を閉じる） |

インポート：`from claude_agent_sdk import Transport`

<h3 id="claudeagentoptions">
  `ClaudeAgentOptions`
</h3>

Claude Code クエリの設定 dataclass。

```python theme={null}
@dataclass
class ClaudeAgentOptions:
    tools: list[str] | ToolsPreset | None = None
    allowed_tools: list[str] = field(default_factory=list)
    system_prompt: str | SystemPromptPreset | SystemPromptFile | None = None
    mcp_servers: dict[str, McpServerConfig] | str | Path = field(default_factory=dict)
    strict_mcp_config: bool = False
    permission_mode: PermissionMode | None = None
    continue_conversation: bool = False
    resume: str | None = None
    max_turns: int | None = None
    max_budget_usd: float | None = None
    disallowed_tools: list[str] = field(default_factory=list)
    model: str | None = None
    fallback_model: str | None = None
    betas: list[SdkBeta] = field(default_factory=list)
    output_format: dict[str, Any] | None = None
    permission_prompt_tool_name: str | None = None
    cwd: str | Path | None = None
    cli_path: str | Path | None = None
    settings: str | None = None
    add_dirs: list[str | Path] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    extra_args: dict[str, str | None] = field(default_factory=dict)
    max_buffer_size: int | None = None
    debug_stderr: Any = sys.stderr  # Deprecated
    stderr: Callable[[str], None] | None = None
    can_use_tool: CanUseTool | None = None
    hooks: dict[HookEvent, list[HookMatcher]] | None = None
    user: str | None = None
    include_partial_messages: bool = False
    include_hook_events: bool = False
    fork_session: bool = False
    agents: dict[str, AgentDefinition] | None = None
    setting_sources: list[SettingSource] | None = None
    skills: list[str] | Literal["all"] | None = None
    sandbox: SandboxSettings | None = None
    plugins: list[SdkPluginConfig] = field(default_factory=list)
    max_thinking_tokens: int | None = None  # Deprecated: use thinking instead
    thinking: ThinkingConfig | None = None
    effort: EffortLevel | None = None
    enable_file_checkpointing: bool = False
    session_store: SessionStore | None = None
    session_store_flush: SessionStoreFlushMode = "batched"
```

| プロパティ                         | 型                                                                                     | デフォルト                     | 説明                                                                                                                                                                                                                                                                                                             |
| :---------------------------- | :------------------------------------------------------------------------------------ | :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tools`                       | `list[str] \| ToolsPreset \| None`                                                    | `None`                    | ツール設定。Claude Code のデフォルトツールには `{"type": "preset", "preset": "claude_code"}` を使用します                                                                                                                                                                                                                             |
| `allowed_tools`               | `list[str]`                                                                           | `[]`                      | プロンプトなしで自動承認するツール。これは Claude をこれらのツールのみに制限しません。リストされていないツールは `permission_mode` と `can_use_tool` にフォールスルーします。`disallowed_tools` を使用してツールをブロックします。[パーミッション](/docs/ja/agent-sdk/permissions#allow-and-deny-rules) を参照                                                                                                  |
| `system_prompt`               | `str \| SystemPromptPreset \| SystemPromptFile \| None`                               | `None`                    | システムプロンプト設定。カスタムプロンプトの場合は文字列を渡すか、Claude Code のシステムプロンプトの場合は `{"type": "preset", "preset": "claude_code"}` を使用します。オプションの `"append"` を含めるか、`{"type": "file", "path": "..."}` を使用してディスクから大きなプロンプトを読み込みます。[`SystemPromptPreset`](#systempromptpreset) と [`SystemPromptFile`](#systempromptfile) を参照                |
| `mcp_servers`                 | `dict[str, McpServerConfig] \| str \| Path`                                           | `{}`                      | MCP サーバー設定または設定ファイルへのパス                                                                                                                                                                                                                                                                                        |
| `strict_mcp_config`           | `bool`                                                                                | `False`                   | `True` の場合、`mcp_servers` で渡されたサーバーのみを使用し、プロジェクト `.mcp.json`、ユーザー設定、プラグイン提供の MCP サーバー、および [claude.ai コネクタ](/docs/ja/mcp#use-mcp-servers-from-claude-ai) を無視します。CLI `--strict-mcp-config` フラグにマップされます                                                                                                                 |
| `permission_mode`             | `PermissionMode \| None`                                                              | `None`                    | ツール使用のパーミッションモード                                                                                                                                                                                                                                                                                               |
| `continue_conversation`       | `bool`                                                                                | `False`                   | 最新の会話を続ける                                                                                                                                                                                                                                                                                                      |
| `resume`                      | `str \| None`                                                                         | `None`                    | 再開するセッション ID                                                                                                                                                                                                                                                                                                   |
| `max_turns`                   | `int \| None`                                                                         | `None`                    | 最大 agentic ターン数（ツール使用ラウンドトリップ）                                                                                                                                                                                                                                                                                 |
| `max_budget_usd`              | `float \| None`                                                                       | `None`                    | クライアント側のコスト推定がこの USD 値に達したときにクエリを停止します。`total_cost_usd` と同じ推定と比較されます。[コストと使用状況を追跡](/docs/ja/agent-sdk/cost-tracking) で精度の注意事項を参照                                                                                                                                                                                    |
| `disallowed_tools`            | `list[str]`                                                                           | `[]`                      | 拒否するツール。`Bash` などの単純な名前はツールを Claude のコンテキストから削除します。`Bash(rm *)` などのスコープ付きルールはツールを利用可能なままにし、`bypassPermissions` を含むすべてのパーミッションモードで一致する呼び出しを拒否します。[パーミッション](/docs/ja/agent-sdk/permissions#allow-and-deny-rules) を参照                                                                                                  |
| `enable_file_checkpointing`   | `bool`                                                                                | `False`                   | ファイル変更追跡を有効にして巻き戻しを可能にします。[ファイルチェックポイント](/docs/ja/agent-sdk/file-checkpointing) を参照                                                                                                                                                                                                                                 |
| `model`                       | `str \| None`                                                                         | `None`                    | Claude モデルエイリアスまたは完全なモデル名。[受け入れられた値とプロバイダー固有の ID](/docs/ja/model-config#available-models) を参照                                                                                                                                                                                                                       |
| `fallback_model`              | `str \| None`                                                                         | `None`                    | プライマリモデルが失敗した場合に使用するフォールバックモデル                                                                                                                                                                                                                                                                                 |
| `betas`                       | `list[SdkBeta]`                                                                       | `[]`                      | 有効にするベータ機能。利用可能なオプションについては [`SdkBeta`](#sdkbeta) を参照                                                                                                                                                                                                                                                           |
| `output_format`               | `dict[str, Any] \| None`                                                              | `None`                    | 構造化応答の出力形式（例：`{"type": "json_schema", "schema": {...}}`）。詳細については [構造化出力](/docs/ja/agent-sdk/structured-outputs) を参照                                                                                                                                                                                                 |
| `permission_prompt_tool_name` | `str \| None`                                                                         | `None`                    | パーミッションプロンプト用の MCP ツール名                                                                                                                                                                                                                                                                                        |
| `cwd`                         | `str \| Path \| None`                                                                 | `None`                    | 現在の作業ディレクトリ                                                                                                                                                                                                                                                                                                    |
| `cli_path`                    | `str \| Path \| None`                                                                 | `None`                    | Claude Code CLI 実行可能ファイルへのカスタムパス                                                                                                                                                                                                                                                                               |
| `settings`                    | `str \| None`                                                                         | `None`                    | 設定ファイルへのパス                                                                                                                                                                                                                                                                                                     |
| `add_dirs`                    | `list[str \| Path]`                                                                   | `[]`                      | Claude がアクセスできる追加ディレクトリ                                                                                                                                                                                                                                                                                        |
| `env`                         | `dict[str, str]`                                                                      | `{}`                      | 継承されたプロセス環境の上にマージされた環境変数。[環境変数](/docs/ja/env-vars) で、基盤となる CLI が読み込む変数を参照し、[遅いまたは停止した API レスポンスを処理](#handle-slow-or-stalled-api-responses) でタイムアウト関連の変数を参照してください                                                                                                                                                    |
| `extra_args`                  | `dict[str, str \| None]`                                                              | `{}`                      | CLI に直接渡す追加 CLI 引数                                                                                                                                                                                                                                                                                             |
| `max_buffer_size`             | `int \| None`                                                                         | `None`                    | CLI stdout をバッファリングする場合の最大バイト数                                                                                                                                                                                                                                                                                 |
| `debug_stderr`                | `Any`                                                                                 | `sys.stderr`              | *非推奨* - デバッグ出力用のファイルのようなオブジェクト。代わりに `stderr` コールバックを使用してください                                                                                                                                                                                                                                                   |
| `stderr`                      | `Callable[[str], None] \| None`                                                       | `None`                    | CLI からの stderr 出力用のコールバック関数                                                                                                                                                                                                                                                                                    |
| `can_use_tool`                | [`CanUseTool`](#canusetool) ` \| None`                                                | `None`                    | ツールパーミッションコールバック関数。[パーミッション評価フロー](/docs/ja/agent-sdk/permissions#how-permissions-are-evaluated) がプロンプトに解決される場合にのみ呼び出されます。`allowed_tools` エントリ、設定許可ルール、または `permission_mode` によって事前承認されたツール呼び出しは呼び出されません。すべてのツール呼び出しをゲートするには、代わりに [`PreToolUse` hook](/docs/ja/agent-sdk/hooks) を使用してください。[`CanUseTool`](#canusetool) を参照 |
| `hooks`                       | `dict[HookEvent, list[HookMatcher]] \| None`                                          | `None`                    | イベントをインターセプトするための hook 設定                                                                                                                                                                                                                                                                                      |
| `user`                        | `str \| None`                                                                         | `None`                    | ユーザー識別子                                                                                                                                                                                                                                                                                                        |
| `include_partial_messages`    | `bool`                                                                                | `False`                   | 部分的なメッセージストリーミングイベントを含めます。有効にすると、[`StreamEvent`](#streamevent) メッセージが生成されます                                                                                                                                                                                                                                    |
| `include_hook_events`         | `bool`                                                                                | `False`                   | hook ライフサイクルイベントをメッセージストリームに `HookEventMessage` オブジェクトとして含めます                                                                                                                                                                                                                                                  |
| `fork_session`                | `bool`                                                                                | `False`                   | `resume` で再開する場合、元のセッションを続ける代わりに新しいセッション ID にフォークします                                                                                                                                                                                                                                                           |
| `agents`                      | `dict[str, AgentDefinition] \| None`                                                  | `None`                    | プログラムで定義されたサブエージェント                                                                                                                                                                                                                                                                                            |
| `plugins`                     | `list[SdkPluginConfig]`                                                               | `[]`                      | ローカルパスからカスタムプラグインを読み込みます。詳細については [プラグイン](/docs/ja/agent-sdk/plugins) を参照                                                                                                                                                                                                                                            |
| `sandbox`                     | [`SandboxSettings`](#sandboxsettings) ` \| None`                                      | `None`                    | プログラムでサンドボックス動作を設定します。詳細については [サンドボックス設定](#sandboxsettings) を参照                                                                                                                                                                                                                                                |
| `setting_sources`             | `list[SettingSource] \| None`                                                         | `None`（CLI デフォルト：すべてのソース） | 読み込むファイルシステム設定を制御します。`[]` を渡してユーザー、プロジェクト、ローカル設定を無効にします。管理ポリシー設定は常に読み込まれます。[Claude Code 機能を使用](/docs/ja/agent-sdk/claude-code-features#what-settingsources-does-not-control) を参照                                                                                                                                    |
| `skills`                      | `list[str] \| Literal["all"] \| None`                                                 | `None`                    | セッションで利用可能なスキル。すべての検出されたスキルを有効にするには `"all"` を渡すか、スキル名のリストを渡します。設定すると、SDK は `allowed_tools` にリストしなくても Skill ツールを自動的に有効にします。[スキル](/docs/ja/agent-sdk/skills) を参照                                                                                                                                                      |
| `max_thinking_tokens`         | `int \| None`                                                                         | `None`                    | *非推奨* - 思考ブロックの最大トークン数。代わりに `thinking` を使用してください                                                                                                                                                                                                                                                               |
| `thinking`                    | [`ThinkingConfig`](#thinkingconfig) ` \| None`                                        | `None`                    | 拡張思考動作を制御します。`max_thinking_tokens` より優先されます                                                                                                                                                                                                                                                                    |
| `effort`                      | [`EffortLevel`](#effortlevel) ` \| None`                                              | `None`                    | 思考の深さの努力レベル。[努力レベルを調整](/docs/ja/model-config#adjust-effort-level) を参照                                                                                                                                                                                                                                               |
| `session_store`               | [`SessionStore`](/docs/ja/agent-sdk/session-storage#the-sessionstore-interface) ` \| None` | `None`                    | セッショントランスクリプトを外部バックエンドにミラーリングして、任意のホストがそれらを再開できるようにします。[セッションを外部ストレージに永続化](/docs/ja/agent-sdk/session-storage) を参照                                                                                                                                                                                                  |
| `session_store_flush`         | `Literal["batched", "eager"]`                                                         | `"batched"`               | ミラーリングされたトランスクリプトエントリを `session_store` にフラッシュするタイミング。`"batched"` はターンごと、またはバッファが満杯になったときにフラッシュします。`"eager"` はすべてのフレームの後にバックグラウンドフラッシュをトリガーします。`session_store` が `None` の場合は無視されます                                                                                                                              |

<h4 id="handle-slow-or-stalled-api-responses">
  遅いまたは停止した API レスポンスを処理
</h4>

CLI サブプロセスは、API タイムアウトと停止検出を制御するいくつかの環境変数を読み込みます。`ClaudeAgentOptions.env` を通じてそれらを渡します：

```python theme={null}
options = ClaudeAgentOptions(
    env={
        "API_TIMEOUT_MS": "120000",
        "CLAUDE_CODE_MAX_RETRIES": "2",
        "CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS": "120000",
    },
)
```

* `API_TIMEOUT_MS`：Anthropic クライアントのリクエストごとのタイムアウト（ミリ秒単位）。デフォルト `600000`。メインループとすべてのサブエージェントに適用されます。
* `CLAUDE_CODE_MAX_RETRIES`：最大 API リトライ数。デフォルト `10`、上限 `15`。各リトライは独自の `API_TIMEOUT_MS` ウィンドウを取得するため、最悪の場合の実時間はおおよそ `API_TIMEOUT_MS × (CLAUDE_CODE_MAX_RETRIES + 1)` にバックオフを加えたものです。無人実行で長時間の停止を待つ必要がある場合は、`CLAUDE_CODE_RETRY_WATCHDOG=1` を設定します：容量エラーを無限に再試行し、Claude Code v2.1.199 以降は他の一時的なエラーのデフォルトを `300` に引き上げ、この変数の上限を削除します。
* `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`：`run_in_background` で起動されたサブエージェント用の停止ウォッチドッグ。デフォルト `600000`。各ストリームイベントでリセットされます。停止時にサブエージェントを中止し、タスクを失敗とマークし、部分的な結果を含むエラーを親に表示します。同期サブエージェントには適用されません。
* `CLAUDE_ENABLE_STREAM_WATCHDOG` と `CLAUDE_STREAM_IDLE_TIMEOUT_MS`：ヘッダーが到着したがレスポンスボディがストリーミングを停止したときにリクエストを中止します。ウォッチドッグはすべてのプロバイダーでデフォルトで有効です。`CLAUDE_ENABLE_STREAM_WATCHDOG=0` を設定して無効にします。`CLAUDE_STREAM_IDLE_TIMEOUT_MS` はデフォルト `300000` で、その最小値にクランプされます。中止されたリクエストは通常のリトライパスを通ります。

<h3 id="outputformat">
  `OutputFormat`
</h3>

構造化出力検証の設定。これを `ClaudeAgentOptions` の `output_format` フィールドに dict として渡します：

```python theme={null}
# Expected dict shape for output_format
{
    "type": "json_schema",
    "schema": {...},  # Your JSON Schema definition
}
```

| フィールド    | 必須 | 説明                                            |
| :------- | :- | :-------------------------------------------- |
| `type`   | はい | JSON Schema 検証の場合は `"json_schema"` である必要があります |
| `schema` | はい | 出力検証用の JSON Schema 定義                         |

<h3 id="systempromptpreset">
  `SystemPromptPreset`
</h3>

オプションの追加を含む Claude Code のプリセットシステムプロンプトを使用するための設定。

```python theme={null}
class SystemPromptPreset(TypedDict):
    type: Literal["preset"]
    preset: Literal["claude_code"]
    append: NotRequired[str]
    exclude_dynamic_sections: NotRequired[bool]
```

| フィールド                      | 必須  | 説明                                                                                                                                                                                                                        |
| :------------------------- | :-- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`                     | はい  | プリセットシステムプロンプトを使用するには `"preset"` である必要があります                                                                                                                                                                               |
| `preset`                   | はい  | Claude Code のシステムプロンプトを使用するには `"claude_code"` である必要があります                                                                                                                                                                  |
| `append`                   | いいえ | プリセットシステムプロンプトに追加する追加の指示                                                                                                                                                                                                  |
| `exclude_dynamic_sections` | いいえ | 作業ディレクトリ、git リポジトリフラグ、自動メモリパスなどのセッションごとのコンテキストをシステムプロンプトから最初のユーザーメッセージに移動します。ユーザーとマシン全体でのプロンプトキャッシュの再利用を改善します。[システムプロンプトを変更](/docs/ja/agent-sdk/modifying-system-prompts#improve-prompt-caching-across-users-and-machines) を参照 |

<h3 id="systempromptfile">
  `SystemPromptFile`
</h3>

ファイルからカスタムシステムプロンプトを読み込むための設定。文字列として渡す代わりに、ファイル形式を使用します。SDK はこれを CLI [`--system-prompt-file`](/docs/ja/cli-reference#system-prompt-flags) フラグにマップします。プロンプトが大きい場合はファイル形式を使用します：SDK は文字列 `system_prompt` を CLI サブプロセス argv に渡します。これは OS コマンドライン長制限の対象となり、SDK が API リクエストを送信する前に失敗します。Linux では、単一の引数が約 128 KB より長い場合、`Argument list too long` でプロセス生成に失敗します。Windows では、コマンドライン全体が約 32 KB に制限されているため、文字列形式はより低いしきい値で失敗します。

```python theme={null}
class SystemPromptFile(TypedDict):
    type: Literal["file"]
    path: str
```

| フィールド  | 必須 | 説明                                     |
| :----- | :- | :------------------------------------- |
| `type` | はい | プロンプトをディスクから読み込むには `"file"` である必要があります |
| `path` | はい | システムプロンプトを含むファイルへのパス                   |

<h3 id="settingsource">
  `SettingSource`
</h3>

SDK が設定を読み込むファイルシステムベースの設定ソースを制御します。

```python theme={null}
SettingSource = Literal["user", "project", "local"]
```

| 値           | 説明                       | 場所                            |
| :---------- | :----------------------- | :---------------------------- |
| `"user"`    | グローバルユーザー設定              | `~/.claude/settings.json`     |
| `"project"` | 共有プロジェクト設定（バージョン管理）      | `.claude/settings.json`       |
| `"local"`   | ローカルプロジェクト設定（gitignored） | `.claude/settings.local.json` |

<h4 id="default-behavior">
  デフォルト動作
</h4>

`setting_sources` が省略されるか `None` の場合、`query()` は Claude Code CLI と同じファイルシステム設定を読み込みます：ユーザー、プロジェクト、ローカル。管理ポリシー設定はすべての場合に読み込まれます。サーバー管理設定は、セッションが [適格な設定](/docs/ja/server-managed-settings#platform-availability) 上の組織認証情報で認証されるときに取得されます。[Claude Code 機能を使用](/docs/ja/agent-sdk/claude-code-features#what-settingsources-does-not-control) を参照して、このオプションに関係なく読み込まれる入力と、それらを無効にする方法を確認してください。

<h4 id="why-use-setting_sources">
  setting\_sources を使用する理由
</h4>

**ファイルシステム設定を無効にする：**

```python theme={null}
# Do not load user, project, or local settings from disk
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Analyze this code",
    options=ClaudeAgentOptions(
        setting_sources=[]
    ),
):
    print(message)
```

<Note>
  Python SDK 0.1.59 以前では、空のリストはオプションを省略するのと同じように扱われていたため、`setting_sources=[]` はファイルシステム設定を無効にしませんでした。空のリストが有効になる必要がある場合は、新しいリリースにアップグレードしてください。TypeScript SDK は影響を受けません。
</Note>

**すべてのファイルシステム設定を明示的に読み込む：**

```python theme={null}
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Analyze this code",
    options=ClaudeAgentOptions(
        setting_sources=["user", "project", "local"]
    ),
):
    print(message)
```

**特定の設定ソースのみを読み込む：**

```python theme={null}
# Load only project settings, ignore user and local
async for message in query(
    prompt="Run CI checks",
    options=ClaudeAgentOptions(
        setting_sources=["project"]  # Only .claude/settings.json
    ),
):
    print(message)
```

**テストと CI 環境：**

```python theme={null}
# Ensure consistent behavior in CI by excluding local settings
async for message in query(
    prompt="Run tests",
    options=ClaudeAgentOptions(
        setting_sources=["project"],  # Only team-shared settings
        permission_mode="bypassPermissions",
    ),
):
    print(message)
```

**SDK のみのアプリケーション：**

```python theme={null}
# Define everything programmatically.
# Pass [] to opt out of filesystem setting sources.
async for message in query(
    prompt="Review this PR",
    options=ClaudeAgentOptions(
        setting_sources=[],
        agents={...},
        mcp_servers={...},
        allowed_tools=["Read", "Grep", "Glob"],
    ),
):
    print(message)
```

**CLAUDE.md プロジェクト指示を読み込む：**

```python theme={null}
# Load project settings to include CLAUDE.md files
async for message in query(
    prompt="Add a new feature following project conventions",
    options=ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",  # Use Claude Code's system prompt
        },
        setting_sources=["project"],  # Loads CLAUDE.md from project
        allowed_tools=["Read", "Write", "Edit"],
    ),
):
    print(message)
```

<h4 id="settings-precedence">
  設定の優先順位
</h4>

複数のソースが読み込まれる場合、設定はこの優先順位（最高から最低）でマージされます：

1. ローカル設定（`.claude/settings.local.json`）
2. プロジェクト設定（`.claude/settings.json`）
3. ユーザー設定（`~/.claude/settings.json`）

`agents` と `allowed_tools` などのプログラム的なオプションは、ユーザー、プロジェクト、ローカルのファイルシステム設定をオーバーライドします。管理ポリシー設定はプログラム的なオプションより優先されます。

<h3 id="agentdefinition">
  `AgentDefinition`
</h3>

プログラムで定義されたサブエージェントの設定。

```python theme={null}
@dataclass
class AgentDefinition:
    description: str
    prompt: str
    tools: list[str] | None = None
    disallowedTools: list[str] | None = None
    model: str | None = None
    skills: list[str] | None = None
    memory: Literal["user", "project", "local"] | None = None
    mcpServers: list[str | dict[str, Any]] | None = None
    initialPrompt: str | None = None
    maxTurns: int | None = None
    background: bool | None = None
    effort: EffortLevel | int | None = None
    permissionMode: PermissionMode | None = None
```

| フィールド             | 必須  | 説明                                                                                                                                                  |
| :---------------- | :-- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| `description`     | はい  | このエージェントを使用する場合の自然言語説明                                                                                                                              |
| `prompt`          | はい  | エージェントのシステムプロンプト                                                                                                                                    |
| `tools`           | いいえ | 許可されたツール名の配列。省略した場合、すべてのツールを継承します                                                                                                                   |
| `disallowedTools` | いいえ | エージェントのツールセットから削除するツール名の配列。MCP サーバーレベルのパターンも受け入れられます：`mcp__server` または `mcp__server__*` はそのサーバーからすべてのツールを削除し、`mcp__*` はすべてのサーバーからすべての MCP ツールを削除します |
| `model`           | いいえ | このエージェントのモデルオーバーライド。`"sonnet"`、`"opus"`、`"haiku"`、`"inherit"` などのエイリアス、または完全なモデル ID を受け入れます。省略した場合、メインモデルを使用します                                     |
| `skills`          | いいえ | このエージェントが起動時にコンテキストにプリロードするスキル名のリスト。リストされていないスキルは Skill ツールを通じて呼び出し可能なままです                                                                          |
| `memory`          | いいえ | このエージェントのメモリソース：`"user"`、`"project"`、または `"local"`                                                                                                  |
| `mcpServers`      | いいえ | このエージェントが利用可能な MCP サーバー。各エントリはサーバー名またはインライン `{name: config}` dict です                                                                                |
| `initialPrompt`   | いいえ | このエージェントがメインスレッドエージェントとして実行される場合、最初のユーザーターンとして自動送信されます                                                                                              |
| `maxTurns`        | いいえ | エージェントが停止する前の最大 agentic ターン数                                                                                                                        |
| `background`      | いいえ | 呼び出されたときにこのエージェントをブロッキングされないバックグラウンドタスクとして実行します                                                                                                     |
| `effort`          | いいえ | このエージェントの推論努力レベル。名前付きレベルまたは整数を受け入れます。[`EffortLevel`](#effortlevel) を参照                                                                              |
| `permissionMode`  | いいえ | このエージェント内のツール実行のパーミッションモード。[`PermissionMode`](#permissionmode) を参照                                                                                  |

<Note>
  `AgentDefinition` フィールド名は `disallowedTools`、`permissionMode`、`maxTurns` などの camelCase を使用します。これらの名前は TypeScript SDK と共有される wire 形式に直接マップされます。これは `disallowed_tools` と `permission_mode` などの同等のトップレベルフィールドに Python snake\_case を使用する `ClaudeAgentOptions` とは異なります。`AgentDefinition` は dataclass であるため、snake\_case キーワードを渡すと構築時に `TypeError` が発生します。
</Note>

<h3 id="permissionmode">
  `PermissionMode`
</h3>

ツール実行を制御するためのパーミッションモード。

```python theme={null}
PermissionMode = Literal[
    "default",  # Standard permission behavior
    "acceptEdits",  # Auto-accept file edits
    "plan",  # Planning mode - explore without editing
    "dontAsk",  # Deny anything not pre-approved instead of prompting
    "bypassPermissions",  # Bypass permission checks; explicit ask rules still prompt (use with caution)
    "auto",  # A model classifier approves or denies each tool call
]
```

<h3 id="effortlevel">
  `EffortLevel`
</h3>

思考の深さを導くための努力レベル。

```python theme={null}
EffortLevel = Literal[
    "low",  # Minimal thinking, fastest responses
    "medium",  # Moderate thinking
    "high",  # Deep reasoning
    "xhigh",  # Extended reasoning; falls back to "high" on models that don't support it
    "max",  # Maximum effort
]
```

<h3 id="canusetool">
  `CanUseTool`
</h3>

ツールパーミッションコールバック関数の型エイリアス。

```python theme={null}
CanUseTool = Callable[
    [str, dict[str, Any], ToolPermissionContext], Awaitable[PermissionResult]
]
```

コールバックは以下を受け取ります：

* `tool_name`：呼び出されるツールの名前
* `input_data`：ツールの入力パラメータ
* `context`：追加情報を含む `ToolPermissionContext`

`PermissionResult`（`PermissionResultAllow` または `PermissionResultDeny`）を返します。

コールバックは対話的なパーミッションプロンプトの SDK 置き換えです：[パーミッション評価フロー](/docs/ja/agent-sdk/permissions#how-permissions-are-evaluated) がプロンプトに解決される場合にのみ呼び出されます。`allowed_tools` エントリ、設定許可ルール、または `acceptEdits` や `bypassPermissions` などのパーミッションモードによって事前承認されたツール呼び出しは呼び出されません。すべてのツール呼び出しをゲートするには、代わりに [`PreToolUse` hook](/docs/ja/agent-sdk/hooks) を使用してください。

`AskUserQuestion`、[`requiresUserInteraction`](/docs/ja/mcp#require-approval-for-a-specific-tool) とマークされた MCP ツール、および [組織が `ask` に設定したコネクタツール](/docs/ja/mcp#organization-controls-on-connector-tools) は、許可ルールが一致する場合でもコールバックに到達します。`dontAsk` モードではこれらの呼び出しは代わりに拒否され、コールバックを呼び出しません。

<h3 id="toolpermissioncontext">
  `ToolPermissionContext`
</h3>

ツールパーミッションコールバックに渡されるコンテキスト情報。

```python theme={null}
@dataclass
class ToolPermissionContext:
    signal: Any | None = None  # Future: abort signal support
    suggestions: list[PermissionUpdate] = field(default_factory=list)
    blocked_path: str | None = None
    decision_reason: str | None = None
    title: str | None = None
    display_name: str | None = None
    description: str | None = None
```

| フィールド             | 型                        | 説明                                                                                                                                                 |
| :---------------- | :----------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| `signal`          | `Any \| None`            | 将来の中止信号サポート用に予約済み                                                                                                                                  |
| `suggestions`     | `list[PermissionUpdate]` | CLI からのパーミッション更新提案。Bash プロンプトには `localSettings` 宛先の提案が含まれているため、`updated_permissions` で返すと、ルールを `.claude/settings.local.json` に書き込み、セッション全体で永続化します。 |
| `blocked_path`    | `str \| None`            | パーミッションリクエストをトリガーしたファイルパス（該当する場合）。例えば、Bash コマンドが許可されたディレクトリ外のパスにアクセスしようとした場合                                                                       |
| `decision_reason` | `str \| None`            | このパーミッションリクエストがトリガーされた理由。PreToolUse hook が `"ask"` を返したときに hook の `permissionDecisionReason` から転送されます                                              |
| `title`           | `str \| None`            | 完全なパーミッションプロンプト文。例えば、`Claude wants to read foo.txt`。存在する場合は、プライマリプロンプトテキストとして使用します                                                                 |
| `display_name`    | `str \| None`            | ツールアクション用の短い名詞句。例えば、`Read file`。ボタンラベルに適しています                                                                                                      |
| `description`     | `str \| None`            | パーミッション UI 用の人間が読める字幕                                                                                                                              |

<h3 id="permissionresult">
  `PermissionResult`
</h3>

パーミッションコールバック結果の Union 型。

```python theme={null}
PermissionResult = PermissionResultAllow | PermissionResultDeny
```

<h3 id="permissionresultallow">
  `PermissionResultAllow`
</h3>

ツール呼び出しを許可すべきことを示す結果。

```python theme={null}
@dataclass
class PermissionResultAllow:
    behavior: Literal["allow"] = "allow"
    updated_input: dict[str, Any] | None = None
    updated_permissions: list[PermissionUpdate] | None = None
```

| フィールド                 | 型                                | デフォルト     | 説明                 |
| :-------------------- | :------------------------------- | :-------- | :----------------- |
| `behavior`            | `Literal["allow"]`               | `"allow"` | "allow" である必要があります |
| `updated_input`       | `dict[str, Any] \| None`         | `None`    | 元の代わりに使用する変更された入力  |
| `updated_permissions` | `list[PermissionUpdate] \| None` | `None`    | 適用するパーミッション更新      |

<h3 id="permissionresultdeny">
  `PermissionResultDeny`
</h3>

ツール呼び出しを拒否すべきことを示す結果。

```python theme={null}
@dataclass
class PermissionResultDeny:
    behavior: Literal["deny"] = "deny"
    message: str = ""
    interrupt: bool = False
```

| フィールド       | 型                 | デフォルト    | 説明                    |
| :---------- | :---------------- | :------- | :-------------------- |
| `behavior`  | `Literal["deny"]` | `"deny"` | "deny" である必要があります     |
| `message`   | `str`             | `""`     | ツールが拒否された理由を説明するメッセージ |
| `interrupt` | `bool`            | `False`  | 現在の実行を割り込むかどうか        |

<h3 id="permissionupdate">
  `PermissionUpdate`
</h3>

プログラムでパーミッションを更新するための設定。

```python theme={null}
@dataclass
class PermissionUpdate:
    type: Literal[
        "addRules",
        "replaceRules",
        "removeRules",
        "setMode",
        "addDirectories",
        "removeDirectories",
    ]
    rules: list[PermissionRuleValue] | None = None
    behavior: Literal["allow", "deny", "ask"] | None = None
    mode: PermissionMode | None = None
    directories: list[str] | None = None
    destination: (
        Literal["userSettings", "projectSettings", "localSettings", "session"] | None
    ) = None
```

| フィールド         | 型                                         | 説明                    |
| :------------ | :---------------------------------------- | :-------------------- |
| `type`        | `Literal[...]`                            | パーミッション更新操作のタイプ       |
| `rules`       | `list[PermissionRuleValue] \| None`       | 追加/置換/削除操作用のルール       |
| `behavior`    | `Literal["allow", "deny", "ask"] \| None` | ルールベースの操作の動作          |
| `mode`        | `PermissionMode \| None`                  | setMode 操作のモード        |
| `directories` | `list[str] \| None`                       | ディレクトリ追加/削除操作用のディレクトリ |
| `destination` | `Literal[...] \| None`                    | パーミッション更新を適用する場所      |

<h3 id="permissionrulevalue">
  `PermissionRuleValue`
</h3>

パーミッション更新で追加、置換、または削除するルール。

```python theme={null}
@dataclass
class PermissionRuleValue:
    tool_name: str
    rule_content: str | None = None
```

<h3 id="toolspreset">
  `ToolsPreset`
</h3>

Claude Code のデフォルトツールセットを使用するためのプリセットツール設定。

```python theme={null}
class ToolsPreset(TypedDict):
    type: Literal["preset"]
    preset: Literal["claude_code"]
```

<h3 id="thinkingconfig">
  `ThinkingConfig`
</h3>

拡張思考動作を制御します。3 つの設定の Union：

```python theme={null}
ThinkingDisplay = Literal["summarized", "omitted"]


class ThinkingConfigAdaptive(TypedDict):
    type: Literal["adaptive"]
    display: NotRequired[ThinkingDisplay]


class ThinkingConfigEnabled(TypedDict):
    type: Literal["enabled"]
    budget_tokens: int
    display: NotRequired[ThinkingDisplay]


class ThinkingConfigDisabled(TypedDict):
    type: Literal["disabled"]


ThinkingConfig = ThinkingConfigAdaptive | ThinkingConfigEnabled | ThinkingConfigDisabled
```

| バリアント      | フィールド                            | 説明                          |
| :--------- | :------------------------------- | :-------------------------- |
| `adaptive` | `type`、`display`                 | Claude は適応的に思考するタイミングを決定します |
| `enabled`  | `type`、`budget_tokens`、`display` | 特定のトークン予算で思考を有効にします         |
| `disabled` | `type`                           | 思考を無効にします                   |

オプションの `display` フィールドは、思考テキストが `"summarized"` または `"omitted"` で返されるかどうかを制御します。Claude Opus 4.7 以降では、API デフォルトは `"omitted"` であるため、[`ThinkingBlock`](#thinkingblock) 出力で思考コンテンツを受け取るには `"summarized"` を設定します。

これらは `TypedDict` クラスであるため、実行時にはプレーンな dict です。dict リテラルとして構築するか、クラスをコンストラクタのように呼び出します。どちらも `dict` を生成します。`config["budget_tokens"]` でフィールドにアクセスし、`config.budget_tokens` ではなく：

```python theme={null}
from claude_agent_sdk import ClaudeAgentOptions, ThinkingConfigEnabled

# Option 1: dict literal (recommended, no import needed)
options = ClaudeAgentOptions(thinking={"type": "enabled", "budget_tokens": 20000})

# Option 2: constructor-style (returns a plain dict)
config = ThinkingConfigEnabled(type="enabled", budget_tokens=20000)
print(config["budget_tokens"])  # 20000
# config.budget_tokens would raise AttributeError
```

<h3 id="sdkbeta">
  `SdkBeta`
</h3>

SDK ベータ機能の Literal 型。

```python theme={null}
SdkBeta = Literal["context-1m-2025-08-07"]
```

`ClaudeAgentOptions` の `betas` フィールドで使用してベータ機能を有効にします。

<Warning>
  `context-1m-2025-08-07` ベータは 2026 年 4 月 30 日時点で廃止されました。このヘッダーを Claude Sonnet 4.5 または Sonnet 4 で渡すと効果がなく、標準の 200k トークンコンテキストウィンドウを超えるリクエストはエラーを返します。1M トークンコンテキストウィンドウを使用するには、[Claude Sonnet 5、Claude Sonnet 4.6、Claude Opus 4.6、Claude Opus 4.7、または Claude Opus 4.8](https://platform.claude.com/docs/en/about-claude/models/overview) に移行してください。これらには、ベータヘッダーなしで標準価格で 1M コンテキストが含まれます。
</Warning>

<h3 id="mcpsdkserverconfig">
  `McpSdkServerConfig`
</h3>

`create_sdk_mcp_server()` で作成された SDK MCP サーバーの設定。

```python theme={null}
class McpSdkServerConfig(TypedDict):
    type: Literal["sdk"]
    name: str
    instance: Any  # MCP Server instance
```

<h3 id="mcpserverconfig">
  `McpServerConfig`
</h3>

MCP サーバー設定の Union 型。

```python theme={null}
McpServerConfig = (
    McpStdioServerConfig | McpSSEServerConfig | McpHttpServerConfig | McpSdkServerConfig
)
```

<h4 id="mcpstdioserverconfig">
  `McpStdioServerConfig`
</h4>

```python theme={null}
class McpStdioServerConfig(TypedDict):
    type: NotRequired[Literal["stdio"]]  # Optional for backwards compatibility
    command: str
    args: NotRequired[list[str]]
    env: NotRequired[dict[str, str]]
```

<h4 id="mcpsseserverconfig">
  `McpSSEServerConfig`
</h4>

```python theme={null}
class McpSSEServerConfig(TypedDict):
    type: Literal["sse"]
    url: str
    headers: NotRequired[dict[str, str]]
```

<h4 id="mcphttpserverconfig">
  `McpHttpServerConfig`
</h4>

```python theme={null}
class McpHttpServerConfig(TypedDict):
    type: Literal["http"]
    url: str
    headers: NotRequired[dict[str, str]]
```

<h3 id="mcpserverstatusconfig">
  `McpServerStatusConfig`
</h3>

[`get_mcp_status()`](#methods) によって報告される MCP サーバーの設定。これは、すべての [`McpServerConfig`](#mcpserverconfig) トランスポートバリアント、および claude.ai を通じてプロキシされるサーバー用の出力のみの `claudeai-proxy` バリアントの Union です。

```python theme={null}
McpServerStatusConfig = (
    McpStdioServerConfig
    | McpSSEServerConfig
    | McpHttpServerConfig
    | McpSdkServerConfigStatus
    | McpClaudeAIProxyServerConfig
)
```

`McpSdkServerConfigStatus` は [`McpSdkServerConfig`](#mcpsdkserverconfig) のシリアライズ可能な形式で、`type`（`"sdk"`）と `name`（`str`）フィールドのみです。インプロセス `instance` は省略されます。`McpClaudeAIProxyServerConfig` には `type`（`"claudeai-proxy"`）、`url`（`str`）、`id`（`str`）フィールドがあります。

<h3 id="mcpstatusresponse">
  `McpStatusResponse`
</h3>

[`ClaudeSDKClient.get_mcp_status()`](#methods) からの応答。サーバーステータスのリストを `mcpServers` キーの下にラップします。

```python theme={null}
class McpStatusResponse(TypedDict):
    mcpServers: list[McpServerStatus]
```

<h3 id="mcpserverstatus">
  `McpServerStatus`
</h3>

接続された MCP サーバーのステータス。[`McpStatusResponse`](#mcpstatusresponse) に含まれます。

```python theme={null}
class McpServerStatus(TypedDict):
    name: str
    status: McpServerConnectionStatus  # "connected" | "failed" | "needs-auth" | "pending" | "disabled"
    serverInfo: NotRequired[McpServerInfo]
    error: NotRequired[str]
    config: NotRequired[McpServerStatusConfig]
    scope: NotRequired[str]
    tools: NotRequired[list[McpToolInfo]]
```

| フィールド        | 型                                                        | 説明                                                                                                                              |
| :----------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| `name`       | `str`                                                    | サーバー名                                                                                                                           |
| `status`     | `str`                                                    | `"connected"`、`"failed"`、`"needs-auth"`、`"pending"`、または `"disabled"` のいずれか                                                      |
| `serverInfo` | `dict`（オプション）                                            | サーバー名とバージョン（`{"name": str, "version": str}`）                                                                                    |
| `error`      | `str`（オプション）                                             | サーバーが接続に失敗した場合のエラーメッセージ                                                                                                         |
| `config`     | [`McpServerStatusConfig`](#mcpserverstatusconfig)（オプション） | サーバー設定。[`McpServerConfig`](#mcpserverconfig) と同じ形状（stdio、SSE、HTTP、または SDK）、および claude.ai を通じて接続されたサーバー用の `claudeai-proxy` バリアント |
| `scope`      | `str`（オプション）                                             | 設定スコープ                                                                                                                          |
| `tools`      | `list`（オプション）                                            | このサーバーが提供するツール。各ツールには `name`、`description`、`annotations` フィールドがあります                                                             |

<h3 id="sdkpluginconfig">
  `SdkPluginConfig`
</h3>

SDK でプラグインを読み込むための設定。

```python theme={null}
class SdkPluginConfig(TypedDict):
    type: Literal["local"]
    path: str
```

| フィールド  | 型                  | 説明                                      |
| :----- | :----------------- | :-------------------------------------- |
| `type` | `Literal["local"]` | `"local"` である必要があります（現在ローカルプラグインのみサポート） |
| `path` | `str`              | プラグインディレクトリへの絶対パスまたは相対パス                |

**例：**

```python theme={null}
plugins = [
    {"type": "local", "path": "./my-plugin"},
    {"type": "local", "path": "/absolute/path/to/plugin"},
]
```

プラグインの作成と使用に関する完全な情報については、[プラグイン](/docs/ja/agent-sdk/plugins) を参照してください。

<h2 id="message-types">
  メッセージ型
</h2>

<h3 id="message">
  `Message`
</h3>

すべての可能なメッセージの Union 型。

```python theme={null}
Message = (
    UserMessage
    | AssistantMessage
    | SystemMessage
    | ResultMessage
    | StreamEvent
    | RateLimitEvent
)
```

<h3 id="usermessage">
  `UserMessage`
</h3>

ユーザー入力メッセージ。

```python theme={null}
@dataclass
class UserMessage:
    content: str | list[ContentBlock]
    uuid: str | None = None
    parent_tool_use_id: str | None = None
    tool_use_result: dict[str, Any] | None = None
```

| フィールド                | 型                           | 説明                             |
| :------------------- | :-------------------------- | :----------------------------- |
| `content`            | `str \| list[ContentBlock]` | テキストまたはコンテンツブロックとしてのメッセージコンテンツ |
| `uuid`               | `str \| None`               | 一意のメッセージ識別子                    |
| `parent_tool_use_id` | `str \| None`               | このメッセージがツール結果応答の場合のツール使用 ID    |
| `tool_use_result`    | `dict[str, Any] \| None`    | 該当する場合のツール結果データ                |

<h3 id="assistantmessage">
  `AssistantMessage`
</h3>

コンテンツブロック付きのアシスタント応答メッセージ。

```python theme={null}
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
    parent_tool_use_id: str | None = None
    error: AssistantMessageError | None = None
    usage: dict[str, Any] | None = None
    message_id: str | None = None
```

| フィールド                | 型                                                            | 説明                                                              |
| :------------------- | :----------------------------------------------------------- | :-------------------------------------------------------------- |
| `content`            | `list[ContentBlock]`                                         | 応答内のコンテンツブロックのリスト                                               |
| `model`              | `str`                                                        | 応答を生成したモデル                                                      |
| `parent_tool_use_id` | `str \| None`                                                | これがネストされた応答の場合のツール使用 ID                                         |
| `error`              | [`AssistantMessageError`](#assistantmessageerror) ` \| None` | 応答がエラーに遭遇した場合のエラー型                                              |
| `usage`              | `dict[str, Any] \| None`                                     | メッセージごとのトークン使用状況（[`ResultMessage.usage`](#resultmessage) と同じキー） |
| `message_id`         | `str \| None`                                                | API メッセージ ID。1 つのターンからの複数のメッセージは同じ ID を共有します                    |

<h3 id="assistantmessageerror">
  `AssistantMessageError`
</h3>

アシスタントメッセージの可能なエラータイプ。

```python theme={null}
AssistantMessageError = Literal[
    "authentication_failed",
    "billing_error",
    "rate_limit",
    "invalid_request",
    "server_error",
    "max_output_tokens",
    "unknown",
]
```

<h3 id="systemmessage">
  `SystemMessage`
</h3>

メタデータ付きのシステムメッセージ。

```python theme={null}
@dataclass
class SystemMessage:
    subtype: str
    data: dict[str, Any]
```

<h3 id="resultmessage">
  `ResultMessage`
</h3>

コストと使用状況情報を含む最終結果メッセージ。

```python theme={null}
@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    stop_reason: str | None = None
    total_cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    result: str | None = None
    structured_output: Any = None
    model_usage: dict[str, Any] | None = None
    permission_denials: list[Any] | None = None
    deferred_tool_use: DeferredToolUse | None = None
    errors: list[str] | None = None
    api_error_status: int | None = None
    uuid: str | None = None
```

`subtype` フィールドは、他のどのフィールドが入力されるかを決定します。これは `"success"`、`"error_during_execution"`、`"error_max_turns"`、`"error_max_budget_usd"`、または `"error_max_structured_output_retries"` のいずれかです。Python データクラスはすべてのバリアントを 1 つの形状にフラット化するため、返された subtype に適用されないフィールドは `None` です。

会話がエラーで終了する場合、いくつかのフィールドは診断の詳細を含みます：

* `is_error`：会話がエラー状態で終了した場合は `True`。`error_*` サブタイプでは常に `True`。`subtype="success"` では、最終モデルリクエストが失敗した場合は `True`。つまり、エージェントループが完了しましたが、最後の API 呼び出しがエラーを返しました。
* `api_error_status`：終了する API エラーの HTTP ステータスコード。ターンがエラーなしで終了した場合は `None`。`subtype="success"` でのみ入力されます。
* `result`：`subtype="success"` での最終アシスタントメッセージのテキスト、または `error_*` サブタイプでは `None`。`subtype="success"` で `is_error=True` の場合、これは利用可能な場合は API エラー文字列を保持しますが、空の場合もあるため、`api_error_status` と前の `AssistantMessage` コンテンツで詳細を確認してください。
* `errors`：最大ターンメッセージなどのループレベルのエラー文字列。`error_*` サブタイプでのみ入力されます。

`usage` dict には、存在する場合、以下のキーが含まれます：

| キー                            | 型     | 説明                                                                                                                                                     |
| ----------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `input_tokens`                | `int` | トップレベルエージェントループで消費された入力トークン。[サブエージェントトークンは含まれません](/docs/ja/agent-sdk/cost-tracking#get-the-total-cost-of-a-query)。全体のアカウンティングについては `model_usage` を使用してください。 |
| `output_tokens`               | `int` | トップレベルエージェントループで生成された出力トークン。サブエージェントトークンは含まれません。                                                                                                       |
| `cache_creation_input_tokens` | `int` | 新しいキャッシュエントリを作成するために使用されたトークン。                                                                                                                         |
| `cache_read_input_tokens`     | `int` | 既存のキャッシュエントリから読み取られたトークン。                                                                                                                              |

`model_usage` dict はモデル名をモデルごとの使用状況にマップします。内部 dict キーは camelCase を使用します。これは、基になる CLI プロセスから変更されずに渡される値であり、TypeScript [`ModelUsage`](/docs/ja/agent-sdk/typescript#modelusage) 型と一致するためです：

| キー                         | 型       | 説明                                                                                            |
| -------------------------- | ------- | --------------------------------------------------------------------------------------------- |
| `inputTokens`              | `int`   | このモデルの入力トークン。                                                                                 |
| `outputTokens`             | `int`   | このモデルの出力トークン。                                                                                 |
| `cacheReadInputTokens`     | `int`   | このモデルのキャッシュ読み取りトークン。                                                                          |
| `cacheCreationInputTokens` | `int`   | このモデルのキャッシュ作成トークン。                                                                            |
| `webSearchRequests`        | `int`   | このモデルが行った Web 検索リクエスト。                                                                        |
| `costUSD`                  | `float` | このモデルの推定 USD コスト。クライアント側で計算されます。[コストと使用状況を追跡](/docs/ja/agent-sdk/cost-tracking) で請求の注意事項を参照してください。 |
| `contextWindow`            | `int`   | このモデルのコンテキストウィンドウサイズ。                                                                         |
| `maxOutputTokens`          | `int`   | このモデルの最大出力トークン制限。                                                                             |

<h3 id="streamevent">
  `StreamEvent`
</h3>

ストリーミング中の部分的なメッセージ更新のためのストリームイベント。`ClaudeAgentOptions` で `include_partial_messages=True` の場合のみ受け取られます。`from claude_agent_sdk.types import StreamEvent` でインポートしてください。

```python theme={null}
@dataclass
class StreamEvent:
    uuid: str
    session_id: str
    event: dict[str, Any]  # The raw Claude API stream event
    parent_tool_use_id: str | None = None
```

| フィールド                | 型                | 説明                                                                                                                    |
| :------------------- | :--------------- | :-------------------------------------------------------------------------------------------------------------------- |
| `uuid`               | `str`            | このイベントの一意の識別子                                                                                                         |
| `session_id`         | `str`            | セッション識別子                                                                                                              |
| `event`              | `dict[str, Any]` | 生の Claude API ストリームイベントデータ                                                                                            |
| `parent_tool_use_id` | `str \| None`    | 常に `None`。ストリームイベントはメインセッションのみに対して発行されます。サブエージェント属性については、[`AssistantMessage`](#assistantmessage) などの完全なメッセージを使用してください |

<h3 id="ratelimitevent">
  `RateLimitEvent`
</h3>

レート制限ステータスが変更されたときに発行されます（例：`"allowed"` から `"allowed_warning"` へ）。ユーザーにハード制限に達する前に警告するか、ステータスが `"rejected"` の場合にバックオフするために使用します。

```python theme={null}
@dataclass
class RateLimitEvent:
    rate_limit_info: RateLimitInfo
    uuid: str
    session_id: str
```

| フィールド             | 型                                 | 説明         |
| :---------------- | :-------------------------------- | :--------- |
| `rate_limit_info` | [`RateLimitInfo`](#ratelimitinfo) | 現在のレート制限状態 |
| `uuid`            | `str`                             | 一意のイベント識別子 |
| `session_id`      | `str`                             | セッション識別子   |

<h3 id="ratelimitinfo">
  `RateLimitInfo`
</h3>

[`RateLimitEvent`](#ratelimitevent) によって運ばれるレート制限状態。

```python theme={null}
RateLimitStatus = Literal["allowed", "allowed_warning", "rejected"]
RateLimitType = Literal[
    "five_hour", "seven_day", "seven_day_opus", "seven_day_sonnet", "overage"
]


@dataclass
class RateLimitInfo:
    status: RateLimitStatus
    resets_at: int | None = None
    rate_limit_type: RateLimitType | None = None
    utilization: float | None = None
    overage_status: RateLimitStatus | None = None
    overage_resets_at: int | None = None
    overage_disabled_reason: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
```

| フィールド                     | 型                         | 説明                                                                           |
| :------------------------ | :------------------------ | :--------------------------------------------------------------------------- |
| `status`                  | `RateLimitStatus`         | 現在のステータス。`"allowed_warning"` は制限に近づいていることを意味します。`"rejected"` は制限に達したことを意味します |
| `resets_at`               | `int \| None`             | レート制限ウィンドウがリセットされる Unix タイムスタンプ                                              |
| `rate_limit_type`         | `RateLimitType \| None`   | どのレート制限ウィンドウが適用されるか                                                          |
| `utilization`             | `float \| None`           | 消費されたレート制限の割合（0.0 から 1.0）                                                    |
| `overage_status`          | `RateLimitStatus \| None` | 該当する場合の従量課金超過使用のステータス                                                        |
| `overage_resets_at`       | `int \| None`             | 超過ウィンドウがリセットされる Unix タイムスタンプ                                                 |
| `overage_disabled_reason` | `str \| None`             | ステータスが `"rejected"` の場合、超過が利用できない理由                                          |
| `raw`                     | `dict[str, Any]`          | 上記でモデル化されていないフィールドを含む、CLI からの完全な生 dict                                       |

<h3 id="taskstartedmessage">
  `TaskStartedMessage`
</h3>

バックグラウンドタスクが開始されたときに発行されます。バックグラウンドタスクは、メインターンの外で追跡されるもの：バックグラウンド Bash コマンド、[Monitor](#monitor) ウォッチ、Agent ツール経由で生成されたサブエージェント、またはリモートエージェント。`task_type` フィールドはどれであるかを示します。このネーミングは `Task` から `Agent` ツールへの名前変更とは無関係です。

```python theme={null}
@dataclass
class TaskStartedMessage(SystemMessage):
    task_id: str
    description: str
    uuid: str
    session_id: str
    tool_use_id: str | None = None
    task_type: str | None = None
```

| フィールド         | 型             | 説明                                                                                                  |
| :------------ | :------------ | :-------------------------------------------------------------------------------------------------- |
| `task_id`     | `str`         | タスクの一意の識別子                                                                                          |
| `description` | `str`         | タスクの説明                                                                                              |
| `uuid`        | `str`         | 一意のメッセージ識別子                                                                                         |
| `session_id`  | `str`         | セッション識別子                                                                                            |
| `tool_use_id` | `str \| None` | 関連するツール使用 ID                                                                                        |
| `task_type`   | `str \| None` | バックグラウンドタスクの種類：バックグラウンド Bash と Monitor ウォッチの場合は `"local_bash"`、`"local_agent"`、または `"remote_agent"` |

<h3 id="taskusage">
  `TaskUsage`
</h3>

バックグラウンドタスクのトークンとタイミングデータ。

```python theme={null}
class TaskUsage(TypedDict):
    total_tokens: int
    tool_uses: int
    duration_ms: int
```

<h3 id="taskprogressmessage">
  `TaskProgressMessage`
</h3>

実行中のバックグラウンドタスクの進捗更新で定期的に発行されます。

```python theme={null}
@dataclass
class TaskProgressMessage(SystemMessage):
    task_id: str
    description: str
    usage: TaskUsage
    uuid: str
    session_id: str
    tool_use_id: str | None = None
    last_tool_name: str | None = None
```

| フィールド            | 型             | 説明                  |
| :--------------- | :------------ | :------------------ |
| `task_id`        | `str`         | タスクの一意の識別子          |
| `description`    | `str`         | 現在のステータス説明          |
| `usage`          | `TaskUsage`   | これまでのこのタスクのトークン使用状況 |
| `uuid`           | `str`         | 一意のメッセージ識別子         |
| `session_id`     | `str`         | セッション識別子            |
| `tool_use_id`    | `str \| None` | 関連するツール使用 ID        |
| `last_tool_name` | `str \| None` | タスクが最後に使用したツールの名前   |

<h3 id="tasknotificationmessage">
  `TaskNotificationMessage`
</h3>

バックグラウンドタスクが完了、失敗、または停止されたときに発行されます。バックグラウンドタスクには、`run_in_background` Bash コマンド、Monitor ウォッチ、バックグラウンドサブエージェントが含まれます。

```python theme={null}
@dataclass
class TaskNotificationMessage(SystemMessage):
    task_id: str
    status: TaskNotificationStatus  # "completed" | "failed" | "stopped"
    output_file: str
    summary: str
    uuid: str
    session_id: str
    tool_use_id: str | None = None
    usage: TaskUsage | None = None
```

| フィールド         | 型                        | 説明                                             |
| :------------ | :----------------------- | :--------------------------------------------- |
| `task_id`     | `str`                    | タスクの一意の識別子                                     |
| `status`      | `TaskNotificationStatus` | `"completed"`、`"failed"`、または `"stopped"` のいずれか |
| `output_file` | `str`                    | タスク出力ファイルへのパス                                  |
| `summary`     | `str`                    | タスク結果のサマリー                                     |
| `uuid`        | `str`                    | 一意のメッセージ識別子                                    |
| `session_id`  | `str`                    | セッション識別子                                       |
| `tool_use_id` | `str \| None`            | 関連するツール使用 ID                                   |
| `usage`       | `TaskUsage \| None`      | タスクの最終トークン使用状況                                 |

<h2 id="content-block-types">
  コンテンツブロック型
</h2>

<h3 id="contentblock">
  `ContentBlock`
</h3>

すべてのコンテンツブロックの Union 型。

```python theme={null}
ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock
```

<h3 id="textblock">
  `TextBlock`
</h3>

テキストコンテンツブロック。

```python theme={null}
@dataclass
class TextBlock:
    text: str
```

<h3 id="thinkingblock">
  `ThinkingBlock`
</h3>

思考コンテンツブロック（思考機能を持つモデル用）。

```python theme={null}
@dataclass
class ThinkingBlock:
    thinking: str
    signature: str
```

<h3 id="tooluseblock">
  `ToolUseBlock`
</h3>

ツール使用リクエストブロック。

```python theme={null}
@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
```

<h3 id="toolresultblock">
  `ToolResultBlock`
</h3>

ツール実行結果ブロック。

```python theme={null}
@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: str | list[dict[str, Any]] | None = None
    is_error: bool | None = None
```

<h2 id="error-types">
  エラー型
</h2>

<h3 id="claudesdkerror">
  `ClaudeSDKError`
</h3>

すべての SDK エラーの基本例外クラス。

```python theme={null}
class ClaudeSDKError(Exception):
    """Base error for Claude SDK."""
```

<h3 id="clinotfounderror">
  `CLINotFoundError`
</h3>

Claude Code CLI がインストールされていないか見つからない場合に発生します。

```python theme={null}
class CLINotFoundError(CLIConnectionError):
    def __init__(
        self, message: str = "Claude Code not found", cli_path: str | None = None
    ):
        """
        Args:
            message: Error message (default: "Claude Code not found")
            cli_path: Optional path to the CLI that was not found
        """
```

<h3 id="cliconnectionerror">
  `CLIConnectionError`
</h3>

Claude Code への接続に失敗した場合に発生します。

```python theme={null}
class CLIConnectionError(ClaudeSDKError):
    """Failed to connect to Claude Code."""
```

<h3 id="processerror">
  `ProcessError`
</h3>

Claude Code プロセスが失敗した場合に発生します。

```python theme={null}
class ProcessError(ClaudeSDKError):
    def __init__(
        self, message: str, exit_code: int | None = None, stderr: str | None = None
    ):
        self.exit_code = exit_code
        self.stderr = stderr
```

<h3 id="clijsondecodeerror">
  `CLIJSONDecodeError`
</h3>

JSON 解析に失敗した場合に発生します。

```python theme={null}
class CLIJSONDecodeError(ClaudeSDKError):
    def __init__(self, line: str, original_error: Exception):
        """
        Args:
            line: The line that failed to parse
            original_error: The original JSON decode exception
        """
        self.line = line
        self.original_error = original_error
```

<h2 id="hook-types">
  Hook 型
</h2>

hooks の使用に関する包括的なガイド、例、一般的なパターンについては、[Hooks ガイド](/docs/ja/agent-sdk/hooks) を参照してください。

<h3 id="hookevent">
  `HookEvent`
</h3>

サポートされている hook イベント型。

```python theme={null}
HookEvent = Literal[
    "PreToolUse",  # Called before tool execution
    "PostToolUse",  # Called after tool execution
    "PostToolUseFailure",  # Called when a tool execution fails
    "UserPromptSubmit",  # Called when user submits a prompt
    "Stop",  # Called when stopping execution
    "SubagentStop",  # Called when a subagent stops
    "PreCompact",  # Called before message compaction
    "Notification",  # Called for notification events
    "SubagentStart",  # Called when a subagent starts
    "PermissionRequest",  # Called when a permission decision is needed
]
```

<Note>
  TypeScript SDK は、Python ではまだ利用できない追加の hook イベントをサポートしています：`SessionStart`、`SessionEnd`、`Setup`、`TeammateIdle`、`TaskCompleted`、`ConfigChange`、`WorktreeCreate`、`WorktreeRemove`、`PostToolBatch`、および `MessageDisplay`。
</Note>

<h3 id="hookcallback">
  `HookCallback`
</h3>

hook コールバック関数の型定義。

```python theme={null}
HookCallback = Callable[[HookInput, str | None, HookContext], Awaitable[HookJSONOutput]]
```

パラメータ：

* `input`：`hook_event_name` に基づいた判別 Union を持つ強く型付けされた hook 入力（[`HookInput`](#hookinput) を参照）
* `tool_use_id`：オプションのツール使用識別子（ツール関連の hook 用）
* `context`：追加情報を含む hook コンテキスト

以下を含む可能性のある [`HookJSONOutput`](#hookjsonoutput) を返します：

* `decision`：アクションをブロックするには `"block"`
* `systemMessage`：ユーザーに表示される警告メッセージ
* `hookSpecificOutput`：hook 固有の出力データ

<h3 id="hookcontext">
  `HookContext`
</h3>

hook コールバックに渡されるコンテキスト情報。

```python theme={null}
class HookContext(TypedDict):
    signal: Any | None  # Future: abort signal support
```

<h3 id="hookmatcher">
  `HookMatcher`
</h3>

特定のイベントまたはツールに hook をマッチングするための設定。

```python theme={null}
@dataclass
class HookMatcher:
    matcher: str | None = (
        None  # Tool name or pattern to match (e.g., "Bash", "Write|Edit")
    )
    hooks: list[HookCallback] = field(
        default_factory=list
    )  # List of callbacks to execute
    timeout: float | None = (
        None  # Timeout in seconds for all hooks in this matcher (default: 60)
    )
```

<h3 id="hookinput">
  `HookInput`
</h3>

すべての hook 入力型の Union 型。実際の型は `hook_event_name` フィールドに依存します。

```python theme={null}
HookInput = (
    PreToolUseHookInput
    | PostToolUseHookInput
    | PostToolUseFailureHookInput
    | UserPromptSubmitHookInput
    | StopHookInput
    | SubagentStopHookInput
    | PreCompactHookInput
    | NotificationHookInput
    | SubagentStartHookInput
    | PermissionRequestHookInput
)
```

<h3 id="basehookinput">
  `BaseHookInput`
</h3>

すべての hook 入力型に存在する基本フィールド。

```python theme={null}
class BaseHookInput(TypedDict):
    session_id: str
    transcript_path: str
    cwd: str
    permission_mode: NotRequired[str]
```

| フィールド             | 型            | 説明                    |
| :---------------- | :----------- | :-------------------- |
| `session_id`      | `str`        | 現在のセッション識別子           |
| `transcript_path` | `str`        | セッショントランスクリプトファイルへのパス |
| `cwd`             | `str`        | 現在の作業ディレクトリ           |
| `permission_mode` | `str`（オプション） | 現在のパーミッションモード         |

<h3 id="pretoolusehookinput">
  `PreToolUseHookInput`
</h3>

`PreToolUse` hook イベントの入力データ。

```python theme={null}
class PreToolUseHookInput(BaseHookInput):
    hook_event_name: Literal["PreToolUse"]
    tool_name: str
    tool_input: dict[str, Any]
    tool_use_id: str
    agent_id: NotRequired[str]
    agent_type: NotRequired[str]
```

| フィールド             | 型                       | 説明                                    |
| :---------------- | :---------------------- | :------------------------------------ |
| `hook_event_name` | `Literal["PreToolUse"]` | 常に "PreToolUse"                       |
| `tool_name`       | `str`                   | 実行しようとしているツールの名前                      |
| `tool_input`      | `dict[str, Any]`        | ツールの入力パラメータ                           |
| `tool_use_id`     | `str`                   | このツール使用の一意の識別子                        |
| `agent_id`        | `str`（オプション）            | サブエージェント識別子。hook がサブエージェント内で発火する場合に存在 |
| `agent_type`      | `str`（オプション）            | サブエージェント型。hook がサブエージェント内で発火する場合に存在   |

<h3 id="posttoolusehookinput">
  `PostToolUseHookInput`
</h3>

`PostToolUse` hook イベントの入力データ。

```python theme={null}
class PostToolUseHookInput(BaseHookInput):
    hook_event_name: Literal["PostToolUse"]
    tool_name: str
    tool_input: dict[str, Any]
    tool_response: Any
    tool_use_id: str
    agent_id: NotRequired[str]
    agent_type: NotRequired[str]
```

| フィールド             | 型                        | 説明                                    |
| :---------------- | :----------------------- | :------------------------------------ |
| `hook_event_name` | `Literal["PostToolUse"]` | 常に "PostToolUse"                      |
| `tool_name`       | `str`                    | 実行されたツールの名前                           |
| `tool_input`      | `dict[str, Any]`         | 使用された入力パラメータ                          |
| `tool_response`   | `Any`                    | ツール実行からの応答                            |
| `tool_use_id`     | `str`                    | このツール使用の一意の識別子                        |
| `agent_id`        | `str`（オプション）             | サブエージェント識別子。hook がサブエージェント内で発火する場合に存在 |
| `agent_type`      | `str`（オプション）             | サブエージェント型。hook がサブエージェント内で発火する場合に存在   |

<h3 id="posttoolusefailurehookinput">
  `PostToolUseFailureHookInput`
</h3>

`PostToolUseFailure` hook イベントの入力データ。ツール実行が失敗したときに呼び出されます。

```python theme={null}
class PostToolUseFailureHookInput(BaseHookInput):
    hook_event_name: Literal["PostToolUseFailure"]
    tool_name: str
    tool_input: dict[str, Any]
    tool_use_id: str
    error: str
    is_interrupt: NotRequired[bool]
    agent_id: NotRequired[str]
    agent_type: NotRequired[str]
```

| フィールド             | 型                               | 説明                                    |
| :---------------- | :------------------------------ | :------------------------------------ |
| `hook_event_name` | `Literal["PostToolUseFailure"]` | 常に "PostToolUseFailure"               |
| `tool_name`       | `str`                           | 失敗したツールの名前                            |
| `tool_input`      | `dict[str, Any]`                | 使用された入力パラメータ                          |
| `tool_use_id`     | `str`                           | このツール使用の一意の識別子                        |
| `error`           | `str`                           | 失敗した実行からのエラーメッセージ                     |
| `is_interrupt`    | `bool`（オプション）                   | 失敗が割り込みによって引き起こされたかどうか                |
| `agent_id`        | `str`（オプション）                    | サブエージェント識別子。hook がサブエージェント内で発火する場合に存在 |
| `agent_type`      | `str`（オプション）                    | サブエージェント型。hook がサブエージェント内で発火する場合に存在   |

<h3 id="userpromptsubmithookinput">
  `UserPromptSubmitHookInput`
</h3>

`UserPromptSubmit` hook イベントの入力データ。

```python theme={null}
class UserPromptSubmitHookInput(BaseHookInput):
    hook_event_name: Literal["UserPromptSubmit"]
    prompt: str
```

| フィールド             | 型                             | 説明                    |
| :---------------- | :---------------------------- | :-------------------- |
| `hook_event_name` | `Literal["UserPromptSubmit"]` | 常に "UserPromptSubmit" |
| `prompt`          | `str`                         | ユーザーが送信したプロンプト        |

<h3 id="stophookinput">
  `StopHookInput`
</h3>

`Stop` hook イベントの入力データ。

```python theme={null}
class StopHookInput(BaseHookInput):
    hook_event_name: Literal["Stop"]
    stop_hook_active: bool
```

| フィールド              | 型                 | 説明                   |
| :----------------- | :---------------- | :------------------- |
| `hook_event_name`  | `Literal["Stop"]` | 常に "Stop"            |
| `stop_hook_active` | `bool`            | stop hook がアクティブかどうか |

<h3 id="subagentstophookinput">
  `SubagentStopHookInput`
</h3>

`SubagentStop` hook イベントの入力データ。

```python theme={null}
class SubagentStopHookInput(BaseHookInput):
    hook_event_name: Literal["SubagentStop"]
    stop_hook_active: bool
    agent_id: str
    agent_transcript_path: str
    agent_type: str
```

| フィールド                   | 型                         | 説明                        |
| :---------------------- | :------------------------ | :------------------------ |
| `hook_event_name`       | `Literal["SubagentStop"]` | 常に "SubagentStop"         |
| `stop_hook_active`      | `bool`                    | stop hook がアクティブかどうか      |
| `agent_id`              | `str`                     | サブエージェントの一意の識別子           |
| `agent_transcript_path` | `str`                     | サブエージェントのトランスクリプトファイルへのパス |
| `agent_type`            | `str`                     | サブエージェントの型                |

<h3 id="precompacthookinput">
  `PreCompactHookInput`
</h3>

`PreCompact` hook イベントの入力データ。

```python theme={null}
class PreCompactHookInput(BaseHookInput):
    hook_event_name: Literal["PreCompact"]
    trigger: Literal["manual", "auto"]
    custom_instructions: str | None
```

| フィールド                 | 型                           | 説明               |
| :-------------------- | :-------------------------- | :--------------- |
| `hook_event_name`     | `Literal["PreCompact"]`     | 常に "PreCompact"  |
| `trigger`             | `Literal["manual", "auto"]` | コンパクションをトリガーしたもの |
| `custom_instructions` | `str \| None`               | コンパクション用のカスタム指示  |

<h3 id="notificationhookinput">
  `NotificationHookInput`
</h3>

`Notification` hook イベントの入力データ。

```python theme={null}
class NotificationHookInput(BaseHookInput):
    hook_event_name: Literal["Notification"]
    message: str
    title: NotRequired[str]
    notification_type: str
```

| フィールド               | 型                         | 説明                |
| :------------------ | :------------------------ | :---------------- |
| `hook_event_name`   | `Literal["Notification"]` | 常に "Notification" |
| `message`           | `str`                     | 通知メッセージコンテンツ      |
| `title`             | `str`（オプション）              | 通知タイトル            |
| `notification_type` | `str`                     | 通知の型              |

<h3 id="subagentstarthookinput">
  `SubagentStartHookInput`
</h3>

`SubagentStart` hook イベントの入力データ。

```python theme={null}
class SubagentStartHookInput(BaseHookInput):
    hook_event_name: Literal["SubagentStart"]
    agent_id: str
    agent_type: str
```

| フィールド             | 型                          | 説明                 |
| :---------------- | :------------------------- | :----------------- |
| `hook_event_name` | `Literal["SubagentStart"]` | 常に "SubagentStart" |
| `agent_id`        | `str`                      | サブエージェントの一意の識別子    |
| `agent_type`      | `str`                      | サブエージェントの型         |

<h3 id="permissionrequesthookinput">
  `PermissionRequestHookInput`
</h3>

`PermissionRequest` hook イベントの入力データ。hooks がパーミッション決定をプログラムで処理できるようにします。

```python theme={null}
class PermissionRequestHookInput(BaseHookInput):
    hook_event_name: Literal["PermissionRequest"]
    tool_name: str
    tool_input: dict[str, Any]
    permission_suggestions: NotRequired[list[Any]]
    agent_id: NotRequired[str]
    agent_type: NotRequired[str]
```

| フィールド                    | 型                              | 説明                                    |
| :----------------------- | :----------------------------- | :------------------------------------ |
| `hook_event_name`        | `Literal["PermissionRequest"]` | 常に "PermissionRequest"                |
| `tool_name`              | `str`                          | パーミッションをリクエストするツールの名前                 |
| `tool_input`             | `dict[str, Any]`               | ツールの入力パラメータ                           |
| `permission_suggestions` | `list[Any]`（オプション）             | CLI からの提案されたパーミッション更新                 |
| `agent_id`               | `str`（オプション）                   | サブエージェント識別子。hook がサブエージェント内で発火する場合に存在 |
| `agent_type`             | `str`（オプション）                   | サブエージェント型。hook がサブエージェント内で発火する場合に存在   |

<h3 id="hookjsonoutput">
  `HookJSONOutput`
</h3>

hook コールバック戻り値の Union 型。

```python theme={null}
HookJSONOutput = AsyncHookJSONOutput | SyncHookJSONOutput
```

<h4 id="synchookjsonoutput">
  `SyncHookJSONOutput`
</h4>

制御フィールドと決定フィールドを持つ同期 hook 出力。

```python theme={null}
class SyncHookJSONOutput(TypedDict):
    # Control fields
    continue_: NotRequired[bool]  # Whether to proceed (default: True)
    suppressOutput: NotRequired[bool]  # Hide stdout from transcript
    stopReason: NotRequired[str]  # Message when continue is False

    # Decision fields
    decision: NotRequired[Literal["block"]]
    systemMessage: NotRequired[str]  # Warning message for user
    reason: NotRequired[str]  # Feedback for Claude

    # Hook-specific output
    hookSpecificOutput: NotRequired[HookSpecificOutput]
```

<Note>
  Python コードで `continue_`（アンダースコア付き）を使用してください。CLI に送信されるときに自動的に `continue` に変換されます。
</Note>

<h4 id="hookspecificoutput">
  `HookSpecificOutput`
</h4>

hook イベント名とイベント固有のフィールドを含む `TypedDict`。形状は `hookEventName` 値に依存します。hook イベントごとに利用可能なフィールドの詳細については、[hooks で実行を制御](/docs/ja/agent-sdk/hooks#outputs) を参照してください。

イベント固有の出力型の判別 union。`hookEventName` フィールドはどのフィールドが有効かを決定します。

```python theme={null}
class PreToolUseHookSpecificOutput(TypedDict):
    hookEventName: Literal["PreToolUse"]
    permissionDecision: NotRequired[Literal["allow", "deny", "ask", "defer"]]
    permissionDecisionReason: NotRequired[str]
    updatedInput: NotRequired[dict[str, Any]]
    additionalContext: NotRequired[str]


class PostToolUseHookSpecificOutput(TypedDict):
    hookEventName: Literal["PostToolUse"]
    additionalContext: NotRequired[str]
    updatedToolOutput: NotRequired[Any]
    updatedMCPToolOutput: NotRequired[Any]  # Deprecated: use updatedToolOutput, which works for all tools


class PostToolUseFailureHookSpecificOutput(TypedDict):
    hookEventName: Literal["PostToolUseFailure"]
    additionalContext: NotRequired[str]


class UserPromptSubmitHookSpecificOutput(TypedDict):
    hookEventName: Literal["UserPromptSubmit"]
    additionalContext: NotRequired[str]


class NotificationHookSpecificOutput(TypedDict):
    hookEventName: Literal["Notification"]
    additionalContext: NotRequired[str]


class SubagentStartHookSpecificOutput(TypedDict):
    hookEventName: Literal["SubagentStart"]
    additionalContext: NotRequired[str]


class PermissionRequestHookSpecificOutput(TypedDict):
    hookEventName: Literal["PermissionRequest"]
    decision: dict[str, Any]


HookSpecificOutput = (
    PreToolUseHookSpecificOutput
    | PostToolUseHookSpecificOutput
    | PostToolUseFailureHookSpecificOutput
    | UserPromptSubmitHookSpecificOutput
    | NotificationHookSpecificOutput
    | SubagentStartHookSpecificOutput
    | PermissionRequestHookSpecificOutput
)
```

<h4 id="asynchookjsonoutput">
  `AsyncHookJSONOutput`
</h4>

hook 実行を遅延させる非同期 hook 出力。

```python theme={null}
class AsyncHookJSONOutput(TypedDict):
    async_: Literal[True]  # Set to True to defer execution
    asyncTimeout: NotRequired[int]  # Timeout in milliseconds
```

<Note>
  Python コードで `async_`（アンダースコア付き）を使用してください。CLI に送信されるときに自動的に `async` に変換されます。
</Note>

<h3 id="hook-usage-example">
  Hook 使用例
</h3>

この例は 2 つの hook を登録します：1 つは `rm -rf /` のような危険な bash コマンドをブロックし、もう 1 つは監査のためにすべてのツール使用をログします。セキュリティ hook は `matcher` を介して Bash コマンドでのみ実行され、ログ hook はすべてのツールで実行されます。

```python theme={null}
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, HookContext
from typing import Any


async def validate_bash_command(
    input_data: dict[str, Any], tool_use_id: str | None, context: HookContext
) -> dict[str, Any]:
    """Validate and potentially block dangerous bash commands."""
    if input_data["tool_name"] == "Bash":
        command = input_data["tool_input"].get("command", "")
        if "rm -rf /" in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Dangerous command blocked",
                }
            }
    return {}


async def log_tool_use(
    input_data: dict[str, Any], tool_use_id: str | None, context: HookContext
) -> dict[str, Any]:
    """Log all tool usage for auditing."""
    print(f"Tool used: {input_data.get('tool_name')}")
    return {}


options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(
                matcher="Bash", hooks=[validate_bash_command], timeout=120
            ),  # 2 min for validation
            HookMatcher(
                hooks=[log_tool_use]
            ),  # Applies to all tools (default 60s timeout)
        ],
        "PostToolUse": [HookMatcher(hooks=[log_tool_use])],
    }
)

async for message in query(prompt="Analyze this codebase", options=options):
    print(message)
```

<h2 id="tool-input/output-types">
  ツール入出力型
</h2>

すべての組み込み Claude Code ツールの入出力スキーマのドキュメント。Python SDK はこれらを型としてエクスポートしませんが、メッセージ内のツール入出力の構造を表します。

<h3 id="agent">
  Agent
</h3>

**ツール名：** `Agent`（以前は `Task`。これはまだエイリアスとして受け入れられます）

**入力：**

```python theme={null}
{
    "description": str,  # タスクの短い説明（3～5 語）
    "prompt": str,  # エージェントが実行するタスク
    "subagent_type": str,  # 使用する特化したエージェントのタイプ
}
```

**出力：**

```python theme={null}
{
    "result": str,  # サブエージェントからの最終結果
    "usage": dict | None,  # トークン使用統計
    "total_cost_usd": float | None,  # 推定総コスト（USD）
    "duration_ms": int | None,  # 実行時間（ミリ秒）
}
```

<h3 id="askuserquestion">
  AskUserQuestion
</h3>

**ツール名：** `AskUserQuestion`

実行中にユーザーに明確化の質問をします。使用の詳細については [承認とユーザー入力を処理](/docs/ja/agent-sdk/user-input#handle-clarifying-questions) を参照してください。

**入力：**

```python theme={null}
{
    "questions": [  # ユーザーに質問する質問（1～4 個の質問）
        {
            "question": str,  # ユーザーに質問する完全な質問
            "header": str,  # チップ/タグとして表示される非常に短いラベル（最大 12 文字）
            "options": [  # 利用可能な選択肢（2～4 個のオプション）
                {
                    "label": str,  # このオプションの表示テキスト（1～5 語）
                    "description": str,  # このオプションが何を意味するかの説明
                }
            ],
            "multiSelect": bool,  # 複数選択を許可する場合は true に設定
        }
    ],
    "answers": dict[str, str | list[str]] | None,
    # パーミッションシステムによって入力されたユーザーの回答。マルチセレクト
    # 回答はラベルのリストまたはカンマ区切り文字列の場合があります
}
```

**出力：**

```python theme={null}
{
    "questions": [  # 質問された質問
        {
            "question": str,
            "header": str,
            "options": [{"label": str, "description": str}],
            "multiSelect": bool,
        }
    ],
    "answers": dict[str, str],  # 質問テキストを回答文字列にマップ
    # マルチセレクト回答はカンマ区切り
}
```

<h3 id="bash">
  Bash
</h3>

**ツール名：** `Bash`

**入力：**

```python theme={null}
{
    "command": str,  # 実行するコマンド
    "timeout": int | None,  # オプションのタイムアウト（ミリ秒、最大 600000。より高い値は最大値にクランプされます）
    "description": str | None,  # 明確で簡潔な説明（5～10 語）
    "run_in_background": bool | None,  # バックグラウンドで実行する場合は true に設定
}
```

**出力：**

```python theme={null}
{
    "output": str,  # 標準出力と標準エラーの結合出力
    "exitCode": int,  # コマンドの終了コード
    "killed": bool | None,  # タイムアウトによってコマンドが強制終了されたかどうか
    "shellId": str | None,  # バックグラウンドプロセスのシェル ID
}
```

<h3 id="monitor">
  Monitor
</h3>

**ツール名：** `Monitor`

バックグラウンドソースを実行し、各イベントを Claude に配信して、ポーリングなしで反応できるようにします。`command` はスクリプトを実行し、stdout 行ごとに 1 つのイベントを発行し、`ws` は WebSocket を開き、テキストフレームごとに 1 つのイベントを発行します。`command` または `ws` のいずれか 1 つを正確に指定してください。

Monitor がコマンドを実行する場合、Bash と同じパーミッションルールに従います。WebSocket ウォッチは別途承認を求めます。`ws` ソースには Claude Code v2.1.195 以降が必要です。動作とプロバイダーの可用性については、[Monitor ツールリファレンス](/docs/ja/tools-reference#monitor-tool) を参照してください。

**入力：**

```python theme={null}
{
    "command": str | None,  # シェルスクリプト。各 stdout 行はイベント、終了はウォッチを終了
    "ws": dict | None,  # WebSocket ソース：{"url": str, "protocols": list[str] | None}。各テキストフレームはイベント
    "description": str,  # 通知に表示される短い説明
    "timeout_ms": int | None,  # この期限後に強制終了（デフォルト 300000、最大 3600000）
    "persistent": bool | None,  # セッションの期間中実行。TaskStop で停止
}
```

**出力：**

```python theme={null}
{
    "taskId": str,  # バックグラウンド監視タスクの ID
    "timeoutMs": int,  # タイムアウト期限（ミリ秒）（persistent の場合は 0）
    "persistent": bool | None,  # TaskStop またはセッション終了まで実行する場合は True
}
```

<h3 id="edit">
  Edit
</h3>

**ツール名：** `Edit`

**入力：**

```python theme={null}
{
    "file_path": str,  # 変更するファイルの絶対パス
    "old_string": str,  # 置換するテキスト
    "new_string": str,  # 置換後のテキスト
    "replace_all": bool | None,  # すべての出現を置換（デフォルト False）
}
```

**出力：**

```python theme={null}
{
    "message": str,  # 確認メッセージ
    "replacements": int,  # 実行された置換の数
    "file_path": str,  # 編集されたファイルパス
}
```

<h3 id="read">
  Read
</h3>

**ツール名：** `Read`

**入力：**

```python theme={null}
{
    "file_path": str,  # 読み込むファイルの絶対パス
    "offset": int | None,  # 読み込みを開始する行番号
    "limit": int | None,  # 読み込む行数
}
```

**出力（テキストファイル）：**

```python theme={null}
{
    "content": str,  # 行番号付きのファイル内容
    "total_lines": int,  # ファイルの総行数
    "lines_returned": int,  # 実際に返された行数
}
```

**出力（画像）：**

```python theme={null}
{
    "image": str,  # Base64 エンコードされた画像データ
    "mime_type": str,  # 画像の MIME タイプ
    "file_size": int,  # ファイルサイズ（バイト）
}
```

<h3 id="write">
  Write
</h3>

**ツール名：** `Write`

**入力：**

```python theme={null}
{
    "file_path": str,  # 書き込むファイルの絶対パス
    "content": str,  # ファイルに書き込むコンテンツ
}
```

**出力：**

```python theme={null}
{
    "message": str,  # 成功メッセージ
    "bytes_written": int,  # 書き込まれたバイト数
    "file_path": str,  # 書き込まれたファイルパス
}
```

<h3 id="glob">
  Glob
</h3>

**ツール名：** `Glob`

**入力：**

```python theme={null}
{
    "pattern": str,  # ファイルにマッチさせるグロブパターン
    "path": str | None,  # 検索するディレクトリ（デフォルトは cwd）
}
```

**出力：**

```python theme={null}
{
    "matches": list[str],  # マッチしたファイルパスの配列
    "count": int,  # 見つかったマッチの数
    "search_path": str,  # 使用された検索ディレクトリ
}
```

<h3 id="grep">
  Grep
</h3>

**ツール名：** `Grep`

**入力：**

```python theme={null}
{
    "pattern": str,  # 正規表現パターン
    "path": str | None,  # 検索するファイルまたはディレクトリ
    "glob": str | None,  # ファイルをフィルタリングするグロブパターン
    "type": str | None,  # 検索するファイルタイプ
    "output_mode": str | None,  # 「content」、「files_with_matches」、または「count」
    "-i": bool | None,  # 大文字小文字を区別しない検索
    "-n": bool | None,  # 行番号を表示
    "-B": int | None,  # 各マッチの前に表示する行
    "-A": int | None,  # 各マッチの後に表示する行
    "-C": int | None,  # 前後に表示する行
    "head_limit": int | None,  # 出力を最初の N 行/エントリに制限
    "multiline": bool | None,  # マルチラインモードを有効化
}
```

**出力（content モード）：**

```python theme={null}
{
    "matches": [
        {
            "file": str,
            "line_number": int | None,
            "line": str,
            "before_context": list[str] | None,
            "after_context": list[str] | None,
        }
    ],
    "total_matches": int,
}
```

**出力（files\_with\_matches モード）：**

```python theme={null}
{
    "files": list[str],  # マッチを含むファイル
    "count": int,  # マッチを含むファイルの数
}
```

<h3 id="notebookedit">
  NotebookEdit
</h3>

**ツール名：** `NotebookEdit`

**入力：**

```python theme={null}
{
    "notebook_path": str,  # Jupyter ノートブックの絶対パス
    "cell_id": str | None,  # 編集するセルの ID
    "new_source": str,  # セルの新しいソース
    "cell_type": "code" | "markdown" | None,  # セルのタイプ
    "edit_mode": "replace" | "insert" | "delete" | None,  # 編集操作のタイプ
}
```

**出力：**

```python theme={null}
{
    "message": str,  # 成功メッセージ
    "edit_type": "replaced" | "inserted" | "deleted",  # 実行された編集のタイプ
    "cell_id": str | None,  # 影響を受けたセル ID
    "total_cells": int,  # 編集後のノートブックの総セル数
}
```

<h3 id="webfetch">
  WebFetch
</h3>

**ツール名：** `WebFetch`

**入力：**

```python theme={null}
{
    "url": str,  # コンテンツを取得する URL
    "prompt": str,  # 取得したコンテンツで実行するプロンプト
}
```

**出力：**

```python theme={null}
{
    "bytes": int,  # 取得したコンテンツのサイズ（バイト）
    "code": int,  # HTTP レスポンスコード
    "codeText": str,  # HTTP レスポンスコードテキスト
    "result": str,  # コンテンツにプロンプトを適用した処理結果
    "durationMs": int,  # コンテンツを取得して処理するのにかかった時間（ミリ秒）
    "url": str,  # 取得された URL
}
```

<h3 id="websearch">
  WebSearch
</h3>

**ツール名：** `WebSearch`

**入力：**

```python theme={null}
{
    "query": str,  # 使用する検索クエリ
    "allowed_domains": list[str] | None,  # これらのドメインからのみ結果を含める
    "blocked_domains": list[str] | None,  # これらのドメインからの結果は決して含めない
}
```

**出力：**

```python theme={null}
{
    "query": str,  # 検索クエリ
    "results": list[str | {"tool_use_id": str, "content": list[{"title": str, "url": str}]}],
    "durationSeconds": float,  # 検索時間（秒）
}
```

<h3 id="todowrite">
  TodoWrite
</h3>

**ツール名：** `TodoWrite`

<Note>
  Claude Code v2.1.142 以降、`TodoWrite` はデフォルトで無効になっています。代わりに `TaskCreate`、`TaskGet`、`TaskUpdate`、および `TaskList` を使用してください。[Task ツールへの移行](/docs/ja/agent-sdk/todo-tracking#migrate-to-task-tools) を参照して監視コードを更新するか、`CLAUDE_CODE_ENABLE_TASKS=0` を設定して `TodoWrite` に戻してください。
</Note>

**入力：**

```python theme={null}
{
    "todos": [
        {
            "content": str,  # タスクの説明
            "status": "pending" | "in_progress" | "completed",  # タスクのステータス
            "activeForm": str,  # 説明のアクティブな形式
        }
    ]
}
```

**出力：**

```python theme={null}
{
    "message": str,  # 成功メッセージ
    "stats": {"total": int, "pending": int, "in_progress": int, "completed": int},
}
```

<h3 id="taskcreate">
  TaskCreate
</h3>

**ツール名：** `TaskCreate`

**入力：**

```python theme={null}
{
    "subject": str,  # 短いタスクタイトル
    "description": str,  # 詳細なタスク本文
    "activeForm": str | None,  # 進行中に表示される現在形ラベル
    "metadata": dict | None,  # 任意の呼び出し元メタデータ
}
```

**出力：**

```python theme={null}
{
    "task": {"id": str, "subject": str},  # 割り当てられた ID を持つ作成されたタスク
}
```

<h3 id="taskupdate">
  TaskUpdate
</h3>

**ツール名：** `TaskUpdate`

**入力：**

```python theme={null}
{
    "taskId": str,  # パッチするタスクの ID
    "status": Literal["pending", "in_progress", "completed", "deleted"] | None,
    "subject": str | None,
    "description": str | None,
    "activeForm": str | None,
    "addBlocks": list[str] | None,  # このタスクが現在ブロックするタスク ID
    "addBlockedBy": list[str] | None,  # 現在このタスクをブロックするタスク ID
    "owner": str | None,
    "metadata": dict | None,
}
```

**出力：**

```python theme={null}
{
    "success": bool,
    "taskId": str,
    "updatedFields": list[str],  # 変更されたフィールドの名前
    "error": str | None,
    "statusChange": {"from": str, "to": str} | None,
}
```

<h3 id="taskget">
  TaskGet
</h3>

**ツール名：** `TaskGet`

**入力：**

```python theme={null}
{
    "taskId": str,  # 読み込むタスクの ID
}
```

**出力：**

```python theme={null}
{
    "task": {
        "id": str,
        "subject": str,
        "description": str,
        "status": Literal["pending", "in_progress", "completed"],
        "blocks": list[str],
        "blockedBy": list[str],
    } | None,  # ID が見つからない場合は None
}
```

<h3 id="tasklist">
  TaskList
</h3>

**ツール名：** `TaskList`

**入力：**

```python theme={null}
{}
```

**出力：**

```python theme={null}
{
    "tasks": [
        {
            "id": str,
            "subject": str,
            "status": Literal["pending", "in_progress", "completed"],
            "owner": str | None,
            "blockedBy": list[str],
        }
    ],
}
```

<h3 id="bashoutput">
  BashOutput
</h3>

**ツール名：** `BashOutput`

**入力：**

```python theme={null}
{
    "bash_id": str,  # バックグラウンドシェルの ID
    "filter": str | None,  # 出力行をフィルタリングするオプションの正規表現
}
```

**出力：**

```python theme={null}
{
    "output": str,  # 最後のチェック以降の新しい出力
    "status": "running" | "completed" | "failed",  # 現在のシェルステータス
    "exitCode": int | None,  # 完了時の終了コード
}
```

<h3 id="killbash">
  KillBash
</h3>

**ツール名：** `KillBash`

**入力：**

```python theme={null}
{
    "shell_id": str  # 強制終了するバックグラウンドシェルの ID
}
```

**出力：**

```python theme={null}
{
    "message": str,  # 成功メッセージ
    "shell_id": str,  # 強制終了されたシェルの ID
}
```

<h3 id="exitplanmode">
  ExitPlanMode
</h3>

**ツール名：** `ExitPlanMode`

**入力：**

```python theme={null}
{
    "plan": str  # ユーザーが承認するために実行するプラン
}
```

**出力：**

```python theme={null}
{
    "message": str,  # 確認メッセージ
    "approved": bool | None,  # ユーザーがプランを承認したかどうか
}
```

<h3 id="listmcpresources">
  ListMcpResources
</h3>

**ツール名：** `ListMcpResourcesTool`

**入力：**

```python theme={null}
{
    "server": str | None  # リソースをフィルタリングするオプションのサーバー名
}
```

**出力：**

```python theme={null}
{
    "resources": [
        {
            "uri": str,
            "name": str,
            "description": str | None,
            "mimeType": str | None,
            "server": str,
        }
    ],
    "total": int,
}
```

<h3 id="readmcpresource">
  ReadMcpResource
</h3>

**ツール名：** `ReadMcpResourceTool`

**入力：**

```python theme={null}
{
    "server": str,  # MCP サーバー名
    "uri": str,  # 読み込むリソース URI
}
```

**出力：**

```python theme={null}
{
    "contents": [
        {"uri": str, "mimeType": str | None, "text": str | None, "blob": str | None}
    ],
    "server": str,
}
```

<h2 id="advanced-features-with-claudesdkclient">
  ClaudeSDKClient を使用した高度な機能
</h2>

<h3 id="building-a-continuous-conversation-interface">
  継続的な会話インターフェースの構築
</h3>

```python theme={null}
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)
import asyncio


class ConversationSession:
    """Maintains a single conversation session with Claude."""

    def __init__(self, options: ClaudeAgentOptions | None = None):
        self.client = ClaudeSDKClient(options)
        self.turn_count = 0

    async def start(self):
        await self.client.connect()
        print("Starting conversation session. Claude will remember context.")
        print(
            "Commands: 'exit' to quit, 'interrupt' to stop current task, 'new' for new session"
        )

        while True:
            user_input = input(f"\n[Turn {self.turn_count + 1}] You: ")

            if user_input.lower() == "exit":
                break
            elif user_input.lower() == "interrupt":
                await self.client.interrupt()
                print("Task interrupted!")
                continue
            elif user_input.lower() == "new":
                # Disconnect and reconnect for a fresh session
                await self.client.disconnect()
                await self.client.connect()
                self.turn_count = 0
                print("Started new conversation session (previous context cleared)")
                continue

            # Send message - the session retains all previous messages
            await self.client.query(user_input)
            self.turn_count += 1

            # Process response
            print(f"[Turn {self.turn_count}] Claude: ", end="")
            async for message in self.client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text, end="")
            print()  # New line after response

        await self.client.disconnect()
        print(f"Conversation ended after {self.turn_count} turns.")


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"], permission_mode="acceptEdits"
    )
    session = ConversationSession(options)
    await session.start()


# Example conversation:
# Turn 1 - You: "Create a file called hello.py"
# Turn 1 - Claude: "I'll create a hello.py file for you..."
# Turn 2 - You: "What's in that file?"
# Turn 2 - Claude: "The hello.py file I just created contains..." (remembers!)
# Turn 3 - You: "Add a main function to it"
# Turn 3 - Claude: "I'll add a main function to hello.py..." (knows which file!)

asyncio.run(main())
```

<h3 id="using-hooks-for-behavior-modification">
  動作修正のための hooks の使用
</h3>

```python theme={null}
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext,
)
import asyncio
from typing import Any


async def pre_tool_logger(
    input_data: dict[str, Any], tool_use_id: str | None, context: HookContext
) -> dict[str, Any]:
    """Log all tool usage before execution."""
    tool_name = input_data.get("tool_name", "unknown")
    print(f"[PRE-TOOL] About to use: {tool_name}")

    # You can modify or block the tool execution here
    if tool_name == "Bash" and "rm -rf" in str(input_data.get("tool_input", {})):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Dangerous command blocked",
            }
        }
    return {}


async def post_tool_logger(
    input_data: dict[str, Any], tool_use_id: str | None, context: HookContext
) -> dict[str, Any]:
    """Log results after tool execution."""
    tool_name = input_data.get("tool_name", "unknown")
    print(f"[POST-TOOL] Completed: {tool_name}")
    return {}


async def user_prompt_modifier(
    input_data: dict[str, Any], tool_use_id: str | None, context: HookContext
) -> dict[str, Any]:
    """Add context to user prompts."""
    original_prompt = input_data.get("prompt", "")

    # Add a timestamp as additional context for Claude to see
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"[Submitted at {timestamp}] Original prompt: {original_prompt}",
        }
    }


async def main():
    options = ClaudeAgentOptions(
        hooks={
            "PreToolUse": [
                HookMatcher(hooks=[pre_tool_logger]),
                HookMatcher(matcher="Bash", hooks=[pre_tool_logger]),
            ],
            "PostToolUse": [HookMatcher(hooks=[post_tool_logger])],
            "UserPromptSubmit": [HookMatcher(hooks=[user_prompt_modifier])],
        },
        allowed_tools=["Read", "Write", "Bash"],
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("List files in current directory")

        async for message in client.receive_response():
            # Hooks will automatically log tool usage
            pass


asyncio.run(main())
```

<h3 id="real-time-progress-monitoring">
  リアルタイム進捗監視
</h3>

```python theme={null}
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ToolUseBlock,
    ToolResultBlock,
    TextBlock,
)
import asyncio


async def monitor_progress():
    options = ClaudeAgentOptions(
        allowed_tools=["Write", "Bash"], permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Create 5 Python files with different sorting algorithms")

        # Monitor progress in real-time
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        if block.name == "Write":
                            file_path = block.input.get("file_path", "")
                            print(f"Creating: {file_path}")
                    elif isinstance(block, ToolResultBlock):
                        print("Completed tool execution")
                    elif isinstance(block, TextBlock):
                        print(f"Claude says: {block.text[:100]}...")

        print("Task completed!")


asyncio.run(monitor_progress())
```

<h2 id="example-usage">
  使用例
</h2>

<h3 id="basic-file-operations-using-query">
  基本的なファイル操作（query を使用）
</h3>

```python theme={null}
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock
import asyncio


async def create_project():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits",
        cwd="/home/user/project",
    )

    async for message in query(
        prompt="Create a Python project structure with setup.py", options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Using tool: {block.name}")


asyncio.run(create_project())
```

<h3 id="error-handling">
  エラー処理
</h3>

```python theme={null}
from claude_agent_sdk import query, CLINotFoundError, ProcessError, CLIJSONDecodeError

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLINotFoundError:
    print(
        "Claude Code CLI not found. Try reinstalling: pip install --force-reinstall claude-agent-sdk"
    )
except ProcessError as e:
    print(f"Process failed with exit code: {e.exit_code}")
except CLIJSONDecodeError as e:
    print(f"Failed to parse response: {e}")
```

<h3 id="streaming-mode-with-client">
  クライアントでのストリーミングモード
</h3>

```python theme={null}
from claude_agent_sdk import ClaudeSDKClient
import asyncio


async def interactive_session():
    async with ClaudeSDKClient() as client:
        # Send initial message
        await client.query("What's the weather like?")

        # Process responses
        async for msg in client.receive_response():
            print(msg)

        # Send follow-up
        await client.query("Tell me more about that")

        # Process follow-up response
        async for msg in client.receive_response():
            print(msg)


asyncio.run(interactive_session())
```

<h3 id="using-custom-tools-with-claudesdkclient">
  ClaudeSDKClient でカスタムツールを使用する
</h3>

```python theme={null}
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
)
import asyncio
from typing import Any


# Define custom tools with @tool decorator
@tool("calculate", "Perform mathematical calculations", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    try:
        result = eval(args["expression"], {"__builtins__": {}})
        return {"content": [{"type": "text", "text": f"Result: {result}"}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "is_error": True,
        }


@tool("get_time", "Get current time", {})
async def get_time(args: dict[str, Any]) -> dict[str, Any]:
    from datetime import datetime

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"content": [{"type": "text", "text": f"Current time: {current_time}"}]}


async def main():
    # Create SDK MCP server with custom tools
    my_server = create_sdk_mcp_server(
        name="utilities", version="1.0.0", tools=[calculate, get_time]
    )

    # Configure options with the server
    options = ClaudeAgentOptions(
        mcp_servers={"utils": my_server},
        allowed_tools=["mcp__utils__calculate", "mcp__utils__get_time"],
    )

    # Use ClaudeSDKClient for interactive tool usage
    async with ClaudeSDKClient(options=options) as client:
        await client.query("What's 123 * 456?")

        # Process calculation response
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Calculation: {block.text}")

        # Follow up with time query
        await client.query("What time is it now?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Time: {block.text}")


asyncio.run(main())
```

<h2 id="sandbox-configuration">
  サンドボックス設定
</h2>

<h3 id="sandboxsettings">
  `SandboxSettings`
</h3>

サンドボックス動作の設定。これを使用してコマンドサンドボックスを有効にし、ネットワーク制限をプログラムで設定します。

```python theme={null}
class SandboxSettings(TypedDict, total=False):
    enabled: bool
    autoAllowBashIfSandboxed: bool
    excludedCommands: list[str]
    allowUnsandboxedCommands: bool
    network: SandboxNetworkConfig
    ignoreViolations: SandboxIgnoreViolations
    enableWeakerNestedSandbox: bool
```

| プロパティ                       | 型                                                     | デフォルト   | 説明                                                                                                                                                                          |
| :-------------------------- | :---------------------------------------------------- | :------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `enabled`                   | `bool`                                                | `False` | コマンド実行のサンドボックスモードを有効にします                                                                                                                                                    |
| `autoAllowBashIfSandboxed`  | `bool`                                                | `True`  | サンドボックスが有効な場合、bash コマンドを自動承認します                                                                                                                                             |
| `excludedCommands`          | `list[str]`                                           | `[]`    | 常にサンドボックス制限をバイパスするコマンド（例：`["docker"]`）。これらはモデルの関与なしに自動的にサンドボックスなしで実行されます                                                                                                    |
| `allowUnsandboxedCommands`  | `bool`                                                | `True`  | モデルがサンドボックスの外でコマンドを実行するようにリクエストすることを許可します。`True` の場合、モデルはツール入力で `dangerouslyDisableSandbox` を設定でき、[パーミッションシステム](#permissions-fallback-for-unsandboxed-commands) にフォールバックします |
| `network`                   | [`SandboxNetworkConfig`](#sandboxnetworkconfig)       | `None`  | ネットワーク固有のサンドボックス設定                                                                                                                                                          |
| `ignoreViolations`          | [`SandboxIgnoreViolations`](#sandboxignoreviolations) | `None`  | 無視するサンドボックス違反を設定します                                                                                                                                                         |
| `enableWeakerNestedSandbox` | `bool`                                                | `False` | 互換性のためにより弱いネストされたサンドボックスを有効にします                                                                                                                                             |

<Note>
  サンドボックスはプラットフォームサポートに依存し、Linux では `bubblewrap` や `socat` などのツールが必要です。デフォルトでは、`enabled` が `True` でもサンドボックスが起動できない場合、コマンドはサンドボックスなしで実行され、stderr に警告が表示されます。このデフォルト動作は TypeScript SDK とは異なり、TypeScript SDK では `failIfUnavailable` がデフォルトで `true` です。

  サンドボックス設定で `"failIfUnavailable": True` を設定して、代わりに停止するようにしてください。このキーはまだ `SandboxSettings` で宣言されていませんが、SDK は Claude Code に転送し、Claude Code がこれを尊重します。その後、`query()` は `subtype="error_during_execution"` の `ResultMessage` を報告し、理由は `errors` に含まれます。`query()` がメッセージを生成する前に例外を発生させることを期待するのではなく、そのサブタイプを監視してください。
</Note>

<h4 id="example-usage-2">
  使用例
</h4>

```python theme={null}
from claude_agent_sdk import query, ClaudeAgentOptions, SandboxSettings

sandbox_settings: SandboxSettings = {
    "enabled": True,
    "autoAllowBashIfSandboxed": True,
    "network": {"allowLocalBinding": True},
}

async for message in query(
    prompt="Build and test my project",
    options=ClaudeAgentOptions(sandbox=sandbox_settings),
):
    print(message)
```

<Warning>
  **Unix ソケットセキュリティ**：`allowUnixSockets` オプションは強力なシステムサービスへのアクセスを許可できます。例えば、`/var/run/docker.sock` を許可すると、Docker API を通じてホストシステムへの完全なアクセスが効果的に許可され、サンドボックス分離がバイパスされます。厳密に必要な Unix ソケットのみを許可し、各ソケットのセキュリティへの影響を理解してください。
</Warning>

<h3 id="sandboxnetworkconfig">
  `SandboxNetworkConfig`
</h3>

サンドボックスモード用のネットワーク固有の設定。これらの設定は、親の [`SandboxSettings`](#sandboxsettings) で `enabled` が `True` の場合、サンドボックス化された Bash コマンドに適用されます。WebFetch ツールには適用されず、WebFetch ツールは代わりに [パーミッションルール](/docs/ja/permissions#webfetch) を使用します。

```python theme={null}
class SandboxNetworkConfig(TypedDict, total=False):
    allowedDomains: list[str]
    deniedDomains: list[str]
    allowManagedDomainsOnly: bool
    allowUnixSockets: list[str]
    allowAllUnixSockets: bool
    allowLocalBinding: bool
    allowMachLookup: list[str]
    httpProxyPort: int
    socksProxyPort: int
```

| プロパティ                     | 型           | デフォルト   | 説明                                                                                            |
| :------------------------ | :---------- | :------ | :-------------------------------------------------------------------------------------------- |
| `allowedDomains`          | `list[str]` | `[]`    | サンドボックス化されたプロセスがアクセスできるドメイン名                                                                  |
| `deniedDomains`           | `list[str]` | `[]`    | サンドボックス化されたプロセスがアクセスできないドメイン名。`allowedDomains` より優先されます                                       |
| `allowManagedDomainsOnly` | `bool`      | `False` | マネージド設定のみ：マネージド設定で設定されている場合、非マネージド設定ソースからの `allowedDomains` を無視します。SDK オプションで設定された場合は効果がありません |
| `allowUnixSockets`        | `list[str]` | `[]`    | プロセスがアクセスできる Unix ソケットパス（例：Docker ソケット）                                                       |
| `allowAllUnixSockets`     | `bool`      | `False` | すべての Unix ソケットへのアクセスを許可します                                                                    |
| `allowLocalBinding`       | `bool`      | `False` | プロセスがローカルポートにバインドすることを許可します（例：dev サーバー用）                                                      |
| `allowMachLookup`         | `list[str]` | `[]`    | macOS のみ：許可する XPC/Mach サービス名。末尾のワイルドカードをサポートします                                               |
| `httpProxyPort`           | `int`       | `None`  | ネットワークリクエスト用の HTTP プロキシポート                                                                    |
| `socksProxyPort`          | `int`       | `None`  | ネットワークリクエスト用の SOCKS プロキシポート                                                                   |

<Note>
  組み込みサンドボックスプロキシは、リクエストされたホスト名に基づいてネットワーク許可リストを強制し、TLS トラフィックを終了または検査しないため、[ドメインフロンティング](https://en.wikipedia.org/wiki/Domain_fronting) などの技術がそれをバイパスする可能性があります。詳細は [サンドボックスセキュリティの制限事項](/docs/ja/sandboxing#security-limitations) を参照し、TLS 終了プロキシの設定については [セキュアなデプロイ](/docs/ja/agent-sdk/secure-deployment#traffic-forwarding) を参照してください。
</Note>

<h3 id="sandboxignoreviolations">
  `SandboxIgnoreViolations`
</h3>

特定のサンドボックス違反を無視するための設定。

```python theme={null}
class SandboxIgnoreViolations(TypedDict, total=False):
    file: list[str]
    network: list[str]
```

| プロパティ     | 型           | デフォルト | 説明                |
| :-------- | :---------- | :---- | :---------------- |
| `file`    | `list[str]` | `[]`  | 違反を無視するファイルパスパターン |
| `network` | `list[str]` | `[]`  | 違反を無視するネットワークパターン |

<h3 id="permissions-fallback-for-unsandboxed-commands">
  サンドボックスなしコマンドのパーミッションフォールバック
</h3>

`allowUnsandboxedCommands` が有効な場合、モデルはツール入力で `dangerouslyDisableSandbox: True` を設定することでサンドボックスの外でコマンドを実行するようにリクエストできます。これらのリクエストは既存のパーミッションシステムにフォールバックします。つまり、`can_use_tool` ハンドラーが呼び出され、カスタム認可ロジックを実装できます。

<Note>
  **`excludedCommands` vs `allowUnsandboxedCommands`：**

  * `excludedCommands`：常にサンドボックスを自動的にバイパスするコマンドの静的リスト（例：`["docker"]`）。モデルはこれを制御できません。
  * `allowUnsandboxedCommands`：モデルが実行時にツール入力で `dangerouslyDisableSandbox: True` を設定することでサンドボックスなし実行をリクエストすることを許可します。
</Note>

```python theme={null}
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookMatcher,
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)


async def can_use_tool(
    tool: str, input: dict, context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    # Check if the model is requesting to bypass the sandbox
    if tool == "Bash" and input.get("dangerouslyDisableSandbox"):
        # The model is requesting to run this command outside the sandbox
        print(f"Unsandboxed command requested: {input.get('command')}")

        if is_command_authorized(input.get("command")):
            return PermissionResultAllow()
        return PermissionResultDeny(
            message="Command not authorized for unsandboxed execution"
        )
    return PermissionResultAllow()


# Required: dummy hook keeps the stream open for can_use_tool
async def dummy_hook(input_data, tool_use_id, context):
    return {"continue_": True}


async def prompt_stream():
    yield {
        "type": "user",
        "message": {"role": "user", "content": "Deploy my application"},
    }


async def main():
    async for message in query(
        prompt=prompt_stream(),
        options=ClaudeAgentOptions(
            sandbox={
                "enabled": True,
                "allowUnsandboxedCommands": True,  # Model can request unsandboxed execution
            },
            permission_mode="default",
            can_use_tool=can_use_tool,
            hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[dummy_hook])]},
        ),
    ):
        print(message)
```

このパターンにより、以下が可能になります：

* **モデルリクエストを監査する**：モデルがサンドボックスなし実行をリクエストするときをログします
* **許可リストを実装する**：特定のコマンドのみがサンドボックスなしで実行されることを許可します
* **承認ワークフローを追加する**：特権操作に明示的な認可を要求します

<Warning>
  `dangerouslyDisableSandbox: True` で実行されるコマンドはシステムへの完全なアクセスを持ちます。`can_use_tool` ハンドラーがこれらのリクエストを慎重に検証することを確認してください。

  `permission_mode` が `bypassPermissions` に設定され、`allow_unsandboxed_commands` が有効な場合、モデルは承認プロンプトなしにサンドボックスの外でコマンドを自律的に実行できます。この組み合わせは、モデルがサンドボックス分離をサイレントに逃れることを効果的に許可します。
</Warning>

<h2 id="see-also">
  関連項目
</h2>

* [SDK 概要](/docs/ja/agent-sdk/overview) - 一般的な SDK 概念
* [TypeScript SDK リファレンス](/docs/ja/agent-sdk/typescript) - TypeScript SDK ドキュメント
* [CLI リファレンス](/docs/ja/cli-reference) - コマンドラインインターフェース
* [一般的なワークフロー](/docs/ja/common-workflows) - ステップバイステップガイド
