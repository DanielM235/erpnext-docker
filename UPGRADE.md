# ERPNext v16 Upgrade Guide

This document provides instructions for upgrading from ERPNext v15 to v16, and guidance for fresh v16 installations.

## 🆕 What's New in ERPNext v16

ERPNext v16 was released in January 2026 with significant improvements:

### Key Features
- **Master Production Schedule & MRP**: New consolidated planning views for production and purchase needs
- **Stock Reservation for Production Plan & Work Order**: Reserve materials directly from planning documents
- **Enhanced Subcontracting**: New Subcontracted Sales Order and Subcontracting Inward Order documents
- **Improved Point of Sale**: List-style item selector with partial payment support
- **Better Reporting**: Enhanced Trial Balance, Ledger reports with new filters
- **New Naming Series**: `.ABBR.` placeholder for company abbreviation in document numbers
- **Per-Company Settings**: Stock valuation method and manufacturing warehouses now configurable per company

### Technical Updates
- Python 3.12+ support
- Node.js 22+ support  
- Updated dependencies and security patches
- Improved Docker image efficiency (smaller size)
- Better platform support (linux/amd64, linux/arm64)

---

## 🔄 Upgrading from v15 to v16

### Prerequisites
- Current working ERPNext v15 installation
- Full backup of all data
- At least 30 minutes of maintenance window
- Tested upgrade path in staging environment

### Pre-Upgrade Checklist

```bash
# 1. Verify current version
docker compose exec backend bench version

# 2. Check for pending migrations
docker compose exec backend bench --site <your-site> show-pending-migrations

# 3. Create full backup
docker compose exec backend bench --site <your-site> backup --with-files

# 4. Copy backup to host system
docker compose cp backend:/home/frappe/frappe-bench/sites/<your-site>/private/backups/ ./backups/

# 5. Note your current database size
docker compose exec db mysql -u root -p${DB_ROOT_PASSWORD} -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables GROUP BY table_schema;"
```

### Upgrade Steps

#### Step 1: Stop Current Services
```bash
# Stop all services gracefully
docker compose down

# Verify all containers are stopped
docker compose ps
```

#### Step 2: Update Configuration Files

Update your `.env` file:
```bash
# Change version from v15 to v16
ERPNEXT_VERSION=16.0.1

# Optionally update MariaDB if needed (10.6 is recommended for v16)
DB_VERSION=10.6

# Ensure Redis is up to date
REDIS_VERSION=7-alpine
```

If you're using the old docker-compose.yml structure, replace it with the new v16 version from this repository. Your old configuration has been backed up as `docker-compose.v15.bak.yml`.

#### Step 3: Pull New Images
```bash
# Pull all updated images
docker compose pull

# Verify new images
docker images | grep erpnext
```

#### Step 4: Start Services
```bash
# Start all services
docker compose up -d

# Monitor startup (wait for all services to be healthy)
docker compose ps
docker compose logs -f configurator
```

#### Step 5: Run Migrations
```bash
# Wait for configurator to complete
# Then run database migrations
docker compose exec backend bench --site <your-site> migrate

# This may take several minutes depending on your data size
# Monitor the output for any errors
```

#### Step 6: Post-Migration Tasks
```bash
# Clear all caches
docker compose exec backend bench --site <your-site> clear-cache
docker compose exec backend bench --site <your-site> clear-website-cache

# Rebuild assets
docker compose exec backend bench build

# Restart all services
docker compose restart
```

#### Step 7: Verify Upgrade
```bash
# Check new version
docker compose exec backend bench version

# Verify site is accessible
curl -I http://localhost:8080

# Check for any errors in logs
docker compose logs backend | tail -50
docker compose logs frontend | tail -20
```

### Rollback Procedure

If something goes wrong during the upgrade:

