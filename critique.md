# Critique (`critique`)

A usability read of a screen or a flow, as a report. It doesn't touch the
code and it doesn't change the score: `unslop-score.py` stays mechanical
and comparable, and this is the judgment the scripts can't make. Use it
before a redesign, when a screen is clean (score 90+) but still hard to
use, or when the user asks "is this easy to use?".

Work on the render, never on the code alone: screenshots or the running
app, light and dark, real data.

## 1. Tasks, not screens

Write the two or three things a user comes to do ("find the cheapest
station on my route", "cancel my plan"). Walk each one as three people:

- **First time:** no idea what the icons mean, reads every word.
- **Every day:** knows the app, wants it in one tap, hates confirmations.
- **Largest text, screen reader:** Dynamic Type at its largest or 200%
  zoom; VoiceOver / TalkBack reading the screen in order.

Count the steps and note where each one hesitates. A task that the
first-time user can't finish is P0.

## 2. Cognitive load (eight checks)

Mark each **pass** or **fail** with the element that fails it.

1. **Four or fewer per group.** Options, tabs, tiles, filters (#72).
2. **One primary action** per screen or sheet (#41).
3. **One decision per step** in a flow; no form asking for what it could
   infer or ask later.
4. **Recognition over recall.** The user never has to remember something
   from a previous screen to act on this one (a code, a price, a name).
5. **Labels in the user's words**, not the system's (`notifications`, not
   `webhook config`; #25, #64).
6. **Nothing to read twice.** Each number once (#17); no instruction that
   repeats the label.
7. **State is visible.** Selected, loading, saved, offline: shown with a
   shape or a word, not only color (#24).
8. **Undo over confirm.** Reversible actions happen and offer Undo (#70).

## 3. Ten heuristics, scored 0-4

0 = broken, 1 = poor, 2 = works with friction, 3 = good, 4 = nothing to
add. One line of evidence for each score, from the screen, never generic.

| # | Heuristic | Ask |
|---|---|---|
| H1 | Visibility of system status | Does it say what's happening and what just happened? |
| H2 | Match with the real world | Its words, units and order are the user's (#16, #52)? |
| H3 | User control and freedom | Back, cancel and undo everywhere a user can get lost? |
| H4 | Consistency and standards | Platform controls, one card per idea (#40, #46)? |
| H5 | Error prevention | Wrong input impossible or caught before submit? |
| H6 | Recognition rather than recall | Options visible; nothing to remember (#12)? |
| H7 | Flexibility and efficiency | Shortcuts and defaults for the everyday user (#54)? |
| H8 | Aesthetic and minimalist design | Every element earns its place (#30, #60)? |
| H9 | Help users recover from errors | The error says what failed and how to fix it (#71)? |
| H10 | Help and documentation | Help where the doubt is, not in a separate page? |

The total (out of 40) is for comparing two versions of the same screen,
not two products. Don't average it into the unslop score.

## 4. Findings

Each finding: severity, where, what happens, the fix (with its checklist
number when there is one).

- **P0** blocks a task or excludes someone (contrast, a target, a dead end).
- **P1** a task succeeds with real friction or a wrong turn.
- **P2** slows the everyday user; a fix worth the next round.
- **P3** polish.

## Report

```text
Critique · <screen or flow> · <date>
Rendered        yes / no (widths, light/dark, largest text)
Tasks           1. … (steps: 4, first-timer stuck at step 2)
Cognitive load  6/8 pass · fails: 1 (7 filters), 8 (delete asks to confirm)
Heuristics      H1 3 · H2 4 · H3 2 · … · total 29/40
Findings        P0 1 · P1 2 · P2 3 · P3 1
Top 3 fixes     #72 …, #70 …, H3 …
Not checked     screen reader on Android, offline
```

Then offer the fixes as a normal review (quick mode), so they go through
the before/after and the "yes" like any other.
