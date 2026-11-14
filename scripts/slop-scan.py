#!/usr/bin/env python3
"""Find the usual slop patterns in UI source code, with the checklist number.

    python3 scripts/slop-scan.py [paths…] [--scale 0,2,4,8,12,16,20,24,32,40,48,64]
                                 [--max 8] [--strict]

Reads web (CSS, SCSS, HTML, JSX/TSX, Vue, Svelte, Astro), SwiftUI and
Compose files. Standard library only. It is a grep with opinions: each hit
is a place to look, not a verdict — a gradient can be the one signature
gesture (#34, principle 7). Silence a line with a comment containing
`unslop-ignore`. With --strict it exits 1 when anything is found (for a
pre-commit hook; don't put it in paid CI without asking).
"""
import argparse
import os
import re
import sys

WEB = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro", ".mdx"}
NATIVE = {".swift", ".kt"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", ".svelte-kit", "out", "coverage",
             "vendor", "Pods", "DerivedData", ".build", ".gradle", "public", "static"}
# Files where literals belong: the token/theme definitions themselves.
TOKEN_FILE = re.compile(r"(token|theme|variables|palette|colors?|tailwind\.config|design[-_]?system)", re.I)

# Typographic marks in the same blocks (✓ ✔ ✕ ✗ ★ ☆) are characters, not emoji.
EMOJI = re.compile("(?![✓✔✕✖✗✘★☆✦✧])[\U0001F300-\U0001FAFF☀-➿⭐⬆↔-↪⌚-⏿]")
PX_PROP = re.compile(r"\b(padding|margin|gap|row-gap|column-gap|font-size|border-radius|inset|top|left|right|bottom)"
                     r"(-[a-z]+)?\s*:\s*([^;}{]+)", re.I)
PX = re.compile(r"(-?\d+(?:\.\d+)?)px")

# Title Case: two to six capitalized words with at least one common word, so
# brand, product and place names ("Spotify Family", "New York Times") pass and "Your Subscriptions",
# "Recent Activity", "Start Run" don't. Only whole UI strings: a text node,
# or the string in Text/Button/Label/navigationTitle/Section/Tab.
_COMMON = ("Your|My|All|Of|For|To|And|With|In|On|At|By|From|Add|Edit|View|Get|Start|Stop|Save|"
           "Create|Delete|Remove|Manage|Recent|Next|Total|Today|This|Upcoming|Soon|Now|More|See|Show|Go|"
           "Back|Sign|Log|Up|Out|Learn|Try|Unlock|Upgrade|Activity|Settings|Account|Details|Overview")
_TC_WORDS = r"(?=[^\"<\n]*\b(?:" + _COMMON + r")\b)[A-Z][\w'’+-]*(?:\s+[A-Z][\w'’+-]*){1,5}"
_LEAD = r"(?:[\U0001F300-\U0001FAFF☀-➿]\uFE0F?\s*)?"  # an emoji in front doesn't hide it
TITLE_CASE = re.compile(r">\s*" + _LEAD + _TC_WORDS + r"[!?.]?\s*<|"
                        r"\b(?:Text|Button|Label|navigationTitle|Section|Tab)\(\s*(?:text\s*=\s*)?\"" + _LEAD + _TC_WORDS + r"[!?.]?\"")

