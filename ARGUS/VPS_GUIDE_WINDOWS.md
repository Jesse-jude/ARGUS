# ARGUS — VPS Deployment Guide (Windows)

This guide deploys ARGUS to a DigitalOcean or Linode VPS from a Windows machine
using PowerShell. No Docker, no Linux knowledge required on your end.

---

## What You'll Need

- A Windows 10/11 machine (PowerShell built-in)
- A DigitalOcean or Linode account (~$6/month for a basic server)
- Your Anthropic API key

---

## Step 1 — Create Your VPS

### DigitalOcean (recommended)
1. Go to [digitalocean.com](https://digitalocean.com) → Create → Droplets
2. Choose **Ubuntu 22.04 LTS**
3. Plan: **$6/month** (1 vCPU, 1GB RAM — enough for ARGUS)
4. Region: pick closest to your users
5. Authentication: **Password** for now (we'll add SSH key in a moment)
6. Click **Create Droplet**
7. Copy your server IP address (e.g. `143.198.123.45`)

### Linode (alternative)
1. Go to [linode.com](https://linode.com) → Create → Linode
2. Choose **Ubuntu 22.04 LTS**
3. Plan: **Nanode 1GB** ($5/month)
4. Same steps as above

---

## Step 2 — Run Windows Setup Script

Open **PowerShell as Administrator** and run:

```powershell
# Allow scripts to run (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup
.\setup-windows.ps1
```

This will:
- Check Python is installed
- Create a virtual environment
- Install all dependencies
- Generate an SSH key at `C:\Users\YOU\.ssh\argus_vps`
- Print your **public key** — copy it!

---

## Step 3 — Add SSH Key to Your Server

You need to paste your public key onto the server so PowerShell can connect without a password.

**Option A — Via DigitalOcean web console:**
1. In DigitalOcean dashboard, click your droplet → **Console**
2. Log in as `root` with your password
3. Run these commands:
```bash
mkdir -p ~/.ssh
echo "PASTE_YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

**Option B — Via PowerShell (if you can SSH with password first):**
```powershell
# Replace with your server IP
$serverIp = "143.198.123.45"
$pubKey = Get-Content "$env:USERPROFILE\.ssh\argus_vps.pub"
ssh root@$serverIp "mkdir -p ~/.ssh && echo '$pubKey' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

---

## Step 4 — Edit Your .env File

Open `.env` in Notepad and add your real API key:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Save and close.

---

## Step 5 — First Deploy

Run this from PowerShell in your ARGUS folder:

```powershell
.\deploy-vps.ps1 -Server root@143.198.123.45 -FirstDeploy
```

Replace `143.198.123.45` with your actual server IP.

This will:
1. Test the SSH connection
2. Install Python, Nginx, and all system packages on the server
3. Upload your code and `.env`
4. Install Python dependencies
5. Start the ARGUS service

**Takes about 3-5 minutes on first run.**

---

## Step 6 — Test It

```powershell
# Quick health check (replace IP)
Invoke-RestMethod -Uri "http://143.198.123.45/" -Method Get

# Test argument analysis
$body = @{
    input_text = "AI will replace doctors"
    stance     = "dialectic"
    persona    = "academic"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://143.198.123.45/analyze" -Method Post `
    -Body $body -ContentType "application/json"
```

Or open in your browser: `http://143.198.123.45/docs` for the interactive API explorer.

---

## Step 7 — (Optional) Add a Domain + HTTPS

If you have a domain name:

1. Point your domain's **A record** to your server IP in your DNS settings
2. Wait 5-10 minutes for DNS to propagate
3. Run:

```powershell
.\enable-ssl.ps1 -Server root@143.198.123.45 `
    -Domain argus.yourdomain.com `
    -Email you@email.com
```

Your API will then be live at `https://argus.yourdomain.com`.

---

## Everyday Commands

### Deploy code updates
```powershell
# After editing any .py file, just re-run without -FirstDeploy
.\deploy-vps.ps1 -Server root@143.198.123.45
```

### View live logs
```powershell
.\manage.ps1 -Server root@143.198.123.45 -Action logs
.\manage.ps1 -Server root@143.198.123.45 -Action errors
```

### Restart the service
```powershell
.\manage.ps1 -Server root@143.198.123.45 -Action restart
```

### Check status
```powershell
.\manage.ps1 -Server root@143.198.123.45 -Action status
```

### Open an SSH terminal
```powershell
.\manage.ps1 -Server root@143.198.123.45 -Action ssh
```

---

## Troubleshooting

### "Permission denied" when running scripts
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "SSH connection refused"
- Check the server IP is correct
- Make sure your VPS is running (check DigitalOcean dashboard)
- Make sure port 22 isn't blocked (it shouldn't be on a fresh droplet)

### Service not starting after deploy
```powershell
# View the last 50 log lines
$key = "$env:USERPROFILE\.ssh\argus_vps"
ssh -i $key root@YOUR_IP "journalctl -u argus -n 50 --no-pager"
```

Common causes:
- `.env` file missing or has wrong API key
- Python dependency failed to install (check error log)

### Nginx showing "502 Bad Gateway"
The ARGUS service crashed. Check logs:
```powershell
.\manage.ps1 -Server root@YOUR_IP -Action errors
```

---

## File Reference

| File | Purpose |
|------|---------|
| `setup-windows.ps1` | One-time Windows setup (Python venv, SSH key) |
| `deploy-vps.ps1` | Push code to server and restart service |
| `setup-server.sh` | Runs on the server during first deploy |
| `enable-ssl.ps1` | Add HTTPS once domain is pointed |
| `manage.ps1` | Logs, restart, status from PowerShell |
| `run-local.bat` | Run ARGUS locally for testing |

---

## Cost Summary

| Service | Cost |
|---------|------|
| DigitalOcean Droplet (1GB) | $6/month |
| Linode Nanode (1GB) | $5/month |
| Domain name (optional) | ~$10/year |
| SSL certificate (Let's Encrypt) | Free |
| Anthropic API | Pay per use |
