#!/usr/bin/env bash
# ==============================================================================
# Standalone Herdr Terminal Multiplexer Installer
# ==============================================================================
set -e

echo "======================================================================"
echo " Installing Herdr (https://herdr.dev)"
echo " Terminal Runtime & Multiplexer for AI Coding Agents"
echo "======================================================================"

mkdir -p "$HOME/.local/bin"
export HERDR_INSTALL_DIR="${HERDR_INSTALL_DIR:-$HOME/.local/bin}"

curl -fsSL https://herdr.dev/install.sh | sh

# Ensure PATH is configured
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    export PATH="$HOME/.local/bin:$PATH"
    if [ -f "$HOME/.bashrc" ] && ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
fi

echo "==> Verifying installation:"
if command -v herdr &>/dev/null; then
    herdr --version
    echo "==> Herdr is ready to use! Run 'herdr' to launch."
else
    "$HOME/.local/bin/herdr" --version
    echo "==> Herdr installed to $HOME/.local/bin/herdr."
fi