# (id, checklist ref, description, regex, applies to: "web" | "native" | "all")
RULES = [
    ("gradient-text", "#55", "Gradient text",
     re.compile(r"bg-clip-text|(-webkit-)?background-clip\s*:\s*text", re.I), "web"),
    ("gradient", "#30 #34", "Gradient fill (fine once, as the signature; not as decoration)",
     re.compile(r"bg-gradient-to-|from-\w+-\d{3}\s+(via|to)-|(linear|radial|conic)-gradient\(|LinearGradient\(|RadialGradient\(|Brush\.(linear|radial|vertical|horizontal)Gradient"), "all"),
    ("glow", "#32", "Colored glow / neon shadow (a shadow means height)",
     re.compile(r"shadow-(purple|violet|indigo|fuchsia|pink|blue|cyan|emerald|green)-\d{3}|drop-shadow-\[|"
                r"box-shadow\s*:\s*0(px)?\s+0(px)?\s+\d+px\s+(#|rgba?\((?!0,\s*0,\s*0))|"
                r"\.shadow\(color:\s*\.(purple|blue|pink|accentColor|indigo)", re.I), "all"),
    ("blur-content", "#46", "Backdrop blur (chrome only, never behind content)",
     re.compile(r"backdrop-blur|backdrop-filter\s*:|\.ultraThinMaterial|\.thinMaterial"), "all"),
    ("ai-palette", "#19", "Default AI palette (purple/violet/indigo/fuchsia) — is it a decision?",
     re.compile(r"\b(?:bg|text|from|via|to|border|ring|shadow)-(purple|violet|indigo|fuchsia)-[3-7]00\b"), "web"),
    ("arbitrary-value", "#1", "Tailwind arbitrary value instead of a scale step",
     re.compile(r"\b-?(?:p|px|py|pt|pr|pb|pl|m|mx|my|mt|mr|mb|ml|gap|gap-x|gap-y|space-x|space-y|w|h|"
                r"min-w|max-w|text|rounded|top|left|right|bottom|inset|leading|tracking)-\[\d"), "web"),
    ("raw-color", "#3", "Raw color in a component (should be a role token)",
     re.compile(r"(?<![\w&-])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b(?![\w-])|\brgba?\(\s*\d|Color\(red:|Color\(0x[0-9A-Fa-f]{8}\)"), "all"),
    ("native-literal", "#1", "Spacing / size literal in a view (should be a token)",
     re.compile(r"\.padding\(\s*\d+(\.\d+)?\s*\)|\.padding\(\.\w+,\s*\d+|\.font\(\.system\(size:\s*\d+|"
                r"\b(?:padding|spacedBy|size|height|width)\(\s*\d+(\.\d+)?\.dp|\d+(\.\d+)?\.sp\b|cornerRadius\(\s*\d+|RoundedCornerShape\(\s*\d+\.dp"), "native"),
    ("emoji", "#33 #45", "Emoji in UI text (use the icon set, or nothing)",
     EMOJI, "all"),
    ("shouting", "#52", "Exclamation marks in UI copy",
     re.compile(r"[\"'>`][^\"'<`\n]{2,}!!"), "all"),
    ("exclaim", "#25", "Exclamation mark in UI text (say it plainly)",
     re.compile(r">[^<>{}\n]*[A-Za-z][!¡](?=[\s\U0001F300-\U0001FAFF☀-➿]*<)|"
                r"\b(?:Text|Button|Label|navigationTitle)\(\s*(?:text\s*=\s*)?\"[^\"\n]*[A-Za-z][!¡][\s\U0001F300-\U0001FAFF☀-➿]*\""), "all"),
    ("title-case", "#25", "Title Case in UI text (sentence case: \"Your subscriptions\")",
     TITLE_CASE, "all"),
    ("greeting", "#26", "Greeting as a title (name what the screen is)",
     re.compile(r"(?i:\b(Welcome back|Hey there|Hello there|Good (morning|afternoon|evening)),?\b)|"
                r"[\"'>`]\s*(?i:Hey|Hi|Hello|Welcome back|Welcome),?\s+(?:[A-Z][a-z]+\b|\{|\$\{|\\\()"), "all"),
    ("transition-all", "#63", "transition: all (animate transform and opacity, named)",
     re.compile(r"transition\s*:\s*all\b|transition-property\s*:\s*all\b|\btransition-all\b"), "web"),
    ("tracked-caps", "#45 #60", "Small tracked all-caps label (eyebrow/kicker) — does it carry information?",
     re.compile(r"\buppercase\b[^\"'\n]*\btracking-(wide|wider|widest)\b|\btracking-(wide|wider|widest)\b[^\"'\n]*\buppercase\b|"
                r"text-transform\s*:\s*uppercase|\.textCase\(\.uppercase\)|\.uppercase\(\)"), "all"),
    ("three-dots", "#61", "Three dots in UI text (use the … character)",
     re.compile(r"[\"'>`][^\"'<`\n]*[A-Za-z]\.\.\.(?=[\"'<`\s])"), "all"),
    ("hype-copy", "#64", "Hype copy (say what it does, with a number if there is one)",
     re.compile(r"[\"'>`][^\"'<`\n]*\b(Supercharge|Unleash|Revolutioni[sz]e|Seamless(ly)?|Effortless(ly)?|Game-changing|"
                r"Cutting-edge|Next-level|Elevate your|Transform your|Take your \w+ to the next level|"
                r"Crush (it|your)|You'?ve got this|You got this|Let'?s (go|do this|crush)|Beast mode|Level up|"
                r"(?:adventure|journey|story|future|next chapter|\w+ experience) awaits|Your (?:journey|adventure) (?:starts|begins)|"
                r"Ready when you are|Like never before|At your fingertips|The future of \w+|"
                r"Unlock your|Smash (it|your))\b", re.I), "all"),
    ("no-focus", "#53", "Focus outline removed — is there a :focus-visible style?",
     re.compile(r"outline\s*:\s*(none|0)\b|\boutline-none\b|focus:outline-none"), "web"),
]


