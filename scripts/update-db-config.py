"""
Script untuk menambahkan/mengupdate konfigurasi database PostgreSQL di .env
"""
import os
import sys
from pathlib import Path
import re

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

# Database configuration yang akan ditambahkan
DB_CONFIG = {
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "5432",
    "DB_NAME": "bagana-ai-cp",
    "DB_USER": "postgres",
    "DB_PASSWORD": "123456"
}

def update_env_file(env_path: Path):
    """Update atau tambahkan konfigurasi database di file .env"""
    
    # Baca file .env jika ada
    lines = []
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error membaca file .env: {e}")
            return False
    else:
        print(f"File .env tidak ditemukan di {env_path}")
        print("Membuat file .env baru...")
    
    # Cari apakah sudah ada konfigurasi database
    db_section_start = -1
    db_vars = {}
    new_lines = []
    
    for i, line in enumerate(lines):
        # Cek apakah ini bagian PostgreSQL Database Configuration
        if "PostgreSQL Database Configuration" in line or "PostgreSQL" in line and "Database" in line:
            db_section_start = i
            new_lines.append(line)
            continue
        
        # Cek apakah ini variabel database
        for db_var in DB_CONFIG.keys():
            if line.strip().startswith(f"{db_var}="):
                db_vars[db_var] = i
                # Update nilai jika sudah ada
                new_lines.append(f"{db_var}={DB_CONFIG[db_var]}\n")
                break
        else:
            # Bukan variabel database, tambahkan line asli
            if not any(line.strip().startswith(f"{db_var}=") for db_var in DB_CONFIG.keys()):
                new_lines.append(line)
    
    # Jika belum ada section database, tambahkan di akhir
    if db_section_start == -1:
        # Cari posisi yang tepat (setelah komentar terakhir atau di akhir file)
        insert_pos = len(new_lines)
        
        # Cari komentar terakhir atau baris kosong terakhir
        for i in range(len(new_lines) - 1, -1, -1):
            if new_lines[i].strip().startswith("#") or new_lines[i].strip() == "":
                insert_pos = i + 1
                break
        
        # Tambahkan section database
        if insert_pos > 0 and not new_lines[insert_pos - 1].endswith("\n"):
            new_lines.insert(insert_pos, "\n")
            insert_pos += 1
        
        new_lines.insert(insert_pos, "\n# PostgreSQL Database Configuration (for chat history)\n")
        insert_pos += 1
        
        for db_var, db_value in DB_CONFIG.items():
            if db_var not in db_vars:
                new_lines.insert(insert_pos, f"{db_var}={db_value}\n")
                insert_pos += 1
    
    # Tulis kembali ke file
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    except Exception as e:
        print(f"Error menulis file .env: {e}")
        return False

def main():
    """Main function"""
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"
    
    print("=" * 60)
    print("Update Konfigurasi Database PostgreSQL di .env")
    print("=" * 60)
    print()
    
    print(f"File .env: {env_path}")
    print()
    
    print("Konfigurasi yang akan ditambahkan/diupdate:")
    for key, value in DB_CONFIG.items():
        if key == "DB_PASSWORD":
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")
    print()
    
    if update_env_file(env_path):
        print("[OK] Konfigurasi database berhasil diupdate di .env")
        print()
        print("Catatan: Pastikan PostgreSQL sudah berjalan dan database 'bagana-ai-cp' sudah dibuat.")
        print("Untuk test koneksi, jalankan: python scripts/test-db-connection.py")
    else:
        print("[ERROR] Gagal mengupdate konfigurasi database")
        sys.exit(1)

if __name__ == "__main__":
    main()
