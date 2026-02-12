# Demo Request Email Setup

Dokumentasi konfigurasi email SMTP untuk form Request Demo di landing page BAGANA AI.

## Konfigurasi SMTP

Form Request Demo menggunakan konfigurasi SMTP berikut:

- **Username:** `demo@baganatech.com`
- **Password:** Gunakan password dari akun email tersebut (disimpan di environment variable)
- **Incoming Server:** `mail.baganatech.com`
  - IMAP Port: 993
  - POP3 Port: 995
- **Outgoing Server:** `mail.baganatech.com`
  - SMTP Port: 465 (SSL/TLS)

## Setup Environment Variables

Tambahkan variabel berikut ke file `.env` di root project:

```env
# SMTP Configuration untuk Demo Request Email
SMTP_HOST=mail.baganatech.com
SMTP_PORT=465
SMTP_USER=demo@baganatech.com
SMTP_PASSWORD=your_email_account_password_here
SMTP_SECURE=true
SMTP_REJECT_UNAUTHORIZED=true

# Email tujuan untuk menerima demo request
DEMO_REQUEST_RECIPIENT=sales@bagana.ai
```

## Instalasi Dependencies

Install package yang diperlukan:

```bash
npm install nodemailer @types/nodemailer
```

## API Endpoint

Endpoint API tersedia di: `POST /api/demo-request`

### Request Format

```json
{
  "nama": "John Doe",
  "email": "john@example.com",
  "perusahaan": "Example Corp (optional)",
  "timestamp": "2025-02-10T10:00:00.000Z (optional)",
  "language": "id" // "id" atau "en"
}
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "message": "Request demo berhasil dikirim. Tim kami akan menghubungi Anda dalam 1-2 hari kerja.",
  "messageId": "message-id-from-smtp-server"
}
```

**Error (400/500/503):**
```json
{
  "success": false,
  "error": "Error message description"
}
```

## Testing

### Test dengan cURL

```bash
curl -X POST http://localhost:3000/api/demo-request \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Test User",
    "email": "test@example.com",
    "perusahaan": "Test Company",
    "language": "id"
  }'
```

### Test dari Browser Console

```javascript
fetch('/api/demo-request', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    nama: 'Test User',
    email: 'test@example.com',
    perusahaan: 'Test Company',
    language: 'id'
  })
})
.then(res => res.json())
.then(data => console.log(data))
.catch(err => console.error(err));
```

## Troubleshooting

### Error: "nodemailer tidak ditemukan"
- **Solusi:** Install dependencies dengan `npm install nodemailer @types/nodemailer`

### Error: "SMTP_PASSWORD tidak dikonfigurasi"
- **Solusi:** Pastikan variabel `SMTP_PASSWORD` sudah ditambahkan ke file `.env`

### Error: "EAUTH" atau "ECONNECTION"
- **Solusi:** 
  - Periksa username dan password SMTP
  - Pastikan server `mail.baganatech.com` dapat diakses dari server
  - Periksa firewall atau network restrictions
  - Pastikan port 465 tidak diblokir

### Error: "rejectUnauthorized"
- **Solusi:** Jika menggunakan SSL certificate self-signed, set `SMTP_REJECT_UNAUTHORIZED=false` (tidak disarankan untuk production)

## Security Notes

1. **Jangan commit file `.env`** ke repository (sudah ada di `.gitignore`)
2. **Gunakan environment variables** untuk semua sensitive data
3. **Validasi input** di frontend dan backend
4. **Rate limiting** disarankan untuk mencegah spam
5. **Email sanitization** untuk mencegah injection attacks

## Email Template

Email yang dikirim menggunakan HTML template dengan:
- Subject berdasarkan bahasa (ID/EN)
- Informasi lengkap dari form (nama, email, perusahaan)
- Timestamp dan bahasa yang digunakan
- Reply-to header di-set ke email user untuk memudahkan reply langsung

## Production Checklist

- [ ] Environment variables sudah dikonfigurasi dengan benar
- [ ] SMTP credentials sudah diverifikasi
- [ ] Email recipient (`DEMO_REQUEST_RECIPIENT`) sudah benar
- [ ] Dependencies sudah terinstall (`nodemailer`)
- [ ] Error handling sudah di-test
- [ ] Rate limiting sudah diimplementasikan (opsional)
- [ ] Monitoring/logging sudah disetup untuk email failures
