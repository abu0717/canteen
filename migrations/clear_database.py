"""
Script to clear all records from the database for fresh testing
Run this with: python3 migrations/clear_database.py
"""

import sqlite3
from pathlib import Path

# Path to your SQLite database
DB_PATH = Path(__file__).parent.parent / "test.db"

def clear_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        
        print("🗑️  Clearing all records from database...")
        
        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Clear all tables
        for table in tables:
            table_name = table[0]
            # Use quotes to handle reserved keywords like 'order'
            cursor.execute(f'DELETE FROM "{table_name}"')
            print(f"   ✅ Cleared {table_name}")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        print("\n✅ Database cleared successfully!")
        print("   All records have been deleted. You can now test from the beginning.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to clear database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    confirmation = input("⚠️  This will delete ALL records from the database. Are you sure? (yes/no): ")
    if confirmation.lower() == 'yes':
        clear_database()
    else:
        print("❌ Operation cancelled")
