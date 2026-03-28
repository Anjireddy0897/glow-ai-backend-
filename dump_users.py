import sqlite3
import os

db_path = r"c:\facecream\database.db"
if not os.path.exists(db_path):
    print("DB does not exist!")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print(f"{'ID':<5} | {'Email':<25} | {'FullName':<20} | {'Age':<5}")
print("-" * 65)

cursor.execute("SELECT id, email, full_name, age FROM users ORDER BY id DESC LIMIT 5")
for row in cursor.fetchall():
    print(f"{row['id']:<5} | {row['email']:<25} | {row['full_name']:<20} | {row['age']:<5}")

conn.close()
