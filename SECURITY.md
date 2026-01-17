# ERPNext Docker Security Guide

## 🔐 Security Best Practices for Production Deployment

This guide covers essential security considerations for deploying ERPNext in production, including user management, password generation, and port configuration.

---

## 1. 👤 User Management and File Permissions

### Understanding Docker User in Official Images

**IMPORTANT**: The official `frappe/erpnext` Docker images run as a **fixed user**:

| Property | Value | Notes |
|----------|-------|-------|
| Username | `frappe` | Created inside the container |
| UID | `1000` | **Fixed - cannot be changed at runtime** |
| GID | `1000` | **Fixed - cannot be changed at runtime** |

This is baked into the Docker image during build time. You **cannot** change the UID by setting environment variables - the images are pre-built with files owned by UID 1000.

### Why UID 1000?

- UID 1000 is typically the first regular user created on Linux systems
- The Frappe Docker images use `useradd` without specifying a UID, which assigns 1000 on a fresh image
- All files in `/home/frappe/frappe-bench/` are owned by UID 1000

### Setting Up File Permissions

Since the container runs as UID 1000, your host directories must be accessible by UID 1000:

#### Option A: UID 1000 Exists on Your System (Most Common) ✅

```bash
# Check if UID 1000 exists
getent passwd 1000

# If it's a regular user, you can use them or create the data directories:
mkdir -p data/{sites,logs,db,redis_queue}
sudo chown -R 1000:1000 data/
chmod -R 755 data/
```

#### Option B: Create a User with UID 1000 ⭐ RECOMMENDED

```bash
# Check if UID 1000 is available
id 1000 2>/dev/null && echo "UID 1000 exists" || echo "UID 1000 is available"

# If available, create a dedicated erpnext user with UID 1000
sudo useradd -u 1000 -m -s /bin/bash erpnext
sudo usermod -aG docker erpnext

# Create directories
sudo -u erpnext mkdir -p data/{sites,logs,db,redis_queue}
chmod -R 755 data/
```

#### Option C: UID 1000 Is Taken by System User ⚠️

If UID 1000 belongs to a system/service account you can't use:

```bash
# Create directories as root and set ownership to UID 1000
sudo mkdir -p data/{sites,logs,db,redis_queue}
sudo chown -R 1000:1000 data/
chmod -R 755 data/
```

This works because Docker maps by UID number, not username. Even if no user with UID 1000 exists on your host, the container will still work correctly.

### 🛡️ Security Recommendations for User Management

1. **Dedicated User**: If possible, create a dedicated user with UID 1000 named `erpnext`
2. **Docker Group**: Add the user to the docker group for running compose commands
3. **Limited Privileges**: The user should only have Docker access, not sudo
4. **Project Directory**: Store the project in a dedicated location
```bash
# Set up project directory
sudo mkdir -p /opt/erpnext
sudo chown 1000:1000 /opt/erpnext
sudo chmod 755 /opt/erpnext
```

### 📂 Understanding Volume Permissions

**How it works:**
1. Container process runs as UID 1000 inside the container
2. Files created in mounted volumes are owned by UID 1000 on the host
3. Your host must allow UID 1000 to read/write the data directories

**Verification:**
```bash
# After starting containers, check file ownership
ls -la data/sites/
# Should show files owned by UID 1000 (or your erpnext user)

# Verify container is running as expected
docker compose exec backend id
# Output: uid=1000(frappe) gid=1000(frappe) groups=1000(frappe)
```

### ⚡ Quick Setup Summary

```bash
# 1. Create directories with correct permissions
mkdir -p data/{sites,logs,db,redis_queue}
sudo chown -R 1000:1000 data/

# 2. Copy and configure environment
cp .env.example .env
nano .env  # Set SITE_NAME, passwords, etc.

# 3. Start services
docker compose pull
docker compose up -d
```

**Best practices for execution:**
```bash
# Switch to erpnext user (if you created one with UID 1000)
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

### 🔍 Troubleshooting Permission Issues

**If you see permission errors:**
```bash
# Verify container is running as UID 1000
docker compose exec backend id
# Expected: uid=1000(frappe) gid=1000(frappe) groups=1000(frappe)

# Check data directory ownership
ls -la data/
# Should show UID 1000

# Fix ownership if needed (must be UID 1000!)
sudo chown -R 1000:1000 data/

# Check if any files have wrong permissions
find data/ ! -user 1000 -ls
```

### 🚨 Important Notes About UID

1. **Cannot customize UID at runtime**: The official images have UID 1000 baked in
2. **Building custom images**: If you need a different UID, you must build your own images with `--build-arg USER_ID=...`
3. **Rootless Docker**: Works fine with UID namespace remapping
4. **SELinux/AppArmor**: May require additional configuration for volume mounts

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