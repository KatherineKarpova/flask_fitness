import sqlite3
from flask import Flask, render_template, request, redirect, flash, session
from flask_session import Session 
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import hashlib
from email_validator import validate_email, EmailNotValidError
import calendar
import datetime

# initialize flask app
app = Flask(__name__)

# set configurations from config.py for security
app.config.from_object(Config)

#initialize flask session
Session(app)

conn = sqlite3.connect('fitness.db')
c = conn.cursor()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# function to make list of exercise names
def exercise_names(c):
    return c.execute("SELECT name FROM exercises").fetchall()

# get dates from a date form
def get_date_input(form_id):
    month = request.form.get(f'month-{form_id}').strip()
    day = request.form.get(f'day-{form_id}').strip()
    year = request.form.get(f'year-{form_id}').strip()
    
    # check for empty fields
    if not month or not year or not day:
        raise ValueError('Missing data: month, day, and year are required')
    try:
        month, year, day = map(int, [month, year, day])
    except ValueError as e:
        # In case of invalid month or other issues
        raise ValueError(f'Invalid data provided: {str(e)}')
    return month, day, year
    
def format_date(month, day, year):
    # format date as YYYY-MM-DD
    return datetime.date(year, month, day).isoformat()

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    # get exercises from db for dropdown menu
    exercises = exercise_names(c)

    if request.method == 'POST':
        month, day, year = get_date_input('entry-date')
        date = format_date(month, day, year)
        exercise = request.form.get('exercise')
        exercise_query = c.execute('''SELECT id FROM exercises WHERE name = ?''', (exercise,)).fetchone()
        if exercise_query is None:
            flash('Exercise not found.')
            return redirect('/index.html')
        exercise_id = exercise_query[0]
        # convert weight, reps, and time to ints unless empty
        weight = request.form.get('weight')
        if weight != 'bodyweight':
            try:
                weight = int(weight)
            except ValueError:
                flash('Please give a valid number for the weight unless it is bodyweight.')
        else:
            weight = 0
        # convert reps to int
        try:
            reps = int(request.form.get('reps'))
        except ValueError:
            reps = None
        try:
            hours, minutes, seconds = map(int,[request.form.get('hours')], request.form.get('minutes'), request.form.get('seconds'))
            time = (f"{hours:02}:{minutes:02}:{seconds:02}")

        except ValueError:
            time = None
        print(session['user_id'], date, exercise_id, weight, reps, time)
        # Save data to database
        c.execute('INSERT INTO logs (user_id, date, exercise_id, weight, reps, time) VALUES (?, ?, ?, ?, ?, ?)',
                  (session['user_id'], date, exercise_id, weight, reps, time))
        conn.commit()
        conn.close()

        # Re-render the form with the previous values filled in
        return render_template('index.html', month=month, day=day, year=year, exercises=exercises,
                               exercise=exercise, weight=weight, reps=reps, time=time)
    return render_template('index.html', exercises=exercises)

# link to login page
def login_link():
    return '<br><a href="/login">login</a>'

# link to register page
def register_link():
    return '<br><a href="/register">create account</a>'

def hash_email(email):
    return hashlib.sha256(email.encode()).hexdigest()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/')  # Redirect to home if already logged in

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate that email and password are provided
        if not email:
            flash(f'Email is required! {login_link()}')
            return redirect('/login')
        elif not password:
            flash(f'Password is required! {login_link()}')
            return redirect('/login')

        # Hash the email before checking it in the database
        email_hash = hash_email(email)

        # Query the database for a matching email hash
        conn = sqlite3.connect('fitness.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email_hash = ?', (email_hash,))
        user = c.fetchone()  # Fetch the first matching user

        if user is None:
            flash(f'Email is not registered! {register_link()}')
            return redirect('/login')

        # Verify the password with the stored password hash
        if not check_password_hash(user[1], password):  # user[1] is the password hash
            flash('Incorrect username or password')
            return redirect('/login')

        # Successful login: Store user_id in session
        session['user_id'] = user[0]  # user[0] is the user_id from the database

        flash('Login successful!', 'success')
        return redirect('/')  # Redirect to home page or dashboard

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        email_confirmation = request.form.get('email-confirmation')
        password = request.form.get('password')
        password_confirmation = request.form.get('password-confirmation')

        if not email or not email_confirmation or not password or not password_confirmation:
            flash("All fields are required!")
            return redirect('/register')
        
        # used email_validator library example as outline for the below code
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
            confirmemailinfo = validate_email(email_confirmation, check_deliverability=False)
            email_confirmation = confirmemailinfo.normalized

        except EmailNotValidError as e:
            flash(str(e))

        if email != email_confirmation:
            flash("Emails do not match")
            return redirect('/register')

        if password != password_confirmation:
            flash("Passwords do not match")
            return redirect('/register')

        password_hash = generate_password_hash(password)
        email_hash = hash_email(email)

        conn = sqlite3.connect('fitness.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (email_hash TEXT, password_hash TEXT)')
        c.execute('INSERT INTO users (email_hash, password_hash) VALUES (?, ?)', (email_hash, password_hash))
        conn.commit()
        conn.close()

        flash("Registration successful!")
        return redirect('/login')

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)

