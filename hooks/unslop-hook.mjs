#!/usr/bin/env node
// Post-edit hook: scan the UI files the agent just wrote or edited with
// scripts/slop-scan.py and hand the new hits back to the agent as context.
//
// One script for every agent whose hooks can talk back to the model:
//   Claude Code   PostToolUse  Write, Edit, MultiEdit: tool_input.file_path
//   Gemini CLI    AfterTool    write_file, replace: tool_input.file_path
//   Codex CLI     PostToolUse  apply_patch: the paths inside the patch text
//   Copilot / VS Code agents  PostToolUse: a file path in tool_input or toolArgs
// All of them read {"hookSpecificOutput": {"additionalContext": "…"}} on stdout.
//
// Silent when clean, when no UI file was touched, when Python is missing, or
// when turned off (UNSLOP_HOOK=off, or a line "hook: off" in .unslop/context.md).
// It never edits anything: the agent decides, the user approves.
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, relative, resolve, extname } from "node:path";
import { fileURLToPath } from "node:url";

const UI = new Set([".css", ".scss", ".sass", ".less", ".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".mdx", ".swift", ".kt"]);
const SCAN = join(dirname(fileURLToPath(import.meta.url)), "..", "scripts", "slop-scan.py");
const MAX = 8;
const PATH_KEYS = ["file_path", "filePath", "path", "absolute_path", "absolutePath", "target_file", "filename"];
const WRITE_TOOLS = /^(Write|write_file|create_file|createFile|create)$/;

function quit() { process.exit(0); }

let input = "";
try { input = readFileSync(0, "utf8"); } catch { quit(); }
let ev;
try { ev = JSON.parse(input); } catch { quit(); }
if (/^(off|0|false|no)$/i.test(process.env.UNSLOP_HOOK || "")) quit();

const cwd = ev.cwd || process.cwd();
let tool = ev.tool_input ?? ev.toolArgs ?? ev.tool_args ?? {};
if (typeof tool === "string") { try { tool = JSON.parse(tool); } catch { tool = { input: tool }; } }
const toolName = ev.tool_name || ev.toolName || "";

// The files this edit touched -> the text it brought in (null: the whole file is new).
const files = new Map();
const fresh = [tool.new_string, tool.newString, ...(Array.isArray(tool.edits) ? tool.edits : [])
  .map(e => e && (e.new_string ?? e.newString))].filter(s => typeof s === "string" && s);
const whole = WRITE_TOOLS.test(toolName) || !fresh.length;
for (const key of PATH_KEYS) {
  if (typeof tool[key] === "string" && tool[key]) files.set(resolve(cwd, tool[key]), whole ? null : fresh.join("\n"));
}
// Codex apply_patch: "*** Update File: src/Card.tsx" then "+added line" rows.
const strings = [];
(function walk(v) {
  if (typeof v === "string") strings.push(v);
  else if (Array.isArray(v)) v.forEach(walk);
  else if (v && typeof v === "object") Object.values(v).forEach(walk);
})(tool);
for (const s of strings) {
  for (const block of s.split(/^(?=\*\*\* (?:Add|Update|Delete) File: )/m)) {
    const m = block.match(/^\*\*\* (Add|Update) File: (.+)$/m);
    if (!m) continue;
    const added = block.split("\n").filter(l => l.startsWith("+") && !l.startsWith("+++")).map(l => l.slice(1));
    files.set(resolve(cwd, m[2].trim()), m[1] === "Add" ? null : added.join("\n"));
  }
}
const targets = [...files].filter(([f]) => UI.has(extname(f).toLowerCase()) && existsSync(f));
if (!targets.length) quit();

// Project context (written by "init"): slop-scan reads its scales and allowed rules itself.
const opts = [];
const ctxPath = join(cwd, ".unslop", "context.md");
if (existsSync(ctxPath)) {
  if (/^\s*[-*]?\s*hook:\s*off\b/im.test(readFileSync(ctxPath, "utf8"))) quit();
  opts.push("--context", ctxPath);
}

let out = null;
for (const py of process.platform === "win32" ? ["py", "python", "python3"] : ["python3", "python"]) {
  const r = spawnSync(py, [SCAN, ...targets.map(([f]) => f), "--json", ...opts], { encoding: "utf8", timeout: 15000 });
  if (r.error) continue; // not installed under this name
  if (r.status !== 0) quit(); // a bad --allow in context.md, etc.: stay out of the way
  out = r.stdout;
  break;
}
if (!out) quit();

let hits;
try { hits = JSON.parse(out).hits; } catch { quit(); }

// After an edit, only the lines its new text now sits on (a partial-line edit counts its whole line).
const touched = new Map();
for (const [f, text] of targets) {
  if (text === null) continue;
  const body = readFileSync(f, "utf8");
  const lines = new Set();
  for (const piece of text.split("\n").map(l => l.trim()).filter(l => l.length >= 3)) {
    for (let at = body.indexOf(piece); at !== -1; at = body.indexOf(piece, at + piece.length)) {
      lines.add(body.slice(0, at).split("\n").length);
    }
  }
  touched.set(f, lines);
}
hits = hits.filter(h => {
  const lines = touched.get(resolve(h.file));
  return !lines || lines.has(h.line);
});
if (!hits.length) quit();
hits.sort((a, b) => (a.file === b.file ? a.line - b.line : a.file < b.file ? -1 : 1));

const shown = hits.slice(0, MAX).map(h => `- ${relative(cwd, resolve(h.file)) || h.file}:${h.line}: ${h.ref} ${h.rule} — ${h.description}`);
const more = hits.length > MAX ? `\n- … ${hits.length - MAX} more (run scripts/slop-scan.py on the same files)` : "";
const note = `unslop-design found ${hits.length} slop pattern${hits.length === 1 ? "" : "s"} in what you just wrote:\n` +
  shown.join("\n") + more +
  "\nFix them by changing the value or the token (checklist.md has each fix), not by hiding them. " +
  "If one is a written project decision, it belongs in .unslop/context.md under allow:, not in an unslop-ignore.";
const event = ev.hook_event_name || ev.hookEventName || "PostToolUse";
process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: event, additionalContext: note } }));
