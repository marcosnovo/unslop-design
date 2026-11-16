# Contributing

The checklist grows from real redesigns. The best contribution is a pattern
of AI slop it doesn't catch yet, with proof.

## Share your score

Ran it on your own app? Open a **Share your score** issue: before/after,
the two numbers, and what it missed. With your permission it goes in the
README's *Scores in the wild*, and a miss becomes a rule.

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

## Change a script

Every rule in `slop-scan.py` and every check in `web-audit.mjs` has cases in
`tests/cases`: one folder per case, scanned as a unit, with the exact hits
per rule in `tests/expected.json` (a rule not listed must give zero).

```bash
python3 scripts/test.py            # the scanner rules, standard library only
python3 scripts/test.py --audit    # also the rendered checks (needs Playwright)
```

A new rule or a fixed false positive comes with a case that fails before
the change and passes after: the hit it should give, and the near miss it
must not. When a behavior change is intended, run `--update` and read the
diff of `expected.json`: that diff is the change, and it goes in the PR.

## Releasing

Bump `metadata.version` in `SKILL.md`, `version` in
`.claude-plugin/plugin.json` and `version` in `package.json` together
(`python3 scripts/validate.py` fails if they differ, and plugin users only
get updates when it changes), add the `## x.y.z` entry to `CHANGELOG.md`,
and check `claude plugin validate --strict .`.

Merging that to `main` is the release: `.github/workflows/release.yml` sees
a version with no tag, runs the tests, tags the commit, publishes the
GitHub release with the changelog entry and `unslop-design.zip`, and
publishes to npm through Trusted Publishing (no secret; configured on the
package's npm settings for `release.yml`). An `NPM_TOKEN` secret, if
present, is used instead.
