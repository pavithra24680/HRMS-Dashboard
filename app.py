from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = '46'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hrms_portal'

mysql = MySQL(app)

@app.route('/')
def reg():
    return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_password))
            mysql.connection.commit()
            cur.close()

            
            return redirect(url_for('signup_success'))
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')

    return render_template('signup.html')

@app.route('/signup_success')
def signup_success():
    return render_template('signup_success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please fill in all fields!', 'danger')
            return render_template('login.html')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", [username])
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash(f'Welcome, {user[1]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')


    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    full_name = session['username']
    name_parts = full_name.split()
    if len(name_parts) > 1:
        first_two_letters = name_parts[0][0].upper() + name_parts[1][0].upper()
    else:
        first_two_letters = full_name[:2].upper()

    return render_template('dash1.html', first_two_letters=first_two_letters)

@app.route('/attendance')
def attendance():
    
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))

    full_name = session['username']
    name_parts = full_name.split()
    if len(name_parts) > 1:
        first_two_letters = name_parts[0][0].upper() + name_parts[1][0].upper()
    else:
        first_two_letters = full_name[:2].upper()

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, employee_name, status
            FROM attendance
        """)
        attendance_records = cur.fetchall()
        cur.close()
    except Exception as e:
        flash(f'Error retrieving attendance records: {e}', 'danger')
        attendance_records = []

    return render_template('attendance.html', first_two_letters=first_two_letters, attendance_records=attendance_records)


@app.route('/add-attendance', methods=['GET', 'POST'])
def add_attendance():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        series = request.form['series']
        date = request.form['date']
        employee = request.form['employee']
        company = request.form['company']
        status = request.form['status']
        shift = request.form['shift']
        late_entry = request.form.get('late_entry')  
        early_exit = request.form.get('early_exit')  

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO attendance (series, attendance_date, employee_name, company, status, shift, late_entry, early_exit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (series, date, employee, company, status, shift, late_entry is not None, early_exit is not None))
            
            mysql.connection.commit()
            cur.close()

            flash('Attendance added successfully!', 'success')
            return redirect(url_for('add_attendance'))  
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, employee_name, status
            FROM attendance
        """)
        attendance_records = cur.fetchall()
        cur.close()
    except Exception as e:
        flash(f'Error retrieving attendance records: {e}', 'danger')
        attendance_records = []

    full_name = session['username']
    name_parts = full_name.split()
    if len(name_parts) > 1:
        first_two_letters = name_parts[0][0].upper() + name_parts[1][0].upper()
    else:
        first_two_letters = full_name[:2].upper()

    return render_template('add_attendance.html', first_two_letters=first_two_letters, attendance_records=attendance_records)

@app.route('/leave')
def leave():
    
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))

    full_name = session['username']
    name_parts = full_name.split()
    if len(name_parts) > 1:
        first_two_letters = name_parts[0][0].upper() + name_parts[1][0].upper()
    else:
        first_two_letters = full_name[:2].upper()

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, employee_name, leave_type, status 
            FROM leave_applications
        """)
        leave_records = cur.fetchall()
        cur.close()
    except Exception as e:
        flash(f'Error retrieving leave applications: {e}', 'danger')
        leave_records = []

    return render_template('leave.html', first_two_letters=first_two_letters, leave_records=leave_records)

@app.route('/leave_applications', methods=['GET', 'POST'])
def leave_application():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))

    full_name = session['username']
    name_parts = full_name.split()
    if len(name_parts) > 1:
        first_two_letters = name_parts[0][0].upper() + name_parts[1][0].upper()
    else:
        first_two_letters = full_name[:2].upper()

    if request.method == 'POST':
        # Fetch form data
        series = request.form['series']
        leave_type = request.form['leaveType']
        employee = request.form['employee']
        company = request.form['company']
        from_date = request.form['date']
        to_date = request.form['date']
        reason = request.form['reason']
        half_day = request.form.get('half_day') is not None
        approval = request.form['approval']
        posting_date = request.form['date']
        follow_via_email = request.form.get('late_entry') is not None
        status = request.form['status']
        salary_slip = request.form['salaryslip']
        letterhead = request.form['letterhead']
        color = request.form['colorPicker']

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO leave_applications (
                    series, leave_type, employee_name, company_name, from_date, to_date, 
                    reason, is_half_day, approval_status, posting_date, follow_via_email, 
                    status, salary_slip, letterhead, color_code
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                series, leave_type, employee, company, from_date, to_date, reason,
                half_day, approval, posting_date, follow_via_email, status, salary_slip,
                letterhead, color
            ))
            mysql.connection.commit()
            cur.close()
 
            flash('Leave application submitted successfully!', 'success')
            return redirect(url_for('leave_application'))
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, employee_name, leave_type, status 
            FROM leave_applications
        """)
        leave_records = cur.fetchall()
        cur.close()
    except Exception as e:
        flash(f'Error retrieving leave applications: {e}', 'danger')
        leave_records = []

    return render_template('leave_applications.html', first_two_letters=first_two_letters, leave_records=leave_records)


if __name__ == '__main__':
    app.run(debug=True)
