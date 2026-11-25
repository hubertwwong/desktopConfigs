# 🔐 Proton Pass & Local KeePassXC Credential Workflow

This guide details how offline, encrypted password backups and local workspace credentials are managed across Linux and Windows machines using **Proton Pass**, **GPG**, **Syncthing**, and **KeePassXC**.

---

## 🏛️ Architecture & Security Model

```
┌─────────────────┐       Browser Export        ┌────────────────────────────────────────────────────────┐
│   Proton Pass   │ ─────────────────────────>  │  Syncthing Workspace Backup (OpenPGP AES-256)         │
│  (Cloud Vault)  │    (AES-256 PGP Zip)        │  /media/hubert/Elements/syncthing/workspace/backups/   │
└─────────────────┘                             └────────────────────────────────────────────────────────┘
                                                                            │
                                                                            │  sync-proton-vault
                                                                            ▼
                                                ┌────────────────────────────────────────────────────────┐
                                                │  Local Encrypted KeePassXC Database (.kdbx4)           │
                                                │  ~/vault.kdbx (chmod 600, Argon2id + ChaCha20/AES)     │
                                                └────────────────────────────────────────────────────────┘
                                                                            │
                                                       ┌────────────────────┴────────────────────┐
                                                       ▼                                         ▼
                                                Terminal / Scripts                        KeePassXC GUI
                                                (keepassxc-cli)                           (Desktop / Browser)
```

1. **Zero Cloud Secret Leakage:** No plaintext files, decrypted JSON, or raw credentials ever touch disk or Git.
2. **Peer-to-Peer Sync (Syncthing):** Encrypted backups automatically sync across your physical Windows and Linux machines without touching third-party servers.
3. **Dual Access:**
   - Use **OpenPGP** archives for long-term cold backup / disaster recovery.
   - Use **KeePassXC (`keepassxc-cli`)** for fast, local, scripted password queries in developer workspaces.

---

## 📦 File Locations

| Component | Path | Description |
| :--- | :--- | :--- |
| **Sync Script** | `~/.local/bin/sync-proton-vault` | CLI import & in-memory sync tool |
| **Repo Source** | `projects/desktopConfigs/scripts/sync-proton-vault.py` | Version-controlled source script |
| **Encrypted Backups** | `/media/hubert/Elements/syncthing/workspace/backups/proton-pass/` | Synced PGP archives (`.zip`) |
| **Local Vault** | `~/vault.kdbx` | Encrypted KeePassXC database (`0600`) |

---

## 🔄 Routine: Exporting & Verifying a Backup

### Step 1: Export from Proton Pass
1. In your browser or desktop app, go to **Settings** $\rightarrow$ **Export data**.
2. Format: Select **Proton Pass (PGP encrypted)** or **JSON**.
3. Choose a passphrase when prompted.
4. Save the export into your Syncthing folder:
   - On Windows: `syncthing\workspace\backups\proton-pass\`
   - On Linux: `/media/hubert/Elements/syncthing/workspace/backups/proton-pass/`

### Step 2: In-Memory Decryption Verification (No Disk Leaks)
To test that your passphrase is correct and the backup is healthy:

```bash
python3 -c "
import zipfile, subprocess, getpass, glob

zips = sorted(glob.glob('/media/hubert/Elements/syncthing/workspace/backups/proton-pass/Proton Pass_export_*.zip'))
if not zips:
    print('No export zip found.')
    exit(1)

latest_zip = zips[-1]
print(f'Testing latest backup: {latest_zip}')

with zipfile.ZipFile(latest_zip, 'r') as zf:
    pgp_data = zf.read('Proton Pass/data.pgp')

pwd = getpass.getpass('Enter Proton Pass export passphrase: ')
proc = subprocess.Popen(
    ['gpg', '--decrypt', '--quiet', '--batch', '--yes', '--pinentry-mode', 'loopback', '--passphrase', pwd],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
out, err = proc.communicate(input=pgp_data)
if proc.returncode == 0:
    print(f'\n[VERIFIED] Successfully decrypted! Archive is healthy ({len(out)} bytes).')
else:
    print(f'\n[FAILED] Decryption error:\n{err.decode()}')
"
```

---

## ⚡ Syncing to Local KeePassXC (`~/vault.kdbx`)

To populate or refresh your local KeePassXC vault from the backup:

```bash
sync-proton-vault -f "/media/hubert/Elements/syncthing/workspace/backups/proton-pass/Proton Pass_export_2026-11-07_1794091985.zip"
```

The script:
1. Decrypts the PGP payload in memory using `gpg`.
2. Prompts for your master database password (or creates `~/vault.kdbx` if it doesn't exist).
3. Inserts or updates credentials organized under `ProtonPass/<VaultName>/`.
4. Enforces `chmod 600` permissions.

---

## 💻 Accessing Credentials on the Command Line

### 1. Interactive Shell Mode
```bash
keepassxc-cli open ~/vault.kdbx
```

### 2. Copy Password to Clipboard (Auto-Clears in 10s)
```bash
keepassxc-cli clip ~/vault.kdbx "ProtonPass/Personal/GitHub"
```

### 3. Inject Password into Environment Variables (for Scripts / Dev)
```bash
export API_TOKEN=$(keepassxc-cli show -s -a password ~/vault.kdbx "ProtonPass/Workspaces/StagingAPI")
```

### 4. Launch Desktop GUI
```bash
keepassxc ~/vault.kdbx &
```

---

## 🛡️ Git Safety Rule
- **NEVER** commit `.zip`, `.pgp`, `.kdbx`, or `.json` files to Git (even in private repositories).
- All backup directories should include a `.gitignore` containing:
  ```gitignore
  *.zip
  *.pgp
  *.gpg
  *.kdbx
  *.json
  *.csv
  ```
