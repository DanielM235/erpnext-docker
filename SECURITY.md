# ERPNext Docker Security Guide

## 🔐 Security Best Practices for Production Deployment

This guide covers essential security considerations for deploying ERPNext in production, including user management, password generation, and port configuration.

---

## 1. 👤 User Management and Docker Compose Execution

### Understanding Docker User Mapping

**CRITICAL CONCEPT**: Docker user mapping involves TWO different users:

1. **Host User**: The user on your server who runs `docker compose`
2. **Container User**: The user ID inside the container (configured via `DOCKER_USER_ID`)

The Docker Compose configuration uses `user: "${DOCKER_USER_ID}:${DOCKER_GROUP_ID}"` which:
- **Inside container**: Process runs as this UID/GID
- **On host filesystem**: Files are owned by the corresponding host user with same UID
- **Security benefit**: Avoids running containers as root

**Key principle**: The `DOCKER_USER_ID` should match the UID of your host user for proper file permissions.

### Step 1: Check Current User Situation

First, understand your server's user configuration:
```bash
# Check if UID 1000 exists and what user it belongs to
id 1000 2>/dev/null && echo "UID 1000 exists" || echo "UID 1000 not found"
getent passwd 1000

# Check your current user's UID (this is important!)
whoami
id -u
id -g
```

### Step 2: Choose Your Strategy

**Strategy A: Use Existing User with UID 1000** ✅ **SIMPLEST**
- If UID 1000 exists and belongs to a regular user
- Use default configuration (no changes needed)

**Strategy B: Create Dedicated User with UID 1000** ⭐ **RECOMMENDED**
- If UID 1000 is free
- Create dedicated ERPNext user

**Strategy C: Use Different UID** 🔧 **MOST FLEXIBLE**
- If UID 1000 is unavailable or you prefer different user
- Requires updating environment variables

### Step 3: Implementation Based on Your Strategy

#### **Strategy A: Use Existing UID 1000 User**
```bash
# Add existing user to docker group (replace 'username' with actual username)
sudo usermod -aG docker username

# Verify docker group membership
groups username

# Keep default .env configuration (DOCKER_USER_ID=1000)
# No changes needed to environment variables
```

#### **Strategy B: Create Dedicated User with UID 1000** ⭐ **RECOMMENDED**
```bash
# Create erpnext user with specific UID 1000
sudo useradd -u 1000 -g users -m -s /bin/bash erpnext

# Add to docker group
sudo usermod -aG docker erpnext

# Set password for the user
sudo passwd erpnext

# Keep default .env configuration (DOCKER_USER_ID=1000)
# No changes needed to environment variables
```

#### **Strategy C: Use Different UID** 🔧 **FOR YOUR CASE**

Since UID 1000 is not available on your server, this is your approach:

```bash
# Create erpnext user (system will assign available UID)
sudo useradd -m -s /bin/bash erpnext
sudo usermod -aG docker erpnext
sudo passwd erpnext

# Find the assigned UID and GID
NEW_UID=$(id -u erpnext)
NEW_GID=$(id -g erpnext)
echo "ERPNext user created with UID: $NEW_UID, GID: $NEW_GID"

# Update .env file with the new UID/GID
echo "DOCKER_USER_ID=$NEW_UID" >> .env
echo "DOCKER_GROUP_ID=$NEW_GID" >> .env

# Example: if erpnext user gets UID 1001
# Your .env file should contain:
# DOCKER_USER_ID=1001
# DOCKER_GROUP_ID=1001
```

**Important**: After creating the user, you must update the environment variables in `.env` file!

### 🛡️ Security Recommendations for User Management

1. **Dedicated User**: Always create a dedicated user for ERPNext
2. **Limited Privileges**: The user should only have Docker access, no sudo
3. **Strong Authentication**: Use strong passwords or SSH keys
4. **Home Directory Permissions**: Secure the user's home directory
```bash
# Set secure permissions for erpnext user home
sudo chmod 750 /home/erpnext
sudo chown erpnext:erpnext /home/erpnext

# Create ERPNext project directory with proper ownership
sudo mkdir -p /opt/erpnext
sudo chown erpnext:erpnext /opt/erpnext
sudo chmod 755 /opt/erpnext
```

