#!/usr/bin/env python3
"""Find the usual slop patterns in UI source code, with the checklist number.

    python3 scripts/slop-scan.py [paths…] [--scale 0,2,4,8,12,16,20,24,32,40,48,64]
                                 [--max 8] [--strict] [--json] [--github] [--list-rules]

Reads web (CSS, SCSS, HTML, JSX/TSX, Vue, Svelte, Astro), SwiftUI and
Compose files. Standard library only. It is a grep with opinions: each hit
is a place to look, not a verdict — a gradient can be the one signature
gesture (#34, principle 7). Silence a line with a comment containing
`unslop-ignore`. With --strict it exits 1 when anything is found (for a
pre-commit hook; don't put it in paid CI without asking). --github adds an
Actions annotation per hit; --json prints every location for other tools.
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
TOKEN_FILE = re.compile(r"(token|theme|variables|palette|colors?|tailwind\.config|design[-_]?system|typography|dimens|spacing|"
                        r"^type\.(kt|swift)$|^shapes?\.(kt|swift)$)", re.I)

TOKEN_DECL = re.compile(r"--[\w-]+\s*:\s*[^;}]+")
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
           "Back|Sign|Log|Up|Out|Learn|Try|Unlock|Upgrade|Activity|Settings|Account|Details|Overview|"
           "Status|Order|Orders|Tracking|History|Profile|Notifications|Summary|Payment|Payments|Billing|"
           "Preferences|Privacy|Security|Plan|Plans|Subscription|Subscriptions|Report|Reports|Messages")
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
     re.compile(r">[^<>{}\n]*[A-Za-z][!¡](?=[\s\U0001F300-\U0001FAFF☀-➿<])|"
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
                r"Crush(?:ing)? (it|your)|You'?ve got this|You got this|Let'?s (go|do this|crush)|Beast mode|Level up|"
                r"(?:adventure|journey|story|future|next chapter|\w+ experience) awaits|Your (?:journey|adventure) (?:starts|begins)|"
                r"Ready when you are|Like never before|At your fingertips|The future of \w+|"
                r"In today'?s (?:fast-paced|digital|busy) (?:world|age)|Let'?s dive in|"
                r"Unlock your|Smash (it|your))\b", re.I), "all"),
    ("elevation-literal", "#5 #32", "Shadow / elevation literal on a component (one named elevation token)",
     re.compile(r"\b(?:cardElevation|shadowElevation|tonalElevation|elevation)\s*(?:=\s*|\()\s*\d+(?:\.\d+)?\.dp|"
                r"\.shadow\(\s*(?:color:[^)]*?,\s*)?radius:\s*\d"), "native"),
    ("translucent-text", "#22", "Semi-transparent white text (on color it washes out: use a role color, measured)",
     re.compile(r"Color\.White\.copy\(\s*alpha\s*=\s*0?\.\d|(?:foregroundColor|foregroundStyle)\(\s*(?:Color)?\.white\.opacity\(|"
                r"\btext-white/\d{1,2}\b|(?<![-\w])color\s*:\s*rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0?\.\d"), "all"),
    ("empty-action", "#64", "A control whose action is empty (it implies a feature that doesn't exist: principle 6)",
     re.compile(r"\bonClick\s*=\s*\{\s*\}|\bonClick=\{\s*\(\s*\)\s*=>\s*\{\s*\}\s*\}|"
                r"\bButton\s*\(\s*(?:action:\s*)?\{\s*\}|\bButton\s*\{\s*\}\s*label|\baction:\s*\{\s*\}"), "all"),
    ("pressure", "#64", "Pressure copy (countdown, scarcity, \"most popular\", \"save N%\"): true, computed and sourced?",
     re.compile(r"(?i:\boffer ends in\b|\bends in \d|\blimited[- ]time (?:offer|deal|only)\b|\bonly \d+ (?:left|spots?|seats?)\b|"
                r"\bhurry\b|\bact now\b|\blast chance\b|\bmost popular\b|\bbest (?:value|seller)\b|"
                r"\bsave \d+\s?%(?!(?:\s|<[^<>]+>)*(?:vs\.?|versus|compared|than)\b))"), "all"),
    ("plural-hack", "#71", "\"item(s)\" in UI text (let the platform's plural rules pick the form)",
     re.compile(r"(?:[\"'`]|(?<!=)>)[^\"'<`\n]*(?<=[\s>\"'`])[A-Za-z][a-z]{2,}\(s\)(?=[\s.,:!?<\"'`]|$)"), "all"),
    ("justified-text", "#28", "Justified text (uneven gaps on screens; align left)",
     re.compile(r"text-align\s*:\s*justify\b|\btext-justify\b(?!\s*:)"), "web"),
    ("extreme-tracking", "#29", "Letter-spacing tighter than -0.04em (letters collide; a bit tighter, not crushed)",
     re.compile(r"letter-spacing\s*:\s*-0?\.(?:0[5-9]|[1-9])\d*em|\btracking-\[-0?\.(?:0[5-9]|[1-9])\d*em\]"), "web"),
    ("fixed-width", "#57", "Fixed width of 400px or more (scrolls sideways on a phone: max-width and fluid)",
     re.compile(r"(?<![-\w(])(?:min-)?width\s*:\s*(?:[4-9]\d{2}|\d{4,})px|(?<![\w-])(?:min-)?w-\[(?:[4-9]\d{2}|\d{4,})px\]"), "web"),
    ("lorem", "#48", "Lorem ipsum (real content in every mock)",
     re.compile(r"(?i:\blorem ipsum\b|\bdolor sit amet\b)"), "all"),
    ("placeholder-image", "#35 #48", "Placeholder image service (real images, or none)",
     re.compile(r"(?i:via\.placeholder\.com|placehold\.(?:co|it)\b|picsum\.photos|dummyimage\.com|placekitten\.com|"
                r"loremflickr\.com|source\.unsplash\.com/random|placeimg\.com)"), "all"),
    ("bare-delta", "#52", "A delta with no baseline (\"+12%\" vs what? \"+12% vs September\")",
     re.compile(r"(?:>|[\"'`]|\(\s*\")\s*[+↑▲↓▼−]\s?\d+(?:[.,]\d+)?\s?%(?!(?:[^<\"'`\n]|<[^<>]+>){0,48}?"
                r"(?i:\b(?:vs\.?|versus|than|from|since|compared|over|last|previous|prior|yesterday|week|month|quarter|year|"
                r"yoy|mom|wow|qoq|baseline|target|goal|avg|average)\b))"), "all"),
    ("straight-quotes", "#61", "Straight quote or apostrophe in UI copy (use ’ “ ”)",
     re.compile(r">[^<>{}\n]*[A-Za-z]'[A-Za-z][^<>{}\n]*<|>[^<>{}\n=]*\s\"[A-Za-z][^\"<>{}\n]*\"[^<>{}\n]*<|"
                r"\b(?:Text|Button|Label|navigationTitle)\(\s*(?:text\s*=\s*)?\"[^\"\n]*[A-Za-z]'[A-Za-z]"), "all"),
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
                r"(?i:\b(?:join|over|more than)\s+[\d,.]+\s*[km]?\+\s+(?:[a-z]+\s+){0,2}(?:teams|users|customers|companies|developers|engineers|"
                r"businesses|people|creators|members|readers|subscribers))|"
                r"\b\d+(?:\.\d+)?x\b(?:\s|<[^<>]+>){1,12}(?i:faster|better|more|quicker|cheaper|productiv|[a-z]{3,}er\b)|"
                r"\b100\s?%(?:\s|<[^<>]+>){1,12}(?i:waterproof|secure|safe|guaranteed|satisfaction|natural|organic|accurate|"
                r"reliable|effective|confidence|private|free\b)|"
                r"\b99\.9+%(?:\s|<[^<>]+>){1,12}(?i:uptime|reliab|sla)")
# A map, camera or canvas with a permanent tab bar under it (#59): the chrome eats the
# canvas's bottom edge. Heuristic and cheap in the score: one canvas and one bottom bar
# in the same file.
# Native constructors only in Swift/Kotlin: on the web `new Map()` is a collection, not a map.
CANVAS_NATIVE = re.compile(r"\b(?:GoogleMap|MapView|MapboxMap|Map|[A-Z]\w*Map|CameraPreview|CameraView|ARView|SceneView)\s*\(|\bMap\s*\{")
CANVAS_WEB = re.compile(r"maplibregl|mapboxgl|\bL\.map\(|<canvas\b|<(?:GoogleMap|MapContainer|Map)\b|"
                        r"<(?:svg|div)\b[^<>]*\bclass(?:Name)?=[\"'{`]+[^\"'`}]*\bmap\b")
BOTTOM_BAR = re.compile(r"\bNavigationBar\s*[({]|\bBottomNavigation\w*\s*[({]|\bTabView\s*[({]|\.tabItem\s*\{|"
                        r"<nav\b[^<>]*\bclass(?:Name)?=[\"'{`]+[^\"'`}]*\bfixed\b[^\"'`}]*\bbottom-0|"
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


LINK_CSS = re.compile(r"""<link\b[^>]*\brel=["']?stylesheet[^>]*>""", re.I)


