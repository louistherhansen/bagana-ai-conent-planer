# Test Docker Lokal - Panduan Lengkap

Panduan untuk test Docker deployment secara lokal sebelum deploy ke production.

---

## 📋 Prerequisites

1. **Docker Desktop** terinstall
   - Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - Mac: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - Linux: [Docker Engine](https://docs.docker.com/engine/install/)

2. **Docker Compose** terinstall (biasanya sudah included dengan Docker Desktop)

3. **Git** terinstall (untuk clone repository)

---

## 🚀 Quick Start

### Windows (PowerShell)

```powershell
# Run test script
.\scripts\test-docker-local.ps1

# Atau manual
docker-compose build
docker-compose up -d
```

### Linux/Mac (Bash)

```bash
# Make script executable
chmod +x scripts/test-docker-local.sh

# Run test script
./scripts/test-docker-local.sh

# Atau manual
docker-compose build
docker-compose up -d
```

---

## 📝 Step-by-Step Manual Testing

### Step 1: Setup Environment

```bash
# Copy example env file
cp .env.production.example .env

# Edit .env dengan nilai lokal
nano .env  # atau gunakan editor favorit Anda
```

**Minimal configuration untuk local testing:**

```env
# Database
DB_PASSWORD=local_test_password_123
DB_NAME=bagana_ai
DB_USER=bagana_user

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=local_test_secret_change_in_production

# Backend
OPENROUTER_API_KEY=your_openrouter_key_here

# Security
BCRYPT_SALT_ROUNDS=10  # Lower untuk testing (faster)
NODE_ENV=development   # Atau production untuk test production mode
```

### Step 2: Build Docker Images

```bash
# Build semua images
docker-compose build

# Build dengan no-cache (untuk fresh build)
docker-compose build --no-cache

# Build specific service
docker-compose build frontend
docker-compose build backend
```

**Expected output:**
- Frontend image built successfully
- Backend image built successfully
- PostgreSQL akan menggunakan official image (tidak perlu build)

### Step 3: Start Services

```bash
# Start semua services di background
docker-compose up -d

# Start dengan melihat logs
docker-compose up

# Start specific service
docker-compose up -d postgres
docker-compose up -d backend
docker-compose up -d frontend
```

**Expected output:**
```
Creating network "bagana-ai-conent-planer_bagana-network" ... done
Creating volume "bagana-ai-conent-planer_postgres_data" ... done
Creating bagana-ai-db ... done
Creating bagana-ai-backend ... done
Creating bagana-ai-frontend ... done
```

### Step 4: Check Service Status

```bash
# Check status semua services
docker-compose ps

# Expected output:
# NAME                  STATUS          PORTS
# bagana-ai-backend     Up (healthy)    0.0.0.0:8000->8000/tcp
# bagana-ai-db          Up (healthy)    0.0.0.0:5432->5432/tcp
# bagana-ai-frontend    Up (healthy)    0.0.0.0:3000->3000/tcp
```

### Step 5: Check Service Health

```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U bagana_user

# Check Backend API
curl http://localhost:8000/health
# atau
curl http://localhost:8000/docs  # FastAPI docs

# Check Frontend
curl http://localhost:3000
# atau buka browser: http://localhost:3000
```

### Step 6: Initialize Database

```bash
# Initialize auth tables
docker-compose exec backend python scripts/init-auth-db.py

# Initialize chat history tables
docker-compose exec backend python scripts/init-chat-history-db.py

# Initialize content plans tables
docker-compose exec backend python scripts/init-content-plans-db.py
```

### Step 7: Test Application

1. **Frontend:**
   - Buka browser: http://localhost:3000
   - Test login/register
   - Test semua fitur aplikasi

2. **Backend API:**
   - Buka: http://localhost:8000/docs
   - Test API endpoints melalui Swagger UI

3. **Database:**
   ```bash
   # Access PostgreSQL
   docker-compose exec postgres psql -U bagana_user -d bagana_ai
   
   # Check tables
   \dt
   
   # Check users
   SELECT email, username, role FROM users;
   ```

---

## 🔍 View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 frontend

# Since specific time
docker-compose logs --since 10m frontend
```

---

## 🐛 Troubleshooting

### Issue 1: Port Already in Use

**Error:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Check what's using the port
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Linux/Mac
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Stop the service using the port, atau change port di .env
FRONTEND_PORT=3001
BACKEND_PORT=8001
DB_PORT=5433
```

### Issue 2: Database Connection Failed

**Error:**
```
Error: connect ECONNREFUSED
```

**Solution:**
```bash
# Check if database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Wait for database to be ready
docker-compose exec postgres pg_isready -U bagana_user

# Check environment variables
docker-compose exec backend env | grep DB_
```

### Issue 3: Frontend Build Failed

**Error:**
```
Error: Cannot find module
```

**Solution:**
```bash
# Rebuild dengan no-cache
docker-compose build --no-cache frontend

# Check package.json
docker-compose exec frontend cat package.json

# Check node_modules
docker-compose exec frontend ls -la node_modules
```

### Issue 4: Backend Import Error

**Error:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
```bash
# Rebuild backend
docker-compose build --no-cache backend

# Check Python packages
docker-compose exec backend pip list

# Install missing package
docker-compose exec backend pip install package-name
```

### Issue 5: Permission Denied

**Error:**
```
Permission denied
```

**Solution:**
```bash
# Check file permissions
docker-compose exec backend ls -la /app

# Fix permissions (if needed)
docker-compose exec backend chown -R appuser:appuser /app
```

---

## 🧹 Cleanup

```bash
# Stop semua services
docker-compose stop

# Stop dan remove containers
docker-compose down

# Stop, remove containers, dan volumes (⚠️ Hapus data!)
docker-compose down -v

# Remove images juga
docker-compose down --rmi all -v

# Clean Docker system (remove unused resources)
docker system prune -a
```

---

## ✅ Testing Checklist

- [ ] Docker dan Docker Compose terinstall
- [ ] File `.env` dikonfigurasi dengan benar
- [ ] Images berhasil di-build
- [ ] Semua services berhasil start
- [ ] Health checks pass untuk semua services
- [ ] Database bisa diakses
- [ ] Frontend bisa diakses di browser
- [ ] Backend API bisa diakses
- [ ] Database tables berhasil di-initialize
- [ ] Login/Register berfungsi
- [ ] Semua fitur aplikasi berfungsi

---

## 📊 Performance Testing

```bash
# Check resource usage
docker stats

# Check specific container
docker stats bagana-ai-frontend
docker stats bagana-ai-backend
docker stats bagana-ai-db

# Check disk usage
docker system df

# Check container logs size
docker-compose exec frontend du -sh /app
```

---

## 🔄 Update & Rebuild

```bash
# Pull latest code
git pull

# Rebuild dan restart
docker-compose build --no-cache
docker-compose up -d

# Restart specific service
docker-compose restart frontend
docker-compose restart backend
```

---

## 📝 Notes

- **Development mode:** Set `NODE_ENV=development` di `.env` untuk faster rebuilds
- **Production mode:** Set `NODE_ENV=production` untuk test production build
- **Database data:** Data akan persist di Docker volume `postgres_data`
- **Hot reload:** Tidak tersedia di Docker, perlu rebuild untuk changes

---

## 🆘 Need Help?

Jika mengalami masalah:
1. Check logs: `docker-compose logs -f`
2. Check service status: `docker-compose ps`
3. Check Docker resources: `docker system df`
4. Review documentation di `DOCKER_DEPLOYMENT.md`

---

**Happy Testing! 🚀**
