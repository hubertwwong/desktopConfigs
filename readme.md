# 🚀 desktopConfigs

> **Automated, Ansible-based desktop & server provisioning for 🐧 Linux Mint, 🌀 Debian, and 🟠 Ubuntu.**

---

> [!NOTE]
> ### 🏛️ Desktop Architecture
> - 🖥️ **Local / Physical Sessions**: Default to **Cinnamon** (standard Linux Mint edition).
> - 🌐 **Remote Desktop Sessions**: Use lightweight **XFCE** on an isolated headless virtual display (`:20` via Chrome Remote Desktop / XRDP) so remote access never conflicts with or disconnects your physical Cinnamon display.

---

## ⚡ Quickstart by Linux Mint Variant

Run any of the one-liners below on a fresh system to clone into `~/projects/desktopConfigs`, auto-install dependencies, and begin provisioning immediately:

### 1. 🖥️ Linux Mint Server (`mint-server` / `server`)
*Designed for always-on mini-PCs (e.g. Lenovo Tiny, Intel NUC), home labs, and headless/server nodes.*

- ⚡ **24/7 Power Lock**: Permanently masks system sleep/hibernate targets; ignores laptop lid switches.
- 💤 **Display Sleep**: Physical display safely enters low-power DPMS sleep after **10 minutes** (`600s`).
- 🔒 **Remote Access**: OpenSSH server enabled & started, Tailscale mesh VPN, Chrome Remote Desktop (isolated XFCE session).
- 🛠️ **Server Stack**: 🐳 Docker CE & Compose, 🌐 Mise, 🐍 Python, 👻 Ghostty, 🤖 Antigravity, 📊 `tmux`, `htop`, `iotop`, `net-tools`, `ufw`.

```bash
# 🚀 One-Liner (Remote):
curl -fsSL https://raw.githubusercontent.com/hubertwwong/desktopConfigs/master/bootstrap.sh | bash -s -- mint-server

# 💻 From Cloned Repo:
./setup.sh mint-server
```

---

### 2. 💻 Linux Mint Desktop Workstation (`mint-desktop` / `desktop` / `mint`)
*Designed for daily-driver physical laptops and desktop workstations.*

- 🎨 **Desktop Environment**: Native **Cinnamon** desktop edition.
- 🔋 **Desktop Power**: Standard desktop power management (normal system suspend/sleep allowed; display sleeps after **10 minutes** DPMS).
- 🛠️ **Productivity Stack**: 📝 VS Code (native APT), 🌐 Google Chrome, 🐳 Docker CE, 🐙 Git, 🌐 Mise polyglot manager, 👻 Ghostty terminal, 🤖 Antigravity, 🔐 KeepassXC, 🎬 media codecs.

```bash
# 🚀 One-Liner (Remote):
curl -fsSL https://raw.githubusercontent.com/hubertwwong/desktopConfigs/master/bootstrap.sh | bash -s -- mint-desktop

# 💻 From Cloned Repo:
./setup.sh mint-desktop
```

---

### 3. 📦 Linux Mint VirtualBox VM (`mint-vm` / `vm`)
*Designed for VirtualBox virtual machines and local test sandboxes.*

- 🔑 **Default Credentials**: User **`vboxuser`** with password **`changeme`**.
- 🛡️ **Permissions**: Passwordless `sudo` (`/etc/sudoers.d/vboxuser`) & added to **`vboxsf`** group for shared folders.
- 🔌 **Guest Integration**: Installs `virtualbox-guest-utils` & `virtualbox-guest-x11` (dynamic resolution resize & shared clipboard).
- ⚡ **VM Stability**: Disables OS suspend/hibernate to eliminate hypervisor freeze and lockup issues.

```bash
# 🚀 One-Liner (Remote):
curl -fsSL https://raw.githubusercontent.com/hubertwwong/desktopConfigs/master/bootstrap.sh | bash -s -- mint-vm

# 💻 From Cloned Repo:
./setup.sh mint-vm
```

---

## 🎯 All Supported Targets