def linked_css(path, text):
    """Local stylesheets the page links: the card and layout rules often live there, not inline."""
    out = []
    for tag in LINK_CSS.findall(text):
        href = re.search(r"""\bhref=["']([^"'#?]+)""", tag)
        if href and not re.match(r"^(?:[a-z]+:)?//", href.group(1)):
            f = os.path.normpath(os.path.join(os.path.dirname(path), href.group(1)))
            try:
                out.append(open(f, encoding="utf-8", errors="replace").read())
            except OSError:
                pass
    return "\n" + "\n".join(out)


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


def side_by_side(text, start, cls, css=""):
    """(True when the card sits in a multi-column grid or a flex row, its parent's offset)."""
    own_row = bool(re.search(r"flex\s*:\s*1\b|flex-grow\s*:\s*1", css_rules(text + css, set(cls.split()))))
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
    rules = css_rules(text + css, set(pcls.split())) + " " + jsx_style(attrs)
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
        canvas, bar = (CANVAS_NATIVE if kind == "native" else CANVAS_WEB).search(text, a, b), BOTTOM_BAR.search(text, a, b)
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

    if kind == "web":
        block_checks(path, text, ignored, line_of, hits)

    key = ("card-sameness", "#40 #65", "Same card repeated with a number inside (a row of stat tiles?)")
    if kind == "web":
        css = linked_css(path, text)
        surfaces = {m.group(1) for m in CSS_RULE.finditer(text + css)
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
                inline, parent = side_by_side(text, s, cls, css)
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


# Rule-level checks (#60, #66-#69): what a declaration means depends on its neighbors in the
# same rule or class list, so they read whole CSS blocks and whole class attributes.
CSS_EXT = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".vue", ".svelte", ".astro"}
MARKUP_EXT = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".mdx"}
PAGE_EXT = {".html", ".htm", ".vue", ".svelte", ".astro"}
ANY_CLASS = re.compile(r"""\bclass(?:Name)?\s*=\s*["'{`]+([^"'`}]+)""")
SECTION_NUMBER = re.compile(r">\s*0([1-9])\s*[.·/—–-]?\s*<")
COUNT_PILL = re.compile(r"""<(?:span|small|b|div|em|i)\b[^<>]*\bclass(?:Name)?\s*=\s*["'{`]+[^"'`}]*(?:\brounded-full\b[^"'`}]*\bbg-[a-z]+-(?:[4-9]00)\b|\bbg-[a-z]+-(?:[4-9]00)\b[^"'`}]*\brounded-full\b|\b(?:badge|pill)\b)[^"'`}]*["'`}]+[^<>]*>\s*\d{1,4}\+?\s*</""")
ICON_CIRCLE = re.compile(r"(?=.*\brounded-(?:full|xl|2xl)\b)(?=.*\bbg-[a-z]+-(?:50|100|200)\b)(?=.*\b(?:size|w|h)-(?:8|9|10|11|12|14)\b)")
CSS_BLOCK = re.compile(r"([^{}]+)\{([^{}]*)\}")
SIDE_BORDER = re.compile(r"border-(?:left|right|inline-start|inline-end)(?:-width)?\s*:\s*(\d+(?:\.\d+)?)px\s*(?:solid|[^;]*)", re.I)
RADIUS = re.compile(r"border-radius\s*:(?!\s*0(?:px)?\s*(?:[;}]|$))", re.I)
# A box-shadow layer with no blur: "4px 4px 0 #000", "6px 6px 0px 0px black". Insets and 0 0 rings excluded.
HARD_SHADOW = re.compile(r"(?<![\w.-])(-?[1-9]\d*(?:\.\d+)?)px\s+(-?\d+(?:\.\d+)?)(?:px)?\s+0(?:px)?(?:\s+-?\d+(?:px)?)?\s+(?:#|rgba?\(|hsla?\(|oklch\(|[a-z]+\b)", re.I)
TW_HARD_SHADOW = re.compile(r"\bshadow-\[-?\d+px_-?\d+px_0(?:px)?[_\]]")
SHADOW_DECL_ANY = re.compile(r"box-shadow\s*:\s*([^;}]+)", re.I)
# Easing that overshoots (y outside 0..1) or animations named for a bounce (#67).
CUBIC = re.compile(r"cubic-bezier\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)")
BOUNCE_NAME = re.compile(r"@keyframes\s+[\w-]*(bounce|elastic|wobble|jiggle|rubber)|\banimation(?:-name)?\s*:[^;]*\b[\w-]*(bounce|elastic|wobble|jiggle|rubber)|"
                         r"\banimate-bounce\b|\bease(?:In|Out|InOut)?(?:Back|Elastic|Bounce)\b|\b(?:back|elastic|bounce)\.(?:out|in|inOut)\b", re.I)
