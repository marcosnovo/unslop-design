#!/usr/bin/env node
// Measure a rendered web page against the unslop checklist.
//
//   node scripts/web-audit.mjs <url-or-file> [--out dir] [--widths 390,768,1280]
//        [--scale 0,2,4,8,12,16,20,24,32,40,48,64,80,96] [--dark] [--wait ms]
//        [--device iphone,iphone-se,pixel]
//
// Needs Playwright in the project (`npm i -D playwright`); it uses the
// bundled Chromium and falls back to the installed Chrome. It writes, per
// width, a full-page screenshot, plus a grayscale one at the widest width
// (principle 2), and `report.md` + `report.json` with:
//   - horizontal overflow per width and the elements that cause it   (#57)
//   - token census: distinct font sizes, weights, colors, radii,
//     shadows, spacing values, and which spacing is off the scale   (#1-#5)
//   - text contrast computed from the real colors, failures listed  (principle 5)
//     (SVG text by its fill; text on a gradient against its worst stop, estimated)
//   - text drawn under 11 px at each width (SVG text at its drawn size) (#2)
//   - icon and small-graphic contrast (SVG ≤ 64 px), under 3:1       (WCAG 1.4.11)
//   - text scale: whether type grows with the reader's text size     (#2)
//   - reading: lines over ~85 characters, justified/centered long text (#27, #28)
//   - empty blocks: big painted boxes with no text or media           (#35)
//   - focus: focusable elements with no visible focus style         (#53)
//   - targets smaller than 24×24 px                                  (Also)
//   - emoji used in visible text                                     (#33)
//   - distinct left edges text starts on                              (#43)
//   - craft floor: color-scheme, ::selection, transition: all, "..."  (#61-#63)
//
// --device renders at real phone size (viewport, device pixel ratio, touch,
// mobile viewport, safe areas) instead of bare widths: `iphone` 393×852 @3x
// (Dynamic Island, 59/34 pt insets), `iphone-se` 375×667 @2x, `pixel`
// 412×915 @2.625x, or any Playwright device name ("iPhone 16 Pro"). Per
// device: a first-screen and a full-page shot, overflow, and which font
// family the text really rendered in (CDP platform fonts), so a fallback
// for -apple-system / SF Pro on Linux or CI is reported, not hidden. Without
// --device nothing changes. SF Pro is not installed on Linux and can't be
// redistributed: the report names the stand-in; judge metrics, not looks.
// It measures; it doesn't judge taste. Read the report next to the
// screenshots.
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const flags = {}, positional = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === "--dark") flags.dark = true;
  else if (a.startsWith("--")) flags[a.slice(2)] = args[++i];
  else positional.push(a);
}
const opt = (name, dflt) => flags[name] ?? dflt;
const target = positional[0];
if (!target) {
  console.error("usage: web-audit.mjs <url-or-file> [--out dir] [--widths 390,768,1280] [--scale …] [--dark] [--wait ms] [--device iphone,iphone-se,pixel]");
  process.exit(2);
}
const url = /^https?:|^file:/.test(target) ? target : pathToFileURL(resolve(target)).href;
const out = resolve(opt("out", "unslop-audit"));
const widths = opt("widths", "390,768,1280").split(",").map(Number);
const scale = opt("scale", "0,1,2,4,8,12,16,20,24,32,40,48,64,80,96").split(",").map(Number);
const dark = !!flags.dark;
const wait = Number(opt("wait", "500"));
const deviceArg = opt("device", "");
// name -> Playwright descriptor, full-screen viewport (the descriptor's own
// height subtracts browser chrome), safe-area insets in CSS px.
const PRESETS = {
  "iphone": { base: "iPhone 15 Pro", viewport: { width: 393, height: 852 }, insets: { top: 59, bottom: 34, left: 0, right: 0 } },
  "iphone-se": { base: "iPhone SE (3rd gen)", viewport: { width: 375, height: 667 }, insets: { top: 20, bottom: 0, left: 0, right: 0 } },
  "pixel": { base: "Pixel 7", viewport: { width: 412, height: 915 }, insets: { top: 24, bottom: 24, left: 0, right: 0 } },
};
const devices = deviceArg ? deviceArg.split(",").map((s) => s.trim()).filter(Boolean) : [];

// Playwright from next to this script, else from the project it runs in (npx runs this
// script from npm's cache, where the project's node_modules isn't on the import path).
async function loadPlaywright() {
  for (const name of ["playwright", "playwright-core"]) {
    const pick = (m) => (m.chromium ? m : m.default);
    try { return pick(await import(name)); } catch {}
    try {
      const { createRequire } = await import("node:module");
      const { pathToFileURL } = await import("node:url");
      const resolved = createRequire(pathToFileURL(process.cwd() + "/").href).resolve(name);
      return pick(await import(pathToFileURL(resolved).href));
    } catch {}
  }
  return null;
}
const pw = await loadPlaywright();
if (!pw) {
  console.error("Playwright not found. In the project: npm i -D playwright && npx playwright install chromium");
  process.exit(2);
}
let browser;
try { browser = await pw.chromium.launch(); } catch {
  try { browser = await pw.chromium.launch({ channel: "chrome" }); } catch (e) {
    console.error("Could not start Chromium or Chrome: " + e.message.split("\n")[0]);
    console.error("Run: npx playwright install chromium");
    process.exit(2);
  }
}
mkdirSync(out, { recursive: true });
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

