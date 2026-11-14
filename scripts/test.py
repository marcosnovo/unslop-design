#!/usr/bin/env python3
"""Regression tests for the scripts: every case in tests/cases must give exactly
the hits tests/expected.json says, per rule, and no others.

    python3 scripts/test.py                 # slop-scan rules, stdlib only
    python3 scripts/test.py --audit         # also web-audit.mjs on the audit cases (needs Playwright)
    python3 scripts/test.py --update        # rewrite expected.json from the current output (review the diff!)
    python3 scripts/test.py stock-kit       # only cases whose name contains "stock-kit"

expected.json also holds "cli" checks: a script, its arguments, the exit code
and strings the output must (or must not) contain.

Each case is one folder, scanned as a unit (so cross-file checks like
undefined tokens see the whole case). A rule not listed for a case must give
zero hits. When a change to a rule is intended, run --update and read the
diff of expected.json in the PR: that diff is the behavior change.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CASES = os.path.join(ROOT, "tests", "cases")
EXPECTED = os.path.join(ROOT, "tests", "expected.json")


def load_scanner():
    spec = importlib.util.spec_from_file_location("slop_scan", os.path.join(HERE, "slop-scan.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scan_case(scan, folder):
    scale = {float(x) for x in "0,1,2,4,8,12,16,20,24,32,40,48,64,80,96".split(",")}
    hits, seen = {}, []
    for f in scan.files([folder]):
        seen.append(f)
        scan.scan(f, scale, hits)
    scan.token_checks(seen, hits)
    counts = {}
    for (rid, _ref, _desc), where in hits.items():
        counts[rid] = counts.get(rid, 0) + len(where)
    return dict(sorted(counts.items()))


def audit_case(script, html, widths="390"):
    """Run web-audit.mjs on one page; None if Playwright isn't available."""
    with tempfile.TemporaryDirectory() as out:
        r = subprocess.run(["node", script, html, "--out", out, "--widths", widths],
                           capture_output=True, text=True, timeout=300)
        if r.returncode == 2 and "Playwright" in (r.stderr + r.stdout):
            return None
        if r.returncode != 0:
            raise RuntimeError(f"web-audit failed on {html}: {r.stderr.strip()[:300]}")
        rep = json.load(open(os.path.join(out, "report.json")))
    m, ts = rep["measure"], rep.get("textScale") or {}
    return {
        "contrast": len(m["contrastFails"]),
        "graphics": len(m.get("graphicsFails", [])),
        "emoji": len(m["emoji"]),
        "glow": len(m["glow"]),
        "text_scales": bool(ts.get("checked")) and ts.get("grew", 0) / ts["checked"] >= 0.5,
        "long_lines": len(m.get("longLines", [])),
        "aligned_text": len(m.get("alignedText", [])),
        "empty_blocks": len(m.get("emptyBlocks", [])),
        "tiny_text": max([len(w.get("tinyText", [])) for w in rep["widths"].values()] or [0]),
        "estimated": sum(1 for x in m["contrastFails"] if x.get("estimated")),
        "unknown": m.get("contrastUnknown", 0),
        "off_scale": len(m["census"]["offScaleSpacing"]),
        "edges": len(m.get("leftEdges", [])),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("only", nargs="?", help="run only cases whose name contains this")
    ap.add_argument("--audit", nargs="?", const=os.path.join(HERE, "web-audit.mjs"), metavar="SCRIPT",
                    help="also run web-audit.mjs (or this copy of it) on the cases listed under 'audit'")
    ap.add_argument("--update", action="store_true", help="rewrite expected.json from the current output")
    a = ap.parse_args()

    expected = json.load(open(EXPECTED)) if os.path.exists(EXPECTED) else {"scan": {}, "audit": {}}
    scan = load_scanner()
    names = sorted(d for d in os.listdir(CASES) if os.path.isdir(os.path.join(CASES, d)))
    if a.only:
        names = [n for n in names if a.only in n]

    failures, ran = [], 0
    for name in names:
        got = scan_case(scan, os.path.join(CASES, name))
        ran += 1
        if a.update:
            expected["scan"][name] = got
            continue
        want = expected["scan"].get(name)
        if want is None:
            failures.append(f"{name}: no expectation (run --update and review it)")
        elif got != want:
            diff = {k: f"{want.get(k, 0)} → {got.get(k, 0)}" for k in sorted(set(want) | set(got)) if want.get(k, 0) != got.get(k, 0)}
            failures.append(f"{name}: " + ", ".join(f"{k} {v}" for k, v in diff.items()))

    # Command-line behavior that hit counts can't express: --allow, refusals, exit codes.
    for check in expected.get("cli", []):
        if a.only and a.only not in check["name"]:
            continue
        cmd = [sys.executable, os.path.join(HERE, check["script"])] + [
            arg.replace("{cases}", CASES) for arg in check["args"]]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        out = r.stdout + r.stderr
        ran += 1
        problems = []
        if r.returncode != check["exit"]:
            problems.append(f"exit {check['exit']} → {r.returncode}")
        for s in check.get("contains", []):
            if s not in out:
                problems.append(f"missing {s!r}")
        for s in check.get("excludes", []):
            if s in out:
                problems.append(f"unexpected {s!r}")
        if problems:
            failures.append(f"{check['name']} (cli): " + "; ".join(problems))

    audited = skipped = 0
    if a.audit:
        for name, page in sorted(expected.get("audit", {}).items()):
            if a.only and a.only not in name:
                continue
            got = audit_case(a.audit, os.path.join(CASES, name, page["page"]), page.get("widths", "390"))
            if got is None:
                skipped += 1
                continue
            audited += 1
            if a.update:
                page["expect"] = got
            elif got != page["expect"]:
                diff = {k: f"{page['expect'].get(k)} → {got.get(k)}" for k in got if page["expect"].get(k) != got.get(k)}
                failures.append(f"{name} (audit): " + ", ".join(f"{k} {v}" for k, v in diff.items()))

    if a.update:
        with open(EXPECTED, "w") as f:
            json.dump(expected, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"expected.json rewritten from {ran} cases" + (f" and {audited} audits" if audited else "") +
              ". Review the diff: it is the behavior change.")
        return 0
    for line in failures:
        print("✗", line)
    note = f", {audited} audits" if a.audit else ""
    note += f" ({skipped} skipped: Playwright not found)" if skipped else ""
    print(f"{'FAIL' if failures else 'ok'}: {ran} cases{note}, {len(failures)} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
