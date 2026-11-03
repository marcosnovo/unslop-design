#!/usr/bin/env bash
# Install unslop-design for every coding agent found on this machine.
#
#   curl -fsSL https://raw.githubusercontent.com/marcosnovo/unslop-design/main/install.sh | bash
#
# One real copy lives in ~/.agents/skills/unslop-design (read by Codex,
# Cline and Zed). Every other agent whose config folder exists gets a
# symlink to it, so `git pull` there updates them all.
#
#   --copy     copy instead of symlinking (for agents that skip symlinks)
#   --dry-run  print what would happen, change nothing
#   --uninstall remove the copy and every link this script made
set -euo pipefail

NAME=unslop-design
REPO=${UNSLOP_REPO:-https://github.com/marcosnovo/unslop-design}
HOME_DIR=${HOME:?}
MAIN="$HOME_DIR/.agents/skills/$NAME"

MODE=link DRY=0 UNINSTALL=0
for arg in "$@"; do
  case "$arg" in
    --copy) MODE=copy ;;
    --dry-run) DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) echo "usage: install.sh [--copy] [--dry-run] [--uninstall]"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

run() { if [ "$DRY" = 1 ]; then echo "  would run: $*"; else "$@"; fi; }

# agent name | config folder that proves it is installed | its global skills folder
AGENTS="
Claude Code|.claude|.claude/skills
Cursor|.cursor|.cursor/skills
GitHub Copilot|.copilot|.copilot/skills
Gemini CLI|.gemini|.gemini/skills
Antigravity|.gemini/antigravity|.gemini/antigravity/skills
Windsurf|.codeium/windsurf|.codeium/windsurf/skills
OpenCode|.config/opencode|.config/opencode/skills
Amp|.config/agents|.config/agents/skills
Kiro|.kiro|.kiro/skills
Goose|.config/goose|.config/goose/skills
Roo Code|.roo|.roo/skills
Junie|.junie|.junie/skills
"

MARK=.installed-by-unslop-design

ours() {  # true only for things this script created
  local t=$1
  if [ -L "$t" ]; then [ "$(readlink "$t")" = "$MAIN" ]; return; fi
  [ -f "$t/$MARK" ]
}

if [ "$UNINSTALL" = 1 ]; then
  echo "Removing $NAME (only what this script installed)"
  while IFS='|' read -r agent _ skills; do
    [ -n "$agent" ] || continue
    target="$HOME_DIR/$skills/$NAME"
    [ -e "$target" ] || [ -L "$target" ] || continue
    if ours "$target"; then echo "  $agent: $target"; run rm -rf "$target"
    else echo "  $agent: $target was not installed by this script, kept"; fi
  done <<< "$AGENTS"
  if [ -e "$MAIN" ]; then
    if ours "$MAIN"; then echo "  main copy: $MAIN"; run rm -rf "$MAIN"
    else echo "  main copy: $MAIN was not installed by this script, kept"; fi
  fi
  exit 0
fi

echo "Installing $NAME"
if [ -d "$MAIN/.git" ]; then
  echo "  updating $MAIN"
  run git -C "$MAIN" pull --ff-only --quiet
elif [ -e "$MAIN" ]; then
  echo "  $MAIN exists and is not a git clone: leaving it as it is"
else
  echo "  cloning into $MAIN  (Codex, Cline, Zed)"
  run mkdir -p "$(dirname "$MAIN")"
  run git clone --quiet --depth 1 "$REPO" "$MAIN"
  [ "$DRY" = 1 ] || touch "$MAIN/$MARK"
fi

linked=0
while IFS='|' read -r agent marker skills; do
  [ -n "$agent" ] || continue
  [ -d "$HOME_DIR/$marker" ] || continue
  target="$HOME_DIR/$skills/$NAME"
  if [ -e "$target" ] && [ "$(cd "$target" && pwd -P)" = "$(cd "$MAIN" 2>/dev/null && pwd -P)" ]; then
    echo "  $agent: already linked"; linked=$((linked + 1)); continue
  fi
  if [ -e "$target" ] || [ -L "$target" ]; then
    echo "  $agent: $target already exists, skipped (remove it to let this script manage it)"
    continue
  fi
  run mkdir -p "$HOME_DIR/$skills"
  if [ "$MODE" = copy ]; then
    run cp -R "$MAIN" "$target"
    [ "$DRY" = 1 ] || touch "$target/$MARK"
    echo "  $agent: copied to $target"
  else
    run ln -s "$MAIN" "$target"
    echo "  $agent: linked $target"
  fi
  linked=$((linked + 1))
done <<< "$AGENTS"

echo
echo "Done: Codex/Cline/Zed + $linked more agent(s)."
echo "Restart open agents, then try /unslop-design (Claude Code, Cursor…) or \$unslop-design (Codex)."