```bash
# 1. Stop v16 services
docker compose down

# 2. Restore old docker-compose.yml
mv docker-compose.yml docker-compose.v16.yml
mv docker-compose.v15.bak.yml docker-compose.yml

# 3. Update .env to use v15 version
sed -i 's/ERPNEXT_VERSION=16.0.1/ERPNEXT_VERSION=15.94.3/' .env

# 4. If database was migrated, restore from backup
# CAUTION: This will overwrite current database
docker compose up -d db
docker compose exec db mysql -u root -p${DB_ROOT_PASSWORD} < ./backups/<your-backup>.sql

# 5. Restore sites directory if needed
# tar -xzf ./backups/sites_backup_<date>.tar.gz -C data/

# 6. Start v15 services
docker compose up -d

# 7. Verify rollback
docker compose exec backend bench version
```

---

## 🆕 Fresh v16 Installation

For new installations, follow these steps:

### Step 1: Prepare Environment
```bash
# Clone or copy configuration files
cd /opt/erpnext  # or your preferred location

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### Step 2: Configure Environment Variables

At minimum, set these values in `.env`:
```bash
COMPOSE_PROJECT_NAME=erpnext-prod
ERPNEXT_VERSION=16.0.1
SITE_NAME=your-domain.com
ADMIN_PASSWORD=your_secure_password
DB_ROOT_PASSWORD=your_very_secure_db_password
```

### Step 3: Create Data Directories
```bash
# Create directory structure
mkdir -p data/{sites,logs,db,redis_queue}

# Set permissions (UID 1000 is the frappe user in container)
sudo chown -R 1000:1000 data/
chmod -R 755 data/
```

### Step 4: Start Services
```bash
# Pull images and start services
docker compose pull
docker compose up -d

# Monitor site creation
docker compose logs -f create-site

# Wait until you see "Site created successfully" or similar
```

### Step 5: Verify Installation
```bash
# Check all services are running
docker compose ps

# Test site access
curl -I http://localhost:8080

# Login at http://your-domain.com
# Username: Administrator
# Password: (what you set in ADMIN_PASSWORD)
```

---

## ⚠️ Known Issues & Solutions

### Issue: Site creation fails with database connection error
**Solution**: Ensure MariaDB has fully started before site creation
```bash
docker compose logs db
# Wait for "ready for connections" message
docker compose restart create-site
```

### Issue: WebSocket connection fails
**Solution**: Verify frontend can reach websocket service
```bash
docker compose logs websocket
docker compose logs frontend
# Check SOCKETIO environment variable in frontend
```

### Issue: Background jobs not processing
**Solution**: Check queue worker logs and Redis connection
```bash
docker compose logs queue-long
docker compose logs redis-queue
```

### Issue: File upload fails with "413 Request Entity Too Large"
**Solution**: Increase CLIENT_MAX_BODY_SIZE in .env
```bash
CLIENT_MAX_BODY_SIZE=100m
docker compose up -d frontend
```

---

## 📊 Configuration Changes from v15

### Removed Environment Variables
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - No longer needed for basic setup (site creates its own database)
- `WORKER_CLASS`, `BACKEND_WORKERS`, `BACKEND_TIMEOUT` - Now configured via bench

### New Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| `FRAPPE_SITE_NAME_HEADER` | Site resolution method | `$$host` |
| `FRAPPE_REDIS_CACHE` | Redis cache URL for workers | Auto-configured |
| `FRAPPE_REDIS_QUEUE` | Redis queue URL for workers | Auto-configured |
| `PULL_POLICY` | Docker image pull policy | `always` |
| `RESTART_POLICY` | Service restart policy | `unless-stopped` |

### Changed Default Values
| Setting | v15 Default | v16 Default |
|---------|-------------|-------------|
| MariaDB Version | 10.11 | 10.6 |
| Redis Version | 7-alpine | 7-alpine |
| Backend Memory | 4G | 4G |
| Queue Memory | 1G | 2G |

### Docker Compose Structure Changes
- Added YAML anchors for DRY configuration
- Separate `create-site` service (was part of configurator)
- `platform: linux/amd64` specified for compatibility
- New `FRAPPE_REDIS_*` environment variables for workers
- Improved health check endpoints

---

## 📞 Getting Help

- **ERPNext Forum**: https://discuss.frappe.io/
- **GitHub Issues**: https://github.com/frappe/erpnext/issues
- **Frappe Docker Issues**: https://github.com/frappe/frappe_docker/issues

---

**Version**: ERPNext v16.0.1  
**Last Updated**: January 2026
