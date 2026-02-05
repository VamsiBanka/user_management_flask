from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
print("DB_PASSWORD =", os.getenv("DB_PASSWORD"))


app = Flask(__name__)

# ================= DATABASE CONFIG =================
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# ================= DB CONNECTION =================
def get_db_connection():
    return psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )

# ================= INIT TABLE =================
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("users"))

    return render_template("register.html")

@app.route("/users")
def users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users")
    users = cur.fetchall()   # list of dicts
    cur.close()
    conn.close()

    return render_template("users.html", users=users)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_user(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        cur.execute(
            "UPDATE users SET name=%s, email=%s WHERE id=%s",
            (name, email, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("users"))

    cur.execute("SELECT id, name, email FROM users WHERE id=%s", (id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("edit.html", user=user)

@app.route("/delete/<int:id>")
def delete_user(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("users"))

# ================= RUN =================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
