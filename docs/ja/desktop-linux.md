> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude Desktop on Linux (beta)

> Ubuntu と Debian に Claude デスクトップアプリをインストールおよび更新する

<Note>
  Claude デスクトップアプリの Linux サポートはベータ版です。Chat、Cowork、Code タブはすべて利用可能です。
</Note>

Linux 上のデスクトップアプリは、macOS と Windows と同じ Chat、Cowork、Claude Code エクスペリエンスを提供します。並列セッション、ビジュアル diff レビュー、統合ターミナルとエディタ、ライブアプリプレビューが含まれます。完全な機能リファレンスについては、[Claude Code Desktop を使用する](/docs/ja/desktop)を参照してください。

<h2 id="requirements">
  要件
</h2>

* Ubuntu 22.04 以降、または Debian 12 以降
* x86\_64 または arm64

これらの要件を満たす他の Debian ベースのディストリビューションは動作する可能性がありますが、公式にはテストされていません。

<h2 id="install">
  インストール
</h2>

Anthropic の apt リポジトリからインストールして、更新がシステムの通常のパッケージ更新を通じて提供されるようにします。ターミナルを開き、各ステップのコマンドを実行してください。

<Steps>
  <Step title="Anthropic の apt リポジトリを追加する">
    このステップでは `curl` を使用して署名キーをダウンロードします。新しい Debian および Ubuntu インストールには `curl` が含まれていない場合があります。ダウンロードコマンドが `sudo: curl: command not found` で失敗する場合は、まず curl をインストールしてください。

    ```bash theme={null}
    sudo apt install curl
    ```

    Anthropic の署名キーをダウンロードします。

    ```bash theme={null}
    sudo curl -fsSLo /usr/share/keyrings/claude-desktop-archive-keyring.asc https://downloads.claude.ai/claude-desktop/key.asc
    ```

    リポジトリを登録します。

    ```bash theme={null}
    echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/claude-desktop-archive-keyring.asc] https://downloads.claude.ai/claude-desktop/apt/stable stable main" | sudo tee /etc/apt/sources.list.d/claude-desktop.list
    ```
  </Step>

  <Step title="パッケージをインストールする">
    ```bash theme={null}
    sudo apt update && sudo apt install claude-desktop
    ```
  </Step>

  <Step title="起動してサインインする">
    アプリケーションランチャーから **Claude** を起動するか、ターミナルから `claude-desktop` を実行して、Anthropic アカウントでサインインします。

    Linux アプリは macOS と Windows と同じ方法でサインインします。claude.ai サブスクリプション、または組織の SSO を通じてサインインします。Desktop は Claude Console API キーを直接受け入れません。API キー認証には [CLI](/docs/ja/quickstart) を使用してください。Google Cloud の Agent Platform または LLM ゲートウェイに Desktop をルーティングするエンタープライズデプロイメントについては、[Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview) および [ネットワーク設定](/docs/ja/network-config) を参照してください。
  </Step>
</Steps>

<Accordion title="署名キーを検証する">
  ダウンロードした署名キーが Anthropic に属していることを確認できます。

  ```bash theme={null}
  gpg --show-keys /usr/share/keyrings/claude-desktop-archive-keyring.asc
  ```

  フィンガープリントは `31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE` である必要があります。
</Accordion>

<h3 id="install-from-a-downloaded-file">
  ダウンロードしたファイルからインストールする
</h3>

apt リポジトリを使用できない場合は、リポジトリのパッケージプールから `.deb` パッケージを直接ダウンロードしてください。このコマンドはリポジトリインデックスでアーキテクチャに対応した最新パッケージを検索し、現在のディレクトリにダウンロードします。

```bash theme={null}
curl -fLO "https://downloads.claude.ai/claude-desktop/apt/stable/$(curl -s "https://downloads.claude.ai/claude-desktop/apt/stable/dists/stable/main/binary-$(dpkg --print-architecture)/Packages" | grep '^Filename: pool/main/c/claude-desktop/claude-desktop_' | sort -V | tail -n 1 | cut -d' ' -f2)"
```

