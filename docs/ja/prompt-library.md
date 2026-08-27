> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# プロンプトライブラリ

> Claude Code 用のコピー＆ペーストプロンプト。タスクと役割でタグ付けされています。

export const PromptLibrary = ({text = {}, labels = {}, tagLabels = {}, phaseLabels = {}, sourceLabels = {}, catLabels = {}}) => {
  const RAW = useMemo(() => [{
    id: 'get-oriented-in-a',
    sdlc: 'discover',
    cat: 'Onboard',
    startN: 1,
    roles: [],
    prompt: 'give me an overview of this codebase: architecture, key directories, and how the pieces connect',
    nextHref: '/en/memory',
    src: 'workflows'
  }, {
    id: 'explain-unfamiliar-code',
    sdlc: 'discover',
    cat: 'Understand',
    roles: [],
    prompt: 'explain what {path} does and how data flows through it. write it up as {format}',
    slots: {
      path: 'src/scheduler/queue.ts',
      format: 'an HTML page with a diagram, then open it in my browser'
    },
    nextHref: '/en/output-styles',
    src: 'workflows'
  }, {
    id: 'find-where-something-happens',
    sdlc: 'discover',
    cat: 'Understand',
    startN: 2,
    roles: [],
    prompt: 'where do we {behavior}?',
    slots: {
      behavior: 'validate uploaded file types'
    },
    src: 'workflows'
  }, {
    id: 'see-what-depends-on',
    sdlc: 'discover',
    cat: 'Understand',
    roles: [],
    prompt: 'what would break if I deleted {target}?',
    slots: {
      target: 'the retryWithBackoff helper'
    },
    src: 'workflows'
  }, {
    id: 'trace-how-code-evolved',
    sdlc: 'discover',
    cat: 'Understand',
    roles: [],
    prompt: 'look through the commit history of {path} and summarize how it evolved and why',
    slots: {
      path: 'internal/auth/session.go'
    },
    src: 'best-practices'
  }, {
    id: 'scope-a-change-before',
    sdlc: 'discover',
    cat: 'Understand',
    roles: ['pm', 'design'],
    prompt: 'which files would I need to touch to {change}?',
    slots: {
      change: 'add a dark mode toggle to settings'
    },
    src: 'teams'
  }, {
    id: 'ask-the-codebase-a',
    sdlc: 'discover',
    cat: 'Understand',
    roles: ['pm'],
    prompt: 'I am a {role}. walk me through what happens when a user {action}, from the UI down to the result',
    slots: {
      role: 'PM',
      action: 'clicks Export to PDF'
    },
    nextHref: '/en/output-styles',
    src: 'teams'
  }, {
    id: 'plan-a-multi-file',
    sdlc: 'design',
    cat: 'Plan',
    roles: ['pm', 'design'],
    prompt: 'plan how to refactor the {target} to {goal}. list the files you would change, but don\'t edit anything yet',
    slots: {
      target: 'payment module',
      goal: 'support multiple currencies'
    },
    src: 'workflows'
  }, {
    id: 'draft-a-spec-by',
    sdlc: 'design',
    cat: 'Plan',
    roles: ['pm'],
    prompt: 'I want to build {feature}. interview me about implementation, UX, edge cases, and tradeoffs until we have covered everything, then write the spec to SPEC.md',
    slots: {
      feature: 'per-workspace rate limits'
    },
    nextHref: '/en/skills',
    src: 'best-practices'
  }, {
    id: 'turn-a-meeting-into',
    sdlc: 'design',
    cat: 'Plan',
    roles: ['pm'],
    prompt: 'read {input} and write up the action items, then create a {tracker} ticket for each with acceptance criteria',
    slots: {
      input: '@meeting-notes.md',
      tracker: 'Linear'
    },
    needs: 'tracker',
    nextHref: '/en/skills',
    src: 'teams'
  }, {
    id: 'map-edge-cases-before',
    sdlc: 'design',
    cat: 'Plan',
    roles: ['design', 'pm'],
    prompt: 'list the error states, empty states, and edge cases for {feature} that the design needs to cover',
    slots: {
      feature: 'the file upload flow'
    },
    src: 'teams'
  }, {
    id: 'turn-a-mockup-into',
    sdlc: 'design',
    cat: 'Prototype',
    roles: ['design', 'pm', 'marketing'],
    paste: 'mockup',
    prompt: 'here is a mockup. build a working prototype I can click through, matching the layout and states shown',
    src: 'teams'
  }, {
    id: 'implement-from-a-screenshot',
    sdlc: 'design',
    cat: 'Prototype',
    roles: ['design'],
    paste: 'design',
    needs: 'browser',
    prompt: 'implement this design, then take a screenshot of the result, compare it to the original, and fix any differences',
    nextHref: '/en/goal',
    src: 'best-practices'
  }, {
    id: 'follow-an-existing-pattern',
    sdlc: 'build',
    cat: 'Implement',
    roles: [],
    prompt: 'look at how {example} is implemented to understand the pattern, then build {new} the same way',
    slots: {
      example: 'the GitHub webhook handler',
      new: 'a Stripe webhook handler'
    },
    nextHref: '/en/memory',
    src: 'best-practices'
  }, {
    id: 'generate-docs-for-code',
    sdlc: 'build',
    cat: 'Implement',
    roles: ['docs'],
    prompt: 'find {scope} without {format} comments and add them, matching the style already used in the file',
    slots: {
      scope: 'the public functions in src/auth/',
      format: 'JSDoc'
    },
    src: 'workflows'
  }, {
    id: 'add-a-small-well',
    sdlc: 'build',
    cat: 'Implement',
    roles: [],
    prompt: 'add a {endpoint} endpoint that returns {payload}',
    slots: {
      endpoint: '/health',
      payload: 'the app version and uptime'
    },
    src: 'workflows'
  }, {
    id: 'build-a-small-internal',
    sdlc: 'build',
    cat: 'Implement',
    roles: ['pm', 'design', 'marketing', 'docs'],
    prompt: 'create a {tool} using HTML, CSS, and vanilla JavaScript, then open it in my browser',
    slots: {
      tool: 'drag-and-drop Kanban board with three columns'
    },
    src: 'teams'
  }, {
    id: 'work-an-issue-end',
    sdlc: 'build',
    cat: 'Implement',
    roles: [],
    prompt: 'read issue #{issue}, implement the fix, and run the tests',
    slots: {
      issue: '312'
    },
    needs: 'gh',
    src: 'workflows'
  }, {
    id: 'find-and-update-copy',
    sdlc: 'build',
    cat: 'Implement',
    roles: ['design', 'docs', 'marketing'],
    prompt: 'find every place we say "{copy}" or a close variant, show me each one in context, then update them all to "{new}". leave tests and the changelog alone',
    slots: {
      copy: 'Sign up free',
      new: 'Start free trial'
    },
    src: 'teams'
  }, {
    id: 'draft-from-past-examples',
    sdlc: 'build',
    cat: 'Implement',
    roles: ['docs', 'marketing', 'pm'],
    prompt: 'read the {examples} in {folder} to learn the structure and voice, then draft a new one for {topic}',
    slots: {
      examples: 'privacy impact assessments',
      folder: 'legal/pia/',
      topic: 'the new analytics integration'
    },
    nextHref: '/en/skills',
    src: 'legal'
  }, {
    id: 'write-tests-run-them',
    sdlc: 'build',
    cat: 'Test',
    startN: 4,
    roles: [],
    prompt: 'write tests for {path}, run them, and fix any failures',
    slots: {
      path: 'app/parsers/feed.py'
    },
    nextHref: '/en/memory',
    src: 'workflows'
  }, {
    id: 'drive-implementation-from-tests',
    sdlc: 'build',
    cat: 'Test',
    roles: [],
    prompt: 'write tests for {feature} first, then implement it until they pass',
    slots: {
      feature: 'the password reset flow'
    },
    src: 'ebook'
  }, {
    id: 'fill-gaps-from-a',
    sdlc: 'build',
    cat: 'Test',
    roles: [],
    prompt: 'read {report} and add tests for the lowest-covered files until each is above {target}%',
    slots: {
      report: 'coverage/coverage-summary.json',
      target: '80'
    },
    nextHref: '/en/goal',
    src: 'workflows'
  }, {
    id: 'migrate-a-pattern-across',
    sdlc: 'build',
    cat: 'Refactor',
    roles: [],
    prompt: 'migrate everything from {from} to {to}: identify every place that needs to change, then make the changes',
    slots: {
      from: 'the old logging API',
      to: 'the structured logger'
    },
    src: 'workflows'
  }, {
    id: 'port-code-between-languages',
    sdlc: 'build',
    cat: 'Refactor',
    roles: [],
    prompt: 'port {source} to {target}, keeping the same {keep}',
    slots: {
      source: 'this Python module',
      target: 'Rust',
      keep: 'public API and test behavior'
    },
    src: 'teams'
  }, {
    id: 'optimize-against-a-measurable',
    sdlc: 'build',
    cat: 'Refactor',
    roles: ['data'],
    prompt: 'optimize {target} to bring {metric} from {current} down to under {goal}',
    slots: {
      target: 'the search query',
      metric: 'p95 latency',
      current: '2s',
      goal: '500ms'
    },
    nextHref: '/en/goal',
    src: 'ebook'
  }, {
    id: 'fix-a-precise-visual',
    sdlc: 'build',
    cat: 'Refactor',
    roles: ['design'],
    prompt: 'the {element} extends {amount} beyond the {container} on {viewport}. fix it.',
    slots: {
      element: 'login button',
      amount: '20px',
      container: 'card border',
      viewport: 'mobile'
    },
    nextHref: '/en/desktop#preview-your-app',
    src: 'ebook'
  }, {
    id: 'review-your-changes-before',
    sdlc: 'build',
    cat: 'Review',
    startN: 5,
    roles: [],
    prompt: 'review my uncommitted changes and flag anything that looks risky before I commit',
    nextHref: '/en/commands',
    src: 'workflows'
  }, {
    id: 'review-a-pull-request',
    sdlc: 'build',
    cat: 'Review',
    roles: [],
    prompt: 'review PR #{pr} and summarize what changed, then list any concerns',
    slots: {
      pr: '247'
    },
    needs: 'gh',
    nextHref: '/en/code-review',
    src: 'workflows'
  }, {
    id: 'review-infrastructure-changes-before',
    sdlc: 'build',
    cat: 'Review',
    roles: ['security', 'ops'],
    paste: 'plan',
    prompt: 'here is my Terraform plan output. what is this going to do, and is anything here going to cause problems?',
    src: 'teams'
  }, {
    id: 'run-a-security-review',
    sdlc: 'build',
    cat: 'Review',
    roles: ['security'],
    prompt: 'use a subagent to review {path} for security issues and report what it finds',
    slots: {
      path: 'src/api/'
    },
    nextHref: '/en/sub-agents',
    src: 'best-practices'
  }, {
    id: 'review-content-before-sending',
    sdlc: 'build',
    cat: 'Review',
    roles: ['marketing', 'docs'],
    prompt: 'review {file} for {concerns} and list anything I should fix before it goes to {reviewer}',
    slots: {
      file: 'launch-post.md',
      concerns: 'unsupported claims, missing attributions, and brand-guideline issues',
      reviewer: 'legal'
    },
    nextHref: '/en/skills',
    src: 'legal'
  }, {
    id: 'course-correct-a-wrong',
    sdlc: 'build',
    cat: 'Steer',
    roles: [],
    prompt: 'that is not right: {feedback}. try a different approach',
    slots: {
      feedback: 'the function signature needs to stay backward-compatible'
    },
    nextHref: '/en/checkpointing',
    src: 'best-practices'
  }, {
    id: 'narrow-the-scope-of',
    sdlc: 'build',
    cat: 'Steer',
    roles: [],
    prompt: 'that is too much. keep only the changes to {scope} and undo your other edits',
    slots: {
      scope: 'the validation logic in src/forms/'
    },
    src: 'best-practices'
  }, {
    id: 'turn-a-correction-into',
    sdlc: 'build',
    cat: 'Steer',
    roles: [],
    prompt: 'you keep {mistake}. add a rule to CLAUDE.md so this stops happening',
    slots: {
      mistake: 'using default exports when this project uses named exports'
    },
    nextHref: '/en/memory',
    src: 'best-practices'
  }, {
    id: 'resolve-merge-conflicts',
    sdlc: 'ship',
    cat: 'Git',
    roles: [],
    prompt: 'resolve the merge conflicts in this branch and explain what you kept from each side',
    src: 'workflows'
  }, {
    id: 'commit-with-a-generated',
    sdlc: 'ship',
    cat: 'Git',
    roles: [],
    prompt: 'commit these changes with a message that summarizes what I did',
    src: 'workflows'
  }, {
    id: 'open-a-pull-request',
    sdlc: 'ship',
    cat: 'Git',
    roles: [],
    prompt: 'find the {tracker} ticket about {topic} and open a PR that implements it',
    slots: {
      tracker: 'Linear',
      topic: 'the login timeout'
    },
    needs: 'tracker',
    src: 'workflows'
  }, {
    id: 'draft-release-notes-from',
    sdlc: 'ship',
    cat: 'Release',
    roles: ['pm', 'docs', 'marketing'],
    prompt: 'compare {from} to {to} and draft release notes grouped by feature, fix, and breaking change',
    slots: {
      from: 'v2.3.0',
      to: 'v2.4.0'
    },
    nextHref: '/en/skills',
    src: 'workflows'
  }, {
    id: 'write-a-ci-workflow',
    sdlc: 'ship',
    cat: 'Release',
    roles: ['ops'],
    prompt: 'write a GitHub Actions workflow that {steps} on every push to {branch}',
    slots: {
      steps: 'runs the tests and deploys to staging',
      branch: 'main'
    },
    src: 'workflows'
  }, {
    id: 'find-and-fix-a',
    sdlc: 'operate',
    cat: 'Debug',
    startN: 3,
    roles: [],
    prompt: 'the {test} test is failing, find out why and fix it',
    slots: {
      test: 'UserAuth'
    },
    src: 'workflows'
  }, {
    id: 'investigate-a-reported-error',
    sdlc: 'operate',
    cat: 'Debug',
    roles: ['ops'],
    prompt: 'users are seeing {symptom} on {where}. investigate and tell me what is going on',
    slots: {
      symptom: '500 errors',
      where: '/api/settings'
    },
    nextHref: '/en/web-quickstart#pre-fill-sessions',
    src: 'workflows'
  }, {
    id: 'fix-a-build-error',
    sdlc: 'operate',
    cat: 'Debug',
    roles: ['ops'],
    paste: 'error',
    prompt: 'here is a build error. fix the root cause and verify the build succeeds',
    src: 'best-practices'
  }, {
    id: 'investigate-a-production-incident',
    sdlc: 'operate',
    cat: 'Incident',
    roles: ['ops', 'security'],
    prompt: '{symptom}. check the logs, recent deploys, and config changes, then tell me the most likely cause',
    slots: {
      symptom: 'the checkout endpoint started returning 500s an hour ago'
    },
    nextHref: '/en/mcp',
    src: 'workflows'
  }, {
    id: 'diagnose-from-a-console',
    sdlc: 'operate',
    cat: 'Incident',
    roles: ['ops', 'data'],
    paste: 'screenshot',
    prompt: 'here is a screenshot of {console}. walk me through why {resource} is failing and give me the exact commands to fix it',
    slots: {
      console: 'the GCP Kubernetes dashboard',
      resource: 'this pod'
    },
    src: 'teams'
  }, {
    id: 'query-logs-in-plain',
    sdlc: 'operate',
    cat: 'Incident',
    roles: ['security', 'ops', 'data'],
    prompt: 'show me all {events} for {scope} over {timeframe}. write the query, run it, and tell me what stands out',
    slots: {
      events: 'failed logins',
      scope: 'the auth service',
      timeframe: 'the past 24 hours'
    },
    needs: 'db',
    src: 'cybersecurity'
  }, {
    id: 'analyze-a-data-file',
    sdlc: 'operate',
    cat: 'Data',
    roles: ['data', 'pm', 'marketing'],
    paste: 'csv',
    prompt: 'read {file}, summarize the key patterns, and write the results to {output}',
    slots: {
      file: '@reports/q1-signups.csv',
      output: 'an HTML page with charts, then open it in my browser'
    },
    nextHref: '/en/mcp',
    src: 'teams'
  }, {
    id: 'generate-variations-from-performance',
    sdlc: 'operate',
    cat: 'Data',
    roles: ['marketing', 'data'],
    paste: 'csv',
    prompt: 'read {file}, find the underperforming {items}, and generate {n} new variations that stay under {limit} characters',
    slots: {
      file: '@ads-performance.csv',
      items: 'headlines',
      n: '20',
      limit: '90'
    },
    nextHref: '/en/mcp',
    src: 'teams'
  }, {
    id: 'turn-a-recurring-task',
    sdlc: 'operate',
    cat: 'Automate',
    roles: [],
    prompt: 'create a /{name} skill for this project that {steps}',
    slots: {
      name: 'ship',
      steps: 'runs the linter and tests, then drafts a commit message'
    },
    src: 'workflows'
  }, {
    id: 'add-a-hook-for',
    sdlc: 'operate',
    cat: 'Automate',
    roles: [],
    prompt: 'write a hook that {action} after every {event}',
    slots: {
      action: 'runs prettier',
      event: 'edit to a .ts or .tsx file'
    },
    src: 'best-practices'
  }, {
    id: 'connect-a-tool-with',
    sdlc: 'operate',
    cat: 'Automate',
    roles: [],
    prompt: 'set up the {server} MCP server so you can read my {data} directly',
    slots: {
      server: 'Sentry',
      data: 'error reports'
    },
    src: 'workflows'
  }, {
    id: 'capture-what-to-remember',
    sdlc: 'operate',
    cat: 'Automate',
    roles: ['pm', 'docs'],
    prompt: 'summarize what we did this session and suggest what to add to CLAUDE.md',
    src: 'teams'
  }], []);
  const PROMPTS = useMemo(() => {
    if (typeof window !== 'undefined') {
      const rawIds = new Set(RAW.map(p => p.id));
      RAW.forEach(p => {
        if (!text[p.id]) console.warn('[prompt-library] no text[] entry for id:', p.id);
      });
      Object.keys(text).forEach(k => {
        if (!rawIds.has(k)) console.warn('[prompt-library] orphaned text[] key:', k);
      });
    }
    return RAW.map(p => ({
      ...p,
      title: p.id,
      teaches: '',
      ...text[p.id] || ({})
    }));
  }, [RAW, text]);
  const L = labels;
  const TL = k => tagLabels[k] || k;
  const CAT_TAG = useMemo(() => ({
    Onboard: 'understand',
    Understand: 'understand',
    Plan: 'plan',
    Prototype: 'prototype',
    Implement: 'build',
    Test: 'test',
    Refactor: 'refactor',
    Review: 'review',
    Steer: 'steer',
    Git: 'git',
    Release: 'release',
    Debug: 'debug',
    Incident: 'debug',
    Data: 'data',
    Automate: 'automate'
  }), []);
  const TAGS = useMemo(() => ['understand', 'plan', 'prototype', 'build', 'test', 'refactor', 'review', 'steer', 'debug', 'git', 'release', 'data', 'automate', 'pm', 'design', 'docs', 'marketing', 'security', 'ops'], []);
  const tagsOf = p => [CAT_TAG[p.cat], ...p.roles || []];
  const doc = useMemo(() => {
    const p = typeof window !== 'undefined' ? window.location.pathname : '';
    const base = p.startsWith('/docs/') ? '/docs' : '';
    const m = p.slice(base.length).match(/^\/([a-z]{2}(?:-[A-Z]{2})?)\//);
    const locale = m ? m[1] : 'en';
    return href => {
      if (!href || href[0] !== '/' || href[1] === '/') return href;
      return base + (href.startsWith('/en/') ? '/' + locale + href.slice(3) : href);
    };
  }, []);
  const linkify = s => {
    const out = [];
    let last = 0;
    const re = /\[([^\]]+)\]\(([^)]+)\)/g;
    for (let m; m = re.exec(s); ) {
      if (m.index > last) out.push(s.slice(last, m.index));
      out.push(<a key={m.index} href={doc(m[2])}>{m[1]}</a>);
      last = re.lastIndex;
    }
    if (last < s.length) out.push(s.slice(last));
    return out;
  };
  const codeify = s => s.split(/(`[^`]+`)/g).map((part, i) => part[0] === '`' ? <code key={i}>{part.slice(1, -1)}</code> : part);
  const SOURCES = useMemo(() => ({
    'workflows': '/en/common-workflows',
    'teams': 'https://claude.com/blog/how-anthropic-teams-use-claude-code',
    'legal': 'https://claude.com/blog/how-anthropic-uses-claude-legal',
    'cybersecurity': 'https://claude.com/blog/how-anthropic-uses-claude-cybersecurity',
    'best-practices': '/en/best-practices',
    'ebook': 'https://resources.anthropic.com/hubfs/Scaling%20agentic%20coding%20across%20your%20organization.pdf'
  }), []);
  const [mounted, setMounted] = useState(false);
  const [q, setQ] = useState('');
  const [start, setStart] = useState(true);
  const [sel, setSel] = useState(null);
  const [openId, setOpenId] = useState(null);
  const [copied, setCopied] = useState(null);
  const [fills, setFills] = useState({});
  const copyTimer = useRef(null);
  useEffect(() => {
    setMounted(true);
    return () => clearTimeout(copyTimer.current);
  }, []);
  const setFill = (id, key, val) => setFills(f => ({
    ...f,
    [id + '.' + key]: val
  }));
  const fillOf = (p, key) => {
    const v = fills[p.id + '.' + key];
    return v !== undefined ? v : p.slots && p.slots[key] !== undefined ? p.slots[key] : '';
  };
  const assemble = p => p.prompt.replace(/\{(\w+)\}/g, (_, k) => fillOf(p, k) || p.slots && p.slots[k] || k);
  const preview = p => p.prompt.replace(/\{(\w+)\}/g, (_, k) => p.slots && p.slots[k] || k);
  const bodyText = p => preview(p) + ' ' + p.teaches.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') + ' ' + (p.next || '');
  const widthFor = s => (s || '').length + 3 + 'ch';
  const ql = q.trim().toLowerCase();
  const toggleTag = k => {
    setStart(false);
    setSel(s => !ql && s === k ? null : k);
  };
  const clear = () => {
    setStart(false);
    setSel(null);
    setQ('');
  };
  const results = useMemo(() => {
    const list = PROMPTS.filter(p => {
      if (ql) return p.title.toLowerCase().includes(ql) || bodyText(p).toLowerCase().includes(ql);
      if (start) return !!p.startN;
      if (sel) return tagsOf(p).includes(sel);
      return true;
    });
    if (ql) return list;
    if (start) return list.sort((a, b) => a.startN - b.startN);
    if (sel) return list.sort((a, b) => (a.roles || []).length - (b.roles || []).length || (b.sdlc === 'operate') - (a.sdlc === 'operate'));
    return list;
  }, [PROMPTS, ql, start, sel]);
  const matchSnippet = p => {
    if (!ql || p.title.toLowerCase().includes(ql)) return null;
    const txt = bodyText(p);
    const at = txt.toLowerCase().indexOf(ql);
    if (at < 0) return null;
    const lo = Math.max(0, at - 30), hi = Math.min(txt.length, at + ql.length + 50);
    return [lo > 0 ? '…' : '', txt.slice(lo, at), <mark key="m">{txt.slice(at, at + ql.length)}</mark>, txt.slice(at + ql.length, hi), hi < txt.length ? '…' : ''];
  };
  const grouped = useMemo(() => {
    if (start && !q.trim()) return [];
    const g = {};
    for (const p of results) {
      const key = p.sdlc + '|' + p.cat;
      (g[key] = g[key] || ({
        sdlc: p.sdlc,
        cat: p.cat,
        items: []
      })).items.push(p);
    }
    return Object.values(g);
  }, [results, start, q]);
  const copy = async (str, id) => {
    try {
      await navigator.clipboard.writeText(str);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = str;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    clearTimeout(copyTimer.current);
    setCopied(id);
    copyTimer.current = setTimeout(() => setCopied(null), 1600);
  };
  const promptBody = p => {
    if (!p.slots) return <code>{p.prompt}</code>;
    const parts = p.prompt.split(/(\{\w+\})/g);
    return <code>
        {parts.map((part, idx) => {
      const m = part.match(/^\{(\w+)\}$/);
      if (!m) return <span key={idx}>{part}</span>;
      const k = m[1];
      const val = fillOf(p, k);
      return <input key={idx} type="text" className="pl-slot" value={val} placeholder={p.slots[k] || k} aria-label={k} style={{
        width: widthFor(val || p.slots[k])
      }} onChange={e => setFill(p.id, k, e.target.value)} onFocus={e => e.target.select()} onClick={e => e.stopPropagation()} />;
    })}
      </code>;
  };
  const card = p => {
    const open = openId === p.id;
    const srcHref = SOURCES[p.src];
    const srcLabel = sourceLabels[p.src];
    const snip = matchSnippet(p);
    return <div key={p.id} className={'pl-card' + (open ? ' pl-open' : '')}>
        <button type="button" className="pl-head" onClick={() => setOpenId(open ? null : p.id)} aria-expanded={open}>
          <span className="pl-title">{p.title}</span>
          {!!p.startN && <span className="pl-chip">{L.startHere} · {p.startN}</span>}
        </button>
        {snip ? <div className="pl-match">{snip}</div> : <code className="pl-prompt-preview">{preview(p)}</code>}
        {open && <div className="pl-body">
            <div className="pl-label">{p.slots ? L.fillAndCopy : L.copyThis}</div>
            {p.needs && L.needs && L.needs[p.needs] && <div className="pl-hint pl-needs">
                <span className="pl-needs-label">{L.needsLabel}</span> {linkify(L.needs[p.needs])}
              </div>}
            {p.paste && L.paste && L.paste[p.paste] && <div className="pl-hint pl-paste">{L.paste[p.paste]}</div>}
            {p.slots && <div className="pl-hint">
                {L.hintBefore} <span className="pl-hint-chip">{L.hintChip}</span> {L.hintAfter}
              </div>}
            <div className="pl-prompt-box">
              <span className="pl-caret">{'❯'}</span>
              {promptBody(p)}
              <button type="button" className="pl-copy" onClick={() => copy(assemble(p), p.id)}>
                {copied === p.id ? L.copied : L.copy}
              </button>
            </div>
            <div className="pl-label">{L.whyWorks}</div>
            <div className="pl-teaches">{linkify(p.teaches)}</div>
            {p.nextHref && p.next && <div className="pl-next">
                <span className="pl-next-label">{L.makeItStick}</span>
                <a href={doc(p.nextHref)}>{codeify(p.next)} →</a>
              </div>}
            {srcLabel && <div className="pl-src">{L.from} {srcHref ? <a href={doc(srcHref)}>{srcLabel}</a> : srcLabel}</div>}
          </div>}
      </div>;
  };
  const STYLES = useMemo(() => `
.pl {
  --pl-accent: #D97757;
  --pl-accent-bg: rgba(217,119,87,0.07);
  --pl-bg: #fff;
  --pl-surface: #FAFAF7;
  --pl-border: #E8E6DC;
  --pl-border-subtle: rgba(31,30,29,0.08);
  --pl-text: #141413;
  --pl-text-2: #5E5D59;
  --pl-text-3: #73726C;
  --pl-text-4: #9C9A92;
  --pl-mono: var(--font-mono, ui-monospace, SFMono-Regular, Menlo, monospace);
  font-family: 'Anthropic Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px; color: var(--pl-text); margin: 8px 0 32px;
}
.dark .pl {
  --pl-bg: #1f1e1d;
  --pl-surface: #262624;
  --pl-border: #3d3d3a;
  --pl-border-subtle: rgba(240,238,230,0.08);
  --pl-text: #f0eee6;
  --pl-text-2: #bfbdb4;
  --pl-text-3: #91908a;
  --pl-text-4: #73726c;
}
.pl *, .pl *::before, .pl *::after { box-sizing: border-box; }
.pl button { font-family: inherit; cursor: pointer; }
.pl a { color: var(--pl-accent); text-decoration: none; }
.pl a:hover { text-decoration: underline; }

.pl-search {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 18px; background: var(--pl-surface);
  border: 1px solid var(--pl-border); border-radius: 12px;
  margin-bottom: 14px;
}
.pl-search input {
  flex: 1; border: none; outline: none; background: transparent;
  font-size: 16px; color: var(--pl-text);
}
.pl-search input::placeholder { color: var(--pl-text-4); }

.pl-tags { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 18px; }
.pl-tag {
  padding: 7px 14px; border: 1px solid var(--pl-border); background: var(--pl-bg);
  font-size: 14px; color: var(--pl-text-2); border-radius: 999px;
}
.pl-tag:hover { background: var(--pl-surface); }
.pl-tag.pl-on { background: var(--pl-text); border-color: var(--pl-text); color: var(--pl-bg); }
.pl-tag.pl-start { color: var(--pl-accent); font-weight: 500; }
.pl-tag.pl-start.pl-on { background: var(--pl-accent); border-color: var(--pl-accent); color: #fff; }
.pl-tags.pl-dim .pl-tag { opacity: 0.5; }
.pl-tags.pl-dim .pl-tag:hover { opacity: 1; }
.pl-sep { width: 1px; height: 22px; background: var(--pl-border); margin: 0 4px; }
.pl-clear { border: none; background: none; font-size: 13px; color: var(--pl-text-4); padding: 4px 6px; }
.pl-clear:hover { color: var(--pl-text-2); }
.pl-count { margin-left: auto; font-size: 14px; color: var(--pl-text-4); }

.pl-group-h {
  font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--pl-text-4); margin: 24px 0 12px;
}
.pl-group-h .pl-phase { color: var(--pl-text-3); }
.pl-card {
  border: 1px solid var(--pl-border-subtle); border-radius: 10px;
  margin-bottom: 12px; background: var(--pl-bg); overflow: hidden;
  padding: 14px 18px;
}
.pl-card.pl-open { border-color: var(--pl-border); background: var(--pl-surface); }
.pl-head {
  width: 100%; display: flex; align-items: baseline; gap: 12px;
  border: none; background: transparent; text-align: left; padding: 0;
}
.pl-head:focus-visible { outline: 2px solid var(--pl-accent); outline-offset: 2px; border-radius: 6px; }
.pl-title {
  flex: 1; font-size: 17px; font-weight: 500; color: var(--pl-text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.pl-prompt-preview {
  display: block; font-family: var(--pl-mono); font-size: 13.5px; color: var(--pl-text-3);
  margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.pl-chip {
  font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase;
  padding: 3px 9px; border-radius: 999px; flex-shrink: 0;
  background: var(--pl-accent-bg); color: var(--pl-accent);
}

.pl-body { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--pl-border-subtle); }
.pl-label {
  font-size: 11.5px; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--pl-text-4); margin: 12px 0 8px;
}
.pl-prompt-box {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 16px; background: #141413; color: #f0eee6;
  border-radius: 8px; font-family: var(--pl-mono); font-size: 15px;
}
.pl-caret { color: var(--pl-accent); flex-shrink: 0; }
.pl-prompt-box code { flex: 1; background: none; padding: 0; color: inherit; white-space: pre-wrap; line-height: 1.9; }
.pl-slot {
  font-family: var(--pl-mono); font-size: inherit;
  background: rgba(217,119,87,0.15); color: #f0eee6;
  border: none; border-bottom: 1.5px dashed var(--pl-accent);
  border-radius: 4px 4px 0 0; padding: 2px 6px; margin: 0 1px;
  outline: none; min-width: 6ch; max-width: 100%;
  box-sizing: content-box; cursor: text;
}
.pl-slot:hover { background: rgba(217,119,87,0.22); }
.pl-slot:focus { background: rgba(217,119,87,0.28); border-bottom-style: solid; }
.pl-slot::placeholder { color: rgba(240,238,230,0.4); font-style: italic; }
.pl-hint { font-size: 14px; color: var(--pl-text-3); margin: 0 0 10px; }
.pl-paste { color: var(--pl-text-2); }
.pl-needs { color: var(--pl-text-2); }
.pl-needs-label {
  display: inline-block; font-size: 10.5px; letter-spacing: 0.06em;
  text-transform: uppercase; padding: 2px 7px; margin-right: 6px;
  border-radius: 4px; background: var(--pl-accent-bg); color: var(--pl-accent);
}
.pl-hint-chip {
  font-family: var(--pl-mono); font-size: 0.92em;
  background: var(--pl-accent-bg); color: var(--pl-accent);
  border-bottom: 1.5px dashed var(--pl-accent);
  border-radius: 3px 3px 0 0; padding: 1px 5px;
}
.pl-copy {
  font-size: 12.5px; padding: 6px 12px; border-radius: 6px;
  background: var(--pl-accent); color: #fff; border: none; flex-shrink: 0;
}
.pl-teaches { display: block; font-size: 15.5px; color: var(--pl-text-2); margin: 4px 0 0; line-height: 1.6; }
.pl-match {
  display: block; font-size: 13.5px; color: var(--pl-text-3);
  margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.pl-match mark { background: var(--pl-accent-bg); color: var(--pl-text); padding: 1px 2px; border-radius: 3px; }
.pl-next {
  display: flex; align-items: baseline; gap: 10px;
  margin: 14px 0 0; padding: 10px 12px;
  background: var(--pl-accent-bg); border-radius: 8px; font-size: 14.5px;
}
.pl-next-label {
  font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--pl-accent); font-weight: 600; flex-shrink: 0;
}
.pl-src { display: block; font-size: 14px; color: var(--pl-text-4); margin: 14px 0 0; }

.pl-show-all {
  display: block; width: 100%; padding: 14px; margin-top: 4px;
  border: 1px dashed var(--pl-border); border-radius: 10px;
  background: transparent; font-size: 15px; color: var(--pl-accent);
  text-align: center;
}
.pl-show-all:hover { background: var(--pl-accent-bg); border-style: solid; }

.pl-empty {
  padding: 32px; text-align: center; color: var(--pl-text-4);
  border: 1px dashed var(--pl-border); border-radius: 10px;
}
`, []);
  if (!mounted) return <div className="pl" style={{
    minHeight: 480
  }} />;
  return <div className="pl">
      <style>{STYLES}</style>

      <div className="pl-search">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{
    color: 'var(--pl-text-4)'
  }}>
          <circle cx="11" cy="11" r="7" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input type="text" placeholder={L.search} value={q} onChange={e => {
    setQ(e.target.value);
    if (e.target.value) setStart(false);
  }} aria-label={L.search} />
      </div>

      <div className={'pl-tags' + (ql ? ' pl-dim' : '')}>
        <button type="button" className={'pl-tag pl-start' + (!ql && start ? ' pl-on' : '')} onClick={() => {
    setQ('');
    setStart(!start);
    if (!start) setSel(null);
  }}>
          ★ {L.startHere}
        </button>
        <span className="pl-sep" />
        {TAGS.map(k => <button key={k} type="button" aria-pressed={!ql && sel === k} className={'pl-tag' + (!ql && sel === k ? ' pl-on' : '')} onClick={() => {
    setQ('');
    toggleTag(k);
  }}>
            {TL(k)}
          </button>)}
        {(start || sel || q) && <button type="button" className="pl-clear" onClick={clear}>{L.clear}</button>}
        <span className="pl-count">{results.length} {results.length === 1 ? L.prompt : L.prompts}</span>
      </div>

      {results.length === 0 ? <div className="pl-empty">
          {L.noMatch} {ql ? <code>{q}</code> : null} <button type="button" className="pl-clear" onClick={clear}>{L.clear}</button>
        </div> : !ql && start ? <div>
          <div className="pl-group-h">{L.startHereHeader}</div>
          {results.map(card)}
          <button type="button" className="pl-show-all" onClick={clear}>
            {L.showAll && L.showAll.replace('{n}', PROMPTS.length)} →
          </button>
        </div> : grouped.map(g => <div key={g.sdlc + '|' + g.cat}>
            <div className="pl-group-h"><span className="pl-phase">{phaseLabels[g.sdlc] || g.sdlc}</span> · {catLabels[g.cat] || g.cat}</div>
            {g.items.map(card)}
          </div>)}
    </div>;
};

