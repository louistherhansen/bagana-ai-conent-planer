# Quick Start Guide - Hostinger VPS Deployment

Panduan cepat untuk deploy Bagana AI ke Hostinger VPS dalam 5 langkah.

## Prerequisites

- VPS Hostinger dengan Ubuntu 22.04+ atau Debian 11+
- Akses SSH dengan root atau sudo privileges
- Domain name (opsional, untuk SSL)

## Langkah-langkah Deployment

### 1. Koneksi ke VPS

```bash
ssh root@YOUR_VPS_IP
```

### 2. Setup Server (Hanya pertama kali)

```bash
cd /var/www
git clone https://github.com/YOUR_USERNAME/bagana-ai-content-planner.git bagana-ai
cd bagana-ai/production
chmod +x setup.sh
sudo ./setup.sh
```

### 3. Konfigurasi Environment Variables

```bash
cd /var/www/bagana-ai/production
cp env.example .env
nano .env
```

**Edit file `.env` dengan informasi berikut:**

```env
# Database
DB_PASSWORD=your_secure_password_here

# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key

# URLs (ganti YOUR_VPS_IP dengan IP VPS Anda)
NEXT_PUBLIC_API_URL=http://YOUR_VPS_IP:8000/api
NEXTAUTH_URL=http://YOUR_VPS_IP:3000

# Generate secret: openssl rand -base64 32
NEXTAUTH_SECRET=paste_generated_secret_here

# CORS
CORS_ORIGINS=http://YOUR_VPS_IP:3000
```

### 4. Deploy Application

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### 5. Verifikasi

```bash
# Check status
docker-compose ps

# Check logs
docker-compose logs -f

# Test aplikasi
curl http://localhost:3000
curl http://localhost:8000/health
```

## Akses Aplikasi

Setelah deployment selesai, akses aplikasi di:

- **Frontend:** `http://YOUR_VPS_IP:3000`
- **Backend API:** `http://YOUR_VPS_IP:8000`
- **Health Check:** `http://YOUR_VPS_IP:8000/health`

## Troubleshooting

### Container tidak start

```bash
docker-compose logs
docker-compose up -d --build
```

### Port sudah digunakan

```bash
sudo netstat -tulpn | grep :3000
sudo kill -9 PID
```

### Database error

```bash
docker-compose restart postgres
docker-compose logs postgres
```

## Update Application

```bash
cd /var/www/bagana-ai
git pull origin main
cd production
sudo ./deploy.sh
```

## Backup Database

```bash
cd /var/www/bagana-ai/production
docker-compose exec postgres pg_dump -U bagana_user bagana_ai > backup_$(date +%Y%m%d).sql
```

## Migrasi dari Local Docker ke VPS Hostinger

Jika Anda ingin memigrasikan aplikasi dari Docker lokal ke VPS Hostinger (termasuk frontend, backend, dan database):

### Metode Lengkap (Recommended)

**1. Backup Database di Local**

```bash
cd production
chmod +x migrate-database.sh
./migrate-database.sh backup
```

**2. Build & Package Docker Images di Local**

```bash
chmod +x package-docker.sh
./package-docker.sh
```

**3. Transfer Docker Images ke VPS**

```bash
chmod +x transfer-package.sh
./transfer-package.sh root@YOUR_VPS_IP
```

**4. Transfer Database Backup ke VPS**

```bash
# Transfer backup terbaru
./migrate-database.sh transfer root@YOUR_VPS_IP

# Atau manual
scp backups/backup_*.sql root@YOUR_VPS_IP:/tmp/bagana-ai-database/
```

**5. Setup di VPS**

```bash
# SSH ke VPS
ssh root@YOUR_VPS_IP

# Setup server (jika pertama kali)
cd /var/www
git clone https://github.com/YOUR_USERNAME/bagana-ai-content-planner.git bagana-ai
cd bagana-ai/production
chmod +x setup.sh
sudo ./setup.sh

# Load Docker images
chmod +x load-docker.sh
./load-docker.sh /tmp/bagana-ai-packages/bagana-ai-docker-images-*.tar.gz

# Konfigurasi environment
cp env.example .env
nano .env  # Edit sesuai kebutuhan

# Restore database
chmod +x migrate-database.sh
./migrate-database.sh restore /tmp/bagana-ai-database/backup_*.sql

# Deploy aplikasi
chmod +x deploy.sh
sudo ./deploy.sh
```

### Alternatif: Deploy dengan Package Docker Images (Tanpa Database)

Jika Anda hanya ingin transfer Docker images tanpa database:

**1. Buat Package di Local**
```bash
cd production
chmod +x package-docker.sh
./package-docker.sh
```

**2. Transfer ke VPS**
```bash
chmod +x transfer-package.sh
./transfer-package.sh root@YOUR_VPS_IP
```

**3. Load di VPS**
```bash
ssh root@YOUR_VPS_IP
cd /var/www/bagana-ai/production
chmod +x load-docker.sh
./load-docker.sh /tmp/bagana-ai-packages/bagana-ai-docker-images-*.tar.gz
chmod +x deploy.sh
sudo ./deploy.sh
```

**Catatan:** Untuk panduan migrasi lengkap termasuk troubleshooting, lihat `MIGRATION.md`.

## Next Steps

1. Setup SSL dengan Let's Encrypt (lihat README.md)
2. Konfigurasi domain name
3. Setup monitoring dan alerts
4. Configure automated backups

## Dokumentasi Lengkap

- **README.md** - Dokumentasi deployment lengkap
- **MIGRATION.md** - Panduan migrasi lengkap dari local Docker ke VPS (termasuk database)
- **QUICK-START.md** - Panduan cepat ini
