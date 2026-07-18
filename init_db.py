# """
# Run this once (python init_db.py) to create database.db and fill it with
# 50 sample employee accounts you can use to test the login page.

# Plain-text credentials for testing are also written to credentials.txt
# (passwords are stored HASHED in database.db, never in plain text there).
# """

# import sqlite3
# import os
# from werkzeug.security import generate_password_hash

# DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

# conn = sqlite3.connect(DB_PATH)
# cur = conn.cursor()

# cur.execute("DROP TABLE IF EXISTS users")
# cur.execute(
#     """
#     CREATE TABLE users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         email TEXT UNIQUE NOT NULL,
#         password_hash TEXT NOT NULL,
#         last_login TEXT
#     )
#     """
# )

# cur.execute("DROP TABLE IF EXISTS login_history")
# cur.execute(
#     """
#     CREATE TABLE login_history (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         email TEXT NOT NULL,
#         login_time TEXT NOT NULL,
#         FOREIGN KEY (email) REFERENCES users(email)
#     )
#     """
# )

# credentials_lines = ["email | password", "-" * 50]

# for i in range(1, 51):
#     email = f"teadyuser{i:03d}@gmail.com"
#     password = f"Teady@{i:03d}"          # e.g. Teady@001
#     password_hash = generate_password_hash(password)

#     cur.execute(
#         "INSERT INTO users (email, password_hash) VALUES (?, ?)",
#         (email, password_hash),
#     )
#     credentials_lines.append(f"{email} | {password}")

# conn.commit()
# conn.close()

# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.txt"), "w") as f:
#     f.write("\n".join(credentials_lines))

# print("database.db created with 50 test users.")
# print("Plain-text test credentials saved to credentials.txt")

"""
Run:
    python init_db.py

This recreates database.db with demo users.

Columns:
- email
- password (demo only)
- password_hash
- last_login
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# -----------------------------
# Drop old tables
# -----------------------------
cur.execute("DROP TABLE IF EXISTS login_history")
cur.execute("DROP TABLE IF EXISTS users")

# -----------------------------
# Create users table
# -----------------------------
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    password_hash TEXT NOT NULL,
    last_login TEXT
)
""")

# -----------------------------
# Create login history table
# -----------------------------
cur.execute("""
CREATE TABLE login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    login_time TEXT NOT NULL,
    FOREIGN KEY(email) REFERENCES users(email)
)
""")

# -----------------------------
# Demo Users
# -----------------------------
users = [
    ("kumarvijay99777mk@gmail.com", "vijjuuuuuu"),
    ("sanjanamarkala24@gmail.com", "Sanjana@123"),
    ("Satishdudala541@gmail.com", "Moon!Tiger47River#"),
    ("pawarbhavani04@gmail.com", "Bhav@#04125"),
]

# Add 50 demo users also
for i in range(1, 51):
    users.append(
        (
            f"teadyuser{i:03d}@gmail.com",
            f"Teady@{i:03d}"
        )
    )

credentials = []

for email, password in users:

    password_hash = generate_password_hash(password)

    cur.execute(
        """
        INSERT INTO users
        (
            email,
            password,
            password_hash,
            last_login
        )
        VALUES
        (
            ?, ?, ?, NULL
        )
        """,
        (
            email,
            password,
            password_hash
        )
    )

    credentials.append(f"{email} | {password}")

conn.commit()
conn.close()

# -----------------------------
# Save credentials
# -----------------------------
with open("credentials.txt", "w") as f:
    f.write("email | password\n")
    f.write("-"*60 + "\n")

    for line in credentials:
        f.write(line + "\n")

print("="*60)
print("Database created successfully.")
print("Users inserted :", len(users))
print("credentials.txt generated.")
print("="*60)