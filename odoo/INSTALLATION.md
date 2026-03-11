# Odoo Installation Guide

## Option 1: Docker (Recommended)

### Prerequisites
- Docker Desktop for Windows
- Docker Compose (included with Docker Desktop)

### Installation

1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and restart computer
   - Open Docker Desktop to start the daemon

2. **Start Odoo**
   ```bash
   cd E:\AI-Employee-FTE\odoo
   docker compose up -d
   ```

3. **Access Odoo**
   - Open browser: http://localhost:8069
   - Create database:
     - Database Name: `odoo_db`
     - Email: your-email@example.com
     - Password: Choose admin password

4. **Verify Running**
   ```bash
   docker ps
   ```

---

## Option 2: Local Installation (Without Docker)

### Prerequisites
- Python 3.8+
- PostgreSQL 12+

### Step 1: Install PostgreSQL

1. Download from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the postgres password

### Step 2: Create Database

```bash
# Open Command Prompt as Administrator
cd "C:\Program Files\PostgreSQL\15\bin"

# Create Odoo user and database
.\psql -U postgres -c "CREATE USER odoo WITH PASSWORD 'odoo_password' CREATEDB;"
.\psql -U postgres -c "CREATE DATABASE odoo_db OWNER odoo;"
```

### Step 3: Install Odoo

```bash
# Download Odoo Community from:
# https://nightly.odoo.com/16.0/nightly/src/

# Extract to E:\AI-Employee-FTE\odoo\odoo-server

# Install Python dependencies
cd E:\AI-Employee-FTE\odoo\odoo-server
pip install -r requirements.txt
```

### Step 4: Create Odoo Configuration

Create `E:\AI-Employee-FTE\odoo\odoo.conf`:

```ini
[options]
admin_passwd = admin_password_change_me
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo_password
db_name = odoo_db
addons_path = E:\AI-Employee-FTE\odoo\odoo-server\odoo\addons
http_port = 8069
```

### Step 5: Start Odoo

```bash
cd E:\AI-Employee-FTE\odoo\odoo-server
python odoo-bin --config=E:\AI-Employee-FTE\odoo\odoo.conf
```

### Step 6: Access Odoo

Open browser: http://localhost:8069

---

## Option 3: Odoo Online (Simplest - No Installation)

1. Go to https://www.odoo.com/trial
2. Sign up for free trial
3. Get your Odoo URL (e.g., yourcompany.odoo.com)
4. Update Odoo MCP Server config:
   ```bash
   python odoo-mcp-server.py --odoo-url https://yourcompany.odoo.com
   ```

**Note:** Odoo Online requires internet connection and has some limitations compared to self-hosted.

---

## Verify Odoo is Running

### Test Connection

```bash
cd E:\AI-Employee-FTE\.qwen\skills\odoo-mcp\scripts

# Start Odoo MCP Server
python odoo-mcp-server.py --port 8770 --odoo-url http://localhost:8069 --odoo-db odoo_db --odoo-user admin --odoo-password YOUR_PASSWORD
```

If connection successful:
```
INFO:OdooMCP:Authenticated with Odoo as user ID: 2
INFO:OdooMCP:Odoo MCP Server initialized
```

---

## Troubleshooting

### Docker Issues

**"Cannot connect to Docker daemon"**
- Open Docker Desktop
- Wait for whale icon to stop animating
- Try command again

**"Port already in use"**
- Change port in docker-compose.yml: `8070:8069`

### PostgreSQL Issues

**"Authentication failed"**
- Check password in odoo.conf matches database password
- Verify user exists: `.\psql -U postgres -c "\du"`

### Odoo Won't Start

**Check logs:**
```bash
# Docker
docker logs ai-employee-odoo

# Local
# Check output in terminal where you started Odoo
```

---

## Quick Start (Recommended for Hackathon)

For the hackathon demo, use **Odoo Online Trial** (Option 3):

1. Sign up at https://odoo.com/trial (free, no credit card)
2. Get your Odoo URL immediately
3. Update MCP Server config
4. Start testing!

This avoids Docker/PostgreSQL installation complexity.

API_KEY= "f86347539a6bd4767fbc8a5c8af27278375a130c"
cd E:\AI-Employee-FTE\.qwen\skills\odoo-mcp\scripts
      
python -c "import urllib.request import json request = {'jsonrpc': '2.0','id': 1'method': 'tools/call','params': {'name': 'create_customer','arguments': {'name': 'Test Customer','email': 'test@example.com'}}} data = json.dumps(request).encode('utf-8') req = urllib.request.Request('http://localhost:8770/mcp', data=data, headers={'Content-Type': 'application/json'}, method='POST') with urllib.request.urlopen(req, timeout=10) as response: result = json.loads(response.read().decode('utf-8'))print('Result:', json.dumps(result, indent=2))"

python odoo-mcp-server.py --port 8770 --odoo-url https://hassuu1.odoo.com --odoo-db hassuu1 --odoo-user mohammedhassaan449@gmail.com --odoo-password f86347539a6bd4767fbc8a5c8af27278375a130c