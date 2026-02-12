# Panduan Migrasi Lengkap - Local Docker ke VPS Hostinger

**Versi:** 1.0  
**Terakhir Diupdate:** 2025-02-13  
**Target:** Migrasi dari Docker lokal ke VPS Hostinger  
**Cakupan:** Frontend, Backend, dan Database

---

## 📋 Daftar Isi

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Migrasi Frontend & Backend (Docker Images)](#migrasi-frontend--backend-docker-images)
4. [Migrasi Database](#migrasi-database)
5. [Verifikasi & Testing](#verifikasi--testing)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Panduan ini menjelaskan langkah-langkah lengkap untuk memigrasikan aplikasi Bagana AI dari environment Docker lokal ke VPS Hostinger, termasuk:

- ✅ **Frontend** (Next.js) - Docker image
- ✅ **Backend** (FastAPI) - Docker image  
- ✅ **Database** (PostgreSQL) - Data dump & restore

### Metode Migrasi

Terdapat dua metode migrasi:

1. **Metode Package (Recommended)** - Build images di local, package, transfer ke VPS
2. **Metode Git Clone** - Clone repository di VPS dan build langsung di VPS

Panduan ini fokus pada **Metode Package** karena lebih efisien untuk bandwidth dan waktu.

---

## ✅ Prerequisites

### Di Local Machine

- ✅ Docker & Docker Compose terinstall
- ✅ Aplikasi berjalan dengan baik di local
- ✅ Akses SSH ke VPS Hostinger
- ✅ Database lokal memiliki data yang ingin dimigrasikan

### Di VPS Hostinger

- ✅ VPS dengan Ubuntu 22.04+ atau Debian 11+
- ✅ Docker & Docker Compose sudah terinstall (jalankan `setup.sh` jika belum)
- ✅ Akses SSH dengan root atau sudo privileges
- ✅ Minimal 10GB free space untuk images dan database

---

## 🐳 Migrasi Frontend & Backend (Docker Images)

### Langkah 1: Build & Package Docker Images di Local

```bash
# Masuk ke direktori production
cd production

# Pastikan script executable
chmod +x package-docker.sh

# Jalankan script untuk build dan package images
./package-docker.sh
```

Script ini akan:
- Build Docker images untuk backend dan frontend
- Pull images yang diperlukan (PostgreSQL, Nginx)
- Save semua images ke file `.tar`
- Compress menjadi `.tar.gz`
- Menyimpan di folder `packages/`

**Output:** `packages/bagana-ai-docker-images-YYYYMMDD_HHMMSS.tar.gz`

### Langkah 2: Transfer Package ke VPS

**Opsi A: Menggunakan Transfer Script (Recommended)**

```bash
# Pastikan script executable
chmod +x transfer-package.sh

# Transfer package ke VPS
./transfer-package.sh root@YOUR_VPS_IP
```

Script ini akan:
- Mencari package terbaru secara otomatis
- Test koneksi SSH ke VPS
- Transfer file dengan progress indicator
- Verify file setelah transfer

**Opsi B: Manual dengan SCP**

```bash
# Transfer manual
scp packages/bagana-ai-docker-images-*.tar.gz root@YOUR_VPS_IP:/tmp/bagana-ai-packages/
```

### Langkah 3: Load Images di VPS

```bash
# SSH ke VPS
ssh root@YOUR_VPS_IP

# Masuk ke direktori production
cd /var/www/bagana-ai/production

# Pastikan script executable
chmod +x load-docker.sh

# Load images dari package
./load-docker.sh /tmp/bagana-ai-packages/bagana-ai-docker-images-*.tar.gz
```

Script ini akan:
- Extract package file
- Load semua Docker images
- Verify images yang ter-load
- Menampilkan next steps

**Verifikasi Images:**

```bash
# Check images yang sudah di-load
docker images | grep -E "bagana-ai|postgres|nginx"
```

---

## 🗄️ Migrasi Database

### Langkah 1: Backup Database di Local

**Opsi A: Menggunakan Script (Recommended)**

```bash
# Pastikan script executable
chmod +x migrate-database.sh

# Backup database lokal
./migrate-database.sh backup
```

**Opsi B: Manual Backup**

```bash
# Backup database dari container lokal
docker-compose exec postgres pg_dump -U bagana_user bagana_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# Atau jika menggunakan docker-compose di production folder
cd production
docker-compose exec postgres pg_dump -U bagana_user bagana_ai > ../backup_$(date +%Y%m%d_%H%M%S).sql
```

**Verifikasi Backup:**

```bash
# Check file size
ls -lh backup_*.sql

# Check file content (first few lines)
head -n 20 backup_*.sql
```

### Langkah 2: Transfer Database Backup ke VPS

**Opsi A: Menggunakan Script**

```bash
# Transfer backup ke VPS
./migrate-database.sh transfer root@YOUR_VPS_IP backup_YYYYMMDD_HHMMSS.sql
```

**Opsi B: Manual dengan SCP**

```bash
# Transfer manual
scp backup_*.sql root@YOUR_VPS_IP:/tmp/bagana-ai-database/
```

### Langkah 3: Restore Database di VPS

**PENTING:** Pastikan VPS sudah memiliki:
- ✅ Docker containers sudah running (minimal PostgreSQL)
- ✅ Database sudah diinisialisasi dengan struktur tabel

**Opsi A: Menggunakan Script**

```bash
# SSH ke VPS
ssh root@YOUR_VPS_IP

# Masuk ke direktori production
cd /var/www/bagana-ai/production

# Restore database
./migrate-database.sh restore /tmp/bagana-ai-database/backup_*.sql
```

**Opsi B: Manual Restore**

```bash
# SSH ke VPS
ssh root@YOUR_VPS_IP

# Masuk ke direktori production
cd /var/www/bagana-ai/production

# Pastikan PostgreSQL container running
docker-compose ps postgres

# Restore database
docker-compose exec -T postgres psql -U bagana_user -d bagana_ai < /tmp/bagana-ai-database/backup_YYYYMMDD_HHMMSS.sql

# Atau jika file sudah di local VPS
cat backup_*.sql | docker-compose exec -T postgres psql -U bagana_user -d bagana_ai
```

**Verifikasi Restore:**

```bash
# Check jumlah records
docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "SELECT COUNT(*) FROM users;"
docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "SELECT COUNT(*) FROM content_plans;"
docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "SELECT COUNT(*) FROM chat_history;"

# List semua tabel
docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "\dt"
```

---

## 🔧 Konfigurasi Environment di VPS

Setelah migrasi images dan database, pastikan konfigurasi environment sudah benar:

```bash
# SSH ke VPS
ssh root@YOUR_VPS_IP

# Masuk ke direktori production
cd /var/www/bagana-ai/production

# Copy template environment
cp env.example .env

# Edit environment variables
nano .env
```

**Pastikan konfigurasi berikut:**

```env
# Database (harus sama dengan yang digunakan saat backup)
DB_NAME=bagana_ai
DB_USER=bagana_user
DB_PASSWORD=your_secure_password_here
DB_PORT=5432

# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key

# URLs (ganti dengan IP VPS atau domain)
NEXT_PUBLIC_API_URL=http://YOUR_VPS_IP:8000/api
NEXTAUTH_URL=http://YOUR_VPS_IP:3000

# Generate secret: openssl rand -base64 32
NEXTAUTH_SECRET=paste_generated_secret_here

# CORS
CORS_ORIGINS=http://YOUR_VPS_IP:3000
```

---

## 🚀 Deploy di VPS

Setelah semua komponen sudah dimigrasikan:

```bash
# Pastikan di direktori production
cd /var/www/bagana-ai/production

# Pastikan script executable
chmod +x deploy.sh

# Deploy aplikasi
sudo ./deploy.sh
```

Script ini akan:
- Stop containers yang berjalan
- Build images (akan menggunakan images yang sudah di-load)
- Start semua services
- Initialize database (jika belum)
- Wait for services to be healthy

**Catatan:** Jika images sudah di-load sebelumnya, deploy.sh akan menggunakan images yang sudah ada tanpa rebuild.

---

## ✅ Verifikasi & Testing

### 1. Check Container Status

```bash
docker-compose ps
```

Semua container harus dalam status `Up` dan `healthy`.

### 2. Check Logs

```bash
# Semua services
docker-compose logs -f

# Service tertentu
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f postgres
```

### 3. Test Endpoints

```bash
# Health check backend
curl http://localhost:8000/health

# Health check frontend
curl http://localhost:3000

# Test database connection
docker-compose exec postgres pg_isready -U bagana_user
```

### 4. Verify Data Migration

```bash
# Check users
docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "SELECT id, email, username, role FROM users LIMIT 5;"

# Check content plans
docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "SELECT COUNT(*) as total_plans FROM content_plans;"

# Check chat history
docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "SELECT COUNT(*) as total_chats FROM chat_history;"
```

### 5. Test Aplikasi dari Browser

- Buka `http://YOUR_VPS_IP:3000`
- Login dengan credentials yang ada di database
- Test fitur-fitur utama aplikasi

---

## 🔧 Troubleshooting

### Database Restore Error: "relation already exists"

Jika tabel sudah ada, gunakan `--clean` flag:

```bash
# Drop semua objects sebelum restore
docker-compose exec -T postgres psql -U bagana_user -d bagana_ai -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Restore lagi
cat backup_*.sql | docker-compose exec -T postgres psql -U bagana_user -d bagana_ai
```

### Database Restore Error: "permission denied"

Pastikan menggunakan user yang benar:

```bash
# Check database user
docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "\du"

# Restore dengan user yang tepat
docker-compose exec -T postgres psql -U bagana_user -d bagana_ai < backup.sql
```

### Images Tidak Ter-load

```bash
# Check images
docker images | grep bagana-ai

# Load manual
gunzip bagana-ai-docker-images-*.tar.gz
docker load -i bagana-ai-docker-images-*.tar
```

### Container Tidak Start Setelah Migrasi

```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose up -d --build --force-recreate

# Check environment variables
docker-compose config
```

### Database Connection Error

```bash
# Check database status
docker-compose exec postgres pg_isready -U bagana_user

# Check environment variables
docker-compose exec backend env | grep DB

# Restart database
docker-compose restart postgres
```

### Data Tidak Muncul Setelah Restore

1. Verify backup file:
   ```bash
   head -n 50 backup_*.sql
   ```

2. Check database connection:
   ```bash
   docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "SELECT COUNT(*) FROM users;"
   ```

3. Check application logs:
   ```bash
   docker-compose logs backend | grep -i error
   ```

---

## 📝 Checklist Migrasi

Gunakan checklist ini untuk memastikan semua langkah sudah dilakukan:

### Pre-Migration
- [ ] Backup database lokal
- [ ] Verify backup file integrity
- [ ] Build Docker images di local
- [ ] Package Docker images
- [ ] Verify package file

### Migration
- [ ] Transfer Docker images package ke VPS
- [ ] Load Docker images di VPS
- [ ] Transfer database backup ke VPS
- [ ] Setup environment variables di VPS
- [ ] Initialize database di VPS (jika pertama kali)
- [ ] Restore database backup di VPS

### Post-Migration
- [ ] Deploy aplikasi di VPS
- [ ] Verify container status
- [ ] Test endpoints
- [ ] Verify data migration
- [ ] Test aplikasi dari browser
- [ ] Setup SSL (opsional)
- [ ] Configure domain (opsional)

---

## 🔐 Security Notes

1. **Jangan commit** file backup database ke repository
2. **Hapus backup files** setelah migrasi selesai (atau simpan di tempat aman)
3. **Gunakan password yang kuat** untuk database di production
4. **Limit SSH access** dengan key-based authentication
5. **Setup firewall** di VPS
6. **Enable SSL** untuk production

---

## 📞 Support

Jika mengalami masalah selama migrasi:

1. Check logs: `docker-compose logs`
2. Review troubleshooting section di atas
3. Verify semua prerequisites sudah terpenuhi
4. Check GitHub Issues
5. Hubungi tim support

---

**Selamat! Migrasi dari Local Docker ke VPS Hostinger sudah selesai! 🎉**
