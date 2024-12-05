-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    image VARCHAR(255) NOT NULL
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    session_name VARCHAR(255) NOT NULL,
    session_date DATE NOT NULL,
    UNIQUE (session_name, session_date)
);

-- Create attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    session_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Present', 'Absent') DEFAULT 'Present',
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
);

-- Create error_log table
CREATE TABLE IF NOT EXISTS error_log (
    error_id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    student_id INT,
    error_message TEXT,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE SET NULL
);
