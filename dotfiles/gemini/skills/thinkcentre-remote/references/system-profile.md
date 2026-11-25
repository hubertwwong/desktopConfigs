# ThinkCentre Hardware & Environment Profile

## Hardware Specs
- **Model:** Lenovo ThinkCentre M75q Gen 2
- **CPU Architecture:** x86_64 (AMD Ryzen PRO platform)
- **Memory (RAM):** 16 GB DDR4 (15 GiB usable)
- **Primary Storage:** 256 GB NVMe SSD (`/dev/nvme0n1p2`, ~194 GB free space)
- **Swap:** 2.0 GiB

## Operating System & Kernel
- **Distribution:** Linux Mint 22.3 (Codename: Zena)
- **Upstream Base:** Ubuntu 24.04 LTS (Noble Numbat) / Debian package base
- **Kernel Version:** 7.0.0-42-generic

## Network & Tailscale Configuration
- **Tailscale Hostname:** `hubert-thinkcentre-m75q-gen-2`
- **Tailscale IPv4:** `100.85.13.5`
- **SSH Daemon:** Tailscale SSH enabled on port 22
- **Default SSH User:** `hubert`
- **Authentication:** Web-based Tailscale ACL authorization / Tailscale SSH key exchange
