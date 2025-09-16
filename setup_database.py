#!/usr/bin/env python3
"""
Database setup script for InlinkAI
Run this script to initialize PostgreSQL database with sample data
"""

import os
import sys
from flask import Flask
from config import Config
from models import db
from database import create_tables, seed_sample_data

def setup_database():
    """Setup database with tables and sample data"""
    
    print("🚀 Setting up InlinkAI Database...")
    print("=" * 50)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Test database connection
            print("📡 Testing database connection...")
            with db.engine.connect() as connection:
                connection.execute(db.text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Create tables
            print("🗄️  Creating database tables...")
            create_tables()
            print("✅ Database tables created!")
            
            # Seed sample data
            print("🌱 Creating sample data...")
            seed_sample_data()
            print("✅ Sample data created!")
            
            print("\n" + "=" * 50)
            print("🎉 Database setup completed successfully!")
            print("\nSample users created:")
            print("- john.doe@example.com")
            print("- sarah.smith@company.com") 
            print("- mike.johnson@startup.io")
            print("- lisa.brown@agency.com")
            print("- david.wilson@freelance.com")
            print("\nYou can now login with any of these emails using any 6-digit OTP.")
            print("\n🚀 Start the application with: python app.py")
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure PostgreSQL is running")
            print("2. Check database credentials in config.py")
            print("3. Ensure database 'inlinkai' exists")
            print("4. Run: createdb inlinkai")
            return False
    
    return True

def create_database():
    """Create the PostgreSQL database if it doesn't exist"""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host='localhost',
            user='postgres',
            password='postgres',
            port=5432
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'inlinkai'")
        exists = cursor.fetchone()
        
        if not exists:
            print("📦 Creating database 'inlinkai'...")
            cursor.execute('CREATE DATABASE inlinkai')
            print("✅ Database 'inlinkai' created successfully!")
        else:
            print("✅ Database 'inlinkai' already exists!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. User 'postgres' exists with password 'postgres'")
        print("3. You have permission to create databases")
        return False

if __name__ == '__main__':
    print("🔧 InlinkAI Database Setup")
    print("=" * 30)
    
    # First create the database
    if create_database():
        # Then setup tables and data
        setup_database()
    else:
        sys.exit(1)
