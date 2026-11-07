#!/usr/bin/env bash
# ==============================================================================
# desktopConfigs - Streamlined Provisioning & Test Runner
# ==============================================================================
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

# 1. Install prerequisites if missing
if ! command -v ansible-playbook &>/dev/null; then
    echo "==> Ansible not found. Installing git and ansible..."
    sudo apt update && sudo apt install -y git ansible
fi

# 2. Parse target and arguments
TARGET=""
EXTRA_ARGS=()

for arg in "$@"; do
    case "$arg" in
        all|mint|mint-server|server|mint-desktop|desktop|mint-vm|vm|deb|min|test|tailscale|crd|herdr)
            if [ -z "$TARGET" ]; then
                TARGET="$arg"
            else
                EXTRA_ARGS+=("$arg")
            fi
            ;;
        *)
            EXTRA_ARGS+=("$arg")
            ;;
    esac
done

TARGET="${TARGET:-all}"

# 3. Handle 'test' target
if [ "$TARGET" = "test" ]; then
    echo "==> Running distribution variable assertions (test/test_distro_vars.yaml)..."
    ansible-playbook test/test_distro_vars.yaml "${EXTRA_ARGS[@]}"
    exit 0
fi

# 4. Resolve provisioning playbook
if [ "$TARGET" = "tailscale" ]; then
    PLAYBOOK="prod/initialSetup/install-tailscale.yaml"
elif [ "$TARGET" = "crd" ]; then
    PLAYBOOK="prod/initialSetup/install-crd.yaml"
elif [ "$TARGET" = "herdr" ]; then
    PLAYBOOK="prod/initialSetup/install-herdr.yaml"
elif [ "$TARGET" = "mint-server" ] || [ "$TARGET" = "server" ]; then
    PLAYBOOK="prod/initialSetup/site-mint-server.yaml"
elif [ "$TARGET" = "mint-vm" ] || [ "$TARGET" = "vm" ]; then
    PLAYBOOK="prod/initialSetup/site-mint-vm.yaml"
elif [ "$TARGET" = "mint-desktop" ] || [ "$TARGET" = "desktop" ] || [ "$TARGET" = "mint" ]; then
    PLAYBOOK="prod/initialSetup/site-mint-desktop.yaml"
else
    PLAYBOOK="prod/initialSetup/site-${TARGET}.yaml"
fi

if [ ! -f "$PLAYBOOK" ]; then
    echo "Error: Playbook '$PLAYBOOK' not found."
    echo "Usage: ./setup.sh [all|mint|mint-server|server|mint-desktop|desktop|mint-vm|vm|deb|min|test|tailscale|crd|herdr] [ansible-playbook options...]"
    exit 1
fi

echo "======================================================================"
echo " Starting Provisioning: $TARGET ($PLAYBOOK)"
echo " Password prompt (-K / --ask-become-pass) enabled for sudo tasks."
echo "======================================================================"

# 5. Run playbook with -K for sudo password prompt
ansible-playbook -K -v "$PLAYBOOK" "${EXTRA_ARGS[@]}"
