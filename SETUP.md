# ERPNext Production Setup Guide

## 📋 Quick Setup Instructions

### 1. Initial Directory Setup

**⚠️ IMPORTANT**: Before creating directories, read **[SECURITY.md](SECURITY.md)** if:
- User ID 1000 doesn't exist on your system  
- You need to use a different port than 8080
- You want to understand Docker user mapping

**Quick setup (if UID 1000 is available):**
```bash
# Create directories with proper permissions
mkdir -p data/{sites,logs,db,redis_queue}
sudo chown -R 1000:1000 data/
chmod -R 755 data/
```

**Custom UID setup (if UID 1000 is not available):**
```bash
# 1. Create user and get UID
sudo useradd -m -s /bin/bash erpnext
sudo usermod -aG docker erpnext
USER_UID=$(id -u erpnext)

# 2. Update .env with your user's UID
cp .env.example .env
echo "DOCKER_USER_ID=$USER_UID" >> .env
echo "DOCKER_GROUP_ID=$USER_UID" >> .env

# 3. Create directories as the correct user
sudo -u erpnext mkdir -p data/{sites,logs,db,redis_queue}
sudo -u erpnext chmod -R 755 data/
```

### 2. Environment Configuration
```bash
# Copy and configure environment variables
cp .env.example .env

# Edit the .env file with your production values
nano .env
```

### 3. Required Environment Variables
**You MUST configure these variables before starting:**

- `SITE_NAME`: Your domain name (e.g., erp.company.com)
- `ADMIN_PASSWORD`: Strong password for ERPNext admin (see [SECURITY.md](SECURITY.md) for password generation)
- `DB_ROOT_PASSWORD`: Strong password for database root
- `DB_PASSWORD`: Strong password for application database user
- `FRONTEND_PORT`: Port for host nginx connection (default 8080, change if conflicts)
- `DOCKER_USER_ID`: User ID for containers (default 1000, change if UID 1000 unavailable)
- `DOCKER_GROUP_ID`: Group ID for containers (default 1000, change if needed)

### 4. Start Services
```bash
# Start all services
docker compose up -d

# Monitor the startup process
docker compose logs -f configurator

# Check service status
docker compose ps
```

### 5. Verify Installation
```bash
# Check if your site is accessible
curl -I http://localhost:8080

# View logs if there are issues
docker compose logs backend
docker compose logs frontend
```

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

## 🚨 Important Security Notes

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
**Version**: ERPNext v15.83.0  
**Last Updated**: October 15, 2025