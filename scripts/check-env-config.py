"""
Script untuk memeriksa konfigurasi .env untuk CrewAI
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
        os.system('chcp 65001 >nul 2>&1')
    except Exception:
        pass

# Load .env dari project root
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")

print("=" * 50)
print("KONFIGURASI .ENV UNTUK CREWAI")
print("=" * 50)
print()

# AAMAD Adapter
aamad_adapter = os.getenv("AAMAD_ADAPTER", "TIDAK DIISI")
print(f"AAMAD_ADAPTER: {aamad_adapter}")

# API Keys
or_key = os.getenv("OPENROUTER_API_KEY", "").strip()
oa_key = os.getenv("OPENAI_API_KEY", "").strip()

print(f"\nOPENROUTER_API_KEY: {'DIISI' if or_key else 'TIDAK DIISI'}", end="")
if or_key:
    print(f" (panjang: {len(or_key)}, prefix: {or_key[:10]}...)")
else:
    print()

print(f"OPENAI_API_KEY: {'DIISI' if oa_key else 'TIDAK DIISI'}", end="")
if oa_key:
    print(f" (panjang: {len(oa_key)}, prefix: {oa_key[:10]}...)")
else:
    print()

# Base URL dan Model
base_url = os.getenv("OPENAI_BASE_URL", "TIDAK DIISI")
model = os.getenv("OPENAI_MODEL", "TIDAK DIISI")
print(f"\nOPENAI_BASE_URL: {base_url}")
print(f"OPENAI_MODEL: {model}")

# Optional settings
storage_dir = os.getenv("CREWAI_STORAGE_DIR", "")
print(f"CREWAI_STORAGE_DIR: {storage_dir if storage_dir else 'TIDAK DIISI (opsional)'}")

# Database config (untuk chat history)
print(f"\nDB_HOST: {os.getenv('DB_HOST', 'TIDAK DIISI')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'TIDAK DIISI')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'TIDAK DIISI')}")
print(f"DB_USER: {os.getenv('DB_USER', 'TIDAK DIISI')}")
print(f"DB_PASSWORD: {'DIISI' if os.getenv('DB_PASSWORD') else 'TIDAK DIISI'}")

print("\n" + "=" * 50)
print("VALIDASI")
print("=" * 50)

# Validasi OpenRouter key
has_or = or_key and len(or_key) > 20 and or_key.startswith("sk-or-v1-")
print(f"OpenRouter key valid: {has_or}")

# Validasi OpenAI key
has_oa = oa_key and len(oa_key) > 20 and (
    oa_key.startswith("sk-") or oa_key.startswith("sk-proj-")
)
print(f"OpenAI key valid: {has_oa}")

# Status keseluruhan
if has_or or has_oa:
    provider = "OpenRouter" if has_or else "OpenAI"
    print(f"\n[OK] Status: OK - Menggunakan {provider}")
    if has_or:
        print(f"  -> Model akan menggunakan: {model}")
        print(f"  -> Base URL: {base_url}")
else:
    print("\n[ERROR] Status: ERROR - Perlu API key yang valid")
    print("  -> Buat key di https://openrouter.ai/settings/keys")
    print("  -> Atau gunakan OpenAI API key")
    print("  -> Isi di .env sebagai OPENROUTER_API_KEY atau OPENAI_API_KEY")

# Cek apakah base URL sesuai dengan provider
if has_or and "openrouter.ai" not in base_url.lower():
    print("\n[WARNING] OpenRouter key terdeteksi tapi base URL bukan OpenRouter")
elif has_oa and not has_or and "openai.com" not in base_url.lower():
    print("\n[WARNING] OpenAI key terdeteksi tapi base URL bukan OpenAI")

print()
