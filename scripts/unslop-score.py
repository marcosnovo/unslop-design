#!/usr/bin/env python3
"""One number for how unslopped a UI is: 100 = clean, 0 = every tic at once.

    python3 scripts/unslop-score.py [paths…] [--audit unslop-audit/report.json]
                                    [--scale …] [--json | --markdown] [--min 80]
                                    [--save [.unslop]] [--baseline base.json]

Scores the source with the same rules as `slop-scan.py` and, if you pass a
`web-audit.mjs` report, the rendered page too (scroll, contrast, focus,
targets, how many distinct values the page really uses). Each kind of slop
costs points per hit up to a cap, so the score says how many *kinds* of slop
are left more than how big the codebase is. Prints the breakdown and a
README badge. With --min it exits 1 below that score (pre-commit hook).
With --save it appends the run to .unslop/history.json and prints the
trend ("score 41 → 88 → 91"); --markdown prints a table for a PR comment or
a GitHub Actions job summary. --baseline compares with an earlier --json
run (the base branch in a PR): "score 72 → 81 (+9)", what got better and what
got worse.

It is a smoke alarm, not a judge: a 95 can still have a flat hierarchy,
and a gradient you chose on purpose costs points anyway (silence that line
with `unslop-ignore`). Standard library only.
"""
import argparse
import importlib.util
import json
import datetime
import os
import subprocess
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
    "exclaim": ("Exclamation in UI text", "#25", 1, 4),
    "title-case": ("Title Case in UI text", "#25", 0.5, 3),
    "blur-content": ("Backdrop blur", "#46", 2, 6),
    "transition-all": ("transition: all", "#63", 2, 6),
    "hype-copy": ("Hype copy", "#64", 2, 6),
    "unverified-claim": ("Unsourced social proof / metrics", "#64", 2, 6),
    "pressure": ("Pressure copy (countdowns, scarcity, badges)", "#64", 2, 6),
    "hidden-nav": ("Nav hidden on phones", "#57", 3, 3),
    "undefined-token": ("Tokens used but never defined", "#1", 2, 6),
    "canvas-tabbar": ("Tab bar over a map or camera", "#59", 1, 2),
    "tracked-caps": ("Tracked caps labels", "#45", 1, 4),
    "stock-kit": ("Starter kit at its defaults", "#6", 3, 3),
    "card-sameness": ("Repeated stat cards", "#65", 1, 3),
    "three-dots": ("Three dots instead of …", "#61", 1, 3),
    "raw-color": ("Raw colors outside tokens", "#3", 0.5, 8),
    "arbitrary-value": ("Tailwind arbitrary values", "#1", 0.5, 8),
    "off-scale": ("Values off the spacing scale", "#1", 0.5, 8),
    "native-literal": ("Literals in native views", "#1", 0.5, 8),
    "elevation-literal": ("Elevation literals on components", "#5", 1, 3),
    "translucent-text": ("Semi-transparent white text", "#22", 1, 4),
    "empty-action": ("Controls with an empty action", "#64", 2, 6),
    "side-stripe": ("Side stripes on rounded cards", "#60", 1, 3),
    "hard-shadow": ("Hard offset shadows", "#66", 1, 3),
    "bounce-easing": ("Bouncy or elastic easing", "#67", 1, 3),
    "ghost-card": ("Border and shadow on one card", "#68", 1, 4),
    "mono-disguise": ("Monospace headings or body", "#69", 2, 4),
    "plural-hack": ("\"item(s)\" plurals", "#71", 1, 3),
    "justified-text": ("Justified text", "#28", 1, 3),
    "extreme-tracking": ("Crushed letter-spacing", "#29", 1, 3),
    "fixed-width": ("Fixed widths of 400px+", "#57", 2, 6),
    "lorem": ("Lorem ipsum", "#48", 3, 6),
    "placeholder-image": ("Placeholder images", "#48", 2, 6),
    "bare-delta": ("Deltas with no baseline", "#52", 1, 4),
    "straight-quotes": ("Straight quotes in copy", "#61", 0.5, 3),
    "multiple-h1": ("More than one h1", "#13", 2, 2),
    "section-numbers": ("Sections numbered 01/02/03", "#60", 1, 1),
    "count-pill": ("Counts in filled pills", "#50", 1, 4),
    "icon-circle": ("Icons in colored circles", "#33", 1, 2),
    "no-color-scheme": ("Dark theme without color-scheme", "#62", 2, 2),
    "no-reduced-motion": ("Animation without reduced motion", "#63", 3, 3),
}
# Rendered page. "sprawl" = distinct values beyond what a system needs.
PAGE = {
    "overflow": ("Horizontal scroll", "#57", 5, 10),
    "contrast": ("Text under WCAG AA", "P5", 1, 15),
    "graphics-contrast": ("Icons/graphics under 3:1", "P5", 1, 6),
    "text-scale": ("Type ignores the reader's text size", "#2", 3, 3),
    "long-lines": ("Lines over ~85 characters", "#27", 1, 4),
    "aligned-text": ("Long text justified or centered", "#28", 1, 3),
    "empty-block": ("Empty placeholder blocks", "#35", 2, 4),
    "tiny-text": ("Text drawn under 11 px", "#2", 1, 4),
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


def score_code(paths, scale, type_scale=None):
    scan = load_scanner()
    hits, files, seen = {}, 0, []
    for f in scan.files(paths):
        files += 1
        seen.append(f)
        scan.scan(f, scale, hits, type_scale)
    scan.token_checks(seen, hits)
    counts = {rid: len(where) for (rid, _ref, _desc), where in hits.items()}
    return files, counts


def score_page(report):
    m, rows = report["measure"], {}
    c = m["census"]
    rows["overflow"] = sum(1 for w in report["widths"].values() if w["overflow"]["scrollWidth"] > w["overflow"]["viewport"])
    rows["contrast"] = len(m["contrastFails"])
    rows["graphics-contrast"] = len(m.get("graphicsFails", []))
    rows["long-lines"] = len(m.get("longLines", []))
    rows["aligned-text"] = len(m.get("alignedText", []))
    rows["empty-block"] = len(m.get("emptyBlocks", []))
    rows["tiny-text"] = max([len(w.get("tinyText", [])) for w in report["widths"].values()] or [0])
    ts = report.get("textScale") or {}
    rows["text-scale"] = 1 if ts.get("checked") and ts.get("grew", 0) / ts["checked"] < 0.5 else 0
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


def save_run(folder, run):
    """Append this run to <folder>/history.json; return the scores so far, oldest first."""
    path = os.path.join(folder, "history.json")
    try:
        with open(path, encoding="utf-8") as fh:
            history = json.load(fh)
    except (OSError, ValueError):
        history = []
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                                timeout=5).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        commit = None
    history.append({"date": datetime.datetime.now().isoformat(timespec="seconds"), "commit": commit, **run})
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(history[-200:], fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return [h["score"] for h in history]


def compare(base, score, lines):
    """Score delta and per-row changes against an earlier --json output."""
    before = {r["rule"]: (r["count"], r["points"]) for r in base.get("penalties", [])}
    now = {r: (n, p) for p, r, n in lines}
    better, worse = [], []
    for rule in sorted(set(before) | set(now)):
        (bn, bp), (nn, np_) = before.get(rule, (0, 0)), now.get(rule, (0, 0))
        if np_ < bp:
            better.append({"rule": rule, "from": bn, "to": nn, "points": round(bp - np_, 1)})
        elif np_ > bp:
            worse.append({"rule": rule, "from": bn, "to": nn, "points": round(np_ - bp, 1)})
    better.sort(key=lambda x: -x["points"])
    worse.sort(key=lambda x: -x["points"])
    return {"score": base["score"], "delta": score - base["score"], "better": better, "worse": worse}


def signed(n):
    return f"+{n:g}" if n > 0 else f"{n:g}" if n < 0 else "±0"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="source to scan (default: . unless only --audit is given)")
    ap.add_argument("--audit", help="report.json written by web-audit.mjs")
    ap.add_argument("--scale", help="allowed px values (default: the project context, else slop-scan's)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--markdown", action="store_true", help="a Markdown table (PR comment, Actions job summary)")
    ap.add_argument("--save", nargs="?", const=".unslop", metavar="DIR",
                    help="append this run to DIR/history.json (default .unslop) and show the trend")
    ap.add_argument("--min", type=float, help="exit 1 below this score")
    ap.add_argument("--baseline", metavar="JSON", help="an earlier --json output to compare with (e.g. the base branch)")
    ap.add_argument("--baseline-label", default="baseline", metavar="NAME", help="what to call it (e.g. main)")
    ap.add_argument("--type-scale", help="allowed font sizes in px (default: the project context, else slop-scan's)")
    ap.add_argument("--context", metavar="FILE", help="project context to read (default .unslop/context.md if present)")
    ap.add_argument("--no-context", action="store_true", help="ignore .unslop/context.md")
    ap.add_argument("--allow", metavar="RULES",
                    help="rule ids a written project decision allows; not scored, listed apart. "
                         "Never contrast, graphics-contrast or unverified-claim")
    a = ap.parse_args()
    scanner = load_scanner()
    ctx = scanner.resolve_options(a)
    allow = scanner.parse_allow(a.allow)
    paths = a.paths or ([] if a.audit else ["."])
    lines, total = [], 0.0

    code_counts, files = {}, 0
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        sys.exit(f"no such path: {', '.join(missing)}")
    if paths:
        files, code_counts = score_code(paths, {float(x) for x in a.scale.split(",")},
                                        {float(x) for x in a.type_scale.split(",")} if a.type_scale else None)
        if not files and not a.audit:
            sys.exit(f"no UI source files under {', '.join(paths)}: nothing to score")
    page_rows, focus, shared = {}, {}, {}
    if a.audit:
        try:
            with open(a.audit, encoding="utf-8") as fh:
                page_rows, focus, shared = score_page(json.load(fh))
        except (OSError, ValueError, KeyError) as e:
            sys.exit(f"can't read the audit report {a.audit}: {e}. Run scripts/web-audit.mjs first.")

    allowed = []
    for rid, (label, ref, per, cap) in CODE.items():
        n = max(code_counts.get(rid, 0), shared.get(rid, 0))
        if rid in allow:
            if n:
                allowed.append(f"{rid} ×{n}")
            continue
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
            if rid in allow:
                if n:
                    allowed.append(f"{rid} ×{n}")
                continue
            p = cost(n, per, cap)
        if p:
            lines.append((p, f"[{ref}] {label}", n))
            total += p

    score = max(0, round(100 - total))
    word, color = verdict(score)
    badge = f"https://img.shields.io/badge/unslop_score-{score}%2F100-{color}"
    lines.sort(key=lambda x: -x[0])
    trend = None
    if a.save:
        scores = save_run(a.save, {"score": score, "files": files, "audit": bool(a.audit), "allowed": allowed,
                                   "penalties": [{"rule": r, "count": n, "points": p} for p, r, n in lines]})
        trend = " → ".join(str(s) for s in scores[-5:])
    cmp_ = None
    if a.baseline:
        try:
            with open(a.baseline, encoding="utf-8") as fh:
                cmp_ = compare(json.load(fh), score, lines)
        except (OSError, ValueError, KeyError) as e:
            sys.exit(f"can't read the baseline {a.baseline}: {e}. It is the --json output of an earlier run.")
    if a.markdown:
        if cmp_:
            out = [f"### unslop score: {score}/100 ({signed(cmp_['delta'])} vs {a.baseline_label})", "",
                   f"{a.baseline_label} {cmp_['score']} → this change {score}", ""]
            for title, rows, sign in (("Worse", cmp_["worse"], "-"), ("Better", cmp_["better"], "+")):
                if rows:
                    out.append(f"**{title}**")
                    out += [f"- {r['rule']}: {r['from']} → {r['to']} ({sign}{r['points']:g})" for r in rows]
                    out.append("")
            if not cmp_["better"] and not cmp_["worse"]:
                out += ["No change in any row.", ""]
            if lines:
                out += ["<details><summary>Every row now</summary>", ""]
        else:
            out = [f"### unslop score: {score}/100 ({word})", ""]
        if trend and "→" in trend:
            out += [f"Trend: {trend}", ""]
        if lines:
            out += ["| Points | Fix | Hits |", "|---:|---|---:|"] + [f"| -{p:g} | {r} | {n} |" for p, r, n in lines]
            if cmp_:
                out += ["", "</details>"]
        else:
            out.append("Nothing found.")
        if allowed:
            out += ["", "Allowed by the project (not scored): " + ", ".join(allowed)]
        out += ["", f"[![unslop score]({badge})](https://github.com/marcosnovo/unslop-design)"]
        print("\n".join(out))
    elif a.json:
        print(json.dumps({"score": score, "verdict": word, "files": files, "audit": bool(a.audit), "badge": badge,
                          "penalties": [{"rule": r, "count": n, "points": p} for p, r, n in lines],
                          "allowed": allowed, "trend": trend, "baseline": cmp_}, indent=2))
    else:
        src = []
        if paths:
            src.append(f"{files} source file{'' if files == 1 else 's'}")
        if a.audit:
            src.append("rendered page")
        if ctx:
            src.append(f"context {a.context or '.unslop/context.md'}")
        print(f"unslop score: {score}/100 — {word}  ({' + '.join(src)})")
        if trend and "→" in trend:
            print(f"trend: {trend}  ({os.path.join(a.save, 'history.json')})")
        if cmp_:
            print(f"vs {a.baseline_label}: {cmp_['score']} → {score} ({signed(cmp_['delta'])})")
            for title, rows, sign in (("worse", cmp_["worse"], "-"), ("better", cmp_["better"], "+")):
                for r in rows:
                    print(f"  {title}: {r['rule']} {r['from']} → {r['to']} ({sign}{r['points']:g})")
        if allowed:
            print("allowed by the project (--allow, not scored): " + ", ".join(allowed))
        if lines:
            print("\nWhere the points went (fix the top rows first):")
            for p, rule, n in lines:
                print(f"  -{p:>4g}  {rule}  ({n})")
        print(f"\nBadge: [![unslop score]({badge})](https://github.com/marcosnovo/unslop-design)")
    return 1 if a.min is not None and score < a.min else 0


if __name__ == "__main__":
    sys.exit(main())
