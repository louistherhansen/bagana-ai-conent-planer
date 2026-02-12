# Docker Deployment Guide - BAGANA AI

Panduan lengkap untuk deploy aplikasi BAGANA AI menggunakan Docker di VPS Production.

---

## 📋 Prerequisites

- VPS dengan Ubuntu 20.04+ atau Debian 11+
- Docker Engine 20.10+
- Docker Compose 2.0+
- Domain name (optional, untuk production)
- SSL Certificate (optional, untuk HTTPS)

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd bagana-ai-conent-planer
```

### 2. Setup Environment Variables

```bash
# Copy example file
cp .env.production.example .env

# Edit .env file dengan nilai production Anda
nano .env
```

**PENTING:** Pastikan semua nilai diisi dengan benar, terutama:
- `DB_PASSWORD` - Password database yang kuat
- `NEXTAUTH_SECRET` - Random string untuk NextAuth (generate dengan: `openssl rand -base64 32`)
- `OPENROUTER_API_KEY` - API key untuk OpenRouter
- `NEXT_PUBLIC_API_URL` - URL API backend (misal: `https://api.yourdomain.com`)
- `NEXTAUTH_URL` - URL frontend (misal: `https://yourdomain.com`)

### 3. Build dan Start Services

```bash
# Build semua images
docker-compose build

# Start semua services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Run database initialization scripts
docker-compose exec postgres psql -U bagana_user -d bagana_ai -f /docker-entrypoint-initdb.d/init.sql

# Atau run Python scripts untuk init tables
docker-compose exec backend python scripts/init-auth-db.py
docker-compose exec backend python scripts/init-chat-history-db.py
docker-compose exec backend python scripts/init-content-plans-db.py
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Nginx (80/443) │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Frontend│ │Backend│
│:3000  │ │:8000  │
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         │
    ┌────▼────┐
    │PostgreSQL│
    │  :5432  │
    └─────────┘
```

---

## 📦 Services

### 1. PostgreSQL Database

- **Image:** `postgres:14-alpine`
- **Port:** 5432 (internal), bisa di-expose jika perlu
- **Volume:** `postgres_data` (persistent storage)
- **Health Check:** Automatic dengan `pg_isready`

**Configuration:**
- Max connections: 200
- Shared buffers: 256MB
- Effective cache size: 1GB
- Optimized untuk production workload

### 2. FastAPI Backend

- **Image:** Custom build dari `Dockerfile.backend`
- **Port:** 8000
- **Workers:** 2 (Gunicorn + Uvicorn)
- **Health Check:** `/health` endpoint

**Features:**
- Multi-stage build untuk optimasi size
- Non-root user untuk security
- Auto-restart on failure
- Volume untuk storage persistence

### 3. Next.js Frontend

- **Image:** Custom build dari `Dockerfile.frontend`
- **Port:** 3000
- **Build:** Standalone output untuk optimasi
- **Health Check:** `/api/health` endpoint

**Features:**
- Multi-stage build (deps → builder → runner)
- Standalone output untuk size optimization
- Non-root user untuk security
- Production optimizations enabled

### 4. Nginx Reverse Proxy (Optional)

- **Image:** `nginx:alpine`
- **Ports:** 80 (HTTP), 443 (HTTPS)
- **Profile:** `with-nginx` (optional)

**Usage:**
```bash
# Start dengan Nginx
docker-compose --profile with-nginx up -d
```

---

## 🔧 Configuration

### Environment Variables

Semua environment variables dikonfigurasi melalui file `.env`. Lihat `.env.production.example` untuk daftar lengkap.

**Critical Variables:**
- `DB_PASSWORD` - **REQUIRED** - Password database
- `NEXTAUTH_SECRET` - **REQUIRED** - Secret untuk NextAuth
- `OPENROUTER_API_KEY` - **REQUIRED** - API key untuk CrewAI

### Ports Configuration

Default ports bisa diubah di `.env`:
- `FRONTEND_PORT` - Port untuk frontend (default: 3000)
- `BACKEND_PORT` - Port untuk backend (default: 8000)
- `DB_PORT` - Port untuk database (default: 5432)

---

## 🛠️ Management Commands

### Start Services

```bash
# Start semua services
docker-compose up -d

# Start dengan Nginx
docker-compose --profile with-nginx up -d

# Start specific service
docker-compose up -d postgres
docker-compose up -d backend
docker-compose up -d frontend
```

