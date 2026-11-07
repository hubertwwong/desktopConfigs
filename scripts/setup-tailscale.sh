#!/usr/bin/env bash
# ==============================================================================
# setup-tailscale.sh - Quick Standalone Tailscale Installer & Configurator
# Compatible with: Debian, Ubuntu, Linux Mint
# ==============================================================================
set -e

echo "======================================================================"
echo " Tailscale Quick Installer"
echo "======================================================================"

# 1. Check root / sudo
if ! command -v sudo &>/dev/null && [ "$EUID" -ne 0 ]; then
    echo "Error: sudo is required to install Tailscale."
    exit 1
fi

SUDO="sudo"
[ "$EUID" -eq 0 ] && SUDO=""

# 2. Detect Distribution and Upstream Release
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO_ID="$ID"
    CODENAME="${VERSION_CODENAME:-$UBUNTU_CODENAME}"
else
    echo "Error: Cannot detect OS distribution (/etc/os-release missing)."
    exit 1
fi

# Map derivatives (e.g. Linux Mint) to upstream
UPSTREAM_DISTRO="$DISTRO_ID"
UPSTREAM_CODENAME="$CODENAME"

if [ "$DISTRO_ID" = "linuxmint" ]; then
    UPSTREAM_DISTRO="ubuntu"
    UPSTREAM_CODENAME="${UBUNTU_CODENAME:-noble}"
fi

echo "==> Detected OS: $PRETTY_NAME"
echo "==> Tailscale repository target: $UPSTREAM_DISTRO ($UPSTREAM_CODENAME)"

# 3. Install prerequisites
echo "==> Ensuring curl and gpg are installed..."
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq curl gnupg apt-transport-https

# 4. Install Tailscale GPG key and APT repository
echo "==> Adding Tailscale repository..."
$SUDO mkdir -p /usr/share/keyrings
curl -fsSL "https://pkgs.tailscale.com/stable/${UPSTREAM_DISTRO}/${UPSTREAM_CODENAME}.noarmor.gpg" \
    | $SUDO tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null

echo "deb [signed-by=/usr/share/keyrings/tailscale-archive-keyring.gpg] https://pkgs.tailscale.com/stable/${UPSTREAM_DISTRO} ${UPSTREAM_CODENAME} main" \
    | $SUDO tee /etc/apt/sources.list.d/tailscale.list >/dev/null

# 5. Install Tailscale
echo "==> Installing Tailscale package..."
$SUDO apt-get update -qq
$SUDO apt-get install -y tailscale

# 6. Enable and start daemon
echo "==> Enabling and starting tailscaled service..."
$SUDO systemctl enable --now tailscaled

# 7. Set operator permission for non-root user
CURRENT_USER="${SUDO_USER:-$USER}"
if [ "$CURRENT_USER" != "root" ]; then
    echo "==> Granting Tailscale operator rights to '$CURRENT_USER'..."
    $SUDO tailscale set --operator="$CURRENT_USER" 2>/dev/null || true
fi

# 8. Check login status
echo "----------------------------------------------------------------------"
if tailscale status 2>/dev/null | grep -vq "Logged out"; then
    echo "Tailscale is already authenticated and active!"
    tailscale status
    echo "Tailscale IP: $(tailscale ip -4 2>/dev/null || echo 'N/A')"
else
    echo "Tailscale is installed and running."
    echo ""
    echo "To authenticate this machine and enable Tailscale SSH, run:"
    echo "  sudo tailscale up --ssh"
    echo ""
    read -p "Would you like to run 'sudo tailscale up --ssh' now? [Y/n] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        $SUDO tailscale up --ssh
        echo ""
        echo "Authentication complete! Your Tailscale IP is:"
        tailscale ip -4 2>/dev/null || true
    fi
fi
echo "======================================================================"
