# Login Fix - Manual Testing Guide

**Date:** 2025-02-12  
**Issue:** Login tidak bisa setelah perubahan security database  
**Status:** ✅ Fixed - Ready for Testing

---

## 🔧 Perbaikan yang Dilakukan

### 1. Password Verification - Backward Compatibility ✅

**Masalah:**
- Password lama di database menggunakan SHA-256 (64 karakter hex)
- Password baru menggunakan bcrypt (60 karakter dengan prefix `$2a$`)
- Fungsi `verifyPassword` hanya menggunakan bcrypt, sehingga password lama tidak bisa diverifikasi

**Solusi:**
- Update `verifyPassword` untuk mendeteksi format hash secara otomatis
- Support kedua format: SHA-256 (backward compatibility) dan bcrypt (new format)
- Auto-migrate password dari SHA-256 ke bcrypt saat login berhasil

**File yang Diubah:**
- `lib/auth.ts` - Update fungsi `verifyPassword()`
- `app/api/auth/login/route.ts` - Tambah auto-migration saat login

---

## 🧪 Manual Testing Steps

### Test 1: Login dengan Password Lama (SHA-256)

1. **Persiapan:**
   - Pastikan ada user di database dengan password lama (SHA-256)
   - Atau buat user baru dengan password tertentu

2. **Test Login:**
   - Buka halaman login: `http://localhost:3000/login`
   - Masukkan email/username dan password yang sudah ada
   - Klik "Sign In"

3. **Expected Result:**
   - ✅ Login berhasil
   - ✅ Redirect ke dashboard
   - ✅ Password otomatis di-migrate ke bcrypt di database

4. **Verify Migration:**
   - Cek database: password_hash harus berubah dari SHA-256 (64 hex) ke bcrypt (60 chars dengan prefix `$2a$`)
   - Login lagi dengan password yang sama - harus tetap berhasil

---

### Test 2: Login dengan Password Baru (bcrypt)

1. **Persiapan:**
   - Buat user baru melalui User Management atau Register
   - Password baru akan otomatis di-hash dengan bcrypt

2. **Test Login:**
   - Buka halaman login
   - Masukkan email/username dan password user baru
   - Klik "Sign In"

3. **Expected Result:**
   - ✅ Login berhasil
   - ✅ Redirect ke dashboard
   - ✅ Password sudah menggunakan bcrypt (tidak perlu migration)

---

### Test 3: Login dengan Password Salah

1. **Test:**
   - Buka halaman login
   - Masukkan email/username yang benar
   - Masukkan password yang salah
   - Klik "Sign In"

2. **Expected Result:**
   - ❌ Login gagal
   - ✅ Error message: "Invalid email/username or password"
   - ✅ Tidak ada redirect

---

### Test 4: Login dengan User yang Tidak Ada

1. **Test:**
   - Buka halaman login
   - Masukkan email/username yang tidak ada di database
   - Masukkan password apapun
   - Klik "Sign In"

2. **Expected Result:**
   - ❌ Login gagal
   - ✅ Error message: "Invalid email/username or password"
   - ✅ Tidak ada redirect

---

### Test 5: Environment Variable Validation

1. **Test tanpa DB_PASSWORD:**
   - Hapus atau comment `DB_PASSWORD` dari `.env`
   - Restart aplikasi

2. **Expected Result:**
   - ❌ Aplikasi gagal start dengan error yang jelas
   - ✅ Error message: "Missing required environment variables: DB_PASSWORD"
   - ✅ Instruksi untuk check `.env.example`

---

## 🔍 Debugging Tips

### Jika Login Masih Gagal:

1. **Cek Database Connection:**
   ```bash
   # Pastikan DB_PASSWORD sudah di-set di .env
   # Cek apakah database bisa diakses
   ```

2. **Cek Password Hash Format di Database:**
   ```sql
   SELECT email, username, 
          LENGTH(password_hash) as hash_length,
          SUBSTRING(password_hash, 1, 4) as hash_prefix
   FROM users;
   ```
   
   - SHA-256: length = 64, prefix = hex characters (0-9a-f)
   - bcrypt: length = 60, prefix = `$2a$` atau `$2b$`

3. **Cek Console Logs:**
   - Buka browser DevTools → Console
   - Cek Network tab untuk melihat response dari `/api/auth/login`
   - Cek server logs untuk error messages

4. **Test Password Verification Manual:**
   ```typescript
   // Di Node.js console atau script
   const { verifyPassword } = require('./lib/auth');
   const password = 'your_password';
   const hash = 'hash_from_database';
   const result = await verifyPassword(password, hash);
   console.log('Result:', result);
   ```

---

## 📋 Checklist Testing

- [ ] Test 1: Login dengan password lama (SHA-256) - ✅ Berhasil
- [ ] Test 2: Login dengan password baru (bcrypt) - ✅ Berhasil
- [ ] Test 3: Login dengan password salah - ❌ Ditolak dengan benar
- [ ] Test 4: Login dengan user tidak ada - ❌ Ditolak dengan benar
- [ ] Test 5: Environment variable validation - ✅ Error jelas jika tidak ada DB_PASSWORD
- [ ] Verify: Password migration dari SHA-256 ke bcrypt bekerja
- [ ] Verify: Login kedua kali dengan password yang sama tetap berhasil setelah migration

---

## 🐛 Known Issues & Solutions

### Issue 1: "Missing required environment variables: DB_PASSWORD"

**Solution:**
- Pastikan file `.env` ada di root project
- Set `DB_PASSWORD=your_secure_password` di `.env`
- Restart aplikasi

### Issue 2: "bcrypt is required for production"

**Solution:**
- Install bcrypt: `npm install bcrypt @types/bcrypt`
- Pastikan bcrypt terinstall dengan benar

### Issue 3: Password lama tidak bisa login

**Solution:**
- Pastikan fungsi `verifyPassword` sudah di-update (support SHA-256)
- Cek format password_hash di database
- Jika masih gagal, reset password user melalui User Management

---

## ✅ Expected Behavior After Fix

1. **Password Lama (SHA-256):**
   - ✅ Bisa login dengan password lama
   - ✅ Password otomatis di-migrate ke bcrypt saat login pertama kali
   - ✅ Login kedua kali tetap berhasil dengan password yang sama

2. **Password Baru (bcrypt):**
   - ✅ Bisa login langsung
   - ✅ Password sudah menggunakan bcrypt (secure)

3. **Security:**
   - ✅ Password baru menggunakan bcrypt (secure)
   - ✅ Password lama tetap bisa digunakan (backward compatibility)
   - ✅ Auto-migration memastikan semua password akhirnya menggunakan bcrypt

---

## 📝 Notes

- **Migration Strategy:** Password di-migrate secara gradual saat user login
- **No Downtime:** User tidak perlu reset password - bisa langsung login
- **Security:** Setelah migration, password menggunakan bcrypt yang lebih aman
- **Backward Compatibility:** Password lama tetap bisa digunakan sampai di-migrate

---

## Audit

**Persona:** QA Engineer  
**Action:** Login Fix Manual Testing Guide  
**Timestamp:** 2025-02-12  
**Status:** Ready for Testing ✅