# A 1px border and a soft shadow on the same rounded surface (#68): two separators doing one job.
TW_GHOST = re.compile(r"""(?=[^"'`]*\brounded(?:-\w+)?\b)(?=[^"'`]*(?<![\w:-])border(?![\w-]))(?=[^"'`]*(?<![\w:-])shadow(?:-(?:sm|md|xs))?(?![\w-]))""")
BORDER_1PX = re.compile(r"(?<![\w-])border\s*:\s*1px\s+solid", re.I)
SOFT_SHADOW = re.compile(r"box-shadow\s*:\s*(?!none|0\s+0\s+0)[^;}]*\d+px\s+\d+px", re.I)
# Monospace as a costume (#69): headings or the whole page set in a code face.
MONO_FACE = re.compile(r"font-family\s*:\s*[^;}]*(?:\bmono\b|monospace|courier|fira code|space mono|menlo|consolas|jetbrains mono|ibm plex mono|geist mono|sf mono|roboto mono)", re.I)
MONO_SELECTOR = re.compile(r"(?:^|[\s,>])(?:h[1-3]|body|html|:root)\b|\.[\w-]*(?:hero|title|headline|heading|display)\b", re.I)
TW_MONO_HEADING = re.compile(r"<(h[1-3]|body|html)\b[^<>]*\bclass(?:Name)?\s*=\s*[\"'{`]+[^\"'`}]*\bfont-mono\b")


