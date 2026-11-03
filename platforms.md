# Platform notes

## SwiftUI
- Tokens in a `Theme` (Colors by role, Fonts, Spacing, Radius, Elevation);
  button styles (`ButtonStyle`) for primary/secondary/tertiary; a custom
  `ToggleStyle` if the global tint is neutral and switches should keep the
  accent.
- `.tint(label)` at the root + `UIAppearance` for what SwiftUI can't reach.
- Numerals: `monospacedDigit()`, split integer/decimals into a component
  (`PriceNumeral`) and have VoiceOver read the whole number. Number + unit
  in `HStack(alignment: .firstTextBaseline)`, never centered.
- Line spacing and tracking as tokens: `.lineSpacing` for body, positive
  `.tracking` on all-caps overlines, slightly negative on large headlines.
  Secondary text with `.foregroundStyle(.secondary)` / roles, not
  `.opacity` over white.
- Elevation: `.shadow` only from the token; in dark mode, a lighter surface
  instead of a shadow.
- A `body` with more than ~10 multi-statement closures gets split into
  stages (`with…<Content: View>`): with strict concurrency the type-checker
  blows up.
- Sheets: measured `presentationDetents` (`onGeometryChange`/
  `GeometryReader`) instead of fixed heights, **measuring with the padding
  inside** (otherwise it shrinks in a loop). Present with `.sheet(item:)`,
  not `isPresented` + `if let` (opens empty). `.task(id:)` with ALL inputs
  in the key.
- Calls with long arguments (ternaries with closures) → extract to
  properties: the type-checker gives up.

## Jetpack Compose
- Same tokens in `ui/theme` (colors by role, spacing, shapes, elevation,
  `TextStyle` with `lineHeight` and `letterSpacing`); `onSizeChanged` for
  measured sheets (before the outer padding, not after); never a
  `horizontalScroll` nested inside another horizontal scroll (crash).
  Inserting a header into a `LazyColumn` shifts scroll indices: add the
  offset.
- Number + unit in a `Row` with `Modifier.alignByBaseline()` on each text;
  tabular digits with `fontFeatureSettings = "tnum"`.
- Strings generated from the source of truth if there is one; not by hand.

## Web
The full playbook (stacks, scanners, dashboards, landing pages) is in
`web.md`. The short version:
- Tokens in `:root` with a dark version; no loose colors in components.
  Contrast checked with the same script. Think of shades in HSL/OKLCH (hue,
  saturation, lightness), not hex.
- Sizes in `px`/`rem`, never `em` for the type scale (nested, you get
  17.5 px). Paragraphs at roughly `max-width: 65ch`; blocks with
  `max-width`, not percentage widths; fixed-width sidebars with flexible
  content.
- Safe font: the system stack (`system-ui, -apple-system, "Segoe UI",
  Roboto, …`). `font-variant-numeric: tabular-nums` on numbers and tables;
  table numbers right-aligned.
- `align-items: baseline` when mixing sizes on one line; `text-wrap:
  balance` on short headlines.
- User images with `object-fit: cover` in a fixed frame and
  `box-shadow: inset 0 0 0 1px rgb(0 0 0 / .1)` against bleed.

## Widgets / Live Activities / watch / car
- Color is a data light: verdict via shape + word (tinted and vibrant modes
  strip color). `widgetAccentable()` only on the number.
- One widget that follows the theme beats two (light/dark); when retiring
  widget kinds, keep the old ones for one version.
- Data age visible and honest (re-stamp on confirmation even if unchanged).
- Car (CarPlay/Android Auto): no emoji, stable row titles (the host limits
  new templates), badge with dark text on color.
- New fields in shared snapshots: always optional.
- When removing a "duplicate" element, keep its action (a row hidden for
  repeating the header was the only way to navigate).
