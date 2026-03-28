#!/usr/bin/env python3
"""
Test MySQL database connection
Tests connection to the 'glow' database in XAMPP
"""

import sys

try:
    import MySQLdb
except ImportError:
    print("[ERROR] MySQLdb not installed. Try: pip install mysqlclient")
    sys.exit(1)

# Database configuration (from app.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',  # empty password for XAMPP root user
    'db': 'antireddy',
    'port': 3306,
}

def test_connection():
    """Test MySQL database connection"""
    print("=" * 60)
    print("TESTING MYSQL DATABASE CONNECTION")
    print("=" * 60)
    print(f"\nConnection Details:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  User: {DB_CONFIG['user']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['db']}")
    print(f"  Password: {'(empty)' if not DB_CONFIG['passwd'] else '(set)'}")
    
    try:
        print("\n[1] Connecting to MySQL server...")
        conn = MySQLdb.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            passwd=DB_CONFIG['passwd'],
            port=DB_CONFIG['port'],
            db=DB_CONFIG['db']
        )
        print("✓ Connection successful!")
        
        cursor = conn.cursor()
        
        # Get database info
        print("\n[2] Checking database info...")
        cursor.execute("SELECT DATABASE();")
        current_db = cursor.fetchone()[0]
        print(f"✓ Current database: {current_db}")
        
        # Get MySQL version
        print("\n[3] Getting MySQL version...")
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()[0]
        print(f"✓ MySQL version: {version}")
        
        # List all tables
        print("\n[4] Listing tables...")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        if tables:
            print(f"✓ Found {len(tables)} table(s):")
            for table in tables:
                print(f"  - {table[0]}")
                # Get row count for each table
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                row_count = cursor.fetchone()[0]
                print(f"    Rows: {row_count}")
        else:
            print("✗ No tables found in database")
        
        # Get server status
        print("\n[5] Server status...")
        cursor.execute("SHOW STATUS LIKE 'Threads_%';")
        statuses = cursor.fetchall()
        for status in statuses:
            print(f"  {status[0]}: {status[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - DATABASE CONNECTION OK")
        print("=" * 60)
        return True
        
    except MySQLdb.OperationalError as e:
        print(f"\n✗ CONNECTION ERROR: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Check if XAMPP MySQL is running")
        print("  2. Verify database 'glow' exists")
        print("  3. Check if port 3306 is correct")
        print("  4. Verify root password (usually empty for XAMPP)")
        return False
        
    except MySQLdb.DatabaseError as e:
        print(f"\n✗ DATABASE ERROR: {e}")
        return False
        
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