# Starter-kit values nobody changed (#6). Checked against the shadcn registry
# (apps/v4/public/r/colors: neutral, zinc, slate; v4 oklch and v3 HSL) and
# Android Studio's Compose template (ui/theme/Color.kt). Only the values that
# carry the kit's identity count; two or more in one file = the personality
# was inherited. A team that set its own radius and accent isn't flagged for
# keeping the kit's grays.
SHADCN_DEFAULTS = {
    "radius": {"0.625rem", "0.5rem"},
    "primary": {"oklch(0.205 0 0)", "oklch(0.21 0.006 285.885)", "oklch(0.208 0.042 265.755)",
                "222.2 47.4% 11.2%", "240 5.9% 10%", "0 0% 9%"},
    "foreground": {"oklch(0.145 0 0)", "oklch(0.141 0.005 285.823)", "oklch(0.129 0.042 264.695)",
                   "222.2 84% 4.9%", "240 10% 3.9%", "0 0% 3.9%"},
    "ring": {"oklch(0.708 0 0)", "oklch(0.705 0.015 286.067)", "oklch(0.704 0.04 256.788)",
             "222.2 84% 4.9%", "240 10% 3.9%", "0 0% 3.9%"},
}
SHADCN_DECL = re.compile(r"--(radius|primary|foreground|ring)\s*:\s*([^;]+);")
COMPOSE_TEMPLATE = re.compile(r"0xFF(D0BCFF|CCC2DC|EFB8C8|6650A4|625B71|7D5260)\b", re.I)

# Repeated surfaces (#40, #58, #65): the same card markup three or more times
# in one file, each holding a number = a row of stat tiles. Literal repeats
# only: a card rendered by .map()/ForEach appears once and isn't counted.
# The element and its class, block-level only: a pill or badge (<span>) isn't a card.
CLASS_ATTR = re.compile(r"""<(?!(?:span|small|i|b|em|strong|code|kbd|label|svg|img)\b)([\w.]+)\b[^<>]*?\bclass(?:Name)?\s*=\s*["'{`]+([^"'`}]+)["'`}]""")
UTILITY_SURFACE = re.compile(r"\brounded(-\w+)?\b")
UTILITY_FILL = re.compile(r"\b(bg-\S+|border\b|border-\S+|shadow(-\S+)?)")
CSS_RULE = re.compile(r"\.([\w-]+)\s*\{([^}]*)\}")
# A number is digits in the text ("$12,400", "99.9%", "10x", "500+"), not just large type: an
# emoji icon at text-2xl isn't a stat.
NUMBER_CHILD = re.compile(r">\s*[$€£¥+\-−]?\d[\d.,:]*\s*(%|k|K|M|km|h|min|x|\+)?\s*<|"
                          r"class(?:Name)?=[\"'][^\"']*\b(num|number|value|metric|stat|kpi)\b")
