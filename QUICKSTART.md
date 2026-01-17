# ERPNext Docker Quick Start Guide

This guide walks you through the complete setup process from initial configuration to a running ERPNext instance.

## Prerequisites

- Docker Engine 20.10+ and Docker Compose v2+
- Debian 12 (or compatible Linux distribution)
- Minimum 4GB RAM (8GB+ recommended for production)
- 20GB+ free disk space
- Root or sudo access

Verify Docker installation:
```bash
docker --version
docker compose version
```

---

## Step 1: Copy Environment Configuration

Create your environment file from the template:

```bash
cd /home/dev1/dev/dmla/finance/erpnext/erpnext-docker
cp .env.example .env
```

---

## Step 2: Generate Secure Passwords

**CRITICAL**: Generate strong random passwords for security.

### Generate both passwords at once:
```bash
echo "ADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d '=+/' | cut -c1-16)"
echo "DB_ROOT_PASSWORD=$(openssl rand -base64 24 | tr -d '=+/' | cut -c1-24)"
```

**Copy the output** - you'll need these values in the next step.

### Alternative: Generate individually
```bash
# For ERPNext admin password
openssl rand -base64 16 | tr -d '=+/' | cut -c1-16

# For database root password
openssl rand -base64 24 | tr -d '=+/' | cut -c1-24
```

---

## Step 3: Configure Required Environment Variables

Edit the `.env` file:

```bash
nano .env
```

### MUST CHANGE - Required Configuration:

1. **SITE_NAME** - Your domain name (CRITICAL):
   ```bash
   SITE_NAME=erp.yourdomain.com
   ```
   - For production: Use your actual domain (e.g., `erp.company.com`)
   - For testing/local: Use `localhost` or IP address

2. **ADMIN_PASSWORD** - ERPNext Administrator password:
   ```bash
   ADMIN_PASSWORD=<paste-generated-password-here>
   ```
   - Paste the password generated in Step 2

3. **DB_ROOT_PASSWORD** - MariaDB root password:
   ```bash
   DB_ROOT_PASSWORD=<paste-generated-password-here>
   ```
   - Paste the password generated in Step 2

### RECOMMENDED TO REVIEW:

4. **COMPOSE_PROJECT_NAME** - Project identifier:
   ```bash
   COMPOSE_PROJECT_NAME=erpnext-prod
   ```
   - Change if you want a different project name

5. **FRONTEND_PORT** - External access port:
   ```bash
   FRONTEND_PORT=8080
   ```
   - Change if port 8080 conflicts with existing applications

6. **TIMEZONE** - System timezone:
   ```bash
   TIMEZONE=UTC
   ```
   - Use your timezone (e.g., `America/New_York`, `Europe/Paris`, `Asia/Singapore`)

Save and exit (Ctrl+X, then Y, then Enter in nano).

---

## Step 4: Create Data Directories

Create the required directories with proper permissions:

```bash
# Create directory structure
mkdir -p data/{sites,logs,db,redis_queue}

# Set correct ownership (user ID 1000 is the frappe user in containers)
sudo chown -R 1000:1000 data/

# Verify permissions
ls -la data/
```

Expected output should show directories owned by user ID 1000.

---

## Step 5: Start ERPNext Services

### Start all services in detached mode:
```bash
docker compose up -d
```

This will:
- Pull all required Docker images (may take 5-10 minutes on first run)
- Create the Docker network
- Start all services (database, redis, backend, frontend, etc.)
- Configure ERPNext
- Create your site

---

## Step 6: Monitor Site Creation (IMPORTANT)

Watch the site creation process to ensure it completes successfully:

```bash
docker compose logs -f create-site
```

**What to look for:**
- `Waiting for sites/common_site_config.json to be created`
- `sites/common_site_config.json found`
- `Creating site <your-site-name>...`
- `Site <your-site-name> created successfully` ✅

**Expected duration:** 3-5 minutes

Press `Ctrl+C` to exit the logs once you see "Site created successfully".

### If errors occur:
```bash
# Check all service logs
docker compose logs

# Check specific service
docker compose logs backend
docker compose logs db
```

---

## Step 7: Verify All Services Are Running

Check that all services are healthy:

```bash
docker compose ps
```

Expected output - all services should show "Up" or "Up (healthy)":
```
NAME                              STATUS
erpnext-prod_backend              Up (healthy)
erpnext-prod_configurator         Exited (0)
erpnext-prod_create_site          Exited (0)
erpnext-prod_database             Up (healthy)
erpnext-prod_frontend             Up (healthy)
erpnext-prod_queue_long           Up
erpnext-prod_queue_short          Up
erpnext-prod_redis_cache          Up (healthy)
erpnext-prod_redis_queue          Up (healthy)
erpnext-prod_scheduler            Up
erpnext-prod_websocket            Up
```

**Note:** `configurator` and `create-site` containers will show "Exited (0)" - this is normal.

---

## Step 8: Post-Deployment Configuration

### 8.1 Find Docker Gateway IP (CRITICAL for Security)

Determine the Docker gateway IP for proper client IP logging:

```bash
docker network inspect erpnext-prod_network | grep Gateway
```

**Example output:**
```json
"Gateway": "172.18.0.1"
```

### 8.2 Update UPSTREAM_REAL_IP_ADDRESS

Edit your `.env` file:

```bash
nano .env
```

