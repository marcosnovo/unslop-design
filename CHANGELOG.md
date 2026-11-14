# Changelog

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
