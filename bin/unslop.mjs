#!/usr/bin/env node
// npx unslop-design <command>: one entry point for the installer and the scripts.
// No dependencies. scan and score need Python 3; audit needs Playwright.
import { spawnSync } from "node:child_process";
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
  case "audit": process.exit(run(process.execPath, [join(ROOT, "scripts", "web-audit.mjs"), ...rest]) ?? 1);
  case undefined: case "help": case "-h": case "--help": console.log(HELP); break;
  default:
    console.error(`unslop-design: unknown command "${cmd}"\n\n${HELP}`);
    process.exit(2);
}