From inside the cloned repository, [`./setup.sh`](file:///home/hubert/projects/desktopConfigs/setup.sh) handles dependencies, prompts for sudo password (`-K`), and configures your environment:

```bash
cd ~/projects/desktopConfigs

# 🧪 Run dry assertion tests for distribution variables
./setup.sh test

# 🐧 Linux Mint Targets
./setup.sh mint-server   # 🖥️ 24/7 Server (No sleep, display DPMS sleep, SSH, Docker, CRD)
./setup.sh mint-desktop  # 💻 Daily-driver workstation (Cinnamon, normal sleep, full stack)
./setup.sh mint-vm       # 📦 VirtualBox VM (vboxuser:changeme, Guest Additions, vboxsf)

# 🌐 General & Multi-Distro Targets
./setup.sh all           # 🌍 Auto-detect distribution & desktop (Mint, Ubuntu, Debian)
./setup.sh min           # 🪶 Minimal headless CLI stack (no GUI applications)
./setup.sh deb           # 🌀 Debian workstation with XRDP & Syncthing

# 🔧 Targeted Service Installers
./setup.sh tailscale     # 🔒 Tailscale mesh VPN & Tailscale SSH
./setup.sh crd           # 🖥️ Chrome Remote Desktop (isolated XFCE virtual host)
./setup.sh herdr         # 🤠 Herdr terminal runtime for AI coding agents
```

> [!TIP]
> 💡 You can pass standard Ansible flags directly through `./setup.sh`, e.g. `./setup.sh mint-server --check` for a dry run, or `-vv` for extra verbosity.

---

## 📊 Target Comparison Matrix

| Target | 🎯 Primary Use | 🖥️ Local Desktop | 🌐 Remote Desktop | 🔑 Credentials | ⚡ System Sleep | 💤 Display Sleep |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`mint-server` / `server`** | 24/7 Server Node | Cinnamon | XFCE (CRD `:20`) | Host User | ❌ Disabled (24/7) | ✅ 10 Min DPMS |
| **`mint-desktop` / `mint`** | Workstation PC | Cinnamon | N/A | Host User | ✅ Enabled (Normal) | ✅ 10 Min DPMS |
| **`mint-vm` / `vm`** | VirtualBox VM | Cinnamon | N/A | `vboxuser` : `changeme` | ❌ Disabled (Anti-Freeze) | ⚙️ Configurable |
| **`all`** | Multi-Distro Setup | Cinnamon / GNOME | N/A | Host User | ✅ Enabled | ✅ 10 Min DPMS |
| **`deb`** | Debian Remote Host | GNOME / Minimal | XFCE (XRDP) | Host User | ✅ Enabled | ✅ Standard |
| **`min`** | Minimal / Headless | None (CLI Only) | None | Host User | ❌ Unmanaged | ❌ Unmanaged |

---

## 📦 Included Software & Tooling

### 🛠️ Developer Runtimes & Applications
- 🤠 **Herdr**: Modern terminal runtime & multiplexer for AI coding agents (see [docs/herdr.md](docs/herdr.md)).
- 📝 **VS Code**: Native `.deb` via official Microsoft APT repository (no Snap bloat).
- 🌐 **Mise Polyglot Manager**: Global installations of latest Node.js, Go, Python, `kubectl`, and `helm`.
- 🐳 **Docker CE & Compose**: Dynamic repository integration with armored keyring verification.
- 👻 **Ghostty Terminal**: Native `.deb` auto-matched to upstream distro release with `Gruvbox Dark` styling.
- 🌐 **Google Chrome**: Official Google APT package repository.

### 🔒 Networking & Remote Access
- 🔒 **Tailscale Mesh VPN**: Official Tailscale repository, client packages, and systemd service (see [docs/tailscale.md](docs/tailscale.md)).
- 🔄 **Syncthing P2P File Sync**: Continuous cross-device synchronization and canonical folder ID mapping (see [docs/syncthing.md](docs/syncthing.md)).
- 🖥️ **Chrome Remote Desktop**: Headless virtual host via XFCE with dual-session local/remote isolation (see [docs/chrome-remote-desktop.md](docs/chrome-remote-desktop.md)).
- 🔑 **OpenSSH Server**: Configured, enabled, and started automatically on server profiles.

### 🔐 Secret & Credential Management
- 🔐 **Proton Pass & KeePassXC Workflow**: Offline, PGP-encrypted Syncthing backups and CLI credential injection (see [docs/proton-pass-backup.md](docs/proton-pass-backup.md)).

### ⚡ System & Power Management
- 🔋 **Server Power Lock**: Permanently masks systemd sleep/suspend/hibernate targets; ignores lid switches and sleep buttons.
- 💤 **DPMS Display Sleep**: Multi-layer monitor blanking across Xorg server (`/etc/X11/xorg.conf.d/10-dpms.conf`), autostart entries, and desktop `gsettings`.
- 📦 **VirtualBox Guest Suite**: `virtualbox-guest-utils`, `vboxsf` shared folder permissions, and passwordless sudo for `vboxuser`.

---

## 📁 Repository Structure

```text
├── 🚀 bootstrap.sh                 # One-liner remote installer
├── 📜 setup.sh                     # Local runner script (handles sudo prompt & args)
├── ⚙️ ansible.cfg                  # Ansible configuration (inventory & output formatting)
├── 📋 hosts                        # Localhost inventory definition
├── 📚 docs/                        # Detailed architecture & setup documentation
│   ├── 📑 mint-variants.md         # Linux Mint variants guide (Server, Desktop, VM)
│   ├── 🖥️ mint-server.md           # 24/7 Linux Mint Server setup guide
│   ├── 🤠 herdr.md                 # Herdr terminal runtime for AI agents guide
│   ├── 🌐 chrome-remote-desktop.md # CRD dual-session remote desktop guide
│   ├── 🔒 tailscale.md             # Tailscale VPN & SSH guide
│   ├── 🔄 syncthing.md             # Syncthing cluster & folder ID mapping
│   └── 🔐 proton-pass-backup.md    # Proton Pass & KeePassXC local credential workflow
├── 📦 prod/
│   ├── 🛠️ initialSetup/
│   │   ├── 🖥️ site-mint-server.yaml  # Linux Mint 24/7 server playbook
│   │   ├── 💻 site-mint-desktop.yaml # Linux Mint desktop workstation playbook
│   │   ├── 📦 site-mint-vm.yaml      # Linux Mint VirtualBox VM playbook
│   │   ├── 🌍 site-all.yaml          # Complete auto-detected desktop playbook
│   │   ├── 🌀 site-deb.yaml          # Debian remote desktop playbook
│   │   ├── 🪶 site-min.yaml          # Minimal headless playbook
│   │   └── 🧩 roles/                 # Modular Ansible roles
│   └── 🏷️ vars/distros/            # Distribution-specific variable overrides
└── 🧪 test/
    └── 🔍 test_distro_vars.yaml    # Unit assertions for distro upstream mappings
```
