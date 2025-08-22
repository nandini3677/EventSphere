from flask import Flask, render_template, request, jsonify
import mysql.connector

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
    name = data["name"]
    email = data["email"]
    password = data["password"]
    role = data["role"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "❌ Email already registered!"})

    # Insert new user
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (name, email, password, role)
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

    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify({
            "success": True,
            "name": user["name"],
            "role": user["role"]
        })

    return jsonify({"success": False, "message": "❌ Invalid email or password!"})

if __name__ == "__main__":
    app.run(debug=True)