def block_checks(path, text, ignored, line_of, hits):
    ext = os.path.splitext(path)[1].lower()

    def add(key, pos, snippet):
        n = line_of(pos)
        if n not in ignored:
            hits.setdefault(key, []).append((path, n, snippet[:110]))

    stripe = ("side-stripe", "#60", "Colored side stripe on a rounded card (does the stripe encode a status?)")
    hard = ("hard-shadow", "#66", "Hard offset shadow (no blur): a costume unless the brand is neobrutalist")
    bounce = ("bounce-easing", "#67", "Bouncy or elastic easing (ease out, don't overshoot)")
    ghost = ("ghost-card", "#68", "1px border and a soft shadow on the same card (pick one separator)")
    mono = ("mono-disguise", "#69", "Monospace on headings or the whole page (code faces are for code and data)")

    if ext in CSS_EXT:
        for m in CSS_BLOCK.finditer(text):
            sel, body = m.group(1).strip(), m.group(2)
            if sel.startswith("@") or "@keyframes" in sel:
                continue
            pos = m.start(2)
            side = SIDE_BORDER.search(body)
            if side and float(side.group(1)) >= 2 and RADIUS.search(body):
                add(stripe, pos + side.start(), f"{sel.split()[-1] if sel.split() else sel} {{ {side.group(0).strip()} …radius }}")
            if BORDER_1PX.search(body) and SOFT_SHADOW.search(body) and RADIUS.search(body):
                add(ghost, pos, f"{sel[-40:]} {{ border: 1px … box-shadow … }}")
            if MONO_FACE.search(body) and MONO_SELECTOR.search(" " + sel):
                add(mono, pos + MONO_FACE.search(body).start(), f"{sel[-40:]} {{ {MONO_FACE.search(body).group(0)[:60]} }}")
    for m in SHADOW_DECL_ANY.finditer(text):
        for layer in re.split(r",(?![^()]*\))", m.group(1)):
            if "inset" in layer:
                continue
            h = HARD_SHADOW.search(layer.strip())
            if h:
                add(hard, m.start(), f"box-shadow: {layer.strip()[:60]}")
                break
    for m in TW_HARD_SHADOW.finditer(text):
        add(hard, m.start(), m.group(0))
    for m in CUBIC.finditer(text):
        y1, y2 = float(m.group(2)), float(m.group(4))
        if y1 < -0.05 or y1 > 1.05 or y2 < -0.05 or y2 > 1.05:
            add(bounce, m.start(), m.group(0))
    for m in BOUNCE_NAME.finditer(text):
        add(bounce, m.start(), m.group(0).strip())
    for m in CLASS_ATTR.finditer(text):
        cls = m.group(2)
        if TW_GHOST.match(cls):
            add(ghost, m.start(), f'class "{" ".join(cls.split())[:60]}"')
        side = re.search(r"\bborder-[lrse]-(?:[2-9]|\[\d+px\])\b", cls)
        if side and re.search(r"\brounded(?:-\w+)?\b", cls):
            add(stripe, m.start(), f'class "{" ".join(cls.split())[:60]}"')
    for m in TW_MONO_HEADING.finditer(text):
        add(mono, m.start(), f"<{m.group(1)} class=… font-mono>")

    if ext in MARKUP_EXT:
        # #13: one h1 per page; section titles are labels.
        h1s = [m.start() for m in re.finditer(r"<h1\b", text)]
        if len(h1s) >= 2 and ext in PAGE_EXT:  # a .tsx file often holds several components
            add(("multiple-h1", "#13", "More than one h1 on the page (section titles are labels, not h1)"), h1s[1], f"{len(h1s)} × <h1>")
        # #60: 01 / 02 / 03 on sections.
        nums = [(m.start(), int(m.group(1))) for m in SECTION_NUMBER.finditer(text)]
        if {1, 2, 3} <= {n for _, n in nums}:
            add(("section-numbers", "#60", "Sections numbered 01 / 02 / 03 (does the order carry information?)"), nums[0][0], "01, 02, 03…")
        # #50: counts in filled pills.
        for m in COUNT_PILL.finditer(text):
            add(("count-pill", "#50", "A count in a filled pill (counts are muted tabular text: \"Inbox 12\")"), m.start(), m.group(0)[-40:])
        # #33: icons in colored circles, row after row.
        circles = [m.start() for m in ANY_CLASS.finditer(text) if ICON_CIRCLE.search(m.group(1))]
        if len(circles) >= 3:
            add(("icon-circle", "#33", "Icons in colored circles on every row (one icon style; shapes only in empty states)"), circles[0], f"{len(circles)} tinted circles")


