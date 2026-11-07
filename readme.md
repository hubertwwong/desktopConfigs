# desktopConfigs

Automated, Ansible-based desktop and server provisioning for **Linux Mint**, **Debian**, and **Ubuntu**.

> [!NOTE]
> **Desktop Architecture**:
> - **Local / Physical Sessions**: Default to **Cinnamon** (standard Linux Mint edition).
> - **Remote Desktop Sessions**: Use lightweight **XFCE** on an isolated virtual display (`:20` via Chrome Remote Desktop / XRDP) so remote access never conflicts with or hijacks the physical Cinnamon display.

---

## Quickstart by Linux Mint Variant

Run any of the one-liners below on a fresh machine to clone into `~/projects/desktopConfigs`, install prerequisites, and start provisioning immediately:

### 1. 🖥️ Linux Mint Server (`mint-server` / `server`)
For always-on mini-PCs, home servers, or workstation nodes.
- **Power**: 24/7 server power lock (OS never sleeps/hibernates, lid close ignored; display sleeps after 10 min DPMS).
- **Remote Access & Services**: OpenSSH server enabled & started, Tailscale VPN, Chrome Remote Desktop (isolated XFCE session).
- **Stack**: Docker CE, Mise, Python, Ghostty, Antigravity, `tmux`, `htop`, `iotop`, `net-tools`, `ufw`.

```bash
# One-Liner (Remote):
curl -fsSL https://raw.githubusercontent.com/hubertwwong/linuxDesktopConfig/master/bootstrap.sh | bash -s -- mint-server

# Cloned Repo:
./setup.sh mint-server
```

---

### 2. 💻 Linux Mint Desktop Workstation (`mint-desktop` / `desktop` / `mint`)
For daily-driver physical laptops and desktop workstations.
- **Desktop**: Native **Cinnamon** environment.
- **Power**: Standard desktop power management (normal system suspend/sleep enabled; display sleeps after 10 min DPMS).
- **Stack**: VS Code (APT), Google Chrome, Docker CE, Git, Mise polyglot runtimes, Ghostty terminal, Antigravity tooling, KeepassXC, media codecs.

```bash
# One-Liner (Remote):
curl -fsSL https://raw.githubusercontent.com/hubertwwong/linuxDesktopConfig/master/bootstrap.sh | bash -s -- mint-desktop

# Cloned Repo:
./setup.sh mint-desktop
```

---

### 3. 📦 Linux Mint VirtualBox VM (`mint-vm` / `vm`)
For VirtualBox virtual machines and local test sandboxes.
- **Credentials**: User **`vboxuser`** with password **`changeme`**.
- **Permissions**: Grants passwordless `sudo` and adds `vboxuser` to the **`vboxsf`** group for shared folders.
- **Integration**: Installs `virtualbox-guest-utils` & `virtualbox-guest-x11` (auto-resize display & shared clipboard).
- **Power**: Disables OS suspend/hibernate to prevent hypervisor freeze.

```bash
# One-Liner (Remote):
curl -fsSL https://raw.githubusercontent.com/hubertwwong/linuxDesktopConfig/master/bootstrap.sh | bash -s -- mint-vm

# Cloned Repo:
./setup.sh mint-vm
```

---

## All Supported Targets

From inside the cloned repository, `./setup.sh` handles dependencies, prompts for sudo password (`-K`), and defaults your Git identity:

```bash
cd ~/projects/desktopConfigs

# Verify distro variables (dry assertion test)
./setup.sh test

# Linux Mint Targets
./setup.sh mint-server   # 24/7 Server (No sleep, display sleep, SSH, Docker, CRD)
./setup.sh mint-desktop  # Daily-driver desktop workstation (Cinnamon, normal sleep)
./setup.sh mint-vm       # VirtualBox VM (vboxuser:changeme, Guest Additions, vboxsf)

# General / Multi-Distro Targets
./setup.sh all           # Auto-detect distribution & desktop (Mint, Ubuntu, Debian)
./setup.sh min           # Minimal headless CLI stack (no GUI apps)
./setup.sh deb           # Debian workstation with XRDP & Syncthing

# Standalone Service Targets
./setup.sh tailscale     # Tailscale mesh VPN & SSH setup
./setup.sh crd           # Chrome Remote Desktop (isolated XFCE virtual host)
```

