# Orchestrated process (as used on Refil, rounds 1-6)

## 1. Inventory from videos or screenshots
```bash
mkdir -p "$SCRATCH/frames"
ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4
# Contact sheet: one frame every 2 s, 6×2 per image
ffmpeg -v error -i video.mp4 -vf "fps=1/2,scale=300:-1,tile=6x2" "$SCRATCH/frames/v1_%d.jpg"
```
Look at the sheets (read the image) and write a list: screen → states seen
→ obvious problems, citing the `checklist.md` number. Higher-resolution
frames only for what's unclear (`-ss 00:00:12 -frames:v 1 -vf
scale=1170:-1`). If there's code, locate each screen in the repo (grep the
visible title) before giving an opinion. Reference videos (other people's
before/afters) are read the same way: what you take is the **rule**, not the
style (`references.md`).

## 2. Ground it, then the system and grayscale pass
- **Ground it first**, in four lines the reviewers get: what the product is
  about, who uses it, the one job of each key screen, and one thing only
  this product has (a price board, a route, a scrapbook). Plus the surface
  mode (`SKILL.md` § Surface modes). A proposal that would fit any other
  product starts from here, not from the checklist.
- Before judging screens, check the scales (`checklist.md` § System):
  spacing, type and weights, palette with shades, elevation, radii. Whatever
  is missing goes into an infrastructure PR 1.
- **Grayscale pass** on each key screen (desaturate the screenshot, or mock
  it without color): at a glance, is it clear what matters and what belongs
  together? If not, the fix is spacing/size/weight/contrast, not color.
- **Critique passes on the render**, never on the code alone (screenshots
  or the running app, light and dark):
  1. *One second*: what's the first thing you see? It should be the answer
     (principle 3). *Five seconds*: can you say what the screen is for?
  2. *Squint* (or blur the screenshot): the blocks that remain are the
     hierarchy. Too many equal blobs = flat; one blob = nothing else reads.
  3. *Cover the logo*: could a competitor ship this screen unchanged? Then
     it has no signature yet (#47, #58).
  4. *Count the left edges*: draw a line where each block's text starts.
     A composed screen reuses two to four; a new edge per block means it
     was placed piece by piece (#43; `web-audit.mjs` lists them).
  5. *Gray*: the grayscale pass above.
- **Start with the feature, not the shell.** For a new screen, design the
  functionality (search a flight: fields + button) before the navigation;
  the smallest shippable version, without implying what doesn't exist yet.

## 3. Parallel reviewers (senior product designers)
3-4 agents, one per area (e.g. Home · Detail · Search · Profile, or Shared
modals · Settings · Payments · Widgets).

**Keep the eyes and the numbers apart.** Script output anchors judgment: a
reviewer who has read "91 hits" looks for hits. So the area reviewers judge
from screenshots and code, and one extra agent works only from
`slop-scan.py`, `web-audit.mjs` and `unslop-score.py`; the jury merges both.
With no subagents, write your visual review down before running the
scripts.

Each brief includes:
- the screenshots/frames for THEIR area and the code paths;
- `checklist.md` and the principles from `SKILL.md`;
- the project's current design system (tokens, roles, components);
- the deliverable: an HTML board (before/after drawn with the system's CSS,
  not descriptions) + a numbered list of decisions with their reason
  (citing the checklist #) + what NOT to change;
- that they review what earlier rounds shipped and keep it consistent.
Reviewer deliverable format: an HTML fragment with prefixed selectors
(`.r1 …`) so they don't clash when merged, a "before" faithful to the real
code, an issue inventory with severity and size (S/M/L), each finding marked
"measured" (seen in code) or "unverified", an "after" also in grayscale (it
must hold up without color) and a headless render at 400 px checked by the
reviewer (no horizontal scroll).
Give them each surface's real constraints (WidgetKit, CarPlay/Android Auto
templates, native controls). And real data: long names, 2,000 items, zero
items, the longest language.

**To choose a value** (icon size, spacing, shadow): try the candidate and
its two neighbors on the scale; if an end wins, repeat with it in the
middle. Never pixel by pixel.

**Spec card:** every reviewer ends with a filled `spec-card.md` for their
screens: the named values (Gap, Gutter, Rails, Radius, Heads, Canvas,
Accent…) that the before/after shows. Devs implement the card row by row
and tick only what's visible on screen.

**Jury:** one more agent merges the proposals: a "conflict → winner → why"
table, fixes inconsistent numbers across mockups and leaves a "owner
decides" list per PR. The winner comes from there, not from the prettiest.

## 4. Winning proposal
**Score the plan before showing it.** Rate the merged proposal 1-5 on six
axes, honestly, and put the scores on the page:

| Axis | The question |
|---|---|
| Hierarchy | Is the first thing you read the answer, in gray too? |
| Restraint | Did anything get added that a removal would have solved? |
| Specificity | Covering the logo, is it still this product? |
| Execution | Every value from a token; states, long text, dark mode drawn? |
| Honesty | Only real data, features and numbers (#64, principle 6)? |
| Fit | Right ambition for the surface mode (operate, persuade, read)? |

Any axis under 3 means revise before the user sees it, not after.

Combine the boards into ONE HTML page (an artifact in Claude Code, a local
file in Codex) with: principles,
each screen before/after, numbered decisions, what was dropped and why, and
risks (measured contrast, long languages, states). Hand it to the user and
wait for their "yes" or changes: design is their call.

## 5. Devs per area (senior, in worktrees)
- One agent per area, each in its own git worktree, **commit without push**; a
  closed brief: numbered decisions to implement, files, tokens/components to
  use or create, platforms (iOS + Android/web), languages, tests to touch,
  checks to run, and what not to touch (so areas don't collide).
- Shared work (tokens, base components) goes in an infrastructure PR 1 that
  can merge on its own without redesigning screens; then screens, by real
  usage.
- **In short cycles**: implement what's decided, use it with real data and
  go back to design with what comes up (edge cases, long text). It's easier
  to fix design in an interface you can use than to imagine it.
- To avoid collisions: new strings in a new file per area; each file with a
  declared owner in the brief; each worktree starts with
  `git merge --ff-only <integration branch>` and, if it can't fast-forward,
  stops and reports. If two devs rewrite the same screen, the orchestrator
  picks one and says so in the PR.
- **A new entry point to an existing action calls the SAME function** as the
  original entry (same plan gate, same picker, same logging). It was the
  most repeated bug: a new button that skipped the free-tier limit or the
  app picker.
- Integrate: temporary branch, merge each worktree; generated files
  (strings, resources) in conflict are regenerated with the repo's tool,
  not resolved by hand.

## 6. Verify before pushing
- Whatever compiles in your environment: build and tests.
- Whatever doesn't (e.g. iOS without Xcode in the cloud): an auditor agent
  reads the whole diff looking for symbols outside their target, APIs with
  doubtful signatures, availability, concurrency, non-exhaustive switches,
  tests referencing deleted code and giant UI expressions; fix and say so
  in the PR.
- Contrast: a script that reads the real hex values and computes ratios —
  also after merging or renaming roles (an alias dropped a small usage to
  3.8:1) and never trusting a comment ("4.5:1" that was 4.26).
- Off-scale literals: grep the diff for stray numbers in paddings, font
  sizes, radii and shadows (`padding(13)`, `fontSize = 15.sp`, `#3a7bd5`):
  each one is a missing token. `scripts/slop-scan.py <changed paths>` does
  it, together with the other patterns.
