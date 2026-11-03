# Cases and sources

## The before/afters that shaped this skill
Short videos (Oct/Nov 2026) of "unslop" redesigns of iOS apps. What's worth
taking from each is the **rule**, with its checklist number; don't copy
their style.

**1. Finance (SwiftUI, "16 fixes, one at a time").** Balance on a lime card
with a "Net" badge, a dashed frame, stacked cards, an icon in a circle,
"Welcome!" as the title and a horizontal carousel of tips.
Fixes, one per step with the diff visible: uniform card padding and
group spacing (#8, #9) · lime background gone, one accent (#19) · quiet
badge (#20) · dashed frame, stacked plates and icon circle removed (#30,
#33) · title = "November 2026" (#26) · sentence case (#25) · one card,
balance first (#11, #40) · the 14 dots of "upcoming payments" → "₺1,700 ·
Yapı Kredi installment · 2 days" (#18) · carousel → stack (#40) · the period
summary repeating income/expenses removed (#17).

**2. Workout (light).** Spacing measured and annotated on the screenshot
(the stray 13 and 17 px move onto the scale, #1) · purple button → ink
capsule naming its destination "Continue · Full Body Strength" (#41) ·
completed days in status green, not the accent (#19) · generic dumbbell
illustrations → a domain render (#35).

**3. Running (dark).** Purple gradient background, colorful cards, "Hey
Alex! 👋", gradient button with an emoji. After: neutral dark background,
"Morning run" title with an all-caps letter-spaced overline (#26, #29), a
single warm glow on the data card (#30), emoji → 1.5 px stroke icons (#33),
dot-matrix numerals as the one signature gesture (principle 7), a sparkline
with the latest point marked (#18), mini bars and a ring as context for
each number, "Start run" with its "GPS ready" state (#41).

**4. Progress (bar chart).** "123 min earned" becomes a large number with
the small unit on the same baseline (#15) · bars in a light tint with today
saturated and the value written above, no gridlines (#39) · very light gray
background and white cards to separate without borders (#31) · trophy emoji
→ a custom illustration (#33, #35).

**5. Social photo feed ("what did you get up to?").** The video shows a
spec card beside the phone and ticks each row as it lands — the idea behind
`spec-card.md`. Spacing first: one gap between sections, rails at 16 pt,
radius 28 (#1, #43, #44) · filler line "✨ Share your best moments" removed
(#44) · emoji section headers → small caps labels (#45) · ✈️ 🔔 and emoji
tabs → line icons in floating glass pills, create as its own black circle
(#33, #46) · one red primary, the only accent on screen (#41) · a scrapbook
signature: stadium-shaped photos, hand-drawn rank numbers, a polaroid
sticker for "your story", a taped handwritten caption (#47) · real photos,
places and times in the feed (#48).

**6. Web dashboard ("EmberAI", from Damir Sokolovsky's unslopping post on
X).** A purple-gradient finance dashboard with emoji everywhere. The video
first draws the spacing on top (16, 24, 36, 18, 32, 20 px: no scale, #1)
and a guide through the nav showing labels starting 13 px and 8 px from the
icons (#49). Then: purple tint, glows and gradient text gone, neutral dark
canvas (#55) · emoji → line icons; plan emoji → small dots in the same
colors as the chart series (#33, #51) · pill counts → muted tabular
numbers, "New ✨" → a chevron (#50) · ALL CAPS overlines → muted
sentence-case labels (#45) · "Welcome back, Damir!" → "October 2026" with
the year muted (#26) · "+12%!!" → "+12% vs last month" in a mono data voice
(#52, #56) · "Search anything… ⌘K" → "Search" with two key caps (#54) ·
"EmberAI PRO" → "Ember", the bell → a sidebar toggle (#55, #57) · clip-art
card → a rendered card (#35) · glowing bars → series lines with a few axis
ticks (#39). `examples/` rebuilds it so the scripts have something to bite.

## Refactoring UI (Wathan & Schoger): what it adds to the checklist
| Chapter | Idea | # |
|---|---|---|
| Starting from scratch | Feature before shell; details later; design in grayscale; smallest shippable version; don't imply what doesn't exist; personality (font, color, radius, tone) | process § 2, #6, principles 2 and 6 |
| Limit your choices | Systems for everything (type, weight, line height, color, spacing, width, shadow, radius, border, opacity); choose by elimination between neighbors | #1-#5, principle 1 |
| Hierarchy is everything | Weight and color before size; 2-3 text tones, 2 weights; no gray on color; emphasize by de-emphasizing; labels as a last resort; small section titles; balance weight and contrast; action pyramid; big red destructive only on confirm | #11-#14, #22, #41 |
| Layout and spacing | Start with too much space; non-linear scale (≥ 25% between neighbors); don't fill the screen; max-width before grids; non-proportional sizing; more space around a group than within | #1, #7-#10, #42 |
| Designing text | Hand-picked scale in px/rem; system font or ≥ 5 weights; 45-75 characters; baseline alignment; line height inverse to size; not every link colored; left-aligned text and right-aligned numbers; tracking for headlines and caps | #2, #15, #23, #27-#29 |
| Working with color | HSL; 8-10 grays and 5-10 shades per color defined up front; saturation at the extremes; rotate hue to lighten/darken; tinted grays; flipped contrast; don't rely on color alone | #3, #4, #20-#24 |
| Creating depth | Light from above; shadows = elevation (system of ~5); two layers; lighter feels closer; overlapping layers | #5, #32 |
| Working with images | Good photos; consistent contrast over images; intended size of icons and screenshots; user content in fixed frames | #33, #35-#38 |
| Finishing touches | Supercharge the defaults; accent borders and decorated backgrounds in moderation; empty states as a priority; fewer borders; rethink components (selectable cards) | #31, #34, Also |
| Leveling up | Note the decision you wouldn't have made; rebuild designs you like | process § 8 |

**Where this skill is stricter than the book.** The book allows accent
borders, gradient backgrounds and icons inside shapes as ways to "add
life"; in reviews of AI-generated apps those are exactly the tics to
remove, so here they come with conditions (#30, #33, #34): once per screen,
with a purpose, and never on every row.
