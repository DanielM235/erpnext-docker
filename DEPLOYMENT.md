# ERPNext Docker Deployment Guide

## 🚀 Transferring Configuration from Local to Server

This guide explains how to deploy your ERPNext Docker configuration from your **Ubuntu 24.10 local machine** to your **Debian 12 production server** using SSH.

---

## 📋 Prerequisites

### Local Machine (Ubuntu 24.10)
- ✅ SSH client installed (`openssh-client` - usually pre-installed)
- ✅ SSH configuration properly set up for your server
- ✅ ERPNext Docker project files ready locally

### Remote Server (Debian 12)
- ✅ SSH server running and accessible
- ✅ Docker and Docker Compose installed
- ✅ User account with sudo privileges and docker group membership

### SSH Configuration Verification
```bash
# Test SSH connection from local machine
ssh your-server-name
# or
ssh user@your-server-ip

# Should connect without password prompts if SSH keys are configured
```

---

## 🎯 Deployment Methods

### Method 1: Direct rsync Transfer ⭐ **RECOMMENDED**

**Advantages:**
- Fast and efficient (only transfers changed files)
- Preserves file permissions and timestamps
- Built-in progress display
- Can resume interrupted transfers

#### Step 1: Prepare Local Project
```bash
# Navigate to your local ERPNext project directory
cd /path/to/your/erpnext-docker

# Verify all files are present
ls -la
# Should show: docker-compose.yml, .env.example, *.md files, etc.

# Create .env from template (if not done already)
cp .env.example .env

# Edit .env with your production values (CRITICAL!)
nano .env
# Configure: SITE_NAME, passwords, FRONTEND_PORT, etc.
```

#### Step 2: Transfer Files to Server
```bash
# Transfer entire project directory to server
# Replace 'your-server' with your SSH config hostname
# Replace 'your-user' with your server username

rsync -avz --progress \
  --exclude='.git' \
  --exclude='data/' \
  --exclude='*.log' \
  . your-server:/opt/erpnext/

# Alternative with specific user and IP
rsync -avz --progress \
  --exclude='.git' \
  --exclude='data/' \
  --exclude='*.log' \
  . user@server-ip:/opt/erpnext/
```

**Explanation of rsync options:**
- `-a`: Archive mode (preserves permissions, timestamps, etc.)
- `-v`: Verbose output
- `-z`: Compress during transfer
- `--progress`: Show transfer progress
- `--exclude`: Skip unnecessary files/directories

#### Step 3: Verify Transfer
```bash
# Connect to server
ssh your-server

# Check transferred files
ls -la /opt/erpnext/
# Should show all your project files

# Verify .env file was transferred
ls -la /opt/erpnext/.env
```

### Method 2: SCP Transfer 🔧 **SIMPLE ALTERNATIVE**

**Use when:** rsync is not available or you prefer simpler commands

#### Transfer Individual Files
```bash
# Transfer docker-compose.yml
scp docker-compose.yml your-server:/opt/erpnext/

# Transfer .env file (be careful with this sensitive file!)
scp .env your-server:/opt/erpnext/

# Transfer all markdown files
scp *.md your-server:/opt/erpnext/

# Transfer specific files
scp .env.example .gitignore your-server:/opt/erpnext/
```

#### Transfer Entire Directory
```bash
# Transfer entire directory (creates erpnext-docker folder on server)
scp -r . your-server:/opt/erpnext/
```

### Method 3: Git Repository 📦 **DEVELOPMENT WORKFLOW**

**Use when:** You want version control and collaborative development

#### Step 1: Create Git Repository (Local)
```bash
# Initialize git repository
git init

# Add files (NEVER add .env to git!)
git add docker-compose.yml
git add .env.example
git add *.md
git add .gitignore

# Commit files
git commit -m "Initial ERPNext Docker configuration"

# Add remote repository (GitHub, GitLab, etc.)
git remote add origin https://github.com/yourusername/erpnext-docker.git
git push -u origin main
```

#### Step 2: Clone on Server
```bash
# Connect to server
ssh your-server

# Clone repository
cd /opt
sudo git clone https://github.com/yourusername/erpnext-docker.git erpnext
sudo chown -R erpnext:erpnext /opt/erpnext

# Setup environment
cd /opt/erpnext
cp .env.example .env
nano .env  # Configure production values
```

---

## 🔒 Security Considerations

### Protecting Sensitive Files

#### .env File Security
```bash
# Method 1: Transfer .env securely and set permissions immediately
scp .env your-server:/opt/erpnext/
ssh your-server "chmod 600 /opt/erpnext/.env && chown erpnext:erpnext /opt/erpnext/.env"

# Method 2: Create .env on server (more secure)
# Don't transfer .env, instead:
ssh your-server
cd /opt/erpnext
cp .env.example .env
chmod 600 .env
nano .env  # Enter production values manually
```

#### SSH Security Best Practices
```bash
# Use SSH key authentication (never passwords for production)
# Verify SSH connection uses keys
ssh -v your-server 2>&1 | grep -i "publickey"

# Use SSH config for convenience and security
# Add to ~/.ssh/config:
# Host production-erp
#     HostName your-server-ip
#     User erpnext
#     Port 22
#     IdentityFile ~/.ssh/id_rsa_erpnext
#     IdentitiesOnly yes
```

