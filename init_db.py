import sqlite3
from flask import Flask

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL UNIQUE,
                       image TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
                       session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       session_name TEXT NOT NULL,
                       session_date DATE NOT NULL,
                       UNIQUE (session_name, session_date))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       student_id INTEGER NOT NULL,
                       session_id INTEGER NOT NULL,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       status TEXT DEFAULT 'Present' CHECK(status IN ('Present', 'Absent')),
                       FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                       FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS error_log (
                       error_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       student_id INTEGER,
                       error_message TEXT,
                       FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE SET NULL)''')

    conn.commit()
    conn.close()

# Initialize database tables on startup
initialize_database()

@app.route('/')
def index():
    return "Database tables initialized and app is running!"

if __name__ == '__main__':
    app.run(debug=True)
