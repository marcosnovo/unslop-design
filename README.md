# unslop-design

A [Claude Code](https://claude.com/claude-code) skill to review and redesign
an app or website so it stops looking AI-generated: decorative accents,
gradients, noisy badges, emoji icons, eyeballed spacing, greetings as page
titles, flat hierarchy.

It brings two things:

- **A checklist of 42 numbered fixes** (spacing scale, one accent, quiet
  badges, baseline-aligned numbers, shadows as elevation, charts without
  noise…), built on *Refactoring UI* and real before/after redesigns.
- **An orchestrated process**: frames from your screen recordings, a
  grayscale pass, senior product-designer reviewers in parallel, one
  published before/after proposal for you to approve, then devs per area
  shipping the PR.

Works with SwiftUI, Jetpack Compose and the web.

## Install

```bash
git clone https://github.com/marcosnovo/unslop-design ~/.claude/skills/unslop-design
```

Then, in any project, type `/unslop-design`, or just ask Claude to "review
the design" or "make it look less AI" and send it screenshots or a screen
recording. Video frames need `ffmpeg`.

To update: `git -C ~/.claude/skills/unslop-design pull`.

## What's inside

| File | What it covers |
|---|---|
| `SKILL.md` | Principles and the short flow |
| `checklist.md` | The 42 fixes, each with what to do and why |
| `process.md` | Inventory, reviewers, winning proposal, devs, verification, PR |
| `platforms.md` | SwiftUI, Compose, web, widgets, watch and car notes |
| `references.md` | The four before/afters behind the skill and a map of *Refactoring UI* |

Built while redesigning [Refil](https://refil.app), a fuel price app.

## License

MIT
