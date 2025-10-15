# ERPNext Docker Security Guide

## 🔐 Security Best Practices for Production Deployment

This guide covers essential security considerations for deploying ERPNext in production, including user management, password generation, and port configuration.

---

## 1. 👤 User Management and Docker Compose Execution

### Understanding User ID 1000 in Docker

The Docker Compose configuration specifies `user: "1000:1000"` for containers. This refers to:
- **User ID (UID)**: 1000
- **Group ID (GID)**: 1000

This is a security best practice to avoid running containers as root.

### Scenario 1: User ID 1000 Already Exists

Check if user ID 1000 exists on your server:
```bash
# Check if UID 1000 exists
id 1000 2>/dev/null && echo "UID 1000 exists" || echo "UID 1000 not found"

# See which user has UID 1000
getent passwd 1000

# Check current user's UID
id -u
```

**If UID 1000 exists and belongs to a regular user:**
- ✅ **Recommended**: Use that existing user to run Docker Compose
- The user should be in the `docker` group to run Docker commands

**Setup for existing UID 1000:**
```bash
# Add user to docker group (replace 'username' with actual username)
sudo usermod -aG docker username

# Verify docker group membership
groups username

# Switch to that user or run commands as that user
sudo -u username docker compose up -d
```

### Scenario 2: UID 1000 Does Not Exist

**Option A: Create a dedicated ERPNext user with UID 1000** ⭐ **RECOMMENDED**
```bash
# Create erpnext user with specific UID 1000
sudo useradd -u 1000 -g users -m -s /bin/bash erpnext

# Add to docker group
sudo usermod -aG docker erpnext

# Set password for the user
sudo passwd erpnext

# Switch to erpnext user
sudo -u erpnext bash
```

**Option B: Use a different UID and modify Docker configuration**
```bash
# Create user with system-assigned UID
sudo useradd -m -s /bin/bash erpnext
sudo usermod -aG docker erpnext

# Check the assigned UID
id erpnext
# Example output: uid=1001(erpnext) gid=1001(erpnext)

# Update docker-compose.yml to use the new UID
# Replace all instances of "1000:1000" with "1001:1001" (or your actual UID)
```

### Scenario 3: UID 1000 Belongs to System Service

If UID 1000 is used by a system service:
```bash
# Check what owns UID 1000
ps -u 1000
ls -la /home/ | grep 1000

# If it's a system service, create ERPNext user with different UID
sudo useradd -u 1001 -m -s /bin/bash erpnext
sudo usermod -aG docker erpnext

# Update docker-compose.yml accordingly
sed -i 's/user: "1000:1000"/user: "1001:1001"/g' docker-compose.yml
```

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