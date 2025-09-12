from flask import Flask, render_template, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates")

# === Database connection ===
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",        # change to your MySQL username
        password="lokesh@123#",  # change to your MySQL password
        database="eventdb"
    )
    return conn

@app.route("/")
def home():
    return render_template("index.html")

# === Signup Route ===
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    print("📩 Received signup data:", data) 
    name = data["name"]
    email = data["email"]
    password = data["password"]
    role = data["role"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if email already exists
    cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "❌ Email already registered!"})

    # Hash password before saving
    hashed_password = generate_password_hash(password)

    # Insert new user
    cursor.execute(
        "INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (name, email, hashed_password, role)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True, "message": f"✅ Registered as {role}!"})

# === Signin Route ===
@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return jsonify({
            "success": True,
            "name": user["name"],
            "role": user["role"]
        })

    return jsonify({"success": False, "message": "❌ Invalid email orgit  password!"})

if __name__ == "__main__":
    app.run(debug=True)
