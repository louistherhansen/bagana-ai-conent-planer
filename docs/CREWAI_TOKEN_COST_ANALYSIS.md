# Analisis Biaya Token CrewAI — BAGANA AI

Dokumen ini menjelaskan **apa saja yang berjalan di CrewAI** dan **mengapa penggunaan token bisa tinggi**, plus rekomendasi untuk menurunkan biaya.

---

## Optimasi yang sudah diterapkan

- **max_iter**: diturunkan dari 12 → **6** di `config/agents.yaml` (semua 3 agent).
- **Agent**: goal dan backstory dipendekkan (role tetap); mengurangi token system per request.
- **Tasks**: deskripsi dan expected_output di `config/tasks.yaml` dipadatkan; heading wajib dan format (Pie Chart, Bar/Line Chart) tetap dipertahankan.
- **Efek**: pengurangan signifikan token input per task dan jumlah iterasi per task; kualitas output tetap mengandalkan heading dan instruksi kunci.

---

## 1. Yang Berjalan di Setiap `crew.kickoff()`

Satu kali jalankan crew = **3 task berurutan**:

| Urutan | Task               | Agent            | Konteks yang dikirim ke LLM |
|--------|--------------------|------------------|-----------------------------|
| 1      | `create_content_plan` | content_planner  | System + role/goal/backstory + **deskripsi task sangat panjang** + expected_output |
| 2      | `analyze_sentiment`  | sentiment_analyst| Idem + **seluruh output task 1 (content plan)** sebagai context |
| 3      | `research_trends`    | trend_researcher | Idem + **seluruh output task 1 (content plan)** sebagai context |

Setiap task bisa melakukan sampai **12 iterasi** (reasoning + tool calls) karena `max_iter: 12` di `config/agents.yaml`. Jadi satu kickoff = **banyak panggilan LLM** (bukan cuma 3 kali).

---

## 2. Penyebab Token Cukup Mahal

### 2.1 Prompt per task sangat besar

- **Role, goal, backstory** tiap agent (~10–15 baris per agent) dikirim di **setiap** task.
- **Deskripsi task** di `config/tasks.yaml` sangat panjang (puluhan baris per task).
- **expected_output** juga sangat panjang (ratusan baris total untuk 3 task).
- Semua itu masuk ke **setiap** request ke model → token input tinggi.

### 2.2 Context chaining (output task 1 dipakai 2 kali)

- Task 2 dan 3 dapat **seluruh output** `create_content_plan` (satu dokumen content strategy penuh).
- Satu dokumen yang sama dikirim **2 kali** (ke sentiment_analyst dan trend_researcher).
- Jika content plan = 2.000–5.000 token, maka tambahan **4.000–10.000 token** hanya untuk context ini.

### 2.3 max_iter: 12 per agent

- Setiap task boleh sampai **12 langkah** (ReAct/tool/reasoning).
- Setiap langkah = 1+ panggilan LLM (input + output).
- 3 task × sampai 12 iter = **sampai 36+ panggilan LLM** dalam satu kickoff → token input+output berulang.

### 2.4 Model di .env

- Model dipakai dari `.env`: `OPENAI_MODEL` (atau OpenRouter).
- Jika pakai model besar (mis. `gpt-4o`, `claude-3-opus`) biaya per token jauh lebih tinggi.
- Default di kode: `gpt-4o-mini` (relatif murah); pastikan `.env` tidak memakai model mahal kalau ingin hemat.

---

## 3. Perkiraan Token per Kickoff (kasar)

| Komponen                         | Perkiraan token (input)     |
|----------------------------------|-----------------------------|
| System + 3 agent definitions     | ~2.000–3.000                |
| Task 1 (description + expected_output) | ~1.500–2.500          |
| Task 2 (idem + **full content plan**)  | ~2.000 + panjang plan |
| Task 3 (idem + **full content plan**)  | ~2.000 + panjang plan |
| Output tiap task (dibalik ke iterasi)  | ratusan–ribuan per task |
| **Total per kickoff**            | **10.000–30.000+ token** (tergantung panjang plan & jumlah iterasi) |