// Runs inside the page. Returns plain data only.
// Both run inside the page, so each carries its own copy of drawnSize: the size text is
// drawn at. SVG text scales with its viewBox, so 11 user units can be 5 px on a phone.
const DRAWN = `const drawnSize = (el, cs) => {
  const size = parseFloat(cs.fontSize);
  const m = el.closest("svg") && el.getScreenCTM ? el.getScreenCTM() : null;
  return m ? size * Math.hypot(m.a, m.b) : size;
};`;

// Text drawn under 11 px at this width (a chart squeezed to a phone, a caption at 10px).
const tinyText = `(() => { ${DRAWN}
  const out = [];
  for (const el of document.body.querySelectorAll("*")) {
    if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if (!r.width || !r.height || cs.visibility === "hidden") continue;
    const s = drawnSize(el, cs);
    if (s < 11) out.push({ el: el.tagName.toLowerCase() + (typeof el.className === "string" && el.className.trim() ? "." + el.className.trim().split(/\\s+/)[0] : ""),
      size: Math.round(s * 10) / 10, text: el.textContent.trim().slice(0, 30) });
  }
  return out;
})()`;

function measure(scaleValues) {
  const drawnSize = (el, cs) => {
    const size = parseFloat(cs.fontSize);
    const m = el.closest("svg") && el.getScreenCTM ? el.getScreenCTM() : null;
    return m ? size * Math.hypot(m.a, m.b) : size;
  };
  const vis = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || Number(cs.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const label = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += "#" + el.id;
    const cls = typeof el.className === "string" ? el.className.trim().split(/\s+/).slice(0, 3).join(".") : "";
    if (cls) s += "." + cls;
    const t = (el.innerText || el.getAttribute("aria-label") || "").trim().replace(/\s+/g, " ").slice(0, 40);
    return t ? `${s} "${t}"` : s;
  };
  // Computed colors can be rgb() or, with Tailwind v4 and modern CSS,
  // oklch()/lab()/color(). Anything that isn't rgb is painted on a 1×1
  // canvas and read back as sRGB, so no color escapes the measurement.
  const probe = document.createElement("canvas").getContext("2d", { willReadFrequently: true });
  const parsed = new Map();
  const parse = (c) => {
    if (!c) return null;
    if (parsed.has(c)) return parsed.get(c);
    let out = null;
    const m = c.match(/^rgba?\(([^)]+)\)$/);
    if (m) {
      const p = m[1].split(/[ ,/]+/).filter(Boolean).map((v) => (v.endsWith("%") ? parseFloat(v) / 100 : Number(v)));
      out = { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
    } else if (probe && CSS.supports("color", c)) {
      probe.clearRect(0, 0, 1, 1);
      probe.fillStyle = "#000";
      probe.fillStyle = c;
      probe.fillRect(0, 0, 1, 1);
      const d = probe.getImageData(0, 0, 1, 1).data;
      out = { r: d[0], g: d[1], b: d[2], a: d[3] / 255 };
    }
    parsed.set(c, out);
    return out;
  };
  // Opacity on the element or any ancestor fades the text too.
  const opacityOf = (el) => {
    let o = 1;
    for (let n = el; n && n !== document.documentElement; n = n.parentElement) o *= Number(getComputedStyle(n).opacity);
    return o;
  };
  const blend = (top, under) => ({
    r: top.r * top.a + under.r * (1 - top.a),
    g: top.g * top.a + under.g * (1 - top.a),
    b: top.b * top.a + under.b * (1 - top.a),
    a: 1,
  });
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  // Background behind an element: blend translucent layers up the tree.
  // A gradient or image anywhere on the way makes it unknowable.
  const bgOf = (el) => {
    const layers = [];
    for (let n = el; n; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.backgroundImage && cs.backgroundImage !== "none") return null;
      if (cs.backgroundColor && cs.backgroundColor !== "transparent" && !parse(cs.backgroundColor)) return null;
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    let base = { r: 255, g: 255, b: 255, a: 1 };
    const rootBg = parse(getComputedStyle(document.documentElement).backgroundColor);
    if (rootBg && rootBg.a > 0) base = blend(rootBg, base);
    for (let i = layers.length - 1; i >= 0; i--) base = blend(layers[i], base);
    return base;
  };
  const count = (map, key, el) => {
    if (key === undefined || key === null || key === "") return;
    const e = map.get(key) || { n: 0, sample: label(el) };
    e.n++; map.set(key, e);
  };
  const toList = (map) => [...map.entries()].sort((a, b) => b[1].n - a[1].n).map(([value, v]) => ({ value, n: v.n, sample: v.sample }));

  const sizes = new Map(), weights = new Map(), families = new Map(), colors = new Map(), bgs = new Map(),
    radii = new Map(), shadows = new Map(), spacing = new Map(), offScale = new Map(), tracking = new Map();
  const contrastFails = [], contrastUnknown = [], emoji = [], smallTargets = [], gradientText = [], glow = [];
  // © ® ™ and typographic marks (✓ ✔ ✕ ✗ ★ ☆) are Extended_Pictographic but they're characters, not emoji.
  const emojiRe = /(?![©®™✓✔✕✖✗✘★☆])\p{Extended_Pictographic}/u;
  // Text in the second and later column of a multi-column grid or a flex row starts on that
  // column's own rail: not a stray left edge.
  const inColumn = (el) => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const p = n.parentElement;
      if (!p) break;
      const ps = getComputedStyle(p);
      const row = (ps.display.includes("grid") && ps.gridTemplateColumns.split(" ").filter(Boolean).length > 1)
        || (ps.display.includes("flex") && !ps.flexDirection.startsWith("column"));
      if (row && n.getBoundingClientRect().left > p.getBoundingClientRect().left + parseFloat(ps.paddingLeft) + 1) return true;
    }
    return false;
  };
  // A text over a gradient: estimate against each stop and keep the worst (marked as estimated).
  const gradientStops = (el) => {
    for (let n = el; n; n = n.parentElement) {
      const bi = getComputedStyle(n).backgroundImage;
      if (!bi || bi === "none") continue;
      if (/url\(/.test(bi) || !/gradient\(/.test(bi)) return null;
      const stops = (bi.match(/(?:rgba?|hsla?|oklch|oklab|lab|lch|color)\([^)]*\)|#[0-9a-f]{3,8}\b/gi) || []).map(parse).filter(Boolean);
      if (!stops.length) return null;
      if (stops.every((c) => c.a >= 1)) return stops;  // opaque stops: what's underneath doesn't show
      // Translucent stops sit on the element's own background color first, then on what's behind it.
      const behind = n.parentElement ? bgOf(n.parentElement) : { r: 255, g: 255, b: 255, a: 1 };
      const own = parse(getComputedStyle(n).backgroundColor);
      const under = own && own.a >= 1 ? own : own && own.a > 0 ? (behind ? blend(own, behind) : null) : behind;
      return under ? stops.map((c) => (c.a < 1 ? blend(c, under) : c)) : null;
    }
    return null;
  };
  const edges = new Map(), transitionAll = [], dots = [], defaultMargins = new Set();
  const all = [...document.body.querySelectorAll("*")].filter(vis);
  // Controls the author never padded keep the browser's own 1px 6px: not a spacing decision.
  const uaPadded = (el, cs) => el.matches("button, input, select, textarea")
    && cs.paddingTop === "1px" && cs.paddingBottom === "1px" && cs.paddingLeft === "6px" && cs.paddingRight === "6px";
  for (const el of all) {
    const cs = getComputedStyle(el);
    const ua = uaPadded(el, cs);
    for (const p of ["paddingTop", "paddingRight", "paddingBottom", "paddingLeft", "marginTop", "marginBottom", "rowGap", "columnGap"]) {
      if (ua && p.startsWith("padding")) continue;
      const v = cs[p];
      if (!v || v === "normal" || v === "auto") continue;
      const px = Math.round(parseFloat(v));
      if (!px || px < 0) continue;
      // A margin far past the scale is layout (margin: auto resolves to px), not a spacing step.
      if (p.startsWith("margin") && px > Math.max(...scaleValues) * 2) continue;
      count(spacing, px, el);
      if (!scaleValues.includes(px)) {
        count(offScale, px, el);
        // 1em block margins on p, ul, dl, h1… are the browser's default, not a value anyone typed.
        if (p.startsWith("margin") && el.matches("p, ul, ol, dl, dd, blockquote, figure, h1, h2, h3, h4, h5, h6, pre, hr")
            && Math.abs(parseFloat(v) - parseFloat(cs.fontSize) * (/^h1$/i.test(el.tagName) ? 0.67 : /^h2$/i.test(el.tagName) ? 0.83 : 1)) < 0.6)
          defaultMargins.add(px);
      }
    }
    const rad = cs.borderTopLeftRadius;
    if (rad && rad !== "0px") count(radii, rad, el);
    if (cs.boxShadow && cs.boxShadow !== "none") {
      count(shadows, cs.boxShadow, el);
      // A glow: a colored (non-gray) shadow at any offset. A shadow means height, so it's neutral (#32).
      for (const s of cs.boxShadow.split(/,(?![^(]*\))/)) {
        const col = parse((s.match(/(?:rgba?|hsla?|oklch|oklab|lab|lch|color)\([^)]*\)|#[0-9a-f]{3,8}\b/i) || [])[0]);
        const colored = col && col.a >= 0.2 && (Math.max(col.r, col.g, col.b) - Math.min(col.r, col.g, col.b)) > 40;
        if (colored) { glow.push(label(el)); break; }
      }
    }
    if (/(^|,\s*)all\b/.test(cs.transitionProperty) && cs.transitionDuration.split(",").some((d) => parseFloat(d) > 0)) transitionAll.push(label(el));
    const bgc = parse(cs.backgroundColor);
    if (bgc && bgc.a > 0) count(bgs, cs.backgroundColor, el);

    const ownText = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join("").trim();
    if (ownText) {
      count(sizes, cs.fontSize, el);
      count(weights, cs.fontWeight, el);
      count(families, cs.fontFamily.split(",")[0].replace(/["']/g, "").trim(), el);
      count(colors, cs.color, el);
      if (cs.letterSpacing !== "normal") count(tracking, cs.letterSpacing, el);
      // Left edges: block-level, left-aligned text only (inline runs, table cells, chart labels and
      // centered or right-aligned numbers start wherever their neighbors end).
      if (ownText.length > 1 && !cs.display.startsWith("inline") && cs.display !== "table-cell" && !el.closest("svg")
          && !inColumn(el) && /^(start|left|-webkit-left|justify)$/.test(cs.textAlign)) {
        // Where the glyphs start, not the border box: padding, borders and text-indent move the text.
        const node = [...el.childNodes].find((n) => n.nodeType === 3 && n.textContent.trim());
        const range = document.createRange();
        range.selectNodeContents(node);
        const first = [...range.getClientRects()].find((r) => r.width > 0);
        if (first) count(edges, Math.round(first.left / 4) * 4, el);
      }
      if (/\w\.\.\.(\s|$)/.test(ownText)) dots.push({ el: label(el), text: ownText.slice(0, 40) });
      if (emojiRe.test(ownText)) emoji.push({ el: label(el), text: ownText.slice(0, 40) });
      const clip = cs.webkitBackgroundClip || cs.backgroundClip;
      if (clip === "text" && cs.backgroundImage !== "none") { gradientText.push(label(el)); continue; }
      // Emoji are color bitmaps: CSS color doesn't paint them, so an emoji-only span isn't text to measure.
      // Typographic marks (✓ ✔ © ™ ★) are painted with CSS color, so they stay in; only real emoji go.
      if (!ownText.replace(/(?![©®™✓✔✕✖✗✘★☆])\p{Extended_Pictographic}|[\uFE0F\u200D\s]/gu, "")) continue;
      // SVG text paints with fill, not color.
      const paint = el.closest("svg") && parse(cs.fill) ? cs.fill : cs.color;
      const fg = parse(paint);
      const bg = bgOf(el);
      const fade = opacityOf(el);
      if (fg && bg) {
        const fga = { ...fg, a: fg.a * fade };
        const eff = fga.a < 1 ? blend(fga, bg) : fga;
        const r = ratio(eff, bg);
        const size = drawnSize(el, cs), bold = Number(cs.fontWeight) >= 700;
        const large = size >= 24 || (bold && size >= 18.66);
        const need = large ? 3 : 4.5;
        if (r < need) contrastFails.push({ el: label(el), ratio: Math.round(r * 100) / 100, need, color: paint, size: Math.round(size * 10) / 10 + "px" });
      } else if (fg) {
        const stops = gradientStops(el);
        if (stops) {
          const r = Math.min(...stops.map((s) => { const fga = { ...fg, a: fg.a * fade }; return ratio(fga.a < 1 ? blend(fga, s) : fga, s); }));
          const size = drawnSize(el, cs), bold = Number(cs.fontWeight) >= 700;
          const need = size >= 24 || (bold && size >= 18.66) ? 3 : 4.5;
          if (r < need) contrastFails.push({ el: label(el), ratio: Math.round(r * 100) / 100, need, color: paint, size: Math.round(size * 10) / 10 + "px", estimated: true });
        } else contrastUnknown.push(label(el));
      } else {
        contrastUnknown.push(label(el));
      }
    }
  }
  // Non-text contrast (WCAG 1.4.11): an icon or small graphic that carries meaning needs 3:1
  // against what's behind it. Icon-sized inline SVG only (≤ 64 px); the best-contrasting
  // fill or stroke of each one counts, so an outline around a pale fill passes.
  const graphicsFails = [];
  for (const svg of document.querySelectorAll("svg")) {
    if (!vis(svg)) continue;  // aria-hidden icons still mean something to people who see them
    const box = svg.getBoundingClientRect();
    if (box.width > 64 || box.height > 64 || box.width < 6 || box.height < 6) continue;
    const bg = bgOf(svg);
    if (!bg) continue;
    let best = 0, color = "";
    for (const s of svg.querySelectorAll("rect, circle, ellipse, path, polygon, polyline, line")) {
      const scs = getComputedStyle(s);
      const fade = opacityOf(s);  // the shape, any <g opacity> between it and the svg, and everything above
      // A fill only paints if the shape has an area: a stroke-only path keeps SVG's default
      // black fill, which would otherwise count as a 21:1 icon nobody can see.
      let area = s.tagName !== "line";
      try { const b = s.getBBox(); area = area && b.width > 0 && b.height > 0; } catch {}
      const paints = [[scs.stroke, scs.strokeOpacity]];
      if (area) paints.unshift([scs.fill, scs.fillOpacity]);
      for (const [paint, paintOpacity] of paints) {
        const c = paint && paint !== "none" && !paint.startsWith("url(") ? parse(paint) : null;
        if (!c || c.a === 0) continue;
        const ca = { ...c, a: c.a * fade * Number(paintOpacity ?? 1) };
        const r = ratio(ca.a < 1 ? blend(ca, bg) : ca, bg);
        if (r > best) { best = r; color = paint; }
      }
    }
    const where = svg.closest("button, a, [aria-label], section, li, nav, header, footer");
    if (best && best < 3) graphicsFails.push({ el: (where ? label(where) + " > " : "") + label(svg), ratio: Math.round(best * 100) / 100, color });
  }
  // Reading (#27, #28): running text longer than ~85 characters a line, or justified/centered.
  const longLines = [], alignedText = [];
  for (const el of document.body.querySelectorAll("p, li, blockquote, dd, figcaption")) {
    if (!vis(el)) continue;
    const text = (el.innerText || "").replace(/\s+/g, " ").trim();
    if (text.length < 160) continue;
    const cs = getComputedStyle(el);
    if (/^(justify|center)$/.test(cs.textAlign)) alignedText.push({ el: label(el), align: cs.textAlign });
    const range = document.createRange();
    range.selectNodeContents(el);
    const lines = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top))).size;
    if (lines >= 2 && text.length / lines > 85) longLines.push({ el: label(el), cpl: Math.round(text.length / lines) });
  }
  // Empty blocks (#35): a big painted box with nothing in it, a placeholder where an image or the product should be.
  const media = "img, svg, video, canvas, picture, iframe, object, embed, input, textarea, select";
  let emptyBlocks = [...document.body.querySelectorAll("*")].filter((el) => {
    if (!vis(el) || el.matches(media) || el.querySelector(media) || (el.innerText || "").trim()) return false;
    const r = el.getBoundingClientRect();
    if (r.width < 200 || r.height < 120) return false;
    const cs = getComputedStyle(el), bg = parse(cs.backgroundColor), under = el.parentElement && bgOf(el.parentElement);
    // A url() background is a real image (a CSS photo), not a placeholder; only fills count.
    if (/url\(/.test(cs.backgroundImage)) return false;
    const painted = cs.backgroundImage !== "none" || parseFloat(cs.borderTopWidth) > 0 || parseFloat(cs.borderLeftWidth) > 0
      || (bg && bg.a > 0 && under && Math.abs(bg.r - under.r) + Math.abs(bg.g - under.g) + Math.abs(bg.b - under.b) > 12);
    return painted;
  });
  emptyBlocks = emptyBlocks.filter((el) => !emptyBlocks.some((o) => o !== el && o.contains(el)))
    .map((el) => { const r = el.getBoundingClientRect(); return { el: label(el), w: Math.round(r.width), h: Math.round(r.height) }; });
  const focusables = [...document.querySelectorAll('a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"]), [role="button"]')].filter(vis);
  for (const el of focusables) {
    const r = el.getBoundingClientRect();
    if (r.width < 24 || r.height < 24) smallTargets.push({ el: label(el), w: Math.round(r.width), h: Math.round(r.height) });
  }
  return {
    title: document.title,
    census: {
      fontSizes: toList(sizes), fontWeights: toList(weights), fontFamilies: toList(families),
      textColors: toList(colors), backgrounds: toList(bgs), radii: toList(radii), shadows: toList(shadows),
      letterSpacing: toList(tracking), spacing: toList(spacing), offScaleSpacing: toList(offScale),
    },
    contrastFails, contrastUnknown: contrastUnknown.length, graphicsFails, emoji, smallTargets, gradientText, glow,
    longLines, alignedText, emptyBlocks, defaultMargins: [...defaultMargins],
    focusableCount: focusables.length,
    leftEdges: toList(edges).sort((a, b) => a.value - b.value),
    craft: {
      colorScheme: getComputedStyle(document.documentElement).colorScheme,
      selectionThemed: getComputedStyle(document.body, "::selection").backgroundColor !== "rgba(0, 0, 0, 0)",
      transitionAll, dots,
    },
  };
}

function overflow() {
  const vw = document.documentElement.clientWidth;
  const sw = document.documentElement.scrollWidth;
  const culprits = [];
  if (sw > vw) {
    for (const el of document.body.querySelectorAll("*")) {
      const r = el.getBoundingClientRect();
      if (r.right > vw + 1 && r.width > 0) {
        const parentOver = el.parentElement && el.parentElement.getBoundingClientRect().right > vw + 1;
        if (!parentOver) culprits.push(`${el.tagName.toLowerCase()}${el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\s+/).slice(0, 2).join(".") : ""} (right ${Math.round(r.right)} px)`);
      }
      if (culprits.length >= 8) break;
    }
  }
  return { viewport: vw, scrollWidth: sw, culprits };
}

// Focus: tab to each element and compare its look with and without focus.
async function focusCheck(page, limit = 40) {
  return page.evaluate(async (limit) => {
    const sel = 'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"]), [role="button"]';
    const els = [...document.querySelectorAll(sel)].filter((e) => e.getBoundingClientRect().width > 0).slice(0, limit);
    const look = (e) => { const c = getComputedStyle(e); return [c.outlineStyle, c.outlineWidth, c.outlineColor, c.boxShadow, c.borderColor, c.backgroundColor, c.textDecorationLine].join("|"); };
    const missing = [];
    for (const e of els) {
      e.blur();
      const before = look(e);
      e.focus({ focusVisible: true });
      const after = look(e);
      if (document.activeElement === e && before === after) {
        const t = (e.innerText || e.getAttribute("aria-label") || e.getAttribute("placeholder") || e.tagName).trim().replace(/\s+/g, " ").slice(0, 40);
        missing.push(`${e.tagName.toLowerCase()} "${t}"`);
      }
      e.blur();
    }
    return { checked: els.length, missing };
  }, limit);
}

// Which font actually painted the text. CSS says what was asked; Chromium
// (CDP CSS.getPlatformFontsForNode) says what was used. A stack that starts
// with -apple-system / SF Pro resolves to a fallback on Linux and CI.
async function fontCheck(page) {
  const probes = await page.evaluate(() => {
    document.querySelectorAll("[data-unslop-font]").forEach((e) => e.removeAttribute("data-unslop-font"));
    const seen = new Set(), picked = [];
    const cands = [...document.querySelectorAll("h1, h2, p, button, a, li, td, span, div")].filter((el) => {
      const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 2);
    });
    // The first heading and the most common body family/size pair.
    const h = document.querySelector("h1, h2");
    const order = h && cands.includes(h) ? [h, ...cands] : cands;
    for (const el of order) {
      const cs = getComputedStyle(el), key = cs.fontFamily + "|" + (el === h ? "h" : "b");
      if (seen.has(key) || picked.length >= 4) continue;
      seen.add(key);
      el.setAttribute("data-unslop-font", String(picked.length));
      picked.push({ role: el === h ? "heading" : el.tagName.toLowerCase(), stack: cs.fontFamily, size: cs.fontSize, weight: cs.fontWeight,
        sample: (el.innerText || "").trim().replace(/\s+/g, " ").slice(0, 30) });
    }
    return picked;
  });
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("DOM.enable"); await cdp.send("CSS.enable");
  const { root } = await cdp.send("DOM.getDocument", { depth: 0 });
  const rows = [];
  for (let i = 0; i < probes.length; i++) {
    const { nodeId } = await cdp.send("DOM.querySelector", { nodeId: root.nodeId, selector: `[data-unslop-font="${i}"]` });
    const { fonts } = await cdp.send("CSS.getPlatformFontsForNode", { nodeId });
    const used = fonts.map((f) => f.familyName);
    const first = probes[i].stack.split(",")[0].replace(/["']/g, "").trim();
    const system = /^(-apple-system|blinkmacsystemfont|system-ui|sf pro.*|\.sf.*|ui-sans-serif)$/i.test(first);
    // A named stack head that isn't among the used fonts fell back; system-ui /
    // -apple-system resolve to whatever the OS has, which on Linux is never SF.
    const sf = used.some((u) => /^(sf pro|\.sf|sf ui|san francisco)/i.test(u));
    const fellBack = system ? !sf : !used.some((u) => u.toLowerCase() === first.toLowerCase());
    rows.push({ ...probes[i], used, fellBack, asksForSF: /-apple-system|sf pro|system-ui|blinkmacsystemfont/i.test(probes[i].stack) });
  }
  await cdp.detach();
  return rows;
}

const results = { url, widths: {}, generated: new Date().toISOString() };
const context = await browser.newContext({ colorScheme: dark ? "dark" : "light", deviceScaleFactor: 1 });
const page = await context.newPage();
for (const w of widths) {
  await page.setViewportSize({ width: w, height: 900 });
  await page.goto(url, { waitUntil: "networkidle" }).catch(() => page.goto(url));
  await page.waitForTimeout(wait);
  const shot = join(out, `w${w}${dark ? "-dark" : ""}.png`);
  await page.screenshot({ path: shot, fullPage: true });
  results.widths[w] = { screenshot: shot, overflow: await page.evaluate(overflow),
    tinyText: await page.evaluate(tinyText) };
}
// Real device renders (opt-in).
results.devices = {};
for (const name of devices) {
  const preset = PRESETS[name.toLowerCase()];
  const desc = pw.devices[preset ? preset.base : name];
  if (!desc) { console.error(`Unknown device "${name}". Presets: ${Object.keys(PRESETS).join(", ")}; or a Playwright name like "iPhone 16 Pro".`); process.exit(2); }
  const { defaultBrowserType, ...d } = desc;
  if (preset) d.viewport = preset.viewport;
  const ctx = await browser.newContext({ ...d, colorScheme: dark ? "dark" : "light" });
  const dp = await ctx.newPage();
  let safeArea = false;
  if (preset) {
    try {
      const s = await ctx.newCDPSession(dp);
      await s.send("Emulation.setSafeAreaInsetsOverride", { insets: preset.insets });
      safeArea = true;
    } catch { /* older Chromium: env(safe-area-inset-*) stays 0 */ }
  }
  await dp.goto(url, { waitUntil: "networkidle" }).catch(() => dp.goto(url));
  await dp.waitForTimeout(wait);
  const id = slug(name), tag = dark ? "-dark" : "";
  const fold = join(out, `device-${id}${tag}.png`), full = join(out, `device-${id}${tag}-full.png`);
  await dp.screenshot({ path: fold });
  await dp.screenshot({ path: full, fullPage: true });
  results.devices[name] = {
    viewport: d.viewport, dpr: d.deviceScaleFactor, insets: preset ? preset.insets : null, safeAreaApplied: safeArea,
    screenshot: fold, fullPage: full, overflow: await dp.evaluate(overflow), fonts: await fontCheck(dp).catch(() => []),
    textScaleNote: "Dynamic Type / Android font scale are not emulated: re-run with html{font-size} raised or check on device",
  };
  await ctx.close();
}
const widest = Math.max(...widths);
await page.setViewportSize({ width: widest, height: 900 });
await page.goto(url, { waitUntil: "networkidle" }).catch(() => page.goto(url));
await page.waitForTimeout(wait);
results.measure = await page.evaluate(measure, scale);
results.focus = await focusCheck(page);
// Does the type follow the reader's text size? Double the root size and see whether text grows.
// Type set in px ignores it (Dynamic Type, browser zoom of text only, Android font scale).
results.textScale = await page.evaluate(() => {
  const els = [...document.body.querySelectorAll("*")].filter((el) => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && !el.closest("svg") && [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 1);
  }).slice(0, 80);
  const before = els.map((el) => parseFloat(getComputedStyle(el).fontSize));
  // Twice the root's current size, whatever the page set it to (a page already at 200% must still grow).
  const root = document.documentElement, old = root.style.fontSize;
  root.style.fontSize = parseFloat(getComputedStyle(root).fontSize) * 2 + "px";
  const after = els.map((el) => parseFloat(getComputedStyle(el).fontSize));
  root.style.fontSize = old;
  const grew = els.filter((_, i) => after[i] > before[i] * 1.1).length;
  const fixed = els.map((el, i) => (after[i] > before[i] * 1.1 ? null : el)).filter(Boolean).slice(0, 6)
    .map((el) => (el.tagName.toLowerCase() + (el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\s+/)[0] : "")));
  return { checked: els.length, grew, fixed };
});
await page.addStyleTag({ content: "html{filter:grayscale(1)!important}" });
const gray = join(out, `w${widest}${dark ? "-dark" : ""}-grayscale.png`);
await page.screenshot({ path: gray, fullPage: true });
results.grayscale = gray;
await browser.close();

// ---------- report ----------
const m = results.measure, c = m.census;
const top = (list, n = 12) => list.slice(0, n).map((x) => `\`${x.value}\` ×${x.n}`).join(" · ") || "—";
const L = [];
L.push(`# Unslop web audit`, ``, `${url}${m.title ? ` — ${m.title}` : ""}`, ``, `Measured at ${widths.join(", ")} px${dark ? " (dark)" : ""}. Checklist numbers in brackets.`, ``);
L.push(`## Layout at each width [#57]`);
for (const w of widths) {
  const o = results.widths[w].overflow;
  L.push(o.scrollWidth > o.viewport
    ? `- **${w} px: horizontal scroll** (page ${o.scrollWidth} px wide). Starts at: ${o.culprits.join("; ") || "?"}`
    : `- ${w} px: no horizontal scroll`);
}
L.push(``, `## System census [#1-#5]`, ``,
  `Every distinct value the page actually renders. A system shows up as few values used many times; slop shows up as many values used once.`, ``,
  `| | distinct | values (most used first) |`, `|---|---|---|`,
  `| Font sizes | ${c.fontSizes.length} | ${top(c.fontSizes)} |`,
  `| Weights | ${c.fontWeights.length} | ${top(c.fontWeights)} |`,
  `| Families | ${c.fontFamilies.length} | ${top(c.fontFamilies)} |`,
  `| Text colors | ${c.textColors.length} | ${top(c.textColors, 8)} |`,
  `| Backgrounds | ${c.backgrounds.length} | ${top(c.backgrounds, 8)} |`,
  `| Radii | ${c.radii.length} | ${top(c.radii)} |`,
  `| Shadows | ${c.shadows.length} | ${c.shadows.length ? c.shadows.slice(0, 4).map((x) => `\`${x.value.slice(0, 60)}\` ×${x.n}`).join(" · ") : "—"} |`,
  `| Letter-spacing | ${c.letterSpacing.length} | ${top(c.letterSpacing)} |`,
  `| Spacing (px) | ${c.spacing.length} | ${top(c.spacing, 16)} |`, ``);
const warn = [];
if (c.fontSizes.length > 8) warn.push(`${c.fontSizes.length} font sizes: a hand-picked scale has 6-8 [#2]`);
if (c.fontWeights.length > 3) warn.push(`${c.fontWeights.length} weights: two (plus one for numbers) are enough [#2]`);
if (c.radii.length > 5) warn.push(`${c.radii.length} radii: pick 3-4 and make inner = outer − padding [#9]`);
if (c.shadows.length > 5) warn.push(`${c.shadows.length} shadows: 3-5 named elevations max [#5]`);
if (c.textColors.length > 8) warn.push(`${c.textColors.length} text colors: 2-3 tones plus roles [#3, #19]`);
if (warn.length) L.push(...warn.map((x) => `- ⚠ ${x}`), ``);
L.push(`**Off-scale spacing** (scale: ${scale.join(", ")}):`, ``);
L.push(c.offScaleSpacing.length
  ? c.offScaleSpacing.slice(0, 15).map((x) => `- \`${x.value}px\` ×${x.n} — e.g. ${x.sample}`
      + ((m.defaultMargins || []).includes(x.value) ? " (likely the browser's default 1em margin: set the margin from the scale)" : "")).join("\n")
  : `- none`);
L.push(``, `## Contrast [principle 5]`, ``);
L.push(m.contrastFails.length
  ? (() => {  // one line per distinct failure, so eleven axis labels in one color read as one fix
      const g = new Map();
      for (const x of m.contrastFails) { const k = [x.ratio, x.el, x.color, x.size, !!x.estimated].join("|"); g.set(k, { ...x, n: (g.get(k)?.n || 0) + 1 }); }
      return [...g.values()].slice(0, 30).map((x) => `- **${x.ratio}:1** (needs ${x.need}) ${x.el}${x.n > 1 ? ` ×${x.n}` : ""} — ${x.color}, ${x.size}${x.estimated ? " (on a gradient: its worst stop, estimated)" : ""}`).join("\n");
    })()
  : `- No text below AA among the ones measurable (SVG text included, by its fill).`);
if (m.contrastUnknown) L.push(`- ${m.contrastUnknown} text element(s) sit on an image: check those by eye [#36]. Text on gradients is estimated against the worst stop.`);
L.push(``, `## Icons and graphics under 3:1 [principle 5, WCAG 1.4.11]`, ``,
  m.graphicsFails.length
    ? m.graphicsFails.slice(0, 20).map((x) => `- **${x.ratio}:1** (needs 3) ${x.el} — ${x.color}`).join("\n")
    : `- none among icon-sized SVG (≤ 64 px). Larger graphics, images and icon fonts: check by eye.`);
L.push(``, `## Focus [#53]`, ``,
  results.focus.missing.length
    ? `${results.focus.missing.length} of ${results.focus.checked} focusable elements look the same focused and unfocused:\n\n` + results.focus.missing.slice(0, 20).map((x) => `- ${x}`).join("\n")
    : `All ${results.focus.checked} focusable elements checked change when focused.`);
L.push(``, `## Targets under 24×24 px`, ``,
  m.smallTargets.length ? m.smallTargets.slice(0, 20).map((x) => `- ${x.el} (${x.w}×${x.h})`).join("\n") : `- none`);
L.push(``, `## Reading [#27, #28]`, ``,
  ...(m.longLines.length ? m.longLines.slice(0, 10).map((x) => `- **${x.cpl} characters a line** (aim for 45-75): ${x.el}`) : [`- line length within ~85 characters`]),
  ...(m.alignedText.length ? m.alignedText.slice(0, 10).map((x) => `- long text ${x.align === "justify" ? "justified" : "centered"}: ${x.el}`) : []));
{
  const tiny = Object.entries(results.widths).filter(([, r]) => r.tinyText && r.tinyText.length);
  L.push(``, `## Text drawn under 11 px [#2]`, ``,
    tiny.length ? tiny.map(([w, r]) => `- at ${w} px, ${r.tinyText.length}: ` + r.tinyText.slice(0, 6).map((x) => `${x.el} ${x.size}px "${x.text}"`).join("; ")).join("\n")
      + `\n\nSVG text counts at the size it's drawn: a chart whose viewBox shrinks to the phone shrinks its labels too.`
      : `- none at any width (SVG text measured at its drawn size)`);
}
L.push(``, `## Empty blocks [#35]`, ``,
  m.emptyBlocks.length ? m.emptyBlocks.slice(0, 10).map((x) => `- ${x.w}×${x.h} painted box with no text or media: ${x.el}`).join("\n") : `- none`);
L.push(``, `## Emoji in visible text [#33, #45]`, ``,
  m.emoji.length ? m.emoji.slice(0, 20).map((x) => `- ${x.el}`).join("\n") : `- none`);
L.push(``, `## Gradient text and glows [#30, #32, #55]`, ``,
  [...m.gradientText.map((x) => `- gradient text: ${x}`), ...m.glow.slice(0, 15).map((x) => `- colored glow: ${x}`)].join("\n") || `- none`);
const edgesList = m.leftEdges || [];
L.push(``, `## Left edges [#43]`, ``,
  `Left-aligned text blocks start on ${edgesList.length} distinct x positions at ${widest} px; ${edgesList.filter((x) => x.n === 1).length} are used by a single block. A composed page reuses a few rails; many one-off edges mean it was placed piece by piece. Draw them over the screenshot.`, ``,
  edgesList.length ? edgesList.map((x) => `\`${x.value}px\` ×${x.n}`).join(" · ") : `—`);
const cf = m.craft || {};
{
  const ts = results.textScale;
  L.push(``, `## Text scale [#2]`, ``,
    !ts || !ts.checked ? `- no text measured`
      : ts.grew / ts.checked >= 0.5
        ? `- ${ts.grew} of ${ts.checked} text elements grow with the reader's text size (root doubled).`
        : `- **${ts.checked - ts.grew} of ${ts.checked} text elements stay the same size** with the root doubled: type in px ignores the reader's text size. Set the type scale in rem. e.g. ${ts.fixed.join(", ")}`);
}
L.push(``, `## Craft floor [#61-#63]`, ``,
  `- color-scheme: ${cf.colorScheme && cf.colorScheme !== "normal" ? `\`${cf.colorScheme}\`` : "**not set** (native controls and scrollbars won't follow dark mode)"}`,
  `- ::selection: ${cf.selectionThemed ? "themed" : "browser default"}`,
  `- \`transition: all\`: ${cf.transitionAll && cf.transitionAll.length ? `**${cf.transitionAll.length}** — ${cf.transitionAll.slice(0, 6).join(", ")}` : "none"}`,
  `- three dots instead of …: ${cf.dots && cf.dots.length ? cf.dots.slice(0, 6).map((x) => `${x.el} ("${x.text}")`).join("; ") : "none"}`);
if (devices.length) {
  L.push(``, `## Device renders`, ``);
  for (const [name, r] of Object.entries(results.devices)) {
    const o = r.overflow;
    L.push(`### ${name}: ${r.viewport.width}×${r.viewport.height} @${r.dpr}x${r.insets ? `, safe area top ${r.insets.top} / bottom ${r.insets.bottom}${r.safeAreaApplied ? "" : " (not applied: Chromium too old)"}` : ""}`, ``,
      o.scrollWidth > o.viewport ? `- **horizontal scroll** (page ${o.scrollWidth} px wide). Starts at: ${o.culprits.join("; ") || "?"}` : `- no horizontal scroll`);
    for (const f of r.fonts) {
      const used = f.used.join(", ") || "?";
      L.push(`- ${f.role} \`${f.size}/${f.weight}\`: asked \`${f.stack.slice(0, 60)}\`, rendered **${used}**${f.fellBack ? ` — ${f.asksForSF ? "SF/system font not available here: fallback, judge metrics not looks" : "stack head not used: fallback"}` : ""}`);
    }
    L.push(`- ${r.screenshot} (first screen) · ${r.fullPage}`, ``);
  }
  L.push(`- Dynamic Type / font scale: not emulated. Check the largest size by hand.`);
}
L.push(``, `## Screenshots`, ``, ...widths.map((w) => `- ${results.widths[w].screenshot}`), `- ${gray} (grayscale: does the hierarchy hold without color? [principle 2])`, ``);
writeFileSync(join(out, "report.md"), L.join("\n"));
writeFileSync(join(out, "report.json"), JSON.stringify(results, null, 2));
console.log(L.join("\n"));
console.log(`\nWritten to ${out}`);
