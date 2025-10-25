# Deployment Guide - Health Data Exchange Platform

This guide provides step-by-step instructions for deploying the Health Data Exchange Platform to production.

## 🚀 Pre-Deployment Checklist

### Environment Requirements
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL 13+ (for production database)
- [ ] Redis (for caching and sessions)
- [ ] Nginx (for reverse proxy)
- [ ] SSL certificate (for HTTPS)
- [ ] Domain name configured

### Security Requirements
- [ ] Strong SECRET_KEY generated
- [ ] Database credentials secured
- [ ] SMTP credentials configured
- [ ] Firewall rules configured
- [ ] SSL/TLS certificates installed
- [ ] Environment variables secured

## 📦 Production Setup

### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server nginx
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Database Setup

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE health_data_exchange;
CREATE USER health_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE health_data_exchange TO health_user;
\q
```

### 3. Application Setup

```bash
# Clone repository
git clone <repository-url>
cd health-data-exchange

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Install frontend dependencies
npm install
npm run build
```

### 4. Environment Configuration

Create `.env` file:

```env
# Application
DEBUG=False
APP_NAME="Health Data Exchange API"
APP_VERSION="1.0.0"

# Security
SECRET_KEY="your-super-secure-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL="postgresql://health_user:secure_password_here@localhost/health_data_exchange"

# File Upload
UPLOAD_DIR="/var/www/health-data-exchange/uploads"
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=[".csv", ".xlsx", ".json"]

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Email
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
SMTP_USERNAME="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"

# Logging
LOG_LEVEL="INFO"
LOG_FILE="/var/log/health-data-exchange/app.log"

# MPC Settings
MPC_THRESHOLD=2
MPC_KEY_SIZE=32

# Audit
AUDIT_LOG_ENABLED=True
AUDIT_LOG_RETENTION_DAYS=90
```

### 5. Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
# Gunicorn configuration
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

### 6. Systemd Service

Create `/etc/systemd/system/health-data-exchange.service`:

```ini
[Unit]
Description=Health Data Exchange API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/health-data-exchange
Environment=PATH=/var/www/health-data-exchange/venv/bin
ExecStart=/var/www/health-data-exchange/venv/bin/gunicorn -c gunicorn.conf.py backend.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 7. Nginx Configuration

Create `/etc/nginx/sites-available/health-data-exchange`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Frontend
    location / {
        root /var/www/health-data-exchange/.next;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

### 8. SSL Certificate

```bash
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 9. Start Services

```bash
# Enable and start services
sudo systemctl enable health-data-exchange
sudo systemctl start health-data-exchange
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl enable redis
sudo systemctl start redis

# Check status
sudo systemctl status health-data-exchange
sudo systemctl status nginx
sudo systemctl status redis
```

## 🔧 Monitoring & Maintenance

### 1. Log Management

```bash
# Create log directory
sudo mkdir -p /var/log/health-data-exchange
sudo chown www-data:www-data /var/log/health-data-exchange

# Configure log rotation
sudo nano /etc/logrotate.d/health-data-exchange

/var/log/health-data-exchange/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload health-data-exchange
    endscript
}
```

### 2. Database Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-health-db.sh

#!/bin/bash
BACKUP_DIR="/var/backups/health-data-exchange"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="health_data_exchange"

mkdir -p $BACKUP_DIR
pg_dump $DB_NAME > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Set up cron job
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-health-db.sh
```

### 3. Performance Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor application logs
sudo journalctl -u health-data-exchange -f

# Monitor nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🚨 Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Database Security

```bash
# Secure PostgreSQL
sudo nano /etc/postgresql/*/main/postgresql.conf

# Add/modify:
listen_addresses = 'localhost'
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB

sudo nano /etc/postgresql/*/main/pg_hba.conf

# Ensure only local connections:
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

### 3. Application Security

```bash
# Set proper file permissions
sudo chown -R www-data:www-data /var/www/health-data-exchange
sudo chmod -R 755 /var/www/health-data-exchange
sudo chmod 600 /var/www/health-data-exchange/.env

# Create upload directory with proper permissions
sudo mkdir -p /var/www/health-data-exchange/uploads
sudo chown www-data:www-data /var/www/health-data-exchange/uploads
sudo chmod 755 /var/www/health-data-exchange/uploads
```

## 📊 Health Checks

### 1. Application Health

```bash
# Test API endpoints
curl -k https://yourdomain.com/health
curl -k https://yourdomain.com/api/

# Test database connection
sudo -u www-data python3 -c "
from backend.models import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection: OK')
"
```

### 2. Performance Monitoring

```bash
# Monitor system resources
htop
iotop
nethogs

# Check application logs
sudo journalctl -u health-data-exchange --since "1 hour ago"
```

## 🔄 Updates & Maintenance

### 1. Application Updates

```bash
# Update application
cd /var/www/health-data-exchange
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt
npm install
npm run build

# Restart services
sudo systemctl restart health-data-exchange
sudo systemctl restart nginx
```

### 2. Database Migrations

```bash
# Run database migrations
cd /var/www/health-data-exchange
source venv/bin/activate
python -c "
from backend.models import Base, engine
Base.metadata.create_all(bind=engine)
print('Database migrations completed')
"
```

## 🆘 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   sudo journalctl -u health-data-exchange -n 50
   sudo systemctl status health-data-exchange
   ```

2. **Database connection issues**
   ```bash
   sudo -u postgres psql -c "\l"
   sudo -u postgres psql -d health_data_exchange -c "SELECT 1;"
   ```

3. **Nginx configuration errors**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

4. **SSL certificate issues**
   ```bash
   sudo certbot certificates
   sudo certbot renew --dry-run
   ```

## 📞 Support

For deployment issues:
1. Check application logs: `sudo journalctl -u health-data-exchange`
2. Check nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify configuration files
4. Test individual components
5. Contact development team

---

**Last Updated**: December 2024
**Version**: 1.0.0
