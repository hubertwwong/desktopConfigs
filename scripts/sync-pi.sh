#!/usr/bin/env bash
# ==============================================================================
# sync-pi: Cross-Machine Synchronization Tool for Pi (@earendil-works/pi-coding-agent)
# Symlinks dotfiles/pi/* and shared AGY skills into ~/.pi/agent/ via Git.
# ==============================================================================
set -euo pipefail

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
if [ -d "$SCRIPT_DIR/../dotfiles/pi" ]; then
    REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
elif [ -d "$HOME/projects/desktopConfigs/dotfiles/pi" ]; then
    REPO_DIR="$HOME/projects/desktopConfigs"
else
    echo -e "${RED}Error: Cannot locate desktopConfigs repository containing dotfiles/pi.${RESET}"
    exit 1
fi

PI_DIR="$REPO_DIR/dotfiles/pi"
GEMINI_SKILLS_DIR="$REPO_DIR/dotfiles/gemini/skills"
AGENT_TARGET="$HOME/.pi/agent"

mkdir -p "$AGENT_TARGET"

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
    ensure_link "$PI_DIR/AGENTS.md" "$AGENT_TARGET/AGENTS.md"
    ensure_link "$PI_DIR/settings.json" "$AGENT_TARGET/settings.json"
    ensure_link "$PI_DIR/models.json" "$AGENT_TARGET/models.json"
    ensure_link "$PI_DIR/agents" "$AGENT_TARGET/agents"
    ensure_link "$PI_DIR/extensions" "$AGENT_TARGET/extensions"
    if [ -d "$GEMINI_SKILLS_DIR" ]; then
        ensure_link "$GEMINI_SKILLS_DIR" "$AGENT_TARGET/skills"
    fi
}

cmd_status() {
    echo -e "${BOLD}${CYAN}=== Pi Sync Status ===${RESET}"
    verify_links
    echo -e "\nRepository: $REPO_DIR"
    echo -e "Branch: $(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)"

    echo -e "\n${BOLD}Local Changes in Pi dotfiles:${RESET}"
    local changes
    changes=$(git -C "$REPO_DIR" status --porcelain "dotfiles/pi")
    if [ -z "$changes" ]; then
        echo -e "${GREEN}✓ All local Pi configs and extensions are clean.${RESET}"
    else
        echo "$changes"
    fi

    echo -e "\n${BOLD}Symlink Targets:${RESET}"
    ls -la "$AGENT_TARGET" | grep -E "AGENTS\.md|settings\.json|models\.json|agents|extensions|skills" || true
}

cmd_pull() {
    echo -e "${BOLD}${CYAN}Pulling latest Pi configs...${RESET}"
    if git -C "$REPO_DIR" pull --rebase origin master 2>&1; then
        verify_links
        echo -e "${GREEN}✓ Successfully synced Pi configs from remote.${RESET}"
    else
        echo -e "${RED}Warning: Git pull failed or encountered conflicts. Check $REPO_DIR.${RESET}"
        return 1
    fi
}

cmd_push() {
    local message="${1:-chore(pi): sync pi configs and extensions}"
    echo -e "${BOLD}${CYAN}Pushing Pi changes to remote...${RESET}"
    verify_links

    git -C "$REPO_DIR" add "dotfiles/pi"
    if git -C "$REPO_DIR" diff --cached --quiet "dotfiles/pi"; then
        echo -e "${YELLOW}No changes in dotfiles/pi to commit.${RESET}"
    else
        git -C "$REPO_DIR" commit -m "$message"
        echo -e "${GREEN}✓ Changes committed: $message${RESET}"
    fi

    echo "Pushing to origin..."
    git -C "$REPO_DIR" push origin master
}

ACTION="${1:-link}"
shift || true

case "$ACTION" in
    pull|up|update) cmd_pull ;;
    push) cmd_push "$@" ;;
    status|check) cmd_status ;;
    link|relink)
        verify_links
        echo -e "${GREEN}✓ All Pi configuration symlinks verified.${RESET}"
        ;;
    -h|--help|help)
        echo "Usage: sync-pi [link|status|pull|push [msg]]"
        ;;
    *)
        echo -e "${RED}Unknown command: $ACTION${RESET}"
        exit 1
        ;;
esac
