# Docker Deployment - Quick Reference

## 🚀 Quick Start Commands

```bash
# 1. Setup environment
cp .env.production.example .env
nano .env  # Edit dengan nilai production Anda

# 2. Build dan start
docker-compose build
docker-compose up -d

# 3. Check status
docker-compose ps
docker-compose logs -f

# 4. Initialize database (first time only)
docker-compose exec backend python scripts/init-auth-db.py
```

## 📋 Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service-name]

# Rebuild after code changes
docker-compose build --no-cache [service-name]
docker-compose up -d [service-name]

# Database backup
docker-compose exec postgres pg_dump -U bagana_user bagana_ai > backup.sql

# Database restore
docker-compose exec -T postgres psql -U bagana_user bagana_ai < backup.sql
```

## 🔧 Services

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **Database:** localhost:5432
- **Nginx:** http://localhost:80 (optional)

## 📖 Full Documentation

Lihat `DOCKER_DEPLOYMENT.md` untuk panduan lengkap.
