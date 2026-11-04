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

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆↔-↪⌚-⏿]")
PX_PROP = re.compile(r"\b(padding|margin|gap|row-gap|column-gap|font-size|border-radius|inset|top|left|right|bottom)"
                     r"(-[a-z]+)?\s*:\s*([^;}{]+)", re.I)
PX = re.compile(r"(-?\d+(?:\.\d+)?)px")

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
    ("greeting", "#26", "Greeting as a title (name what the screen is)",
     re.compile(r"\b(Welcome back|Hey there|Hello there|Good (morning|afternoon|evening)),?\b", re.I), "all"),
    ("transition-all", "#63", "transition: all (animate transform and opacity, named)",
     re.compile(r"transition\s*:\s*all\b|transition-property\s*:\s*all\b|\btransition-all\b"), "web"),
    ("tracked-caps", "#45 #60", "Small tracked all-caps label (eyebrow/kicker) — does it carry information?",
     re.compile(r"\buppercase\b[^\"'\n]*\btracking-(wide|wider|widest)\b|\btracking-(wide|wider|widest)\b[^\"'\n]*\buppercase\b|"
                r"text-transform\s*:\s*uppercase|\.textCase\(\.uppercase\)|\.uppercase\(\)"), "all"),
    ("three-dots", "#61", "Three dots in UI text (use the … character)",
     re.compile(r"[\"'>`][^\"'<`\n]*[A-Za-z]\.\.\.(?=[\"'<`\s])"), "all"),
    ("hype-copy", "#64", "Hype copy (say what it does, with a number if there is one)",
     re.compile(r"[\"'>`][^\"'<`\n]*\b(Supercharge|Unleash|Revolutioni[sz]e|Seamless(ly)?|Effortless(ly)?|Game-changing|"
                r"Cutting-edge|Next-level|Elevate your|Transform your|Take your \w+ to the next level)\b"), "all"),
    ("no-focus", "#53", "Focus outline removed — is there a :focus-visible style?",
     re.compile(r"outline\s*:\s*(none|0)\b|\boutline-none\b|focus:outline-none"), "web"),
]


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
    order = [r[0] for r in RULES] + ["off-scale"]
    for (rid, ref, desc), where in sorted(hits.items(), key=lambda kv: (-len(kv[1]), order.index(kv[0][0]))):
        print(f"\n[{ref}] {desc} — {len(where)} hit(s)")
        for path, n, snippet in where[: a.max]:
            print(f"  {path}:{n}  {snippet}")
        if len(where) > a.max:
            print(f"  … {len(where) - a.max} more")
    return 1 if a.strict else 0


if __name__ == "__main__":
    sys.exit(main())
