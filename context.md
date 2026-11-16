# Project context (`init`)

What the project is and what it has already decided, written once to
`.unslop/context.md` in the project and read at the start of every run.
Without it, every session re-asks the same questions or guesses the scale.

## How `init` works

1. **Read before asking.** The README, the app's screens, the token or
   theme files (`tokens`, `theme`, `tailwind.config`, `Color.kt`,
   `Theme.swift`), the existing design doc or skill. Derive the scales from
   the tokens, not from what the screens happen to use. With no tokens,
   propose the base-4 scale (`checklist.md` #1) nearest to the values the
   screens use most, and list the values off it as findings: the scale is a proposal for the user, not a
   fact about the project.
2. **Ask three questions at most**, only what the code can't answer:
   who uses it and in what scene (`process.md` § 2b, step 0), what must
   not change (the brand face, a color, a signature), and which surface
   mode each main area is (`SKILL.md` § Surface modes).
3. **Write the file** with the template below and show it. Commit it only
   on a "yes" to the context itself (a "yes" to a later proposal isn't
   one). Keep it under a screen: it is read on every run. Leave `allow:`
   empty (or drop the line) when nothing is allowed.
4. **Never block on it.** A one-screen quick pass without context runs as
   before and offers `init` at the end, once.

Update it when a decision changes (a new token scale, an allowed rule), not
after every review. A stale context is worse than none: when the tokens
change, reread the file against them.

## Template

The `key: value` lines under **Machine-read** are read by `slop-scan.py`,
`unslop-score.py` and the Claude Code hook when they run in the project;
flags on the command line still win. Everything else is for the agent.

```markdown
# unslop context

## Product
- What: fuel prices near you, cheapest first
- Users: drivers on the move, phone in a holder, often at night
- Scene: glanced at for 3 seconds at a red light; dark car, bright sun
- Platforms: iOS (SwiftUI), Android (Compose), web landing

## Surfaces
- Map, station sheet: Experience (the map is the canvas)
- Settings, history: Operate
- Landing page: Persuade

## Keeps (written decisions; the project wins over the checklist)
- Brand face Manrope for numbers; system font for text (beats #6)
- Price with a small last digit: the signature (#15, #47)
- Base-6 spacing grid (beats #1)

## Machine-read
- scale: 0,1,2,6,12,18,24,36,48
- type-scale: 11,13,15,17,20,24,34
- allow: tracked-caps
- hook: on

## Not negotiable here either
Contrast, focus, target size and invented claims can't be allowed
(principles 5 and 6). They are reported with the measured value.
```

`allow:` takes rule ids from `python3 scripts/slop-scan.py --list-rules`;
each one should match a line under **Keeps**. `hook: off` silences the
Claude Code hook for this project.

## Files `.unslop/` holds

| File | Written by | Commit it? |
|---|---|---|
| `context.md` | `init` | yes: it is the project's decision record |
| `review.md` | each review: the numbered fixes and their state | yes, while work is open |
| `history.json` | `unslop-score.py --save` | optional: the score over time |

`review.md` is the backlog `apply` reads:

```markdown
# unslop review · 2026-11-16 · Station sheet (quick mode)
Score 41 → (pending)
- [x] #19 One accent: Navigate button to ink, accent on the price only
- [x] #11 Price first, 34 pt tabular
- [ ] #20 Quiet badges: "Cheapest" as dark text on a 10% tint
- [ ] #43 One left edge for title, price and address
- [-] #47 Dot-matrix numerals: rejected, the brand face stays (Keeps)
- [~] #65 Stat row as one line: the user keeps the cards for now
```

`[ ]` proposed and accepted, `[x]` applied (rerun the score), `[-]`
rejected with the reason, so the next review doesn't propose it again,
`[~]` deferred by the user ("not now"): *apply* skips it and the next
review may raise it once more.
