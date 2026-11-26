#!/usr/bin/env bash
# ==============================================================================
# sync-agy: Cross-Machine Synchronization Tool for Antigravity (AGY)
# Synchronizes global skills, rules, and configurations via Git.
# ==============================================================================
set -euo pipefail

# ANSI Color Codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

# Resolve repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$SCRIPT_DIR/../dotfiles/gemini" ]; then
    REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
elif [ -d "$HOME/projects/desktopConfigs/dotfiles/gemini" ]; then
    REPO_DIR="$HOME/projects/desktopConfigs"
elif [ -d "$HOME/projects/desktopConfigs/dotfiles/gemini" ]; then
    REPO_DIR="$HOME/projects/desktopConfigs"
else
    echo -e "${RED}Error: Cannot locate desktopConfigs repository containing dotfiles/gemini.${RESET}"
    exit 1
fi

GEMINI_DIR="$REPO_DIR/dotfiles/gemini"
CONFIG_TARGET="$HOME/.gemini/config"
CLI_TARGET="$HOME/.gemini/antigravity-cli"

# Ensure ~/.gemini target directories exist
mkdir -p "$CONFIG_TARGET" "$CLI_TARGET"

# Helper: Ensure symlink exists and points to repo
ensure_link() {
    local src="$1"
    local dest="$2"

    if [ -L "$dest" ]; then
        local current_target
        current_target="$(readlink "$dest")"
        if [ "$current_target" != "$src" ]; then
            rm -f "$dest"
            ln -s "$src" "$dest"
            echo -e "${CYAN}Updated symlink: $dest -> $src${RESET}"
        fi
    elif [ -e "$dest" ]; then
        # Back up existing real file/directory if it's not a symlink
        local backup="${dest}.bak-$(date +%s)"
        mv "$dest" "$backup"
        ln -s "$src" "$dest"
        echo -e "${YELLOW}Backed up existing $dest to $backup and created symlink -> $src${RESET}"
    else
        ln -s "$src" "$dest"
        echo -e "${GREEN}Created symlink: $dest -> $src${RESET}"
    fi
}

verify_links() {
    ensure_link "$GEMINI_DIR/AGENTS.md" "$CONFIG_TARGET/AGENTS.md"
    ensure_link "$GEMINI_DIR/mcp_config.json" "$CONFIG_TARGET/mcp_config.json"
    ensure_link "$GEMINI_DIR/skills" "$CONFIG_TARGET/skills"
    if [ -f "$GEMINI_DIR/hooks.json" ]; then
        ensure_link "$GEMINI_DIR/hooks.json" "$CONFIG_TARGET/hooks.json"
    fi
    if [ -d "$GEMINI_DIR/hooks" ]; then
        ensure_link "$GEMINI_DIR/hooks" "$CONFIG_TARGET/hooks"
    fi
    if [ -f "$GEMINI_DIR/antigravity-cli/statusline.py" ]; then
        ensure_link "$GEMINI_DIR/antigravity-cli/statusline.py" "$CLI_TARGET/statusline.py"
    fi
    if [ -d "$REPO_DIR/dotfiles/git/hooks" ]; then
        mkdir -p "$HOME/.config/git"
        ensure_link "$REPO_DIR/dotfiles/git/hooks" "$HOME/.config/git/hooks"
        git config --global core.hooksPath "$HOME/.config/git/hooks"
    fi
}

