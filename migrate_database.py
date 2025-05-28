#!/usr/bin/env python3
"""
Database migration script to add profile_picture_data column to users table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
import sqlite3

def migrate_database():
    """Add profile_picture_data column to existing users table"""
    
    with app.app_context():
        try:
            # Check if using SQLite (local development)
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            
            if db_uri.startswith('sqlite'):
                print("🔧 Migrating SQLite database...")
                
                # Get the database file path
                db_path = db_uri.replace('sqlite:///', '')
                
                # Connect to SQLite directly to add column
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if column already exists
                cursor.execute("PRAGMA table_info(users)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'profile_picture_data' not in columns:
                    print("➕ Adding profile_picture_data column...")
                    cursor.execute("ALTER TABLE users ADD COLUMN profile_picture_data TEXT")
                    conn.commit()
                    print("✓ Column added successfully")
                else:
                    print("✓ Column already exists")
                
                conn.close()
                
            else:
                print("🔧 Migrating PostgreSQL database...")
                
                # For PostgreSQL, use SQLAlchemy text() for raw SQL
                from sqlalchemy import text
                
                with db.engine.connect() as conn:
                    # Check if column exists
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = 'profile_picture_data'
                    """))
                    
                    if not result.fetchone():
                        print("➕ Adding profile_picture_data column...")
                        conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture_data TEXT"))
                        conn.commit()
                        print("✓ Column added successfully")
                    else:
                        print("✓ Column already exists")
            
            print("✅ Database migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("=== Database Migration: Add profile_picture_data column ===")
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration successful! You can now use database storage for profile pictures.")
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Test profile picture upload functionality")
        print("3. Deploy to Railway with the updated schema")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
        sys.exit(1)