### File Permissions After Transfer
```bash
# Connect to server and set proper permissions
ssh your-server

# Navigate to project directory
cd /opt/erpnext

# Set directory ownership
sudo chown -R erpnext:erpnext /opt/erpnext

# Set file permissions
chmod 644 *.yml *.md
chmod 600 .env
chmod 755 .

# Verify permissions
ls -la
```

---

## 🛠️ Complete Deployment Workflow

### Step-by-Step Production Deployment

#### 1. **Local Preparation**
```bash
# Navigate to project
cd ~/projects/erpnext-docker

# Final check of configuration
cat .env.example  # Review template
nano .env         # Configure production values

# Test docker-compose syntax locally (optional)
docker compose config
```

#### 2. **Server Preparation**
```bash
# Connect to server
ssh your-server

# Create project directory
sudo mkdir -p /opt/erpnext
sudo chown erpnext:erpnext /opt/erpnext

# Verify Docker is installed and working
docker --version
docker compose version
sudo systemctl status docker
```

#### 3. **Transfer Files**
```bash
# From local machine - transfer files
rsync -avz --progress \
  --exclude='.git' \
  --exclude='data/' \
  --exclude='*.log' \
  --exclude='.env' \
  ~/projects/erpnext-docker/ your-server:/opt/erpnext/

# Transfer .env separately for security
scp ~/projects/erpnext-docker/.env your-server:/tmp/erpnext.env
```

#### 4. **Server Setup**
```bash
# Connect to server
ssh your-server

# Move .env to proper location with secure permissions
sudo mv /tmp/erpnext.env /opt/erpnext/.env
sudo chown erpnext:erpnext /opt/erpnext/.env
sudo chmod 600 /opt/erpnext/.env

# Set project ownership
sudo chown -R erpnext:erpnext /opt/erpnext

# Switch to erpnext user
sudo -u erpnext bash

# Navigate to project
cd /opt/erpnext

# Verify configuration
docker compose config
```

#### 5. **Initial Deployment**
```bash
# Create data directories (as erpnext user)
mkdir -p data/{sites,logs,db,redis_queue}
chmod -R 755 data/

# Start services
docker compose up -d

# Monitor startup
docker compose logs -f configurator

# Check service status
docker compose ps
```

---

## 🔄 Update Workflow

### For Configuration Updates

#### Method 1: Quick File Updates
```bash
# Update specific files
scp docker-compose.yml your-server:/opt/erpnext/
scp SECURITY.md your-server:/opt/erpnext/

# Restart if needed
ssh your-server "cd /opt/erpnext && docker compose restart"
```

#### Method 2: Full Sync (Recommended)
```bash
# Sync all changes
rsync -avz --progress \
  --exclude='.git' \
  --exclude='data/' \
  --exclude='.env' \
  ~/projects/erpnext-docker/ your-server:/opt/erpnext/

# Apply changes
ssh your-server "cd /opt/erpnext && docker compose up -d"
```

---

## 🚨 Troubleshooting

### Common Transfer Issues

#### Permission Denied
```bash
# Check SSH key permissions (local)
ls -la ~/.ssh/
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# Check target directory permissions (server)
ssh your-server "ls -la /opt/"
# If needed: sudo chown erpnext:erpnext /opt/erpnext
```

#### Connection Issues
```bash
# Test SSH connectivity
ssh -v your-server

# Check SSH config
cat ~/.ssh/config

# Test with specific key
ssh -i ~/.ssh/id_rsa user@server-ip
```

#### File Transfer Failures
```bash
# Check disk space on server
ssh your-server "df -h"

# Check file sizes
du -sh ~/projects/erpnext-docker/

# Use rsync dry-run to test
rsync -avz --dry-run --progress \
  ~/projects/erpnext-docker/ your-server:/opt/erpnext/
```

### Verification Commands
```bash
# Verify all files transferred correctly
ssh your-server "cd /opt/erpnext && find . -type f -name '*.yml' -o -name '*.md' -o -name '.env*'"

# Check file integrity
ssh your-server "cd /opt/erpnext && md5sum docker-compose.yml"
# Compare with local: md5sum docker-compose.yml

# Test Docker Compose configuration
ssh your-server "cd /opt/erpnext && docker compose config"
```

---

## 📚 Additional Tips

### SSH Config Optimization
Add to `~/.ssh/config` for easier connections:
```
# ERPNext Production Server
Host erp-prod
    HostName your-server-ip
    User erpnext
    Port 22
    IdentityFile ~/.ssh/id_rsa_erpnext
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Then use: `ssh erp-prod` and `rsync ... erp-prod:/opt/erpnext/`

### Automation Script
Create a deployment script `deploy.sh`:
```bash
#!/bin/bash
# ERPNext deployment script

echo "Deploying ERPNext to production..."

# Sync files
rsync -avz --progress \
  --exclude='.git' \
  --exclude='data/' \
  --exclude='.env' \
  ./ erp-prod:/opt/erpnext/

# Restart services
ssh erp-prod "cd /opt/erpnext && docker compose up -d"

echo "Deployment complete!"
```

Make executable: `chmod +x deploy.sh`
Run: `./deploy.sh`

---

**Security Reminder**: Always verify that `.env` contains production values and never commit it to version control. Keep your SSH keys secure and use strong authentication methods.

**Last Updated**: October 15, 2025  
**Target**: Ubuntu 24.10 → Debian 12 deployment