merge_cli_settings() {
    local defaults_file="$GEMINI_DIR/antigravity-cli/cli-defaults.json"
    local settings_file="$CLI_TARGET/settings.json"
    [ -f "$defaults_file" ] || return 0

    local py_bin
    py_bin="$(command -v python3 || command -v /usr/bin/python3 || true)"
    if [ -z "$py_bin" ]; then
        echo -e "${YELLOW}Warning: python3 not found; skipping Antigravity CLI settings merge.${RESET}"
        return 0
    fi

    "$py_bin" - "$defaults_file" "$settings_file" <<'PYEOF'
import copy
import json
import os
import sys

defaults_path, settings_path = sys.argv[1], sys.argv[2]

with open(defaults_path, "r", encoding="utf-8") as f:
    defaults = json.load(f)

sl = defaults.get("statusLine")
if isinstance(sl, dict) and isinstance(sl.get("command"), str):
    sl["command"] = os.path.expanduser(sl["command"])

if os.path.exists(settings_path):
    with open(settings_path, "r", encoding="utf-8") as f:
        current = json.load(f)
else:
    current = {}

merged = copy.deepcopy(current)
for k, v in defaults.items():
    if isinstance(v, dict) and isinstance(merged.get(k), dict):
        merged[k] = {**merged[k], **v}
    else:
        merged[k] = v

if merged != current:
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    print(f"\033[0;36mUpdated Antigravity CLI settings: {settings_path}\033[0m")
PYEOF
}

cmd_status() {
    echo -e "${BOLD}${CYAN}=== Antigravity Sync Status ===${RESET}"
    verify_links
    echo -e "\nRepository: $REPO_DIR"
    echo -e "Branch: $(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)"
    
    echo -e "\n${BOLD}Local Changes in AGY dotfiles:${RESET}"
    local changes
    changes=$(git -C "$REPO_DIR" status --porcelain "dotfiles/gemini")
    if [ -z "$changes" ]; then
        echo -e "${GREEN}✓ All local skills and rules are clean (no uncommitted changes).${RESET}"
    else
        echo "$changes"
    fi

    echo -e "\n${BOLD}Remote Tracking Status:${RESET}"
    git -C "$REPO_DIR" fetch --quiet origin 2>/dev/null || true
    local upstream
    upstream=$(git -C "$REPO_DIR" rev-parse --abbrev-ref '@{u}' 2>/dev/null || echo "")
    if [ -n "$upstream" ]; then
        local local_sha remote_sha base_sha
        local_sha=$(git -C "$REPO_DIR" rev-parse @)
        remote_sha=$(git -C "$REPO_DIR" rev-parse "$upstream")
        base_sha=$(git -C "$REPO_DIR" merge-base @ "$upstream")

        if [ "$local_sha" = "$remote_sha" ]; then
            echo -e "${GREEN}✓ Local repository is up to date with $upstream.${RESET}"
        elif [ "$local_sha" = "$base_sha" ]; then
            echo -e "${YELLOW}⚠ Behind $upstream. Run 'sync-agy pull' to update.${RESET}"
        elif [ "$remote_sha" = "$base_sha" ]; then
            echo -e "${YELLOW}↑ Ahead of $upstream. Run 'sync-agy push' to sync to other machines.${RESET}"
        else
            echo -e "${RED}⚠ Diverged from $upstream.${RESET}"
        fi
    fi
}

cmd_pull() {
    echo -e "${BOLD}${CYAN}Pulling latest Antigravity configs and skills...${RESET}"

    if git -C "$REPO_DIR" pull --rebase origin master 2>&1; then
        verify_links
        merge_cli_settings
        echo -e "${GREEN}✓ Successfully synced Antigravity configs and skills from remote!${RESET}"
    else
        echo -e "${RED}Warning: Git pull failed or encountered conflicts. Please check $REPO_DIR.${RESET}"
        return 1
    fi
}

cmd_push() {
    local message="${1:-chore(agy): sync skills and rules across machines}"
    echo -e "${BOLD}${CYAN}Pushing Antigravity changes to remote...${RESET}"
    verify_links

    local linter="$HOME/projects/agy-lab/scripts/lint_skills.py"
    if [ -f "$linter" ] && command -v python3 >/dev/null 2>&1; then
        python3 "$linter" "$GEMINI_DIR/skills" || return 1
    fi

    git -C "$REPO_DIR" add "dotfiles/gemini"
    if git -C "$REPO_DIR" diff --cached --quiet "dotfiles/gemini"; then
        echo -e "${YELLOW}No changes in dotfiles/gemini to commit.${RESET}"
    else
        git -C "$REPO_DIR" commit -m "$message"
        echo -e "${GREEN}✓ Changes committed: $message${RESET}"
    fi

    echo "Pushing to origin..."
    if git -C "$REPO_DIR" push origin master; then
        echo -e "${GREEN}✓ Successfully pushed Antigravity configs to remote!${RESET}"
    else
        echo -e "${RED}Error: Git push failed.${RESET}"
        return 1
    fi
}

