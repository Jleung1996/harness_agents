# DSH skill pack — 60 agent skills

A curated set of Agent Skills (`SKILL.md` format) installed and pruned during one
working session. Shares as-is: copy the folders, restart your assistant, done.

**60 skills · 528 files · 7.1 MB**

---

## Install

Skills are loaded from `~/.agents/skills/` — the Agent Skills standard directory.

**Windows (PowerShell):**

```powershell
Copy-Item .\skills\* "$env:USERPROFILE\.agents\skills\" -Recurse -Force
```

**macOS / Linux:**

```bash
mkdir -p ~/.agents/skills && cp -R ./skills/* ~/.agents/skills/
```

Then **restart your assistant session.** Skill catalogs are read at session start.

Verify it worked — you should see `ui-ux-pro-max` and `python-pro` in the list of
available skills.

If your client reads a different directory, point it at `./skills` or symlink:

| client | directory |
|---|---|
| DeepSeek Harness, universal / Agent Skills | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |

Nothing here is auto-run. Skills are markdown instructions loaded into the model's
context; they execute no code on install.

---

## What's inside

### 1. UI/UX suite — 7 skills

Source: **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** · MIT

| skill | what it does |
|---|---|
| `ui-ux-pro-max` | the big one: 79 styles, 192 product palettes, 74 font pairings, 119 UX guidelines, 22 stacks. Local BM25 search over bundled CSVs — no network, no API |
| `ui-styling` | shadcn/ui + Radix + Tailwind implementation |
| `design-system` | token architecture (primitive → semantic → component) |
| `slides` | HTML presentations with Chart.js |
| `design` | brand identity, logos, CIP, mockups, icons |
| `banner-design` | social/ads/print banners |
| `brand` | brand voice, messaging, asset management |

**Note:** `ui-ux-pro-max` ships a Python search engine — `python3 scripts/search.py "fintech dashboard" --design-system`. Standard library only, no network calls.

### 2. Full-stack engineering — 47 skills

Source: **[Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills)** · MIT

Languages, frameworks, infrastructure, security, testing, data/ML. Highlights:

| area | skills |
|---|---|
| **languages** | `python-pro`, `typescript-pro`, `javascript-pro`, `sql-pro` |
| **backend** | `fastapi-expert`, `django-expert`, `nestjs-expert`, `spring-boot-engineer`, `dotnet-core-expert` |
| **frontend** | `react-expert`, `nextjs-developer`, `vue-expert` |
| **architecture** | `architecture-designer`, `api-designer`, `microservices-architect`, `cloud-architect`, `graphql-architect`, `legacy-modernizer` |
| **infra/devops** | `kubernetes-specialist`, `terraform-engineer`, `devops-engineer`, `sre-engineer`, `chaos-engineer`, `monitoring-expert` |
| **security** | `secure-code-guardian`, `security-reviewer` |
| **testing** | `test-master`, `playwright-expert`, `code-reviewer`, `debugging-wizard` |
| **data/ML** | `pandas-pro`, `spark-engineer`, `ml-pipeline`, `rag-architect`, `fine-tuning-expert`, `postgres-pro`, `database-optimizer` |
| **product** | `feature-forge`, `prompt-engineer`, `spec-miner`, `the-fool` |

**Pruned from the original 67.** These 20 were removed as irrelevant to the work at
hand; re-clone the repo and copy them back if you want them:
`swift-expert`, `kotlin-specialist`, `csharp-developer`, `php-pro`, `java-architect`,
`cpp-pro`, `rust-engineer`, `golang-pro`, `angular-architect`, `vue-expert-js`,
`laravel-specialist`, `rails-expert`, `atlassian-mcp`, `salesforce-developer`,
`shopify-expert`, `wordpress-pro`, `game-developer`, `embedded-systems`,
`flutter-expert`, `react-native-expert`

### 3. Planning and disciplined execution — 6 skills

Source: **[obra/superpowers](https://github.com/obra/superpowers)** · MIT · ~321k stars

| skill | what it does |
|---|---|
| `brainstorming` | interrogates what you actually want before anything is built |
| `writing-plans` | produces a task-by-task plan with TDD steps and exact interfaces |
| `subagent-driven-development` | executes a plan with a fresh subagent per task plus a reviewer |
| `executing-plans` | executes a plan inline, in one session |
| `verification-before-completion` | refuses to claim success without evidence |
| `using-superpowers` | how the six fit together |

The chain is `brainstorming → writing-plans → subagent-driven-development → verification-before-completion`.

---

## Caveats worth reading before you rely on this

**1. Some skills assume capabilities you may not have.**
`design` and `banner-design` advertise AI image generation and Gemini models. Without
an image-generation tool wired into your client, those paths degrade to SVG/CSS
mockups or fail. `ui-styling` assumes React + shadcn; useless for plain HTML.

**2. Three bash scripts need Git Bash or WSL on Windows.**
```
subagent-driven-development/scripts/sdd-workspace
executing-plans/scripts/task-start
executing-plans/scripts/task-done
```
`sdd-workspace` is a mandatory first step of the execution skills. On Windows, call
`"C:\Program Files\Git\bin\bash.exe"` explicitly — **not** `bash` from PATH, which is
usually the WSL launcher and cannot see `C:\` paths.

**3. `brainstorming` ships a local HTTP server.**
`scripts/server.cjs` plus start/stop shell scripts power an optional "Visual
Companion" browser tab. It is opt-in — the skill only offers it just-in-time and never
starts it unprompted. Nothing runs unless a human accepts.

**4. Two descriptions are deliberately aggressive.**
`brainstorming` says *"You MUST use this before any creative work"* and
`using-superpowers` says *"requiring skill invocation before ANY response"*. Both will
try to fire constantly. If that gets noisy, edit the `description:` line in the
`SKILL.md` frontmatter — that line, not the body, is the trigger.

**5. Skills do not call skills.**
A skill is markdown loaded into context. It cannot invoke another skill. If you want
`writing-plans` output executed *by* `python-pro`, say so explicitly — the model
chooses which skills to load, the skill does not.

---

## Attribution

All three upstream projects are MIT licensed. The `SKILL.md` files carry their original
text; this pack adds no modifications beyond removing 20 skills from the Jeffallan set.

If you redistribute this folder, keep the upstream repository links above with it.

| source | license | skills |
|---|---|---|
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | MIT | 7 |
| [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills) | MIT | 47 |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | 6 |