CAPS_LITERAL = re.compile(r"\b(?:Text)\(\s*(?:text\s*=\s*)?\"([A-Z][A-Z0-9 &·'’/-]{3,})\"")
TRACKING = re.compile(r"\.tracking\(|\.kerning\(|letterSpacing\s*=")
# Invented social proof and metrics (#64). File-level, so a figure and its label on
# separate lines ("<div>10x</div>" then "<div>Faster</div>") still read as one claim.
UNVERIFIED_CLAIM = re.compile(r"(?i:\b(?:trusted|used|loved|chosen|relied on) by\s+(?:over\s+|more than\s+)?[\d,.]+\s*[km]?\+?\s+\w+)|"
                r"(?i:\b(?:join|over|more than)\s+[\d,.]+\s*[km]?\+\s+(?:teams|users|customers|companies|developers|engineers|businesses|people|creators))|"
                r"\b\d+(?:\.\d+)?x\b(?:\s|<[^<>]+>){1,12}(?i:faster|better|more|quicker|cheaper|productiv)|"
                r"\b99\.9+%(?:\s|<[^<>]+>){1,12}(?i:uptime|reliab|sla)")
# A map, camera or canvas with a permanent tab bar under it (#59): the chrome eats the
# canvas's bottom edge. Heuristic and cheap in the score: one canvas and one bottom bar
# in the same file.
CANVAS = re.compile(r"\b(?:GoogleMap|MapView|MapboxMap|Map|[A-Z]\w*Map|CameraPreview|CameraView|ARView|SceneView)\s*\(|"
                    r"\bMap\s*\{|maplibregl|mapboxgl|\bL\.map\(|<canvas\b|<(?:svg|div)\b[^<>]*\bclass=[\"'][^\"']*\bmap\b")
BOTTOM_BAR = re.compile(r"\bNavigationBar\s*[({]|\bBottomNavigation\w*\s*[({]|\bTabView\s*[({]|\.tabItem\s*\{|"
                        r"<nav\b[^<>]*\bclass=[\"'][^\"']*\bfixed\b[^\"']*\bbottom-0|"
                        r"\bnav\s*\{[^}]*position\s*:\s*fixed[^}]*bottom\s*:\s*0")
COMPONENT = re.compile(r"@Composable\b|\bstruct\s+\w+\s*:\s*(?:some\s+)?\w*View\b")
CTA = re.compile(r"<(button|Button)\b|<a\b[^>]*\bhref")
NATIVE_ROW = re.compile(r"\b(LazyVGrid|LazyHGrid|Grid|GridRow|HStack|LazyVerticalGrid|LazyHorizontalGrid|Row|FlowRow)\s*[({]")
NATIVE_CARD_CALL = re.compile(r"\b([A-Z]\w*(?:Card|Tile))\(")


def element_at(text, start):
    """The element opening at `start`, up to its own closing tag (nesting counted)."""
    tag = re.match(r"<([\w.]+)", text[start:]).group(1)
    tags = re.compile(rf"<(/?){re.escape(tag)}\b[^>]*?(/?)>")
    depth = 0
    for m in tags.finditer(text, start):
        if m.group(2):  # self-closing
            if depth == 0:
                return text[start:m.end()]
            continue
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return text[start:m.end()]
    return text[start:start + 400]


TAG = re.compile(r"<(/?)([\w.]+)\b([^<>]*?)(/?)>")
ROW_UTILITY = re.compile(r"\bgrid-cols-([2-9]|1[0-2])\b|\bflex\b(?![^\"']*\bflex-col\b)|\bflex-row\b")


def css_rules(text, names):
    return " ".join(m.group(2) for m in CSS_RULE.finditer(text) if m.group(1) in names)


