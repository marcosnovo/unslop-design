#!/usr/bin/env python3
"""Check SKILL.md against the Agent Skills spec (agentskills.io/specification).

    python3 scripts/validate.py [skill-dir]

Stdlib only. Exits 1 and lists every problem if something is off.
"""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent)
problems = []

text = (root / "SKILL.md").read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
if not m:
    sys.exit("SKILL.md: missing YAML frontmatter between --- lines")
front, body = m.groups()

def field(key):
    hit = re.search(rf"^{key}:\s*(.*)$", front, re.M)
    return hit.group(1).strip().strip('"') if hit else None

name, desc = field("name"), field("description")
if not name:
    problems.append("name: missing")
else:
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append(f"name: '{name}' must be 1-64 chars of a-z, 0-9 and single hyphens")
    if root.resolve().name != name:
        print(f"! name '{name}' differs from folder '{root.resolve().name}': install it as a folder called {name}")
if not desc:
    problems.append("description: missing")
elif len(desc) > 1024:
    problems.append(f"description: {len(desc)} chars, max 1024")
compat = field("compatibility")
if compat and len(compat) > 500:
    problems.append(f"compatibility: {len(compat)} chars, max 500")

lines = body.count("\n")
if lines > 500:
    problems.append(f"SKILL.md body: {lines} lines, keep it under 500")

for ref in sorted(set(re.findall(r"`([\w./-]+\.(?:md|yaml|py|sh))`", text))):
    if "/" not in ref and not (root / ref).exists() and ref not in ("SKILL.md",):
        problems.append(f"referenced file not found: {ref}")

for p in problems:
    print("✗", p)
if problems:
    sys.exit(1)
print(f"✓ {name}: frontmatter OK, description {len(desc)}/1024 chars, body {lines} lines")
