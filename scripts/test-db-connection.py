#!/usr/bin/env python3
"""
Test PostgreSQL Database Connection
Tests connection to local PostgreSQL database for BAGANA AI Content Planner.
"""

import psycopg2
import sys
import os
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')  # Set UTF-8 code page
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Database connection parameters
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "bagana-ai-cp",
    "user": "postgres",
    "password": "123456"
}

def test_connection():
    """Test database connection and basic operations."""
    print("=" * 60)
    print("BAGANA AI - PostgreSQL Connection Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("Connection Parameters:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User: {DB_CONFIG['user']}")
    print(f"  Password: {'*' * len(DB_CONFIG['password'])}")
    print()
    
    conn = None
    try:
        print("Attempting to connect...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("[OK] Connection successful!")
        print()
        
        # Create cursor
        cur = conn.cursor()
        
        # Test 1: Check PostgreSQL version
        print("Test 1: PostgreSQL Version")
        print("-" * 60)
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"PostgreSQL Version: {version}")
        print()
        
        # Test 2: Check current database
        print("Test 2: Current Database")
        print("-" * 60)
        cur.execute("SELECT current_database();")
        current_db = cur.fetchone()[0]
        print(f"Current Database: {current_db}")
        print()
        
        # Test 3: Check current user
        print("Test 3: Current User")
        print("-" * 60)
        cur.execute("SELECT current_user;")
        current_user = cur.fetchone()[0]
        print(f"Current User: {current_user}")
        print()
        
        # Test 4: List all tables
        print("Test 4: List All Tables")
        print("-" * 60)
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        if tables:
            print(f"Found {len(tables)} table(s):")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("No tables found in public schema.")
        print()
        
        # Test 5: Test write operation (create test table if not exists)
        print("Test 5: Write Operation Test")
        print("-" * 60)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                test_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("[OK] Test table created/verified")
        
        # Insert test record
        cur.execute("""
            INSERT INTO test_connection (test_message) 
            VALUES (%s) 
            RETURNING id, created_at;
        """, ("Connection test successful",))
        test_record = cur.fetchone()
        print(f"[OK] Test record inserted: ID={test_record[0]}, Created={test_record[1]}")
        
        # Read test record
        cur.execute("SELECT COUNT(*) FROM test_connection;")
        count = cur.fetchone()[0]
        print(f"[OK] Test records count: {count}")
        print()
        
        # Test 6: Database size
        print("Test 6: Database Size")
        print("-" * 60)
        cur.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database()));
        """)
        db_size = cur.fetchone()[0]
        print(f"Database Size: {db_size}")
        print()
        
        # Cleanup: Optionally remove test table (commented out to keep for verification)
        # cur.execute("DROP TABLE IF EXISTS test_connection;")
        # conn.commit()
        # print("✓ Test table cleaned up")
        
        cur.close()
        
        print("=" * 60)
        print("[OK] All tests passed successfully!")
        print("=" * 60)
        return True
        
    except psycopg2.OperationalError as e:
        print("[FAIL] Connection failed!")
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Ensure PostgreSQL is running")
        print("  2. Check if database 'bagana-ai-cp' exists")
        print("  3. Verify credentials (host, port, user, password)")
        print("  4. Check PostgreSQL logs for details")
        return False
        
    except psycopg2.Error as e:
        print(f"[FAIL] Database error: {e}")
        return False
        
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False
        
    finally:
        if conn:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
