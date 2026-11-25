# Web Extraction & Navigation Toolkit Guide

## Overview
A complete multi-tier web extraction and discovery pipeline is installed on the ThinkCentre (`hubert-thinkcentre-m75q-gen-2`).
All CLI tools are available in `~/.local/bin/`.

## The 4-Tool Agent Ladder

```text
1. DISCOVER  ➔  search-web "<query>"         (SearXNG local Docker on :8888, 0 cost)
2. FAST-PATH ➔  fast-web --url "<url>"        (~200ms, curl_cffi Chrome TLS/JA3 impersonation)
3. READ/DOCS ➔  clean-reader --url "<url>"    (Trafilatura boilerplate stripper, -70% tokens)
4. FULL JS   ➔  query-web --url "<url>"       (Stealth Playwright headless Chrome for dynamic SPAs)
```

---

## 1. Search: `search-web`
```powershell
ssh hubert@100.85.13.5 "search-web 'python playwright stealth' --num 3"
ssh hubert@100.85.13.5 "search-web 'linux mint 22' --format json"
```

## 2. Ultra-Fast Fetch: `fast-web`
```powershell
ssh hubert@100.85.13.5 "fast-web --url https://news.ycombinator.com --format markdown"
ssh hubert@100.85.13.5 "fast-web --url https://httpbin.org/get --format json"
```

## 3. Article & Documentation Reader: `clean-reader`
```powershell
ssh hubert@100.85.13.5 "clean-reader --url https://blog.example.com/post"
ssh hubert@100.85.13.5 "clean-reader --url https://example.com/article --format json"
```

## 4. Full Dynamic SPA Scraping: `query-web`
```powershell
ssh hubert@100.85.13.5 "query-web --url https://spa-app.com --format markdown"
ssh hubert@100.85.13.5 "query-web --url https://example.com --screenshot ~/projects/playwright-agent/ai/scratch/view.png"
```

---

## Standard Exit Codes
- `0`: Success
- `1`: Network / Navigation / Timeout error
- `2`: Blocked by interactive bot challenge / CAPTCHA (do not retry)
