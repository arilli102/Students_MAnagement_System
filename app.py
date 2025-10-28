from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib # Import hashlib for password hashing

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2002'
app.config['MYSQL_DB'] = 'college_db'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

# Routes
@app.route('/')
def home():
    return render_template('index.html') # This should be your main landing page

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Query with the plain text password
        cursor.execute('SELECT * FROM admin_users WHERE username = %s AND password = %s', (username, password))
        admin = cursor.fetchone()
        
        if admin:
            session['loggedin'] = True
            session['admin_id'] = admin['id']
            session['username'] = admin['username']
            session['name'] = admin.get('name', admin['username']) # Use username as fallback for name
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard')) # This will now work correctly
        else:
            msg = 'Incorrect username/password!'
    
    return render_template('admin_login.html', msg=msg)

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM students WHERE student_id = %s AND password = %s', (username, password))
        student = cursor.fetchone()
        
        if student:
            session['loggedin'] = True
            session['student_id'] = student['id']
            session['username'] = student['student_id']
            session['name'] = student.get('name', student['student_id'])
            session['role'] = 'student'
            return redirect(url_for('student_dashboard'))
        else:
            msg = 'Incorrect Student ID / Password!'
    return render_template('student_login.html', msg=msg)

@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM teachers WHERE teacher_id = %s AND password = %s', (username, password))
        teacher = cursor.fetchone()
        
        if teacher:
            session['loggedin'] = True
            session['teacher_id'] = teacher['id']
            session['username'] = teacher['teacher_id']
            session['name'] = teacher.get('name', teacher['teacher_id'])
            session['role'] = 'teacher'
            return redirect(url_for('teacher_dashboard'))
        else:
            msg = 'Incorrect Teacher ID / Password!'
    return render_template('teacher_login.html', msg=msg)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT COUNT(id) AS count FROM students')
        student_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(id) AS count FROM teachers')
        teacher_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(id) AS count FROM courses')
        course_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(id) AS count FROM departments')
        department_count = cursor.fetchone()['count']

        # Fetch all students to display in the table
        cursor.execute('SELECT * FROM students ORDER BY created_at DESC')
        students = cursor.fetchall()

        # Fetch all teachers to display in the table
        cursor.execute('SELECT * FROM teachers ORDER BY created_at DESC')
        teachers = cursor.fetchall()

        # Fetch all courses to display in the table
        # We join with teachers to get the instructor's name
        cursor.execute('SELECT c.*, t.name as instructor_name FROM courses c LEFT JOIN teachers t ON c.instructor_id = t.id ORDER BY c.created_at DESC')
        courses = cursor.fetchall()
        
        # Fetch all departments to display in the table
        cursor.execute('SELECT * FROM departments ORDER BY created_at DESC')
        departments = cursor.fetchall()

        cursor.close()

        return render_template('admin_dashboard.html', 
                             username=session['username'],
                             name=session['name'],
                             student_count=student_count,
                             teacher_count=teacher_count,
                             course_count=course_count,
                             department_count=department_count,
                             students=students,
                             teachers=teachers,
                             courses=courses,
                             departments=departments)
    return redirect(url_for('admin_login'))

