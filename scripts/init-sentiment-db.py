#!/usr/bin/env python3
"""
Initialize PostgreSQL Database Schema for Sentiment Analysis
Creates table: sentiment_analyses (results from sentiment_analyst agent, by brand_name).
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
    """Create database schema for sentiment analyses."""
    print("=" * 60)
    print("BAGANA AI - Sentiment Analysis Database Schema Initialization")
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

        # sentiment_analyses: id, brand_name, positive_pct, negative_pct, neutral_pct, full_output, conversation_id, created_at
        print("Creating sentiment_analyses table...")
        cur.execute("""
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
        """)
        print("[OK] sentiment_analyses table created/verified")

        print("Creating indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sentiment_analyses_brand_name
            ON sentiment_analyses(brand_name);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sentiment_analyses_created_at
            ON sentiment_analyses(created_at DESC);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sentiment_analyses_conversation_id
            ON sentiment_analyses(conversation_id);
        """)
        print("[OK] Indexes created/verified")

        conn.commit()
        print()
        print("=" * 60)
        print("[OK] Sentiment analysis schema initialized successfully!")
        print("=" * 60)

        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'sentiment_analyses';
        """)
        if cur.fetchone():
            print("Table: sentiment_analyses")
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
