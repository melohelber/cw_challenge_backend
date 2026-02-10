#!/usr/bin/env python3
"""
Migration Script: Add sessions table and session_id FK to conversations

This script:
1. Creates sessions table
2. Adds session_id column to conversations table
3. Creates indexes for performance

Usage:
    python scripts/migrate_add_sessions.py
"""

import sys
import sqlite3
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import DATABASE_URL


def run_migration():
    """Execute the migration to add sessions"""

    # Extract database path from DATABASE_URL (format: sqlite:///path/to/db.db)
    db_path = DATABASE_URL.replace('sqlite:///', '')

    print(f"🔧 Running sessions migration on database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Step 1: Check if sessions table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='sessions'
        """)
        sessions_table_exists = cursor.fetchone() is not None

        if not sessions_table_exists:
            print("📝 Creating sessions table...")
            cursor.execute("""
                CREATE TABLE sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(36) UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at DATETIME NOT NULL,
                    last_activity_at DATETIME NOT NULL,
                    expires_at DATETIME NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX idx_sessions_session_id ON sessions(session_id)")
            cursor.execute("CREATE INDEX idx_sessions_user_id ON sessions(user_id)")
            cursor.execute("CREATE INDEX idx_sessions_created_at ON sessions(created_at)")
            cursor.execute("CREATE INDEX idx_sessions_last_activity_at ON sessions(last_activity_at)")
            cursor.execute("CREATE INDEX idx_sessions_is_active ON sessions(is_active)")

            conn.commit()
            print("✅ Sessions table created successfully")
        else:
            print("ℹ️  Sessions table already exists")

        # Step 2: Check if session_id column exists in conversations
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'session_id' not in columns:
            print("📝 Adding session_id column to conversations table...")
            cursor.execute("""
                ALTER TABLE conversations
                ADD COLUMN session_id VARCHAR(36)
            """)

            # Create index on session_id
            cursor.execute("CREATE INDEX idx_conversations_session_id ON conversations(session_id)")

            conn.commit()
            print("✅ session_id column added successfully")
        else:
            print("ℹ️  session_id column already exists")

        # Step 3: Verify migration
        cursor.execute("SELECT COUNT(*) FROM sessions")
        sessions_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM conversations WHERE session_id IS NOT NULL")
        conversations_with_session = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]

        print("\n📊 Migration Summary:")
        print(f"   Total sessions: {sessions_count}")
        print(f"   Conversations with session_id: {conversations_with_session}")
        print(f"   Total conversations: {total_conversations}")

        if conversations_with_session == 0 and total_conversations > 0:
            print("\n⚠️  Note: Existing conversations don't have session_id (this is normal)")
            print("   New conversations will be created with session_id automatically")

        print("\n✅ Migration completed successfully!")

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add sessions table")
    print("=" * 60)

    run_migration()

    print("\n" + "=" * 60)
    print("Migration completed!")
    print("=" * 60)
