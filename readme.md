# desktopConfigs

An automated, Ansible-based desktop and server provisioning system for Debian, Ubuntu, and Linux Mint environments.

---

## Quickstart (One-Liner)

On a fresh VM or machine, run this single command to clone the repo into `~/projects/desktopConfigs` (avoiding `$HOME` clutter), install dependencies, and start provisioning:

```bash
# Provision Linux Mint 24/7 Server (No sleep, display sleep, SSH, Docker, Tailscale, CRD):
curl -fsSL https://raw.githubusercontent.com/hubertwwong/linuxDesktopConfig/master/bootstrap.sh | bash -s -- mint-server

# Provision Linux Mint Desktop (XFCE Edition):
curl -fsSL https://raw.githubusercontent.com/hubertwwong/linuxDesktopConfig/master/bootstrap.sh | bash -s -- mint

# Or auto-detect any supported distribution (Debian / Ubuntu / Mint):
curl -fsSL https://raw.githubusercontent.com/hubertwwong/linuxDesktopConfig/master/bootstrap.sh | bash
```

---

## Usage (Cloned Repository)

If you already have the repository cloned, use the `./setup.sh` runner. It automatically installs prerequisites (`git`, `ansible`), prompts for your sudo password (`-K`), and defaults your Git identity from existing config.

```bash
cd ~/projects/desktopConfigs

# Run distro assertion tests (dry verification)
./setup.sh test

# Provision target environments
./setup.sh mint-server # Linux Mint 24/7 Server (No sleep, display sleep, SSH, Docker, CRD)
./setup.sh mint        # Linux Mint Desktop (XFCE Edition)
./setup.sh all         # Auto-detect distribution & desktop
./setup.sh min         # Minimal / headless (CLI tools only)
./setup.sh deb         # Debian with XRDP remote desktop & Syncthing

# Targeted service provisioning
./setup.sh tailscale   # Tailscale mesh VPN & Tailscale SSH
./setup.sh crd         # Chrome Remote Desktop (headless host)
```

Alternatively, you can run standalone helper scripts directly without Ansible:
```bash
./scripts/setup-tailscale.sh              # Quick interactive Tailscale installer
./scripts/setup-chrome-remote-desktop.sh  # Quick interactive CRD installer
```

> [!TIP]
> You can pass standard Ansible flags directly through `./setup.sh`, e.g. `./setup.sh mint-server --check` for a dry run, or `-vv` for extra verbosity.

---

## Supported Distributions & Targets

The system automatically detects your OS distribution and applies matching configurations from [`prod/vars/distros/`](./prod/vars/distros/):

| Target | Description | Recommended For |
| :--- | :--- | :--- |
| **`mint-server` / `server`** | 24/7 Server (power sleep disabled, display sleep enabled, SSH, Tailscale, Docker, CRD) | Always-on mini-PCs, home servers, and Linux Mint workstations |
| **`mint`** | Desktop environment provisioning (XFCE / Cinnamon) | Daily driver laptops and desktops |
| **`all`** | Auto-detected multi-distro setup (Mint, Debian, Ubuntu) | General desktop installations |
| **`min`** | Minimal headless CLI stack (no GUI apps) | Lightweight VPS or compute nodes |
| **`deb`** | Debian workstation with XRDP and Syncthing | Debian VMs and remote machines |

---

## Included Software & Tools

- **Desktop Runtimes & Development**:
  - **VSCode**: Installed via official Microsoft APT repository (native .deb, no Snap).
  - **Mise Polyglot Manager**: Global installations of latest Node.js, Go, Python, `kubectl`, and `helm`.
  - **Docker CE & Compose**: Dynamic distro repository integration with armored keyring verification.
  - **Ghostty Terminal**: Native `.deb` package auto-matched to upstream distro version with `Gruvbox Dark` styling.
  - **Google Chrome**: Official Google APT package repository.
- **Networking & Remote Services**:
  - **Tailscale**: Official Tailscale repository, package installation, and systemd service setup (see [docs/tailscale.md](docs/tailscale.md)).
  - **Chrome Remote Desktop**: Headless remote desktop host via XFCE with dual-session local/remote isolation (see [docs/chrome-remote-desktop.md](docs/chrome-remote-desktop.md)).
  - **OpenSSH Server**: Configured and enabled on server profiles.
- **System & Server Operations**:
  - **24/7 Server Power Management**: Permanently masks systemd sleep/suspend/hibernate targets, configures `systemd-logind` to ignore laptop lid closing and power/suspend buttons, and prevents OS sleep while preserving DPMS display timeout for energy savings.
  - **Dotfiles**: Prompt enhancements and CLI shortcuts (`k`, `mk`, docker aliases).
  - **Desktop Customizations**: Screensaver timeout and lock-screen behavior (`xfconf-query` for XFCE, `gsettings` for GNOME/Cinnamon).
  - **Antigravity Customizations & Skills**: Configures global AGY rules, MCP config, and skills directory (`~/.gemini/config/skills/`) for on-demand progressive disclosure.

---

## Repository Structure

```text
├── bootstrap.sh                 # One-liner remote installer
├── setup.sh                     # Local runner script (handles sudo prompt & args)
├── ansible.cfg                  # Ansible configuration (inventory & output formatting)
├── hosts                        # Localhost inventory definition
├── docs/                        # Detailed architecture & setup documentation
│   ├── mint-server.md           # 24/7 Linux Mint Server setup guide
│   ├── chrome-remote-desktop.md # CRD dual-session remote desktop guide
│   └── tailscale.md             # Tailscale VPN & SSH guide
├── prod/
│   ├── initialSetup/
│   │   ├── site-mint-server.yaml# Linux Mint 24/7 server playbook
│   │   ├── site-all.yaml        # Complete auto-detected desktop playbook
│   │   ├── site-mint.yaml       # Linux Mint XFCE playbook
│   │   ├── site-deb.yaml        # Debian remote desktop playbook
│   │   ├── site-min.yaml        # Minimal headless playbook
│   │   └── roles/               # Modular Ansible roles
│   └── vars/distros/            # Distribution-specific variable overrides
└── test/
    └── test_distro_vars.yaml    # Unit assertions for distro upstream mappings
```
