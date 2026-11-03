---
name: unslop-design
description: Review and redesign an app or website UI to strip out the "slop" (decorative accent color, gradients, meaningless shadows, noisy badges, emoji as icons, eyeballed spacing, greetings as page titles, Title Case, flat hierarchy, repeated numbers) using a system (spacing, type, color roles, elevation) and an orchestrated process — inventory from screen recordings or screenshots, a grayscale pass, parallel product-designer reviewers, a published winning proposal, devs per area, audits and a PR. Works for any project (SwiftUI, Compose, web). Use it when asked to "review the design", "make a proposal", "make it look less AI", "unslop", "polish this screen", "design review", "product designer review", "winning proposal", or when given videos or screenshots of an app with a request for feedback or a redesign. Also use it when starting a design system (spacing, type, palette, shadow scales) or auditing tokens, contrast or consistency across screens.
license: MIT
metadata:
  author: marcosnovo
  version: "1.3.0"
  homepage: https://github.com/marcosnovo/unslop-design
---

# Unslop design

Three parts: **what to fix** (`checklist.md`, each fix with its reason),
**how to orchestrate it** (`process.md`, rounds with reviewers and devs in
parallel) and **cases and sources** (`references.md`: the five before/afters
that started this skill and a map of *Refactoring UI*). The spec card every
reviewer fills is in `spec-card.md`. Per-platform notes
(SwiftUI, Compose, web, widgets, watch, car) live in `platforms.md`. Read the
one you need, not all of them.

## Principles (non-negotiable)

1. **A fix is a rule, not a tweak.** Every change ships as a token or
   component (spacing, font size, weight, color role, radius, shadow,
   button), never as a literal in the view. If the token is missing, create
   it in the same change. Pick values **by elimination** within the scale
   (try the value and its two neighbors; the middle wins or you repeat),
   never pixel by pixel.
2. **Hierarchy before color.** The screen has to work **in grayscale**:
   spacing, size, weight and contrast do the work; color comes afterwards and
   only to mean something. If it's unclear in gray what matters, color won't
   fix it.
3. **The first thing you read is the answer.** One hero number per screen
   (the balance, the price, today's progress); everything else steps back.
   Emphasize by **de-emphasizing the competition**, not by inflating the
   hero. At most one dark/hero surface per screen, and **none in sheets or
   modals**.
4. **Color says one thing.** One brand accent for the action or the hero
   number; everything else is a role with meaning (money/success, up/danger,
   status, reward) and gray for what only navigates. Decorative color =
   slop. Color never works alone: shape or a word goes with it.
5. **Measured contrast, not assumed.** WCAG AA (4.5:1 text, 3:1 large text
   and icons) computed from the real hex values against the real
   backgrounds, light and dark. White on a green/yellow brand color almost
   never passes; gray text on a colored background doesn't either (pick a
   shade of the same hue).
6. **Nothing the screen can't deliver.** No invented numbers, no projection
   presented as data, no implied feature that doesn't exist, no empty state
   that lies. Design the smallest version you can actually ship.
7. **One signature gesture, taken from the domain.** A brand detail born
   from what the app shows (a price-board price with a smaller last digit,
   dot-matrix numerals on a running app), not a new font or effect; and it
   degrades gracefully where it doesn't apply. Everything else is native:
   don't fight the tab bar, switches or system sheets.
8. **Platforms ship together.** If the project has iOS and Android (or app
   and web), the change goes to both in the same PR, in every language.
9. **Verify what the user sees.** Screenshots in light and dark, largest
   text size, a non-default currency/language, real data (long names, empty,
   2,000 items). What can't be compiled in your environment gets audited by
   reading, and the PR says so.

## Any agent (Claude Code, Codex, Cursor, Copilot, Gemini…)

The rules are the same everywhere. Where it says "agents", use what your
tool has: subagents if it has them (Claude Code, Codex…), with a git
worktree each for devs. With no subagents, run the reviewers one after another,
each with its own brief, and keep their outputs separate before the jury
step. Where it says "publish", Claude Code publishes an artifact; other agents
write an HTML file the user opens. In a chat app without a codebase, stop
after the before/after proposal.

## Working agreement (defaults)

- Reviewers = *senior product designers* and devs = *senior devs*, as
  agents (use the model the user asks for). The orchestrator doesn't build
  the areas: it does the shared work, integrates and audits.
- Every decision comes with an **explicit, actionable recommendation**.
- **Before implementing, publish the before/after** and wait for the user's
  "yes".
- Every round also reviews what earlier rounds shipped and **all** the
  videos/screenshots received, not just the latest.
- When merging is allowed once CI is green: close with a list of what to
  check when compiling (concrete risks) and, if there's no Mac/simulator, a
  self-contained prompt for a local session.
- On "is everything done?": done (with PRs) · pending on you · left out on
  purpose.
- After the last round, update the project's design system.

## Short flow

1. Inventory: frames from the videos (`process.md` § 1), screens and
   states, and each screen located in the code.
2. System: check (or create) the spacing, type, color and elevation scales
   (`checklist.md` § System). Without scales, reviewers judge by eye.
3. Grayscale pass + parallel reviewers (3-4, one per area) against
   `checklist.md`, applying fixes **one at a time**.
4. Winning proposal: one HTML page with before/after, the spec card and
   the list of decisions; the user chooses.
5. Devs per area in isolated worktrees with a closed brief; integrate,
   compile, audit, PR, answer review bots, merge when green.
6. Finally: update the project's design system (doc + tokens + its own
   skill) with what's new.

## If the project already has its own design skill

Use it for concrete tokens and components; this one brings the method and
the general checklist. If a rule here clashes with a written project
decision, the project wins and the proposal points it out.
