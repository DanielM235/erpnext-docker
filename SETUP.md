# ERPNext Production Setup Guide

> **Version**: ERPNext v16.0.1 | **Platform**: Debian 12 + Host Nginx

## 📋 Quick Setup Instructions

### 1. Initial Directory Setup

**⚠️ IMPORTANT**: The official ERPNext Docker images run as **UID 1000**. This is fixed and cannot be changed at runtime. Your data directories must be accessible by UID 1000.

**Quick setup:**
```bash
# Create directories with proper permissions for UID 1000
mkdir -p data/{sites,logs,db,redis_queue}
sudo chown -R 1000:1000 data/
chmod -R 755 data/
```

**Optional: Create a dedicated host user with UID 1000 (recommended):**
```bash
# Check if UID 1000 is available
id 1000 2>/dev/null && echo "UID 1000 exists" || echo "UID 1000 is available"

# If available, create dedicated user
sudo useradd -u 1000 -m -s /bin/bash erpnext
sudo usermod -aG docker erpnext

# Create directories as the erpnext user
sudo -u erpnext mkdir -p data/{sites,logs,db,redis_queue}
chmod -R 755 data/
```

> **Note**: Even if you don't create a host user with UID 1000, the containers will work correctly as long as the data directories are owned by UID 1000. See **[SECURITY.md](SECURITY.md)** for detailed security considerations.

### 2. Environment Configuration
```bash
# Copy and configure environment variables
cp .env.example .env

# Edit the .env file with your production values
nano .env
```

### 3. Required Environment Variables
**You MUST configure these variables before starting:**

| Variable | Description | Example |
|----------|-------------|---------|
| `SITE_NAME` | Your domain name | `erp.company.com` |
| `ADMIN_PASSWORD` | ERPNext Administrator password | Strong password (min 8 chars) |
| `DB_ROOT_PASSWORD` | MariaDB root password | Very strong password |
| `FRONTEND_PORT` | Port for host nginx (default 8080) | `8080` |

**Optional but recommended:**
- `ERPNEXT_VERSION`: Specific version (default: 16.0.1)
- `TIMEZONE`: Your timezone (default: UTC)
- See `.env.example` for all options

### 4. Start Services
```bash
# Pull latest images
docker compose pull

# Start all services
docker compose up -d

# Monitor the site creation process (wait for completion)
docker compose logs -f create-site

# Check service status
docker compose ps
```

**⏱️ Initial startup takes 3-5 minutes** as it:
1. Configures common site settings
2. Initializes the database
3. Creates your ERPNext site
4. Installs ERPNext apps

### 5. Verify Installation
```bash
# Check all services are healthy
docker compose ps

# Verify site is accessible
curl -I http://localhost:8080

# If issues, check these logs:
docker compose logs backend
docker compose logs frontend
docker compose logs create-site
```

### 6. Access ERPNext
- **URL**: http://localhost:8080 (or your configured FRONTEND_PORT)
- **Username**: Administrator
- **Password**: (what you set in ADMIN_PASSWORD)

## 🔧 Host Nginx Configuration

Add this to your host Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy to ERPNext frontend
    # Change port if you modified FRONTEND_PORT in .env
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        
        # File upload size
        client_max_body_size 50m;
    }
    
    # Static files optimization
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## � Email Configuration (SMTP)

ERPNext requires email configuration for notifications, password resets, sending invoices, and other features.

### Option 1: Configure via ERPNext Web Interface (Recommended)

1. Log in to ERPNext as Administrator
2. Go to **Setup > Email > Email Account**
3. Click **New** to create a new email account
4. Configure the following:
   - **Email Address**: your-email@example.com
   - **Email Account Name**: Notifications (or any name)
   - **SMTP Server**: smtp.example.com
   - **SMTP Port**: 587 (for TLS) or 465 (for SSL)
   - **Use TLS**: ✓ (checked for port 587)
   - **Use SSL**: ✓ (checked for port 465)
   - **Password**: Your SMTP password
