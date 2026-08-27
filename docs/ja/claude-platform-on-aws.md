> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# AWS 上の Claude Platform での Claude Code

> AWS 認証、IAM アクセス制御、AWS Marketplace 請求を使用して、Anthropic が運営する Claude API を使用するように Claude Code を設定します。

export const ContactSalesCard = ({surface}) => {
  const utm = content => `utm_source=claude_code&utm_medium=docs&utm_content=${surface}_${content}`;
  const iconArrowRight = (size = 13) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>;
  const STYLES = `
.cc-cs {
  --cs-slate: #141413;
  --cs-clay: #d97757;
  --cs-clay-deep: #c6613f;
  --cs-gray-000: #ffffff;
  --cs-gray-700: #3d3d3a;
  --cs-border-default: rgba(31, 30, 29, 0.15);
  font-family: inherit;
}
.dark .cc-cs {
  --cs-slate: #f0eee6;
  --cs-gray-000: #262624;
  --cs-gray-700: #bfbdb4;
  --cs-border-default: rgba(240, 238, 230, 0.14);
}
.cc-cs-card {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 14px 16px; margin: 0;
  background: var(--cs-gray-000); border: 0.5px solid var(--cs-border-default);
  border-radius: 8px; flex-wrap: wrap;
}
.cc-cs-text { font-size: 13px; color: var(--cs-gray-700); line-height: 1.5; flex: 1; min-width: 240px; }
.cc-cs-text strong { font-weight: 550; color: var(--cs-slate); }
.cc-cs-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.cc-cs-btn-clay {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--cs-clay-deep); color: #fff; border: none;
  border-radius: 8px; padding: 8px 14px;
  font-size: 13px; font-weight: 500;
  transition: background-color 0.15s; white-space: nowrap;
}
.cc-cs-btn-clay:hover { background: var(--cs-clay); }
.cc-cs-btn-ghost {
  display: inline-flex; align-items: center; gap: 8px;
  background: transparent; color: var(--cs-gray-700);
  border: 0.5px solid var(--cs-border-default);
  border-radius: 8px; padding: 8px 14px;
  font-size: 13px; font-weight: 500;
}
.cc-cs-btn-ghost:hover { background: rgba(0, 0, 0, 0.04); }
.dark .cc-cs-btn-ghost:hover { background: rgba(255, 255, 255, 0.04); }
@media (max-width: 720px) {
  .cc-cs-actions { width: 100%; }
}
`;
  return <div className="cc-cs not-prose">
      <style>{STYLES}</style>
      <div className="cc-cs-card">
        <div className="cc-cs-text">
          <strong>Deploying Claude Code across your organization?</strong> Talk to sales about enterprise plans, SSO, and centralized billing.
        </div>
        <div className="cc-cs-actions">
          <a href={`https://claude.com/pricing?${utm('view_plans')}#plans-business`} className="cc-cs-btn-ghost">
            View plans
          </a>
          <a href={`https://claude.com/contact-sales?${utm('contact_sales')}`} className="cc-cs-btn-clay">
            Contact sales {iconArrowRight()}
          </a>
        </div>
      </div>
    </div>;
};

