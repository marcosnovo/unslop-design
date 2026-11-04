# Contributing

The checklist grows from real redesigns. The best contribution is a pattern
of AI slop it doesn't catch yet, with proof.

## Propose a new fix

Open an issue with the **New fix** template and include:

1. **Before and after** — two screenshots (your own app or a mock you made;
   please don't post other people's work without permission).
2. **The rule** in one sentence, written as an instruction ("Section titles
   are labels: small, not `h1`").
3. **Why** it matters: what the user loses with the "before".
4. **How to check it**: what a reviewer looks for in code or on screen.

A fix gets in when it's general (not one app's taste), checkable, and
doesn't duplicate an existing number.

## Change an existing fix

Fix numbers are stable: reviewers cite them. Edit the text, don't renumber.
New fixes go at the end of their section's range or in "Also" until a
release renumbers deliberately (noted in `CHANGELOG.md`).

## Style

- Short sentences, imperative voice, one idea per bullet.
- Concrete over abstract: a value, a component name, a before/after.
- No new jargon when a plain word works.

## Releasing

Bump `metadata.version` in `SKILL.md` and `version` in
`.claude-plugin/plugin.json` together (`python3 scripts/validate.py` fails
if they differ, and plugin users only get updates when it changes), add the
entry to `CHANGELOG.md`, and check `claude plugin validate --strict .`.