5. Enable **Default Outgoing** to use this for all outgoing emails
6. Click **Save**

### Option 2: Configure via bench command

After the site is created, you can configure email via the command line:

```bash
# Enter the backend container
docker compose exec backend bash

# Set up email account
bench --site ${SITE_NAME} set-config mail_server "smtp.example.com"
bench --site ${SITE_NAME} set-config mail_port 587
bench --site ${SITE_NAME} set-config use_tls 1
bench --site ${SITE_NAME} set-config mail_login "your-email@example.com"
bench --site ${SITE_NAME} set-config mail_password "your_smtp_password"
bench --site ${SITE_NAME} set-config auto_email_id "noreply@your-domain.com"
```

### Common SMTP Settings

| Provider | SMTP Server | Port | Encryption | Notes |
|----------|-------------|------|------------|-------|
| **Gmail** | smtp.gmail.com | 587 | TLS | Requires App Password |
| **Google Workspace** | smtp.gmail.com | 587 | TLS | Requires App Password |
| **Office 365** | smtp.office365.com | 587 | TLS | May need App Password with MFA |
| **Outlook.com** | smtp-mail.outlook.com | 587 | TLS | Standard login |
| **Amazon SES** | email-smtp.{region}.amazonaws.com | 587 | TLS | IAM credentials |
| **Mailgun** | smtp.mailgun.org | 587 | TLS | Domain credentials |
| **SendGrid** | smtp.sendgrid.net | 587 | TLS | API key as password |
| **Zoho Mail** | smtp.zoho.com | 587 | TLS | Standard login |

### Gmail / Google Workspace Setup

1. Enable 2-Factor Authentication on your Google account
2. Go to **Google Account > Security > App Passwords**
3. Generate a new App Password for "Mail"
4. Use this App Password (not your regular password) as `SMTP_PASSWORD`

### Testing Email Configuration

```bash
# Test email sending from within the container
docker compose exec backend bench --site ${SITE_NAME} sendmail your-test-email@example.com

# Check email queue
docker compose exec backend bench --site ${SITE_NAME} show-pending-emails
```

## �🚨 Important Security Notes

1. **Change all default passwords** in the .env file
2. **Use strong passwords** (minimum 16 characters)
3. **Enable firewall** to block direct access to Docker ports
4. **Regular backups** of the data directory
5. **Keep Docker images updated** regularly
6. **Monitor logs** for suspicious activity

## 📊 Monitoring and Maintenance

### Daily Monitoring
```bash
# Check container health
docker compose ps

# View resource usage
docker stats

# Check recent logs
docker compose logs --tail=100 backend
```

### Weekly Maintenance
```bash
# Update Docker images
docker compose pull

# Restart services with new images
docker compose up -d

# Clean up unused resources
docker system prune -f
```

### Monthly Backups
```bash
# Backup database
docker compose exec db mysqldump -u root -p${DB_ROOT_PASSWORD} ${DB_NAME} > backup_$(date +%Y%m%d).sql

# Backup sites data
tar -czf sites_backup_$(date +%Y%m%d).tar.gz data/sites/

# Store backups off-site for disaster recovery
```

## 🔧 Troubleshooting

### Common Issues

**Site not accessible:**
```bash
# Check if frontend is running
docker compose ps frontend

# Check frontend logs
docker compose logs frontend

# Verify nginx configuration on host
nginx -t && systemctl reload nginx
```

**Database connection errors:**
```bash
# Check database status
docker compose ps db

# Test database connectivity
docker compose exec db mysql -u root -p${DB_ROOT_PASSWORD} -e "SHOW DATABASES;"
```

**Performance issues:**
```bash
# Monitor resource usage
docker stats

# Check for memory or CPU limits
docker compose logs | grep -i "memory\|cpu\|limit"
```

## 📚 Additional Resources

- [ERPNext User Manual](https://docs.erpnext.com/)
- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---
**Version**: ERPNext v16.0.1  
**Last Updated**: January 2026