Ini hanya perkiraan; angka sebenarnya tergantung panjang user input, panjang output task 1, dan berapa iterasi yang benar-benar dipakai.

---

## 4. Rekomendasi Menurunkan Biaya

### 4.1 Kurangi `max_iter` (paling gampang)

Di `config/agents.yaml`:

- Sekarang: `max_iter: 12`.
- Coba: `max_iter: 6` atau `max_iter: 8` untuk MVP.
- Efek: lebih sedikit putaran reasoning/tool per task → lebih sedikit panggilan LLM.

### 4.2 Ringkas deskripsi dan expected_output di `config/tasks.yaml`

- Pertahankan struktur dan heading yang wajib, tapi **potong instruksi yang berulang**.
- Gabungkan poin yang mirip; buang kalimat yang tidak mengubah perilaku output.
- Efek: token input per request turun.

### 4.3 Ringkas role/goal/backstory di `config/agents.yaml`

- Tetap spesifik dan jelas, tapi **hindari paragraf panjang**.
- Efek: token system/context tiap task turun.

### 4.4 Batasi context ke task 2 dan 3 (advanced)

- Sekarang: **seluruh** output `create_content_plan` dikirim ke sentiment dan trend.
- Opsi: kirim hanya **ringkasan** (mis. 1–2 paragraf) atau bagian tertentu (mis. hanya “Key Messaging” + “Content Themes”) ke task 2 dan 3.
- Perlu ubah di `crew/run.py` atau lewat task context (mis. task yang hanya menerima summary).
- Efek: pengurangan besar token context untuk task 2 dan 3.

### 4.5 Pakai model murah di .env

- Pastikan `OPENAI_MODEL` (atau OpenRouter model) set ke model murah, mis. `openai/gpt-4o-mini` atau setara.
- Cek harga per token di OpenRouter/OpenAI dan bandingkan dengan model lain.

### 4.6 Pantau penggunaan di dashboard

- **OpenRouter**: https://openrouter.ai/activity  
- **OpenAI**: https://platform.openai.com/usage  
Di sana bisa lihat jumlah request dan token per model sehingga Anda bisa korelasikan dengan “setelah jalankan crew”.

---

## 5. Mengecek Jumlah Token (opsional)

- **OpenRouter / OpenAI dashboard**: cara paling andal untuk lihat token per request dan per hari.
- **CrewAI**: versi open-source tidak selalu mengembalikan `usage` (token in/out) di response; bila ada, bisa ditambahkan log di `crew/run.py` setelah `crew.kickoff()` (mis. dari `result` atau callback) dan ditulis ke `project-context/2.build/logs/trace.log` atau file terpisah.
- **LiteLLM / wrapper**: jika kelak crew dipanggil lewat proxy yang mendukung logging usage, token bisa dicatat di sana.

---

## 6. Ringkasan

| Faktor              | Pengaruh terhadap token / biaya |
|---------------------|----------------------------------|
| 3 task berurutan    | Banyak panggilan LLM per kickoff |
| Context = full plan ke 2 task | Satu dokumen besar dikirim 2× |
| max_iter: 12        | Sampai 12× lipat langkah per task |
| Deskripsi/expected_output panjang | Input token besar per request |
| Model mahal di .env | Biaya per token tinggi |

**Langkah pertama yang disarankan:** turunkan `max_iter` ke 6–8 dan pastikan model di `.env` adalah model murah; lalu pantau di OpenRouter/OpenAI dashboard. Setelah itu, ringkas prompt di `tasks.yaml` dan `agents.yaml`, dan pertimbangkan membatasi context ke task 2 dan 3 jika masih perlu penghematan lebih besar.
