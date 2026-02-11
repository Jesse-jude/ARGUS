# =============================================================================
# ARGUS — Server Management Helper (Windows PowerShell)
# Usage: .\manage.ps1 -Server root@YOUR_IP -Action logs
# =============================================================================

param(
    [Parameter(Mandatory=$true)] [string]$Server,
    [ValidateSet("logs","errors","status","restart","stop","start","ssh")]
    [string]$Action = "status",
    [string]$SshKey = "$env:USERPROFILE\.ssh\argus_vps"
)

function Run-SSH { param([string]$Cmd) ssh -i $SshKey -o StrictHostKeyChecking=no $Server $Cmd }
function Run-SSH-Live { param([string]$Cmd) ssh -i $SshKey -o StrictHostKeyChecking=no -t $Server $Cmd }

switch ($Action) {

    "logs" {
        Write-Host "  Streaming access logs (Ctrl+C to stop)..." -ForegroundColor Cyan
        Run-SSH-Live "tail -f /var/log/argus/access.log"
    }

    "errors" {
        Write-Host "  Streaming error logs (Ctrl+C to stop)..." -ForegroundColor Cyan
        Run-SSH-Live "tail -f /var/log/argus/error.log"
    }

    "status" {
        Write-Host "  Service status:" -ForegroundColor Cyan
        Run-SSH "systemctl status argus --no-pager"
    }

    "restart" {
        Write-Host "  Restarting ARGUS service..." -ForegroundColor Yellow
        Run-SSH "systemctl restart argus"
        Start-Sleep -Seconds 2
        $state = Run-SSH "systemctl is-active argus"
        Write-Host "  Status: $state" -ForegroundColor $(if ($state -eq "active") {"Green"} else {"Red"})
    }

    "stop" {
        Write-Host "  Stopping ARGUS service..." -ForegroundColor Yellow
        Run-SSH "systemctl stop argus"
        Write-Host "  Stopped." -ForegroundColor Gray
    }

    "start" {
        Write-Host "  Starting ARGUS service..." -ForegroundColor Green
        Run-SSH "systemctl start argus"
        Start-Sleep -Seconds 2
        Run-SSH "systemctl status argus --no-pager -l"
    }

    "ssh" {
        Write-Host "  Opening SSH session to $Server..." -ForegroundColor Cyan
        ssh -i $SshKey $Server
    }
}
