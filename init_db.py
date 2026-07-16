"""
Run this once (python init_db.py) to create database.db and fill it with
50 sample employee accounts you can use to test the login page.

Plain-text credentials for testing are also written to credentials.txt
(passwords are stored HASHED in database.db, never in plain text there).
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS users")
cur.execute(
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        last_login TEXT
    )
    """
)

cur.execute("DROP TABLE IF EXISTS login_history")
cur.execute(
    """
    CREATE TABLE login_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        login_time TEXT NOT NULL,
        FOREIGN KEY (email) REFERENCES users(email)
    )
    """
)

credentials_lines = ["email | password", "-" * 50]

for i in range(1, 51):
    email = f"teadyuser{i:03d}@gmail.com"
    password = f"Teady@{i:03d}"          # e.g. Teady@001
    password_hash = generate_password_hash(password)

    cur.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, password_hash),
    )
    credentials_lines.append(f"{email} | {password}")

conn.commit()
conn.close()

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.txt"), "w") as f:
    f.write("\n".join(credentials_lines))

print("database.db created with 50 test users.")
print("Plain-text test credentials saved to credentials.txt")
