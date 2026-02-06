#!/usr/bin/env python3
"""
Initialize PostgreSQL Database Schema for Content Plans
Creates tables: content_plans, plan_versions
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

def init_schema():
    """Create database schema for content plans."""
    print("=" * 60)
    print("BAGANA AI - Content Plans Database Schema Initialization")
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
        
        # Create content_plans table
        print("Creating content_plans table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS content_plans (
                id VARCHAR(255) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                campaign VARCHAR(500),
                brand_name VARCHAR(255),
                conversation_id VARCHAR(255) REFERENCES conversations(id) ON DELETE SET NULL,
                schema_valid BOOLEAN NOT NULL DEFAULT true,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("[OK] Content plans table created/verified")
        
        # Create plan_versions table
        print("Creating plan_versions table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS plan_versions (
                id VARCHAR(255) PRIMARY KEY,
                plan_id VARCHAR(255) NOT NULL REFERENCES content_plans(id) ON DELETE CASCADE,
                version VARCHAR(50) NOT NULL,
                content JSONB NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_plan_version UNIQUE(plan_id, version)
            );
        """)
        print("[OK] Plan versions table created/verified")
        
        # Create plan_talents junction table (many-to-many relationship)
        print("Creating plan_talents table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS plan_talents (
                plan_id VARCHAR(255) NOT NULL REFERENCES content_plans(id) ON DELETE CASCADE,
                talent_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (plan_id, talent_name)
            );
        """)
        print("[OK] Plan talents table created/verified")
        
        # Create indexes for better query performance
        print("Creating indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_plans_conversation_id 
            ON content_plans(conversation_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_plans_updated_at 
            ON content_plans(updated_at DESC);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_plans_brand_name 
            ON content_plans(brand_name);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_plan_versions_plan_id 
            ON plan_versions(plan_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_plan_talents_plan_id 
            ON plan_talents(plan_id);
        """)
        print("[OK] Indexes created/verified")
        
        # Create trigger to update updated_at automatically
        print("Creating trigger for updated_at...")
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_content_plans_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        cur.execute("""
            DROP TRIGGER IF EXISTS update_content_plans_updated_at ON content_plans;
            CREATE TRIGGER update_content_plans_updated_at
            BEFORE UPDATE ON content_plans
            FOR EACH ROW
            EXECUTE FUNCTION update_content_plans_updated_at();
        """)
        print("[OK] Trigger created/verified")
        
        conn.commit()
        
        print()
        print("=" * 60)
        print("[OK] Database schema initialized successfully!")
        print("=" * 60)
        
        # Verify tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('content_plans', 'plan_versions', 'plan_talents')
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        print(f"\nCreated tables: {', '.join([t[0] for t in tables])}")
        
        cur.close()
        return True
        
    except psycopg2.OperationalError as e:
        print("[FAIL] Connection failed!")
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Ensure PostgreSQL is running")
        print("  2. Check if database exists")
        print("  3. Verify credentials")
        return False
        
    except psycopg2.Error as e:
        print(f"[FAIL] Database error: {e}")
        if conn:
            conn.rollback()
        return False
        
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False
        
    finally:
        if conn:
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    success = init_schema()
    sys.exit(0 if success else 1)
