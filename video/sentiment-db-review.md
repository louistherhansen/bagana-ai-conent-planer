# Database Review: PostgreSQL sentiment_analyses Table

## Schema Saat Ini

### Tabel: `sentiment_analyses`

```sql
CREATE TABLE IF NOT EXISTS sentiment_analyses (
    id VARCHAR(255) PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    positive_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
    negative_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
    neutral_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
    full_output TEXT,
    conversation_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
CREATE INDEX idx_sentiment_analyses_brand_name ON sentiment_analyses(brand_name);
CREATE INDEX idx_sentiment_analyses_created_at ON sentiment_analyses(created_at DESC);
CREATE INDEX idx_sentiment_analyses_conversation_id ON sentiment_analyses(conversation_id);
```

## Analisis terhadap Template sentiment_risk.md

### Data yang Tersimpan Saat Ini ✅

| Field | Status | Keterangan |
|-------|--------|------------|
| `id` | ✅ | Primary key untuk identifikasi unik |
| `brand_name` | ✅ | Nama brand (indexed untuk filtering) |
| `positive_pct` | ✅ | Persentase sentiment positif (0-100) |
| `negative_pct` | ✅ | Persentase sentiment negatif (0-100) |
| `neutral_pct` | ✅ | Persentase sentiment netral (0-100) |
| `full_output` | ✅ | Seluruh output markdown dari agent (TEXT) |
| `conversation_id` | ✅ | Link ke conversation (indexed) |
| `created_at` | ✅ | Timestamp pembuatan (indexed DESC untuk sorting) |

### Data dari Template yang Tersimpan di `full_output` ✅

Semua data berikut tersimpan dalam `full_output` sebagai markdown:
- ✅ Sentiment Composition (Pie Chart line)
- ✅ Overall Sentiment Score dengan confidence level
- ✅ Key Positive Sentiment Drivers
- ✅ Key Negative Sentiment Triggers
- ✅ Audience Sensitivity Areas
- ✅ Platform-Specific Risk Matrix
- ✅ Potential Controversy Scenarios
- ✅ Misinformation & Claim Risk Assessment
- ✅ Cultural, Legal, or Ethical Risk Flags
- ✅ Risk Severity Classification
- ✅ Recommended Mitigation Actions
- ✅ Opportunities
- ✅ Go/Caution/No-Go Recommendation

## Evaluasi Schema

### ✅ Kelebihan Schema Saat Ini

1. **Struktur Minimalis dan Efisien**
   - Hanya menyimpan data esensial untuk visualisasi (persentase)
   - Full output tersimpan lengkap untuk detail analysis
   - Indexes sudah optimal untuk query umum

2. **Fleksibilitas**
   - `full_output` TEXT dapat menyimpan struktur markdown lengkap
   - Tidak perlu migration jika struktur template berubah
   - Parsing dapat dilakukan di application layer

3. **Performance**
   - Indexes pada `brand_name`, `created_at`, dan `conversation_id` sudah optimal
   - Query filtering dan sorting sudah efisien

### ⚠️ Potensi Perbaikan (Opsional)

Jika diperlukan query yang lebih spesifik tanpa parsing `full_output`, pertimbangkan menambahkan field berikut:

#### 1. Risk Severity Classification
```sql
risk_severity VARCHAR(20) CHECK (risk_severity IN ('Low', 'Medium', 'High'))
```
**Manfaat**: Query cepat untuk filter berdasarkan risk level
**Trade-off**: Perlu parsing dan update saat insert

#### 2. Overall Sentiment Score
```sql
overall_sentiment VARCHAR(50),  -- e.g., "Positive", "Neutral", "Negative"
sentiment_score_pct NUMERIC(5,2),  -- Overall percentage
confidence_level VARCHAR(20)  -- e.g., "High", "Medium", "Low"
```
**Manfaat**: Query cepat untuk sentiment trend analysis
**Trade-off**: Redundant dengan positive/neutral/negative percentages

#### 3. Recommendation Status
```sql
recommendation_status VARCHAR(20) CHECK (recommendation_status IN ('Go', 'Caution', 'No-Go'))
```
**Manfaat**: Query cepat untuk filter campaign recommendations
**Trade-off**: Perlu parsing dari full_output

#### 4. Platform Risk Summary (JSONB)
```sql
platform_risks JSONB  -- e.g., {"YouTube": "Medium", "Instagram": "Low", ...}
```
**Manfaat**: Query dan filter berdasarkan platform risk
**Trade-off**: Perlu parsing dan struktur JSON

## Rekomendasi

### ✅ Schema Saat Ini CUKUP untuk MVP

Schema saat ini sudah **cukup baik** untuk kebutuhan MVP karena:

1. **Data Esensial Tersimpan**: Persentase sentiment untuk Pie Chart sudah ada
2. **Data Lengkap Tersedia**: Full output markdown menyimpan semua detail analysis
3. **Query Efisien**: Indexes sudah optimal untuk use case umum
4. **Fleksibilitas**: Tidak perlu migration jika template berubah

### 📋 Jika Perlu Optimasi di Masa Depan

Jika di masa depan diperlukan:
- **Dashboard dengan filter risk severity**
- **Analytics berdasarkan recommendation status**
- **Platform-specific risk filtering**

Maka pertimbangkan menambahkan field-field opsional di atas dengan migration script.

### 🔍 Validasi Schema terhadap Template

| Requirement dari Template | Status | Implementasi |
|--------------------------|--------|---------------|
| Pie Chart data (Positive/Neutral/Negative %) | ✅ | Field: `positive_pct`, `neutral_pct`, `negative_pct` |
| Overall Sentiment Score | ✅ | Tersimpan di `full_output` |
| Confidence Level | ✅ | Tersimpan di `full_output` |
| Key Drivers/Triggers | ✅ | Tersimpan di `full_output` |
| Platform-Specific Risk Matrix | ✅ | Tersimpan di `full_output` |
| Risk Severity Classification | ✅ | Tersimpan di `full_output` |
| Recommendations | ✅ | Tersimpan di `full_output` |
| Go/Caution/No-Go | ✅ | Tersimpan di `full_output` |

## Kesimpulan

✅ **Schema database saat ini SUDAH SESUAI** dengan template `sentiment_risk.md`

- Semua data dari template tersimpan lengkap di `full_output`
- Data esensial untuk visualisasi (persentase) sudah tersimpan sebagai field terpisah
- Indexes sudah optimal untuk performa query
- Struktur fleksibel dan tidak memerlukan migration jika template berubah

**Tidak ada perubahan yang diperlukan** untuk MVP. Schema dapat dioptimasi di masa depan jika diperlukan query yang lebih spesifik tanpa parsing.