def jsx_style(attrs):
    """style="…" as is; style={{ display: "grid", gridTemplateColumns: "…" }} as CSS."""
    html = re.search(r"""\bstyle\s*=\s*["']([^"']+)""", attrs)
    if html:
        return html.group(1)
    obj = re.search(r"\bstyle\s*=\s*\{\{(.*?)\}\}", attrs, re.S)
    if not obj:
        return ""
    out = []
    for k, v in re.findall(r"""(\w+)\s*:\s*(["'`][^"'`]*["'`]|[\w.-]+)""", obj.group(1)):
        out.append(re.sub(r"[A-Z]", lambda c: "-" + c.group(0).lower(), k) + ": " + v.strip("\"'`") + ";")
    return " ".join(out)


def side_by_side(text, start, cls):
    """(True when the card sits in a multi-column grid or a flex row, its parent's offset)."""
    own_row = bool(re.search(r"flex\s*:\s*1\b|flex-grow\s*:\s*1", css_rules(text, set(cls.split()))))
    stack = []
    for m in TAG.finditer(text, 0, start):
        closing, name, attrs, selfclose = m.groups()
        if selfclose or name.lower() in ("br", "img", "input", "meta", "link", "hr", "source"):
            continue
        if closing:
            while stack and stack.pop()[0] != name:
                pass
        else:
            stack.append((name, attrs, m.start()))
    if not stack:
        return own_row, -1
    _, attrs, parent = stack[-1]
    if own_row:
        return True, parent
    pc = re.search(r"""\bclass(?:Name)?\s*=\s*["'{`]+([^"'`}]+)""", attrs)
    pcls = pc.group(1) if pc else ""
    rules = css_rules(text, set(pcls.split())) + " " + jsx_style(attrs)
    if ROW_UTILITY.search(pcls):
        return True, parent
    cols = re.search(r"grid-template-columns\s*:\s*([^;}]+)", rules)
    if cols and (len(cols.group(1).split()) >= 2 or re.search(r"repeat\(\s*([2-9]|auto)", cols.group(1))):
        return True, parent
    row = re.search(r"display\s*:\s*(inline-)?flex", rules) and not re.search(r"flex-direction\s*:\s*column", rules)
    return bool(row), parent


def balanced(text, i):
    """Index just past the parenthesis group that opens at text[i] ("(")."""
    depth, quote = 0, None
    for j in range(i, len(text)):
        c = text[j]
        if quote:
            if c == "\\":
                continue
            if c == quote:
                quote = None
        elif c == '"':
            quote = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j + 1
    return len(text)


MODIFIER = re.compile(r"\s*\.(\w+)")


def own_call_and_modifiers(text, start):
    """The call opening at `start` (its arguments) plus its own modifier chain:
    `.font(…).tracking(…)` across lines, nothing after the chain ends."""
    end = balanced(text, text.index("(", start))
    while True:
        m = MODIFIER.match(text, end)
        if not m:
            break
        end = m.end()
        if end < len(text) and text[end] == "(":
            end = balanced(text, end)
    return text[start:end]