### 📂 **Docker User Mapping and File Permissions - CRITICAL UNDERSTANDING**

**How Docker User Mapping Works:**

1. **Container Internal User**: Process inside container runs as `DOCKER_USER_ID:DOCKER_GROUP_ID`
2. **Host File Ownership**: Files created by container are owned by host user with same UID
3. **Permission Match**: Host user UID must match container UID for proper access

**Example with UID 1001:**
```bash
# You create user with UID 1001
sudo useradd -u 1001 erpnext

# You set in .env: DOCKER_USER_ID=1001
echo "DOCKER_USER_ID=1001" >> .env

# Container runs as UID 1001 internally
# Files created by container = owned by erpnext user (UID 1001) on host
# Perfect permission alignment! ✅
```

### 🎯 **Best Practice for File Permissions**

**ALWAYS match host user UID with container UID:**

```bash
# After creating your user and updating .env, set up directories
# Use the SAME user that will run docker compose

# Method 1: Run as the erpnext user (RECOMMENDED)
sudo -u erpnext mkdir -p data/{sites,logs,db,redis_queue}
sudo -u erpnext chmod -R 755 data/

# Method 2: Create as root then change ownership to match DOCKER_USER_ID
sudo mkdir -p data/{sites,logs,db,redis_queue}
sudo chown -R $(id -u erpnext):$(id -g erpnext) data/
sudo chmod -R 755 data/

# Verify ownership matches your DOCKER_USER_ID
ls -la data/
# Should show: drwxr-xr-x erpnext erpnext (or your user)
```

### ⚡ **Quick Setup for Your Case (UID 1000 Not Available)**

**Complete procedure:**
```bash
# 1. Create dedicated user (gets available UID, e.g., 1001)
sudo useradd -m -s /bin/bash erpnext
sudo usermod -aG docker erpnext
sudo passwd erpnext

# 2. Find assigned UID/GID
USER_UID=$(id -u erpnext)
USER_GID=$(id -g erpnext)
echo "User UID: $USER_UID, GID: $USER_GID"

# 3. Update .env file
cp .env.example .env
echo "DOCKER_USER_ID=$USER_UID" >> .env
echo "DOCKER_GROUP_ID=$USER_GID" >> .env

# 4. Create directories as the erpnext user
sudo -u erpnext mkdir -p /opt/erpnext/data/{sites,logs,db,redis_queue}
sudo -u erpnext chmod -R 755 /opt/erpnext/data/

# 5. Set .env file permissions
sudo chown erpnext:erpnext .env
sudo chmod 600 .env

# 6. Run Docker Compose as erpnext user
sudo -u erpnext docker compose up -d
```

### Running Docker Compose Securely

**Best practices for execution:**
```bash
# Switch to erpnext user
sudo -u erpnext bash

# Navigate to project directory
cd /opt/erpnext

# Run Docker Compose (never as root!)
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

**⚠️ NEVER run Docker Compose as root unless absolutely necessary**

### 🔍 **Troubleshooting Permission Issues**

**If you see permission errors:**
```bash
# Check if UID matches between host and container
echo "Host user UID: $(id -u erpnext)"
echo "Container UID from .env: $(grep DOCKER_USER_ID .env)"

# Check data directory ownership
ls -la data/
# Should be owned by erpnext user

# Fix ownership if needed
sudo chown -R $(id -u erpnext):$(id -g erpnext) data/

# Check container user ID is correct
docker compose exec backend id
# Should show uid=1001(frappe) or whatever your DOCKER_USER_ID is
```

---

## 2. 🔑 Password Generation and Management

### Password Requirements

All passwords in ERPNext deployment should meet these criteria:
- **Minimum 16 characters** for database passwords
- **Minimum 12 characters** for application passwords
- Include: uppercase, lowercase, numbers, and symbols
- Avoid: dictionary words, personal information, predictable patterns

### Generating Secure Passwords

#### Method 1: Using OpenSSL (Recommended)
```bash
# Generate 20-character random password
openssl rand -base64 20

# Generate 32-character hex password
openssl rand -hex 16

