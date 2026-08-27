> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude Code Desktop でスケジュール設定されたタスクを実行する

> Claude Code Desktop でスケジュール設定されたタスクを設定して、毎日のコードレビュー、依存関係の監査、または朝のブリーフィングなど、定期的に Claude を自動的に実行します。

スケジュール設定されたタスクは、選択した時刻と頻度で新しいセッションを自動的に開始します。毎日のコードレビュー、依存関係の更新チェック、またはカレンダーとインボックスから情報を取得する朝のブリーフィングなど、定期的な作業に使用します。

Desktop アプリの **Routines** ページでは、ローカルスケジュール設定されたタスクとリモート [routines](/docs/ja/routines) の両方を作成できます。ローカルタスクはマシン上で実行され、ファイルとツールに直接アクセスできますが、アプリが開いていてコンピュータが起動している場合にのみ実行されます。リモートルーチンは Anthropic が管理するクラウドインフラストラクチャで実行され、コンピュータがオフの場合でも実行でき、API 呼び出しや GitHub イベントでも実行できます。このページではローカルスケジュール設定されたタスクについて説明します。リモートルーチンとそのトリガーオプションについては、[Routines](/docs/ja/routines) を参照してください。

<h2 id="compare-scheduling-options">
  スケジュール設定オプションの比較
</h2>

Claude Code offers three ways to schedule recurring or one-off work:

|                            | [Cloud](/docs/en/routines)               | [Desktop](/docs/en/desktop-scheduled-tasks) | [`/loop`](/docs/en/scheduled-tasks)      |
| :------------------------- | :---------------------------------- | :------------------------------------- | :---------------------------------- |
| Runs on                    | Cloud, Anthropic-managed by default | Your machine                           | Your machine                        |
| Requires machine on        | No                                  | Yes                                    | Yes                                 |
| Requires open session      | No                                  | No                                     | Yes                                 |
| Persistent across restarts | Yes                                 | Yes                                    | Restored on `--resume` if unexpired |
| Access to local files      | No (fresh clone)                    | Yes                                    | Yes                                 |
| MCP servers                | Connectors configured per task      | [Config files](/docs/en/mcp) and connectors | Inherits from session               |
| Permission prompts         | No (runs autonomously)              | Configurable per task                  | Inherits from session               |
| Customizable schedule      | Via `/schedule` in the CLI          | Yes                                    | Yes                                 |
| Minimum interval           | 1 hour                              | 1 minute                               | 1 minute                            |

<Tip>
  Use **cloud tasks** for work that should run reliably without your machine. Use **Desktop tasks** when you need access to local files and tools. Use **`/loop`** for quick polling during a session.
</Tip>

