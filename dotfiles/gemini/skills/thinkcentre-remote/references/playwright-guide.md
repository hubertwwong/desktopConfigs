# Playwright Stealth Web Querying Guide

## Overview
A hardened Playwright stealth scraping pipeline is installed on the ThinkCentre at `/home/hubert/projects/playwright-agent`. It uses the machine's native Google Chrome binary (`/usr/bin/google-chrome-stable`) with automated bot evasions.

## Features & Bot Mitigation
- **Clean WebDriver**: Strips `navigator.webdriver` on prototype and instance; passes Sannysoft's `missing (passed)` and `advanced-webdriver (passed)` benchmarks.
- **Chrome Emulation**: Replaces generic headless signatures with authentic `window.chrome` properties (runtime, app, csi).
- **Client Hints & Headers**: Supplies consistent `Sec-Ch-Ua`, `Sec-Ch-Ua-Mobile`, `Sec-Ch-Ua-Platform`, and `Accept-Language` headers matching Linux x86_64.
- **Challenge Detection (No-Go)**: Auto-detects Cloudflare Turnstile, CAPTCHA, or human verification barriers and exits with code `2` rather than looping.
- **Zero Zombie Processes**: Strictly wrapped in Playwright context managers with automatic cleanup.

## CLI Usage Patterns

### 1. Extract Markdown from Any Webpage
```powershell
ssh hubert@100.85.13.5 "query-web --url https://example.com --format markdown"
```

### 2. Extract Structured JSON (Title, Final URL, Markdown Content)
```powershell
ssh hubert@100.85.13.5 "query-web --url https://example.com --format json"
```

### 3. Capture Full-Page Screenshot
```powershell
ssh hubert@100.85.13.5 "query-web --url https://example.com --screenshot ~/projects/playwright-agent/ai/scratch/page.png"
```

### 4. Wait for a Dynamic JavaScript Selector
```powershell
ssh hubert@100.85.13.5 "query-web --url https://spa-app.com --wait-selector '#main-content' --format markdown"
```

## Exit Codes
- `0`: Success
- `1`: Network / Navigation / Timeout error
- `2`: Blocked by interactive bot challenge / CAPTCHA (do not retry)
