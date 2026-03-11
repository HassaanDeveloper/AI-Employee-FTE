# Oracle Cloud Free Tier - AI Employee Deployment Guide

## Why Oracle Cloud?

| Feature | Benefit |
|---------|---------|
| **Always Free** | 24/7 deployment at no cost |
| **4 OCPUs, 24GB RAM** | Plenty of power for AI Employee + Odoo |
| **200GB Storage** | Ample space for vault, logs, Odoo data |
| **10TB Transfer** | More than enough for API calls |

---

## Step 1: Create Oracle Cloud Account

### 1.1 Sign Up

**Go to:** https://www.oracle.com/cloud/free/

1. **Click:** "Start for free"
2. **Fill in:** Name, email, company
3. **Verify:** Phone number
4. **Add:** Credit card (for identity verification, NOT charged)
5. **Wait:** Account activation (5-10 minutes)

### 1.2 Login to Console

**Go to:** https://cloud.oracle.com/

1. **Username:** Your email
2. **Password:** Set during signup
3. **Cloud Account Name:** Your account name

---

## Step 2: Create Compute Instance

### 2.1 Navigate to Compute

1. **Click:** Hamburger menu (top left)
2. **Select:** Compute → Instances

### 2.2 Create Instance

1. **Click:** "Create Instance"

2. **Configure:**
   - **Name:** `ai-employee-cloud`
   - **Compartment:** Your compartment
   - **Availability Domain:** Any (e.g., AD-1)

3. **Image and Shape:**
   - **Image:** Oracle Linux 8 or Ubuntu 22.04
   - **Shape:** VM.Standard.A1.Flex (Always Free)
   - **OCPUs:** 4
   - **Memory:** 24 GB

4. **Networking:**
   - **VCN:** Create new (default)
   - **Subnet:** Public
   - **Assign public IPv4:** ✅ Checked

5. **SSH Keys:**
   - **Generate key pair** (download both private and public)
   - **OR** upload your existing SSH public key
   - **Save private key securely** (e.g., `~/.ssh/oracle_cloud`)

6. **Boot Volume:**
   - **Size:** 100 GB (default is 50GB, increase for Odoo)

7. **Click:** "Create"

### 2.3 Wait for Instance

- **Status:** Provisioning → Running (2-5 minutes)
- **Note:** Public IP address (e.g., `129.146.123.45`)

---

## Step 3: Connect to Your Instance

### 3.1 SSH Connection

**Windows (PowerShell):**
```powershell
ssh -i ~/.ssh/oracle_cloud opc@YOUR_PUBLIC_IP
```

**Mac/Linux:**
```bash
chmod 400 ~/.ssh/oracle_cloud
ssh -i ~/.ssh/oracle_cloud opc@YOUR_PUBLIC_IP
```

**First time:** Type `yes` to accept fingerprint

### 3.2 Update System

```bash
sudo dnf update -y  # Oracle Linux
# OR
sudo apt update && sudo apt upgrade -y  # Ubuntu
```

---

## Step 4: Install Docker & Docker Compose

### 4.1 Install Docker

**Oracle Linux:**
```bash
# Install Docker
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker opc
```

**Ubuntu:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

### 4.2 Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### 4.3 Verify Installation

```bash
docker --version
docker-compose --version
docker run hello-world
```

---

## Step 5: Deploy Odoo Community

### 5.1 Create Odoo Directory

```bash
mkdir -p ~/odoo/{config,data,addons}
cd ~/odoo
```

### 5.2 Create docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
version: '3.1'

services:
  odoo:
    image: odoo:16.0
    container_name: ai-employee-odoo
    depends_on:
      - postgres
    ports:
      - "8069:8069"
    volumes:
      - ./data/odoo-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    environment:
      - ODOO_ADMIN_PASS=CHANGE_THIS_PASSWORD
      - ODOO_DB_HOST=postgres
      - ODOO_DB_USER=odoo
      - ODOO_DB_PASSWORD=CHANGE_THIS_PASSWORD
      - ODOO_DB_NAME=odoo_db
    restart: unless-stopped

  postgres:
    image: postgres:15
    container_name: ai-employee-odoo-db
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
      - POSTGRES_DB=postgres
    volumes:
      - ./data/postgresql:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  odoo-data:
  postgresql:
EOF
```

### 5.3 Start Odoo

```bash
docker-compose up -d
```

### 5.4 Access Odoo

**Open browser:** `http://YOUR_PUBLIC_IP:8069`

**First-time setup:**
- **Master Password:** CHANGE_THIS_PASSWORD
- **Database:** odoo_db
- **Email:** your-email@example.com
- **Password:** Choose admin password
- **Install:** Invoicing, CRM, Sales apps

---

## Step 6: Deploy AI Employee Cloud Agent

### 6.1 Create AI Employee Directory

```bash
mkdir -p ~/ai-employee/{scripts,vault,logs}
cd ~/ai-employee
```

### 6.2 Clone Your Repository

```bash
# If using Git
git clone https://github.com/YOUR_USERNAME/AI-Employee-FTE.git .

# OR copy files manually
# (Use SCP or create new files)
```

### 6.3 Install Python Dependencies

```bash
sudo dnf install -y python3 python3-pip  # Oracle Linux
# OR
sudo apt install -y python3 python3-pip  # Ubuntu

pip3 install --upgrade pip
pip3 install -r AI_Employee_Vault/requirements.txt
```

### 6.4 Create Cloud Configuration

