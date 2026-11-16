#!/usr/bin/env node
// PostToolUse hook: scan the UI file the agent just wrote or edited with
// scripts/slop-scan.py and hand the new hits back to the agent as context.
// Silent when clean, when the file isn't UI, when Python is missing, or when
// turned off (UNSLOP_HOOK=off, or a line "hook: off" in .unslop/context.md).
// It never edits anything: the agent decides, the user approves.
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, relative, extname } from "node:path";
import { fileURLToPath } from "node:url";

const UI = new Set([".css", ".scss", ".sass", ".less", ".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".mdx", ".swift", ".kt"]);
const SCAN = join(dirname(fileURLToPath(import.meta.url)), "..", "scripts", "slop-scan.py");
const MAX = 8;

function quit() { process.exit(0); }

let input = "";
try { input = readFileSync(0, "utf8"); } catch { quit(); }
let ev;
try { ev = JSON.parse(input); } catch { quit(); }
if (/^(off|0|false|no)$/i.test(process.env.UNSLOP_HOOK || "")) quit();

const tool = ev.tool_input || {};
const file = tool.file_path;
if (!file || !UI.has(extname(file).toLowerCase()) || !existsSync(file)) quit();

// Project context (written by "init"): slop-scan reads its scales and allowed rules itself.
const cwd = ev.cwd || process.cwd();
const opts = [];
const ctxPath = join(cwd, ".unslop", "context.md");
if (existsSync(ctxPath)) {
  if (/^\s*[-*]?\s*hook:\s*off\b/im.test(readFileSync(ctxPath, "utf8"))) quit();
  opts.push("--context", ctxPath);
}

let out = null;
for (const py of ["python3", "python"]) {
  const r = spawnSync(py, [SCAN, file, "--json", ...opts], { encoding: "utf8", timeout: 15000 });
  if (r.error) continue; // not installed under this name
  if (r.status !== 0) quit(); // a bad --allow in context.md, etc.: stay out of the way
  out = r.stdout;
  break;
}
if (!out) quit();

let hits;
try { hits = JSON.parse(out).hits; } catch { quit(); }
// After an Edit, only what the edit brought in: hits on the lines its new text now spans
// (a partial-line edit counts its whole line).
const fresh = [tool.new_string, ...(tool.edits || []).map(e => e.new_string)].filter(Boolean);
if (fresh.length && ev.tool_name !== "Write") {
  const text = readFileSync(file, "utf8");
  const touched = new Set();
  for (const ns of fresh) {
    for (let at = text.indexOf(ns); at !== -1; at = text.indexOf(ns, at + Math.max(1, ns.length))) {
      const first = text.slice(0, at).split("\n").length;
      const last = first + ns.split("\n").length - 1;
      for (let n = first; n <= last; n++) touched.add(n);
    }
  }
  hits = hits.filter(h => touched.has(h.line));
}
if (!hits.length) quit();
hits.sort((a, b) => a.line - b.line);

const rel = relative(cwd, file) || file;
const shown = hits.slice(0, MAX).map(h => `- line ${h.line}: ${h.ref} ${h.rule} — ${h.description}`);
const more = hits.length > MAX ? `\n- … ${hits.length - MAX} more (python3 scripts/slop-scan.py ${rel})` : "";
const note = `unslop-design found ${hits.length} slop pattern${hits.length === 1 ? "" : "s"} in what you just wrote to ${rel}:\n` +
  shown.join("\n") + more +
  "\nFix them by changing the value or the token (checklist.md has each fix), not by hiding them. " +
  "If one is a written project decision, it belongs in .unslop/context.md under allow:, not in an unslop-ignore.";
process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: "PostToolUse", additionalContext: note } }));
