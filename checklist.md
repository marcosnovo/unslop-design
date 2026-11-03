# Fix checklist (one at a time)

Each fix: what looks wrong → what to do → how to check it. Apply them one
at a time and look at the screen in between: several at once hide which one
helped and which one broke something. Numbers are stable so reviewers can
cite them ("#14") in their boards.

## System (before touching screens)
1. **Non-linear spacing scale.** Base 4, values spreading further apart as
   they grow (4/8/12/16/24/32/48/64; 20 only if the project already has it).
   Neighbors never closer than ~25%: there's no decision to make between 120
   and 125. A stray 13, 15 or 18 is noise.
2. **Hand-picked type scale**, not modular or relative: 6-8 sizes (e.g.
   12/14/16/18/20/24/30/36/48) and **two weights** (regular 400-500,
   emphasis 600-700). Nothing below 400 in UI: to de-emphasize, use color or
   size, not a thin weight.
3. **Palette with shades defined up front.** Grays: 8-10 shades from the
   darkest text (never pure black) to an almost-white background. Accent and
   roles: 5-10 shades each (100-900; 500 works as a button background, 900
   for text, 100 for tinted backgrounds). No on-the-fly "lighten/darken":
   that's how you get 35 nearly identical blues. Away from 50% lightness,
   raise saturation so shades don't wash out.
4. **Grays with a temperature**, the same across the app (a bit of blue =
   cool, a bit of yellow = warm). Mixing cool and warm grays reads as
   carelessness.
5. **Named elevation**: 3-5 shadows max, each with a meaning on the z-axis
   (button < menu < sheet/modal). You choose the height, not the shadow.
   Radii: three max (row, panel, card) and capsule only for buttons and
   chips; don't mix square and rounded corners.
6. **A chosen personality, not an inherited one.** Font, radius, color and
   copy tone say the same thing (serious/friendly/technical). Default to the
   system font; a custom font only if it has ≥ 5 weights and a good
   x-height.

## Spacing
7. **Start with too much white space and remove.** What looks like "a bit
   much" on a lone element is usually just right on the full screen. Dense
   is a decision (data panels), not the starting point.
8. **Groups, not rules.** More space **around** a group than **within** it
   (8-12 inside, 24-32 between groups). Label hugging its field; section
   title with more space above than below. If you need a divider to tell
   blocks apart, you're missing space.
9. **Uniform card padding** (16-20) across the app; concentric radii (inner
   = outer − padding) where it shows: the button inside its card. Don't
   change a token nobody will notice.
10. **You don't have to fill the screen.** Each block gets the width it
    needs (max-width, not percentages); what works narrow gets split into
    columns instead of stretched. Design at ~400 px first.

## Hierarchy
11. **Data first.** The hero number on top and large (tabular digits); small
    gray label below. One number, not three of the same size competing.
    Build hierarchy with **weight and color** before size: primary text
    dark, secondary gray, tertiary light gray.
12. **Labels are a last resort.** "12 left in stock" beats "Stock: 12"; "3
    bedrooms", not "Bedrooms: 3". If the format already says it (price,
    email, date), no label. If one is needed it's secondary (smaller,
    lighter); only on spec sheets, where people scan for the label, does the
    label lead.
13. **Small section titles.** A section title is a label, not an `h1`: the
    content leads. Semantics (h1, `.headline`) don't decide the size.
14. **Balance weight and contrast.** A solid icon next to text weighs more:
    lower its contrast. A 1 px border you can't see: make it thicker, not
    darker.
15. **Parts of a number, with rules.** If you shrink a part (decimals, last
    digit, unit): only when it applies (e.g. 3 decimals and ≥ 17 pt), never
    the separator, relative size so it scales with the rest, **aligned on
    the baseline** (not centered), and the screen reader reads the whole
    number. "123 min earned": large number, small unit, same baseline.