# Custom properties across the scanned files: a var(--name) nobody defines falls back in
# silence (after a rename, a merge, a typo). Only when some token is defined in scope.
TOKEN_DEF = re.compile(r"(?<![\w-])(--[\w-]+)\s*:|setProperty\(\s*[\"'](--[\w-]+)|[\"'](--[\w-]+)[\"']\s*:")
TOKEN_USE = re.compile(r"var\(\s*(--[\w-]+)\s*\)")  # a var() with a fallback is deliberate


def token_checks(paths, hits):
    defined, uses = set(), []
    for path in paths:
        if os.path.splitext(path)[1].lower() not in WEB or path.endswith((".min.js", ".min.css")):
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if len(text) > 2_000_000:  # same limits as scan(): bundles aren't ours to judge
            continue
        defined |= {a or b or c for a, b, c in TOKEN_DEF.findall(text)}
        for n, line in enumerate(text.splitlines(), 1):
            if "unslop-ignore" not in line:
                uses += [(path, n, m.group(1)) for m in TOKEN_USE.finditer(line)]
    project_checks(paths, hits)
    if not defined:
        return  # the token file isn't in what was scanned: nothing to compare against
    key = ("undefined-token", "#1", "Token used but defined nowhere in the scanned files")
    for path, n, name in uses:
        if name not in defined:
            hits.setdefault(key, []).append((path, n, f"var({name})"))


# Across the scanned web files (#62, #63): a dark theme with no color-scheme anywhere, and
# keyframe animations with no reduced-motion alternative anywhere.
DARK_THEME = re.compile(r"prefers-color-scheme\s*:\s*dark|\[data-theme=[\"']?dark|\bdark:[a-z]")
COLOR_SCHEME = re.compile(r"(?<![-\w])color-scheme\s*:|name=[\"']color-scheme[\"']|\bcolorScheme\s*:")
ANIMATION = re.compile(r"@keyframes\s+[\w-]+|\banimate-(?:spin|ping|pulse|bounce|\[)")
REDUCED_MOTION = re.compile(r"prefers-reduced-motion|\bmotion-(?:reduce|safe):|useReducedMotion|reducedMotion")


