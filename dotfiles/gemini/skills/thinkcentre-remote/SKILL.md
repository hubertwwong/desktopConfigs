---
name: thinkcentre-remote
description: >-
  Use this skill when connecting to, operating, administering, troubleshooting, or running
  commands on the remote ThinkCentre Linux machine (hubert-thinkcentre-m75q-gen-2) via Tailscale SSH.
---

# ThinkCentre Remote Operations Runbook

This skill defines the standardized operational runbook for executing commands, managing services, and deploying workloads on the remote `thinkcentre` over Tailscale SSH.

---

## Target Machine Quick Reference

- **Host Alias / Hostname:** `hubert-thinkcentre-m75q-gen-2`
- **Tailscale IP:** `100.85.13.5`
- **User:** `hubert`
- **OS:** Linux Mint 22.3 (Ubuntu Noble base)
- **Detailed Specs:** See [system-profile.md](./references/system-profile.md)

---

## Operating Guidelines & Constraints

1. **Sandbox Bypass**: All SSH and network commands to the ThinkCentre require `BypassSandbox: true` in `run_command` because they establish external TCP sockets.
2. **Non-Interactive Execution**: Never run commands that trigger interactive prompts without non-interactive flags (e.g. use `apt-get -y`, `ssh -o BatchMode=yes`, `DEBIAN_FRONTEND=noninteractive`).
3. **Tailscale SSH Authentication**: If a command output returns a Tailscale authorization URL (`https://login.tailscale.com/a/...`), immediately present the link to the user and pause until authenticated.

---

## Standard Execution Procedures

### 1. Pre-flight Connectivity Verification
Before running multi-step tasks, verify network reachability:
```powershell
tailscale ping -c 1 100.85.13.5
```
**Verification:** Confirm `pong from hubert-thinkcentre-m75q-gen-2` is returned.

### 2. Remote Command Execution
Execute commands over SSH using `hubert@100.85.13.5`:
```powershell
ssh -o BatchMode=yes hubert@100.85.13.5 "<command>"
```
*Tip:* For complex commands with pipes or quotes, wrap the remote command block carefully or write a local script and copy it over.

### 3. File Transfer
Copy files between local machine and ThinkCentre:
```powershell
# Upload local file to ThinkCentre
scp <local-path> hubert@100.85.13.5:<remote-path>

# Download remote file to local machine
scp hubert@100.85.13.5:<remote-path> <local-path>
```
**Verification:** Verify exit code `0` and confirm file existence with `ssh hubert@100.85.13.5 "ls -la <remote-path>"`.

### 4. Web Intelligence & Extraction Toolkit
Operate the 4-tier web ladder (`search-web`, `fast-web`, `clean-reader`, `query-web`):
```powershell
# 1. Search the web (SearXNG local gateway)
ssh hubert@100.85.13.5 "search-web '<query>' --num 3"

# 2. Fast TLS fetch (~200ms via Chrome TLS impersonation)
ssh hubert@100.85.13.5 "fast-web --url <URL> --format markdown"

# 3. Clean article extraction (boilerplate-stripped markdown)
ssh hubert@100.85.13.5 "clean-reader --url <URL>"

# 4. Full stealth Playwright browser (for dynamic JS SPAs)
ssh hubert@100.85.13.5 "query-web --url <URL> --format markdown"
```
*Full Guide & Options:* See [playwright-guide.md](./references/playwright-guide.md).

### 5. Service & Process Management
- **Check service status:**
  ```powershell
  ssh hubert@100.85.13.5 "systemctl status <service-name> --no-pager"
  ```
- **Check system resource usage:**
  ```powershell
  ssh hubert@100.85.13.5 "free -h; df -h /; uptime"
  ```
- **Docker containers (if applicable):**
  ```powershell
  ssh hubert@100.85.13.5 "docker ps -a"
  ```

---

## Troubleshooting

- **Connection timed out / Host down:** Check `tailscale status` to confirm the node is active. If offline, the physical machine may be suspended or disconnected from power/network.
- **Permission denied (publickey):** Tailscale SSH session key may have expired. Re-authenticate via the Tailscale admin console or browser check URL.