# Generate password with special characters
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
```

#### Method 2: Using /dev/urandom
```bash
# Generate random password
tr -dc A-Za-z0-9 </dev/urandom | head -c 20; echo

# Generate password with special characters
tr -dc 'A-Za-z0-9!@#$%^&*()_+' </dev/urandom | head -c 20; echo
```

#### Method 3: Using pwgen (if available)
```bash
# Install pwgen
sudo apt-get install pwgen  # Debian/Ubuntu

# Generate secure passwords
pwgen -s -y 20 1  # 20 chars with symbols
pwgen -s 16 5     # 5 passwords, 16 chars each
```

### Password Configuration in .env

**Step-by-step secure password setup:**

1. **Generate all required passwords:**
```bash
# Database root password (20 characters)
DB_ROOT_PWD=$(openssl rand -base64 20 | tr -d "=+/" | cut -c1-20)
echo "DB_ROOT_PASSWORD: $DB_ROOT_PWD"

# Database application password (18 characters)
DB_APP_PWD=$(openssl rand -base64 18 | tr -d "=+/" | cut -c1-18)
echo "DB_PASSWORD: $DB_APP_PWD"

# ERPNext admin password (16 characters)
ADMIN_PWD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
echo "ADMIN_PASSWORD: $ADMIN_PWD"
```

2. **Update .env file securely:**
```bash
# Copy environment template
cp .env.example .env

# Set secure permissions immediately
chmod 600 .env
chown erpnext:erpnext .env

# Edit with generated passwords
nano .env
```

3. **Example .env password section:**
```bash
# Use the generated passwords from above
DB_ROOT_PASSWORD=Kx9mP2nQ4vR8sT1uY5wZ
DB_PASSWORD=Aa7bC3dE9fG1hJ4kL6m
ADMIN_PASSWORD=Pp8qR2sT6uV9xZ
```

### 🔐 Password Security Best Practices

1. **Never reuse passwords** between different services
2. **Store passwords securely** - consider using a password manager
3. **Regular rotation** - change passwords every 90 days
4. **Backup .env securely** - encrypted and off-site
5. **Limit .env access** - only ERPNext user should read it

```bash
# Secure .env file permissions
chmod 600 .env                    # Read/write for owner only
chattr +i .env                   # Make immutable (optional)
# To modify: chattr -i .env, edit, then chattr +i .env again
```

---

## 3. 🌐 Port Configuration and Conflicts

### Understanding Current Port Usage

The default configuration uses port **8080** for the frontend service. If this conflicts with existing applications:

#### Check Current Port Usage
```bash
# Check what's using port 8080
sudo netstat -tlnp | grep :8080
# or
sudo ss -tlnp | grep :8080

# List all listening ports
sudo netstat -tlnp | grep LISTEN

# Check for common web server ports
sudo netstat -tlnp | grep -E ':(80|443|8000|8080|8443|9000)'
```

### Changing the Frontend Port

#### Method 1: Using Environment Variables (Recommended)

1. **Add port configuration to .env file:**
```bash
# Add this to your .env file
FRONTEND_PORT=8090  # Change to your desired port
```

2. **Update docker-compose.yml to use the environment variable:**

You need to modify the frontend service in docker-compose.yml:

```yaml
frontend:
  # ... existing configuration ...
  
  # Replace the expose section with ports for custom port
  ports:
    - "${FRONTEND_PORT:-8080}:8080"
  
  # Remove the original expose section:
  # expose:
  #   - "8080"
```

#### Method 2: Direct Docker Compose Modification

**Edit docker-compose.yml directly:**

Find the frontend service section and change:
```yaml
# FROM:
frontend:
  expose:
    - "8080"

# TO:
frontend:
  ports:
    - "8090:8080"  # Change 8090 to your desired port
```

### 🔧 Complete Port Change Procedure

1. **Stop running services:**
```bash
docker compose down
```

2. **Choose available port:**
```bash
# Find available port (example checks 8090)
sudo netstat -tlnp | grep :8090 || echo "Port 8090 is available"
```

3. **Update configuration:**

**Option A: Using .env (Recommended)**
```bash
# Add to .env file
echo "FRONTEND_PORT=8090" >> .env
```

Then modify docker-compose.yml frontend service:
```yaml
frontend:
  # ... other configuration ...
  ports:
    - "${FRONTEND_PORT:-8080}:8080"
  # Remove expose section
