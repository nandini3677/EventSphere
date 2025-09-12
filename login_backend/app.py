from flask import Flask, request, jsonify, render_template
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="lokesh@123#",
        database="eventdb"
    )

@app.route("/")
def home():
    return render_template("signup.html")

# ------------------ SIGNUP ------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    role = data.get("role")
    password = data.get("password")
    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if role == "visitor":
            sql = """INSERT INTO visitor (name, email, mobile, event_type, event_space, password)
                     VALUES (%s,%s,%s,%s,%s,%s)"""
            values = (data["name"], data["email"], data.get("mobile"),
                      data.get("event_type"), data["event_space"], hashed_password)
        elif role == "self":
            sql = """INSERT INTO self (name,email,mobile,company,business_type,website,company_id,event_space,password)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            values = (data["name"], data["email"], data["mobile"], data["company"],
                      data["business_type"], data.get("website"), data.get("company_id"),
                      data.get("event_space"), hashed_password)
        elif role == "organizer":
            sql = """INSERT INTO organizer (name,email,mobile,company,business_type,website,company_id,event_space,password)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            values = (data["name"], data["email"], data["mobile"], data["company"],
                      data["business_type"], data.get("website"), data.get("company_id"),
                      data.get("event_space"), hashed_password)
        else:
            return jsonify({"message": "Invalid role!"}), 400
        cursor.execute(sql, values)
        conn.commit()
        return jsonify({"message": f"{role.capitalize()} registered successfully!"})
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {str(err)}"}), 500
    finally:
        cursor.close()
        conn.close()

# ------------------ SIGN-IN ------------------
@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()
    role = data.get("role")
    email = data.get("email")
    password = data.get("password")
    if role not in ["visitor","self","organizer"]:
        return jsonify({"message":"Please select a valid role!"}),400
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = f"SELECT * FROM {role} WHERE email=%s"
        cursor.execute(sql,(email,))
        user = cursor.fetchone()
        if user and check_password_hash(user["password"],password):
            return jsonify({"message":f"Welcome {user['name']}! Login successful.","role":role})
        else:
            return jsonify({"message":"Invalid email or password!"}),401
    except mysql.connector.Error as err:
        return jsonify({"message":f"Database error: {str(err)}"}),500
    finally:
        cursor.close()
        conn.close()

if __name__=="__main__":
    app.run(debug=True)
