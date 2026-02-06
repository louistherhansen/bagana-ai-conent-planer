# Chat History dengan PostgreSQL

Dokumentasi untuk setup dan penggunaan fitur chat history yang menggunakan PostgreSQL sebagai database.

## Setup Database

### 1. Pastikan PostgreSQL sudah berjalan

```bash
# Test koneksi database
python scripts/test-db-connection.py
```

### 2. Inisialisasi schema database

```bash
# Buat tabel conversations dan messages
python scripts/init-chat-history-db.py
```

### 3. Konfigurasi Environment Variables

Tambahkan konfigurasi database ke file `.env`:

```env
# PostgreSQL Database Configuration
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=bagana-ai-cp
DB_USER=postgres
DB_PASSWORD=123456
```

## Struktur Database

### Tabel `conversations`
- `id` (VARCHAR(255), PRIMARY KEY) - ID unik conversation
- `title` (VARCHAR(500)) - Judul conversation
- `created_at` (TIMESTAMP) - Waktu dibuat
- `updated_at` (TIMESTAMP) - Waktu terakhir diupdate (auto-update via trigger)

### Tabel `messages`
- `id` (VARCHAR(255), PRIMARY KEY) - ID unik message
- `conversation_id` (VARCHAR(255), FOREIGN KEY) - ID conversation
- `role` (VARCHAR(20)) - Role message: 'user' atau 'assistant'
- `content` (JSONB) - Konten message dalam format JSON
- `created_at` (TIMESTAMP) - Waktu dibuat

## API Endpoints

### GET /api/chat-history
Mendapatkan semua conversations atau conversation spesifik.

**Query Parameters:**
- `id` (optional) - ID conversation untuk mendapatkan conversation spesifik

**Response:**
```json
// Tanpa id: array of conversations
[
  {
    "id": "conv_123",
    "title": "New Chat",
    "createdAt": 1234567890,
    "updatedAt": 1234567890,
    "messages": []
  }
]

// Dengan id: single conversation dengan messages
{
  "id": "conv_123",
  "title": "New Chat",
  "createdAt": 1234567890,
  "updatedAt": 1234567890,
  "messages": [
    {
      "id": "msg_123",
      "role": "user",
      "content": [{"type": "text", "text": "Hello"}]
    }
  ]
}
```

### POST /api/chat-history
Membuat conversation baru.

**Request Body:**
```json
{
  "id": "conv_123",
  "title": "New Chat",
  "messages": [
    {
      "id": "msg_123",
      "role": "user",
      "content": [{"type": "text", "text": "Hello"}]
    }
  ]
}
```

### PUT /api/chat-history
Update conversation (title dan/atau messages).

**Request Body:**
```json
{
  "id": "conv_123",
  "title": "Updated Title",
  "messages": [...]
}
```

### DELETE /api/chat-history?id=<conversation_id>
Menghapus conversation dan semua messages-nya.

## Penggunaan di Frontend

### Import functions dari `lib/chatHistory.ts`

```typescript
import {
  getAllConversations,
  getConversation,
  createConversation,
  saveConversation,
  updateConversationMessages,
  deleteConversation,
  type Conversation,
  type ChatMessage
} from "@/lib/chatHistory";
```

### Contoh Penggunaan

```typescript
// Get all conversations
const conversations = await getAllConversations();

// Get specific conversation
const conversation = await getConversation("conv_123");

// Create new conversation
const newConv = await createConversation([
  {
    id: "msg_1",
    role: "user",
    content: [{ type: "text", text: "Hello" }]
  }
]);

// Update conversation messages
await updateConversationMessages("conv_123", [
  ...existingMessages,
  newMessage
]);

// Delete conversation
await deleteConversation("conv_123");
```

## Fallback ke localStorage

Jika API PostgreSQL tidak tersedia atau gagal, semua fungsi akan otomatis fallback ke localStorage untuk memastikan aplikasi tetap berfungsi.

## Troubleshooting

### Error: "relation does not exist"
- Pastikan sudah menjalankan `python scripts/init-chat-history-db.py`

### Error: "connection refused"
- Pastikan PostgreSQL sudah berjalan
- Periksa konfigurasi di `.env` (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD)

### Error: "password authentication failed"
- Periksa DB_PASSWORD di `.env` sesuai dengan password PostgreSQL

### API tidak merespons
- Pastikan Next.js dev server sudah berjalan (`npm run dev`)
- Periksa console browser untuk error details
- Fungsi akan otomatis fallback ke localStorage jika API gagal
