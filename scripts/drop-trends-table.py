#!/usr/bin/env python3
"""
Drop market_trends table from PostgreSQL database.
WARNING: This will delete all data in the table!
"""

import psycopg2
import sys
import os
from datetime import datetime

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "bagana-ai-cp"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456")
}

def drop_table():
    """Drop market_trends table and its indexes."""
    print("=" * 60)
    print("BAGANA AI - Drop market_trends Table")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("WARNING: This will delete all data in market_trends table!")
    print()
    print("Connection Parameters:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User: {DB_CONFIG['user']}")
    print()

    conn = None
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("[OK] Connected successfully!")
        print()

        cur = conn.cursor()

        # Drop indexes first
        print("Dropping indexes...")
        cur.execute("DROP INDEX IF EXISTS idx_market_trends_brand_name;")
        cur.execute("DROP INDEX IF EXISTS idx_market_trends_created_at;")
        cur.execute("DROP INDEX IF EXISTS idx_market_trends_conversation_id;")
        print("[OK] Indexes dropped")

        # Drop table
        print("Dropping market_trends table...")
        cur.execute("DROP TABLE IF EXISTS market_trends CASCADE;")
        print("[OK] market_trends table dropped")

        conn.commit()
        print()
        print("=" * 60)
        print("[OK] Table dropped successfully!")
        print("=" * 60)

        cur.close()
        return True

    except psycopg2.OperationalError as e:
        print("[FAIL] Connection failed!")
        print(f"Error: {e}")
        return False
    except psycopg2.Error as e:
        print(f"[FAIL] Database error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    success = drop_table()
    sys.exit(0 if success else 1)
