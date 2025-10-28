def init_database():
    import mysql.connector
    from config import DB_CONFIG
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Create tables
    tables = [
        """
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(15),
            date_of_birth DATE,
            course VARCHAR(50),
            year INT,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS teachers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            teacher_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(15),
            department VARCHAR(50),
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS admin_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS parents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(15),
            student_id INT,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            instructor_id INT,
            credits INT,
            department VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (instructor_id) REFERENCES teachers(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS departments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            hod VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        ALTER TABLE courses
        DROP COLUMN description 
        """
    ]
    
    for table in tables:
        cursor.execute(table)
    
    # Insert sample data
    
    # Sample admin
    cursor.execute("INSERT IGNORE INTO admin_users (username, password, email) VALUES (%s, %s, %s)",
                  ('admin', 'admin123', 'admin@rec.edu')
    )    
    # Sample student
    cursor.execute("""INSERT IGNORE INTO students 
                   (student_id, name, email, phone, date_of_birth, course, year, password) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                  ('REC2023001', 'John Doe', 'john.doe@rec.edu', '9876543210', '2000-01-15', 'Computer Science', 3, 'student123'))
    
    # Sample teacher
    cursor.execute("""INSERT IGNORE INTO teachers 
                   (teacher_id, name, email, phone, department, password) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                  ('TREC001', 'Dr. Smith', 'smith@rec.edu', '9876543211', 'cse', 'teacher123'))
    # Sample parent
    cursor.execute("SELECT id FROM students WHERE student_id = 'REC2023001'")
    student = cursor.fetchone()
    if student:
        cursor.execute("""INSERT IGNORE INTO parents 
                       (name, email, phone, student_id, password) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    ('Robert Doe', 'robert.doe@email.com', '9876543212', student[0], 'parent123'))
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")