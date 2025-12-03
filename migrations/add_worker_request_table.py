"""
Migration script to add worker_request table to SQLite database
Run this with: python migrations/add_worker_request_table.py
"""

import sqlite3
from pathlib import Path

# Path to your SQLite database
DB_PATH = Path(__file__).parent.parent / "test.db"

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create worker_request table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker_request (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                cafe_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (cafe_id) REFERENCES cafe(id) ON DELETE CASCADE,
                UNIQUE(user_id, cafe_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_worker_request_cafe_status 
            ON worker_request(cafe_id, status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_worker_request_user 
            ON worker_request(user_id)
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   - Created worker_request table")
        print("   - Created indexes")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Running migration: add_worker_request_table")
    run_migration()
