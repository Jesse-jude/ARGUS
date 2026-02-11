#!/bin/bash
# =============================================================================
# ARGUS — Server Provisioning Script
# Runs on the VPS (Ubuntu 22.04). Called automatically by deploy-vps.ps1
# Do NOT run this manually on Windows — it's for the server.
# =============================================================================

set -e

APP_USER="argus"
APP_DIR="/var/www/argus"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}  [✓]${NC} $1"; }
warn() { echo -e "${YELLOW}  [!]${NC} $1"; }

echo ""
echo "  Provisioning ARGUS server..."
echo ""

# ── System Packages ───────────────────────────────────────────────────────────
log "Updating packages..."
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
    curl wget git \
    build-essential \
    software-properties-common \
    ufw fail2ban \
    nginx

# ── Python 3.11 ───────────────────────────────────────────────────────────────
log "Installing Python 3.11..."
add-apt-repository -y ppa:deadsnakes/ppa > /dev/null 2>&1
apt-get update -qq
apt-get install -y -qq python3.11 python3.11-venv python3.11-dev python3-pip

# ── App User ──────────────────────────────────────────────────────────────────
log "Creating app user '$APP_USER'..."
id "$APP_USER" &>/dev/null || useradd -m -s /bin/bash "$APP_USER"

# ── App Directory ─────────────────────────────────────────────────────────────
log "Creating app directory..."
mkdir -p "$APP_DIR"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# ── Firewall ──────────────────────────────────────────────────────────────────
log "Configuring firewall..."
ufw default deny incoming  > /dev/null
ufw default allow outgoing > /dev/null
ufw allow ssh              > /dev/null
ufw allow 'Nginx Full'     > /dev/null
ufw --force enable         > /dev/null

# ── Fail2ban ──────────────────────────────────────────────────────────────────
log "Enabling fail2ban..."
systemctl enable fail2ban --quiet
systemctl start  fail2ban

# ── Nginx Config ──────────────────────────────────────────────────────────────
log "Writing Nginx config..."
cat > /etc/nginx/sites-available/argus << 'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    # Security headers
    add_header X-Frame-Options        "SAMEORIGIN"                   always;
    add_header X-Content-Type-Options "nosniff"                      always;
    add_header X-XSS-Protection       "1; mode=block"                always;
    add_header Referrer-Policy        "strict-origin-when-cross-origin" always;

    client_max_body_size 10M;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;

        # CORS
        add_header 'Access-Control-Allow-Origin'  '*'                  always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type'       always;
        if ($request_method = OPTIONS) { return 204; }
    }

    location ~ /\.  { deny all; }
}
NGINX

ln -sf /etc/nginx/sites-available/argus /etc/nginx/sites-enabled/argus
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
log "Nginx configured"

# ── Log Directory ─────────────────────────────────────────────────────────────
log "Creating log directory..."
mkdir -p /var/log/argus
chown -R "$APP_USER:$APP_USER" /var/log/argus

# ── systemd Service ───────────────────────────────────────────────────────────
log "Writing systemd service..."
cat > /etc/systemd/system/argus.service << SYSTEMD
[Unit]
Description=ARGUS Universal Argument Engine
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn api:app \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 127.0.0.1:8000 \\
    --timeout 120 \\
    --access-logfile /var/log/argus/access.log \\
    --error-logfile  /var/log/argus/error.log
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$APP_DIR /var/log/argus

[Install]
WantedBy=multi-user.target
SYSTEMD

systemctl daemon-reload
systemctl enable argus
log "systemd service registered"

# ── Logrotate ─────────────────────────────────────────────────────────────────
cat > /etc/logrotate.d/argus << 'LOGROTATE'
/var/log/argus/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 argus argus
}
LOGROTATE

log "Server provisioning complete!"
echo ""
echo "  Next: deploy-vps.ps1 will now upload code and start the service."
echo ""
