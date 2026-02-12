# Solusi Masalah "Invalid email/username or password" Setelah Fix bcrypt

## Masalah
Setelah memperbaiki bcrypt di container, login masih gagal dengan error "Invalid email/username or password".

## Penyebab
Kode Next.js yang sudah di-build (di folder `.next/server`) masih menggunakan versi lama yang:
1. Menggunakan dynamic import (`await import('bcrypt')`) yang mungkin tidak bekerja dengan baik di standalone mode
2. Throw error di production jika bcrypt tidak tersedia
3. Tidak menangani error dengan baik

## Solusi

### Solusi 1: Rebuild Docker Image (Permanen - Direkomendasikan)

**Windows PowerShell:**
```powershell
.\scripts\rebuild-frontend-fix.ps1
```

**Manual:**
```bash
# Stop frontend
docker-compose stop frontend

# Rebuild image
docker-compose build frontend

# Start frontend
docker-compose up -d frontend

# Verify bcrypt
docker-compose exec frontend node -e "try { require('bcrypt'); console.log('✅ bcrypt is available'); } catch(e) { console.log('❌ bcrypt is NOT available:', e.message); }"
```

### Solusi 2: Temporary Fix - Set NODE_ENV ke development

Jika tidak bisa rebuild sekarang, Anda bisa set `NODE_ENV=development` sementara untuk menghindari error throw:

1. **Edit docker-compose.yml** - ubah `NODE_ENV: production` menjadi `NODE_ENV: development` untuk service frontend
2. **Restart container:**
   ```bash
   docker-compose restart frontend
   ```

**Catatan:** Ini hanya temporary fix. Rebuild image untuk solusi permanen.

## Perubahan yang Sudah Dilakukan

### 1. lib/auth.ts
- Mengubah dynamic import (`await import('bcrypt')`) menjadi `require('bcrypt')` untuk kompatibilitas yang lebih baik
- Memperbaiki error handling di `verifyPassword()` agar tidak throw error di production
- Menambahkan fallback yang lebih robust

### 2. Dockerfile.frontend
- Menambahkan rebuild bcrypt setelah instalasi dependencies
- Memastikan build dependencies tersedia

## Verifikasi Setelah Fix

1. **Test bcrypt:**
   ```bash
   docker-compose exec frontend node -e "try { require('bcrypt'); console.log('✅ bcrypt is available'); } catch(e) { console.log('❌ bcrypt is NOT available:', e.message); }"
   ```

2. **Test login:**
   - Buka frontend di browser
   - Coba login dengan kredensial yang valid
   - Login seharusnya berhasil sekarang

3. **Cek log untuk error:**
   ```bash
   docker-compose logs frontend --tail 50 | grep -i "bcrypt\|password\|login"
   ```

## Troubleshooting

### Masih error "Invalid email/username or password"

1. **Cek apakah user ada di database:**
   ```bash
   docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "SELECT email, username FROM users LIMIT 5;"
   ```

2. **Cek format password hash:**
   ```bash
   docker-compose exec postgres psql -U bagana_user -d bagana_ai -c "SELECT email, LEFT(password_hash, 20) as hash_preview FROM users LIMIT 5;"
   ```
   - Jika hash dimulai dengan `$2a$`, `$2b$`, atau `$2y$` → bcrypt hash
   - Jika hash adalah 64 karakter hex → SHA-256 hash

3. **Test verify password secara langsung:**
   ```bash
   docker-compose exec frontend node -e "
   const bcrypt = require('bcrypt');
   const hash = '\$2b\$10\$...'; // ganti dengan hash dari database
   bcrypt.compare('password123', hash).then(result => console.log('Match:', result));
   "
   ```

### Error "bcrypt is required for production"

Ini berarti kode yang sudah di-build masih menggunakan versi lama. **Rebuild Docker image** untuk memperbaikinya.

### Error "No native build was found"

bcrypt belum di-rebuild untuk platform Alpine Linux. Pastikan:
1. Build dependencies terinstall: `python3`, `make`, `g++`
2. bcrypt di-rebuild: `npm rebuild bcrypt --build-from-source`

## Catatan Penting

- **Rebuild Docker image adalah solusi permanen** - perubahan di `lib/auth.ts` hanya akan berlaku setelah rebuild
- bcrypt sudah tersedia di container (sudah diinstall dan di-rebuild)
- Masalahnya adalah kode yang sudah di-build masih menggunakan versi lama
- Setelah rebuild, semua perubahan akan diterapkan dan login akan berfungsi