export const Experiment = ({flag, treatment, children}) => {
  const VID_KEY = 'exp_vid';
  const CONSENT_COUNTRIES = new Set(['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'RE', 'GP', 'MQ', 'GF', 'YT', 'BL', 'MF', 'PM', 'WF', 'PF', 'NC', 'AW', 'CW', 'SX', 'FO', 'GL', 'AX', 'GB', 'UK', 'AI', 'BM', 'IO', 'VG', 'KY', 'FK', 'GI', 'MS', 'PN', 'SH', 'TC', 'GG', 'JE', 'IM', 'CA', 'BR', 'IN']);
  const fnv1a = s => {
    let h = 0x811c9dc5;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24);
    }
    return h >>> 0;
  };
  const bucket = (seed, vid) => fnv1a(fnv1a(seed + vid) + '') % 10000 < 5000 ? 'control' : 'treatment';
  const [decision] = useState(() => {
    const params = new URLSearchParams(location.search);
    const preBucketed = document.documentElement.dataset['gb_' + flag.replace(/-/g, '_')];
    const force = params.get('gb-force');
    if (force) {
      for (const p of force.split(',')) {
        const [k, v] = p.split(':');
        if (k === flag) return {
          variant: v || 'treatment',
          track: false
        };
      }
    }
    if (navigator.globalPrivacyControl) {
      return {
        variant: 'control',
        track: false
      };
    }
    const prefsMatch = document.cookie.match(/(?:^|; )anthropic-consent-preferences=([^;]+)/);
    if (prefsMatch) {
      try {
        if (JSON.parse(decodeURIComponent(prefsMatch[1])).analytics !== true) {
          return {
            variant: 'control',
            track: false
          };
        }
      } catch {
        return {
          variant: 'control',
          track: false
        };
      }
    } else {
      const country = params.get('country')?.toUpperCase() || (document.cookie.match(/(?:^|; )cf_geo=([A-Z]{2})/) || [])[1];
      if (!country || CONSENT_COUNTRIES.has(country)) {
        return {
          variant: 'control',
          track: false
        };
      }
    }
    let vid;
    try {
      const ajsMatch = document.cookie.match(/(?:^|; )ajs_anonymous_id=([^;]+)/);
      if (ajsMatch) {
        vid = decodeURIComponent(ajsMatch[1]).replace(/^"|"$/g, '');
      } else {
        vid = localStorage.getItem(VID_KEY);
        if (!vid) {
          vid = crypto.randomUUID();
        }
        document.cookie = `ajs_anonymous_id=${vid}; domain=.claude.com; path=/; Secure; SameSite=Lax; max-age=31536000`;
      }
      try {
        localStorage.setItem(VID_KEY, vid);
      } catch {}
    } catch {
      return {
        variant: 'control',
        track: false
      };
    }
    const variant = preBucketed === '1' ? 'treatment' : preBucketed === '0' ? 'control' : bucket(flag, vid);
    return {
      variant,
      track: true,
      vid
    };
  });
  useEffect(() => {
    if (!decision.track) return;
    fetch('https://api.anthropic.com/api/event_logging/v2/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-service-name': 'claude_code_docs'
      },
      body: JSON.stringify({
        events: [{
          event_type: 'GrowthbookExperimentEvent',
          event_data: {
            device_id: decision.vid,
            anonymous_id: decision.vid,
            timestamp: new Date().toISOString(),
            experiment_id: flag,
            variation_id: decision.variant === 'treatment' ? 1 : 0,
            environment: 'production'
          }
        }]
      }),
      keepalive: true
    }).catch(() => {});
  }, []);
  return decision.variant === 'treatment' ? treatment : children;
};

<Experiment flag="docs-contact-sales-cta" treatment={<ContactSalesCard surface="claude_platform_on_aws" />} />

