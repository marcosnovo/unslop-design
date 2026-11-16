# Changelog

## 1.14.1 — 2026-11-16

Two blind runs of 1.14 with a small model (Haiku), only the skill and the
user's messages: the web app flow (no command, init, quick pass, "yes",
score: 58 → 99) and the SwiftUI flow with a partial yes ("skip the stat
cards for now"), apply, the Gemini hook and the Action (62 → 94). Both
followed the 1.14 changes (baseline saved, proposal in `.unslop/proposal/`,
Contrast and Context rows, context not committed). What they had to guess:

- `review.md` gets `[~]` for "not now": *apply* skips it, the next review
  may raise it once. "Skip for now" had to be filed as rejected.
- `SKILL.md` names the Action as `uses: marcosnovo/unslop-design@v1`; a run
  pinned the version from the skill's metadata instead.
- On the web, the screen's score is its markup plus the rendered audit; a
  shared stylesheet's code score is reported apart.
- With code, the edited "after" is a copy in `.unslop/proposal/after/`.
- A "revise" verdict from the second critic: one more pass, then show it
  with the verdict stated. Commit nothing unless the user asks.
- `context.md`: with no tokens, propose the base-4 scale nearest to the
  most used values (it contradicted #1).
- `unslop-score.py` and `test.py` no longer write `__pycache__` into the
  installed skill's folder.

## 1.14.0 — 2026-11-16

Three blind runs of 1.13 by fresh agents that only had the skill and the
request: a web app (no command, then init, a quick pass, "yes", score), a
SwiftUI screen with no simulator (quick pass, apply, then the Gemini hook
and the Action), and a landing page (critique, then "refine, don't
redesign"). Each worked end to end (27 → 68, 62 → 100, 2 → 96); what they
had to guess is now written down.

Quick mode (`SKILL.md`):
- The "before" is saved (`--save --json > .unslop/before.json`) and the
  "after" compares with it (`--baseline`): the trend had only one entry.
- Score **the screen's own files**; a stylesheet shared with other screens
  carries their slop and is reported apart (a fixed screen read 68).
- The board, mocks and audits go in `.unslop/proposal/`, each audit with its
  own `--out`: mocks were counted in the project's score (and its CI),
  and the second audit overwrote the first. No project file changes
  before the "yes".
- On "yes", apply the accepted fixes; *apply* picks up `[ ]` rows and,
  with none left, says so and offers the next steps.
- The report gets **Contrast** (pairs measured) and **Context** (read, or
  none: offer `init` once) rows.
- Refine or redesign: don't ask when the request already says. The three
  concepts are for a redesign only. A refine still removes what principles
  5 and 6 rule out, keeping the slot and saying what real content goes in.

- `scripts/contrast.py` (and `npx unslop-design contrast`): the WCAG ratio
  of any pair, translucent text composited, Compose `0xFF…` hex read, the
  worst of several backgrounds. Native screens had no way to measure
  principle 5.
- `context.md`: with no tokens, the scale is a proposal from the most used
  values; commit only on a "yes" to the context; `allow:` may be empty.
- `web.md` and the `pressure` rule: the recommended plan is labeled
  "Recommended", never "Most popular" without data (they contradicted).
- `npx unslop-design --help` lists `hook` and `contrast`.
- Releases move a major tag (`v1`), so `uses: marcosnovo/unslop-design@v1`
  follows every 1.x release; the README and guide use it.
- README in 30 seconds (587 → 266 lines); install options, automation,
  how it works and the FAQ move to `guide/`.

Tests: 4 contrast checks.

## 1.13.0 — 2026-11-16

The post-edit hook in every agent whose hooks can talk back to the model.

- `hooks/unslop-hook.mjs` reads the event of each agent: Claude Code
  (`Write`/`Edit`/`MultiEdit`), Gemini CLI (`AfterTool` on `write_file` and
  `replace`), Codex CLI (`apply_patch`, with the paths and added lines taken
  from the patch) and GitHub Copilot / VS Code agents (`postToolUse`, the
  path from `tool_input` or `toolArgs`). It scans every UI file the edit
  touched and answers with `hookSpecificOutput.additionalContext`, which all
  four read. Hits now show as `file:line`.
- `npx unslop-design hook` runs it from npm, so a config needs no path.
- `npx unslop-design hooks gemini|copilot|claude [--write]` prints or adds
  the config to the project (`.gemini/settings.json` merged,
  `.github/hooks/unslop-design.json`, `.claude/settings.json`; writing twice
  doesn't duplicate it). `hooks codex` prints the `config.toml` block.
- Cursor and Windsurf are left out on purpose: their post-edit hooks can't
  send anything back to the agent yet.

Tests: 4 new hook checks (Gemini write and a clean replace, a Codex patch,
Copilot `toolArgs`).

## 1.12.0 — 2026-11-16

The score where people read it: on the pull request, against the base
branch.

- **PR comment** (`action.yml`): on `pull_request`, the action also scores
  the base commit with the same scripts and options, and keeps one comment
  on the PR, updated on every push: "unslop score: 88/100 (+7 vs main)",
  what got worse, what got better, every row in a fold. New inputs
  `comment` (default true) and `github-token`, a new `delta` output. It
  needs `pull-requests: write`; without it (or on a fork's read-only token)
  it leaves a warning and the job goes on.
- **`unslop-score.py --baseline`** compares with an earlier `--json` run, in
  text, Markdown and JSON (`--baseline-label main`), so the same comparison
  works locally between two branches.
- **Share your score**: an issue template (before/after, both numbers, the
  fixes that mattered, what it missed, permission to show it) and a
  **Scores in the wild** section in the README.
- This repo's CI comments its own score on its PRs.

Tests: 3 new command-line checks (text, Markdown, a missing baseline).

## 1.11.0 — 2026-11-16

Thirteen scanner rules for fixes that had no automatic check, picked by one
test: the fix is already in the checklist and a static check is reliable.
Each comes with hits and near misses (13 new cases), and none fires on an
"after" case. The checklist ends with **Automatic checks**, every rule
by fix number (48 rules).

- **multiple-h1** (#13): two or more `<h1>` in one page file (HTML, Vue,
  Svelte, Astro; not `.tsx`, which often holds several components).
- **justified-text** (#28): `text-align: justify`, `text-justify`.
- **extreme-tracking** (#29): letter-spacing tighter than -0.04em;
  `tracking-tight` and -0.02em headlines pass.
- **icon-circle** (#33): three or more icons in tinted circles in one file;
  one in an empty state passes.
- **lorem** and **placeholder-image** (#35, #48): lorem ipsum, and
  placeholder.com, picsum, placehold.co and similar.
- **count-pill** (#50): a bare count in a filled pill or a `badge`/`pill`;
  a muted `count` passes.
- **bare-delta** (#52): "+12%" or "▲ 8%" with no baseline within a few
  words ("vs September", "from last month" pass), in web and native text.
- **fixed-width** (#57): `width` or `min-width` of 400px or more, `w-[640px]`;
  `max-width` and media queries pass.
- **section-numbers** (#60): 01, 02 and 03 as section markers.
- **straight-quotes** (#61): "You're", "Let's Go" and straight double
  quotes in visible copy; attributes and code pass.
- **no-color-scheme** (#62): a dark theme with no `color-scheme` anywhere
  in the scanned files. **no-reduced-motion** (#63): keyframe animations
  with no `prefers-reduced-motion` or `motion-safe:` anywhere.

Found on our own pages: the example dashboard's after had a dark theme with
no `color-scheme` (fixed, still 100), and the website had one straight
apostrophe (fixed). The dashboard's before now scores 21 (91 hits).

Workflows use `actions/checkout@v5`, `setup-python@v6` and `setup-node@v5`
(Node 24), so GitHub's Node 20 deprecation warning is gone.

## 1.10.1 — 2026-11-16

Native proof, and releases that run themselves.

- `examples/swiftui/` and `examples/compose/`: a SwiftUI subscriptions
  screen (32 → 100, with the HTML mock of each state at iPhone size) and a
  Compose settings screen (62 → 100), next to the web dashboard. The README
  and the website show the SwiftUI pair (`assets/swiftui-before-after.png`).
- Releases: merging a version bump to `main` tags it, publishes the GitHub
  release with the CHANGELOG entry and `unslop-design.zip` (the skill for
  claude.ai, Claude desktop and ChatGPT, which earlier releases lacked), and
  publishes to npm through Trusted Publishing.
- `npx unslop-design` is on npm; the website is at
  https://marcosnovo.github.io/unslop-design/.

## 1.10.0 — 2026-11-16

A release about what happens after the review: the project's decisions are
written down once, slop is caught while the agent writes it, and CI keeps
the score. Plus seven fixes and six scanner rules from a comparison with
other design skills.

Commands and context (`SKILL.md`, `context.md`, `critique.md`):
- **Commands:** *init*, *score*, *audit*, *critique*, *apply* and *full*
  next to the default review. With no command and nothing attached, the
  agent reads where you left off and proposes the next two or three steps.
- **`init`** writes `.unslop/context.md`: users, the scene, surface modes,
  what must not change, and machine-read lines (`scale`, `type-scale`,
  `allow`, `hook`). Three questions at most, and it never blocks a quick
  pass. `slop-scan.py`, `unslop-score.py` and the hook read it; flags win.
- **`.unslop/review.md`** is the backlog: each quick pass writes its five
  fixes as applied, pending or rejected (with the reason), and *apply*
  picks up the pending ones.
- **`critique.md`**: a usability report that changes nothing and doesn't
  touch the score: tasks walked as three users, eight cognitive-load
  checks, ten heuristics scored 0-4, findings P0-P3.
- **Refine or redesign:** ask first. Refining keeps the layout, face,
  signature and voice; only a redesign may change the skeleton.
- `process.md` § 2b starts from the **scene** (who, where, when, what
  light): it decides light or dark and density, not the product category.

Seven fixes (`checklist.md`), numbered after the current ones:
- #66 a hard offset shadow is a style, not depth · #67 ease out, don't
  bounce · #68 one separator per surface (the "ghost card") · #69 code
  faces for code and data · #70 a modal is the last resort, Undo beats
  Confirm · #71 built for every language and every size of data (text
  expansion, RTL with logical properties, platform plurals and formatters,
  errors with Retry) · #72 four choices or fewer per group.

Scanner (`slop-scan.py`), six rules, each with hits and near misses:
- **side-stripe** (#60): a 2px+ side border on a rounded card, CSS and
  Tailwind; a square blockquote rule and 1px dividers pass.
- **hard-shadow** (#66): box-shadow layers with no blur; insets and focus
  rings pass. **bounce-easing** (#67): overshooting `cubic-bezier`,
  `animate-bounce`, bounce/elastic/wobble keyframes.
- **ghost-card** (#68): a 1px border and a soft shadow on one rounded
  surface, including the shadcn card (`rounded-xl border … shadow`);
  `hover:shadow` passes. **mono-disguise** (#69): monospace on `h1`-`h3`,
  title classes or `body`. **plural-hack** (#71): "item(s)" in UI text,
  not `trim(s)` in code.
- `--json`, `--github` (an Actions annotation per hit) and `--list-rules`.
- Scores: the six rules cost 1-2 points per hit with small caps. The
  example dashboard's before goes from 25 to 24 (its cards are ghost cards).

Score (`unslop-score.py`): `--save` appends each run to
`.unslop/history.json` and prints the trend; `--markdown` prints a table
for a PR comment or a job summary.

Automation:
- **Claude Code hook** (`hooks/`): after each Write or Edit of a UI file,
  the scan runs on that file and the agent gets the hits its edit added, as
  context. Silent when clean, never edits, off with `UNSLOP_HOOK=off` or
  `hook: off`.
- **GitHub Action** (`action.yml`): annotations, the score in the job
  summary, a `score` output and an optional `min`.
- This repo now runs `validate.py` and `test.py` in CI, and the action on
  its own example.

Distribution:
- `npx unslop-design install | scan | score | audit | rules`
  (`package.json`, `bin/unslop.mjs`), no dependencies.
- `install.sh` links eleven more agents: Devin, Grok Build, Hermes, Pi, Oh
  My Pi, Qoder, Trae, Trae CN, Rovo Dev, Mistral Vibe, DeepSeek Harness
  (Replit already reads `~/.agents/skills`).
- `docs/`: a landing page for GitHub Pages with a draggable before/after of
  the example dashboard. It scores 100 on its own code and rendered page.

Tests: 9 new cases (one per rule, plus Next/shadcn, Vue and Svelte), 10 new
command-line checks (rule list, annotations, JSON, Markdown, context file,
flags over context, the hook on a write, a clean edit and a non-UI file).
`validate.py` checks a 3,000-word budget for `SKILL.md` and that
`package.json` carries the same version.

## 1.9.0 — 2026-11-14

One release for three blind runs by a fresh agent that only had the skill
and the request: an order-tracking screen given only as a screenshot, a
SwiftUI paywall, and a web analytics dashboard.

Paywalls and pressure copy:
- `checklist.md` gets a **Paywall** bullet: a visible 44pt close, Restore,
  Terms and Privacy, the price after the trial, one primary, a computed
  "save N%" with its baseline, plans as rows with one selected state. No
  resetting countdown, "only N left", unsourced counts or "most popular".
  Paywalls are no longer exempt as a "brand moment".
- `slop-scan.py` adds the rule **pressure** (#64): countdowns, "limited
  time", "only N left", "hurry", "most popular", "best value", and a bare
  "save N%". "Save 88% vs weekly" passes, even with a tag in between.
- **unverified-claim** catches "Join 2,000,000+ happy users" (up to two
  words before the noun).
- **title-case** knows common screen nouns (Status, Order, History,
  Payment, Preferences…): "Order Status Tracking" passed before.

Web audit (`web-audit.mjs`):
- Text on a gradient is checked against its worst stop and marked
  "estimated", instead of being left as unknown.
- The default scale includes 1, and the browser's own 1px 6px button
  padding no longer counts as off-scale. Margins over twice the largest
  step (`margin: auto` resolved) are skipped.
- SVG text (chart labels) is left out of the text-scale check.
- Left edges ignore text in the second and later columns of a grid or
  flex row.
- SVG text is measured as drawn: its contrast uses `fill` (not CSS
  `color`), and a new check lists text drawn under 11 px at each width,
  with a score row (**tiny-text**). A chart whose viewBox shrinks to a
  phone took its 12-unit labels down to 5 px with nothing reported.
- The report groups identical contrast failures (eleven axis labels in
  one color are one line, ×11) and marks off-scale values that are the
  browser's default 1em margin on `p`, `ul`, `dl` or a heading.

Process (`SKILL.md`, `checklist.md`):
- A scanner hit is fixed by changing the value, not by hiding it (a
  `calc()` that lands on the same 11px). Phone mocks are fluid up to the
  device width, so the 390 audit doesn't report a scroll that isn't there.
- #39: chart labels stay at 11 px or more as drawn on a phone.
- **Only a screenshot, no code:** rebuild the before as an HTML mock,
  call sampled colors approximate, and label scores as mock scores.
- Phone mocks are audited with `--device` at 390; the text-scale line
  doesn't apply to native Dynamic Type. A desktop page is compared at
  its real width, stacked, not shrunk.
- With no subagents, the second critic is a separate pass with its own
  prompt, reported as such.
- #52: a delta's color follows its meaning (churn or latency going up is
  worse). #39: keep horizontal grid lines at the kept ticks, drop the
  vertical ones. #51: app-wide categories keep their color; parts of one
  measure use one hue light and dark, with a dash or a direct label.

Tests: 14 new cases (pressure, adjective claims, gradient text (twice), the UA
button, SVG text, an SVG chart, Title Case nouns, grid edges, and the three test screens before and
after).

## 1.8.9 — 2026-11-14

One release for three test runs, held until all three were in: a project
with its own design skill (Ledger), and two blind runs by a fresh agent
that only had the skill and the user's request: a long article (Read
mode) and a Jetpack Compose settings screen it couldn't compile.

Project decisions and the floors (`SKILL.md`):
- A written project decision beats a taste rule (a base-6 grid over #1,
  a brand face over #6, tracked caps as the signature over #45), never
  **contrast** (principle 5) or **invented claims** (principle 6). The
  agent had offered "keep white on the brand green at 3.4:1" as an option;
  it's now a blocker reported with the ratio and a fix inside the brand.
- `slop-scan.py` and `unslop-score.py` take `--allow` for the rules a
  written decision covers (listed apart, not scored) and refuse
  `contrast`, `graphics-contrast` and `unverified-claim`. Run them with the
  project's own `--scale` / `--type-scale`.

Quick mode (`SKILL.md`):
- It ends with a fixed report (render looked at, the passes, six axes,
  spec card rows, score, not checked), so a skipped step shows: the first
  agent never opened the render and said so only when asked.
- The before/after is one page, side by side at the same width. Native
  code that can't run here gets an HTML mock at device size, which counts
  as the render, and each state is audited on its own page (a board mixed
  both into one census).

Scanner (`slop-scan.py`):
- Fixed: a one-line `:root { … }` left the scanner "inside :root" for the
  rest of the file, hiding raw colors and off-scale values after it.
- Fixed: hex values in custom-property definitions anywhere on a line (a
  dark palette in `@media … { :root { … } }`) aren't raw colors.
- Fixed: literals in token files on native (`Tokens.kt`, `Type.swift`,
  typography, dimens, spacing, shapes) aren't literals in a view.
- New `elevation-literal` (#5, #32): `cardElevation(6.dp)`,
  `.shadow(radius: 12)` on components.
- New `translucent-text` (#22): `Color.White.copy(alpha = …)`,
  `.white.opacity(…)`, `text-white/60`, `color: rgba(255,255,255,.6)`.
- New `empty-action` (#64, principle 6): `onClick = {}`, `Button { }`,
  `action: {}`, `onClick={() => {}}`: a control that implies a feature
  that doesn't exist ("Save changes" when switches already save).
- `unverified-claim` reads any comparative after "Nx" ("10x warmer") and
  "100% waterproof / secure / guaranteed…"; `hype-copy` knows "crushing
  it", "in today's fast-paced world", "let's dive in".

Rendered checks (`web-audit.mjs`):
- **Reading** (#27, #28): running text over ~85 characters a line, and
  long text justified or centered. The article had 114-141 characters a
  line, justified, and nothing measured it.
- **Empty blocks** (#35): a big painted box with no text or media, the
  placeholder where a photo or the product should be.
- `unslop-score.py` weighs all three.

Checklist: #34's "one gradient" allowance never covers gradient text
(#55).

Tests: 57 cases and 10 rendered checks (from 41 and 8), including the
three test projects before and after, and five command-line checks for
`--allow` and its refusals.

## 1.8.8 — 2026-11-14

A regression suite for the scripts, from the cases built while testing
1.8.0-1.8.7 (they lived in a temporary session and were checked by hand on
every PR):
- `tests/cases`: 41 cases, one folder each. They cover every detector's
  hit and its near miss: starter kits (shadcn v3/v4, the Compose
  template, a customized theme), stat-card rows vs lists, pricing tiers,
  `.map()` and declared-first components, tracked caps, canvas + tab bar,
  hidden navs, split claims, dangling tokens, quoted JSX definitions. Plus
  the five test screens before and after (Stride, Subscriptions, Relay,
  Trail, Mise).
- `tests/expected.json`: the exact hits per rule for each case, and eight
  rendered checks for `web-audit.mjs` (faded icons, typographic marks,
  root at 200 %, contrast, glows, text scale).
- `scripts/test.py`: standard library only; `--audit` adds the rendered
  checks when Playwright is there and says so when it isn't; `--update`
  rewrites the expectations so a behavior change shows as a diff.
  Breaking the glow detector on purpose fails exactly the three cases that
  depend on it.
- `CONTRIBUTING.md`: a new rule or a fixed false positive comes with a
  case for the hit and one for the near miss.

## 1.8.7 — 2026-11-14

The first run of the **implementation stage** of the full flow
(`process.md` § 5-6) on the test recipe app: a tokens PR 1, two devs in
their own worktrees from closed briefs (each started with
`git merge --ff-only`), a temporary integration branch, then the checks.
Library 22 → 100, recipe 31 → 100, settings 31 → 100, light and dark. Four
gaps:
- **The spec card didn't take the jury's values.** A dev built the
  quantity unit at 15 px from the reviewer's card after the jury had set
  0.875rem; no script can tell, both values are valid. The redraw after
  the jury now covers boards, spec cards and decision lists (§ 3).
- **Parallel devs invented duplicate tokens.** Both added 1 px and 2 px
  line widths under different names (`--bw`, `--hair`) at the end of
  `tokens.css`, a certain merge conflict. The tokens file now has one
  owner, the orchestrator; devs ask for what's missing in their report
  (§ 5).
- **Nothing checked that every `var(--name)` resolves.** After unifying
  the names, a dangling one falls back in silence. New `undefined-token`
  rule in `slop-scan.py` (across all scanned files, only when some token
  is defined in scope; a `var()` with a fallback is left alone), weighed by
  `unslop-score.py`, and a line in § 6.
- **The before moved with the scripts.** The same untouched screen scored
  35 under 1.8.5 and 22 under 1.8.6. "Score X → Y" now requires both
  numbers from the same version of the scripts (§ 6).

## 1.8.6 — 2026-11-14

The first run of the **full flow** end to end (a three-screen recipe app:
three blind directions, three area reviewers plus a numbers-only one, a
jury, the second critic and a published winning proposal) found four
process gaps and five tool bugs:

Process (`process.md`, `checklist.md`):
- **Directions converged.** The grounding's "one thing only this product
  has" seeded every agent, and the control ended up as one of the bold
  directions. The orchestrator now assigns each direction its source, and
  the control's brief leaves that line out (§ 2c).
- **Nobody redrew after the jury.** It corrected 23 values on paper; the
  boards kept the old ones, and two of the critic's three findings were
  values already replaced. Each board now takes the jury's table and is
  re-rendered before the critic (§ 3, SKILL.md full flow step 5).
- **Shared components had no owner.** Two reviewers redesigned the same
  tab bar. Each brief names one owner per shared component (§ 3).
- **Type in px.** It ignores the reader's text size; the skill didn't say
  so. #2 asks for a `rem` scale on the web, and `web-audit.mjs` now
  doubles the root font size and reports text that doesn't grow.

Tools:
- `web-audit.mjs` never reported a glow: it parsed the whole shadow
  string as a color. It now reads the color inside the shadow and counts
  any colored shadow (#32). `slop-scan.py` only knew `0 0 Npx` glows; it
  now flags colored `box-shadow` at any offset.
- `slop-scan.py` checked `font-size` and `border-radius` against the
  spacing scale. Font sizes have their own `--type-scale`, and a full
  radius (999px) isn't a step.
- Emoji-only text is no longer a contrast failure (CSS color doesn't
  paint it), which also removes the double count with its link.
- `card-sameness` reads the local stylesheets a page links, not only the
  CSS in the same file.
- An exclamation mark mid-sentence ("Ready in 30 minutes! Your…") is
  caught, not only at the end of a text.
- `unslop-score.py` weighs type that ignores the text size (3 points).
  The example dashboard still scores 25 → 100, with 88 hits (font sizes no
  longer count as off the spacing scale).

## 1.8.5 — 2026-11-14

Found by a fourth end-to-end run, on a Jetpack Compose map screen in
Experience mode (hiking navigation, Pixel, light and dark: code 70 →
100). It also confirmed 1.8.4: with the interaction's second frame, the
critic gave Specificity 4 and the loop exited in round 1.
- `web-audit.mjs` measures **icon and small-graphic contrast** (WCAG
  1.4.11): every visible inline SVG up to 64 px, its best fill or stroke
  against the real background, under 3:1 reported with the element that
  holds it. The run's light theme had a yellow trail mark on a cream card
  at 1.41:1 that neither the text audit nor the critic saw.
  `unslop-score.py` weighs it (1 per icon, cap 6).
- The second critic's findings are checked before they're applied
  (`process.md` § 4): the cited rule has to say what the finding claims,
  and a contrast finding has to hold against the audit. In the run the
  critic called gray-on-dark text a #22 failure; it measured 7.9:1.
- New `canvas-tabbar` rule (#59): a map or camera (`GoogleMap`, `Map`,
  `MapView`, `…Map(`, `CameraPreview`, `<canvas>`, `class="map"`) and a
  permanent tab bar (`NavigationBar`, `TabView`, a fixed bottom `<nav>`) in
  the same composable, view or web page. Two screens in one file don't
  count.
- `hype-copy` (#64) knows the adventure clichés: "your adventure awaits",
  "your journey starts here", "ready when you are", "like never before",
  "at your fingertips", "the future of …".

## 1.8.4 — 2026-11-14

Found by a third end-to-end run, on a Tailwind landing page in Persuade
mode (on-call scheduling: 9 → 98 with the rendered page). Two rounds of
the second critic both cited checklist numbers, and the stop rule ended
the loop when the second round raised no axis:
- The loop couldn't raise Specificity. The axis asks whether the concept
  reaches one interaction, but the critic sees still images and may only
  remove or replace. Both critics stopped at 3 for "no interaction
  visible". In Persuade and Experience the key screen now comes with a
  **second frame** of the concept's interaction (`process.md` § 2c), and
  the critic and the Specificity axis judge it (§ 4).
- `web-audit.mjs` no longer counts © ® ™ (or ✓ ★ and the like) as emoji:
  they're `Extended_Pictographic` but they're characters.
- `card-sameness` counts a number only when there are digits ("$12,400",
  "99.9%", "10x", "500+"). Large type alone made three emoji feature cards
  read as stat tiles.
- New `unverified-claim` rule (#64): "Trusted by 10,000+ teams", "Join
  50k+ developers", "10x faster", "99.9% uptime", the usual invented
  social proof. It asks whether the claim is real and sourced.
- New `hidden-nav` rule (#57): nav links hidden below a breakpoint
  (`hidden md:flex`) with no menu button (`aria-expanded`,
  `aria-controls`, `<details>`), so the phone has no navigation.

## 1.8.3 — 2026-11-14

Found by a second end-to-end run, on a SwiftUI screen in Operate mode (a
budget app's subscriptions: 72 → 100 rendered). The web rules were ahead
of the native ones; the code alone scored a plainly sloppy screen 74:
- Greetings with a name: "Hey Maya! 👋", `Hi {user.name}`,
  `"Hey \(name)"`, not only the fixed phrases (#26).
- Exclamation marks in SwiftUI/Compose strings (`Text("Renews soon!")`),
  not only in HTML text (#25).
- A literal ALL CAPS `Text("…")` with `.tracking`, `.kerning` or
  `letterSpacing` on it (#45, #60), not only `.textCase(.uppercase)`.
- Title Case in UI strings, new `title-case` rule (#25): two to six
  capitalized words with at least one common word ("Your Subscriptions",
  "Recent Activity", "🚀 Start Run"), so brand, product and place names
  ("Spotify Family", "New York Times") pass. Text nodes and
  `Text`/`Button`/`Label`/`navigationTitle`/`Section`/`Tab` strings; it
  weighs little in the score.
- `platforms.md`: the system secondary gray is about 3.4:1 on white and
  3.1:1 on the grouped-list gray, under AA for small text; it used to
  recommend `.foregroundStyle(.secondary)` for secondary text.
- The test screen's code now scores 64 before (was 74) and 100 after.

## 1.8.2 — 2026-11-14

Found by running the skill end to end on a new screen (a running app's
Today screen in the AI template: 31 → 94, the ten-app lineup passed, the
second critic gave Specificity 4):
- `card-sameness` only counts cards that sit side by side, three or more
  in the same container: a multi-column grid, a flex row (class, CSS,
  `style="…"` or a JSX `style={{…}}`) or `flex: 1` cards (SwiftUI/Compose:
  inside a grid, `HStack` or `Row`). A stacked list of rows is #40's
  entity row, not a row of tiles, and was a false positive.
- The emoji rule no longer counts typographic marks (✓ ✔ ✕ ✗ ★ ☆).
- Pep-talk copy is caught: a single "!" in UI text (#25, new `exclaim`
  rule) and motivational hype ("crush it", "you've got this", "let's go",
  "level up", "beast mode"…) under #64.
- The second critic (`process.md` § 4) gets the checklist's fix titles,
  so its findings can cite a number, and a finding that contradicts a rule
  is rejected rather than applied. In the test it proposed dropping the
  destination from the primary button, against #41.
- The example dashboard scores 25 before and 100 after: its "Welcome
  back, Damir!" now counts, and its two side-by-side KPI cards no longer
  read as a row of three.

## 1.8.1 — 2026-11-14

Two `slop-scan.py` detectors left out of 1.8.0, now checked against the
real defaults:
- `stock-kit` (#6): a starter kit left as generated. shadcn's identity
  values (`--radius`, `--primary`, `--foreground`, `--ring`) for the
  neutral, zinc and slate bases, v4 oklch and v3 HSL, taken from the
  shadcn registry; and Android Studio's Compose template colors
  (`Purple80`… `Pink40`). Two or more in one file to count; a team that set
  its own radius and accent isn't flagged for keeping the kit's grays.
  Token files are scanned for this one, since it's about them.
- `card-sameness` (#40, #65): the same card markup three or more times in
  one file with a number in each, i.e. a row of stat tiles. Block elements
  only (a `<span>` pill isn't a card) and not when the cards carry a button
  or link (pricing tiers). SwiftUI/Compose: the same `…Card(`/`…Tile(`
  called three or more times. Cards rendered by `.map()`/`ForEach` appear
  once in the source and aren't seen.
- `unslop-score.py` weighs both (3 points for the kit, 1 per card row, cap
  3). The example dashboard scores 25 before (was 26) and 100 after.

## 1.8.0 — 2026-11-14

What "How to stop making your apps look like AI slop" (concept →
directions → design → render → critique → refine) adds, reviewed by four
specialist agents and adapted so "different" never buys lower contrast or
decoration:
- Find the concept (`process.md` § 2b): one sentence from the domain's
  physical world that decides type, layout, color and motion; tests
  (reach, competitor, legibility, honesty, dullest screen), a mandatory
  "stops at", and the new template to watch for: concept slop. Its size is
  set by the surface mode: a signature for Operate and Read, one idea for
  Persuade, a world for Experience. Principle 7 now points to it.
- Three directions before committing (§ 2c): different sources, not three
  palettes; one card each on the same key screen; one safe control; the
  user picks. Quick mode: three one-liners, render the pick.
- A second critic (§ 4): a fresh agent judges the render only (blind
  read, ten-app lineup, skeleton, sameness, six axes, three findings),
  at most two refine rounds with a mechanical stop.
- Critique pass 6, the ten-app lineup, and #65 "A skeleton from the job,
  not from the template". #6 allows one display face for the hero and
  names stock kits left at defaults; #35 lets a concept's illustration in
  when it earns its height; #40 and #47 clarified.
- `web-audit.mjs --device iphone,iphone-se,pixel`: real phone viewport,
  pixel density, touch and safe areas, and which font really rendered (SF
  Pro isn't on Linux/CI; the report names the fallback).
- Spec card: CONCEPT rows. References: case 8, with what not to copy.

## 1.7.0 — 2026-11-04

What the best design skills do that this one didn't (a review of
impeccable, taste-skill, hallmark, Anthropic's frontend-design and Vercel's
interface guidelines), adapted:
- Critique passes on the render: one second, five seconds, squint, cover
  the logo, count the left edges, gray (`process.md` § 2).
- Ground the design first (subject, audience, one job, one thing only this
  product has) and name the surface mode — operate, persuade, read,
  experience — with an expression budget for each (`SKILL.md`).
- Score the plan on six axes before showing it; under 3 on any axis means
  revise first (`process.md` § 4). Quick mode uses it too.
- Reviewers judge from screenshots and code; one separate agent reads the
  script output, so numbers don't anchor taste.
- Five craft-floor fixes (#60-#64): structure that carries information,
  real typography characters, themed system surfaces, named motion,
  nothing invented or inflated.
- #45 flipped: section headers are muted sentence-case labels; small
  tracked capitals only as a deliberate signature.
- `slop-scan.py`: `transition: all`, tracked-caps labels, three dots
  instead of …, hype copy. `web-audit.mjs`: left edges and a craft-floor
  section (color-scheme, ::selection, `transition: all`, "...").
  `unslop-score.py` weighs the new rules.

## 1.6.1 — 2026-11-04

- Claude Code plugin: `.claude-plugin/plugin.json` and `marketplace.json`,
  so `/plugin marketplace add marcosnovo/unslop-design` and
  `/plugin install unslop-design@unslop` install and update it.
- README: a quick start at the top (plugin, skills CLI, a check that it
  works) and a release badge.
- `scripts/validate.py` fails if `SKILL.md` and `plugin.json` versions
  differ.

## 1.6.0 — 2026-11-04

- Quick mode, the default for one screenshot, screen or page: no
  subagents, the five fixes that change the screen most with their
  numbers, the before/after, and the score before and after. The
  orchestrated process stays for whole apps and full reviews.
- `scripts/unslop-score.py`: `slop-scan.py` and, optionally, a
  `web-audit.mjs` report as one score from 0 to 100, with where the points
  went, a README badge and `--min` for a pre-commit hook. The example
  dashboard goes from 0 to 99.

## 1.5.0 — 2026-11-03

- Two fixes beyond clean (#58-#59): objects from the domain before boxes,
  and floating chrome when the content is a canvas (map, camera,
  timeline). From the developer of Utkik, used with permission.
- A seventh reference: Utkik, a flight and ship tracker built from objects
  instead of cards.

## 1.4.0 — 2026-11-03

- Web: `web.md` playbook (finding tokens per stack — Tailwind, shadcn, CSS
  modules, CSS-in-JS —, dashboards, landing pages, verification for a web
  PR).
- `scripts/slop-scan.py`: slop patterns in web, SwiftUI and Compose source
  with file, line and fix number (standard library only).
- `scripts/web-audit.mjs`: measures the rendered page at 390/768/1280 px —
  horizontal scroll, a census of every value in use, computed contrast,
  focus states, small targets, emoji, gradient text and glows — plus a
  grayscale screenshot (Playwright).
- Nine new fixes (#49-#57) from a dashboard before/after: icon slot, counts
  as text, one color per category, deltas with a baseline, interactive
  states, shortcuts as keys, no gradient text or page glow, a data voice,
  three widths.
- `examples/`: the same dashboard before and after; #26, #39 and #45
  refined; a WEB block in the spec card; a sixth reference case.

## 1.3.0 — 2026-11-03

- Six new fixes (#43-#48): rails, one section gap with no filler copy,
  section headers as labels, floating chrome in the system material with
  solid content, a signature as a small family of details, real content in
  every mock.
- `spec-card.md`: the card of named values each reviewer fills and devs
  tick as they land; also the script for a fix-by-fix recording.
- Process: spec card before the jury, optional fix-by-fix recording.
- #41: the brand accent can fill the primary when it is its only use on
  the screen.
- A fifth reference case (a social photo feed).

## 1.2.0 — 2026-11-03

- Works in every agent that reads the open Agent Skills format: Cursor,
  GitHub Copilot, Gemini CLI, Antigravity, Windsurf, OpenCode, Amp, Kiro,
  Goose, Roo Code, Junie, Cline and Zed, besides Claude Code and Codex.
- `install.sh`: one command installs it for every agent found, links them
  to one copy, and uninstalls only what it installed.
- `unslop-design.zip` in each release, for claude.ai, Claude desktop and
  ChatGPT.
- `scripts/validate.py` checks `SKILL.md` against the spec; frontmatter now
  has `license` and `metadata`.

## 1.1.0 — 2026-11-03

- Works in Codex too: install in `~/.agents/skills`, call it with `$unslop-design`.
- `agents/openai.yaml` with Codex UI metadata.
- Agent-neutral wording: subagents where the tool has them, sequential
  reviews where it does not; the before/after is an HTML page.
- Real before/after screenshots of Refil and two fix-by-fix animations in
  the README.

## 1.0.0 — 2026-11-03

First public release.

- 42 numbered fixes in `checklist.md` across system, spacing, hierarchy,
  color, typography, decoration and depth, images and charts, and layout.
- Orchestrated process: inventory from screen recordings, grayscale pass,
  parallel reviewers, a before/after you approve, devs per area in
  worktrees, audits and PR.
- Platform notes for SwiftUI, Jetpack Compose, the web, widgets, watch and
  car.
- Four real before/after cases and a chapter map of *Refactoring UI*.