16. **Only numbers that exist.** No ETA without data, no "vs. last month"
    without two periods, no "Today" if it's "Latest". A delta only if it
    shows in the last printed digit (otherwise you get "−0"). A list shows
    the value it's sorted by. Same numbers across all mockups.
17. **Each number once per screen.** A "period summary" repeating income and
    expenses already shown above goes away, or becomes what's missing (the
    trend, the next payment).
18. **What's next, concretely.** "Next payment: Dec 4 · $120" beats 14 dots
    without axes. If there's a series, highlight the latest value (today)
    and mute the rest.

## Color
19. **One accent.** The brand color fills ONE specific gesture or the hero
    number, not card backgrounds, icons and titles all at once. Merge
    redundant roles ("medium" without color, "expensive" = "up"); red only
    for errors and delete. Done = status green, not the accent.
20. **Quiet badges.** An informational badge is **dark text of the role on a
    light shade of the same role** (flipped contrast), not saturated accent
    with white text. Strong fill is reserved for "best"/"now".
21. **Text on a brand fill = dark ink.** White on green, lime, yellow or
    light blue usually lands at 2-3:1.
22. **No gray or semi-transparent white on colored backgrounds.** It looks
    washed out and disabled. Secondary text on a colored panel = a shade of
    the same hue, adjusting saturation and lightness; if it can't reach the
    contrast, rotate the hue ≤ 20-30° toward a brighter one (yellow, cyan,
    magenta).
23. **Neutral global tint.** Toolbar buttons, links and checkmarks in the
    text color; the accent only on stateful controls (switch, slider,
    progress). Not every link needs a color: where everything is a link, use
    weight or a darker tone.
24. **Color never works alone.** Up/down/better/worse also via shape or word
    (arrow, "−6%", "Normal"): color blindness, tinted mode, monochrome
    widgets. In multi-series charts, separate by **light/dark** of one hue,
    not by different hues.

## Typography
25. **Sentence case everywhere** ("Expense added", "Add expense"), buttons
    with verb + object, no exclamation marks or AI jargon ("Unlock your
    potential!"). Numbers with their unit and the user's currency, never
    hardcoded.
26. **Page title = what it is, not a greeting.** "Morning run", "November
    2026", not "Hey Alex! 👋". Date or context small (above or below), or
    as a second tone in the same line ("October" in ink, "2026" muted). One
    concept, one name across the app; name the feature, not the ownership.
    Renaming a product is the owner's call.
27. **Line height inverse to size.** Small text or long lines: 1.5-2; large
    headlines: ~1-1.2. Paragraphs at 45-75 characters per line even if the
    block is wider.
28. **Align for readability.** Text left-aligned; centered only for
    headlines and blocks of ≤ 2-3 lines (if one runs long, rewrite it
    shorter). Numbers in tables right-aligned, with tabular digits.
29. **Letter-spacing with intent.** Large headlines set in a text font: a
    bit tighter. ALL CAPS (overlines, "WED, OCT 28 · 7:42"): wider. Leave
    the rest as the type designer set it.

## Decoration and depth
30. **Remove frames and ornaments.** Dashed borders, meaningless stacked
    shadows, background gradients, emoji as icons, icons inside colored
    circles on every row, decorative glow/blur. One light effect at most,
    and only where there's data.
31. **Fewer borders.** To separate, in order: more space → two slightly
    different backgrounds → a soft shadow. Borders last. If backgrounds
    already differ, drop the border.
32. **A shadow means height, not style.** Light comes from above: raised
    elements get a slightly lighter top edge and a short shadow below;
    inset ones (fields, wells) the reverse. A shadow = two layers (a wide,
    soft one and a short, dark one that fades the higher the element sits).
    Dragging raises it; pressing lowers it. In flat design, lighter reads as
    closer. No photorealism.
33. **One icon style.** One set (SF Symbols / Material) with a uniform
    stroke (e.g. 1.5 px), one weight, one size per context; **no emoji** as
    icons; none that repeat the text beside them. An icon drawn at 16-24 px
    isn't scaled to 64: use it at its size (or inside a shape, only in empty
    states and highlights, not on every row). A large logo isn't shrunk to a
    favicon: redraw it simplified. Data from another source (community,
    estimated) is marked with shape (dashed outline + word), not a new color.
