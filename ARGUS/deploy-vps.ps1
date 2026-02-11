# =============================================================================
# ARGUS — VPS Deploy Script (Windows PowerShell)
# Usage: .\deploy-vps.ps1 -Server root@YOUR_SERVER_IP
# Subsequent deploys: .\deploy-vps.ps1 -Server root@YOUR_SERVER_IP
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Server,           # e.g. root@143.198.123.45

    [string]$AppDir = "/var/www/argus",
    [string]$SshKey = "$env:USERPROFILE\.ssh\argus_vps",
    [switch]$FirstDeploy       # Pass -FirstDeploy on initial setup only
)

$ErrorActionPreference = "Stop"

function Write-Step { param($msg) Write-Host "`n  [>] $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "      [OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "      [!]  $msg" -ForegroundColor Yellow }

function Run-SSH {
    param([string]$Command)
    ssh -i $SshKey -o StrictHostKeyChecking=no $Server $Command
}

function Copy-ToServer {
    param([string]$Local, [string]$Remote)
    scp -i $SshKey -o StrictHostKeyChecking=no $Local "${Server}:${Remote}"
}

Clear-Host
Write-Host @"

  ╔══════════════════════════════════════╗
  ║   ARGUS — Deploying to VPS           ║
  ╚══════════════════════════════════════╝
  Server: $Server
  Dir:    $AppDir

"@ -ForegroundColor Magenta

# ── Validate SSH Key ─────────────────────────────────────────────────────────
Write-Step "Checking SSH key..."
if (-not (Test-Path $SshKey)) {
    Write-Host "  SSH key not found at $SshKey" -ForegroundColor Red
    Write-Host "  Run .\setup-windows.ps1 first to generate one." -ForegroundColor Yellow
    exit 1
}
Write-OK "SSH key found"

# ── Test Server Connection ────────────────────────────────────────────────────
Write-Step "Testing connection to $Server..."
try {
    Run-SSH "echo 'connection_ok'" | Out-Null
    Write-OK "Connected successfully"
} catch {
    Write-Host "  Cannot reach $Server — check IP and that your SSH key is authorised." -ForegroundColor Red
    exit 1
}

# ── First Deploy: Provision the server ───────────────────────────────────────
if ($FirstDeploy) {
    Write-Step "First deploy — provisioning server..."

    # Upload and run the server setup script
    Copy-ToServer ".\setup-server.sh" "/tmp/setup-server.sh"
    Run-SSH "chmod +x /tmp/setup-server.sh && bash /tmp/setup-server.sh"
    Write-OK "Server provisioned"
}

# ── Bundle App Files ──────────────────────────────────────────────────────────
Write-Step "Bundling application files..."

$filesToDeploy = @(
    "api.py",
    "argus_core.py",
    "llm_engine.py",
    "requirements.txt"
)

# Verify all files exist locally
foreach ($file in $filesToDeploy) {
    if (-not (Test-Path $file)) {
        Write-Host "  Missing file: $file" -ForegroundColor Red
        exit 1
    }
}

Write-OK "All files ready"

# ── Upload Files ──────────────────────────────────────────────────────────────
Write-Step "Uploading files to $AppDir..."

foreach ($file in $filesToDeploy) {
    Write-Host "      Uploading $file..." -ForegroundColor Gray
    Copy-ToServer $file "$AppDir/$file"
}

Write-OK "Files uploaded"

# ── Upload .env (only if it exists and not placeholder) ──────────────────────
if (Test-Path ".\.env") {
    $envContent = Get-Content ".\.env" -Raw
    if ($envContent -notmatch "sk-ant-your-key-here") {
        Write-Step "Uploading .env..."
        Copy-ToServer ".\.env" "$AppDir/.env"
        # Lock down permissions on server
        Run-SSH "chmod 600 $AppDir/.env && chown argus:argus $AppDir/.env"
        Write-OK ".env uploaded and secured (chmod 600)"
    } else {
        Write-Warn "Skipping .env — still has placeholder key. Update it first!"
    }
}

# ── Install / Update Dependencies on Server ───────────────────────────────────
Write-Step "Installing dependencies on server..."
Run-SSH @"
cd $AppDir
if [ ! -d venv ]; then
    python3.11 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install gunicorn uvicorn[standard] --quiet
chown -R argus:argus $AppDir
"@
Write-OK "Dependencies installed"

# ── Restart Service ───────────────────────────────────────────────────────────
Write-Step "Restarting ARGUS service..."
Run-SSH "systemctl restart argus"
Start-Sleep -Seconds 3

# ── Health Check ──────────────────────────────────────────────────────────────
Write-Step "Running health check..."
$health = Run-SSH "systemctl is-active argus"
if ($health -eq "active") {
    Write-OK "Service is running"
} else {
    Write-Warn "Service may not have started — check logs:"
    Write-Host "      ssh -i $SshKey $Server 'journalctl -u argus -n 50'" -ForegroundColor Yellow
}

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║           Deploy complete!                     ║" -ForegroundColor Green
Write-Host "  ╚════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

$serverIp = $Server -replace ".*@", ""
Write-Host "  Your API is live at:" -ForegroundColor White
Write-Host "    http://$serverIp/" -ForegroundColor Yellow
Write-Host "    http://$serverIp/docs  (interactive API docs)" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Useful commands:" -ForegroundColor White
Write-Host "    View logs:    ssh -i $SshKey $Server 'tail -f /var/log/argus/error.log'" -ForegroundColor Gray
Write-Host "    Restart:      ssh -i $SshKey $Server 'systemctl restart argus'" -ForegroundColor Gray
Write-Host "    Status:       ssh -i $SshKey $Server 'systemctl status argus'" -ForegroundColor Gray
Write-Host ""
