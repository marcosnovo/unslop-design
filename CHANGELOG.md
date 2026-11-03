# Changelog

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
