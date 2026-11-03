# Web playbook

For websites, web apps and dashboards. Same method as the rest of the
skill; this file adds what's specific to the browser: how to find the
system in the code, how to measure the rendered page, and the web-only
fixes (#49-#57 in `checklist.md`). Try it on `examples/`: the same
dashboard before and after.

## 1. Find the system in the code

Before judging screens, find where the values live:

| Stack | Tokens live in | Slop usually hides in |
|---|---|---|
| Tailwind v4 | `@theme { --color-…; --spacing: … }` in the main CSS | arbitrary values `p-[13px]`, `bg-gradient-to-r from-purple-500`, `shadow-purple-500/50` |
| Tailwind v3 | `tailwind.config.{js,ts}` → `theme.extend` | the same, plus `!important` overrides |
| shadcn/ui | CSS variables in `globals.css` (`--background`, `--primary`…) | components copied and edited by hand, `rounded-xl` everywhere |
| CSS / SCSS modules | `:root` custom properties, `_variables.scss` | literals in each module |
| CSS-in-JS | `theme.ts` passed to the provider | inline `style={{ padding: 13 }}` |

If there are no tokens, the first PR creates them (spacing, type, color
roles, radii, elevation) and nothing else. Then:

```bash
python3 scripts/slop-scan.py src/            # where the patterns are, with the checklist #
```

It prints each hit with its file and line and the fix number: gradient
text, gradients, colored glows, backdrop blur, the default purple palette,
Tailwind arbitrary values, raw colors outside token files, off-scale px,
emoji, "!!", greetings as titles, removed focus outlines. It's a grep with
opinions: a gradient can be the one signature gesture. Pass `--scale` with
your own spacing steps.

## 2. Measure the rendered page

Code shows intent; the browser shows what happened. With the dev server
running (or a static file):

```bash
npm i -D playwright            # once, if the project doesn't have it
node scripts/web-audit.mjs http://localhost:3000/dashboard --out unslop-audit
node scripts/web-audit.mjs http://localhost:3000/dashboard --dark --widths 1280
```

It writes screenshots at 390, 768 and 1280 px, a grayscale one (principle
2), and `report.md` with:

- **Horizontal scroll** at each width and the element that causes it (#57).
- **System census**: every distinct font size, weight, family, text color,
  background, radius, shadow and spacing value the page renders, most used
  first, and the spacing values that fall off your scale. A system looks
  like a few values used many times; slop looks like many values used once.
- **Contrast** of every text from its computed colors, translucent layers
  blended (principle 5). Text over gradients or images is listed for an eye
  check.
- **Focus**: focusable elements that look the same focused and not (#53).
- **Targets** under 24×24 px, **emoji** in visible text, **gradient text**
  and **colored glows**.

Run it before and after a round and put both reports in the PR. Its numbers
are facts; the reviewer still decides what's slop.

## 3. Web-specific rules

- **Tokens as CSS custom properties**, redefined for dark mode in
  `@media (prefers-color-scheme: dark)` (and `[data-theme="dark"]` if there's
  a switch). Components use `var(--…)` only. In dark mode, elevation comes
  from a lighter surface, not a shadow.
- **Sizes in px/rem**, never `em` for type (it compounds). Paragraphs at
  `max-width: 65ch`; content blocks with a `max-width`, not percentages.
- **Layout with grid**: `grid-template-columns: 264px minmax(0, 1fr)` for a
  sidebar app (`minmax(0, …)` stops long content from widening the page);
  cards with `repeat(auto-fit, minmax(240px, 1fr))`. Container queries for
  components that live in different widths.
- **Numbers**: `font-variant-numeric: tabular-nums`, right-aligned in
  tables; number and unit with `align-items: baseline`.
- **States**: `:hover`, `:focus-visible`, `:active`, `[aria-current]`,
  `:disabled`, `[aria-busy]`. Never remove `outline` without a replacement.
- **Motion**: transitions ≤ 200 ms on color/opacity/transform; everything
  inside `@media (prefers-reduced-motion: no-preference)`.
- **Icons**: one SVG set (Lucide, Heroicons, Phosphor…) at one stroke
  width, sized by the icon slot (#49). No emoji in UI.
- **Fonts**: the system stack is the safe default; a web font only if it
  is the chosen personality (#6), with `font-display: swap` and at most two
  weights loaded.
- **Performance is design too**: `backdrop-filter` over large areas and
  stacked big shadows make scrolling stutter on cheap laptops; a page that
  jumps while fonts load (CLS) looks broken however pretty it is.

## 4. Dashboards

The most common AI-generated web screen. Check in this order:

1. **Title**: what and when ("October 2026"), not "Welcome back" (#26).
2. **KPI cards**: label in sentence case, number large, delta with its
   baseline in the data voice (#52, #56). Two to four cards; if all are
   "important", none is (#11).
3. **Charts**: series in the category colors shared with the nav and the
   legend (#51), a few axis ticks, no glow, previous period in gray when
   comparing (#39).
4. **Sidebar**: one icon slot (#49), counts as text (#50), one quiet
   selected state (#53), groups separated by space and a small label (#8,
   #45), a collapse toggle (#57).
5. **Tables**: left-aligned text, right-aligned tabular numbers, row height
   from the spacing scale, hover row, sticky header, horizontal scroll
   inside the table, an empty state that says what to do.
6. **Empty, loading and error** for every card: skeletons with the card's
   real shape, never a spinner in the middle of the page.

## 5. Landing pages

- One message and one primary action above the fold; the product
  screenshot is real and legible (#38, #48).
- Sections share one gap (#44); no "✨ Powered by AI" eyebrow above every
  heading.
- Logos of customers in one tone, one height, fixed frames (#37).
- Pricing: one recommended plan, prices from the source of truth, the
  currency of the visitor's market or none.
- Check at 390 px first: most visits are on a phone.

## 6. Verification for a web PR

- `slop-scan.py` on the changed paths: no new hits, or each one justified.
- `web-audit.mjs` before and after, light and dark: no horizontal scroll,
  fewer distinct values, zero contrast failures, every focusable element
  shows focus.
- Keyboard pass: Tab through the page; the order follows the reading
  order; Esc closes what opened.
- Screenshots in the PR at 390 and 1280 px, and the grayscale one.
