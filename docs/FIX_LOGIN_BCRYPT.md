# Solusi Masalah Login - bcrypt tidak tersedia di Docker

## Masalah
Login di frontend gagal karena bcrypt tidak dapat digunakan di container Docker. Error yang muncul:
```
❌ bcrypt is NOT available: No native build was found for platform=linux arch=x64 runtime=node abi=108 uv=1 libc=musl node=18.20.8
```

## Penyebab
bcrypt adalah native module yang perlu dikompilasi untuk platform spesifik. Di Alpine Linux (yang menggunakan musl libc), bcrypt perlu di-rebuild setelah instalasi.

## Solusi

### Solusi 1: Rebuild Docker Image (Permanen - Direkomendasikan)

1. **Pastikan package-lock.json sudah terupdate:**
   ```bash
   npm install
   ```

2. **Rebuild image frontend:**
   ```bash
   docker-compose build frontend
   ```

3. **Restart container:**
   ```bash
   docker-compose up -d frontend
   ```

4. **Verifikasi bcrypt:**
   ```bash
   docker-compose exec frontend node -e "try { require('bcrypt'); console.log('✅ bcrypt is available'); } catch(e) { console.log('❌ bcrypt is NOT available:', e.message); }"
   ```

### Solusi 2: Fix di Container yang Berjalan (Temporary)

Jika Anda tidak bisa rebuild image sekarang, gunakan script berikut:

**Windows PowerShell:**
```powershell
.\scripts\fix-bcrypt-docker.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/fix-bcrypt-docker.sh
./scripts/fix-bcrypt-docker.sh
```

**Manual:**
```bash
docker-compose exec -u root frontend sh -c "apk add --no-cache python3 make g++ && cd /app && npm rebuild bcrypt --build-from-source"
```

## Perubahan yang Sudah Dilakukan

### Dockerfile.frontend
Ditambahkan rebuild bcrypt setelah instalasi dependencies:
```dockerfile
# Install production dependencies (including native modules)
RUN npm ci --only=production && \
    npm rebuild bcrypt --build-from-source && \
    npm cache clean --force
```

Ini memastikan bcrypt dikompilasi dengan benar untuk Alpine Linux/musl libc.

## Verifikasi Setelah Fix

1. **Test bcrypt:**
   ```bash
   docker-compose exec frontend node -e "try { require('bcrypt'); console.log('✅ bcrypt is available'); } catch(e) { console.log('❌ bcrypt is NOT available:', e.message); }"
   ```

2. **Test login:**
   - Buka frontend di browser
   - Coba login dengan kredensial yang valid
   - Login seharusnya berhasil sekarang

## Catatan Penting

- Solusi 1 (rebuild image) adalah solusi permanen dan direkomendasikan
- Solusi 2 hanya temporary dan akan hilang jika container di-recreate
- Pastikan build dependencies (python3, make, g++) tersedia di runner stage
- bcrypt akan otomatis di-rebuild setiap kali image di-build dengan Dockerfile yang sudah diperbaiki

## Troubleshooting

Jika masih ada masalah setelah rebuild:

1. **Cek log container:**
   ```bash
   docker-compose logs frontend
   ```

2. **Pastikan build dependencies terinstall:**
   ```bash
   docker-compose exec -u root frontend apk list | grep -E "python3|make|g\+\+"
   ```

3. **Cek versi Node.js:**
   ```bash
   docker-compose exec frontend node --version
   ```

4. **Coba rebuild manual di container:**
   ```bash
   docker-compose exec -u root frontend sh -c "cd /app && npm rebuild bcrypt --build-from-source --verbose"
   ```
