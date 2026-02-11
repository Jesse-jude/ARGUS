# =============================================================================
# ARGUS — Enable HTTPS (SSL via Let's Encrypt)
# Run AFTER your domain's DNS A-record points to your server IP
# Usage: .\enable-ssl.ps1 -Server root@YOUR_IP -Domain argus.yourdomain.com
# =============================================================================

param(
    [Parameter(Mandatory=$true)] [string]$Server,
    [Parameter(Mandatory=$true)] [string]$Domain,
    [Parameter(Mandatory=$true)] [string]$Email,
    [string]$SshKey = "$env:USERPROFILE\.ssh\argus_vps"
)

function Write-Step { param($msg) Write-Host "`n  [>] $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "      [OK] $msg" -ForegroundColor Green }
function Run-SSH    { param([string]$Cmd) ssh -i $SshKey -o StrictHostKeyChecking=no $Server $Cmd }

Write-Host ""
Write-Host "  Enabling HTTPS for $Domain" -ForegroundColor Magenta
Write-Host ""

# ── Install Certbot ───────────────────────────────────────────────────────────
Write-Step "Installing Certbot on server..."
Run-SSH "apt-get install -y -qq certbot python3-certbot-nginx"
Write-OK "Certbot installed"

# ── Update Nginx to use domain name ──────────────────────────────────────────
Write-Step "Updating Nginx config with domain..."
Run-SSH "sed -i 's/listen 80 default_server;/listen 80;/' /etc/nginx/sites-available/argus"
Run-SSH "sed -i 's/listen \[::\]:80 default_server;/server_name $Domain;/' /etc/nginx/sites-available/argus"
Run-SSH "nginx -t && systemctl reload nginx"
Write-OK "Nginx updated"

# ── Request Certificate ───────────────────────────────────────────────────────
Write-Step "Requesting SSL certificate for $Domain..."
Run-SSH "certbot --nginx -d $Domain --email $Email --agree-tos --non-interactive --redirect"
Write-OK "SSL certificate installed"

# ── Auto-renewal check ────────────────────────────────────────────────────────
Write-Step "Verifying auto-renewal is set up..."
Run-SSH "systemctl is-enabled certbot.timer && echo 'renewal timer active'"
Write-OK "Certbot auto-renewal enabled"

# ── Done ─────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║   HTTPS enabled!                             ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Your API is now live at:" -ForegroundColor White
Write-Host "    https://$Domain/" -ForegroundColor Yellow
Write-Host "    https://$Domain/docs" -ForegroundColor Yellow
Write-Host ""
