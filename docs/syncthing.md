# 🔄 Syncthing Cluster & Folder Reference

This document tracks the shared folder IDs and configuration topology for Syncthing across your Linux machines, Windows desktop, and mobile devices.

---

## 📋 Canonical Shared Folders

When connecting a new device or re-provisioning a system, matching the **Folder ID** ensures Syncthing links directly to the existing cluster data without duplicates.

| Folder Label | Example Folder ID | Default Linux Mount Path | Purpose |
| :--- | :--- | :--- | :--- |
| **`workspace`** | `<your-workspace-id>` | `/media/hubert/Elements/syncthing/workspace` | Primary development repos, notes, and local backups |
| **`tmp`** | `<your-tmp-id>` | `/media/hubert/Elements/syncthing/tmp` | Cross-device dropzone for scratch files & transfers |
| **`mobileMisc`** | `<your-mobilemisc-id>` | `/media/hubert/Elements/syncthing/mobileMisc` | General mobile device file sync |
| **`mobileVids`** | `<your-mobilevids-id>` | `/media/hubert/Elements/syncthing/mobileVids` | Camera & video captures from mobile |

> [!TIP]
> Keep your active cluster Folder IDs in your private Syncthing `workspace/backups/proton-pass/README.md` so they sync peer-to-peer across your hardware without being published to public repositories.

---

## 🏛️ Device Philosophy: Ephemeral Node Identity

- **No Need to Back Up Device Keys:** Syncthing device identity keys (`cert.pem` and `key.pem`) do not need to be preserved.
- When provisioning a new machine (or rebuilding via Ansible):
  1. Install Syncthing (let it generate a fresh Device ID automatically).
  2. Open the Syncthing Web GUI (`http://127.0.0.1:8384` on local, or via Tailscale).
  3. Accept the pairing request from your other machine.
  4. Share the desired folders using the **Folder IDs** in the table above.

---

## 🔐 Encrypted Backup Subfolder

The `workspace` folder includes the offline, PGP-encrypted credential backups:
- **Path:** `/media/hubert/Elements/syncthing/workspace/backups/proton-pass/`
- **Docs:** See [docs/proton-pass-backup.md](proton-pass-backup.md) for verification commands and KeePassXC integration.

---

## 🛠️ Service Management (Linux)

Syncthing runs as a systemd user service:

```bash
# Check service status
systemctl --user status syncthing

# Restart Syncthing service
systemctl --user restart syncthing

# View live service logs
journalctl --user -u syncthing -f
```

Web GUI default URL: `http://127.0.0.1:8384`