def project_checks(paths, hits):
    dark = anim = None
    has_scheme = has_reduced = False
    for path in paths:
        if os.path.splitext(path)[1].lower() not in WEB or path.endswith((".min.js", ".min.css")):
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if len(text) > 2_000_000:
            continue
        lines = text.splitlines()

        def first(rx):
            for n, line in enumerate(lines, 1):
                if "unslop-ignore" not in line and rx.search(line):
                    return (path, n, rx.search(line).group(0))
            return None
        dark = dark or first(DARK_THEME)
        anim = anim or first(ANIMATION)
        has_scheme = has_scheme or bool(COLOR_SCHEME.search(text))
        has_reduced = has_reduced or bool(REDUCED_MOTION.search(text))
    if dark and not has_scheme:
        hits.setdefault(("no-color-scheme", "#62", "A dark theme with no color-scheme (form controls and scrollbars stay light)"), []).append(dark)
    if anim and not has_reduced:
        hits.setdefault(("no-reduced-motion", "#63", "Animations with no prefers-reduced-motion alternative"), []).append(anim)


# A written project decision can allow a taste rule (a base-6 grid, tracked caps as the
# brand's signature). It can't allow the floors: contrast and visible focus and target size
# (accessibility, principle 5) and invented claims (principle 6). Shared with unslop-score.py.
NEVER_ALLOW = {"contrast", "graphics-contrast", "focus", "no-focus", "targets", "unverified-claim"}


def parse_allow(value):
    allow = {r.strip() for r in (value or "").split(",") if r.strip()}
    refused = allow & NEVER_ALLOW
    if refused:
        sys.exit(f"--allow can't include {', '.join(sorted(refused))}: contrast, focus, target size and invented "
                 f"claims are floors (accessibility, principles 5 and 6), not taste. Report them as blockers "
                 f"with the measured value instead.")
    return allow


CONTEXT = ".unslop/context.md"
CONTEXT_KEY = re.compile(r"^\s*[-*]?\s*(scale|type-scale|allow):\s*`?([\w.,\s-]+?)`?\s*$", re.M)


def read_context(path=None):
    """The machine-read lines of .unslop/context.md (scale, type-scale, allow), {} if there is none."""
    path = path or CONTEXT
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return {}
    return {k: v.replace(" ", "") for k, v in CONTEXT_KEY.findall(text)}


def resolve_options(a):
    """Command-line flags win; then the project's .unslop/context.md; then the defaults."""
    ctx = {} if getattr(a, "no_context", False) else read_context(getattr(a, "context", None))
    a.scale = a.scale or ctx.get("scale") or DEFAULT_SCALE
    a.type_scale = a.type_scale or ctx.get("type-scale")
    a.allow = a.allow if a.allow is not None else ctx.get("allow")
    return ctx


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


# Code samples and at-rule conditions aren't UI copy or layout (straight-quotes, fixed-width).
CODE_SPAN = re.compile(r"<(code|pre|kbd|samp)\b[^>]*>.*?</\1>", re.S)


def mask_code(line, in_pre):
    """The line without code: what a multi-line <pre> still holds, inline <code>/<pre>/<kbd>/<samp>
    spans, and an unclosed <pre> to the end of the line. Returns (masked line, inside <pre> after it)."""
    if in_pre:
        end = line.find("</pre>")
        if end == -1:
            return "", True
        line = line[end + len("</pre>"):]
    line = CODE_SPAN.sub("", line)
    start = line.find("<pre")
    if start != -1:
        return line[:start], True
    return line, False

