#!/usr/bin/env python3
"""
Initialize PostgreSQL Database Schema for Market Trends (New Structure)
Creates table: market_trends with structured columns matching CrewAI trend_researcher output.
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
    """Create database schema for market trends with structured columns."""
    print("=" * 60)
    print("BAGANA AI - Market Trends Database Schema Initialization (New Structure)")
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

        # Check if PostgreSQL version supports JSONB
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"PostgreSQL version: {version}")
        print()

        # market_trends: structured columns matching CrewAI output
        print("Creating market_trends table with new structure...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS market_trends (
                id VARCHAR(255) PRIMARY KEY,
                brand_name VARCHAR(255) NOT NULL,
                conversation_id VARCHAR(255),
                
                -- Structured data from CrewAI output
                key_market_trends JSONB,
                summary_bar_chart_data JSONB,
                trend_line_chart_data JSONB,
                creator_economy_insights TEXT,
                competitive_landscape TEXT,
                content_format_trends TEXT,
                timing_seasonality TEXT,
                implications_strategy TEXT,
                recommendations TEXT,
                sources TEXT,
                audit TEXT,
                
                -- Full output for backward compatibility and parsing
                full_output TEXT,
                
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("[OK] market_trends table created/verified")
        print()
        print("Table structure:")
        print("  - id: Primary key")
        print("  - brand_name: Brand name")
        print("  - conversation_id: Link to conversation")
        print("  - key_market_trends: JSONB array of trend objects")
        print("  - summary_bar_chart_data: JSONB array [{name, value}]")
        print("  - trend_line_chart_data: JSONB array [{name, data: [{period, value}]}]")
        print("  - creator_economy_insights: TEXT")
        print("  - competitive_landscape: TEXT")
        print("  - content_format_trends: TEXT")
        print("  - timing_seasonality: TEXT")
        print("  - implications_strategy: TEXT")
        print("  - recommendations: TEXT")
        print("  - sources: TEXT")
        print("  - audit: TEXT")
        print("  - full_output: Complete markdown output (backward compatibility)")
        print("  - created_at: Timestamp")

        print()
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
        # JSONB indexes for querying structured data
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_trends_summary_bar
            ON market_trends USING GIN (summary_bar_chart_data);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_trends_trend_lines
            ON market_trends USING GIN (trend_line_chart_data);
        """)
        print("[OK] Indexes created/verified")

        conn.commit()
        print()
        print("=" * 60)
        print("[OK] Market trends schema initialized successfully!")
        print("=" * 60)

        # Verify table exists
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'market_trends'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        if columns:
            print()
            print("Table columns:")
            for col_name, col_type in columns:
                print(f"  - {col_name}: {col_type}")
        
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
