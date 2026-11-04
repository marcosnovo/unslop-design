# Spec card

One card per screen (or per area). It's the contract between the proposal
and the code: a short list of **named** decisions, each with its value, and
a tick when it's applied **and visible on screen**. Reviewers fill it in
their proposal; devs tick it; the fix-by-fix recording follows its order.

Keep names short and stable — the same word in the card, the token, the PR
and the recording. Drop rows that don't apply; add rows only for real
decisions.

```text
SPACING                         TYPE
[ ] Gap      34 pt  between sections      [ ] Font    system / Manrope
[ ] Gutter   16 pt  between items         [ ] Heads   13 pt sentence case, muted
[ ] Padding  24 pt  inside cards          [ ] Title   23 pt semibold
[ ] Rails    16 pt  left/right edges      [ ] Numbers tabular, small unit
[ ] Radius   28 pt  cards (inner = outer − padding)

COLOR                           SIGNATURE (from the domain, #47)
[ ] Canvas   off-white / neutral          [ ] e.g. cut-out photo shapes
[ ] Accent   one use: primary button      [ ] e.g. hand-drawn rank numbers
[ ] Shadows  soft, 2 levels max           [ ] e.g. price with small last digit
[ ] Photos   real, fixed frames

CHROME                          STATES
[ ] Top bar   floating pill, line icons   [ ] Empty   drawn + one action
[ ] Tab bar   floating, create apart      [ ] Long    longest language
[ ] Primary   names its destination       [ ] Dark    checked separately

WEB (if it's a site or web app)
[ ] Widths    390 / 768 / 1280, no horizontal scroll
[ ] Icons     20 px slot, one stroke set
[ ] Focus     2 px ring, offset 2
[ ] Data      mono / tabular for deltas, axes, counts
[ ] Surfaces  color-scheme, ::selection, accent-color themed
[ ] Motion    transform/opacity only, reduced-motion
```

Ticking order = the order the fixes are applied, one at a time (system →
spacing → type → color → signature → chrome). That's also the script of the
before/after recording: one beat per row, the card on screen with the tick
landing as the change appears.
