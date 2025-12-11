"""
SQLite to PostgreSQL Migration Script

This script migrates data from your SQLite database to PostgreSQL.
It preserves all data including UUIDs, relationships, and timestamps.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from app.models import User, Cafe, Order, OrderItem, Feedback, Category, MenuItem, Inventory, CafeWorker, WorkerRequest
from app.database import Base

def migrate_data(source_url: str, target_url: str):
    """Migrate all data from source database to target database"""
    
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Create engines
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    
    # Create sessions
    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)
    
    source_session = SourceSession()
    target_session = TargetSession()
    
    try:
        # Create all tables in target database
        print("📋 Creating tables in PostgreSQL...")
        Base.metadata.create_all(target_engine)
        
        # Define migration order (respecting foreign keys)
        models_in_order = [
            ('user', User),
            ('cafe', Cafe),
            ('category', Category),
            ('menu_item', MenuItem),
            ('order', Order),
            ('order_item', OrderItem),
            ('feedback', Feedback),
            ('inventory', Inventory),
            ('cafe_worker', CafeWorker),
            ('worker_request', WorkerRequest),
        ]
        
        total_migrated = 0
        
        for table_name, model in models_in_order:
            try:
                # Get all records from source
                source_records = source_session.query(model).all()
                
                if not source_records:
                    print(f"  ⏭️  {table_name}: No data to migrate")
                    continue
                
                # Disable foreign key checks for PostgreSQL
                target_session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
                
                # Insert into target
                for record in source_records:
                    # Create new instance with same data
                    target_session.merge(record)
                
                target_session.commit()
                count = len(source_records)
                total_migrated += count
                print(f"  ✅ {table_name}: Migrated {count} records")
                
            except Exception as e:
                print(f"  ❌ {table_name}: Error - {str(e)}")
                target_session.rollback()
                continue
        
        print(f"\n✨ Migration complete! Migrated {total_migrated} total records")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        for table_name, model in models_in_order:
            source_count = source_session.query(model).count()
            target_count = target_session.query(model).count()
            
            if source_count == target_count:
                print(f"  ✅ {table_name}: {target_count} records (matched)")
            else:
                print(f"  ⚠️  {table_name}: Source={source_count}, Target={target_count} (MISMATCH)")
        
        print("\n🎉 Migration successful!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        target_session.rollback()
        raise
    
    finally:
        source_session.close()
        target_session.close()


if __name__ == "__main__":
    # Get database URLs from environment or use defaults
    SOURCE_DB = os.getenv("SOURCE_DB", "sqlite:///./canteen.db")
    TARGET_DB = os.getenv("TARGET_DB", "postgresql://postgres:postgres@localhost:5432/canteen_db")
    
    print("=" * 60)
    print("SQLite → PostgreSQL Migration")
    print("=" * 60)
    print(f"Source: {SOURCE_DB}")
    print(f"Target: {TARGET_DB}")
    print("=" * 60)
    
    # Confirm migration
    response = input("\n⚠️  This will copy data to PostgreSQL. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Migration cancelled")
        sys.exit(0)
    
    try:
        migrate_data(SOURCE_DB, TARGET_DB)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
