#!/usr/bin/env python3
"""
sync-proton-vault:
Syncs credentials from Proton Pass (via pass-cli or export file) directly
into a local encrypted KeePassXC database (.kdbx).
"""

import argparse
import getpass
import json
import os
import subprocess
import sys
import zipfile
from pykeepass import PyKeePass, create_database

DEFAULT_VAULT_PATH = os.path.expanduser(os.environ.get("PROTON_VAULT_PATH", "~/vault.kdbx"))

def get_cli_vaults():
    """Fetch vaults from pass-cli."""
    res = subprocess.run(
        ["pass-cli", "vault", "list", "--output", "json"],
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        sys.stderr.write(f"Error fetching vaults from pass-cli:\n{res.stderr}\n")
        sys.stderr.write("Hint: Have you logged in with 'pass-cli login'?\n")
        sys.exit(1)
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as err:
        sys.stderr.write(f"Failed to parse pass-cli vault list JSON: {err}\n")
        sys.exit(1)

def get_cli_vault_items(share_id):
    """Fetch all items with decrypted content from pass-cli for a specific share/vault."""
    res = subprocess.run(
        ["pass-cli", "item", "list", "--share-id", share_id, "--output", "json", "--show-secrets"],
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        sys.stderr.write(f"Error fetching items for share {share_id}:\n{res.stderr}\n")
        return []
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as err:
        sys.stderr.write(f"Failed to parse items JSON for share {share_id}: {err}\n")
        return []

def decrypt_pgp(data_bytes, export_pass=None):
    """Decrypt OpenPGP data in-memory using gpg."""
    if not export_pass:
        export_pass = os.environ.get("PROTON_EXPORT_PASSWORD")
    if not export_pass:
        export_pass = getpass.getpass("Enter the passphrase used when exporting from Proton Pass: ")

    proc = subprocess.Popen(
        ["gpg", "--decrypt", "--quiet", "--batch", "--yes", "--pinentry-mode", "loopback", "--passphrase", export_pass],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate(input=data_bytes)
    if proc.returncode != 0:
        sys.stderr.write(f"Error decrypting PGP export:\n{stderr.decode(errors='replace')}\n")
        sys.exit(1)
    return stdout.decode("utf-8")

def load_from_export_file(file_path, export_pass=None):
    """Load vaults and items from a JSON/ZIP/PGP export file or stdin."""
    raw = None
    if file_path == "-":
        raw = sys.stdin.read()
    elif zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, "r") as zf:
            namelist = zf.namelist()
            pgp_files = [n for n in namelist if n.endswith(".pgp") or n.endswith(".gpg")]
            json_files = [n for n in namelist if n.endswith(".json")]

            if pgp_files:
                print(f"Detected PGP-encrypted export in archive ({pgp_files[0]}).")
                pgp_data = zf.read(pgp_files[0])
                raw = decrypt_pgp(pgp_data, export_pass)
            elif json_files:
                primary_json = json_files[0]
                with zf.open(primary_json) as f:
                    raw = f.read().decode("utf-8")
            else:
                sys.stderr.write(f"No .json or .pgp file found inside zip archive: {file_path}\n")
                sys.exit(1)
    elif file_path.endswith(".pgp") or file_path.endswith(".gpg"):
        with open(file_path, "rb") as f:
            raw = decrypt_pgp(f.read(), export_pass)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()

    data = json.loads(raw)

    # 1. pass-cli list dump (array of items)
    if isinstance(data, list):
        return [{"name": "ProtonPass", "items": data}]

    # 2. Proton Pass web/extension JSON export
    if isinstance(data, dict):
        vaults_raw = data.get("vaults")
        if vaults_raw:
            results = []
            if isinstance(vaults_raw, dict):
                for v_id, v_val in vaults_raw.items():
                    v_name = v_val.get("name") or "Personal"
                    results.append({"name": v_name, "items": v_val.get("items", [])})
                return results
            elif isinstance(vaults_raw, list):
                for v_val in vaults_raw:
                    v_name = v_val.get("name") or "Personal"
                    results.append({"name": v_name, "items": v_val.get("items", [])})
                return results
        elif "items" in data:
            return [{"name": data.get("name", "ProtonPass"), "items": data["items"]}]

    return [{"name": "ProtonPass", "items": []}]

def get_or_create_group(kp, parent_group, group_name):
    """Find a subgroup by name under parent, or create it if not present."""
    for grp in parent_group.subgroups:
        if grp.name == group_name:
            return grp
    return kp.add_group(parent_group, group_name)

def sync_entries(kp, vault_data, dry_run=False):
    """Process vaults and sync items into the KeePass database."""
    total_added = 0
    total_updated = 0

    root_proton_group = None if dry_run else get_or_create_group(kp, kp.root_group, "ProtonPass")

    for vault in vault_data:
        v_name = vault.get("name") or vault.get("title") or "General"
        items = vault.get("items", [])
        v_group = None if dry_run else get_or_create_group(kp, root_proton_group, v_name)

        for item in items:
            # Handle both direct pass-cli and web export hierarchies
            data_sec = item.get("data", {})
            meta = data_sec.get("metadata", {})
            content = data_sec.get("content") or item.get("content") or {}

            title = (
                item.get("title") or
                item.get("name") or
                meta.get("name") or
                meta.get("title") or
                "Untitled"
            )
            username = content.get("username") or ""
            password = content.get("password") or ""
            notes = content.get("notes") or meta.get("note") or ""
            urls = content.get("urls", [])
            url = urls[0] if urls else ""
            totp = content.get("totp") or content.get("totpUri") or ""

            if dry_run:
                print(f"[DRY-RUN] {v_name} / {title} (user: {username})")
                continue

            existing = kp.find_entries(group=v_group, title=title, first=True)
            if existing:
                existing.username = username
                existing.password = password
                existing.url = url
                existing.notes = notes
                if totp:
                    existing.set_custom_property("TOTP", totp)
                total_updated += 1
            else:
                new_entry = kp.add_entry(
                    destination_group=v_group,
                    title=title,
                    username=username,
                    password=password,
                    url=url,
                    notes=notes
                )
                if totp:
                    new_entry.set_custom_property("TOTP", totp)
                total_added += 1

    return total_added, total_updated

def main():
    parser = argparse.ArgumentParser(
        description="Sync credentials from Proton Pass into a local encrypted KeePassXC vault (.kdbx)."
    )
    parser.add_argument(
        "-k", "--kdbx",
        default=DEFAULT_VAULT_PATH,
        help=f"Path to local KeePassXC database (default: {DEFAULT_VAULT_PATH})"
    )
    parser.add_argument(
        "-f", "--file",
        help="Read from an exported Proton Pass JSON/ZIP/PGP file instead of calling pass-cli (use '-' for stdin)"
    )
    parser.add_argument(
        "--export-password",
        help="Passphrase used when exporting from Proton Pass (if encrypted with PGP)"
    )
    parser.add_argument(
        "-p", "--password",
        help="Master password for the .kdbx database (if omitted, will prompt or check KEEPASS_PASSWORD env)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and display credentials that would be synced without modifying database"
    )

    args = parser.parse_args()
    db_path = os.path.abspath(os.path.expanduser(args.kdbx))

    # 1. Collect Vault Data
    vaults_data = []
    if args.file:
        print(f"Reading Proton Pass export from {args.file}...")
        vaults_data = load_from_export_file(args.file, export_pass=args.export_password)
    else:
        print("Connecting to pass-cli...")
        raw_vaults = get_cli_vaults()
        for v in raw_vaults:
            v_id = v.get("share_id") or v.get("id")
            v_name = v.get("name") or "Default"
            print(f"Fetching items for vault '{v_name}'...")
            items = get_cli_vault_items(v_id)
            vaults_data.append({"name": v_name, "items": items})

    if args.dry_run:
        print("\n--- Dry Run Results ---")
        # Dummy pass to count
        class DummyKP:
            root_group = None
        sync_entries(None, vaults_data, dry_run=True)
        print("Dry run complete.")
        return

    # 2. Get master password
    db_pass = args.password or os.environ.get("KEEPASS_PASSWORD")
    if not db_pass:
        if os.path.exists(db_path):
            db_pass = getpass.getpass(f"Enter master password for existing database [{db_path}]: ")
        else:
            print(f"Database [{db_path}] does not exist yet. It will be created.")
            db_pass = getpass.getpass("Enter new master password: ")
            confirm = getpass.getpass("Confirm master password: ")
            if db_pass != confirm:
                sys.stderr.write("Error: Passwords do not match.\n")
                sys.exit(1)

    # 3. Open or Create Database
    if os.path.exists(db_path):
        kp = PyKeePass(db_path, password=db_pass)
    else:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        kp = create_database(db_path, password=db_pass)

    # 4. Sync
    added, updated = sync_entries(kp, vaults_data, dry_run=False)
    kp.save()

    # Enforce strict file permissions
    os.chmod(db_path, 0o600)

    print(f"\nSuccessfully synced to {db_path}!")
    print(f"  Added:   {added} items")
    print(f"  Updated: {updated} items")
    print(f"  Permissions: {oct(os.stat(db_path).st_mode & 0o777)} (read/write by owner only)")

if __name__ == "__main__":
    main()