AT_RULE_PRELUDE = re.compile(r"@(?:media|container|supports)\b[^{]*")
DEFAULT_SCALE = "0,1,2,4,8,12,16,20,24,32,40,48,64,80,96"
DEFAULT_TYPE_SCALE = {11, 12, 13, 14, 15, 16, 17, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 40, 44, 48, 56, 64, 72, 80, 96}
# Colored shadows in CSS, any offset: "0 10px 30px rgba(255,107,107,.45)" is a glow too (#32).
SHADOW_DECL = re.compile(r"box-shadow\s*:\s*([^;}]+)", re.I)
SHADOW_COLOR = re.compile(r"rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)(?:[\s,/]+([\d.]+%?))?\s*\)|#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def colored_shadow(value):
    for m in SHADOW_COLOR.finditer(value):
        if m.group(5):
            h = m.group(5)
            h = "".join(c * 2 for c in h) if len(h) == 3 else h
            r, g, b, a = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0
        else:
            r, g, b = (int(m.group(i)) for i in (1, 2, 3))
            a = m.group(4)
            a = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
        if max(r, g, b) - min(r, g, b) > 40 and a >= 0.2:
            return m.group(0)
    return None


def scan(path, scale, hits, type_scale=None):
    type_scale = type_scale or DEFAULT_TYPE_SCALE
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
    in_pre = False
    for n, line in enumerate(text.splitlines(), 1):
        copy_line, in_pre = mask_code(line, in_pre)
        if "unslop-ignore" in line:
            continue
        stripped = line.strip()
        if (stripped.startswith(":root") or "@theme" in stripped) and stripped.count("{") > stripped.count("}"):
            in_root = True  # a block that stays open; a one-line ":root { … }" closes itself
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
            if rid == "raw-color" and not rx.search(TOKEN_DECL.sub("", line)):
                continue  # only token definitions (e.g. a dark palette inside @media … { :root { … } })
            if rid == "no-focus" and has_focus_visible:
                continue
            if rid in ("native-literal", "elevation-literal") and is_token_file:
                continue  # Tokens.kt / Type.kt / Theme.swift: literals belong there
            target = line
            if rid == "straight-quotes":
                target = copy_line  # code samples keep their straight quotes
            elif rid == "fixed-width":
                target = AT_RULE_PRELUDE.sub("", line)  # @media (min-width: 768px) is a breakpoint, not a width
            if rx.search(target):
                hits.setdefault((rid, ref, desc), []).append((path, n, stripped[:110]))
        if kind == "web":
            glow_key = next((r[0], r[1], r[2]) for r in RULES if r[0] == "glow")
            already = any(w[0] == path and w[1] == n for w in hits.get(glow_key, []))
            for m in SHADOW_DECL.finditer(line):
                c = colored_shadow(m.group(1))
                if c and not already:
                    hits.setdefault(glow_key, []).append((path, n, f"box-shadow with {c}"))
                    already = True
        if kind == "web" and not is_token_file and not in_root:
            for m in PX_PROP.finditer(line):
                if "var(" in m.group(3) or "calc(" in m.group(3):
                    continue
                prop = m.group(1).lower()
                if prop == "font-size":       # type has its own scale (#2), not the spacing one
                    allowed = type_scale
                elif prop == "border-radius":  # a capsule or circle (999px) is "full", not a step
                    allowed = scale | {v for v in map(float, PX.findall(m.group(3))) if abs(v) >= 100}
                else:
                    allowed = scale
                off = [v for v in PX.findall(m.group(3)) if abs(float(v)) not in allowed]
                if off:
                    key = ("off-scale", "#1", "Spacing / type / radius value off the scale")
                    hits.setdefault(key, []).append((path, n, f"{m.group(1)}{m.group(2) or ''}: {', '.join(o + 'px' for o in off)}"))


# Rules that run on whole files or blocks rather than line regexes: (id, ref, description).
FILE_RULES = [
    ("off-scale", "#1", "Spacing / type / radius value off the scale"),
    ("stock-kit", "#6", "Starter kit left at its defaults (set radius, grays and accent from the product)"),
    ("card-sameness", "#40 #65", "Same card repeated with a number inside (a row of stat tiles?)"),
    ("hidden-nav", "#57", "Nav links hidden on phones with no menu button"),
    ("unverified-claim", "#64", "Social proof or metric to source (\"Trusted by 10,000+ teams\", \"10x faster\") — is it real?"),
    ("canvas-tabbar", "#59", "Map or camera with a permanent tab bar under it (let the chrome float)"),
    ("undefined-token", "#1", "Token used but defined nowhere in the scanned files"),
    ("side-stripe", "#60", "Colored side stripe on a rounded card (does the stripe encode a status?)"),
    ("hard-shadow", "#66", "Hard offset shadow (no blur): a costume unless the brand is neobrutalist"),
    ("bounce-easing", "#67", "Bouncy or elastic easing (ease out, don't overshoot)"),
    ("ghost-card", "#68", "1px border and a soft shadow on the same card (pick one separator)"),
    ("mono-disguise", "#69", "Monospace on headings or the whole page (code faces are for code and data)"),
    ("multiple-h1", "#13", "More than one h1 on the page (section titles are labels, not h1)"),
    ("section-numbers", "#60", "Sections numbered 01 / 02 / 03 (does the order carry information?)"),
    ("count-pill", "#50", "A count in a filled pill (counts are muted tabular text: \"Inbox 12\")"),
    ("icon-circle", "#33", "Icons in colored circles on every row (one icon style; shapes only in empty states)"),
    ("no-color-scheme", "#62", "A dark theme with no color-scheme (form controls and scrollbars stay light)"),
    ("no-reduced-motion", "#63", "Animations with no prefers-reduced-motion alternative"),
]


def all_rules():
    return [(r[0], r[1], r[2], r[4]) for r in RULES] + [(i, ref, d, "web" if i in ("hidden-nav", "side-stripe", "hard-shadow",
            "bounce-easing", "ghost-card", "mono-disguise", "off-scale", "undefined-token", "multiple-h1", "section-numbers",
            "count-pill", "icon-circle", "no-color-scheme", "no-reduced-motion") else "all") for i, ref, d in FILE_RULES]


def gh_escape(s):
    return str(s).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--scale", help=f"allowed px values (1 for hairlines); match your tokens. Default: {DEFAULT_SCALE}")
    ap.add_argument("--type-scale", help="allowed font sizes in px; match your type tokens")
    ap.add_argument("--context", metavar="FILE", help=f"project context to read (default {CONTEXT} if present)")
    ap.add_argument("--no-context", action="store_true", help=f"ignore {CONTEXT}")
    ap.add_argument("--max", type=int, default=8, help="locations shown per rule")
    ap.add_argument("--strict", action="store_true", help="exit 1 if anything is found")
    ap.add_argument("--allow", metavar="RULES",
                    help="rule ids a written project decision allows (e.g. tracked-caps,off-scale); "
                         "listed apart, not counted. Never contrast or invented claims")
    ap.add_argument("--json", action="store_true", help="machine-readable hits (every location, no cap)")
    ap.add_argument("--github", action="store_true",
                    help="also print GitHub Actions annotations (::warning file=…,line=…) for every hit")
    ap.add_argument("--list-rules", action="store_true", help="print every rule id with its fix number and exit")
    a = ap.parse_args()
    if a.list_rules:
        for rid, ref, desc, applies in all_rules():
            print(f"{rid:<18} {ref:<8} {applies:<6} {desc}")
        return 0
    ctx = resolve_options(a)
    allow = parse_allow(a.allow)
    scale = {float(x) for x in a.scale.split(",")}
    type_scale = {float(x) for x in a.type_scale.split(",")} if a.type_scale else DEFAULT_TYPE_SCALE
    hits, count, seen = {}, 0, []
    for f in files(a.paths):
        count += 1
        seen.append(f)
        scan(f, scale, hits, type_scale)
    token_checks(seen, hits)
    allowed = {k: v for k, v in hits.items() if k[0] in allow}
    hits = {k: v for k, v in hits.items() if k[0] not in allow}
    if a.github:
        for (rid, ref, desc), where in sorted(hits.items()):
            for path, n, snippet in where:
                print(f"::warning file={gh_escape(path).replace(',', '%2C').replace(':', '%3A')},line={n},title=unslop {ref} {rid}::{gh_escape(desc)}")
    if a.json:
        import json
        print(json.dumps({"files": count,
                          "hits": [{"rule": rid, "ref": ref, "description": desc, "file": path, "line": n, "snippet": snip}
                                   for (rid, ref, desc), where in sorted(hits.items()) for path, n, snip in where],
                          "allowed": {k[0]: len(v) for k, v in sorted(allowed.items())}}, indent=2, ensure_ascii=False))
        return 1 if a.strict and hits else 0
    print(f"unslop scan: {count} files" + (f"  (context: {a.context or CONTEXT})" if ctx else ""))
    if allowed:
        print("allowed by the project (--allow): " + ", ".join(f"{k[0]} ×{len(v)}" for k, v in sorted(allowed.items())))
    if not hits:
        print("nothing found")
        return 0
    order = [r[0] for r in RULES] + [r[0] for r in FILE_RULES]
    for (rid, ref, desc), where in sorted(hits.items(), key=lambda kv: (-len(kv[1]), order.index(kv[0][0]))):
        print(f"\n[{ref}] {desc} — {len(where)} hit(s)")
        for path, n, snippet in where[: a.max]:
            print(f"  {path}:{n}  {snippet}")
        if len(where) > a.max:
            print(f"  … {len(where) - a.max} more")
    return 1 if a.strict else 0


if __name__ == "__main__":
    sys.exit(main())
