# =============================================================================
# ARGUS — Windows Local Setup & VPS Deploy Toolkit
# Run in PowerShell (right-click PowerShell → "Run as Administrator")
# =============================================================================

param(
    [switch]$SkipDependencies,
    [switch]$LocalOnly
)

$ErrorActionPreference = "Stop"

function Write-Step  { param($msg) Write-Host "`n[>] $msg" -ForegroundColor Cyan }
function Write-OK    { param($msg) Write-Host "    [OK] $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "    [!]  $msg" -ForegroundColor Yellow }
function Write-Fail  { param($msg) Write-Host "    [X]  $msg" -ForegroundColor Red; exit 1 }

Clear-Host
Write-Host @"
  ╔══════════════════════════════════════╗
  ║   ARGUS — Windows Setup Script      ║
  ╚══════════════════════════════════════╝
"@ -ForegroundColor Magenta

# ── 1. Check Python ──────────────────────────────────────────────────────────
Write-Step "Checking Python..."
try {
    $pyVersion = python --version 2>&1
    if ($pyVersion -match "3\.(1[01])") {
        Write-OK "Found $pyVersion"
    } else {
        Write-Warn "Found $pyVersion — Python 3.10+ recommended"
        Write-Warn "Download from https://www.python.org/downloads/"
    }
} catch {
    Write-Fail "Python not found. Install from https://www.python.org/downloads/ and re-run."
}

# ── 2. Check/Install SSH (built into Windows 10+) ────────────────────────────
Write-Step "Checking SSH client..."
if (Get-Command ssh -ErrorAction SilentlyContinue) {
    Write-OK "SSH client available"
} else {
    Write-Step "Installing OpenSSH client..."
    Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
    Write-OK "OpenSSH installed"
}

# ── 3. Virtual Environment ───────────────────────────────────────────────────
Write-Step "Setting up Python virtual environment..."
$venvPath = ".\venv"
if (-not (Test-Path $venvPath)) {
    python -m venv venv
    Write-OK "Virtual environment created at .\venv"
} else {
    Write-OK "Virtual environment already exists"
}

# ── 4. Install Python Dependencies ───────────────────────────────────────────
Write-Step "Installing Python dependencies..."
& ".\venv\Scripts\pip.exe" install --upgrade pip --quiet
& ".\venv\Scripts\pip.exe" install -r requirements.txt --quiet
Write-OK "All dependencies installed"

# ── 5. Check for .env file ───────────────────────────────────────────────────
Write-Step "Checking environment configuration..."
if (-not (Test-Path ".\.env")) {
    Write-Warn ".env file not found — creating template..."
    @"
# ARGUS Environment Variables
# Fill in your Anthropic API key below

ANTHROPIC_API_KEY=sk-ant-your-key-here
"@ | Set-Content ".\.env"
    Write-Warn "Created .env — EDIT IT and add your ANTHROPIC_API_KEY before running!"
} else {
    $envContent = Get-Content ".\.env" -Raw
    if ($envContent -match "sk-ant-your-key-here") {
        Write-Warn ".env exists but still has placeholder key — update ANTHROPIC_API_KEY!"
    } else {
        Write-OK ".env file configured"
    }
}

# ── 6. Generate SSH Key for VPS (if needed) ───────────────────────────────────
Write-Step "Checking SSH key for VPS access..."
$sshKeyPath = "$env:USERPROFILE\.ssh\argus_vps"
if (-not (Test-Path $sshKeyPath)) {
    Write-Warn "No ARGUS SSH key found. Generating one..."
    if (-not (Test-Path "$env:USERPROFILE\.ssh")) {
        New-Item -ItemType Directory -Path "$env:USERPROFILE\.ssh" | Out-Null
    }
    ssh-keygen -t ed25519 -f $sshKeyPath -N '""' -C "argus-vps-deploy"
    Write-OK "SSH key generated at $sshKeyPath"
    Write-Warn "Copy the PUBLIC key below to your VPS (see deploy instructions):"
    Write-Host ""
    Get-Content "$sshKeyPath.pub"
    Write-Host ""
} else {
    Write-OK "SSH key already exists at $sshKeyPath"
}

# ── Done ─────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║        Windows setup complete!               ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "   1. Edit .env and add your ANTHROPIC_API_KEY" -ForegroundColor Yellow
Write-Host "   2. Test locally:  .\run-local.bat" -ForegroundColor Yellow
Write-Host "   3. Deploy to VPS: .\deploy-vps.ps1 -Server root@YOUR_SERVER_IP" -ForegroundColor Yellow
Write-Host ""
