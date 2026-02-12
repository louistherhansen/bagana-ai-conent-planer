# Bagana AI - Deployment Guide untuk Hostinger VPS

**Versi:** 2.0  
**Terakhir Diupdate:** 2025-02-13  
**Target:** Hostinger VPS (Ubuntu/Debian)  
**Metode:** Docker Compose

---

## 📋 Daftar Isi

1. [Persiapan](#persiapan)
2. [Setup Server](#setup-server)
3. [Deployment](#deployment)
4. [Konfigurasi SSL](#konfigurasi-ssl)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Persiapan

### Requirements

- **VPS Hostinger** dengan spesifikasi minimal:
  - CPU: 2 vCPU
  - RAM: 4GB
  - Storage: 40GB SSD
  - OS: Ubuntu 22.04 LTS atau Debian 11+
  
- **Akses SSH** ke VPS dengan root atau sudo privileges
- **Domain name** (opsional, untuk SSL)
- **API Keys:**
  - OpenRouter API Key
  - Database credentials

### Informasi Server

Setelah deployment, aplikasi akan accessible di:
- Frontend: `http://YOUR_VPS_IP:3000` atau `https://yourdomain.com`
- Backend API: `http://YOUR_VPS_IP:8000` atau `https://yourdomain.com/api`
- Database: `localhost:5432` (internal Docker network)

---

## 🚀 Setup Server

### 1. Koneksi ke VPS

```bash
ssh root@YOUR_VPS_IP
```

### 2. Jalankan Setup Script

```bash
# Download atau copy setup.sh ke server
chmod +x setup.sh
sudo ./setup.sh
```

Script ini akan:
- Update sistem
- Install Docker & Docker Compose
- Install Nginx (opsional)
- Setup firewall
- Buat direktori aplikasi

### 3. Clone Repository

```bash
cd /var/www
git clone https://github.com/YOUR_USERNAME/bagana-ai-content-planner.git bagana-ai
cd bagana-ai
```

---

## 📦 Deployment

### 1. Konfigurasi Environment Variables

```bash
cd production
cp env.example .env
nano .env
```

Edit file `.env` dengan informasi yang sesuai:

```env
# Database
DB_NAME=bagana_ai
DB_USER=bagana_user
DB_PASSWORD=your_secure_password_here
DB_PORT=5432

# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Application URLs
NEXT_PUBLIC_API_URL=http://YOUR_VPS_IP:8000/api
NEXTAUTH_URL=http://YOUR_VPS_IP:3000
NEXTAUTH_SECRET=generate_random_secret_here

# Ports
FRONTEND_PORT=3000
BACKEND_PORT=8000
DB_PORT=5432

# CORS
CORS_ORIGINS=http://YOUR_VPS_IP:3000,https://yourdomain.com

# Security
BCRYPT_SALT_ROUNDS=12
```

**Generate NEXTAUTH_SECRET:**
```bash
openssl rand -base64 32
```

### 2. Jalankan Deployment Script

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

Script ini akan:
- Build Docker images
- Start semua services
- Initialize database
- Setup Nginx reverse proxy (jika diperlukan)

### 3. Verifikasi Deployment

```bash
# Check status containers
docker-compose ps

# Check logs
docker-compose logs -f

# Test endpoints
curl http://localhost:3000
curl http://localhost:8000/health
```

---

## 🔒 Konfigurasi SSL (Opsional)

### Menggunakan Certbot (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx -y

# Generate SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Update Nginx Configuration

File `nginx.conf` sudah dikonfigurasi untuk mendukung SSL. Pastikan:
- Certificate paths sudah benar
- Port 443 sudah dibuka di firewall
- Domain DNS sudah mengarah ke VPS IP

---

## 📊 Monitoring & Maintenance

### Check Logs

```bash
# Semua services
docker-compose logs -f

# Service tertentu
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Restart Services

```bash
# Restart semua
docker-compose restart

# Restart service tertentu
docker-compose restart frontend
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild dan restart
docker-compose up -d --build
```

### Backup Database

```bash
# Backup
docker-compose exec postgres pg_dump -U bagana_user bagana_ai > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U bagana_user bagana_ai < backup_YYYYMMDD.sql
```

### Check Resource Usage

```bash
# Docker stats
docker stats

# Disk usage
df -h
docker system df
```

---

## 🔧 Troubleshooting

### Container tidak start

```bash
# Check logs
docker-compose logs

# Check status
docker-compose ps

# Rebuild
docker-compose up -d --build --force-recreate
```

### Database connection error

```bash
# Check database status
docker-compose exec postgres pg_isready -U bagana_user

# Check environment variables
docker-compose exec backend env | grep DB

# Restart database
docker-compose restart postgres
```

### Port sudah digunakan

```bash
# Check port usage
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8000

# Kill process
sudo kill -9 PID
```

### Frontend tidak bisa connect ke backend

1. Check `NEXT_PUBLIC_API_URL` di `.env`
2. Check CORS settings di backend
3. Check firewall rules
4. Verify backend health: `curl http://localhost:8000/health`

### Permission denied errors

```bash
# Fix permissions
sudo chown -R $USER:$USER /var/www/bagana-ai
chmod +x deploy.sh setup.sh
```

---

## 📦 Migrasi dari Local Docker ke VPS

Untuk panduan lengkap migrasi aplikasi dari Docker lokal ke VPS Hostinger (termasuk frontend, backend, dan database), lihat **[MIGRATION.md](./MIGRATION.md)**.

### Package Docker Images untuk Transfer

Jika Anda ingin membuat package Docker images untuk ditransfer ke VPS (berguna jika VPS memiliki bandwidth terbatas atau ingin build di local):

### 1. Buat Package di Local Machine

```bash
cd production
chmod +x package-docker.sh
./package-docker.sh
```

Script ini akan:
- Build Docker images (backend & frontend)
- Save semua images ke file `.tar`
- Compress menjadi `.tar.gz`
- Menyimpan di folder `packages/`

### 2. Transfer Package ke VPS

**Opsi A: Menggunakan transfer script**
```bash
chmod +x transfer-package.sh
./transfer-package.sh root@YOUR_VPS_IP
```

**Opsi B: Manual dengan SCP**
```bash
scp packages/bagana-ai-docker-images-*.tar.gz root@YOUR_VPS_IP:/tmp/
```

### 3. Load Images di VPS

```bash
# SSH ke VPS
ssh root@YOUR_VPS_IP

# Load images
cd /var/www/bagana-ai/production
chmod +x load-docker.sh
./load-docker.sh /tmp/bagana-ai-docker-images-*.tar.gz

# Atau manual
gunzip /tmp/bagana-ai-docker-images-*.tar.gz
docker load -i /tmp/bagana-ai-docker-images-*.tar
```

### 4. Deploy Setelah Load Images

```bash
cd /var/www/bagana-ai/production
./deploy.sh
```

**Catatan:** Setelah images di-load, `deploy.sh` akan langsung menggunakan images yang sudah ada tanpa rebuild.

---

## 📝 File Structure

```
production/
├── README.md              # Dokumentasi ini
├── QUICK-START.md         # Panduan cepat
├── docker-compose.yml     # Docker Compose configuration
├── deploy.sh             # Deployment script
├── setup.sh              # Server setup script
├── package-docker.sh     # Script untuk membuat package Docker images
├── load-docker.sh        # Script untuk load images di VPS
├── transfer-package.sh   # Script untuk transfer package ke VPS
├── init-database.sql     # Database initialization
├── nginx.conf            # Nginx configuration
├── env.example           # Environment variables template
└── packages/             # Folder untuk menyimpan package files (auto-created)
```

---

## 🔐 Security Best Practices

1. **Gunakan password yang kuat** untuk database
2. **Jangan commit** file `.env` ke repository
3. **Update sistem** secara berkala: `sudo apt update && sudo apt upgrade`
4. **Setup firewall** dengan UFW atau iptables
5. **Gunakan SSL** untuk production
6. **Limit SSH access** dengan key-based authentication
7. **Monitor logs** secara berkala untuk aktivitas mencurigakan

---

## 📞 Support

Jika mengalami masalah:
1. Check logs: `docker-compose logs`
2. Review dokumentasi troubleshooting di atas
3. Check GitHub Issues
4. Hubungi tim support

---

**Selamat! Aplikasi Bagana AI sudah berjalan di Hostinger VPS Anda! 🎉**