Find the line:
```bash
UPSTREAM_REAL_IP_ADDRESS=0.0.0.0/0
```

Replace with the Gateway IP from the previous command:
```bash
UPSTREAM_REAL_IP_ADDRESS=172.18.0.1
```

### 8.3 Restart Frontend Service

Apply the updated configuration:

```bash
docker compose restart frontend
```

Verify the restart:
```bash
docker compose ps frontend
```

---

## Step 9: Access ERPNext

### Option A: Local Testing (No Nginx Reverse Proxy)

Access ERPNext directly via Docker:

```bash
# If FRONTEND_PORT=8080 (default)
http://localhost:8080

# Or using your server's IP
http://YOUR_SERVER_IP:8080
```

### Option B: Production (With Host Nginx - Recommended)

**Before accessing via domain:**
1. Configure host Nginx reverse proxy (see `SETUP.md`)
2. Set up SSL certificates with Let's Encrypt
3. Ensure DNS points to your server

Then access via:
```
https://erp.yourdomain.com
```

---

## Step 10: First Login

1. **Navigate to your ERPNext URL**
2. **Login credentials:**
   - **Username:** `Administrator`
   - **Password:** `<your ADMIN_PASSWORD from .env>`

3. **Complete the Setup Wizard:**
   - Company information
   - Chart of accounts
   - Financial year
   - User preferences

---

## Step 11: Save Your Credentials (IMPORTANT)

Store these credentials in a secure password manager:

```
ERPNext Administrator Password: <from ADMIN_PASSWORD>
Database Root Password: <from DB_ROOT_PASSWORD>
Site Name: <from SITE_NAME>
Docker Gateway IP: <from step 8.1>
```

**NEVER commit your `.env` file to version control!**

---

## Verification Checklist

Before proceeding to production, verify:

- [ ] All Docker containers are running (`docker compose ps`)
- [ ] Site created successfully (check logs)
- [ ] Can access ERPNext web interface
- [ ] Can login with Administrator credentials
- [ ] Setup wizard completed
- [ ] UPSTREAM_REAL_IP_ADDRESS updated with gateway IP
- [ ] Credentials saved securely
- [ ] `.env` file is NOT in git (check `.gitignore`)

---

## Next Steps

### For Development/Testing:
- Create test users and explore features
- Configure email settings in ERPNext
- Import sample data

### For Production:
1. **Configure host Nginx reverse proxy** (see `SETUP.md`)
   - Set up SSL with Let's Encrypt
   - Configure firewall rules
   
2. **Set up backups** (see `DEPLOYMENT.md`)
   ```bash
   docker compose exec backend bench --site <site-name> backup --with-files
   ```

3. **Configure email** in ERPNext:
   - Setup → Email Domain
   - Setup → Email Account
   - Test email sending

4. **Harden security**:
   - Change default ports if needed
   - Set up firewall rules (allow only 80, 443)
   - Enable fail2ban
   - Regular security updates

5. **Monitor performance**:
   ```bash
   # Check resource usage
   docker stats
   
   # Check logs
   docker compose logs -f backend
   ```

---

## Common Commands

### View logs:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f db
```

### Restart services:
```bash
# All services
docker compose restart

# Specific service
docker compose restart backend
docker compose restart frontend
```

### Stop all services:
```bash
docker compose down
```

### Start all services:
```bash
docker compose up -d
```

### Access container shell:
```bash
# Backend/bench commands
docker compose exec backend bash

# Database access
docker compose exec db mysql -u root -p
```

### Create database backup:
```bash
docker compose exec backend bench --site <site-name> backup --with-files
```

---

## Troubleshooting

### Site creation fails:
```bash
# Check database connectivity
docker compose logs db

# Check configurator logs
docker compose logs configurator

# Retry site creation
docker compose up create-site
```

### Cannot access web interface:
```bash
# Check frontend logs
docker compose logs frontend

# Check backend health
docker compose exec backend curl -s http://localhost:8000/api/method/frappe.ping

# Check port binding
netstat -tulpn | grep 8080
```

### Permission errors:
```bash
# Fix data directory permissions
sudo chown -R 1000:1000 data/

# Restart services
docker compose restart
```

### Database connection errors:
```bash
# Verify database is running
docker compose ps db

# Check database logs
docker compose logs db

# Test connection
docker compose exec backend bash -c "mysql -h db -u root -p${DB_ROOT_PASSWORD} -e 'SELECT 1'"
```

---

## Getting Help

- **Official Documentation:** https://docs.erpnext.com
- **Frappe Docker Repo:** https://github.com/frappe/frappe_docker
- **ERPNext Forum:** https://discuss.erpnext.com
- **Check Logs:** `docker compose logs -f`

---

## Important Notes

⚠️ **Security Warnings:**
- NEVER use default passwords in production
- NEVER commit `.env` file to git
- ALWAYS use SSL/HTTPS in production
- ALWAYS keep regular backups
- ALWAYS update UPSTREAM_REAL_IP_ADDRESS after network creation

✅ **Best Practices:**
- Use specific version tags (not `latest`) for production
- Set up automated backups
- Monitor disk space and resource usage
- Keep Docker and system packages updated
- Document any custom configurations

---

**Installation Complete!** 🎉

Your ERPNext instance should now be running. Proceed with the Setup Wizard and start exploring ERPNext features.