34. **Decoration allowed, with conditions.** If a screen still feels flat
    after fixing hierarchy and spacing: a section background color, a
    two-hue gradient ≤ 30° apart or a low-contrast pattern, once per screen
    and never behind small text. Better to "supercharge what's there"
    (checkmarks instead of bullets, selectable cards instead of a stack of
    radio buttons) than to add pieces.

## Images and charts
35. **Good images or none.** Generic clip art, template illustrations or
    filler phone photos = slop. A quality photo or render from the domain,
    or nothing.
36. **Text over images with consistent contrast**: dark/light overlay,
    lower the image contrast, colorize it with one hue, or a text glow with
    no offset. Never text straight on a photo with light and dark areas.
37. **User content (and third-party logos) in a fixed frame**: fixed aspect
    ratio with centered crop; against background bleed, a soft inner shadow
    or semi-transparent border, not a solid border.
38. **Screenshots inside the UI (store listing, landing page)**: don't shrink
    them to 30%; crop partially, capture at a smaller size, or draw a
    simplified UI.
39. **Charts without noise.** Remove gridlines and axes nobody reads; write
    values above bars when they fit; current period saturated, the rest in a
    tint of the same hue; an axis only if its numbers get used. On a
    dashboard people do read the axis: keep 3-4 ticks in the data voice
    (#56), series in their category colors (#51) and no glow on the bar you
    want to highlight.

## Layout
40. **One card per idea, the same everywhere.** The "answer card" repeats on
    every screen answering its question; a single entity row for every
    list. No horizontal carousels hiding content
    (`ScrollView(.horizontal)` of cards): stack them. No card inside a card.
41. **Action pyramid.** One primary per screen/sheet: an **ink** capsule
    (by default the accent stops being a button color; it can fill the
    primary only when that is its single use on the screen and the label
    passes contrast) that **names its destination**
    ("Continue · Full Body Strength", "Go to Shell · 0.7 mi") and, if it
    helps, its state ("● GPS ready"); secondary = gray or outline; tertiary
    = link. Destructive in red **only in the confirmation step**; elsewhere
    secondary or tertiary. "Cancel" is always secondary. Exception: when the
    law requires two equal options (consent). Height ≥ 44 pt / 48 dp.
42. **Components don't scale proportionally.** A large button gets
    relatively more padding and a small one less; a headline isn't "2.5×
    body" on every screen. Each size is tuned, not zoomed.

## Chrome and signature
43. **Rails: one left edge, one right edge.** Every block starts on the same
    left line and ends on the same right one (e.g. 16 pt). Horizontal rows
    start on the left rail and bleed off the right edge to say "there's
    more". Draw the rails over a screenshot: whatever pokes out is a bug.
44. **One gap between sections, no filler copy.** The space between
    sections is a single token (e.g. 34 pt) everywhere. Lines like "✨ Share
    your best moments" that only fill a hole are deleted: the gap separates.
45. **Section headers are labels.** Small, all caps with a little tracking,
    no emoji: "THE GOOD ONES", not "🔥 The good ones" (#13, #29, #33). In a
    dense tool (a sidebar with many groups) a muted sentence-case label
    ("Plans") is quieter still. Pick one style per product.
46. **Floating chrome in the platform material, content solid.** Top bar
    and tab bar float as pills in the system material (Liquid Glass, blur)
    with line icons; the main create action is its own solid circle, not a
    tab. Glass never goes on content cards or behind long text.
47. **A signature is a family, not a trick.** If the domain has a metaphor
    (a scrapbook for a photo app, a price board for fuel), take a small set
    of details from it — cut-out photo shapes, hand-drawn rank numbers, a
    taped caption, a sticker instead of the 📷 emoji — each with one role,
    and nothing else decorative. Still principle 7: from the domain,
    degrading where it doesn't apply.
48. **Real content in every mock.** Real photos, names, places and times
    ("williamsburg · 2m") in proposals and screenshots. Gray boxes and lorem
    ipsum hide whether the layout survives a long name or a dark photo.

## Web and dashboards
49. **One icon slot.** Nav icons sit in a fixed-width column (e.g. 20 px)
    so every label starts on the same line, with or without an icon. Draw a
    vertical guide through the labels: an emoji 13 px wide next to one 8 px
    wide shows up immediately (#43).
50. **Counts are text, not pills.** "Inbox 12" is a right-aligned tabular
    number in the muted tone; a filled pill only for what needs action now
    (unread mentions, a failure). "New ✨" badges, "👤" after every count
    and plan badges on the logo go.
51. **One category, one color, everywhere.** If plans or series need color,
    each gets one hue used as a small dot in the nav, the line in the chart
    and the legend — the same token. Color that only decorates a row goes
    (#19, #24).
52. **A delta names its baseline.** "+12% vs September", "3 fewer than last
    week" — never "+12%!!" or an emoji. Up/down in the role color and a word
    or arrow (#16, #24).
53. **Interactive states are drawn.** Hover, `:focus-visible` (a visible
    ring, never `outline: none` alone), active, disabled and selected. The
    selected nav row is a quiet filled row, not a gradient pill with a glow.
    Keyboard users see where they are.
54. **Shortcuts as keys, placeholders as verbs.** `⌘` `K` as two quiet key
    caps (`<kbd>`), the field says "Search", not "Search anything…".
55. **No gradient text, no page glow.** Headline in the ink color, page on
    a neutral canvas, colored `box-shadow` glows and translucent cards over
    a purple gradient gone. The default AI palette (purple → blue,
    fuchsia accents) is a decision only if someone made it (#19, #30, #32).
56. **A data voice, if it's a tool.** Deltas, axes, counts and timestamps
    can share one secondary face (a mono or tabular face) so data reads as
    data. One family more at most, only for numbers and metadata (#2).
57. **Works at 390, 768 and 1280 px.** No horizontal scroll at any width;
    the sidebar collapses behind a toggle (that toggle earns the top-left
    slot, not a bell); cards reflow with `minmax()`; tables scroll inside
    their own container. Check with `scripts/web-audit.mjs`.

## Also (what came up in real reviews)
- **Sheets/modals sized to content**, not fixed heights that clip text at
  larger type sizes; opaque background over maps or glass; a visible close
  (✕/"Done"), never gesture-only.
- **Order depends on state** (e.g. savings first when there's no live
  alert); know the state before drawing so nothing jumps.
- **Empty states as a first impression**, not centered gray text: what this
  is + one clear action (+ an image if there's a good one), and **without
  the tabs and filters** that do nothing until there's content. Two
  different empties: "no data" (silhouette, no number) and "data but
  zero/negative" (compact line).
- **Surface contrast**, not just text: a dark hero has to separate from its
  neighbors (map, system cards).
- **Size caps on chrome**: fixed chips and circles limit their text size so
  the card doesn't overflow the screen.
- **Delete before redesigning** dead screens; merge duplicates that have
  already drifted.
- **Exempt**: brand moments (splash, login, milestones), onboarding and
  paywall get their own review, not this checklist blindly.
- **States**: empty, loading, error, no permission, free vs. paid — each one
  drawn.
- **Accessibility**: largest text size without clipping, VoiceOver/TalkBack
  reads one sentence ("$3.29 a gallon, 6% below average, 0.7 miles away"),
  touch targets ≥ 44.
- **Dark mode** reviewed separately: 10-15% tints and grays change contrast;
  elevation comes from lighter surfaces, not shadows.
- **No invented data**: a number in a headline is one the user has already
  seen; if there isn't one, use the generic headline.
