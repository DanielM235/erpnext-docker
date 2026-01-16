# ERPNext Docker Production Deployment

Production-ready Docker Compose configuration for ERPNext v16, based on the official [Frappe Docker](https://github.com/frappe/frappe_docker) repository.

## 🎯 Project Overview

This project provides a secure, scalable, and maintainable Docker-based deployment for ERPNext v16 in production environments. It follows Docker Compose best practices and integrates seamlessly with existing Nginx reverse proxy infrastructure on Debian 12.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Debian 12 (or compatible Linux distribution)
- **Docker**: v24.0+ with Compose v2
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 20GB free space
- **Network**: Nginx reverse proxy on host for SSL termination

### Quick Check
```bash
docker --version      # Should be 24.0+
docker compose version  # Should be v2.x
```

## 🚀 Quick Start

### 1. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your values (REQUIRED: SITE_NAME, ADMIN_PASSWORD, DB_ROOT_PASSWORD)
nano .env
```

### 2. Create Data Directories
```bash
mkdir -p data/{sites,logs,db,redis_queue}
sudo chown -R 1000:1000 data/
```

### 3. Deploy
```bash
# Pull images and start
docker compose pull
docker compose up -d

# Monitor site creation (wait for completion)
docker compose logs -f create-site

# Check status
docker compose ps
```

### 4. Access ERPNext
- **URL**: http://localhost:8080
- **Username**: Administrator
- **Password**: (your ADMIN_PASSWORD from .env)

📦 **For detailed setup**: See **[SETUP.md](SETUP.md)**  
🚀 **For server deployment**: See **[DEPLOYMENT.md](DEPLOYMENT.md)**  
⬆️ **Upgrading from v15**: See **[UPGRADE.md](UPGRADE.md)**

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────────────────────────────┐
│   Host Nginx    │─────────│           Docker Network                │
│  (SSL + Proxy)  │  :8080  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
└─────────────────┘         │  │Frontend │──│ Backend │──│Websocket│  │
                            │  │ (Nginx) │  │(Gunicorn)│ │(Node.js)│  │
                            │  └─────────┘  └────┬────┘  └─────────┘  │
                            │                    │                     │
                            │  ┌─────────┐  ┌────┴────┐  ┌─────────┐  │
                            │  │ MariaDB │  │  Redis  │  │Scheduler│  │
                            │  │  10.6   │  │  Cache  │  │& Workers│  │
                            │  └─────────┘  └─────────┘  └─────────┘  │
                            └─────────────────────────────────────────┘
```

## 📁 Project Structure

```
erpnext-docker/
├── docker-compose.yml      # Main Docker Compose configuration (v16)
├── .env.example            # Environment variables template
├── .env                    # Your configuration (git-ignored)
├── data/                   # Persistent data volumes
│   ├── sites/              # ERPNext sites and uploads
│   ├── logs/               # Application logs
│   ├── db/                 # MariaDB data
│   └── redis_queue/        # Redis queue persistence
├── SETUP.md                # Quick setup guide
├── DEPLOYMENT.md           # Server deployment guide
├── UPGRADE.md              # v15 to v16 upgrade guide
├── SECURITY.md             # Security configuration
└── README.md               # This file
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
- **Image**: `frappe/erpnext:v16.0.1`
- **Purpose**: Main application server (backend, frontend, workers)
- **Volumes**: Site data, logs
- **Security**: Non-root user, resource limits, no-new-privileges

#### Database (MariaDB)
- **Image**: `mariadb:10.6`
- **Purpose**: Database server (officially recommended by Frappe)
- **Volumes**: Persistent database storage
- **Security**: Custom user, health checks, connection limits

#### Redis Cache & Queue
- **Image**: `redis:7-alpine`
- **Purpose**: Caching, session storage, and background job queue
- **Security**: No external exposure, memory limits, persistence for queue

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

**Version**: ERPNext v16.0.1 (Frappe Framework v16)  
**Last Updated**: January 2026  
**Maintainer**: Your Organization  
**Support**: Create an issue in this repository for support