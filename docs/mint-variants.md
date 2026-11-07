# Linux Mint Provisioning Variants

`desktopConfigs` provides three tailored variants for Linux Mint depending on your deployment target:

---

## Comparison Summary

| Feature / Setting | 🖥️ Server (`mint-server` / `server`) | 💻 Desktop (`mint-desktop` / `desktop` / `mint`) | 📦 VirtualBox VM (`mint-vm` / `vm`) |
| :--- | :--- | :--- | :--- |
| **Primary Use Case** | Always-on home/office server or node | Daily-driver physical laptop or desktop | VirtualBox virtual machine |
| **Credentials** | Existing user / host credentials | Existing user / host credentials | `vboxuser` / `changeme` (passwordless sudo) |
| **System Sleep / Suspend** | **Disabled** (systemd targets masked to `/dev/null`) | **Enabled** (standard desktop sleep/suspend) | **Disabled** (prevents VM hypervisor freeze) |
| **Display Sleep (DPMS)** | **Enabled** (turns off monitor after 10m / 600s) | **Enabled** (turns off monitor after 10m / 600s) | Disabled / Generous (`0` or configurable) |
| **Lid Close Action** | Ignore lid switch (never suspend) | Standard desktop blank / suspend | N/A |
| **VirtualBox Guest Additions** | No | No | **Yes** (`virtualbox-guest-utils`, `x11`, `vboxsf` group) |
| **OpenSSH Server** | **Yes** (installed, enabled, started) | Optional / default | Optional / default |
| **Tailscale VPN** | Yes | Yes | Yes |
| **Chrome Remote Desktop** | Yes | Optional | Optional |
| **Docker CE & Compose** | Yes | Yes | Yes |
| **Mise, VS Code, Git, Ghostty** | Yes | Yes | Yes |

---

## 1. Linux Mint Server (`mint-server` / `server`)

Designed for dedicated servers, mini-PCs (e.g. Lenovo Tiny, Intel NUC), or always-on headless/semi-headless workstations.

- **Power Management**:
  - Permanently masks `sleep.target`, `suspend.target`, `hibernate.target`, `hybrid-sleep.target`.
  - Sets `systemd-logind` to ignore lid close and sleep button presses.
  - Keeps display DPMS active (10 minutes) to save monitor power and backlight without suspending the server.
- **Services**:
  - OpenSSH server running out of the box.
  - Tailscale mesh networking.
  - Chrome Remote Desktop (headless `:20` display session).
  - Server diagnostics: `tmux`, `htop`, `iotop`, `net-tools`, `ufw`.

**Usage**:
```bash
./setup.sh mint-server
# or
./setup.sh server
```

---

## 2. Linux Mint Desktop (`mint-desktop` / `desktop` / `mint`)

Designed for daily-driver laptops and physical desktop workstations running Cinnamon or XFCE.

- **Power Management**:
  - Normal desktop sleep and power management preserved.
  - Display turns off after 10 minutes of inactivity (`600s`).
- **Software Suite**:
  - Full desktop tooling, KeepassXC, media codecs (`libavcodec-extra`), VS Code, Docker, Mise polyglot runtimes, Ghostty terminal, and Antigravity tooling.

**Usage**:
```bash
./setup.sh mint-desktop
# or
./setup.sh desktop
# or
./setup.sh mint
```

---

## 3. Linux Mint VirtualBox VM (`mint-vm` / `vm`)

Designed specifically for VirtualBox virtual machines and local development sandboxes.

- **Credentials & Access**:
  - Configures user: **`vboxuser`**
  - Password: **`changeme`**
  - Grants passwordless sudo access via `/etc/sudoers.d/vboxuser`.
  - Adds `vboxuser` to the **`vboxsf`** group for seamless access to VirtualBox Shared Folders.
- **Guest Additions**:
  - Installs and enables `virtualbox-guest-utils` and `virtualbox-guest-x11` for dynamic screen resizing and shared clipboard integration.
- **VM Power Management**:
  - Disables OS suspend/hibernate to prevent hypervisor state corruption and freeze issues.

**Usage**:
```bash
./setup.sh mint-vm
# or
./setup.sh vm
```
