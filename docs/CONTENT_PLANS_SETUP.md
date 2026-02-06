# Content Plans dengan PostgreSQL

Dokumentasi untuk setup dan penggunaan fitur Content Plans yang menggunakan PostgreSQL sebagai database.

## Setup Database

### 1. Pastikan PostgreSQL sudah berjalan

```bash
# Test koneksi database
python scripts/test-db-connection.py
```

### 2. Inisialisasi schema database

```bash
# Buat tabel content_plans, plan_versions, dan plan_talents
python scripts/init-content-plans-db.py
```

### 3. Konfigurasi Environment Variables

Pastikan konfigurasi database sudah ada di file `.env`:

```env
# PostgreSQL Database Configuration
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=bagana-ai-cp
DB_USER=postgres
DB_PASSWORD=123456
```

## Struktur Database

### Tabel `content_plans`
- `id` (VARCHAR(255), PRIMARY KEY) - ID unik plan
- `title` (VARCHAR(500)) - Judul plan
- `campaign` (VARCHAR(500)) - Nama campaign (opsional)
- `brand_name` (VARCHAR(255)) - Nama brand (opsional)
- `conversation_id` (VARCHAR(255), FOREIGN KEY) - ID conversation yang menghasilkan plan ini
- `schema_valid` (BOOLEAN) - Apakah plan valid terhadap schema
- `created_at` (TIMESTAMP) - Waktu dibuat
- `updated_at` (TIMESTAMP) - Waktu terakhir diupdate (auto-update via trigger)

### Tabel `plan_versions`
- `id` (VARCHAR(255), PRIMARY KEY) - ID unik version
- `plan_id` (VARCHAR(255), FOREIGN KEY) - ID plan
- `version` (VARCHAR(50)) - Nomor versi (e.g., "v1.0", "v2.0")
- `content` (JSONB) - Konten plan dalam format JSON
- `metadata` (JSONB) - Metadata tambahan (opsional)
- `created_at` (TIMESTAMP) - Waktu dibuat
- CONSTRAINT: unique_plan_version (plan_id, version)

### Tabel `plan_talents`
- `plan_id` (VARCHAR(255), FOREIGN KEY) - ID plan
- `talent_name` (VARCHAR(255)) - Nama talent
- `created_at` (TIMESTAMP) - Waktu dibuat
- PRIMARY KEY: (plan_id, talent_name)

## API Endpoints

### GET /api/content-plans
Mendapatkan semua content plans atau plan spesifik.

**Query Parameters:**
- `id` (optional) - ID plan untuk mendapatkan plan spesifik dengan versions

**Response:**
```json
// Tanpa id: array of plan summaries
[
  {
    "id": "plan_123",
    "title": "Nike Content Plan",
    "campaign": "Summer Campaign",
    "brandName": "Nike",
    "schemaValid": true,
    "talents": ["Creator 1", "Creator 2"],
    "version": "v1.0",
    "updatedAt": 1234567890
  }
]

// Dengan id: single plan dengan versions
{
  "id": "plan_123",
  "title": "Nike Content Plan",
  "campaign": "Summer Campaign",
  "brandName": "Nike",
  "conversationId": "conv_123",
  "schemaValid": true,
  "talents": ["Creator 1", "Creator 2"],
  "versions": [
    {
      "id": "plan_123_v1.0",
      "version": "v1.0",
      "content": {...},
      "metadata": {...},
      "createdAt": 1234567890
    }
  ],
  "createdAt": 1234567890,
  "updatedAt": 1234567890
}
```

### POST /api/content-plans
Membuat content plan baru atau menambahkan version baru ke plan yang sudah ada.

**Request Body:**
```json
{
  "id": "plan_123",
  "title": "Nike Content Plan",
  "campaign": "Summer Campaign",
  "brandName": "Nike",
  "conversationId": "conv_123",
  "schemaValid": true,
  "talents": ["Creator 1", "Creator 2"],
  "version": "v1.0",
  "content": {...},
  "metadata": {...}
}
```

### PUT /api/content-plans
Update content plan (title, campaign, brandName, schemaValid, talents).

**Request Body:**
```json
{
  "id": "plan_123",
  "title": "Updated Title",
  "campaign": "Updated Campaign",
  "brandName": "Updated Brand",
  "schemaValid": true,
  "talents": ["Creator 1", "Creator 2", "Creator 3"]
}
```

### DELETE /api/content-plans?id=<plan_id>
Menghapus content plan dan semua versions serta talents terkait.

## Frontend Library

File `lib/contentPlans.ts` menyediakan fungsi-fungsi untuk mengakses content plans:

- `getAllPlans()` - Mendapatkan semua plans
- `getPlan(id)` - Mendapatkan plan spesifik dengan versions
- `createPlan(data)` - Membuat plan baru
- `updatePlan(id, data)` - Update plan
- `addPlanVersion(planId, version, content, metadata)` - Menambahkan version baru
- `deletePlan(id)` - Menghapus plan

Semua fungsi memiliki fallback ke localStorage jika API tidak tersedia.

## Auto-Extraction dari Chat

Ketika crew selesai menghasilkan content plan melalui chat, sistem akan secara otomatis:

1. Mengekstrak content strategy dari `task_outputs`
2. Mengekstrak brand name dan campaign dari conversation messages
3. Mengekstrak talents dari content strategy output
4. Menyimpan plan ke database dengan versi v1.0

Plan akan muncul di halaman `/plans` setelah crew selesai.

## Cara Menggunakan

1. **Buat plan melalui Chat:**
   - Buka `/chat`
   - Isi form dengan brand name, campaign, dan talents
   - Kirim pesan
   - Crew akan menghasilkan content plan
   - Plan akan otomatis tersimpan ke database

2. **Lihat plans:**
   - Buka `/plans`
   - Semua plans akan ditampilkan di tab "Plans"
   - Klik plan untuk melihat detail (future feature)

3. **Manual create plan (via API):**
   ```typescript
   import { createPlan } from "@/lib/contentPlans";
   
   await createPlan({
     title: "My Content Plan",
     brandName: "Nike",
     campaign: "Summer 2025",
     talents: ["Creator 1", "Creator 2"],
     content: { ... },
   });
   ```

## Troubleshooting

- **Plan tidak muncul setelah chat:**
  - Periksa console browser untuk error
  - Pastikan content strategy task menghasilkan output
  - Periksa database apakah plan tersimpan

- **Error saat load plans:**
  - Pastikan PostgreSQL berjalan
  - Periksa konfigurasi database di `.env`
  - Jalankan `python scripts/init-content-plans-db.py` untuk memastikan schema sudah dibuat

- **Plan tidak ter-extract dari chat:**
  - Pastikan task `create_content_strategy` menghasilkan output
  - Periksa format output dari crew
  - Lihat console log untuk detail extraction
