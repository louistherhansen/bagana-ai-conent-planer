# Template Check: Sentiment Analysis Agent Output

## Template yang Diharapkan (dari `config/tasks.yaml`)

### Format Baris Pie Chart (WAJIB di baris pertama)
```
Sentiment Composition (Pie Chart): Positive X%, Neutral Y%, Negative Z%
```
- X + Y + Z harus = 100
- Format ini digunakan untuk parsing oleh `parseSentimentComposition()` di `lib/sentimentAnalysis.ts`
- Regex pattern: `/Sentiment Composition\s*\([^)]*\)\s*:\s*(?:Positive|Positif)\s*(\d+(?:\.\d+)?)\s*%?\s*,?\s*(?:Neutral|Netral)\s*(\d+(?:\.\d+)?)\s*%?\s*,?\s*(?:Negative|Negatif)\s*(\d+(?:\.\d+)?)\s*%?/i`

### Konten yang Harus Ada (dari `expected_output`)
1. ✅ **Sentiment Composition (Pie Chart)** - Baris pertama dengan format di atas
2. ✅ **Overall Sentiment Score** dengan confidence level
3. ✅ **Key Positive Sentiment Drivers**
4. ✅ **Key Negative Sentiment Triggers**
5. ✅ **Audience Sensitivity Areas** (e.g. pricing, safety, ethics, claims)
6. ⚠️ **Platform-Specific Risk Matrix** (YouTube, Instagram, TikTok, X, LinkedIn)
7. ✅ **Potential Controversy Scenarios**
8. ⚠️ **Misinformation & Claim Risk Assessment**
9. ⚠️ **Cultural, Legal, or Ethical Risk Flags**
10. ⚠️ **Risk Severity Classification** (Low / Medium / High)
11. ✅ **Recommended Mitigation Actions**
12. ✅ **Opportunities**
13. ✅ **Recommendations**

### Struktur Heading yang Diperlukan (dari `expected_output`)
```
# Sentiment Summary (include the Pie Chart line here)
# Identified Risks
# Brand Safety Concerns
# Risk Mitigation Strategies
# Opportunities
# Recommendations
# Audit
```

## Hasil Aktual (dari `project-context/2.build/artifacts/sentiment.md`)

### ✅ Yang Sudah Sesuai:
1. ✅ **Sentiment Composition (Pie Chart)** - Ada di baris pertama dengan format benar
2. ✅ **Sentiment Summary** - Ada dengan Overall Sentiment Score dan confidence level
3. ✅ **Key Positive Sentiment Drivers** - Ada di dalam Sentiment Summary
4. ✅ **Key Negative Sentiment Triggers** - Ada di dalam Sentiment Summary
5. ✅ **Identified Risks** - Ada dengan Audience Sensitivity Areas dan Potential Controversy Scenarios
6. ✅ **Brand Safety Concerns** - Ada
7. ✅ **Risk Mitigation Strategies** - Ada
8. ✅ **Opportunities** - Ada
9. ✅ **Recommendations** - Ada
10. ✅ **Audit** - Ada

### ⚠️ Yang Kurang/Kurang Eksplisit:
1. ⚠️ **Platform-Specific Risk Matrix** - Tidak ada heading khusus untuk ini. Seharusnya ada evaluasi risiko per platform (YouTube, Instagram, TikTok, X, LinkedIn)
2. ⚠️ **Misinformation & Claim Risk Assessment** - Tidak ada heading khusus. Seharusnya ada deteksi risiko misinformasi dan klaim berlebihan
3. ⚠️ **Cultural, Legal, or Ethical Risk Flags** - Tidak ada heading khusus. Seharusnya ada flagging untuk sensitivitas budaya, hukum, atau etika
4. ⚠️ **Risk Severity Classification** - Tidak ada klasifikasi Low/Medium/High yang eksplisit

## Rekomendasi Perbaikan Template

### Opsi 1: Update Task Description (Lebih Eksplisit)
Tambahkan instruksi yang lebih jelas di `config/tasks.yaml` untuk memastikan semua elemen ada:

