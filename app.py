from flask import Flask, render_template, request, redirect, url_for, session
from forms import StudentForm, SectionForm, LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import io
from flask import send_file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Створення бази даних
def init_db():
    conn = sqlite3.connect('sports_club.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Person (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            role TEXT NOT NULL,
            section TEXT NOT NULL,
            random_id INTEGER,
            competition BOOLEAN
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Section (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            monday TEXT,
            tuesday TEXT,
            wednesday TEXT,
            thursday TEXT,
            friday TEXT,
            saturday TEXT,
            sunday TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if 'username' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

@app.route('/')
def index():
    conn = sqlite3.connect('sports_club.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Person')
    people = cursor.fetchall()
    cursor.execute('SELECT * FROM Section')
    sections = cursor.fetchall()
    
    user_age = None
    if 'username' in session:
        cursor.execute('SELECT age FROM User WHERE name=?', (session['username'],))
        user = cursor.fetchone()
        if user:
            user_age = user[0]
    
    conn.close()
    return render_template('index.html', people=people, sections=sections, user_age=user_age)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = sqlite3.connect('sports_club.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE name=?', (form.name.data,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[4], form.password.data):
            session['username'] = user[1]
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = sqlite3.connect('sports_club.db')
        cursor = conn.cursor()
        hashed_password = generate_password_hash(form.password.data)
        cursor.execute('INSERT INTO User (name, age, role, password_hash) VALUES (?, ?, ?, ?)',
                       (form.name.data, form.age.data, form.role.data, hashed_password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('sports_club.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM User WHERE name=?', (session['username'],))
    user = cursor.fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/add_people', methods=['GET', 'POST'])
def add_people():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('sports_club.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM Section')
    sections = cursor.fetchall()
    section_choices = [(section[0], section[0]) for section in sections]
    section_choices.insert(0, ('No Section', 'No Section'))

    current_user = session['username']
    cursor.execute('SELECT role FROM User WHERE name=?', (current_user,))
    user_role = cursor.fetchone()[0]  # Fetch the role from the User table
    
    student_form = StudentForm(prefix='student')
    student_form.section.choices = section_choices

    if request.method == 'POST':
        if student_form.validate_on_submit():
            section = student_form.section.data
            competition = 1 if student_form.competition.data else 0  # Save as boolean value
            # Generate a random ID
            random_id = random.randint(1000, 9999)
            cursor.execute('INSERT INTO Person (name, age, role, section, random_id, competition) VALUES (?, ?, ?, ?, ?, ?)',
                           (current_user, 0, user_role, section, random_id, competition))  # Insert role correctly
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    
    conn.close()
    return render_template('add_people.html', student_form=student_form)
@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if 'username' not in session:
        return redirect(url_for('login'))
    section_form = SectionForm()
    if section_form.validate_on_submit():
        conn = sqlite3.connect('sports_club.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Section (name, monday, tuesday, wednesday, thursday, friday, saturday, sunday)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (section_form.name.data, section_form.monday.data, section_form.tuesday.data, section_form.wednesday.data,
              section_form.thursday.data, section_form.friday.data, section_form.saturday.data, section_form.sunday.data))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_section.html', section_form=section_form)


@app.route('/generate_report/<int:person_id>')
def generate_report(person_id):
    conn = sqlite3.connect('sports_club.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Person WHERE id=?', (person_id,))
    person = cursor.fetchone()
    conn.close()

    if not person:
        return "Student not found", 404

    report_content = f"""
    Ім'я: {person[1]}
    Роль: {person[3]}
    Секція: {person[4]}
    ID: {person[5]}
    Змагання: {'Так' if person[6] else 'Ні'}
    """

    return send_file(
        io.BytesIO(report_content.encode('utf-8')),
        mimetype='text/plain',
        as_attachment=True,
        download_name=f'report_{person[1]}.txt'
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)