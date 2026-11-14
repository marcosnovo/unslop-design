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
  product starts from here, not from the checklist. The fourth line is
  the seed of the concept (§ 2b).
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
  6. *Ten-app lineup*: blur the text and logo and set the screen in a row
     of nine generic AI app screens (greeting, hero stat card, 2×2 tiles,
     list, tab bar, purple-blue accent, rounded cards). Can you pick it
     out, and by which two attributes (structure, palette, type, shape,
     object)? "No" means it's a template (#65). Cover-the-logo asks whether
     a *competitor* could ship it; this asks whether *any* AI app could.
     Operate and Read: one attribute is enough.
- **Render at device size.** Native screens mocked in HTML are judged at
  the device's points and pixel density (393×852 @3x, 375×667 for the
  small phone, 412×915 for Android), with the status bar and home
  indicator drawn, the system font stack, and once at the largest text
  size. `web-audit.mjs --device` does it and says which font actually
  rendered: SF Pro isn't installed on Linux or CI and can't be
  redistributed, so a fallback is fine for critique as long as the report
  says so.
- **Start with the feature, not the shell.** For a new screen, design the
  functionality (search a flight: fields + button) before the navigation;
  the smallest shippable version, without implying what doesn't exist yet.

## 2b. Find the concept
A concept is **one sentence that makes design decisions**: "a running app
built around an athletics track", "a sleep app as a village going to
sleep", "a plant app as a paper cut-out", "Italian lessons on Neapolitan
playing cards". "Clean", "minimal" and "premium" are not concepts: they
describe a result and decide nothing. Principle 7 and #47 are what a
concept looks like when the budget is small.

**Scope by surface mode** (`SKILL.md` § Surface modes): Operate and Read
get a signature (one detail family on a native shell; never a fill);
Persuade, one bold idea in the hero and one more place; Experience, a
world (type, layout, color, illustration and motion all come from it).

**Procedure (ten minutes):**
1. List 5-8 candidates from the domain's physical world, not from other
   apps: tools of the trade (stopwatch, jar, seed packet), places (track,
   village, market stall), rituals (lights out, watering day, dealing
   cards), printed things (playing cards, timetables, race bibs, ledger
   paper), ways of making (paper cut-out, woodblock, enamel sign).
2. Name each one's **rules**, not its look: lanes and a ruler on the left
   rail; a jar that fills; a suit and a corner index; windows going dark.
   Rules become layout and data; looks become skins.
