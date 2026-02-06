/**
 * Test OpenRouter API key manually (baca dari .env).
 * Jalankan: node scripts/validate-openrouter-key.mjs
 * Dari folder root project (yang ada package.json dan .env).
 */
import { readFileSync, existsSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const envPath = join(root, ".env");

/** Bersihkan key seperti backend: hapus semua spasi/newline/kutip (sering bikin 401). */
function cleanKey(val) {
  if (!val || typeof val !== "string") return "";
  return val.replace(/\s/g, "").replace(/^["']|["']$/g, "").trim();
}

function loadKey() {
  if (!existsSync(envPath)) {
    console.error("File .env tidak ditemukan. Copy env.example ke .env lalu isi OPENROUTER_API_KEY.");
    process.exit(1);
  }
  const content = readFileSync(envPath, "utf-8").replace(/\r\n/g, "\n");
  for (const line of content.split("\n")) {
    const m = line.match(/^\s*OPENROUTER_API_KEY\s*=\s*(.+)$/);
    if (m) {
      const val = cleanKey(m[1].split("#")[0]);
      if (val && val !== "your-openrouter-api-key-here" && !val.startsWith("sk-or-v1-xxx")) return val;
      break;
    }
  }
  const m2 = content.match(/OPENAI_API_KEY\s*=\s*([^\n#]+)/m);
  if (m2) {
    const val = cleanKey(m2[1]);
    if (val && !val.startsWith("your-") && val.length > 20) return val;
  }
  console.error("OPENROUTER_API_KEY tidak di-set di .env atau masih placeholder.");
  process.exit(1);
}

async function main() {
  let key = loadKey();
  key = cleanKey(key);
  if (!key || key.length < 25) {
    console.error("Key terlalu pendek atau kosong setelah dibersihkan. Pastikan .env berisi OPENROUTER_API_KEY=sk-or-v1-... (copy utuh).");
    process.exit(1);
  }
  console.log("Mengecek API key di OpenRouter...");
  try {
    const res = await fetch("https://openrouter.ai/api/v1/models", {
      method: "GET",
      headers: { Authorization: `Bearer ${key}` },
    });
    if (res.status === 401) {
      console.error("❌ Key ditolak (401). Langkah:");
      console.error("   1. Buka https://openrouter.ai/settings/keys → Create Key (atau pakai key yang masih aktif)");
      console.error("   2. Copy key utuh (sk-or-v1-...). Di .env tulis satu baris: OPENROUTER_API_KEY=sk-or-v1-... (tanpa spasi/kutip di nilai)");
      console.error("   3. Simpan .env, lalu jalankan lagi: npm run validate-key");
      console.error("   4. Jika sudah OK, restart: npm run dev");
      process.exit(1);
    }
    if (!res.ok) {
      console.error(`❌ OpenRouter mengembalikan ${res.status}`);
      process.exit(1);
    }
    console.log("✅ API key valid. OpenRouter siap dipakai.");
  } catch (e) {
    console.error("❌ Gagal:", e.message);
    process.exit(1);
  }
}

main();
