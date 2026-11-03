# Changelog

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
