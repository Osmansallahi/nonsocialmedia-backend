#!/usr/bin/env python3
"""
Database initialization script for PostgreSQL
"""
from app import app, db
from dotenv import load_dotenv
import os

def init_database():
    """Initialize the database with tables"""
    load_dotenv()
    
    with app.app_context():
        print("Creating database tables...")
        try:
            # Drop all tables (be careful in production!)
            db.drop_all()
            print("Dropped existing tables")
            
            # Create all tables
            db.create_all()
            print("Created all tables successfully!")
            
            # Test the connection
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1"))
                print("Database connection test successful!")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

if __name__ == '__main__':
    init_database()