3. Drop whatever fails a test:
   - *Reach*: it explains at least the type, the layout and one
     interaction or data display. Only a palette and an illustration = a
     skin.
   - *Competitor*: it would fit the leading competitor unchanged
     (cover the logo).
   - *Legibility*: in grayscale the screen still reads (principle 2);
     every text/fill pair passes the contrast floor, secondary text
     included, light and dark (principle 5, #21, #22); the answer is still
     the first thing you read (principle 3); it survives the largest text
     size and the platform's own controls.
   - *Honesty*: a jar that fills, fills from real data; no lux, calories
     or pace the app can't measure (principle 6, #64).
   - *Dullest screen*: it can still be shown on settings, an empty state,
     an error, a 2,000-row list and the longest language. If it only works
     on the hero shot, it's a poster, not a design.
4. Write the survivor as: *sentence · the rules it borrows · its
   consequences for type, layout, color and motion · where it stops* (the
   parts that stay native: tab bar, sheets, settings) · *dark variant or
   "one appearance"*. "Where it stops" is mandatory.

**Concept slop** (the new template, watch for it):
- *Theme park*: the metaphor leaks into the copy ("Your lane awaits,
  champion!"). Copy stays plain (#25, #26); the concept lives in form.
- *Metaphor over the answer*: the jar hides the exact amount, the village
  hides the alarm time. The number stays first and exact; the metaphor
  shows what it means.
- *Skin on a template*: a paper-cut leaf above a standard card list, or
  the same layout in red and in blue. Delete the illustration: if the
  layout reads as a template, the concept never reached it (#35, #65).
- *Every screen a poster*: a saturated full-bleed fill plus a second
  accent, secondary text at 3:1 on it. World color is one canvas or one
  gesture, never both (#19).
- *Stock metaphor*: a rocket for launch, a trophy for streaks, a sprout
  for growth. Fails *Competitor* by construction.

## 2c. Three directions (before anything is polished)
The first idea is the most generic one. For a new product, a redesign or
any Persuade or Experience screen, explore **three directions that differ
in concept**, compare them and continue with one.

- **Different means a different source** (object, place, ritual, printed
  thing), so type, layout and color differ by consequence. **The
  orchestrator assigns the sources**, one per agent, before they start: the
  grounding's fourth line (the one thing only this product has) seeds every
  agent toward the same idea otherwise. In a test run the control and one
  bold direction both turned the ingredients into the same checklist. Three palettes
  on one layout is one direction. Keep one *safe* direction (a signature on
  a native shell) as the control: it shows what the bolder ones cost. The
  control's brief leaves out the fourth grounding line, so it stays a
  control.
- **One card each**, all on the same key screen (the answer screen), drawn
  with real content (#48) and its grayscale:

```text
Direction A · <name>
Concept     one sentence
Borrows     the object's 2-3 rules
Type        face + how numbers look
Layout      the one structural consequence
Color       2-4 values, roles named (#19), contrast measured
Motion      one named interaction (#63), drawn as a second frame
Stops at    what stays native
Risk        the hardest test it faces (long text, dark, density)
```
- **Draw the interaction, don't describe it.** In Persuade and Experience
  the key screen comes with a **second frame**: the same screen mid-way
  through the concept's one interaction (the board at the handoff, the jar
  as a coin drops, the row being ticked off). A static render can't show
  an interaction, and the critic of § 4 can only remove or replace, so
  without this frame Specificity stays at 3 however good the concept is.
- **Compare** with the six axes of § 4 plus *Reach* and *Cost* (how much
  must be redrawn or illustrated and maintained). Hierarchy or Honesty
  under 3 disqualifies a direction. Don't average: recommend one, name what
  you'd steal from the others, and **the user picks**. The pick goes into
  the spec card's CONCEPT rows.
- **Quick mode**: three one-line concepts, the pick and why in one
  sentence, render only the pick. **Full flow**: after the system check and
  before the area reviewers, one agent per direction in parallel, blind to
  each other, all drawing the same key screen. Never one set of directions
  per screen: one key screen decides and the card carries the rest.

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
- **one owner for each shared component** (tab bar, navigation, buttons,
  switches, the type and color tokens): the reviewer whose area owns it
  redesigns it, and the others draw it as it is. Two reviewers redesigning
  the same tab bar is a conflict the jury then has to undo;
- `checklist.md` and the principles from `SKILL.md`;
- the project's current design system (tokens, roles, components);
- the chosen direction's card (concept, rules, "stops at"): reviewers apply
  it to their area and flag where it fails a § 2b test; they don't reopen
  the choice;
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

**Redraw after the jury.** The jury's table changes values on paper; the
boards, spec cards and decision lists still show the old ones. Before the
second critic (§ 4) and before the owner sees anything, each area reviewer
(or one agent for all) applies the jury's table to all three and
re-renders the board. Otherwise the critic judges values already replaced
and the proposal shows them (in a test run, two of the critic's three
findings), and the devs, who implement the spec card row by row, build
them: a quantity unit shipped at 15 px from a stale card after the jury
had set 14 (0.875rem). No script catches it, both values are valid.

## 4. Winning proposal
**Score the plan before showing it.** Rate the merged proposal 1-5 on six
axes, honestly, and put the scores on the page:

| Axis | The question |
|---|---|
| Hierarchy | Is the first thing you read the answer, in gray too? |
| Restraint | Did anything get added that a removal would have solved? |
| Specificity | Covering the logo, is it still this product? Does the concept reach type, layout and one interaction (judged on the second frame, § 2c)? |
| Execution | Every value from a token; states, long text, dark mode drawn? |
| Honesty | Only real data, features and numbers (#64, principle 6)? |
| Fit | Right ambition for the surface mode (operate and read: a signature; persuade: one idea; experience: a world)? Does it survive the dullest screen? |

Any axis under 3 means revise before the user sees it, not after.

**Second critic (two rounds at most).** Your own scores run optimistic.
Before the user sees the proposal, a separate agent that didn't design it
judges the **render** only: light, grayscale and dark if drawn, the
interaction's second frame for Persuade and Experience (§ 2c), plus the
four grounding lines and the surface mode, and the checklist's fix titles
only, so findings can cite a number:
`grep -E '^[0-9]+\. \*\*' checklist.md`. Not the spec card, the
rationale, the code or script output. (No subagents: answer 1-3 from the
image alone before rereading your own card.) It answers, in order:
1. *Blind read*: what is this app, what's the screen's one job, what do
   you see first?
2. *Lineup*: among nine generic AI screens, can you pick it out? By which
   attributes?
3. *Skeleton*: the blocks top to bottom, six words each. Which exist only
   because templates have them (#60, #65)?
4. *Sameness*: how many siblings share one container? Which could be an
   object or plain type on the canvas (#58)?
5. *Score* the six axes, one line of evidence each.
6. *Findings*: three at most, each with where · checklist # · the smallest
   change that removes or replaces (never "add"). Verdict PASS or REVISE.

The designer applies the findings one at a time and re-renders; a
**fresh** critic (no memory of round 1) asks the same questions; the
orchestrator checks round 1's findings are gone. **Stop** when every axis
is ≥ 3 with Specificity ≥ 4 for Persuade and Experience and the lineup
answer is yes, when the critic says PASS, when a round raised no axis
(keep the better render), or after two refines (list what's open under
"owner decides"). The lower of the designer's and the critic's score wins
per axis; a fix can't add a block unless it replaces one. A finding that
contradicts a checklist rule (dropping the destination from the primary
button against #41) is rejected, with the number, not applied. Before
applying the rest, check two things the critic can't: that the rule it
cites says what the finding claims (read the fix, not just its title),
and that a contrast finding holds against the audit's measurement, since
eyes misjudge gray on dark (principle 5). A claim the numbers refute is
rejected with the ratio.

Combine the boards into ONE HTML page (an artifact in Claude Code, a local
file in Codex) with: principles,
each screen before/after, numbered decisions, what was dropped and why, and
risks (measured contrast, long languages, states). Hand it to the user and
wait for their "yes" or changes: design is their call.

## 5. Devs per area (senior, in worktrees)
- **The tokens file has one owner: the orchestrator.** Devs don't add
  tokens; a value their screen needs that isn't a token goes in their
  report, and the orchestrator adds it (to PR 1, or one infra commit on the
  integration branch) and tells the others. Two devs adding tokens in
  parallel invent the same value twice under two names (`--bw` and
  `--hair`, both 1px) and collide at the end of the file.
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
  points. Both numbers come from **the same version of the scripts**: when
  they change, measure the before again (check it out, rerun it). A test
  screen's before went from 35 to 22 between two releases while nothing in
  it changed.
- Tokens resolve: `slop-scan.py` flags a `var(--name)` that no scanned file
  defines (after a rename, a dangling one falls back in silence). Scan the
  token file together with the screens.
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