```yaml
Tasks:
  1. Compute overall sentiment composition...
  2. Analyze sentiment trends...
  3. Identify potential reputational risks...
  4. Assess audience sentiment polarity...
  5. Detect misinformation, exaggerated claims... → HARUS ada heading "Misinformation & Claim Risk Assessment"
  6. Evaluate platform-specific sentiment risks... → HARUS ada heading "Platform-Specific Risk Matrix" dengan tabel/daftar per platform
  7. Flag legal, ethical, or cultural sensitivities... → HARUS ada heading "Cultural, Legal, or Ethical Risk Flags"
  8. Provide actionable mitigation recommendations... → HARUS include Risk Severity Classification (Low/Medium/High) untuk setiap risiko
```

### Opsi 2: Update Expected Output Structure
Perjelas struktur heading di `expected_output`:

```yaml
Artifact structure with headings:
  - Sentiment Summary (include the Pie Chart line here, Overall Sentiment Score, Key Drivers/Triggers)
  - Platform-Specific Risk Matrix (REQUIRED: evaluate risks per platform: YouTube, Instagram, TikTok, X, LinkedIn)
  - Identified Risks (include Audience Sensitivity Areas, Potential Controversy Scenarios)
  - Misinformation & Claim Risk Assessment (REQUIRED: detect misinformation and exaggerated claims)
  - Cultural, Legal, or Ethical Risk Flags (REQUIRED: flag cultural, legal, ethical sensitivities)
  - Brand Safety Concerns (include Risk Severity Classification: Low/Medium/High for each concern)
  - Risk Mitigation Strategies
  - Opportunities
  - Recommendations
  - Audit
```

## Checklist Validasi Template

Gunakan checklist ini untuk memvalidasi setiap output sentiment analysis:

- [ ] Baris pertama memiliki format: `Sentiment Composition (Pie Chart): Positive X%, Neutral Y%, Negative Z%`
- [ ] X + Y + Z = 100
- [ ] Ada heading `# Sentiment Summary` dengan Overall Sentiment Score dan confidence level
- [ ] Ada heading `# Platform-Specific Risk Matrix` dengan evaluasi per platform
- [ ] Ada heading `# Identified Risks` dengan Audience Sensitivity Areas dan Potential Controversy Scenarios
- [ ] Ada heading `# Misinformation & Claim Risk Assessment`
- [ ] Ada heading `# Cultural, Legal, or Ethical Risk Flags`
- [ ] Ada heading `# Brand Safety Concerns` dengan Risk Severity Classification (Low/Medium/High)
- [ ] Ada heading `# Risk Mitigation Strategies`
- [ ] Ada heading `# Opportunities`
- [ ] Ada heading `# Recommendations`
- [ ] Ada heading `# Audit`
- [ ] Tidak ada code fences (triple backticks) di sekitar konten
- [ ] Semua konten dalam bahasa yang sama (sesuai `{output_language}`)

## Testing Parser

Untuk menguji apakah parser bisa membaca output dengan benar:

```typescript
import { parseSentimentComposition } from '@/lib/sentimentAnalysis';

const testOutput = `Sentiment Composition (Pie Chart): Positive 70%, Neutral 20%, Negative 10%

# Sentiment Summary
...`;

const result = parseSentimentComposition(testOutput);
console.log(result); 
// Should output: { positivePct: 70, neutralPct: 20, negativePct: 10 }
```

## Catatan Penting

1. **Pie Chart Line**: Harus di baris pertama output, sebelum heading apapun
2. **No Code Fences**: Jangan gunakan triple backticks (```) di sekitar konten markdown
3. **Language Consistency**: Semua konten harus dalam bahasa yang sama sesuai `{output_language}`
4. **Heading Consistency**: Gunakan format markdown standar (# untuk H1, ## untuk H2)
5. **Risk Severity**: Setiap risiko harus diklasifikasikan sebagai Low, Medium, atau High
