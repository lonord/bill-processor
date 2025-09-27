#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bill Processor Database Setup Script
Create SQLite database and BILL table
"""

import sqlite3
import os
from datetime import datetime

def create_billing_database(db_path="billing.sqlite"):
    """
    Create billing database and BILL table
    
    Args:
        db_path (str): Database file path, defaults to "billing.sqlite"
    
    Returns:
        bool: Returns True if creation successful, False if failed
    """
    
    try:
        # If database file already exists, ask whether to overwrite
        if os.path.exists(db_path):
            print(f"Database file {db_path} already exists")
            response = input("Do you want to recreate the database? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Operation cancelled")
                return False
            os.remove(db_path)
            print(f"Deleted existing database file: {db_path}")
        
        # Connect to database (will be created automatically if not exists)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL statement to create BILL table
        create_table_sql = """
        CREATE TABLE BILL (
            ID TEXT PRIMARY KEY,                    -- Bill ID, string type, primary key
            TIME TEXT NOT NULL,                     -- Time, yyyy-MM-dd HH:mm:ss format
            AMOUNT DECIMAL(10,2) NOT NULL,          -- Amount, decimal type, max 2 decimal places
            CURRENCY TEXT NOT NULL,                 -- Currency type, string
            TYPE TEXT NOT NULL,                     -- Bill type, string (expense, transfer, etc.)
            INFO TEXT,                              -- Bill information, long string
            NOTE TEXT,                              -- Note, long string
            SOURCE TEXT NOT NULL,                   -- Bill source, string type
            UPDATE_TIME INTEGER NOT NULL            -- Record update time, Unix timestamp
        )
        """
        
        # Execute table creation statement
        cursor.execute(create_table_sql)
        conn.commit()
        
        print("=" * 60)
        print("Database and table created successfully!")
        print("=" * 60)
        print(f"Database file: {os.path.abspath(db_path)}")
        print(f"Creation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Table structure (BILL):")
        print("-" * 40)
        print("ID         - TEXT     - Primary key, unique bill identifier")
        print("TIME       - TEXT     - Time (yyyy-MM-dd HH:mm:ss format)")
        print("AMOUNT     - DECIMAL  - Amount (max 2 decimal places)")
        print("CURRENCY   - TEXT     - Currency type")
        print("TYPE       - TEXT     - Bill type")
        print("INFO       - TEXT     - Bill information")
        print("NOTE       - TEXT     - Note")
        print("SOURCE     - TEXT     - Bill source")
        print("UPDATE_TIME- INTEGER  - Record update time (Unix timestamp)")
        print("=" * 60)
        
        return True
        
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
        return False
    except Exception as e:
        print(f"Unknown error occurred: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def verify_database(db_path="billing.sqlite"):
    """
    Verify database and table structure
    
    Args:
        db_path (str): Database file path
    
    Returns:
        bool: Returns True if verification successful, False if failed
    """
    
    try:
        if not os.path.exists(db_path):
            print(f"Database file {db_path} does not exist")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='BILL'
        """)
        
        if not cursor.fetchone():
            print("BILL table does not exist")
            return False
        
        # Get table structure information
        cursor.execute("PRAGMA table_info(BILL)")
        columns = cursor.fetchall()
        
        print("Database verification successful!")
        print("Table structure information:")
        print("-" * 50)
        for col in columns:
            pk = " (Primary Key)" if col[5] else ""
            not_null = " NOT NULL" if col[3] else ""
            print(f"{col[1]:<10} - {col[2]:<15} - {not_null}{pk}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Error verifying database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function"""
    print("Bill Processor Database Setup")
    print("=" * 60)
    
    # Create database
    if create_billing_database():
        print()
        # Verify database
        verify_database()
    else:
        print("Database creation failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
