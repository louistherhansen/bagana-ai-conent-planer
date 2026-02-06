#!/usr/bin/env python3
"""
Drop Chat History Database Tables
DANGEROUS: This will permanently delete all chat history tables and data
"""

import psycopg2
import sys
import os
from datetime import datetime

# Database connection parameters (can be overridden by env vars)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "bagana-ai-cp"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456")
}

def drop_tables():
    """Drop chat history tables from database."""
    print("=" * 60)
    print("BAGANA AI - Drop Chat History Database Tables")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("⚠️  WARNING: This will PERMANENTLY DELETE:")
    print("   - All conversations")
    print("   - All messages")
    print("   - The table structure itself")
    print()
    
    print("Connection Parameters:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User: {DB_CONFIG['user']}")
    print()
    
    # Confirmation
    confirm = input("Type 'DROP TABLES' to confirm: ")
    if confirm != "DROP TABLES":
        print("Operation cancelled.")
        return False

    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("[OK] Connected successfully!")
        print()
        
        cur = conn.cursor()
        
        # Drop messages table first (due to foreign key constraint)
        print("Dropping messages table...")
        cur.execute("DROP TABLE IF EXISTS messages CASCADE;")
        print("[OK] Messages table dropped")
        
        # Drop conversations table
        print("Dropping conversations table...")
        cur.execute("DROP TABLE IF EXISTS conversations CASCADE;")
        print("[OK] Conversations table dropped")
        
        # Drop trigger function if exists
        print("Dropping trigger function...")
        cur.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;")
        print("[OK] Trigger function dropped")
        
        # Commit changes
        conn.commit()
        print()
        print("=" * 60)
        print("[SUCCESS] All chat history tables dropped successfully!")
        print("=" * 60)
        print()
        print("To recreate tables, run: python scripts/init-chat-history-db.py")
        
        cur.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"[ERROR] Database error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = drop_tables()
    sys.exit(0 if success else 1)