<Note>
  デフォルトでは、スケジュール設定されたタスクは、コミットされていない変更を含む、作業ディレクトリの現在の状態に対して実行されます。タスクを作成するときに worktree トグルを有効にすると、各実行が独立した Git worktree を取得します。これは [parallel sessions](/docs/ja/desktop#work-in-parallel-with-sessions) と同じ方法です。
</Note>

<h2 id="create-a-scheduled-task">
  スケジュール設定されたタスクを作成する
</h2>

サイドバーで **Routines** をクリックし、**New routine** をクリックして **Local** を選択します。これらのフィールドを設定します。

| フィールド        | 説明                                                                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name         | タスクの識別子。小文字のケバブケースに変換され、ディスク上のフォルダ名として使用されます。タスク全体で一意である必要があります。                                                                                       |
| Description  | タスクリストに表示される短い概要。                                                                                                                                      |
| Instructions | タスクが実行されるときに Claude が実行する内容。プロンプトボックスで任意のメッセージを記述するのと同じ方法で記述します。instructions 入力には、権限モードとモデルのピッカーが含まれており、その下で作業フォルダを選択し、分離された worktree で実行するかどうかを選択します。 |
| Schedule     | タスクが実行される頻度。以下の [schedule options](#schedule-options) を参照してください。                                                                                       |

タスクを保存する前に、フォルダが必要です。そのフォルダをまだ信頼していない場合、Desktop は保存する前にそのフォルダを信頼するよう促します。

任意のセッションで実行したい内容を説明することで、タスクを作成することもできます。たとえば、「毎朝 9 時に実行される毎日のコードレビューを設定する」と言うと、定期的なタスクが作成され、「明日午後 3 時にデプロイをチェックするよう通知する」と言うと、実行後に自分自身を無効にする 1 回限りのタスクが作成されます。

<h2 id="schedule-options">
  スケジュール設定オプション
</h2>

Schedule コントロールからプリセットを選択します。

* **Manual**: スケジュールなし、**Run now** をクリックしたときのみ実行されます。オンデマンドでトリガーするプロンプトを保存するのに便利です
* **Hourly**: 1 時間ごとに実行されます
* **Daily**: 時刻ピッカーを表示し、デフォルトは現地時間の午前 9 時です
* **Weekdays**: Daily と同じですが、土曜日と日曜日をスキップします
* **Weekly**: 時刻ピッカーと曜日ピッカーを表示します

15 分ごと、毎月 1 日、または特定の将来の時刻での 1 回限りの実行など、ピッカーが提供しないインターバルの場合は、任意の Desktop セッションで Claude に尋ねてスケジュールを設定します。プレーンテキストを使用します。たとえば、「6 時間ごとにすべてのテストを実行するタスクをスケジュール設定する」などです。

<h2 id="how-scheduled-tasks-run">
  スケジュール設定されたタスクの実行方法
</h2>

スケジュール設定されたタスクはマシン上で実行されます。Desktop はアプリが開いている間、毎分スケジュールをチェックし、開いている手動セッションとは独立して、タスクが期限を迎えたときに新しいセッションを開始します。各タスクは、スケジュール設定された時刻の後に数分の小さな遅延を取得して、API トラフィックを分散させます。遅延は決定的です。同じタスクは常に同じオフセットで開始されます。

タスクが実行されると、デスクトップ通知が表示され、新しいセッションがサイドバーの **Scheduled** セクションの下に表示されます。それを開いて、Claude が何をしたかを確認し、変更をレビューするか、権限プロンプトに応答します。セッションは他のセッションと同じように機能します。Claude はファイルを編集し、コマンドを実行し、コミットを作成し、プルリクエストを開くことができます。

タスクは Desktop アプリが実行されていて、コンピュータが起動している場合にのみ実行されます。コンピュータがスケジュール設定された時刻を通じてスリープ状態になった場合、実行はスキップされます。アイドルスリープを防ぐには、Settings の **Desktop app → General** で **Keep computer awake** を有効にします。ラップトップのふたを閉じるとスリープ状態になります。コンピュータがオフの場合でも実行する必要があるタスク、または API 呼び出しや GitHub イベントでトリガーする必要があるタスクの場合は、代わりにリモート [routine](/docs/ja/routines) を作成します。

<h2 id="missed-runs">
  見落とされた実行
</h2>

アプリが起動するか、コンピュータが起動すると、Desktop は各タスクが過去 7 日間に実行を見落としたかどうかをチェックします。見落とされた場合、Desktop は最近見落とされた時刻に対して正確に 1 つのキャッチアップ実行を開始し、それより古いものは破棄します。6 日間見落とされた毎日のタスクは、起動時に 1 回実行されます。Desktop はキャッチアップ実行が開始されたときに通知を表示します。

プロンプトを記述するときはこれを念頭に置いてください。午前 9 時にスケジュール設定されたタスクは、コンピュータが一日中スリープ状態だった場合、午後 11 時に実行される可能性があります。タイミングが重要な場合は、プロンプト自体にガードレールを追加します。たとえば、「今日のコミットのみをレビューします。午後 5 時以降の場合は、レビューをスキップして、見落とされたものの概要を投稿するだけです。」

<h2 id="permissions-for-scheduled-tasks">
  スケジュール設定されたタスクの権限
</h2>

各タスクには独自の権限モードがあり、タスクを作成または編集するときに設定します。`~/.claude/settings.json` からの許可ルールもスケジュール設定されたタスクセッションに適用されます。タスクが Ask モードで実行され、権限がないツールを実行する必要がある場合、実行は承認されるまで停止します。セッションはサイドバーに開いたままなので、後で応答できます。

停止を避けるには、タスクを作成した後に **Run now** をクリックし、権限プロンプトを監視し、各プロンプトに対して「常に許可」を選択します。そのタスクの将来の実行は、プロンプトなしで同じツールを自動承認します。タスクの詳細ページからこれらの承認をレビューして取り消すことができます。

Connector ツール [組織が `ask` に設定](/docs/ja/mcp#organization-controls-on-connector-tools) および [`requiresUserInteraction`](/docs/ja/mcp#require-approval-for-a-specific-tool) とマークされた MCP ツールは、毎回呼び出しのたびにプロンプトが表示され、常に許可オプションは提供されません。これらのツールを呼び出す実行は毎回停止します。

<h2 id="manage-scheduled-tasks">
  スケジュール設定されたタスクを管理する
</h2>

**Routines** リストのタスクをクリックして、その詳細ページを開きます。ここから以下を実行できます。

* **Run now**: 次のスケジュール設定された時刻を待たずに、タスクを直ちに開始します
* **Status**: Active と Paused の間を切り替えて、タスクを削除せずにスケジュール設定された実行を一時停止または再開します
* **Edit**: 指示、スケジュール、フォルダ、またはその他の設定を変更します
* **Review history**: スキップされた実行を含む、すべての過去の実行を確認します。スキップされたエントリにマウスを置くと、理由が表示されます。コンピュータがスリープ状態だった、前の実行がまだ進行中だった、または他のスケジュール設定されたタスクが既に実行されていました。**Show more** をクリックして、古いエントリを読み込みます。
* **Review allowed permissions**: **Always allowed** パネルからこのタスクの保存されたツール承認を確認および取り消します
* **Delete**: タスクを削除し、作成したすべてのセッションをアーカイブします。確認ダイアログに **Also delete files on disk** チェックボックスが表示されます。これをチェックして、タスクの `SKILL.md` ファイルと `~/.claude/scheduled-tasks/` の関連データも削除します。

任意の Desktop セッションで Claude に尋ねることで、タスクをリスト、作成、編集、および一時停止することもできます。たとえば、「dependency-audit タスクを一時停止する」または「スケジュール設定されたタスクを表示する」などです。タスクを削除するには、その詳細ページの **Delete** ボタンを使用します。

スケジュール設定されたタスクは、実行中のセッション内から `update_scheduled_task` MCP ツールを使用して、独自のスケジュールまたはプロンプトを変更することもできます。これにより、タスクは検出内容に基づいて自身をスケジュール変更できます。たとえば、リリースブランチが作成されたことを検出したときに、コードレビューを早期に実行するようにスケジュール変更します。

ディスク上のタスクのプロンプトを編集するには、`~/.claude/scheduled-tasks/<task-name>/SKILL.md` を開きます（[`CLAUDE_CONFIG_DIR`](/docs/ja/env-vars) が設定されている場合はその下）。ファイルは `name` と `description` の YAML frontmatter を使用し、プロンプトが本文です。変更は次の実行時に有効になります。スケジュール、フォルダ、モデル、および有効な状態はこのファイルにはありません。Edit フォームを通じて変更するか、Claude に尋ねます。

<h2 id="related-resources">
  関連リソース
</h2>

* [Routines](/docs/ja/routines): Anthropic が管理するインフラストラクチャでタスクを実行し、スケジュール、API 呼び出し、または GitHub イベントに応答して実行します。コンピュータがオフの場合でも実行できます
* [Run prompts on a schedule](/docs/ja/scheduled-tasks): CLI で `/loop` を使用したセッションスコープのスケジュール設定
* [Claude Code GitHub Actions](/docs/ja/github-actions): マシン上ではなく CI でスケジュール設定に従って Claude を実行します
* [Use Claude Code Desktop](/docs/ja/desktop): 完全な Desktop アプリガイド
