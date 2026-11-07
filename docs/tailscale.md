# Tailscale Setup & Architecture Guide

This guide details how **Tailscale** is installed, configured, and managed on Debian, Ubuntu, and Linux Mint machines within this repository.

---

## 1. Overview & Architecture

Tailscale creates a secure, peer-to-peer mesh network (a **tailnet**) between your servers, laptops, and mobile devices using WireGuard:

* **No Port Forwarding Required**: Connect securely to your server from anywhere in the world behind NATs, firewalls, and dynamic IPs.
* **Built-in Tailscale SSH**: Connect via SSH (`ssh hubert@<machine-name>`) authenticated via your identity provider (Google, GitHub, etc.) without managing static SSH keys.
* **Non-Root Operator Access**: The current user is granted operator permissions (`tailscale set --operator=$USER`), allowing you to check status and change settings without needing `sudo`.
* **System Daemon**: Runs as `tailscaled.service` managed by `systemd`.

---

## 2. Quick Setup Methods

You can set up Tailscale using any of the following methods:

### Method A: Standalone Quick Script (Fastest)

Run the included installer script:

```bash
cd ~/projects/desktopConfigs
./scripts/setup-tailscale.sh
```

Or run directly on any fresh machine:

```bash
curl -fsSL https://raw.githubusercontent.com/hubertwwong/linuxDesktopConfig/master/scripts/setup-tailscale.sh | bash
```

### Method B: Via Ansible Runner

```bash
cd ~/projects/desktopConfigs
./setup.sh tailscale
```

This runs [`prod/initialSetup/install-tailscale.yaml`](../prod/initialSetup/install-tailscale.yaml) using Ansible.

---

## 3. Authentication & Tailscale SSH

### Interactive Login

After installation, connect your node to your tailnet and enable Tailscale SSH:

```bash
sudo tailscale up --ssh
```

1. Tailscale will display an authentication URL in your terminal:
   ```text
   To authenticate, visit:
           https://login.tailscale.com/a/0123456789ab
   ```
2. Open that URL in any browser, log into your account, and authorize the device.

### Non-Interactive (Headless) Login via Auth Key

If you want to automate login without a web browser (e.g. in automated scripts or CI/CD):

1. Generate a reusable or one-off auth key from the [Tailscale Admin Console](https://login.tailscale.com/admin/settings/keys).
2. Authenticate directly:
   ```bash
   sudo tailscale up --authkey="tskey-auth-kXXXXX-XXXXXXXXXXXX" --ssh
   ```
   Or pass it via Ansible extra variables:
   ```bash
   ./setup.sh tailscale --extra-vars "tailscale_authkey=tskey-auth-..."
   ```

---

## 4. Connecting to Your Server

Once authenticated, your server receives a 100.x.y.z Tailscale IP and a MagicDNS name (e.g. `hubert-thinkcentre`).

### SSH Access
From any other computer or phone on your tailnet:

```bash
ssh hubert@<tailscale-ip>
# or using MagicDNS:
ssh hubert@<hostname>
```

### Remote Desktop via Tailscale
If you run remote desktop (XRDP or Chrome Remote Desktop), you can access services directly over Tailscale without exposing any ports to the public internet:
* Connect to `<tailscale-ip>:3389` for RDP.
* Or use Chrome Remote Desktop knowing your SSH fallback is always available via Tailscale.

---

## 5. Useful Commands & Diagnostics

```bash
# Check connection status and peer list
tailscale status

# View this machine's Tailscale IPv4 and IPv6 addresses
tailscale ip -4

# Check network connectivity, NAT traversal, and latency to DERP relays
tailscale netcheck

# Ping another node on your tailnet via WireGuard
tailscale ping <peer-name-or-ip>

# Check the background daemon service
systemctl status tailscaled
```
