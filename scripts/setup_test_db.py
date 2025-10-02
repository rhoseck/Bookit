"""
Database setup script for BookIt API
Run this to create the test database for development
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_test_database():
    """Create bookit_test database if it doesn't exist"""
    
    # Get credentials from environment variables
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    if not db_password:
        print("Error: DB_PASSWORD environment variable not set")
        print("Please set it with: export DB_PASSWORD=your_password")
        sys.exit(1)
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname='postgres',
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'bookit_test'")
        exists = cursor.fetchone()
        
        # Create database if it doesn't exist
        if not exists:
            print("Creating bookit_test database...")
            cursor.execute("CREATE DATABASE bookit_test")
            print("✅ Database bookit_test created successfully!")
        else:
            print("ℹ️  Database bookit_test already exists.")
        
        # Close connection
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_test_database()