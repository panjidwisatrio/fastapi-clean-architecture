# Production Deployment

Guide for deploying FastAPI Clean Architecture to production.

## Pre-Deployment Checklist

### Environment Configuration

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set strong `SECRET_KEY` (min 32 characters)
- [ ] Configure proper `DATABASE_URL`
- [ ] Set `ALLOWED_ORIGINS` for CORS
- [ ] Configure SMTP settings for emails

### Security

- [ ] Enable HTTPS/TLS
- [ ] Use environment variables (never commit secrets)
- [ ] Change default passwords
- [ ] Enable rate limiting
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerts

### Database

- [ ] Run all migrations: `alembic upgrade head`
- [ ] Configure database backups
- [ ] Set up connection pooling
- [ ] Enable query logging for errors

### Application

- [ ] Set workers based on CPU cores
- [ ] Configure logging (rotating file handler)
- [ ] Disable debug mode
- [ ] Set up health check endpoint
- [ ] Configure reverse proxy (Nginx)

## Deployment Steps

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
```

### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/yourusername/fastapi-clean-architecture.git
cd fastapi-clean-architecture

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file:

```env
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://user:password@localhost/dbname
ALLOWED_ORIGINS=https://your-domain.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. Database Setup

```bash
# Create database
sudo -u postgres createdb fastapi_db

# Run migrations
alembic upgrade head

# Verify tables created
psql -U postgres -d fastapi_db -c "\dt"
```

### 5. Run with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run application
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### 6. Set Up Systemd Service

Create `/etc/systemd/system/fastapi.service`:

```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/fastapi-clean-architecture
Environment="PATH=/path/to/fastapi-clean-architecture/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

### 7. Configure Nginx

Create `/etc/nginx/sites-available/fastapi`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Monitoring

### Health Check Endpoint

Add to `app/main.py`:

```python
@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

### Log Monitoring

```bash
# Application logs
tail -f logs/app.log

# Nginx access logs
tail -f /var/log/nginx/access.log

# System logs
journalctl -u fastapi -f
```

### Database Monitoring

```bash
# Check connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('fastapi_db'));"
```

## Backup Strategy

### Database Backups

Daily backup script:

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"
DB_NAME="fastapi_db"

mkdir -p $BACKUP_DIR
pg_dump $DB_NAME | gzip > $BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

Add to crontab:

```bash
0 2 * * * /path/to/backup.sh
```

## Performance Optimization

### Worker Configuration

```python
# Calculate workers
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
```

### Database Connection Pool

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Caching

Consider adding Redis for caching:

```bash
pip install redis
```

## Troubleshooting

### Application Won't Start

```bash
# Check logs
journalctl -u fastapi -n 50

# Verify environment
source venv/bin/activate
python -c "from app.main import app; print('OK')"

# Check database connection
python -c "from app.core.database import engine; print(engine.connect())"
```

### High Memory Usage

```bash
# Check memory
free -h

# Monitor process
top -p $(pgrep -f gunicorn)

# Reduce workers if needed
```

See [Docker Deployment](docker.md) for containerized deployment.
