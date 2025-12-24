# Deployment Guide

## Production Deployment

### Backend Deployment

#### Option 1: Docker (Recommended)

```bash
cd backend
docker-compose up -d
```

#### Option 2: Gunicorn

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URI=postgresql://user:password@localhost/dbname
export SECRET_KEY=your-secret-key
export JWT_SECRET_KEY=your-jwt-secret-key

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 src.app:app
```

#### Option 3: Systemd Service

Create `/etc/systemd/system/stock-backend.service`:

```ini
[Unit]
Description=Stock Backend Service
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/stock/backend
Environment="PATH=/opt/stock/venv/bin"
ExecStart=/opt/stock/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 src.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Frontend Deployment

#### Option 1: Vercel

```bash
npm install -g vercel
vercel
```

#### Option 2: Netlify

```bash
npm run build
# Upload build/ folder to Netlify
```

#### Option 3: Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/stock-frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Setup (PostgreSQL)

```bash
# Create database
createdb stock_db

# Set environment variable
export DATABASE_URI=postgresql://user:password@localhost/stock_db

# Run migrations
flask db upgrade
```

### Environment Variables

Create `.env` file:

```env
# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False

# Database
DATABASE_URI=postgresql://user:password@localhost/stock_db

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES_DAYS=1
JWT_COOKIE_SECURE=True
JWT_COOKIE_SAMESITE=None

# CORS
CORS_ORIGINS=https://your-frontend-domain.com

# Logging
LOG_LEVEL=INFO
```

### Mobile App Deployment

#### Android

```bash
cd mobile/StockerMobile
npm run android -- --variant=release
```

#### iOS

```bash
cd mobile/StockerMobile
npm run ios -- --configuration Release
```

## CI/CD

The project includes GitHub Actions workflows for:
- Automated testing
- Security audits
- Docker builds

See `.github/workflows/ci.yml` for details.

## Monitoring

### Health Checks

Backend health endpoint:
```
GET http://localhost:5000/
```

### Logging

Logs are structured JSON format. Configure log level via `LOG_LEVEL` environment variable.

### Database Backups

```bash
# Backup
pg_dump stock_db > backup_$(date +%Y%m%d).sql

# Restore
psql stock_db < backup_20240115.sql
```

