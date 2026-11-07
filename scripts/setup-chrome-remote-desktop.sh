#!/usr/bin/env bash
# ==============================================================================
# setup-chrome-remote-desktop.sh - Standalone Chrome Remote Desktop Setup
# Sets up headless XFCE remote desktop with dual-session isolation
# ==============================================================================
set -e

echo "======================================================================"
echo " Chrome Remote Desktop Quick Installer"
echo "======================================================================"

# 1. Determine user and sudo
if ! command -v sudo &>/dev/null && [ "$EUID" -ne 0 ]; then
    echo "Error: sudo is required to install system packages."
    exit 1
fi

SUDO="sudo"
[ "$EUID" -eq 0 ] && SUDO=""

TARGET_USER="${SUDO_USER:-$USER}"
TARGET_HOME=$(getent passwd "$TARGET_USER" | cut -d: -f6)

echo "==> Setting up for user: $TARGET_USER ($TARGET_HOME)"

# 2. Install desktop session prerequisites
echo "==> Installing XFCE session and headless display prerequisites..."
$SUDO apt-get update -qq
$SUDO apt-get install -y \
    xfce4 \
    xfce4-session \
    dbus-x11 \
    xvfb \
    xbase-clients \
    python3-psutil \
    curl \
    wget

# 3. Install Google Chrome (if missing)
if ! command -v google-chrome &>/dev/null; then
    echo "==> Installing Google Chrome..."
    wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    $SUDO apt-get install -y /tmp/google-chrome.deb
    rm -f /tmp/google-chrome.deb
else
    echo "==> Google Chrome is already installed."
fi

# 4. Install Chrome Remote Desktop package
echo "==> Downloading and installing Chrome Remote Desktop..."
wget -q -O /tmp/chrome-remote-desktop.deb https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
$SUDO apt-get install -y /tmp/chrome-remote-desktop.deb
rm -f /tmp/chrome-remote-desktop.deb

# 5. Deploy ~/.chrome-remote-desktop-session with dual-session isolation
echo "==> Deploying $TARGET_HOME/.chrome-remote-desktop-session..."
cat << 'EOF' | $SUDO -u "$TARGET_USER" tee "$TARGET_HOME/.chrome-remote-desktop-session" >/dev/null
#!/bin/sh
# Keep systemd --user clean so a concurrent local Cinnamon (:0) session's
# apps, audio, GPU, and Chrome are not redirected to the virtual CRD session.
systemctl --user unset-environment \
  CHROME_CONFIG_HOME \
  CHROME_REMOTE_DESKTOP_AUDIO_PIPE \
  CHROME_REMOTE_DESKTOP_SESSION \
  CHROME_USER_DATA_DIR \
  GDK_BACKEND \
  LD_LIBRARY_PATH \
  PIPEWIRE_REMOTE \
  PULSE_CONFIG_PATH \
  PULSE_RUNTIME_PATH \
  PULSE_SINK \
  PULSE_STATE_PATH >/dev/null 2>&1 || true

if [ -S /tmp/.X11-unix/X0 ] && pgrep -u "$USER" -x cinnamon-session-binary >/dev/null 2>&1; then
  systemctl --user set-environment DISPLAY=:0 XDG_CURRENT_DESKTOP=X-Cinnamon >/dev/null 2>&1 || true
fi

unset DBUS_SESSION_BUS_ADDRESS
unset SESSION_MANAGER
exec /usr/bin/dbus-run-session -- /usr/bin/startxfce4
EOF

chmod +x "$TARGET_HOME/.chrome-remote-desktop-session"
chown "$TARGET_USER":"$TARGET_USER" "$TARGET_HOME/.chrome-remote-desktop-session"

# 6. Enable systemd user service
echo "==> Enabling chrome-remote-desktop@$TARGET_USER.service..."
$SUDO systemctl enable "chrome-remote-desktop@${TARGET_USER}.service"

# 7. Authorization instructions
echo ""
echo "======================================================================"
echo " Chrome Remote Desktop is installed and configured!"
echo "======================================================================"
echo ""
echo "To link this machine to your Google Account (Headless Setup):"
echo ""
echo "  1. On any browser signed into your Google Account, open:"
echo "     👉 https://remotedesktop.google.com/headless"
echo ""
echo "  2. Click 'Set up another computer' -> 'Begin' -> 'Next' -> 'Authorize'"
echo "  3. Copy the command generated for 'Debian Linux', which looks like:"
echo "     DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=... --name=..."
echo ""
echo "  4. Paste and execute that command right here, and enter your 6-digit PIN."
echo ""
read -p "Would you like to paste and run your authorization command now? [y/N] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Paste the full command: " AUTH_CMD
    if [ -n "$AUTH_CMD" ]; then
        eval "$AUTH_CMD"
        echo ""
        echo "==> Verifying service status..."
        $SUDO systemctl restart "chrome-remote-desktop@${TARGET_USER}.service"
        systemctl status "chrome-remote-desktop@${TARGET_USER}.service" --no-pager
    fi
else
    echo "You can run the authorization command whenever you are ready."
    echo "Check status later with: systemctl status chrome-remote-desktop@$TARGET_USER.service"
fi
echo "======================================================================"