def file_checks(path, text, kind, hits):
    lines = text.splitlines()
    ignored = {n for n, l in enumerate(lines, 1) if "unslop-ignore" in l}

    def line_of(pos):
        return text.count("\n", 0, pos) + 1

    kit_key = ("stock-kit", "#6", "Starter kit left at its defaults (set radius, grays and accent from the product)")
    found = [(line_of(m.start()), f"--{m.group(1)}: {m.group(2).strip()}") for m in SHADCN_DECL.finditer(text)
             if m.group(2).strip() in SHADCN_DEFAULTS[m.group(1)]]
    found = [f for f in found if f[0] not in ignored]
    props = {v.split(":")[0] for _, v in found}
    if len(props) >= 2 and props & {"--radius", "--primary"}:  # kept grays alone aren't an untouched kit
        hits.setdefault(kit_key, []).append((path, found[0][0], f"shadcn: {', '.join(v for _, v in found[:3])}"))
    found = [(line_of(m.start()), m.group(0)) for m in COMPOSE_TEMPLATE.finditer(text)]
    found = [f for f in found if f[0] not in ignored]
    if len({v.upper() for _, v in found}) >= 2:
        hits.setdefault(kit_key, []).append((path, found[0][0], f"Compose template colors: {', '.join(v for _, v in found[:3])}"))

    # Native: the map and the bar must be in the same composable / view, not two screens in one file.
    starts = [0] + ([m.start() for m in COMPONENT.finditer(text)] if kind == "native" else []) + [len(text)]
    for a, b in zip(starts, starts[1:]):
        canvas, bar = CANVAS.search(text, a, b), BOTTOM_BAR.search(text, a, b)
        if canvas and bar and line_of(bar.start()) not in ignored:
            hits.setdefault(("canvas-tabbar", "#59", "Map or camera with a permanent tab bar under it (let the chrome float)"), []).append(
                (path, line_of(bar.start()), f"canvas: {canvas.group(0).strip()[:30]}"))

    for m in UNVERIFIED_CLAIM.finditer(text):
        n = line_of(m.start())
        if n not in ignored:
            claim = re.sub(r"<[^<>]+>", " ", m.group(0))
            hits.setdefault(("unverified-claim", "#64", "Social proof or metric to source (\"Trusted by 10,000+ teams\", \"10x faster\") — is it real?"), []).append(
                (path, n, " ".join(claim.split())[:80]))

    if kind == "web":
        # A row of nav links hidden on small screens with no menu button: the phone loses navigation (#57).
        toggle = re.compile(r"aria-expanded|aria-controls|<details\b|popovertarget")
        for nav in re.finditer(r"<nav\b", text):
            block = element_at(text, nav.start())
            # A menu counts only if it's inside this nav or points at it (or at the hidden links) by id.
            ids = re.findall(r"""\bid\s*=\s*["']([^"']+)""", block)
            targets = set(re.findall(r"""(?:aria-controls|popovertarget)\s*=\s*["']([^"']+)""", text))
            menu = toggle.search(block) or (set(ids) & targets)
            for h in re.finditer(r"""<[\w.]+\b[^<>]*?\bclass(?:Name)?\s*=\s*["'{`]+[^"'`}]*\bhidden\s+(?:[^"'`}]*\s)?(?:sm|md|lg|xl):(?:flex|block|inline-flex|grid|inline)\b""", block):
                n = line_of(nav.start() + h.start())
                if not menu and n not in ignored and len(re.findall(r"<a\b", element_at(block, h.start()))) >= 2:
                    hits.setdefault(("hidden-nav", "#57", "Nav links hidden on phones with no menu button"), []).append(
                        (path, n, "links hidden below a breakpoint, nothing replaces them"))

    key = ("card-sameness", "#40 #65", "Same card repeated with a number inside (a row of stat tiles?)")
    if kind == "web":
        surfaces = {m.group(1) for m in CSS_RULE.finditer(text)
                    if re.search(r"border-radius", m.group(2)) and re.search(r"background|box-shadow|border\s*:", m.group(2))}
        groups = {}
        for m in CLASS_ATTR.finditer(text):
            cls = " ".join(m.group(2).split())
            names = set(cls.split())
            is_surface = (UTILITY_SURFACE.search(cls) and UTILITY_FILL.search(cls)) or names & surfaces
            if is_surface:
                groups.setdefault(cls, []).append(m.start())
        rows = {}  # (class, parent) -> starts: each container judged on its own
        for cls, all_starts in groups.items():
            if len(all_starts) < 3:
                continue
            for s in all_starts:
                inline, parent = side_by_side(text, s, cls)
                if inline:  # a stacked list of rows is #40's entity row, not tiles
                    rows.setdefault((cls, parent), []).append(s)
        for (cls, _parent), starts in rows.items():
            n = line_of(starts[0])
            if len(starts) < 3 or n in ignored:
                continue
            blocks = [element_at(text, s) for s in starts]
            with_number = sum(1 for b in blocks if NUMBER_CHILD.search(b))
            with_action = sum(1 for b in blocks if CTA.search(b))
            if with_number >= 3 and with_action * 2 < len(blocks):  # cards with a button are offers (pricing), not stat tiles
                hits.setdefault(key, []).append((path, n, f'class "{cls[:50]}" ×{len(starts)}, {with_number} with a number'))
    else:
        for m in CAPS_LITERAL.finditer(text):
            n = line_of(m.start())
            if n not in ignored and len(m.group(1).split()) <= 5 and TRACKING.search(own_call_and_modifiers(text, m.start())):
                hits.setdefault(("tracked-caps", "#45 #60", "Small tracked all-caps label (eyebrow/kicker) — does it carry information?"), []).append(
                    (path, n, f'"{m.group(1)}" + tracking'))
        calls = {}
        for m in NATIVE_CARD_CALL.finditer(text):
            if re.search(r"\b(struct|fun|class|func|init)\s+$", text[max(0, m.start() - 20):m.start()]):
                continue  # the declaration, not a call
            calls.setdefault(m.group(1), []).append(m.start())
        for name, starts in calls.items():
            n = line_of(starts[0])
            if len(starts) >= 3 and n not in ignored and NATIVE_ROW.search(text):
                hits.setdefault(key, []).append((path, n, f"{name}(…) ×{len(starts)}"))