- Web: `scripts/web-audit.mjs` before and after, light and dark (`web.md`
  § 6); attach both reports to the PR.
- `scripts/unslop-score.py` before and after (with `--audit` on the web):
  "score X → Y" goes at the top of the PR, with the rows still costing
  points.
- Grep every changed string and symbol in UI tests, previews and
  showcase/demo code too: they don't run in CI and go stale.
- Audits in parallel with CI: one for **compilation** and one for
  **parity** across platforms; wait for both before merging.
- Reread the diff as a reviewer: untranslated strings, spacing/color
  literals, hardcoded currency.

## 6b. Fix-by-fix recording (optional, great for the PR and for sharing)
Capture the screen after each card row lands (same device, data and
position), then cut a 10-15 s clip: one beat per row, the spec card beside
the phone with the tick appearing as the change does. It proves each fix on
its own and doubles as release material.

## 7. PR and loop
- Run local checks before pushing (don't burn CI minutes).
- A job that dies in 1-2 s with no steps = no runners or quota exhausted:
  rerun once, note it in the PR, and keep working on something else.
- PR with what changes per area, verification done, what was NOT compiled
  and known limits. Answer review bots (verify each finding, fix what's
  real, reply in the thread and resolve). Squash-merge with green CI and no
  open threads.

## 8. Close the round
- A prompt for a local session (with a Mac/simulator) that builds, takes
  screenshots in light/dark/largest text/another currency and fixes what's
  broken without redesigning.
- After the last round: update the project's design system (one doc with
  tokens, roles with measured contrast, components, a cross-platform map),
  delete unreferenced leftovers and create/update the project's own design
  skill.
- For next time: when a design you like shows up, note **the decision you
  wouldn't have made** (an inverted background, a button inside the field,
  two colors in one headline) and, if you can, rebuild it without peeking at
  the code: that's where new checklist rules come from.