```bash
cat > cloud_config.env << 'EOF'
# Cloud Agent Configuration
CLOUD_MODE=true
VAULT_PATH=/home/opc/ai-employee/AI_Employee_Vault
LOG_PATH=/home/opc/ai-employee/logs

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USER=admin
ODOO_PASSWORD=YOUR_ODOO_ADMIN_PASSWORD

# Email Configuration (Cloud - draft only)
GMAIL_CREDENTIALS_PATH=/home/opc/ai-employee/credentials.json
GMAIL_DRAFT_ONLY=true

# Facebook Configuration (Cloud - draft only)
FACEBOOK_PAGE_ID=993926910480113
FACEBOOK_DRAFT_ONLY=true

# Security
SECRETS_PATH=/home/opc/ai-employee/.secrets
NEVER_SYNC=true
EOF
```

### 6.5 Create Systemd Service

```bash
sudo cat > /etc/systemd/system/ai-employee-cloud.service << 'EOF'
[Unit]
Description=AI Employee Cloud Agent
After=network.target docker.service

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/ai-employee
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 -m AI_Employee_Vault.scripts.orchestrator /home/opc/ai-employee/AI_Employee_Vault --interval 30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### 6.6 Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-cloud
sudo systemctl start ai-employee-cloud
sudo systemctl status ai-employee-cloud
```

---

## Step 7: Setup Vault Sync (Git)

### 7.1 Initialize Git Repository

**On Cloud:**
```bash
cd ~/ai-employee
git init
git remote add origin https://github.com/YOUR_USERNAME/ai-employee-vault.git
```

**On Local:**
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault
git init
git remote add origin https://github.com/YOUR_USERNAME/ai-employee-vault.git
```

### 7.2 Create .gitignore

```bash
cat > .gitignore << 'EOF'
# NEVER sync secrets
.env
*.env
credentials.json
token.json
whatsapp-session/
linkedin-session/
__pycache__/
*.pyc
Logs/
*.log

# Sync only markdown and state files
# Exclude sensitive data
EOF
```

### 7.3 Configure Git

```bash
git config user.name "AI Employee"
git config user.email "ai-employee@localhost"
```

### 7.4 Sync Script

Create `sync-vault.sh`:

```bash
cat > sync-vault.sh << 'EOF'
#!/bin/bash
# Vault Sync Script - Run every 5 minutes

cd ~/ai-employee/AI_Employee_Vault

# Pull changes from remote
git pull origin main --rebase

# Add local changes
git add -A

# Commit changes
git commit -m "Auto-sync: $(date)"

# Push to remote
git push origin main

echo "Vault synced at $(date)"
EOF

chmod +x sync-vault.sh
```

### 7.5 Add to Cron

```bash
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/opc/ai-employee/sync-vault.sh") | crontab -
```

---

## Step 8: Setup Health Monitoring

### 8.1 Create Health Check Script

```bash
cat > health_check.sh << 'EOF'
#!/bin/bash
# Health Check Script

LOG_FILE=/home/opc/ai-employee/logs/health_$(date +%Y-%m-%d).log

echo "=== Health Check $(date) ===" >> $LOG_FILE

# Check Docker containers
echo "Docker Containers:" >> $LOG_FILE
docker ps --format "table {{.Names}}\t{{.Status}}" >> $LOG_FILE

# Check AI Employee service
echo "AI Employee Service:" >> $LOG_FILE
systemctl is-active ai-employee-cloud >> $LOG_FILE

# Check disk space
echo "Disk Space:" >> $LOG_FILE
df -h / >> $LOG_FILE

# Check memory
echo "Memory:" >> $LOG_FILE
free -h >> $LOG_FILE

# Restart if needed
if ! systemctl is-active --quiet ai-employee-cloud; then
    echo "Restarting AI Employee..." >> $LOG_FILE
    sudo systemctl restart ai-employee-cloud
fi

echo "" >> $LOG_FILE
EOF

chmod +x health_check.sh
```

### 8.2 Add to Cron

```bash
(crontab -l 2>/dev/null; echo "*/10 * * * * /home/opc/ai-employee/health_check.sh") | crontab -
```

---

## Step 9: Security Configuration

### 9.1 Setup Firewall

```bash
# Oracle Linux
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-port=8069/tcp
sudo firewall-cmd --reload

# Ubuntu
sudo ufw allow ssh
sudo ufw allow 8069/tcp
sudo ufw enable
```

### 9.2 Setup Fail2Ban

```bash
sudo dnf install -y fail2ban  # Oracle Linux
# OR
sudo apt install -y fail2ban  # Ubuntu

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 9.3 Secure Secrets

```bash
# Create secrets directory (never synced)
mkdir -p ~/ai-employee/.secrets
chmod 700 ~/ai-employee/.secrets

# Move sensitive files
mv ~/ai-employee/AI_Employee_Vault/.env ~/ai-employee/.secrets/
mv ~/ai-employee/AI_Employee_Vault/credentials.json ~/ai-employee/.secrets/
```

---

## Step 10: Access & URLs

| Service | URL | Port |
|---------|-----|------|
| **Odoo** | http://YOUR_PUBLIC_IP:8069 | 8069 |
| **SSH** | ssh -i key opc@YOUR_PUBLIC_IP | 22 |
| **Cloud Agent** | Local service | - |

---

## Summary

| Component | Status | Location |
|-----------|--------|----------|
| ✅ Oracle Cloud VM | Running | Oracle Cloud Console |
| ✅ Docker & Compose | Installed | Cloud VM |
| ✅ Odoo Community | Running | Port 8069 |
| ✅ AI Employee Cloud | Running | Systemd service |
| ✅ Git Sync | Configured | Every 5 minutes |
| ✅ Health Monitor | Running | Every 10 minutes |
| ✅ Security | Configured | Firewall, Fail2Ban |

---

**Your AI Employee Platinum Tier is now deployed on Oracle Cloud 24/7!** 🎉
