#!/usr/bin/env python3
"""
Migration Script: Add user_key (UUID) to existing users

This script:
1. Adds user_key column to users table if it doesn't exist
2. Generates UUID for existing users that don't have one
3. Creates unique index on user_key

Usage:
    python scripts/migrate_add_user_key.py
"""

import sys
import sqlite3
import uuid
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import DATABASE_URL


def run_migration():
    """Execute the migration to add user_key to users table"""

    # Extract database path from DATABASE_URL (format: sqlite:///path/to/db.db)
    db_path = DATABASE_URL.replace('sqlite:///', '')

    print(f"🔧 Running migration on database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Step 1: Check if user_key column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'user_key' not in columns:
            print("📝 Adding user_key column to users table...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN user_key VARCHAR(36)
            """)
            conn.commit()
            print("✅ Column added successfully")
        else:
            print("ℹ️  user_key column already exists")

        # Step 2: Generate UUIDs for existing users without user_key
        cursor.execute("SELECT id, user_key FROM users WHERE user_key IS NULL OR user_key = ''")
        users_without_key = cursor.fetchall()

        if users_without_key:
            print(f"🔑 Generating UUIDs for {len(users_without_key)} existing users...")

            for user_id, _ in users_without_key:
                new_uuid = str(uuid.uuid4())
                cursor.execute(
                    "UPDATE users SET user_key = ? WHERE id = ?",
                    (new_uuid, user_id)
                )
                print(f"   User ID {user_id} → UUID: {new_uuid[:8]}***")

            conn.commit()
            print("✅ UUIDs generated successfully")
        else:
            print("ℹ️  All users already have user_key")

        # Step 3: Create unique index on user_key if it doesn't exist
        cursor.execute("PRAGMA index_list(users)")
        indexes = [index[1] for index in cursor.fetchall()]

        if 'idx_users_user_key' not in indexes:
            print("📊 Creating unique index on user_key...")
            cursor.execute("""
                CREATE UNIQUE INDEX idx_users_user_key
                ON users(user_key)
            """)
            conn.commit()
            print("✅ Index created successfully")
        else:
            print("ℹ️  Index on user_key already exists")

        # Step 4: Verify migration
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_key IS NULL OR user_key = ''")
        null_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users")
        total_count = cursor.fetchone()[0]

        print("\n📊 Migration Summary:")
        print(f"   Total users: {total_count}")
        print(f"   Users with user_key: {total_count - null_count}")
        print(f"   Users without user_key: {null_count}")

        if null_count == 0:
            print("\n✅ Migration completed successfully! All users have UUID keys.")
        else:
            print(f"\n⚠️  Warning: {null_count} users still don't have user_key")

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add user_key (UUID) to users table")
    print("=" * 60)

    run_migration()

    print("\n" + "=" * 60)
    print("Migration completed!")
    print("=" * 60)
