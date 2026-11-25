# Chrome Remote Desktop Setup & Architecture Guide

This guide details how **Chrome Remote Desktop (CRD)** is installed, configured, and run in headless / server mode on Debian, Ubuntu, and Linux Mint systems.

---

## 1. Overview & Architecture

Chrome Remote Desktop allows secure remote access to your Linux machine via any Chrome browser or mobile app.

* **Daemon Service**: Managed by `systemd` via the template service `chrome-remote-desktop@<username>.service`.
* **Virtual Display**: Runs an isolated virtual X11 display (typically `:20`), separate from any physical local display attached to the machine (typically `:0`).
* **Desktop Environment**: Uses XFCE (`startxfce4`) inside the virtual session for low memory overhead, rock-solid stability, and fast streaming performance.
* **Dual-Session Isolation**: A custom session startup wrapper (`~/.chrome-remote-desktop-session`) prevents environment variables (such as DBUS, PulseAudio, and DISPLAY) from leaking between your physical local session (e.g. Cinnamon on `:0`) and the virtual remote session (`:20`).

---

## 2. Quick Setup Methods

### Method A: Standalone Quick Script (Fastest)

Run the included installer script:

```bash
cd ~/projects/desktopConfigs
./scripts/setup-chrome-remote-desktop.sh
```

Or run directly on any fresh machine:

```bash
curl -fsSL https://raw.githubusercontent.com/hubertwwong/desktopConfigs/master/scripts/setup-chrome-remote-desktop.sh | bash
```

The script installs all dependencies, deploys the isolated session wrapper, and prompts you to paste the authorization command from Google.

### Method B: Via Ansible Runner

```bash
cd ~/projects/desktopConfigs
./setup.sh crd
```

This provisions Chrome Remote Desktop using the Ansible role in [`prod/initialSetup/roles/chrome_remote_desktop/`](../prod/initialSetup/roles/chrome_remote_desktop/).

---

## 3. Prerequisites

The following packages are required on the host system:

* **XFCE & Session Tools**: `xfce4`, `xfce4-session`, `dbus-x11`, `xvfb`, `xbase-clients`, `python3-psutil`
* **Google Chrome**: Stable release installed via the official Google APT repository.
* **Chrome Remote Desktop**: `.deb` package installed from `https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb`.

---

## 4. The Session Configuration (`~/.chrome-remote-desktop-session`)

To prevent virtual remote sessions from hijacking local display and audio channels, the session script unsets inherited Chrome Remote Desktop variables from the user's `systemd --user` environment before launching XFCE.

File location: `~/.chrome-remote-desktop-session` (must be executable `chmod +x`):

```sh
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
```

---

## 5. Initial Setup & Authorization (Headless)

Because Google OAuth authorization requires your Google Account credentials, host linking is done via Google's headless authorization portal:

1. On any browser where you are signed into your Google account, open:
   👉 **[https://remotedesktop.google.com/headless](https://remotedesktop.google.com/headless)**
2. Click **Set up another computer** and click **Begin**.
3. Click **Next**, then **Authorize**.
4. Google will generate a command for Debian Linux that looks like this:
   ```bash
   DISPLAY= /opt/google/chrome-remote-desktop/start-host \
     --code="4/0Axxxxxxxxxxxxxx..." \
     --redirect-url="https://remotedesktop.google.com/_/oauthredirect" \
     --name=$(hostname)
   ```
5. Paste and run that command in your terminal on the server machine.
6. When prompted, enter a **6-digit PIN** (and confirm it). This PIN is required when connecting from client devices.

---

## 6. Service Management

Once authorized, the service is managed automatically by `systemd`:

```bash
# Check service status
systemctl status chrome-remote-desktop@$USER.service

# Restart the service
sudo systemctl restart chrome-remote-desktop@$USER.service

# View live service logs
journalctl -u chrome-remote-desktop@$USER.service -f
```

Host authorization files and persistent tokens are stored in:
* `~/.config/chrome-remote-desktop/host#<host-id>.json`

---

## 7. Troubleshooting

* **Blank/Grey Screen upon connection**:
  Verify `~/.chrome-remote-desktop-session` exists, is marked executable (`chmod +x ~/.chrome-remote-desktop-session`), and that `xfce4` and `dbus-x11` are installed.
* **Authentication expired or host offline**:
  Re-run the authorization command from [remotedesktop.google.com/headless](https://remotedesktop.google.com/headless).
* **Display Resolution**:
  You can resize the virtual desktop dynamically from the Chrome Remote Desktop slide-out side menu by selecting **"Resize desktop to fit"**.
