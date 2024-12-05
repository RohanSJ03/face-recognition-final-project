from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error, pooling
import cv2
import numpy as np
import os
import pickle
import base64

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key')

# Database connection pooling configuration
db_config = {
    'host': "localhost",
    'user': "root",
    'password': "rohan1234",
    'database': "attendance_db",
    'pool_name': "attendance_pool",
    'pool_size': 5,
    'pool_reset_session': True
}

# Initialize database connection pool
try:
    db_connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
    app.logger.info("Database connection pool created successfully.")
except Error as e:
    app.logger.error(f"Error creating MySQL connection pool: {e}")
    db_connection_pool = None

# File paths for models and known names
MODEL_DIR = 'models'
cascade_path = os.path.join(MODEL_DIR, 'haarcascade_frontalface_default.xml')
model_path = os.path.join(MODEL_DIR, 'face_model.yml')
names_path = os.path.join(MODEL_DIR, 'names.pkl')

# Load Haar cascade for face detection
if not os.path.exists(cascade_path):
    raise FileNotFoundError(f"Could not find '{cascade_path}'. Ensure it is in the '{MODEL_DIR}' directory.")
face_cascade = cv2.CascadeClassifier(cascade_path)

# Load or initialize the LBPH face recognizer
try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    if os.path.exists(model_path):
        recognizer.read(model_path)
    else:
        raise FileNotFoundError(f"Model file '{model_path}' not found. Train the model and save it.")
except AttributeError:
    raise Exception("LBPHFaceRecognizer is not available. Ensure 'opencv-contrib-python' is installed.")

# Load known names or initialize an empty dictionary
if os.path.exists(names_path):
    with open(names_path, "rb") as f:
        known_names = pickle.load(f)
else:
    known_names = {}
    with open(names_path, "wb") as f:
        pickle.dump(known_names, f)

# Helper function to add padding for Base64 data
def add_padding(base64_string):
    return base64_string + '=' * (-len(base64_string) % 4)

# Helper function for database connection
def get_db_connection():
    try:
        if db_connection_pool:
            return db_connection_pool.get_connection()
        else:
            raise ConnectionError("Database connection pool is not available.")
    except Error as e:
        app.logger.error(f"Error getting connection from pool: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    conn = get_db_connection()
    if not conn:
        return "Failed to connect to the database", 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

        cursor.execute("SELECT * FROM attendance")
        attendance_records = cursor.fetchall()
    except Error as e:
        app.logger.error(f"Database error: {e}")
        students, attendance_records = [], []
    finally:
        cursor.close()
        conn.close()

    return render_template('admin.html', students=students, attendance_records=attendance_records)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        try:
            conn = get_db_connection()
            if not conn:
                flash("Database connection failed.", "error")
                return redirect(url_for('register'))

            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name) VALUES (%s)", (name,))
            conn.commit()
            flash("Student registered successfully.", "success")
        except Error as e:
            app.logger.error(f"Database error: {e}")
            flash(f"Database error: {e}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/real_time_recognition', methods=['GET', 'POST'])
def real_time_recognition():
    if request.method == 'GET':
        return render_template('real_time_recognition.html')

    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                app.logger.error("No image provided in request.")
                return jsonify({"status": "error", "message": "No image provided."}), 400

            image_file = request.files['image']
            img_array = np.frombuffer(image_file.read(), np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if img is None:
                app.logger.error("Invalid image file received.")
                return jsonify({"status": "error", "message": "Invalid image file."}), 400

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
            app.logger.info(f"Detected faces: {faces}")

            if len(faces) == 0:
                app.logger.warning("No faces detected.")
                return jsonify({"status": "error", "message": "No faces detected."}), 400

            RECOGNITION_THRESHOLD = 150
            for (x, y, w, h) in faces:
                face_region = gray[y:y+h, x:x+w]
                id_, confidence = recognizer.predict(face_region)
                app.logger.info(f"Predicted ID: {id_}, Confidence: {confidence}")

                if confidence < RECOGNITION_THRESHOLD:
                    recognized_name = known_names.get(id_, "Unknown")

                    # Log attendance
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO attendance (student_id, name) VALUES (%s, %s)",
                        (id_, recognized_name)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()

                    app.logger.info(f"Attendance logged for {recognized_name} (ID: {id_}).")
                    return jsonify({
                        "status": "success",
                        "name": recognized_name,
                        "confidence": confidence
                    })

            return jsonify({"status": "error", "message": "Face not recognized."}), 400
        except Exception as e:
            app.logger.error(f"Error in recognition: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
        
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
