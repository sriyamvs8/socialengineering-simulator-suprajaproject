from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "teady-secret-key-change-me"  # change this before real deployment

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=["GET"])
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user"] = user["email"]

            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = get_db()
            # store previous last_login before overwriting, to show on dashboard
            prev_login = conn.execute(
                "SELECT last_login FROM users WHERE email = ?", (email,)
            ).fetchone()["last_login"]
            session["previous_login"] = prev_login

            conn.execute(
                "UPDATE users SET last_login = ? WHERE email = ?",
                (login_time, email),
            )
            conn.execute(
                "INSERT INTO login_history (email, login_time) VALUES (?, ?)",
                (email, login_time),
            )
            conn.commit()
            conn.close()

            session["login_time"] = login_time
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template("dashboard.html", email=session["user"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("database.db not found. Run init_db.py first to create and seed it.")
    app.run(debug=True)