@app.route('/student_dashboard')
def student_dashboard():
    if 'loggedin' in session and 'student_id' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch student details
        cursor.execute('SELECT * FROM students WHERE id = %s', (session['student_id'],))
        student = cursor.fetchone()

        if not student:
            flash('Student not found!', 'danger')
            return redirect(url_for('student_login'))

        # Fetch courses for the student's department
        cursor.execute('SELECT c.*, t.name as instructor_name FROM courses c LEFT JOIN teachers t ON c.instructor_id = t.id WHERE c.department = %s', (student['course'],))
        courses = cursor.fetchall()

        # Fetch teachers from the student's department
        cursor.execute('SELECT * FROM teachers WHERE department = %s', (student['course'],))
        teachers = cursor.fetchall()

        # Placeholder data for features not yet implemented
        attendance_percentage = 85 # Placeholder
        pending_assignments = 3 # Placeholder
        current_cgpa = 8.7 # Placeholder

        return render_template('student_dashboard.html', 
                               student=student, courses=courses, teachers=teachers,
                               attendance_percentage=attendance_percentage, pending_assignments=pending_assignments,
                               current_cgpa=current_cgpa)
    return redirect(url_for('student_login'))

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'loggedin' in session and 'teacher_id' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch teacher details
        cursor.execute('SELECT *, DATE_FORMAT(created_at, "%%b %%Y") as member_since FROM teachers WHERE id = %s', (session['teacher_id'],))
        teacher = cursor.fetchone()

        if not teacher:
            flash('Teacher not found!', 'danger')
            return redirect(url_for('teacher_login'))

        # Fetch courses taught by this teacher
        cursor.execute('SELECT * FROM courses WHERE instructor_id = %s', (teacher['id'],))
        courses = cursor.fetchall()

        # Fetch total number of students in the teacher's department
        cursor.execute('SELECT COUNT(id) as count FROM students WHERE course = %s', (teacher['department'],))
        student_count = cursor.fetchone()['count']

        return render_template('teacher_dashboard.html', 
                               teacher=teacher, courses=courses, student_count=student_count)
    return redirect(url_for('teacher_login'))

