#!/usr/bin/env python3
"""
Initialize PostgreSQL Database Schema for User Authentication
Creates table: users (for login/authentication system).
"""

import psycopg2
import sys
import os
from datetime import datetime
import bcrypt

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "bagana-ai-cp"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456")
}

def init_schema():
    """Create database schema for user authentication."""
    print("=" * 60)
    print("BAGANA AI - User Authentication Database Schema Initialization")
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

        # users: id, email, username, password_hash, full_name, role, is_active, created_at, updated_at, last_login
        print("Creating users table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                role VARCHAR(50) NOT NULL DEFAULT 'user',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
        """)
        print("[OK] users table created/verified")

        print("Creating indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email
            ON users(email);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username
            ON users(username);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_is_active
            ON users(is_active);
        """)
        print("[OK] Indexes created/verified")

        # Create trigger to update updated_at timestamp
        print("Creating update trigger...")
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        cur.execute("""
            DROP TRIGGER IF EXISTS update_users_updated_at ON users;
        """)
        cur.execute("""
            CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)
        print("[OK] Update trigger created/verified")

        # Create sessions table for session management
        print("Creating sessions table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT
            );
        """)
        print("[OK] sessions table created/verified")

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id
            ON sessions(user_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_token
            ON sessions(token);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_expires_at
            ON sessions(expires_at);
        """)
        print("[OK] Session indexes created/verified")

        conn.commit()
        print()
        print("=" * 60)
        print("[OK] User authentication schema initialized successfully!")
        print("=" * 60)

        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name IN ('users', 'sessions');
        """)
        tables = cur.fetchall()
        if tables:
            print("Tables created:")
            for table in tables:
                print(f"  - {table[0]}")
        
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
