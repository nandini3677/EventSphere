from flask import Flask, request, jsonify, render_template
import mysql.connector
import re
from datetime import datetime

app = Flask(__name__)

# ---------------- MySQL Connection ----------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="27042004",
        database="contactUs"
    )

# ---------------- Create Table if not exists ----------------
def create_table():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquiries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        phone VARCHAR(20),
        event_type VARCHAR(50) NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    db.commit()
    cursor.close()
    db.close()

create_table()


# ---------------- Route to serve frontend ----------------
@app.route("/")
def index():
    return render_template("contact.html")   # your HTML page


# ---------------- API to handle form ----------------
@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()

        full_name = data.get("full_name", "").strip()
        email = data.get("email", "").strip().lower()
        phone = data.get("phone", "").strip()
        event_type = data.get("event_type", "").strip()
        message = data.get("message", "").strip()

        # ---- Basic Validations ----
        if not full_name or not email or not event_type or not message:
            return jsonify({"success": False, "message": "❌ Missing required fields"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"success": False, "message": "❌ Invalid email format"}), 400

        if phone and not re.match(r"^\+?[0-9]{7,15}$", phone):
            return jsonify({"success": False, "message": "❌ Invalid phone number"}), 400

        # ---- Insert into DB ----
        db = get_db_connection()
        cursor = db.cursor()

        try:
            sql = "INSERT INTO inquiries (full_name, email, phone, event_type, message) VALUES (%s, %s, %s, %s, %s)"
            values = (full_name, email, phone, event_type, message)
            cursor.execute(sql, values)
            db.commit()
        except mysql.connector.IntegrityError:
            return jsonify({"success": False, "message": "⚠️ This email already submitted an inquiry."}), 400
        finally:
            cursor.close()
            db.close()

        # ---- Log entry (optional) ----
        with open("submissions.log", "a") as log_file:
            log_file.write(f"{datetime.now()} | {full_name} | {email} | {event_type}\n")

        return jsonify({"success": True, "message": "✅ Inquiry submitted successfully!"})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"success": False, "message": "❌ Server error"}), 500


# ---------------- Admin route to view inquiries ----------------
@app.route("/admin/inquiries")
def view_inquiries():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inquiries ORDER BY created_at DESC")
        inquiries = cursor.fetchall()
        cursor.close()
        db.close()

        return render_template("admin.html", inquiries=inquiries)

    except Exception as e:
        return f"<h2>Error loading inquiries: {str(e)}</h2>"


if __name__ == "__main__":
    app.run(debug=True)