AWS 上の Claude Platform は、AWS 認証、IAM アクセス制御、AWS Marketplace 請求を備えた Anthropic が運営する Claude API です。リクエストは Anthropic の API に直接到達するため、[Claude API](https://platform.claude.com/docs) と同じモデルと API 機能を同じリリーススケジュールで取得できます。Claude Code が Anthropic の機能フラグサービスを通じてオンにするクライアント側機能（[`/loop` 自動ペーシング](/docs/ja/scheduled-tasks#let-claude-choose-the-interval)など）はデフォルトではオフであり、[アドバイザーツール](/docs/ja/advisor)は利用できません。完全なリストについては、[機能可用性マトリックス](/docs/ja/feature-availability#summary-by-provider)を参照してください。AWS 認証情報またはワークスペース API キーで認証し、AWS Marketplace を通じて支払います。

このガイドを使用して、AWS 上の Claude Platform を通じてすでにプロビジョニングしたワークスペースに Claude Code をポイントします。このガイドの前に行う AWS サブスクリプションとワークスペースのセットアップについては、[AWS 上の Claude Platform ドキュメント](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws)を参照してください。

<Note>
  AWS Marketplace を通じてサブスクリプションすると、AWS アカウントに関連付けられた新しい Anthropic 組織がプロビジョニングされます。この組織は、Anthropic で既に持っている組織とは別であり、認証情報はそれらの間で転送されません。AWS にリンクされた組織のワークスペース ID と API キーを使用してください。既存の Claude Console アカウントからではなく。
</Note>

<h2 id="prerequisites">
  前提条件
</h2>

Claude Code を設定する前に、以下が必要です。

* AWS Marketplace を通じた有効な AWS 上の Claude Platform サブスクリプション
* AWS にリンクされた Anthropic 組織内のワークスペース（ワークスペース ID 付き）
* Anthropic サービスを呼び出す権限を持つ IAM プリンシパル、またはワークスペースにスコープされた API キー
* 環境内、`~/.aws/credentials` 内、または SigV4 認証が必要な場合は接続された IAM ロールからの AWS 認証情報。AWS CLI は SSO ログインフローにのみ必要です。

<h2 id="setup">
  セットアップ
</h2>

<h3 id="1-configure-aws-credentials">
  1. AWS 認証情報を設定する
</h3>

Claude Code は AWS 上の Claude Platform に対して 2 つの認証方法をサポートしています。チームがアクセスを管理する方法に合った方法を選択してください。

**オプション A: SigV4 を使用した AWS 認証情報**

Claude Code は標準的な AWS 認証情報チェーンを使用して SigV4 でリクエストに署名します。環境変数、`~/.aws/credentials` の共有認証情報、IAM ロール、AWS SSO セッション、および AWS SDK がサポートするその他のソース。

ローカル使用の場合、Claude Code を開始する前に AWS CLI でログインしてください。以下の例は SSO プロファイルを使用していますが、標準的な場所に認証情報を生成する任意の方法が機能します。

```bash theme={null}
aws sso login --profile my-profile
export AWS_PROFILE=my-profile
```

CI と自動化の場合、Anthropic サービスを呼び出す権限を持つ IAM ロールをランナーに付与し、`AWS_REGION` を設定します。認証情報チェーンはロールを自動的に取得します。

SSO 認証情報がセッション中に期限切れになった場合、[`awsAuthRefresh`](/docs/ja/amazon-bedrock#advanced-credential-configuration) を設定して、Claude Code がログインコマンドを再実行し、失敗する代わりに再試行するようにします。AWS 上の Claude Platform での自動更新には Claude Code v2.1.198 以降が必要です。それより前のバージョンは `/login` を実行するプロンプトで停止します。これは AWS 認証情報を更新できません。コマンドを `settings.json` に追加します。

```json theme={null}
{
  "awsAuthRefresh": "aws sso login --profile my-profile"
}
```

`awsAuthRefresh` が設定されている場合、`/login` は **Using 3rd-party platforms** の下に **Claude Platform on AWS · refresh credentials** オプションを表示します。これを選択すると、設定されたコマンドが実行され、Claude Code を再起動せずに AWS 認証情報が再度読み込まれます。

**オプション B: ワークスペース API キー**

ワークスペース API キーは長期間有効なシークレットで、フェデレーション AWS 認証情報を管理したくない場合に便利です。AWS Console の **Claude Platform on AWS → API keys** で生成し、`ANTHROPIC_AWS_API_KEY` として設定します。

```bash theme={null}
export ANTHROPIC_AWS_API_KEY=sk-ant-xxxxx
```

キーは `x-api-key` として送信され、SigV4 よりも優先されるため、環境内の AWS 認証情報は無視されます。別の Claude Console 組織からの API キーはここでは機能しません。

ワークスペース API キーは他の本番認証情報と同様に扱ってください。[ユーザー設定ファイル](/docs/ja/settings) の `env` ブロックは、グローバルにエクスポートせずにキーをマシンにスコープするための便利な方法です。

<Note>
  `/login` および `/logout` コマンドは Claude.ai サブスクリプションに対してサインインしません。AWS 上の Claude Platform の場合、認証は AWS 認証情報またはワークスペース API キーを通じて実行されます。例外は、`awsAuthRefresh` が設定されている場合に `/login` が表示する **refresh credentials** オプションで、これは上記で説明したように AWS 認証情報を再度読み込みます。
</Note>

<h3 id="2-configure-claude-code">
  2. Claude Code を設定する
</h3>

Claude Code をデフォルトの Anthropic API ではなく AWS 上の Claude Platform を通じてルーティングする環境変数を設定します。

```bash theme={null}
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export ANTHROPIC_AWS_WORKSPACE_ID=wrkspc_01ABCDEFGHIJKLMN
export AWS_REGION=us-east-1
```

`ANTHROPIC_AWS_WORKSPACE_ID` は必須であり、すべてのリクエストで `anthropic-workspace-id` ヘッダーとして送信されます。ベース URL は `AWS_REGION` から `https://aws-external-anthropic.{region}.api.aws` として計算されます。URL を直接オーバーライドするには、`ANTHROPIC_AWS_BASE_URL` を設定します。

AWS 上の Claude Platform は、環境に AWS 認証情報が存在する場合でもオプトインです。Amazon Bedrock と Microsoft Foundry はプロバイダールーティングで優先されるため、設定されている場合は `CLAUDE_CODE_USE_BEDROCK` と `CLAUDE_CODE_USE_FOUNDRY` をアンセットします。

<h3 id="3-pin-model-versions">
  3. モデルバージョンをピン留めする
</h3>

AWS 上の Claude Platform は、直接 Claude API と同じモデル ID を使用します。

デフォルトのエイリアス `fable`、`opus`、`sonnet`、`haiku` は Claude Code の AWS 上の Claude Platform 用の組み込みデフォルトに解決されます。これは最新リリースより遅れる可能性があります。`ANTHROPIC_DEFAULT_OPUS_MODEL` がない場合、`opus` エイリアスは Opus 4.8 に解決されます。v2.1.207 より前では、Opus 4.7 に解決されていました。

Claude Code をチームにデプロイする場合、モデル ID を明示的にピン留めして、新しいリリースがすべてのユーザーを一度に移動しないようにします。

```bash theme={null}
export ANTHROPIC_DEFAULT_FABLE_MODEL=claude-fable-5
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-8
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-5
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5
```

モデル ID とエイリアスの完全なリストについては、[モデル概要](https://platform.claude.com/docs/en/about-claude/models/overview) を参照してください。その他のモデル関連の変数については、[モデル設定](/docs/ja/model-config) を参照してください。

[プロンプトキャッシング](/docs/ja/prompt-caching) は自動的に有効になります。5 分のデフォルトの代わりに 1 時間のキャッシュ TTL をリクエストするには、`ENABLE_PROMPT_CACHING_1H=1` を設定します。API は 1 時間のキャッシュ書き込みをより高いレートで請求します。レートについては、[プロンプトキャッシング価格](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#pricing) を参照してください。

<h2 id="use-the-agent-sdk">
  Agent SDK を使用する
</h2>

[Agent SDK](/docs/ja/agent-sdk/overview) は CLI と同じ環境変数を読み取るため、Claude Code サブプロセスを生成するプログラムは、呼び出しの前に `CLAUDE_CODE_USE_ANTHROPIC_AWS`、`ANTHROPIC_AWS_WORKSPACE_ID`、および `ANTHROPIC_AWS_API_KEY` または AWS 認証情報をエクスポートすることで AWS 上の Claude Platform をターゲットにできます。

```typescript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";

process.env.CLAUDE_CODE_USE_ANTHROPIC_AWS = "1";
process.env.ANTHROPIC_AWS_WORKSPACE_ID = "wrkspc_01ABCDEFGHIJKLMN";
process.env.AWS_REGION = "us-east-1";

for await (const msg of query({ prompt: "What's in this repo?" })) {
  console.log(msg);
}
```

この例は SigV4 のアンビエント AWS 認証情報チェーンに依存しています。代わりにワークスペース API キーで認証するには、同じ方法で `ANTHROPIC_AWS_API_KEY` を設定します。より広い Agent SDK サーフェスについては、[Agent SDK 概要](/docs/ja/agent-sdk/overview)を参照してください。

<h2 id="route-through-a-corporate-proxy">
  企業プロキシを通じてルーティングする
</h2>

プロキシまたは [LLM ゲートウェイ](/docs/ja/llm-gateway)を通じてトラフィックをルーティングするには、`ANTHROPIC_AWS_BASE_URL` をプロキシのアドレスに設定します。Claude Code は同じワークスペースと認証ヘッダーを使用してそのアドレスにリクエストを送信するため、それらを変更せずに転送するゲートウェイが機能します。

```bash theme={null}
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export ANTHROPIC_AWS_WORKSPACE_ID=wrkspc_01ABCDEFGHIJKLMN
export ANTHROPIC_AWS_BASE_URL=https://anthropic-proxy.example.com
```

ゲートウェイがリクエストに自身で署名する場合、`CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH=1` を設定して、Claude Code が署名なしのリクエストを送信し、ゲートウェイが AWS に転送する前に SigV4 ヘッダーを追加するようにします。ゲートウェイが独自のトークンを必要とする場合は、`ANTHROPIC_AUTH_TOKEN` に設定します。

```bash theme={null}
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH=1
export ANTHROPIC_AWS_WORKSPACE_ID=wrkspc_01ABCDEFGHIJKLMN
export ANTHROPIC_AWS_BASE_URL=https://anthropic-proxy.example.com
```

<h2 id="troubleshooting">
  トラブルシューティング
</h2>

`/status` を実行して、解決されたプロバイダーと明示的に設定されたワークスペース ID、リージョン、ベース URL オーバーライド、および認証スキップ設定を確認します。これは Claude Code が AWS 上の Claude Platform をターゲットにしているかどうかを確認する最速の方法です。

<h3 id="403-forbidden-or-accessdenied-on-every-request">
  すべてのリクエストで `403 Forbidden` または `AccessDenied`
</h3>

Claude Code が解決した IAM プリンシパルは、ワークスペースで Anthropic サービスを呼び出す権限がない可能性があります。AWS プロファイルに接続されたロール、または Claude Code を開始したランナーを確認し、[IAM アクション参照](https://platform.claude.com/docs/ja/api/claude-platform-on-aws-iam-actions)に記載されている `aws-external-anthropic` アクションがあることを確認します。

`ANTHROPIC_AWS_API_KEY` を設定した場合、キーは SigV4 よりも優先され、古いキーは同じエラーを生成します。AWS Console の **Claude Platform on AWS → API keys** でキーを再生成するか、変数をアンセットして AWS 認証情報にフォールバックします。

<h3 id="requests-fail-with-a-missing-workspace-error">
  リクエストがワークスペース不足エラーで失敗する
</h3>

`ANTHROPIC_AWS_WORKSPACE_ID` がアンセットまたは空の可能性があります。すべての AWS 上の Claude Platform リクエストにはワークスペース ID を含める必要があります。AWS 認証情報によって暗示されません。AWS Console サービスページの **Workspaces** の下で ID を見つけ、Claude Code を開始する前にエクスポートします。

<h3 id="requests-still-go-to-api-anthropic-com">
  リクエストが依然として `api.anthropic.com` に送信される
</h3>

`CLAUDE_CODE_USE_ANTHROPIC_AWS` がアンセットまたは truthy として解析されない値に設定されている可能性があります。`1` に設定し、`/status` を実行して解決されたプロバイダーを確認します。`CLAUDE_CODE_USE_BEDROCK` または `CLAUDE_CODE_USE_FOUNDRY` も設定されている場合、それらは AWS 上の Claude Platform よりも優先されます。

<h2 id="additional-resources">
  追加リソース
</h2>

Claude Code を設定する前に行う AWS 上の Claude Platform サブスクリプション、ワークスペース、IAM セットアップはプラットフォームドキュメントで説明されています。

* [AWS 上の Claude Platform 概要](https://platform.claude.com/docs/ja/build-with-claude/claude-platform-on-aws): サブスクリプション、ワークスペースセットアップ、製品リファレンス
* [IAM アクション参照](https://platform.claude.com/docs/ja/api/claude-platform-on-aws-iam-actions): 権限とマネージドポリシー
