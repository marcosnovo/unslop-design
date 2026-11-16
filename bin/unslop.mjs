#!/usr/bin/env node
// npx unslop-design <command>: one entry point for the installer and the scripts.
// No dependencies. scan and score need Python 3; audit needs Playwright.
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const [cmd, ...rest] = process.argv.slice(2);

const HELP = `unslop-design: make your app or site stop looking AI-generated

  npx unslop-design install [--copy] [--dry-run] [--uninstall]
      install the skill for every coding agent found on this machine
  npx unslop-design scan [paths] [--json] [--github] [--allow rules]
      slop patterns in UI source, with file, line and fix number
  npx unslop-design score [paths] [--audit report.json] [--save] [--min 80]
      one number from 0 to 100 and where the points went
  npx unslop-design audit <url> [--device iphone,pixel] [--dark]
      the rendered page at 390/768/1280 px (needs Playwright)
  npx unslop-design rules
      every rule id with its fix number
  npx unslop-design hooks <gemini|codex|copilot|claude> [--write]
      the post-edit hook for that agent: prints its config, --write adds it to this project

Then, in your agent: "unslop this screen". Docs: https://github.com/marcosnovo/unslop-design`;

function run(bin, args) {
  const r = spawnSync(bin, args, { stdio: "inherit" });
  if (r.error) return null;
  return r.status ?? 1;
}

function python(script, args) {
  for (const py of process.platform === "win32" ? ["py", "python", "python3"] : ["python3", "python"]) {
    const code = run(py, [join(ROOT, "scripts", script), ...args]);
    if (code !== null) process.exit(code);
  }
  console.error("unslop-design: Python 3 is needed for scan and score (https://www.python.org/downloads/).");
  process.exit(2);
}

// The same hook for every agent: `npx -y unslop-design hook` reads the agent's event on stdin.
const HOOK = "npx -y unslop-design hook";
const HOOKS = {
  gemini: {
    file: ".gemini/settings.json",
    note: "Gemini CLI: AfterTool on write_file and replace. Project hooks ask for approval the first time.",
    merge: (cfg) => {
      cfg.hooks ??= {};
      cfg.hooks.AfterTool = withOurHook(cfg.hooks.AfterTool,
        { matcher: "write_file|replace", hooks: [{ name: "unslop-design", type: "command", command: HOOK, timeout: 30000 }] });
      return cfg;
    },
  },
  copilot: {
    file: ".github/hooks/unslop-design.json",
    note: "GitHub Copilot (VS Code agent, Copilot CLI, cloud agent): postToolUse. Agent hooks are in preview; commit the file for cloud sessions.",
    merge: () => ({ version: 1, hooks: { postToolUse: [{ type: "command", command: HOOK, timeoutSec: 30 }] } }),
  },
  claude: {
    file: ".claude/settings.json",
    note: "Claude Code: the plugin already ships this hook (/plugin install unslop-design@unslop). Use this only without the plugin.",
    merge: (cfg) => {
      cfg.hooks ??= {};
      cfg.hooks.PostToolUse = withOurHook(cfg.hooks.PostToolUse,
        { matcher: "Write|Edit|MultiEdit", hooks: [{ type: "command", command: HOOK, timeout: 30 }] });
      return cfg;
    },
  },
  codex: {
    file: null,
    note: "Codex CLI: PostToolUse on apply_patch. Add this to ~/.codex/config.toml (hooks may need enabling in your version, and some versions don't fire it for apply_patch).",
    text: `[[hooks.PostToolUse]]\nmatcher = "apply_patch"\n\n[[hooks.PostToolUse.hooks]]\ntype = "command"\ncommand = "${HOOK}"\n`,
  },
};

// Replace only our own handler in a list of hook groups: other commands in the same group stay.
function withOurHook(groups, group) {
  const ours = (h) => typeof h?.command === "string" && h.command.includes("unslop-design");
  const kept = (groups || []).map(g => ({ ...g, hooks: (g.hooks || []).filter(h => !ours(h)) })).filter(g => g.hooks.length);
  return [...kept, group];
}

function hooks([agent, ...flags]) {
  const h = HOOKS[agent];
  if (!h) {
    console.error(`usage: npx unslop-design hooks <${Object.keys(HOOKS).join("|")}> [--write]\n` +
      "Cursor and Windsurf hooks can't send a note back to the agent yet, so there is no hook for them.");
    process.exit(2);
  }
  console.log(h.note + "\n");
  if (!h.file) { console.log(h.text); return; }
  let cfg = {};
  if (existsSync(h.file)) {
    try { cfg = JSON.parse(readFileSync(h.file, "utf8")); }
    catch { console.error(`${h.file} isn't valid JSON: fix it or add the hook by hand.`); process.exit(2); }
  }
  const next = JSON.stringify(h.merge(cfg), null, 2) + "\n";
  if (flags.includes("--write")) {
    mkdirSync(dirname(h.file), { recursive: true });
    writeFileSync(h.file, next);
    console.log(`Wrote ${h.file}. The hook runs after each UI edit and is silent when it's clean.`);
  } else {
    console.log(`${h.file}:\n${next}\nRun again with --write to save it.`);
  }
}

switch (cmd) {
  case "install": {
    const code = run("bash", [join(ROOT, "install.sh"), ...rest]);
    if (code === null) {
      console.error("unslop-design: install needs bash. On Windows use Git Bash, or: npx skills add marcosnovo/unslop-design -g");
      process.exit(2);
    }
    process.exit(code);
  }
  case "scan": python("slop-scan.py", rest); break;
  case "score": python("unslop-score.py", rest); break;
  case "rules": python("slop-scan.py", ["--list-rules"]); break;
  case "hook": {
    const r = spawnSync(process.execPath, [join(ROOT, "hooks", "unslop-hook.mjs")], { stdio: "inherit" });
    process.exit(r.status ?? 0);
  }
  case "hooks": hooks(rest); break;
  case "audit": process.exit(run(process.execPath, [join(ROOT, "scripts", "web-audit.mjs"), ...rest]) ?? 1);
  case undefined: case "help": case "-h": case "--help": console.log(HELP); break;
  default:
    console.error(`unslop-design: unknown command "${cmd}"\n\n${HELP}`);
    process.exit(2);
}