```

**Option B: Direct modification**
```bash
# Edit docker-compose.yml
sed -i 's/expose:/ports:/g' docker-compose.yml
sed -i 's/- "8080"/- "8090:8080"/g' docker-compose.yml
```

4. **Update host Nginx configuration:**
```nginx
# Change in your host nginx config
# FROM:
proxy_pass http://127.0.0.1:8080;

# TO:
proxy_pass http://127.0.0.1:8090;
```

5. **Restart services:**
```bash
# Start with new port configuration
docker compose up -d

# Verify new port
docker compose ps
sudo netstat -tlnp | grep :8090
```

6. **Test connectivity:**
```bash
# Test internal connectivity
curl -I http://localhost:8090

# Test through nginx proxy
curl -I http://your-domain.com
```

### 🚨 Security Considerations for Port Changes

1. **Firewall Rules**: Update firewall to allow new port if needed
```bash
# If using UFW
sudo ufw allow 8090/tcp

# If using iptables
sudo iptables -A INPUT -p tcp --dport 8090 -j ACCEPT
```

2. **Host Nginx Security**: Ensure only local access to Docker port
```nginx
# In nginx upstream configuration
upstream erpnext_backend {
    server 127.0.0.1:8090;  # Only localhost access
    # Never use 0.0.0.0:8090 in production
}
```

3. **Docker Network Security**: Keep internal networks isolated
```bash
# Verify network isolation
docker network ls
docker network inspect erpnext-prod_erpnext_backend
```

### 📋 Port Change Checklist

- [ ] Stop Docker services
- [ ] Check port availability
- [ ] Update .env or docker-compose.yml
- [ ] Modify host Nginx configuration
- [ ] Update firewall rules if needed
- [ ] Restart Docker services
- [ ] Test connectivity
- [ ] Monitor logs for errors
- [ ] Update documentation/runbooks

---

## 🛡️ Additional Security Hardening

### File Permissions Security
```bash
# Secure project directory
sudo chmod -R 755 /opt/erpnext
sudo chown -R erpnext:erpnext /opt/erpnext

# Secure sensitive files
chmod 600 .env
chmod 644 docker-compose.yml
chmod 644 *.md

# Secure data directories
chmod -R 750 data/
chown -R 1000:1000 data/  # Match Docker user
```

### Network Security
```bash
# Verify Docker networks are isolated
docker network inspect erpnext-prod_erpnext_backend | grep -i internal

# Check no unnecessary ports are exposed
docker compose ps --format "table {{.Name}}\t{{.Ports}}"
```

### Monitoring Security
```bash
# Monitor failed authentication attempts
docker compose logs backend | grep -i "auth\|login\|fail"

# Check for unusual access patterns
docker compose logs frontend | grep -E "GET|POST" | tail -100
```

---

## 🚨 Security Incident Response

### Immediate Actions for Security Issues

1. **Suspected Breach:**
```bash
# Stop all services immediately
docker compose down

# Check logs for suspicious activity
docker compose logs > security_incident_$(date +%Y%m%d_%H%M).log

# Review recent access
last -n 20
journalctl -u docker -n 100
```

2. **Password Rotation:**
```bash
# Generate new passwords
NEW_DB_ROOT=$(openssl rand -base64 20)
NEW_DB_APP=$(openssl rand -base64 18)
NEW_ADMIN=$(openssl rand -base64 16)

# Update .env file
# Update database passwords
# Restart services
```

3. **Recovery Checklist:**
- [ ] Change all passwords
- [ ] Review and update firewall rules
- [ ] Check for unauthorized users
- [ ] Verify data integrity
- [ ] Update all Docker images
- [ ] Review access logs
- [ ] Document incident

---

**Remember**: Security is an ongoing process. Regularly review and update these configurations based on your evolving security requirements and threat landscape.

**Last Updated**: October 15, 2025  
**Version**: ERPNext v15.83.0