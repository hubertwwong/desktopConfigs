<#
.SYNOPSIS
  Cross-Machine Synchronization Tool for Antigravity (AGY) on Windows.
  Works natively in PowerShell without requiring Administrator privileges.
.EXAMPLE
  .\sync-agy.ps1 pull
  .\sync-agy.ps1 push "added new research skill"
  .\sync-agy.ps1 status
#>
param(
    [ValidateSet('pull', 'push', 'status', 'link', 'help')]
    [string]$Action = 'pull',
    [string]$Message = 'chore(agy): sync skills and rules across machines'
)

$ErrorActionPreference = 'Stop'

# Resolve repository root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoDir = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$GeminiDotfiles = Join-Path $RepoDir "dotfiles\gemini"
$GlobalConfig = Join-Path $env:USERPROFILE ".gemini\config"

if (-not (Test-Path $GlobalConfig)) {
    New-Item -ItemType Directory -Path $GlobalConfig -Force | Out-Null
}

function Ensure-Link {
    param(
        [string]$Source,
        [string]$Target,
        [bool]$IsDirectory
    )
    
    if (Test-Path $Target) {
        $item = Get-Item $Target
        if ($item.LinkType) {
            return
        }
        $backup = "$Target.bak-$((Get-Date).ToString('yyyyMMddHHmmss'))"
        Write-Host "Backing up existing $Target -> $backup" -ForegroundColor Yellow
        Move-Item $Target $backup -Force
    }

    if ($IsDirectory) {
        # Directory Junctions on Windows work without Administrator rights
        New-Item -ItemType Junction -Path $Target -Value $Source | Out-Null
        Write-Host "Created Junction: $Target -> $Source" -ForegroundColor Green
    } else {
        # Try symbolic link, fallback to hard link (no admin required on same drive)
        try {
            New-Item -ItemType SymbolicLink -Path $Target -Value $Source -ErrorAction Stop | Out-Null
            Write-Host "Created Symlink: $Target -> $Source" -ForegroundColor Green
        } catch {
            New-Item -ItemType HardLink -Path $Target -Value $Source -ErrorAction Stop | Out-Null
            Write-Host "Created HardLink: $Target -> $Source" -ForegroundColor Green
        }
    }
}

function Verify-Links {
    Ensure-Link -Source (Join-Path $GeminiDotfiles "skills") -Target (Join-Path $GlobalConfig "skills") -IsDirectory $true
    Ensure-Link -Source (Join-Path $GeminiDotfiles "AGENTS.md") -Target (Join-Path $GlobalConfig "AGENTS.md") -IsDirectory $false
    Ensure-Link -Source (Join-Path $GeminiDotfiles "mcp_config.json") -Target (Join-Path $GlobalConfig "mcp_config.json") -IsDirectory $false
}

switch ($Action) {
    'link' {
        Verify-Links
        Write-Host "✓ All Antigravity links verified." -ForegroundColor Green
    }

    'status' {
        Write-Host "=== Antigravity Sync Status (Windows) ===" -ForegroundColor Cyan
        Verify-Links
        Write-Host "`nRepository: $RepoDir"
        git -C $RepoDir status --short "dotfiles/gemini"
        Write-Host "`nRemote Status:"
        git -C $RepoDir fetch --quiet origin
        git -C $RepoDir status -uno
    }

    'pull' {
        Write-Host "Pulling latest Antigravity skills and rules..." -ForegroundColor Cyan
        Verify-Links
        git -C $RepoDir pull --rebase origin master
        Write-Host "✓ Successfully synced Antigravity configs!" -ForegroundColor Green
    }

    'push' {
        Write-Host "Pushing Antigravity updates to remote..." -ForegroundColor Cyan
        Verify-Links
        git -C $RepoDir add "dotfiles/gemini"
        git -C $RepoDir commit -m $Message
        git -C $RepoDir push origin master
        Write-Host "✓ Successfully pushed Antigravity configs!" -ForegroundColor Green
    }

    'help' {
        Write-Host "Usage: .\sync-agy.ps1 [pull|push|status|link] [-Message 'commit message']"
    }
}
