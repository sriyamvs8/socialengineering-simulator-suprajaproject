import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check if password column exists
cur.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cur.fetchall()]

if "password" not in columns:
    cur.execute("ALTER TABLE users ADD COLUMN password TEXT")
    print("Password column added.")
else:
    print("Password column already exists.")

# Demo passwords
passwords = {
    "kumarvijay99777mk@gmail.com": "vijjuuuuuu",
    "sanjanamarkala24@gmail.com": "Sanjana@123",
    "Satishdudala541@gmail.com": "Moon!Tiger47River#",
    "pawarbhavani04@gmail.com": "Bhav@#04125"
}

for email, pwd in passwords.items():
    cur.execute(
        "UPDATE users SET password=? WHERE email=?",
        (pwd, email)
    )

conn.commit()
conn.close()

print("Database updated successfully.")