cmd_tag() {
    local tag_name="${1:-agy-v$(date +%Y.%m.%d-%H%M)}"
    git -C "$REPO_DIR" tag -a "$tag_name" -m "AGY config snapshot $tag_name"
    echo -e "${GREEN}✓ Created tag: $tag_name${RESET}"
    echo "Run 'git -C $REPO_DIR push origin $tag_name' to publish tag."
}

cmd_versions() {
    echo -e "${BOLD}${CYAN}=== AGY Tags & Recent History ===${RESET}"
    git -C "$REPO_DIR" tag -l 'agy-*' --sort=-creatordate | head -n 10
    echo -e "\n${BOLD}Recent dotfiles/gemini commits:${RESET}"
    git -C "$REPO_DIR" log -n 8 --oneline -- "dotfiles/gemini"
}

cmd_rollback() {
    local target="${1:-}"
    if [ -n "$(git -C "$REPO_DIR" status --porcelain "dotfiles/gemini")" ]; then
        echo -e "${RED}Error: Uncommitted changes in dotfiles/gemini. Commit or stash first.${RESET}"
        return 1
    fi
    if [ -z "$target" ]; then
        target="$(git -C "$REPO_DIR" log -n 2 --format=%H -- "dotfiles/gemini" | tail -n 1)"
    fi
    if [ -z "$target" ]; then
        echo -e "${RED}Error: Could not resolve rollback target.${RESET}"
        return 1
    fi
    git -C "$REPO_DIR" checkout "$target" -- "dotfiles/gemini"
    if git -C "$REPO_DIR" diff --cached --quiet "dotfiles/gemini"; then
        echo -e "${YELLOW}dotfiles/gemini already matches $target.${RESET}"
        return 0
    fi
    git -C "$REPO_DIR" commit -m "chore(agy): rollback dotfiles/gemini to $target"
    verify_links
    merge_cli_settings
    echo -e "${GREEN}✓ Rolled back dotfiles/gemini to $target (committed non-destructively).${RESET}"
}

# CLI routing
ACTION="${1:-pull}"
shift || true

case "$ACTION" in
    pull|up|update)
        cmd_pull
        ;;
    push)
        cmd_push "$@"
        ;;
    status|check)
        cmd_status
        ;;
    tag)
        cmd_tag "$@"
        ;;
    versions|history)
        cmd_versions
        ;;
    rollback)
        cmd_rollback "$@"
        ;;
    link|relink)
        verify_links
        merge_cli_settings
        echo -e "${GREEN}✓ All Antigravity configuration symlinks and CLI defaults verified.${RESET}"
        ;;
    -h|--help|help)
        echo "Usage: sync-agy [pull|push [msg]|status|link|tag [name]|versions|rollback [ref]]"
        echo ""
        echo "Commands:"
        echo "  pull            Pull latest skills and rules from git (default)"
        echo "  push [msg]      Lint, commit, and push local skill/rule updates to git"
        echo "  status          Check git sync state and symlink integrity"
        echo "  link            Ensure ~/.gemini/config symlinks point to repository"
        echo "  tag [name]      Create an annotated agy-v* snapshot tag"
        echo "  versions        List agy-* tags and recent dotfiles/gemini commits"
        echo "  rollback [ref]  Restore dotfiles/gemini to tag/commit cleanly"
        ;;
    *)
        echo -e "${RED}Unknown command: $ACTION${RESET}"
        echo "Run 'sync-agy --help' for usage."
        exit 1
        ;;
esac