def files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, names in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for n in names:
                if os.path.splitext(n)[1].lower() in WEB | NATIVE:
                    yield os.path.join(root, n)


def scan(path, scale, hits):
    ext = os.path.splitext(path)[1].lower()
    kind = "native" if ext in NATIVE else "web"
    is_token_file = bool(TOKEN_FILE.search(os.path.basename(path)))
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return
    if path.endswith(".min.js") or path.endswith(".min.css") or len(text) > 2_000_000:
        return
    has_focus_visible = "focus-visible" in text
    file_checks(path, text, kind, hits)
    in_root = False
    for n, line in enumerate(text.splitlines(), 1):
        if "unslop-ignore" in line:
            continue
        stripped = line.strip()
        if stripped.startswith(":root") or "@theme" in stripped:
            in_root = True
        if in_root and stripped.startswith("}"):
            in_root = False
            continue
        if stripped.startswith(("//", "/*", "*", "#!", "import ", "@import")):
            continue
        for rid, ref, desc, rx, applies in RULES:
            if applies != "all" and applies != kind:
                continue
            if rid == "raw-color" and (is_token_file or in_root or stripped.startswith("--")):
                continue
            if rid == "no-focus" and has_focus_visible:
                continue
            if rx.search(line):
                hits.setdefault((rid, ref, desc), []).append((path, n, stripped[:110]))
        if kind == "web" and not is_token_file and not in_root:
            for m in PX_PROP.finditer(line):
                if "var(" in m.group(3) or "calc(" in m.group(3):
                    continue
                off = [v for v in PX.findall(m.group(3)) if abs(float(v)) not in scale]
                if off:
                    key = ("off-scale", "#1", "Spacing / type / radius value off the scale")
                    hits.setdefault(key, []).append((path, n, f"{m.group(1)}{m.group(2) or ''}: {', '.join(o + 'px' for o in off)}"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--scale", default="0,1,2,4,8,12,16,20,24,32,40,48,64,80,96",
                    help="allowed px values (1 for hairlines); match your tokens")
    ap.add_argument("--max", type=int, default=8, help="locations shown per rule")
    ap.add_argument("--strict", action="store_true", help="exit 1 if anything is found")
    a = ap.parse_args()
    scale = {float(x) for x in a.scale.split(",")}
    hits, count = {}, 0
    for f in files(a.paths):
        count += 1
        scan(f, scale, hits)
    print(f"unslop scan: {count} files")
    if not hits:
        print("nothing found")
        return 0
    order = [r[0] for r in RULES] + ["off-scale", "stock-kit", "card-sameness", "hidden-nav", "unverified-claim", "canvas-tabbar"]
    for (rid, ref, desc), where in sorted(hits.items(), key=lambda kv: (-len(kv[1]), order.index(kv[0][0]))):
        print(f"\n[{ref}] {desc} — {len(where)} hit(s)")
        for path, n, snippet in where[: a.max]:
            print(f"  {path}:{n}  {snippet}")
        if len(where) > a.max:
            print(f"  … {len(where) - a.max} more")
    return 1 if a.strict else 0


if __name__ == "__main__":
    sys.exit(main())