Alternatively, run standalone interactive installers directly:
```bash
./scripts/setup-tailscale.sh              # Quick interactive Tailscale installer
./scripts/setup-chrome-remote-desktop.sh  # Quick interactive CRD installer
```

---

## Target Matrix

| Target | Description | Local Desktop | Remote Desktop | Credentials | Power Profile |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`mint-server` / `server`** | 24/7 Server Node | Cinnamon | XFCE (CRD `:20`) | Host user | System sleep disabled; Display sleeps (10m) |
| **`mint-desktop` / `mint`** | Workstation PC | Cinnamon | N/A | Host user | Standard desktop sleep; Display sleeps (10m) |
| **`mint-vm` / `vm`** | VirtualBox VM | Cinnamon | N/A | `vboxuser` : `changeme` | Sleep disabled (prevents VM freeze) |
| **`all`** | Auto-detected multi-distro | Auto (Cinnamon/GNOME) | N/A | Host user | Standard desktop |
| **`deb`** | Debian remote host | GNOME / Minimal | XFCE (XRDP) | Host user | Standard desktop |
| **`min`** | Minimal / Headless | None (CLI only) | None | Host user | Minimal headless |

---

## Included Software & Tools

- **Development Runtimes**:
  - **VS Code**: Native `.deb` via official Microsoft APT repository (no Snap).
  - **Mise Polyglot Manager**: Global Node.js, Go, Python, `kubectl`, and `helm`.
  - **Docker CE & Compose**: Dynamic distro repository integration with armored keyring verification.
  - **Ghostty Terminal**: Native `.deb` package auto-matched to upstream distro version with `Gruvbox Dark` styling.
  - **Google Chrome**: Official Google APT package repository.
- **Networking & Remote Services**:
  - **Tailscale**: Official Tailscale repository, package installation, and systemd service setup (see [docs/tailscale.md](docs/tailscale.md)).
  - **Chrome Remote Desktop**: Headless remote desktop host via XFCE with dual-session local/remote isolation (see [docs/chrome-remote-desktop.md](docs/chrome-remote-desktop.md)).
  - **OpenSSH Server**: Configured and enabled on server profiles.
- **System & Power Management**:
  - **Power Profiles**: 24/7 server mode (systemd masked, lid close ignored) vs standard desktop mode.
  - **DPMS Display Sleep**: Multi-layer display blanking (`/etc/X11/xorg.conf.d/10-dpms.conf`, `~/.config/autostart/dpms.desktop`, `gsettings`).
  - **VirtualBox Integration**: `virtualbox-guest-utils`, `vboxsf` group permissions, and passwordless sudo for `vboxuser`.

---

## Repository Structure

```text
├── bootstrap.sh                 # One-liner remote installer
├── setup.sh                     # Local runner script (handles sudo prompt & args)
├── ansible.cfg                  # Ansible configuration (inventory & output formatting)
├── hosts                        # Localhost inventory definition
├── docs/                        # Detailed architecture & setup documentation
│   ├── mint-variants.md         # Linux Mint variants guide (Server, Desktop, VM)
│   ├── mint-server.md           # 24/7 Linux Mint Server setup guide
│   ├── chrome-remote-desktop.md # CRD dual-session remote desktop guide
│   └── tailscale.md             # Tailscale VPN & SSH guide
├── prod/
│   ├── initialSetup/
│   │   ├── site-mint-server.yaml  # Linux Mint 24/7 server playbook
│   │   ├── site-mint-desktop.yaml # Linux Mint desktop workstation playbook
│   │   ├── site-mint-vm.yaml      # Linux Mint VirtualBox VM playbook
│   │   ├── site-all.yaml          # Complete auto-detected desktop playbook
│   │   ├── site-deb.yaml          # Debian remote desktop playbook
│   │   ├── site-min.yaml          # Minimal headless playbook
│   │   └── roles/                 # Modular Ansible roles
│   └── vars/distros/            # Distribution-specific variable overrides
└── test/
    └── test_distro_vars.yaml    # Unit assertions for distro upstream mappings
```
