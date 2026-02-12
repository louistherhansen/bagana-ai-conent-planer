# Landing Page BAGANA AI

Halaman landing page HTML murni untuk informasi produk BAGANA AI.

## Cara Menggunakan

1. **Buka file langsung di browser:**
   - Buka `index.html` di browser web Anda (Chrome, Firefox, Edge, dll.)
   - File ini adalah HTML standalone yang tidak memerlukan server

2. **Atau jalankan dengan server lokal (opsional):**
   ```bash
   # Menggunakan Python
   python -m http.server 8000
   
   # Menggunakan Node.js (http-server)
   npx http-server -p 8000
   
   # Menggunakan PHP
   php -S localhost:8000
   ```
   Kemudian buka `http://localhost:8000` di browser

## Konten

Halaman ini menampilkan:
- **Header:** Judul dan deskripsi BAGANA AI
- **Fitur Utama:** 6 fitur utama platform (Content Plans, Sentiment Analysis, Trend Insights, AI Chat, Messaging Optimization, Reports & Dashboards)
- **Produk AI Chart:** 4 produk chart (Sentiment Pie Charts, Trend Line Charts, Summary Bar Charts, Custom Charts)
- **Cara Kerja:** 4 langkah proses workflow
- **Footer:** Informasi kontak dan repository

## Styling

Halaman menggunakan CSS inline yang responsif dan modern dengan:
- Skema warna BAGANA AI (teal/turquoise)
- Grid layout yang responsif
- Hover effects dan transisi
- Mobile-friendly design

## Menu Dinamis

Menu navigasi dibuat secara dinamis menggunakan JavaScript. Konfigurasi menu dapat diubah dengan dua cara:

### 1. Menggunakan File JSON (`menu-config.json`)

Edit file `menu-config.json` untuk mengubah menu:
- Tambah/hapus item menu
- Ubah label atau order
- Toggle visibility dengan `"visible": false`

### 2. Menggunakan JavaScript Functions (dari Browser Console)

Buka browser console dan gunakan fungsi berikut:

```javascript
// Tambah menu item baru
addMenuItem('#section-id', 'Label Menu', 6);

// Hapus menu item
removeMenuItem('#section-id');

// Update menu item
updateMenuItem('#old-id', '#new-id', 'New Label', 7);
```

### Fitur Menu Dinamis

- **Auto-sort**: Menu diurutkan berdasarkan `order`
- **Smooth scroll**: Klik menu akan scroll ke section dengan smooth animation
- **Active highlight**: Menu item yang aktif akan di-highlight saat scroll
- **Visibility control**: Menu dapat disembunyikan dengan `visible: false`

## Form Request Demo dengan Email SMTP

Form Request Demo di section "Demo" dapat mengirim email melalui backend API endpoint `/api/demo-request`.

### Konfigurasi SMTP

Backend API menggunakan konfigurasi SMTP berikut:

- **Username:** `demo@baganatech.com`
- **Password:** (dari environment variable `SMTP_PASSWORD`)
- **Outgoing Server:** `mail.baganatech.com`
- **SMTP Port:** `465`
- **Security:** SSL/TLS (secure: true)

### Environment Variables yang Diperlukan

Tambahkan variabel berikut ke file `.env` di root project:

```env
# SMTP Configuration untuk Demo Request Email
SMTP_HOST=mail.baganatech.com
SMTP_PORT=465
SMTP_USER=demo@baganatech.com
SMTP_PASSWORD=your_email_password_here
SMTP_SECURE=true
SMTP_REJECT_UNAUTHORIZED=true

# Email tujuan untuk menerima demo request
DEMO_REQUEST_RECIPIENT=sales@bagana.ai
```

### Instalasi Dependencies

Pastikan `nodemailer` sudah terinstall:

```bash
npm install nodemailer @types/nodemailer
```

### API Endpoint

Endpoint API tersedia di: `POST /api/demo-request`

**Request Body:**
```json
{
  "nama": "John Doe",
  "email": "john@example.com",
  "perusahaan": "Example Corp",
  "timestamp": "2025-02-10T10:00:00.000Z",
  "language": "id"
}
```

**Response Success:**
```json
{
  "success": true,
  "message": "Request demo berhasil dikirim...",
  "messageId": "..."
}
```

**Response Error:**
```json
{
  "success": false,
  "error": "Error message..."
}
```

### Catatan Penting

- Pastikan password email (`SMTP_PASSWORD`) disimpan dengan aman di environment variables
- Jangan commit file `.env` ke repository (sudah ada di `.gitignore`)
- Email akan dikirim ke alamat yang dikonfigurasi di `DEMO_REQUEST_RECIPIENT`
- Form akan menampilkan pesan error jika email gagal dikirim

## Catatan

- File ini adalah HTML murni tanpa dependensi eksternal
- Form Request Demo memerlukan backend API endpoint untuk mengirim email
- Tidak terhubung dengan aplikasi Next.js utama (kecuali untuk API endpoint email)
- Dapat digunakan sebagai halaman marketing standalone atau di-host secara terpisah
- Menu dinamis menggunakan JavaScript vanilla (tidak perlu framework)