### Stop Services

```bash
# Stop semua services
docker-compose stop

# Stop specific service
docker-compose stop frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Restart Services

```bash
# Restart semua
docker-compose restart

# Restart specific
docker-compose restart frontend
```

### Rebuild Services

```bash
# Rebuild semua
docker-compose build --no-cache

# Rebuild specific
docker-compose build --no-cache frontend
```

### Database Management

```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U bagana_user -d bagana_ai

# Backup database
docker-compose exec postgres pg_dump -U bagana_user bagana_ai > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T postgres psql -U bagana_user bagana_ai < backup_20250212.sql
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

- ✅ Jangan commit `.env` file ke Git
- ✅ Gunakan password yang kuat untuk `DB_PASSWORD`
- ✅ Generate random `NEXTAUTH_SECRET`
- ✅ Rotate secrets secara berkala

### 2. Database Security

- ✅ Database hanya accessible dari internal network
- ✅ Gunakan SSL untuk production (`DB_SSL=true`)
- ✅ Regular backups
- ✅ Monitor connection logs

### 3. Container Security

- ✅ Non-root users di semua containers
- ✅ Minimal base images (alpine)
- ✅ Regular security updates
- ✅ Health checks enabled

### 4. Network Security

- ✅ Use Docker networks untuk isolation
- ✅ Expose hanya ports yang diperlukan
- ✅ Use reverse proxy (Nginx) untuk HTTPS
- ✅ Firewall rules di VPS

---

## 📊 Monitoring

### Health Checks

Semua services memiliki health checks:
- **PostgreSQL:** `pg_isready` check setiap 10s
- **Backend:** `/health` endpoint setiap 30s
- **Frontend:** `/api/health` endpoint setiap 30s

### Check Status

```bash
# Service status
docker-compose ps

# Health check status
docker inspect bagana-ai-frontend | grep -A 10 Health
docker inspect bagana-ai-backend | grep -A 10 Health
docker inspect bagana-ai-db | grep -A 10 Health
```

### Logs Monitoring

```bash
# Real-time logs
docker-compose logs -f

# Logs dengan filter
docker-compose logs -f | grep ERROR
docker-compose logs -f frontend | grep -i error
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

### Database Migrations

```bash
# Run migration scripts
docker-compose exec backend python scripts/init-auth-db.py
docker-compose exec backend python scripts/init-content-plans-db.py
```

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
docker-compose exec -T postgres pg_dump -U bagana_user bagana_ai | gzip > backups/db_$DATE.sql.gz

# Keep last 7 days
find backups/ -name "*.sql.gz" -mtime +7 -delete
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs service-name

# Check environment variables
docker-compose config

# Verify Docker resources
docker system df
docker system prune  # Clean unused resources
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps postgres

# Test connection
docker-compose exec backend python -c "from lib.db import testConnection; print(testConnection())"

# Check database logs
docker-compose logs postgres
```

### Frontend Build Issues

```bash
# Check build logs
docker-compose build frontend --no-cache

# Verify Next.js config
cat next.config.mjs

# Check standalone output
docker-compose exec frontend ls -la /app
```

### Backend Issues

```bash
# Check Python dependencies
docker-compose exec backend pip list

# Test API endpoint
curl http://localhost:8000/health

# Check backend logs
docker-compose logs backend
```

---

## 📝 Production Checklist

- [ ] Environment variables di-set dengan benar
- [ ] Database password kuat dan aman
- [ ] SSL certificates dikonfigurasi (jika menggunakan HTTPS)
- [ ] Firewall rules dikonfigurasi di VPS
- [ ] Backup strategy di-setup
- [ ] Monitoring dan alerting dikonfigurasi
- [ ] Health checks berfungsi
- [ ] Logs rotation dikonfigurasi
- [ ] Security updates dijadwalkan
- [ ] Domain DNS dikonfigurasi
- [ ] Nginx reverse proxy dikonfigurasi (jika digunakan)

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)

---

## 🆘 Support

Jika mengalami masalah:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables: `docker-compose config`
3. Check service status: `docker-compose ps`
4. Review documentation di `docs/` folder

---

**Last Updated:** 2025-02-12  
**Version:** 1.0.0
