# Score, hook and CI

How the number is computed, and how it keeps working after the review: the post-edit hook, the PR comment and the checks for other tools.

## Score it

```bash
python3 scripts/unslop-score.py src/                                   # the code alone
python3 scripts/unslop-score.py src/ --audit unslop-audit/report.json  # plus the rendered page (web-audit.mjs)
```

```text
$ python3 scripts/unslop-score.py examples/dashboard-before.html
unslop score: 21/100 — slop  (1 source file)

Where the points went (fix the top rows first):
  -  12  [#32] Colored glows  (6)
  -  10  [#33] Emoji in the UI  (19)
  -   8  [#53] Focus outline removed  (1)
  …

Badge: [![unslop score](https://img.shields.io/badge/unslop_score-21%2F100-red)](https://github.com/marcosnovo/unslop-design)
```

Each kind of slop costs points per hit up to a cap, so the number says how
many kinds are left, not how big the codebase is. Paste the badge in your
README, and put "score 21 → 100" at the top of the PR. It's a smoke alarm,
not a judge: a 95 can still have a flat hierarchy. `--min 80` makes it exit
1 below 80 if you want it in a pre-commit hook, and `--save` keeps every run
in `.unslop/history.json` so the score has a trend.

## Keep it clean

A review fixes the screen; these keep the next edit from undoing it.

**While the agent writes (Claude Code).** The plugin ships a hook: after
every edit to a UI file it scans that file and tells the agent what slop the
edit just added, with the fix number. It says nothing when the edit is
clean, never changes code itself, and turns off with `UNSLOP_HOOK=off` or
`hook: off` in `.unslop/context.md`.

**While other agents write.** The same hook works wherever an agent's hooks
can hand a note back to the model. One command sets it up in the project:

```bash
npx unslop-design hooks gemini --write    # .gemini/settings.json, AfterTool
npx unslop-design hooks copilot --write   # .github/hooks/unslop-design.json, postToolUse (preview)
npx unslop-design hooks codex             # prints the ~/.codex/config.toml block, PostToolUse
```

Each runs `npx -y unslop-design hook` after a write or edit, reads the
agent's event (Gemini's `write_file`/`replace`, Codex's `apply_patch`,
Copilot's tool arguments) and answers in the format they share. Cursor's and
Windsurf's post-edit hooks can't send anything back to the agent yet, so
there is no hook for them; the scanner and the CI work there as anywhere.

**On every pull request (GitHub Actions).** Each hit becomes an annotation
on its line, and one comment on the PR keeps the score and the change
against the base branch, updated on every push:

> ### unslop score: 88/100 (+7 vs main)
> **Worse** · [#68] Border and shadow on one card: 0 → 2 (-2)
> **Better** · [#32] Colored glows: 3 → 0 (+8) · [#33] Emoji in the UI: 4 → 0 (+8)

The job fails under your minimum, if you set one:

```yaml
# .github/workflows/unslop.yml
on: pull_request
permissions:
  contents: read
  pull-requests: write   # for the comment
jobs:
  unslop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: marcosnovo/unslop-design@v1.13.0
        with:
          paths: src
          min: 80           # optional; also: allow, scale, type-scale, comment: false
```

Locally, `unslop-score.py --json > main.json` on one branch and
`--baseline main.json` on another gives the same comparison.

**Anywhere else.** `python3 scripts/slop-scan.py src --github` prints the
same annotations, `--json` every hit for other tools, and `--list-rules`
every rule id. All of them read `.unslop/context.md`, so your scale and your
allowed rules apply without flags.

Screen recordings need `ffmpeg` (`brew install ffmpeg`) so the agent can
pull frames from them.

---

[← Back to the README](../README.md)