コマンドが `Remote file name has no length` で失敗する場合、検索がパッケージパスを返しませんでした。これはリポジトリインデックスを取得できなかった場合（例えば、ネットワークが `downloads.claude.ai` をブロックしている場合）、またはアーキテクチャに対応したパッケージが存在しない場合を意味します。ネットワークが `downloads.claude.ai` に到達できることを確認し、`dpkg --print-architecture` が `amd64` または `arm64` を出力することを確認してください。リポジトリは他のアーキテクチャのパッケージを公開していません。

次に、ダウンロードしたファイルをソフトウェアインストーラー（GNOME Software など）で開くか、ダウンロードしたファイルが含まれているディレクトリから apt でインストールします。

```bash theme={null}
sudo apt install ./claude-desktop_*.deb
```

apt が `E: Unsupported file ./claude-desktop_*.deb given on commandline` を報告する場合、パターンが現在のディレクトリ内の `.deb` ファイルと一致しませんでした。ダウンロードが完了したことを確認してから、ファイルが含まれているディレクトリからコマンドを再度実行してください。

この方法でインストールされた `.deb` は更新を受け取りません。apt を通じて更新を取得するには、[Anthropic の apt リポジトリを追加する](#install) ステップからリポジトリを登録してください。パッケージは `/etc/apt/sources.list.d/claude-desktop.list` にコメントアウトされたリポジトリエントリも書き込みます。その `deb` 行をコメント解除することと同等です。

<h2 id="update">
  更新
</h2>

デスクトップアプリは Linux では自動的に更新されません。更新はシステムの通常のパッケージ更新で提供されます。

```bash theme={null}
sudo apt update && sudo apt upgrade
```

ディストリビューションのグラフィカルソフトウェアアップデーターも新しいバージョンを検出します。

<h2 id="uninstall">
  アンインストール
</h2>

```bash theme={null}
sudo apt remove claude-desktop
```

これはアプリと一緒に署名キーを削除するため、インストール中にリポジトリエントリを追加した場合は、それも削除します。

```bash theme={null}
sudo rm /etc/apt/sources.list.d/claude-desktop.list
```

<h2 id="troubleshoot">
  トラブルシューティング
</h2>

<h3 id="unable-to-locate-package-claude-desktop">
  claude-desktop パッケージが見つからない
</h3>

`sudo apt install claude-desktop` が `E: Unable to locate package claude-desktop` で失敗する場合、apt が追加したリポジトリを見つけられていません。以下を確認してください。

* リポジトリエントリが書き込まれたことを確認します。`cat /etc/apt/sources.list.d/claude-desktop.list` は [Anthropic の apt リポジトリを追加](#install) ステップの `deb` 行を表示する必要があります。ファイルが空または見つからない場合は、そのステップを再度実行してください。
* アーキテクチャがサポートされていることを確認します。`dpkg --print-architecture` は `amd64` または `arm64` を出力する必要があります。リポジトリは他のアーキテクチャのパッケージを公開していません。
* `sudo apt update` を再度実行し、`downloads.claude.ai` に関連するエラーの出力を確認します。そこでネットワークまたはキーエラーが発生している場合は、リポジトリが追加されましたが、到達またはベリファイできなかったことを意味します。

リポジトリが配置されており到達可能で、パッケージがまだ見つからない場合は、代わりに [ダウンロードしたファイルからインストール](#install-from-a-downloaded-file) してください。

<h2 id="what’s-not-in-the-linux-beta-yet">
  Linux ベータ版にまだ含まれていない機能
</h2>

* **Computer Use**: [アプリとスクリーン制御](/docs/ja/desktop#let-claude-use-your-computer)は Linux では利用できません。
* **Dictation**: 音声入力は Linux デスクトップアプリでは利用できません。代わりに CLI で[音声ディクテーション](/docs/ja/voice-dictation)を使用してください。
* **Quick Entry グローバルホットキー**: X11 で動作します。ネイティブ Wayland では、デスクトップ環境の GlobalShortcuts ポータルが必要です。
* **Fedora と RHEL**: 現在、Debian ベースのディストリビューションのみがサポートされています。追加のディストリビューションのサポートは今後提供される予定です。

デスクトップアプリでまだ利用できない機能については、[CLI](/docs/ja/quickstart)は同じ Claude Code エンジンを実行し、より広い範囲の Linux ディストリビューションをサポートしています。[システム要件](/docs/ja/setup#system-requirements)を参照してください。
