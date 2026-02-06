#!/usr/bin/env python3
"""
Initialize PostgreSQL Database Schema for Market Trends
Creates table: market_trends (results from trend_researcher agent, by brand_name).
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

def init_schema():
    """Create database schema for market trends."""
    print("=" * 60)
    print("BAGANA AI - Market Trends Database Schema Initialization")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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

        # market_trends: id, brand_name, full_output, conversation_id, created_at
        print("Creating market_trends table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS market_trends (
                id VARCHAR(255) PRIMARY KEY,
                brand_name VARCHAR(255) NOT NULL,
                full_output TEXT,
                conversation_id VARCHAR(255),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("[OK] market_trends table created/verified")

        print("Creating indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_trends_brand_name
            ON market_trends(brand_name);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_trends_created_at
            ON market_trends(created_at DESC);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_trends_conversation_id
            ON market_trends(conversation_id);
        """)
        print("[OK] Indexes created/verified")

        conn.commit()
        print()
        print("=" * 60)
        print("[OK] Market trends schema initialized successfully!")
        print("=" * 60)

        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'market_trends';
        """)
        if cur.fetchone():
            print("Table: market_trends")
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
    success = init_schema()
    sys.exit(0 if success else 1)
