#!/usr/bin/env python3
"""
Initialize PostgreSQL Database Schema for Chat History
Creates tables: conversations and messages
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
    """Create database schema for chat history."""
    print("=" * 60)
    print("BAGANA AI - Chat History Database Schema Initialization")
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
        
        # Create conversations table
        print("Creating conversations table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id VARCHAR(255) PRIMARY KEY,
                title VARCHAR(500) NOT NULL DEFAULT 'New Chat',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("[OK] Conversations table created/verified")
        
        # Create messages table
        print("Creating messages table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id VARCHAR(255) PRIMARY KEY,
                conversation_id VARCHAR(255) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
                content JSONB NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
        """)
        print("[OK] Messages table created/verified")
        
        # Create indexes for better query performance
        print("Creating indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
            ON messages(conversation_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_updated_at 
            ON conversations(updated_at DESC);
        """)
        print("[OK] Indexes created/verified")
        
        # Create trigger to update updated_at automatically
        print("Creating trigger for updated_at...")
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
            DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
            CREATE TRIGGER update_conversations_updated_at
            BEFORE UPDATE ON conversations
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
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
            AND table_name IN ('conversations', 'messages')
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
