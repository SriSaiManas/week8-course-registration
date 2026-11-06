from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
import re

app = Flask(__name__)
app.secret_key = "course-registration-demo"
DB = Path(__file__).with_name("registrations.db")
COURSES = ["Python Programming", "Web Development", "Data Structures",
           "Machine Learning", "Cloud Computing"]

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def initialize():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL, roll_no TEXT NOT NULL,
            email TEXT NOT NULL, course TEXT NOT NULL,
            UNIQUE(roll_no, course))""")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("student_name", "").strip()
        roll = request.form.get("roll_no", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()
        if not all([name, roll, email, course]):
            flash("Please complete every field.")
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.")
        elif course not in COURSES:
            flash("Select a valid course.")
        else:
            try:
                with connect() as db:
                    db.execute("""INSERT INTO registrations
                        (student_name, roll_no, email, course) VALUES (?,?,?,?)""",
                        (name, roll, email, course))
                flash("Course registration completed.")
            except sqlite3.IntegrityError:
                flash("This student is already registered for this course.")
        return redirect(url_for("index"))
    with connect() as db:
        registrations = db.execute("SELECT * FROM registrations ORDER BY id DESC").fetchall()
    return render_template("index.html", courses=COURSES, registrations=registrations)

if __name__ == "__main__":
    initialize()
    app.run(debug=True)
