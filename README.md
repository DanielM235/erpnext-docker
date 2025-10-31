# ERPNext Docker Production Deployment

This repository contains the production-ready Docker Compose configuration for deploying ERPNext using the official [Frappe Docker](https://github.com/frappe/frappe_docker) guidelines.

## 🎯 Project Overview

This project provides a secure, scalable, and maintainable Docker-based deployment configuration for ERPNext in production environments. It follows Docker Compose best practices and integrates seamlessly with existing reverse proxy infrastructure.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Debian 12 (or compatible Linux distribution)
- **Docker**: Latest stable version (24.0+)
- **Docker Compose**: v2.x (latest recommended)
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 20GB free space
- **Network**: HTTPS reverse proxy (Nginx) running on host

### Infrastructure Requirements
- Nginx reverse proxy configured at host level for SSL termination
- Domain name with proper DNS configuration
- SSL certificate (Let's Encrypt recommended)
- Firewall configured to allow only necessary ports

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Host Nginx    │────│  Docker Network │────│   ERPNext App   │
│  (SSL/Reverse   │    │                 │    │   Container     │
│     Proxy)      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   MariaDB/      │
                       │   PostgreSQL    │
                       │   Container     │
                       └─────────────────┘
```

## 🚀 Quick Start

### 1. Setup and Deployment
```bash
# For local development/testing
git clone <repository-url>
cd erpnext-docker

# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env
```

**📦 For Production Deployment**: See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete instructions on transferring files from your local Ubuntu 24.10 machine to your Debian 12 production server via SSH.

### 2. Configure Environment Variables
Edit the `.env` file with your specific values:
```bash
# Database Configuration
DB_ROOT_PASSWORD=your_secure_root_password
DB_PASSWORD=your_secure_db_password
DB_NAME=erpnext_db
DB_USER=erpnext_user

# ERPNext Configuration
SITE_NAME=your-domain.com
ADMIN_PASSWORD=your_admin_password

# Security
SECRET_KEY=your_long_random_secret_key
```

### 3. Deploy
```bash
# Create Docker network (if not exists)
docker network create erpnext-network

# Start services
docker compose up -d

# Check status
docker compose ps
```

### 4. Initial Setup
```bash
# Create your first site
docker compose exec erpnext bench new-site your-domain.com \
  --admin-password your_admin_password \
  --db-root-password your_db_root_password

# Install ERPNext app
docker compose exec erpnext bench --site your-domain.com install-app erpnext
```

## 📁 Project Structure

```
erpnext-docker/
├── docker-compose.yml          # Main Docker Compose configuration
├── docker-compose.override.yml # Local development overrides (optional)
├── .env.example               # Environment variables template
├── .env                      # Environment variables (git-ignored)
├── nginx/                    # Nginx configuration for container
│   ├── nginx.conf           # Main Nginx config
│   └── sites-available/     # Site-specific configurations
├── backups/                 # Backup storage directory
├── logs/                   # Application logs
├── data/                   # Persistent data volumes
│   ├── sites/              # ERPNext sites data
│   └── db/                 # Database data
└── docs/                   # Additional documentation
    ├── deployment.md       # Detailed deployment guide
    ├── maintenance.md      # Maintenance procedures
    └── troubleshooting.md  # Common issues and solutions
```

## 🔒 Security Best Practices

### Docker Security
- **Non-root containers**: All containers run as non-root users
- **Read-only filesystems**: Applied where possible
- **Resource limits**: CPU and memory limits configured
- **Network isolation**: Custom Docker networks with minimal exposure
- **Secrets management**: Use Docker secrets for sensitive data

### Environment Security
- **Environment variables**: Never commit `.env` file
- **Strong passwords**: Use complex, unique passwords
- **Regular updates**: Keep Docker images and host system updated
- **Firewall**: Configure iptables/UFW to restrict access
- **SSL/TLS**: Always use HTTPS in production

### Data Protection
- **Backups**: Automated daily backups configured
- **Encryption**: Database and volume encryption recommended
- **Access control**: Implement proper user permissions
- **Audit logging**: Enable comprehensive logging

## 🔧 Configuration

### Environment Variables
All configuration is managed through environment variables defined in `.env`:

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DB_ROOT_PASSWORD` | Database root password | `super_secure_password` | Yes |
| `DB_PASSWORD` | Application database password | `app_secure_password` | Yes |
| `DB_NAME` | Database name | `erpnext_db` | Yes |
| `SITE_NAME` | Primary site domain | `erp.company.com` | Yes |
| `ADMIN_PASSWORD` | ERPNext admin password | `admin_secure_password` | Yes |
| `LETSENCRYPT_EMAIL` | Email for SSL certificates | `admin@company.com` | Yes |

### Docker Compose Services

#### ERPNext Application
- **Image**: `frappe/erpnext:latest`
- **Purpose**: Main application server
- **Volumes**: Site data, logs, backups
- **Security**: Non-root user, resource limits

#### Database (MariaDB)
- **Image**: `mariadb:10.8`
- **Purpose**: Database server
- **Volumes**: Persistent database storage
- **Security**: Custom user, encrypted storage

#### Redis Cache
- **Image**: `redis:alpine`
- **Purpose**: Caching and session storage
- **Security**: No external exposure, memory limits

## 🔄 Maintenance

### Regular Tasks
```bash
# View logs
docker compose logs -f erpnext

# Backup database
docker compose exec db mysqldump -u root -p erpnext_db > backup_$(date +%Y%m%d).sql

# Update containers
docker compose pull
docker compose up -d

# Clean unused resources
docker system prune -a
```

### Monitoring
- **Health checks**: Configured for all services
- **Log rotation**: Automatic log rotation enabled
- **Resource monitoring**: Use `docker stats` to monitor usage
- **Alerts**: Configure monitoring for disk space, memory, CPU

## 🚨 Troubleshooting

### Common Issues
1. **Container won't start**: Check logs with `docker compose logs [service]`
2. **Database connection failed**: Verify environment variables and network connectivity
3. **Site not accessible**: Check Nginx proxy configuration and firewall rules
4. **Performance issues**: Monitor resource usage and scale accordingly

### Debug Mode
```bash
# Enable debug mode
docker compose -f docker-compose.yml -f docker-compose.debug.yml up -d

# Access container shell
docker compose exec erpnext bash
```

## 📚 Project Documentation

### 📖 Configuration Guides
- **[SETUP.md](SETUP.md)** - Quick setup and installation guide
- **[SECURITY.md](SECURITY.md)** - User management, passwords, and port configuration
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Transfer files from local to production server

### 🔗 External Resources
- [ERPNext Documentation](https://docs.erpnext.com/)
- [Frappe Docker Guide](https://github.com/frappe/frappe_docker)
- [Docker Compose Best Practices](https://docs.docker.com/compose/production/)
- [ERPNext Community Forum](https://discuss.erpnext.com/)

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

- **Production Use**: This configuration is optimized for production environments
- **Security**: Always change default passwords and keep systems updated
- **Backups**: Implement automated backup strategies before going live
- **Monitoring**: Set up proper monitoring and alerting
- **Documentation**: Keep this documentation updated as your setup evolves

---

**Last Updated**: October 2025  
**Maintainer**: Your Organization  
**Support**: Create an issue in this repository for support