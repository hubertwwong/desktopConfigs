# Linux Mint 24/7 Server Variant

The **Linux Mint Server** variant provisions Linux Mint (Cinnamon, XFCE, or MATE) into a reliable, always-on home/office server or workstation node.

---

## Key Features

1. **24/7 Server Power Management**:
   - **System Power**: Permanently disables sleep, suspend, and hibernation at both the `systemd` level (`sleep.target`, `suspend.target`, `hibernate.target`, `hybrid-sleep.target` masked to `/dev/null`) and user session level (`sleep-inactive-ac-timeout: 0`, `sleep-inactive-ac-type: 'nothing'`).
   - **Lid & Button Controls**: Configures `systemd-logind` to ignore laptop lid close events and sleep buttons (`HandleLidSwitch=ignore`, `IdleAction=ignore`).
   - **Display Sleep (DPMS)**: The physical display is configured to turn off / enter low-power sleep after 10 minutes of inactivity (`600s`), saving electricity and monitor backlight life without putting the server to sleep. Deployed via Xorg DPMS (`/etc/X11/xorg.conf.d/10-dpms.conf`), Cinnamon/GNOME `gsettings`, and user autostart (`~/.config/autostart/dpms.desktop` and `~/.xprofile`).

2. **Remote Access & Networking**:
   - **OpenSSH Server**: `openssh-server` installed, enabled, and started automatically.
   - **Tailscale Mesh VPN**: Seamless remote access across Tailscale network without port forwarding.
   - **Chrome Remote Desktop**: Independent headless GUI access via dedicated display session (`:20`).

3. **Developer & Container Stack**:
   - **Docker CE & Docker Compose**: Native container engine for running server services, databases, and microservices.
   - **Mise Polyglot Manager**: Global versions of Node.js, Go, Python, `kubectl`, and `helm`.
   - **Terminal & Editor**: VS Code (APT), Ghostty terminal, and Antigravity tooling.

4. **Server Operations & Diagnostics**:
   - Includes `tmux`, `htop`, `iotop`, `ufw`, `curl`, `net-tools`, and `git`.

---

## Quickstart

Run directly from the repository:

```bash
cd ~/projects/desktopConfigs

# Provision the Linux Mint 24/7 Server variant
./setup.sh mint-server
# Or alias
./setup.sh server
```

Or run via the one-liner bootstrap installer on a new machine:

```bash
curl -fsSL https://raw.githubusercontent.com/hubertwwong/desktopConfigs/master/bootstrap.sh | bash -s -- mint-server
```

---

## Configuration Variables

In `prod/initialSetup/site-mint-server.yaml` (or overridden via `--extra-vars`):

| Variable | Default | Description |
| :--- | :--- | :--- |
| `disable_server_sleep` | `true` | Masks systemd sleep/suspend/hibernate targets and disables OS idle sleep. |
| `display_sleep_timeout` | `600` | Inactivity timeout in seconds before the physical monitor sleeps (10 mins). Set to `0` for never. |
