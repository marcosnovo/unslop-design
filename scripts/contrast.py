#!/usr/bin/env python3
"""WCAG contrast of a text or icon color on a background, measured, not assumed.

    python3 scripts/contrast.py <foreground> <background> [<more backgrounds>…]

Colors as #rgb, #rrggbb, #rrggbbaa, rgb(…) or rgba(…). A translucent
foreground is composited over each background first, the way it renders.
For text on a gradient or a photo, pass its lightest and darkest colors:
the worst one is the ratio. Native colors work the same: SwiftUI
Color(red:green:blue:) and Compose Color(0xFFrrggbb) are hex values too.

    $ python3 scripts/contrast.py '#ffffff' '#3ddc84'
    #ffffff on #3ddc84: 1.78:1  fails text (4.5), large text (3), icons (3)

Exit code 1 if any pair is under 4.5:1 (or under --min). Standard library only.
"""
import argparse
import re
import sys


def parse(color):
    c = color.strip().lower()
    if c.startswith("0xff") and len(c) == 10:  # Compose Color(0xFFrrggbb)
        c = "#" + c[4:]
    m = re.fullmatch(r"#?([0-9a-f]{3,8})", c)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        if len(h) not in (6, 8):
            raise ValueError(color)
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return r, g, b, a
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)(?:[\s,/]+([\d.]+%?))?\s*\)", c)
    if m:
        r, g, b = (float(m.group(i)) for i in (1, 2, 3))
        a = m.group(4)
        a = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
        return r, g, b, a
    raise ValueError(color)


def over(fg, bg):
    """fg composited over an opaque bg."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1.0,)


def luminance(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    l1, l2 = sorted((luminance(over(fg, bg)), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("foreground")
    ap.add_argument("backgrounds", nargs="+")
    ap.add_argument("--min", type=float, default=4.5, help="exit 1 under this ratio (default 4.5, body text)")
    a = ap.parse_args()
    try:
        fg = parse(a.foreground)
        bgs = [parse(b) for b in a.backgrounds]
    except ValueError as e:
        sys.exit(f"can't read the color {e}: use #rrggbb, #rrggbbaa, rgb(…) or rgba(…)")
    worst = None
    for raw, bg in zip(a.backgrounds, bgs):
        if bg[3] < 1:
            sys.exit(f"the background {raw} is translucent: pass the color it renders as (composite it first)")
        r = ratio(fg, bg)
        worst = r if worst is None else min(worst, r)
        passes = [name for name, need in (("text", 4.5), ("large text", 3), ("icons", 3)) if r >= need]
        fails = [f"{name} ({need:g})" for name, need in (("text", 4.5), ("large text", 3), ("icons", 3)) if r < need]
        verdict = ("passes " + ", ".join(passes)) if not fails else ("fails " + ", ".join(fails))
        print(f"{a.foreground} on {raw}: {r:.2f}:1  {verdict}")
    if len(bgs) > 1:
        print(f"worst: {worst:.2f}:1")
    return 1 if worst < a.min else 0


if __name__ == "__main__":
    sys.exit(main())