@app.route('/add_student', methods=['POST'])
def add_student():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        student_id = request.form['studentId']
        name = request.form['fullName']
        email = request.form['email']
        phone = request.form['phone']
        course = request.form['department'] # Using 'department' from form as 'course' for DB
        year = request.form['year']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if student_id or email already exists
        cursor.execute('SELECT * FROM students WHERE student_id = %s OR email = %s', (student_id, email,))
        account = cursor.fetchone()

        if account:
            flash('Student with this ID or Email already exists!', 'danger')
        else:
            # Note: Storing passwords in plain text is insecure. Consider using hashing.
            cursor.execute('INSERT INTO students (student_id, name, email, phone, course, year, password) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                           (student_id, name, email, phone, course, year, password))
            mysql.connection.commit()
            flash('New student added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM students WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/update_student/<int:id>', methods=['POST'])
def update_student(id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        student_id = request.form['studentId']
        name = request.form['fullName']
        email = request.form['email']
        phone = request.form['phone']
        course = request.form['department']
        year = request.form['year']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if the new student_id or email already exists for a DIFFERENT student
        cursor.execute('SELECT * FROM students WHERE (student_id = %s OR email = %s) AND id != %s', (student_id, email, id))
        existing_student = cursor.fetchone()

        if existing_student:
            flash('Another student with this ID or Email already exists!', 'danger')
        else:
            cursor.execute('UPDATE students SET student_id = %s, name = %s, email = %s, phone = %s, course = %s, year = %s WHERE id = %s',
                           (student_id, name, email, phone, course, year, id))
            mysql.connection.commit()
            flash('Student details updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        teacher_id = request.form['teacherId']
        name = request.form['teacherName']
        email = request.form['teacherEmail']
        phone = request.form['teacherPhone']
        department = request.form['teacherDepartment']
        password = request.form['teacherPassword']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if teacher_id or email already exists
        cursor.execute('SELECT * FROM teachers WHERE teacher_id = %s OR email = %s', (teacher_id, email,))
        account = cursor.fetchone()

        if account:
            flash('Teacher with this ID or Email already exists!', 'danger')
        else:
            # Note: Storing passwords in plain text is insecure. Consider using hashing.
            cursor.execute('INSERT INTO teachers (teacher_id, name, email, phone, department, password) VALUES (%s, %s, %s, %s, %s, %s)',
                           (teacher_id, name, email, phone, department, password))
            mysql.connection.commit()
            flash('New teacher added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/update_teacher/<int:id>', methods=['POST'])
def update_teacher(id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        teacher_id = request.form['teacherId']
        name = request.form['teacherName']
        email = request.form['teacherEmail']
        phone = request.form['teacherPhone']
        department = request.form['teacherDepartment']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if the new teacher_id or email already exists for a DIFFERENT teacher
        cursor.execute('SELECT * FROM teachers WHERE (teacher_id = %s OR email = %s) AND id != %s', (teacher_id, email, id))
        existing_teacher = cursor.fetchone()

        if existing_teacher:
            flash('Another teacher with this ID or Email already exists!', 'danger')
        else:
            cursor.execute('UPDATE teachers SET teacher_id = %s, name = %s, email = %s, phone = %s, department = %s WHERE id = %s',
                           (teacher_id, name, email, phone, department, id))
            mysql.connection.commit()
            flash('Teacher details updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_teacher/<int:id>', methods=['POST'])
def delete_teacher(id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM teachers WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_course', methods=['POST'])
def add_course():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        course_code = request.form['courseCode']
        course_name = request.form['courseName']
        instructor_id = request.form['courseInstructor']
        credits = request.form['courseCredits']
        department = request.form['courseDepartment']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if course code already exists
        cursor.execute('SELECT * FROM courses WHERE code = %s', (course_code,))
        course = cursor.fetchone()

        if course:
            flash('Course with this code already exists!', 'danger')
        else:
            cursor.execute('INSERT INTO courses (code, name, instructor_id, credits, department) VALUES (%s, %s, %s, %s, %s)',
                           (course_code, course_name, instructor_id, credits, department))
            mysql.connection.commit()
            flash('New course added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/update_course/<int:id>', methods=['POST'])
def update_course(id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        course_code = request.form['courseCode']
        course_name = request.form['courseName']
        instructor_id = request.form['courseInstructor']
        credits = request.form['courseCredits']
        department = request.form['courseDepartment']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if the new course code already exists for a DIFFERENT course
        cursor.execute('SELECT * FROM courses WHERE code = %s AND id != %s', (course_code, id))
        existing_course = cursor.fetchone()

        if existing_course:
            flash('Another course with this code already exists!', 'danger')
        else:
            cursor.execute('UPDATE courses SET code = %s, name = %s, instructor_id = %s, credits = %s, department = %s WHERE id = %s',
                           (course_code, course_name, instructor_id, credits, department, id))
            mysql.connection.commit()
            flash('Course details updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_course/<int:id>', methods=['POST'])
def delete_course(id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM courses WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_department', methods=['POST'])
def add_department():
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    
    code = request.form['departmentCode']
    name = request.form['departmentName']
    hod = request.form['departmentHOD']
    description = request.form['departmentDescription']
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO departments (code, name, hod, description) VALUES (%s, %s, %s, %s)', (code, name, hod, description))
    mysql.connection.commit()
    flash('Department added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/update_department/<int:id>', methods=['POST'])
def update_department(id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        code = request.form['departmentCode']
        name = request.form['departmentName']
        hod = request.form['departmentHOD']
        description = request.form['departmentDescription']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if the new department code already exists for a DIFFERENT department
        cursor.execute('SELECT * FROM departments WHERE code = %s AND id != %s', (code, id))
        existing_department = cursor.fetchone()

        if existing_department:
            flash('Another department with this code already exists!', 'danger')
        else:
            cursor.execute('UPDATE departments SET code = %s, name = %s, hod = %s, description = %s WHERE id = %s',
                           (code, name, hod, description, id))
            mysql.connection.commit()
            flash('Department details updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_department/<int:id>', methods=['POST'])
def delete_department(id):
    if 'loggedin' not in session:
        return redirect(url_for('admin_login'))
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM departments WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/change_password', methods=['POST'])
def admin_change_password():
    if 'loggedin' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']
        admin_id = session['admin_id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT password FROM admin_users WHERE id = %s', (admin_id,))
        admin = cursor.fetchone()

        if admin and admin['password'] == current_password:
            if new_password == confirm_password:
                if len(new_password) >= 6:
                    # In a real-world app, hash the new_password before storing it
                    cursor.execute('UPDATE admin_users SET password = %s WHERE id = %s', (new_password, admin_id))
                    mysql.connection.commit()
                    flash('Password updated successfully!', 'success')
                else:
                    flash('New password must be at least 6 characters long.', 'danger')
            else:
                flash('New passwords do not match.', 'danger')
        else:
            flash('Incorrect current password.', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)