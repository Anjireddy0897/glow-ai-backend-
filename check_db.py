import sqlite3
import os

db_path = r"c:\facecream\database.db"
print(f"Checking DB at: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    if ('users',) in tables:
        cursor.execute("SELECT count(*) FROM users;")
        print(f"User count: {cursor.fetchone()[0]}")
    
    if ('skin_surveys',) in tables:
        cursor.execute("SELECT count(*) FROM skin_surveys;")
        print(f"Survey count: {cursor.fetchone()[0]}")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
