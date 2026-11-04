#!/usr/bin/env python3
"""One number for how unslopped a UI is: 100 = clean, 0 = every tic at once.

    python3 scripts/unslop-score.py [paths…] [--audit unslop-audit/report.json]
                                    [--scale …] [--json] [--min 80]

Scores the source with the same rules as `slop-scan.py` and, if you pass a
`web-audit.mjs` report, the rendered page too (scroll, contrast, focus,
targets, how many distinct values the page really uses). Each kind of slop
costs points per hit up to a cap, so the score says how many *kinds* of slop
are left more than how big the codebase is. Prints the breakdown and a
README badge. With --min it exits 1 below that score (pre-commit hook).

It is a smoke alarm, not a judge: a 95 can still have a flat hierarchy,
and a gradient you chose on purpose costs points anyway (silence that line
with `unslop-ignore`). Standard library only.
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# id: (label, checklist ref, points per hit, cap)
CODE = {
    "gradient-text": ("Gradient text", "#55", 6, 12),
    "glow": ("Colored glows", "#32", 4, 12),
    "no-focus": ("Focus outline removed", "#53", 8, 8),
    "greeting": ("Greeting as title", "#26", 5, 5),
    "emoji": ("Emoji in the UI", "#33", 2, 10),
    "ai-palette": ("Default purple palette", "#19", 2, 10),
    "gradient": ("Gradient fills", "#30", 2, 8),
    "shouting": ("Exclamation marks", "#52", 3, 6),
    "blur-content": ("Backdrop blur", "#46", 2, 6),
    "raw-color": ("Raw colors outside tokens", "#3", 0.5, 8),
    "arbitrary-value": ("Tailwind arbitrary values", "#1", 0.5, 8),
    "off-scale": ("Values off the spacing scale", "#1", 0.5, 8),
    "native-literal": ("Literals in native views", "#1", 0.5, 8),
}
# Rendered page. "sprawl" = distinct values beyond what a system needs.
PAGE = {
    "overflow": ("Horizontal scroll", "#57", 5, 10),
    "contrast": ("Text under WCAG AA", "P5", 1, 15),
    "focus": ("No visible focus", "#53", None, 10),
    "targets": ("Targets under 24 px", "#53", 0.5, 5),
    "spacing-sprawl": ("Distinct spacing values > 8", "#1", 0.5, 8),
    "size-sprawl": ("Distinct font sizes > 6", "#2", 1, 6),
    "weight-sprawl": ("Distinct weights > 3", "#2", 2, 4),
    "radius-sprawl": ("Distinct radii > 4", "#5", 1, 4),
    "shadow-sprawl": ("Distinct shadows > 3", "#5", 1, 4),
}
# Seen both in code and on the page: count the worse of the two, not both.
SHARED = {"emoji": "emoji", "gradientText": "gradient-text", "glow": "glow"}


def load_scanner():
    spec = importlib.util.spec_from_file_location("slop_scan", os.path.join(HERE, "slop-scan.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cost(n, per, cap):
    return min(cap, n * per) if n else 0


def score_code(paths, scale):
    scan = load_scanner()
    hits, files = {}, 0
    for f in scan.files(paths):
        files += 1
        scan.scan(f, scale, hits)
    counts = {rid: len(where) for (rid, _ref, _desc), where in hits.items()}
    return files, counts


def score_page(report):
    m, rows = report["measure"], {}
    c = m["census"]
    rows["overflow"] = sum(1 for w in report["widths"].values() if w["overflow"]["scrollWidth"] > w["overflow"]["viewport"])
    rows["contrast"] = len(m["contrastFails"])
    rows["targets"] = len(m["smallTargets"])
    rows["spacing-sprawl"] = max(0, len(c["spacing"]) - 8)
    rows["size-sprawl"] = max(0, len(c["fontSizes"]) - 6)
    rows["weight-sprawl"] = max(0, len(c["fontWeights"]) - 3)
    rows["radius-sprawl"] = max(0, len(c["radii"]) - 4)
    rows["shadow-sprawl"] = max(0, len(c["shadows"]) - 3)
    focus = report.get("focus") or {}
    shared = {SHARED[k]: len(m.get(k, [])) for k in SHARED}
    return rows, focus, shared


def verdict(score):
    if score >= 90:
        return "clean", "brightgreen"
    if score >= 75:
        return "a few tics", "green"
    if score >= 50:
        return "sloppy", "yellow"
    return "slop", "red"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="source to scan (default: . unless only --audit is given)")
    ap.add_argument("--audit", help="report.json written by web-audit.mjs")
    ap.add_argument("--scale", default="0,1,2,4,8,12,16,20,24,32,40,48,64,80,96")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--min", type=float, help="exit 1 below this score")
    a = ap.parse_args()
    paths = a.paths or ([] if a.audit else ["."])
    lines, total = [], 0.0

    code_counts, files = {}, 0
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        sys.exit(f"no such path: {', '.join(missing)}")
    if paths:
        files, code_counts = score_code(paths, {float(x) for x in a.scale.split(",")})
        if not files and not a.audit:
            sys.exit(f"no UI source files under {', '.join(paths)}: nothing to score")
    page_rows, focus, shared = {}, {}, {}
    if a.audit:
        try:
            with open(a.audit, encoding="utf-8") as fh:
                page_rows, focus, shared = score_page(json.load(fh))
        except (OSError, ValueError, KeyError) as e:
            sys.exit(f"can't read the audit report {a.audit}: {e}. Run scripts/web-audit.mjs first.")

    for rid, (label, ref, per, cap) in CODE.items():
        n = max(code_counts.get(rid, 0), shared.get(rid, 0))
        p = cost(n, per, cap)
        if p:
            lines.append((p, f"[{ref}] {label}", n))
            total += p
    for rid, (label, ref, per, cap) in PAGE.items():
        if rid == "focus":
            checked, missing = focus.get("checked", 0), len(focus.get("missing", []))
            p = round(cap * missing / checked, 1) if checked else 0
            n = f"{missing}/{checked}"
        else:
            n = page_rows.get(rid, 0)
            p = cost(n, per, cap)
        if p:
            lines.append((p, f"[{ref}] {label}", n))
            total += p

    score = max(0, round(100 - total))
    word, color = verdict(score)
    badge = f"https://img.shields.io/badge/unslop_score-{score}%2F100-{color}"
    lines.sort(key=lambda x: -x[0])
    if a.json:
        print(json.dumps({"score": score, "verdict": word, "files": files, "audit": bool(a.audit), "badge": badge,
                          "penalties": [{"rule": r, "count": n, "points": p} for p, r, n in lines]}, indent=2))
    else:
        src = []
        if paths:
            src.append(f"{files} source file{'' if files == 1 else 's'}")
        if a.audit:
            src.append("rendered page")
        print(f"unslop score: {score}/100 — {word}  ({' + '.join(src)})")
        if lines:
            print("\nWhere the points went (fix the top rows first):")
            for p, rule, n in lines:
                print(f"  -{p:>4g}  {rule}  ({n})")
        print(f"\nBadge: [![unslop score]({badge})](https://github.com/marcosnovo/unslop-design)")
    return 1 if a.min is not None and score < a.min else 0


if __name__ == "__main__":
    sys.exit(main())