これは Claude Code にコピーして使用するプロンプトのライブラリです。試したことのない作業方法を探索したり、どこから始めたらよいかわからない場合に使用してください。

プロンプトは、[一般的なワークフロー](/docs/ja/common-workflows)、[ベストプラクティス](/docs/ja/best-practices)、[Anthropic チームが Claude Code をどのように使用しているか](https://claude.com/blog/how-anthropic-teams-use-claude-code)など、様々な Anthropic ガイドから収集されています。これらはスクリプトではなく、出発点です。任意のプロンプトの下にある **このプロンプトが機能する理由** を開くと、その背後にあるパターンを確認できるため、独自のプロンプトを作成できます。

export const labels = {
  startHere: "ここから始める",
  startHereHeader: "最初に試すべき 5 つのプロンプト",
  showAll: "{n} 個のプロンプトをすべて表示",
  search: "プロンプトを検索…",
  clear: "クリア",
  prompt: "プロンプト",
  prompts: "プロンプト",
  noMatch: "一致するプロンプトがありません",
  fillAndCopy: "入力してコピー",
  copyThis: "このプロンプトをコピー",
  hintBefore: "次の",
  hintChip: "ハイライト",
  hintAfter: "フィールドに入力してからコピーしてください。",
  copy: "コピー",
  copied: "コピーしました",
  whyWorks: "このプロンプトが機能する理由",
  makeItStick: "記憶に残す",
  from: "出典",
  paste: {
    mockup: "モックアップ画像をペースト、ドラッグ、または @-mention してから、以下を送信してください:",
    design: "デザイン画像をペースト、ドラッグ、または @-mention してから、以下を送信してください:",
    screenshot: "スクリーンショットをペースト、ドラッグ、または @-mention してから、以下を送信してください:",
    plan: "プラン出力をプロンプトに最初にペーストしてから、以下を送信してください:",
    error: "エラー出力をプロンプトに最初にペーストしてから、以下を送信してください:",
    csv: "ファイルをプロンプトにドラッグするか、以下のパスを独自の @-mention に置き換えてください:"
  },
  needsLabel: "必要なもの",
  needs: {
    tracker: "[claude.ai コネクタ](/docs/ja/mcp#use-mcp-servers-from-claude-ai)または [MCP サーバー](/docs/ja/mcp)として追加されたイシュートラッカー。",
    gh: "[gh CLI](https://cli.github.com) が認証されているか、GitHub が [claude.ai コネクタ](/docs/ja/mcp#use-mcp-servers-from-claude-ai)として追加されていること。",
    browser: "Claude が結果をレンダリングしてスクリーンショットを撮る方法。[デスクトップアプリ](/docs/ja/desktop#preview-your-app)にはこれが組み込まれています。ターミナルでは、[Chrome 拡張機能](/docs/ja/chrome)または Playwright [MCP](/docs/ja/mcp) サーバーをインストールしてください。",
    db: "[claude.ai コネクタ](/docs/ja/mcp#use-mcp-servers-from-claude-ai)または [MCP サーバー](/docs/ja/mcp)として追加されたデータウェアハウスまたはログストア。"
  }
};

export const tagLabels = {
  understand: "理解",
  plan: "計画",
  prototype: "プロトタイプ",
  build: "構築",
  test: "テスト",
  refactor: "リファクタリング",
  review: "レビュー",
  steer: "操舵",
  debug: "デバッグ",
  git: "Git",
  release: "リリース",
  data: "データ",
  automate: "自動化",
  pm: "プロダクト",
  design: "デザイン",
  docs: "ドキュメント",
  marketing: "マーケティング",
  security: "セキュリティ",
  ops: "オンコール"
};

export const phaseLabels = {
  discover: "発見",
  design: "設計",
  build: "構築",
  ship: "リリース",
  operate: "運用"
};

export const sourceLabels = {
  workflows: "一般的なワークフロー",
  teams: "Anthropic チームが Claude Code をどのように使用しているか",
  legal: "Anthropic が法務で Claude をどのように使用しているか",
  cybersecurity: "Anthropic がサイバーセキュリティで Claude をどのように使用しているか",
  "best-practices": "ベストプラクティス",
  ebook: "agentic coding スケーリングガイド"
};

export const catLabels = {
  Onboard: "オンボード",
  Understand: "理解",
  Plan: "計画",
  Prototype: "プロトタイプ",
  Implement: "実装",
  Test: "テスト",
  Refactor: "リファクタリング",
  Review: "レビュー",
  Steer: "操舵",
  Git: "Git",
  Release: "リリース",
  Debug: "デバッグ",
  Incident: "インシデント",
  Data: "データ",
  Automate: "自動化"
};

export const text = {
  "get-oriented-in-a": {
    title: "新しいリポジトリで方向性を確認する",
    teaches: "読むべきファイルではなく、知りたいことを説明してください。Claude はプロジェクトを独自に探索し、それがどのように組み合わさっているかの概要を返します。",
    next: "`/init` を実行して `CLAUDE.md` をセットアップし、Claude がこれを毎回のセッションで覚えるようにしてください"
  },
  "explain-unfamiliar-code": {
    title: "なじみのないコードを説明する",
    teaches: "ファイル名を指定し、答えてほしい形式を言ってください。HTML ページを図、箇条書き、または学習方法に合ったものに置き換えてください。",
    next: "出力スタイルを設定して、Claude が常に好みの形式で説明するようにしてください"
  },
  "find-where-something-happens": {
    title: "何かが起こる場所を見つける",
    teaches: "ファイル名ではなく動作で検索してください。ファイルの名前やディレクトリの場所がわからない場合でも、検索は機能します。"
  },
  "see-what-depends-on": {
    title: "削除する前に何が壊れるかを確認する",
    teaches: "何かを削除する前に尋ねてください。呼び出し元と下流への影響のリストは、1 行のクリーンアップを見ているのか、調整が必要な変更を見ているのかを示します。"
  },
  "trace-how-code-evolved": {
    title: "コードがどのように進化したかを追跡する",
    teaches: "質問が「何」ではなく「なぜ」の場合は、コミット履歴を指してください。Claude はどのバージョン管理を使用していても、ログと blame を読み、現在の実装の背後にある決定を説明します。"
  },
  "scope-a-change-before": {
    title: "開始する前に変更の範囲を決定する",
    teaches: "ロードマップにコミットする前に作業をサイズ化してください。ファイルリストは、1 つのコンポーネントを見ているのか、クロスカッティング変更を見ているのかを示します。"
  },
  "ask-the-codebase-a": {
    title: "コードベースにプロダクト質問をする",
    teaches: "役割を述べて、答えが適切なレベルで提供されるようにしてください。Claude はソースコードから実際に何をするかを説明し、読む必要はありません。",
    next: "出力スタイルを設定して、Claude が常にこのレベルで答えを提供するようにしてください"
  },
  "plan-a-multi-file": {
    title: "コードに触れる前に複数ファイルの変更を計画する",
    teaches: "「まだ編集しないでください」を追加すると、探索と変更が分離されるため、コードが移動する前にアプローチが表示されます。すべてのプロンプトでプラン優先をデフォルトにするには、Shift+Tab を押して [プランモード](/docs/ja/permission-modes#analyze-before-you-edit-with-plan-mode)を使用してください。"
  },
  "draft-a-spec-by": {
    title: "インタビューでスペックを作成する",
    teaches: "スペックを自分で書く代わりに、インタビューを受けるよう依頼してください。Claude は要件が完全になるまで構造化された質問をし、その後、結果をファイルに書き込みます。",
    next: "インタビュー質問を `/spec` スキルとして保存して、すべてのスペックが同じ方法で開始されるようにしてください"
  },
  "turn-a-meeting-into": {
    title: "ミーティングをチケットに変換する",
    teaches: "トランスクリプションステップをスキップしてください。Claude は非構造化入力からアクション項目を抽出し、[MCP](/docs/ja/mcp)経由でトラッカーに直接書き込むため、トランスクリプトではなくチケットをレビューします。",
    next: "これを `/tickets` スキルとして保存してください"
  },
  "map-edge-cases-before": {
    title: "構築する前にエッジケースをマップする",
    teaches: "そこにあるものではなく、欠けているものを尋ねてください。Claude はエラー状態、空の状態、ハッピーパス設計が傾向としてスキップするエッジケースをリストアップします。"
  },
  "turn-a-mockup-into": {
    title: "モックアップを動作するプロトタイプに変換する",
    teaches: "クリック可能なプロトタイプは、静的モックアップが答えられない質問に答えます。ドキュメントで相互作用を説明する代わりに、動作するコードをエンジニアリングに渡してください。"
  },
  "implement-from-a-screenshot": {
    title: "スクリーンショットから実装して自己チェックする",
    teaches: "これは Claude に検証ループを提供します。レンダリングし、ソース画像と比較し、各ギャップを指摘することなく反復します。",
    next: "`/goal` を使用して、Claude がスクリーンショットが一致するまで反復し続けるようにしてください"
  },
  "follow-an-existing-pattern": {
    title: "既存のパターンに従う",
    teaches: "既に気に入っているコードを指してください。参照がないと、Claude は一般的なベストプラクティスにデフォルト設定されます。参照があると、コードベースが実際に使用する規約に一致します。",
    next: "Claude に、従ったパターンを `CLAUDE.md` に書き込むよう依頼して、将来のセッションが参照なしで一致するようにしてください"
  },
  "add-a-small-well": {
    title: "小さく、明確に定義された機能を追加する",
    teaches: "構築方法ではなく、入力と出力を述べてください。Claude は同様のコードが存在する場所を見つけ、その横に追加します。"
  },
  "build-a-small-internal": {
    title: "小さな内部ツールをゼロから構築する",
    teaches: "プロジェクト、フレームワーク、またはビルドステップは必要ありません。ツールを説明し、Claude に開くよう依頼して、すぐに動作を確認してください。"
  },
  "work-an-issue-end": {
    title: "イシューをエンドツーエンドで処理する",
    teaches: "概要ではなく、イシュー番号を指定してください。Claude はチケット全体を読むため、言及し忘れた要件が含まれ、変更を報告する前に検証します。"
  },
  "find-and-update-copy": {
    title: "コードベース全体でコピーを見つけて更新する",
    teaches: "バリエーションを尋ね、スキップするものを言ってください。Claude はリテラル検索が見落とすフレーズングを見つけ、テストフィクスチャと履歴をそのままにしておくため、ユーザーが実際に見るコピーのみをレビューします。"
  },
  "draft-from-past-examples": {
    title: "過去の例からドキュメントを作成する",
    teaches: "スタイルを説明する代わりに、完成した作業のフォルダを指してください。Claude は既に出荷したものからスタイルと声を学ぶため、最初のドラフトはあなたのものの 1 つのように読めます。",
    next: "声をスキルとして保存して、すべてのドラフトがそこから開始されるようにしてください"
  },
  "write-tests-run-them": {
    title: "テストを書き、実行し、失敗を修正する",
    teaches: "書き込み、実行、修正を一緒に依頼して、Claude が指示を待たずに反復するようにしてください。",
    next: "`/init` を実行して、Claude がテストコマンドを自動的に学習するようにしてください"
  },
  "drive-implementation-from-tests": {
    title: "テストから実装を駆動する",
    teaches: "テスト駆動開発: テストは作業が完了したときを定義し、Claude は合格するまで実装を反復します。"
  },
  "fill-gaps-from-a": {
    title: "カバレッジレポートからギャップを埋める",
    teaches: "何がテストされていないかを推測する代わりに、カバレッジレポートを指してください。Claude は実際の数字を読み、最も必要なファイルのテストを書きます。",
    next: "これを `/goal` として設定して、Claude がカバレッジがターゲットに達するまでテストを書き続けるようにしてください"
  },
  "port-code-between-languages": {
    title: "コードを別の言語に移植する",
    teaches: "ターゲット言語だけでなく、保持するものを言ってください。保持する必要がある API または動作に名前を付けると、Claude がポートをチェックするための契約が与えられます。"
  },
  "generate-docs-for-code": {
    title: "ドキュメント化されていないコードのドキュメントを生成する",
    teaches: "スコープと形式に名前を付けてください。Claude は欠けているものを見つけ、ファイルに既にある comment スタイルに一致するため、新しいドキュメントは残りのように読めます。"
  },
  "migrate-a-pattern-across": {
    title: "コードベース全体でパターンを移行する",
    teaches: "古いパターンと新しいパターンを説明してください。Claude に最初にすべての場所を識別するよう依頼すると、呼び出しサイトが応答にリストアップされるため、何も見落とされていないことを確認できます。"
  },
  "optimize-against-a-measurable": {
    title: "測定可能なターゲットに対して最適化する",
    teaches: "メトリックとターゲットを述べると、Claude に完了の明確な定義が与えられます。",
    next: "これを `/goal` として設定して、Claude がターゲットに達するまで測定と反復を続けるようにしてください"
  },
  "fix-a-precise-visual": {
    title: "正確なビジュアルバグを修正する",
    teaches: "正確なビジュアルフィードバックは正確な修正を得ます。正確な要素、測定、ビューポートを述べてください。",
    next: "プレビューツールを追加して、Claude がスクリーンショットを撮り、修正を自分で検証するようにしてください"
  },
  "review-your-changes-before": {
    title: "コミットする前に変更をレビューする",
    teaches: "問題が修正するのに安い間に問題をキャッチしてください。Claude は diff 行だけでなく、変更されたファイル全体を読むため、迅速な自己レビューが見落とす問題を見つけます。",
    next: "同じチェックを 1 つのコマンドで実行するために `/code-review` を実行してください"
  },
  "review-a-pull-request": {
    title: "プルリクエストをレビューする",
    teaches: "Claude は diff だけでなく、コードベース全体のコンテキストでレビューします。変更されたコードとそれが呼び出すものを読むため、diff のみのレビューが見落とす問題をキャッチします。",
    next: "Code Review ですべての PR に対してこれをオンにしてください"
  },
  "review-infrastructure-changes-before": {
    title: "適用する前にインフラストラクチャの変更をレビューする",
    teaches: "プラン出力は密集していてスキャンが難しいです。ペーストすると、実際に何が変わるかの平易な言語の概要が得られます。"
  },
  "run-a-security-review": {
    title: "サブエージェントでセキュリティレビューを実行する",
    teaches: "[サブエージェント](/docs/ja/sub-agents)は独自のコンテキストウィンドウで監査を実行し、概要を報告するため、長いセキュリティレビューがメインセッションを満たしません。組み込みの汎用サブエージェントは追加のセットアップなしでこれを処理します。",
    next: "チーム全体が使用できる専用のセキュリティレビューサブエージェントをセットアップしてください"
  },
  "review-content-before-sending": {
    title: "正式なレビューの前に問題をキャッチする",
    teaches: "人間が時間を費やす前に最初のパスを取得してください。チェックしたい懸念事項に名前を付けて、レビューが焦点を当てるようにしてから、見つけたものを修正して、よりクリーンなドラフトを送信してください。",
    next: "レビューチェックリストをスキルとしてキャプチャして、チーム全体が実行できるようにしてください"
  },
  "course-correct-a-wrong": {
    title: "間違ったアプローチを修正する",
    teaches: "それが間違っているだけでなく、Claude が見落とした制約に名前を付けてください。具体的な理由は、Claude に再試行時に満たすべき具体的な制約を与え、再度推測する代わりに。",
    next: "Esc を 2 回押して巻き戻しメニューを開き、コードと会話を復元して、再試行がクリーンに開始されるようにしてください"
  },
  "narrow-the-scope-of": {
    title: "変更の範囲を絞る",
    teaches: "方向が正しいが変更が広すぎる場合は、Claude にすべてを巻き戻すのではなく、その一部を保持するよう依頼してください。述べられた境界は、小さな修正がリファクタリングになるのを防ぎます。"
  },
  "turn-a-correction-into": {
    title: "修正をルールに変える",
    teaches: "チャットの修正はチーム全体と共有されません。プロジェクトの [CLAUDE.md](/docs/ja/memory)のルールはコミットすると共有され、Claude はすべてのセッションの開始時にそれを読みます。",
    next: "`/memory` を開いて、Claude が書いたものをレビューしてください"
  },
  "resolve-merge-conflicts": {
    title: "マージコンフリクトを解決する",
    teaches: "保持するマーカーではなく、望む状態を言ってください。推論を求めると、マージがレビュー可能になり、ブラックボックスではなくなります。"
  },
  "commit-with-a-generated": {
    title: "生成されたメッセージでコミットする",
    teaches: "Claude に diff からメッセージを導出させてください。リポジトリの既存のコミットスタイルに一致します。"
  },
  "open-a-pull-request": {
    title: "チケットからプルリクエストを開く",
    teaches: "トラッカー、エディタ、GitHub 間のコンテキストスイッチをスキップしてください。1 つのプロンプトがスペックを読み、変更を加え、PR を開きます。"
  },
  "draft-release-notes-from": {
    title: "git 履歴からリリースノートを作成する",
    teaches: "2 つの参照ポイントと望む構造を指定してください。Claude はそれらの間のコミットログを読み、編集できるチェンジログを作成します。",
    next: "これを `/changelog` スキルとして保存してください"
  },
  "write-a-ci-workflow": {
    title: "CI ワークフローを書く",
    teaches: "いつ実行すべきか、何をすべきかを説明してください。YAML はプロジェクトのビルドおよびテストコマンドに一致して生成されます。"
  },
  "find-and-fix-a": {
    title: "失敗したテストを見つけて修正する",
    teaches: "症状を説明してください。どのファイルが壊れているかを知る必要はありません。Claude はテストを実行して失敗を確認し、ソースに追跡して修正します。"
  },
  "investigate-a-reported-error": {
    title: "報告されたエラーを調査する",
    teaches: "症状と場所を説明してください。Claude は関連するコードパスを読み、可能性のある原因を追跡します。スタックトレースまたはログがあればペーストしてください。",
    next: "実行ブックに deeplink を入れて、このプロンプトが事前に入力された状態で Claude を開くようにしてください"
  },
  "fix-a-build-error": {
    title: "ビルドエラーを根本から修正する",
    teaches: "根本原因と検証を求めると、エラーを修正せずに抑制する表面レベルのパッチが防止されます。"
  },
  "investigate-a-production-incident": {
    title: "本番インシデントを調査する",
    teaches: "実行するステップではなく、相関させるエビデンスソースをリストアップしてください。Claude はログ、git 履歴、設定を一緒に読んで、原因を絞り込みます。",
    next: "Sentry またはログストアを MCP 経由で接続してください"
  },
  "query-logs-in-plain": {
    title: "平易な英語でログをクエリする",
    teaches: "SQL を書く代わりに、質問を尋ねてください。Claude はクエリを構築し、接続されたログに対して実行し、クエリと結果の両方を表示して、何が実行されたかを確認できるようにします。"
  },
  "diagnose-from-a-console": {
    title: "コンソールスクリーンショットから診断する",
    teaches: "クラウドコンソールは問題を表示しますが、修正するコマンドは表示しません。Claude はスクリーンショットを読み、ダッシュボードを実行する kubectl、gcloud、または aws コマンドに変換します。"
  },
  "analyze-a-data-file": {
    title: "データファイルを分析する",
    teaches: "1 回限りの質問は 1 回限りのスクリプトを必要としません。プロジェクトフォルダ内のファイルを指してください。Claude はそれを直接読み、パターンを見つけ、要求した場所に出力を書き込みます。",
    next: "ファイルをエクスポートする代わりに、MCP 経由でデータソースを接続してください"
  },
  "generate-variations-from-performance": {
    title: "パフォーマンスデータからバリエーションを生成する",
    teaches: "制約を最初に述べて、生成が制限内に留まるようにしてください。Claude はメトリックを読み、置き換えるものを選択し、制限に適合する代替案を生成します。",
    next: "ファイルをエクスポートする代わりに、MCP 経由で広告プラットフォームを接続してください"
  },
  "turn-a-recurring-task": {
    title: "繰り返しタスクをスキルに変える",
    teaches: "ステップに一度名前を付けてください。コマンドとして再利用してください。Claude はチーム内の誰でも実行できる [スキル](/docs/ja/skills)を書きます。"
  },
  "add-a-hook-for": {
    title: "繰り返し動作のためのフックを追加する",
    teaches: "フックは、覚えておく必要があるものではなく、動作を自動にします。トリガーとアクションを説明し、Claude が [フック](/docs/ja/hooks)設定を書きます。"
  },
  "connect-a-tool-with": {
    title: "MCP でツールを接続する",
    teaches: "毎回のセッションでデータをペーストする代わりに、ソースを一度接続してください。[MCP](/docs/ja/mcp)セットアップ後、Claude はそれについて尋ねるときにツールから直接読みます。"
  },
  "capture-what-to-remember": {
    title: "次回のために覚えておくべきことをキャプチャする",
    teaches: "忘れる前に尋ねてください。Claude はこのセッションで何を理解する必要があったかを知っており、次のセッションがその文脈で開始されるように [CLAUDE.md](/docs/ja/memory)エントリを提案します。"
  }
};

<PromptLibrary text={text} labels={labels} tagLabels={tagLabels} phaseLabels={phaseLabels} sourceLabels={sourceLabels} catLabels={catLabels} />

<h2 id="what-makes-these-prompts-work">
  これらのプロンプトを機能させるもの
</h2>

上記のプロンプトはいくつかのパターンを共有しています。それらを認識することは、ここで任意のプロンプトを独自のタスクに適応させるのに役立ちます。

**ステップではなく結果を説明してください。** 何をしたいかを言い、Claude にファイルを見つけさせてください。以下のプロンプトは、単一のファイルパスを名前付けなくても機能します。

```text theme={null}
add rate limiting to the public API and make sure existing tests still pass
```

**自分の作業をチェックする方法を与えてください。** 同じプロンプトで実行、テスト、比較、または検証を依頼して、Claude が 1 回の試行後に停止する代わりに反復するようにしてください。

```text theme={null}
write the migration, run it against the dev database, and confirm the schema matches
```

**参照を指してください。** 既存のファイル、テスト、またはパターンに名前を付けて、新しいコードが既に持っているものと一致するようにしてください。

```text theme={null}
add a settings page that follows the same layout as the profile page
```

**測定可能なターゲットを述べてください。** 目標がパフォーマンスまたはカバレッジの場合、メトリックとしきい値を指定して、完了が明確になるようにしてください。

```text theme={null}
get the bundle size under 200KB and show me what you removed
```

**アーティファクトを与えてください。** エラー、ログ、スクリーンショット、プラン出力をプロンプトに直接ペーストするか、`@` を入力してファイルを参照してください。Claude はあなたの説明ではなくソースを読みます。

```text theme={null}
why is the build failing? @build.log
```

**答えてほしい方法を言ってください。** 形式、長さ、または対象者に名前を付けて、説明がどのように使用するかに適合するようにしてください。すべての応答のデフォルトとして形式を作成するには、[出力スタイル](/docs/ja/output-styles)を設定してください。

```text theme={null}
explain how the payment retry logic works as an HTML page with a diagram, then open it in my browser
```

各パターンの詳細については、[ベストプラクティス](/docs/ja/best-practices)を参照してください。

<h2 id="where-these-come-from">
  これらはどこから来ているのか
</h2>

これらのプロンプトは、公開されている Anthropic リソースのパターンに基づいています。各カードはそのソースにリンクしています:

* [一般的なワークフロー](/docs/ja/common-workflows): コアタスクのステップバイステップガイド
* [ベストプラクティス](/docs/ja/best-practices): プロンプティングパターンとプロジェクトセットアップ
* [Anthropic チームが Claude Code をどのように使用しているか](https://claude.com/blog/how-anthropic-teams-use-claude-code): エンジニアリング、プロダクト、デザイン、データチームからの実際のワークフロー。[法務](https://claude.com/blog/how-anthropic-uses-claude-legal)、[マーケティング](https://claude.com/blog/how-anthropic-uses-claude-marketing)、[サイバーセキュリティ](https://claude.com/blog/how-anthropic-uses-claude-cybersecurity)の詳細なダイブ
* [agentic coding スケーリングガイド](https://resources.anthropic.com/hubfs/Scaling%20agentic%20coding%20across%20your%20organization.pdf): エンタープライズ採用ガイド

これらのパターンのビデオウォークスルーについては、Anthropic Academy の無料 [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action)コースを参照してください。

<h2 id="related-resources">
  関連リソース
</h2>

このページのプロンプトは出発点です。1 つがプロジェクトで機能したら、次のステップはそれを繰り返し可能にすることです。[スキル](/docs/ja/skills)として保存して、チーム内の誰でも `/command` として実行でき、Claude が学習したコンベンションを [CLAUDE.md](/docs/ja/memory)に記録して、すべてのセッションがその文脈で開始されるようにしてください。より大きなまたはより危険な変更については、[プランモード](/docs/ja/permission-modes#analyze-before-you-edit-with-plan-mode)は編集が発生する前にファイルリストを表示します。

チーム全体に Claude Code を導入している場合は、管理設定とポリシーについては [管理](/docs/ja/admin-setup)を、このワークがプランでどのように請求されるかについては [コストと使用状況](/docs/ja/costs)を参照してください。
